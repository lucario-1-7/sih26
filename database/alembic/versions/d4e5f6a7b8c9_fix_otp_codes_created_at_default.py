"""fix otp_codes.created_at frozen-default bug

Root cause of the OTP login "Invalid or expired OTP" bug: the column was
declared with `server_default="now()"` — a plain Python string. SQLAlchemy
emits that as `DEFAULT 'now()'::timestamptz`, a quoted *string literal*
default. Postgres constant-folds that cast once, at the moment the DEFAULT
clause itself is created (not per-row) — freezing every row's `created_at`
to the exact instant the migration ran. Contrast with `func.now()` /
`sa.text("now()")`, which emit the bare function call `DEFAULT now()`,
correctly re-evaluated on every INSERT.

`OtpRepository.get_latest_active()` orders by `created_at DESC` to find the
OTP just issued. With every row sharing one frozen timestamp, that ordering
is a coin flip among all of a phone's historical OTPs — so a freshly
requested, genuinely correct OTP could be checked against a stale row's
hash and fail as "Invalid or expired OTP".

This migration only repoints the column's DEFAULT going forward — existing
otp_codes rows keep whatever (wrong) created_at they already have, which is
fine: they're either already used, already expired, or about to be
superseded by a new request now getting a real timestamp.

Four other tables (audit_logs, duplicate_candidates, duplicate_decisions,
consortium_members) share the identical `server_default="now()"` string-literal
bug and are NOT touched here — out of scope for the OTP fix; flagged
separately for a follow-up migration.

Revision ID: d4e5f6a7b8c9
Revises: c3f4a5b6d7e8
Create Date: 2026-08-22 20:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3f4a5b6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('otp_codes', 'created_at', server_default=sa.text('now()'))


def downgrade() -> None:
    op.alter_column('otp_codes', 'created_at', server_default=sa.text("'now()'"))
