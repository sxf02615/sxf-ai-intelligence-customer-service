"""Cancel Order Service for handling order cancellation and refunds.

This service handles order cancellation operations including status validation,
refund processing, and result reporting based on FR5 requirements.
"""

from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel

from app.models import OrderStatus
from app.repositories.base import OrderRepository


class CancelResult(BaseModel):
    """Result of a cancel order operation."""

    success: bool
    order_id: str
    message: str
    refund_amount: Optional[float] = None
    refund_arrival_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class CancelService:
    """Service for handling order cancellation and refunds."""

    # Refund processing time in days
    REFUND_PROCESSING_DAYS = 3

    def __init__(self, order_repository: OrderRepository):
        """Initialize the cancel service.

        Args:
            order_repository: Repository for order data access.
        """
        self.order_repository = order_repository

    def cancel_order(
        self,
        order_id: str,
        reason: Optional[str] = None,
    ) -> CancelResult:
        """Cancel an order and process refund if applicable.

        Args:
            order_id: The order ID to cancel.
            reason: Optional reason for cancellation.

        Returns:
            CancelResult with cancellation status and refund info.
        """
        # Get order
        order = self.order_repository.get_by_id(order_id)
        if not order:
            return CancelResult(
                success=False,
                order_id=order_id,
                message="Order not found",
            )

        # Validate order status
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

        # Process cancellation via repository
        result = self.order_repository.cancel(order_id, reason or "User requested cancellation")

        # Calculate refund arrival time
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
        """Calculate when refund will arrive in user's account.

        Returns:
            Estimated refund arrival datetime.
        """
        return datetime.now() + timedelta(days=self.REFUND_PROCESSING_DAYS)

    def validate_order_for_cancellation(self, order_id: str) -> tuple[bool, str]:
        """Validate if an order can be cancelled.

        Args:
            order_id: The order ID to validate.

        Returns:
            Tuple of (is_valid, reason_if_invalid)
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
        """Get the refund amount for an order.

        Args:
            order_id: The order ID.

        Returns:
            Refund amount if order exists, None otherwise.
        """
        order = self.order_repository.get_by_id(order_id)
        if order:
            return order.amount
        return None