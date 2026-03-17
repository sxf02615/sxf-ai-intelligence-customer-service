"""Urgent Ticket Service for handling ticket creation and management.

This service handles urgent ticket operations including ticket creation,
priority assignment, estimated processing time calculation, and
customer service notification.
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

# Configure logger for customer service notifications
logger = logging.getLogger(__name__)


class UrgentService:
    """Service for handling urgent ticket operations."""

    # Customer service contact information
    CUSTOMER_SERVICE_CONTACT = "400-123-4567"

    # Estimated processing time in hours by priority
    PROCESSING_TIME_HOURS = {
        TicketPriority.HIGH: 2,   # 2 hours for high priority
        TicketPriority.MEDIUM: 4,  # 4 hours for medium priority
        TicketPriority.LOW: 8,     # 8 hours for low priority
    }

    def __init__(self, ticket_repository: TicketRepository):
        """Initialize the urgent ticket service.

        Args:
            ticket_repository: Repository for ticket data access.
        """
        self.ticket_repository = ticket_repository

    def create_urgent_ticket(
        self,
        order_id: str,
        reason: Optional[str] = None,
    ) -> dict:
        """Create an urgent ticket for an order.

        Args:
            order_id: The order ID to create ticket for.
            reason: Optional reason for the urgent ticket.

        Returns:
            Dict with ticket_id, estimated_processing_time, and contact info.
        """
        # Generate ticket ID with TKT+timestamp format
        ticket_id = self._generate_ticket_id()

        # Determine priority based on reason content
        priority = self._determine_priority(reason)

        # Calculate estimated processing time
        estimated_processing_time = self._calculate_estimated_processing_time(priority)

        # Create ticket
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

        # Save ticket to repository
        created_ticket = self.ticket_repository.create(ticket)

        # Notify customer service (log notification)
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
        """Generate a unique ticket ID with TKT+timestamp format.

        Returns:
            Ticket ID string in format TKT+timestamp.
        """
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        return f"TKT{timestamp}"

    def _determine_priority(self, reason: Optional[str]) -> TicketPriority:
        """Determine ticket priority based on reason content.

        Args:
            reason: The reason for creating the urgent ticket.

        Returns:
            TicketPriority based on reason analysis.
        """
        if not reason:
            # Default to medium priority if no reason provided
            return TicketPriority.MEDIUM

        reason_lower = reason.lower()

        # High priority keywords
        high_priority_keywords = [
            "紧急", "非常急", "马上", "立刻", "尽快",
            "urgent", "asap", "immediately", "emergency",
        ]

        # Low priority keywords
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

        # Default to medium priority
        return TicketPriority.MEDIUM

    def _calculate_estimated_processing_time(
        self,
        priority: TicketPriority,
    ) -> datetime:
        """Calculate estimated processing time based on priority.

        Args:
            priority: The ticket priority level.

        Returns:
            Estimated processing datetime.
        """
        hours = self.PROCESSING_TIME_HOURS.get(priority, self.PROCESSING_TIME_HOURS[TicketPriority.MEDIUM])
        return datetime.now() + timedelta(hours=hours)

    def _notify_customer_service(self, ticket: Ticket) -> None:
        """Send notification to customer service.

        Args:
            ticket: The created ticket to notify about.
        """
        notification_message = (
            f"[Customer Service Notification] New urgent ticket created:\n"
            f"  Ticket ID: {ticket.ticket_id}\n"
            f"  Order ID: {ticket.order_id}\n"
            f"  Priority: {ticket.priority.value}\n"
            f"  Reason: {ticket.reason or 'Not provided'}\n"
            f"  Estimated Processing Time: {ticket.estimated_processing_time.isoformat()}"
        )
        logger.info(notification_message)

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get a ticket by its ID.

        Args:
            ticket_id: The ticket ID to look up.

        Returns:
            Ticket if found, None otherwise.
        """
        return self.ticket_repository.get_by_id(ticket_id)

    def list_tickets_by_order(self, order_id: str) -> list[Ticket]:
        """List all tickets for an order.

        Args:
            order_id: The order ID to look up.

        Returns:
            List of tickets for the order.
        """
        return self.ticket_repository.list_by_order(order_id)