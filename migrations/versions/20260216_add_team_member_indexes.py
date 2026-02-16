"""
Alembic migration: add indexes to team_member_links

Creates single-column indexes on `team_id` and `user_id` to improve lookup
performance for common WHERE filters used by dashboard and governance endpoints.

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260216_add_team_member_indexes"
down_revision = "20260216_add_enrichment_lineage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_team_member_links_team_id", "team_member_links", ["team_id"], unique=False)
    op.create_index("ix_team_member_links_user_id", "team_member_links", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_team_member_links_user_id", table_name="team_member_links")
    op.drop_index("ix_team_member_links_team_id", table_name="team_member_links")
