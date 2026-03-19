"""取消订单服务，用于处理订单取消和退款。

该服务处理订单取消操作，包括状态验证、
退款处理和基于FR5要求的结果报告。
"""

from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel

from app.models import OrderStatus
from app.repositories.base import OrderRepository


class CancelResult(BaseModel):
    """取消订单操作的结果。"""

    success: bool
    order_id: str
    message: str
    refund_amount: Optional[float] = None
    refund_arrival_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class CancelService:
    """处理订单取消和退款的服务。"""

    # 退款处理天数
    REFUND_PROCESSING_DAYS = 3

    def __init__(self, order_repository: OrderRepository):
        """初始化取消服务。

        Args:
            order_repository: 订单数据访问的仓库。
        """
        self.order_repository = order_repository

    def cancel_order(
        self,
        order_id: str,
        reason: Optional[str] = None,
    ) -> CancelResult:
        """取消订单并在适用时处理退款。

        Args:
            order_id: 要取消的订单ID。
            reason: 可选的取消原因。

        Returns:
            包含取消状态和退款信息的CancelResult。
        """
        # 获取订单
        order = self.order_repository.get_by_id(order_id)
        if not order:
            return CancelResult(
                success=False,
                order_id=order_id,
                message="Order not found",
            )

        # 验证订单状态
        if order.status == OrderStatus.CANCELLED:
            return CancelResult(
                success=False,
                order_id=order_id,
                message="Order is already cancelled",
            )

        if order.status == OrderStatus.DELIVERED:
            return CancelResult(
                success=False,
                order_id=order_id,
                message="Order is delivered, please use after-sales return process",
            )

        # 通过仓库处理取消
        result = self.order_repository.cancel(order_id, reason or "User requested cancellation")

        # 计算退款到账时间
        refund_arrival_time = None
        if result.get("success"):
            refund_arrival_time = self._calculate_refund_arrival_time()

        return CancelResult(
            success=result.get("success", False),
            order_id=order_id,
            message=result.get("message", ""),
            refund_amount=result.get("refund_amount"),
            refund_arrival_time=refund_arrival_time,
        )

    def _calculate_refund_arrival_time(self) -> datetime:
        """计算退款到账时间。

        Returns:
            预计退款到账时间。
        """
        return datetime.now() + timedelta(days=self.REFUND_PROCESSING_DAYS)

    def validate_order_for_cancellation(self, order_id: str) -> tuple[bool, str]:
        """验证订单是否可以取消。

        Args:
            order_id: 要验证的订单ID。

        Returns:
            (是否有效, 无效原因)的元组
        """
        order = self.order_repository.get_by_id(order_id)
        if not order:
            return False, "Order not found"

        if order.status == OrderStatus.CANCELLED:
            return False, "Order is already cancelled"

        if order.status == OrderStatus.DELIVERED:
            return False, "Order is delivered, please use after-sales return process"

        return True, ""

    def get_refund_amount(self, order_id: str) -> Optional[float]:
        """获取订单的退款金额。

        Args:
            order_id: 订单ID。

        Returns:
            如果订单存在返回退款金额，否则返回None。
        """
        order = self.order_repository.get_by_id(order_id)
        if order:
            return order.amount
        return None