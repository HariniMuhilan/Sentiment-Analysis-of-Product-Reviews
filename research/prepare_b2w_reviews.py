"""Create a research-ready, privacy-minimized B2W-Reviews01 corpus copy.

The released source includes reviewer identifiers and demographic fields that
are unnecessary for the current product review sentiment research. This
script retains product/review fields only and creates a deterministic review
key without including the source reviewer ID.
"""

import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Datasets" / "B2WReviews01" / "raw" / "B2W-Reviews01.csv"
OUTPUT_DIR = ROOT / "Datasets" / "B2WReviews01" / "processed"
OUTPUT = OUTPUT_DIR / "B2W-Reviews01-clean.csv.gz"


def stable_review_id(row: dict[str, str], review_text: str) -> str:
    material = "|".join(
        [
            row.get("product_id", ""),
            row.get("submission_date", ""),
            row.get("overall_rating", ""),
            review_text,
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def prepare() -> dict:
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Missing {SOURCE.relative_to(ROOT)}. See Datasets/B2WReviews01/README.md for download instructions."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = [
        "review_id",
        "product_id",
        "product_name",
        "category_level_1",
        "category_level_2",
        "review_title",
        "rating",
        "recommend_to_a_friend",
        "review_text",
        "review_date",
        "source_platform",
    ]
    counts = Counter()
    categories = Counter()

    with SOURCE.open(encoding="utf-8-sig", newline="") as source, gzip.open(
        OUTPUT, "wt", encoding="utf-8", newline=""
    ) as destination:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        for row in reader:
            counts["source_rows"] += 1
            title = (row.get("review_title") or "").strip()
            body = (row.get("review_text") or "").strip()
            review_text = "\n".join(part for part in (title, body) if part)
            if not review_text:
                counts["excluded_without_text"] += 1
                continue

            try:
                rating = int(row.get("overall_rating", ""))
            except ValueError:
                counts["excluded_invalid_rating"] += 1
                continue
            if not 1 <= rating <= 5:
                counts["excluded_invalid_rating"] += 1
                continue

            category = (row.get("site_category_lv1") or "Unspecified").strip()
            writer.writerow(
                {
                    "review_id": stable_review_id(row, review_text),
                    "product_id": (row.get("product_id") or "").strip(),
                    "product_name": (row.get("product_name") or "").strip(),
                    "category_level_1": category,
                    "category_level_2": (row.get("site_category_lv2") or "").strip(),
                    "review_title": title,
                    "rating": rating,
                    "recommend_to_a_friend": (row.get("recommend_to_a_friend") or "").strip(),
                    "review_text": review_text,
                    "review_date": (row.get("submission_date") or "").strip(),
                    "source_platform": "americanas_brazil",
                }
            )
            counts["prepared_reviews"] += 1
            categories[category] += 1

    summary = {
        "dataset": "B2W-Reviews01",
        "source_platform": "Americanas.com (Brazil)",
        "source_rows": counts["source_rows"],
        "prepared_reviews": counts["prepared_reviews"],
        "excluded_without_text": counts["excluded_without_text"],
        "excluded_invalid_rating": counts["excluded_invalid_rating"],
        "category_counts": dict(sorted(categories.items())),
        "prepared_file": str(OUTPUT.relative_to(ROOT)),
        "removed_from_derivative": ["reviewer_id", "reviewer_birth_year", "reviewer_gender", "reviewer_state"],
        "sentiment_scoring_performed": False,
        "rating_interpretation": "Observed 1-to-5 product rating; not human-annotated text sentiment.",
    }
    (OUTPUT_DIR / "preparation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2, ensure_ascii=False))
