"""Seed a fresh installation with the repository's licensed demo corpus."""

import argparse
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.ingestion.importer import ensure_platforms_exist, import_records_from_stream
from app.models import Review


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True, help="Authorized normalized review CSV")
    args = parser.parse_args()

    if not args.file.is_file():
        raise SystemExit(f"Demo dataset not found: {args.file}")

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_platforms_exist(db)
        existing_count = db.query(Review.id).count()
        if existing_count:
            print(f"Database already contains {existing_count:,} reviews; demo seeding skipped.")
            return

        content = args.file.read_text(encoding="utf-8-sig", errors="replace")
        result = import_records_from_stream(
            db,
            content,
            platform_code="generic",
            dataset_name="virtual-assistant-devices-demo",
            dataset_version="1",
        )
        print(
            f"Seeded {result['total_imported']:,} reviews from the CC BY 4.0 "
            "Virtual Assistant Devices dataset. See its dataset card for attribution and limitations."
        )


if __name__ == "__main__":
    main()
