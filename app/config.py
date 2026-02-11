"""
TokenPool Configuration
Centralized settings management using Pydantic Settings.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic import Field, field_validator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables.
    Example: APP_NAME -> app_name, DATABASE_URL -> database_url
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="TokenPool", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="production", description="Environment (development, staging, production)")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=4, ge=1, description="Number of workers for production")
    
    # Database
    database_url: str = Field(
        default="sqlite:///./tokenpool.db",
        description="Database connection URL (PostgreSQL recommended for production)"
    )
    database_pool_size: int = Field(default=5, ge=1, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, ge=0, description="Max overflow connections")
    database_echo: bool = Field(default=False, description="Echo SQL statements")
    
    # Security
    api_key_prefix: str = Field(default="tp-", description="Prefix for generated API keys")
    api_key_length: int = Field(default=32, ge=16, le=64, description="Length of API keys")
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, ge=1, description="Requests per window")
    rate_limit_window_seconds: int = Field(default=60, ge=1, description="Rate limit window in seconds")
    rate_limit_burst: int = Field(default=20, ge=1, description="Burst allowance")
    
    # LLM Providers
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google AI API key")
    azure_api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    azure_api_base: Optional[str] = Field(default=None, description="Azure OpenAI API base URL")
    
    # Quota Settings
    default_personal_quota: float = Field(default=1000.0, ge=0, description="Default personal quota in credits")
    default_team_pool: float = Field(default=10000.0, ge=0, description="Default team pool in credits")
    vacation_share_percentage: float = Field(default=10.0, ge=0, le=100, description="Max vacation share percentage")
    allow_priority_bypass: bool = Field(default=True, description="Allow critical priority to bypass limits")
    allow_vacation_sharing: bool = Field(default=True, description="Allow vacation quota sharing")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json, text)")
    log_requests: bool = Field(default=True, description="Log API requests")
    log_file: Optional[str] = Field(default=None, description="Log file path (None for stdout)")
    
    # Privacy
    force_strict_privacy: bool = Field(default=False, description="Force strict privacy mode org-wide")
    mask_pii_in_logs: bool = Field(default=True, description="Mask PII in log messages")
    
    # Notifications - Slack
    slack_webhook_url: Optional[str] = Field(default=None, description="Slack incoming webhook URL")
    slack_alerts_webhook_url: Optional[str] = Field(default=None, description="Slack webhook for critical alerts")
    slack_bot_token: Optional[str] = Field(default=None, description="Slack bot token for advanced features")
    
    # Notifications - Microsoft Teams
    teams_webhook_url: Optional[str] = Field(default=None, description="Microsoft Teams incoming webhook URL")
    teams_alerts_webhook_url: Optional[str] = Field(default=None, description="Teams webhook for critical alerts")
    
    # Notifications - Telegram
    telegram_bot_token: Optional[str] = Field(default=None, description="Telegram bot token from @BotFather")
    telegram_chat_id: Optional[str] = Field(default=None, description="Default Telegram chat/group/channel ID")
    telegram_alerts_chat_id: Optional[str] = Field(default=None, description="Telegram chat for critical alerts")
    
    # Notifications - WhatsApp Business
    whatsapp_phone_number_id: Optional[str] = Field(default=None, description="WhatsApp Business Phone Number ID")
    whatsapp_access_token: Optional[str] = Field(default=None, description="Meta Graph API access token")
    whatsapp_recipient_number: Optional[str] = Field(default=None, description="Default recipient phone number")
    whatsapp_alerts_recipient_number: Optional[str] = Field(default=None, description="Recipient for critical alerts")
    whatsapp_template_name: Optional[str] = Field(default=None, description="Pre-approved message template name")
    
    # Notification Settings
    notifications_enabled: bool = Field(default=True, description="Enable/disable notifications globally")
    notify_quota_warning_threshold: int = Field(default=80, ge=1, le=99, description="Quota % to trigger warning")
    notify_on_quota_exceeded: bool = Field(default=True, description="Notify when quota is exceeded")
    notify_on_approval_request: bool = Field(default=True, description="Notify on new approval requests")
    notify_on_vacation_change: bool = Field(default=True, description="Notify when users change vacation status")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_envs = ["development", "staging", "production", "test"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_envs}")
        return v_lower
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return "sqlite" in self.database_url.lower()
    
    @property
    def rate_limit_string(self) -> str:
        """Get rate limit as string for slowapi."""
        return f"{self.rate_limit_requests}/{self.rate_limit_window_seconds}seconds"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    Clear cache with get_settings.cache_clear() if needed.
    """
    return Settings()


# Convenience instance for direct import
settings = get_settings()
