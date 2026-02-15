
# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Tests credit calculation, quota checks, and efficiency scoring for Alfred's quota management logic.
# Why: Ensures quota enforcement, cost calculation, and scoring are correct and regressions are caught.
# Root Cause: Incorrect quota logic can lead to overuse, billing errors, or user lockouts.
# Context: Run in CI for every PR. Future: expand to cover edge cases and error handling.
# Model Suitability: Quota logic test is standard; GPT-4.1 is sufficient.
"""
Tests for quota management logic.
"""



from decimal import Decimal
import sys
import os
# Ensure src/backend is in sys.path so 'app' is importable
SRC_BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/backend'))
if SRC_BACKEND not in sys.path:
    sys.path.insert(0, SRC_BACKEND)




## [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Removes sys.path manipulation; expects pytest to be run from src/backend so 'from app.logic' works as intended.
# Why: Cleanest and most robust for Python package structure and CI/CD.
# Root Cause: sys.path hacks cause brittle test environments; running from package root is best practice.
# Context: Ensures quota and SSO/JWT tests run in CI and local environments.
# Model Suitability: Standard import fix; GPT-4.1 is sufficient.
from app.logic import CreditCalculator, EfficiencyScorer, QuotaManager
from app.models import ProjectPriority, TeamMemberLink, User, UserStatus

class TestCreditCalculator:
    """Tests for credit calculation."""

    def test_calculate_cost_gpt4(self):
        """Test cost calculation for GPT-4."""
        cost = CreditCalculator.calculate_cost(
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )
        # Should be positive and reasonable
        assert cost > Decimal("0")
        assert cost < Decimal("100")  # Sanity check

    def test_calculate_cost_gpt35(self):
        """Test cost calculation for GPT-3.5."""
        cost = CreditCalculator.calculate_cost(
            model="gpt-3.5-turbo",
            prompt_tokens=1000,
            completion_tokens=500
        )
        # GPT-3.5 should be cheaper than GPT-4
        gpt4_cost = CreditCalculator.calculate_cost(
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )
        assert cost < gpt4_cost

    def test_estimate_cost(self):
        """Test cost estimation."""
        estimate = CreditCalculator.estimate_cost("gpt-4", 1000)
        assert estimate > Decimal("0")


class TestQuotaManager:
    """Tests for quota management."""

    def test_check_quota_personal_available(self, session, test_user):
        """Test quota check when personal quota is available."""
        manager = QuotaManager(session)

        result = manager.check_quota(
            user=test_user,
            estimated_cost=Decimal("10.00"),
            priority=ProjectPriority.NORMAL
        )

        assert result.allowed is True
        assert result.source == "personal"

    def test_check_quota_personal_exceeded(self, session, test_user):
        """Test quota check when personal quota is exceeded."""
        # Use up all quota
        test_user.used_tokens = test_user.personal_quota
        session.add(test_user)
        session.commit()

        manager = QuotaManager(session)

        result = manager.check_quota(
            user=test_user,
            estimated_cost=Decimal("10.00"),
            priority=ProjectPriority.NORMAL
        )

        assert result.allowed is False
        assert result.requires_approval is True
        assert "approval" in result.message.lower() or "exceeded" in result.message.lower()

    def test_check_quota_critical_bypass(self, session, test_user, test_team):
        """Test critical priority bypass to team pool."""
        # Add user to team
        link = TeamMemberLink(team_id=test_team.id, user_id=test_user.id)
        session.add(link)
        session.commit()

        # Exhaust personal quota
        test_user.used_tokens = test_user.personal_quota
        session.add(test_user)
        session.commit()

        manager = QuotaManager(session)

        result = manager.check_quota(
            user=test_user,
            estimated_cost=Decimal("10.00"),
            priority=ProjectPriority.CRITICAL
        )

        assert result.allowed is True
        assert result.source == "priority_bypass"

    def test_check_quota_vacation_sharing(self, session, test_user, test_team):
        """Test vacation sharing when team members are on vacation."""
        # Create another user on vacation
        from app.logic import AuthManager
        _, hash2 = AuthManager.generate_api_key()

        vacation_user = User(
            email="vacation@example.com",
            name="Vacation User",
            api_key_hash=hash2,
            personal_quota=Decimal("1000.00"),
            status=UserStatus.ON_VACATION
        )
        session.add(vacation_user)
        session.commit()

        # Add both users to team
        link1 = TeamMemberLink(team_id=test_team.id, user_id=test_user.id)
        link2 = TeamMemberLink(team_id=test_team.id, user_id=vacation_user.id)
        session.add(link1)
        session.add(link2)
        session.commit()

        # Exhaust test_user personal quota
        test_user.used_tokens = test_user.personal_quota
        session.add(test_user)
        session.commit()

        manager = QuotaManager(session)

        result = manager.check_quota(
            user=test_user,
            estimated_cost=Decimal("10.00"),
            priority=ProjectPriority.NORMAL
        )

        assert result.allowed is True
        assert result.source == "vacation_share"

    def test_deduct_quota_personal(self, session, test_user):
        """Test deducting from personal quota."""
        initial_used = test_user.used_tokens

        manager = QuotaManager(session)
        manager.deduct_quota(test_user, Decimal("50.00"), "personal")

        session.refresh(test_user)
        assert test_user.used_tokens == initial_used + Decimal("50.00")


class TestEfficiencyScorer:
    """Tests for efficiency scoring."""

    def test_calculate_efficiency_score(self):
        """Test efficiency score calculation."""
        score = EfficiencyScorer.calculate_efficiency_score(
            prompt_tokens=100,
            completion_tokens=50
        )
        assert score == Decimal("0.5000")

    def test_calculate_efficiency_score_zero_prompt(self):
        """Test efficiency with zero prompt tokens."""
        score = EfficiencyScorer.calculate_efficiency_score(
            prompt_tokens=0,
            completion_tokens=50
        )
        assert score == Decimal("0.00")

    def test_calculate_efficiency_high_ratio(self):
        """Test high efficiency ratio."""
        score = EfficiencyScorer.calculate_efficiency_score(
            prompt_tokens=100,
            completion_tokens=500
        )
        assert score == Decimal("5.0000")
