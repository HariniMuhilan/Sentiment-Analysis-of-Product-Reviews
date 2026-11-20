from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.schemas import PlatformResponse, ProductSearchResult, ProductDetailResponse, ReviewListResponse
from app.models import Platform, Product, Review
from app.crud import get_product_search, get_product_details, get_paginated_reviews
from app.config import settings

router = APIRouter(tags=["Catalog & Platforms"])


@router.get("/categories", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    """Lists product categories present in the local catalog."""
    rows = (
        db.query(Product.category)
        .filter(Product.category.isnot(None))
        .distinct()
        .order_by(Product.category.asc())
        .all()
    )
    return [category for (category,) in rows if category]

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
    category: Optional[str] = Query(None, description="Optional exact product category filter"),
    limit: int = Query(20, ge=1, le=100, description="Max search results"),
    db: Session = Depends(get_db)
):
    """Case-insensitive partial product name search on local catalog."""
    return get_product_search(db, query=q, limit=limit, category=category)


@router.get("/products/{product_id}", response_model=ProductDetailResponse)
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get full details for a single product including sentiment breakdown and platform stats.

    Only includes platforms where reviews exist for THIS exact product.
    Does not infer cross-platform identity from similar names.
    """
    product_details = get_product_details(db, product_id=product_id)

    if product_details is None:
        raise HTTPException(status_code=404, detail=f"Product with id={product_id} not found")

    return product_details


@router.get("/products/{product_id}/reviews", response_model=ReviewListResponse)
def list_product_reviews(
    product_id: int,
    platform: Optional[str] = Query(None, description="Optional platform code filter"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return paginated reviews linked to this exact catalog product ID."""
    if not db.query(Product.id).filter(Product.id == product_id).first():
        raise HTTPException(status_code=404, detail=f"Product with id={product_id} not found")

    return get_paginated_reviews(
        db,
        platform_code=platform,
        page=page,
        page_size=min(page_size, settings.MAX_PAGE_SIZE),
        product_id=product_id,
    )
