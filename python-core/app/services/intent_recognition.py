"""
智能工单系统的意图识别服务。

使用LangChain和结构化输出进行意图分类和实体提取。
支持多种LLM提供商：OpenAI、DeepSeek、豆包等。
"""
import logging
import time
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.exceptions import LangChainException

from app.models import (
    IntentType,
    IntentEntities,
    IntentResult,
)
from app.config import settings, get_llm_config
from app.services.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 1  # 秒


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
    使用LangChain和结构化输出的意图识别服务。
    
    该服务将用户消息分类为意图（物流、催单、取消）
    并提取相关实体（order_id、user_detail）。
    """
    
    def __init__(self):
        """使用LangChain初始化意图识别服务。"""
        self._llm = None
        self._prompt = None
        self._parser = None
        self._confidence_threshold = settings.intent.confidence_threshold
        
    @property
    def llm(self):
        """LLM的延迟初始化。"""
        if self._llm is None:
            self._llm = LLMFactory.get_default_llm(temperature=0)
        return self._llm
    
    @property
    def prompt(self) -> ChatPromptTemplate:
        """获取意图分类提示模板。"""
        if self._prompt is None:
            self._prompt = ChatPromptTemplate.from_messages([
                ("human", INTENT_CLASSIFICATION_PROMPT)
            ])
        return self._prompt
    
    @property
    def parser(self) -> PydanticOutputParser:
        """获取IntentResult的Pydantic输出解析器。"""
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
        当置信度低或实体缺失时创建澄清问题。
        
        Args:
            intent: 识别的意图
            confidence: 置信度分数
            entities: 提取的实体
            
        Returns:
            str: 澄清问题
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
        从用户消息中识别意图并提取实体。

        Args:
            user_message: 用户的输入消息
            conversation_history: 可选的对话历史用于上下文

        Returns:
            IntentResult: 识别的意图和提取的实体
        """
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            # Get LLM configuration
            llm_config = get_llm_config()
            provider = llm_config.get('provider')
            model = llm_config.get('model')
            base_url = llm_config.get('base_url')
            
            # Construct actual URL based on provider if not set
            if not base_url:
                if provider == "deepseek":
                    base_url = "https://api.deepseek.com/v1"
                elif provider == "openai":
                    base_url = "https://api.openai.com/v1"
                elif provider == "doubao":
                    base_url = "https://ark.cn-beijing.volces.com/api/v3"
                elif provider == "qwen":
                    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                else:
                    base_url = "unknown"
            
            logger.info(f"==> 发送请求到第三方 LLM (尝试 {attempt + 1}/{MAX_RETRIES}): provider={provider}, model={model}")
            
            try:
                # Get format instructions from parser
                format_instructions = self.parser.get_format_instructions()
                
                # Create the prompt with user message
                prompt_value = self.prompt.format(
                    user_message=user_message,
                    format_instructions=format_instructions,
                )
                
                # Log all LLM input parameters (with masked sensitive keys)
                logger.info(f"==> LLM 请求参数:")
                logger.info(f"    provider: {provider}")
                logger.info(f"    model: {model}")
                logger.info(f"    base_url: {base_url}")
                logger.info(f"    temperature: {self.llm.temperature}")
                logger.info(f"    request_timeout: {self.llm.request_timeout}")
                logger.info(f"    prompt: {prompt_value[:500]}...")
                
                # Call LLM with structured output
                response = self.llm.invoke([HumanMessage(content=prompt_value)])
                
                # Log the LLM response
                logger.info(f"<== 收到第三方 LLM 响应: {response.content[:500]}")
                
                # Parse the response into IntentResult
                result = self.parser.parse(response.content)
                
                # Check confidence threshold and handle clarification
                if result.confidence < self._confidence_threshold:
                    result.needs_clarification = True
                    # 保留LLM返回的clarification_question，如果没有则使用默认的
                    if not result.clarification_question:
                        result.clarification_question = self._create_clarification_question(
                            intent=result.intent,
                            confidence=result.confidence,
                            entities=result.entities,
                        )
                    logger.info(
                        f"意图 '{result.intent.value}' 置信度较低 ({result.confidence:.2f})，"
                        f"请求澄清"
                    )
                
                # Check if order_id is missing
                if not result.entities.order_id:
                    result.needs_clarification = True
                    # 保留LLM返回的clarification_question，如果没有则使用默认的
                    if not result.clarification_question:
                        result.clarification_question = self._create_clarification_question(
                            intent=result.intent,
                            confidence=result.confidence,
                            entities=result.entities,
                        )
                    logger.info(
                        f"意图 '{result.intent.value}' 缺少order_id，"
                        f"请求澄清"
                    )
                
                logger.info(
                    f"意图已识别: {result.intent.value}, "
                    f"置信度: {result.confidence:.2f}, "
                    f"订单号: {result.entities.order_id}"
                )
                
                return result
                
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                logger.warning(f"意图识别尝试 {attempt + 1}/{MAX_RETRIES} 失败: {error_type} - {e}")
                
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))  # 指数退避
        
        # 所有重试都失败
        logger.error(f"意图识别最终失败: {last_error}")
        
        # 返回一个澄清结果，并包含错误信息
        return IntentResult(
            intent=IntentType.LOGISTICS,
            confidence=0.0,
            entities=IntentEntities(),
            needs_clarification=True,
            clarification_question="抱歉，服务暂时不可用。请稍后重试或联系客服。",
        )
    
    def get_clarification_response(
        self,
        intent: IntentType,
        missing_info: list,
    ) -> str:
        """
        为缺失信息生成澄清响应。
        
        Args:
            intent: 识别的意图
            missing_info: 缺失信息字段列表
            
        Returns:
            str: 澄清问题
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
    获取意图识别服务实例。
    
    Returns:
        IntentRecognitionService: 服务实例
    """
    return intent_recognition_service