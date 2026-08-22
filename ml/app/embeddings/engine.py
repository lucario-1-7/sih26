from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

MODEL_VERSION = "1"  # bump when the model or preprocessing changes; historical scores stay valid.


@lru_cache
def _model() -> SentenceTransformer:
    return SentenceTransformer(get_settings().ML_MODEL_NAME)


def embed(text: str) -> list[float]:
    """Encode text into a fixed-dimension multilingual sentence embedding."""
    vector = _model().encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    vectors = _model().encode(texts, normalize_embeddings=True)
    return vectors.tolist()
