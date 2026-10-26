from app.nlp.sentiment import (
    analyze_review_text,
    classify_sentiment,
    calculate_confidence,
    MODEL_NAME,
    MODEL_VERSION,
    POSITIVE_THRESHOLD,
    NEGATIVE_THRESHOLD
)

def test_classify_sentiment_rules():
    assert classify_sentiment(0.8) == "POSITIVE"
    assert classify_sentiment(0.05) == "POSITIVE"
    assert classify_sentiment(0.049) == "NEUTRAL"
    assert classify_sentiment(0.0) == "NEUTRAL"
    assert classify_sentiment(-0.049) == "NEUTRAL"
    assert classify_sentiment(-0.05) == "NEGATIVE"
    assert classify_sentiment(-0.7) == "NEGATIVE"

def test_analyze_positive_text():
    res = analyze_review_text("Absolutely fantastic sound quality, crisp treble and wonderful battery!", rating=5.0)
    assert res["sentiment"] == "POSITIVE"
    assert res["compound_score"] >= POSITIVE_THRESHOLD
    assert res["confidence"] >= 0.5
    assert res["model_name"] == MODEL_NAME
    assert res["model_version"] == MODEL_VERSION
    assert res["rating_reconciliation"] == "aligned"

def test_analyze_negative_text():
    res = analyze_review_text("Terrible product. Arrived broken, completely unusable and seller refused refund.", rating=1.0)
    assert res["sentiment"] == "NEGATIVE"
    assert res["compound_score"] <= NEGATIVE_THRESHOLD
    assert res["confidence"] >= 0.5
    assert res["rating_reconciliation"] == "aligned"

def test_analyze_empty_text():
    res = analyze_review_text("")
    assert res["sentiment"] == "NEUTRAL"
    assert res["compound_score"] == 0.0
    assert res["rating_reconciliation"] == "empty_text"

def test_rating_reconciliation_divergence():
    # 5-star rating with strongly negative text
    res = analyze_review_text("Worst purchase ever, completely broke after one hour.", rating=5.0)
    assert res["sentiment"] == "NEGATIVE"
    assert res["rating_reconciliation"] == "divergent_high_rating_negative_text"

    # 1-star rating with strongly positive text
    res = analyze_review_text("I love this so much, wonderful and perfect experience!", rating=1.0)
    assert res["sentiment"] == "POSITIVE"
    assert res["rating_reconciliation"] == "divergent_low_rating_positive_text"
