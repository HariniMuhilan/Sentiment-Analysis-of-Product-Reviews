from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import sqlalchemy as sa
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database import get_db
from app.schemas import (
    PlatformResponse,
    ProductSearchResult,
    ProductDetailResponse,
    ReviewListResponse,
    FullEvaluationResponse,
    ProductCrossPlatformAnalysisResponse,
)
from app.models import Platform, Product, Review
from app.crud import get_product_search, get_product_details, get_paginated_reviews, build_review_filter, calculate_wilson_interval, compute_two_proportion_z_test
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


@router.get("/products/{product_id}/analysis", response_model=ProductCrossPlatformAnalysisResponse)
def get_product_cross_platform_analysis(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Compute cross-retailer sentiment comparison for this exact product.

    Aggregates all reviews across platforms where this product exists.
    Returns VADER-based sentiment metrics and statistical comparisons.

    Does not infer product identity across marketplaces—only uses reviews
    linked to THIS catalog product ID.
    """
    filter_clause = build_review_filter(
        db, query=None, platform_code=None, category=None,
        min_rating=None, max_rating=None, sentiment=None,
        start_date=None, end_date=None
    )

    # Single SQL aggregate query with JOIN for platform info and case() for sentiment counts
    platform_stats = (
        db.query(
            Review.product_id.label("product_id"),
            Review.platform_id.label("platform_id"),
            func.count(Review.id).label("review_count"),
            func.avg(Review.rating).label("avg_rating"),
            func.avg(Review.compound_score).label("avg_compound"),
            func.sum(sa.case((Review.sentiment == 'POSITIVE', 1), else_=0)).label("pos_count"),
            func.sum(sa.case((Review.sentiment == 'NEUTRAL', 1), else_=0)).label("neu_count"),
            func.sum(sa.case((Review.sentiment == 'NEGATIVE', 1), else_=0)).label("neg_count"),
            func.count(Review.rating).label("rating_count"),
            func.count(Review.compound_score).label("compound_count"),
            Platform.code.label("platform_code"),
            Platform.name.label("platform_name")
        ).filter(Review.product_id == product_id, filter_clause)
        .join(Platform, Platform.id == Review.platform_id)
        .group_by(Review.platform_id, Platform.code, Platform.name)
        .all()
    )

    if not platform_stats:
        raise HTTPException(
            status_code=404,
            detail=f"No reviews found for product with id={product_id}"
        )

    pos_count = sum(int(row.pos_count or 0) for row in platform_stats)
    neu_count = sum(int(row.neu_count or 0) for row in platform_stats)
    neg_count = sum(int(row.neg_count or 0) for row in platform_stats)

    # Calculate overall metrics - sum review counts for total and use non-null counts for weighted averages
    total_reviews = sum(int(row.review_count or 0) for row in platform_stats)

    # Overall average rating: weight by platform's non-null rating count
    avg_rating_weighted_sum = 0.0
    rating_count_total = 0
    for row in platform_stats:
        if row.avg_rating is not None:
            avg_rating_weighted_sum += float(row.avg_rating or 0) * (row.rating_count or 0)
            rating_count_total += int(row.rating_count or 0)

    avg_rating = round(avg_rating_weighted_sum / rating_count_total, 2) if rating_count_total > 0 else None

    # Overall compound average: weight by platform's non-null compound count
    avg_compound_weighted_sum = 0.0
    compound_count_total = 0
    for row in platform_stats:
        if row.avg_compound is not None:
            avg_compound_weighted_sum += float(row.avg_compound or 0) * (row.compound_count or 0)
            compound_count_total += int(row.compound_count or 0)

    avg_compound = round(avg_compound_weighted_sum / compound_count_total, 4) if compound_count_total > 0 else None

    # Overall sentiment percentages: use total_reviews for denominator
    pos_pct = round((pos_count / total_reviews) * 100, 1) if total_reviews > 0 else 0.0
    neu_pct = round((neu_count / total_reviews) * 100, 1) if total_reviews > 0 else 0.0
    neg_pct = round((neg_count / total_reviews) * 100, 1) if total_reviews > 0 else 0.0

    # Per-platform stats with Wilson intervals
    platform_stats_list = []
    for row in platform_stats:
        p_total = int(row.review_count or 0)
        p_pos = int(row.pos_count or 0)
        p_neu = int(row.neu_count or 0)
        p_neg = int(row.neg_count or 0)

        # Use platform-specific review_count as denominator for sentiment percentages
        pos_pct_platform = round((p_pos / p_total) * 100, 1) if p_total > 0 else 0.0
        neu_pct_platform = round((p_neu / p_total) * 100, 1) if p_total > 0 else 0.0
        neg_pct_platform = round((p_neg / p_total) * 100, 1) if p_total > 0 else 0.0

        # Platform info already available from SQL JOIN - use directly
        platform_code = str(row.platform_code)
        platform_name_val = str(row.platform_name)

        if p_total > 0:
            wilson_low, wilson_high = calculate_wilson_interval(p_pos, p_total)
            notes = f"Adequate sample (N={p_total}). 95% Wilson positive sentiment CI: [{round(wilson_low*100, 1)}%, {round(wilson_high*100, 1)}%]."
        else:
            notes = "No reviews for this platform."

        platform_stats_list.append({
            "platform_code": platform_code,
            "platform_name": platform_name_val,
            "review_count": p_total,
            "average_rating": round(float(row.avg_rating), 2) if row.avg_rating is not None else None,
            "average_compound": round(float(row.avg_compound), 4) if row.avg_compound is not None else None,
            "sentiment_breakdown": {
                "positive": p_pos,
                "neutral": p_neu,
                "negative": p_neg,
                "positive_pct": pos_pct_platform,
                "neutral_pct": neu_pct_platform,
                "negative_pct": neg_pct_platform
            },
            "wilson_positive_interval": (wilson_low, wilson_high),
            "statistical_notes": notes
        })

    # Find leader and perform statistical comparison
    sorted_platforms = sorted(
        platform_stats_list,
        key=lambda x: (x["sentiment_breakdown"]["positive_pct"], x["review_count"]),
        reverse=True
    )

    # Leave comparison stats null unless we have adequate samples
    leader_platform = None
    is_significant = False
    z_statistic = p_value = effect_size = None
    explanation = ""
    sample_size_adequate = False

    if len(sorted_platforms) >= 2:
        top1 = sorted_platforms[0]
        top2 = sorted_platforms[1]

        # Only assign leader_platform when both platforms have at least 30 reviews
        sample_size_adequate = top1["review_count"] >= 30 and top2["review_count"] >= 30
        if sample_size_adequate:
            leader_platform = top1["platform_name"]

            p1_pos = top1["sentiment_breakdown"]["positive"]
            p2_pos = top2["sentiment_breakdown"]["positive"]

            z_res = compute_two_proportion_z_test(
                p1_pos, top1["review_count"],
                p2_pos, top2["review_count"]
            )
            z_statistic = round(z_res["z_stat"], 4)
            p_value = round(z_res["p_value"], 6) if z_res["p_value"] is not None else None
            effect_size = round(z_res["effect_size"], 4)
            is_significant = p_value is not None and p_value < 0.05

            explanation = (
                f"Z-statistic: {z_statistic}, P-value: {p_value}. "
                f"{'Statistically significant' if is_significant else 'Not statistically significant'} "
                f"difference in positive sentiment proportions. Effect size (Cohen's h): {effect_size}."
            )
        else:
            # Stats remain null, provide clear explanation when sample insufficient
            explanation = (
                f"Insufficient sample for comparison. Platform 1 ({top1['platform_name']}), N={top1['review_count']}, "
                f"and Platform 2 ({top2['platform_name']}), N={top2['review_count']}, do not both have 30+ reviews "
                f"required for statistical comparison."
            )
    else:
        # Insufficient platforms or samples - stats remain null, provide clear explanation
        if len(sorted_platforms) == 1:
            explanation = (
                f"Only one platform ({sorted_platforms[0]['platform_name']}) has reviews "
                f"for this product. Comparison requires at least two platforms."
            )
        else:
            # Two+ platforms but insufficient samples for comparison
            exp1 = sorted_platforms[0].get("statistical_notes", "")
            if "30+" in exp1:
                exp2 = exp1.replace("Adequate sample (N=", "Insufficient sample for comparison.")
            else:
                exp2 = f"Platform {sorted_platforms[0]['platform_name']} has {sorted_platforms[0]['review_count'] or 0} reviews. " \
                        f"Need at least 2 platforms with 30+ reviews each to compute statistical comparisons."
            explanation = f"{exp2}. Found {len(sorted_platforms)} platform(s) with reviews."

    return ProductCrossPlatformAnalysisResponse(
        total_reviews=total_reviews,
        average_rating=avg_rating,
        average_compound=avg_compound,
        overall_sentiment_breakdown={
            "positive": pos_count,
            "neutral": neu_count,
            "negative": neg_count,
            "positive_pct": pos_pct,
            "neutral_pct": neu_pct,
            "negative_pct": neg_pct
        },
        platform_stats=platform_stats_list,
        leader_platform=leader_platform,
        is_significant=is_significant,
        z_statistic=z_statistic,
        p_value=p_value,
        effect_size=effect_size,
        explanation=explanation,
        total_platforms_analyzed=len(platform_stats_list),
        data_coverage_notice=f"Data available for {len(platform_stats_list)} platform(s). Reviews linked to product ID {product_id} only."
    )
