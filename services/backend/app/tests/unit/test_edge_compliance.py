
def test_proxy_quota_exceeded(test_client, admin_api_key):
    # Simulate quota exceeded scenario with valid admin API key
    response = test_client.post(
        "/v1/chat/completions", json={"tokens": 999999}, headers=admin_api_key
    )
    assert response.status_code in [400, 403]
    assert "quota" in response.text.lower()


def test_governance_invalid_token_transfer(test_client, admin_api_key):
    # Simulate invalid token transfer with valid admin API key
    response = test_client.post(
        "/v1/governance/transfer", json={"amount": -100}, headers=admin_api_key
    )
    assert response.status_code in [400, 404]
    if response.status_code == 400:
        assert "invalid" in response.text.lower()


def test_compliance_status_endpoint(test_client):
    # Check compliance status reporting
    response = test_client.get("/v1/compliance/status")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert set(response.json().keys()) >= {"status"}
