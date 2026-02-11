"""
Tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


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
    
    def test_root(self, test_client: TestClient):
        """Test root endpoint returns API info."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TokenPool"
        assert "version" in data


class TestUserEndpoints:
    """Tests for user management endpoints."""
    
    def test_create_user(self, test_client: TestClient):
        """Test user creation returns API key."""
        response = test_client.post(
            "/v1/admin/users",
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "personal_quota": 5000
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["api_key"].startswith("ab-")
    
    def test_create_user_duplicate_email(self, test_client: TestClient):
        """Test duplicate email returns error."""
        # Create first user
        test_client.post(
            "/v1/admin/users",
            json={
                "email": "duplicate@example.com",
                "name": "First User"
            }
        )
        
        # Try to create duplicate
        response = test_client.post(
            "/v1/admin/users",
            json={
                "email": "duplicate@example.com",
                "name": "Second User"
            }
        )
        assert response.status_code == 400
    
    def test_get_current_user_no_auth(self, test_client: TestClient):
        """Test getting user without auth returns 401."""
        response = test_client.get("/v1/users/me")
        assert response.status_code == 401
    
    def test_get_current_user_invalid_key(self, test_client: TestClient):
        """Test getting user with invalid key returns 401."""
        response = test_client.get(
            "/v1/users/me",
            headers={"Authorization": "Bearer invalid-key"}
        )
        assert response.status_code == 401


class TestChatCompletions:
    """Tests for chat completions endpoint."""
    
    def test_chat_completions_no_auth(self, test_client: TestClient):
        """Test chat completions without auth returns 401."""
        response = test_client.post(
            "/v1/chat/completions",
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
        assert response.status_code == 401


class TestTeamEndpoints:
    """Tests for team management endpoints."""
    
    def test_create_team(self, test_client: TestClient):
        """Test team creation."""
        response = test_client.post(
            "/v1/admin/teams",
            json={
                "name": "Engineering Team",
                "description": "The engineering department",
                "common_pool": 50000
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Engineering Team"
        assert data["common_pool"] == 50000


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
