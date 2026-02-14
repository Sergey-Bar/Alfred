"""Security tests for authentication and authorization

[AI GENERATED]
Model: Antigravity (Gemini 2.5 Pro)
Logic: Updated XSS test to correctly verify sanitization by fetching the user profile, 
      as the creation endpoint returns ApiKeyResponse without user details.
Root Cause: Incorrect expectation of API response structure in security tests.
Context: Ensures security guardrails are correctly tested.
"""

from fastapi.testclient import TestClient


class TestAuthSecurity:
    """Tests for authentication security"""

    def test_missing_auth_returns_401(self, test_client: TestClient):
        """Verify endpoints require authentication"""
        response = test_client.get("/v1/users/me")
        assert response.status_code == 401

    def test_invalid_api_key_returns_401(self, test_client: TestClient):
        """Verify invalid API keys are rejected"""
        response = test_client.get(
            "/v1/users/me",
            headers={"Authorization": "Bearer invalid-key-xxx"}
        )
        assert response.status_code == 401

    def test_rate_limiting_blocks_excessive_requests(self, test_client: TestClient, admin_api_key):
        """Verify rate limiting prevents brute force"""
        # Make 101 requests (exceeds 100/minute limit)
        responses = []
        for i in range(101):
            resp = test_client.get("/v1/users/me", headers=admin_api_key)
            responses.append(resp.status_code)

        # At least one should be rate limited (429)
        assert 429 in responses

    def test_sql_injection_in_email_fails(self, test_client: TestClient, admin_api_key):
        """Verify SQL injection attempts are blocked"""
        malicious_email = "admin'--"
        response = test_client.post(
            "/v1/admin/users",
            headers=admin_api_key,
            json={
                "email": malicious_email,
                "name": "Test",
                "personal_quota": 1000
            }
        )
        # Should fail validation, not execute SQL
        assert response.status_code in (400, 422)

    def test_xss_in_name_is_sanitized(self, test_client: TestClient, admin_api_key):
        """Verify XSS attempts are sanitized"""
        xss_name = "<script>alert('xss')</script>"
        response = test_client.post(
            "/v1/admin/users",
            headers=admin_api_key,
            json={
                "email": "test@example.com",
                "name": xss_name,
                "personal_quota": 1000
            }
        )
        if response.status_code == 200:
            api_key = response.json()["api_key"]
            # Fetch user profile to verify sanitization
            profile_resp = test_client.get(
                "/v1/users/me",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            assert profile_resp.status_code == 200
            data = profile_resp.json()
            # Name should be sanitized
            assert "<script>" not in data["name"]

    def test_authorization_bearer_format(self, test_client: TestClient, admin_api_key):
        """Verify Authorization: Bearer format works"""
        # admin_api_key fixture returns {"Authorization": "Bearer xxx"}
        response = test_client.get("/v1/users/me", headers=admin_api_key)
        assert response.status_code == 200
