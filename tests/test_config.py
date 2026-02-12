"""
Tests for configuration and settings.
"""

import pytest
import os
from unittest.mock import patch


class TestSettings:
    """Tests for Pydantic Settings configuration."""
    
    def test_default_settings(self):
        """Test default settings values."""
        # Clear cache to get fresh settings
        from app.config import get_settings
        get_settings.cache_clear()
        
        settings = get_settings()
        
        assert settings.app_name == "Alfred"
        assert settings.debug is False
        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_requests == 100
        assert settings.default_personal_quota == 1000.0
    
    def test_settings_from_env(self):
        """Test settings loaded from environment variables."""
        from app.config import get_settings
        get_settings.cache_clear()
        
        with patch.dict(os.environ, {
            "DEBUG": "true",
            "RATE_LIMIT_REQUESTS": "50",
            "LOG_LEVEL": "DEBUG"
        }):
            get_settings.cache_clear()
            settings = get_settings()
            
            assert settings.debug is True
            assert settings.rate_limit_requests == 50
            assert settings.log_level == "DEBUG"
        
        get_settings.cache_clear()
    
    def test_log_level_validation(self):
        """Test log level validation."""
        from pydantic import ValidationError
        from app.config import Settings
        
        # Valid level
        settings = Settings(log_level="DEBUG")
        assert settings.log_level == "DEBUG"
        
        # Invalid level should raise
        with pytest.raises(ValidationError):
            Settings(log_level="INVALID_LEVEL")
    
    def test_environment_validation(self):
        """Test environment validation."""
        from pydantic import ValidationError
        from app.config import Settings
        
        # Valid environments
        for env in ["development", "staging", "production", "test"]:
            settings = Settings(environment=env)
            assert settings.environment == env
        
        # Invalid environment should raise
        with pytest.raises(ValidationError):
            Settings(environment="invalid_env")
    
    def test_is_production_property(self):
        """Test is_production property."""
        from app.config import Settings
        
        settings = Settings(environment="production")
        assert settings.is_production is True
        assert settings.is_development is False
        
        settings = Settings(environment="development")
        assert settings.is_production is False
        assert settings.is_development is True
    
    def test_is_sqlite_property(self):
        """Test is_sqlite property."""
        from app.config import Settings
        
        settings = Settings(database_url="sqlite:///./test.db")
        assert settings.is_sqlite is True
        
        settings = Settings(database_url="postgresql://user:pass@localhost/db")
        assert settings.is_sqlite is False
    
    def test_rate_limit_string(self):
        """Test rate limit string generation."""
        from app.config import Settings
        
        settings = Settings(rate_limit_requests=100, rate_limit_window_seconds=60)
        assert settings.rate_limit_string == "100/60seconds"


class TestLogging:
    """Tests for logging configuration."""
    
    def test_json_formatter(self):
        """Test JSON log formatter."""
        from app.logging_config import JSONFormatter
        import logging
        import json
        
        formatter = JSONFormatter(mask_pii=True)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data["message"] == "Test message"
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert "timestamp" in data
    
    def test_pii_masking(self):
        """Test PII masking in logs."""
        from app.logging_config import JSONFormatter
        import json
        import logging
        
        formatter = JSONFormatter(mask_pii=True)
        
        # Test masking in extra_data
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None
        )
        record.extra_data = {"email": "user@example.com", "api_key": "secret_key_123"}
        
        output = formatter.format(record)
        data = json.loads(output)
        
        # PII should be masked
        assert "user@example.com" not in str(data)
        assert "secret_key_123" not in str(data)
    
    def test_get_logger(self):
        """Test getting a logger instance."""
        from app.logging_config import get_logger
        
        logger = get_logger("test.module")
        assert logger.name == "test.module"
    
    def test_request_context_vars(self):
        """Test request context variables."""
        from app.logging_config import request_id_var, user_id_var
        
        # Test setting and getting
        request_id_var.set("test-request-123")
        user_id_var.set("test-user-456")
        
        assert request_id_var.get() == "test-request-123"
        assert user_id_var.get() == "test-user-456"
        
        # Clean up
        request_id_var.set(None)
        user_id_var.set(None)


class TestExceptions:
    """Tests for custom exceptions."""
    
    def test_quota_exceeded_exception(self):
        """Test QuotaExceededException."""
        from app.exceptions import QuotaExceededException
        
        exc = QuotaExceededException(
            message="Quota exceeded",
            quota_remaining=100.5,
            approval_instructions={"process": "Submit request"}
        )
        
        assert exc.status_code == 403
        assert exc.code == "quota_exceeded"
        assert exc.details["quota_remaining"] == 100.5
        assert exc.details["approval_process"]["process"] == "Submit request"
    
    def test_authentication_exception(self):
        """Test AuthenticationException."""
        from app.exceptions import AuthenticationException
        
        exc = AuthenticationException("Invalid token")
        
        assert exc.status_code == 401
        assert exc.code == "authentication_required"
        assert exc.message == "Invalid token"
    
    def test_resource_not_found_exception(self):
        """Test ResourceNotFoundException."""
        from app.exceptions import ResourceNotFoundException
        
        exc = ResourceNotFoundException("User", "user-123")
        
        assert exc.status_code == 404
        assert exc.code == "not_found"
        assert "User not found: user-123" in exc.message
        assert exc.details["resource_type"] == "User"
        assert exc.details["resource_id"] == "user-123"
    
    def test_llm_provider_exception(self):
        """Test LLMProviderException."""
        from app.exceptions import LLMProviderException
        
        exc = LLMProviderException(
            provider="openai",
            message="Rate limited",
            original_error="Error: 429"
        )
        
        assert exc.status_code == 502
        assert exc.code == "llm_provider_error"
        assert "openai" in exc.message
        assert exc.details["provider"] == "openai"
        assert exc.details["original_error"] == "Error: 429"
