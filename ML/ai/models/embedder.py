"""
MODEL 1 of 3 - the shared representation.

This is not "a model we also have". It is THE model: one encoder, one
forward pass per text, five consumers downstream:

    (1) domain classification      -> models/train_domain.py
    (2) field-intensity            -> models/train_field.py
    (3) duplicate search           -> pgvector, via the stored vector
    (4) institution expertise match-> pgvector, via institution_units.embedding
    (5) solution replication search-> pgvector, via solutions.embedding

Consequences of that design worth stating out loud, because they are the
answer to "what is your ML architecture":
  - one model to load, one latency budget, one cache, one thing to debug
  - consumers stay consistent: the vector that decided a challenge's domain
    is the same vector that matches it to a department
  - adding a sixth capability costs a classifier head, not a new model

WHY paraphrase-multilingual-MiniLM-L12-v2
  384 dims, ~470 MB, CPU-only, ~20 ms/doc. The alternative all-MiniLM-L6-v2
  is smaller and faster but English-only. 33% of the domain corpus is Hindi
  and 33% is Hinglish - an English-only encoder would put "हैंडपंप खराब है"
  and "the hand pump is broken" in unrelated regions of the space, and then
  dedup, classification and matching would all silently fail on two thirds
  of real submissions. The multilingual model buys the entire Hindi story
  for ~390 MB and zero extra code.

OFFLINE IS NON-NEGOTIABLE
  Bake the weights into the Docker image and set HF_HUB_OFFLINE=1. A demo
  where .encode() tries to reach huggingface.co over venue wifi is a lost
  competition. Verify with the laptop in airplane mode before judging.
      python -c "from ai.models.embedder import Embedder; Embedder().warm()"

TWO BACKENDS
  SAHYOG_BACKEND=transformer   (default) the real encoder, described above.
  SAHYOG_BACKEND=tfidf         TF-IDF over character n-grams -> TruncatedSVD
                               -> 384 dims. Pure scikit-learn, NO DOWNLOAD.

  The tfidf backend exists for two reasons, and neither is laziness:
    1. It is the emergency fallback. If the venue machine cannot load the
       transformer, one env var keeps the entire pipeline running with
       degraded accuracy instead of a dead demo.
    2. It is the ABLATION BASELINE. "Our classifier gets X" means nothing
       on its own. "Our classifier gets X with the multilingual encoder and
       Y with a bag-of-character-n-grams baseline" is evidence that the
       encoder is doing work. Judges ask this. Have the number ready.

  Character n-grams (3-5) rather than word n-grams because they degrade
  gracefully across scripts: Devanagari, Latin and romanised Hinglish all
  produce usable features without a tokeniser per language. It has no
  cross-lingual alignment at all, though - "handpump" and "चापाकल" share no
  characters - so expect it to lose badly on the Hindi slice specifically.
  That gap IS the argument for the multilingual model.
"""

from __future__ import annotations

import hashlib
import os
import pickle
from pathlib import Path

import numpy as np

