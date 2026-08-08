import logging
from typing import List, Optional
from config.settings import settings

logger = logging.getLogger("autonomous_agent.memory.embeddings")

_sentence_transformer_model = None

def _get_sentence_transformer():
    """
    Lazy loader for SentenceTransformer model to avoid overhead at import time.
    """
    global _sentence_transformer_model
    if _sentence_transformer_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local SentenceTransformer model: {settings.EMBEDDING_MODEL}")
            _sentence_transformer_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            _sentence_transformer_model = False
    return _sentence_transformer_model if _sentence_transformer_model is not False else None


def get_embedding(text: str) -> List[float]:
    """
    Generates a vector embedding for the given text input.
    Tries SentenceTransformers first (local fast inference), then OpenAI API if available,
    and falls back to a deterministic hash-based vector for offline / testing environments.
    """
    if not text or not text.strip():
        return [0.0] * 384  # Standard MiniLM dimension

    # 1. Try local SentenceTransformers
    model = _get_sentence_transformer()
    if model is not None:
        try:
            embedding = model.encode(text, convert_to_numpy=True).tolist()
            return [float(val) for val in embedding]
        except Exception as e:
            logger.warning(f"SentenceTransformer encoding failed: {e}. Trying fallback.")

    # 2. Try OpenAI API if key is present
    api_key = settings.effective_api_key or settings.OPENAI_API_KEY
    if api_key and not any(x in api_key.lower() for x in ["your_", "placeholder", "groq_api_key", "openai_api_key"]):
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return [float(val) for val in response.data[0].embedding]
        except Exception as e:
            logger.warning(f"OpenAI embedding generation failed: {e}")

    # 3. Deterministic fallback embedding for testing without models
    import numpy as np
    seed = sum(ord(c) for c in text) % (2**32)
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(384)
    norm_vec = vec / np.linalg.norm(vec)
    return norm_vec.tolist()
