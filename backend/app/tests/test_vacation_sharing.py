# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Tests vacation quota sharing logic, ensuring users can borrow quota from team members on vacation, with correct status and time window handling.
# Why: Prevents quota lockout and enables fair resource sharing during absences.
# Root Cause: Incorrect vacation logic can block users or allow quota abuse.
# Context: Run in CI for every PR. Future: add edge cases for overlapping vacations and error handling.
# Model Suitability: Vacation sharing test logic is standard; GPT-4.1 is sufficient.

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from ..logic import QuotaManager
from ..models import ProjectPriority, TeamMemberLink, User, UserStatus

class TestVacationSharing:
    """Comprehensive tests for vacation sharing logic."""
    # ...existing test code...
