import httpx
import feedparser
import logging
from typing import List
from src.intelligence.schemas import RawTopic
from src.scrapers.base import BaseScraper

logger = logging.getLogger("autonomous_agent.scrapers.arxiv")

class ArxivScraper(BaseScraper):
    """
    Scraper for recent arXiv papers in AI, Security/Cryptography, and Computation/Language.
    """
    def __init__(self, max_results: int = 15, timeout: float = 15.0):
        super().__init__(timeout=timeout)
        self.max_results = max_results
        self.endpoint = "https://export.arxiv.org/api/query"

    async def scrape(self) -> List[RawTopic]:
        params = {
            "search_query": "cat:cs.AI OR cat:cs.CR OR cat:cs.CL",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": self.max_results
        }
        
        topics = []
        try:
            logger.info("Fetching recent papers from arXiv...")
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(self.endpoint, params=params)
                response.raise_for_status()
                
            # Parse XML feed asynchronously retrieved
            feed = feedparser.parse(response.text)
            
            if not feed.entries:
                logger.warning("No entries found in arXiv feed response.")
                return []

            for entry in feed.entries:
                title = entry.get("title", "").strip()
                # Clean up newlines/extra spaces standard in arXiv abstracts
                summary = entry.get("summary", entry.get("description", "")).strip()
                summary = " ".join(summary.split())
                
                url = entry.get("id", entry.get("link", ""))
                
                # Check for empty entries
                if title and url:
                    topics.append(RawTopic(
                        title=title,
                        summary=summary,
                        url=url,
                        source_name="arXiv"
                    ))
            logger.info(f"Successfully scraped {len(topics)} papers from arXiv.")
        except Exception as e:
            logger.error(f"Error scraping arXiv: {e}", exc_info=True)
            
        return topics
