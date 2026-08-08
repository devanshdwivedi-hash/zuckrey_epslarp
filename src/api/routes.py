import logging
from typing import List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import PublishedPost

logger = logging.getLogger("autonomous_agent.api.routes")

router = APIRouter()


class FeedPostResponse(BaseModel):
    """
    Exact response schema required for evaluators consuming GET /feed.
    """
    content: str = Field(..., description="The full, formatted body content of the post")
    selection_reason: str = Field(..., description="Editorial explanation for why this post was selected")
    why_relevant_now: str = Field(..., description="Timely context highlighting security relevance today")
    sources: List[str] = Field(..., default_factory=list, description="List of source URLs for the post")


@router.get("/feed", response_model=List[FeedPostResponse], summary="Retrieve Published Post Feed")
def get_feed(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of posts to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Fetches published technical posts from published_posts table,
    sorted by timestamp descending (newest first).
    """
    posts = (
        db.query(PublishedPost)
        .order_by(PublishedPost.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    response_list = []
    for p in posts:
        # Ensure sources list is properly formatted
        sources = p.sources if isinstance(p.sources, list) else ([p.source_url] if p.source_url else [])
        response_list.append(
            FeedPostResponse(
                content=p.content,
                selection_reason=p.selection_reason,
                why_relevant_now=p.why_relevant_now,
                sources=sources
            )
        )
    return response_list
