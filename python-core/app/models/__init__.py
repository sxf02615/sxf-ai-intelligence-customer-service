from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(BaseModel):
    """订单模型"""
    order_id: str = Field(..., description="订单号，格式：ORD+数字")
    status: OrderStatus = Field(..., description="订单状态")
    amount: float = Field(..., description="订单金额")
    created_at: datetime = Field(..., description="创建时间")


class TrackingEvent(BaseModel):
    """物流轨迹事件"""
    status: str = Field(..., description="状态描述")
    timestamp: datetime = Field(..., description="事件时间")
    location: Optional[str] = Field(None, description="事件地点")


class LogisticsInfo(BaseModel):
    """物流信息模型"""
    order_id: str = Field(..., description="订单号")
    status: OrderStatus = Field(..., description="订单状态")
    latest_status: str = Field(..., description="最新物流状态")
    estimated_delivery: Optional[datetime] = Field(None, description="预计送达时间")
    tracking_history: List[TrackingEvent] = Field(default_factory=list, description="最近3条物流轨迹")


class TicketPriority(str, Enum):
    """工单优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str, Enum):
    """工单状态枚举"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class Ticket(BaseModel):
    """工单模型"""
    ticket_id: str = Field(..., description="工单号，格式：TKT+时间戳")
    order_id: str = Field(..., description="关联订单号")
    reason: Optional[str] = Field(None, description="工单原因")
    priority: TicketPriority = Field(..., description="优先级")
    status: TicketStatus = Field(default=TicketStatus.OPEN, description="工单状态")
    created_at: datetime = Field(..., description="创建时间")
    estimated_processing_time: datetime = Field(..., description="预计处理时间")

    @field_validator('ticket_id')
    @classmethod
    def ticket_id_must_start_with_tkt(cls, v: str) -> str:
        """Ticket ID must start with 'TKT' followed by digits."""
        if not v.startswith('TKT'):
            raise ValueError('ticket_id must start with "TKT"')
        if len(v) <= 3:
            raise ValueError('ticket_id must have a numeric timestamp after "TKT"')
        numeric_part = v[3:]
        if not numeric_part.isdigit():
            raise ValueError('ticket_id timestamp must be numeric')
        return v


class IntentType(str, Enum):
    """意图类型枚举"""
    LOGISTICS = "logistics"
    URGENT = "urgent"
    CANCEL = "cancel"


class IntentEntities(BaseModel):
    """意图实体"""
    order_id: Optional[str] = Field(None, description="订单号，格式：ORD+数字")
    user_detail: Optional[str] = Field(None, description="用户诉求细节")


class IntentResult(BaseModel):
    """意图识别结果"""
    intent: IntentType = Field(..., description="识别的意图类型")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    entities: IntentEntities = Field(..., description="提取的实体")
    needs_clarification: bool = Field(default=False, description="是否需要澄清")
    clarification_question: Optional[str] = Field(None, description="澄清问题")