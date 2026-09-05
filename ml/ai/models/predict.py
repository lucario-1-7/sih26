"""
INFERENCE - all three models behind one call.

This is the body of `POST /ai/analyze`, the single endpoint Express calls
on every submission. It is the place where the "one embedding, five
consumers" claim either is or is not true, so read the order of operations:

    text
      |
      +-- normalise
      |
      +-- embed  ..................... ONE forward pass, ~20 ms   [MODEL 1]
             |
             +-- domain classifier  ... < 1 ms                    [MODEL 2]
             |      |
             |      +-- domain -> field prior --+
             |                                  |
             +-- field classifier  .... < 1 ms  +--> blend        [MODEL 3]
             |
             +-- capability extraction  ~2 ms   (cosine vs taxonomy)
             |
             +-- returned to Express, stored in challenges.embedding,
                 then reused by pgvector for dedup / matching / replication

The embedding is computed once and never recomputed. Everything after it is
linear algebra on a 384-vector. That is why the whole call is ~90 ms and can
run synchronously inside POST /challenges.

DEGRADATION IS PART OF THE CONTRACT
  Every model is optional at runtime. Missing or unloadable artifact ->
  documented fallback, never a 500:
      domain    -> zero-shot prototype cosine  (same embedding, no artifact)
      field     -> domain prior + keyword ratio only
      capability-> cosine against taxonomy descriptions (never needs training)
  A demo that shows a slightly worse answer beats a demo that shows a stack
  trace, and Express additionally circuit-breaks this whole service after a
  2 s timeout.

Run standalone:
    python ai/models/predict.py                      # demo on sample texts
    SOCIOSOLVE_BACKEND=tfidf python ai/models/predict.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ai.models.dataprep import normalise                 # noqa: E402
from ai.models.embedder import get_embedder              # noqa: E402
from ai.models.train_domain import DOMAIN_PROTOTYPES     # noqa: E402
from ai.models.train_field import (                      # noqa: E402
    DEFAULT_PRIOR, DOMAIN_FIELD_PRIOR, LABEL_CUTS, LABEL_INTENSITY,
    expected_intensity, keyword_ratio,
)

ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"
SEED_DIR = Path(__file__).resolve().parent.parent.parent / "seed"

CONFIDENCE_GATE = 0.55
CAPABILITY_THRESHOLD = 0.28     # cosine above which a capability is "required"
MAX_CAPABILITIES = 8


class Analyzer:
    """Loads once, serves many. FastAPI holds a single instance."""

    def __init__(self):
        self.embedder = get_embedder()
        self.domain = self._load("domain_clf.joblib")
        self.field = self._load("field_clf.joblib")
        self._proto_vecs = None
        self._cap_codes: list[str] = []
        self._cap_labels: dict[str, str] = {}
        self._cap_vecs = None
        self._load_taxonomy()

    @staticmethod
    def _load(name):
        import joblib
        p = ARTIFACTS / name
        if not p.exists():
            print(f"  [warn] {name} missing - falling back", file=sys.stderr)
            return None
        try:
            return joblib.load(p)
        except Exception as e:
            print(f"  [warn] {name} failed to load ({e}) - falling back", file=sys.stderr)
            return None

    def _load_taxonomy(self):
        """Capability descriptions are embedded once at startup. The taxonomy
        is 30 static rows in seed/, deliberately NOT a database table - see
        docs/schema-ml.sql."""
        path = SEED_DIR / "capability_taxonomy.json"
        if not path.exists():
            return
        caps = json.loads(path.read_text())["capabilities"]
        self._cap_codes = [c["code"] for c in caps]
        self._cap_labels = {c["code"]: c["label"] for c in caps}
        # label + description together: the label alone is too short to embed
        # into a useful region of the space.
        self._cap_vecs = self.embedder.encode(
            [f"{c['label']}. {c['desc']}" for c in caps])

    # -- model 2 -----------------------------------------------------------
    def _classify_domain(self, vec):
        if self.domain is not None:
            clf = self.domain["model"]
            proba = clf.predict_proba(vec.reshape(1, -1))[0]
            order = np.argsort(-proba)
            return {
                "domain": str(clf.classes_[order[0]]),
                "confidence": round(float(proba[order[0]]), 4),
                "alternatives": [
                    {"domain": str(clf.classes_[i]), "confidence": round(float(proba[i]), 4)}
                    for i in order[1:4]],
                "needs_review": bool(proba[order[0]] < CONFIDENCE_GATE),
                "source": "trained",
            }
        # fallback: zero-shot prototypes, same embedding, no artifact needed
        labels = sorted(DOMAIN_PROTOTYPES)
        if self._proto_vecs is None:
            self._proto_vecs = self.embedder.encode([DOMAIN_PROTOTYPES[l] for l in labels])
        sims = self._proto_vecs @ vec
        order = np.argsort(-sims)
        # softmax over cosines is NOT a probability - temperature 10 keeps it
        # in a sane range, but the value is a ranking score. `source` says so.
        e = np.exp((sims - sims.max()) * 10)
        p = e / e.sum()
        return {
            "domain": labels[order[0]],
            "confidence": round(float(p[order[0]]), 4),
            "alternatives": [{"domain": labels[i], "confidence": round(float(p[i]), 4)}
                             for i in order[1:4]],
            "needs_review": True,      # always flag: this path is degraded
            "source": "zero_shot_fallback",
        }

    # -- model 3 -----------------------------------------------------------
    def _field_intensity(self, vec, text, domain):
        prior = DOMAIN_FIELD_PRIOR.get(domain, DEFAULT_PRIOR)
        kw, f_hits, r_hits = keyword_ratio(text)

        if self.field is not None:
            clf = self.field["model"]
            blend_w = self.field.get("blend", {"model": 0.9, "keyword": 0.05, "prior": 0.05})
            proba = clf.predict_proba(vec.reshape(1, -1))[0]
            model_p = expected_intensity(proba, clf.classes_)
            source = "trained"
        else:
            # no classifier: prior and lexical signal only, reweighted to sum to 1
            blend_w = {"model": 0.0, "keyword": 0.5, "prior": 0.5}
            model_p, source = 0.0, "rules_fallback"

        fi = float(np.clip(blend_w["model"] * model_p
                           + blend_w["keyword"] * kw
                           + blend_w["prior"] * prior, 0.0, 1.0))
        label = ("FIELD_HEAVY" if fi >= LABEL_CUTS["FIELD_HEAVY"]
                 else "HYBRID" if fi >= LABEL_CUTS["HYBRID"]
                 else "REMOTE_ANALYTICAL")
        return {
            "field_intensity": round(fi, 3),
            "label": label,
            "source": source,
            "signals": {"model": round(model_p, 3), "keyword_ratio": round(kw, 3),
                        "domain_prior": prior, "field_hits": f_hits, "remote_hits": r_hits},
            "explanation": (
                f"Classified {label} (field intensity {fi:.2f}): domain '{domain}' carries a "
                f"{prior:.2f} field prior and the report contains {f_hits} physical-work "
                f"indicator(s) against {r_hits} analytical indicator(s)."),
        }

    # -- capability extraction --------------------------------------------
    def _capabilities(self, vec):
        """Multi-label zero-shot over the 30-code taxonomy. No training data
        exists for this and none is needed: it is cosine against capability
        descriptions in the shared space. Criticality is the rescaled
        similarity, so it degrades gracefully rather than snapping to 1.

        *** THIS IS THE ONE COMPONENT THAT REQUIRES THE TRANSFORMER. ***
        Domain and field-intensity have trained classifiers and survive on
        the tfidf backend. Capability extraction has no classifier - it is
        pure semantic similarity between a citizen's phrasing ("hand pumps
        keep breaking down") and an abstract capability description ("Civil /
        hydrology / groundwater"). Those share almost no CHARACTERS, so
        char-n-gram vectors put them nowhere near each other. Measured on the
        tfidf backend it returns ORG_INCUBATION and EQ_GIS_RS for a hand-pump
        report, and nothing at all for Hindi.

        So: the tfidf fallback keeps the demo alive, but the CONSORTIUM
        BUILDER runs on these capability codes, and garbage codes produce a
        garbage team. If you are running degraded, fall back to the
        domain->capability lookup table rather than shipping these numbers.
        """
        if self._cap_vecs is None or not len(self._cap_codes):
            return []
        if self.embedder.backend != "transformer":
            # Refuse rather than emit plausible-looking nonsense into the
            # consortium builder. An empty list is a visible failure; a wrong
            # capability list is an invisible one.
            return []
        sims = self._cap_vecs @ vec
        out = []
        for i in np.argsort(-sims)[:MAX_CAPABILITIES]:
            s = float(sims[i])
            if s < CAPABILITY_THRESHOLD:
                break
            out.append({
                "code": self._cap_codes[i],
                "label": self._cap_labels[self._cap_codes[i]],
                "criticality": round(min(1.0, (s - CAPABILITY_THRESHOLD) / 0.45 + 0.5), 2),
                "similarity": round(s, 3),
                "source": "AI",
            })
        return out

    # -- the endpoint ------------------------------------------------------
    def analyze(self, text: str, language: str = "auto") -> dict:
        t0 = time.time()
        clean = normalise(text)
        vec = self.embedder.encode_one(clean)

        dom = self._classify_domain(vec)
        fi = self._field_intensity(vec, clean, dom["domain"])
        caps = self._capabilities(vec)

        return {
            "embedding": [round(float(x), 6) for x in vec],   # Express stores this
            "domain": dom["domain"],
            "domain_confidence": dom["confidence"],
            "domain_alternatives": dom["alternatives"],
            "domain_needs_review": dom["needs_review"],
            "field_intensity": fi["field_intensity"],
            "field_label": fi["label"],
            "field_explanation": fi["explanation"],
            "field_signals": fi["signals"],
            "required_capabilities": caps,
            "ai_meta": {
                "model_version": (self.domain or {}).get("version", "fallback"),
                "field_version": (self.field or {}).get("version", "fallback"),
                "encoder": self.embedder.model_name,
                "backend": self.embedder.backend,
                "domain_source": dom["source"],
                "field_source": fi["source"],
                "inference_ms": round((time.time() - t0) * 1000, 1),
            },
        }


_analyzer: Analyzer | None = None


def get_analyzer() -> Analyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = Analyzer()
    return _analyzer


if __name__ == "__main__":
    a = get_analyzer()
    a.analyze("warmup")     # exclude cold start from the timings below

    samples = [
        ("Hand pumps in our village keep breaking down and stay out of order for weeks. "
         "The water that does come out is reddish and leaves iron stains.", "en"),
        ("गाँव के हैंडपंप बार-बार खराब हो जाते हैं और हफ्तों तक ठीक नहीं होते। जो पानी आता है वह लाल है।", "hi"),
        ("Scholarship portal baar baar valid documents reject kar raha hai, "
         "server side error lagta hai.", "hinglish"),
    ]
    for text, lang in samples:
        r = a.analyze(text, lang)
        print("=" * 74)
        print(f"[{lang}] {text[:68]}...")
        print(f"  domain          {r['domain']}  ({r['domain_confidence']:.2f})"
              f"{'  NEEDS REVIEW' if r['domain_needs_review'] else ''}")
        print(f"  alternatives    " + ", ".join(
            f"{x['domain']} {x['confidence']:.2f}" for x in r['domain_alternatives']))
        print(f"  field           {r['field_label']}  ({r['field_intensity']})")
        print(f"  capabilities    " + ", ".join(
            f"{c['code']}({c['criticality']})" for c in r['required_capabilities'][:5]))
        print(f"  timing          {r['ai_meta']['inference_ms']} ms   "
              f"[{r['ai_meta']['domain_source']} / {r['ai_meta']['field_source']}]")
