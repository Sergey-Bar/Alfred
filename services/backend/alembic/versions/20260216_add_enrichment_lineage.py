"""
Alembic migration stub: add enrichment and lineage tables

Model: GitHub Copilot (GPT-5 mini)
Logic: Create persistent tables for enrichment pipelines, enrichment jobs, and lineage events.
Why: Replace prior in-memory demo stores to ensure durability and auditing across restarts.
Root Cause: Demo lists were not persisted; production requires DB schema updates.
Context: Run `alembic upgrade head` after placing this file (verify `down_revision` with existing history).
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260216_add_enrichment_lineage"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "enrichment_pipelines",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("target_dataset", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("config", sa.JSON, nullable=True),
    )

    op.create_table(
        "enrichment_jobs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "pipeline_id", sa.Integer, sa.ForeignKey("enrichment_pipelines.id"), nullable=False
        ),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime, nullable=False),
        sa.Column("finished_at", sa.DateTime, nullable=True),
        sa.Column("result", sa.Text, nullable=True),
    )

    op.create_table(
        "lineage_events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("timestamp", sa.DateTime, nullable=False),
        sa.Column("dataset", sa.String(length=255), nullable=False),
        sa.Column("operation", sa.String(length=100), nullable=False),
        sa.Column("source_datasets", sa.JSON, nullable=True),
        sa.Column("user", sa.String(length=255), nullable=True),
        sa.Column("details", sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("lineage_events")
    op.drop_table("enrichment_jobs")
    op.drop_table("enrichment_pipelines")
