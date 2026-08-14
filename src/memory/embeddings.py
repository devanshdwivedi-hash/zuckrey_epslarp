import os
import logging
from typing import List, Optional
from config.settings import settings

logger = logging.getLogger("autonomous_agent.memory.embeddings")

_sentence_transformer_model = None

def _get_sentence_transformer():
    """
    Lazy loader for SentenceTransformer model to avoid overhead at import time.
    Suppressed on Vercel serverless environment to prevent cold-start PyTorch memory limit crashes.
    """
    global _sentence_transformer_model
    if "VERCEL" in os.environ:
        return None

    if _sentence_transformer_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local SentenceTransformer model: {settings.EMBEDDING_MODEL}")
            _sentence_transformer_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        except Exception as e:
            logger.warning(f"SentenceTransformer not available or failed to load: {e}")
            _sentence_transformer_model = False
    return _sentence_transformer_model if _sentence_transformer_model is not False else None


def get_embedding(text: str) -> List[float]:
    """
    Generates a vector embedding for the given text input.
    Uses lightweight OpenAI API (text-embedding-3-small) ONLY when a valid OpenAI key (starting with 'sk-') is provided.
    Prevents sending Groq ('gsk_...') or xAI ('xai-') keys to OpenAI API.
    Lazy-loads SentenceTransformers locally, and falls back to deterministic vector for offline environments.
    """
    if not text or not text.strip():
        return [0.0] * 384  # Standard vector dimension

    # 1. Prefer lightweight OpenAI API embedding ONLY if a valid OpenAI key (sk-...) is configured
    openai_key = settings.OPENAI_API_KEY
    if not openai_key or not (openai_key.startswith("sk-") and not openai_key.startswith("gsk-")):
        eff_key = settings.effective_api_key
        if eff_key and eff_key.startswith("sk-") and not eff_key.startswith("gsk-"):
            openai_key = eff_key
        else:
            openai_key = None

    if openai_key and not any(x in openai_key.lower() for x in ["your_", "placeholder", "groq_api_key", "openai_api_key"]):
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return [float(val) for val in response.data[0].embedding]
        except Exception as e:
            logger.warning(f"OpenAI API embedding generation failed: {e}. Trying local fallback.")

    # 2. Try local SentenceTransformers (if available and not on Vercel serverless)
    model = _get_sentence_transformer()
    if model is not None:
        try:
            embedding = model.encode(text, convert_to_numpy=True).tolist()
            return [float(val) for val in embedding]
        except Exception as e:
            logger.warning(f"SentenceTransformer encoding failed: {e}. Trying fallback.")

    # 3. Deterministic fallback embedding for testing / offline environments without models
    import numpy as np
    seed = sum(ord(c) for c in text) % (2**32)
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(384)
    norm_vec = vec / np.linalg.norm(vec)
    return norm_vec.tolist()
