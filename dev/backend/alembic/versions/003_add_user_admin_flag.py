"""Add is_admin flag to users table.

Revision ID: 003
Revises: 002_add_token_transfers
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '003'
down_revision = '002_add_token_transfers'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('users', 'is_admin')
