"""Target classifier and robots.txt policy verification for polite scraping."""

import urllib.error
import urllib.request
from typing import Any


class TargetClassifier:
    """Classifies scraping target and performs initial permission checks."""

    TARGET_BASE_URL = "https://books.toscrape.com"
    ROBOTS_URL = "https://books.toscrape.com/robots.txt"
    MAX_CATALOGUE_PAGES = 3
    BOOKS_PER_PAGE = 20
    TOTAL_BOOKS_SCOPE = 60

    @classmethod
    def check_robots_txt(cls) -> dict[str, Any]:
        """Request the target robots.txt file to determine crawler policies."""
        headers = {"User-Agent": "PoliteScraper/1.0 (FlyRank Assignment 5; respectful sandbox scraper)"}
        req = urllib.request.Request(cls.ROBOTS_URL, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode("utf-8")
                return {
                    "status_code": response.status,
                    "found": True,
                    "content": content,
                    "summary": "robots.txt found and loaded",
                }
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {
                    "status_code": 404,
                    "found": False,
                    "content": "",
                    "summary": "no robots file found",
                }
            return {
                "status_code": e.code,
                "found": False,
                "content": "",
                "summary": f"HTTP error {e.code} while fetching robots.txt",
            }
        except urllib.error.URLError as e:
            return {
                "status_code": None,
                "found": False,
                "content": "",
                "summary": f"Connection error: {e!s}",
            }

    @classmethod
    def get_target_classification(cls) -> dict[str, Any]:
        """Return the target classification metadata."""
        robots_result = cls.check_robots_txt()
        return {
            "target": "Books to Scrape",
            "base_url": cls.TARGET_BASE_URL,
            "is_sandbox": True,
            "sandbox_permission_note": "A fictional bookstore that desperately wants to be scraped. It's a safe place for beginners learning web scraping.",
            "scope": {
                "max_catalogue_pages": cls.MAX_CATALOGUE_PAGES,
                "books_per_page": cls.BOOKS_PER_PAGE,
                "total_target_books": cls.TOTAL_BOOKS_SCOPE,
            },
            "data_collected": [
                "title",
                "price",
                "rating",
                "availability",
                "upc",
                "category",
                "description",
                "image_url",
            ],
            "robots_txt": robots_result,
            "ethics_statement": "I will not reuse this code on another site without checking its rules and terms first.",
        }
