
# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Tests FastAPI middleware (rate limiting) for correct enforcement, headers, and blocking logic using TestClient and patching settings.
# Why: Ensures middleware enforces limits and behaves as expected under different configurations.
# Root Cause: Broken middleware can allow abuse or block legitimate users.
# Context: Run in CI for every PR. Future: add tests for logging, error handling, and edge cases.
# Model Suitability: Middleware test logic is standard; GPT-4.1 is sufficient.
"""
Tests for middleware components.
"""

from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestRateLimitMiddleware:
    """Tests for rate limiting middleware."""

    def test_rate_limit_allows_requests_within_limit(self):
        """Test that requests within limit are allowed."""
        from app.middleware import RateLimitMiddleware

        app = FastAPI()
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_window=10,
            window_seconds=60,
            burst=5
        )

        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}

        with patch("app.middleware.settings") as mock_settings:
            mock_settings.rate_limit_enabled = True
            mock_settings.log_requests = False

            client = TestClient(app)

            # First request should succeed
            response = client.get("/test")
            assert response.status_code == 200

            # Check rate limit headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers

    def test_rate_limit_blocks_excess_requests(self):
        """Test that excess requests are blocked."""
        from app.middleware import RateLimitMiddleware

        app = FastAPI()
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_window=3,
            window_seconds=60,
            burst=0  # No burst allowance
        )

        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}

        with patch("app.middleware.settings") as mock_settings:
            mock_settings.rate_limit_enabled = True
            mock_settings.log_requests = False

            client = TestClient(app)

            # Make requests up to limit
            for i in range(3):
                response = client.get("/test")
                assert response.status_code == 200

            # Next request should be rate limited
            response = client.get("/test")
            assert response.status_code == 429
            assert "Retry-After" in response.headers
            assert response.json()["code"] == "rate_limit_exceeded"

    def test_rate_limit_skips_health_endpoint(self):
        """Test that health endpoint bypasses rate limiting."""
        from app.middleware import RateLimitMiddleware

        app = FastAPI()
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_window=1,  # Very low limit
            window_seconds=60,
            burst=0
        )

        @app.get("/health")
        def health():
            return {"status": "healthy"}

        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}

        with patch("app.middleware.settings") as mock_settings:
            mock_settings.rate_limit_enabled = True
            mock_settings.log_requests = False

            client = TestClient(app)

            # Health endpoint should always succeed
            for _ in range(10):
                response = client.get("/health")
                assert response.status_code == 200

    def test_rate_limit_disabled(self):
        """Test that rate limiting can be disabled."""
        from app.middleware import RateLimitMiddleware

        app = FastAPI()
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_window=1,
            window_seconds=60,
            burst=0
        )

        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}

        with patch("app.middleware.settings") as mock_settings:
            mock_settings.rate_limit_enabled = False
            mock_settings.log_requests = False

            client = TestClient(app)

            # All requests should succeed when disabled
            for _ in range(10):
                response = client.get("/test")
                assert response.status_code == 200


class TestRequestContextMiddleware:
    """Tests for request context middleware."""

    def test_adds_request_id_header(self):
        """Test that request ID is added to response."""
        from app.middleware import RequestContextMiddleware

        app = FastAPI()
        app.add_middleware(RequestContextMiddleware)

        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}

        with patch("app.middleware.settings") as mock_settings:
            mock_settings.log_requests = False

            client = TestClient(app)
            response = client.get("/test")

            assert response.status_code == 200
            assert "X-Request-ID" in response.headers
            assert "X-Response-Time" in response.headers

    def test_uses_provided_request_id(self):
        """Test that provided request ID is used."""
        from app.middleware import RequestContextMiddleware

        app = FastAPI()
        app.add_middleware(RequestContextMiddleware)

        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}

        with patch("app.middleware.settings") as mock_settings:
            mock_settings.log_requests = False

            client = TestClient(app)
            custom_id = "custom-request-id-123"
            response = client.get("/test", headers={"X-Request-ID": custom_id})

            assert response.headers["X-Request-ID"] == custom_id


class TestEfficiencyScorer:
    """Tests for efficiency scoring."""

    def test_calculate_efficiency_score(self):
        """Test efficiency score calculation."""
        from decimal import Decimal

        from app.logic import EfficiencyScorer

        # Normal case
        score = EfficiencyScorer.calculate_efficiency_score(
            prompt_tokens=1000,
            completion_tokens=500
        )
        assert score == Decimal("0.5")

        # High efficiency (more output than input)
        score = EfficiencyScorer.calculate_efficiency_score(
            prompt_tokens=100,
            completion_tokens=500
        )
        assert score == Decimal("5.0")

        # Zero prompt tokens
        score = EfficiencyScorer.calculate_efficiency_score(
            prompt_tokens=0,
            completion_tokens=500
        )
        assert score == Decimal("0.00")

    def test_efficiency_score_rounding(self):
        """Test that efficiency score is properly rounded."""
        from decimal import Decimal

        from app.logic import EfficiencyScorer

        score = EfficiencyScorer.calculate_efficiency_score(
            prompt_tokens=3,
            completion_tokens=10
        )
        # Should be rounded to 4 decimal places
        assert score == Decimal("3.3333")
