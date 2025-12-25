"""WebDriver factory for creating and managing browser instances."""

import logging
from typing import Optional
from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class WebDriverFactory:
    """Factory class for creating Selenium WebDriver instances."""

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        headless: bool = True,
        window_size: tuple[int, int] = (1920, 1080),
        user_agent: Optional[str] = None,
        lang: str = "en-US"
    ):
        self.headless = headless
        self.window_size = window_size
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT
        self.lang = lang

    def _build_options(self) -> Options:
        """Build Chrome options based on configuration."""
        options = Options()

        if self.headless:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
        options.add_argument(f"--lang={self.lang}")
        options.add_argument(f"--user-agent={self.user_agent}")

        return options

    def create(self) -> WebDriver:
        """Create and return a new WebDriver instance."""
        logger.info("Initializing Chrome WebDriver...")

        options = self._build_options()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        logger.info("WebDriver initialized successfully")
        return driver

    @contextmanager
    def session(self):
        """Context manager for WebDriver sessions.

        Usage:
            factory = WebDriverFactory()
            with factory.session() as driver:
                driver.get("https://example.com")
        """
        driver = self.create()
        try:
            yield driver
        finally:
            logger.info("Closing WebDriver session")
            driver.quit()
