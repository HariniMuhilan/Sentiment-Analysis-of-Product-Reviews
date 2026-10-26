from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.schemas import ReviewListResponse
from app.crud import get_paginated_reviews
from app.config import settings

router = APIRouter(tags=["Reviews"])

@router.get("/reviews", response_model=ReviewListResponse)
def list_reviews(
    q: Optional[str] = Query(None, description="Search term in review text, headline, or product name"),
    platform: Optional[str] = Query(None, description="Platform code filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0, description="Minimum star rating"),
    max_rating: Optional[float] = Query(None, ge=1.0, le=5.0, description="Maximum star rating"),
    sentiment: Optional[str] = Query(None, description="Sentiment filter (POSITIVE, NEUTRAL, NEGATIVE, ALL)"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    Paginated review search. Prevents loading large datasets into browser memory.
    """
    return get_paginated_reviews(
        db,
        query=q,
        platform_code=platform,
        category=category,
        min_rating=min_rating,
        max_rating=max_rating,
        sentiment=sentiment,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=min(page_size, settings.MAX_PAGE_SIZE)
    )
