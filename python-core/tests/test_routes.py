"""Tests for API routes.

Tests the API endpoints including logistics, urgent ticket, and cancel order.
"""
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from fastapi.testclient import TestClient


class TestLogisticsEndpoint(unittest.TestCase):
    """Test logistics API endpoint."""

    def setUp(self):
        """Set up test fixtures."""
        from app.main import app
        from app.api.routes import router, get_logistics_service
        from app.services.logistics import LogisticsService
        from app.models import LogisticsInfo, OrderStatus, TrackingEvent
        
        # Create mock services
        self.mock_logistics_service = MagicMock(spec=LogisticsService)
        
        # Override the dependency
        app.dependency_overrides[get_logistics_service] = lambda: self.mock_logistics_service
        
        # Include router
        app.include_router(router, prefix="/api/v1")
        self.app = app
        self.client = TestClient(app)

    def tearDown(self):
        """Clean up dependency overrides."""
        self.app.dependency_overrides.clear()

    def test_get_logistics_valid_order(self):
        """Test getting logistics info for a valid order."""
        from app.models import LogisticsInfo, OrderStatus, TrackingEvent
        
        # Create mock logistics info
        logistics_info = LogisticsInfo(
            order_id="ORD001",
            status=OrderStatus.SHIPPED,
            latest_status="Package out for delivery",
            estimated_delivery=datetime.now() + timedelta(days=1),
            tracking_history=[
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
            ],
        )
        self.mock_logistics_service.get_logistics_info.return_value = logistics_info
        
        # Make request
        response = self.client.get("/api/v1/logistics/ORD001")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["order_id"], "ORD001")
        self.assertEqual(data["data"]["status"], "shipped")
        self.assertEqual(data["data"]["latest_status"], "Package out for delivery")
        self.assertIsNotNone(data["data"]["estimated_delivery"])
        self.assertEqual(len(data["data"]["tracking_history"]), 2)

    def test_get_logistics_order_not_found(self):
        """Test getting logistics info for non-existent order."""
        # Return None for non-existent order
        self.mock_logistics_service.get_logistics_info.return_value = None
        
        response = self.client.get("/api/v1/logistics/ORD999")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Order not found")
        self.assertIn("未找到订单", data["message"])

    def test_get_logistics_invalid_order_id_format(self):
        """Test getting logistics info with invalid order ID format."""
        # Test various invalid formats
        invalid_ids = ["ORD", "ORD001abc", "ORD001!", "001", "order001", "ORD-001"]
        
        for order_id in invalid_ids:
            response = self.client.get(f"/api/v1/logistics/{order_id}")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertFalse(data["success"])
            self.assertEqual(data["error"], "Invalid order ID format")
            self.assertIn("订单号格式不正确", data["message"])

    def test_get_logistics_valid_formats(self):
        """Test that valid order ID formats are accepted."""
        # Test valid formats
        valid_ids = ["ORD001", "ORD123", "ORD999999"]
        
        for order_id in valid_ids:
            # Mock the service to return None (we're just testing format validation)
            self.mock_logistics_service.get_logistics_info.return_value = None
            
            response = self.client.get(f"/api/v1/logistics/{order_id}")
            # Should not get format error (might get order not found)
            data = response.json()
            self.assertNotEqual(data.get("error"), "Invalid order ID format")


class TestUrgentTicketEndpoint(unittest.TestCase):
    """Test urgent ticket API endpoint."""

    def setUp(self):
        """Set up test fixtures."""
        from app.main import app
        from app.api.routes import router, get_urgent_service
        from app.services.urgent import UrgentService
        
        # Create mock services
        self.mock_urgent_service = MagicMock(spec=UrgentService)
        
        # Override the dependency
        app.dependency_overrides[get_urgent_service] = lambda: self.mock_urgent_service
        
        # Include router
        app.include_router(router, prefix="/api/v1")
        self.app = app
        self.client = TestClient(app)

    def tearDown(self):
        """Clean up dependency overrides."""
        self.app.dependency_overrides.clear()

    def test_create_urgent_ticket_basic(self):
        """Test creating an urgent ticket with basic request."""
        # Mock the service response
        self.mock_urgent_service.create_urgent_ticket.return_value = {
            "ticket_id": "TKT123456",
            "order_id": "ORD001",
            "priority": "medium",
            "status": "open",
            "estimated_processing_time": "2024-01-15T10:00:00",
            "contact": "400-123-4567",
            "message": "Urgent ticket created successfully",
        }
        
        # Make request
        response = self.client.post(
            "/api/v1/tickets/urgent",
            json={"order_id": "ORD001"}
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["ticket_id"], "TKT123456")
        self.assertEqual(data["data"]["order_id"], "ORD001")
        self.assertIsNotNone(data["data"]["estimated_processing_time"])
        self.assertEqual(data["data"]["contact"], "400-123-4567")

    def test_create_urgent_ticket_with_reason(self):
        """Test creating an urgent ticket with reason."""
        self.mock_urgent_service.create_urgent_ticket.return_value = {
            "ticket_id": "TKT123456",
            "order_id": "ORD001",
            "priority": "high",
            "status": "open",
            "estimated_processing_time": "2024-01-15T10:00:00",
            "contact": "400-123-4567",
            "message": "Urgent ticket created successfully",
        }
        
        # Make request with reason
        response = self.client.post(
            "/api/v1/tickets/urgent",
            json={"order_id": "ORD001", "reason": "非常急，请尽快处理"}
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["ticket_id"], "TKT123456")

    def test_create_urgent_ticket_missing_order_id(self):
        """Test creating an urgent ticket without order_id."""
        # Make request without order_id
        response = self.client.post(
            "/api/v1/tickets/urgent",
            json={"reason": "请帮忙处理"}
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "order_id is required")


if __name__ == '__main__':
    unittest.main()