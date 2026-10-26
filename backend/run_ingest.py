import argparse
import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal, Base, engine
from app.ingestion.importer import import_records_from_stream, ensure_platforms_exist

def main():
    parser = argparse.ArgumentParser(description="Ingest review datasets into Sentiment Analysis database.")
    parser.add_argument("--platform", required=True, choices=["amazon", "flipkart", "myntra", "meesho", "generic"],
                        help="Platform identifier (amazon, flipkart, myntra, meesho, generic)")
    parser.add_argument("--file", required=True, help="Path to TSV, CSV, or JSONL dataset file")
    parser.add_argument("--dataset-name", default="unspecified_dataset", help="Dataset name/identifier for provenance")
    parser.add_argument("--dataset-version", default="1.0", help="Dataset version identifier")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch commit size")
    
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    print(f"Reading file: {file_path}")
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    print(f"Initializing database and verifying platform schemas...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        ensure_platforms_exist(db)
        print(f"Starting ingestion for platform: {args.platform} (Dataset: {args.dataset_name} v{args.dataset_version})...")
        result = import_records_from_stream(
            db=db,
            content_str=content,
            platform_code=args.platform,
            dataset_name=args.dataset_name,
            dataset_version=args.dataset_version,
            batch_size=args.batch_size
        )
        print("\n=== Ingestion Complete ===")
        print(f"Status: {result['status']}")
        print(f"Dataset:        {result.get('dataset_name')} (v{result.get('dataset_version')})")
        print(f"Total Parsed:   {result['total_parsed']}")
        print(f"Total Imported: {result['total_imported']}")
        print(f"Total Skipped:  {result['total_skipped']} (duplicates)")
        print(f"Rejections:     {result.get('rejection_summary')}")
        print(f"Model Applied:  {result['model_used']}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
