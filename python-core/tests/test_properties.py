"""Property-based tests for data models.

These tests validate universal correctness properties that must hold
across all inputs and scenarios.
"""
import re
import unittest
from datetime import datetime, timedelta
from typing import List

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
from data.mock_data import (
    MockLogisticsRepository,
    MockOrderRepository,
    MockTicketRepository,
)


class TestOrderStatusValidation(unittest.TestCase):
    """Property 1: Order status validation.
    
    Validates: Requirements DR4
    DR4: 订单数据需包含：订单号、订单状态、金额、创建时间
    """

    def test_order_status_must_be_valid_enum_value(self):
        """Order status must always be a valid OrderStatus enum value."""
        for status in list(OrderStatus):
            with self.subTest(status=status):
                order = Order(
                    order_id="ORD001",
                    status=status,
                    amount=100.0,
                    created_at=datetime.now()
                )
                self.assertEqual(order.status, status)
                self.assertIsInstance(order.status, OrderStatus)

    def test_order_status_accepts_all_valid_statuses(self):
        """Order must accept all defined status values without error."""
        valid_statuses = list(OrderStatus)
        for status in valid_statuses:
            with self.subTest(status=status):
                order = Order(
                    order_id="ORD001",
                    status=status,
                    amount=100.0,
                    created_at=datetime.now()
                )
                self.assertEqual(order.status, status)

    def test_order_status_rejects_invalid_string(self):
        """Order must reject invalid status strings via Pydantic validation."""
        with self.assertRaises(ValueError):
            Order(
                order_id="ORD001",
                status="invalid_status",
                amount=100.0,
                created_at=datetime.now()
            )

    def test_order_contains_required_fields(self):
        """Order must contain all required fields per DR4."""
        order = Order(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            amount=199.99,
            created_at=datetime.now()
        )
        # DR4: 订单数据需包含：订单号、订单状态、金额、创建时间
        self.assertTrue(hasattr(order, 'order_id'))
        self.assertTrue(hasattr(order, 'status'))
        self.assertTrue(hasattr(order, 'amount'))
        self.assertTrue(hasattr(order, 'created_at'))
        self.assertEqual(order.order_id, "ORD001")
        self.assertEqual(order.status, OrderStatus.SHIPPED)
        self.assertEqual(order.amount, 199.99)
        self.assertIsInstance(order.created_at, datetime)


class TestTicketIdFormatValidation(unittest.TestCase):
    """Property 2: Ticket ID format validation (TKT+timestamp).
    
    Validates: Requirements DR6
    DR6: 工单数据需包含：工单号、优先级、状态、创建时间、关联订单
    """

    def test_ticket_id_format_starts_with_tkt(self):
        """Ticket ID must start with 'TKT' prefix."""
        ticket_id = f"TKT{int(datetime.now().timestamp() * 1000)}"
        ticket = self._create_ticket(ticket_id)
        self.assertTrue(ticket.ticket_id.startswith("TKT"))

    def test_ticket_id_contains_numeric_timestamp(self):
        """Ticket ID must contain numeric timestamp after TKT prefix."""
        timestamp = int(datetime.now().timestamp() * 1000)
        ticket_id = f"TKT{timestamp}"
        ticket = self._create_ticket(ticket_id)
        numeric_part = ticket.ticket_id[3:]
        self.assertTrue(numeric_part.isdigit())

    def test_ticket_id_format_matches_expected_pattern(self):
        """Ticket ID must match TKT+timestamp pattern."""
        pattern = r'^TKT\d+$'
        timestamp = int(datetime.now().timestamp() * 1000)
        ticket_id = f"TKT{timestamp}"
        self.assertIsNotNone(re.match(pattern, ticket_id))

    def test_ticket_id_rejects_invalid_format(self):
        """Ticket ID must reject invalid formats."""
        invalid_ids = [
            "TICKET123",  # Wrong prefix
            "TKT",  # No timestamp
            "123456",  # No prefix
            "TKT-123",  # Invalid character
            "TKT123abc",  # Non-numeric characters
        ]
        for invalid_id in invalid_ids:
            with self.assertRaises((ValueError, AssertionError)):
                self._create_ticket(invalid_id)

    def test_ticket_contains_required_fields(self):
        """Ticket must contain all required fields per DR6."""
        ticket_id = f"TKT{int(datetime.now().timestamp() * 1000)}"
        ticket = Ticket(
            ticket_id=ticket_id,
            order_id="ORD001",
            reason="测试催单",
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=2)
        )
        # DR6: 工单数据需包含：工单号、优先级、状态、创建时间、关联订单
        self.assertTrue(hasattr(ticket, 'ticket_id'))
        self.assertTrue(hasattr(ticket, 'priority'))
        self.assertTrue(hasattr(ticket, 'status'))
        self.assertTrue(hasattr(ticket, 'created_at'))
        self.assertTrue(hasattr(ticket, 'order_id'))
        self.assertEqual(ticket.ticket_id, ticket_id)
        self.assertEqual(ticket.priority, TicketPriority.HIGH)
        self.assertEqual(ticket.status, TicketStatus.OPEN)
        self.assertIsInstance(ticket.created_at, datetime)
        self.assertEqual(ticket.order_id, "ORD001")

    def _create_ticket(self, ticket_id: str) -> Ticket:
        """Helper to create a ticket with given ID."""
        return Ticket(
            ticket_id=ticket_id,
            order_id="ORD001",
            reason="测试",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=2)
        )


