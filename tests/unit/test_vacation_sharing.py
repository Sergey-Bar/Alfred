# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Relocates vacation sharing unit tests to top-level tests/unit/ for reliable pytest discovery.
# Why: Ensures all unit tests are collected and run in CI and local environments.
# Root Cause: Pytest was not discovering tests in src/backend/app/tests/unit/ due to project structure.
# Context: This file is a direct copy of the previously maintained vacation sharing tests.
# Model Suitability: For test relocation and structure, GPT-4.1 is sufficient.

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.logic import AuthManager, QuotaManager
from app.models import ProjectPriority, TeamMemberLink, User, UserStatus


class TestVacationSharing:
    """Tests for vacation quota sharing functionality."""

    def test_vacation_share_available_when_member_on_vacation(self, session, test_user, test_team):
        # Add test_user to team
        link = TeamMemberLink(team_id=test_team.id, user_id=test_user.id)
        session.add(link)

        # Create another user who is on vacation
        _, api_key_hash = AuthManager.generate_api_key()
        vacation_user = User(
            email="vacation@example.com",
            name="Vacation User",
            api_key_hash=api_key_hash,
            personal_quota=Decimal("1000.00"),
            used_tokens=Decimal("0.00"),
            status=UserStatus.ON_VACATION,
            vacation_start=datetime.now(timezone.utc) - timedelta(days=1),
            vacation_end=datetime.now(timezone.utc) + timedelta(days=7),
        )
        session.add(vacation_user)
        session.commit()

        # Add vacation user to same team
        link2 = TeamMemberLink(team_id=test_team.id, user_id=vacation_user.id)
        session.add(link2)
        session.commit()

        # Exhaust test_user's personal quota
        test_user.used_tokens = test_user.personal_quota
        session.add(test_user)
        session.commit()

        manager = QuotaManager(session)

        # Should be able to use vacation share
        result = manager.check_quota(
            user=test_user, estimated_cost=Decimal("50.00"), priority=ProjectPriority.NORMAL
        )

        assert result.allowed is True
        assert result.source == "vacation_share"
        assert "vacation" in result.message.lower()

    def test_no_vacation_share_when_no_members_on_vacation(self, session, test_user, test_team):
        # Add test_user to team
        link = TeamMemberLink(team_id=test_team.id, user_id=test_user.id)
        session.add(link)
        session.commit()

        # Exhaust test_user's personal quota
        test_user.used_tokens = test_user.personal_quota
        session.add(test_user)
        session.commit()

        manager = QuotaManager(session)

        # Should not be allowed (no vacation members)
        result = manager.check_quota(
            user=test_user, estimated_cost=Decimal("50.00"), priority=ProjectPriority.NORMAL
        )

        assert result.allowed is False
        assert result.requires_approval is True

    def test_vacation_share_respects_percentage_limit(self, session, test_user, test_team):
        from app.logic import AuthManager

        # Set team vacation share to 5%
        test_team.vacation_share_percentage = Decimal("5.00")
        test_team.common_pool = Decimal("1000.00")  # 5% = 50 credits max
        session.add(test_team)

        # Add test_user to team
        link = TeamMemberLink(team_id=test_team.id, user_id=test_user.id)
        session.add(link)

        # Create vacation user
        _, api_key_hash = AuthManager.generate_api_key()
        vacation_user = User(
            email="vacation2@example.com",
            name="Vacation User 2",
            api_key_hash=api_key_hash,
            personal_quota=Decimal("1000.00"),
            used_tokens=Decimal("0.00"),
            status=UserStatus.ON_VACATION,
        )
        session.add(vacation_user)
        session.commit()

        link2 = TeamMemberLink(team_id=test_team.id, user_id=vacation_user.id)
        session.add(link2)
        session.commit()

        # Exhaust test_user's personal quota
        test_user.used_tokens = test_user.personal_quota
        session.add(test_user)
        session.commit()

        manager = QuotaManager(session)

        # Request within limit should succeed
        result = manager.check_quota(
            user=test_user, estimated_cost=Decimal("40.00"), priority=ProjectPriority.NORMAL
        )
        assert result.allowed is True

        # Request exceeding limit should fail
        result = manager.check_quota(
            user=test_user, estimated_cost=Decimal("100.00"), priority=ProjectPriority.NORMAL
        )
        assert result.allowed is False


