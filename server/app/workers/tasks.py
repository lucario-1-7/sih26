import logging
import uuid

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.models.enums import ChallengeStatus, OrganizationType
from app.repositories.audit_repository import AuditRepository
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.consortium_repository import ConsortiumRepository
from app.repositories.duplicate_repository import DuplicateRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.project_repository import ProjectRepository
from app.services import ml_client

logger = logging.getLogger("app.workers")


async def generate_duplicate_candidates(ctx, challenge_id: str) -> None:
    """Idempotent: safe to run twice for the same challenge_id.

    Embedding computation is skipped if already present; candidate rows are
    de-duplicated via the (challenge_id, candidate_challenge_id) unique constraint.
    """
    settings = get_settings()
    cid = uuid.UUID(challenge_id)

    async with AsyncSessionLocal() as db:
        async with db.begin():
            challenge_repo = ChallengeRepository(db)
            challenge = await challenge_repo.get(cid)
            if challenge is None:
                logger.info("duplicate_job_skipped_missing_challenge challenge_id=%s", challenge_id)
                return

            if challenge.embedding is None:
                embedding = await ml_client.embed_text(f"{challenge.title}\n{challenge.description}")
                challenge.embedding = embedding
            else:
                embedding = challenge.embedding

            if challenge.content_domain is None:
                classification = await ml_client.classify_domain(embedding)
                challenge.content_domain = classification["domain"]
                challenge.content_domain_confidence = classification["confidence"]
                challenge.content_domain_needs_review = classification["needs_review"]
                challenge.content_domain_source = classification["source"]

            if challenge.content_field_intensity is None:
                # Chains the (possibly fallback) domain result as the prior,
                # exactly as ai/models/train_field.py evaluates the pipeline.
                field = await ml_client.classify_field_intensity(
                    f"{challenge.title}\n{challenge.description}", challenge.content_domain, embedding
                )
                challenge.content_field_intensity = field["field_intensity"]
                challenge.content_field_label = field["label"]
                challenge.content_field_needs_review = field["needs_review"]
                challenge.content_field_source = field["source"]

            neighbors = await challenge_repo.find_nearest_by_embedding(
                embedding=embedding, exclude_id=challenge.id, limit=settings.DUPLICATE_CANDIDATE_LIMIT
            )

            ranked = []
            if neighbors:
                ranked = await ml_client.rank_duplicate_candidates(
                    query_embedding=embedding,
                    candidates=[{"id": str(n.id), "embedding": n.embedding} for n in neighbors],
                    threshold=settings.DUPLICATE_SIMILARITY_THRESHOLD,
                )

            dup_repo = DuplicateRepository(db)
            has_candidates = False
            for item in ranked:
                if not item["is_candidate"]:
                    continue
                has_candidates = True
                existing = await dup_repo.get_candidate(challenge.id, uuid.UUID(item["id"]))
                if existing is not None:
                    continue
                await dup_repo.create_candidate(
                    challenge_id=challenge.id,
                    candidate_challenge_id=uuid.UUID(item["id"]),
                    similarity_score=item["similarity_score"],
                    model_name=item["model_name"],
                    model_version=item["model_version"],
                )

            if not has_candidates and challenge.status == ChallengeStatus.SUBMITTED:
                challenge.status = ChallengeStatus.OPEN

            await AuditRepository(db).log(
                user_id=None,
                action="challenge.duplicate_candidates_generated",
                entity_type="challenge",
                entity_id=challenge.id,
                meta={"candidate_count": sum(1 for i in ranked if i["is_candidate"])},
            )


async def generate_cluster_embedding(ctx, cluster_id: str) -> None:
    """Idempotent: skips computation if the cluster already has an embedding.

    Runs after cluster create/update so `GET /matching/clusters/{id}` never has
    to compute-and-persist an embedding as a side effect of a read.
    """
    cid = uuid.UUID(cluster_id)

    async with AsyncSessionLocal() as db:
        async with db.begin():
            cluster_repo = ClusterRepository(db)
            cluster = await cluster_repo.get(cid)
            if cluster is None:
                logger.info("cluster_embedding_job_skipped_missing_cluster cluster_id=%s", cluster_id)
                return

            if cluster.embedding is not None:
                logger.info("cluster_embedding_job_skipped_already_present cluster_id=%s", cluster_id)
                return

            cluster.embedding = await ml_client.embed_text(f"{cluster.title}\n{cluster.description or ''}")

            await AuditRepository(db).log(
                user_id=None,
                action="cluster.embedding_generated",
                entity_type="cluster",
                entity_id=cluster.id,
            )


async def generate_consortium_suggestion(ctx, project_id: str, team_size: int) -> None:
    """Idempotent: if a consortium already exists for this project, does nothing."""
    pid = uuid.UUID(project_id)

    async with AsyncSessionLocal() as db:
        async with db.begin():
            project_repo = ProjectRepository(db)
            project = await project_repo.get(pid)
            if project is None:
                logger.info("consortium_job_skipped_missing_project project_id=%s", project_id)
                return

            consortium_repo = ConsortiumRepository(db)
            existing = await consortium_repo.get_by_project(pid)
            if existing is not None:
                logger.info("consortium_job_skipped_already_exists project_id=%s", project_id)
                return

            cluster = await ClusterRepository(db).get(project.cluster_id)
            if cluster is None:
                return

            if cluster.embedding is None:
                cluster.embedding = await ml_client.embed_text(f"{cluster.title}\n{cluster.description or ''}")
            embedding = cluster.embedding

            org_repo = OrganizationRepository(db)
            candidates = []
            for org_type in (OrganizationType.UNIVERSITY, OrganizationType.INDUSTRY):
                candidates.extend(
                    await org_repo.find_nearest_by_embedding(embedding=embedding, type=org_type, limit=15)
                )
            if not candidates:
                logger.info("consortium_job_no_candidates project_id=%s", project_id)
                return

            ranked = await ml_client.rank_matches(
                query_embedding=embedding,
                query_domain_tags=[],
                candidates=[
                    {"id": str(c.id), "embedding": c.embedding, "domain_tags": c.domain_tags, "type": c.type.value}
                    for c in candidates
                ],
            )

            suggested_members = await ml_client.suggest_consortium(
                ranked_matches=ranked, team_size=team_size
            )

            consortium = await consortium_repo.create(project_id=pid)
            for member in suggested_members:
                await consortium_repo.add_member(
                    consortium_id=consortium.id,
                    organization_id=uuid.UUID(member["organization_id"]),
                    role=member["role"],
                    match_score=member["score"],
                    rationale=member["rationale"],
                )

            await AuditRepository(db).log(
                user_id=None,
                action="consortium.propose",
                entity_type="consortium",
                entity_id=consortium.id,
                meta={"project_id": project_id, "member_count": len(suggested_members)},
            )
