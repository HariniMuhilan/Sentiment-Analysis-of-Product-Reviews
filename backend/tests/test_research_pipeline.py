from app.crud import compute_two_proportion_z_test, compute_chi_square_2x3
from app.nlp.evaluate import (
    compute_expected_calibration_error,
    evaluate_majority_baseline,
    evaluate_rating_heuristic
)
from app.ingestion.parsers import parse_amazon_record

def test_missing_rating_preserved_as_none():
    row = {
        "product_title": "Unrated Item",
        "review_body": "Nice text without any rating score.",
        "review_id": "AMZ-NULL-RATING"
    }
    rec = parse_amazon_record(row)
    assert rec is not None
    assert rec["rating"] is None # Crucial: Must NOT be defaulted to 3.0

def test_two_proportion_z_test_significant():
    # Large samples with distinct proportions (80% vs 40%)
    res = compute_two_proportion_z_test(80, 100, 40, 100)
    assert res["z_stat"] > 0
    assert res["p_value"] < 0.001
    assert res["is_significant"] is True
    assert res["effect_size"] > 0.5 # Substantial Cohen's h

def test_two_proportion_z_test_not_significant():
    # Samples with minor difference (52% vs 50%)
    res = compute_two_proportion_z_test(52, 100, 50, 100)
    assert res["is_significant"] is False
    assert res["p_value"] > 0.05

def test_chi_square_2x3():
    row1 = [50, 20, 30]
    row2 = [10, 40, 50]
    res = compute_chi_square_2x3(row1, row2)
    assert res["chi2"] > 0
    assert res["cramers_v"] > 0

def test_expected_calibration_error():
    # Perfectly calibrated case: confidence = 1.0, all correct
    ece_zero = compute_expected_calibration_error([1.0, 1.0, 1.0], [True, True, True])
    assert ece_zero == 0.0

    # Miscalibrated case: confidence = 0.9, but all wrong
    ece_high = compute_expected_calibration_error([0.9, 0.9], [False, False])
    assert ece_high > 0.8

def test_majority_baseline():
    y_true = ["POSITIVE", "POSITIVE", "NEGATIVE"]
    res = evaluate_majority_baseline(y_true)
    assert res["accuracy"] == round(2 / 3, 4)
    assert res["majority_class"] == "POSITIVE"

def test_rating_heuristic():
    recs = [
        {"ground_truth_sentiment": "POSITIVE", "rating": 5.0},
        {"ground_truth_sentiment": "NEGATIVE", "rating": 1.0},
        {"ground_truth_sentiment": "NEUTRAL", "rating": 3.0},
        {"ground_truth_sentiment": "POSITIVE", "rating": 2.0} # Divergent case
    ]
    res = evaluate_rating_heuristic(recs)
    assert res["total_samples"] == 4
    assert res["accuracy"] == 0.75 # 3 out of 4 correct
