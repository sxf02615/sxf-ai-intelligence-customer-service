"""
Intent Recognition Service for Smart Ticket System.

Uses LangChain with structured output for intent classification and entity extraction.
"""
import logging
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage

from app.models import (
    IntentType,
    IntentEntities,
    IntentResult,
)
from app.config import get_llm_config, settings

logger = logging.getLogger(__name__)


# Prompt template for intent classification
INTENT_CLASSIFICATION_PROMPT = """你是一个智能客服系统的意图识别助手。

用户消息: {user_message}

请分析用户消息，识别其意图并提取相关实体。

意图类型说明:
- logistics: 用户想查询订单物流状态，例如"我的订单到哪了"、"查询ORD001物流"
- urgent: 用户想催促订单处理，例如"帮我催一下订单"、"快点处理我的订单"
- cancel: 用户想取消订单，例如"我想取消订单"、"帮我退掉ORD002"

实体提取规则:
- order_id: 订单号，格式为ORD+数字，例如ORD001、ORD002
- user_detail: 用户的具体诉求细节

请根据用户消息的内容和上下文进行判断。

{format_instructions}
"""


class IntentRecognitionService:
    """
    Intent Recognition Service using LangChain with structured output.
    
    This service classifies user messages into intents (logistics, urgent, cancel)
    and extracts relevant entities (order_id, user_detail).
    """
    
    def __init__(self):
        """Initialize the intent recognition service with LangChain."""
        self._llm = None
        self._prompt = None
        self._parser = None
        self._confidence_threshold = settings.intent.confidence_threshold
        
    @property
    def llm(self):
        """Lazy initialization of LLM."""
        if self._llm is None:
            llm_config = get_llm_config()
            self._llm = ChatOpenAI(
                model=llm_config.get("model", "gpt-3.5-turbo"),
                api_key=llm_config.get("api_key", ""),
                temperature=0,
            )
        return self._llm
    
    @property
    def prompt(self) -> ChatPromptTemplate:
        """Get the intent classification prompt template."""
        if self._prompt is None:
            self._prompt = ChatPromptTemplate.from_messages([
                ("human", INTENT_CLASSIFICATION_PROMPT)
            ])
        return self._prompt
    
    @property
    def parser(self) -> PydanticOutputParser:
        """Get the Pydantic output parser for IntentResult."""
        if self._parser is None:
            self._parser = PydanticOutputParser(pydantic_object=IntentResult)
        return self._parser
    
    def _create_clarification_question(
        self,
        intent: IntentType,
        confidence: float,
        entities: IntentEntities,
    ) -> str:
        """
        Create a clarification question when confidence is low or entities are missing.
        
        Args:
            intent: The recognized intent
            confidence: The confidence score
            entities: The extracted entities
            
        Returns:
            str: A clarification question
        """
        missing_parts = []
        
        if not entities.order_id:
            missing_parts.append("订单号")
        
        if intent == IntentType.URGENT and not entities.user_detail:
            missing_parts.append("催单原因（可选）")
        elif intent == IntentType.CANCEL and not entities.user_detail:
            missing_parts.append("取消原因")
        
        if missing_parts:
            return f"为了更好地帮助您，请提供{'和'.join(missing_parts)}。"
        
        if confidence < self._confidence_threshold:
            return "我不太确定您的意思，请重新描述一下您的需求可以吗？"
        
        return "请您详细说明一下您的需求。"
    
    def recognize(
        self,
        user_message: str,
        conversation_history: Optional[list] = None,
    ) -> IntentResult:
        """
        Recognize intent and extract entities from user message.
        
        Args:
            user_message: The user's input message
            conversation_history: Optional conversation history for context
            
        Returns:
            IntentResult: The recognized intent and extracted entities
        """
        try:
            # Get format instructions from parser
            format_instructions = self.parser.get_format_instructions()
            
            # Create the prompt with user message
            prompt_value = self.prompt.format(
                user_message=user_message,
                format_instructions=format_instructions,
            )
            
            # Call LLM with structured output
            response = self.llm.invoke([HumanMessage(content=prompt_value)])
            
            # Parse the response into IntentResult
            result = self.parser.parse(response.content)
            
            # Check confidence threshold and handle clarification
            if result.confidence < self._confidence_threshold:
                result.needs_clarification = True
                result.clarification_question = self._create_clarification_question(
                    intent=result.intent,
                    confidence=result.confidence,
                    entities=result.entities,
                )
                logger.info(
                    f"Low confidence ({result.confidence:.2f}) for intent '{result.intent.value}', "
                    f"requesting clarification"
                )
            
            # Check if order_id is missing
            if not result.entities.order_id:
                result.needs_clarification = True
                result.clarification_question = self._create_clarification_question(
                    intent=result.intent,
                    confidence=result.confidence,
                    entities=result.entities,
                )
                logger.info(
                    f"Missing order_id for intent '{result.intent.value}', "
                    f"requesting clarification"
                )
            
            logger.info(
                f"Intent recognized: {result.intent.value}, "
                f"confidence: {result.confidence:.2f}, "
                f"order_id: {result.entities.order_id}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in intent recognition: {e}")
            # Return a clarification result on error
            return IntentResult(
                intent=IntentType.LOGISTICS,
                confidence=0.0,
                entities=IntentEntities(),
                needs_clarification=True,
                clarification_question="抱歉，我遇到了一个问题。请重新描述一下您的需求可以吗？",
            )
    
    def get_clarification_response(
        self,
        intent: IntentType,
        missing_info: list,
    ) -> str:
        """
        Generate a clarification response for missing information.
        
        Args:
            intent: The recognized intent
            missing_info: List of missing information fields
            
        Returns:
            str: Clarification question
        """
        return self._create_clarification_question(
            intent=intent,
            confidence=0.0,
            entities=IntentEntities(),
        )


# Global service instance
intent_recognition_service = IntentRecognitionService()


def get_intent_recognition_service() -> IntentRecognitionService:
    """
    Get the intent recognition service instance.
    
    Returns:
        IntentRecognitionService: The service instance
    """
    return intent_recognition_service