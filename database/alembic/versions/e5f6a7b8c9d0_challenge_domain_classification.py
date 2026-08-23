"""challenge domain classification

Adds AI-suggested civic-domain classification fields to `challenges`,
populated by the `generate_duplicate_candidates` worker job via
ml/app/domain_classification (POST /api/v1/classify-domain). Advisory only —
these fields are never authoritative and no workflow requires a human to
accept them; `content_domain_needs_review` and `content_domain_source`
("trained" | "zero_shot_fallback") exist so the UI can flag low-confidence or
degraded classifications for a human to look at.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-08-23 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('challenges', sa.Column('content_domain', sa.String(length=50), nullable=True))
    op.add_column('challenges', sa.Column('content_domain_confidence', sa.Float(), nullable=True))
    op.add_column('challenges', sa.Column('content_domain_needs_review', sa.Boolean(), nullable=True))
    op.add_column('challenges', sa.Column('content_domain_source', sa.String(length=30), nullable=True))


def downgrade() -> None:
    op.drop_column('challenges', 'content_domain_source')
    op.drop_column('challenges', 'content_domain_needs_review')
    op.drop_column('challenges', 'content_domain_confidence')
    op.drop_column('challenges', 'content_domain')
