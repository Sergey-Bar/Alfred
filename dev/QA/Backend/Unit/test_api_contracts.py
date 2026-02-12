"""
API contract tests — verify response shapes for critical endpoints.

These tests assert that the API returns the expected field names and basic types
so frontend and other clients can rely on stable contracts.
"""

import pytest
from fastapi.testclient import TestClient


def test_get_current_user_contract(test_client: TestClient, admin_api_key):
    resp = test_client.get("/v1/users/me", headers=admin_api_key)
    assert resp.status_code == 200
    data = resp.json()
    # Required keys in UserResponse
    expected_keys = {"id", "email", "name", "status", "personal_quota", "used_tokens", "available_quota", "default_priority", "preferences"}
    assert expected_keys.issubset(set(data.keys()))


def test_admin_users_requires_auth(test_client: TestClient):
    # Calling admin endpoint without auth should be unauthorized (401) or forbidden
    resp = test_client.post("/v1/admin/users", json={"email": "x@x.com", "name": "X"})
    assert resp.status_code in (401, 403)


def test_create_approval_contract(test_client: TestClient, admin_api_key):
    body = {"requested_credits": 1000, "reason": "Need more for test"}
    resp = test_client.post("/v1/approvals", json=body, headers=admin_api_key)
    assert resp.status_code == 200
    data = resp.json()
    expected = {"id", "status", "requested_credits", "approved_credits", "reason", "created_at"}
    assert expected.issubset(set(data.keys()))
