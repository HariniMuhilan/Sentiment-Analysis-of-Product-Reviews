from typing import Dict, Any, Optional
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime, timezone

# Ensure VADER lexicon is downloaded
try:
    _analyzer = SentimentIntensityAnalyzer()
except LookupError:
    nltk.download("vader_lexicon", quiet=True)
    _analyzer = SentimentIntensityAnalyzer()

MODEL_NAME = "vader-lexicon-v3.3"
MODEL_VERSION = "1.0.0"

# Documented thresholds for 3-class classification
POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05

def classify_sentiment(compound: float) -> str:
    """
    Standard VADER classification boundary:
      - compound >= 0.05: POSITIVE
      - -0.05 < compound < 0.05: NEUTRAL
      - compound <= -0.05: NEGATIVE
    """
    if compound >= POSITIVE_THRESHOLD:
        return "POSITIVE"
    elif compound <= NEGATIVE_THRESHOLD:
        return "NEGATIVE"
    else:
        return "NEUTRAL"

def calculate_confidence(scores: Dict[str, float], compound: float) -> float:
    """
    Computes heuristic decision-margin intensity separate from raw valence:
    Measures how decisively the dominant sentiment class exceeds neutrality.
    
    NOTE ON CALIBRATION:
    This is an uncalibrated heuristic intensity score in [0.50, 1.00], NOT an
    empirical posterior probability P(y=true | x). True probability calibration
    requires Platt scaling or isotonic regression on annotated validation sets.
    """
    dominant_valence = max(scores.get("pos", 0.0), scores.get("neg", 0.0))
    neu = scores.get("neu", 0.0)
    
    # If text is predominantly neutral with compound near 0:
    if abs(compound) < 0.05:
        # Confidence in neutrality is proportional to neu score
        return round(float(neu), 4)
    
    # For positive or negative classifications, confidence scales with compound intensity
    # and valence separation from neutrality:
    conf = 0.50 + (abs(compound) * 0.50)
    return round(min(1.0, max(0.50, float(conf))), 4)

def analyze_review_text(text: str, rating: Optional[float] = None) -> Dict[str, Any]:
    """
    Analyzes review text and returns genuine sentiment metrics.
    
    Returns:
        dict containing:
          - sentiment: "POSITIVE" | "NEUTRAL" | "NEGATIVE"
          - compound_score: float in [-1.0, 1.0]
          - positive_score: float in [0.0, 1.0]
          - neutral_score: float in [0.0, 1.0]
          - negative_score: float in [0.0, 1.0]
          - confidence: float in [0.0, 1.0]
          - model_name: str
          - model_version: str
          - analyzed_at: datetime
          - rating_reconciliation: Optional[str] (notes if text diverges from star rating)
    """
    clean_text = (text or "").strip()
    if not clean_text:
        return {
            "sentiment": "NEUTRAL",
            "compound_score": 0.0,
            "positive_score": 0.0,
            "neutral_score": 1.0,
            "negative_score": 0.0,
            "confidence": 0.5,
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "analyzed_at": datetime.now(timezone.utc),
            "rating_reconciliation": "empty_text"
        }

    scores = _analyzer.polarity_scores(clean_text)
    compound = float(scores["compound"])
    sentiment = classify_sentiment(compound)
    confidence = calculate_confidence(scores, compound)

    # Check for sentiment vs star-rating divergence if rating is supplied
    reconciliation = None
    if rating is not None:
        if rating >= 4.0 and sentiment == "NEGATIVE":
            reconciliation = "divergent_high_rating_negative_text"
        elif rating <= 2.0 and sentiment == "POSITIVE":
            reconciliation = "divergent_low_rating_positive_text"
        else:
            reconciliation = "aligned"

    return {
        "sentiment": sentiment,
        "compound_score": round(compound, 4),
        "positive_score": round(float(scores["pos"]), 4),
        "neutral_score": round(float(scores["neu"]), 4),
        "negative_score": round(float(scores["neg"]), 4),
        "confidence": confidence,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "analyzed_at": datetime.now(timezone.utc),
        "rating_reconciliation": reconciliation
    }
