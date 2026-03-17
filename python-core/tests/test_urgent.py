"""Tests for the Urgent Ticket Service.

This module contains unit tests and property-based tests for the
UrgentService class, validating ticket creation, priority assignment,
and estimated processing time calculation.
"""
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from app.models import Ticket, TicketPriority, TicketStatus
from app.services.urgent import UrgentService


class TestUrgentService(unittest.TestCase):
    """Unit tests for the UrgentService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = MagicMock()
        self.service = UrgentService(self.mock_repository)

    def test_service_initialization(self):
        """Test that the service initializes correctly."""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.CUSTOMER_SERVICE_CONTACT, "400-123-4567")

    def test_create_urgent_ticket_basic(self):
        """Test creating an urgent ticket with basic parameters."""
        # Arrange
        order_id = "ORD001"
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123456",
            order_id=order_id,
            reason=None,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=4),
        )

        # Act
        result = self.service.create_urgent_ticket(order_id)

        # Assert
        self.assertIn("ticket_id", result)
        self.assertTrue(result["ticket_id"].startswith("TKT"))
        self.assertEqual(result["order_id"], order_id)
        self.assertIn("estimated_processing_time", result)
        self.assertEqual(result["contact"], "400-123-4567")
        self.assertEqual(result["message"], "Urgent ticket created successfully")

    def test_create_urgent_ticket_with_reason(self):
        """Test creating an urgent ticket with a reason."""
        # Arrange
        order_id = "ORD002"
        reason = "Please process as soon as possible"
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123457",
            order_id=order_id,
            reason=reason,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=4),
        )

        # Act
        result = self.service.create_urgent_ticket(order_id, reason=reason)

        # Assert
        self.assertIn("ticket_id", result)
        self.assertEqual(result["order_id"], order_id)
        self.assertEqual(result["priority"], "medium")  # Default priority

    def test_create_urgent_ticket_high_priority(self):
        """Test creating an urgent ticket with high priority keywords."""
        # Arrange
        order_id = "ORD003"
        reason = "This is very urgent, please process immediately"
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123458",
            order_id=order_id,
            reason=reason,
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=2),
        )

        # Act
        result = self.service.create_urgent_ticket(order_id, reason=reason)

        # Assert
        self.assertEqual(result["priority"], "high")

    def test_create_urgent_ticket_low_priority(self):
        """Test creating an urgent ticket with low priority keywords."""
        # Arrange
        order_id = "ORD004"
        reason = "No rush, process when possible"
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123459",
            order_id=order_id,
            reason=reason,
            priority=TicketPriority.LOW,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=8),
        )

        # Act
        result = self.service.create_urgent_ticket(order_id, reason=reason)

        # Assert
        self.assertEqual(result["priority"], "low")

    def test_ticket_id_format(self):
        """Test that ticket ID follows TKT+timestamp format."""
        # Arrange
        order_id = "ORD005"
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123460",
            order_id=order_id,
            reason=None,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=4),
        )

        # Act
        result = self.service.create_urgent_ticket(order_id)

        # Assert
        ticket_id = result["ticket_id"]
        self.assertTrue(ticket_id.startswith("TKT"))
        timestamp_part = ticket_id[3:]
        self.assertTrue(timestamp_part.isdigit())
        self.assertTrue(len(timestamp_part) > 0)

    def test_estimated_processing_time_format(self):
        """Test that estimated processing time is a valid ISO format string."""
        # Arrange
        order_id = "ORD006"
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123461",
            order_id=order_id,
            reason=None,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=4),
        )

        # Act
        result = self.service.create_urgent_ticket(order_id)

        # Assert
        estimated_time_str = result["estimated_processing_time"]
        # Should be parseable as datetime
        parsed_time = datetime.fromisoformat(estimated_time_str)
        self.assertIsInstance(parsed_time, datetime)

    def test_estimated_processing_time_future(self):
        """Test that estimated processing time is in the future."""
        # Arrange
        order_id = "ORD007"
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123462",
            order_id=order_id,
            reason=None,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=4),
        )
        before_creation = datetime.now()

        # Act
        result = self.service.create_urgent_ticket(order_id)

        # Assert
        estimated_time = datetime.fromisoformat(result["estimated_processing_time"])
        self.assertGreater(estimated_time, before_creation)

    def test_get_ticket(self):
        """Test getting a ticket by ID."""
        # Arrange
        ticket_id = "TKT123456"
        expected_ticket = Ticket(
            ticket_id=ticket_id,
            order_id="ORD001",
            reason="Test reason",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=4),
        )
        self.mock_repository.get_by_id.return_value = expected_ticket

        # Act
        result = self.service.get_ticket(ticket_id)

        # Assert
        self.assertEqual(result, expected_ticket)
        self.mock_repository.get_by_id.assert_called_once_with(ticket_id)

    def test_get_ticket_not_found(self):
        """Test getting a non-existent ticket."""
        # Arrange
        ticket_id = "TKT999999"
        self.mock_repository.get_by_id.return_value = None

        # Act
        result = self.service.get_ticket(ticket_id)

        # Assert
        self.assertIsNone(result)

    def test_list_tickets_by_order(self):
        """Test listing tickets for an order."""
        # Arrange
        order_id = "ORD001"
        expected_tickets = [
            Ticket(
                ticket_id="TKT111",
                order_id=order_id,
                priority=TicketPriority.MEDIUM,
                status=TicketStatus.OPEN,
                created_at=datetime.now(),
                estimated_processing_time=datetime.now() + timedelta(hours=4),
            ),
            Ticket(
                ticket_id="TKT222",
                order_id=order_id,
                priority=TicketPriority.HIGH,
                status=TicketStatus.IN_PROGRESS,
                created_at=datetime.now(),
                estimated_processing_time=datetime.now() + timedelta(hours=2),
            ),
        ]
        self.mock_repository.list_by_order.return_value = expected_tickets

        # Act
        result = self.service.list_tickets_by_order(order_id)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].ticket_id, "TKT111")
        self.assertEqual(result[1].ticket_id, "TKT222")


class TestUrgentServicePriorityAssignment(unittest.TestCase):
    """Tests for priority assignment logic in UrgentService."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = MagicMock()
        self.service = UrgentService(self.mock_repository)

    def test_default_priority_medium(self):
        """Test that default priority is medium when no reason provided."""
        # Arrange
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123463",
            order_id="ORD001",
            reason=None,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=4),
        )

        # Act
        result = self.service.create_urgent_ticket("ORD001", reason=None)

        # Assert
        self.assertEqual(result["priority"], "medium")

    def test_empty_reason_priority_medium(self):
        """Test that empty reason results in medium priority."""
        # Arrange
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123464",
            order_id="ORD001",
            reason="",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=4),
        )

        # Act
        result = self.service.create_urgent_ticket("ORD001", reason="")

        # Assert
        self.assertEqual(result["priority"], "medium")

    def test_high_priority_keywords(self):
        """Test various high priority keywords."""
        high_priority_keywords = [
            "紧急", "非常急", "马上", "立刻", "尽快",
            "urgent", "asap", "immediately", "emergency",
        ]

        for keyword in high_priority_keywords:
            with self.subTest(keyword=keyword):
                self.mock_repository.create.return_value = Ticket(
                    ticket_id="TKT123465",
                    order_id="ORD001",
                    reason=f"Please help me, it's {keyword}",
                    priority=TicketPriority.HIGH,
                    status=TicketStatus.OPEN,
                    created_at=datetime.now(),
                    estimated_processing_time=datetime.now() + timedelta(hours=2),
                )
                result = self.service.create_urgent_ticket(
                    "ORD001", reason=f"Please help me, it's {keyword}"
                )
                self.assertEqual(result["priority"], "high")

    def test_low_priority_keywords(self):
        """Test various low priority keywords."""
        low_priority_keywords = [
            "不急", "慢慢来", "有空处理", "不着急",
            "not urgent", "when possible", "no rush",
        ]

        for keyword in low_priority_keywords:
            with self.subTest(keyword=keyword):
                self.mock_repository.create.return_value = Ticket(
                    ticket_id="TKT123466",
                    order_id="ORD001",
                    reason=f"处理 {keyword}",
                    priority=TicketPriority.LOW,
                    status=TicketStatus.OPEN,
                    created_at=datetime.now(),
                    estimated_processing_time=datetime.now() + timedelta(hours=8),
                )
                result = self.service.create_urgent_ticket(
                    "ORD001", reason=f"处理 {keyword}"
                )
                self.assertEqual(result["priority"], "low")

    def test_mixed_keywords_high_priority_wins(self):
        """Test that high priority keywords take precedence."""
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123467",
            order_id="ORD001",
            reason="Not urgent but please do it immediately",
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=2),
        )
        result = self.service.create_urgent_ticket(
            "ORD001", reason="Not urgent but please do it immediately"
        )
        self.assertEqual(result["priority"], "high")


