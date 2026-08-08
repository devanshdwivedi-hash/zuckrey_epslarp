import json
import logging
from typing import Optional
import openai

from config.settings import settings
from config.persona_config import PERSONA_NAME, PERSONA_SYSTEM_PROMPT
from src.intelligence.schemas import RawTopic, GeneratedPost

logger = logging.getLogger("autonomous_agent.intelligence.generator")


class PostGenerator:
    """
    LLM Persona Post Generator.
    Transforms raw approved topics into persona-consistent, publication-ready technical posts
    with explicit selection rationales and timeliness metadata.
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self._is_mock_key = (
            not self.api_key or 
            "your_openai" in self.api_key.lower() or 
            self.api_key == "OPENAI_API_KEY"
        )
        if not self._is_mock_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key is unset or a placeholder. Running in fallback generator mode.")

    def _fallback_generate(self, topic: RawTopic) -> GeneratedPost:
        """
        Deterministic fallback post generation for local / offline testing without an active API key.
        """
        content = (
            f"### Technical Deep Dive: {topic.title}\n\n"
            f"**Source**: {topic.source_name} ([Reference Material]({topic.url}))\n\n"
            f"#### Technical Overview\n"
            f"{topic.summary}\n\n"
            f"#### Vulnerability & Adversarial Impact Analysis\n"
            f"This topic represents a critical vector in AI safety and machine learning robustness. "
            f"Security researchers and software engineers must evaluate the empirical findings disclosed in this report "
            f"to harden foundation model deployments against potential adversarial exploitation.\n"
        )
        return GeneratedPost(
            title=topic.title,
            content=content,
            selection_reason=(
                f"Selected due to high technical relevance to {PERSONA_NAME} principles, "
                f"demonstrating empirical research findings rather than PR hype."
            ),
            why_relevant_now=(
                f"Timely technical disclosure from {topic.source_name} highlighting critical vulnerabilities "
                f"and security posture in current AI systems."
            ),
            sources=[topic.url]
        )

    async def generate(self, topic: RawTopic) -> GeneratedPost:
        """
        Generates a persona-consistent post for the given RawTopic.
        """
        if self._is_mock_key:
            return self._fallback_generate(topic)

        prompt = f"""
You are the {PERSONA_NAME}. Follow these exact guidelines:
---
{PERSONA_SYSTEM_PROMPT}
---

TASK: Generate a high-quality, technical post for an elite audience of security researchers based on the approved topic below.

TOPIC DETAILS:
Title: {topic.title}
Source Name: {topic.source_name}
Source URL: {topic.url}
Summary: {topic.summary}

REQUIREMENTS:
1. Title: Curated, publication-ready technical title.
2. Content: Written post in Markdown enforcing analytical, objective, and authoritative persona voice. Avoid marketing buzzwords and PR speak.
3. Selection Reason: Detailed explanation of why this topic was selected over generic news.
4. Why Relevant Now: Timeliness and immediate technical relevance today.
5. Sources: Must be a list containing the original URL ["{topic.url}"].

Provide your response as a valid JSON object matching this exact schema:
{{
  "title": "Curated post title",
  "content": "Full formatted body of post in Markdown format",
  "selection_reason": "Detailed selection rationale explaining technical criteria",
  "why_relevant_now": "Timely context explaining immediate relevance",
  "sources": ["{topic.url}"]
}}
"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            # Ensure sources contains topic.url
            if not data.get("sources"):
                data["sources"] = [topic.url]
            return GeneratedPost(**data)
        except Exception as e:
            logger.error(f"LLM post generation error: {e}. Utilizing fallback generator.")
            return self._fallback_generate(topic)


# Standalone helper function as required by Phase 4 interface
async def generate_post(topic: RawTopic) -> GeneratedPost:
    """
    Convenience function matching `generate_post(topic: RawTopic) -> GeneratedPost`.
    """
    generator = PostGenerator()
    return await generator.generate(topic)
