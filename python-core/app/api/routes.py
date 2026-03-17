"""
API routes for the Smart Ticket System.

This module defines the API endpoints for:
- Chat/Intent recognition
- Logistics queries
- Urgent ticket creation
- Order cancellation
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

# Import models
from app.models.intent import IntentType, IntentResult, IntentEntities
from app.models.order import Order, CancelResult
from app.models.logistics import LogisticsInfo
from app.models.ticket import Ticket

# Import services
from app.services.intent_recognition import get_intent_recognition_service, IntentRecognitionService
from app.services.logistics import LogisticsService
from app.services.urgent import UrgentService
from app.services.cancel import CancelService

# Import repositories
from app.repositories.base import OrderRepository, LogisticsRepository, TicketRepository
from data.mock_data import MockOrderRepository, MockLogisticsRepository, MockTicketRepository


# Create main router
router = APIRouter()


# Dependency functions for service instances
def get_order_repository() -> OrderRepository:
    """Get order repository instance."""
    return MockOrderRepository()


def get_logistics_repository() -> LogisticsRepository:
    """Get logistics repository instance."""
    return MockLogisticsRepository()


def get_ticket_repository() -> TicketRepository:
    """Get ticket repository instance."""
    return MockTicketRepository()


def get_intent_service() -> IntentRecognitionService:
    """Get intent recognition service instance."""
    return get_intent_recognition_service()


def get_logistics_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    logistics_repo: LogisticsRepository = Depends(get_logistics_repository),
) -> LogisticsService:
    """Get logistics service instance."""
    return LogisticsService(order_repo, logistics_repo)


def get_urgent_service(
    ticket_repo: TicketRepository = Depends(get_ticket_repository),
) -> UrgentService:
    """Get urgent ticket service instance."""
    return UrgentService(ticket_repo)


def get_cancel_service(
    order_repo: OrderRepository = Depends(get_order_repository),
) -> CancelService:
    """Get cancel order service instance."""
    return CancelService(order_repo)


# Chat request/response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: str
    user_id: str
    message: str
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    success: bool
    response: str
    intent: str
    session_id: str
    needs_clarification: bool = False
    clarification_question: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    intent_service: IntentRecognitionService = Depends(get_intent_service),
    logistics_service: LogisticsService = Depends(get_logistics_service),
    urgent_service: UrgentService = Depends(get_urgent_service),
    cancel_service: CancelService = Depends(get_cancel_service),
) -> ChatResponse:
    """
    Chat endpoint for intent recognition and routing.
    
    This endpoint:
    1. Receives user message with session info
    2. Uses intent recognition to identify user intent
    3. Routes to appropriate service (logistics, urgent, cancel)
    4. Returns structured response with intent, response text, and session info
    
    Args:
        request: ChatRequest containing session_id, user_id, and message
        
    Returns:
        ChatResponse with intent, response text, and session info
    """
    # Step 1: Recognize intent from user message
    intent_result = intent_service.recognize(request.message)
    
    # Step 2: Handle clarification if needed
    if intent_result.needs_clarification:
        return ChatResponse(
            success=True,
            response=intent_result.clarification_question or "请提供更多信息以便我帮助您。",
            intent=intent_result.intent.value,
            session_id=request.session_id,
            needs_clarification=True,
            clarification_question=intent_result.clarification_question,
        )
    
    # Step 3: Route to appropriate service based on intent
    order_id = intent_result.entities.order_id
    user_detail = intent_result.entities.user_detail
    
    if intent_result.intent == IntentType.LOGISTICS:
        # Handle logistics query
        if not order_id:
            return ChatResponse(
                success=True,
                response="请提供您要查询的订单号，例如：查询ORD001的物流",
                intent=IntentType.LOGISTICS.value,
                session_id=request.session_id,
                needs_clarification=True,
                clarification_question="请提供订单号",
            )
        
        logistics_info = logistics_service.get_logistics_info(order_id)
        if not logistics_info:
            return ChatResponse(
                success=False,
                response=f"未找到订单 {order_id}，请检查订单号是否正确",
                intent=IntentType.LOGISTICS.value,
                session_id=request.session_id,
            )
        
        # Format logistics response
        response_text = f"订单 {order_id} 的物流信息：\n"
        response_text += f"最新状态：{logistics_info.latest_status}\n"
        if logistics_info.estimated_delivery:
            response_text += f"预计送达时间：{logistics_info.estimated_delivery.strftime('%Y-%m-%d %H:%M')}\n"
        if logistics_info.tracking_history:
            response_text += "\n最近物流轨迹：\n"
            for i, event in enumerate(logistics_info.tracking_history, 1):
                location = event.location or "未知地点"
                response_text += f"{i}. {event.status} - {event.timestamp.strftime('%Y-%m-%d %H:%M')} ({location})\n"
        
        return ChatResponse(
            success=True,
            response=response_text.strip(),
            intent=IntentType.LOGISTICS.value,
            session_id=request.session_id,
        )
    
    elif intent_result.intent == IntentType.URGENT:
        # Handle urgent ticket creation
        if not order_id:
            return ChatResponse(
                success=True,
                response="请提供您要催单的订单号",
                intent=IntentType.URGENT.value,
                session_id=request.session_id,
                needs_clarification=True,
                clarification_question="请提供订单号",
            )
        
        result = urgent_service.create_urgent_ticket(order_id, user_detail)
        
        response_text = f"已为您创建催单工单：\n"
        response_text += f"工单号：{result['ticket_id']}\n"
        response_text += f"预计处理时间：{result['estimated_processing_time']}\n"
        response_text += f"客服热线：{result['contact']}\n"
        response_text += f"状态：{result['message']}"
        
        return ChatResponse(
            success=True,
            response=response_text,
            intent=IntentType.URGENT.value,
            session_id=request.session_id,
        )
    
    elif intent_result.intent == IntentType.CANCEL:
        # Handle order cancellation
        if not order_id:
            return ChatResponse(
                success=True,
                response="请提供您要取消的订单号",
                intent=IntentType.CANCEL.value,
                session_id=request.session_id,
                needs_clarification=True,
                clarification_question="请提供订单号",
            )
        
        result = cancel_service.cancel_order(order_id, user_detail)
        
        if result.success:
            response_text = f"订单取消成功：\n"
            response_text += f"订单号：{result.order_id}\n"
            response_text += f"退款金额：¥{result.refund_amount:.2f}\n"
            if result.refund_arrival_time:
                response_text += f"退款到账时间：{result.refund_arrival_time.strftime('%Y-%m-%d')}\n"
            response_text += f"信息：{result.message}"
        else:
            response_text = f"无法取消订单：\n"
            response_text += f"原因：{result.message}"
        
        return ChatResponse(
            success=result.success,
            response=response_text,
            intent=IntentType.CANCEL.value,
            session_id=request.session_id,
        )
    
    # Fallback for unknown intent
    return ChatResponse(
        success=True,
        response="抱歉，我无法理解您的请求。请尝试描述您的需求（查询物流、催单或取消订单）。",
        intent="unknown",
        session_id=request.session_id,
        needs_clarification=True,
        clarification_question="请告诉我您需要什么帮助？",
    )


@router.get("/logistics/{order_id}", response_model=dict)
async def get_logistics(order_id: str) -> dict:
    """
    Get logistics information for an order.
    
    Args:
        order_id: Order ID (format: ORD+number)
        
    Returns:
        Logistics information including status, tracking history, and estimated delivery
    """
    # TODO: Implement in Task 3.3
    return {
        "success": True,
        "data": {
            "order_id": order_id,
            "status": "unknown",
            "latest_status": "Order not found",
            "estimated_delivery": None,
            "tracking_history": []
        }
    }


@router.post("/tickets/urgent", response_model=dict)
async def create_urgent_ticket(request: dict) -> dict:
    """
    Create an urgent ticket for an order.
    
    Args:
        request: Request containing order_id and optional reason
        
    Returns:
        Ticket information including ticket_id, estimated processing time, and contact
    """
    # TODO: Implement in Task 3.4
    return {
        "success": True,
        "data": {
            "ticket_id": "TKT-placeholder",
            "estimated_processing_time": None,
            "contact": "客服热线：400-xxx-xxxx"
        }
    }


@router.post("/orders/cancel", response_model=dict)
async def cancel_order(request: dict) -> dict:
    """
    Cancel an order and process refund.
    
    Args:
        request: Request containing order_id and reason
        
    Returns:
        Cancel result including refund amount and arrival time
    """
    # TODO: Implement in Task 3.5
    return {
        "success": True,
        "data": {
            "order_id": request.get("order_id"),
            "refund_amount": 0.0,
            "refund_arrival_time": None,
            "message": "Cancel endpoint not yet implemented"
        }
    }