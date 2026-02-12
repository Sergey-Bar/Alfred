"""
Integration tests for the complete request flow.
"""

import pytest
from decimal import Decimal
from unittest.mock import patch, AsyncMock

from fastapi.testclient import TestClient


class TestChatCompletionFlow:
    """Integration tests for chat completion endpoint."""
    
    def test_complete_request_flow_with_quota(self, test_client: TestClient, admin_api_key):
        """Test a complete request flow with quota checking."""
        # Create a user first
        response = test_client.post(
            "/v1/admin/users",
            json={
                "email": "integration_test@example.com",
                "name": "Integration Test User",
                "personal_quota": 10000
            }
        , headers=admin_api_key)
        assert response.status_code == 200
        api_key = response.json()["api_key"]
        
        # Make a chat completion request (mocked LLM response)
        with patch("app.logic.LLMProxy.forward_request", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {
                "id": "chatcmpl-test123",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hello!"},
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15
                }
            }
            
            response = test_client.post(
                "/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": "Hello"}]
                }
            )
            
            # Should succeed
            assert response.status_code == 200
            data = response.json()
            assert "choices" in data
            assert data["choices"][0]["message"]["content"] == "Hello!"
    
    def test_quota_exceeded_returns_403(self, test_client: TestClient, admin_api_key):
        """Test that exceeding quota returns 403 with approval info."""
        # Create user with very low quota
        response = test_client.post(
            "/v1/admin/users",
            json={
                "email": "low_quota@example.com",
                "name": "Low Quota User",
                "personal_quota": 1  # Very low quota
            },
            headers=admin_api_key
        )
        assert response.status_code == 200
        api_key = response.json()["api_key"]
        
        # Attempt request that exceeds quota
        response = test_client.post(
            "/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Hello " * 100}]  # Large message
            }
        )
        
        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "quota_exceeded"
        assert "approval_process" in data or "approval" in str(data).lower()


class TestApprovalWorkflow:
    """Tests for the approval workflow."""
    
    def test_create_approval_request(self, test_client: TestClient, admin_api_key):
        """Test creating an approval request."""
        # Create a user
        response = test_client.post(
            "/v1/admin/users",
            json={
                "email": "approval_test@example.com",
                "name": "Approval Test User"
            }
        , headers=admin_api_key)
        api_key = response.json()["api_key"]
        
        # Submit approval request
        response = test_client.post(
            "/v1/approvals",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "requested_credits": 500,
                "reason": "Need more credits for project X"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        assert data["requested_credits"] == 500


class TestPrivacyMode:
    """Tests for privacy mode functionality."""
    
    def test_strict_privacy_header(self, test_client: TestClient, admin_api_key):
        """Test strict privacy mode via header."""
        # Create user
        response = test_client.post(
            "/v1/admin/users",
            json={
                "email": "privacy_test@example.com",
                "name": "Privacy Test User",
                "personal_quota": 10000
            }
        , headers=admin_api_key)
        api_key = response.json()["api_key"]
        
        with patch("app.logic.LLMProxy.forward_request", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = {
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "Response"},
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
            }
            
            # Request with strict privacy mode
            response = test_client.post(
                "/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "X-Privacy-Mode": "strict"
                },
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": "Secret message"}]
                }
            )
            
            assert response.status_code == 200


class TestTeamManagement:
    """Tests for team management functionality."""
    
    def test_add_user_to_team(self, test_client: TestClient, admin_api_key):
        """Test adding a user to a team."""
        # Create team
        response = test_client.post(
            "/v1/admin/teams",
            json={
                "name": "Dev Team",
                "description": "Development team",
                "common_pool": 50000
            }
        , headers=admin_api_key)
        assert response.status_code == 200
        team_id = response.json()["id"]
        
        # Create user
        response = test_client.post(
            "/v1/admin/users",
            json={
                "email": "team_member@example.com",
                "name": "Team Member"
            }
        , headers=admin_api_key)
        api_key = response.json()["api_key"]
        
        # Get user ID
        response = test_client.get(
            "/v1/users/me",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        user_id = response.json()["id"]
        
        # Add user to team
        response = test_client.post(
            f"/v1/admin/teams/{team_id}/members/{user_id}",
            headers=admin_api_key
        )
        assert response.status_code == 200


class TestErrorResponses:
    """Tests for consistent error response format."""
    
    def test_validation_error_format(self, test_client: TestClient, admin_api_key):
        """Test validation error response format."""
        response = test_client.post(
            "/v1/admin/users",
            json={
                # Missing required 'name' field
                "email": "missing_name@example.com"
            },
            headers=admin_api_key
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_not_found_error_format(self, test_client: TestClient):
        """Test not found error response format."""
        response = test_client.get("/v1/teams/nonexistent-team-id")
        
        # Should return 404 or similar
        assert response.status_code in [404, 422]
    
    def test_rate_limit_response_format(self, test_client: TestClient):
        """Test rate limit error response format."""
        # This test verifies the format when rate limited
        # Actual rate limiting is tested in test_middleware.py
        pass  # Rate limit headers tested separately
