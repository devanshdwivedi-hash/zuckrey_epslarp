from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from src.db.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class PublishedPost(Base):
    """
    SQLAlchemy model representing approved and published technical posts.
    Stored in table: published_posts
    """
    __tablename__ = "published_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    title = Column(String(512), nullable=False)
    content = Column(Text, nullable=False)
    source_url = Column(String(1024), nullable=False, index=True)
    selection_reason = Column(Text, nullable=False)
    why_relevant_now = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # Stores vector embedding array as JSON
    
    # Metadata attributes
    persona_name = Column(String(256), nullable=True)
    score = Column(Integer, nullable=True)
    source_name = Column(String(256), nullable=True)
    sources = Column(JSON, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "title": self.title,
            "content": self.content,
            "source_url": self.source_url,
            "selection_reason": self.selection_reason,
            "why_relevant_now": self.why_relevant_now,
            "embedding": self.embedding,
            "persona_name": self.persona_name,
            "score": self.score,
            "source_name": self.source_name,
            "sources": self.sources or [self.source_url],
        }


class RejectedPost(Base):
    """
    SQLAlchemy model representing topics filtered out by the LLM Editor-in-Chief.
    Stored in table: rejected_posts (for inspection & verifying high rejection criteria).
    """
    __tablename__ = "rejected_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    title = Column(String(512), nullable=False)
    source_url = Column(String(1024), nullable=False, index=True)
    rejection_reason = Column(Text, nullable=False)
    
    # Metadata attributes
    score = Column(Integer, nullable=True)
    source_name = Column(String(256), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "title": self.title,
            "source_url": self.source_url,
            "rejection_reason": self.rejection_reason,
            "score": self.score,
            "source_name": self.source_name,
        }
