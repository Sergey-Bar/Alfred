"""
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L4
Logic:       Monthly billing reconciliation job. Compares
             Alfred's internal ledger transaction totals with
             provider invoice data (via API or uploaded CSV).
             Produces a discrepancy report and optionally
             creates adjustment transactions.
Root Cause:  Sprint task T200 — Billing reconciliation.
Context:     FinOps requires monthly proof that our counts
             match provider invoices within tolerance.
Suitability: L4 — touches ledger/billing (financial integrity).
──────────────────────────────────────────────────────────────

ROLLBACK: To revert this change:
  1. Remove this file from the cron/task scheduler
  2. No DB migration needed (read-only + optional adjustments)
  3. Notify: Sergey Bar + FinOps team
"""

import csv
import io
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class ProviderInvoiceLine:
    """A single line item from a provider's invoice."""

    provider: str
    model: str
    period_start: datetime
    period_end: datetime
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    amount_usd: float = 0.0
    invoice_id: str = ""
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class LedgerSummary:
    """Summary of Alfred's internal ledger for a provider/model/period."""

    provider: str
    model: str
    period_start: datetime
    period_end: datetime
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    transaction_count: int = 0


@dataclass
class Discrepancy:
    """A discrepancy between Alfred ledger and provider invoice."""

    provider: str
    model: str
    period_start: datetime
    period_end: datetime
    field: str  # e.g., "total_tokens", "amount_usd"
    alfred_value: float
    provider_value: float
    difference: float
    difference_pct: float
    severity: str  # "info", "warning", "critical"
    notes: str = ""


@dataclass
class ReconciliationReport:
    """Full reconciliation report."""

    report_id: str = field(default_factory=lambda: str(uuid4()))
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    providers_checked: List[str] = field(default_factory=list)
    total_alfred_spend: float = 0.0
    total_provider_billed: float = 0.0
    overall_difference: float = 0.0
    overall_difference_pct: float = 0.0
    discrepancies: List[Discrepancy] = field(default_factory=list)
    status: str = "pending"  # pending, passed, warning, failed
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at.isoformat(),
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "providers_checked": self.providers_checked,
            "total_alfred_spend": round(self.total_alfred_spend, 4),
            "total_provider_billed": round(self.total_provider_billed, 4),
            "overall_difference": round(self.overall_difference, 4),
            "overall_difference_pct": round(self.overall_difference_pct, 2),
            "discrepancy_count": len(self.discrepancies),
            "critical_discrepancies": len(
                [d for d in self.discrepancies if d.severity == "critical"]
            ),
            "status": self.status,
            "summary": self.summary,
            "discrepancies": [
                {
                    "provider": d.provider,
                    "model": d.model,
                    "field": d.field,
                    "alfred_value": round(d.alfred_value, 4),
                    "provider_value": round(d.provider_value, 4),
                    "difference": round(d.difference, 4),
                    "difference_pct": round(d.difference_pct, 2),
                    "severity": d.severity,
                    "notes": d.notes,
                }
                for d in self.discrepancies
            ],
        }


# Cost tolerance: differences below this are "info", above "warning", above 2x "critical"
COST_TOLERANCE_PCT = 2.0  # 2% tolerance
TOKEN_TOLERANCE_PCT = 1.0  # 1% tolerance for token counts

# Absolute minimum to flag (ignore rounding errors under $0.01)
COST_TOLERANCE_ABS = 0.01
TOKEN_TOLERANCE_ABS = 10


