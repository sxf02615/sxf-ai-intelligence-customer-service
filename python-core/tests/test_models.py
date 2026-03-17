from datetime import datetime, timedelta
from unittest import TestCase

from app.models import (
    Order,
    OrderStatus,
    LogisticsInfo,
    TrackingEvent,
    Ticket,
    TicketPriority,
    TicketStatus,
    IntentType,
    IntentEntities,
    IntentResult,
)


class TestOrderModel(TestCase):
    """Test Order model"""

    def test_create_order(self):
        """Test creating an order with valid data"""
        order = Order(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            amount=199.99,
            created_at=datetime.now()
        )
        self.assertEqual(order.order_id, "ORD001")
        self.assertEqual(order.status, OrderStatus.SHIPPED)
        self.assertEqual(order.amount, 199.99)

    def test_order_status_enum(self):
        """Test order status enum values"""
        self.assertEqual(OrderStatus.PENDING.value, "pending")
        self.assertEqual(OrderStatus.PROCESSING.value, "processing")
        self.assertEqual(OrderStatus.SHIPPED.value, "shipped")
        self.assertEqual(OrderStatus.DELIVERED.value, "delivered")
        self.assertEqual(OrderStatus.CANCELLED.value, "cancelled")


class TestLogisticsInfoModel(TestCase):
    """Test LogisticsInfo model"""

    def test_create_logistics_info(self):
        """Test creating logistics info with valid data"""
        tracking_events = [
            TrackingEvent(status="已发货", timestamp=datetime.now() - timedelta(days=2)),
            TrackingEvent(status="运输中", timestamp=datetime.now() - timedelta(days=1)),
            TrackingEvent(status="派送中", timestamp=datetime.now()),
        ]
        logistics = LogisticsInfo(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            latest_status="派送中",
            estimated_delivery=datetime.now() + timedelta(days=1),
            tracking_history=tracking_events
        )
        self.assertEqual(logistics.order_id, "ORD001")
        self.assertEqual(len(logistics.tracking_history), 3)

    def test_logistics_info_empty_tracking(self):
        """Test logistics info with empty tracking history"""
        logistics = LogisticsInfo(
            order_id="ORD002",
            status=OrderStatus.PENDING,
            latest_status="待发货",
            tracking_history=[]
        )
        self.assertEqual(len(logistics.tracking_history), 0)


class TestTicketModel(TestCase):
    """Test Ticket model"""

    def test_create_ticket(self):
        """Test creating a ticket with valid data"""
        ticket = Ticket(
            ticket_id="TKT1700000000000",
            order_id="ORD001",
            reason="订单催办",
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=2)
        )
        self.assertEqual(ticket.ticket_id, "TKT1700000000000")
        self.assertEqual(ticket.priority, TicketPriority.HIGH)
        self.assertEqual(ticket.status, TicketStatus.OPEN)

    def test_ticket_priority_enum(self):
        """Test ticket priority enum values"""
        self.assertEqual(TicketPriority.LOW.value, "low")
        self.assertEqual(TicketPriority.MEDIUM.value, "medium")
        self.assertEqual(TicketPriority.HIGH.value, "high")

    def test_ticket_status_enum(self):
        """Test ticket status enum values"""
        self.assertEqual(TicketStatus.OPEN.value, "open")
        self.assertEqual(TicketStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(TicketStatus.RESOLVED.value, "resolved")


class TestIntentModels(TestCase):
    """Test Intent models"""

    def test_intent_type_enum(self):
        """Test intent type enum values"""
        self.assertEqual(IntentType.LOGISTICS.value, "logistics")
        self.assertEqual(IntentType.URGENT.value, "urgent")
        self.assertEqual(IntentType.CANCEL.value, "cancel")

    def test_intent_entities(self):
        """Test intent entities model"""
        entities = IntentEntities(
            order_id="ORD001",
            user_detail="查询物流状态"
        )
        self.assertEqual(entities.order_id, "ORD001")
        self.assertEqual(entities.user_detail, "查询物流状态")

    def test_intent_entities_optional(self):
        """Test intent entities with optional fields"""
        entities = IntentEntities()
        self.assertIsNone(entities.order_id)
        self.assertIsNone(entities.user_detail)

    def test_intent_result(self):
        """Test intent result model"""
        entities = IntentEntities(order_id="ORD001")
        result = IntentResult(
            intent=IntentType.LOGISTICS,
            confidence=0.95,
            entities=entities
        )
        self.assertEqual(result.intent, IntentType.LOGISTICS)
        self.assertEqual(result.confidence, 0.95)
        self.assertFalse(result.needs_clarification)

    def test_intent_result_with_clarification(self):
        """Test intent result with clarification needed"""
        entities = IntentEntities()
        result = IntentResult(
            intent=IntentType.LOGISTICS,
            confidence=0.5,
            entities=entities,
            needs_clarification=True,
            clarification_question="请提供您的订单号"
        )
        self.assertTrue(result.needs_clarification)
        self.assertEqual(result.clarification_question, "请提供您的订单号")


class TestTrackingEventModel(TestCase):
    """Test TrackingEvent model"""

    def test_create_tracking_event(self):
        """Test creating a tracking event"""
        event = TrackingEvent(
            status="已签收",
            timestamp=datetime.now(),
            location="北京市"
        )
        self.assertEqual(event.status, "已签收")
        self.assertEqual(event.location, "北京市")

    def test_tracking_event_optional_location(self):
        """Test tracking event with optional location"""
        event = TrackingEvent(
            status="运输中",
            timestamp=datetime.now()
        )
        self.assertIsNone(event.location)