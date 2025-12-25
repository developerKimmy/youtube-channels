"""Base scraper interface for platform-agnostic scraping."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..core.driver import WebDriverFactory
from ..core.output import OutputManager, OutputFormat
from ..config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all scrapers.

    Provides common functionality for web scraping including
    WebDriver management, configuration loading, and output handling.
    """

    def __init__(
        self,
        config_name: str,
        config_dir: str = "config",
        output_dir: str = "output"
    ):
        self.config_loader = ConfigLoader(config_dir)
        self.config = self.config_loader.load(config_name)
        self.output_manager = OutputManager(output_dir)

        headless = self.config.get("options", {}).get("headless", True)
        self.driver_factory = WebDriverFactory(headless=headless)

    @abstractmethod
    def scrape(self, query: str) -> list[dict]:
        """Execute scraping for the given query.

        Args:
            query: Search query or target identifier

        Returns:
            List of scraped data dictionaries
        """
        pass

    def save(
        self,
        data: list[dict],
        query: str,
        format: Optional[OutputFormat] = None
    ) -> Optional[Path]:
        """Save scraped data to file.

        Args:
            data: List of scraped data dictionaries
            query: Query used for scraping (used in filename)
            format: Output format (csv or json)

        Returns:
            Path to saved file, or None if no data
        """
        output_config = self.config.get("output", {})
        output_format = format or output_config.get("format", "csv")
        base_filename = output_config.get("filename", "output")

        return self.output_manager.save(
            data=data,
            filename=base_filename,
            suffix=query,
            format=output_format
        )
