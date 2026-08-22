"""business feature completion: project lifecycle, milestones, deliverables,
industry collaboration, impact indicators, solution replication support

Adds the schema needed for the full university/industry business
workflow on top of the already-locked RBAC/domain model:

  - `projects.status`: remapped onto a richer lifecycle enum
    (proposed/accepted/active/on_hold/completed/cancelled), replacing
    planned -> proposed and in_progress -> active (data-preserving remap,
    same pattern as the prior role-enum migration).
  - `milestones`, `deliverables`: first-class project tracking, FK'd to
    `projects` with ON DELETE CASCADE (they have no independent meaning
    without their project).
  - `collaborations`, `collaboration_commitments`: the industry
    engagement model — one row per (organization, project) partnership,
    with typed/statused commitments underneath. Deliberately distinct
    from `consortiums` (see model docstring): a Consortium is the
    ML-suggested multi-org team proposed *for* a project; a Collaboration
    is one org's own bilateral engagement lifecycle, which an org drives
    itself by expressing interest.
  - `impact_indicators`: baseline/target/actual with a separate
    verification step — completing a project never implies verified
    impact.
  - `solutions`: adds `status`, `outcome`, and `embedding` (for
    replication-candidate search against open clusters).
  - `challenges`: adds `on_behalf_of_name`/`on_behalf_of_phone`, set only
    when a FIELD_ASSISTANT submits for a citizen who has no account.

Revision ID: c3f4a5b6d7e8
Revises: b2e7f8a9c0d1
Create Date: 2026-08-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql


revision: str = 'c3f4a5b6d7e8'
down_revision: Union[str, None] = 'b2e7f8a9c0d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_PROJECT_STATUS_VALUES = ('proposed', 'accepted', 'active', 'on_hold', 'completed', 'cancelled')
MILESTONE_STATUS_VALUES = ('pending', 'in_progress', 'completed', 'blocked')
DELIVERABLE_STATUS_VALUES = ('pending', 'submitted', 'verified', 'rejected')
COLLABORATION_TYPE_VALUES = ('funding', 'mentoring', 'equipment', 'technical_support', 'pilot_support', 'other')
COLLABORATION_STATUS_VALUES = ('interested', 'proposed', 'accepted', 'active', 'completed', 'rejected')
COMMITMENT_STATUS_VALUES = ('proposed', 'accepted', 'fulfilled', 'rejected')
SOLUTION_STATUS_VALUES = ('draft', 'published')


def upgrade() -> None:
    # --- 1. projects.status -> richer lifecycle enum, data-preserving ------
    status_new = postgresql.ENUM(*NEW_PROJECT_STATUS_VALUES, name='project_status_new')
    status_new.create(op.get_bind())
    op.add_column('projects', sa.Column('status_new', status_new, nullable=True))
    op.execute(
        """
        UPDATE projects SET status_new = (CASE status::text
            WHEN 'planned' THEN 'proposed'
            WHEN 'in_progress' THEN 'active'
            ELSE status::text
        END)::project_status_new
        """
    )
    op.alter_column('projects', 'status_new', nullable=False)
    op.drop_column('projects', 'status')
    op.execute('DROP TYPE project_status')
    op.alter_column('projects', 'status_new', new_column_name='status')
    op.execute('ALTER TYPE project_status_new RENAME TO project_status')

    # --- 2. challenges: on-behalf-of fields ---------------------------------
    op.add_column('challenges', sa.Column('on_behalf_of_name', sa.String(length=200), nullable=True))
    op.add_column('challenges', sa.Column('on_behalf_of_phone', sa.String(length=20), nullable=True))

    # --- 3. milestones -------------------------------------------------------
    milestone_status = postgresql.ENUM(*MILESTONE_STATUS_VALUES, name='milestone_status')
    op.create_table(
        'milestones',
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('status', milestone_status, nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['project_id'], ['projects.id'], name=op.f('fk_milestones_project_id_projects'), ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_milestones')),
    )
    op.create_index(op.f('ix_milestones_project_id'), 'milestones', ['project_id'], unique=False)

    # --- 4. deliverables -------------------------------------------------------
    deliverable_status = postgresql.ENUM(*DELIVERABLE_STATUS_VALUES, name='deliverable_status')
    op.create_table(
        'deliverables',
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('status', deliverable_status, nullable=False),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by_id', sa.Uuid(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['project_id'], ['projects.id'], name=op.f('fk_deliverables_project_id_projects'), ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['verified_by_id'], ['users.id'], name=op.f('fk_deliverables_verified_by_id_users'), ondelete='RESTRICT'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_deliverables')),
    )
    op.create_index(op.f('ix_deliverables_project_id'), 'deliverables', ['project_id'], unique=False)
    op.create_index(op.f('ix_deliverables_verified_by_id'), 'deliverables', ['verified_by_id'], unique=False)

    # --- 5. collaborations + collaboration_commitments ------------------------
    collab_type = postgresql.ENUM(*COLLABORATION_TYPE_VALUES, name='collaboration_type')
    collab_status = postgresql.ENUM(*COLLABORATION_STATUS_VALUES, name='collaboration_status')
    op.create_table(
        'collaborations',
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('type', collab_type, nullable=False),
        sa.Column('status', collab_status, nullable=False),
        sa.Column('proposal', sa.Text(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['organization_id'], ['organizations.id'],
            name=op.f('fk_collaborations_organization_id_organizations'), ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['project_id'], ['projects.id'], name=op.f('fk_collaborations_project_id_projects'), ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_collaborations')),
        sa.UniqueConstraint('organization_id', 'project_id', name='uq_collaboration_org_project'),
    )
    op.create_index(op.f('ix_collaborations_organization_id'), 'collaborations', ['organization_id'], unique=False)
    op.create_index(op.f('ix_collaborations_project_id'), 'collaborations', ['project_id'], unique=False)

    commitment_status = postgresql.ENUM(*COMMITMENT_STATUS_VALUES, name='commitment_status')
    op.create_table(
        'collaboration_commitments',
        sa.Column('collaboration_id', sa.Uuid(), nullable=False),
        sa.Column('type', postgresql.ENUM(*COLLABORATION_TYPE_VALUES, name='collaboration_type', create_type=False), nullable=False),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', commitment_status, nullable=False),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['collaboration_id'], ['collaborations.id'],
            name=op.f('fk_collaboration_commitments_collaboration_id_collaborations'), ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_collaboration_commitments')),
    )
    op.create_index(
        op.f('ix_collaboration_commitments_collaboration_id'), 'collaboration_commitments',
        ['collaboration_id'], unique=False,
    )

    # --- 6. impact_indicators -----------------------------------------------
    op.create_table(
        'impact_indicators',
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('baseline_value', sa.Float(), nullable=True),
        sa.Column('baseline_date', sa.Date(), nullable=True),
        sa.Column('target_value', sa.Float(), nullable=True),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('endline_date', sa.Date(), nullable=True),
        sa.Column('endline_evidence', sa.Text(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by_id', sa.Uuid(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['project_id'], ['projects.id'], name=op.f('fk_impact_indicators_project_id_projects'), ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['verified_by_id'], ['users.id'],
            name=op.f('fk_impact_indicators_verified_by_id_users'), ondelete='RESTRICT',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_impact_indicators')),
    )
    op.create_index(op.f('ix_impact_indicators_project_id'), 'impact_indicators', ['project_id'], unique=False)
    op.create_index(
        op.f('ix_impact_indicators_verified_by_id'), 'impact_indicators', ['verified_by_id'], unique=False
    )

    # --- 7. solutions: status/outcome/embedding ------------------------------
    solution_status = postgresql.ENUM(*SOLUTION_STATUS_VALUES, name='solution_status')
    solution_status.create(op.get_bind())
    op.add_column('solutions', sa.Column('outcome', sa.Text(), nullable=True))
    op.add_column(
        'solutions', sa.Column('status', solution_status, nullable=False, server_default='draft')
    )
    op.alter_column('solutions', 'status', server_default=None)
    op.add_column('solutions', sa.Column('embedding', Vector(384), nullable=True))
    op.execute(
        "CREATE INDEX ix_solutions_embedding_hnsw ON solutions USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS ix_solutions_embedding_hnsw')
    op.drop_column('solutions', 'embedding')
    op.drop_column('solutions', 'status')
    op.drop_column('solutions', 'outcome')
    op.execute('DROP TYPE solution_status')

    op.drop_index(op.f('ix_impact_indicators_verified_by_id'), table_name='impact_indicators')
    op.drop_index(op.f('ix_impact_indicators_project_id'), table_name='impact_indicators')
    op.drop_table('impact_indicators')

    op.drop_index(op.f('ix_collaboration_commitments_collaboration_id'), table_name='collaboration_commitments')
    op.drop_table('collaboration_commitments')
    op.execute('DROP TYPE commitment_status')

    op.drop_index(op.f('ix_collaborations_project_id'), table_name='collaborations')
    op.drop_index(op.f('ix_collaborations_organization_id'), table_name='collaborations')
    op.drop_table('collaborations')
    op.execute('DROP TYPE collaboration_status')
    op.execute('DROP TYPE collaboration_type')

    op.drop_index(op.f('ix_deliverables_verified_by_id'), table_name='deliverables')
    op.drop_index(op.f('ix_deliverables_project_id'), table_name='deliverables')
    op.drop_table('deliverables')
    op.execute('DROP TYPE deliverable_status')

    op.drop_index(op.f('ix_milestones_project_id'), table_name='milestones')
    op.drop_table('milestones')
    op.execute('DROP TYPE milestone_status')

    op.drop_column('challenges', 'on_behalf_of_phone')
    op.drop_column('challenges', 'on_behalf_of_name')

    status_old = postgresql.ENUM('planned', 'in_progress', 'completed', 'cancelled', name='project_status_old')
    status_old.create(op.get_bind())
    op.add_column('projects', sa.Column('status_old', status_old, nullable=True))
    op.execute(
        """
        UPDATE projects SET status_old = (CASE status::text
            WHEN 'proposed' THEN 'planned'
            WHEN 'accepted' THEN 'planned'
            WHEN 'active' THEN 'in_progress'
            WHEN 'on_hold' THEN 'in_progress'
            ELSE status::text
        END)::project_status_old
        """
    )
    op.alter_column('projects', 'status_old', nullable=False)
    op.drop_column('projects', 'status')
    op.execute('DROP TYPE project_status')
    op.alter_column('projects', 'status_old', new_column_name='status')
    op.execute('ALTER TYPE project_status_old RENAME TO project_status')
