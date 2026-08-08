import asyncio
import re
import httpx
import feedparser
import logging
from urllib.parse import urlparse
from typing import List, Optional
from src.intelligence.schemas import RawTopic
from src.scrapers.base import BaseScraper

logger = logging.getLogger("autonomous_agent.scrapers.rss")

class RSSScraper(BaseScraper):
    """
    Scraper for technical blogs via RSS feeds. Parses and cleans descriptions.
    """
    def __init__(self, feeds: Optional[List[str]] = None, timeout: float = 15.0):
        super().__init__(timeout=timeout)
        self.feeds = feeds or [
            "https://huggingface.co/blog/feed.xml",
            "https://openai.com/news/rss.xml",
            "https://security.googleblog.com/feeds/posts/default"
        ]
        self.html_tag_re = re.compile(r"<[^>]+>")

    def _strip_html(self, text: str) -> str:
        """
        Removes HTML tags and normalizes whitespace from summaries.
        """
        if not text:
            return ""
        cleaned = self.html_tag_re.sub(" ", text)
        return " ".join(cleaned.split()).strip()

    def _get_source_name(self, url: str) -> str:
        """
        Extracts a clean, human-readable source name based on the feed URL.
        """
        domain = urlparse(url).netloc.lower()
        if "huggingface" in domain:
            return "Hugging Face Blog"
        elif "openai" in domain:
            return "OpenAI Blog"
        elif "googleblog" in domain:
            return "Google Security Blog"
        return domain

    async def _fetch_and_parse_feed(self, client: httpx.AsyncClient, feed_url: str) -> List[RawTopic]:
        """
        Fetches a single feed and parses its entries.
        """
        topics = []
        try:
            logger.info(f"Fetching RSS feed from: {feed_url}")
            response = await client.get(feed_url)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch feed {feed_url}: HTTP {response.status_code}")
                return []
            
            feed = feedparser.parse(response.text)
            source_name = self._get_source_name(feed_url)
            
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                raw_summary = entry.get("summary", entry.get("description", "")).strip()
                summary = self._strip_html(raw_summary)
                url = entry.get("link", "").strip()
                
                if title and url:
                    topics.append(RawTopic(
                        title=title,
                        summary=summary,
                        url=url,
                        source_name=source_name
                    ))
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {e}")
            
        return topics

    async def scrape(self) -> List[RawTopic]:
        topics = []
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                tasks = [self._fetch_and_parse_feed(client, feed_url) for feed_url in self.feeds]
                results = await asyncio.gather(*tasks)
                
                for feed_topics in results:
                    topics.extend(feed_topics)
                    
            logger.info(f"Successfully scraped a total of {len(topics)} items from all RSS feeds.")
        except Exception as e:
            logger.error(f"Error orchestrating RSS scraping: {e}", exc_info=True)
            
        return topics
