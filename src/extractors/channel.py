"""YouTube channel extractor."""

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .base import BaseExtractor

logger = logging.getLogger(__name__)


class ChannelExtractor(BaseExtractor):
    """Extracts channel information from YouTube search results."""

    def build_search_url(self, query: str) -> str:
        """Build YouTube search URL with channel filter."""
        search_config = self.config.get("search", {})
        base_url = search_config.get("base_url", "https://www.youtube.com/results")
        query_param = search_config.get("query_param", "search_query")
        filter_param = search_config.get("filter_param", "sp")
        filter_value = search_config.get("filter_value", "EgIQAg%3D%3D")

        return f"{base_url}?{query_param}={query}&{filter_param}={filter_value}"

    def extract(self, query: str) -> list[dict]:
        """Extract channel data from YouTube search results."""
        url = self.build_search_url(query)
        logger.info(f"Fetching: {url}")

        self.driver.get(url)

        container_selector = self.selectors.get("item_container", "ytd-channel-renderer")

        try:
            self.wait_for_element(container_selector)
        except Exception:
            logger.warning("No channels found or page didn't load")
            return []

        self.scroll_page()

        items = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
        logger.info(f"Found {len(items)} channel elements")

        channels: list[dict] = []
        for item in items:
            channel = self._extract_channel_data(item)
            if channel.get("channel_url"):
                channels.append(channel)

        logger.info(f"Extracted {len(channels)} valid channels")
        return channels

    def _extract_channel_data(self, item: WebElement) -> dict:
        """Extract data from a single channel element."""
        channel_url = self.safe_get_attribute(
            item,
            self.selectors.get("channel_url", "#main-link"),
            "href"
        )

        if channel_url and not channel_url.startswith("http"):
            channel_url = f"https://www.youtube.com{channel_url}"

        return {
            "channel_name": self.safe_get_text(
                item,
                self.selectors.get("channel_name", "#text")
            ),
            "channel_url": channel_url,
            "subscribers": self.safe_get_text(
                item,
                self.selectors.get("subscribers", "#subscribers")
            ),
            "video_count": self.safe_get_text(
                item,
                self.selectors.get("video_count", "#video-count")
            ),
            "description": self.safe_get_text(
                item,
                self.selectors.get("description", "#description")
            ),
        }
