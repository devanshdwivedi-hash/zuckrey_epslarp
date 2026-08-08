import asyncio
import logging
from typing import List, Tuple, Callable, Optional

from src.intelligence.schemas import RawTopic, EditorialDecision, GeneratedPost
from src.intelligence.evaluator import LLMEvaluator
from src.intelligence.generator import generate_post
from src.memory.embeddings import get_embedding

logger = logging.getLogger("autonomous_agent.intelligence.pipeline")


async def run_discovery_and_evaluation(
    is_duplicate_fn: Optional[Callable[[RawTopic, List[float]], bool]] = None
) -> Tuple[List[GeneratedPost], List[Tuple[RawTopic, EditorialDecision]]]:
    """
    Unified master discovery, evaluation, and post generation pipeline:
    1. Aggregation: Scrapes candidate RawTopic items concurrently from arXiv, HackerNews, and RSS feeds.
    2. Deduplication: Generates embeddings for candidates and uses is_duplicate_fn to drop duplicate items.
    3. Evaluation: Evaluates remaining topics with LLMEvaluator against persona criteria (PUBLISH vs REJECT).
    4. Generation: Invokes generate_post for each approved topic to construct complete GeneratedPost objects.
    5. Returns a tuple: (accepted_posts, rejected_items)
    """
    # Import scrapers dynamically inside function to prevent circular package imports
    from src.scrapers.arxiv_scraper import ArxivScraper
    from src.scrapers.hn_scraper import HNScraper
    from src.scrapers.rss_scraper import RSSScraper

    logger.info("=== STARTING DISCOVERY & EVALUATION PIPELINE ===")
    raw_topics: List[RawTopic] = []

    # 1. Aggregation: Run web scrapers concurrently
    try:
        arxiv_task = ArxivScraper(max_results=10).scrape()
        hn_task = HNScraper(limit=20).scrape()
        rss_task = RSSScraper().scrape()

        results = await asyncio.gather(arxiv_task, hn_task, rss_task, return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Scraper error during pipeline aggregation: {res}")
            elif isinstance(res, list):
                raw_topics.extend(res)
    except Exception as e:
        logger.error(f"Failed to orchestrate scrapers aggregation: {e}", exc_info=True)

    logger.info(f"Aggregated a total of {len(raw_topics)} raw topics from scrapers.")

    # 2. Deduplication & Filtering
    filtered_topics: List[Tuple[RawTopic, List[float]]] = []
    for topic in raw_topics:
        try:
            text_for_embedding = f"{topic.title} {topic.summary}"
            vector = get_embedding(text_for_embedding)

            # Check if caller provided duplicate check function
            if is_duplicate_fn and is_duplicate_fn(topic, vector):
                logger.info(f"Deduplicator dropped candidate topic: '{topic.title}'")
                continue

            filtered_topics.append((topic, vector))
        except Exception as dup_err:
            logger.error(f"Error during topic deduplication check for '{topic.title}': {dup_err}")
            filtered_topics.append((topic, []))

    logger.info(f"Remaining topics after deduplication check: {len(filtered_topics)}")

    # 3. Evaluation & Post Generation
    evaluator = LLMEvaluator()
    accepted_posts: List[GeneratedPost] = []
    rejected_items: List[Tuple[RawTopic, EditorialDecision]] = []

    for topic, vector in filtered_topics:
        try:
            decision: EditorialDecision = await evaluator.evaluate_topic(topic)
            logger.info(f"Evaluated '{topic.title}' -> {decision.decision} (Score: {decision.score}/10)")

            if decision.decision == "PUBLISH":
                # 4. Generation: Construct GeneratedPost
                post: GeneratedPost = await generate_post(topic)
                accepted_posts.append(post)
            else:
                rejected_items.append((topic, decision))

        except Exception as eval_err:
            logger.error(f"Error evaluating topic '{topic.title}': {eval_err}", exc_info=True)
            continue

    logger.info(
        f"=== DISCOVERY & EVALUATION PIPELINE COMPLETE ===\n"
        f"Approved Posts Generated: {len(accepted_posts)} | Rejected Items: {len(rejected_items)}"
    )

    return accepted_posts, rejected_items
