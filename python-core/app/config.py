"""
Configuration management for Smart Ticket System - Python Core.

Uses Pydantic for type validation and python-dotenv for environment variable management.
"""
import os
from enum import Enum
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel


class DataSourceType(str, Enum):
    """Data source type enumeration."""
    MOCK = "mock"
    REAL = "real"


class LLMProvider(str, Enum):
    """LLM provider enumeration."""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    DOUBAO = "doubao"


class LLMConfig(BaseModel):
    """LLM configuration settings."""
    provider: LLMProvider = LLMProvider.OPENAI
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    base_url: str = ""


class AppConfig(BaseModel):
    """Application configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


class SessionConfig(BaseModel):
    """Session configuration settings."""
    secret: str = "default-session-secret-change-in-production"


class IntentConfig(BaseModel):
    """Intent recognition configuration settings."""
    confidence_threshold: float = 0.7


class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    level: str = "INFO"


class CORSConfig(BaseModel):
    """CORS (Cross-Origin Resource Sharing) configuration settings."""
    allow_origins: list = ["*"]
    allow_credentials: bool = True
    allow_methods: list = ["*"]
    allow_headers: list = ["*"]


class Settings(BaseModel):
    """
    Application settings loaded from environment variables.
    
    Uses pydantic for type validation and python-dotenv for .env file loading.
    """
    # LLM Configuration
    llm: LLMConfig = LLMConfig()
    
    # Application Configuration
    app: AppConfig = AppConfig()
    
    # CORS Configuration
    cors: CORSConfig = CORSConfig()
    
    # Data Source Configuration
    # Set to "mock" for mock data, or "real" for real business system
    data_source: DataSourceType = DataSourceType.MOCK
    
    # Session Configuration
    session: SessionConfig = SessionConfig()
    
    # Intent Recognition Configuration
    intent: IntentConfig = IntentConfig()
    
    # Logging Configuration
    logging: LoggingConfig = LoggingConfig()


def _get_env(key: str, default: str = "") -> str:
    """
    Get environment variable with optional default.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        str: Environment variable value or default
    """
    return os.environ.get(key, default)


def _get_bool_env(key: str, default: bool = False) -> bool:
    """
    Get boolean environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        bool: Environment variable value as boolean
    """
    value = _get_env(key, str(default)).lower()
    return value in ("true", "1", "yes")


def _get_int_env(key: str, default: int = 0) -> int:
    """
    Get integer environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        int: Environment variable value as integer
    """
    try:
        return int(_get_env(key, str(default)))
    except ValueError:
        return default


def _get_float_env(key: str, default: float = 0.0) -> float:
    """
    Get float environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        float: Environment variable value as float
    """
    try:
        return float(_get_env(key, str(default)))
    except ValueError:
        return default


def load_settings() -> Settings:
    """
    Load settings from environment variables and .env file.
    
    Returns:
        Settings: Loaded settings instance
    """
    # Load .env file if it exists
    load_dotenv()
    
    # LLM settings
    provider_value = _get_env("LLM_PROVIDER", "openai").lower()
    provider = LLMProvider.OPENAI
    if provider_value == "deepseek":
        provider = LLMProvider.DEEPSEEK
    elif provider_value == "doubao":
        provider = LLMProvider.DOUBAO
    
    # Get API key based on provider
    api_key = ""
    if provider == LLMProvider.OPENAI:
        api_key = _get_env("OPENAI_API_KEY", "")
    elif provider == LLMProvider.DEEPSEEK:
        api_key = _get_env("DEEPSEEK_API_KEY", "")
    elif provider == LLMProvider.DOUBAO:
        api_key = _get_env("DOUBAO_API_KEY", "")
    
    # Get model based on provider
    model = ""
    if provider == LLMProvider.OPENAI:
        model = _get_env("OPENAI_MODEL", "gpt-3.5-turbo")
    elif provider == LLMProvider.DEEPSEEK:
        model = _get_env("DEEPSEEK_MODEL", "deepseek-chat")
    elif provider == LLMProvider.DOUBAO:
        model = _get_env("DOUBAO_MODEL", "Doubao-pro-32k")
    
    # Get base URL if provided
    base_url = _get_env("LLM_BASE_URL", "")
    
    llm_config = LLMConfig(
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url
    )
    
    # App settings
    app_config = AppConfig(
        host=_get_env("APP_HOST", "0.0.0.0"),
        port=_get_int_env("APP_PORT", 8000),
        debug=_get_bool_env("DEBUG", False)
    )
    
    # CORS settings
    cors_origins = _get_env("CORS_ALLOW_ORIGINS", "*").split(",")
    cors_config = CORSConfig(
        allow_origins=cors_origins if cors_origins != ["*"] else ["*"],
        allow_credentials=_get_bool_env("CORS_ALLOW_CREDENTIALS", True),
        allow_methods=_get_env("CORS_ALLOW_METHODS", "*").split(","),
        allow_headers=_get_env("CORS_ALLOW_HEADERS", "*").split(",")
    )
    
    # Data source
    data_source_value = _get_env("DATA_SOURCE", "mock").lower()
    data_source = DataSourceType.MOCK
    if data_source_value == "real":
        data_source = DataSourceType.REAL
    
    # Session settings
    session_config = SessionConfig(
        secret=_get_env("SESSION_SECRET", "default-session-secret-change-in-production")
    )
    
    # Intent settings
    intent_config = IntentConfig(
        confidence_threshold=_get_float_env("INTENT_CONFIDENCE_THRESHOLD", 0.7)
    )
    
    # Logging settings
    logging_config = LoggingConfig(
        level=_get_env("LOG_LEVEL", "INFO")
    )
    
    return Settings(
        llm=llm_config,
        app=app_config,
        cors=cors_config,
        data_source=data_source,
        session=session_config,
        intent=intent_config,
        logging=logging_config
    )


# Global settings instance
settings = load_settings()


def get_llm_config() -> dict:
    """
    Get LLM configuration dictionary for LangChain.
    
    Returns:
        dict: LLM configuration with provider, API key, model name, and base URL.
    """
    return {
        "provider": settings.llm.provider,
        "api_key": settings.llm.api_key,
        "model": settings.llm.model,
        "base_url": settings.llm.base_url,
    }


def get_data_source() -> DataSourceType:
    """
    Get the current data source type.
    
    Returns:
        DataSourceType: Either MOCK or REAL data source.
    """
    return settings.data_source


def is_mock_data_source() -> bool:
    """
    Check if using mock data source.
    
    Returns:
        bool: True if using mock data, False otherwise.
    """
    return settings.data_source == DataSourceType.MOCK