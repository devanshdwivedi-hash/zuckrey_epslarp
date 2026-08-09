import logging
from typing import List
import numpy as np

logger = logging.getLogger("autonomous_agent.memory.deduplicator")

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Computes the cosine similarity between two 1D vector arrays.
    """
    arr1 = np.array(v1, dtype=float)
    arr2 = np.array(v2, dtype=float)
    
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return float(np.dot(arr1, arr2) / (norm1 * norm2))


def is_duplicate(
    candidate_vector: List[float], 
    published_vectors: List[List[float]], 
    threshold: float = 0.88
) -> bool:
    """
    Determines if candidate_vector is semantically similar to any vector in published_vectors.
    Returns True if any cosine similarity score >= threshold, otherwise False.
    """
    if not candidate_vector or not published_vectors:
        return False

    cand_norm = np.array(candidate_vector, dtype=float)
    cand_magnitude = np.linalg.norm(cand_norm)
    if cand_magnitude == 0:
        return False

    for idx, pub_vec in enumerate(published_vectors):
        if not pub_vec:
            continue
        sim = cosine_similarity(candidate_vector, pub_vec)
        if sim >= threshold:
            logger.info(f"Duplicate detected! Similarity score {sim:.4f} exceeds threshold {threshold}.")
            return True

    return False
