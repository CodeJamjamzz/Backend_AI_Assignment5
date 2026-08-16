# The Polite Scraper — Backend AI Engineering

A polite, robust, and strongly typed web scraping pipeline integrated with a **FastAPI** backend and CLI. It extracts book details from the Books to Scrape sandbox, transforms messy HTML into validated JSON records, survives network/parsing failures gracefully, and generates transparent execution reports.

## 🎯 Target Classification (Stage 0)

- **Target Site:** [Books to Scrape](https://books.toscrape.com/)
- **Why this target:** As stated directly on [toscrape.com](https://toscrape.com/), Books to Scrape is *"a fictional bookstore that desperately wants to be scraped. It's a safe place for beginners learning web scraping and for developers validating their scraping technologies as well."* It is an explicitly provided public sandbox for practicing scraping techniques.
- **Scraping Scope:** Strictly limited to the first **3 catalogue pages** (a total of **60 books**).
- **Data Collected:** Book Title, Price, Star Rating, Availability / Stock Count, and Product Description.
- **Robots.txt Analysis:** Request to `https://books.toscrape.com/robots.txt` returned `404 Not Found` (**no robots file found**). As a sandbox with explicit site-level permission, no crawling restrictions are defined.

## ⚖️ Ethics & Best Practices

> **Ethics Statement:** Use an official API when one exists; never bypass logins, paywalls, or blocks; collect only what you need. I will not reuse this code on another site without checking its rules and terms first.

**Why this assignment used standard HTTP requests instead of a headless browser:**
The data is already present in the raw HTML that the server sends, so launching a heavy browser (like Puppeteer or Playwright) would only add unnecessary compute cost, memory overhead, and latency.

## 🤝 Politeness Rules Implemented

This scraper is designed to be a good internet citizen:
- **User-Agent:** Sends a transparent, custom identifier: `FlyRankInternshipA9/1.0 (+https://github.com/CodeJamjamzz/Backend_AI_Assignment5)`
- **Rate Limiting:** Enforces a strict `0.5` second delay between all live network requests.
- **Timeout Protection:** Gives up after `10.0` seconds instead of hanging connections indefinitely.
- **Local Caching:** Caches all fetched HTML to a local `cache/` directory. Repeated runs read from the disk cache, ensuring the target server only ever fields a request exactly once during development.

## 🚀 Quick Start (Installation & Run)

**Lane:** Python 3.10+

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Full Pipeline (Stage 5)
```bash
python -m src.main --stage 5
```
*(This command will discover URLs, fetch/extract data, normalize it, validate it against the schema, survive any injected bad links, save exactly 60 records to `output/books.json`, and print the final report).*

## 🏗️ Record Schema

Every valid record extracted conforms strictly to this Pydantic schema:

```json
{
  "title": "string (Required)",
  "product_url": "string (Required, Canonical ID)",
  "price_text": "string (Required, e.g., '£51.77')",
  "price_gbp": "float (Required, e.g., 51.77)",
  "availability_text": "string (Required)",
  "rating_text": "string (Required)",
  "description": "string | null (Optional)",
  "source_page": "string (Required)",
  "fetched_at": "string (Required, ISO 8601 Timestamp)"
}
```

## 📊 Proof of Execution (Run Report)

Below is an honest, generated report from a successful run (with one purposefully injected fake URL to prove failure resilience):

```json
{
  "start_time": "2026-08-16T14:45:21.038968+00:00",
  "duration_seconds": 2.57,
  "pages_fetched": 61,
  "cache_hits": 60,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}
```

## ⚠️ Honest Limitation

**Fragile Extraction Logic:** The HTML extraction process relies heavily on specific CSS classes (like `div.product_main`, `p.price_color`, and `p.star-rating`). If the target website's developers change their frontend layout, redesign the page, or rename their CSS classes, the extraction logic will immediately break and require manual updates to the BeautifulSoup selectors.
