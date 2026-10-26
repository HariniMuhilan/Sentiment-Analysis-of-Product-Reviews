"""Load RePro's non-mixed human labels into the API evaluation benchmark.

This populates only benchmark_reviews; it does not add the RePro sample to the
searchable review database. RePro is derived from B2W-Reviews01, so its records
must not be counted as additional independent reviews alongside B2W.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import Base, SessionLocal, engine
from app.models import BenchmarkReview


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Datasets" / "B2WReviews01" / "processed" / "RePro-3class-evaluation.csv"
SOURCE_ID = "RePro-2024-single-polarity"
ALLOWED = {"POSITIVE", "NEUTRAL", "NEGATIVE"}


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(
            "Prepared RePro benchmark is missing. See Datasets/B2WReviews01/README.md "
            "and run research/prepare_repro_benchmark.py first."
        )

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.query(BenchmarkReview).filter(BenchmarkReview.source == SOURCE_ID).delete(
            synchronize_session=False
        )
        inserted = 0
        with SOURCE.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                label = (row.get("ground_truth_sentiment") or "").strip().upper()
                if label not in ALLOWED:
                    continue
                title = (row.get("review_title") or "").strip()
                body = (row.get("review_text") or "").strip()
                text = "\n".join(part for part in (title, body) if part)
                if not text:
                    continue
                try:
                    rating = float(row["rating"]) if row.get("rating") else None
                except ValueError:
                    rating = None
                db.add(
                    BenchmarkReview(
                        platform_code="americanas_brazil",
                        review_text=text,
                        ground_truth_sentiment=label,
                        rating=rating,
                        source=SOURCE_ID,
                    )
                )
                inserted += 1
        db.commit()
        print(
            f"Loaded {inserted:,} single-polarity RePro labels into benchmark_reviews. "
            "Mixed labels remain in the full corpus and were not coerced."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
