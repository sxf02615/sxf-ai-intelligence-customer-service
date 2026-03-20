"""
LLM Factory for managing different LLM providers.

This module provides a factory pattern for creating LLM instances
for different providers (OpenAI, DeepSeek, Doubao).
"""
import os
import logging
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.exceptions import LangChainException

from app.config import LLMProvider, get_llm_config

logger = logging.getLogger(__name__)

# 禁用系统代理（用于 DeepSeek 等不需要代理的 API）
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)


class LLMFactory:
    """
    Factory for creating LLM instances based on provider configuration.
    
    This factory handles the creation of appropriate LLM instances
    for different providers (OpenAI, DeepSeek, Doubao).
    """
    
    @staticmethod
    def create_llm(
        provider: Optional[LLMProvider] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0,
    ) -> BaseChatModel:
        """
        Create an LLM instance based on provider configuration.
        
        Args:
            provider: LLM provider (openai, deepseek, doubao)
            api_key: API key for the provider
            model: Model name
            base_url: Custom base URL for API endpoint
            temperature: Temperature for generation (0 for deterministic)
            
        Returns:
            BaseChatModel: Configured LLM instance
            
        Raises:
            ValueError: If provider is not supported or configuration is invalid
        """
        # Get default configuration if not provided
        if provider is None or api_key is None or model is None:
            config = get_llm_config()
            provider = provider or config.get("provider", LLMProvider.OPENAI)
            api_key = api_key or config.get("api_key", "")
            model = model or config.get("model", "gpt-3.5-turbo")
            base_url = base_url or config.get("base_url", "")
        
        if not api_key:
            raise ValueError(f"API key is required for {provider} provider")
        
        logger.info(f"Creating LLM instance for provider: {provider}, model: {model}")
        
        # Configure common parameters
        common_params = {
            "model": model,
            "api_key": api_key,
            "temperature": temperature,
            "request_timeout": 30,  # 超时时间30秒
        }
        
        # Add base_url if provided
        if base_url:
            common_params["base_url"] = base_url
        
        # Create custom HTTP client without proxy
        import httpx
        http_client = httpx.Client(proxies={"http://": None, "https://": None})
        common_params["http_client"] = http_client
        
        # Create LLM based on provider
        try:
            if provider == LLMProvider.OPENAI:
                return ChatOpenAI(**common_params)
            
            elif provider == LLMProvider.DEEPSEEK:
                # DeepSeek uses OpenAI-compatible API
                deepseek_params = common_params.copy()
                if not base_url:
                    deepseek_params["base_url"] = "https://api.deepseek.com/v1"
                return ChatOpenAI(**deepseek_params)
            
            elif provider == LLMProvider.DOUBAO:
                # Doubao uses OpenAI-compatible API
                doubao_params = common_params.copy()
                if not base_url:
                    doubao_params["base_url"] = "https://ark.cn-beijing.volces.com/api/v3"
                return ChatOpenAI(**doubao_params)
            
            elif provider == LLMProvider.QWEN:
                # Qwen (Alibaba) uses OpenAI-compatible API
                qwen_params = common_params.copy()
                if not base_url:
                    qwen_params["base_url"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                return ChatOpenAI(**qwen_params)
            
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        except Exception as e:
            logger.error(f"创建LLM实例失败 (provider={provider}, model={model}): {e}")
            raise
    
    @staticmethod
    def get_default_llm(temperature: float = 0) -> BaseChatModel:
        """
        Get default LLM instance using application configuration.
        
        Args:
            temperature: Temperature for generation (0 for deterministic)
            
        Returns:
            BaseChatModel: Configured LLM instance
        """
        config = get_llm_config()
        return LLMFactory.create_llm(
            provider=config.get("provider", LLMProvider.OPENAI),
            api_key=config.get("api_key", ""),
            model=config.get("model", "gpt-3.5-turbo"),
            base_url=config.get("base_url", ""),
            temperature=temperature,
        )


# Global factory instance
llm_factory = LLMFactory()


def get_llm_factory() -> LLMFactory:
    """
    Get the LLM factory instance.
    
    Returns:
        LLMFactory: Factory instance
    """
    return llm_factory