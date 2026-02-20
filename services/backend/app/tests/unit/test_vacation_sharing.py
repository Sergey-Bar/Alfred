"""
Comprehensive tests for vacation sharing logic.
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../app")))


from app.logic import AuthManager, QuotaManager
from app.models import ProjectPriority, TeamMemberLink, User, UserStatus


class TestVacationSharing:
    """Tests for vacation quota sharing functionality."""

    def test_vacation_share_available_when_member_on_vacation(self, session, test_user, test_team):
        """Test that vacation share is available when a team member is on vacation."""
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
        """Test that vacation share is not available when no members are on vacation."""
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
        """Test that vacation share respects the team's vacation share percentage."""
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
        """Test deducting from personal quota."""
        initial_used = test_user.used_tokens
        manager = QuotaManager(session)

        manager.deduct_quota(user=test_user, cost=Decimal("50.00"), source="personal")

        session.refresh(test_user)
        assert test_user.used_tokens == initial_used + Decimal("50.00")
        assert test_user.last_request_at is not None

    def test_deduct_team_pool(self, session, test_user, test_team):
        """Test deducting from team pool."""
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
        """Test adding quota to a user."""
        initial_quota = test_user.personal_quota
        manager = QuotaManager(session)

        manager.add_quota(test_user, Decimal("500.00"))

        session.refresh(test_user)
        assert test_user.personal_quota == initial_quota + Decimal("500.00")


class TestPriorityBypass:
    """Tests for priority bypass functionality."""

    def test_critical_priority_uses_team_pool(self, session, test_user, test_team):
        """Test that critical priority can bypass to team pool."""
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
        """Test that normal priority cannot bypass to team pool."""
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
        """Test that high (non-critical) priority is treated as normal."""
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
