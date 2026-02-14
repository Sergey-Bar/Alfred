"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-11 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column('common_pool', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('used_pool', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('vacation_share_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('api_key_hash', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('personal_quota', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('used_tokens', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('default_priority', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('strict_privacy_default', sa.Boolean(), nullable=False),
        sa.Column('vacation_start', sa.DateTime(), nullable=True),
        sa.Column('vacation_end', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_request_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create team_member_links table
    op.create_table(
        'team_member_links',
        sa.Column('team_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('team_id', 'user_id')
    )

    # Create org_settings table
    op.create_table(
        'org_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('allow_vacation_sharing', sa.Boolean(), nullable=False),
        sa.Column('allow_priority_bypass', sa.Boolean(), nullable=False),
        sa.Column('force_strict_privacy', sa.Boolean(), nullable=False),
        sa.Column('max_vacation_share_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('default_personal_quota', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('default_team_pool', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create request_logs table
    op.create_table(
        'request_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('team_id', sa.Uuid(), nullable=True),
        sa.Column('model', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=False),
        sa.Column('completion_tokens', sa.Integer(), nullable=False),
        sa.Column('total_tokens', sa.Integer(), nullable=False),
        sa.Column('cost_credits', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('quota_source', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('priority', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('efficiency_score', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=False),
        sa.Column('privacy_mode', sa.Boolean(), nullable=False),
        sa.Column('messages_logged', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_request_logs_created_at'), 'request_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_request_logs_user_id'), 'request_logs', ['user_id'], unique=False)

    # Create leaderboard_entries table
    op.create_table(
        'leaderboard_entries',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('period_type', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('total_requests', sa.Integer(), nullable=False),
        sa.Column('total_tokens', sa.Integer(), nullable=False),
        sa.Column('total_cost_credits', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('avg_efficiency_score', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leaderboard_entries_period_type'), 'leaderboard_entries', ['period_type'], unique=False)

    # Create approval_requests table
    op.create_table(
        'approval_requests',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('team_id', sa.Uuid(), nullable=True),
        sa.Column('requested_credits', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('approved_credits', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('reason', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('priority', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('reviewed_by_id', sa.Uuid(), nullable=True),
        sa.Column('review_notes', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_approval_requests_status'), 'approval_requests', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_approval_requests_status'), table_name='approval_requests')
    op.drop_table('approval_requests')
    op.drop_index(op.f('ix_leaderboard_entries_period_type'), table_name='leaderboard_entries')
    op.drop_table('leaderboard_entries')
    op.drop_index(op.f('ix_request_logs_user_id'), table_name='request_logs')
    op.drop_index(op.f('ix_request_logs_created_at'), table_name='request_logs')
    op.drop_table('request_logs')
    op.drop_table('org_settings')
    op.drop_table('team_member_links')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_teams_name'), table_name='teams')
    op.drop_table('teams')
