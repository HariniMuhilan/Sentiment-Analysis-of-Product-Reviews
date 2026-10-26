"""Import local UCSD Amazon Reviews '23 research files into the app database.

The source corpus is made available primarily for research use and has no
license assigned by its curators. Do not redistribute the raw corpus or a
database containing its review text. See Datasets/research/README.md.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import Base, SessionLocal, engine
from app.models import AnalysisRun, Platform, Product, Review
from app.nlp.sentiment import MODEL_NAME, MODEL_VERSION, analyze_review_text

DATASET_ID = "AMAZON-REVIEWS-2023-UCSD"
DATASET_VERSION = "2023-09"
PLATFORM_CODE = "amazon_ucsd_2023"
CATEGORY_FILES = {
    "All_Beauty": ("All_Beauty.jsonl", "meta_All_Beauty.jsonl"),
    "Appliances": ("Appliances.jsonl", "meta_Appliances.jsonl"),
}


def load_products(metadata_path: Path, category: str) -> dict[str, tuple[str, str]]:
    products: dict[str, tuple[str, str]] = {}
    with metadata_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            asin = row.get("parent_asin")
            title = " ".join(str(row.get("title") or "").split())
            if asin and title:
                products[asin] = (title[:255], category)
    return products


def review_external_id(row: dict) -> str:
    stable_fields = "|".join(
        str(row.get(field) or "")
        for field in ("parent_asin", "asin", "user_id", "timestamp", "rating", "title", "text")
    )
    return hashlib.sha256(stable_fields.encode("utf-8")).hexdigest()


def import_category(db, category: str, data_dir: Path, batch_size: int, max_records: int | None) -> int:
    review_path, metadata_path = (data_dir / name for name in CATEGORY_FILES[category])
    if not review_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError(f"Missing files for {category}; see Datasets/research/README.md")

    print(f"Loading {category} product metadata...", flush=True)
    display_category = category.replace("_", " ")
    products = load_products(metadata_path, display_category)
    existing_products = {
        (name.casefold(), product_category)
        for name, product_category in db.query(Product.name, Product.category).all()
    }
    new_products = [
        {"name": name, "category": product_category}
        for name, product_category in products.values()
        if (name.casefold(), product_category) not in existing_products
    ]
    for offset in range(0, len(new_products), 1000):
        db.bulk_insert_mappings(Product, new_products[offset : offset + 1000])
    db.commit()

    product_ids: dict[tuple[str, str], int] = {
        (product.name.casefold(), product.category): product.id
        for product in db.query(Product.id, Product.name, Product.category).all()
        if product.category == display_category
    }
    asin_to_product_id = {
        asin: product_ids.get((name.casefold(), product_category))
        for asin, (name, product_category) in products.items()
    }

    platform = db.query(Platform).filter(Platform.code == PLATFORM_CODE).first()
    if platform is None:
        platform = Platform(
            code=PLATFORM_CODE,
            name="Amazon Research Corpus (UCSD 2023)",
            description="Historical Amazon product reviews collected through September 2023; research corpus, not live marketplace data.",
            source_info=(
                "McAuley Lab, Amazon Reviews 2023. Retrieved from the official Hugging Face dataset repository; "
                "category-specific raw reviews and item metadata."
            ),
            terms_info=(
                "Curators state no license is assigned and the dataset is made available primarily for research. "
                "Use locally for non-commercial research; do not redistribute raw review text or this database."
            ),
        )
        db.add(platform)
        db.commit()
        db.refresh(platform)

    existing_ids = set(
        value[0]
        for value in db.query(Review.external_id)
        .filter(Review.platform_id == platform.id, Review.external_id.isnot(None))
        .yield_per(10000)
    )
    run = AnalysisRun(
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        status="in_progress",
        notes=f"{DATASET_ID} {DATASET_VERSION}; category={category}; source rows read from {review_path.name}",
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    inserted = 0
    parsed = 0
    batch: list[Review] = []
    with review_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if max_records is not None and parsed >= max_records:
                break
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            parsed += 1
            review_text = " ".join(str(row.get("text") or "").split())
            if not review_text:
                continue
            ext_id = review_external_id(row)
            if ext_id in existing_ids:
                continue

            asin = row.get("parent_asin") or row.get("asin")
            product_name, product_category = products.get(
                asin, (f"Amazon item {asin or 'unknown'}", category)
            )
            rating = row.get("rating")
            try:
                rating = float(rating) if rating is not None else None
                if rating is not None and not 1 <= rating <= 5:
                    rating = None
            except (TypeError, ValueError):
                rating = None

            analysis = analyze_review_text(review_text, rating=rating)
            timestamp = row.get("timestamp")
            try:
                review_date = datetime.fromtimestamp(float(timestamp) / 1000, tz=timezone.utc)
            except (TypeError, ValueError, OSError, OverflowError):
                review_date = None

            batch.append(
                Review(
                    external_id=ext_id,
                    platform_id=platform.id,
                    product_id=asin_to_product_id.get(asin),
                    product_name=product_name,
                    category=product_category,
                    headline=str(row.get("title") or "")[:500] or None,
                    review_text=review_text,
                    rating=rating,
                    helpful_votes=int(row.get("helpful_vote") or 0),
                    review_date=review_date,
                    sentiment=analysis["sentiment"],
                    compound_score=analysis["compound_score"],
                    positive_score=analysis["positive_score"],
                    neutral_score=analysis["neutral_score"],
                    negative_score=analysis["negative_score"],
                    confidence=analysis["confidence"],
                    model_name=analysis["model_name"],
                    model_version=analysis["model_version"],
                    analyzed_at=analysis["analyzed_at"],
                )
            )
            existing_ids.add(ext_id)

            if len(batch) >= batch_size:
                db.bulk_save_objects(batch)
                db.commit()
                inserted += len(batch)
                batch.clear()
                if parsed % 50000 < batch_size:
                    print(f"{category}: read {parsed:,}, imported {inserted:,}", flush=True)

    if batch:
        db.bulk_save_objects(batch)
        db.commit()
        inserted += len(batch)

    run.records_processed = inserted
    run.status = "completed"
    run.completed_at = datetime.now(timezone.utc)
    db.commit()
    print(f"{category}: read {parsed:,}, imported {inserted:,} new reviews", flush=True)
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Import the local research copy of Amazon Reviews 2023.")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "Datasets/research/raw")
    parser.add_argument("--categories", nargs="+", choices=sorted(CATEGORY_FILES), default=sorted(CATEGORY_FILES))
    parser.add_argument("--batch-size", type=int, default=2000)
    parser.add_argument("--max-records", type=int, help="Optional per-category limit for a quick local smoke run")
    args = parser.parse_args()

    if args.batch_size < 100 or args.batch_size > 10000:
        parser.error("--batch-size must be between 100 and 10000")

    Base.metadata.create_all(bind=engine)
    if engine.dialect.name == "sqlite":
        with engine.begin() as connection:
            connection.execute(text("PRAGMA journal_mode=WAL"))
            connection.execute(text("PRAGMA synchronous=NORMAL"))

    db = SessionLocal()
    try:
        total = sum(import_category(db, category, args.data_dir, args.batch_size, args.max_records) for category in args.categories)
        print(f"Done. Imported {total:,} reviews in total.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
