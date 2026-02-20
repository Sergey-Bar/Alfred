"""
Alfred - Enterprise AI Credit Governance Platform
Core Configuration System

[ARCHITECTURAL OVERVIEW]
This module provides a centralized, Type-Safe configuration system built on Pydantic Settings.
It follows the "12-Factor App" methodology by externalizing configuration in environment
variables, with a fallback to local .env files for development convenience.

"""

from functools import lru_cache
from typing import List, Optional
import secrets

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Main Application Settings.

    This class defines all configurable parameters for the Alfred platform.
    Configurations are loaded with the following priority:
    1. Environment Variables (e.g., ALFRED_APP_NAME)
    2. .env file
    3. Default values specified in the Field objects
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Case-insensitive matching allows 'DATABASE_URL' to map to 'database_url'
        case_sensitive=False,
        # Ignore extra environment variables instead of crashing
        extra="ignore",
    )

    # --- Application Metadata ---
    app_name: str = Field(default="Alfred", description="Identifying name for the instance")
    app_version: str = Field(default="1.0.0", description="Semantic version of the application")
    debug: bool = Field(
        default=False,
        description="Enable verbose debugging and stack traces (SECURITY RISK in prod)",
    )
    environment: str = Field(
        default="development",
        description="Runtime environment (development, staging, production, test)",
    )

    # --- Network / Server Configuration ---
    app_url: str = Field(
        default="http://localhost:8000",
        description="Public base URL of the Alfred application (used for OAuth callbacks, Slack redirects, etc.)",
    )
    host: str = Field(default="0.0.0.0", description="The interface to bind the server to")
    port: int = Field(default=8000, ge=1, le=65535, description="TCP port for the application")
    workers: int = Field(
        default=4, ge=1, description="Number of worker processes for production concurrency"
    )

    # --- Database Persistence ---
    database_url: str = Field(
        default="sqlite:///./alfred.db",
        description="SQL Connection string. Use PostgreSQL for high-concurrency production",
    )
    database_pool_size: int = Field(
        default=5, ge=1, description="Size of the SQLAlchemy connection pool"
    )
    database_max_overflow: int = Field(
        default=10, ge=0, description="Connections allowed beyond pool_size under load"
    )
    database_echo: bool = Field(
        default=False, description="Log all SQL statements to stdout (extremely noisy)"
    )

    # --- Security & Auth ---
    api_key_prefix: str = Field(
        default="tp-", description="Consistent prefix for identifying system API keys"
    )
    api_key_length: int = Field(
        default=32, ge=16, le=64, description="Entropy length for generated secrets"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed origins for cross-origin resource sharing. Enforced in middleware",
    )

    # --- Traffic Control (Rate Limiting) ---
    rate_limit_enabled: bool = Field(
        default=True, description="Master switch for the rate-limiting middleware"
    )
    rate_limit_requests: int = Field(
        default=100, ge=1, description="Maximum requests allowed per window"
    )
    rate_limit_window_seconds: int = Field(
        default=60, ge=1, description="Sliding window duration in seconds"
    )
    rate_limit_burst: int = Field(
        default=20, ge=1, description="Allowance for temporary traffic spikes"
    )

    # --- Public LLM Provider Secrets ---
    openai_api_key: Optional[str] = Field(
        default=None, description="OpenAI API authentication token"
    )
    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic API authentication token"
    )
    google_api_key: Optional[str] = Field(
        default=None, description="Google Gemini API authentication token"
    )

    # --- Azure Enterprise LLM Configuration ---
    azure_api_key: Optional[str] = Field(
        default=None, description="Secret key for Azure OpenAI Service"
    )
    azure_api_base: Optional[str] = Field(
        default=None, description="Endpoint URL for Azure instance"
    )
    azure_api_version: Optional[str] = Field(
        default="2024-02-15-preview", description="Azure API schema version"
    )
    azure_deployment_name: Optional[str] = Field(
        default=None, description="Logical name of the model deployment"
    )

    # --- Infrastructure: AWS Bedrock ---
    aws_access_key_id: Optional[str] = Field(default=None, description="IAM Access Key for Bedrock")
    aws_secret_access_key: Optional[str] = Field(
        default=None, description="IAM Secret Key for Bedrock"
    )
    aws_region: Optional[str] = Field(
        default="us-east-1", description="Physical region for computing/inference"
    )

    # --- Infrastructure: Self-Hosted Models ---
    vllm_api_base: Optional[str] = Field(
        default=None, description="Base URL for private vLLM clusters"
    )
    tgi_api_base: Optional[str] = Field(
        default=None, description="Base URL for Text Generation Inference servers"
    )
    ollama_api_base: Optional[str] = Field(
        default=None, description="Base URL for local Ollama instances"
    )

    # --- Governance & Quota Policy ---
    default_personal_quota: float = Field(
        default=1000.0, ge=0, description="Base credit allowance for new users"
    )
    default_team_pool: float = Field(
        default=10000.0, ge=0, description="Initial credit pool for new teams"
    )
    vacation_share_percentage: float = Field(
        default=10.0, ge=0, le=100, description="Max portion of team pool usable for absent members"
    )
    allow_priority_bypass: bool = Field(
        default=True, description="Enables 'Critical' priority to dip into team pools"
    )
    allow_vacation_sharing: bool = Field(
        default=True, description="Enables automatic quota reallocation for vacationing users"
    )

    # --- Observability & Logging ---
    log_level: str = Field(default="INFO", description="Standard Python log level")
    log_format: str = Field(
        default="json", description="Serialization format (JSON for ELK/Datadog, text for local)"
    )
    log_requests: bool = Field(
        default=True, description="Enables detailed HTTP request/response logging"
    )
    log_file: Optional[str] = Field(
        default=None, description="File path for logs (Leave None for container logs to stdout)"
    )

    # --- Privacy Assurance ---
    force_strict_privacy: bool = Field(
        default=False, description="Enforces Privacy-By-Design across the entire org"
    )
    mask_pii_in_logs: bool = Field(
        default=True, description="Redacts emails, keys, and names from application logs"
    )
    log_suspicious_patterns: bool = Field(
        default=True, description="Audit-log detected prompt injection fingerprints"
    )

    # --- Notification Hub: Slack ---
    slack_webhook_url: Optional[str] = Field(
        default=None, description="Standard notification channel"
    )
    slack_alerts_webhook_url: Optional[str] = Field(
        default=None, description="Dedicated channel for infrastructure alerts"
    )
    slack_bot_token: Optional[str] = Field(
        default=None, description="Bot token for bi-directional Slack features"
    )

    # --- Notification Hub: MS Teams ---
    teams_webhook_url: Optional[str] = Field(
        default=None, description="Teams incoming connector URL"
    )
    teams_alerts_webhook_url: Optional[str] = Field(
        default=None, description="Teams alerts connector URL"
    )

    # --- Notification Hub: Telegram ---
    telegram_bot_token: Optional[str] = Field(default=None, description="API token from @BotFather")
    telegram_chat_id: Optional[str] = Field(default=None, description="Default chat/group ID")
    telegram_alerts_chat_id: Optional[str] = Field(
        default=None, description="Critical alerts group ID"
    )

    # --- Notification Hub: WhatsApp ---
    whatsapp_phone_number_id: Optional[str] = Field(
        default=None, description="Meta Business Phone ID"
    )
    whatsapp_access_token: Optional[str] = Field(
        default=None, description="Meta Graph long-lived access token"
    )
    whatsapp_recipient_number: Optional[str] = Field(
        default=None, description="Admin recipient for automated messages"
    )
    whatsapp_alerts_recipient_number: Optional[str] = Field(
        default=None, description="Emergency contact phone number"
    )
    whatsapp_template_name: Optional[str] = Field(
        default=None, description="Pre-approved HSM template identifier"
    )

    # --- Governance: Notification Thresholds ---
    notifications_enabled: bool = Field(
        default=True, description="Master enable for the NotificationManager"
    )
    notify_quota_warning_threshold: int = Field(
        default=80, ge=1, le=99, description="Percentage of quota use to trigger alert"
    )
    notify_on_quota_exceeded: bool = Field(
        default=True, description="Alert user when request is denied due to quota"
    )

    # --- Performance: Redis Layer ---
    redis_enabled: bool = Field(default=False, description="Enable secondary caching layer")
    redis_host: str = Field(default="localhost", description="Redis server address")
    redis_port: int = Field(default=6379, description="Redis server port")
    redis_db: int = Field(default=0, description="Logical database index")
    redis_url: str = "redis://localhost:6379/0"  # Default Redis URL for local development
    notify_on_approval_request: bool = Field(
        default=True, description="Notify admins of pending quota requests"
    )
    notify_on_vacation_change: bool = Field(
        default=True, description="Notify team leads when a member's status changes"
    )

    # --- Enterprise Identity: LDAP ---
    ldap_enabled: bool = Field(default=False, description="Enable Active Directory integration")
    ldap_server: Optional[str] = Field(default=None, description="LDAP URI (ldap:// or ldaps://)")
    ldap_base_dn: Optional[str] = Field(
        default=None, description="Search base for organization unit"
    )
    ldap_bind_dn: Optional[str] = Field(
        default=None, description="Service account for directory searching"
    )
    ldap_bind_password: Optional[str] = Field(default=None, description="Service account secret")
    ldap_user_filter: str = Field(
        default="(objectClass=user)", description="AD Query for human users"
    )
    ldap_group_filter: str = Field(
        default="(objectClass=group)", description="AD Query for logical teams"
    )
    ldap_sync_interval_minutes: int = Field(
        default=60, ge=5, description="Frequency of directory synchronization"
    )

    # --- Enterprise Identity: SSO ---
    sso_enabled: bool = Field(default=False, description="Enable OAuth2/OIDC login flows")
    sso_provider: Optional[str] = Field(
        default=None, description="Identity Provider ID (okta, azure, etc)"
    )
    sso_client_id: Optional[str] = Field(default=None, description="OAuth Client ID")
    sso_client_secret: Optional[str] = Field(default=None, description="OAuth Client Secret")
    sso_issuer_url: Optional[str] = Field(
        default=None, description="Discovery endpoint for the IdP"
    )
    sso_scopes: str = Field(
        default="openid profile email", description="Requested permission scopes"
    )

    # --- Enterprise Identity: automated Provisioning ---
    scim_enabled: bool = Field(
        default=False, description="Enable SCIM 2.0 API for Okta/Azure provisioning"
    )
    scim_bearer_token: Optional[str] = Field(
        default=None, description="Inbound authentication for SCIM requests"
    )

    # --- Human Resources Integration ---
    hris_enabled: bool = Field(
        default=False, description="Connect to HR systems for job-level metadata"
    )
    hris_provider: Optional[str] = Field(
        default=None, description="Platform identifier (workday,hibob,etc)"
    )
    hris_api_url: Optional[str] = Field(default=None, description="API Base for HRIS")
    hris_api_key: Optional[str] = Field(default=None, description="Auth token for HRIS")
    hris_sync_interval_minutes: int = Field(
        default=120, ge=15, description="Frequency of HR metadata refresh"
    )

    # --- Governance: RBAC Quotas ---
    rbac_default_quotas: str = Field(
        default='{"junior": 50000, "mid": 100000, "senior": 250000, "lead": 500000, "executive": 1000000}',
        description="JSON map defining credit limits by organization seniority/role",
    )

    # --- External Tooling Integrations ---
    pm_integration_enabled: bool = Field(
        default=False, description="Connect to Jira/Linear for task correlation"
    )
    pm_provider: Optional[str] = Field(default=None, description="Jira, Linear, Monday, etc")
    pm_api_url: Optional[str] = Field(default=None, description="Tool base URL")
    pm_api_token: Optional[str] = Field(default=None, description="Tool auth token")
    pm_high_priority_burst_multiplier: float = Field(
        default=2.0, ge=1.0, le=10.0, description="Quota allowance bonus for critical tickets"
    )

    # --- Financial Guardrails: Liquidity & Rollover ---
    liquidity_pool_enabled: bool = Field(
        default=True, description="Aggregates unused small-user quotas into an org-wide pool"
    )
    rollover_enabled: bool = Field(
        default=True, description="Unused credits roll to the next billing cycle"
    )
    rollover_percentage: float = Field(
        default=50.0, ge=0, le=100, description="Percent of unused credits to retain"
    )
    reserve_request_discount: float = Field(
        default=20.0, ge=0, le=50, description="Discount multiplier for using reserve pools"
    )
    billing_cycle_day: int = Field(
        default=1, ge=1, le=28, description="Calendar day for monthly resets"
    )

    # --- Operations: Advanced Guardrails ---
    mfa_required_threshold: float = Field(
        default=10000.0, ge=0, description="Transfer amount requiring second-factor confirmation"
    )
    transfer_cooldown_seconds: int = Field(
        default=60, ge=0, description="Minimum time between sequential transfers to same target"
    )
    max_daily_transfer_amount: float = Field(
        default=100000.0, ge=0, description="Daily limit for credit reallocations"
    )

    # --- Safety: Output Controls ---
    max_output_tokens_transferred: int = Field(
        default=4096, ge=100, description="Strict cap on response length for shared credits"
    )
    enable_semantic_scrutiny: bool = Field(
        default=True, description="Heuristic detection of repetitive model output"
    )
    loop_detection_threshold: int = Field(
        default=3, ge=2, description="Tolerant limit for identical token sequences"
    )

    # --- Operations: AI-Driven Anomaly Detection ---
    anomaly_detection_enabled: bool = Field(
        default=True, description="ML-based detection of usage spikes or abnormal patterns"
    )
    anomaly_alert_threshold: float = Field(
        default=3.0, ge=1.5, description="Z-score sensitivity for anomaly flagging"
    )

    # --- Security: Ephemeral Secrets ---
    jwt_secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT token signing (HS256). MUST be set in production."
    )
    jwt_algorithm: str = Field(
        default="HS256", description="JWT signing algorithm"
    )
    jwt_access_token_expire_minutes: int = Field(
        default=60, ge=5, le=1440, description="JWT access token expiration (minutes)"
    )
    session_token_ttl_minutes: int = Field(
        default=15, ge=1, le=60, description="Life-span of JIT access tokens"
    )

    # --- Infrastructure: Enterprise Secrets (Vault) ---
    vault_enabled: bool = Field(
        default=False, description="Use HashiCorp Vault for credential orchestration"
    )
    vault_addr: Optional[str] = Field(default=None, description="Vault cluster address")
    vault_token: Optional[str] = Field(
        default=None, description="Application entry-token for Vault"
    )

    # --- Business ROI Intelligence ---
    github_token: Optional[str] = Field(
        default=None, description="Token for correlating AI use with repo activity"
    )
    github_org: Optional[str] = Field(
        default=None, description="Focus organization for GitHub metrics"
    )
    salesforce_enabled: bool = Field(
        default=False, description="Connect to CRM to track deal impact"
    )
    salesforce_instance_url: Optional[str] = Field(default=None, description="SFDC cluster base")
    salesforce_access_token: Optional[str] = Field(default=None, description="SFDC API credential")

    # --- Intelligence: Semantic Caching ---
    semantic_cache_enabled: bool = Field(
        default=False, description="Reduces provider costs by caching identical queries"
    )
    semantic_cache_similarity_threshold: float = Field(
        default=0.90, ge=0.5, le=1.0, description="Vector similarity needed for cache hit"
    )
    semantic_cache_ttl_hours: int = Field(
        default=24, ge=1, le=168, description="Validity duration for cached responses"
    )
    cache_access_fee_credits: float = Field(
        default=0.1, ge=0, description="Internal billing cost for cache retrieval"
    )

    # --- SaaS Topology: Multi-Tenancy & TEE ---
    multi_tenant_mode: bool = Field(
        default=False, description="Enables shared-infrastructure with logical isolation"
    )
    tee_provider: Optional[str] = Field(
        default=None, description="Trusted Execution Environment platform"
    )
    enclave_attestation_enabled: bool = Field(
        default=False, description="Verify hardware integrity upon startup"
    )
    client_data_isolation: str = Field(
        default="strict", description="Isolation policy (strict prevents cross-request data bleed)"
    )

    # --- Intelligence: capability-Based Pricing ---
    version_locked_pricing_enabled: bool = Field(
        default=True,
        description="Locks cost to capability tier, insulating from model price changes",
    )
    capability_pricing_map: str = Field(
        default='{"frontier_reasoning": 3.0, "standard_chat": 1.0, "fast_inference": 0.5, "embedding": 0.1}',
        description="JSON defining relative weights of model tiers",
    )

    # --- Resilience: Emergency Overdraft ---
    overdraft_enabled: bool = Field(
        default=True, description="Allows users to exceed quota under high-pressure conditions"
    )
    overdraft_limit_multiplier: float = Field(
        default=0.1, ge=0, le=0.5, description="Extra buffer as % of base quota"
    )
    overdraft_interest_rate: float = Field(
        default=1.5, ge=0, le=10, description="Repayment premium for using overdraft"
    )

    # --- Predictive Intelligence ---
    burn_rate_alerts_enabled: bool = Field(
        default=True, description="Forecasts quota depletion based on current velocity"
    )
    burn_rate_warning_threshold: float = Field(
        default=0.8, ge=0.5, le=0.95, description="Threshold for warning based on burn trajectory"
    )

    # --- Advanced Validation Logic ---

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v, info):
        """Guardrail: Forbid wildcard CORS in production deployment."""
        if info.data.get("environment") == "production":
            if "*" in v:
                raise ValueError(
                    "Wildcard CORS origin ('*') is not allowed in production. "
                    "Explicitly list allowed domains for security."
                )
        return v

    @field_validator("database_url")
    @classmethod
    def validate_production_database(cls, v, info):
        """Guardrail: Enforce production-grade storage."""
        if info.data.get("environment") == "production":
            if v.startswith("sqlite"):
                raise ValueError(
                    "SQLite is disallowed for production. "
                    "Migrate to PostgreSQL for data integrity and concurrency."
                )
        return v

    @field_validator("debug")
    @classmethod
    def validate_production_debug(cls, v, info):
        """Guardrail: Prevent accidental leak of system internals."""
        if info.data.get("environment") == "production" and v is True:
            raise ValueError("Debug mode must be strictly disabled in production.")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Sanitize and validate logging severity."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Unknown log level '{v}'. Must be one of {valid_levels}.")
        return v_upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Enforce standard environment naming."""
        valid_envs = ["development", "staging", "production", "test"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"Invalid environment '{v}'. Use {valid_envs}.")
        return v_lower

    # --- Computed Properties ---

    @property
    def is_production(self) -> bool:
        """Utility for runtime production checks."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Utility for development-only features."""
        return self.environment == "development"

    @property
    def is_sqlite(self) -> bool:
        """Automatic driver detection."""
        return "sqlite" in self.database_url.lower()

    @property
    def rate_limit_string(self) -> str:
        """Format for compatibility with SlowAPI/Limiter."""
        return f"{self.rate_limit_requests}/{self.rate_limit_window_seconds}seconds"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
