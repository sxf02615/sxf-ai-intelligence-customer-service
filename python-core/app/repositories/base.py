"""Repository abstract interfaces for data abstraction layer.

This module defines the abstract interfaces for data access,
allowing easy switching between mock and real data sources.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from app.models import Order, Ticket, TrackingEvent


class OrderRepository(ABC):
    """Abstract interface for order data access."""

    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by order_id.
        
        Args:
            order_id: The order ID to look up.
            
        Returns:
            Order if found, None otherwise.
        """
        pass

    @abstractmethod
    def update_status(self, order_id: str, status: str) -> bool:
        """Update order status.
        
        Args:
            order_id: The order ID to update.
            status: The new status.
            
        Returns:
            True if update successful, False otherwise.
        """
        pass

    @abstractmethod
    def cancel(self, order_id: str, reason: str) -> dict:
        """Cancel an order.
        
        Args:
            order_id: The order ID to cancel.
            reason: The cancellation reason.
            
        Returns:
            Dict with cancel result including refund info.
        """
        pass


class LogisticsRepository(ABC):
    """Abstract interface for logistics data access."""

    @abstractmethod
    def get_tracking(self, order_id: str) -> List[TrackingEvent]:
        """Get tracking events for an order.
        
        Args:
            order_id: The order ID to look up.
            
        Returns:
            List of tracking events (max 3 recent).
        """
        pass

    @abstractmethod
    def get_estimated_delivery(self, order_id: str) -> Optional[datetime]:
        """Get estimated delivery time for an order.
        
        Args:
            order_id: The order ID to look up.
            
        Returns:
            Estimated delivery datetime if available.
        """
        pass


class TicketRepository(ABC):
    """Abstract interface for ticket data access."""

    @abstractmethod
    def create(self, ticket: Ticket) -> Ticket:
        """Create a new ticket.
        
        Args:
            ticket: The ticket to create.
            
        Returns:
            The created ticket with generated ID.
        """
        pass

    @abstractmethod
    def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ticket_id.
        
        Args:
            ticket_id: The ticket ID to look up.
            
        Returns:
            Ticket if found, None otherwise.
        """
        pass

    @abstractmethod
    def list_by_order(self, order_id: str) -> List[Ticket]:
        """List all tickets for an order.
        
        Args:
            order_id: The order ID to look up.
            
        Returns:
            List of tickets for the order.
        """
        pass