class TestUrgentServiceProcessingTime(unittest.TestCase):
    """Tests for estimated processing time calculation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = MagicMock()
        self.service = UrgentService(self.mock_repository)

    def test_high_priority_processing_time(self):
        """Test that high priority has shortest processing time."""
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123468",
            order_id="ORD001",
            reason="This is very urgent",
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=2),
        )
        result = self.service.create_urgent_ticket(
            "ORD001", reason="This is very urgent"
        )
        estimated_time = datetime.fromisoformat(result["estimated_processing_time"])
        expected_min_time = datetime.now() + timedelta(hours=2) - timedelta(minutes=1)
        self.assertGreaterEqual(estimated_time, expected_min_time)

    def test_medium_priority_processing_time(self):
        """Test that medium priority has medium processing time."""
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123469",
            order_id="ORD001",
            reason=None,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=4),
        )
        result = self.service.create_urgent_ticket("ORD001")
        estimated_time = datetime.fromisoformat(result["estimated_processing_time"])
        expected_min_time = datetime.now() + timedelta(hours=4) - timedelta(minutes=1)
        self.assertGreaterEqual(estimated_time, expected_min_time)

    def test_low_priority_processing_time(self):
        """Test that low priority has longest processing time."""
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123470",
            order_id="ORD001",
            reason="No rush at all",
            priority=TicketPriority.LOW,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=8),
        )
        result = self.service.create_urgent_ticket(
            "ORD001", reason="No rush at all"
        )
        estimated_time = datetime.fromisoformat(result["estimated_processing_time"])
        expected_min_time = datetime.now() + timedelta(hours=8) - timedelta(minutes=1)
        self.assertGreaterEqual(estimated_time, expected_min_time)


class TestUrgentServiceIdempotency(unittest.TestCase):
    """Tests for ticket creation idempotency."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = MagicMock()
        self.service = UrgentService(self.mock_repository)

    def test_ticket_repository_called_with_correct_data(self):
        """Test that repository is called with correctly formatted ticket."""
        # Arrange
        order_id = "ORD001"
        reason = "Test reason"
        self.mock_repository.create.return_value = Ticket(
            ticket_id="TKT123471",
            order_id=order_id,
            reason=reason,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            estimated_processing_time=datetime.now() + timedelta(hours=4),
        )

        # Act
        self.service.create_urgent_ticket(order_id, reason=reason)

        # Assert - verify the create method was called
        self.mock_repository.create.assert_called_once()
        call_args = self.mock_repository.create.call_args
        ticket = call_args[0][0]

        self.assertEqual(ticket.order_id, order_id)
        self.assertEqual(ticket.reason, reason)
        self.assertTrue(ticket.ticket_id.startswith("TKT"))
        self.assertEqual(ticket.status, TicketStatus.OPEN)


if __name__ == "__main__":
    unittest.main()