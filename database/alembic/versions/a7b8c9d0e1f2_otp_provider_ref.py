"""otp provider reference

Supports MSG91's native OTP lifecycle (Widget product): MSG91 generates and
verifies the OTP itself, returning a `reqId` our backend must present back on
verify. `otp_codes.code_hash` becomes nullable (a provider-native row has no
local hash to check — verification happens via a call to the provider) and
`provider_ref` stores that reqId. Existing console/delivery-only rows are
unaffected — `code_hash` stays populated, `provider_ref` stays null.

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-08-23 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('otp_codes', sa.Column('provider_ref', sa.String(length=100), nullable=True))
    op.alter_column('otp_codes', 'code_hash', existing_type=sa.String(length=128), nullable=True)


def downgrade() -> None:
    op.alter_column('otp_codes', 'code_hash', existing_type=sa.String(length=128), nullable=False)
    op.drop_column('otp_codes', 'provider_ref')
