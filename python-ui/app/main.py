"""
Main FastAPI application for Smart Ticket System - Python UI.

Provides user interface endpoints including login and chat pages.

Requirements: FR1.1, FR2.1, NFR1
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, get_static_paths, get_session_config
from app.api import auth, chat


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
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers
    )
    
    # Mount static files
    static_paths = get_static_paths()
    app.mount(
        f"/static/{static_paths['css']}",
        StaticFiles(directory=f"app/static/{static_paths['css']}"),
        name="static-css"
    )
    app.mount(
        f"/static/{static_paths['js']}",
        StaticFiles(directory=f"app/static/{static_paths['js']}"),
        name="static-js"
    )
    
    # Set up templates
    templates = Jinja2Templates(directory="app/templates")
    
    # Include API routers
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
        # Check if user is already logged in
        session_config = get_session_config()
        cookie_name = session_config["cookie_name"]
        
        token = request.cookies.get(cookie_name)
        
        if token:
            # User is logged in, redirect to chat
            return RedirectResponse(url="/chat")
        
        # Render login page
        return templates.TemplateResponse("login.html", {"request": request})
    
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


# Create application instance
app = create_app()


# Re-export configuration functions for convenience
def get_java_service_url() -> str:
    """Get the Java service base URL."""
    return settings.java_service.base_url


def get_java_service_timeout() -> int:
    """Get the Java service timeout in seconds."""
    return settings.java_service.timeout


def get_session_config() -> dict:
    """Get session configuration dictionary."""
    return {
        "secret": settings.session.secret,
        "cookie_name": settings.session.cookie_name,
        "timeout_minutes": settings.session.timeout_minutes,
        "secure": settings.session.secure,
        "httponly": settings.session.httponly
    }


def get_static_paths() -> dict:
    """Get static file paths configuration."""
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