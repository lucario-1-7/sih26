"""End-to-end proof of the intended ML pipeline against the REAL Docker stack —
real Postgres, real ML FastAPI service, real embedding/domain/field models.
No mocks. This is the acceptance test for:

    grievance -> embedding -> domain classification -> field-intensity
    classification -> duplicate evidence -> [cluster -> matching -> consortium
    suggestion -> human confirmation]

and for the rule that ML output is evidence, never a decision: duplicate
candidates never become a DuplicateDecision by themselves, and a proposed
Consortium never becomes CONFIRMED without an explicit human action.
"""

import uuid

import pytest

from app.models.challenge import Challenge
from app.models.cluster import Cluster
from app.models.enums import OrganizationType
from app.models.organization import Organization
from app.repositories.consortium_repository import ConsortiumRepository
from app.repositories.duplicate_repository import DuplicateRepository
from app.repositories.project_repository import ProjectRepository
from app.services import matching_service
from app.services import ml_client
from app.workers.tasks import generate_consortium_suggestion, generate_duplicate_candidates


@pytest.mark.asyncio
async def test_full_classification_pipeline_runs_against_the_real_ml_service(
    db, administrative_area, citizen_user
):
    challenge = Challenge(
        title="Hand pump broken for three weeks",
        description=(
            "The hand pump in our village has been broken for three weeks and needs a "
            "mechanic to repair the borewell pipe onsite. The water that does come out is reddish."
        ),
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    db.add(challenge)
    await db.commit()
    await db.refresh(challenge)

    await generate_duplicate_candidates(None, str(challenge.id))
    await db.refresh(challenge)

    # -- embedding: real 384-dim MiniLM vector --------------------------------
    assert challenge.embedding is not None
    assert len(challenge.embedding) == 384

    # -- domain classification: real trained classifier -----------------------
    assert challenge.content_domain == "water"
    assert challenge.content_domain_source in ("trained", "zero_shot_fallback")
    assert 0.0 <= challenge.content_domain_confidence <= 1.0
    assert isinstance(challenge.content_domain_needs_review, bool)

    # -- field-intensity classification: real trained classifier, chained on domain
    assert challenge.content_field_label in ("FIELD_HEAVY", "HYBRID", "REMOTE_ANALYTICAL")
    assert 0.0 <= challenge.content_field_intensity <= 1.0
    assert challenge.content_field_source in ("trained", "rules_fallback")
    # A hand-pump repair report onsite is unambiguously physical work.
    assert challenge.content_field_label == "FIELD_HEAVY"

    # -- idempotency: re-running the job must not change or duplicate results -
    domain_before, field_before = challenge.content_domain, challenge.content_field_intensity
    await generate_duplicate_candidates(None, str(challenge.id))
    await db.refresh(challenge)
    assert challenge.content_domain == domain_before
    assert challenge.content_field_intensity == field_before


@pytest.mark.asyncio
async def test_duplicate_evidence_never_becomes_a_decision_by_itself(db, administrative_area, citizen_user):
    original = Challenge(
        title="Streetlight broken near market",
        description="The streetlight outside the main market has not worked for two weeks.",
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    similar = Challenge(
        title="Street light not working near bazaar",
        description="Streetlight close to the bazaar has been out for a couple of weeks now.",
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    db.add_all([original, similar])
    await db.commit()
    await db.refresh(original)
    await db.refresh(similar)

    await generate_duplicate_candidates(None, str(original.id))
    await generate_duplicate_candidates(None, str(similar.id))

    candidates = await DuplicateRepository(db).list_candidates(similar.id)
    # ML produced ranked evidence...
    assert isinstance(candidates, list)
    # ...but no decision exists until a human reviewer explicitly makes one —
    # the worker job itself must never create a DuplicateDecision row.
    decisions = await DuplicateRepository(db).list_decisions(similar.id)
    assert decisions == []


@pytest.mark.asyncio
async def test_consortium_suggestion_with_no_candidates_creates_nothing(db, coordinator_user, monkeypatch):
    # The organizations table is shared, cumulative test state across the whole
    # suite run (other tests/fixtures create real organizations with real
    # embeddings, and nearest-by-embedding always returns *some* top-N result
    # rather than an empty one below a distance floor) — so "zero candidates
    # anywhere in the database" is not a state this test can reliably force by
    # construction. Instead it pins the exact behavior the worker must have
    # when the organization search genuinely comes back empty, by controlling
    # that search directly.
    from app.repositories.organization_repository import OrganizationRepository

    async def _no_candidates(self, *, embedding, type, limit):
        return []

    monkeypatch.setattr(OrganizationRepository, "find_nearest_by_embedding", _no_candidates)

    cluster = Cluster(title=f"Empty-candidate cluster {uuid.uuid4().hex[:8]}", embedding=[0.001] * 384)
    db.add(cluster)
    await db.commit()
    await db.refresh(cluster)

    project = await ProjectRepository(db).create(
        cluster_id=cluster.id, title="Project with no matching orgs", description=None, owner_id=coordinator_user.id
    )
    await db.commit()

    await generate_consortium_suggestion(None, str(project.id), team_size=3)

    consortium = await ConsortiumRepository(db).get_by_project(project.id)
    assert consortium is None


@pytest.mark.asyncio
async def test_consortium_suggestion_and_human_confirmation_are_separate_steps(
    db, coordinator_user, superadmin_user
):
    # Real orgs with real embeddings from the live ML service — this is what
    # makes the matching + consortium stages genuinely exercised, not stubbed.
    org_embedding = await ml_client.embed_text("civil engineering water supply infrastructure")
    orgs = []
    for i, org_type in enumerate([OrganizationType.UNIVERSITY, OrganizationType.UNIVERSITY, OrganizationType.INDUSTRY]):
        org = Organization(
            name=f"Consortium Test Org {i} {uuid.uuid4().hex[:8]}",
            type=org_type,
            domain_tags=["water", "civil-engineering"],
            embedding=org_embedding,
        )
        db.add(org)
        orgs.append(org)
    await db.commit()

    cluster = Cluster(title=f"Water infra cluster {uuid.uuid4().hex[:8]}", embedding=org_embedding)
    db.add(cluster)
    await db.commit()
    await db.refresh(cluster)

    project = await ProjectRepository(db).create(
        cluster_id=cluster.id, title="Village water supply pilot", description=None, owner_id=coordinator_user.id
    )
    await db.commit()

    # -- ML suggests a composition ---------------------------------------------
    await generate_consortium_suggestion(None, str(project.id), team_size=2)

    consortium = await ConsortiumRepository(db).get_by_project(project.id)
    assert consortium is not None
    assert consortium.status.value == "proposed"  # ML's suggestion is not yet a decision

    members = await ConsortiumRepository(db).list_members(consortium.id)
    assert 0 < len(members) <= 2
    for member in members:
        assert member.role  # every member's role is explainable, never blank
        assert member.match_score is not None

    # -- re-running must not duplicate the consortium (idempotent) -------------
    await generate_consortium_suggestion(None, str(project.id), team_size=2)
    consortium_again = await ConsortiumRepository(db).get_by_project(project.id)
    assert consortium_again.id == consortium.id

    # -- confirmation is a distinct, explicit human action ----------------------
    confirmed = await matching_service.confirm_consortium(db, consortium.id, actor_id=superadmin_user.id)
    assert confirmed.status.value == "confirmed"

    # -- cleanup: the organizations table is shared, cumulative state across
    # the whole suite run, and an org with a real (non-degenerate) embedding
    # would otherwise become a "nearest match" for every other test's cluster.
    await db.delete(confirmed)  # cascades to consortium_members
    await db.flush()
    project_row = await ProjectRepository(db).get(project.id)
    await db.delete(project_row)
    await db.flush()
    cluster_row = await db.get(Cluster, cluster.id)
    await db.delete(cluster_row)
    for org in orgs:
        org_row = await db.get(Organization, org.id)
        await db.delete(org_row)
    await db.commit()
