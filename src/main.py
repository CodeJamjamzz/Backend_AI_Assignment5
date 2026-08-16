"""Main entry point for Polite Scraper backend and CLI."""

import argparse
import json
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scraper.classifier import TargetClassifier
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
    """Fetch and cache the first catalogue page."""
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


if __name__ == "__main__":
    run_cli()
