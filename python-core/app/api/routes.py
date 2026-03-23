"""
智能工单系统的API路由。

本模块定义了以下API端点：
- 聊天/意图识别
- 物流查询
- 催单工单创建
- 订单取消
"""

import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

# 导入模型
from app.models import IntentType, IntentResult, IntentEntities, Order, LogisticsInfo, Ticket

# 导入服务
from app.services.intent_recognition import get_intent_recognition_service, IntentRecognitionService
from app.services.logistics import LogisticsService
from app.services.urgent import UrgentService
from app.services.cancel import CancelService, CancelResult

# 导入仓库
from app.repositories.base import OrderRepository, LogisticsRepository, TicketRepository
from data.mock_data import MockOrderRepository, MockLogisticsRepository, MockTicketRepository


# 创建主路由器
router = APIRouter()


def _is_confirmation(message: str) -> bool:
    """判断用户消息是否为确认回答。"""
    confirm_keywords = ["是的", "对", "确认", "正确", "ok", "yes", "y", "好", "可以", "来"]
    return any(keyword in message.lower() for keyword in [k.lower() for k in confirm_keywords])


# 服务实例的依赖函数
def get_order_repository() -> OrderRepository:
    """获取订单仓库实例。"""
    return MockOrderRepository()


def get_logistics_repository() -> LogisticsRepository:
    """获取物流仓库实例。"""
    return MockLogisticsRepository()


def get_ticket_repository() -> TicketRepository:
    """获取工单仓库实例。"""
    return MockTicketRepository()


def get_intent_service() -> IntentRecognitionService:
    """获取意图识别服务实例。"""
    return get_intent_recognition_service()


def get_logistics_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    logistics_repo: LogisticsRepository = Depends(get_logistics_repository),
) -> LogisticsService:
    """获取物流服务实例。"""
    return LogisticsService(order_repo, logistics_repo)


def get_urgent_service(
    ticket_repo: TicketRepository = Depends(get_ticket_repository),
) -> UrgentService:
    """获取催单服务实例。"""
    return UrgentService(ticket_repo)


def get_cancel_service(
    order_repo: OrderRepository = Depends(get_order_repository),
) -> CancelService:
    """获取取消订单服务实例。"""
    return CancelService(order_repo)


