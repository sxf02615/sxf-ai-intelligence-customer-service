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
            "TKT",  # No content after TKT
            "123456",  # No prefix
            "TKT-123",  # Invalid character (-)
            "TKT@123",  # Invalid character (@)
            "TKT#abc",  # Invalid character (#)
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


# =============================================================================
# Property Tests for Core Services (Task 2.5)
# =============================================================================

class TestIntentRecognitionRoundTrip(unittest.TestCase):
    """Property 4: Intent recognition round-trip (parse → print → parse)
    
    Validates: Requirements FR2.1
    FR2.1: 系统必须使用 LangChain + Pydantic 进行结构化输出
    """

    def test_intent_result_serialization_round_trip(self):
        """IntentResult should survive serialization and deserialization."""
        from app.models import IntentResult, IntentType, IntentEntities
        
        # Create an IntentResult
        original = IntentResult(
            intent=IntentType.LOGISTICS,
            confidence=0.85,
            entities=IntentEntities(order_id="ORD001", user_detail="查询物流"),
            needs_clarification=False,
        )
        
        # Serialize to dict
        data = original.model_dump()
        
        # Deserialize back
        restored = IntentResult.model_validate(data)
        
        # Verify all fields match
        self.assertEqual(restored.intent, original.intent)
        self.assertEqual(restored.confidence, original.confidence)
        self.assertEqual(restored.entities.order_id, original.entities.order_id)
        self.assertEqual(restored.entities.user_detail, original.entities.user_detail)
        self.assertEqual(restored.needs_clarification, original.needs_clarification)

    def test_intent_entities_serialization_round_trip(self):
        """IntentEntities should survive serialization and deserialization."""
        from app.models import IntentEntities
        
        # Test with various entity combinations
        test_cases = [
            IntentEntities(order_id="ORD001", user_detail=None),
            IntentEntities(order_id=None, user_detail="催单原因"),
            IntentEntities(order_id="ORD002", user_detail="取消订单"),
            IntentEntities(order_id=None, user_detail=None),
        ]
        
        for original in test_cases:
            data = original.model_dump()
            restored = IntentEntities.model_validate(data)
            self.assertEqual(restored.order_id, original.order_id)
            self.assertEqual(restored.user_detail, original.user_detail)

    def test_intent_type_serialization_round_trip(self):
        """IntentType enum should survive serialization and deserialization."""
        from app.models import IntentType
        
        intent_types = [IntentType.LOGISTICS, IntentType.URGENT, IntentType.CANCEL]
        
        for intent in intent_types:
            # Serialize to string
            serialized = intent.value
            # Deserialize back
            restored = IntentType(serialized)
            self.assertEqual(restored, intent)


class TestLogisticsInfoCompleteness(unittest.TestCase):
    """Property 5: Logistics info completeness
    
    Validates: Requirements FR3.4
    FR3.4: 系统必须输出格式化物流信息，包括：最新状态、预计送达时间、最近 3 条轨迹
    """

    def test_logistics_info_contains_all_required_fields(self):
        """LogisticsInfo should always contain all required fields."""
        from app.models import LogisticsInfo, OrderStatus, TrackingEvent
        from datetime import datetime
        
        # Create a complete LogisticsInfo
        tracking_events = [
            TrackingEvent(
                status="Package shipped",
                timestamp=datetime.now(),
                location="Shanghai",
            )
        ]
        
        info = LogisticsInfo(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            latest_status="Package shipped",
            estimated_delivery=datetime.now(),
            tracking_history=tracking_events,
        )
        
        # Verify all fields are present
        self.assertIsNotNone(info.order_id)
        self.assertIsNotNone(info.status)
        self.assertIsNotNone(info.latest_status)
        self.assertIsNotNone(info.tracking_history)

    def test_logistics_info_tracking_history_stored(self):
        """LogisticsInfo should store tracking history correctly."""
        from app.models import LogisticsInfo, OrderStatus, TrackingEvent
        from datetime import datetime, timedelta
        
        # Create multiple tracking events
        events = [
            TrackingEvent(
                status=f"Event {i}",
                timestamp=datetime.now() - timedelta(hours=i),
                location=f"Location {i}",
            )
            for i in range(5)
        ]
        
        info = LogisticsInfo(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            latest_status="Latest event",
            estimated_delivery=None,
            tracking_history=events,
        )
        
        # Verify tracking history is stored
        self.assertEqual(len(info.tracking_history), 5)

    def test_logistics_info_empty_tracking_history(self):
        """LogisticsInfo should handle empty tracking history."""
        from app.models import LogisticsInfo, OrderStatus
        
        info = LogisticsInfo(
            order_id="ORD001",
            status=OrderStatus.PENDING,
            latest_status="Order pending",
            estimated_delivery=None,
            tracking_history=[],
        )
        
        # Verify empty tracking history is handled
        self.assertEqual(info.tracking_history, [])
        self.assertEqual(len(info.tracking_history), 0)


