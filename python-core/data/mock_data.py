"""Mock data sources for development and testing.

This module provides mock implementations of repository interfaces
with test data for orders, logistics, and tickets.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.models import (
    Order,
    OrderStatus,
    Ticket,
    TicketPriority,
    TicketStatus,
    TrackingEvent,
)
from app.repositories.base import (
    LogisticsRepository,
    OrderRepository,
    TicketRepository,
)


class MockOrderRepository(OrderRepository):
    """Mock implementation of OrderRepository with test data."""

    def __init__(self):
        # Test data: ORD001-shipped, ORD002-delivered, ORD003-cancelled
        self.orders: Dict[str, Order] = {
            "ORD001": Order(
                order_id="ORD001",
                status=OrderStatus.SHIPPED,
                amount=199.00,
                created_at=datetime.now() - timedelta(days=3),
            ),
            "ORD002": Order(
                order_id="ORD002",
                status=OrderStatus.DELIVERED,
                amount=299.00,
                created_at=datetime.now() - timedelta(days=7),
            ),
            "ORD003": Order(
                order_id="ORD003",
                status=OrderStatus.CANCELLED,
                amount=99.00,
                created_at=datetime.now() - timedelta(days=2),
            ),
        }

    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by order_id."""
        return self.orders.get(order_id)

    def update_status(self, order_id: str, status: str) -> bool:
        """Update order status."""
        if order_id in self.orders:
            try:
                self.orders[order_id].status = OrderStatus(status)
                return True
            except ValueError:
                return False
        return False

    def cancel(self, order_id: str, reason: str) -> dict:
        """Cancel an order and return cancel result."""
        order = self.orders.get(order_id)
        if not order:
            return {
                "success": False,
                "order_id": order_id,
                "message": "Order not found",
            }

        if order.status == OrderStatus.CANCELLED:
            return {
                "success": False,
                "order_id": order_id,
                "message": "Order is already cancelled",
            }

        if order.status == OrderStatus.DELIVERED:
            return {
                "success": False,
                "order_id": order_id,
                "message": "Order is delivered, please use after-sales return process",
            }

        # Process cancellation
        self.orders[order_id].status = OrderStatus.CANCELLED
        refund_amount = order.amount
        refund_arrival_time = datetime.now() + timedelta(days=3)

        return {
            "success": True,
            "order_id": order_id,
            "refund_amount": refund_amount,
            "refund_arrival_time": refund_arrival_time,
            "message": "Order cancelled successfully",
        }


class MockLogisticsRepository(LogisticsRepository):
    """Mock implementation of LogisticsRepository with tracking events."""

    def __init__(self):
        # Tracking events for shipped orders
        self.tracking_data: Dict[str, List[TrackingEvent]] = {
            "ORD001": [
                TrackingEvent(
                    status="Package has been shipped",
                    timestamp=datetime.now() - timedelta(days=3),
                    location="Shanghai Warehouse",
                ),
                TrackingEvent(
                    status="Package in transit",
                    timestamp=datetime.now() - timedelta(days=2),
                    location="Nanjing Distribution Center",
                ),
                TrackingEvent(
                    status="Package out for delivery",
                    timestamp=datetime.now() - timedelta(days=1),
                    location="Beijing Local Delivery Hub",
                ),
            ],
            "ORD002": [
                TrackingEvent(
                    status="Package has been shipped",
                    timestamp=datetime.now() - timedelta(days=7),
                    location="Shenzhen Warehouse",
                ),
                TrackingEvent(
                    status="Package delivered",
                    timestamp=datetime.now() - timedelta(days=5),
                    location="Customer Address",
                ),
            ],
        }
        # Estimated delivery times
        self.estimated_delivery: Dict[str, datetime] = {
            "ORD001": datetime.now() + timedelta(days=1),
        }

    def get_tracking(self, order_id: str) -> List[TrackingEvent]:
        """Get tracking events for an order (max 3 recent)."""
        events = self.tracking_data.get(order_id, [])
        return sorted(events, key=lambda x: x.timestamp, reverse=True)[:3]

    def get_estimated_delivery(self, order_id: str) -> Optional[datetime]:
        """Get estimated delivery time for an order."""
        return self.estimated_delivery.get(order_id)


class MockTicketRepository(TicketRepository):
    """Mock implementation of TicketRepository for ticket storage."""

    def __init__(self):
        self.tickets: Dict[str, Ticket] = {}
        self.order_tickets: Dict[str, List[str]] = {}

    def create(self, ticket: Ticket) -> Ticket:
        """Create a new ticket."""
        self.tickets[ticket.ticket_id] = ticket
        if ticket.order_id not in self.order_tickets:
            self.order_tickets[ticket.order_id] = []
        self.order_tickets[ticket.order_id].append(ticket.ticket_id)
        return ticket

    def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ticket_id."""
        return self.tickets.get(ticket_id)

    def list_by_order(self, order_id: str) -> List[Ticket]:
        """List all tickets for an order."""
        ticket_ids = self.order_tickets.get(order_id, [])
        return [self.tickets[tid] for tid in ticket_ids if tid in self.tickets]