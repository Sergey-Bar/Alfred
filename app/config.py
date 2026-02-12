"""
Alfred Configuration
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
    app_name: str = Field(default="Alfred", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="production", description="Environment (development, staging, production)")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=4, ge=1, description="Number of workers for production")
    
    # Database
    database_url: str = Field(
        default="sqlite:///./alfred.db",
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
    
    # LLM Providers - Public APIs
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google AI API key")
    
    # LLM Providers - Enterprise Cloud
    azure_api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    azure_api_base: Optional[str] = Field(default=None, description="Azure OpenAI API base URL")
    azure_api_version: Optional[str] = Field(default="2024-02-15-preview", description="Azure OpenAI API version")
    azure_deployment_name: Optional[str] = Field(default=None, description="Azure OpenAI deployment name")
    
    # AWS Bedrock
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key for Bedrock")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret key for Bedrock")
    aws_region: Optional[str] = Field(default="us-east-1", description="AWS region for Bedrock")
    
    # Self-Hosted / Open Source (vLLM, TGI)
    vllm_api_base: Optional[str] = Field(default=None, description="vLLM server base URL (e.g., http://localhost:8080/v1)")
    tgi_api_base: Optional[str] = Field(default=None, description="TGI server base URL (e.g., http://localhost:8080)")
    ollama_api_base: Optional[str] = Field(default=None, description="Ollama server base URL (e.g., http://localhost:11434)")
    
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
    
    # --- Enterprise Identity & SSO ---
    
    # Active Directory / LDAP
    ldap_enabled: bool = Field(default=False, description="Enable LDAP/Active Directory user sync")
    ldap_server: Optional[str] = Field(default=None, description="LDAP server URL (e.g., ldap://ad.company.com:389)")
    ldap_base_dn: Optional[str] = Field(default=None, description="LDAP base DN (e.g., DC=company,DC=com)")
    ldap_bind_dn: Optional[str] = Field(default=None, description="LDAP bind DN for service account")
    ldap_bind_password: Optional[str] = Field(default=None, description="LDAP bind password")
    ldap_user_filter: str = Field(default="(objectClass=user)", description="LDAP filter for users")
    ldap_group_filter: str = Field(default="(objectClass=group)", description="LDAP filter for groups (teams)")
    ldap_sync_interval_minutes: int = Field(default=60, ge=5, description="LDAP sync interval in minutes")
    
    # SSO / OAuth2 (Okta, Azure AD, Google Workspace)
    sso_enabled: bool = Field(default=False, description="Enable SSO authentication")
    sso_provider: Optional[str] = Field(default=None, description="SSO provider: okta, azure_ad, google, keycloak")
    sso_client_id: Optional[str] = Field(default=None, description="OAuth2 client ID")
    sso_client_secret: Optional[str] = Field(default=None, description="OAuth2 client secret")
    sso_issuer_url: Optional[str] = Field(default=None, description="SSO issuer URL / tenant")
    sso_scopes: str = Field(default="openid profile email", description="OAuth2 scopes")
    
    # SCIM Provisioning (auto user/team creation)
    scim_enabled: bool = Field(default=False, description="Enable SCIM 2.0 provisioning endpoint")
    scim_bearer_token: Optional[str] = Field(default=None, description="SCIM bearer token for auth")
    
    # --- HR System Integration (RBAC) ---
    
    # HRIS Integration (Workday, SAP SuccessFactors, HiBob, BambooHR)
    hris_enabled: bool = Field(default=False, description="Enable HR system integration")
    hris_provider: Optional[str] = Field(default=None, description="HRIS: workday, sap_sf, hibob, bamboohr, personio")
    hris_api_url: Optional[str] = Field(default=None, description="HRIS API base URL")
    hris_api_key: Optional[str] = Field(default=None, description="HRIS API key or token")
    hris_sync_interval_minutes: int = Field(default=120, ge=15, description="HRIS sync interval")
    
    # Role-Based Quota Allocation
    rbac_default_quotas: str = Field(
        default='{"junior": 50000, "mid": 100000, "senior": 250000, "lead": 500000, "executive": 1000000}',
        description="JSON mapping of job levels to daily token quotas"
    )
    
    # Project Management Integration (Jira, Asana, Linear)
    pm_integration_enabled: bool = Field(default=False, description="Enable project management integration")
    pm_provider: Optional[str] = Field(default=None, description="PM tool: jira, asana, linear, monday")
    pm_api_url: Optional[str] = Field(default=None, description="PM API URL")
    pm_api_token: Optional[str] = Field(default=None, description="PM API token")
    pm_high_priority_burst_multiplier: float = Field(default=2.0, ge=1.0, le=10.0, description="Quota multiplier for high-priority tasks")
    
    # --- Liquidity Pool & Rollover ---
    
    liquidity_pool_enabled: bool = Field(default=True, description="Enable company-wide liquidity pool")
    rollover_enabled: bool = Field(default=True, description="Roll unused credits to reserve at cycle end")
    rollover_percentage: float = Field(default=50.0, ge=0, le=100, description="% of unused credits that roll over")
    reserve_request_discount: float = Field(default=20.0, ge=0, le=50, description="% discount for reserve requests")
    billing_cycle_day: int = Field(default=1, ge=1, le=28, description="Day of month for billing cycle reset")
    
    # --- Security & Guardrails ---
    
    # Transfer Security
    mfa_required_threshold: float = Field(default=10000.0, ge=0, description="Credit threshold requiring MFA for transfers")
    transfer_cooldown_seconds: int = Field(default=60, ge=0, description="Cooldown between transfers to same recipient")
    max_daily_transfer_amount: float = Field(default=100000.0, ge=0, description="Max credits transferable per day")
    
    # Output Guardrails
    max_output_tokens_transferred: int = Field(default=4096, ge=100, description="Max output tokens for transferred credits")
    enable_semantic_scrutiny: bool = Field(default=True, description="Detect repetitive/nonsensical output patterns")
    loop_detection_threshold: int = Field(default=3, ge=2, description="Repetitions before killing stream")
    
    # Anomaly Detection
    anomaly_detection_enabled: bool = Field(default=True, description="AI-driven usage anomaly detection")
    anomaly_alert_threshold: float = Field(default=3.0, ge=1.5, description="Standard deviations for anomaly alert")
    
    # Session Tokens (JIT)
    session_token_ttl_minutes: int = Field(default=15, ge=1, le=60, description="Session token TTL for API access")
    
    # Secrets Management
    vault_enabled: bool = Field(default=False, description="Use HashiCorp Vault for secrets")
    vault_addr: Optional[str] = Field(default=None, description="Vault server address")
    vault_token: Optional[str] = Field(default=None, description="Vault access token")
    
    # --- Analytics Integrations ---
    
    # GitHub (for engineering ROI tracking)
    github_token: Optional[str] = Field(default=None, description="GitHub API token for code correlation")
    github_org: Optional[str] = Field(default=None, description="GitHub organization name")
    
    # Salesforce (for sales ROI tracking)
    salesforce_enabled: bool = Field(default=False, description="Enable Salesforce integration")
    salesforce_instance_url: Optional[str] = Field(default=None, description="Salesforce instance URL")
    salesforce_access_token: Optional[str] = Field(default=None, description="Salesforce access token")
    
    # --- Semantic Cache ---
    
    # Token-Aware Caching (reduces redundant API calls)
    semantic_cache_enabled: bool = Field(default=False, description="Enable semantic caching for redundant queries")
    semantic_cache_similarity_threshold: float = Field(default=0.90, ge=0.5, le=1.0, description="Similarity threshold for cache hit")
    semantic_cache_ttl_hours: int = Field(default=24, ge=1, le=168, description="Cache TTL in hours")
    cache_access_fee_credits: float = Field(default=0.1, ge=0, description="Small fee for cache hits (0 = free)")
    
    # --- Multi-Tenant / SaaS Mode ---
    
    # Isolated Vaulting with TEE
    multi_tenant_mode: bool = Field(default=False, description="Enable multi-tenant SaaS mode")
    tee_provider: Optional[str] = Field(default=None, description="TEE provider: azure_confidential, aws_nitro, gcp_confidential")
    enclave_attestation_enabled: bool = Field(default=False, description="Enable enclave attestation")
    client_data_isolation: str = Field(default="strict", description="Data isolation: strict, standard")
    
    # --- Version-Locked Pricing ---
    
    # Insulate budgets from model version changes
    version_locked_pricing_enabled: bool = Field(default=True, description="Lock pricing to capability class, not raw tokens")
    capability_pricing_map: str = Field(
        default='{"frontier_reasoning": 3.0, "standard_chat": 1.0, "fast_inference": 0.5, "embedding": 0.1}',
        description="JSON mapping of capability classes to credit/1K multipliers"
    )
    
    # --- Emergency Overdraft ---
    
    overdraft_enabled: bool = Field(default=True, description="Allow emergency overdraft for critical work")
    overdraft_limit_multiplier: float = Field(default=0.1, ge=0, le=0.5, description="Overdraft limit as % of quota")
    overdraft_interest_rate: float = Field(default=1.5, ge=0, le=10, description="Interest rate % for overdraft repayment")
    
    # --- Predictive Analytics ---
    
    burn_rate_alerts_enabled: bool = Field(default=True, description="Enable predictive burn-rate alerts")
    burn_rate_warning_threshold: float = Field(default=0.8, ge=0.5, le=0.95, description="Alert when projected depletion before cycle end")

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
