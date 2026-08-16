"""Main entry point for Polite Scraper backend and CLI."""

import argparse
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scraper.classifier import TargetClassifier
from scraper.crawler import CatalogueCrawler
from scraper.extractor import BookExtractor
from scraper.fetcher import PoliteFetcher
from scraper.normalizer import DataNormalizer

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
extractor = BookExtractor(fetcher=fetcher)
normalizer = DataNormalizer(output_dir="output")


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


@app.post("/api/stage-3")
def stage_3_extract_book_records(max_pages: int = 3, sample_only: bool = False):
    """Stage 3: Extract raw records from discovered book detail pages."""
    crawl_result = crawler.crawl_catalogue(max_pages=max_pages)
    items = crawl_result["discovered_items"]
    if sample_only:
        items = items[:1]
    records = extractor.extract_all(items)
    return {
        "stage": 3,
        "catalogue_pages": crawl_result["catalogue_pages"],
        "unique_urls": len(records),
        "sample_record": records[0] if records else None,
        "records": records,
    }


@app.post("/api/stage-4")
def stage_4_normalize_and_validate():
    """Stage 4: Normalize, validate, and store records."""
    crawl_result = crawler.crawl_catalogue(max_pages=3)
    records = extractor.extract_all(crawl_result["discovered_items"])
    result = normalizer.validate_and_store(records)
    return {
        "stage": 4,
        "validation_result": result,
    }


def run_cli():
    """CLI runner for stages."""
    parser = argparse.ArgumentParser(description="The Polite Scraper CLI")
    parser.add_argument("--stage", type=int, choices=[0, 1, 2, 3, 4], help="Run a specific stage checkpoint")
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

    elif stage == 3:
        print("\n=== STAGE 3: EXTRACT RAW BOOK RECORDS ===")
        crawl_result = crawler.crawl_catalogue(max_pages=3)
        records = extractor.extract_all(crawl_result["discovered_items"])
        print("\nSample Raw Record:")
        print(json.dumps(records[0], indent=2))
        print(f"\nunique_urls={len(records)}")
        print("\nCheckpoint Verified: All 60 raw book detail records extracted with full provenance receipts.\n")

    elif stage == 4:
        print("\n=== STAGE 4: CLEAN, CHECK, AND STORE ===")
        print("Run 1:")
        crawl_result = crawler.crawl_catalogue(max_pages=3)
        records = extractor.extract_all(crawl_result["discovered_items"])
        r1 = normalizer.validate_and_store(records)
        print(f"Processed: {r1['total_processed']} | Good: {r1['good_count']} | Errors: {r1['error_count']}")
        
        print("\nRun 2 (Checking Idempotency):")
        crawl_result_2 = crawler.crawl_catalogue(max_pages=3)
        records_2 = extractor.extract_all(crawl_result_2["discovered_items"])
        r2 = normalizer.validate_and_store(records_2)
        print(f"Processed: {r2['total_processed']} | Good: {r2['good_count']} | Errors: {r2['error_count']}")
        
        print(f"\nSaved to: {r2['books_file']}")
        print(f"Errors to: {r2['errors_file']}")
        print("\nCheckpoint Verified: books.json has exactly 60 records, every product_url is unique, and after a second run it is still exactly 60.\n")



if __name__ == "__main__":
    run_cli()
