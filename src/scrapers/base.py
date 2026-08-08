from abc import ABC, abstractmethod
from typing import List
from src.intelligence.schemas import RawTopic

class BaseScraper(ABC):
    """
    Abstract base class for all scraper components.
    Provides standard headers and enforces the scrape contract.
    """
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "AutonomousAIContentAgent/1.0.0 (+https://github.com/zuckrey-epslarp/bunker; security-bot)"
        }

    @abstractmethod
    async def scrape(self) -> List[RawTopic]:
        """
        Asynchronously fetches and parses source items.
        Returns a list of RawTopic Pydantic models.
        """
        pass