class TestQuotaDeduction:
    """Tests for quota deduction functionality."""

    def test_deduct_personal_quota(self, session, test_user):
        initial_used = test_user.used_tokens
        manager = QuotaManager(session)

        manager.deduct_quota(user=test_user, cost=Decimal("50.00"), source="personal")

        session.refresh(test_user)
        assert test_user.used_tokens == initial_used + Decimal("50.00")
        assert test_user.last_request_at is not None

    def test_deduct_team_pool(self, session, test_user, test_team):
        # Add user to team
        link = TeamMemberLink(team_id=test_team.id, user_id=test_user.id)
        session.add(link)
        session.commit()

        initial_used = test_team.used_pool
        manager = QuotaManager(session)

        manager.deduct_quota(
            user=test_user, cost=Decimal("100.00"), source="team_pool", team=test_team
        )

        session.refresh(test_team)
        assert test_team.used_pool == initial_used + Decimal("100.00")

    def test_add_quota(self, session, test_user):
        initial_quota = test_user.personal_quota
        manager = QuotaManager(session)

        manager.add_quota(test_user, Decimal("500.00"))

        session.refresh(test_user)
        assert test_user.personal_quota == initial_quota + Decimal("500.00")


class TestPriorityBypass:
    """Tests for priority bypass functionality."""

    def test_critical_priority_uses_team_pool(self, session, test_user, test_team):
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
            user=test_user, estimated_cost=Decimal("100.00"), priority=ProjectPriority.CRITICAL
        )

        assert result.allowed is True
        assert result.source == "priority_bypass"
        assert "critical" in result.message.lower() or "bypass" in result.message.lower()

    def test_normal_priority_cannot_bypass(self, session, test_user, test_team):
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
            user=test_user, estimated_cost=Decimal("100.00"), priority=ProjectPriority.NORMAL
        )

        # Should fail without team members on vacation
        assert result.allowed is False
        assert result.requires_approval is True

    def test_high_priority_treated_as_normal(self, session, test_user, test_team):
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
            user=test_user, estimated_cost=Decimal("100.00"), priority=ProjectPriority.HIGH
        )

        # HIGH is not CRITICAL, so should not bypass
        assert result.allowed is False

    # Added test cases for critical priority bypass logic to ensure team liquidity is utilized effectively.
    def test_critical_priority_uses_team_pool_effectively(self, session, test_user, test_team):
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
            user=test_user, estimated_cost=Decimal("100.00"), priority=ProjectPriority.CRITICAL
        )

        assert result.allowed is True
        assert result.source == "priority_bypass"
        assert "critical" in result.message.lower() or "bypass" in result.message.lower()


# Added test for vacation liquidity sharing logic
def test_allocate_vacation_liquidity(session, test_user, test_team):
    """Test vacation liquidity sharing logic."""
    from app.logic import allocate_vacation_liquidity
    from app.models import TeamMemberLink, User, UserStatus

    # Create vacation user (ensure required fields like api_key_hash are present)
    _, api_key_hash = AuthManager.generate_api_key()
    vacation_user = User(
        email="vacation@example.com",
        name="Vacation User",
        api_key_hash=api_key_hash,
        personal_quota=Decimal("1000.00"),
        used_tokens=Decimal("0.00"),
        status=UserStatus.ON_VACATION,
    )
    session.add(vacation_user)
    session.commit()

    # Link vacation user to team
    link = TeamMemberLink(team_id=test_team.id, user_id=vacation_user.id)
    session.add(link)
    session.commit()

    # Test allocation
    result = allocate_vacation_liquidity(session, test_user.id, test_team.id, Decimal("500.00"))
    assert result is True
    assert vacation_user.used_tokens == Decimal("500.00")
