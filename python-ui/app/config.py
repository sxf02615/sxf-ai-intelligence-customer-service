"""
Configuration management for Smart Ticket System - Python UI.

Uses Pydantic for type validation and python-dotenv for environment variable management.
"""
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel


class JavaServiceConfig(BaseModel):
    """Java service configuration settings."""
    base_url: str = "http://localhost:8080"
    timeout: int = 30


class SessionConfig(BaseModel):
    """Session configuration settings."""
    secret: str = "default-session-secret-change-in-production"
    cookie_name: str = "session_id"
    timeout_minutes: int = 60
    secure: bool = False
    httponly: bool = True


class StaticFilesConfig(BaseModel):
    """Static files configuration settings."""
    css_path: str = "css"
    js_path: str = "js"
    images_path: str = "images"


class AppConfig(BaseModel):
    """Application configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False
    title: str = "Smart Ticket System"


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
    # Java Service Configuration
    java_service: JavaServiceConfig = JavaServiceConfig()
    
    # Application Configuration
    app: AppConfig = AppConfig()
    
    # Session Configuration
    session: SessionConfig = SessionConfig()
    
    # Static Files Configuration
    static_files: StaticFilesConfig = StaticFilesConfig()
    
    # CORS Configuration
    cors: CORSConfig = CORSConfig()


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


def load_settings() -> Settings:
    """
    Load settings from environment variables and .env file.
    
    Returns:
        Settings: Loaded settings instance
    """
    # Load .env file if it exists
    load_dotenv()
    
    # Java service settings
    java_service_config = JavaServiceConfig(
        base_url=_get_env("JAVA_SERVICE_URL", "http://localhost:8080"),
        timeout=_get_int_env("JAVA_SERVICE_TIMEOUT", 30)
    )
    
    # App settings
    app_config = AppConfig(
        host=_get_env("APP_HOST", "0.0.0.0"),
        port=_get_int_env("APP_PORT", 8001),
        debug=_get_bool_env("DEBUG", False),
        title=_get_env("APP_TITLE", "Smart Ticket System")
    )
    
    # Session settings
    session_config = SessionConfig(
        secret=_get_env("SESSION_SECRET", "default-session-secret-change-in-production"),
        cookie_name=_get_env("SESSION_COOKIE_NAME", "session_id"),
        timeout_minutes=_get_int_env("SESSION_TIMEOUT_MINUTES", 60),
        secure=_get_bool_env("SESSION_SECURE", False),
        httponly=_get_bool_env("SESSION_HTTPONLY", True)
    )
    
    # Static files settings
    static_files_config = StaticFilesConfig(
        css_path=_get_env("STATIC_CSS_PATH", "css"),
        js_path=_get_env("STATIC_JS_PATH", "js"),
        images_path=_get_env("STATIC_IMAGES_PATH", "images")
    )
    
    # CORS settings
    cors_origins = _get_env("CORS_ALLOW_ORIGINS", "*").split(",")
    cors_config = CORSConfig(
        allow_origins=cors_origins if cors_origins != ["*"] else ["*"],
        allow_credentials=_get_bool_env("CORS_ALLOW_CREDENTIALS", True),
        allow_methods=_get_env("CORS_ALLOW_METHODS", "*").split(","),
        allow_headers=_get_env("CORS_ALLOW_HEADERS", "*").split(",")
    )
    
    return Settings(
        java_service=java_service_config,
        app=app_config,
        session=session_config,
        static_files=static_files_config,
        cors=cors_config
    )


# Global settings instance
settings = load_settings()


def get_java_service_url() -> str:
    """
    Get the Java service base URL.
    
    Returns:
        str: Java service base URL.
    """
    return settings.java_service.base_url


def get_java_service_timeout() -> int:
    """
    Get the Java service timeout in seconds.
    
    Returns:
        int: Timeout in seconds.
    """
    return settings.java_service.timeout


def get_session_config() -> dict:
    """
    Get session configuration dictionary.
    
    Returns:
        dict: Session configuration with secret, cookie name, and timeout.
    """
    return {
        "secret": settings.session.secret,
        "cookie_name": settings.session.cookie_name,
        "timeout_minutes": settings.session.timeout_minutes,
        "secure": settings.session.secure,
        "httponly": settings.session.httponly
    }


def get_static_paths() -> dict:
    """
    Get static file paths configuration.
    
    Returns:
        dict: Static file paths for CSS, JS, and images.
    """
    return {
        "css": settings.static_files.css_path,
        "js": settings.static_files.js_path,
        "images": settings.static_files.images_path
    }