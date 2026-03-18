"""
Authentication API endpoints for Smart Ticket System Python UI.

Provides login functionality by calling the Java authentication service
and managing user sessions.

Requirements: FR1.1, FR1.2, FR1.3
"""

from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel
from typing import Optional
import httpx
import time

from app.config import get_java_service_url, get_java_service_timeout, get_session_config


router = APIRouter(prefix="/api/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    success: bool
    message: str
    token: Optional[str] = None
    user_id: Optional[str] = None
    expires_in: Optional[int] = None


class JavaLoginRequest(BaseModel):
    """Request model for Java authentication service."""
    username: str
    password: str


class JavaLoginResponse(BaseModel):
    """Response model from Java authentication service."""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


def get_java_auth_url() -> str:
    """Get the Java authentication service URL."""
    return f"{get_java_service_url()}/api/v1/auth/login"


async def call_java_auth_service(username: str, password: str) -> dict:
    """
    Call the Java authentication service to validate credentials.
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        dict: Response from Java service containing success status and token info
        
    Raises:
        HTTPException: If the authentication service is unavailable
    """
    timeout = get_java_service_timeout()
    java_url = get_java_auth_url()
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(
                java_url,
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Authentication service unavailable: {str(e)}"
            )


def create_session_response(
    response: Response,
    token: str,
    user_id: str,
    expires_in: int
) -> Response:
    """
    Create a session cookie for successful login.
    
    Args:
        response: Response object to modify
        token: Authentication token
        user_id: User ID
        expires_in: Token expiration time in seconds
        
    Returns:
        Response with session cookie set
    """
    session_config = get_session_config()
    
    # Set session cookie
    max_age = expires_in if expires_in > 0 else 3600  # Default 1 hour
    response.set_cookie(
        key=session_config["cookie_name"],
        value=token,
        max_age=max_age,
        httponly=session_config["httponly"],
        secure=session_config["secure"],
        samesite="lax"
    )
    
    return response


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response
) -> LoginResponse:
    """
    Handle user login by authenticating with Java service.
    
    POST /api/auth/login
    
    Args:
        request: LoginRequest containing username and password
        response: Response object for setting session cookie
        
    Returns:
        LoginResponse with success status and token on success,
        or error message on failure
        
    Requirements: FR1.1, FR1.2, FR1.3
    """
    # Validate input
    if not request.username or not request.password:
        return LoginResponse(
            success=False,
            message="用户名和密码不能为空"
        )
    
    if request.username.strip() == "" or request.password.strip() == "":
        return LoginResponse(
            success=False,
            message="用户名和密码不能为空"
        )
    
    # Call Java authentication service
    try:
        java_response = await call_java_auth_service(
            request.username,
            request.password
        )
    except HTTPException:
        raise
    
    # Handle Java service response
    if java_response.get("success"):
        # Extract token data from Java response
        data = java_response.get("data", {})
        token = data.get("token")
        user_id = data.get("user_id")
        expires_in = data.get("expires_in", 3600)
        
        # Set session cookie
        create_session_response(response, token, user_id, expires_in)
        
        return LoginResponse(
            success=True,
            message=java_response.get("message", "登录成功"),
            token=token,
            user_id=user_id,
            expires_in=expires_in
        )
    else:
        # Authentication failed
        error_code = java_response.get("error", "AUTH_002")
        error_message = java_response.get("message", "用户名或密码错误")
        
        return LoginResponse(
            success=False,
            message=error_message
        )


@router.post("/logout")
async def logout(request: Request, response: Response) -> dict:
    """
    Handle user logout by clearing session.
    
    POST /api/auth/logout
    
    Args:
        request: Request object for accessing cookies
        response: Response object for clearing cookies
        
    Returns:
        dict with logout status
    """
    session_config = get_session_config()
    
    # Clear session cookie
    response.delete_cookie(
        key=session_config["cookie_name"],
        httponly=session_config["httponly"],
        secure=session_config["secure"],
        samesite="lax"
    )
    
    return {"success": True, "message": "已退出登录"}


@router.get("/session")
async def get_session(request: Request) -> dict:
    """
    Get current session information.
    
    GET /api/auth/session
    
    Args:
        request: Request object for accessing cookies
        
    Returns:
        dict with session status
    """
    session_config = get_session_config()
    cookie_name = session_config["cookie_name"]
    
    token = request.cookies.get(cookie_name)
    
    if token:
        return {
            "authenticated": True,
            "token": token
        }
    else:
        return {
            "authenticated": False
        }