import logging
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Header, HTTPException, status
from fastapi.responses import JSONResponse
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
    created_at: Optional[str] = Field(None, description="ISO timestamp when AI Agent published the post")
    article_published_at: Optional[str] = Field(None, description="ISO timestamp when original article was published")


class CronExecutionResponse(BaseModel):
    status: str
    message: str


@router.get("/feed", response_model=List[FeedPostResponse], summary="Retrieve Published Post Feed")
def get_feed(
    limit: Optional[int] = Query(50, ge=1, le=2000, description="Maximum number of posts to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Fetches published technical posts from published_posts table,
    sorted by created_at descending (newest first).
    Wrapped in try/except to handle database or query exceptions gracefully without crashing Vercel functions.
    """
    try:
        query = db.query(PublishedPost).order_by(PublishedPost.created_at.desc(), PublishedPost.id.desc()).offset(offset)
        if limit is not None and limit > 0:
            query = query.limit(limit)
        posts = query.all()
        
        response_list = []
        for p in posts:
            sources = p.sources if isinstance(p.sources, list) else ([p.source_url] if p.source_url else [])
            created_at_str = p.created_at.isoformat() if p.created_at else (p.timestamp.isoformat() if p.timestamp else None)
            article_pub_str = p.article_published_at.isoformat() if p.article_published_at else None
            response_list.append(
                FeedPostResponse(
                    content=p.content,
                    selection_reason=p.selection_reason,
                    why_relevant_now=p.why_relevant_now,
                    sources=sources,
                    created_at=created_at_str,
                    article_published_at=article_pub_str
                )
            )
        return response_list
    except Exception as e:
        logger.error(f"DB ERROR in /feed: {e}", exc_info=True)
        return []


@router.get("/api/agent/feed", summary="Retrieve Agent Feed (Legacy & Agent Query API)")
def get_agent_feed(
    agentId: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Alias endpoint serving posts wrapped under 'posts' key for agent feed integrations.
    """
    try:
        posts = (
            db.query(PublishedPost)
            .order_by(PublishedPost.timestamp.desc())
            .limit(limit)
            .all()
        )
        post_items = []
        for index, p in enumerate(posts):
            sources = p.sources if isinstance(p.sources, list) else ([p.source_url] if p.source_url else [])
            created_at_str = p.created_at.isoformat() if p.created_at else (p.timestamp.isoformat() if p.timestamp else None)
            article_pub_str = p.article_published_at.isoformat() if p.article_published_at else None
            post_items.append({
                "id": p.id or (index + 1),
                "createdAt": created_at_str,
                "created_at": created_at_str,
                "article_published_at": article_pub_str,
                "text": p.content,
                "rationale": p.selection_reason,
                "sources": sources
            })
        return {"posts": post_items}
    except Exception as e:
        logger.error(f"Error fetching agent feed: {e}")
        return {"posts": []}



def verify_cron_secret(
    authorization: Optional[str] = Header(None),
    x_cron_secret: Optional[str] = Header(None, alias="x-cron-secret"),
    secret: Optional[str] = Query(None)
):
    """
    Protects /api/cron against unauthorized invocations by checking CRON_SECRET.
    """
    expected_secret = os.getenv("CRON_SECRET", settings.CRON_SECRET)
    
    # If CRON_SECRET is configured, enforce verification
    if expected_secret and expected_secret not in ["default_cron_secret_key", "default_cron_secret"]:
        provided_secret = None
        if authorization and authorization.startswith("Bearer "):
            provided_secret = authorization.split("Bearer ", 1)[1].strip()
        elif x_cron_secret:
            provided_secret = x_cron_secret.strip()
        elif secret:
            provided_secret = secret.strip()

        if provided_secret != expected_secret:
            logger.warning("Unauthorized access attempt to /api/cron.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing CRON_SECRET token."
            )


@router.get("/api/cron", summary="Serverless Vercel Cron Trigger")
@router.get("/cron", include_in_schema=False)
async def trigger_cron(
    _: None = Depends(verify_cron_secret)
):
    """
    Serverless Vercel Cron endpoint.
    Triggers full autonomous pipeline loop:
    - Scrapes raw topics via arXiv, HN, RSS engines.
    - Runs vector memory deduplication against database history.
    - Evaluates topics via LLM Editor-in-Chief.
    - Generates technical posts and saves them directly to PostgreSQL/SQLite DB.
    Wrapped in robust try/except to log and return structured 500 JSON errors on failure.
    """
    logger.info("Serverless cron trigger received on /api/cron. Executing pipeline loop...")
    try:
        await run_autonomous_loop()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": "Serverless autonomous pipeline cycle executed successfully."
            }
        )
    except Exception as e:
        logger.error(f"Error executing serverless cron pipeline: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": f"Pipeline execution error: {str(e)}",
                "error_type": type(e).__name__
            }
        )
