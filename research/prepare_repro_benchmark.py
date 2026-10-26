"""Create privacy-minimized RePro corpus and 3-class evaluation files.

RePro labels are human annotated in Brazilian Portuguese. The source includes
reviewer demographics; this derivative omits all reviewer-level fields. Mixed
positive/negative reviews are retained in the full corpus and excluded from
the separate 3-class evaluation file.
"""

import ast
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Datasets" / "B2WReviews01" / "raw" / "RePro.csv"
OUTPUT_DIR = ROOT / "Datasets" / "B2WReviews01" / "processed"
FULL_OUTPUT = OUTPUT_DIR / "RePro-clean.csv"
EVAL_OUTPUT = OUTPUT_DIR / "RePro-3class-evaluation.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "RePro-preparation-summary.json"

LABEL_MAP = {
    ("POSITIVO",): "POSITIVE",
    ("NEGATIVO",): "NEGATIVE",
    ("NEUTRO",): "NEUTRAL",
    ("NEGATIVO", "POSITIVO"): "MIXED",
    ("POSITIVO", "NEGATIVO"): "MIXED",
}
FIELDS = [
    "review_id",
    "product_id",
    "product_name",
    "category_level_1",
    "category_level_2",
    "review_title",
    "review_text",
    "rating",
    "recommend_to_a_friend",
    "review_date",
    "topics",
    "ground_truth_sentiment",
    "source_platform",
]


def stable_id(row: dict[str, str], title: str, body: str) -> str:
    key = "|".join(
        [row.get("product_id", ""), row.get("submission_date", ""), title, body]
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def prepare() -> dict:
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Missing {SOURCE.relative_to(ROOT)}. Download RePro.csv from "
            "https://raw.githubusercontent.com/lucasnil/repro/main/RePro.csv "
            "and save it to Datasets/B2WReviews01/raw/RePro.csv."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    label_counts: Counter[str] = Counter()
    full_rows = 0
    eval_rows = 0
    with SOURCE.open(encoding="utf-8-sig", newline="") as source, FULL_OUTPUT.open(
        "w", encoding="utf-8", newline=""
    ) as full_file, EVAL_OUTPUT.open("w", encoding="utf-8", newline="") as eval_file:
        reader = csv.DictReader(source)
        full_writer = csv.DictWriter(full_file, fieldnames=FIELDS)
        eval_writer = csv.DictWriter(eval_file, fieldnames=FIELDS)
        full_writer.writeheader()
        eval_writer.writeheader()

        for row in reader:
            title = (row.get("review_title") or "").strip()
            body = (row.get("review_text") or "").strip()
            if not (title or body):
                continue
            original_labels = tuple(
                str(label).strip().upper()
                for label in ast.literal_eval(row.get("polarity") or "[]")
            )
            label = LABEL_MAP.get(original_labels)
            if label is None:
                raise ValueError(f"Unrecognized RePro polarity value: {original_labels!r}")
            record = {
                "review_id": stable_id(row, title, body),
                "product_id": (row.get("product_id") or "").strip(),
                "product_name": (row.get("product_name") or "").strip(),
                "category_level_1": (row.get("site_category_lv1") or "").strip(),
                "category_level_2": (row.get("site_category_lv2") or "").strip(),
                "review_title": title,
                "review_text": body,
                "rating": (row.get("overall_rating") or "").strip(),
                "recommend_to_a_friend": (row.get("recommend_to_a_friend") or "").strip(),
                "review_date": (row.get("submission_date") or "").strip(),
                "topics": json.dumps(
                    ast.literal_eval(row.get("topics") or "[]"), ensure_ascii=False
                ),
                "ground_truth_sentiment": label,
                "source_platform": "americanas_brazil",
            }
            full_writer.writerow(record)
            full_rows += 1
            label_counts[label] += 1
            if label != "MIXED":
                eval_writer.writerow(record)
                eval_rows += 1

    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    summary = {
        "dataset": "RePro",
        "provider": "RePro authors; based on B2W-Reviews01 from Americanas.com",
        "source_url": "https://github.com/lucasnil/repro",
        "license": "CC BY-NC-SA 4.0",
        "source_rows_reported_by_paper": 10000,
        "source_rows_in_downloaded_release": full_rows,
        "source_sha256": source_hash,
        "prepared_rows": full_rows,
        "single_polarity_3class_evaluation_rows": eval_rows,
        "label_counts": dict(sorted(label_counts.items())),
        "mixed_reviews_excluded_from_3class_evaluation": label_counts["MIXED"],
        "removed_fields": [
            "reviewer_id",
            "reviewer_birth_year",
            "reviewer_gender",
            "reviewer_state",
        ],
        "full_corpus_path": str(FULL_OUTPUT.relative_to(ROOT)),
        "full_corpus_sha256": digest(FULL_OUTPUT),
        "evaluation_file_path": str(EVAL_OUTPUT.relative_to(ROOT)),
        "evaluation_file_sha256": digest(EVAL_OUTPUT),
        "annotation_note": (
            "The paper reports 10,000 samples; the downloaded CSV contains the exact row count above. "
            "The 3-class evaluation excludes multi-polarity mixed reviews."
        ),
        "model_limit": (
            "VADER is English-oriented; its result on Brazilian Portuguese is a cross-language stress "
            "baseline, not validated Portuguese in-language performance."
        ),
    }
    SUMMARY_OUTPUT.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2, ensure_ascii=False))
