"""Tests for Stage 1: Fetch and cache HTML."""

import os
import shutil
import pytest
from scraper.fetcher import PoliteFetcher


@pytest.fixture
def temp_fetcher(tmp_path):
    cache_dir = str(tmp_path / "cache")
    return PoliteFetcher(cache_dir=cache_dir, polite_delay=0.1, timeout=10.0)


def test_stage_1_fetch_and_cache(temp_fetcher):
    url = "https://books.toscrape.com/catalogue/page-1.html"
    cache_file = "catalogue-page-1.html"

    # First call: live network fetch
    content_1, is_cache_1, status_1, size_1 = temp_fetcher.fetch(url, cache_filename=cache_file)
    assert not is_cache_1
    assert status_1 == 200
    assert size_1 > 0
    assert "<html" in content_1.lower()
    assert os.path.exists(os.path.join(temp_fetcher.cache_dir, cache_file))

    # Second call: cache hit
    content_2, is_cache_2, status_2, size_2 = temp_fetcher.fetch(url, cache_filename=cache_file)
    assert is_cache_2
    assert status_2 == 200
    assert size_2 == size_1
    assert content_2 == content_1
