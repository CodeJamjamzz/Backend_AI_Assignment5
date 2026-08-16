"""Raw record extractor for book detail pages."""

import hashlib
from datetime import datetime, timezone
from typing import Any

from bs4 import BeautifulSoup

from scraper.fetcher import PoliteFetcher


class BookExtractor:
    """Extracts raw provenance-rich book records from detail HTML pages."""

    def __init__(self, fetcher: PoliteFetcher | None = None):
        self.fetcher = fetcher or PoliteFetcher()

    @staticmethod
    def _generate_cache_key(url: str) -> str:
        """Generate a safe, readable cache filename for a book URL."""
        # e.g., 'a-light-in-the-attic_1000' from '.../a-light-in-the-attic_1000/index.html'
        parts = [p for p in url.split("/") if p and p != "index.html"]
        slug = parts[-1] if parts else "book"
        slug_clean = "".join(c if c.isalnum() or c in "-_" else "_" for c in slug)
        hash_suffix = hashlib.md5(url.encode("utf-8")).hexdigest()[:6]
        return f"book-{slug_clean}-{hash_suffix}.html"

    def extract_raw_record(
        self,
        html_content: str,
        product_url: str,
        source_page: str,
        fetched_at: str | None = None,
    ) -> dict[str, Any]:
        """
        Parses a book detail page HTML and extracts raw untransformed fields.
        Selectors are aimed specifically at the product section of the document.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        product_main = soup.select_one("div.product_main")

        if not product_main:
            raise ValueError(f"Could not locate div.product_main in HTML for {product_url}")

        # Title: inside div.product_main h1
        title_el = product_main.select_one("h1")
        title = title_el.get_text(strip=True) if title_el else ""

        # Price text: div.product_main p.price_color
        price_el = product_main.select_one("p.price_color")
        price_text = price_el.get_text(strip=True) if price_el else ""

        # Availability text: div.product_main p.availability or p.instock
        avail_el = product_main.select_one("p.availability, p.instock")
        availability_text = avail_el.get_text(strip=True) if avail_el else ""

        # Rating text: div.product_main p.star-rating class name (One, Two, Three, Four, Five)
        rating_el = product_main.select_one("p.star-rating")
        rating_text = ""
        if rating_el and rating_el.get("class"):
            rating_classes = [c for c in rating_el["class"] if c != "star-rating"]
            rating_text = rating_classes[0] if rating_classes else ""

        # Description: #product_description + p or #product_description ~ p
        # If absent or empty, store None (null in JSON) — never invent text
        desc_heading = soup.select_one("#product_description")
        description: str | None = None
        if desc_heading:
            desc_p = desc_heading.find_next_sibling("p")
            if desc_p:
                text = desc_p.get_text(strip=True)
                if text:
                    description = text

        if not fetched_at:
            fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        return {
            "title": title,
            "product_url": product_url,
            "price_text": price_text,
            "availability_text": availability_text,
            "rating_text": rating_text,
            "description": description,
            "source_page": source_page,
            "fetched_at": fetched_at,
        }

    def fetch_and_extract_book(
        self,
        product_url: str,
        source_page: str,
        force_refresh: bool = False,
    ) -> tuple[dict[str, Any], bool]:
        """Fetch (or read from cache) and extract a single book record."""
        cache_filename = self._generate_cache_key(product_url)
        html_content, is_cache_hit, _, _ = self.fetcher.fetch(
            product_url,
            cache_filename=cache_filename,
            force_refresh=force_refresh,
        )
        record = self.extract_raw_record(
            html_content=html_content,
            product_url=product_url,
            source_page=source_page,
        )
        return record, is_cache_hit

    def extract_all(
        self,
        discovered_items: list[dict[str, str]],
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Fetches and extracts raw records for all discovered book items.

        Args:
            discovered_items: List of dicts with keys {'url', 'source_page'}
        """
        records: list[dict[str, Any]] = []
        failed_urls: list[str] = []
        cache_hits = 0

        for item in discovered_items:
            url = item["url"]
            source_page = item.get("source_page", "")
            try:
                record, is_cache_hit = self.fetch_and_extract_book(
                    product_url=url,
                    source_page=source_page,
                    force_refresh=force_refresh,
                )
                records.append(record)
                if is_cache_hit:
                    cache_hits += 1
            except Exception as e:  # noqa: BLE001
                print(f"[EXTRACTION ERROR] Skipping {url} due to error: {e}")
                failed_urls.append(url)
                
        return {
            "records": records,
            "failed_urls": failed_urls,
            "cache_hits": cache_hits
        }
