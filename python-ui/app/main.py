"""
Main FastAPI application for Smart Ticket System - Python UI.

Provides user interface endpoints including login and chat pages.

Requirements: FR1.1, FR2.1, NFR1
"""

import logging
import sys
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, get_static_paths, get_session_config
from app.api import auth, chat

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
                logger.info(f"    请求体: {body_str[:500]}")
        
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
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.app.title,
        debug=settings.app.debug
    )
    
    # 配置CORS跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers
    )
    
    # 添加日志中间件
    app.middleware("http")(LoggingMiddleware())
    
    # 挂载静态文件
    static_paths = get_static_paths()
    app.mount(
        f"/static/{static_paths['css']}",
        StaticFiles(directory=f"app/static/{static_paths['css']}"),
        name="static-css"
    )
    app.mount(
        "/static/js",
        StaticFiles(directory="app/static/js"),
        name="static-js"
    )
    
    # 设置模板
    templates = Jinja2Templates(directory="app/templates")
    
    # 包含API路由
    app.include_router(auth.router)
    app.include_router(chat.router)
    
    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        """
        Root endpoint - redirect to login or chat based on authentication.
        
        GET /
        
        Args:
            request: Request object for checking session cookies
            
        Returns:
            HTMLResponse: Redirect to /login or /chat
        """
        return RedirectResponse(url="/login")
    
    @app.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        """
        Render login page.
        
        GET /login
        
        If user is already authenticated (has valid session cookie),
        redirects to chat page.
        
        Args:
            request: Request object for checking session cookies
            
        Returns:
            HTMLResponse: Login page template or redirect to chat
        """
        # 检查用户是否已登录
        session_config = get_session_config()
        cookie_name = session_config["cookie_name"]
        
        token = request.cookies.get(cookie_name)
        
        if token:
            # 用户已登录，重定向到聊天页面
            return RedirectResponse(url="/chat")
        
        # 渲染登录页面
        return templates.TemplateResponse("login.html", {"request": request})
    
    @app.get("/chat", response_class=HTMLResponse)
    async def chat_page(request: Request):
        """
        Render chat page.
        
        GET /chat
        
        If user is not authenticated (no valid session cookie),
        redirects to login page.
        
        Requirements: FR1.5
        
        Args:
            request: Request object for checking session cookies
            
        Returns:
            HTMLResponse: Chat page template or redirect to login
        """
        # 检查用户是否已认证
        session_config = get_session_config()
        cookie_name = session_config["cookie_name"]
        
        token = request.cookies.get(cookie_name)
        
        if not token:
            # 用户未登录，重定向到登录页面
            return RedirectResponse(url="/login")
        
        # 渲染聊天页面
        return templates.TemplateResponse("chat.html", {"request": request})
    
    @app.get("/health")
    async def health_check() -> dict:
        """
        Health check endpoint.
        
        GET /health
        
        Returns:
            dict: Health status
        """
        return {"status": "healthy", "service": "python-ui"}
    
    return app


# 创建应用实例
app = create_app()


# 重新导出配置函数以方便使用
def get_java_service_url() -> str:
    """获取Java服务基础URL。"""
    return settings.java_service.base_url


def get_java_service_timeout() -> int:
    """获取Java服务的超时时间（秒）。"""
    return settings.java_service.timeout


def get_session_config() -> dict:
    """获取会话配置字典。"""
    return {
        "secret": settings.session.secret,
        "cookie_name": settings.session.cookie_name,
        "timeout_minutes": settings.session.timeout_minutes,
        "secure": settings.session.secure,
        "httponly": settings.session.httponly
    }


def get_static_paths() -> dict:
    """获取静态文件路径配置。"""
    return {
        "css": settings.static_files.css_path,
        "js": settings.static_files.js_path,
        "images": settings.static_files.images_path
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )