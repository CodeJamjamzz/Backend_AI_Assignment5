"""Tests for Stage 0: Target Classification & Robots.txt checking."""

from scraper.classifier import TargetClassifier


def test_target_classification_properties():
    classification = TargetClassifier.get_target_classification()
    assert classification["target"] == "Books to Scrape"
    assert classification["is_sandbox"] is True
    assert classification["scope"]["max_catalogue_pages"] == 3
    assert classification["scope"]["total_target_books"] == 60
    assert (
        classification["ethics_statement"]
        == "I will not reuse this code on another site without checking its rules and terms first."
    )


def test_robots_txt_handling():
    robots = TargetClassifier.check_robots_txt()
    assert "status_code" in robots
    assert "found" in robots
    assert robots["summary"] == "no robots file found" or robots["status_code"] == 404