class TestTicketCreationIdempotence(unittest.TestCase):
    """Property 6: Ticket creation idempotence
    
    Validates: Requirements FR4.2
    FR4.2: 系统必须创建工单（Ticket）并保存到存储
    """

    def test_ticket_creation_produces_unique_ids(self):
        """Each ticket creation should produce a unique ticket ID."""
        from app.services.urgent import UrgentService
        from app.repositories.base import TicketRepository
        from app.models import Ticket, TicketPriority, TicketStatus
        from datetime import datetime
        
        # Create a mock repository
        class MockTicketRepository(TicketRepository):
            def __init__(self):
                self.tickets = {}
                self.order_tickets = {}
                
            def create(self, ticket: Ticket) -> Ticket:
                self.tickets[ticket.ticket_id] = ticket
                if ticket.order_id not in self.order_tickets:
                    self.order_tickets[ticket.order_id] = []
                self.order_tickets[ticket.order_id].append(ticket.ticket_id)
                return ticket
                
            def get_by_id(self, ticket_id: str):
                return self.tickets.get(ticket_id)
                
            def list_by_order(self, order_id: str):
                ticket_ids = self.order_tickets.get(order_id, [])
                return [self.tickets[tid] for tid in ticket_ids if tid in self.tickets]
        
        repo = MockTicketRepository()
        service = UrgentService(repo)
        
        # Create multiple tickets for the same order
        ticket_ids = []
        for i in range(5):
            result = service.create_urgent_ticket(
                order_id="ORD001",
                reason=f"催单原因 {i}"
            )
            ticket_ids.append(result["ticket_id"])
        
        # All ticket IDs should be unique
        self.assertEqual(len(ticket_ids), len(set(ticket_ids)), "Ticket IDs should be unique")

    def test_ticket_creation_produces_valid_format(self):
        """Each ticket creation should produce a valid TKT+timestamp format."""
        from app.services.urgent import UrgentService
        from app.repositories.base import TicketRepository
        from app.models import Ticket, TicketPriority, TicketStatus
        from datetime import datetime
        
        class MockTicketRepository(TicketRepository):
            def __init__(self):
                self.tickets = {}
                self.order_tickets = {}
                
            def create(self, ticket: Ticket) -> Ticket:
                self.tickets[ticket.ticket_id] = ticket
                if ticket.order_id not in self.order_tickets:
                    self.order_tickets[ticket.order_id] = []
                self.order_tickets[ticket.order_id].append(ticket.ticket_id)
                return ticket
                
            def get_by_id(self, ticket_id: str):
                return self.tickets.get(ticket_id)
                
            def list_by_order(self, order_id: str):
                ticket_ids = self.order_tickets.get(order_id, [])
                return [self.tickets[tid] for tid in ticket_ids if tid in self.tickets]
        
        repo = MockTicketRepository()
        service = UrgentService(repo)
        
        # Create a ticket
        result = service.create_urgent_ticket(
            order_id="ORD001",
            reason="测试催单"
        )
        
        # Verify ticket ID format
        ticket_id = result["ticket_id"]
        self.assertTrue(ticket_id.startswith("TKT"), f"Ticket ID should start with 'TKT', got {ticket_id}")
        self.assertGreater(len(ticket_id), 3, f"Ticket ID should have content after 'TKT', got {ticket_id}")
        # After TKT, should have timestamp (digits) + optional UUID suffix (alphanumeric)
        suffix = ticket_id[3:]
        # First part should be digits (timestamp)
        timestamp_part = ''.join(filter(str.isdigit, suffix))
        self.assertGreater(len(timestamp_part), 0, f"Ticket ID should have numeric timestamp, got {ticket_id}")

    def test_ticket_repository_idempotence(self):
        """Creating the same ticket twice should produce different IDs."""
        from app.repositories.base import TicketRepository
        from app.models import Ticket, TicketPriority, TicketStatus
        from datetime import datetime
        
        class MockTicketRepository(TicketRepository):
            def __init__(self):
                self.tickets = {}
                self.order_tickets = {}
                
            def create(self, ticket: Ticket) -> Ticket:
                self.tickets[ticket.ticket_id] = ticket
                if ticket.order_id not in self.order_tickets:
                    self.order_tickets[ticket.order_id] = []
                self.order_tickets[ticket.order_id].append(ticket.ticket_id)
                return ticket
                
            def get_by_id(self, ticket_id: str):
                return self.tickets.get(ticket_id)
                
            def list_by_order(self, order_id: str):
                ticket_ids = self.order_tickets.get(order_id, [])
                return [self.tickets[tid] for tid in ticket_ids if tid in self.tickets]
        
        repo = MockTicketRepository()
        
        # Create ticket with same parameters twice
        from app.services.urgent import UrgentService
        service = UrgentService(repo)
        
        result1 = service.create_urgent_ticket(order_id="ORD001", reason="原因")
        result2 = service.create_urgent_ticket(order_id="ORD001", reason="原因")
        
        # IDs should be different due to timestamp
        self.assertNotEqual(result1["ticket_id"], result2["ticket_id"], "Same input should produce different ticket IDs")


