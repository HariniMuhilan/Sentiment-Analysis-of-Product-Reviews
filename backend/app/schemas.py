from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

class BaseSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

class HealthResponse(BaseSchema):
    status: str
    database: str
    timestamp: datetime
    version: str
    nlp_model: str

class ReadyResponse(BaseSchema):
    ready: bool
    total_reviews: int
    total_products: int
    platforms_active: int
    message: str

class PlatformResponse(BaseSchema):
    id: int
    code: str
    name: str
    description: Optional[str]
    source_info: Optional[str]
    terms_info: Optional[str]
    review_count: int
    average_rating: Optional[float]
    earliest_date: Optional[datetime]
    latest_date: Optional[datetime]
    has_data: bool

class SentimentBreakdown(BaseSchema):
    positive: int
    neutral: int
    negative: int
    positive_pct: float
    neutral_pct: float
    negative_pct: float

class ProductSearchPlatformStats(BaseSchema):
    platform_code: str
    platform_name: str
    review_count: int
    average_rating: Optional[float]
    average_compound: Optional[float]
    sentiment_breakdown: SentimentBreakdown

class ProductSearchResult(BaseSchema):
    id: int
    name: str
    category: Optional[str]
    total_reviews: int
    average_rating: Optional[float]
    platforms: List[str]
    sentiment_breakdown: SentimentBreakdown
    platform_stats: List[ProductSearchPlatformStats]

class PlatformStats(BaseSchema):
    platform_code: str
    platform_name: str
    review_count: int
    average_rating: Optional[float]
    average_compound: Optional[float]
    sentiment_breakdown: SentimentBreakdown
    wilson_positive_interval: Tuple[float, float]
    statistical_notes: str

class StatisticalComparison(BaseSchema):
    leader_platform: Optional[str] = None
    is_statistically_significant: bool = False
    test_method: str = "Pearson Chi-Square & Two-Proportion Z-Test"
    test_statistic: Optional[float] = None
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    effect_size_type: Optional[str] = None
    explanation: str
    sample_size_adequate: bool
    confounder_warning: Optional[str] = None

class DataCoverage(BaseSchema):
    platforms_with_data: List[str]
    platforms_without_data: List[str]
    is_empty: bool
    notice: str

class AnalysisSummaryResponse(BaseSchema):
    query: Optional[str] = None
    applied_filters: Dict[str, Any]
    total_reviews: int
    average_rating: Optional[float]
    average_compound: Optional[float]
    sentiment_breakdown: SentimentBreakdown
    platforms: List[PlatformStats]
    statistical_comparison: StatisticalComparison
    data_coverage: DataCoverage
    model_metadata: Dict[str, str]

class ReviewItem(BaseSchema):
    id: int
    external_id: Optional[str]
    platform_code: str
    platform_name: str
    product_name: str
    category: Optional[str]
    headline: Optional[str]
    review_text: str
    rating: Optional[float] = None
    helpful_votes: int
    review_date: Optional[datetime]
    sentiment: str
    compound_score: float
    confidence: float
    model_name: str
    model_version: str
    analyzed_at: Optional[datetime]

class ReviewListResponse(BaseSchema):
    total: int
    page: int
    page_size: int
    total_pages: int
    reviews: List[ReviewItem]

class ProductDetailResponse(BaseSchema):
    """Detailed information for a single selected product."""
    id: int
    name: str
    category: Optional[str] = None
    matching_query: Optional[str] = None

    # Overall aggregates across all platforms
    total_reviews: int
    average_rating: Optional[float]
    average_compound: Optional[float]
    sentiment_breakdown: SentimentBreakdown

    # Per-platform breakdown for this product (only platforms with data)
    platform_stats: List[PlatformStats] = []

    # Data coverage notice
    data_coverage: DataCoverage

    # Review pagination controls
    total_pages: int
    current_page: int

class EvaluationClassMetrics(BaseSchema):
    precision: float
    recall: float
    f1_score: float
    support: int

class EvaluationReport(BaseSchema):
    total_samples: int
    accuracy: float
    macro_f1: float
    per_class: Dict[str, EvaluationClassMetrics]
    confusion_matrix: Dict[str, Dict[str, int]]
    class_distribution: Dict[str, Dict[str, int]]

class ProductCrossPlatformAnalysisResponse(BaseSchema):
    """Cross-retailer sentiment analysis for a single product across platforms."""
    # Overall aggregate metrics
    total_reviews: int
    average_rating: Optional[float]
    average_compound: Optional[float]
    overall_sentiment_breakdown: SentimentBreakdown

    # Per-platform statistics
    platform_stats: List[Dict[str, Any]]

    # Statistical comparison (leader vs runner-up)
    leader_platform: Optional[str] = None
    is_significant: bool
    z_statistic: Optional[float]
    p_value: Optional[float]
    effect_size: Optional[float]
    explanation: str

    # Data coverage notice
    total_platforms_analyzed: int
    data_coverage_notice: str

class FullEvaluationResponse(BaseSchema):
    overall: EvaluationReport
    per_platform: Dict[str, EvaluationReport]
    calibration_ece: Optional[float] = None
    baselines: Optional[Dict[str, Any]] = None
    model_name: str
    model_version: str
    is_empirical: bool = False
    dataset_source: str
    methodology: str
