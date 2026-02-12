"""
Alfred Notification Base Classes
Abstract interfaces for notification providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class EventType(str, Enum):
    """Types of notification events."""
    
    # Quota events
    QUOTA_WARNING = "quota_warning"          # User at 80%/90% of quota
    QUOTA_EXCEEDED = "quota_exceeded"        # Quota limit reached
    QUOTA_RESET = "quota_reset"              # Quota was reset/refilled
    
    # Credit reallocation events
    TOKEN_TRANSFER_SENT = "token_transfer_sent"         # User reallocated credits out
    TOKEN_TRANSFER_RECEIVED = "token_transfer_received" # User received credits
    
    # Approval events
    APPROVAL_REQUESTED = "approval_requested"   # New approval request
    APPROVAL_APPROVED = "approval_approved"     # Request approved
    APPROVAL_REJECTED = "approval_rejected"     # Request rejected
    
    # User events
    USER_VACATION_START = "user_vacation_start"   # User went on vacation
    USER_VACATION_END = "user_vacation_end"       # User returned from vacation
    USER_SUSPENDED = "user_suspended"             # User account suspended
    
    # Team events
    TEAM_POOL_WARNING = "team_pool_warning"  # Team pool at threshold
    TEAM_POOL_DEPLETED = "team_pool_depleted"  # Team pool empty
    
    # System events
    SYSTEM_ERROR = "system_error"            # System/provider error
    HIGH_LATENCY = "high_latency"            # API latency above threshold


@dataclass
class NotificationEvent:
    """
    Represents a notification event to be sent to providers.
    
    Attributes:
        event_type: The type of event
        title: Short title/summary
        message: Detailed message
        user_id: User ID related to this event (if applicable)
        user_email: User email for mentions/lookups
        user_name: User display name
        team_id: Team ID related to this event (if applicable)
        team_name: Team name
        data: Additional event-specific data
        severity: Event severity (info, warning, error, critical)
        timestamp: When the event occurred
        event_id: Unique event identifier
    """
    event_type: EventType
    title: str
    message: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "title": self.title,
            "message": self.message,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_name": self.user_name,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "data": self.data,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
        }


class NotificationProvider(ABC):
    """
    Abstract base class for notification providers.
    
    Implement this interface to add support for new notification
    channels like Slack, Teams, Discord, Email, etc.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'slack', 'teams')."""
        pass
    
    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured."""
        pass
    
    @abstractmethod
    async def send(self, event: NotificationEvent) -> bool:
        """
        Send a notification.
        
        Args:
            event: The notification event to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def send_batch(self, events: List[NotificationEvent]) -> Dict[str, bool]:
        """
        Send multiple notifications.
        
        Args:
            events: List of events to send
            
        Returns:
            Dict mapping event_id to success status
        """
        pass
    
    def supports_event(self, event_type: EventType) -> bool:
        """
        Check if this provider supports a given event type.
        Override to filter events per provider.
        
        Args:
            event_type: The type of event
            
        Returns:
            True if the provider handles this event type
        """
        return True
    
    def format_message(self, event: NotificationEvent) -> str:
        """
        Format the notification message.
        Override for provider-specific formatting.
        
        Args:
            event: The notification event
            
        Returns:
            Formatted message string
        """
        return f"[{event.severity.upper()}] {event.title}\n{event.message}"


class NotificationResult:
    """Result of a notification send operation."""
    
    def __init__(
        self,
        provider: str,
        event_id: str,
        success: bool,
        error: Optional[str] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.provider = provider
        self.event_id = event_id
        self.success = success
        self.error = error
        self.response_data = response_data or {}
        self.timestamp = datetime.utcnow()
    
    def __repr__(self) -> str:
        status = "OK" if self.success else f"FAILED: {self.error}"
        return f"NotificationResult({self.provider}, {self.event_id}, {status})"
