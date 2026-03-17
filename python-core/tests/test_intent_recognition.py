"""Tests for Intent Recognition Service.

Tests the intent recognition service functionality including
intent classification, entity extraction, and clarification handling.
"""
import unittest
from unittest.mock import patch, MagicMock

from app.models import (
    IntentType,
    IntentEntities,
    IntentResult,
)
from app.services.intent_recognition import (
    IntentRecognitionService,
    intent_recognition_service,
    get_intent_recognition_service,
)


class TestIntentRecognitionService(unittest.TestCase):
    """Test IntentRecognitionService class."""

    def test_service_initialization(self):
        """Test service initializes with default settings."""
        service = IntentRecognitionService()
        self.assertEqual(service._confidence_threshold, 0.7)
        self.assertIsNone(service._llm)
        self.assertIsNone(service._prompt)
        self.assertIsNone(service._parser)

    def test_service_singleton(self):
        """Test global service instance is available."""
        self.assertIsNotNone(intent_recognition_service)
        self.assertIsInstance(intent_recognition_service, IntentRecognitionService)

    def test_get_service_function(self):
        """Test get_intent_recognition_service function."""
        service = get_intent_recognition_service()
        self.assertIsNotNone(service)
        self.assertIsInstance(service, IntentRecognitionService)

    def test_clarification_question_missing_order_id(self):
        """Test clarification question when order_id is missing."""
        service = IntentRecognitionService()
        question = service._create_clarification_question(
            intent=IntentType.LOGISTICS,
            confidence=0.8,
            entities=IntentEntities(),
        )
        self.assertIn("订单号", question)

    def test_clarification_question_missing_cancel_reason(self):
        """Test clarification question for cancel intent without reason."""
        service = IntentRecognitionService()
        question = service._create_clarification_question(
            intent=IntentType.CANCEL,
            confidence=0.8,
            entities=IntentEntities(order_id="ORD001"),
        )
        self.assertIn("取消原因", question)

    def test_clarification_question_missing_urgent_reason(self):
        """Test clarification question for urgent intent without reason."""
        service = IntentRecognitionService()
        question = service._create_clarification_question(
            intent=IntentType.URGENT,
            confidence=0.8,
            entities=IntentEntities(order_id="ORD001"),
        )
        # Reason is optional for urgent, so clarification mentions the optional reason
        self.assertIn("催单原因", question)

    def test_clarification_question_low_confidence(self):
        """Test clarification question when confidence is low."""
        service = IntentRecognitionService()
        question = service._create_clarification_question(
            intent=IntentType.LOGISTICS,
            confidence=0.5,
            entities=IntentEntities(order_id="ORD001"),
        )
        self.assertIsNotNone(question)
        self.assertIsInstance(question, str)

    def test_get_clarification_response(self):
        """Test get_clarification_response method."""
        service = IntentRecognitionService()
        response = service.get_clarification_response(
            intent=IntentType.LOGISTICS,
            missing_info=["订单号"],
        )
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)


class TestIntentRecognitionWithMockLLM(unittest.TestCase):
    """Test intent recognition with mocked LLM responses."""

    @patch('app.services.intent_recognition.ChatOpenAI')
    def test_recognize_logistics_intent(self, mock_llm_class):
        """Test recognizing logistics intent."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = '{"intent": "logistics", "confidence": 0.95, "entities": {"order_id": "ORD001", "user_detail": "查询物流"}}'
        mock_llm_class.return_value = mock_llm

        service = IntentRecognitionService()
        result = service.recognize("我的ORD001到哪了")

        self.assertEqual(result.intent, IntentType.LOGISTICS)
        self.assertEqual(result.entities.order_id, "ORD001")
        self.assertFalse(result.needs_clarification)

    @patch('app.services.intent_recognition.ChatOpenAI')
    def test_recognize_urgent_intent(self, mock_llm_class):
        """Test recognizing urgent intent."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = '{"intent": "urgent", "confidence": 0.92, "entities": {"order_id": "ORD002", "user_detail": "等待太久"}}'
        mock_llm_class.return_value = mock_llm

        service = IntentRecognitionService()
        result = service.recognize("帮我催一下ORD002")

        self.assertEqual(result.intent, IntentType.URGENT)
        self.assertEqual(result.entities.order_id, "ORD002")
        self.assertFalse(result.needs_clarification)

    @patch('app.services.intent_recognition.ChatOpenAI')
    def test_recognize_cancel_intent(self, mock_llm_class):
        """Test recognizing cancel intent."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = '{"intent": "cancel", "confidence": 0.88, "entities": {"order_id": "ORD003", "user_detail": "不想要了"}}'
        mock_llm_class.return_value = mock_llm

        service = IntentRecognitionService()
        result = service.recognize("我想取消ORD003")

        self.assertEqual(result.intent, IntentType.CANCEL)
        self.assertEqual(result.entities.order_id, "ORD003")
        self.assertFalse(result.needs_clarification)

    @patch('app.services.intent_recognition.ChatOpenAI')
    def test_recognize_low_confidence_triggers_clarification(self, mock_llm_class):
        """Test that low confidence triggers clarification."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = '{"intent": "logistics", "confidence": 0.5, "entities": {"order_id": "ORD001", "user_detail": ""}}'
        mock_llm_class.return_value = mock_llm

        service = IntentRecognitionService()
        result = service.recognize("帮我看看")

        self.assertTrue(result.needs_clarification)
        self.assertIsNotNone(result.clarification_question)

    @patch('app.services.intent_recognition.ChatOpenAI')
    def test_recognize_missing_order_id_triggers_clarification(self, mock_llm_class):
        """Test that missing order_id triggers clarification."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = '{"intent": "logistics", "confidence": 0.95, "entities": {"order_id": null, "user_detail": "查询物流"}}'
        mock_llm_class.return_value = mock_llm

        service = IntentRecognitionService()
        result = service.recognize("我的订单到哪了")

        self.assertTrue(result.needs_clarification)
        self.assertIn("订单号", result.clarification_question)

    @patch('app.services.intent_recognition.ChatOpenAI')
    def test_recognize_handles_llm_error(self, mock_llm_class):
        """Test that service handles LLM errors gracefully."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM error")
        mock_llm_class.return_value = mock_llm

        service = IntentRecognitionService()
        result = service.recognize("测试消息")

        # Should return a clarification result on error
        self.assertTrue(result.needs_clarification)
        self.assertIsNotNone(result.clarification_question)


class TestIntentRecognitionPrompt(unittest.TestCase):
    """Test intent recognition prompt template."""

    def test_prompt_template_exists(self):
        """Test that prompt template is defined."""
        from app.services.intent_recognition import INTENT_CLASSIFICATION_PROMPT
        self.assertIsNotNone(INTENT_CLASSIFICATION_PROMPT)
        self.assertIn("logistics", INTENT_CLASSIFICATION_PROMPT)
        self.assertIn("urgent", INTENT_CLASSIFICATION_PROMPT)
        self.assertIn("cancel", INTENT_CLASSIFICATION_PROMPT)
        self.assertIn("ORD", INTENT_CLASSIFICATION_PROMPT)

    def test_prompt_contains_format_instructions_placeholder(self):
        """Test that prompt contains format instructions placeholder."""
        from app.services.intent_recognition import INTENT_CLASSIFICATION_PROMPT
        self.assertIn("{format_instructions}", INTENT_CLASSIFICATION_PROMPT)


if __name__ == '__main__':
    unittest.main()