"""Catalogue crawler for discovering book links across paginated catalogue pages."""

from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from scraper.fetcher import PoliteFetcher


class CatalogueCrawler:
    """Discovers book URLs across catalogue pages by following pagination links."""

    DEFAULT_START_URL = "https://books.toscrape.com/catalogue/page-1.html"

    def __init__(self, fetcher: Optional[PoliteFetcher] = None):
        self.fetcher = fetcher or PoliteFetcher()

    def extract_book_links(self, html_content: str, page_url: str) -> List[str]:
        """
        Extracts all book detail links from a catalogue HTML page and converts
        them into absolute URLs using urllib.parse.urljoin.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        book_links: List[str] = []

        for article in soup.select("article.product_pod"):
            h3_link = article.select_one("h3 a")
            if h3_link and h3_link.get("href"):
                raw_href = h3_link["href"].strip()
                absolute_url = urljoin(page_url, raw_href)
                book_links.append(absolute_url)

        return book_links

    def extract_next_page_url(self, html_content: str, current_page_url: str) -> Optional[str]:
        """
        Extracts the 'next' pagination link from a catalogue HTML page
        and converts it into an absolute URL.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        next_li = soup.select_one("li.next a")
        if next_li and next_li.get("href"):
            raw_href = next_li["href"].strip()
            return urljoin(current_page_url, raw_href)
        return None

    def crawl_catalogue(
        self,
        start_url: str = DEFAULT_START_URL,
        max_pages: int = 3,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Crawls up to `max_pages` catalogue pages, collecting all book links,
        deduplicating them, and respecting polite delays.
        """
        current_url: Optional[str] = start_url
        page_index = 1
        all_book_links: List[str] = []
        visited_pages: List[str] = []

        while current_url and page_index <= max_pages:
            cache_file = f"catalogue-page-{page_index}.html"
            html_content, _, _, _ = self.fetcher.fetch(
                current_url,
                cache_filename=cache_file,
                force_refresh=force_refresh,
            )
            visited_pages.append(current_url)

            page_book_links = self.extract_book_links(html_content, current_url)
            all_book_links.extend(page_book_links)

            # Look up next page URL dynamically from the page markup
            current_url = self.extract_next_page_url(html_content, current_url)
            page_index += 1

        # Deduplicate while preserving discovery order
        seen: Set[str] = set()
        unique_book_links: List[str] = []
        for link in all_book_links:
            if link not in seen:
                seen.add(link)
                unique_book_links.append(link)

        duplicates_removed = len(all_book_links) - len(unique_book_links)

        return {
            "catalogue_pages": len(visited_pages),
            "discovered": len(unique_book_links),
            "total_links_found": len(all_book_links),
            "duplicates_removed": duplicates_removed,
            "book_urls": unique_book_links,
            "visited_pages": visited_pages,
        }
