"""Tests for Cancel Service.

Tests the cancel service functionality including
order status validation, cancellation logic, and refund processing.
"""
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from app.models import Order, OrderStatus
from app.services.cancel import CancelService


class TestCancelService(unittest.TestCase):
    """Test CancelService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_order_repo = MagicMock()
        self.service = CancelService(order_repository=self.mock_order_repo)

    def test_service_initialization(self):
        """Test service initializes with repository."""
        self.assertIsNotNone(self.service.order_repository)

    def test_cancel_order_not_found(self):
        """Test cancellation fails for non-existent order."""
        self.mock_order_repo.get_by_id.return_value = None

        result = self.service.cancel_order("ORD999")

        self.assertFalse(result.success)
        self.assertEqual(result.order_id, "ORD999")
        self.assertEqual(result.message, "Order not found")
        self.mock_order_repo.get_by_id.assert_called_once_with("ORD999")

    def test_cancel_already_cancelled_order(self):
        """Test cancellation fails for already cancelled order."""
        order = Order(
            order_id="ORD003",
            status=OrderStatus.CANCELLED,
            amount=99.00,
            created_at=datetime.now() - timedelta(days=2),
        )
        self.mock_order_repo.get_by_id.return_value = order

        result = self.service.cancel_order("ORD003")

        self.assertFalse(result.success)
        self.assertEqual(result.order_id, "ORD003")
        self.assertEqual(result.message, "Order is already cancelled")
        self.assertIsNone(result.refund_amount)
        self.assertIsNone(result.refund_arrival_time)

    def test_cancel_delivered_order(self):
        """Test cancellation fails for delivered order."""
        order = Order(
            order_id="ORD002",
            status=OrderStatus.DELIVERED,
            amount=299.00,
            created_at=datetime.now() - timedelta(days=7),
        )
        self.mock_order_repo.get_by_id.return_value = order

        result = self.service.cancel_order("ORD002")

        self.assertFalse(result.success)
        self.assertEqual(result.order_id, "ORD002")
        self.assertEqual(result.message, "Order is delivered, please use after-sales return process")
        self.assertIsNone(result.refund_amount)
        self.assertIsNone(result.refund_arrival_time)

    def test_cancel_pending_order(self):
        """Test successful cancellation of pending order."""
        order = Order(
            order_id="ORD004",
            status=OrderStatus.PENDING,
            amount=149.00,
            created_at=datetime.now() - timedelta(days=1),
        )
        self.mock_order_repo.get_by_id.return_value = order
        self.mock_order_repo.cancel.return_value = {
            "success": True,
            "order_id": "ORD004",
            "refund_amount": 149.00,
            "message": "Order cancelled successfully",
        }

        result = self.service.cancel_order("ORD004")

        self.assertTrue(result.success)
        self.assertEqual(result.order_id, "ORD004")
        self.assertEqual(result.refund_amount, 149.00)
        self.assertIsNotNone(result.refund_arrival_time)
        self.mock_order_repo.cancel.assert_called_once()

    def test_cancel_shipped_order(self):
        """Test successful cancellation of shipped order."""
        order = Order(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            amount=199.00,
            created_at=datetime.now() - timedelta(days=3),
        )
        self.mock_order_repo.get_by_id.return_value = order
        self.mock_order_repo.cancel.return_value = {
            "success": True,
            "order_id": "ORD001",
            "refund_amount": 199.00,
            "message": "Order cancelled successfully",
        }

        result = self.service.cancel_order("ORD001")

        self.assertTrue(result.success)
        self.assertEqual(result.order_id, "ORD001")
        self.assertEqual(result.refund_amount, 199.00)
        self.assertIsNotNone(result.refund_arrival_time)

    def test_cancel_with_reason(self):
        """Test cancellation with reason provided."""
        order = Order(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            amount=199.00,
            created_at=datetime.now() - timedelta(days=3),
        )
        self.mock_order_repo.get_by_id.return_value = order
        self.mock_order_repo.cancel.return_value = {
            "success": True,
            "order_id": "ORD001",
            "refund_amount": 199.00,
            "message": "Order cancelled successfully",
        }

        result = self.service.cancel_order("ORD001", reason="Changed my mind")

        self.assertTrue(result.success)
        self.mock_order_repo.cancel.assert_called_once_with("ORD001", "Changed my mind")

    def test_refund_arrival_time_calculation(self):
        """Test refund arrival time is calculated correctly."""
        order = Order(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            amount=199.00,
            created_at=datetime.now() - timedelta(days=3),
        )
        self.mock_order_repo.get_by_id.return_value = order
        self.mock_order_repo.cancel.return_value = {
            "success": True,
            "order_id": "ORD001",
            "refund_amount": 199.00,
            "message": "Order cancelled successfully",
        }

        before_call = datetime.now()
        result = self.service.cancel_order("ORD001")
        after_call = datetime.now()

        self.assertIsNotNone(result.refund_arrival_time)
        # Refund should arrive in 3 days
        expected_min = before_call + timedelta(days=3)
        expected_max = after_call + timedelta(days=3)
        self.assertGreaterEqual(result.refund_arrival_time, expected_min)
        self.assertLessEqual(result.refund_arrival_time, expected_max)


class TestCancelServiceWithMockRepository(unittest.TestCase):
    """Test CancelService with actual mock repository implementation."""

    def test_service_with_mock_repository(self):
        """Test service with mock repository implementations."""
        from data.mock_data import MockOrderRepository

        order_repo = MockOrderRepository()
        service = CancelService(order_repository=order_repo)

        # Test cancelling already cancelled order
        result = service.cancel_order("ORD003")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Order is already cancelled")

        # Test cancelling delivered order
        result = service.cancel_order("ORD002")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Order is delivered, please use after-sales return process")

        # Test cancelling shipped order (should succeed)
        result = service.cancel_order("ORD001")
        self.assertTrue(result.success)
        self.assertEqual(result.refund_amount, 199.00)
        self.assertIsNotNone(result.refund_arrival_time)

        # Test cancelling non-existent order
        result = service.cancel_order("ORD999")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Order not found")


class TestValidateOrderForCancellation(unittest.TestCase):
    """Test validate_order_for_cancellation method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_order_repo = MagicMock()
        self.service = CancelService(order_repository=self.mock_order_repo)

    def test_validate_order_not_found(self):
        """Test validation fails for non-existent order."""
        self.mock_order_repo.get_by_id.return_value = None

        is_valid, reason = self.service.validate_order_for_cancellation("ORD999")

        self.assertFalse(is_valid)
        self.assertEqual(reason, "Order not found")

    def test_validate_already_cancelled(self):
        """Test validation fails for already cancelled order."""
        order = Order(
            order_id="ORD003",
            status=OrderStatus.CANCELLED,
            amount=99.00,
            created_at=datetime.now() - timedelta(days=2),
        )
        self.mock_order_repo.get_by_id.return_value = order

        is_valid, reason = self.service.validate_order_for_cancellation("ORD003")

        self.assertFalse(is_valid)
        self.assertEqual(reason, "Order is already cancelled")

    def test_validate_delivered_order(self):
        """Test validation fails for delivered order."""
        order = Order(
            order_id="ORD002",
            status=OrderStatus.DELIVERED,
            amount=299.00,
            created_at=datetime.now() - timedelta(days=7),
        )
        self.mock_order_repo.get_by_id.return_value = order

        is_valid, reason = self.service.validate_order_for_cancellation("ORD002")

        self.assertFalse(is_valid)
        self.assertEqual(reason, "Order is delivered, please use after-sales return process")

    def test_validate_pending_order(self):
        """Test validation passes for pending order."""
        order = Order(
            order_id="ORD004",
            status=OrderStatus.PENDING,
            amount=149.00,
            created_at=datetime.now() - timedelta(days=1),
        )
        self.mock_order_repo.get_by_id.return_value = order

        is_valid, reason = self.service.validate_order_for_cancellation("ORD004")

        self.assertTrue(is_valid)
        self.assertEqual(reason, "")

    def test_validate_shipped_order(self):
        """Test validation passes for shipped order."""
        order = Order(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            amount=199.00,
            created_at=datetime.now() - timedelta(days=3),
        )
        self.mock_order_repo.get_by_id.return_value = order

        is_valid, reason = self.service.validate_order_for_cancellation("ORD001")

        self.assertTrue(is_valid)
        self.assertEqual(reason, "")


class TestGetRefundAmount(unittest.TestCase):
    """Test get_refund_amount method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_order_repo = MagicMock()
        self.service = CancelService(order_repository=self.mock_order_repo)

    def test_get_refund_amount_exists(self):
        """Test getting refund amount for existing order."""
        order = Order(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            amount=199.00,
            created_at=datetime.now() - timedelta(days=3),
        )
        self.mock_order_repo.get_by_id.return_value = order

        amount = self.service.get_refund_amount("ORD001")

        self.assertEqual(amount, 199.00)

    def test_get_refund_amount_not_found(self):
        """Test getting refund amount for non-existent order."""
        self.mock_order_repo.get_by_id.return_value = None

        amount = self.service.get_refund_amount("ORD999")

        self.assertIsNone(amount)


if __name__ == '__main__':
    unittest.main()