"""challenge field-intensity classification

Adds AI-suggested physical-vs-remote work-intensity classification fields to
`challenges`, populated by the `generate_duplicate_candidates` worker job via
ml/app/field_classification (POST /api/v1/classify-field-intensity). Same
advisory-only contract as `content_domain` (see migration e5f6a7b8c9d0):
never authoritative, `content_field_needs_review` and `content_field_source`
("trained" | "rules_fallback") let the UI flag a degraded classification.

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-23 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('challenges', sa.Column('content_field_intensity', sa.Float(), nullable=True))
    op.add_column('challenges', sa.Column('content_field_label', sa.String(length=30), nullable=True))
    op.add_column('challenges', sa.Column('content_field_needs_review', sa.Boolean(), nullable=True))
    op.add_column('challenges', sa.Column('content_field_source', sa.String(length=30), nullable=True))


def downgrade() -> None:
    op.drop_column('challenges', 'content_field_source')
    op.drop_column('challenges', 'content_field_needs_review')
    op.drop_column('challenges', 'content_field_label')
    op.drop_column('challenges', 'content_field_intensity')