# 聊天请求/响应模型
class ChatRequest(BaseModel):
    """聊天端点请求模型。"""
    session_id: str
    user_id: str
    message: str
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """聊天端点响应模型。"""
    success: bool
    response: str
    intent: str
    session_id: str
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    context: Optional[dict] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    intent_service: IntentRecognitionService = Depends(get_intent_service),
    logistics_service: LogisticsService = Depends(get_logistics_service),
    urgent_service: UrgentService = Depends(get_urgent_service),
    cancel_service: CancelService = Depends(get_cancel_service),
) -> ChatResponse:
    """
    聊天端点，用于意图识别和路由。
    
    此端点的功能：
    1. 接收包含会话信息的用户消息
    2. 使用意图识别来识别用户意图
    3. 路由到相应的服务（物流、催单、取消）
    4. 返回包含意图、响应文本和会话信息的结构化响应
    
    参数：
        request: 包含session_id、user_id和message的ChatRequest
        
    返回：
        包含意图、响应文本和会话信息的ChatResponse
    """
    # 步骤1：检查是否有上下文中的待处理意图
    logger.info(f"==> 收到聊天请求: session_id={request.session_id}, message={request.message}")
    logger.info(f"    请求context: {request.context}")
    logger.info(f"    请求context类型: {type(request.context)}")
    
    saved_order_id = None
    saved_intent = None
    if request.context and isinstance(request.context, dict):
        saved_order_id = request.context.get("pending_order_id")
        saved_intent = request.context.get("pending_intent")
    
    logger.info(f"    上下文信息: saved_order_id={saved_order_id}, saved_intent={saved_intent}")
    
    # 步骤2：识别意图
    intent_result = intent_service.recognize(request.message)
    logger.info(f"    意图识别结果: intent={intent_result.intent.value}, confidence={intent_result.confidence:.2f}, order_id={intent_result.entities.order_id}")
    
    # 步骤3：如果有保存的意图且当前消息提供了订单号，使用保存的意图
    if saved_intent and intent_result.entities.order_id and not saved_order_id:
        logger.info(f"    检测到用户提供订单号，使用保存的意图: {saved_intent}")
        # 将意图改为保存的意图
        intent_result.intent = IntentType(saved_intent)
        intent_result.needs_clarification = False
        intent_result.confidence = 1.0
    
    # 步骤4：如果需要澄清，处理澄清逻辑
    if intent_result.needs_clarification:
        logger.info(f"    需要澄清: needs_clarification=True")
        
        # 如果有保存的订单号且用户确认了，直接处理
        if saved_order_id and _is_confirmation(request.message):
            logger.info(f"    用户确认订单号: {saved_order_id}")
            intent_result.entities.order_id = saved_order_id
            intent_result.needs_clarification = False
            if saved_intent:
                intent_result.intent = IntentType(saved_intent)
        else:
            # 保存当前识别的订单号和意图到context，供下次使用
            response_context = {
                "pending_order_id": intent_result.entities.order_id,
                "pending_intent": intent_result.intent.value
            }
            # 使用LLM返回的clarification_question作为响应
            response_text = intent_result.clarification_question or "请提供更多信息以便我帮助您。"
            response = ChatResponse(
                success=True,
                response=response_text,
                intent=intent_result.intent.value,
                session_id=request.session_id,
                needs_clarification=True,
                clarification_question=intent_result.clarification_question,
                context=response_context,
            )
            logger.info(f"<== 返回响应: needs_clarification=True, response={response_text[:50]}...")
            logger.info(f"    返回context: {response_context}")
            return response
    
    # 步骤3：根据意图路由到相应的服务
    order_id = intent_result.entities.order_id
    user_detail = intent_result.entities.user_detail
    
    if intent_result.intent == IntentType.LOGISTICS:
        # 处理物流查询
        logger.info(f"    处理物流查询: order_id={order_id}")
        
        if not order_id:
            logger.info(f"    缺少订单号，需要澄清")
            return ChatResponse(
                success=True,
                response="请提供您要查询的订单号，例如：查询ORD001的物流",
                intent=IntentType.LOGISTICS.value,
                session_id=request.session_id,
                needs_clarification=True,
                clarification_question="请提供订单号",
                context={"pending_order_id": None, "pending_intent": "logistics"},
            )
        
        logistics_info = logistics_service.get_logistics_info(order_id)
        if not logistics_info:
            logger.info(f"    订单不存在: {order_id}")
            return ChatResponse(
                success=False,
                response=f"查询的订单 {order_id} 不存在，请检查订单号是否正确",
                intent=IntentType.LOGISTICS.value,
                session_id=request.session_id,
                context={"pending_order_id": order_id, "pending_intent": "logistics"},
            )
        
        # 格式化物流响应
        response_text = f"订单 {order_id} 的物流信息：\n"
        response_text += f"最新状态：{logistics_info.latest_status}\n"
        if logistics_info.estimated_delivery:
            response_text += f"预计送达时间：{logistics_info.estimated_delivery.strftime('%Y-%m-%d %H:%M')}\n"
        if logistics_info.tracking_history:
            response_text += "\n最近物流轨迹：\n"
            for i, event in enumerate(logistics_info.tracking_history, 1):
                location = event.location or "未知地点"
                response_text += f"{i}. {event.status} - {event.timestamp.strftime('%Y-%m-%d %H:%M')} ({location})\n"
        
        logger.info(f"    物流查询成功: order_id={order_id}, status={logistics_info.latest_status}")
        
        return ChatResponse(
            success=True,
            response=response_text.strip(),
            intent=IntentType.LOGISTICS.value,
            session_id=request.session_id,
            context={"pending_order_id": order_id, "pending_intent": "logistics"},
        )
    
    elif intent_result.intent == IntentType.URGENT:
        # 处理催单工单创建
        logger.info(f"    处理催单工单: order_id={order_id}")
        
        if not order_id:
            logger.info(f"    缺少订单号，需要澄清")
            return ChatResponse(
                success=True,
                response="请提供您要催单的订单号",
                intent=IntentType.URGENT.value,
                session_id=request.session_id,
                needs_clarification=True,
                clarification_question="请提供订单号",
                context={"pending_order_id": None, "pending_intent": "urgent"},
            )
        
        # 检查订单是否存在
        order = logistics_service.order_repository.get_by_id(order_id)
        if not order:
            logger.info(f"    订单不存在: {order_id}")
            return ChatResponse(
                success=False,
                response=f"查询的订单 {order_id} 不存在，请检查订单号是否正确",
                intent=IntentType.URGENT.value,
                session_id=request.session_id,
                context={"pending_order_id": order_id, "pending_intent": "urgent"},
            )
        
        result = urgent_service.create_urgent_ticket(order_id, user_detail)
        
        logger.info(f"    催单工单创建成功: ticket_id={result['ticket_id']}")
        
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
            context={"pending_order_id": order_id, "pending_intent": "urgent"},
        )
    
    elif intent_result.intent == IntentType.CANCEL:
        # 处理订单取消
        logger.info(f"    处理订单取消: order_id={order_id}")
        
        if not order_id:
            logger.info(f"    缺少订单号，需要澄清")
            return ChatResponse(
                success=True,
                response="请提供您要取消的订单号",
                intent=IntentType.CANCEL.value,
                session_id=request.session_id,
                needs_clarification=True,
                clarification_question="请提供订单号",
                context={"pending_order_id": None, "pending_intent": "cancel"},
            )
        
        # 检查订单是否存在
        order = logistics_service.order_repository.get_by_id(order_id)
        if not order:
            logger.info(f"    订单不存在: {order_id}")
            return ChatResponse(
                success=False,
                response=f"查询的订单 {order_id} 不存在，请检查订单号是否正确",
                intent=IntentType.CANCEL.value,
                session_id=request.session_id,
                context={"pending_order_id": order_id, "pending_intent": "cancel"},
            )
        
        result = cancel_service.cancel_order(order_id, user_detail)
        
        if result.success:
            logger.info(f"    订单取消成功: order_id={order_id}, refund={result.refund_amount}")
            response_text = f"订单取消成功：\n"
            response_text += f"订单号：{result.order_id}\n"
            response_text += f"退款金额：¥{result.refund_amount:.2f}\n"
            if result.refund_arrival_time:
                response_text += f"退款到账时间：{result.refund_arrival_time.strftime('%Y-%m-%d')}\n"
            response_text += f"信息：{result.message}"
        else:
            logger.info(f"    订单取消失败: order_id={order_id}, reason={result.message}")
            response_text = f"无法取消订单：\n"
            response_text += f"原因：{result.message}"
        
        return ChatResponse(
            success=result.success,
            response=response_text,
            intent=IntentType.CANCEL.value,
            session_id=request.session_id,
            context={"pending_order_id": order_id, "pending_intent": "cancel"},
        )
    
    # 未知意图的后备处理
    logger.info(f"    未知意图，跳转到fallback")
    return ChatResponse(
        success=True,
        response="抱歉，我无法理解您的请求。请尝试描述您的需求（查询物流、催单或取消订单）。",
        intent="unknown",
        session_id=request.session_id,
        needs_clarification=True,
        clarification_question="请告诉我您需要什么帮助？",
        context={"pending_order_id": None, "pending_intent": None},
    )


