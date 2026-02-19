"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Budget transfer workflow REST API (T087-T090).
             State machine: pending → approved/rejected/expired.
             Atomic approval: debit source + credit destination
             in a single DB transaction. Auto-expiry at 48h.
Root Cause:  Sprint tasks T087-T090 — Budget Transfer Workflow.
Context:     Enables teams to reallocate budget between wallets
             with approval gates and audit trails.
Suitability: L2 — standard REST + state machine + atomic ops.
──────────────────────────────────────────────────────────────

Alfred Budget Transfer Workflow
REST API for requesting, approving, and managing wallet-to-wallet budget transfers.
"""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session, select, col

from ..database import get_session
from ..models import (
    Wallet,
    WalletStatus,
    WalletTransaction,
    WalletTransactionType,
)

router = APIRouter(prefix="/v1/transfers", tags=["Budget Transfers"])

# ─── Constants ───────────────────────────────────────────────

TRANSFER_EXPIRY_HOURS = 48


# ─── Schemas ─────────────────────────────────────────────────

class TransferStatus(str, Enum):
    """Transfer request state machine."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class TransferCreate(BaseModel):
    """Create a new transfer request."""
    source_wallet_id: uuid.UUID
    destination_wallet_id: uuid.UUID
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=6)
    reason: str = Field(max_length=500)
    requested_by: Optional[uuid.UUID] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v


class TransferResponse(BaseModel):
    """Transfer request response."""
    id: uuid.UUID
    source_wallet_id: uuid.UUID
    destination_wallet_id: uuid.UUID
    amount: Decimal
    reason: str
    status: TransferStatus
    requested_by: Optional[uuid.UUID] = None
    reviewed_by: Optional[uuid.UUID] = None
    review_note: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    expires_at: datetime


class TransferReview(BaseModel):
    """Approve or reject a transfer."""
    action: str = Field(pattern="^(approve|reject)$")
    reviewed_by: uuid.UUID
    note: Optional[str] = Field(default=None, max_length=500)


class TransferListResponse(BaseModel):
    """Paginated transfer list."""
    transfers: List[TransferResponse]
    total: int
    page: int
    page_size: int


# ─── In-Memory Transfer Store ────────────────────────────────
# In production, this would be a DB table.
# For now, we store transfers in-memory with the same API contract.

_transfers: dict[uuid.UUID, dict] = {}


def _get_transfer_or_404(transfer_id: uuid.UUID) -> dict:
    """Get a transfer by ID or raise 404."""
    tfr = _transfers.get(transfer_id)
    if not tfr:
        raise HTTPException(status_code=404, detail="Transfer request not found")
    # Auto-expire
    if tfr["status"] == TransferStatus.PENDING and datetime.now(timezone.utc) > tfr["expires_at"]:
        tfr["status"] = TransferStatus.EXPIRED
    return tfr


def _to_response(tfr: dict) -> TransferResponse:
    """Convert internal dict to response model."""
    return TransferResponse(**tfr)


