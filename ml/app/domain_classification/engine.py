"""Domain classification: which of 11 civic domains a challenge belongs to.

Loads the trained classifier shipped at ai/artifacts/domain_clf.joblib (trained
offline by ai/models/train_domain.py on the same encoder this service uses for
/api/v1/embeddings, so the vector a caller passes in is directly compatible).

Degrades to a zero-shot fallback — cosine similarity against one hand-written
prototype sentence per domain, using the *production* embedder — if the
artifact is missing or fails to load. This mirrors the documented behaviour in
ml/docs/00masterplan.md: every model is optional at runtime, and a missing
artifact must never turn into a 500.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np

logger = logging.getLogger("app.domain_classification")

ARTIFACTS_DIR = Path(__file__).resolve().parents[2] / "ai" / "artifacts"
DOMAIN_MODEL_PATH = ARTIFACTS_DIR / "domain_clf.joblib"

CONFIDENCE_GATE = 0.55  # below this, the caller must treat the label as "needs review"

# One prototype sentence per domain for the zero-shot fallback. Kept in sync
# with ai/models/train_domain.py:DOMAIN_PROTOTYPES by design — duplicated here
# (rather than imported) so this service never depends on the training-only
# `ai.models` package at import time, which pulls in training-only
# dependencies (pandas) that aren't part of ml/requirements.txt.
DOMAIN_PROTOTYPES: dict[str, str] = {
    "education": "school teacher classroom students learning mid-day meal scholarship admission dropout",
    "healthcare": "hospital clinic doctor nurse medicine vaccine patient health centre ambulance treatment",
    "agriculture": "farmer crop soil irrigation seed fertiliser harvest pest mandi farming land",
    "water": "drinking water hand pump borewell pipeline tap supply well groundwater tank",
    "sanitation": "toilet drain sewage garbage waste cleaning open defecation soak pit sanitation",
    "environment": "pollution forest river tree air quality mining erosion wildlife environmental damage",
    "energy": "electricity power transformer solar street light grid outage voltage connection",
    "urban_infrastructure": "road pothole bridge drainage footpath traffic street municipal building construction",
    "accessibility": "disability wheelchair ramp accessible blind deaf divyang assistive impaired",
    "public_administration": "certificate application office portal government scheme document official record grievance",
    "rural_livelihoods": "employment wages MGNREGA self help group artisan livelihood income cooperative skill",
}


@dataclass
class DomainAlternative:
    domain: str
    confidence: float


@dataclass
class DomainClassification:
    domain: str
    confidence: float
    alternatives: list[DomainAlternative] = field(default_factory=list)
    needs_review: bool = True
    source: str = "zero_shot_fallback"  # "trained" | "zero_shot_fallback"
    model_version: str = "fallback"


@lru_cache
def _load_artifact():
    if not DOMAIN_MODEL_PATH.exists():
        logger.warning("domain_clf_missing path=%s — serving zero-shot fallback", DOMAIN_MODEL_PATH)
        return None
    try:
        import joblib

        return joblib.load(DOMAIN_MODEL_PATH)
    except Exception:
        logger.exception("domain_clf_load_failed path=%s — serving zero-shot fallback", DOMAIN_MODEL_PATH)
        return None


@lru_cache
def _prototype_vectors() -> tuple[list[str], np.ndarray]:
    from app.embeddings.engine import embed_batch

    labels = sorted(DOMAIN_PROTOTYPES)
    vectors = np.asarray(embed_batch([DOMAIN_PROTOTYPES[label] for label in labels]), dtype=np.float32)
    return labels, vectors


def _zero_shot_classify(vector: np.ndarray) -> DomainClassification:
    labels, protos = _prototype_vectors()
    sims = protos @ vector
    order = np.argsort(-sims)
    # Softmax over cosines is a ranking score, not a calibrated probability —
    # `source` reflects that so callers never treat it as one.
    exp = np.exp((sims - sims.max()) * 10)
    probs = exp / exp.sum()
    return DomainClassification(
        domain=labels[order[0]],
        confidence=round(float(probs[order[0]]), 4),
        alternatives=[
            DomainAlternative(domain=labels[i], confidence=round(float(probs[i]), 4)) for i in order[1:4]
        ],
        needs_review=True,  # the degraded path always asks for a human look
        source="zero_shot_fallback",
        model_version="fallback",
    )


def classify_domain(embedding: list[float]) -> DomainClassification:
    """embedding must come from the same encoder as /api/v1/embeddings (384-dim,
    L2-normalised) — the classifier was trained on vectors from that encoder."""
    vector = np.asarray(embedding, dtype=np.float32)
    artifact = _load_artifact()

    if artifact is None:
        return _zero_shot_classify(vector)

    try:
        clf = artifact["model"]
        proba = clf.predict_proba(vector.reshape(1, -1))[0]
        order = np.argsort(-proba)
        top = int(order[0])
        return DomainClassification(
            domain=str(clf.classes_[top]),
            confidence=round(float(proba[top]), 4),
            alternatives=[
                DomainAlternative(domain=str(clf.classes_[i]), confidence=round(float(proba[i]), 4))
                for i in order[1:4]
            ],
            needs_review=bool(proba[top] < CONFIDENCE_GATE),
            source="trained",
            model_version=str(artifact.get("version", "unknown")),
        )
    except Exception:
        # A loadable-but-unusable artifact (e.g. scikit-learn version skew
        # between training time and this image) must degrade exactly like a
        # missing one — never surface as a 500.
        logger.exception("domain_clf_inference_failed — serving zero-shot fallback")
        return _zero_shot_classify(vector)
