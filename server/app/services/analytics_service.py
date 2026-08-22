"""Superadmin platform analytics — plain aggregate queries against the
existing tables. No warehouse, no pre-computed rollups: at this project's
data volume, indexed COUNT/GROUP BY queries are fast enough, and adding a
materialized layer now would be premature.
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.administrative_area import AdministrativeArea
from app.models.challenge import Challenge
from app.models.cluster import Cluster
from app.models.collaboration import Collaboration, CollaborationCommitment
from app.models.duplicate import DuplicateCandidate, DuplicateDecision
from app.models.enums import OrganizationType
from app.models.organization import Organization
from app.models.project import Project
from app.models.solution import Solution
from app.schemas.analytics import ChallengeAnalytics, IndustryAnalytics, MLAnalytics, ModelInfo, ProjectAnalytics

ML_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = 384


async def _count_by(db: AsyncSession, column) -> dict[str, int]:
    stmt = select(column, func.count()).group_by(column)
    result = await db.execute(stmt)
    return {(str(key) if key is not None else "unset"): count for key, count in result.all()}


async def get_challenge_analytics(db: AsyncSession) -> ChallengeAnalytics:
    total = (await db.execute(select(func.count()).select_from(Challenge))).scalar_one()
    by_status = await _count_by(db, Challenge.status)
    by_severity = await _count_by(db, Challenge.severity)

    area_stmt = (
        select(AdministrativeArea.name, func.count(Challenge.id))
        .join(Challenge, Challenge.administrative_area_id == AdministrativeArea.id)
        .group_by(AdministrativeArea.name)
    )
    by_area = {name: count for name, count in (await db.execute(area_stmt)).all()}

    return ChallengeAnalytics(
        total=total, by_status=by_status, by_severity=by_severity, by_administrative_area=by_area
    )


async def get_project_analytics(db: AsyncSession) -> ProjectAnalytics:
    total = (await db.execute(select(func.count()).select_from(Project))).scalar_one()
    by_status = await _count_by(db, Project.status)

    org_stmt = (
        select(Organization.name, func.count(Project.id))
        .join(Organization, Project.organization_id == Organization.id)
        .group_by(Organization.name)
    )
    by_org = {name: count for name, count in (await db.execute(org_stmt)).all()}

    return ProjectAnalytics(total=total, by_status=by_status, by_organization=by_org)


async def get_industry_analytics(db: AsyncSession) -> IndustryAnalytics:
    org_count = (
        await db.execute(
            select(func.count()).select_from(Organization).where(Organization.type == OrganizationType.INDUSTRY)
        )
    ).scalar_one()
    collab_count = (await db.execute(select(func.count()).select_from(Collaboration))).scalar_one()
    collab_by_status = await _count_by(db, Collaboration.status)
    commit_by_status = await _count_by(db, CollaborationCommitment.status)
    commit_by_type = await _count_by(db, CollaborationCommitment.type)

    funding_stmt = (
        select(CollaborationCommitment.currency, func.coalesce(func.sum(CollaborationCommitment.amount), 0.0))
        .where(CollaborationCommitment.amount.is_not(None))
        .group_by(CollaborationCommitment.currency)
    )
    funding = {
        (currency or "unspecified"): float(total) for currency, total in (await db.execute(funding_stmt)).all()
    }

    return IndustryAnalytics(
        organization_count=org_count,
        collaboration_count=collab_count,
        collaborations_by_status=collab_by_status,
        commitments_by_status=commit_by_status,
        commitments_by_type=commit_by_type,
        funding_committed_by_currency=funding,
    )


async def get_ml_analytics(db: AsyncSession) -> MLAnalytics:
    challenges_embedded = (
        await db.execute(select(func.count()).select_from(Challenge).where(Challenge.embedding.is_not(None)))
    ).scalar_one()
    clusters_embedded = (
        await db.execute(select(func.count()).select_from(Cluster).where(Cluster.embedding.is_not(None)))
    ).scalar_one()
    solutions_embedded = (
        await db.execute(select(func.count()).select_from(Solution).where(Solution.embedding.is_not(None)))
    ).scalar_one()
    candidates_total = (await db.execute(select(func.count()).select_from(DuplicateCandidate))).scalar_one()
    decisions_total = (await db.execute(select(func.count()).select_from(DuplicateDecision))).scalar_one()
    decisions_by_type = await _count_by(db, DuplicateDecision.decision)

    return MLAnalytics(
        challenges_with_embedding=challenges_embedded,
        clusters_with_embedding=clusters_embedded,
        solutions_with_embedding=solutions_embedded,
        duplicate_candidates_generated=candidates_total,
        duplicate_decisions_total=decisions_total,
        duplicate_decisions_by_type=decisions_by_type,
    )


def get_model_info() -> ModelInfo:
    settings = get_settings()
    return ModelInfo(
        model_name=ML_MODEL_NAME,
        embedding_dimension=EMBEDDING_DIMENSION,
        duplicate_similarity_threshold=settings.DUPLICATE_SIMILARITY_THRESHOLD,
        duplicate_candidate_limit=settings.DUPLICATE_CANDIDATE_LIMIT,
        ml_service_url=settings.ML_SERVICE_URL,
    )
