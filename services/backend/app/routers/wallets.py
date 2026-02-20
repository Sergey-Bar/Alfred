"""
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L4
Logic:       Wallet service REST API implementing CRUD operations,
             atomic balance deduction with SELECT FOR UPDATE,
             hard limit enforcement (HTTP 402), soft limit
             threshold detection, and balance queries.
Root Cause:  Sprint tasks T051-T055 — Wallet Service.
Context:     Financial correctness is critical. All mutations
             must be transactional. Deductions before provider
             calls. Refunds must be idempotent.
Suitability: L4 for financial service — zero-defect requirement.
──────────────────────────────────────────────────────────────
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from io import StringIO
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlmodel import Session, select

from ..database import get_session
from ..models import (
    Wallet,
    WalletStatus,
    WalletTransaction,
    WalletTransactionType,
    WalletType,
)

router = APIRouter(prefix="/v1/wallets", tags=["wallets"])


# --- Request/Response Schemas ---


class WalletCreate(BaseModel):
    """Schema for creating a new wallet."""
    model_config = ConfigDict(strict=True)

    name: str = Field(max_length=255)
    wallet_type: WalletType = WalletType.USER
    owner_user_id: Optional[uuid.UUID] = None
    owner_team_id: Optional[uuid.UUID] = None
    parent_wallet_id: Optional[uuid.UUID] = None
    hard_limit: Decimal = Field(default=Decimal("10000.00"), ge=0)
    soft_limit_percent: Decimal = Field(default=Decimal("80.00"), ge=0, le=100)
    overdraft_enabled: bool = False
    overdraft_percent: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    auto_reset: bool = True
    reset_day: int = Field(default=1, ge=1, le=28)
    currency: str = "credits"
    description: Optional[str] = None


class WalletUpdate(BaseModel):
    """Schema for updating wallet config."""
    model_config = ConfigDict(strict=True)

    name: Optional[str] = None
    hard_limit: Optional[Decimal] = None
    soft_limit_percent: Optional[Decimal] = None
    overdraft_enabled: Optional[bool] = None
    overdraft_percent: Optional[Decimal] = None
    auto_reset: Optional[bool] = None
    reset_day: Optional[int] = None
    status: Optional[WalletStatus] = None
    description: Optional[str] = None


class WalletBalance(BaseModel):
    """Balance response following PRD schema."""
    wallet_id: uuid.UUID
    name: str
    hard_limit: Decimal
    balance_used: Decimal
    balance_reserved: Decimal
    balance_available: Decimal
    utilization_percent: Decimal
    soft_limit_reached: bool
    hard_limit_reached: bool
    currency: str


class DeductRequest(BaseModel):
    """Atomic balance deduction request (T052)."""
    model_config = ConfigDict(strict=True)

    amount: Decimal = Field(gt=0)
    request_id: str
    model: Optional[str] = None
    provider: Optional[str] = None
    description: Optional[str] = None
    idempotency_key: Optional[str] = None


class RefundRequest(BaseModel):
    """Idempotent refund request."""
    model_config = ConfigDict(strict=True)

    amount: Decimal = Field(gt=0)
    original_request_id: str
    idempotency_key: str
    description: Optional[str] = None


class TopUpRequest(BaseModel):
    """Credit injection request."""
    model_config = ConfigDict(strict=True)

    amount: Decimal = Field(gt=0)
    description: Optional[str] = None


class WalletResponse(BaseModel):
    """Full wallet response."""
    id: uuid.UUID
    name: str
    wallet_type: WalletType
    status: WalletStatus
    owner_user_id: Optional[uuid.UUID]
    owner_team_id: Optional[uuid.UUID]
    parent_wallet_id: Optional[uuid.UUID]
    hard_limit: Decimal
    soft_limit_percent: Decimal
    balance_used: Decimal
    balance_reserved: Decimal
    balance_available: Decimal
    utilization_percent: Decimal
    overdraft_enabled: bool
    overdraft_percent: Decimal
    auto_reset: bool
    reset_day: int
    currency: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class TransactionResponse(BaseModel):
    """Wallet transaction response."""
    id: uuid.UUID
    wallet_id: uuid.UUID
    transaction_type: WalletTransactionType
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    request_id: Optional[str]
    model: Optional[str]
    provider: Optional[str]
    description: Optional[str]
    created_at: datetime


# --- Helper Functions ---


def _wallet_to_response(w: Wallet) -> WalletResponse:
    return WalletResponse(
        id=w.id,
        name=w.name,
        wallet_type=w.wallet_type,
        status=w.status,
        owner_user_id=w.owner_user_id,
        owner_team_id=w.owner_team_id,
        parent_wallet_id=w.parent_wallet_id,
        hard_limit=w.hard_limit,
        soft_limit_percent=w.soft_limit_percent,
        balance_used=w.balance_used,
        balance_reserved=w.balance_reserved,
        balance_available=w.balance_available,
        utilization_percent=w.utilization_percent,
        overdraft_enabled=w.overdraft_enabled,
        overdraft_percent=w.overdraft_percent,
        auto_reset=w.auto_reset,
        reset_day=w.reset_day,
        currency=w.currency,
        description=w.description,
        created_at=w.created_at,
        updated_at=w.updated_at,
    )


def _tx_to_response(tx: WalletTransaction) -> TransactionResponse:
    return TransactionResponse(
        id=tx.id,
        wallet_id=tx.wallet_id,
        transaction_type=tx.transaction_type,
        amount=tx.amount,
        balance_before=tx.balance_before,
        balance_after=tx.balance_after,
        request_id=tx.request_id,
        model=tx.model,
        provider=tx.provider,
        description=tx.description,
        created_at=tx.created_at,
    )


def _get_wallet_or_404(session: Session, wallet_id: uuid.UUID) -> Wallet:
    wallet = session.get(Wallet, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail=f"Wallet {wallet_id} not found")
    return wallet


# --- Endpoints ---


@router.post("", response_model=WalletResponse, status_code=201)
def create_wallet(body: WalletCreate, session: Session = Depends(get_session)):
    """Create a new wallet (T051)."""
    wallet = Wallet(
        name=body.name,
        wallet_type=body.wallet_type,
        owner_user_id=body.owner_user_id,
        owner_team_id=body.owner_team_id,
        parent_wallet_id=body.parent_wallet_id,
        hard_limit=body.hard_limit,
        soft_limit_percent=body.soft_limit_percent,
        overdraft_enabled=body.overdraft_enabled,
        overdraft_percent=body.overdraft_percent,
        auto_reset=body.auto_reset,
        reset_day=body.reset_day,
        currency=body.currency,
        description=body.description,
    )
    session.add(wallet)
    session.commit()
    session.refresh(wallet)
    return _wallet_to_response(wallet)


@router.get("", response_model=List[WalletResponse])
def list_wallets(
    wallet_type: Optional[WalletType] = None,
    status: Optional[WalletStatus] = None,
    owner_user_id: Optional[uuid.UUID] = None,
    owner_team_id: Optional[uuid.UUID] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    """List wallets with optional filters (T051)."""
    stmt = select(Wallet)
    if wallet_type:
        stmt = stmt.where(Wallet.wallet_type == wallet_type)
    if status:
        stmt = stmt.where(Wallet.status == status)
    if owner_user_id:
        stmt = stmt.where(Wallet.owner_user_id == owner_user_id)
    if owner_team_id:
        stmt = stmt.where(Wallet.owner_team_id == owner_team_id)
    stmt = stmt.offset(offset).limit(limit)
    wallets = session.exec(stmt).all()
    return [_wallet_to_response(w) for w in wallets]


@router.get("/{wallet_id}", response_model=WalletResponse)
def get_wallet(wallet_id: uuid.UUID, session: Session = Depends(get_session)):
    """Get a single wallet (T051)."""
    wallet = _get_wallet_or_404(session, wallet_id)
    return _wallet_to_response(wallet)


@router.patch("/{wallet_id}", response_model=WalletResponse)
def update_wallet(
    wallet_id: uuid.UUID,
    body: WalletUpdate,
    session: Session = Depends(get_session),
):
    """Update wallet configuration (T051)."""
    wallet = _get_wallet_or_404(session, wallet_id)
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(wallet, key, value)
    wallet.updated_at = datetime.now(timezone.utc)
    session.add(wallet)
    session.commit()
    session.refresh(wallet)
    return _wallet_to_response(wallet)


@router.delete("/{wallet_id}", status_code=204)
def delete_wallet(wallet_id: uuid.UUID, session: Session = Depends(get_session)):
    """Soft-delete a wallet by setting status to CLOSED (T051)."""
    wallet = _get_wallet_or_404(session, wallet_id)
    wallet.status = WalletStatus.CLOSED
    wallet.updated_at = datetime.now(timezone.utc)
    session.add(wallet)
    session.commit()


# --- Balance API (T055) ---


@router.get("/{wallet_id}/balance", response_model=WalletBalance)
def get_balance(wallet_id: uuid.UUID, session: Session = Depends(get_session)):
    """Get wallet balance (T055)."""
    wallet = _get_wallet_or_404(session, wallet_id)
    return WalletBalance(
        wallet_id=wallet.id,
        name=wallet.name,
        hard_limit=wallet.hard_limit,
        balance_used=wallet.balance_used,
        balance_reserved=wallet.balance_reserved,
        balance_available=wallet.balance_available,
        utilization_percent=wallet.utilization_percent,
        soft_limit_reached=wallet.soft_limit_reached,
        hard_limit_reached=wallet.hard_limit_reached,
        currency=wallet.currency,
    )


# --- Atomic Deduction (T052/T053) ---


@router.post("/{wallet_id}/deduct", status_code=200)
def deduct_balance(
    wallet_id: uuid.UUID,
    body: DeductRequest,
    session: Session = Depends(get_session),
):
    """
    Atomic balance deduction using SELECT FOR UPDATE (T052).
    Returns HTTP 402 if hard limit would be exceeded (T053).
    Detects soft limit thresholds at 80%, 90%, 95% (T054).

    LEDGER SAFETY: This is wrapped in a DB transaction.
    Deduction happens BEFORE forwarding to provider.
    """
    # Idempotency check.
    if body.idempotency_key:
        existing = session.exec(
            select(WalletTransaction).where(
                WalletTransaction.idempotency_key == body.idempotency_key
            )
        ).first()
        if existing:
            return {
                "status": "already_processed",
                "transaction_id": str(existing.id),
                "message": "Deduction already processed (idempotent).",
            }

    # Use raw SQL for SELECT FOR UPDATE to lock the row.
    # ROLLBACK: To revert this change:
    # 1. Run: alembic downgrade -1
    # 2. Deploy tag: v<previous-tag>
    # 3. Notify: Sergey Bar + on-call engineer
    result = session.exec(
        text(
            "SELECT id, hard_limit, balance_used, balance_reserved, "
            "overdraft_enabled, overdraft_percent, soft_limit_percent, status "
            "FROM wallets WHERE id = :wid FOR UPDATE"
        ),
        params={"wid": str(wallet_id)},
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail=f"Wallet {wallet_id} not found")

    (
        wid, hard_limit, balance_used, balance_reserved,
        overdraft_enabled, overdraft_percent, soft_limit_percent, status
    ) = result

    if status != WalletStatus.ACTIVE.value:
        raise HTTPException(
            status_code=403, detail=f"Wallet is {status} — cannot deduct."
        )

    # Calculate effective limit (with overdraft if enabled).
    effective_limit = Decimal(str(hard_limit))
    if overdraft_enabled:
        effective_limit += Decimal(str(hard_limit)) * Decimal(str(overdraft_percent)) / Decimal("100")

    current_used = Decimal(str(balance_used))
    current_reserved = Decimal(str(balance_reserved))
    new_used = current_used + body.amount

    # T053: Hard limit enforcement — return HTTP 402.
    if new_used + current_reserved > effective_limit:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "insufficient_balance",
                "code": "hard_limit_exceeded",
                "wallet_id": str(wallet_id),
                "hard_limit": float(hard_limit),
                "balance_used": float(current_used),
                "balance_reserved": float(current_reserved),
                "requested": float(body.amount),
                "available": float(effective_limit - current_used - current_reserved),
            },
        )

    # T057: Check hierarchy limits before deduction.
    wallet_obj = session.get(Wallet, wallet_id)
    if wallet_obj:
        hierarchy_error = _check_hierarchy_limit(session, wallet_obj, body.amount)
        if hierarchy_error:
            raise HTTPException(
                status_code=402,
                detail={"error": "hierarchy_limit", "message": hierarchy_error},
            )

    # Perform atomic deduction.
    session.exec(
        text(
            "UPDATE wallets SET balance_used = :new_used, "
            "updated_at = :now WHERE id = :wid"
        ),
        params={
            "new_used": str(new_used),
            "now": datetime.now(timezone.utc).isoformat(),
            "wid": str(wallet_id),
        },
    )

    # Write transaction log (immutable).
    tx = WalletTransaction(
        wallet_id=wallet_id,
        transaction_type=WalletTransactionType.DEDUCTION,
        amount=body.amount,
        balance_before=current_used,
        balance_after=new_used,
        request_id=body.request_id,
        model=body.model,
        provider=body.provider,
        description=body.description,
        idempotency_key=body.idempotency_key,
    )
    session.add(tx)
    session.commit()

    # T054: Soft limit threshold detection.
    utilization = (new_used / Decimal(str(hard_limit))) * Decimal("100") if Decimal(str(hard_limit)) > 0 else Decimal("100")
    alerts = []
    for threshold in [Decimal("80"), Decimal("90"), Decimal("95")]:
        old_util = (current_used / Decimal(str(hard_limit))) * Decimal("100") if Decimal(str(hard_limit)) > 0 else Decimal("100")
        if old_util < threshold <= utilization:
            alerts.append({
                "type": "soft_limit_warning",
                "threshold": float(threshold),
                "utilization": float(utilization),
                "message": f"Wallet has reached {threshold}% utilization.",
            })

    response = {
        "status": "deducted",
        "transaction_id": str(tx.id),
        "wallet_id": str(wallet_id),
        "amount": float(body.amount),
        "balance_used": float(new_used),
        "balance_available": float(effective_limit - new_used - current_reserved),
    }
    if alerts:
        response["alerts"] = alerts

    return response


# --- Refund (idempotent) ---


@router.post("/{wallet_id}/refund", status_code=200)
def refund_balance(
    wallet_id: uuid.UUID,
    body: RefundRequest,
    session: Session = Depends(get_session),
):
    """
    Idempotent refund on provider error.
    Uses idempotency_key to prevent double-refund.
    """
    # Idempotency check.
    existing = session.exec(
        select(WalletTransaction).where(
            WalletTransaction.idempotency_key == body.idempotency_key
        )
    ).first()
    if existing:
        return {
            "status": "already_processed",
            "transaction_id": str(existing.id),
            "message": "Refund already processed (idempotent).",
        }

    wallet = _get_wallet_or_404(session, wallet_id)

    balance_before = wallet.balance_used
    wallet.balance_used = max(Decimal("0"), wallet.balance_used - body.amount)
    wallet.updated_at = datetime.now(timezone.utc)

    tx = WalletTransaction(
        wallet_id=wallet_id,
        transaction_type=WalletTransactionType.REFUND,
        amount=body.amount,
        balance_before=balance_before,
        balance_after=wallet.balance_used,
        request_id=body.original_request_id,
        idempotency_key=body.idempotency_key,
        description=body.description or f"Refund for request {body.original_request_id}",
    )
    session.add(tx)
    session.add(wallet)
    session.commit()

    return {
        "status": "refunded",
        "transaction_id": str(tx.id),
        "wallet_id": str(wallet_id),
        "amount": float(body.amount),
        "balance_used": float(wallet.balance_used),
    }


# --- Top Up ---


@router.post("/{wallet_id}/topup", status_code=200)
def topup_balance(
    wallet_id: uuid.UUID,
    body: TopUpRequest,
    session: Session = Depends(get_session),
):
    """Add credits to a wallet."""
    wallet = _get_wallet_or_404(session, wallet_id)

    balance_before = wallet.balance_used
    # Top-up reduces the used balance (or increases available).
    wallet.hard_limit += body.amount
    wallet.updated_at = datetime.now(timezone.utc)

    tx = WalletTransaction(
        wallet_id=wallet_id,
        transaction_type=WalletTransactionType.TOPUP,
        amount=body.amount,
        balance_before=balance_before,
        balance_after=wallet.balance_used,
        description=body.description or "Manual top-up",
    )
    session.add(tx)
    session.add(wallet)
    session.commit()

    return {
        "status": "topped_up",
        "transaction_id": str(tx.id),
        "wallet_id": str(wallet_id),
        "new_hard_limit": float(wallet.hard_limit),
        "balance_available": float(wallet.balance_available),
    }


# --- Transaction History ---


@router.get("/{wallet_id}/transactions", response_model=List[TransactionResponse])
def list_transactions(
    wallet_id: uuid.UUID,
    transaction_type: Optional[WalletTransactionType] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    """Get wallet transaction history."""
    _get_wallet_or_404(session, wallet_id)  # Verify wallet exists.
    stmt = select(WalletTransaction).where(
        WalletTransaction.wallet_id == wallet_id
    )
    if transaction_type:
        stmt = stmt.where(WalletTransaction.transaction_type == transaction_type)
    stmt = stmt.order_by(WalletTransaction.created_at.desc()).offset(offset).limit(limit)
    txs = session.exec(stmt).all()
    return [_tx_to_response(tx) for tx in txs]


# --- Wallet Hierarchy (T057) ---


def _check_hierarchy_limit(
    session: Session, wallet: Wallet, additional_amount: Decimal
) -> Optional[str]:
    """
    Recursively check that deducting from this wallet won't violate any
    parent wallet's limits. Returns an error message if violation detected,
    None if OK.

    The rule: a child wallet's total usage (including all sibling children)
    must not exceed the parent's hard limit.
    """
    if not wallet.parent_wallet_id:
        return None  # No parent → no hierarchy constraint.

    parent = session.get(Wallet, wallet.parent_wallet_id)
    if not parent:
        return None  # Orphan wallet — allow.

    # Sum all children's usage under this parent.
    children_stmt = select(Wallet).where(Wallet.parent_wallet_id == parent.id)
    children = session.exec(children_stmt).all()
    total_children_used = sum(
        (c.balance_used + c.balance_reserved for c in children), Decimal("0")
    )
    total_after = total_children_used + additional_amount

    parent_effective = parent.effective_limit
    if total_after > parent_effective:
        return (
            f"Parent wallet '{parent.name}' ({parent.id}) limit exceeded: "
            f"children total {total_after} > parent limit {parent_effective}"
        )

    # Recurse up the hierarchy.
    return _check_hierarchy_limit(session, parent, additional_amount)


@router.get("/{wallet_id}/children", response_model=List[WalletResponse])
def list_children(wallet_id: uuid.UUID, session: Session = Depends(get_session)):
    """List child wallets under a parent (T057)."""
    _get_wallet_or_404(session, wallet_id)
    stmt = select(Wallet).where(Wallet.parent_wallet_id == wallet_id)
    children = session.exec(stmt).all()
    return [_wallet_to_response(c) for c in children]


# --- Reservation System (T059) ---


class ReserveRequest(BaseModel):
    """Pre-flight token cost reservation (two-phase: reserve → settle)."""
    model_config = ConfigDict(strict=True)

    estimated_cost: Decimal = Field(gt=0)
    request_id: str
    model: Optional[str] = None
    provider: Optional[str] = None
    ttl_seconds: int = Field(default=300, ge=30, le=3600)


class SettleRequest(BaseModel):
    """Settle a previously created reservation with actual cost."""
    model_config = ConfigDict(strict=True)

    reservation_id: uuid.UUID
    actual_cost: Decimal = Field(ge=0)


@router.post("/{wallet_id}/reserve", status_code=200)
def reserve_balance(
    wallet_id: uuid.UUID,
    body: ReserveRequest,
    session: Session = Depends(get_session),
):
    """
    Reserve funds before calling the provider (T059).
    The reservation holds balance_reserved, preventing other
    requests from double-spending the same budget.
    """
    wallet = _get_wallet_or_404(session, wallet_id)

    if wallet.status != WalletStatus.ACTIVE:
        raise HTTPException(status_code=403, detail=f"Wallet is {wallet.status.value}")

    # Check available balance includes reserved.
    available = wallet.balance_available
    if body.estimated_cost > available:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "insufficient_balance",
                "code": "reservation_exceeds_available",
                "available": float(available),
                "requested": float(body.estimated_cost),
            },
        )

    # T057: Hierarchy check.
    hierarchy_error = _check_hierarchy_limit(session, wallet, body.estimated_cost)
    if hierarchy_error:
        raise HTTPException(status_code=402, detail={"error": "hierarchy_limit", "message": hierarchy_error})

    # Add to reserved balance.
    wallet.balance_reserved += body.estimated_cost
    wallet.updated_at = datetime.now(timezone.utc)

    tx = WalletTransaction(
        wallet_id=wallet_id,
        transaction_type=WalletTransactionType.RESERVATION,
        amount=body.estimated_cost,
        balance_before=wallet.balance_used,
        balance_after=wallet.balance_used,
        request_id=body.request_id,
        model=body.model,
        provider=body.provider,
        description=f"Reservation (TTL={body.ttl_seconds}s)",
    )
    session.add(wallet)
    session.add(tx)
    session.commit()
    session.refresh(tx)

    return {
        "status": "reserved",
        "reservation_id": str(tx.id),
        "wallet_id": str(wallet_id),
        "estimated_cost": float(body.estimated_cost),
        "balance_reserved": float(wallet.balance_reserved),
        "balance_available": float(wallet.balance_available),
    }


@router.post("/{wallet_id}/settle", status_code=200)
def settle_reservation(
    wallet_id: uuid.UUID,
    body: SettleRequest,
    session: Session = Depends(get_session),
):
    """
    Settle a reservation with the actual cost (T059).
    Moves funds from reserved → used. Refunds excess if actual < estimated.
    """
    wallet = _get_wallet_or_404(session, wallet_id)

    # Find the reservation transaction.
    reservation = session.get(WalletTransaction, body.reservation_id)
    if not reservation or reservation.wallet_id != wallet_id:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.transaction_type != WalletTransactionType.RESERVATION:
        raise HTTPException(status_code=400, detail="Transaction is not a reservation")

    estimated = reservation.amount
    actual = body.actual_cost

    # Release reserved amount and apply actual usage.
    wallet.balance_reserved = max(Decimal("0"), wallet.balance_reserved - estimated)
    balance_before = wallet.balance_used
    wallet.balance_used += actual
    wallet.updated_at = datetime.now(timezone.utc)

    tx = WalletTransaction(
        wallet_id=wallet_id,
        transaction_type=WalletTransactionType.SETTLEMENT,
        amount=actual,
        balance_before=balance_before,
        balance_after=wallet.balance_used,
        request_id=reservation.request_id,
        model=reservation.model,
        provider=reservation.provider,
        description=f"Settlement: estimated={estimated}, actual={actual}",
    )
    session.add(wallet)
    session.add(tx)
    session.commit()

    return {
        "status": "settled",
        "transaction_id": str(tx.id),
        "wallet_id": str(wallet_id),
        "estimated_cost": float(estimated),
        "actual_cost": float(actual),
        "savings": float(estimated - actual),
        "balance_used": float(wallet.balance_used),
        "balance_available": float(wallet.balance_available),
    }


@router.get("/export/chargeback")
async def export_chargeback(
    format: str = Query(default="csv", pattern="^(csv|json)$", description="Export format: csv or json"),
    wallet_type: Optional[str] = Query(default=None, description="Filter by wallet type (team, user, org)"),
    start_date: Optional[datetime] = Query(default=None, description="Start date (inclusive)"),
    end_date: Optional[datetime] = Query(default=None, description="End date (exclusive)"),
    session: Session = Depends(get_session),
):
    """
    T061: Chargeback export — aggregate spend by team/wallet and date range.

    Returns CSV or JSON with per-wallet spend totals for accounting/chargeback.
    """
    import csv
    import json as json_module
    from sqlalchemy import func

    # Build transaction query
    query = (
        select(
            WalletTransaction.wallet_id,
            func.sum(WalletTransaction.amount).label("total_spend"),
            func.count(WalletTransaction.id).label("tx_count"),
        )
        .where(WalletTransaction.transaction_type == WalletTransactionType.DEDUCTION)
    )

    if start_date:
        query = query.where(WalletTransaction.created_at >= start_date)
    if end_date:
        query = query.where(WalletTransaction.created_at < end_date)

    query = query.group_by(WalletTransaction.wallet_id)
    results = session.exec(query).all()

    # Enrich with wallet metadata
    rows = []
    for wallet_id, total_spend, tx_count in results:
        wallet = session.get(Wallet, wallet_id)
        if not wallet:
            continue
        if wallet_type and wallet.wallet_type.value != wallet_type:
            continue

        rows.append({
            "wallet_id": str(wallet.id),
            "wallet_name": wallet.name,
            "wallet_type": wallet.wallet_type.value,
            "owner_id": str(wallet.owner_id) if wallet.owner_id else "",
            "hard_limit": float(wallet.hard_limit),
            "total_spend": float(total_spend),
            "transaction_count": tx_count,
            "utilization_pct": round(float(total_spend / wallet.hard_limit * 100), 2) if wallet.hard_limit > 0 else 0,
            "currency": wallet.currency,
            "period_start": start_date.isoformat() if start_date else "all-time",
            "period_end": end_date.isoformat() if end_date else "now",
        })

    rows.sort(key=lambda r: r["total_spend"], reverse=True)

    if format == "json":
        return {
            "export_type": "chargeback",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_rows": len(rows),
            "total_spend": sum(r["total_spend"] for r in rows),
            "rows": rows,
        }

    # CSV streaming response
    output = StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        output.write("No data for the selected period\n")

    output.seek(0)
    filename = f"chargeback_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
