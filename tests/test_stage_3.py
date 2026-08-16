"""Tests for Stage 3: Extract raw book records."""

import pytest

from scraper.crawler import CatalogueCrawler
from scraper.extractor import BookExtractor
from scraper.fetcher import PoliteFetcher


@pytest.fixture
def temp_environment(tmp_path):
    cache_dir = str(tmp_path / "cache")
    fetcher = PoliteFetcher(cache_dir=cache_dir, polite_delay=0.1, timeout=10.0)
    crawler = CatalogueCrawler(fetcher=fetcher)
    extractor = BookExtractor(fetcher=fetcher)
    return {"fetcher": fetcher, "crawler": crawler, "extractor": extractor}


def test_stage_3_extract_single_record(temp_environment):
    extractor = temp_environment["extractor"]
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    source = "https://books.toscrape.com/catalogue/page-1.html"

    record = extractor.fetch_and_extract_book(product_url=url, source_page=source)

    assert record["title"] == "A Light in the Attic"
    assert record["product_url"] == url
    assert "£" in record["price_text"]
    assert "In stock" in record["availability_text"]
    assert record["rating_text"] == "Three"
    assert record["description"] is not None
    assert record["source_page"] == source
    assert record["fetched_at"].endswith("Z") or "T" in record["fetched_at"]


def test_stage_3_missing_description_handling(temp_environment):
    extractor = temp_environment["extractor"]
    html_without_desc = """
    <div class="product_main">
        <h1>Book Without Description</h1>
        <p class="price_color">£10.00</p>
        <p class="instock availability">In stock (5 available)</p>
        <p class="star-rating Four"></p>
    </div>
    """
    record = extractor.extract_raw_record(
        html_content=html_without_desc,
        product_url="https://books.toscrape.com/catalogue/sample_1/index.html",
        source_page="https://books.toscrape.com/catalogue/page-1.html",
    )
    assert record["title"] == "Book Without Description"
    assert record["description"] is None  # Must store None/null, never invent text
    assert record["rating_text"] == "Four"
