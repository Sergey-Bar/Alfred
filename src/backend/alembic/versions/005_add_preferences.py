"""Add preferences_json to users table

Revision ID: 005
Revises: 004
Create Date: 2026-02-12 13:00:00.000000
"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('preferences_json', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'preferences_json')
