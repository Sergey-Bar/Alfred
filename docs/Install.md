# Alfred Installation Guide

Complete setup instructions for new team members and contributors.

## ⚡ One-Line Install

**Get up and running in seconds:**

### Linux/macOS
```bash
git clone https://github.com/your-org/alfred.git && cd alfred && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cp config/.env.example .env && echo "✅ Ready! Run: uvicorn app.main:app --reload"
```

### Windows (PowerShell)
```powershell
git clone https://github.com/your-org/alfred.git; cd alfred; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; Copy-Item config/.env.example .env; Write-Host "✅ Ready! Run: uvicorn app.main:app --reload"
```

### Windows (CMD)
```cmd
git clone https://github.com/your-org/alfred.git && cd alfred && python -m venv .venv && .venv\Scripts\activate.bat && pip install -r requirements.txt && copy config\.env.example .env && echo Ready! Run: uvicorn app.main:app --reload
```

---

## 📋 Prerequisites

| Requirement | Version | Check Command | Required |
|------------|---------|---------------|----------|
| Python | 3.10+ | `python --version` | ✅ Yes |
| pip | Latest | `pip --version` | ✅ Yes |
| Git | Any | `git --version` | ✅ Yes |
| PostgreSQL | 13+ | `psql --version` | ⚪ Optional |

### Install Python 3.10+

<details>
<summary><b>Ubuntu/Debian</b></summary>

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```
</details>

<details>
<summary><b>macOS (Homebrew)</b></summary>

```bash
brew install python@3.10
```
</details>

<details>
<summary><b>Windows (winget)</b></summary>

```powershell
winget install Python.Python.3.10
```
</details>

<details>
<summary><b>Windows (Chocolatey)</b></summary>

```powershell
choco install python --version=3.10.0
```
</details>

### Install PostgreSQL (Optional - for Production)

<details>
<summary><b>Ubuntu/Debian</b></summary>

```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createuser --interactive
sudo -u postgres createdb alfred
```
</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install postgresql@15
brew services start postgresql@15
createdb alfred
```
</details>

<details>
<summary><b>Windows</b></summary>

```powershell
winget install PostgreSQL.PostgreSQL
# Or download from: https://www.postgresql.org/download/windows/
```
</details>

---

## 🚀 Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/alfred.git
cd alfred
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

| Platform | Command |
|----------|---------|
| Linux/macOS | `source .venv/bin/activate` |
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Windows CMD | `.\.venv\Scripts\activate.bat` |

### 4. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (for contributors)
pip install -r requirements-dev.txt
```

### 5. Configure Environment

```bash
# Copy example configuration
cp config/.env.example .env    # Linux/macOS
# Copy-Item config/.env.example .env  # Windows PowerShell

# Edit .env with your settings
# See Configuration section below
```

### 6. Run Database Migrations

```bash
alembic -c config/alembic.ini upgrade head
```

### 7. Start the Server

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Verify Installation

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "version": "1.0.0"}
```

---

## ⚙️ Configuration

### Minimal Configuration (.env)

```env
# Database
DATABASE_URL=sqlite:///./alfred.db

# At least one LLM provider
OPENAI_API_KEY=sk-your-key-here
```

### Full Configuration Reference

```env
# =============================================================================
# Application Settings
# =============================================================================
APP_NAME=Alfred
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=development  # development, staging, production, test

# =============================================================================
# Server Settings
# =============================================================================
HOST=0.0.0.0
PORT=8000
WORKERS=4  # For production with gunicorn

# =============================================================================
# Database Configuration
# =============================================================================
# SQLite (development)
DATABASE_URL=sqlite:///./alfred.db

# PostgreSQL (production)
# DATABASE_URL=postgresql://user:password@localhost:5432/alfred

DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_ECHO=false

# =============================================================================
# Security Settings
# =============================================================================
API_KEY_PREFIX=tp-
API_KEY_LENGTH=32
CORS_ORIGINS=["*"]  # Restrict in production

# =============================================================================
# Rate Limiting
# =============================================================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_BURST=20

# =============================================================================
# LLM Provider API Keys
# =============================================================================

# Public APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Enterprise Cloud
AZURE_API_KEY=...
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-02-15-preview
AZURE_DEPLOYMENT_NAME=gpt-4o

# AWS Bedrock
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Self-Hosted (vLLM, TGI, Ollama)
VLLM_API_BASE=http://gpu-server:8000/v1
TGI_API_BASE=http://tgi-server:8080
OLLAMA_API_BASE=http://localhost:11434

# =============================================================================
# Quota Settings
# =============================================================================
DEFAULT_PERSONAL_QUOTA=1000.0
DEFAULT_TEAM_POOL=10000.0
VACATION_SHARE_PERCENTAGE=10.0
ALLOW_PRIORITY_BYPASS=true
ALLOW_VACATION_SHARING=true

# =============================================================================
# Logging Configuration
# =============================================================================
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json  # json (production) or text (development)
LOG_REQUESTS=true
LOG_FILE=  # Leave empty for stdout only
MASK_PII_IN_LOGS=true

# =============================================================================
# Privacy Settings
# =============================================================================
FORCE_STRICT_PRIVACY=false
```

