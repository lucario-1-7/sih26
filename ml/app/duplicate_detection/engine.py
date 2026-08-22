from dataclasses import dataclass

import numpy as np

from app.core.config import get_settings
from app.embeddings.engine import MODEL_VERSION


@dataclass
class EmbeddingRecord:
    id: str
    embedding: list[float]


@dataclass
class DuplicateCandidate:
    id: str
    similarity_score: float
    is_candidate: bool
    model_name: str
    model_version: str


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def find_duplicate_candidates(
    query_embedding: list[float],
    corpus: list[EmbeddingRecord],
    threshold: float | None = None,
) -> list[DuplicateCandidate]:
    """Rank corpus by cosine similarity to the query. Never merges — candidates only.

    A human reviewer makes the final DUPLICATE / NOT_DUPLICATE decision; this
    function only supplies ranked evidence.
    """
    settings = get_settings()
    effective_threshold = threshold if threshold is not None else settings.DEFAULT_DUPLICATE_THRESHOLD
    model_name = settings.ML_MODEL_NAME

    ranked = [
        DuplicateCandidate(
            id=record.id,
            similarity_score=_cosine_similarity(query_embedding, record.embedding),
            is_candidate=False,
            model_name=model_name,
            model_version=MODEL_VERSION,
        )
        for record in corpus
    ]
    ranked.sort(key=lambda c: c.similarity_score, reverse=True)
    for candidate in ranked:
        candidate.is_candidate = candidate.similarity_score >= effective_threshold
    return ranked
