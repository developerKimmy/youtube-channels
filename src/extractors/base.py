"""Base extractor interface for data extraction from web pages."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Abstract base class for extracting data from web pages."""

    def __init__(self, driver: WebDriver, config: dict):
        self.driver = driver
        self.config = config
        self.selectors: dict[str, str] = config.get("selectors", {})
        self.options: dict = config.get("options", {})

    @abstractmethod
    def extract(self, query: str) -> list[dict]:
        """Extract data based on query."""
        pass

    def scroll_page(
        self,
        times: Optional[int] = None,
        pause: Optional[float] = None
    ) -> None:
        """Scroll page to load dynamic content."""
        max_scroll = times or self.options.get("max_scroll", 5)
        scroll_pause = pause or self.options.get("scroll_pause", 2)

        for i in range(max_scroll):
            self.driver.execute_script(
                "window.scrollTo(0, document.documentElement.scrollHeight);"
            )
            time.sleep(scroll_pause)
            logger.debug(f"Scrolled {i + 1}/{max_scroll}")

    def safe_get_text(self, element: WebElement, selector: str) -> str:
        """Safely extract text from element."""
        try:
            found = element.find_element(By.CSS_SELECTOR, selector)
            return found.text.strip()
        except Exception:
            return ""

    def safe_get_attribute(
        self,
        element: WebElement,
        selector: str,
        attr: str
    ) -> str:
        """Safely extract attribute from element."""
        try:
            found = element.find_element(By.CSS_SELECTOR, selector)
            return found.get_attribute(attr) or ""
        except Exception:
            return ""

    def wait_for_element(self, selector: str, timeout: int = 10) -> WebElement:
        """Wait for element to be present."""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
