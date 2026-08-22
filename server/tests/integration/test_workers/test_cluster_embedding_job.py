import uuid

import pytest

from app.models.cluster import Cluster
from app.workers.tasks import generate_cluster_embedding


@pytest.mark.asyncio
async def test_cluster_embedding_job_is_idempotent(db):
    cluster = Cluster(title=f"Embedding Job Idempotency Test {uuid.uuid4().hex[:8]}", description="Roads")
    db.add(cluster)
    await db.commit()
    await db.refresh(cluster)
    assert cluster.embedding is None

    await generate_cluster_embedding(None, str(cluster.id))
    await db.refresh(cluster)
    assert cluster.embedding is not None
    assert len(cluster.embedding) == 384

    # Re-running must not error and must not recompute (embedding already present).
    await generate_cluster_embedding(None, str(cluster.id))
    await db.refresh(cluster)
    assert cluster.embedding is not None
    assert len(cluster.embedding) == 384


@pytest.mark.asyncio
async def test_cluster_embedding_job_handles_missing_cluster_gracefully():
    await generate_cluster_embedding(None, str(uuid.uuid4()))  # must not raise
