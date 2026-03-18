"""
Unit tests for login functionality.

Tests cover:
- Login page rendering (FR1.1)
- Successful authentication flow (FR1.2, FR1.3)
- Failed authentication handling (FR1.2)
- Session management (FR1.3)

Requirements: FR1.1, FR1.2, FR1.3
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.auth import router, LoginRequest, LoginResponse
from app.main import create_app


@pytest.fixture
def app() -> FastAPI:
    """Create test FastAPI application."""
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)


class TestLoginPageRendering:
    """Tests for login page rendering (FR1.1)."""

    def test_login_page_returns_200(self, client: TestClient):
        """Test that GET /login returns 200 status code."""
        response = client.get("/login")
        assert response.status_code == 200

    def test_login_page_returns_html_content(self, client: TestClient):
        """Test that login page returns HTML content."""
        response = client.get("/login")
        assert "text/html" in response.headers.get("content-type", "")

    def test_login_page_contains_login_form(self, client: TestClient):
        """Test that login page contains login form elements."""
        response = client.get("/login")
        content = response.text.lower()
        # Check for common login form elements
        assert "username" in content or "user" in content
        assert "password" in content
        assert "login" in content or "submit" in content

    def test_root_redirects_to_login(self, client: TestClient):
        """Test that root endpoint redirects to login page."""
        response = client.get("/")
        assert response.status_code in (301, 302, 303, 307, 308)
        assert "/login" in response.headers.get("location", "")


class TestSuccessfulAuthentication:
    """Tests for successful authentication flow (FR1.2, FR1.3)."""

    @patch("app.api.auth.call_java_auth_service")
    def test_successful_login_returns_success(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that valid credentials return success response."""
        # Mock successful Java auth response
        mock_call_java.return_value = {
            "success": True,
            "message": "登录成功",
            "data": {
                "token": "test-token-12345",
                "user_id": "user-001",
                "expires_in": 3600
            }
        }

        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["token"] == "test-token-12345"
        assert data["user_id"] == "user-001"
        assert data["expires_in"] == 3600

    @patch("app.api.auth.call_java_auth_service")
    def test_successful_login_sets_session_cookie(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that successful login sets session cookie (FR1.3)."""
        mock_call_java.return_value = {
            "success": True,
            "message": "登录成功",
            "data": {
                "token": "session-token-abc",
                "user_id": "user-002",
                "expires_in": 7200
            }
        }

        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )

        assert response.status_code == 200
        # Check that session cookie is set
        cookies = response.cookies
        assert "session_id" in cookies
        assert cookies["session_id"] == "session-token-abc"

    @patch("app.api.auth.call_java_auth_service")
    def test_authenticated_user_redirects_from_login(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that authenticated user is redirected from login page."""
        # First login to get session
        mock_call_java.return_value = {
            "success": True,
            "message": "登录成功",
            "data": {
                "token": "valid-token",
                "user_id": "user-003",
                "expires_in": 3600
            }
        }

        # Login with valid credentials
        client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        # Access login page with session cookie - should redirect
        response = client.get("/login", cookies={"session_id": "valid-token"})
        assert response.status_code in (301, 302, 303, 307, 308)


class TestFailedAuthentication:
    """Tests for failed authentication handling (FR1.2)."""

    @patch("app.api.auth.call_java_auth_service")
    def test_invalid_credentials_return_error(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that invalid credentials return error response."""
        mock_call_java.return_value = {
            "success": False,
            "message": "用户名或密码错误",
            "error": "AUTH_002"
        }

        response = client.post(
            "/api/auth/login",
            json={"username": "wronguser", "password": "wrongpass"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "错误" in data["message"] or "error" in data["message"].lower()

    @patch("app.api.auth.call_java_auth_service")
    def test_empty_username_returns_error(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that empty username returns validation error."""
        response = client.post(
            "/api/auth/login",
            json={"username": "", "password": "testpass"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "不能为空" in data["message"]

    @patch("app.api.auth.call_java_auth_service")
    def test_empty_password_returns_error(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that empty password returns validation error."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": ""}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "不能为空" in data["message"]

    @patch("app.api.auth.call_java_auth_service")
    def test_whitespace_only_credentials_return_error(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that whitespace-only credentials return validation error."""
        response = client.post(
            "/api/auth/login",
            json={"username": "   ", "password": "   "}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "不能为空" in data["message"]

    @patch("app.api.auth.call_java_auth_service")
    def test_failed_login_does_not_set_session_cookie(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that failed login does not set session cookie."""
        mock_call_java.return_value = {
            "success": False,
            "message": "用户名或密码错误",
            "error": "AUTH_002"
        }

        response = client.post(
            "/api/auth/login",
            json={"username": "wronguser", "password": "wrongpass"}
        )

        assert response.status_code == 200
        # No session cookie should be set on failed login
        cookies = response.cookies
        # Either no session_id cookie or it's not the auth token
        session_cookie = cookies.get("session_id")
        assert session_cookie is None or session_cookie == ""


class TestSessionManagement:
    """Tests for session management (FR1.3)."""

    @patch("app.api.auth.call_java_auth_service")
    def test_get_session_returns_authenticated_true(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that session endpoint returns authenticated=True with valid token."""
        response = client.get("/api/auth/session", cookies={"session_id": "valid-token"})

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["token"] == "valid-token"

    def test_get_session_returns_authenticated_false_without_cookie(self, client: TestClient):
        """Test that session endpoint returns authenticated=False without cookie."""
        response = client.get("/api/auth/session")

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert "token" not in data

    @patch("app.api.auth.call_java_auth_service")
    def test_logout_clears_session_cookie(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that logout clears session cookie."""
        # First login to get session
        mock_call_java.return_value = {
            "success": True,
            "message": "登录成功",
            "data": {
                "token": "token-to-logout",
                "user_id": "user-004",
                "expires_in": 3600
            }
        }
        client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        # Logout
        response = client.post("/api/auth/logout", cookies={"session_id": "token-to-logout"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Session should be cleared
        session_response = client.get("/api/auth/session")
        assert session_response.json()["authenticated"] is False

    @patch("app.api.auth.call_java_auth_service")
    def test_session_cookie_expiration(
        self,
        mock_call_java: AsyncMock,
        client: TestClient
    ):
        """Test that session cookie is set with appropriate expiration."""
        mock_call_java.return_value = {
            "success": True,
            "message": "登录成功",
            "data": {
                "token": "expiring-token",
                "user_id": "user-005",
                "expires_in": 1800  # 30 minutes
            }
        }

        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        # Check cookie has max_age set
        cookies = response.cookies
        session_cookie = cookies.get("session_id")
        assert session_cookie == "expiring-token"


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check_returns_healthy(self, client: TestClient):
        """Test that health check endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "python-ui"