"""Tests for Logistics Service.

Tests the logistics service functionality including
order status retrieval, tracking history, and estimated delivery.
"""
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from app.models import (
    LogisticsInfo,
    Order,
    OrderStatus,
    TrackingEvent,
)
from app.services.logistics import LogisticsService


class TestLogisticsService(unittest.TestCase):
    """Test LogisticsService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_order_repo = MagicMock()
        self.mock_logistics_repo = MagicMock()
        self.service = LogisticsService(
            order_repository=self.mock_order_repo,
            logistics_repository=self.mock_logistics_repo,
        )

    def test_service_initialization(self):
        """Test service initializes with repositories."""
        self.assertIsNotNone(self.service.order_repository)
        self.assertIsNotNone(self.service.logistics_repository)

    def test_get_logistics_info_order_not_found(self):
        """Test that None is returned when order not found."""
        self.mock_order_repo.get_by_id.return_value = None
        
        result = self.service.get_logistics_info("ORD999")
        
        self.assertIsNone(result)
        self.mock_order_repo.get_by_id.assert_called_once_with("ORD999")

    def test_get_logistics_info_shipped_order(self):
        """Test logistics info for shipped order with tracking."""
        order = Order(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            amount=199.00,
            created_at=datetime.now() - timedelta(days=3),
        )
        tracking_events = [
            TrackingEvent(
                status="Package out for delivery",
                timestamp=datetime.now() - timedelta(days=1),
                location="Beijing Local Delivery Hub",
            ),
            TrackingEvent(
                status="Package in transit",
                timestamp=datetime.now() - timedelta(days=2),
                location="Nanjing Distribution Center",
            ),
        ]
        estimated_delivery = datetime.now() + timedelta(days=1)
        
        self.mock_order_repo.get_by_id.return_value = order
        self.mock_logistics_repo.get_tracking.return_value = tracking_events
        self.mock_logistics_repo.get_estimated_delivery.return_value = estimated_delivery
        
        result = self.service.get_logistics_info("ORD001")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.order_id, "ORD001")
        self.assertEqual(result.status, OrderStatus.SHIPPED)
        self.assertEqual(result.latest_status, "Package out for delivery")
        self.assertEqual(result.estimated_delivery, estimated_delivery)
        self.assertEqual(len(result.tracking_history), 2)

    def test_get_logistics_info_delivered_order(self):
        """Test logistics info for delivered order."""
        order = Order(
            order_id="ORD002",
            status=OrderStatus.DELIVERED,
            amount=299.00,
            created_at=datetime.now() - timedelta(days=7),
        )
        tracking_events = [
            TrackingEvent(
                status="Package delivered",
                timestamp=datetime.now() - timedelta(days=5),
                location="Customer Address",
            ),
        ]
        
        self.mock_order_repo.get_by_id.return_value = order
        self.mock_logistics_repo.get_tracking.return_value = tracking_events
        self.mock_logistics_repo.get_estimated_delivery.return_value = None
        
        result = self.service.get_logistics_info("ORD002")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.order_id, "ORD002")
        self.assertEqual(result.status, OrderStatus.DELIVERED)
        self.assertEqual(result.latest_status, "Package delivered")
        self.assertIsNone(result.estimated_delivery)

    def test_get_logistics_info_pending_order(self):
        """Test logistics info for pending order (no tracking)."""
        order = Order(
            order_id="ORD003",
            status=OrderStatus.PENDING,
            amount=99.00,
            created_at=datetime.now() - timedelta(days=1),
        )
        
        self.mock_order_repo.get_by_id.return_value = order
        self.mock_logistics_repo.get_tracking.return_value = []
        self.mock_logistics_repo.get_estimated_delivery.return_value = None
        
        result = self.service.get_logistics_info("ORD003")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.order_id, "ORD003")
        self.assertEqual(result.status, OrderStatus.PENDING)
        self.assertEqual(result.latest_status, "Order is pending, not yet shipped")
        self.assertEqual(len(result.tracking_history), 0)
        self.assertIsNone(result.estimated_delivery)

    def test_get_logistics_info_cancelled_order(self):
        """Test logistics info for cancelled order."""
        order = Order(
            order_id="ORD004",
            status=OrderStatus.CANCELLED,
            amount=149.00,
            created_at=datetime.now() - timedelta(days=2),
        )
        
        self.mock_order_repo.get_by_id.return_value = order
        self.mock_logistics_repo.get_tracking.return_value = []
        self.mock_logistics_repo.get_estimated_delivery.return_value = None
        
        result = self.service.get_logistics_info("ORD004")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.order_id, "ORD004")
        self.assertEqual(result.status, OrderStatus.CANCELLED)
        self.assertEqual(result.latest_status, "Order has been cancelled")
        self.assertEqual(len(result.tracking_history), 0)
        self.assertIsNone(result.estimated_delivery)

    def test_get_tracking_history_with_repository_limit(self):
        """Test that tracking history respects repository limit (max 3 events)."""
        order = Order(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            amount=199.00,
            created_at=datetime.now() - timedelta(days=5),
        )
        # Repository returns exactly 3 events (as per interface contract)
        tracking_events = [
            TrackingEvent(
                status=f"Status {i}",
                timestamp=datetime.now() - timedelta(days=i),
                location=f"Location {i}",
            )
            for i in range(3)
        ]
        
        self.mock_order_repo.get_by_id.return_value = order
        self.mock_logistics_repo.get_tracking.return_value = tracking_events
        self.mock_logistics_repo.get_estimated_delivery.return_value = None
        
        result = self.service.get_logistics_info("ORD001")
        
        # Repository should return at most 3 events (per interface contract)
        self.mock_logistics_repo.get_tracking.assert_called_once_with("ORD001")
        self.assertEqual(len(result.tracking_history), 3)

    def test_get_latest_status_from_tracking(self):
        """Test that latest status comes from tracking events."""
        order = Order(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            amount=199.00,
            created_at=datetime.now() - timedelta(days=3),
        )
        tracking_events = [
            TrackingEvent(
                status="Latest tracking status",
                timestamp=datetime.now(),
                location="Current location",
            ),
        ]
        
        self.mock_order_repo.get_by_id.return_value = order
        self.mock_logistics_repo.get_tracking.return_value = tracking_events
        self.mock_logistics_repo.get_estimated_delivery.return_value = None
        
        result = self.service.get_logistics_info("ORD001")
        
        self.assertEqual(result.latest_status, "Latest tracking status")


class TestLogisticsServiceWithMockRepository(unittest.TestCase):
    """Test LogisticsService with actual mock repository implementations."""

    def test_service_with_mock_repositories(self):
        """Test service with mock repository implementations."""
        from data.mock_data import MockLogisticsRepository, MockOrderRepository
        
        order_repo = MockOrderRepository()
        logistics_repo = MockLogisticsRepository()
        service = LogisticsService(
            order_repository=order_repo,
            logistics_repository=logistics_repo,
        )
        
        # Test shipped order
        result = service.get_logistics_info("ORD001")
        self.assertIsNotNone(result)
        self.assertEqual(result.order_id, "ORD001")
        self.assertEqual(result.status, OrderStatus.SHIPPED)
        self.assertIsNotNone(result.latest_status)
        self.assertIsNotNone(result.estimated_delivery)
        
        # Test delivered order
        result = service.get_logistics_info("ORD002")
        self.assertIsNotNone(result)
        self.assertEqual(result.status, OrderStatus.DELIVERED)
        
        # Test non-existent order
        result = service.get_logistics_info("ORD999")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()