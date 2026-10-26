import os
import sys
import json
import math
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any

# Ensure backend directory is in path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.nlp.sentiment import analyze_review_text
from app.nlp.evaluate import (
    evaluate_predictions,
    compute_expected_calibration_error,
    evaluate_majority_baseline,
    evaluate_rating_heuristic,
    CLASSES
)
from app.crud import compute_two_proportion_z_test, compute_chi_square_2x3

RESULTS_DIR = REPO_ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
RANDOM_SEED = 42

def load_evaluation_dataset(dataset_path: Path) -> List[Dict[str, Any]]:
    """Loads JSONL or CSV evaluation records."""
    if not dataset_path.exists():
        return []
    records = []
    if dataset_path.suffix == ".jsonl":
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    elif dataset_path.suffix == ".csv":
        import csv
        with open(dataset_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append({
                    "review_text": row.get("review_text") or row.get("text", ""),
                    "ground_truth_sentiment": row.get("ground_truth_sentiment") or row.get("sentiment", ""),
                    "rating": float(row["rating"]) if row.get("rating") and row["rating"].replace(".", "", 1).isdigit() else None,
                    "platform_code": row.get("platform") or row.get("platform_code", "generic"),
                    "product_name": row.get("product_name", "General Item"),
                    "category": row.get("category", "General")
                })
    return records

def analyze_rating_text_divergence(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Quantifies the divergence between numerical star ratings (1.0-5.0)
    and semantic text polarity classified by VADER.
    """
    total_rated = 0
    aligned = 0
    high_rating_negative_text = 0 # 4-5 stars with negative text
    low_rating_positive_text = 0  # 1-2 stars with positive text
    neutral_ratings_divergence = defaultdict(int) # Distribution of 3-star reviews

    for rec in records:
        rating = rec.get("rating")
        text = rec.get("review_text", "")
        if rating is None or not text.strip():
            continue
        
        total_rated += 1
        nlp_res = analyze_review_text(text, rating=rating)
        pred_sent = nlp_res["sentiment"]

        if rating >= 4.0:
            if pred_sent == "NEGATIVE":
                high_rating_negative_text += 1
            elif pred_sent == "POSITIVE":
                aligned += 1
        elif rating <= 2.0:
            if pred_sent == "POSITIVE":
                low_rating_positive_text += 1
            elif pred_sent == "NEGATIVE":
                aligned += 1
        else: # 3.0 star rating
            neutral_ratings_divergence[pred_sent] += 1
            if pred_sent == "NEUTRAL":
                aligned += 1

    divergent_total = high_rating_negative_text + low_rating_positive_text
    divergence_rate = round(divergent_total / total_rated, 4) if total_rated > 0 else 0.0

    return {
        "total_rated_reviews": total_rated,
        "aligned_count": aligned,
        "divergent_count": divergent_total,
        "divergence_rate": divergence_rate,
        "high_rating_negative_text": high_rating_negative_text,
        "low_rating_positive_text": low_rating_positive_text,
        "neutral_rating_breakdown": dict(neutral_ratings_divergence)
    }

def run_experiment_pipeline(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Executes the full comparative baseline suite and outputs structured reports."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    y_true = []
    y_pred_vader = []
    confidences = []
    matches = []

    for r in records:
        true_label = (r.get("ground_truth_sentiment") or "").upper()
        if true_label not in CLASSES:
            continue
        pred_res = analyze_review_text(r.get("review_text", ""), rating=r.get("rating"))
        pred_label = pred_res["sentiment"]
        conf = pred_res["confidence"]

        y_true.append(true_label)
        y_pred_vader.append(pred_label)
        confidences.append(conf)
        matches.append(bool(pred_label == true_label))

    # 1. Model Evaluations
    vader_eval = evaluate_predictions(y_true, y_pred_vader)
    majority_eval = evaluate_majority_baseline(y_true)
    rating_heuristic_eval = evaluate_rating_heuristic(records)
    ece = compute_expected_calibration_error(confidences, matches)

    # 2. Rating-Text Divergence
    divergence_report = analyze_rating_text_divergence(records)

    # 3. Assemble Full Summary
    summary = {
        "metadata": {
            "random_seed": RANDOM_SEED,
            "total_evaluation_samples": len(y_true),
            "classes": CLASSES
        },
        "models": {
            "vader_lexical": {
                **vader_eval,
                "expected_calibration_error": ece
            },
            "majority_zero_r": majority_eval,
            "star_rating_heuristic": rating_heuristic_eval
        },
        "rating_text_divergence": divergence_report
    }

    # Save JSON results
    with open(RESULTS_DIR / "experiment_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Generate Markdown Table for manuscript
    markdown_table = (
        "| Model / Heuristic | Accuracy | Macro F1 | Pos F1 | Neu F1 | Neg F1 | ECE |\n"
        "|---|---|---|---|---|---|---|\n"
        f"| Majority Class (ZeroR) | {majority_eval['accuracy']:.4f} | {majority_eval['macro_f1']:.4f} | "
        f"{majority_eval['per_class'].get('POSITIVE', {}).get('f1_score', 0):.4f} | "
        f"{majority_eval['per_class'].get('NEUTRAL', {}).get('f1_score', 0):.4f} | "
        f"{majority_eval['per_class'].get('NEGATIVE', {}).get('f1_score', 0):.4f} | N/A |\n"
        f"| Star-Rating Heuristic | {rating_heuristic_eval['accuracy']:.4f} | {rating_heuristic_eval['macro_f1']:.4f} | "
        f"{rating_heuristic_eval['per_class'].get('POSITIVE', {}).get('f1_score', 0):.4f} | "
        f"{rating_heuristic_eval['per_class'].get('NEUTRAL', {}).get('f1_score', 0):.4f} | "
        f"{rating_heuristic_eval['per_class'].get('NEGATIVE', {}).get('f1_score', 0):.4f} | N/A |\n"
        f"| VADER Lexicon (v1.0.0) | {vader_eval['accuracy']:.4f} | {vader_eval['macro_f1']:.4f} | "
        f"{vader_eval['per_class'].get('POSITIVE', {}).get('f1_score', 0):.4f} | "
        f"{vader_eval['per_class'].get('NEUTRAL', {}).get('f1_score', 0):.4f} | "
        f"{vader_eval['per_class'].get('NEGATIVE', {}).get('f1_score', 0):.4f} | {ece:.4f} |\n"
    )
    with open(TABLES_DIR / "baseline_comparison_table.md", "w", encoding="utf-8") as f:
        f.write(markdown_table)

    return summary

if __name__ == "__main__":
    # Empirical metrics require an independently human-annotated benchmark.
    bench_file = REPO_ROOT / "Datasets" / "research" / "benchmark_annotated.csv"
    if not bench_file.exists():
        raise SystemExit(
            "No human-annotated benchmark found. Create Datasets/research/benchmark_annotated.csv "
            "using the annotation protocol before reporting accuracy, F1, or calibration results. "
            "Synthetic unit-test fixtures are not research evidence."
        )

    print(f"Loading human-annotated benchmark: {bench_file}")
    recs = load_evaluation_dataset(bench_file)
    allowed = {"POSITIVE", "NEUTRAL", "NEGATIVE"}
    unlabeled = sum(str(row.get("ground_truth_sentiment") or "").strip().upper() not in allowed for row in recs)
    if not recs or unlabeled:
        raise SystemExit(
            f"Benchmark has {len(recs):,} rows and {unlabeled:,} missing/invalid human labels. "
            "Use POSITIVE, NEUTRAL, or NEGATIVE in ground_truth_sentiment for every evaluated record."
        )

    results = run_experiment_pipeline(recs)
    print("\n=== Experiment Execution Complete ===")
    print(f"Samples Evaluated: {results['metadata']['total_evaluation_samples']}")
    print(f"VADER Macro F1:    {results['models']['vader_lexical']['macro_f1']}")
    print(f"VADER ECE:         {results['models']['vader_lexical']['expected_calibration_error']}")
    print(f"Results exported to: {RESULTS_DIR}")
