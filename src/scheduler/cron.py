import asyncio
import logging
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.settings import settings
from src.db.database import SessionLocal, init_db
from src.db.repository import (
    create_published_post,
    create_rejected_post,
    is_url_processed,
    get_all_published_embeddings
)
from src.scrapers.arxiv_scraper import ArxivScraper
from src.scrapers.hn_scraper import HNScraper
from src.scrapers.rss_scraper import RSSScraper
from src.memory.embeddings import get_embedding
from src.memory.deduplicator import is_duplicate
from src.intelligence.evaluator import LLMEvaluator
from src.intelligence.generator import generate_post

logger = logging.getLogger("autonomous_agent.scheduler.cron")

scheduler = AsyncIOScheduler()


async def run_autonomous_loop():
    """
    Core autonomous pipeline loop:
    1. Ingest raw topics via web scrapers (arXiv, HackerNews, RSS feeds).
    2. Enforce exact URL and vector memory semantic deduplication.
    3. Evaluate remaining topics using LLM Editor-in-Chief.
    4. Generate structured technical posts for approved topics in persona voice.
    5. Save approved posts & rejected topics to DB for feedback and feed serving.
    """
    logger.info("=== STARTING AUTONOMOUS PIPELINE CYCLE ===")
    db = SessionLocal()
    evaluator = LLMEvaluator()

    try:
        # 1. Fetch existing published embeddings for deduplication memory
        existing_records = get_all_published_embeddings(db)
        published_vectors = [rec[2] for rec in existing_records if rec[2] is not None]
        logger.info(f"Loaded {len(published_vectors)} existing vector embeddings from database memory.")

        # 2. Ingest raw topics from all active scrapers concurrently
        raw_topics = []
        scraper_results = await asyncio.gather(
            ArxivScraper(max_results=10).scrape(),
            HNScraper(limit=20).scrape(),
            RSSScraper().scrape(),
            return_exceptions=True
        )

        scraper_names = ["arXiv", "HackerNews", "RSS feeds"]
        for name, res in zip(scraper_names, scraper_results):
            if isinstance(res, Exception):
                logger.error(f"{name} scraper failed during loop: {res}")
            elif isinstance(res, list):
                raw_topics.extend(res)
                logger.info(f"Ingested {len(res)} topics from {name}.")

        logger.info(f"Total raw candidate topics collected: {len(raw_topics)}")

        # 3. Process candidate topics
        published_count = 0
        rejected_count = 0
        duplicate_count = 0

        for topic in raw_topics:
            try:
                # A. URL Deduplication Check
                if is_url_processed(db, topic.url):
                    duplicate_count += 1
                    logger.debug(f"Skipping processed URL: {topic.url}")
                    continue

                # B. Vector Semantic Deduplication Check
                text_to_embed = f"{topic.title} {topic.summary}"
                candidate_vec = get_embedding(text_to_embed)

                if is_duplicate(candidate_vec, published_vectors, threshold=0.88):
                    duplicate_count += 1
                    logger.info(f"Skipping duplicate topic by vector memory: '{topic.title}'")
                    continue

                # C. LLM Editor-in-Chief Evaluation
                decision = await evaluator.evaluate_topic(topic)
                logger.info(f"Evaluated '{topic.title}' -> Decision: {decision.decision} (Score: {decision.score}/10)")

                if decision.decision == "PUBLISH":
                    # D. Persona Post Generation
                    generated_post = await generate_post(topic)
                    
                    # Extract article publication datetime if available
                    article_pub_dt = getattr(topic, "published_at", None) or getattr(topic, "date", None)
                    if not article_pub_dt and getattr(topic, "url", None):
                        import re
                        from datetime import datetime, timezone
                        url_match = re.search(r"/(\d{4})/(\d{2})/", topic.url)
                        if url_match:
                            try:
                                year, month = int(url_match.group(1)), int(url_match.group(2))
                                article_pub_dt = datetime(year, month, 1, tzinfo=timezone.utc)
                            except Exception:
                                pass

                    # E. Database Persistence
                    post_db = create_published_post(
                        db=db,
                        title=generated_post.title,
                        content=generated_post.content,
                        source_url=topic.url,
                        selection_reason=generated_post.selection_reason,
                        why_relevant_now=generated_post.why_relevant_now,
                        embedding=candidate_vec,
                        persona_name="AI Security & Vulnerability Researcher",
                        score=decision.score,
                        source_name=topic.source_name,
                        sources=generated_post.sources,
                        article_published_at=article_pub_dt
                    )
                    
                    # Add candidate vector to in-memory list to prevent duplicate in same cycle
                    published_vectors.append(candidate_vec)
                    published_count += 1
                    logger.info(f"Successfully published post ID {post_db.id}: '{post_db.title}'")
                else:
                    # Record rejected post for audit
                    create_rejected_post(
                        db=db,
                        title=topic.title,
                        source_url=topic.url,
                        rejection_reason=decision.reason,
                        score=decision.score,
                        source_name=topic.source_name
                    )
                    rejected_count += 1

            except Exception as item_error:
                logger.error(f"Error processing topic '{getattr(topic, 'title', 'unknown')}': {item_error}", exc_info=True)
                continue

        logger.info(
            f"=== COMPLETED AUTONOMOUS CYCLE ===\n"
            f"Published: {published_count} | Rejected: {rejected_count} | Duplicates Skipped: {duplicate_count}"
        )

    except Exception as cycle_error:
        logger.error(f"Critical error in autonomous pipeline loop: {cycle_error}", exc_info=True)
    finally:
        db.close()


def start_scheduler(run_immediately: bool = False):
    """
    Initializes and starts the APScheduler background scheduler.
    Schedules run_autonomous_loop() every SCRAPING_INTERVAL_MINUTES.
    """
    if not scheduler.running:
        logger.info(f"Starting APScheduler background task (Interval: {settings.SCRAPING_INTERVAL_MINUTES} minutes)...")
        scheduler.add_job(
            run_autonomous_loop,
            trigger="interval",
            minutes=settings.SCRAPING_INTERVAL_MINUTES,
            id="autonomous_content_loop",
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler started successfully.")
        
        if run_immediately:
            logger.info("Triggering immediate initial pipeline run...")
            asyncio.create_task(run_autonomous_loop())


def stop_scheduler():
    """
    Shuts down the APScheduler background scheduler cleanly.
    """
    if scheduler.running:
        logger.info("Stopping APScheduler background task...")
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")