### 🏢 Enterprise Configuration

For enterprise deployments, additional configuration is available:

<details>
<summary><b>Identity & SSO (LDAP, Azure AD, Okta)</b></summary>

```env
# Active Directory / LDAP
LDAP_ENABLED=true
LDAP_SERVER=ldap://ad.company.com:389
LDAP_BASE_DN=DC=company,DC=com
LDAP_BIND_DN=CN=alfred-svc,OU=ServiceAccounts,DC=company,DC=com
LDAP_BIND_PASSWORD=your-service-account-password
LDAP_SYNC_INTERVAL_MINUTES=60

# SSO (Azure AD example)
SSO_ENABLED=true
SSO_PROVIDER=azure_ad
SSO_CLIENT_ID=your-client-id
SSO_CLIENT_SECRET=your-client-secret
SSO_ISSUER_URL=https://login.microsoftonline.com/{tenant}/v2.0

# SCIM 2.0 for automated user provisioning
SCIM_ENABLED=true
SCIM_BEARER_TOKEN=your-scim-token
```
</details>

<details>
<summary><b>HR System Integration (RBAC)</b></summary>

```env
# Workday Integration
HRIS_ENABLED=true
HRIS_PROVIDER=workday
HRIS_API_URL=https://wd5-impl-services1.workday.com/ccx/service/
HRIS_API_KEY=your-workday-api-key

# Role-based quotas (auto-assigned based on job level)
RBAC_DEFAULT_QUOTAS={"junior": 50000, "mid": 100000, "senior": 250000}

# Project Management (Jira) for priority bursting
PM_INTEGRATION_ENABLED=true
PM_PROVIDER=jira
PM_API_URL=https://company.atlassian.net
PM_API_TOKEN=your-jira-token
PM_HIGH_PRIORITY_BURST_MULTIPLIER=2.0
```
</details>

<details>
<summary><b>Liquidity Pool & Financial Controls</b></summary>

```env
# Liquidity Pool (unused credits rollover)
LIQUIDITY_POOL_ENABLED=true
ROLLOVER_ENABLED=true
ROLLOVER_PERCENTAGE=50.0
RESERVE_REQUEST_DISCOUNT=20.0
BILLING_CYCLE_DAY=1

# Emergency Overdraft
OVERDRAFT_ENABLED=true
OVERDRAFT_LIMIT_MULTIPLIER=0.1
OVERDRAFT_INTEREST_RATE=1.5
```
</details>

<details>
<summary><b>Security & Guardrails</b></summary>

```env
# Transfer Security
MFA_REQUIRED_THRESHOLD=10000.0
TRANSFER_COOLDOWN_SECONDS=60
MAX_DAILY_TRANSFER_AMOUNT=100000.0

# Output Guardrails (prevent prompt injection abuse)
MAX_OUTPUT_TOKENS_TRANSFERRED=4096
ENABLE_SEMANTIC_SCRUTINY=true
LOOP_DETECTION_THRESHOLD=3

# Anomaly Detection
ANOMALY_DETECTION_ENABLED=true
ANOMALY_ALERT_THRESHOLD=3.0

# Session Security
SESSION_TOKEN_TTL_MINUTES=15

# HashiCorp Vault
VAULT_ENABLED=true
VAULT_ADDR=https://vault.company.com:8200
VAULT_TOKEN=your-vault-token
```
</details>

<details>
<summary><b>Semantic Cache & Cost Optimization</b></summary>