class TestCancelOrderStateMachine(unittest.TestCase):
    """Property 7: Cancel order state machine
    
    Validates: Requirements FR5.2, FR5.3
    FR5.2: 系统必须校验订单状态
    FR5.3: 系统必须调用取消 API 并更新订单状态
    """

    def test_cancel_cancelled_order_fails(self):
        """Attempting to cancel an already cancelled order should fail."""
        from app.services.cancel import CancelService
        from app.repositories.base import OrderRepository
        from app.models import Order, OrderStatus
        from datetime import datetime
        
        class MockOrderRepository(OrderRepository):
            def __init__(self):
                self.orders = {
                    "ORD003": Order(
                        order_id="ORD003",
                        status=OrderStatus.CANCELLED,
                        amount=99.00,
                        created_at=datetime.now(),
                    ),
                }
                
            def get_by_id(self, order_id: str):
                return self.orders.get(order_id)
                
            def update_status(self, order_id: str, status: str):
                if order_id in self.orders:
                    try:
                        self.orders[order_id].status = OrderStatus(status)
                        return True
                    except ValueError:
                        return False
                return False
                
            def cancel(self, order_id: str, reason: str):
                order = self.orders.get(order_id)
                if not order:
                    return {"success": False, "order_id": order_id, "message": "Order not found"}
                if order.status == OrderStatus.CANCELLED:
                    return {"success": False, "order_id": order_id, "message": "Order is already cancelled"}
                return {"success": True, "order_id": order_id}
        
        repo = MockOrderRepository()
        service = CancelService(repo)
        
        result = service.cancel_order("ORD003", "用户请求取消")
        
        self.assertFalse(result.success, "Cancelling already cancelled order should fail")
        self.assertIn("already cancelled", result.message.lower())

    def test_cancel_delivered_order_fails(self):
        """Attempting to cancel a delivered order should fail."""
        from app.services.cancel import CancelService
        from app.repositories.base import OrderRepository
        from app.models import Order, OrderStatus
        from datetime import datetime
        
        class MockOrderRepository(OrderRepository):
            def __init__(self):
                self.orders = {
                    "ORD002": Order(
                        order_id="ORD002",
                        status=OrderStatus.DELIVERED,
                        amount=299.00,
                        created_at=datetime.now(),
                    ),
                }
                
            def get_by_id(self, order_id: str):
                return self.orders.get(order_id)
                
            def update_status(self, order_id: str, status: str):
                if order_id in self.orders:
                    try:
                        self.orders[order_id].status = OrderStatus(status)
                        return True
                    except ValueError:
                        return False
                return False
                
            def cancel(self, order_id: str, reason: str):
                order = self.orders.get(order_id)
                if not order:
                    return {"success": False, "order_id": order_id, "message": "Order not found"}
                if order.status == OrderStatus.DELIVERED:
                    return {"success": False, "order_id": order_id, "message": "Order is delivered, please use after-sales return process"}
                return {"success": True, "order_id": order_id}
        
        repo = MockOrderRepository()
        service = CancelService(repo)
        
        result = service.cancel_order("ORD002", "用户请求取消")
        
        self.assertFalse(result.success, "Cancelling delivered order should fail")
        self.assertTrue(
            "delivered" in result.message.lower() or "after-sales" in result.message.lower()
        )

    def test_cancel_pending_order_succeeds(self):
        """Cancelling a pending order should succeed."""
        from app.services.cancel import CancelService
        from app.repositories.base import OrderRepository
        from app.models import Order, OrderStatus
        from datetime import datetime
        
        class MockOrderRepository(OrderRepository):
            def __init__(self):
                self.orders = {
                    "ORD004": Order(
                        order_id="ORD004",
                        status=OrderStatus.PENDING,
                        amount=150.00,
                        created_at=datetime.now(),
                    ),
                }
                
            def get_by_id(self, order_id: str):
                return self.orders.get(order_id)
                
            def update_status(self, order_id: str, status: str):
                if order_id in self.orders:
                    try:
                        self.orders[order_id].status = OrderStatus(status)
                        return True
                    except ValueError:
                        return False
                return False
                
            def cancel(self, order_id: str, reason: str):
                order = self.orders.get(order_id)
                if not order:
                    return {"success": False, "order_id": order_id, "message": "Order not found"}
                if order.status == OrderStatus.CANCELLED:
                    return {"success": False, "order_id": order_id, "message": "Order is already cancelled"}
                if order.status == OrderStatus.DELIVERED:
                    return {"success": False, "order_id": order_id, "message": "Order is delivered"}
                # Process cancellation
                self.orders[order_id].status = OrderStatus.CANCELLED
                return {
                    "success": True,
                    "order_id": order_id,
                    "refund_amount": order.amount,
                    "message": "Order cancelled successfully",
                }
        
        repo = MockOrderRepository()
        service = CancelService(repo)
        
        result = service.cancel_order("ORD004", "用户请求取消")
        
        self.assertTrue(result.success, "Cancelling pending order should succeed")
        self.assertEqual(result.refund_amount, 150.00)

    def test_cancel_processing_order_succeeds(self):
        """Cancelling a processing order should succeed."""
        from app.services.cancel import CancelService
        from app.repositories.base import OrderRepository
        from app.models import Order, OrderStatus
        from datetime import datetime
        
        class MockOrderRepository(OrderRepository):
            def __init__(self):
                self.orders = {
                    "ORD005": Order(
                        order_id="ORD005",
                        status=OrderStatus.PROCESSING,
                        amount=250.00,
                        created_at=datetime.now(),
                    ),
                }
                
            def get_by_id(self, order_id: str):
                return self.orders.get(order_id)
                
            def update_status(self, order_id: str, status: str):
                if order_id in self.orders:
                    try:
                        self.orders[order_id].status = OrderStatus(status)
                        return True
                    except ValueError:
                        return False
                return False
                
            def cancel(self, order_id: str, reason: str):
                order = self.orders.get(order_id)
                if not order:
                    return {"success": False, "order_id": order_id, "message": "Order not found"}
                if order.status == OrderStatus.CANCELLED:
                    return {"success": False, "order_id": order_id, "message": "Order is already cancelled"}
                if order.status == OrderStatus.DELIVERED:
                    return {"success": False, "order_id": order_id, "message": "Order is delivered"}
                # Process cancellation
                self.orders[order_id].status = OrderStatus.CANCELLED
                return {
                    "success": True,
                    "order_id": order_id,
                    "refund_amount": order.amount,
                    "message": "Order cancelled successfully",
                }
        
        repo = MockOrderRepository()
        service = CancelService(repo)
        
        result = service.cancel_order("ORD005", "用户请求取消")
        
        self.assertTrue(result.success, "Cancelling processing order should succeed")
        self.assertEqual(result.refund_amount, 250.00)

    def test_cancel_shipped_order_succeeds(self):
        """Cancelling a shipped order should succeed."""
        from app.services.cancel import CancelService
        from app.repositories.base import OrderRepository
        from app.models import Order, OrderStatus
        from datetime import datetime
        
        class MockOrderRepository(OrderRepository):
            def __init__(self):
                self.orders = {
                    "ORD006": Order(
                        order_id="ORD006",
                        status=OrderStatus.SHIPPED,
                        amount=350.00,
                        created_at=datetime.now(),
                    ),
                }
                
            def get_by_id(self, order_id: str):
                return self.orders.get(order_id)
                
            def update_status(self, order_id: str, status: str):
                if order_id in self.orders:
                    try:
                        self.orders[order_id].status = OrderStatus(status)
                        return True
                    except ValueError:
                        return False
                return False
                
            def cancel(self, order_id: str, reason: str):
                order = self.orders.get(order_id)
                if not order:
                    return {"success": False, "order_id": order_id, "message": "Order not found"}
                if order.status == OrderStatus.CANCELLED:
                    return {"success": False, "order_id": order_id, "message": "Order is already cancelled"}
                if order.status == OrderStatus.DELIVERED:
                    return {"success": False, "order_id": order_id, "message": "Order is delivered"}
                # Process cancellation
                self.orders[order_id].status = OrderStatus.CANCELLED
                return {
                    "success": True,
                    "order_id": order_id,
                    "refund_amount": order.amount,
                    "message": "Order cancelled successfully",
                }
        
        repo = MockOrderRepository()
        service = CancelService(repo)
        
        result = service.cancel_order("ORD006", "用户请求取消")
        
        self.assertTrue(result.success, "Cancelling shipped order should succeed")
        self.assertEqual(result.refund_amount, 350.00)