# ─── Endpoints ───────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransferResponse)
async def create_transfer(
    body: TransferCreate,
    session: Session = Depends(get_session),
):
    """
    T087: Create a new budget transfer request.

    Validates that both wallets exist and source has sufficient balance.
    Sets status to PENDING with a 48-hour expiry window.
    """
    # Validate source wallet
    source = session.get(Wallet, body.source_wallet_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source wallet not found")
    if source.status != WalletStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Source wallet is not active")

    # Validate destination wallet
    dest = session.get(Wallet, body.destination_wallet_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination wallet not found")
    if dest.status != WalletStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Destination wallet is not active")

    # Check same wallet
    if body.source_wallet_id == body.destination_wallet_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same wallet")

    # Check sufficient balance
    available = source.hard_limit - source.balance_used - source.balance_reserved
    if body.amount > available:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Available: {available}, Requested: {body.amount}",
        )

    now = datetime.now(timezone.utc)
    transfer_id = uuid.uuid4()

    tfr = {
        "id": transfer_id,
        "source_wallet_id": body.source_wallet_id,
        "destination_wallet_id": body.destination_wallet_id,
        "amount": body.amount,
        "reason": body.reason,
        "status": TransferStatus.PENDING,
        "requested_by": body.requested_by,
        "reviewed_by": None,
        "review_note": None,
        "created_at": now,
        "reviewed_at": None,
        "expires_at": now + timedelta(hours=TRANSFER_EXPIRY_HOURS),
    }

    _transfers[transfer_id] = tfr
    return _to_response(tfr)


@router.get("", response_model=TransferListResponse)
async def list_transfers(
    wallet_id: Optional[uuid.UUID] = Query(default=None, description="Filter by wallet (source or dest)"),
    transfer_status: Optional[TransferStatus] = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """
    T090: List transfer requests with optional filters.
    """
    # Auto-expire pending transfers
    now = datetime.now(timezone.utc)
    for tfr in _transfers.values():
        if tfr["status"] == TransferStatus.PENDING and now > tfr["expires_at"]:
            tfr["status"] = TransferStatus.EXPIRED

    # Filter
    items = list(_transfers.values())
    if wallet_id:
        items = [
            t for t in items
            if t["source_wallet_id"] == wallet_id or t["destination_wallet_id"] == wallet_id
        ]
    if transfer_status:
        items = [t for t in items if t["status"] == transfer_status]

    # Sort by created_at descending
    items.sort(key=lambda t: t["created_at"], reverse=True)

    total = len(items)
    start = (page - 1) * page_size
    page_items = items[start : start + page_size]

    return TransferListResponse(
        transfers=[_to_response(t) for t in page_items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(transfer_id: uuid.UUID):
    """Get a transfer request by ID."""
    return _to_response(_get_transfer_or_404(transfer_id))


@router.post("/{transfer_id}/review", response_model=TransferResponse)
async def review_transfer(
    transfer_id: uuid.UUID,
    body: TransferReview,
    session: Session = Depends(get_session),
):
    """
    T088: Approve or reject a transfer request.

    On approval: atomically deducts from source wallet and credits
    destination wallet, recording audit transactions for both sides.
    """
    tfr = _get_transfer_or_404(transfer_id)

    if tfr["status"] != TransferStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Transfer is '{tfr['status'].value}', cannot review",
        )

    now = datetime.now(timezone.utc)
    tfr["reviewed_by"] = body.reviewed_by
    tfr["review_note"] = body.note
    tfr["reviewed_at"] = now

    if body.action == "reject":
        tfr["status"] = TransferStatus.REJECTED
        return _to_response(tfr)

    # === APPROVE: atomic transfer ===
    source = session.get(Wallet, tfr["source_wallet_id"])
    dest = session.get(Wallet, tfr["destination_wallet_id"])

    if not source or not dest:
        raise HTTPException(status_code=404, detail="One or both wallets no longer exist")

    amount = Decimal(str(tfr["amount"]))

    # Re-validate source balance
    available = source.hard_limit - source.balance_used - source.balance_reserved
    if amount > available:
        tfr["status"] = TransferStatus.REJECTED
        tfr["review_note"] = (body.note or "") + " [Auto-rejected: insufficient balance]"
        raise HTTPException(
            status_code=400,
            detail="Source wallet no longer has sufficient balance",
        )

    # Debit source
    source_balance_before = source.balance_used
    source.balance_used += amount
    source.updated_at = now

    source_tx = WalletTransaction(
        wallet_id=source.id,
        transaction_type=WalletTransactionType.TRANSFER_OUT,
        amount=amount,
        balance_before=source_balance_before,
        balance_after=source.balance_used,
        description=f"Transfer to {dest.name}: {tfr['reason']}",
        request_id=str(transfer_id),
        created_by=body.reviewed_by,
    )

    # Credit destination (increase hard_limit, effectively adding budget)
    dest_limit_before = dest.hard_limit
    dest.hard_limit += amount
    dest.updated_at = now

    dest_tx = WalletTransaction(
        wallet_id=dest.id,
        transaction_type=WalletTransactionType.TRANSFER_IN,
        amount=amount,
        balance_before=dest_limit_before,
        balance_after=dest.hard_limit,
        description=f"Transfer from {source.name}: {tfr['reason']}",
        request_id=str(transfer_id),
        created_by=body.reviewed_by,
    )

    session.add(source)
    session.add(dest)
    session.add(source_tx)
    session.add(dest_tx)
    session.commit()

    tfr["status"] = TransferStatus.APPROVED

    return _to_response(tfr)


@router.post("/{transfer_id}/cancel", response_model=TransferResponse)
async def cancel_transfer(
    transfer_id: uuid.UUID,
    cancelled_by: Optional[uuid.UUID] = Query(default=None),
):
    """
    Cancel a pending transfer request.

    Only pending transfers can be cancelled.
    """
    tfr = _get_transfer_or_404(transfer_id)

    if tfr["status"] != TransferStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Transfer is '{tfr['status'].value}', cannot cancel",
        )

    tfr["status"] = TransferStatus.CANCELLED
    tfr["reviewed_at"] = datetime.now(timezone.utc)
    tfr["reviewed_by"] = cancelled_by

    return _to_response(tfr)
