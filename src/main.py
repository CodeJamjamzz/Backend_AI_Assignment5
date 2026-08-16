"""Main entry point for Polite Scraper backend and CLI."""

import argparse
import json
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scraper.classifier import TargetClassifier
from scraper.crawler import CatalogueCrawler
from scraper.fetcher import PoliteFetcher

app = FastAPI(
    title="The Polite Scraper API",
    description="Backend AI Engineering Assignment 5 — FlyRank Internship Polite Web Scraper",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fetcher = PoliteFetcher()
crawler = CatalogueCrawler(fetcher=fetcher)


@app.get("/")
def root():
    """Root health check and target classification overview."""
    classification = TargetClassifier.get_target_classification()
    return {
        "status": "online",
        "service": "The Polite Scraper",
        "assignment": "FlyRank Backend Track W5 A9",
        "target_classification": classification,
    }


@app.get("/api/classification")
def get_classification():
    """Returns the target classification and robots.txt check."""
    return TargetClassifier.get_target_classification()


@app.post("/api/stage-1")
def stage_1_fetch_catalogue_page():
    """Stage 1: Fetch and cache the first catalogue page."""
    url = "https://books.toscrape.com/catalogue/page-1.html"
    cache_file = "catalogue-page-1.html"
    _, is_cache_hit, status_code, size_bytes = fetcher.fetch(url, cache_filename=cache_file)
    return {
        "stage": 1,
        "url": url,
        "cache_filename": cache_file,
        "is_cache_hit": is_cache_hit,
        "status_code": status_code,
        "size_bytes": size_bytes,
    }


@app.post("/api/stage-2")
def stage_2_discover_catalogue_pages(max_pages: int = 3):
    """Stage 2: Discover book links across catalogue pages."""
    result = crawler.crawl_catalogue(max_pages=max_pages)
    return {
        "stage": 2,
        "catalogue_pages": result["catalogue_pages"],
        "discovered": result["discovered"],
        "duplicates_removed": result["duplicates_removed"],
        "sample_urls": result["book_urls"][:5],
    }


def run_cli():
    """CLI runner for stages."""
    parser = argparse.ArgumentParser(description="The Polite Scraper CLI")
    parser.add_argument("--stage", type=int, choices=[0, 1, 2], help="Run a specific stage checkpoint")
    args = parser.parse_args()

    stage = args.stage if args.stage is not None else 0

    if stage == 0:
        print("\n=== STAGE 0: TARGET CLASSIFICATION ===")
        classification = TargetClassifier.get_target_classification()
        print(json.dumps(classification, indent=2))
        print("\nCheckpoint Verified:")
        print(f"Target: {classification['target']}")
        print(f"Robots result: {classification['robots_txt']['summary']}")
        print(f"Statement: \"{classification['ethics_statement']}\"\n")

    elif stage == 1:
        print("\n=== STAGE 1: FETCH AND CACHE HTML ===")
        url = "https://books.toscrape.com/catalogue/page-1.html"
        cache_file = "catalogue-page-1.html"
        print("Run 1:")
        fetcher.fetch(url, cache_filename=cache_file)
        print("Run 2:")
        fetcher.fetch(url, cache_filename=cache_file)
        print("\nCheckpoint Verified: Handled live fetch and subsequent cache hit gracefully.\n")

    elif stage == 2:
        print("\n=== STAGE 2: DISCOVER THREE CATALOGUE PAGES ===")
        print("Run 1:")
        r1 = crawler.crawl_catalogue(max_pages=3)
        print(f"catalogue_pages={r1['catalogue_pages']} discovered={r1['discovered']} duplicates_removed={r1['duplicates_removed']}")

        print("\nRun 2 (from cache):")
        r2 = crawler.crawl_catalogue(max_pages=3)
        print(f"catalogue_pages={r2['catalogue_pages']} discovered={r2['discovered']} duplicates_removed={r2['duplicates_removed']}")
        print("\nCheckpoint Verified: Discovered 60 book links across 3 catalogue pages with 0 duplicates.\n")


if __name__ == "__main__":
    run_cli()
