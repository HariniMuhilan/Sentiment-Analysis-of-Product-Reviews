from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.schemas import AnalysisSummaryResponse
from app.crud import get_aggregated_analysis

router = APIRouter(tags=["Sentiment Analysis"])

@router.get("/analysis", response_model=AnalysisSummaryResponse)
def get_sentiment_analysis(
    q: Optional[str] = Query(None, description="Product name or keyword search"),
    platform: Optional[str] = Query(None, description="Platform code (amazon, flipkart, myntra, meesho, all)"),
    category: Optional[str] = Query(None, description="Category filter"),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0, description="Minimum star rating"),
    max_rating: Optional[float] = Query(None, ge=1.0, le=5.0, description="Maximum star rating"),
    sentiment: Optional[str] = Query(None, description="Sentiment filter (POSITIVE, NEUTRAL, NEGATIVE, ALL)"),
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    db: Session = Depends(get_db)
):
    """
    Computes statistical sentiment metrics and platform comparisons
    derived purely from persisted, locally ingested reviews.
    """
    return get_aggregated_analysis(
        db,
        query=q,
        platform_code=platform,
        category=category,
        min_rating=min_rating,
        max_rating=max_rating,
        sentiment=sentiment,
        start_date=start_date,
        end_date=end_date
    )