```env
# Semantic Cache (reduce redundant API calls)
SEMANTIC_CACHE_ENABLED=true
SEMANTIC_CACHE_SIMILARITY_THRESHOLD=0.90
SEMANTIC_CACHE_TTL_HOURS=24
CACHE_ACCESS_FEE_CREDITS=0.1

# Version-Locked Pricing (insulate budgets from model changes)
VERSION_LOCKED_PRICING_ENABLED=true
CAPABILITY_PRICING_MAP={"frontier_reasoning": 3.0, "standard_chat": 1.0}

# Predictive Burn-Rate Alerts
BURN_RATE_ALERTS_ENABLED=true
BURN_RATE_WARNING_THRESHOLD=0.8
```
</details>

<details>
<summary><b>Multi-Tenant SaaS Mode</b></summary>

```env
# Multi-Tenant with TEE Isolation
MULTI_TENANT_MODE=true
TEE_PROVIDER=azure_confidential
ENCLAVE_ATTESTATION_ENABLED=true
CLIENT_DATA_ISOLATION=strict
```
</details>

<details>
<summary><b>Analytics & ROI Tracking</b></summary>

```env
# GitHub Integration (engineering ROI)
GITHUB_TOKEN=ghp_your-token
GITHUB_ORG=your-company

# Salesforce Integration (sales ROI)
SALESFORCE_ENABLED=true
SALESFORCE_INSTANCE_URL=https://company.salesforce.com
SALESFORCE_ACCESS_TOKEN=your-sf-token
```
</details>

---

## 🐳 Docker Installation

### Quick Start with Docker

```bash
# Clone repository
git clone https://github.com/your-org/alfred.git
cd alfred

# Copy and configure environment
cp config/.env.example .env
# Edit .env with your API keys

# Start with Docker Compose
cd docker && docker-compose up -d

# Check logs
docker-compose logs -f
```

### Build from Source

```bash
# Build image
docker build -t alfred -f docker/Dockerfile .

# Run container
docker run -d \
  --name alfred \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./data/alfred.db \
  -e OPENAI_API_KEY=sk-your-key \
  -v alfred-data:/app/data \
  alfred
```

---

## 🧪 Development Setup

For contributors and developers:

```bash
# Clone and setup
git clone https://github.com/your-org/alfred.git
cd alfred

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows

# Install all dependencies (including dev tools)
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest tests/ -v

# Start development server
uvicorn app.main:app --reload
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_quota.py -v

# Run tests matching pattern
pytest tests/ -v -k "test_vacation"
```

### Code Quality Tools

```bash
# Format code
black app/ tests/
isort app/ tests/

# Lint
ruff app/ tests/

# Type check
mypy app/

# Run all checks
black . && isort . && ruff . && mypy app/
```

---

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>ModuleNotFoundError: No module named 'xxx'</b></summary>

Make sure your virtual environment is activated:
```bash
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\Activate.ps1  # Windows
```

Then reinstall dependencies:
```bash
pip install -r requirements.txt
```
</details>

<details>
<summary><b>Database connection failed</b></summary>

1. Check your `DATABASE_URL` in `.env`
2. For PostgreSQL, ensure the service is running:
   ```bash
   sudo systemctl status postgresql  # Linux
   brew services list  # macOS
   ```
3. Verify database exists and user has permissions
</details>

<details>
<summary><b>Port 8000 already in use</b></summary>

Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

Or find and kill the process using port 8000:
```bash
# Linux/macOS
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```
</details>

<details>
<summary><b>LLM API errors</b></summary>

1. Verify your API key is correct in `.env`
2. Check your API key has sufficient quota/credits
3. Ensure the model name is correct (e.g., `gpt-4`, not `GPT-4`)
</details>

---

## 📚 Next Steps

After installation:

1. **Create your first user**: See [README.md](../README.md#-usage-guide)
2. **Explore the API**: Visit http://localhost:8000/docs
3. **Configure teams**: Set up team quotas and members
4. **Set up monitoring**: Configure logging and alerts

---

## 🆘 Getting Help

- 📖 **Documentation**: [README.md](../README.md)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-org/alfred/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/your-org/alfred/discussions)
- 👤 **Author**: [Sergey Bar](https://www.linkedin.com/in/sergeybar/)
