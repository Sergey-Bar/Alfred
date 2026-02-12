# Contributing to Alfred

We welcome contributions! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Areas for Contribution](#areas-for-contribution)

---

## Code of Conduct

Please be respectful and constructive in all interactions. We're building something great together.

---

## Getting Started

### Prerequisites

| Requirement | Version | Check Command |
|------------|---------|---------------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| Git | Any | `git --version` |

### Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/alfred.git
cd alfred
git remote add upstream https://github.com/your-org/alfred.git
```

---

## Development Setup

### Backend

```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate        # Linux/macOS
.\.venv\Scripts\Activate.ps1     # Windows PowerShell

# Install dependencies
pip install -r requirements/requirements-dev.txt

# Copy environment config
cp backend/config/.env.example .env

# Run migrations
alembic -c backend/config/alembic.ini upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies to backend)
npm run dev

# Build for production
npm run build
```

### Running Everything

```bash
# Terminal 1: Backend
uvicorn app.main:app --reload

# Terminal 2: Frontend (dev mode)
cd frontend && npm run dev
```

---

## Code Style

We enforce consistent code style using automated tools.

### Python

| Tool | Purpose |
|------|---------|
| **Black** | Code formatting |
| **isort** | Import sorting |
| **ruff** | Linting |
| **mypy** | Type checking |

**Format code:**
```bash
black app/ tests/
isort app/ tests/
```

**Lint code:**
```bash
ruff app/ tests/
mypy backend/app/
```

**Run all checks:**
```bash
black . && isort . && ruff . && mypy backend/app/
```

### JavaScript/TypeScript

| Tool | Purpose |
|------|---------|
| **Prettier** | Code formatting |
| **ESLint** | Linting |

**Format and lint:**
```bash
cd frontend
npm run lint
npm run format
```

### Pre-commit Hooks

Install pre-commit hooks to run checks automatically:

```bash
pip install pre-commit
pre-commit install
```

---

## Testing

### Run Tests

```bash
# All tests
pytest backend/tests/ -v

# With coverage
pytest backend/tests/ -v --cov=backend/app --cov-report=html

# Specific test file
pytest backend/tests/test_quota.py -v

# Tests matching pattern
pytest backend/tests/ -v -k "test_vacation"

# Run in parallel
pytest backend/tests/ -v -n auto
```

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── test_api.py          # API endpoint tests
├── test_config.py       # Configuration tests
├── test_integration.py  # Integration tests
├── test_middleware.py   # Middleware tests
├── test_quota.py        # Quota logic tests
└── test_vacation_sharing.py  # Vacation feature tests
```

### Writing Tests

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_quota_calculation():
    from app.logic import QuotaManager
    
    manager = QuotaManager()
    result = manager.calculate_cost(model="gpt-4o", tokens=1000)
    
    assert result == 0.5  # 0.5 credits per 1K tokens
```

### Coverage Requirements

- Minimum coverage: 80%
- New features must include tests
- Bug fixes should include regression tests

---

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/amazing-feature
# or
git checkout -b fix/bug-description
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test additions

### 2. Make Changes

- Write code
- Add tests
- Update documentation

### 3. Commit

```bash
git add .
git commit -m "Add amazing feature

- Implemented X
- Added tests for Y
- Updated docs"
```

**Commit message guidelines:**
- Use present tense ("Add feature" not "Added feature")
- First line: brief summary (50 chars max)
- Body: detailed explanation if needed

### 4. Push

```bash
git push origin feature/amazing-feature
```

### 5. Open Pull Request

1. Go to GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in the template:
   - Description of changes
   - Related issues
   - Testing done
   - Screenshots (for UI changes)

### 6. Review Process

- Maintainers will review your PR
- Address feedback with additional commits
- Once approved, maintainers will merge

### PR Checklist

- [ ] Tests pass locally (`pytest backend/tests/ -v`)
- [ ] Code is formatted (`black . && isort .`)
- [ ] No lint errors (`ruff . && mypy backend/app/`)
- [ ] Documentation updated (if needed)
- [ ] Commit messages are clear

---

## Areas for Contribution

### High Priority

| Area | Description | Difficulty |
|------|-------------|------------|
| 🔐 OAuth2/SAML | SSO integration improvements | Medium |
| 📈 Analytics | More detailed usage dashboards | Medium |
| 🌐 Streaming | SSE support for chat completions | Medium |
| 📦 Caching | Response caching for identical prompts | High |

### Medium Priority

| Area | Description | Difficulty |
|------|-------------|------------|
| 🧪 Testing | Increase test coverage | Low |
| 📚 Documentation | More examples and tutorials | Low |
| 🔌 Integrations | Discord, Email, PagerDuty | Medium |
| 🌍 i18n | Internationalization | Medium |

### Good First Issues

Look for issues labeled `good-first-issue` on GitHub. These are designed for new contributors.

---

## Project Structure

```
alfred/
├── app/                    # Backend (Python/FastAPI)
│   ├── main.py            # FastAPI app and routes
│   ├── models.py          # Database models
│   ├── logic.py           # Business logic
│   ├── config.py          # Configuration
│   ├── middleware.py      # Request middleware
│   ├── exceptions.py      # Error handlers
│   └── integrations/      # Notification providers
├── frontend/              # Frontend (React/Vite)
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── services/      # API services
│   └── package.json
├── tests/                 # Test suite
├── docs/                  # Documentation
├── alembic/               # Database migrations
├── config/                # Configuration files
└── docker/                # Docker files
```

---

## Getting Help

- 📖 **Documentation**: [docs/](.)
- 💬 **Questions**: [GitHub Discussions](https://github.com/your-org/alfred/discussions)
- 🐛 **Bugs**: [GitHub Issues](https://github.com/your-org/alfred/issues)

---

*Thank you for contributing to Alfred!*

