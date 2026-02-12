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


def test_get_user_transfers_contract(test_client: TestClient, admin_api_key):
    """Test /v1/users/me/transfers response contract"""
    resp = test_client.get("/v1/users/me/transfers", headers=admin_api_key)
    assert resp.status_code == 200
    data = resp.json()
    
    # Response should be a dict with sent/received arrays
    assert isinstance(data, dict)
    expected_keys = {"sent", "received", "total_sent", "total_received"}
    assert expected_keys.issubset(set(data.keys()))
    
    # Arrays should be lists
    assert isinstance(data["sent"], list)
    assert isinstance(data["received"], list)
    
    # If there are transfers, check their structure
    all_transfers = data["sent"] + data["received"]
    if len(all_transfers) > 0:
        transfer = all_transfers[0]
        expected_transfer_keys = {"id", "sender_id", "recipient_id", "amount", "created_at"}
        assert expected_transfer_keys.issubset(set(transfer.keys()))


def test_get_dashboard_overview_contract(test_client: TestClient, admin_api_key):
    """Test /v1/dashboard/overview response contract"""
    resp = test_client.get("/v1/dashboard/overview", headers=admin_api_key)
    assert resp.status_code == 200
    data = resp.json()
    
    # Expected top-level keys in dashboard overview (actual API structure)
    expected_keys = {
        "total_users",
        "total_teams",
        "total_requests",
        "total_tokens_used",
        "total_credits_spent",
        "active_users_7d",
        "pending_approvals"
    }
    assert expected_keys.issubset(set(data.keys()))
    
    # Validate types
    assert isinstance(data["total_users"], int)
    assert isinstance(data["total_teams"], int)
    assert isinstance(data["total_requests"], int)
    assert isinstance(data["pending_approvals"], int)


def test_admin_endpoint_requires_admin_flag(test_client: TestClient, session):
    """Test that admin endpoints require is_admin=True"""
    from app.models import User
    from app.config import settings
    import hashlib
    
    # Create non-admin user
    non_admin_user = User(
        email="regular@test.com",
        name="Regular User",
        api_key_hash=hashlib.sha256(b"regular-key").hexdigest(),
        is_admin=False
    )
    session.add(non_admin_user)
    session.commit()
    
    # Try to access admin endpoint
    resp = test_client.get(
        "/v1/admin/users",
        headers={"X-API-Key": "regular-key"}
    )
    assert resp.status_code == 403, "Non-admin user should not access admin endpoints"


def test_pagination_contract(test_client: TestClient, admin_api_key):
    """Test pagination parameters work correctly"""
    resp = test_client.get(
        "/v1/admin/users?skip=0&limit=10",
        headers=admin_api_key
    )
    assert resp.status_code == 200
    data = resp.json()
    
    # Should return list of users
    assert isinstance(data, list)
    assert len(data) <= 10, "Should respect limit parameter"
