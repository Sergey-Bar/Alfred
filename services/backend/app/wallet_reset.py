"""
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L4
Logic:       Monthly wallet reset cron job. Iterates wallets
             configured for auto-reset on the matching day,
             resets balance_used to 0, and writes a RESET
             transaction for audit trail.
Root Cause:  Sprint task T056 — Monthly wallet reset cron.
Context:     Runs as a background task on app startup.
             Uses the existing background worker pattern.
Suitability: L4 — touches financial balances, must be correct.
──────────────────────────────────────────────────────────────
"""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Session, select

from . import database as app_database
from .logging_config import get_logger
from .models import (
    Wallet,
    WalletStatus,
    WalletTransaction,
    WalletTransactionType,
)

logger = get_logger(__name__)

# How often to check for wallets that need resetting (in seconds).
_RESET_CHECK_INTERVAL = 3600  # 1 hour


async def wallet_reset_loop():
    """
    Background loop that checks every hour if any wallets need
    their monthly balance reset.

    A wallet is eligible for reset when:
    - auto_reset is True
    - status is ACTIVE
    - reset_day matches today's day-of-month
    - last_reset_at is either None or in a previous month

    LEDGER SAFETY: Each reset is wrapped in a DB transaction and
    writes an immutable RESET transaction log entry.
    """
    logger.info("Wallet reset cron started (interval=%ds)", _RESET_CHECK_INTERVAL)

    while True:
        try:
            await asyncio.sleep(_RESET_CHECK_INTERVAL)
            _run_reset_cycle()
        except asyncio.CancelledError:
            logger.info("Wallet reset cron stopped (cancelled)")
            break
        except Exception:
            logger.exception("Wallet reset cron error — will retry next cycle")


def _run_reset_cycle():
    """
    Synchronous reset cycle — safe to call from async context via
    run_in_executor or directly (SQLModel sessions are sync).
    """
    now = datetime.now(timezone.utc)
    today = now.day

    with Session(app_database.get_engine()) as session:
        # Find wallets due for reset today.
        stmt = (
            select(Wallet)
            .where(Wallet.auto_reset == True)  # noqa: E712
            .where(Wallet.status == WalletStatus.ACTIVE)
            .where(Wallet.reset_day == today)
        )
        wallets = session.exec(stmt).all()

        reset_count = 0
        for wallet in wallets:
            # Skip if already reset this month.
            if wallet.last_reset_at is not None:
                if (
                    wallet.last_reset_at.year == now.year
                    and wallet.last_reset_at.month == now.month
                ):
                    continue

            # Record the reset transaction.
            balance_before = wallet.balance_used
            if balance_before == Decimal("0"):
                # Nothing to reset — skip to avoid noise in audit log.
                wallet.last_reset_at = now
                session.add(wallet)
                continue

            # Reset balance.
            wallet.balance_used = Decimal("0")
            wallet.balance_reserved = Decimal("0")
            wallet.last_reset_at = now
            wallet.updated_at = now

            tx = WalletTransaction(
                wallet_id=wallet.id,
                transaction_type=WalletTransactionType.RESET,
                amount=balance_before,
                balance_before=balance_before,
                balance_after=Decimal("0"),
                description=f"Monthly auto-reset (day {today}, {now.strftime('%Y-%m')})",
            )
            session.add(wallet)
            session.add(tx)
            reset_count += 1

        session.commit()

        if reset_count > 0:
            logger.info(
                "Wallet reset cycle complete: %d wallets reset (day=%d)",
                reset_count,
                today,
            )
