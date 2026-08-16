"""Tests for Stage 2: Discover three catalogue pages and book URLs."""

import pytest

from scraper.crawler import CatalogueCrawler
from scraper.fetcher import PoliteFetcher


@pytest.fixture
def temp_crawler(tmp_path):
    cache_dir = str(tmp_path / "cache")
    fetcher = PoliteFetcher(cache_dir=cache_dir, polite_delay=0.1, timeout=10.0)
    return CatalogueCrawler(fetcher=fetcher)


def test_stage_2_crawl_three_pages(temp_crawler):
    # Run 1: Network fetch & cache creation
    result_1 = temp_crawler.crawl_catalogue(max_pages=3)
    assert result_1["catalogue_pages"] == 3
    assert result_1["discovered"] == 60
    assert len(result_1["book_urls"]) == 60
    assert all(url.startswith("https://books.toscrape.com/catalogue/") for url in result_1["book_urls"])

    # Run 2: Cache hit
    result_2 = temp_crawler.crawl_catalogue(max_pages=3)
    assert result_2["catalogue_pages"] == 3
    assert result_2["discovered"] == 60
    assert result_2["book_urls"] == result_1["book_urls"]
