"""
Chat API endpoints for Smart Ticket System Python UI.

Provides chat functionality by calling the Java chat service
which routes to the Python core for intent recognition and processing.

Requirements: NFR7
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import httpx

from app.config import get_java_service_url, get_java_service_timeout, get_session_config


router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request model from UI."""
    message: str
    session_id: Optional[str] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response model for UI."""
    success: bool
    response: str
    intent: Optional[str] = None
    session_id: Optional[str] = None
    needs_clarification: bool = False
    message: Optional[str] = None


class JavaChatRequest(BaseModel):
    """Request model for Java chat service."""
    session_id: str
    user_id: str
    message: str
    context: Optional[dict] = None


class JavaChatResponse(BaseModel):
    """Response model from Java chat service."""
    success: bool
    response: str
    intent: Optional[str] = None
    session_id: Optional[str] = None
    needs_clarification: bool = False
    message: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None


def get_java_chat_url() -> str:
    """Get the Java chat service URL."""
    return f"{get_java_service_url()}/api/v1/chat"


def get_user_id_from_session(request: Request) -> Optional[str]:
    """
    Extract user ID from session cookie.
    
    Args:
        request: Request object for accessing cookies
        
    Returns:
        str: User ID from session or None
    """
    session_config = get_session_config()
    cookie_name = session_config["cookie_name"]
    
    # For now, return a default user ID since we're using token-based auth
    # In a full implementation, we would decode the token to get user_id
    token = request.cookies.get(cookie_name)
    if token:
        # Extract user_id from token or use a default
        # For simplicity, we'll use a placeholder
        return "user_001"
    return None


async def call_java_chat_service(
    session_id: str,
    user_id: str,
    message: str,
    context: Optional[dict] = None
) -> dict:
    """
    Call the Java chat service to process user message.
    
    Args:
        session_id: Session identifier
        user_id: User identifier
        message: User's message
        context: Optional context information
        
    Returns:
        dict: Response from Java service containing chat result
        
    Raises:
        HTTPException: If the chat service is unavailable
    """
    timeout = get_java_service_timeout()
    java_url = get_java_chat_url()
    
    payload = {
        "sessionId": session_id,
        "userId": user_id,
        "message": message
    }
    
    if context:
        payload["context"] = context
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(
                java_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Chat service unavailable: {str(e)}"
            )


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    http_request: Request
) -> ChatResponse:
    """
    Handle user chat messages by processing through Java service.
    
    POST /api/chat
    
    Args:
        request: ChatRequest containing user's message
        http_request: HTTP request for accessing session cookies
        
    Returns:
        ChatResponse with assistant's reply and intent information
        
    Requirements: NFR7
    """
    # Validate input
    if not request.message or request.message.strip() == "":
        return ChatResponse(
            success=False,
            response="",
            message="消息内容不能为空"
        )
    
    # Get session info
    session_config = get_session_config()
    cookie_name = session_config["cookie_name"]
    session_id = http_request.cookies.get(cookie_name)
    
    if not session_id:
        return ChatResponse(
            success=False,
            response="",
            message="未找到有效的会话，请重新登录"
        )
    
    # Get user ID from session
    user_id = get_user_id_from_session(http_request)
    if not user_id:
        return ChatResponse(
            success=False,
            response="",
            message="无法获取用户信息，请重新登录"
        )
    
    # Call Java chat service
    try:
        java_response = await call_java_chat_service(
            session_id=session_id,
            user_id=user_id,
            message=request.message,
            context=request.context
        )
    except HTTPException:
        raise
    
    # Handle Java service response
    if java_response.get("success"):
        data = java_response.get("data", {})
        
        return ChatResponse(
            success=True,
            response=data.get("response", ""),
            intent=data.get("intent"),
            session_id=data.get("session_id"),
            needs_clarification=data.get("needsClarification", False)
        )
    else:
        # Chat processing failed
        error_message = java_response.get("message", "处理消息时发生错误")
        
        return ChatResponse(
            success=False,
            response="",
            message=error_message
        )


@router.get("/health")
async def chat_health() -> dict:
    """
    Health check endpoint for chat service.
    
    GET /api/chat/health
    
    Returns:
        dict with health status
    """
    return {"status": "healthy", "service": "chat-api"}