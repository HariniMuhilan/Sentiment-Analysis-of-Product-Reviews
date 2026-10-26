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

class ProductSearchResult(BaseSchema):
    id: int
    name: str
    category: Optional[str]
    total_reviews: int
    average_rating: Optional[float]
    platforms: List[str]

class SentimentBreakdown(BaseSchema):
    positive: int
    neutral: int
    negative: int
    positive_pct: float
    neutral_pct: float
    negative_pct: float

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
    explanation: str
    sample_size_adequate: bool

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
    rating: float
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

class FullEvaluationResponse(BaseSchema):
    overall: EvaluationReport
    per_platform: Dict[str, EvaluationReport]
    model_name: str
    model_version: str
    methodology: str
