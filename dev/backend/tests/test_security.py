"""
Tests for security input validation module
"""
import pytest
from fastapi import HTTPException
from app.security import InputValidator
from app.models import ChatMessage


class TestInputValidator:
    """Test input validation functionality"""
    
    def test_validate_chat_messages_valid(self):
        """Test valid chat messages pass validation"""
        messages = [
            ChatMessage(role="user", content="Hello, world!"),
            ChatMessage(role="assistant", content="Hi there!")
        ]
        # Should not raise
        InputValidator.validate_chat_messages(messages)
    
    def test_validate_chat_messages_invalid_role(self):
        """Test invalid role raises HTTPException"""
        messages = [ChatMessage(role="hacker", content="test")]
        with pytest.raises(HTTPException, match="invalid role"):
            InputValidator.validate_chat_messages(messages)
    
    def test_validate_chat_messages_empty_content(self):
        """Test empty content raises HTTPException"""
        messages = [ChatMessage(role="user", content="")]
        with pytest.raises(HTTPException, match="role and content required"):
            InputValidator.validate_chat_messages(messages)
    
    def test_validate_chat_messages_too_long(self):
        """Test message exceeding max length raises HTTPException"""
        long_message = "a" * (InputValidator.MAX_MESSAGE_LENGTH + 1)
        messages = [ChatMessage(role="user", content=long_message)]
        with pytest.raises(HTTPException, match="content exceeds"):
            InputValidator.validate_chat_messages(messages)
    
    def test_validate_chat_messages_too_many(self):
        """Test too many messages raises HTTPException"""
        messages = [
            ChatMessage(role="user", content="test")
            for _ in range(InputValidator.MAX_MESSAGES_PER_REQUEST + 1)
        ]
        with pytest.raises(HTTPException, match="Too many messages"):
            InputValidator.validate_chat_messages(messages)
    
    def test_validate_chat_messages_suspicious_script_tag(self):
        """Test suspicious script tag logs warning but doesn't raise"""
        messages = [ChatMessage(role="user", content="<script>alert('xss')</script>")]
        # Should log warning but not raise (allows legitimate use cases)
        InputValidator.validate_chat_messages(messages)
    
    def test_validate_chat_messages_suspicious_sql_injection(self):
        """Test SQL injection pattern logs warning but doesn't raise"""
        messages = [ChatMessage(role="user", content="'; DROP TABLE users; --")]
        # Should log warning but not raise (allows legitimate use cases)
        InputValidator.validate_chat_messages(messages)
    
    def test_validate_credit_amount_valid(self):
        """Test valid credit amounts pass validation"""
        # Should not raise
        InputValidator.validate_credit_amount(100.0)
        InputValidator.validate_credit_amount(500.50)
        InputValidator.validate_credit_amount(1.23)
    
    def test_validate_credit_amount_negative(self):
        """Test negative amount raises HTTPException"""
        with pytest.raises(HTTPException, match="Amount must be positive"):
            InputValidator.validate_credit_amount(-10.0)
    
    def test_validate_credit_amount_zero(self):
        """Test zero amount raises HTTPException"""
        with pytest.raises(HTTPException, match="Amount must be positive"):
            InputValidator.validate_credit_amount(0)
    
    def test_validate_credit_amount_too_large(self):
        """Test excessive amount raises HTTPException"""
        with pytest.raises(HTTPException, match="Amount exceeds maximum"):
            InputValidator.validate_credit_amount(1_000_001)
    
    def test_validate_credit_amount_too_many_decimals(self):
        """Test too many decimal places raises HTTPException"""
        with pytest.raises(HTTPException, match="Amount cannot have more than 2 decimal places"):
            InputValidator.validate_credit_amount(10.123)
