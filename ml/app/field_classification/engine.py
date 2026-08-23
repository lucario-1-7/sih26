"""Field-intensity classification: how physical (site visits, repairs, hardware)
vs. remote-analytical (records, portals, policy) a challenge's work is.

Consumed downstream as a continuous [0, 1] number, not a hard label — matching
and dedup both use it as a distance/discount factor, so a middle value (a
"HYBRID" case like telemedicine) must stay meaningfully in the middle rather
than collapsing to an arbitrary side.

Loads the trained classifier shipped at ai/artifacts/field_clf.joblib (trained
by ai/models/train_field.py). The blend weights, label thresholds, and prior
table are read from the artifact bundle itself when it loads — they were
fitted together at training time — with hardcoded copies here used only as
constants for the fallback path, exactly like domain_classification/engine.py.

Degrades to a keyword+domain-prior blend (no trained model) if the artifact is
missing or fails to load, per the same "never a 500" contract.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

logger = logging.getLogger("app.field_classification")

ARTIFACTS_DIR = Path(__file__).resolve().parents[2] / "ai" / "artifacts"
FIELD_MODEL_PATH = ARTIFACTS_DIR / "field_clf.joblib"

LABEL_INTENSITY = {"FIELD_HEAVY": 1.0, "HYBRID": 0.5, "REMOTE_ANALYTICAL": 0.0}
LABEL_CUTS = {"FIELD_HEAVY": 0.66, "HYBRID": 0.40}

# Fallback-path constants only — duplicated from ai/models/train_field.py for
# the same reason DOMAIN_PROTOTYPES is duplicated in domain_classification:
# this service must not import the training-only `ai.models` package.
DOMAIN_FIELD_PRIOR: dict[str, float] = {
    "water": 0.85, "sanitation": 0.85, "urban_infrastructure": 0.90,
    "agriculture": 0.75, "energy": 0.70, "environment": 0.65,
    "healthcare": 0.55, "rural_livelihoods": 0.55, "accessibility": 0.60,
    "education": 0.35, "public_administration": 0.20,
}
DEFAULT_PRIOR = 0.5

FIELD_KEYWORDS = [
    "pump", "pipe", "borewell", "road", "drain", "toilet", "install", "repair",
    "broken", "collapsed", "leak", "machine", "hardware", "transformer",
    "wall", "roof", "bridge", "damaged", "replace", "site", "field", "onsite",
    "मरम्मत", "टूट", "खराब", "चापाकल", "पाइप", "सड़क", "नाली", "शौचालय",
    "गिर", "लगाना", "मौके", "मिस्त्री", "तकनीशियन",
    "kharab", "tut", "toot", "marammat", "lagana", "mistri", "technician",
]
REMOTE_KEYWORDS = [
    "data", "portal", "record", "database", "analyse", "analyze", "analysis",
    "review", "report", "dashboard", "software", "duplicate", "format",
    "scheme", "certificate", "statistics", "audit", "reconcile", "policy",
    "आंकड़", "डेटा", "पोर्टल", "समीक्षा", "विश्लेषण", "रिपोर्ट", "विसंगति",
    "अभिलेख", "सूची", "प्रणाली",
    "evaluate", "records", "logs",
]

FALLBACK_BLEND = {"model": 0.0, "keyword": 0.5, "prior": 0.5}


@dataclass
class FieldClassification:
    field_intensity: float
    label: str  # "FIELD_HEAVY" | "HYBRID" | "REMOTE_ANALYTICAL"
    needs_review: bool
    source: str  # "trained" | "rules_fallback"
    model_version: str


def keyword_ratio(text: str) -> float:
    t = text.lower()
    f = sum(1 for k in FIELD_KEYWORDS if k in t)
    r = sum(1 for k in REMOTE_KEYWORDS if k in t)
    if f + r == 0:
        return 0.5  # no lexical evidence -> neutral, not zero
    return f / (f + r)


def _to_label(field_intensity: float, cuts: dict[str, float] = LABEL_CUTS) -> str:
    if field_intensity >= cuts["FIELD_HEAVY"]:
        return "FIELD_HEAVY"
    if field_intensity >= cuts["HYBRID"]:
        return "HYBRID"
    return "REMOTE_ANALYTICAL"


@lru_cache
def _load_artifact():
    if not FIELD_MODEL_PATH.exists():
        logger.warning("field_clf_missing path=%s — serving rules-based fallback", FIELD_MODEL_PATH)
        return None
    try:
        import joblib

        return joblib.load(FIELD_MODEL_PATH)
    except Exception:
        logger.exception("field_clf_load_failed path=%s — serving rules-based fallback", FIELD_MODEL_PATH)
        return None


def classify_field_intensity(text: str, domain: str, embedding: list[float]) -> FieldClassification:
    """embedding must come from the same encoder as /api/v1/embeddings — the
    classifier was trained on vectors from that encoder. `domain` should be
    the (possibly fallback) result of classify_domain: the prior is chained
    from it exactly as the training script evaluates the pipeline."""
    prior = DOMAIN_FIELD_PRIOR.get(domain, DEFAULT_PRIOR)
    kw = keyword_ratio(text)
    artifact = _load_artifact()

    if artifact is not None:
        try:
            vector = np.asarray(embedding, dtype=np.float32)
            clf = artifact["model"]
            proba = clf.predict_proba(vector.reshape(1, -1))[0]
            label_intensity = artifact.get("label_intensity", LABEL_INTENSITY)
            model_p = float(sum(p * label_intensity[c] for p, c in zip(proba, clf.classes_)))
            blend_w = artifact.get("blend", {"model": 0.9, "keyword": 0.05, "prior": 0.05})
            cuts = artifact.get("label_cuts", LABEL_CUTS)
            fi = float(
                np.clip(blend_w["model"] * model_p + blend_w["keyword"] * kw + blend_w["prior"] * prior, 0.0, 1.0)
            )
            return FieldClassification(
                field_intensity=round(fi, 4),
                label=_to_label(fi, cuts),
                needs_review=False,
                source="trained",
                model_version=str(artifact.get("version", "unknown")),
            )
        except Exception:
            # A loadable-but-unusable artifact (e.g. scikit-learn version skew)
            # must degrade exactly like a missing one — never surface as a 500,
            # and never let a partially-trained value pass as "trained".
            logger.exception("field_clf_inference_failed — serving rules-based fallback")

    fi = float(
        np.clip(
            FALLBACK_BLEND["model"] * 0.0 + FALLBACK_BLEND["keyword"] * kw + FALLBACK_BLEND["prior"] * prior,
            0.0,
            1.0,
        )
    )
    return FieldClassification(
        field_intensity=round(fi, 4),
        label=_to_label(fi),
        needs_review=True,
        source="rules_fallback",
        model_version="fallback",
    )
