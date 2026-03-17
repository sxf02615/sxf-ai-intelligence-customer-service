"""Logistics Service for querying order logistics information.

This service handles logistics queries including order status retrieval,
tracking history, and estimated delivery time calculation.
"""
from datetime import datetime
from typing import Optional

from app.models import (
    LogisticsInfo,
    Order,
    OrderStatus,
    TrackingEvent,
)
from app.repositories.base import LogisticsRepository, OrderRepository


class LogisticsService:
    """Service for handling logistics-related operations."""

    def __init__(
        self,
        order_repository: OrderRepository,
        logistics_repository: LogisticsRepository,
    ):
        """Initialize the logistics service.
        
        Args:
            order_repository: Repository for order data access.
            logistics_repository: Repository for logistics data access.
        """
        self.order_repository = order_repository
        self.logistics_repository = logistics_repository

    def get_logistics_info(self, order_id: str) -> Optional[LogisticsInfo]:
        """Get complete logistics information for an order.
        
        Args:
            order_id: The order ID to query.
            
        Returns:
            LogisticsInfo if order found, None otherwise.
        """
        # Get order status
        order = self.order_repository.get_by_id(order_id)
        if not order:
            return None
        
        # Get tracking history (last 3 events)
        tracking_events = self._get_tracking_history(order_id)
        
        # Get estimated delivery time
        estimated_delivery = self._calculate_estimated_delivery(order, order_id)
        
        # Get latest status from tracking or order status
        latest_status = self._get_latest_status(order, tracking_events)
        
        return LogisticsInfo(
            order_id=order_id,
            status=order.status,
            latest_status=latest_status,
            estimated_delivery=estimated_delivery,
            tracking_history=tracking_events,
        )

    def _get_tracking_history(self, order_id: str) -> list[TrackingEvent]:
        """Get tracking history for an order (last 3 events).
        
        Args:
            order_id: The order ID to query.
            
        Returns:
            List of tracking events, most recent first.
        """
        return self.logistics_repository.get_tracking(order_id)

    def _calculate_estimated_delivery(
        self, order: Order, order_id: str
    ) -> Optional[datetime]:
        """Calculate or retrieve estimated delivery time.
        
        Args:
            order: The order object.
            order_id: The order ID.
            
        Returns:
            Estimated delivery datetime if available.
        """
        # For shipped orders, try to get estimated delivery from repository
        if order.status == OrderStatus.SHIPPED:
            return self.logistics_repository.get_estimated_delivery(order_id)
        return None

    def _get_latest_status(self, order: Order, tracking_events: list[TrackingEvent]) -> str:
        """Get the latest logistics status.
        
        Args:
            order: The order object.
            tracking_events: List of tracking events.
            
        Returns:
            Latest status description.
        """
        # If we have tracking events, use the most recent one
        if tracking_events:
            return tracking_events[0].status
        
        # Fall back to order status
        status_messages = {
            OrderStatus.PENDING: "Order is pending, not yet shipped",
            OrderStatus.PROCESSING: "Order is being processed",
            OrderStatus.SHIPPED: "Order has been shipped",
            OrderStatus.DELIVERED: "Order has been delivered",
            OrderStatus.CANCELLED: "Order has been cancelled",
        }
        return status_messages.get(order.status, f"Order status: {order.status.value}")