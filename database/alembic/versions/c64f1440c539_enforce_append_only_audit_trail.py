"""enforce append-only audit trail

Revision ID: c64f1440c539
Revises: 929cadbb3720
Create Date: 2026-08-22 22:02:01.362390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c64f1440c539'
down_revision: Union[str, None] = '929cadbb3720'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE FUNCTION reject_update_or_delete() RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION '% is append-only: % is not permitted on this table', TG_TABLE_NAME, TG_OP;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    for table in ("audit_logs", "duplicate_decisions"):
        op.execute(
            f"""
            CREATE TRIGGER {table}_reject_update
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION reject_update_or_delete();
            """
        )
        op.execute(
            f"""
            CREATE TRIGGER {table}_reject_delete
            BEFORE DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION reject_update_or_delete();
            """
        )


def downgrade() -> None:
    for table in ("audit_logs", "duplicate_decisions"):
        op.execute(f"DROP TRIGGER IF EXISTS {table}_reject_update ON {table}")
        op.execute(f"DROP TRIGGER IF EXISTS {table}_reject_delete ON {table}")
    op.execute("DROP FUNCTION IF EXISTS reject_update_or_delete()")
