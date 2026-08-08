import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config.settings import settings
from src.db.database import get_db
from src.db.models import PublishedPost
from src.scheduler.cron import run_autonomous_loop

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


@router.get("/api/cron", summary="Trigger Autonomous Scraping & Evaluation Cycle")
async def trigger_cron(
    authorization: Optional[str] = Header(None),
    x_cron_secret: Optional[str] = Header(None, alias="x-cron-secret")
):
    """
    Secured cron trigger endpoint for Vercel Cron or external schedulers.
    Validates Authorization header (Bearer <CRON_SECRET>) or x-cron-secret header.
    Runs discovery, vector deduplication, LLM evaluation, post generation, and database persist.
    """
    expected_secret = settings.CRON_SECRET

    # Validate secret header if configured
    if expected_secret and expected_secret != "default_cron_secret":
        provided_token = None
        if authorization and authorization.startswith("Bearer "):
            provided_token = authorization.split("Bearer ")[1].strip()
        elif x_cron_secret:
            provided_token = x_cron_secret.strip()

        if provided_token != expected_secret:
            logger.warning("Unauthorized cron invocation attempt.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Invalid CRON_SECRET token."
            )

    logger.info("Cron trigger request authorized. Executing autonomous pipeline loop...")
    await run_autonomous_loop()
    return {"status": "success", "message": "Autonomous scraping & evaluation cycle completed successfully."}
