from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.schemas import PlatformResponse, ProductSearchResult
from app.models import Platform, Review
from app.crud import get_product_search

router = APIRouter(tags=["Catalog & Platforms"])

@router.get("/platforms", response_model=List[PlatformResponse])
def list_platforms(db: Session = Depends(get_db)):
    """Lists supported platforms and their currently ingested data coverage."""
    platforms = db.query(Platform).all()
    results = []
    for p in platforms:
        stats = db.query(
            func.count(Review.id).label("count"),
            func.avg(Review.rating).label("avg_rating"),
            func.min(Review.review_date).label("min_date"),
            func.max(Review.review_date).label("max_date")
        ).filter(Review.platform_id == p.id).first()

        count = stats.count or 0
        results.append(PlatformResponse(
            id=p.id,
            code=p.code,
            name=p.name,
            description=p.description,
            source_info=p.source_info,
            terms_info=p.terms_info,
            review_count=count,
            average_rating=round(float(stats.avg_rating), 2) if stats.avg_rating else None,
            earliest_date=stats.min_date,
            latest_date=stats.max_date,
            has_data=(count > 0)
        ))
    return results

@router.get("/products", response_model=List[ProductSearchResult])
def search_products(
    q: Optional[str] = Query(None, description="Partial product name search query"),
    limit: int = Query(20, ge=1, le=100, description="Max search results"),
    db: Session = Depends(get_db)
):
    """Case-insensitive partial product name search on local catalog."""
    return get_product_search(db, query=q, limit=limit)
