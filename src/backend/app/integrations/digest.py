"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Daily spend digest cron (T078). Aggregates wallet
             spend from the past 24h, formats a summary, and
             pushes it through the NotificationManager. Runs
             as an async background task in the FastAPI lifespan.
Root Cause:  Sprint task T078 — Daily spend digest.
Context:     Requires DB access for wallet/transaction data
             and NotificationManager for multi-channel delivery.
Suitability: L2 — SQL aggregation + notification wiring.
──────────────────────────────────────────────────────────────

Alfred Daily Spend Digest
Scheduled cron job that sends a daily cost summary to all configured channels.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select, func, col

from ..database import engine
from ..models import Wallet, WalletStatus, WalletTransaction, WalletTransactionType
from ..integrations.base import EventType, NotificationEvent
from ..integrations.manager import get_notification_manager

logger = logging.getLogger(__name__)

# Default digest schedule: 09:00 UTC
DIGEST_HOUR_UTC = 9
DIGEST_MINUTE_UTC = 0

# Check interval: every 10 minutes
CHECK_INTERVAL_SECONDS = 600


async def daily_digest_loop(
    hour_utc: int = DIGEST_HOUR_UTC,
    minute_utc: int = DIGEST_MINUTE_UTC,
) -> None:
    """
    Async loop that fires the daily digest at a configurable UTC time.

    Runs indefinitely. Designed to be launched via asyncio.create_task()
    in the FastAPI lifespan.
    """
    logger.info(f"daily_digest: started, scheduled at {hour_utc:02d}:{minute_utc:02d} UTC")
    last_digest_date: Optional[str] = None  # YYYY-MM-DD of last successful digest

    while True:
        try:
            now = datetime.now(timezone.utc)
            today_str = now.strftime("%Y-%m-%d")

            # Only fire once per day, after the target time
            if (
                now.hour >= hour_utc
                and (now.hour > hour_utc or now.minute >= minute_utc)
                and last_digest_date != today_str
            ):
                logger.info("daily_digest: generating digest")
                try:
                    await _generate_and_send_digest()
                    last_digest_date = today_str
                    logger.info("daily_digest: sent successfully")
                except Exception as e:
                    logger.error(f"daily_digest: generation failed: {e}")

        except asyncio.CancelledError:
            logger.info("daily_digest: cancelled, shutting down")
            return
        except Exception as e:
            logger.error(f"daily_digest: loop error: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


async def _generate_and_send_digest() -> None:
    """Aggregate spend data and send the digest notification."""
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)

    summary = _aggregate_spend(since, now)
    if not summary:
        logger.info("daily_digest: no spend data for the past 24h, skipping")
        return

    # Build the notification event
    event = _build_digest_event(summary, since, now)

    # Send via NotificationManager
    manager = get_notification_manager()
    results = await manager.emit(event)
    successes = sum(1 for r in results.values() if r.success)
    failures = sum(1 for r in results.values() if not r.success)
    logger.info(
        f"daily_digest: delivered to {successes} providers, "
        f"{failures} failed"
    )


def _aggregate_spend(
    since: datetime, until: datetime
) -> Optional[Dict[str, Any]]:
    """
    Query the database for wallet spend in the given window.

    Returns a summary dict or None if no data.
    """
    with Session(engine) as session:
        # Total deductions in the window
        deductions = session.exec(
            select(
                func.count(WalletTransaction.id).label("tx_count"),
                func.coalesce(func.sum(WalletTransaction.amount), 0).label("total_amount"),
            ).where(
                WalletTransaction.transaction_type == WalletTransactionType.DEDUCTION,
                WalletTransaction.created_at >= since,
                WalletTransaction.created_at < until,
            )
        ).first()

        # Active wallets count + total balance
        wallets = session.exec(
            select(
                func.count(Wallet.id).label("wallet_count"),
                func.coalesce(func.sum(Wallet.balance_used), 0).label("total_used"),
                func.coalesce(func.sum(Wallet.hard_limit), 0).label("total_limit"),
            ).where(
                Wallet.status == WalletStatus.ACTIVE,
            )
        ).first()

        # Top 5 wallets by spend in the window
        top_spenders_query = (
            select(
                WalletTransaction.wallet_id,
                func.sum(WalletTransaction.amount).label("spend"),
            )
            .where(
                WalletTransaction.transaction_type == WalletTransactionType.DEDUCTION,
                WalletTransaction.created_at >= since,
                WalletTransaction.created_at < until,
            )
            .group_by(WalletTransaction.wallet_id)
            .order_by(func.sum(WalletTransaction.amount).desc())
            .limit(5)
        )
        top_spenders = session.exec(top_spenders_query).all()

        # Resolve wallet names for top spenders
        top_spender_details = []
        for wallet_id, spend in top_spenders:
            wallet = session.get(Wallet, wallet_id)
            wallet_name = wallet.name if wallet else f"Wallet {wallet_id}"
            top_spender_details.append({"name": wallet_name, "spend": float(spend)})

        tx_count = deductions[0] if deductions else 0
        total_spend = float(deductions[1]) if deductions else 0.0

        if tx_count == 0:
            return None

        wallet_count = wallets[0] if wallets else 0
        total_used = float(wallets[1]) if wallets else 0.0
        total_limit = float(wallets[2]) if wallets else 0.0
        utilization_pct = (total_used / total_limit * 100) if total_limit > 0 else 0

        return {
            "period_start": since.isoformat(),
            "period_end": until.isoformat(),
            "total_transactions": tx_count,
            "total_spend": total_spend,
            "active_wallets": wallet_count,
            "total_balance_used": total_used,
            "total_balance_limit": total_limit,
            "utilization_pct": round(utilization_pct, 1),
            "top_spenders": top_spender_details,
        }


def _build_digest_event(
    summary: Dict[str, Any],
    since: datetime,
    until: datetime,
) -> NotificationEvent:
    """Build a NotificationEvent from the aggregated summary."""
    top_list = ""
    for i, spender in enumerate(summary.get("top_spenders", []), 1):
        top_list += f"\n  {i}. {spender['name']}: ${spender['spend']:,.2f}"

    message = (
        f"📊 **Daily AI Spend Digest** — "
        f"{since.strftime('%b %d')} to {until.strftime('%b %d, %Y')}\n\n"
        f"💰 Total Spend: ${summary['total_spend']:,.2f} "
        f"across {summary['total_transactions']} transactions\n"
        f"🏦 Active Wallets: {summary['active_wallets']}\n"
        f"📈 Overall Utilization: {summary['utilization_pct']}%\n"
        f"💳 Total Used: ${summary['total_balance_used']:,.2f} / "
        f"${summary['total_balance_limit']:,.2f}\n\n"
        f"🏆 Top Spenders (24h):{top_list}"
    )

    severity = "info"
    if summary["utilization_pct"] >= 90:
        severity = "warning"
    if summary["utilization_pct"] >= 100:
        severity = "error"

    return NotificationEvent(
        event_type=EventType.QUOTA_WARNING,  # Closest built-in type
        title="Daily AI Spend Digest",
        message=message,
        data=summary,
        severity=severity,
    )