MODEL_NAME = os.getenv("SAHYOG_ENCODER", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
BACKEND = os.getenv("SAHYOG_BACKEND", "transformer")     # transformer | tfidf
EMBED_DIM = 384
ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"
CACHE_DIR = ARTIFACTS / "embed_cache"
TFIDF_PATH = ARTIFACTS / "tfidf_encoder.joblib"


class Embedder:
    """Thin wrapper around the encoder with an on-disk cache.

    The cache is not premature optimisation: you will re-run training a
    dozen times while tuning C, and re-encoding 1320 texts each time costs
    ~30 s a run. Keyed by (backend, model name, text) so switching encoders
    can never silently serve stale vectors.
    """

    _model = None   # class-level: load the weights exactly once per process

    def __init__(self, model_name: str = MODEL_NAME, use_cache: bool = True,
                 backend: str = None):
        self.backend = backend or BACKEND
        self.model_name = model_name if self.backend == "transformer" else f"tfidf-svd-{EMBED_DIM}"
        self.use_cache = use_cache
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._cache_path = CACHE_DIR / (
            hashlib.sha256(f"{self.backend}:{self.model_name}".encode()).hexdigest()[:16] + ".pkl")
        self._cache: dict[str, np.ndarray] = {}
        if use_cache and self._cache_path.exists():
            try:
                self._cache = pickle.loads(self._cache_path.read_bytes())
            except Exception:
                self._cache = {}      # corrupt cache is never fatal

    # -- tfidf backend -----------------------------------------------------
    @staticmethod
    def fit_tfidf(corpus: list[str], dim: int = EMBED_DIM, seed: int = 42):
        """Fit the fallback encoder on a corpus and persist it.

        Must be fitted before use, unlike the transformer - so training
        scripts call this once on the TRAINING SPLIT ONLY. Fitting on the
        full corpus would leak test-set vocabulary into the representation
        and inflate the held-out score, which is exactly the mistake this
        codebase is trying not to make.
        """
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import Normalizer
        import joblib

        # char_wb n-grams: script-agnostic, no per-language tokeniser needed
        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                              min_df=2, max_features=60000, sublinear_tf=True)
        n_feats = vec.fit(corpus).transform(corpus[:1]).shape[1]
        svd = TruncatedSVD(n_components=min(dim, max(2, n_feats - 1)), random_state=seed)
        pipe = make_pipeline(vec, svd, Normalizer(copy=False))
        pipe.fit(corpus)
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipe, TFIDF_PATH)
        Embedder._model = None          # force reload
        return pipe

    def _load(self):
        if Embedder._model is None:
            if self.backend == "tfidf":
                import joblib
                if not TFIDF_PATH.exists():
                    raise RuntimeError(
                        f"tfidf backend selected but {TFIDF_PATH} is missing. "
                        "Run a training script first - it calls Embedder.fit_tfidf().")
                Embedder._model = joblib.load(TFIDF_PATH)
            else:
                from sentence_transformers import SentenceTransformer
                Embedder._model = SentenceTransformer(self.model_name)
        return Embedder._model

    def warm(self) -> None:
        """Load weights and run one forward pass. Call at service startup so
        the first real request is not 20 s slow, and so a missing model
        fails at boot rather than mid-demo."""
        self.encode(["warmup"])

    def encode(self, texts: list[str], batch_size: int = 64,
               show_progress: bool = False) -> np.ndarray:
        """Returns (n, 384) float32, L2-NORMALISED.

        normalize_embeddings=True is load-bearing, not a default we kept:
          - cosine similarity becomes a dot product
          - pgvector's <=> behaves predictably
          - the mean of member vectors is a meaningful cluster centroid
        Turn it off and cluster centroids drift toward whichever reports
        happened to be longest.
        """
        missing = [t for t in texts if t not in self._cache] if self.use_cache else texts
        if missing:
            model = self._load()
            if self.backend == "tfidf":
                vecs = np.asarray(model.transform(missing), dtype=np.float32)
                # SVD output can be shorter than EMBED_DIM on a small corpus;
                # right-pad so downstream code can always assume 384.
                if vecs.shape[1] < EMBED_DIM:
                    vecs = np.pad(vecs, ((0, 0), (0, EMBED_DIM - vecs.shape[1])))
            else:
                vecs = model.encode(
                    missing, batch_size=batch_size, convert_to_numpy=True,
                    normalize_embeddings=True, show_progress_bar=show_progress)
            if self.use_cache:
                for t, v in zip(missing, vecs):
                    self._cache[t] = v.astype(np.float32)
                self._flush()
            else:
                return vecs.astype(np.float32)
        return np.vstack([self._cache[t] for t in texts]).astype(np.float32)

    def _flush(self) -> None:
        try:
            self._cache_path.write_bytes(pickle.dumps(self._cache))
        except Exception:
            pass      # cache write failure must never break training

    # -- convenience -------------------------------------------------------
    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]

    @staticmethod
    def cosine(a: np.ndarray, b: np.ndarray) -> float:
        """For NORMALISED vectors only, which is all encode() produces."""
        return float(np.dot(a, b))


_default: Embedder | None = None


def get_embedder() -> Embedder:
    """Process-wide singleton. The FastAPI service calls this at startup."""
    global _default
    if _default is None:
        _default = Embedder()
    return _default


if __name__ == "__main__":
    import time
    e = Embedder()
    t0 = time.time()
    e.warm()
    print(f"model loaded in {time.time()-t0:.1f}s  ({MODEL_NAME})")

    probe = [
        "The hand pump in our village has been broken for three weeks.",
        "हमारे गांव का चापाकल तीन हफ्ते से खराब है।",
        "Handpump kharab hai gaon mein teen hafte se.",
        "The scholarship portal keeps rejecting valid documents.",
    ]
    t0 = time.time()
    V = e.encode(probe, show_progress=False)
    print(f"encoded {len(probe)} texts in {(time.time()-t0)*1000:.0f} ms  shape={V.shape}")
    print(f"L2 norms: {np.round(np.linalg.norm(V, axis=1), 4)}  (must be 1.0)")

    print("\nCROSS-LINGUAL CHECK - the reason we pay for the multilingual model:")
    print(f"  EN vs HI  (same meaning)      {Embedder.cosine(V[0], V[1]):.3f}")
    print(f"  EN vs Hinglish (same meaning) {Embedder.cosine(V[0], V[2]):.3f}")
    print(f"  HI vs Hinglish (same meaning) {Embedder.cosine(V[1], V[2]):.3f}")
    print(f"  EN vs unrelated English       {Embedder.cosine(V[0], V[3]):.3f}   <- must be clearly lower")
