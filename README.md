# YouTube Channel Scraper

Automatically collect YouTube channel data from search keywords.

## What You Get

- Channel name
- Channel URL
- Subscriber count
- Collected as CSV or JSON file

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Add Your Keywords

Edit `config/keywords.txt`:
```
your keyword 1
your keyword 2
your keyword 3
```

### 3. Run
```bash
python batch.py -t 500
```

This collects up to 500 channels based on your keywords.

### 4. Get Results

Find your data in `output/all_channels.csv`

## Options

| Option | What it does | Default |
|--------|--------------|---------|
| `-t` | How many channels to collect | 1000 |
| `-w` | Speed (more = faster) | 5 |

Example:
```bash
python batch.py -t 1000 -w 10
```

## Single Query Mode

For a single search query:
```bash
python main.py "python tutorial"
python main.py "web development" -c channels --no-save
```

## Output Sample

| channel_name | channel_url | subscribers |
|--------------|-------------|-------------|
| Corey Schafer | https://youtube.com/@coreyms | 1.2M |
| Tech With Tim | https://youtube.com/@TechWithTim | 1.4M |

## Project Structure

```
src/
├── core/
│   ├── driver.py      # WebDriver factory
│   └── output.py      # Output file manager
├── scrapers/
│   ├── base.py        # Base scraper interface
│   └── youtube.py     # YouTube scraper
├── extractors/
│   ├── base.py        # Base extractor
│   └── channel.py     # Channel data extractor
└── config_loader.py   # YAML config loader
```

## Extending

Add a new extractor:
```python
from src.extractors.base import BaseExtractor

class VideoExtractor(BaseExtractor):
    def extract(self, query: str) -> list[dict]:
        # Your implementation
        pass
```

Add a new platform scraper:
```python
from src.scrapers.base import BaseScraper

class InstagramScraper(BaseScraper):
    def scrape(self, query: str) -> list[dict]:
        # Your implementation
        pass
```

## Configuration

Edit `config/channels.yaml` to customize:
- Search URL parameters
- CSS selectors
- Output format (csv/json)
- Scroll options

## Need Help?

Contact me if you have any questions.
