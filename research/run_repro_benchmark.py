"""Evaluate the current model on RePro's single-polarity labels.

This deliberately reports VADER as a cross-language stress baseline for
Brazilian Portuguese, not as a validated Portuguese sentiment model.
"""

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.nlp.evaluate import run_evaluation_on_dataset


DATASET = ROOT / "Datasets" / "B2WReviews01" / "processed" / "RePro-3class-evaluation.csv"
SUMMARY = ROOT / "results" / "repro_vader_benchmark.json"
TABLE = ROOT / "results" / "tables" / "repro_vader_benchmark.md"


def main() -> None:
    if not DATASET.is_file():
        raise SystemExit(
            "Prepared RePro benchmark is missing. See Datasets/B2WReviews01/README.md "
            "and run research/prepare_repro_benchmark.py first."
        )

    records = []
    with DATASET.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            title = (row.get("review_title") or "").strip()
            body = (row.get("review_text") or "").strip()
            records.append(
                {
                    "platform_code": "americanas_brazil",
                    "review_text": "\n".join(part for part in (title, body) if part),
                    "ground_truth_sentiment": row["ground_truth_sentiment"].strip().upper(),
                    "rating": float(row["rating"]) if row.get("rating") else None,
                }
            )

    evaluation = run_evaluation_on_dataset(records)
    summary = {
        "dataset": "RePro single-polarity 3-class evaluation subset",
        "source": "RePro 2024, based on B2W-Reviews01 / Americanas.com",
        "language": "Brazilian Portuguese",
        "samples_evaluated": len(records),
        "full_repro_release_rows": 10003,
        "mixed_reviews_excluded_from_three_class_evaluation": 2018,
        "sampling_note": "RePro was sampled stratified by star rating; metrics are not prevalence estimates.",
        "model_scope_warning": (
            "VADER is English-oriented. This cross-language stress result is not validated Portuguese "
            "in-language performance and should not be used to claim Portuguese model quality."
        ),
        "source_license": "CC BY-NC-SA 4.0",
        "citation": (
            "dos Santos Silva et al. (2024). RePro: a benchmark for Opinion Mining for Brazilian Portuguese. "
            "Proceedings of PROPOR, pp. 432-440."
        ),
        "results": evaluation,
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    overall = evaluation["overall"]
    rating = evaluation["baselines"]["star_rating_heuristic"]
    majority = evaluation["baselines"]["majority_zero_r"]
    rows = [
        "# RePro Cross-Language Stress Benchmark",
        "",
        "RePro single-polarity Brazilian Portuguese sample. Mixed labels were excluded from the three-class metrics.",
        "VADER is English-oriented; these results are a cross-language stress baseline, not Portuguese in-language performance.",
        "The RePro sample is stratified by star rating, so these numbers are not natural review prevalence estimates.",
        "",
        "| Method | Accuracy | Macro F1 | Samples |",
        "|---|---:|---:|---:|",
        f"| VADER lexical baseline | {overall['accuracy']:.4f} | {overall['macro_f1']:.4f} | {overall['total_samples']:,} |",
        f"| Star-rating heuristic | {rating['accuracy']:.4f} | {rating['macro_f1']:.4f} | {rating['total_samples']:,} |",
        f"| Majority-class baseline | {majority['accuracy']:.4f} | {majority['macro_f1']:.4f} | {majority['total_samples']:,} |",
        "",
        "Citation: dos Santos Silva et al. (2024), *RePro: a benchmark for Opinion Mining for Brazilian Portuguese*, PROPOR, pp. 432–440.",
    ]
    TABLE.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Evaluated {len(records):,} single-polarity RePro reviews.")
    print(f"VADER macro F1: {overall['macro_f1']:.4f}")
    print(f"Results: {SUMMARY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
