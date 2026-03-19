"""催单工单服务，用于处理工单创建和管理。

该服务处理催单工单操作，包括工单创建、优先级分配、
预计处理时间计算和客服通知。
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Optional

from app.models import (
    Ticket,
    TicketPriority,
    TicketStatus,
)
from app.repositories.base import TicketRepository

# 配置客服通知日志记录器
logger = logging.getLogger(__name__)


class UrgentService:
    """处理催单工单操作的服务。"""

    # 客服联系方式
    CUSTOMER_SERVICE_CONTACT = "400-123-4567"

    # 按优先级划分的预计处理时间（小时）
    PROCESSING_TIME_HOURS = {
        TicketPriority.HIGH: 2,   # 高优先级2小时
        TicketPriority.MEDIUM: 4,  # 中优先级4小时
        TicketPriority.LOW: 8,     # 低优先级8小时
    }

    def __init__(self, ticket_repository: TicketRepository):
        """初始化催单服务。

        Args:
            ticket_repository: 工单数据访问的仓库。
        """
        self.ticket_repository = ticket_repository

    def create_urgent_ticket(
        self,
        order_id: str,
        reason: Optional[str] = None,
    ) -> dict:
        """为订单创建催单工单。

        Args:
            order_id: 要创建工单的订单ID。
            reason: 催单的可选原因。

        Returns:
            包含ticket_id、estimated_processing_time和联系信息的字典。
        """
        # 生成TKT+时间戳格式的工单ID
        ticket_id = self._generate_ticket_id()

        # 根据原因内容确定优先级
        priority = self._determine_priority(reason)

        # 计算预计处理时间
        estimated_processing_time = self._calculate_estimated_processing_time(priority)

        # 创建工单
        now = datetime.now()
        ticket = Ticket(
            ticket_id=ticket_id,
            order_id=order_id,
            reason=reason,
            priority=priority,
            status=TicketStatus.OPEN,
            created_at=now,
            estimated_processing_time=estimated_processing_time,
        )

        # 保存工单到仓库
        created_ticket = self.ticket_repository.create(ticket)

        # 通知客服（记录通知）
        self._notify_customer_service(created_ticket)

        return {
            "ticket_id": created_ticket.ticket_id,
            "order_id": created_ticket.order_id,
            "priority": created_ticket.priority.value,
            "status": created_ticket.status.value,
            "estimated_processing_time": created_ticket.estimated_processing_time.isoformat(),
            "contact": self.CUSTOMER_SERVICE_CONTACT,
            "message": "Urgent ticket created successfully",
        }

    def _generate_ticket_id(self) -> str:
        """生成唯一的TKT+时间戳格式的工单ID。

        Returns:
            TKT+时间戳格式的工单ID字符串。
        """
        import uuid
        timestamp = int(time.time() * 1000000)  # 微秒
        unique_id = uuid.uuid4().hex[:8]  # 添加UUID后缀以保证唯一性
        return f"TKT{timestamp}{unique_id}"

    def _determine_priority(self, reason: Optional[str]) -> TicketPriority:
        """根据原因内容确定工单优先级。

        Args:
            reason: 创建催单工单的原因。

        Returns:
            基于原因分析的TicketPriority。
        """
        if not reason:
            # 如果没有提供原因，默认中等优先级
            return TicketPriority.MEDIUM

        reason_lower = reason.lower()

        # 高优先级关键词
        high_priority_keywords = [
            "紧急", "非常急", "马上", "立刻", "尽快",
            "urgent", "asap", "immediately", "emergency",
        ]

        # 低优先级关键词
        low_priority_keywords = [
            "不急", "慢慢来", "有空处理", "不着急",
            "not urgent", "when possible", "no rush",
        ]

        for keyword in high_priority_keywords:
            if keyword in reason_lower:
                return TicketPriority.HIGH

        for keyword in low_priority_keywords:
            if keyword in reason_lower:
                return TicketPriority.LOW

        # 默认中等优先级
        return TicketPriority.MEDIUM

    def _calculate_estimated_processing_time(
        self,
        priority: TicketPriority,
    ) -> datetime:
        """根据优先级计算预计处理时间。

        Args:
            priority: 工单优先级。

        Returns:
            预计处理时间。
        """
        hours = self.PROCESSING_TIME_HOURS.get(priority, self.PROCESSING_TIME_HOURS[TicketPriority.MEDIUM])
        return datetime.now() + timedelta(hours=hours)

    def _notify_customer_service(self, ticket: Ticket) -> None:
        """发送通知给客服。

        Args:
            ticket: 要通知的已创建工单。
        """
        notification_message = (
            f"[客服通知] 新催单工单已创建:\n"
            f"  工单ID: {ticket.ticket_id}\n"
            f"  订单ID: {ticket.order_id}\n"
            f"  优先级: {ticket.priority.value}\n"
            f"  原因: {ticket.reason or '未提供'}\n"
            f"  预计处理时间: {ticket.estimated_processing_time.isoformat()}"
        )
        logger.info(notification_message)

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """根据ID获取工单。

        Args:
            ticket_id: 要查询的工单ID。

        Returns:
            如果找到返回工单，否则返回None。
        """
        return self.ticket_repository.get_by_id(ticket_id)

    def list_tickets_by_order(self, order_id: str) -> list[Ticket]:
        """列出订单的所有工单。

        Args:
            order_id: 要查询的订单ID。

        Returns:
            订单的工单列表。
        """
        return self.ticket_repository.list_by_order(order_id)