from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from src.db.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class ModelQueryProxy:
    def __get__(self, instance, owner):
        from src.db.database import SessionLocal
        return SessionLocal().query(owner)


class PublishedPost(Base):
    """
    SQLAlchemy model representing approved and published technical posts.
    Stored in table: published_posts
    """
    __tablename__ = "published_posts"
    query = ModelQueryProxy()

    id               = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at       = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Backward-compat alias so existing repository.py refs to .timestamp still resolve
    timestamp        = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    title            = Column(String(512), nullable=True)
    content          = Column(Text, nullable=False)
    selection_reason = Column(Text, nullable=False)
    why_relevant_now = Column(Text, nullable=True)
    sources          = Column(JSON, nullable=True)   # List[str] of source URLs

    # Embedding stored as JSON float array
    vector_embedding = Column(JSON, nullable=True)

    # Backward-compat alias: repository.py uses .embedding
    embedding        = Column(JSON, nullable=True)

    # Original article publication date
    article_published_at = Column(DateTime(timezone=True), default=utc_now, nullable=True)

    # Optional metadata
    source_url       = Column(String(1024), nullable=True, index=True)
    source_name      = Column(String(256), nullable=True)
    persona_name     = Column(String(256), nullable=True)
    score            = Column(Integer, nullable=True)

    def __init__(self, **kwargs):
        content = kwargs.get("content", "")
        if "title" not in kwargs or not kwargs["title"]:
            kwargs["title"] = content.split("\n")[0][:250] if content else "Technical Briefing"

        if "why_relevant_now" not in kwargs or not kwargs["why_relevant_now"]:
            kwargs["why_relevant_now"] = kwargs.get("selection_reason", "Critical security vulnerability update.")

        sources = kwargs.get("sources")
        if isinstance(sources, str):
            kwargs["sources"] = [sources]
            if "source_url" not in kwargs or not kwargs["source_url"]:
                kwargs["source_url"] = sources
        elif isinstance(sources, list) and sources:
            if "source_url" not in kwargs or not kwargs["source_url"]:
                kwargs["source_url"] = sources[0]

        now = utc_now()
        if "created_at" not in kwargs:
            kwargs["created_at"] = now
        if "timestamp" not in kwargs:
            kwargs["timestamp"] = now
        if "article_published_at" not in kwargs:
            kwargs["article_published_at"] = now

        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id":                   self.id,
            "created_at":           self.created_at.isoformat() if self.created_at else None,
            "timestamp":            self.timestamp.isoformat() if self.timestamp else None,
            "article_published_at": self.article_published_at.isoformat() if self.article_published_at else None,
            "title":                self.title,
            "content":              self.content,
            "selection_reason":     self.selection_reason,
            "why_relevant_now":     self.why_relevant_now,
            "sources":              self.sources or ([self.source_url] if self.source_url else []),
            "vector_embedding":     self.vector_embedding,
            "embedding":            self.embedding,
            "source_url":           self.source_url,
            "source_name":          self.source_name,
            "persona_name":         self.persona_name,
            "score":                self.score,
        }


# Alias for backward compatibility & prompt instruction compliance
Post = PublishedPost


class RejectedPost(Base):
    """
    SQLAlchemy model representing topics filtered out by the LLM Editor-in-Chief.
    Stored in table: rejected_posts (for inspection & verifying high rejection criteria).
    """
    __tablename__ = "rejected_posts"
    query = ModelQueryProxy()

    id               = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at       = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Backward-compat alias
    timestamp        = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    title            = Column(String(512), nullable=False)
    rejection_reason = Column(Text, nullable=False)
    score            = Column(Integer, nullable=True)

    # Optional metadata
    source_url       = Column(String(1024), nullable=True, index=True)
    source_name      = Column(String(256), nullable=True)

    def to_dict(self):
        return {
            "id":               self.id,
            "created_at":       self.created_at.isoformat() if self.created_at else None,
            "timestamp":        self.timestamp.isoformat() if self.timestamp else None,
            "title":            self.title,
            "rejection_reason": self.rejection_reason,
            "score":            self.score,
            "source_url":       self.source_url,
            "source_name":      self.source_name,
        }

