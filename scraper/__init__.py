"""Polite Scraper Package for FlyRank Assignment A9."""

from scraper.classifier import TargetClassifier
from scraper.crawler import CatalogueCrawler
from scraper.extractor import BookExtractor
from scraper.fetcher import PoliteFetcher

__all__ = ["BookExtractor", "CatalogueCrawler", "PoliteFetcher", "TargetClassifier"]
