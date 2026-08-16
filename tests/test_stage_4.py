import json
import os
import pytest
from pydantic import HttpUrl

from scraper.normalizer import DataNormalizer
from scraper.schema import BookSchema


def test_normalizer_price_parsing():
    normalizer = DataNormalizer(output_dir="test_output")
    raw = {
        "title": "Test Book",
        "product_url": "https://books.toscrape.com/catalogue/test_1/index.html",
        "price_text": "£51.77",
        "availability_text": "In stock (22 available)",
        "rating_text": "Three",
        "description": "A description.",
        "source_page": "https://books.toscrape.com/catalogue/page-1.html",
        "fetched_at": "2026-08-16T14:16:25Z"
    }
    
    normalized = normalizer.normalize_record(raw)
    assert normalized["price_gbp"] == 51.77
    assert normalized["price_text"] == "£51.77"


def test_validate_and_store(tmp_path):
    output_dir = str(tmp_path / "output")
    normalizer = DataNormalizer(output_dir=output_dir)
    
    raw_records = [
        {
            "title": "Good Book",
            "product_url": "https://books.toscrape.com/catalogue/good_1/index.html",
            "price_text": "£10.00",
            "availability_text": "In stock",
            "rating_text": "One",
            "description": None,
            "source_page": "https://books.toscrape.com/catalogue/page-1.html",
            "fetched_at": "2026-08-16T14:16:25Z"
        },
        {
            "title": "Bad Book",
            # Missing product_url, which is required
            "price_text": "£20.00",
            "availability_text": "In stock",
            "rating_text": "Two",
            "description": None,
            "source_page": "https://books.toscrape.com/catalogue/page-1.html",
            "fetched_at": "2026-08-16T14:16:25Z"
        }
    ]
    
    result = normalizer.validate_and_store(raw_records)
    
    assert result["total_processed"] == 2
    assert result["good_count"] == 1
    assert result["error_count"] == 1
    
    # Check output files
    assert os.path.exists(result["books_file"])
    assert os.path.exists(result["errors_file"])
    
    with open(result["books_file"], "r", encoding="utf-8") as f:
        books = json.load(f)
        assert len(books) == 1
        assert books[0]["title"] == "Good Book"
        assert books[0]["price_gbp"] == 10.0
