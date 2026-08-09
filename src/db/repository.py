import logging
from typing import List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from src.db.models import PublishedPost, RejectedPost

logger = logging.getLogger("autonomous_agent.db.repository")

def create_published_post(
    db: Session,
    title: str,
    content: str,
    source_url: str,
    selection_reason: str,
    why_relevant_now: str,
    embedding: Optional[List[float]] = None,
    persona_name: Optional[str] = None,
    score: Optional[int] = None,
    source_name: Optional[str] = None,
    sources: Optional[List[str]] = None,
    article_published_at: Optional[Any] = None
) -> PublishedPost:
    """
    Inserts a newly generated, approved post into the published_posts table.
    """
    post = PublishedPost(
        title=title,
        content=content,
        source_url=source_url,
        selection_reason=selection_reason,
        why_relevant_now=why_relevant_now,
        embedding=embedding,
        vector_embedding=embedding,
        persona_name=persona_name,
        score=score,
        source_name=source_name,
        sources=sources or [source_url],
        article_published_at=article_published_at
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    logger.info(f"Saved published post ID {post.id}: '{post.title}'")
    return post


def create_rejected_post(
    db: Session,
    title: str,
    source_url: str,
    rejection_reason: str,
    score: Optional[int] = None,
    source_name: Optional[str] = None
) -> RejectedPost:
    """
    Inserts a rejected topic into the rejected_posts table for evaluation audit.
    """
    rejected = RejectedPost(
        title=title,
        source_url=source_url,
        rejection_reason=rejection_reason,
        score=score,
        source_name=source_name
    )
    db.add(rejected)
    db.commit()
    db.refresh(rejected)
    logger.info(f"Saved rejected topic ID {rejected.id}: '{rejected.title}'")
    return rejected


def get_published_posts(
    db: Session,
    limit: Optional[int] = 50,
    offset: int = 0
) -> List[PublishedPost]:
    """
    Retrieves published posts ordered by newest first.
    """
    query = db.query(PublishedPost).order_by(PublishedPost.created_at.desc(), PublishedPost.id.desc()).offset(offset)
    if limit is not None and limit > 0:
        query = query.limit(limit)
    return query.all()


def get_rejected_posts(
    db: Session,
    limit: int = 50,
    offset: int = 0
) -> List[RejectedPost]:
    """
    Retrieves rejected posts ordered by newest first.
    """
    return (
        db.query(RejectedPost)
        .order_by(RejectedPost.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def is_url_processed(db: Session, url: str) -> bool:
    """
    Checks if a URL has already been processed (published or rejected).
    """
    in_published = db.query(PublishedPost.id).filter(PublishedPost.source_url == url).first() is not None
    if in_published:
        return True
    in_rejected = db.query(RejectedPost.id).filter(RejectedPost.source_url == url).first() is not None
    return in_rejected


def get_all_published_embeddings(db: Session) -> List[Tuple[int, str, List[float]]]:
    """
    Returns (id, source_url, embedding) tuples for all published posts that have vector embeddings.
    """
    results = (
        db.query(PublishedPost.id, PublishedPost.source_url, PublishedPost.embedding)
        .filter(PublishedPost.embedding.isnot(None))
        .all()
    )
    return [(r[0], r[1], r[2]) for r in results if r[2] is not None]
