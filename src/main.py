"""Main entry point for Polite Scraper backend and CLI."""

import argparse
import json
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scraper.classifier import TargetClassifier

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


def run_cli():
    """CLI runner for stage 0 and verification."""
    parser = argparse.ArgumentParser(description="The Polite Scraper CLI")
    parser.add_argument("--classify", action="store_true", help="Run Stage 0: Classify target and check robots.txt")
    args = parser.parse_args()

    if args.classify or len(sys.argv) == 1:
        print("\n=== STAGE 0: TARGET CLASSIFICATION ===")
        classification = TargetClassifier.get_target_classification()
        print(json.dumps(classification, indent=2))
        print("\nCheckpoint Verified:")
        print(f"Target: {classification['target']}")
        print(f"Robots result: {classification['robots_txt']['summary']}")
        print(f"Statement: \"{classification['ethics_statement']}\"\n")


if __name__ == "__main__":
    run_cli()
