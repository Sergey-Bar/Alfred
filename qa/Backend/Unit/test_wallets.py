"""
Wallet API Unit Tests (T231)

Tests for the wallet management system focusing on:
- CRUD operations
- Balance management
- Atomic deductions with hard limit enforcement
- Edge cases (exact limits, decimal precision, validation)

Note: These tests use the test_client fixture from conftest.py.
"""

import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient


class TestWalletCRUD:
    """Test wallet create, read, update, delete flows."""

    def test_create_wallet(self, test_client: TestClient):
        """Create a wallet with all required fields."""
        response = test_client.post(
            "/v1/wallets",
            json={
                "name": "Engineering Budget",
                "wallet_type": "team",
                "hard_limit": 5000.00,
                "soft_limit_percent": 80.00,
            },
        )
        assert response.status_code == 201, f"Got {response.status_code}: {response.text}"
        data = response.json()
        assert data["name"] == "Engineering Budget"
        assert data["wallet_type"] == "team"
        assert float(data["hard_limit"]) == 5000.00
        assert data["status"] == "active"
        assert float(data["balance_used"]) == 0
        assert "id" in data

    def test_list_wallets(self, test_client: TestClient):
        """List wallets returns created wallets."""
        # Create two wallets
        test_client.post("/v1/wallets", json={"name": "WalletA", "hard_limit": 1000.00})
        test_client.post("/v1/wallets", json={"name": "WalletB", "hard_limit": 2000.00})
        
        response = test_client.get("/v1/wallets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        names = [w["name"] for w in data]
        assert "WalletA" in names
        assert "WalletB" in names

    def test_get_wallet(self, test_client: TestClient):
        """Get single wallet by ID."""
        create_resp = test_client.post(
            "/v1/wallets",
            json={"name": "GetMe", "hard_limit": 3000.00},
        )
        wallet_id = create_resp.json()["id"]
        
        response = test_client.get(f"/v1/wallets/{wallet_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "GetMe"

    def test_get_wallet_not_found(self, test_client: TestClient):
        """Get non-existent wallet returns 404."""
        fake_id = str(uuid.uuid4())
        response = test_client.get(f"/v1/wallets/{fake_id}")
        assert response.status_code == 404

    def test_update_wallet(self, test_client: TestClient):
        """Update wallet fields."""
        create_resp = test_client.post(
            "/v1/wallets",
            json={"name": "OldName", "hard_limit": 1000.00},
        )
        wallet_id = create_resp.json()["id"]
        
        response = test_client.patch(
            f"/v1/wallets/{wallet_id}",
            json={"name": "NewName", "hard_limit": 5000.00},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "NewName"
        assert float(data["hard_limit"]) == 5000.00

    def test_delete_wallet_soft_delete(self, test_client: TestClient):
        """Delete wallet sets status to closed (soft delete)."""
        create_resp = test_client.post(
            "/v1/wallets",
            json={"name": "ToDelete"},
        )
        wallet_id = create_resp.json()["id"]
        
        response = test_client.delete(f"/v1/wallets/{wallet_id}")
        assert response.status_code == 204
        
        # Verify soft-deleted (status=closed)
        get_resp = test_client.get(f"/v1/wallets/{wallet_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "closed"


class TestWalletBalance:
    """Test balance endpoint and calculations."""

    def test_get_balance_fresh_wallet(self, test_client: TestClient):
        """Fresh wallet has full balance available."""
        create_resp = test_client.post(
            "/v1/wallets",
            json={"name": "BalanceTest", "hard_limit": 10000.00},
        )
        wallet_id = create_resp.json()["id"]
        
        response = test_client.get(f"/v1/wallets/{wallet_id}/balance")
        assert response.status_code == 200
        data = response.json()
        assert float(data["hard_limit"]) == 10000.00
        assert float(data["balance_used"]) == 0
        assert float(data["balance_available"]) == 10000.00
        assert data["soft_limit_reached"] is False
        assert data["hard_limit_reached"] is False


class TestWalletDeduction:
    """Test atomic deduction (T052/T053)."""

    def _create_wallet(self, test_client, hard_limit=10000.00):
        """Helper to create a test wallet."""
        resp = test_client.post(
            "/v1/wallets",
            json={"name": f"DeductTest-{uuid.uuid4().hex[:8]}", "hard_limit": hard_limit},
        )
        assert resp.status_code == 201
        return resp.json()["id"]

    def test_deduct_success(self, test_client: TestClient):
        """Successful deduction reduces balance."""
        wallet_id = self._create_wallet(test_client)
        
        response = test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={
                "amount": 50.00,
                "request_id": f"req-{uuid.uuid4().hex[:8]}",
                "model": "gpt-4o",
                "provider": "openai",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deducted"
        
        # Verify balance updated
        balance_resp = test_client.get(f"/v1/wallets/{wallet_id}/balance")
        balance = balance_resp.json()
        assert float(balance["balance_used"]) == 50.00
        assert float(balance["balance_available"]) == 9950.00

    def test_deduct_hard_limit_exceeded(self, test_client: TestClient):
        """Deduction exceeding hard limit returns 402."""
        wallet_id = self._create_wallet(test_client, hard_limit=100.00)
        
        response = test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 150.00, "request_id": f"req-{uuid.uuid4().hex[:8]}"},
        )
        assert response.status_code == 402

    def test_deduct_not_found(self, test_client: TestClient):
        """Deduction on non-existent wallet returns 404."""
        fake_id = str(uuid.uuid4())
        response = test_client.post(
            f"/v1/wallets/{fake_id}/deduct",
            json={"amount": 10.00, "request_id": f"req-{uuid.uuid4().hex[:8]}"},
        )
        assert response.status_code == 404


class TestWalletEdgeCases:
    """Edge case tests for wallet operations (T231)."""

    def _create_wallet(self, test_client, hard_limit=1000.00, soft_limit_percent=80.0):
        """Helper to create a test wallet."""
        resp = test_client.post(
            "/v1/wallets",
            json={
                "name": f"EdgeCase-{uuid.uuid4().hex[:8]}",
                "hard_limit": hard_limit,
                "soft_limit_percent": soft_limit_percent,
            },
        )
        assert resp.status_code == 201
        return resp.json()["id"]

    def test_deduct_exact_hard_limit(self, test_client: TestClient):
        """Deducting exactly the hard limit should succeed."""
        wallet_id = self._create_wallet(test_client, hard_limit=100.00)
        
        response = test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 100.00, "request_id": f"req-{uuid.uuid4().hex[:8]}"},
        )
        assert response.status_code == 200
        
        # Verify balance is now at hard limit
        balance = test_client.get(f"/v1/wallets/{wallet_id}/balance").json()
        assert float(balance["balance_used"]) == 100.00
        assert float(balance["balance_available"]) == 0.00
        assert balance["hard_limit_reached"] is True

    def test_deduct_one_penny_over_hard_limit(self, test_client: TestClient):
        """Deducting 1 cent over hard limit should fail."""
        wallet_id = self._create_wallet(test_client, hard_limit=100.00)
        
        response = test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 100.01, "request_id": f"req-{uuid.uuid4().hex[:8]}"},
        )
        assert response.status_code == 402

    def test_soft_limit_warning(self, test_client: TestClient):
        """Hitting soft limit should set warning flag but allow deduction."""
        wallet_id = self._create_wallet(
            test_client, hard_limit=100.00, soft_limit_percent=80.0
        )
        
        # Deduct 85% - should trigger soft limit warning
        response = test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 85.00, "request_id": f"req-{uuid.uuid4().hex[:8]}"},
        )
        assert response.status_code == 200
        
        balance = test_client.get(f"/v1/wallets/{wallet_id}/balance").json()
        assert balance["soft_limit_reached"] is True
        assert balance["hard_limit_reached"] is False

    def test_multiple_small_deductions_to_limit(self, test_client: TestClient):
        """Multiple small deductions should correctly aggregate."""
        wallet_id = self._create_wallet(test_client, hard_limit=100.00)
        
        # Deduct 10 times, 10 each
        for i in range(10):
            resp = test_client.post(
                f"/v1/wallets/{wallet_id}/deduct",
                json={"amount": 10.00, "request_id": f"req-multi-{i}-{uuid.uuid4().hex[:8]}"},
            )
            assert resp.status_code == 200
        
        # Verify total
        balance = test_client.get(f"/v1/wallets/{wallet_id}/balance").json()
        assert float(balance["balance_used"]) == 100.00
        
        # Next deduction should fail
        resp = test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 0.01, "request_id": f"req-overflow-{uuid.uuid4().hex[:8]}"},
        )
        assert resp.status_code == 402

    def test_zero_amount_deduction_rejected(self, test_client: TestClient):
        """Zero amount deduction should be rejected with 422."""
        wallet_id = self._create_wallet(test_client)
        
        response = test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 0.00, "request_id": f"req-{uuid.uuid4().hex[:8]}"},
        )
        assert response.status_code == 422

    def test_negative_amount_deduction_rejected(self, test_client: TestClient):
        """Negative amount deduction should be rejected with 422."""
        wallet_id = self._create_wallet(test_client)
        
        response = test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": -50.00, "request_id": f"req-{uuid.uuid4().hex[:8]}"},
        )
        assert response.status_code == 422

    def test_decimal_precision_maintained(self, test_client: TestClient):
        """Decimal precision should be maintained across operations."""
        wallet_id = self._create_wallet(test_client, hard_limit=100.00)
        
        # Deduct with specific decimal values
        test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 33.33, "request_id": f"req-d1-{uuid.uuid4().hex[:8]}"},
        )
        test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 33.33, "request_id": f"req-d2-{uuid.uuid4().hex[:8]}"},
        )
        test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 33.34, "request_id": f"req-d3-{uuid.uuid4().hex[:8]}"},
        )
        
        # Total should be exactly 100.00
        balance = test_client.get(f"/v1/wallets/{wallet_id}/balance").json()
        assert float(balance["balance_used"]) == 100.00

    def test_create_wallet_invalid_soft_limit_percent(self, test_client: TestClient):
        """Soft limit percent > 100 should be rejected."""
        response = test_client.post(
            "/v1/wallets",
            json={
                "name": "InvalidSoftLimit",
                "hard_limit": 1000.00,
                "soft_limit_percent": 150.00,
            },
        )
        assert response.status_code == 422

    def test_create_wallet_negative_hard_limit(self, test_client: TestClient):
        """Negative hard limit should be rejected."""
        response = test_client.post(
            "/v1/wallets",
            json={
                "name": "NegativeLimit",
                "hard_limit": -1000.00,
            },
        )
        assert response.status_code == 422

    def test_wallet_with_zero_hard_limit(self, test_client: TestClient):
        """Wallet with zero hard limit should block all deductions."""
        resp = test_client.post(
            "/v1/wallets",
            json={"name": "ZeroLimit", "hard_limit": 0.00},
        )
        # Zero limit might be allowed for informational wallets
        if resp.status_code == 201:
            wallet_id = resp.json()["id"]
            deduct_resp = test_client.post(
                f"/v1/wallets/{wallet_id}/deduct",
                json={"amount": 0.01, "request_id": f"req-{uuid.uuid4().hex[:8]}"},
            )
            assert deduct_resp.status_code == 402


