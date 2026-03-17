"""
API module for the Smart Ticket System.

This module provides API endpoints for:
- Intent recognition and chat
- Logistics queries
- Urgent ticket creation
- Order cancellation
"""

from app.api.routes import router

__all__ = ["router"]