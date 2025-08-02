"""Content moderation service using OpenAI Moderation API"""

import httpx
from loguru import logger

from app.settings import get_settings


class ContentModerationService:
    """Service for checking content appropriateness using OpenAI Moderation API"""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.api_key = self.settings.llm.openai_api_key.get_secret_value()
        self.base_url = "https://api.openai.com/v1"

    async def check_content_appropriateness(self, text: str) -> bool:
        """
        Check if content is appropriate for children using OpenAI Moderation API

        Args:
            text: Text to check for appropriateness

        Returns:
            True if content is appropriate, False otherwise
        """
        if not self.api_key:
            logger.warning("OpenAI API key not configured, skipping content moderation")
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/moderations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"input": text},
                    timeout=10.0,
                )
                response.raise_for_status()

                result = response.json()

                # Check if any categories are flagged
                categories = result.get("results", [{}])[0].get("categories", {})

                # For children's content, we want to be more strict
                # Check for violence, sexual content, hate, harassment, self-harm
                inappropriate_categories = ["violence", "sexual", "hate", "harassment", "self-harm"]

                for category in inappropriate_categories:
                    if categories.get(category, False):
                        logger.info(f"Content flagged as inappropriate: {category} - {text}")
                        return False

                # Also check the overall flagged status
                flagged = result.get("results", [{}])[0].get("flagged", False)
                if flagged:
                    logger.info(f"Content flagged as inappropriate (overall) - {text}")
                    return False

                return True

        except Exception as e:
            logger.error(f"Error checking content moderation: {e}")
            # In case of error, allow the content to avoid blocking the flow
            return True
