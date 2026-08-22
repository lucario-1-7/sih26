import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cluster import Cluster
from app.models.consortium import Consortium
from app.models.enums import ConsortiumStatus, OrganizationType
from app.models.organization import Organization
from app.repositories.audit_repository import AuditRepository
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.consortium_repository import ConsortiumRepository
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.matching import MatchResult, OrganizationCreate
from app.services import ml_client

CLUSTER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Cluster not found", "code": "NOT_FOUND"}
)
CONSORTIUM_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={"detail": "Consortium not found", "code": "NOT_FOUND"},
)
MATCH_CANDIDATE_LIMIT = 25


async def create_organization(
    db: AsyncSession, *, data: OrganizationCreate, actor_id: uuid.UUID
) -> Organization:
    embedding = await ml_client.embed_text(
        f"{data.name}\n{' '.join(data.domain_tags)}\n{data.description or ''}"
    )
    org = await OrganizationRepository(db).create(
        name=data.name,
        type=data.type,
        domain_tags=data.domain_tags,
        description=data.description,
        embedding=embedding,
    )
    await AuditRepository(db).log(
        user_id=actor_id, action="organization.create", entity_type="organization", entity_id=org.id
    )
    await db.commit()
    return org


async def list_organizations(
    db: AsyncSession, *, type: OrganizationType | None, limit: int, offset: int
) -> list[Organization]:
    return await OrganizationRepository(db).list(type=type, limit=limit, offset=offset)


async def _ensure_cluster_embedding(db: AsyncSession, cluster: Cluster) -> list[float]:
    if cluster.embedding is not None:
        return cluster.embedding
    embedding = await ml_client.embed_text(f"{cluster.title}\n{cluster.description or ''}")
    cluster.embedding = embedding
    await db.commit()
    return embedding


async def rank_matches_for_cluster(
    db: AsyncSession, *, cluster_id: uuid.UUID, org_type: OrganizationType | None
) -> list[MatchResult]:
    cluster = await ClusterRepository(db).get(cluster_id)
    if cluster is None:
        raise CLUSTER_NOT_FOUND

    embedding = await _ensure_cluster_embedding(db, cluster)

    candidates = await OrganizationRepository(db).find_nearest_by_embedding(
        embedding=embedding, type=org_type, limit=MATCH_CANDIDATE_LIMIT
    )
    if not candidates:
        return []

    ranked = await ml_client.rank_matches(
        query_embedding=embedding,
        query_domain_tags=[],
        candidates=[
            {"id": str(c.id), "embedding": c.embedding, "domain_tags": c.domain_tags, "type": c.type.value}
            for c in candidates
        ],
    )
    return [
        MatchResult(
            organization_id=uuid.UUID(item["id"]),
            score=item["score"],
            breakdown=item["breakdown"],
            rationale=item["rationale"],
        )
        for item in ranked
    ]


async def confirm_consortium(db: AsyncSession, consortium_id: uuid.UUID, *, actor_id: uuid.UUID) -> Consortium:
    consortium = await ConsortiumRepository(db).get(consortium_id)
    if consortium is None:
        raise CONSORTIUM_NOT_FOUND
    consortium.status = ConsortiumStatus.CONFIRMED
    await AuditRepository(db).log(
        user_id=actor_id,
        action="consortium.confirm",
        entity_type="consortium",
        entity_id=consortium.id,
    )
    await db.commit()
    return consortium
