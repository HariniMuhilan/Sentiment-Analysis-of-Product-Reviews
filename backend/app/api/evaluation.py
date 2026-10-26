from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import FullEvaluationResponse
from app.nlp.evaluate import run_evaluation_on_dataset
from app.models import BenchmarkReview

router = APIRouter(tags=["Model Evaluation"])

# Internal sanity-check unit test fixtures for pipeline verification.
# IMPORTANT: These fixtures are NOT independent validation data and must NEVER be
# cited as empirical model accuracy or real-world performance evidence.
UNIT_TEST_FIXTURES = [
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
    Returns evaluation metrics. Explicitly flags whether the evaluation is derived
    from a verified empirical human-annotated benchmark or internal unit-test fixtures.
    """
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
        is_empirical = True
        source_ids = {b.source for b in db_benchmarks}
        if source_ids == {"RePro-2024-single-polarity"}:
            dataset_source = (
                f"RePro / Americanas.com human-annotated benchmark "
                f"({len(db_benchmarks):,} single-polarity reviews)"
            )
            methodology = (
                "Brazilian Portuguese review titles and bodies were evaluated against RePro's human labels. "
                "The RePro paper reports at least two annotators per sample, expert adjudication, and mean "
                "sentiment Cohen's kappa of 0.71. The source sample was stratified by star rating; its labels "
                "include a mixed positive/negative class, which is excluded from this three-class evaluation. "
                "This project's VADER lexicon is English-oriented, so these metrics are a cross-language stress "
                "baseline, not validated Portuguese in-language performance. Do not interpret them as natural "
                "marketplace sentiment prevalence."
            )
        else:
            source_text = ", ".join(sorted(source_ids))
            dataset_source = (
                f"Empirical Database Benchmark Corpus ({len(db_benchmarks):,} records; {source_text})"
            )
            methodology = (
                f"Evaluated against {len(db_benchmarks):,} human-annotated review records stored in database. "
                "Metrics include precision, recall, macro F1, and a 3x3 confusion matrix. "
                "See each source's annotation and language notes before interpreting pooled metrics."
            )
    else:
        dataset = UNIT_TEST_FIXTURES
        is_empirical = False
        dataset_source = "Internal Unit-Test Fixtures (Non-Empirical Sanity Check)"
        methodology = (
            "NOTICE: No independent human-annotated research dataset has been imported yet. "
            f"Displaying pipeline verification results on {len(UNIT_TEST_FIXTURES)} internal unit-test fixtures. "
            "These metrics demonstrate system software execution and must NOT be cited as empirical accuracy."
        )

    res = run_evaluation_on_dataset(dataset)
    return FullEvaluationResponse(
        overall=res["overall"],
        per_platform=res["per_platform"],
        calibration_ece=res.get("calibration_ece"),
        baselines=res.get("baselines"),
        model_name=res["model_name"],
        model_version=res["model_version"],
        is_empirical=is_empirical,
        dataset_source=dataset_source,
        methodology=methodology
    )