class TestApiResponseFormatConsistency(unittest.TestCase):
    """Property 8: API response format consistency.
    
    Validates: Requirements NFR1
    NFR1: UI 层必须使用 Python FastAPI + HTML
    
    This property ensures all API responses follow a consistent format:
    - success: boolean indicating if the operation was successful
    - data: dict containing response data on success
    - error: string containing error code on failure
    - message: string containing human-readable message
    """
    
    def setUp(self):
        """Set up test client."""
        from app.main import app
        from app.api.routes import router
        from fastapi.testclient import TestClient
        
        app.include_router(router, prefix="/api/v1")
        self.client = TestClient(app)
    
    def _generate_valid_order_id(self):
        """Generate a valid order ID for testing."""
        import random
        return f"ORD{random.randint(1, 999999)}"
    
    def _generate_invalid_order_id(self):
        """Generate various invalid order ID formats."""
        import random
        invalid_formats = [
            "",  # Empty
            "ORD",  # No number
            "ord001",  # Lowercase
            "ORD001abc",  # Extra characters
            "ORD001!",  # Special character
            "001",  # No prefix
            "order001",  # Wrong prefix
            "ORD-001",  # Hyphen instead of number
            "ORD_001",  # Underscore
            "  ORD001",  # Leading space
            "ORD001  ",  # Trailing space
            "ORD",  # Just prefix
            f"ORD{random.randint(1000, 9999)}abc",  # Mixed
        ]
        return random.choice(invalid_formats)
    
    def test_logistics_response_format_consistency(self):
        """All logistics responses must follow consistent format."""
        import re
        import random
        
        # Test with valid order IDs
        valid_order_ids = [f"ORD{i:03d}" for i in range(1, 100)]
        
        for order_id in valid_order_ids:
            with self.subTest(order_id=order_id):
                response = self.client.get(f"/api/v1/logistics/{order_id}")
                data = response.json()
                
                # Verify response has required fields
                self.assertIn("success", data, f"Response missing 'success' field for {order_id}")
                self.assertIsInstance(data["success"], bool, f"'success' must be boolean for {order_id}")
                
                if data["success"]:
                    self.assertIn("data", data, f"Success response must have 'data' field for {order_id}")
                    self.assertIsInstance(data["data"], dict, f"'data' must be dict for {order_id}")
                else:
                    self.assertIn("error", data, f"Error response must have 'error' field for {order_id}")
                    self.assertIn("message", data, f"Error response must have 'message' field for {order_id}")
    
    def test_urgent_ticket_response_format_consistency(self):
        """All urgent ticket responses must follow consistent format."""
        import random
        
        # Test with various order IDs
        order_ids = [f"ORD{i:03d}" for i in range(1, 50)]
        
        for order_id in order_ids:
            with self.subTest(order_id=order_id):
                response = self.client.post(
                    "/api/v1/tickets/urgent",
                    json={"order_id": order_id}
                )
                data = response.json()
                
                # Verify response has required fields
                self.assertIn("success", data, f"Response missing 'success' field for {order_id}")
                self.assertIsInstance(data["success"], bool, f"'success' must be boolean for {order_id}")
                
                if data["success"]:
                    self.assertIn("data", data, f"Success response must have 'data' field for {order_id}")
                    self.assertIsInstance(data["data"], dict, f"'data' must be dict for {order_id}")
                    # Verify data contains expected fields
                    self.assertIn("ticket_id", data["data"], f"Data must contain 'ticket_id' for {order_id}")
                    self.assertIn("estimated_processing_time", data["data"], f"Data must contain 'estimated_processing_time' for {order_id}")
                    self.assertIn("contact", data["data"], f"Data must contain 'contact' for {order_id}")
                else:
                    self.assertIn("error", data, f"Error response must have 'error' field for {order_id}")
    
    def test_cancel_order_response_format_consistency(self):
        """All cancel order responses must follow consistent format."""
        import random
        
        # Test with various order IDs
        order_ids = [f"ORD{i:03d}" for i in range(1, 50)]
        
        for order_id in order_ids:
            with self.subTest(order_id=order_id):
                response = self.client.post(
                    "/api/v1/orders/cancel",
                    json={"order_id": order_id, "reason": "测试取消"}
                )
                data = response.json()
                
                # Verify response has required fields
                self.assertIn("success", data, f"Response missing 'success' field for {order_id}")
                self.assertIsInstance(data["success"], bool, f"'success' must be boolean for {order_id}")
                
                # Cancel order endpoint always returns data with message
                self.assertIn("data", data, f"Response must have 'data' field for {order_id}")
                self.assertIsInstance(data["data"], dict, f"'data' must be dict for {order_id}")
                self.assertIn("order_id", data["data"], f"Data must contain 'order_id' for {order_id}")
                self.assertIn("refund_amount", data["data"], f"Data must contain 'refund_amount' for {order_id}")
                self.assertIn("message", data["data"], f"Data must contain 'message' for {order_id}")
    
    def test_chat_response_format_consistency(self):
        """All chat responses must follow consistent format."""
        import random
        
        # Test with various messages
        messages = [
            "查询物流",
            "催单",
            "取消订单",
            "我的订单到哪了",
            "帮我看看ORD001",
        ]
        
        for message in messages:
            with self.subTest(message=message):
                response = self.client.post(
                    "/api/v1/chat",
                    json={
                        "session_id": f"sess_{random.randint(1, 1000)}",
                        "user_id": f"user_{random.randint(1, 100)}",
                        "message": message
                    }
                )
                data = response.json()
                
                # Verify response has required fields
                self.assertIn("success", data, f"Response missing 'success' field for message: {message}")
                self.assertIsInstance(data["success"], bool, f"'success' must be boolean for {message}")
                self.assertIn("response", data, f"Response missing 'response' field for {message}")
                self.assertIn("intent", data, f"Response missing 'intent' field for {message}")
                self.assertIn("session_id", data, f"Response missing 'session_id' field for {message}")


