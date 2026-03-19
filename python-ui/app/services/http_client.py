"""
HTTP client for communicating with Java service.

Provides async HTTP client with authentication token handling,
error handling, and retry logic for calling Java backend APIs.

Requirements: NFR7
"""

import logging
from typing import Optional, Any, Dict
from contextlib import asynccontextmanager

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)

from app.config import get_java_service_url, get_java_service_timeout


logger = logging.getLogger(__name__)


class JavaServiceClient:
    """
    Async HTTP client for Java service communication.
    
    Handles authentication token injection, request retry logic,
    and error handling for all Java service API calls.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3,
        backoff_factor: float = 0.5
    ):
        """
        Initialize the Java service client.
        
        Args:
            base_url: Java service base URL (defaults to config value)
            timeout: Request timeout in seconds (defaults to config value)
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        self.base_url = base_url or get_java_service_url()
        self.timeout = timeout or get_java_service_timeout()
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """获取或创建HTTP客户端实例。"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """
        Get HTTP headers with optional authentication token.
        
        Args:
            token: Optional authentication token
            
        Returns:
            dict: Headers with Content-Type and optional Authorization
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    @asynccontextmanager
    async def client_context(self, token: Optional[str] = None):
        """
        Context manager for HTTP client with optional token.
        
        Args:
            token: Optional authentication token for requests
        """
        client = self._get_client()
        try:
            yield client
        finally:
            pass  # 客户端生命周期由外部管理
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO)
    )
    async def get(
        self,
        endpoint: str,
        token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """
        Perform GET request to Java service with retry logic.
        
        Args:
            endpoint: API endpoint (will be appended to base URL)
            token: Optional authentication token
            params: Optional query parameters
            
        Returns:
            httpx.Response: HTTP response object
            
        Raises:
            httpx.HTTPStatusError: On HTTP errors (4xx, 5xx)
            httpx.RequestError: On network/request errors
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(token)
        
        logger.debug(f"GET {url}")
        
        async with self.client_context(token) as client:
            return await client.get(
                url,
                headers=headers,
                params=params
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO)
    )
    async def post(
        self,
        endpoint: str,
        token: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """
        Perform POST request to Java service with retry logic.
        
        Args:
            endpoint: API endpoint (will be appended to base URL)
            token: Optional authentication token
            json: Optional JSON body data
            
        Returns:
            httpx.Response: HTTP response object
            
        Raises:
            httpx.HTTPStatusError: On HTTP errors (4xx, 5xx)
            httpx.RequestError: On network/request errors
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(token)
        
        logger.debug(f"POST {url}")
        
        async with self.client_context(token) as client:
            return await client.post(
                url,
                headers=headers,
                json=json
            )
    
    async def call_chat_api(
        self,
        session_id: str,
        user_id: str,
        message: str,
        token: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call the chat API endpoint.
        
        POST /api/v1/chat
        
        Args:
            session_id: User session ID
            user_id: User ID
            message: User message
            token: Authentication token
            context: Optional conversation context
            
        Returns:
            dict: Chat response with intent, response, and session info
            
        Raises:
            JavaServiceError: On service errors
        """
        try:
            response = await self.post(
                "/api/v1/chat",
                token=token,
                json={
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": message,
                    "context": context or {}
                }
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Chat API error: {e.response.status_code} - {e.response.text}")
            raise JavaServiceError(
                f"Chat service error: {e.response.status_code}",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Chat API request error: {str(e)}")
            raise JavaServiceError(
                f"Failed to connect to chat service: {str(e)}",
                status_code=503
            )
    
    async def call_logistics_api(
        self,
        order_id: str,
        token: str
    ) -> Dict[str, Any]:
        """
        Call the logistics API endpoint.
        
        GET /api/v1/logistics/{order_id}
        
        Args:
            order_id: Order ID to query
            token: Authentication token
            
        Returns:
            dict: Logistics information for the order
            
        Raises:
            JavaServiceError: On service errors
        """
        try:
            response = await self.get(
                f"/api/v1/logistics/{order_id}",
                token=token
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Logistics API error: {e.response.status_code} - {e.response.text}")
            raise JavaServiceError(
                f"Logistics service error: {e.response.status_code}",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Logistics API request error: {str(e)}")
            raise JavaServiceError(
                f"Failed to connect to logistics service: {str(e)}",
                status_code=503
            )
    
    async def call_urgent_ticket_api(
        self,
        order_id: str,
        reason: Optional[str],
        token: str
    ) -> Dict[str, Any]:
        """
        Call the urgent ticket API endpoint.
        
        POST /api/v1/tickets/urgent
        
        Args:
            order_id: Order ID for the ticket
            reason: Optional reason for urgency
            token: Authentication token
            
        Returns:
            dict: Created ticket information
            
        Raises:
            JavaServiceError: On service errors
        """
        try:
            response = await self.post(
                "/api/v1/tickets/urgent",
                token=token,
                json={
                    "order_id": order_id,
                    "reason": reason
                }
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Urgent ticket API error: {e.response.status_code} - {e.response.text}")
            raise JavaServiceError(
                f"Urgent ticket service error: {e.response.status_code}",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Urgent ticket API request error: {str(e)}")
            raise JavaServiceError(
                f"Failed to connect to urgent ticket service: {str(e)}",
                status_code=503
            )
    
    async def call_cancel_order_api(
        self,
        order_id: str,
        reason: str,
        token: str
    ) -> Dict[str, Any]:
        """
        Call the cancel order API endpoint.
        
        POST /api/v1/orders/cancel
        
        Args:
            order_id: Order ID to cancel
            reason: Reason for cancellation
            token: Authentication token
            
        Returns:
            dict: Cancel result with refund information
            
        Raises:
            JavaServiceError: On service errors
        """
        try:
            response = await self.post(
                "/api/v1/orders/cancel",
                token=token,
                json={
                    "order_id": order_id,
                    "reason": reason
                }
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Cancel order API error: {e.response.status_code} - {e.response.text}")
            raise JavaServiceError(
                f"Cancel order service error: {e.response.status_code}",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Cancel order API request error: {str(e)}")
            raise JavaServiceError(
                f"Failed to connect to cancel order service: {str(e)}",
                status_code=503
            )
    
    async def close(self):
        """关闭HTTP客户端并释放资源。"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self) -> "JavaServiceClient":
        """异步上下文管理器入口。"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出。"""
        await self.close()


class JavaServiceError(Exception):
    """
    Exception raised when Java service calls fail.
    
    Attributes:
        message: Error description
        status_code: HTTP status code (if applicable)
    """
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# 全局客户端实例以方便使用
_client: Optional[JavaServiceClient] = None


def get_java_client() -> JavaServiceClient:
    """
    Get the global Java service client instance.
    
    Returns:
        JavaServiceClient: Configured HTTP client for Java service
    """
    global _client
    if _client is None:
        _client = JavaServiceClient()
    return _client


async def close_java_client():
    """关闭全局Java服务客户端。"""
    global _client
    if _client:
        await _client.close()
        _client = None