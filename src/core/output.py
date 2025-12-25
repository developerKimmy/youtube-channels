"""Output manager for saving scraped data to files."""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal
from threading import Lock

import pandas as pd

logger = logging.getLogger(__name__)

OutputFormat = Literal["csv", "json"]


class OutputManager:
    """Manages output file operations for scraped data."""

    def __init__(
        self,
        output_dir: str = "output",
        default_format: OutputFormat = "csv"
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.default_format = default_format
        self._lock = Lock()

    def _generate_filename(
        self,
        base_name: str,
        suffix: Optional[str] = None,
        include_timestamp: bool = True
    ) -> str:
        """Generate a filename with optional suffix and timestamp."""
        parts = [base_name]

        if suffix:
            safe_suffix = "".join(c if c.isalnum() else "_" for c in suffix)
            parts.append(safe_suffix)

        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            parts.append(timestamp)

        return "_".join(parts)

    def save(
        self,
        data: list[dict],
        filename: str,
        suffix: Optional[str] = None,
        format: Optional[OutputFormat] = None,
        include_timestamp: bool = True
    ) -> Optional[Path]:
        """Save data to a file.

        Args:
            data: List of dictionaries to save
            filename: Base filename (without extension)
            suffix: Optional suffix to add to filename
            format: Output format (csv or json)
            include_timestamp: Whether to include timestamp in filename

        Returns:
            Path to saved file, or None if no data
        """
        if not data:
            logger.warning("No data to save")
            return None

        output_format = format or self.default_format
        full_filename = self._generate_filename(filename, suffix, include_timestamp)

        df = pd.DataFrame(data)

        if output_format == "csv":
            filepath = self.output_dir / f"{full_filename}.csv"
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
        elif output_format == "json":
            filepath = self.output_dir / f"{full_filename}.json"
            df.to_json(filepath, orient="records", force_ascii=False, indent=2)
        else:
            raise ValueError(f"Unknown output format: {output_format}")

        logger.info(f"Saved {len(data)} items to: {filepath}")
        return filepath

    def append(
        self,
        data: list[str],
        filename: str,
        column_name: str = "value",
        deduplicate: bool = True
    ) -> int:
        """Append data to a file incrementally (thread-safe).

        Args:
            data: List of values to append
            filename: Filename (with extension)
            column_name: Column header name
            deduplicate: Skip duplicates based on existing content

        Returns:
            Number of new items added
        """
        with self._lock:
            filepath = self.output_dir / filename
            existing: set[str] = set()

            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        value = line.strip()
                        if value and value != column_name:
                            existing.add(value)

            if deduplicate:
                new_items = [item for item in data if item not in existing]
            else:
                new_items = data

            if not new_items:
                return 0

            write_header = not filepath.exists()

            with open(filepath, "a", encoding="utf-8") as f:
                if write_header:
                    f.write(f"{column_name}\n")
                for item in new_items:
                    f.write(f"{item}\n")

            logger.debug(f"Appended {len(new_items)} items to {filepath}")
            return len(new_items)

    def load_existing(self, filename: str, column_name: str = "value") -> set[str]:
        """Load existing values from a file.

        Args:
            filename: Filename to load
            column_name: Column header to skip

        Returns:
            Set of existing values
        """
        filepath = self.output_dir / filename
        existing: set[str] = set()

        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    value = line.strip()
                    if value and value != column_name:
                        existing.add(value)
            logger.info(f"Loaded {len(existing)} existing items from {filepath}")

        return existing