@router.get("/logistics/{order_id}", response_model=dict)
async def get_logistics(
    order_id: str,
    logistics_service: LogisticsService = Depends(get_logistics_service),
) -> dict:
    """
    获取订单的物流信息。
    
    参数：
        order_id: 订单号（格式：ORD+数字）
        logistics_service: 物流服务实例
        
    返回：
        包含状态、跟踪历史和预计送达时间的物流信息
    """
    # 验证订单号格式（ORD+数字）
    import re
    if not re.match(r'^ORD\d+$', order_id):
        return {
            "success": False,
            "error": "Invalid order ID format",
            "message": "订单号格式不正确，请使用 ORD+数字 的格式，例如：ORD001"
        }
    
    # 获取物流信息
    logistics_info = logistics_service.get_logistics_info(order_id)
    
    # 处理订单未找到的情况
    if not logistics_info:
        return {
            "success": False,
            "error": "Order not found",
            "message": f"未找到订单 {order_id}，请检查订单号是否正确"
        }
    
    # 返回格式化的物流信息
    return {
        "success": True,
        "data": {
            "order_id": logistics_info.order_id,
            "status": logistics_info.status.value if hasattr(logistics_info.status, 'value') else logistics_info.status,
            "latest_status": logistics_info.latest_status,
            "estimated_delivery": logistics_info.estimated_delivery.isoformat() if logistics_info.estimated_delivery else None,
            "tracking_history": [
                {
                    "status": event.status,
                    "timestamp": event.timestamp.isoformat(),
                    "location": event.location
                }
                for event in logistics_info.tracking_history
            ]
        }
    }


@router.post("/tickets/urgent", response_model=dict)
async def create_urgent_ticket(
    request: dict,
    urgent_service: UrgentService = Depends(get_urgent_service),
) -> dict:
    """
    为订单创建催单工单。
    
    参数：
        request: 包含order_id和可选reason的请求
        urgent_service: 催单工单服务实例
        
    返回：
        包含ticket_id、预计处理时间和联系方式的工单信息
    """
    order_id = request.get("order_id")
    reason = request.get("reason")
    
    if not order_id:
        return {
            "success": False,
            "error": "order_id is required"
        }
    
    result = urgent_service.create_urgent_ticket(order_id, reason)
    
    return {
        "success": True,
        "data": {
            "ticket_id": result["ticket_id"],
            "order_id": result["order_id"],
            "estimated_processing_time": result["estimated_processing_time"],
            "contact": result["contact"]
        }
    }


@router.post("/orders/cancel", response_model=dict)
async def cancel_order(
    request: dict,
    cancel_service: CancelService = Depends(get_cancel_service),
) -> dict:
    """
    取消订单并处理退款。
    
    参数：
        request: 包含order_id和reason的请求
        cancel_service: 取消订单服务实例
        
    返回：
        包含退款金额和到账时间的取消结果
    """
    order_id = request.get("order_id")
    reason = request.get("reason")
    
    if not order_id:
        return {
            "success": False,
            "error": "order_id is required"
        }
    
    result = cancel_service.cancel_order(order_id, reason)
    
    return {
        "success": result.success,
        "data": {
            "order_id": result.order_id,
            "refund_amount": result.refund_amount,
            "refund_arrival_time": result.refund_arrival_time.isoformat() if result.refund_arrival_time else None,
            "message": result.message
        }
    }