class TestWalletRefund:
    """Test refund operations."""

    def _create_and_deduct(self, test_client, amount=100.00):
        """Helper to create wallet and make initial deduction."""
        create_resp = test_client.post(
            "/v1/wallets",
            json={"name": f"RefundTest-{uuid.uuid4().hex[:8]}", "hard_limit": 10000.00},
        )
        wallet_id = create_resp.json()["id"]
        
        test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": amount, "request_id": f"req-to-refund-{uuid.uuid4().hex[:8]}"},
        )
        return wallet_id

    def test_refund_success(self, test_client: TestClient):
        """Successful refund restores balance."""
        wallet_id = self._create_and_deduct(test_client, amount=100.00)
        
        response = test_client.post(
            f"/v1/wallets/{wallet_id}/refund",
            json={
                "amount": 50.00,
                "original_transaction_id": f"tx-{uuid.uuid4().hex[:8]}",
                "idempotency_key": f"rfnd-{uuid.uuid4().hex[:8]}",
            },
        )
        assert response.status_code == 200
        
        # Balance should be 100 - 50 = 50 used
        balance = test_client.get(f"/v1/wallets/{wallet_id}/balance").json()
        assert float(balance["balance_used"]) == 50.00


class TestWalletTopUp:
    """Test top-up operations."""

    def test_topup_success(self, test_client: TestClient):
        """Top-up should restore available credits."""
        # Create wallet and deduct some credits
        create_resp = test_client.post(
            "/v1/wallets",
            json={"name": f"TopUpTest-{uuid.uuid4().hex[:8]}", "hard_limit": 1000.00},
        )
        wallet_id = create_resp.json()["id"]
        
        # Deduct to use some credits
        test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 500.00, "request_id": f"req-{uuid.uuid4().hex[:8]}"},
        )
        
        # Top up
        response = test_client.post(
            f"/v1/wallets/{wallet_id}/topup",
            json={"amount": 200.00, "description": "Monthly credit injection"},
        )
        assert response.status_code == 200
        
        # balance_used should be 500 - 200 = 300
        balance = test_client.get(f"/v1/wallets/{wallet_id}/balance").json()
        assert float(balance["balance_used"]) == 300.00


class TestWalletTransactions:
    """Test transaction history."""

    def test_list_transactions(self, test_client: TestClient):
        """List transactions shows deduction history."""
        create_resp = test_client.post(
            "/v1/wallets",
            json={"name": f"TXTest-{uuid.uuid4().hex[:8]}", "hard_limit": 10000.00},
        )
        wallet_id = create_resp.json()["id"]
        
        # Generate some transactions
        test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 10.00, "request_id": f"tx-1-{uuid.uuid4().hex[:8]}"},
        )
        test_client.post(
            f"/v1/wallets/{wallet_id}/deduct",
            json={"amount": 20.00, "request_id": f"tx-2-{uuid.uuid4().hex[:8]}"},
        )
        
        response = test_client.get(f"/v1/wallets/{wallet_id}/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
