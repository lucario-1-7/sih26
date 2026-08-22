"""duplicate decision ordering sequence

created_at alone is not a safe tiebreaker for "the current effective
decision" — two decisions on the same candidate pair, recorded in quick
succession, can land on the same server-side timestamp. A monotonic
identity column gives correction/rollback logic (and any ORDER BY on this
append-only table) a deterministic, collision-free ordering key.

Revision ID: a1f3c2d4e5b6
Revises: c64f1440c539
Create Date: 2026-08-22 23:59:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1f3c2d4e5b6'
down_revision: Union[str, None] = 'c64f1440c539'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'duplicate_decisions',
        sa.Column('sequence', sa.BigInteger(), sa.Identity(always=True), nullable=False),
    )
    op.create_index(
        op.f('ix_duplicate_decisions_sequence'), 'duplicate_decisions', ['sequence'], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_duplicate_decisions_sequence'), table_name='duplicate_decisions')
    op.drop_column('duplicate_decisions', 'sequence')