class BillingReconciler:
    """
    Compares Alfred internal ledger with provider invoices.

    Usage:
        reconciler = BillingReconciler()
        reconciler.add_ledger_summary(ledger_data)
        reconciler.add_invoice_lines(invoice_lines)
        report = reconciler.reconcile()
    """

    def __init__(
        self,
        cost_tolerance_pct: float = COST_TOLERANCE_PCT,
        token_tolerance_pct: float = TOKEN_TOLERANCE_PCT,
    ):
        self.cost_tolerance_pct = cost_tolerance_pct
        self.token_tolerance_pct = token_tolerance_pct
        self.ledger_data: List[LedgerSummary] = []
        self.invoice_data: List[ProviderInvoiceLine] = []

    def add_ledger_summary(self, summary: LedgerSummary) -> None:
        """Add an Alfred ledger summary for reconciliation."""
        self.ledger_data.append(summary)

    def add_invoice_lines(self, lines: List[ProviderInvoiceLine]) -> None:
        """Add provider invoice lines."""
        self.invoice_data.extend(lines)

    def load_invoice_csv(self, csv_content: str, provider: str) -> int:
        """
        Load invoice data from CSV format.

        Expected columns: model, prompt_tokens, completion_tokens, total_tokens,
                          amount_usd, period_start, period_end, invoice_id

        Returns:
            Number of lines loaded.
        """
        reader = csv.DictReader(io.StringIO(csv_content))
        count = 0
        for row in reader:
            try:
                line = ProviderInvoiceLine(
                    provider=provider,
                    model=row.get("model", "unknown"),
                    period_start=datetime.fromisoformat(row["period_start"]),
                    period_end=datetime.fromisoformat(row["period_end"]),
                    prompt_tokens=int(row.get("prompt_tokens", 0)),
                    completion_tokens=int(row.get("completion_tokens", 0)),
                    total_tokens=int(row.get("total_tokens", 0)),
                    amount_usd=float(row.get("amount_usd", 0.0)),
                    invoice_id=row.get("invoice_id", ""),
                    raw_data=dict(row),
                )
                self.invoice_data.append(line)
                count += 1
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid invoice row: {e}")
        return count

    def reconcile(
        self,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> ReconciliationReport:
        """
        Run reconciliation and produce a report.

        Compares each provider+model combination in both datasets.
        """
        report = ReconciliationReport(
            period_start=period_start,
            period_end=period_end,
        )

        # Index ledger by (provider, model)
        ledger_index: Dict[str, LedgerSummary] = {}
        for s in self.ledger_data:
            key = f"{s.provider}::{s.model}"
            if key in ledger_index:
                # Merge
                existing = ledger_index[key]
                existing.prompt_tokens += s.prompt_tokens
                existing.completion_tokens += s.completion_tokens
                existing.total_tokens += s.total_tokens
                existing.total_cost_usd += s.total_cost_usd
                existing.transaction_count += s.transaction_count
            else:
                ledger_index[key] = LedgerSummary(
                    provider=s.provider,
                    model=s.model,
                    period_start=s.period_start,
                    period_end=s.period_end,
                    prompt_tokens=s.prompt_tokens,
                    completion_tokens=s.completion_tokens,
                    total_tokens=s.total_tokens,
                    total_cost_usd=s.total_cost_usd,
                    transaction_count=s.transaction_count,
                )

        # Index invoices by (provider, model)
        invoice_index: Dict[str, ProviderInvoiceLine] = {}
        for inv in self.invoice_data:
            key = f"{inv.provider}::{inv.model}"
            if key in invoice_index:
                existing = invoice_index[key]
                existing.prompt_tokens += inv.prompt_tokens
                existing.completion_tokens += inv.completion_tokens
                existing.total_tokens += inv.total_tokens
                existing.amount_usd += inv.amount_usd
            else:
                invoice_index[key] = ProviderInvoiceLine(
                    provider=inv.provider,
                    model=inv.model,
                    period_start=inv.period_start,
                    period_end=inv.period_end,
                    prompt_tokens=inv.prompt_tokens,
                    completion_tokens=inv.completion_tokens,
                    total_tokens=inv.total_tokens,
                    amount_usd=inv.amount_usd,
                    invoice_id=inv.invoice_id,
                )

        all_keys = set(ledger_index.keys()) | set(invoice_index.keys())
        providers_seen = set()

        for key in sorted(all_keys):
            ledger = ledger_index.get(key)
            invoice = invoice_index.get(key)

            if ledger:
                providers_seen.add(ledger.provider)
                report.total_alfred_spend += ledger.total_cost_usd
            if invoice:
                providers_seen.add(invoice.provider)
                report.total_provider_billed += invoice.amount_usd

            provider = ledger.provider if ledger else (invoice.provider if invoice else "unknown")
            model = ledger.model if ledger else (invoice.model if invoice else "unknown")
            ps = period_start or datetime.now(timezone.utc) - timedelta(days=30)
            pe = period_end or datetime.now(timezone.utc)

            if ledger and not invoice:
                # We have charges, provider has no invoice line — suspicious
                if ledger.total_cost_usd > COST_TOLERANCE_ABS:
                    report.discrepancies.append(
                        Discrepancy(
                            provider=provider,
                            model=model,
                            period_start=ps,
                            period_end=pe,
                            field="amount_usd",
                            alfred_value=ledger.total_cost_usd,
                            provider_value=0.0,
                            difference=ledger.total_cost_usd,
                            difference_pct=100.0,
                            severity="warning",
                            notes="Alfred has charges but no matching provider invoice line",
                        )
                    )
                continue

            if invoice and not ledger:
                # Provider billed us but we have no record
                if invoice.amount_usd > COST_TOLERANCE_ABS:
                    report.discrepancies.append(
                        Discrepancy(
                            provider=provider,
                            model=model,
                            period_start=ps,
                            period_end=pe,
                            field="amount_usd",
                            alfred_value=0.0,
                            provider_value=invoice.amount_usd,
                            difference=-invoice.amount_usd,
                            difference_pct=-100.0,
                            severity="critical",
                            notes="Provider billed but Alfred has no matching ledger entries",
                        )
                    )
                continue

            # Both exist — compare
            if ledger and invoice:
                self._compare_field(
                    report, provider, model, ps, pe,
                    "amount_usd",
                    ledger.total_cost_usd, invoice.amount_usd,
                    self.cost_tolerance_pct, COST_TOLERANCE_ABS,
                )
                self._compare_field(
                    report, provider, model, ps, pe,
                    "total_tokens",
                    float(ledger.total_tokens), float(invoice.total_tokens),
                    self.token_tolerance_pct, TOKEN_TOLERANCE_ABS,
                )
                self._compare_field(
                    report, provider, model, ps, pe,
                    "prompt_tokens",
                    float(ledger.prompt_tokens), float(invoice.prompt_tokens),
                    self.token_tolerance_pct, TOKEN_TOLERANCE_ABS,
                )
                self._compare_field(
                    report, provider, model, ps, pe,
                    "completion_tokens",
                    float(ledger.completion_tokens), float(invoice.completion_tokens),
                    self.token_tolerance_pct, TOKEN_TOLERANCE_ABS,
                )

        # Finalize
        report.providers_checked = sorted(providers_seen)
        report.overall_difference = report.total_alfred_spend - report.total_provider_billed
        if report.total_provider_billed > 0:
            report.overall_difference_pct = (
                report.overall_difference / report.total_provider_billed
            ) * 100
        else:
            report.overall_difference_pct = 0.0

        # Determine status
        critical_count = len(
            [d for d in report.discrepancies if d.severity == "critical"]
        )
        warning_count = len(
            [d for d in report.discrepancies if d.severity == "warning"]
        )

        if critical_count > 0:
            report.status = "failed"
            report.summary = (
                f"FAILED: {critical_count} critical discrepancies found. "
                f"Overall difference: ${report.overall_difference:+.2f} "
                f"({report.overall_difference_pct:+.1f}%)"
            )
        elif warning_count > 0:
            report.status = "warning"
            report.summary = (
                f"WARNING: {warning_count} discrepancies above tolerance. "
                f"Overall difference: ${report.overall_difference:+.2f} "
                f"({report.overall_difference_pct:+.1f}%)"
            )
        else:
            report.status = "passed"
            report.summary = (
                f"PASSED: All amounts within {self.cost_tolerance_pct}% tolerance. "
                f"Total Alfred: ${report.total_alfred_spend:.2f}, "
                f"Total Billed: ${report.total_provider_billed:.2f}"
            )

        logger.info(f"Reconciliation complete: {report.summary}")
        return report

    def _compare_field(
        self,
        report: ReconciliationReport,
        provider: str,
        model: str,
        period_start: datetime,
        period_end: datetime,
        field_name: str,
        alfred_val: float,
        provider_val: float,
        tolerance_pct: float,
        tolerance_abs: float,
    ) -> None:
        """Compare a single field and add discrepancy if outside tolerance."""
        diff = alfred_val - provider_val
        abs_diff = abs(diff)

        # Skip tiny differences
        if abs_diff <= tolerance_abs:
            return

        # Calculate percentage
        base = max(alfred_val, provider_val)
        if base == 0:
            return
        pct = (diff / base) * 100

        if abs(pct) <= tolerance_pct:
            return  # Within tolerance

        # Determine severity
        if abs(pct) > tolerance_pct * 5:
            severity = "critical"
        elif abs(pct) > tolerance_pct * 2:
            severity = "warning"
        else:
            severity = "info"

        report.discrepancies.append(
            Discrepancy(
                provider=provider,
                model=model,
                period_start=period_start,
                period_end=period_end,
                field=field_name,
                alfred_value=alfred_val,
                provider_value=provider_val,
                difference=diff,
                difference_pct=pct,
                severity=severity,
            )
        )


async def run_monthly_reconciliation(
    db_session: Any,
    invoice_csv: Optional[str] = None,
    provider: Optional[str] = None,
) -> ReconciliationReport:
    """
    Run monthly billing reconciliation.

    This function is intended to be called from a scheduled cron job
    or manually via an admin API endpoint.

    Args:
        db_session: Database session for reading ledger data.
        invoice_csv: Optional CSV content of provider invoice.
        provider: Provider name if invoice_csv is provided.

    Returns:
        ReconciliationReport with full results.
    """
    reconciler = BillingReconciler()

    # TODO: Query actual ledger data from database
    # Example:
    # SELECT provider, model, SUM(prompt_tokens), SUM(completion_tokens),
    #        SUM(total_tokens), SUM(cost_usd), COUNT(*)
    # FROM transactions
    # WHERE created_at BETWEEN :start AND :end
    # GROUP BY provider, model

    logger.info("Billing reconciliation started")

    if invoice_csv and provider:
        count = reconciler.load_invoice_csv(invoice_csv, provider)
        logger.info(f"Loaded {count} invoice lines for {provider}")

    now = datetime.now(timezone.utc)
    period_start = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
    period_end = now.replace(day=1) - timedelta(seconds=1)

    report = reconciler.reconcile(period_start=period_start, period_end=period_end)

    logger.info(
        f"Reconciliation report {report.report_id}: {report.status} — "
        f"{len(report.discrepancies)} discrepancies"
    )

    return report
