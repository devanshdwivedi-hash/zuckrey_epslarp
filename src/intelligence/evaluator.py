import asyncio
import json
import logging
from typing import Optional
import openai
from config.settings import settings
from config.persona_config import PERSONA_NAME, PERSONA_SYSTEM_PROMPT
from src.intelligence.schemas import RawTopic, EditorialDecision, GeneratedPost

logger = logging.getLogger("autonomous_agent.intelligence.evaluator")

class LLMEvaluator:
    """
    LLM Editor-in-Chief Evaluator & Post Generator.
    Evaluates raw ingested topics against persona criteria to accept or reject,
    and generates structured technical posts for approved topics.
    Supports OpenAI, Groq, and xAI (Grok) providers automatically.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: Optional[str] = None, 
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or settings.effective_api_key
        self.model = model or settings.effective_model
        self.base_url = base_url or settings.effective_base_url
        self._is_mock_key = (
            not self.api_key or 
            any(x in self.api_key.lower() for x in ["your_", "placeholder", "groq_api_key", "openai_api_key", "grok_api_key"]) or 
            self.api_key in ("OPENAI_API_KEY", "LLM_API_KEY", "GROQ_API_KEY", "GROK_API_KEY")
        )
        if not self._is_mock_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None
            logger.warning("LLM API key is unset or a placeholder. Running in fallback evaluation mode.")

    def _fallback_evaluate_topic(self, topic: RawTopic) -> EditorialDecision:
        """
        Deterministic fallback evaluation for offline / local testing without an API key.
        Accepts security, vulnerability, AI safety, or research topics. Rejects generic news.
        """
        text = f"{topic.title} {topic.summary}".lower()
        security_keywords = [
            "security", "vulnerability", "exploit", "jailbreak", "prompt injection",
            "cve", "adversarial", "attack", "red team", "safety", "poisoning", "bypass",
            "trust", "paper", "arxiv"
        ]
        matches = [kw for kw in security_keywords if kw in text]
        if len(matches) >= 1 or topic.source_name == "arXiv":
            return EditorialDecision(
                decision="PUBLISH",
                score=min(6 + len(matches), 10),
                reason=f"Technical security/AI topic matching keywords ({', '.join(matches or ['research paper'])})."
            )
        else:
            return EditorialDecision(
                decision="REJECT",
                score=3,
                reason="Lacks technical security angle or empirical research evidence."
            )

    def _fallback_generate_post(self, topic: RawTopic, decision: EditorialDecision) -> GeneratedPost:
        """
        Deterministic fallback post generation for offline / local testing without an API key.
        """
        content = (
            f"### Technical Briefing: {topic.title}\n\n"
            f"**Source**: {topic.source_name} ([Original Material]({topic.url}))\n\n"
            f"#### Analytical Overview\n"
            f"{topic.summary}\n\n"
            f"#### Vulnerability & Security Impact\n"
            f"This topic represents an active area of investigation in AI security and machine learning robustness. "
            f"Researchers and security engineers must account for the implications outlined in this report when hardening foundation model deployments.\n"
        )
        return GeneratedPost(
            title=topic.title,
            content=content,
            selection_reason=decision.reason,
            why_relevant_now=f"Timely technical disclosure from {topic.source_name} highlighting security posture.",
            sources=[topic.url]
        )

    async def evaluate_topic(self, topic: RawTopic) -> EditorialDecision:
        """
        Evaluates a RawTopic using the LLM Editor-in-Chief persona.
        Returns EditorialDecision (PUBLISH / REJECT).
        Enforces a 0.5s rate-limit pause between Groq / LLM API calls.
        """
        if self._is_mock_key:
            return self._fallback_evaluate_topic(topic)

        prompt = f"""
You are acting as the LLM Editor-in-Chief following this exact persona definition:
---
{PERSONA_SYSTEM_PROMPT}
---

EVALUATE THE FOLLOWING TOPIC:
Title: {topic.title}
Source: {topic.source_name}
URL: {topic.url}
Summary: {topic.summary}

Provide your decision as a valid JSON object matching this exact schema:
{{
  "decision": "PUBLISH" or "REJECT",
  "score": integer between 1 and 10,
  "reason": "Detailed technical explanation referencing persona guidelines"
}}
"""
        try:
            await asyncio.sleep(0.5)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            return EditorialDecision(**data)
        except Exception as e:
            logger.error(f"LLM topic evaluation error: {e}. Utilizing fallback evaluation.")
            return self._fallback_evaluate_topic(topic)

    async def generate_post(self, topic: RawTopic, decision: EditorialDecision) -> GeneratedPost:
        """
        Generates a publication-ready post in the active persona tone for an approved topic.
        Enforces a 0.5s rate-limit pause between Groq / LLM API calls.
        """
        if self._is_mock_key:
            return self._fallback_generate_post(topic, decision)

        prompt = f"""
You are the {PERSONA_NAME}. Write a high-quality, technical post for an elite audience of AI security researchers and software engineers based on the approved topic below.

Persona Instructions:
- Tone: Analytical, authoritative, objective, and critical.
- Avoid marketing hype, PR speak, and introductory explanations. Focus on technical specifics, attack vectors, or empirical findings.

TOPIC DETAILS:
Title: {topic.title}
Source: {topic.source_name} ({topic.url})
Summary: {topic.summary}
Editorial Selection Reason: {decision.reason}

Provide your post output as a valid JSON object matching this exact schema:
{{
  "title": "Curated, publication-ready title",
  "content": "Full formatted body of post in Markdown format",
  "selection_reason": "Brief technical rationale for selecting this post",
  "why_relevant_now": "Timely context explaining why this matters today",
  "sources": ["{topic.url}"]
}}
"""
        try:
            await asyncio.sleep(0.5)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            return GeneratedPost(**data)
        except Exception as e:
            logger.error(f"LLM post generation error: {e}. Utilizing fallback post generation.")
            return self._fallback_generate_post(topic, decision)

