"""YouTube-specific scraper implementation."""

import logging
from typing import Optional, Type

from .base import BaseScraper
from ..extractors.base import BaseExtractor
from ..extractors.channel import ChannelExtractor

logger = logging.getLogger(__name__)


class YouTubeScraper(BaseScraper):
    """Scraper for YouTube content using Selenium.

    Supports different types of extraction (channels, videos, etc.)
    based on configuration.
    """

    EXTRACTORS: dict[str, Type[BaseExtractor]] = {
        "channel": ChannelExtractor,
    }

    def __init__(
        self,
        config_name: str = "channels",
        config_dir: str = "config",
        output_dir: str = "output"
    ):
        super().__init__(config_name, config_dir, output_dir)
        self._extractor_class = self._get_extractor_class()

    def _get_extractor_class(self) -> Type[BaseExtractor]:
        """Get the appropriate extractor class based on config."""
        extractor_type = self.config.get("type", "channel")
        extractor_class = self.EXTRACTORS.get(extractor_type)

        if not extractor_class:
            raise ValueError(f"Unknown extractor type: {extractor_type}")

        return extractor_class

    def scrape(self, query: str) -> list[dict]:
        """Scrape YouTube for the given query.

        Args:
            query: Search query

        Returns:
            List of scraped data dictionaries
        """
        logger.info(f"Starting scrape for query: {query}")

        with self.driver_factory.session() as driver:
            extractor = self._extractor_class(driver, self.config)
            results = extractor.extract(query)

        logger.info(f"Extracted {len(results)} items for query: {query}")
        return results
