"""
models.py

SQLAlchemy declarative models. The `JSON` column type is used for the
`embedding` field on `PublishedPost` because it is natively supported by
both SQLite and PostgreSQL and maps automatically to/from Python lists,
so no extra serialization code is needed at the application layer.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PublishedPost(Base):
    __tablename__ = "published_posts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source_url = Column(String, nullable=True)
    selection_reason = Column(Text, nullable=True)
    why_relevant_now = Column(Text, nullable=True)
    # Stores the embedding vector as a JSON array, e.g. [0.123, -0.045, ...]
    embedding = Column(JSON, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"<PublishedPost id={self.id} title={self.title!r}>"


class RejectedPost(Base):
    __tablename__ = "rejected_posts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    title = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"<RejectedPost id={self.id} title={self.title!r}>"
