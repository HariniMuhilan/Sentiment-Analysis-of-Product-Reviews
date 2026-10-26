"""Prepare an unambiguous product-level subset of the Olist review corpus.

Olist reviews attach to an order rather than directly to a product. To avoid
assigning one order-level opinion to several products, this script retains only
orders containing exactly one distinct product. It preserves original text,
ratings, identifiers, source category, and collection date. It does not score
sentiment or treat ratings as human-annotated sentiment labels.
"""

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "Datasets" / "OlistBrazilianEcommerce" / "raw"
OUTPUT = ROOT / "Datasets" / "OlistBrazilianEcommerce" / "processed"


def read_category_translations(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {
            row["product_category_name"]: row["product_category_name_english"]
            for row in csv.DictReader(handle)
            if row.get("product_category_name")
        }


def prepare() -> dict:
    required = [
        "olist_order_reviews_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_products_dataset.csv",
        "product_category_name_translation.csv",
    ]
    missing = [name for name in required if not (RAW / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"Missing Olist source files: {', '.join(missing)}. See Datasets/OlistBrazilianEcommerce/README.md."
        )

    translations = read_category_translations(RAW / required[3])
    product_categories: dict[str, str] = {}
    with (RAW / required[2]).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            product_id = row.get("product_id")
            source_category = row.get("product_category_name") or "uncategorized"
            if product_id:
                category = translations.get(source_category, source_category)
                product_categories[product_id] = category.replace("_", " ").strip()

    order_products: dict[str, set[str]] = defaultdict(set)
    with (RAW / required[1]).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            order_id, product_id = row.get("order_id"), row.get("product_id")
            if order_id and product_id:
                order_products[order_id].add(product_id)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT / "olist_single_product_reviews.csv"
    counts = Counter()
    category_counts = Counter()
    fieldnames = [
        "review_id",
        "order_id",
        "product_id",
        "product_category",
        "rating",
        "review_title",
        "review_text",
        "review_date",
        "source_platform",
    ]

    with (RAW / required[0]).open(encoding="utf-8-sig", newline="") as source, output_path.open(
        "w", encoding="utf-8", newline=""
    ) as destination:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            counts["source_review_rows"] += 1
            order_id = row.get("order_id", "")
            product_ids = order_products.get(order_id, set())
            if len(product_ids) != 1:
                counts["excluded_ambiguous_or_missing_product_link"] += 1
                continue

            review_title = (row.get("review_comment_title") or "").strip()
            review_body = (row.get("review_comment_message") or "").strip()
            review_text = "\n".join(part for part in (review_title, review_body) if part)
            if not review_text:
                counts["excluded_without_written_review_text"] += 1
                continue

            try:
                rating = int(row.get("review_score", ""))
            except ValueError:
                counts["excluded_invalid_rating"] += 1
                continue
            if rating < 1 or rating > 5:
                counts["excluded_invalid_rating"] += 1
                continue

            product_id = next(iter(product_ids))
            category = product_categories.get(product_id, "uncategorized")
            writer.writerow(
                {
                    "review_id": row.get("review_id", ""),
                    "order_id": order_id,
                    "product_id": product_id,
                    "product_category": category,
                    "rating": rating,
                    "review_title": review_title,
                    "review_text": review_text,
                    "review_date": row.get("review_creation_date", ""),
                    "source_platform": "olist_brazil",
                }
            )
            counts["prepared_reviews"] += 1
            category_counts[category] += 1

    summary = {
        "dataset": "Brazilian E-Commerce Public Dataset by Olist",
        "source_review_rows": counts["source_review_rows"],
        "prepared_reviews": counts["prepared_reviews"],
        "excluded_ambiguous_or_missing_product_link": counts[
            "excluded_ambiguous_or_missing_product_link"
        ],
        "excluded_without_written_review_text": counts[
            "excluded_without_written_review_text"
        ],
        "excluded_invalid_rating": counts["excluded_invalid_rating"],
        "category_counts": dict(sorted(category_counts.items())),
        "prepared_file": str(output_path.relative_to(ROOT)),
        "sentiment_scoring_performed": False,
        "rating_interpretation": "Observed 1-to-5 order rating; not human-annotated text sentiment.",
        "product_link_rule": "Retain only orders with exactly one distinct product ID.",
    }
    (OUTPUT / "preparation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    result = prepare()
    print(json.dumps(result, indent=2, ensure_ascii=False))
