"""Security utilities for input validation and sanitization"""

import re
from typing import List
from fastapi import HTTPException

from .models import ChatMessage


class InputValidator:
    """Validate and sanitize user inputs to prevent injection attacks"""
    
    # Patterns that could indicate prompt injection attempts
    SUSPICIOUS_PATTERNS = [
        r'ignore\s+(previous|all)\s+instructions',
        r'system\s*:\s*you\s+are\s+now',
        r'<\s*script[^>]*>',
        r'javascript\s*:',
        r'\b(union|select|insert|update|delete|drop)\s+',
        r'<\s*iframe',
        r'on(load|error|click)\s*=',
    ]
    
    MAX_MESSAGE_LENGTH = 50000  # ~12k tokens for GPT-4
    MAX_MESSAGES_PER_REQUEST = 100
    
    @classmethod
    def validate_chat_messages(cls, messages: List[ChatMessage]) -> None:
        """
        Validate chat messages for security issues.
        
        Raises:
            HTTPException: If validation fails
        """
        if not messages:
            raise HTTPException(400, "Messages list cannot be empty")
        
        if len(messages) > cls.MAX_MESSAGES_PER_REQUEST:
            raise HTTPException(
                400,
                f"Too many messages. Maximum: {cls.MAX_MESSAGES_PER_REQUEST}"
            )
        
        for idx, msg in enumerate(messages):
            # Validate message structure
            if not msg.role or not msg.content:
                raise HTTPException(400, f"Message {idx}: role and content required")
            
            # Validate role
            if msg.role not in ['system', 'user', 'assistant']:
                raise HTTPException(400, f"Message {idx}: invalid role '{msg.role}'")
            
            # Validate content length
            if len(msg.content) > cls.MAX_MESSAGE_LENGTH:
                raise HTTPException(
                    400,
                    f"Message {idx}: content exceeds {cls.MAX_MESSAGE_LENGTH} characters"
                )
            
            # Check for suspicious patterns (warning only, don't block)
            for pattern in cls.SUSPICIOUS_PATTERNS:
                if re.search(pattern, msg.content, re.IGNORECASE):
                    # Log suspicious content but allow request
                    # (could be legitimate use case)
                    from .logging_config import get_logger
                    logger = get_logger(__name__)
                    logger.warning(
                        f"Suspicious pattern detected in message",
                        extra_data={
                            "pattern": pattern,
                            "message_index": idx,
                            "role": msg.role
                        }
                    )
    
    @classmethod
    def validate_credit_amount(cls, amount: float, max_amount: float = 1_000_000) -> None:
        """Validate credit transfer amounts"""
        if amount <= 0:
            raise HTTPException(400, "Amount must be positive")
        
        if amount > max_amount:
            raise HTTPException(400, f"Amount exceeds maximum ({max_amount})")
        
        # Check for unusual precision (potential manipulation)
        if len(str(amount).split('.')[-1]) > 2:
            raise HTTPException(400, "Amount cannot have more than 2 decimal places")
