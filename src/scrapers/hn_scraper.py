import asyncio
import httpx
import logging
from typing import List, Dict, Any
from src.intelligence.schemas import RawTopic
from src.scrapers.base import BaseScraper

logger = logging.getLogger("autonomous_agent.scrapers.hn")

class HNScraper(BaseScraper):
    """
    Scraper for HackerNews top stories, pre-filtered for AI and security keywords.
    """
    def __init__(self, limit: int = 40, timeout: float = 15.0):
        super().__init__(timeout=timeout)
        self.limit = limit
        self.top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        self.item_url_template = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        
        # Keyword filters to select articles relevant to AI, Security, Vulnerabilities, and Tech Criticism
        self.keywords = [
            "ai", "llm", "gpt", "openai", "claude", "gemini", "llama", "deepmind",
            "security", "vulnerability", "exploit", "jailbreak", "hack", "bypass",
            "safety", "guardrail", "cyber", "attack", "threat", "prompt injection",
            "adversarial", "cve", "model weight", "red team", "poisoning"
        ]

    def _is_relevant(self, title: str) -> bool:
        """
        Determines relevance based on case-insensitive keyword matching.
        """
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in self.keywords)

    async def _fetch_story(self, client: httpx.AsyncClient, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetches detail for a single HN story.
        """
        try:
            url = self.item_url_template.format(item_id=item_id)
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"Failed to fetch HN item {item_id}: {e}")
        return None

    async def scrape(self) -> List[RawTopic]:
        topics = []
        try:
            logger.info("Fetching top story IDs from HackerNews...")
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                # 1. Fetch top story IDs
                response = await client.get(self.top_stories_url)
                response.raise_for_status()
                story_ids = response.json()[:self.limit]
                
                # 2. Fetch story details concurrently
                tasks = [self._fetch_story(client, story_id) for story_id in story_ids]
                stories = await asyncio.gather(*tasks)
                
                # 3. Filter and parse relevant stories
                for story in stories:
                    if not story or story.get("type") != "story":
                        continue
                    
                    title = story.get("title", "")
                    if self._is_relevant(title):
                        # Construct a rich summary
                        score = story.get("score", 0)
                        author = story.get("by", "unknown")
                        comments_count = len(story.get("kids", []))
                        hn_link = f"https://news.ycombinator.com/item?id={story.get('id')}"
                        external_url = story.get("url", hn_link)
                        
                        summary = (
                            f"HackerNews discussion on story '{title}' "
                            f"posted by user '{author}'. Score: {score} points. "
                            f"Number of direct/nested comments: {comments_count}. "
                            f"HN Thread: {hn_link}"
                        )
                        
                        topics.append(RawTopic(
                            title=title,
                            summary=summary,
                            url=external_url,
                            source_name="HackerNews"
                        ))
                        
            logger.info(f"Successfully scraped {len(topics)} filtered items from HackerNews.")
        except Exception as e:
            logger.error(f"Error scraping HackerNews: {e}", exc_info=True)
            
        return topics
