from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Platform(Base):
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    source_info = Column(Text, nullable=True)
    terms_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    reviews = relationship("Review", back_populates="platform", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now)

    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), nullable=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    
    product_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    headline = Column(String(500), nullable=True)
    review_text = Column(Text, nullable=False)
    rating = Column(Float, nullable=True, index=True)
    helpful_votes = Column(Integer, default=0)
    review_date = Column(DateTime, nullable=True, index=True)

    # Sentiment analysis metadata
    sentiment = Column(String(20), nullable=False, index=True) # POSITIVE, NEUTRAL, NEGATIVE
    compound_score = Column(Float, nullable=False)             # VADER compound score in [-1.0, 1.0]
    positive_score = Column(Float, nullable=False)             # VADER pos ratio
    neutral_score = Column(Float, nullable=False)              # VADER neu ratio
    negative_score = Column(Float, nullable=False)             # VADER neg ratio
    confidence = Column(Float, nullable=False)                 # Calibration confidence
    model_name = Column(String(100), nullable=False)           # e.g., "vader-lexicon-v3.3"
    model_version = Column(String(50), nullable=False)          # e.g., "1.0.0"
    analyzed_at = Column(DateTime, default=utc_now)
    created_at = Column(DateTime, default=utc_now)

    platform = relationship("Platform", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

    __table_args__ = (
        Index("idx_review_platform_product", "platform_id", "product_name"),
        Index("idx_review_rating_sentiment", "rating", "sentiment"),
    )

class BenchmarkReview(Base):
    """Ground truth dataset for reproducible evaluation and calibration."""
    __tablename__ = "benchmark_reviews"

    id = Column(Integer, primary_key=True, index=True)
    platform_code = Column(String(50), nullable=False)
    review_text = Column(Text, nullable=False)
    ground_truth_sentiment = Column(String(20), nullable=False) # POSITIVE, NEUTRAL, NEGATIVE
    rating = Column(Float, nullable=True)
    source = Column(String(100), default="curated_validation_set")
    created_at = Column(DateTime, default=utc_now)

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    records_processed = Column(Integer, default=0)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="completed")
    notes = Column(Text, nullable=True)
