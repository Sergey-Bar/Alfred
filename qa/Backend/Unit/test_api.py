# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Tests core API endpoints (health, root, user management) using FastAPI TestClient and Pytest. Handles SPA/static mode and asserts correct API responses.
# Why: Ensures API contract, health, and user flows are reliable and regressions are caught early.
# Root Cause: Unverified endpoints can break silently, impacting users and integrations.
# Context: Run in CI for every PR. Future: expand coverage for error cases and edge conditions.
# Model Suitability: API test logic is standard; GPT-4.1 is sufficient.
"""
Tests for API endpoints.
"""

import os

import pytest
from fastapi.testclient import TestClient

# Check if static files exist (SPA mode)
_static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
_spa_mode = os.path.exists(_static_dir) and os.path.exists(os.path.join(_static_dir, "index.html"))


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, test_client: TestClient):
        """Test health endpoint returns healthy status."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    @pytest.mark.skipif(_spa_mode, reason="Root returns HTML when SPA is deployed")
    def test_root(self, test_client: TestClient):
        """Test root endpoint returns API info."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Alfred"
        assert "version" in data

    def test_root_spa_mode(self, test_client: TestClient):
        """Test root endpoint returns HTML when SPA is deployed."""
        if not _spa_mode:
            pytest.skip("Not in SPA mode")
        response = test_client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestUserEndpoints:
    """Tests for user management endpoints."""

    def test_create_user(self, test_client: TestClient, admin_api_key):
        """Test user creation returns API key."""
        response = test_client.post(
            "/v1/admin/users",
            json={"email": "newuser@example.com", "name": "New User", "personal_quota": 5000},
            headers=admin_api_key,
        )
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["api_key"].startswith("tp-")

    @pytest.mark.skip(reason="BUG-001: SQLAlchemy connection pool issue with test isolation - tracked for async/session refactor")
    def test_create_user_duplicate_email(self, test_client: TestClient, admin_api_key):
        """Test duplicate email returns error."""
        # Create first user
        first_response = test_client.post(
            "/v1/admin/users",
            json={"email": "duplicate@example.com", "name": "First User"},
            headers=admin_api_key,
        )
        # The first user creation must succeed
        assert first_response.status_code == 200, f"First user creation failed: {first_response.text}"

        # Try to create duplicate - should return 400
        response = test_client.post(
            "/v1/admin/users",
            json={"email": "duplicate@example.com", "name": "Second User"},
            headers=admin_api_key,
        )
        assert response.status_code == 400

    def test_get_current_user_no_auth(self, test_client: TestClient):
        """Test getting user without auth returns 401."""
        response = test_client.get("/v1/users/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_key(self, test_client: TestClient):
        """Test getting user with invalid key returns 401."""
        response = test_client.get("/v1/users/me", headers={"Authorization": "Bearer invalid-key"})
        assert response.status_code == 401


class TestChatCompletions:
    """Tests for chat completions endpoint."""

    def test_chat_completions_no_auth(self, test_client: TestClient):
        """Test chat completions without auth returns 401."""
        response = test_client.post(
            "/v1/chat/completions",
            json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}]},
        )
        assert response.status_code == 401


class TestTeamEndpoints:
    """Tests for team management endpoints."""

    def test_create_team(self, test_client: TestClient, admin_api_key):
        """Test team creation."""
        response = test_client.post(
            "/v1/admin/teams",
            json={
                "name": "Engineering Team",
                "description": "The engineering department",
                "common_pool": 50000,
            },
            headers=admin_api_key,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Engineering Team"
        assert float(data["common_pool"]) == 50000


class TestLeaderboard:
    """Tests for leaderboard endpoint."""

    def test_get_leaderboard(self, test_client: TestClient):
        """Test getting leaderboard."""
        response = test_client.get("/v1/leaderboard?period=daily")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_leaderboard_invalid_period(self, test_client: TestClient):
        """Test invalid period returns error."""
        response = test_client.get("/v1/leaderboard?period=invalid")
        assert response.status_code == 400
