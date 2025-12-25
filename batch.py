"""Batch processing for YouTube channel collection."""

import argparse
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from src.scrapers import YouTubeScraper
from src.core import OutputManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BatchRunner:
    """Batch runner for collecting YouTube channels from multiple keywords."""

    MASTER_FILE = "all_channels.csv"
    COLUMN_NAME = "channel_url"

    def __init__(self, config_name: str = "channels"):
        self.config_name = config_name
        self.output_manager = OutputManager()
        self.collected_urls = self.output_manager.load_existing(
            self.MASTER_FILE,
            self.COLUMN_NAME
        )

    def _scrape_keyword(
        self,
        keyword: str
    ) -> tuple[str, int, Optional[str]]:
        """Scrape channels for a single keyword."""
        try:
            scraper = YouTubeScraper(self.config_name)
            results = scraper.scrape(keyword)

            if results:
                urls = [r["channel_url"] for r in results if r.get("channel_url")]
                new_count = self.output_manager.append(
                    urls,
                    self.MASTER_FILE,
                    self.COLUMN_NAME
                )
                self.collected_urls.update(urls)
                return keyword, new_count, None

            return keyword, 0, None

        except Exception as e:
            logger.error(f"Error scraping keyword '{keyword}': {e}")
            return keyword, 0, str(e)

    def run(
        self,
        keywords_file: str = "config/keywords.txt",
        target: int = 1000,
        max_workers: int = 5
    ) -> None:
        """Run batch collection."""
        keywords_path = Path(keywords_file)
        if not keywords_path.exists():
            logger.error(f"Keywords file not found: {keywords_file}")
            return

        with open(keywords_path, "r", encoding="utf-8") as f:
            keywords = [line.strip() for line in f if line.strip()]

        logger.info(f"Loaded {len(keywords)} keywords")
        logger.info(f"Target: {target:,} URLs")
        logger.info(f"Current: {len(self.collected_urls):,} URLs")
        logger.info(f"Workers: {max_workers}")
        logger.info("=" * 60)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._scrape_keyword, kw): kw
                for kw in keywords
            }

            for future in as_completed(futures):
                keyword, new_count, error = future.result()

                if error:
                    logger.warning(f"[{keyword}] Error: {error}")
                else:
                    logger.info(f"[{keyword}] +{new_count} (Total: {len(self.collected_urls):,})")

                if len(self.collected_urls) >= target:
                    logger.info("Target reached!")
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

        logger.info("=" * 60)
        logger.info(f"Done! Collected {len(self.collected_urls):,} URLs")
        logger.info(f"Saved to: output/{self.MASTER_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch YouTube Channel Collector")
    parser.add_argument("-t", "--target", type=int, default=1000, help="Target URL count")
    parser.add_argument("-k", "--keywords", default="config/keywords.txt", help="Keywords file")
    parser.add_argument("-w", "--workers", type=int, default=5, help="Number of threads")

    args = parser.parse_args()

    runner = BatchRunner()
    runner.run(keywords_file=args.keywords, target=args.target, max_workers=args.workers)
