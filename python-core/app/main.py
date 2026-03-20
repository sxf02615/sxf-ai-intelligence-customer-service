"""
Smart Ticket System - Python Core Application

This is the main entry point for the Python core business layer.
It sets up the FastAPI application with CORS configuration.
"""

import logging
import sys
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Middleware to log all incoming requests and outgoing responses."""
    
    async def __call__(self, request: Request, call_next):
        # Log incoming request
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            body_str = body.decode() if body else ""
            logger.info(f"==> 收到请求: {request.method} {request.url.path}")
            logger.info(f"    请求头: {dict(request.headers)}")
            if body_str:
                logger.info(f"    请求体: {body_str[:500]}")  # Limit body length
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log outgoing response
        logger.info(f"<== 返回响应: {request.method} {request.url.path} - {response.status_code}")
        logger.info(f"    处理时间: {process_time:.3f}s")
        
        return response


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Smart Ticket System - Core API",
        description="AI-powered ticket system for logistics, urgent tickets, and order cancellation",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS for cross-origin requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    
    # Add logging middleware
    app.middleware("http")(LoggingMiddleware())
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "service": "smart-ticket-core",
            "version": "1.0.0"
        }
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )