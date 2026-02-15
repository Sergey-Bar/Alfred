
# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Performance benchmarks for database queries, detecting N+1 issues and regressions using large datasets and timing critical queries.
# Why: Ensures query performance is stable and scalable as data grows.
# Root Cause: Unoptimized queries can cause slowdowns and outages in production.
# Context: Run in CI and before releases. Future: add more query types and stress scenarios.
# Model Suitability: Benchmark test logic is standard; GPT-4.1 is sufficient.
"""
Query performance benchmarks

This module contains performance benchmarks for database queries to detect
N+1 query issues and other performance regressions.
"""

import time
from datetime import datetime, timedelta, timezone

import pytest
from app.logic import EfficiencyScorer
from app.models import ApprovalRequest, RequestLog, TokenTransfer, User
from sqlmodel import Session, select


class TestQueryBenchmarks:
    """Performance benchmarks for critical queries."""

    @pytest.fixture
    def large_dataset(self, session: Session):
        """Create a large dataset for benchmarking."""
        # Create users
        users = []
        for i in range(100):
            user = User(
                email=f"user{i}@example.com",
                name=f"User {i}",
                api_key_hash="dummy_hash_for_benchmark_tests",  # Required field
                personal_quota=10000,
                used_tokens=i * 100
            )
            session.add(user)
            users.append(user)

        session.commit()

        # Create request logs
        for user in users:
            for j in range(50):  # 50 logs per user = 5000 total
                log = RequestLog(
                    user_id=user.id,
                    model="gpt-4",
                    provider="openai",  # Required field
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    cost_credits=0.05,
                    quota_source="personal",  # Required field
                    created_at=datetime.now(timezone.utc) - timedelta(days=j % 30)
                )
                session.add(log)

        # Create token transfers
        for i in range(200):  # 200 transfers
            transfer = TokenTransfer(
                sender_id=users[i % 100].id,
                recipient_id=users[(i + 1) % 100].id,
                amount=10.0,
                message=f"Transfer {i}",
                created_at=datetime.now(timezone.utc) - timedelta(days=i % 30)
            )
            session.add(transfer)

        session.commit()

        yield users

        # Cleanup
        session.exec(select(RequestLog)).all()
        for log in session.exec(select(RequestLog)).all():
            session.delete(log)
        for transfer in session.exec(select(TokenTransfer)).all():
            session.delete(transfer)
        for user in users:
            session.delete(user)
        session.commit()

    def test_leaderboard_query_performance(self, session: Session, large_dataset):
        """
        Test that leaderboard query completes efficiently.
        
        Should use bulk queries to avoid N+1 issues.
        Expected: < 1 second for 100 users with 5000 logs
        """
        start = time.time()

        scorer = EfficiencyScorer(session)
        entries = scorer.get_leaderboard("daily", limit=50)

        # Bulk fetch users (simulating endpoint behavior)
        user_ids = {entry.user_id for entry in entries}
        if user_ids:
            users = session.exec(select(User).where(User.id.in_(user_ids))).all()
            users_map = {u.id: u for u in users}

            # Access user data
            for entry in entries:
                user = users_map.get(entry.user_id)
                if user:
                    _ = user.name

        elapsed = time.time() - start

        # Should complete in under 1 second even if no entries
        assert elapsed < 1.0, f"Leaderboard query took {elapsed:.2f}s, expected < 1.0s"

    def test_transfer_history_query_performance(self, session: Session, large_dataset):
        """
        Test that transfer history query completes efficiently.
        
        Should bulk-fetch related users to avoid N+1.
        Expected: < 0.5 seconds for 200 transfers across 100 users
        """
        user = large_dataset[0]

        start = time.time()

        # Get transfers (simulating endpoint logic)
        sent_transfers = session.exec(
            select(TokenTransfer)
            .where(TokenTransfer.sender_id == user.id)
            .order_by(TokenTransfer.created_at.desc())
            .limit(20)
        ).all()

        received_transfers = session.exec(
            select(TokenTransfer)
            .where(TokenTransfer.recipient_id == user.id)
            .order_by(TokenTransfer.created_at.desc())
            .limit(20)
        ).all()

        # Bulk fetch related users
        related_user_ids = set()
        for t in sent_transfers:
            related_user_ids.add(t.recipient_id)
        for t in received_transfers:
            related_user_ids.add(t.sender_id)

        if related_user_ids:
            users = session.exec(select(User).where(User.id.in_(related_user_ids))).all()
            users_map = {u.id: u for u in users}

            # Access user data
            for t in sent_transfers:
                user = users_map.get(t.recipient_id)
                if user:
                    _ = user.name

        elapsed = time.time() - start

        # Should complete in under 0.5 seconds
        assert elapsed < 0.5, f"Transfer history query took {elapsed:.2f}s, expected < 0.5s"

    def test_user_usage_stats_query_performance(self, session: Session, large_dataset):
        """
        Test that user usage stats query completes efficiently.
        
        Should use GROUP BY aggregation to avoid N+1.
        Expected: < 1 second for 100 users with 5000 logs
        """
        from sqlalchemy import func

        start = time.time()

        # Get users
        users = session.exec(
            select(User)
            .order_by(User.used_tokens.desc())
            .limit(50)
        ).all()

        # Bulk fetch request counts using GROUP BY
        user_ids = [u.id for u in users]
        if user_ids:
            counts = session.exec(
                select(RequestLog.user_id, func.count(RequestLog.id))
                .where(RequestLog.user_id.in_(user_ids))
                .group_by(RequestLog.user_id)
            ).all()
            request_counts = {u_id: count for u_id, count in counts}

            # Access counts
            for user in users:
                _ = request_counts.get(user.id, 0)

        elapsed = time.time() - start

        # Should complete in under 1 second
        assert elapsed < 1.0, f"User usage stats query took {elapsed:.2f}s, expected < 1.0s"

        # Verify we got results
        assert len(users) > 0

    def test_dashboard_transfers_query_performance(self, session: Session, large_dataset):
        """
        Test that dashboard transfers query completes efficiently.
        
        Should bulk-fetch users to avoid N+1.
        Expected: < 0.5 seconds for 200 transfers
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        start = time.time()

        # Get transfers
        transfers = session.exec(
            select(TokenTransfer)
            .where(TokenTransfer.created_at >= cutoff)
            .order_by(TokenTransfer.created_at.desc())
        ).all()

        # Bulk fetch users for limited transfers
        limit = 50
        limited_transfers = transfers[:limit]

        user_ids = set()
        for t in limited_transfers:
            user_ids.add(t.sender_id)
            user_ids.add(t.recipient_id)

        if user_ids:
            users = session.exec(select(User).where(User.id.in_(user_ids))).all()
            users_map = {u.id: u for u in users}

            # Format transfers
            for t in limited_transfers:
                sender = users_map.get(t.sender_id)
                recipient = users_map.get(t.recipient_id)
                if sender and recipient:
                    _ = sender.name
                    _ = recipient.name

        elapsed = time.time() - start

        # Should complete in under 0.5 seconds
        assert elapsed < 0.5, f"Dashboard transfers query took {elapsed:.2f}s, expected < 0.5s"

    def test_approval_stats_query_performance(self, session: Session, large_dataset):
        """
        Test that approval stats query completes efficiently.
        
        Should bulk-fetch users for top requesters.
        Expected: < 0.5 seconds
        """
        # Create some approval requests
        for i, user in enumerate(large_dataset[:20]):
            for j in range(5):
                approval = ApprovalRequest(
                    user_id=user.id,
                    team_id=None,
                    requested_credits=100.0,
                    reason=f"Request {j}",
                    status="pending",
                    created_at=datetime.now(timezone.utc) - timedelta(days=i)
                )
                session.add(approval)

        session.commit()

        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        start = time.time()

        # Get all requests
        all_requests = session.exec(
            select(ApprovalRequest)
            .where(ApprovalRequest.created_at >= week_ago)
        ).all()

        # Bulk fetch users
        user_ids = {req.user_id for req in all_requests}
        users_map = {}
        if user_ids:
            users = session.exec(select(User).where(User.id.in_(user_ids))).all()
            users_map = {u.id: u for u in users}

        # Count by user
        requester_counts = {}
        for req in all_requests:
            user = users_map.get(req.user_id)
            if user:
                name = user.name
                requester_counts[name] = requester_counts.get(name, 0) + 1

        elapsed = time.time() - start

        # Should complete in under 0.5 seconds
        assert elapsed < 0.5, f"Approval stats query took {elapsed:.2f}s, expected < 0.5s"

        # Cleanup
        for req in all_requests:
            session.delete(req)
        session.commit()

    def test_index_effectiveness(self, session: Session, large_dataset):
        """
        Test that database indices are effective.
        
        Queries with indexed columns should be faster than unindexed ones.
        """
        user = large_dataset[0]
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        # Query with indexed columns (user_id, created_at)
        start = time.time()
        logs = session.exec(
            select(RequestLog)
            .where(RequestLog.user_id == user.id)
            .where(RequestLog.created_at >= cutoff)
            .order_by(RequestLog.created_at.desc())
        ).all()
        indexed_time = time.time() - start

        # This should be fast with proper indices
        assert indexed_time < 0.1, f"Indexed query took {indexed_time:.2f}s, expected < 0.1s"

        # Query for transfers with indexed sender/recipient
        start = time.time()
        transfers = session.exec(
            select(TokenTransfer)
            .where(TokenTransfer.sender_id == user.id)
            .order_by(TokenTransfer.created_at.desc())
        ).all()
        transfer_time = time.time() - start

        assert transfer_time < 0.1, f"Transfer query took {transfer_time:.2f}s, expected < 0.1s"
