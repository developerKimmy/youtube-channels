"""Single query YouTube scraper CLI."""

import argparse
import logging

from src.scrapers import YouTubeScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube Scraper")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "-c", "--config",
        default="channels",
        help="Config name (default: channels)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save results to file"
    )

    args = parser.parse_args()

    scraper = YouTubeScraper(args.config)
    results = scraper.scrape(args.query)

    if results and not args.no_save:
        scraper.save(results, args.query)

    if results:
        logger.info("\n--- Preview (first 5) ---")
        for i, item in enumerate(results[:5]):
            print(f"\n{i + 1}. {item.get('channel_name', 'N/A')}")
            print(f"   URL: {item.get('channel_url', 'N/A')}")
            print(f"   Subscribers: {item.get('subscribers', 'N/A')}")


if __name__ == "__main__":
    main()