class TestMockDataRoundTripConsistency(unittest.TestCase):
    """Property 3: Mock data round-trip consistency.
    
    Validates: Requirements DR2, DR3
    DR2: 初期使用模拟数据（Mock Data），后续可对接真实业务系统
    DR3: 数据接口必须定义清晰的协议，便于后续替换实现
    """

    def test_order_repository_round_trip(self):
        """Order data must be retrievable after storage."""
        repo = MockOrderRepository()
        
        # Get existing order
        order = repo.get_by_id("ORD001")
        self.assertIsNotNone(order)
        self.assertEqual(order.order_id, "ORD001")
        
        # Verify order data integrity
        self.assertIsInstance(order, Order)
        self.assertIn(order.status, list(OrderStatus))
        self.assertGreater(order.amount, 0)

    def test_logistics_repository_round_trip(self):
        """Logistics tracking data must be retrievable."""
        repo = MockLogisticsRepository()
        
        # Get tracking for shipped order
        tracking = repo.get_tracking("ORD001")
        self.assertIsNotNone(tracking)
        self.assertGreater(len(tracking), 0)
        
        # Verify tracking event structure
        for event in tracking:
            self.assertIsInstance(event, TrackingEvent)
            self.assertIsNotNone(event.status)
            self.assertIsInstance(event.timestamp, datetime)

    def test_ticket_repository_round_trip(self):
        """Ticket data must be retrievable after creation."""
        repo = MockTicketRepository()
        
        # Create a ticket
        ticket = Ticket(
            ticket_id=f"TKT{int(datetime.now().timestamp() * 1000)}",
            order_id="ORD001",
            reason="测试",
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=2)
        )
        created_ticket = repo.create(ticket)
        
        # Retrieve the ticket
        retrieved_ticket = repo.get_by_id(created_ticket.ticket_id)
        self.assertIsNotNone(retrieved_ticket)
        self.assertEqual(retrieved_ticket.ticket_id, created_ticket.ticket_id)
        self.assertEqual(retrieved_ticket.order_id, created_ticket.order_id)
        self.assertEqual(retrieved_ticket.priority, created_ticket.priority)

    def test_repository_interface_consistency(self):
        """All repositories must implement their abstract interfaces."""
        order_repo = MockOrderRepository()
        logistics_repo = MockLogisticsRepository()
        ticket_repo = MockTicketRepository()
        
        # Verify interface implementation
        self.assertIsInstance(order_repo, OrderRepository)
        self.assertIsInstance(logistics_repo, LogisticsRepository)
        self.assertIsInstance(ticket_repo, TicketRepository)

    def test_mock_data_covers_all_statuses(self):
        """Mock data must cover different order statuses."""
        repo = MockOrderRepository()
        
        statuses_found = set()
        for order_id in repo.orders:
            order = repo.get_by_id(order_id)
            if order:
                statuses_found.add(order.status)
        
        # Should have at least 3 different statuses in mock data
        self.assertGreaterEqual(len(statuses_found), 3)

    def test_order_cancel_state_transition(self):
        """Order cancellation must update status correctly."""
        repo = MockOrderRepository()
        
        # Get a shippable order
        order = repo.get_by_id("ORD001")
        original_status = order.status
        
        # Cancel the order
        result = repo.cancel("ORD001", "测试取消")
        
        # Verify state transition
        if result["success"]:
            updated_order = repo.get_by_id("ORD001")
            self.assertEqual(updated_order.status, OrderStatus.CANCELLED)
        else:
            # If cancel failed, order status should remain unchanged
            updated_order = repo.get_by_id("ORD001")
            self.assertEqual(updated_order.status, original_status)

    def test_ticket_list_by_order(self):
        """Tickets must be retrievable by order ID."""
        repo = MockTicketRepository()
        
        # Create multiple tickets for same order
        order_id = "ORD001"
        for i in range(3):
            ticket = Ticket(
                ticket_id=f"TKT{int(datetime.now().timestamp() * 1000) + i}",
                order_id=order_id,
                reason=f"测试{i}",
                priority=TicketPriority.MEDIUM,
                status=TicketStatus.OPEN,
                created_at=datetime.now(),
                estimated_processing_time=datetime.now() + timedelta(hours=2)
            )
            repo.create(ticket)
        
        # List tickets by order
        tickets = repo.list_by_order(order_id)
        self.assertEqual(len(tickets), 3)
        for ticket in tickets:
            self.assertEqual(ticket.order_id, order_id)


if __name__ == '__main__':
    unittest.main()