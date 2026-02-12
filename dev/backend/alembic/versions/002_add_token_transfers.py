"""Add credit reallocations table

Revision ID: 002_add_token_transfers
Revises: 001_initial
Create Date: 2026-02-11 16:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '002_add_token_transfers'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create token_transfers table for tracking credit reallocations between users."""
    op.create_table(
        'token_transfers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('sender_id', sa.Uuid(), nullable=False),
        sa.Column('recipient_id', sa.Uuid(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('message', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient querying
    op.create_index(
        op.f('ix_token_transfers_sender_id'),
        'token_transfers',
        ['sender_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_token_transfers_recipient_id'),
        'token_transfers',
        ['recipient_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove token_transfers table."""
    op.drop_index(op.f('ix_token_transfers_recipient_id'), table_name='token_transfers')
    op.drop_index(op.f('ix_token_transfers_sender_id'), table_name='token_transfers')
    op.drop_table('token_transfers')
