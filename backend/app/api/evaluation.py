from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import FullEvaluationResponse
from app.nlp.evaluate import run_evaluation_on_dataset
from app.models import BenchmarkReview

router = APIRouter(tags=["Model Evaluation"])

BENCHMARK_FIXTURES = [
    # Positive examples
    {"platform_code": "amazon", "review_text": "This phone has an exceptional camera, stellar battery life, and snappy performance!", "ground_truth_sentiment": "POSITIVE", "rating": 5.0},
    {"platform_code": "amazon", "review_text": "Great quality and fast delivery. Very satisfied with this purchase.", "ground_truth_sentiment": "POSITIVE", "rating": 5.0},
    {"platform_code": "flipkart", "review_text": "Outstanding product for the price. Sound is crystal clear with deep bass.", "ground_truth_sentiment": "POSITIVE", "rating": 5.0},
    {"platform_code": "flipkart", "review_text": "Totally worth every penny! Build quality is sturdy and looks premium.", "ground_truth_sentiment": "POSITIVE", "rating": 5.0},
    {"platform_code": "myntra", "review_text": "Fabric is wonderfully soft and fits perfectly as described in the size guide.", "ground_truth_sentiment": "POSITIVE", "rating": 5.0},
    {"platform_code": "myntra", "review_text": "Beautiful color and stitch work! Exceeded my expectations.", "ground_truth_sentiment": "POSITIVE", "rating": 5.0},
    {"platform_code": "meesho", "review_text": "Super affordable and surprisingly decent quality. Very happy!", "ground_truth_sentiment": "POSITIVE", "rating": 4.5},
    {"platform_code": "meesho", "review_text": "Very nice item, works as expected. Good value for money.", "ground_truth_sentiment": "POSITIVE", "rating": 4.0},

    # Neutral examples
    {"platform_code": "amazon", "review_text": "The item arrived on Tuesday as scheduled. Packaging was standard cardboard.", "ground_truth_sentiment": "NEUTRAL", "rating": 3.0},
    {"platform_code": "amazon", "review_text": "Average device. Not bad, but nothing remarkable either. It does basic tasks.", "ground_truth_sentiment": "NEUTRAL", "rating": 3.0},
    {"platform_code": "flipkart", "review_text": "Normal product. Works ok so far. Will update after a few weeks of use.", "ground_truth_sentiment": "NEUTRAL", "rating": 3.0},
    {"platform_code": "myntra", "review_text": "Material is standard cotton. Color matches the photograph. Fit is plain.", "ground_truth_sentiment": "NEUTRAL", "rating": 3.0},
    {"platform_code": "meesho", "review_text": "Okay for daily casual wear. Neither high quality nor defective.", "ground_truth_sentiment": "NEUTRAL", "rating": 3.0},

    # Negative examples
    {"platform_code": "amazon", "review_text": "Terrible experience. The screen stopped working within 2 days. Complete waste of money.", "ground_truth_sentiment": "NEGATIVE", "rating": 1.0},
    {"platform_code": "amazon", "review_text": "Extremely disappointed. Poor build, flimsy materials, and broke on first use.", "ground_truth_sentiment": "NEGATIVE", "rating": 1.0},
    {"platform_code": "flipkart", "review_text": "Defective item received. Customer support refused refund. Do not buy!", "ground_truth_sentiment": "NEGATIVE", "rating": 1.0},
    {"platform_code": "flipkart", "review_text": "Horrible quality, feels cheap and fragile. Completely unsatisfied.", "ground_truth_sentiment": "NEGATIVE", "rating": 1.0},
    {"platform_code": "myntra", "review_text": "Sizing is completely wrong and the cloth shrank terribly after one wash.", "ground_truth_sentiment": "NEGATIVE", "rating": 1.0},
    {"platform_code": "meesho", "review_text": "Very poor stitching, threads coming off everywhere. Bad purchase.", "ground_truth_sentiment": "NEGATIVE", "rating": 1.0},
    {"platform_code": "meesho", "review_text": "Worst experience ever. Item arrived damaged and unusable.", "ground_truth_sentiment": "NEGATIVE", "rating": 1.0}
]

@router.get("/evaluation", response_model=FullEvaluationResponse)
def get_evaluation_metrics(db: Session = Depends(get_db)):
    """
    Returns reproducible evaluation metrics (Precision, Recall, Macro F1, Confusion Matrix,
    Class Balance) measured against standard validation benchmark datasets.
    """
    # Check if custom benchmark reviews exist in DB
    db_benchmarks = db.query(BenchmarkReview).all()
    if db_benchmarks and len(db_benchmarks) >= 10:
        dataset = [
            {
                "platform_code": b.platform_code,
                "review_text": b.review_text,
                "ground_truth_sentiment": b.ground_truth_sentiment,
                "rating": b.rating
            }
            for b in db_benchmarks
        ]
        methodology = f"Evaluated against {len(db_benchmarks)} custom database benchmark records."
    else:
        dataset = BENCHMARK_FIXTURES
        methodology = (
            f"Evaluated against {len(BENCHMARK_FIXTURES)} multi-platform validation samples. "
            "Metrics include Precision, Recall, Macro F1, and 3x3 Confusion Matrix."
        )

    res = run_evaluation_on_dataset(dataset)
    return FullEvaluationResponse(
        overall=res["overall"],
        per_platform=res["per_platform"],
        model_name=res["model_name"],
        model_version=res["model_version"],
        methodology=methodology
    )
