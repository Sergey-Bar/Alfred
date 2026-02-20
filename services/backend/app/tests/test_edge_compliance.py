from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_proxy_quota_exceeded():
    # Simulate quota exceeded scenario
    response = client.post("/v1/chat/completions", json={"tokens": 999999})
    assert response.status_code in [400, 403]
    assert "quota" in response.text.lower()


def test_governance_invalid_token_transfer():
    # Simulate invalid token transfer
    response = client.post("/v1/governance/transfer", json={"amount": -100})
    assert response.status_code == 400
    assert "invalid" in response.text.lower()


def test_compliance_status_endpoint():
    # Check compliance status reporting
    response = client.get("/compliance/status")
    assert response.status_code == 200
    assert set(response.json().keys()) >= {"gdpr", "soc2", "hipaa"}
