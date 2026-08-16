import csv
import json
import os
from typing import Any

from pydantic import ValidationError

from scraper.schema import BookSchema


class DataNormalizer:
    """Normalizes and validates raw scraped records."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def normalize_record(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw fields (e.g., price string to float)."""
        normalized = dict(raw_record)

        # Normalize price
        price_text = normalized.get("price_text", "")
        if price_text:
            # Remove any non-numeric characters except the dot
            clean_price = "".join(c for c in price_text if c.isdigit() or c == ".")
            try:
                normalized["price_gbp"] = float(clean_price)
            except ValueError:
                normalized["price_gbp"] = 0.0
        else:
            normalized["price_gbp"] = 0.0

        return normalized

    def _compute_changes(self, old_records: list[dict[str, Any]], new_records: list[dict[str, Any]]) -> dict[str, int]:
        """Compute changes between old and new records ignoring fetched_at."""
        old_urls = {r["product_url"]: r for r in old_records}
        new_urls = {r["product_url"]: r for r in new_records}
        
        stats = {"new": 0, "changed": 0, "unchanged": 0, "gone": 0}
        
        for url, new_rec in new_urls.items():
            if url not in old_urls:
                stats["new"] += 1
            else:
                old_rec = old_urls[url]
                # Compare ignoring 'fetched_at'
                old_rec_clean = {k: v for k, v in old_rec.items() if k != "fetched_at"}
                new_rec_clean = {k: v for k, v in new_rec.items() if k != "fetched_at"}
                if old_rec_clean == new_rec_clean:
                    stats["unchanged"] += 1
                else:
                    stats["changed"] += 1
                    
        for url in old_urls:
            if url not in new_urls:
                stats["gone"] += 1
                
        return stats

    def validate_and_store(self, raw_records: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Normalize, validate, and separate into good records and errors.
        Ensures idempotency by deduplicating on product_url.
        """
        good_records: dict[str, dict[str, Any]] = {}
        errors: list[dict[str, Any]] = []

        for raw in raw_records:
            normalized = self.normalize_record(raw)
            try:
                # Validate using Pydantic schema
                book = BookSchema(**normalized)
                
                # Use canonical URL for idempotency (deduplication)
                canonical_url = str(book.product_url)
                good_records[canonical_url] = book.model_dump(mode="json")
            except ValidationError as e:
                errors.append({
                    "raw_record": raw,
                    "errors": json.loads(e.json())
                })
            except Exception as e:  # noqa: BLE001
                errors.append({
                    "raw_record": raw,
                    "errors": str(e)
                })

        # Save to files
        books_path = os.path.join(self.output_dir, "books.json")
        errors_path = os.path.join(self.output_dir, "errors.json")
        csv_path = os.path.join(self.output_dir, "books.csv")

        final_good = list(good_records.values())
        
        # Change Detection
        old_records = []
        if os.path.exists(books_path):
            try:
                with open(books_path, "r", encoding="utf-8") as f:
                    old_records = json.load(f)
            except (OSError, json.JSONDecodeError):
                old_records = []
                
        changes = self._compute_changes(old_records, final_good)

        with open(books_path, "w", encoding="utf-8") as f:
            json.dump(final_good, f, indent=2, ensure_ascii=False)

        with open(errors_path, "w", encoding="utf-8") as f:
            json.dump(errors, f, indent=2, ensure_ascii=False)
            
        # Export to CSV
        if final_good:
            fieldnames = list(final_good[0].keys())
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(final_good)

        return {
            "total_processed": len(raw_records),
            "good_count": len(final_good),
            "error_count": len(errors),
            "books_file": books_path,
            "errors_file": errors_path,
            "csv_file": csv_path if final_good else None,
            "changes": changes,
        }
