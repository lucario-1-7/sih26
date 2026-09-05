"""domain/role alignment: government/university/industry/superadmin

Aligns the user role model with the final SocioSolve architecture:

  - `Role.OFFICER`  -> `Role.VALIDATOR`     (government challenge/duplicate review)
  - `Role.ANALYST`  -> `Role.VALIDATOR`     (read-only review access folded into VALIDATOR)
  - `Role.ADMIN`    -> `Role.SUPERADMIN`    (platform-wide administration)
  - `Role.CITIZEN`  -> unchanged

No `student` or `gov_admin` role existed in this schema prior to this
migration, so there is nothing to migrate away from for those — this
migration only *adds* the new roles (COORDINATOR, FACULTY, INDUSTRY) and
introduces the `domain` column.

Adds:
  - `users.domain` (new `user_domain` enum) + CHECK constraint pairing it
    with a valid `role`
  - `users.organization_id` (nullable FK -> organizations) for
    university/industry staff
  - `projects.organization_id` (nullable FK -> organizations) for
    institutional project ownership/isolation
  - `challenges.severity` (new `challenge_severity` enum, nullable) —
    VALIDATOR responsibility
  - `project_participants` table — student/participant records with no
    user account, login, or role

Revision ID: b2e7f8a9c0d1
Revises: a1f3c2d4e5b6
Create Date: 2026-08-23 00:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b2e7f8a9c0d1'
down_revision: Union[str, None] = 'a1f3c2d4e5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_ROLE_VALUES = (
    'citizen', 'validator', 'field_assistant', 'coordinator', 'faculty', 'industry', 'superadmin',
)
DOMAIN_VALUES = ('citizen', 'government', 'university', 'industry', 'superadmin')
SEVERITY_VALUES = ('low', 'medium', 'high', 'critical')


def upgrade() -> None:
    # --- 1. Migrate users.role onto the new enum, remapping old values ----
    role_new = postgresql.ENUM(*NEW_ROLE_VALUES, name='user_role_new')
    role_new.create(op.get_bind())

    op.add_column('users', sa.Column('role_new', role_new, nullable=True))
    op.execute(
        """
        UPDATE users SET role_new = (CASE role::text
            WHEN 'officer' THEN 'validator'
            WHEN 'analyst' THEN 'validator'
            WHEN 'admin' THEN 'superadmin'
            ELSE role::text
        END)::user_role_new
        """
    )
    op.alter_column('users', 'role_new', nullable=False)
    op.drop_column('users', 'role')
    op.execute('DROP TYPE user_role')
    op.alter_column('users', 'role_new', new_column_name='role')
    op.execute('ALTER TYPE user_role_new RENAME TO user_role')

    # --- 2. users.domain, backfilled from the now-migrated role -----------
    domain_enum = postgresql.ENUM(*DOMAIN_VALUES, name='user_domain')
    domain_enum.create(op.get_bind())
    op.add_column('users', sa.Column('domain', domain_enum, nullable=True))
    op.execute(
        """
        UPDATE users SET domain = (CASE role::text
            WHEN 'citizen' THEN 'citizen'
            WHEN 'validator' THEN 'government'
            WHEN 'field_assistant' THEN 'government'
            WHEN 'coordinator' THEN 'university'
            WHEN 'faculty' THEN 'university'
            WHEN 'industry' THEN 'industry'
            WHEN 'superadmin' THEN 'superadmin'
        END)::user_domain
        """
    )
    op.alter_column('users', 'domain', nullable=False)

    # --- 3. users.organization_id ------------------------------------------
    op.add_column('users', sa.Column('organization_id', sa.Uuid(), nullable=True))
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    op.create_foreign_key(
        op.f('fk_users_organization_id_organizations'),
        'users', 'organizations', ['organization_id'], ['id'], ondelete='RESTRICT',
    )

    # --- 4. CHECK constraint pairing domain <-> role ------------------------
    op.create_check_constraint(
        'ck_users_valid_domain_role',
        'users',
        """
        (domain = 'citizen' AND role = 'citizen') OR
        (domain = 'government' AND role IN ('validator', 'field_assistant')) OR
        (domain = 'university' AND role IN ('coordinator', 'faculty')) OR
        (domain = 'industry' AND role = 'industry') OR
        (domain = 'superadmin' AND role = 'superadmin')
        """,
    )

    # --- 5. projects.organization_id ---------------------------------------
    op.add_column('projects', sa.Column('organization_id', sa.Uuid(), nullable=True))
    op.create_index(op.f('ix_projects_organization_id'), 'projects', ['organization_id'], unique=False)
    op.create_foreign_key(
        op.f('fk_projects_organization_id_organizations'),
        'projects', 'organizations', ['organization_id'], ['id'], ondelete='RESTRICT',
    )

    # --- 6. challenges.severity ---------------------------------------------
    severity_enum = postgresql.ENUM(*SEVERITY_VALUES, name='challenge_severity')
    severity_enum.create(op.get_bind())
    op.add_column('challenges', sa.Column('severity', severity_enum, nullable=True))

    # --- 7. project_participants (students — no user account) --------------
    op.create_table(
        'project_participants',
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('department', sa.String(length=200), nullable=True),
        sa.Column('academic_year', sa.String(length=20), nullable=True),
        sa.Column('registration_id', sa.String(length=100), nullable=True),
        sa.Column('participation_role', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['project_id'], ['projects.id'],
            name=op.f('fk_project_participants_project_id_projects'), ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_project_participants')),
    )
    op.create_index(
        op.f('ix_project_participants_project_id'), 'project_participants', ['project_id'], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_project_participants_project_id'), table_name='project_participants')
    op.drop_table('project_participants')

    op.drop_column('challenges', 'severity')
    op.execute('DROP TYPE challenge_severity')

    op.drop_constraint(op.f('fk_projects_organization_id_organizations'), 'projects', type_='foreignkey')
    op.drop_index(op.f('ix_projects_organization_id'), table_name='projects')
    op.drop_column('projects', 'organization_id')

    op.drop_constraint('ck_users_valid_domain_role', 'users', type_='check')

    op.drop_constraint(op.f('fk_users_organization_id_organizations'), 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_column('users', 'organization_id')

    op.drop_column('users', 'domain')
    op.execute('DROP TYPE user_domain')

    role_old = postgresql.ENUM('citizen', 'officer', 'analyst', 'admin', name='user_role_old')
    role_old.create(op.get_bind())
    op.add_column('users', sa.Column('role_old', role_old, nullable=True))
    op.execute(
        """
        UPDATE users SET role_old = (CASE role::text
            WHEN 'validator' THEN 'officer'
            WHEN 'field_assistant' THEN 'officer'
            WHEN 'coordinator' THEN 'officer'
            WHEN 'faculty' THEN 'officer'
            WHEN 'industry' THEN 'officer'
            WHEN 'superadmin' THEN 'admin'
            ELSE role::text
        END)::user_role_old
        """
    )
    op.alter_column('users', 'role_old', nullable=False)
    op.drop_column('users', 'role')
    op.execute('DROP TYPE user_role')
    op.alter_column('users', 'role_old', new_column_name='role')
    op.execute('ALTER TYPE user_role_old RENAME TO user_role')
