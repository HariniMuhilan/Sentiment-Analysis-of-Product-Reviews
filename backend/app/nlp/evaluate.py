from typing import List, Dict, Any, Tuple
from collections import defaultdict
from app.nlp.sentiment import analyze_review_text

CLASSES = ["POSITIVE", "NEUTRAL", "NEGATIVE"]

def evaluate_predictions(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    """
    Computes precision, recall, macro F1, confusion matrix, and class balance
    for 3-class sentiment predictions without relying on heavyweight external ML dependencies.
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have identical length.")
    
    total = len(y_true)
    if total == 0:
        return {
            "total_samples": 0,
            "accuracy": 0.0,
            "macro_f1": 0.0,
            "per_class": {},
            "confusion_matrix": {},
            "class_distribution": {}
        }

    # Confusion matrix: cm[actual][predicted]
    cm = {c1: {c2: 0 for c2 in CLASSES} for c1 in CLASSES}
    correct = 0
    actual_counts = defaultdict(int)
    predicted_counts = defaultdict(int)

    for true, pred in zip(y_true, y_pred):
        if true not in CLASSES:
            true = "NEUTRAL"
        if pred not in CLASSES:
            pred = "NEUTRAL"
        cm[true][pred] += 1
        actual_counts[true] += 1
        predicted_counts[pred] += 1
        if true == pred:
            correct += 1

    per_class = {}
    f1_scores = []

    for c in CLASSES:
        tp = cm[c][c]
        fp = sum(cm[other][c] for other in CLASSES if other != c)
        fn = sum(cm[c][other] for other in CLASSES if other != c)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        f1_scores.append(f1)

        per_class[c] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "support": actual_counts[c]
        }

    accuracy = correct / total
    macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

    return {
        "total_samples": total,
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class": per_class,
        "confusion_matrix": cm,
        "class_distribution": {
            "actual": dict(actual_counts),
            "predicted": dict(predicted_counts)
        }
    }

def run_evaluation_on_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates the live VADER sentiment model against a list of ground truth records.
    Each record must have 'review_text' and 'ground_truth_sentiment'.
    Optionally has 'platform_code'.
    """
    y_true = []
    y_pred = []
    per_platform_records = defaultdict(lambda: {"true": [], "pred": []})

    for rec in records:
        text = rec.get("review_text", "")
        true_label = rec.get("ground_truth_sentiment", "").upper()
        if true_label not in CLASSES:
            continue
        
        pred_res = analyze_review_text(text, rating=rec.get("rating"))
        pred_label = pred_res["sentiment"]

        y_true.append(true_label)
        y_pred.append(pred_label)

        platform = rec.get("platform_code", "unknown")
        per_platform_records[platform]["true"].append(true_label)
        per_platform_records[platform]["pred"].append(pred_label)

    overall = evaluate_predictions(y_true, y_pred)
    
    per_platform = {}
    for plat, data in per_platform_records.items():
        per_platform[plat] = evaluate_predictions(data["true"], data["pred"])

    return {
        "overall": overall,
        "per_platform": per_platform,
        "model_name": "vader-lexicon-v3.3",
        "model_version": "1.0.0"
    }