class TestOrderIdFormatValidation(unittest.TestCase):
    """Property 9: Order ID format validation.
    
    Validates: Requirements FR2.3
    FR2.3: 系统必须提取订单号实体（格式：ORD+数字）
    
    This property ensures order ID format validation works correctly:
    - Valid format: ORD followed by digits (e.g., ORD001, ORD12345)
    - Invalid formats are rejected with appropriate error messages
    """
    
    def setUp(self):
        """Set up test client."""
        from app.main import app
        from app.api.routes import router
        from fastapi.testclient import TestClient
        
        app.include_router(router, prefix="/api/v1")
        self.client = TestClient(app)
    
    def test_valid_order_id_formats_accepted(self):
        """All valid order ID formats (ORD+digits) should be accepted."""
        import random
        
        # Generate valid order IDs
        valid_order_ids = []
        for i in range(1, 1000):
            valid_order_ids.append(f"ORD{i:03d}")
        
        for order_id in valid_order_ids:
            with self.subTest(order_id=order_id):
                response = self.client.get(f"/api/v1/logistics/{order_id}")
                data = response.json()
                
                # Should not get format error
                self.assertNotEqual(
                    data.get("error"), 
                    "Invalid order ID format",
                    f"Valid order ID {order_id} was rejected"
                )
    
    def test_invalid_order_id_formats_rejected(self):
        """All invalid order ID formats should be rejected with format error."""
        import random
        
        # Generate invalid order IDs (excluding non-printable characters that can't be tested via HTTP)
        invalid_order_ids = [
            "ORD",  # No number
            "ord001",  # Lowercase
            "ORD001abc",  # Extra characters
            "ORD001!",  # Special character
            "001",  # No prefix
            "order001",  # Wrong prefix
            "ORD-001",  # Hyphen
            "ORD_001",  # Underscore
            "  ORD001",  # Leading space
            "ORD001  ",  # Trailing space
            "OR-D001",  # Hyphen in middle
            "ORD 001",  # Space in middle
        ]
        
        for order_id in invalid_order_ids:
            with self.subTest(order_id=order_id):
                response = self.client.get(f"/api/v1/logistics/{order_id}")
                data = response.json()
                
                # Should get format error
                self.assertEqual(
                    data.get("error"),
                    "Invalid order ID format",
                    f"Invalid order ID '{order_id}' should be rejected with format error"
                )
                self.assertIn("订单号格式不正确", data.get("message", ""))
    
    def test_order_id_regex_pattern_compliance(self):
        """Order IDs must match the regex pattern ^ORD\\d+$."""
        import re
        
        # Define the expected pattern
        pattern = re.compile(r'^ORD\d+$')
        
        # Test cases
        test_cases = [
            # (order_id, should_match)
            ("ORD001", True),
            ("ORD12345", True),
            ("ORD999999", True),
            ("ord001", False),
            ("ORD001abc", False),
            ("ORD", False),
            ("001", False),
            ("ORD-001", False),
            ("ORD_001", False),
            ("  ORD001", False),
            ("ORD001  ", False),
        ]
        
        for order_id, should_match in test_cases:
            with self.subTest(order_id=order_id):
                matches = bool(pattern.match(order_id))
                self.assertEqual(
                    matches, 
                    should_match,
                    f"Order ID '{order_id}' regex match mismatch: expected {should_match}, got {matches}"
                )
    
    def test_order_id_extraction_from_various_inputs(self):
        """Order ID extraction should work with various input formats."""
        import random
        import re
        
        # Test inputs with order IDs embedded
        test_inputs = [
            "我的订单ORD001到哪了",
            "查询ORD123物流信息",
            "ORD456什么时候送达",
            "帮我看看ORD789",
            "ORD001的状态",
            "ORD999999的物流",
        ]
        
        # Expected pattern for extraction
        extract_pattern = re.compile(r'ORD\d+')
        
        for message in test_inputs:
            with self.subTest(message=message):
                # Extract order ID from message
                match = extract_pattern.search(message)
                if match:
                    extracted_id = match.group()
                    
                    # Verify extracted ID is valid
                    self.assertTrue(
                        bool(re.match(r'^ORD\d+$', extracted_id)),
                        f"Extracted order ID '{extracted_id}' from '{message}' is not valid"
                    )
                    
                    # Verify the API accepts this order ID
                    response = self.client.get(f"/api/v1/logistics/{extracted_id}")
                    data = response.json()
                    
                    # Should not get format error (might get order not found)
                    self.assertNotEqual(
                        data.get("error"),
                        "Invalid order ID format",
                        f"Extracted order ID '{extracted_id}' was rejected by API"
                    )


if __name__ == '__main__':
    unittest.main()