import math
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, distinct, case
from datetime import datetime
from app.models import Review, Product, Platform
from app.nlp.sentiment import MODEL_NAME, MODEL_VERSION

def calculate_wilson_interval(positive: int, total: int, z: float = 1.96) -> Tuple[float, float]:
    """
    Computes the 95% Wilson score interval for binomial proportions.
    Provides mathematically sound confidence bounds, especially for smaller samples.
    """
    if total == 0:
        return (0.0, 0.0)
    p = positive / total
    z2 = z * z
    denom = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denom
    margin = (z * math.sqrt((p * (1.0 - p) / total) + (z2 / (4.0 * total * total)))) / denom
    lower = max(0.0, round(center - margin, 4))
    upper = min(1.0, round(center + margin, 4))
    return (lower, upper)

def build_review_filter(
    db: Session,
    query: Optional[str] = None,
    platform_code: Optional[str] = None,
    category: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    sentiment: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    clauses = []
    if query and query.strip():
        term = f"%{query.strip()}%"
        clauses.append(or_(
            Review.product_name.ilike(term),
            Review.headline.ilike(term),
            Review.review_text.ilike(term)
        ))
    if platform_code and platform_code.lower() != "all":
        p = db.query(Platform).filter(Platform.code == platform_code.lower()).first()
        if p:
            clauses.append(Review.platform_id == p.id)
        else:
            clauses.append(Review.platform_id == -1) # No match
    if category and category.lower() != "all":
        clauses.append(Review.category.ilike(f"%{category.strip()}%"))
    if min_rating is not None:
        clauses.append(Review.rating >= min_rating)
    if max_rating is not None:
        clauses.append(Review.rating <= max_rating)
    if sentiment and sentiment.upper() != "ALL":
        clauses.append(Review.sentiment == sentiment.upper())
    if start_date:
        clauses.append(Review.review_date >= start_date)
    if end_date:
        clauses.append(Review.review_date <= end_date)

    return and_(*clauses) if clauses else True

def get_product_search(db: Session, query: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    stmt = db.query(
        Review.product_name,
        Review.category,
        func.count(Review.id).label("total_reviews"),
        func.avg(Review.rating).label("avg_rating")
    )
    if query and query.strip():
        stmt = stmt.filter(Review.product_name.ilike(f"%{query.strip()}%"))
    
    stmt = stmt.group_by(Review.product_name, Review.category).order_by(func.count(Review.id).desc()).limit(limit)
    rows = stmt.all()

    results = []
    for idx, (p_name, cat, rev_count, avg_r) in enumerate(rows):
        # find platforms for this product
        platforms = db.query(Platform.name).join(Review, Review.platform_id == Platform.id)\
            .filter(Review.product_name == p_name).distinct().all()
        plat_names = [p[0] for p in platforms]
        results.append({
            "id": idx + 1,
            "name": p_name,
            "category": cat or "General",
            "total_reviews": rev_count,
            "average_rating": round(float(avg_r), 2) if avg_r else None,
            "platforms": plat_names
        })
    return results

def get_aggregated_analysis(
    db: Session,
    query: Optional[str] = None,
    platform_code: Optional[str] = None,
    category: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    sentiment: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    filter_clause = build_review_filter(
        db, query, platform_code, category, min_rating, max_rating, sentiment, start_date, end_date
    )

    # 1. Total count & overall averages
    overall_stats = db.query(
        func.count(Review.id).label("total"),
        func.avg(Review.rating).label("avg_rating"),
        func.avg(Review.compound_score).label("avg_compound"),
        func.sum(case((Review.sentiment == 'POSITIVE', 1), else_=0)).label("pos_count"),
        func.sum(case((Review.sentiment == 'NEUTRAL', 1), else_=0)).label("neu_count"),
        func.sum(case((Review.sentiment == 'NEGATIVE', 1), else_=0)).label("neg_count")
    ).filter(filter_clause).first()

    total_reviews = overall_stats.total or 0
    avg_rating = round(float(overall_stats.avg_rating), 2) if overall_stats.avg_rating else None
    avg_compound = round(float(overall_stats.avg_compound), 4) if overall_stats.avg_compound else None
    pos_count = int(overall_stats.pos_count or 0)
    neu_count = int(overall_stats.neu_count or 0)
    neg_count = int(overall_stats.neg_count or 0)

    pos_pct = round((pos_count / total_reviews) * 100, 1) if total_reviews > 0 else 0.0
    neu_pct = round((neu_count / total_reviews) * 100, 1) if total_reviews > 0 else 0.0
    neg_pct = round((neg_count / total_reviews) * 100, 1) if total_reviews > 0 else 0.0

    # 2. Per-platform statistics
    all_platforms = db.query(Platform).all()
    platform_stats_list = []
    platforms_with_data = []
    platforms_without_data = []

    for plat in all_platforms:
        # Check platform data within the filtered query
        plat_filter = and_(filter_clause, Review.platform_id == plat.id)
        p_stat = db.query(
            func.count(Review.id).label("total"),
            func.avg(Review.rating).label("avg_rating"),
            func.avg(Review.compound_score).label("avg_compound"),
            func.sum(case((Review.sentiment == 'POSITIVE', 1), else_=0)).label("pos_count"),
            func.sum(case((Review.sentiment == 'NEUTRAL', 1), else_=0)).label("neu_count"),
            func.sum(case((Review.sentiment == 'NEGATIVE', 1), else_=0)).label("neg_count")
        ).filter(plat_filter).first()

        p_total = p_stat.total or 0
        if p_total > 0:
            platforms_with_data.append(plat.name)
            p_pos = int(p_stat.pos_count or 0)
            p_neu = int(p_stat.neu_count or 0)
            p_neg = int(p_stat.neg_count or 0)
            p_pos_pct = round((p_pos / p_total) * 100, 1)
            p_neu_pct = round((p_neu / p_total) * 100, 1)
            p_neg_pct = round((p_neg / p_total) * 100, 1)
            
            wilson_low, wilson_high = calculate_wilson_interval(p_pos, p_total)
            
            if p_total < 30:
                notes = f"Small sample size (N={p_total} < 30). High statistical uncertainty."
            else:
                notes = f"Adequate sample (N={p_total}). 95% Wilson positive sentiment CI: [{round(wilson_low*100, 1)}%, {round(wilson_high*100, 1)}%]."

            platform_stats_list.append({
                "platform_code": plat.code,
                "platform_name": plat.name,
                "review_count": p_total,
                "average_rating": round(float(p_stat.avg_rating), 2) if p_stat.avg_rating else None,
                "average_compound": round(float(p_stat.avg_compound), 4) if p_stat.avg_compound else None,
                "sentiment_breakdown": {
                    "positive": p_pos,
                    "neutral": p_neu,
                    "negative": p_neg,
                    "positive_pct": p_pos_pct,
                    "neutral_pct": p_neu_pct,
                    "negative_pct": p_neg_pct
                },
                "wilson_positive_interval": (wilson_low, wilson_high),
                "statistical_notes": notes
            })
        else:
            platforms_without_data.append(plat.name)

    # 3. Statistical Leader Evaluation (No arbitrary "winners")
    # Compare Wilson score confidence intervals among platforms with N >= 30
    sorted_platforms = sorted(
        platform_stats_list,
        key=lambda x: (x["sentiment_breakdown"]["positive_pct"], x["review_count"]),
        reverse=True
    )

    leader_platform = None
    is_significant = False
    explanation = ""
    sample_size_adequate = False

    if len(sorted_platforms) >= 2:
        top1 = sorted_platforms[0]
        top2 = sorted_platforms[1]
        t1_count = top1["review_count"]
        t2_count = top2["review_count"]

        if t1_count >= 30 and t2_count >= 30:
            sample_size_adequate = True
            low1, high1 = top1["wilson_positive_interval"]
            low2, high2 = top2["wilson_positive_interval"]
            
            # Non-overlapping intervals indicate statistically significant difference at 95% confidence
            if low1 > high2:
                leader_platform = top1["platform_name"]
                is_significant = True
                explanation = (
                    f"{top1['platform_name']} exhibits a statistically significant lead in positive sentiment "
                    f"({top1['sentiment_breakdown']['positive_pct']}%, CI [{round(low1*100,1)}%, {round(high1*100,1)}%]) "
                    f"over {top2['platform_name']} ({top2['sentiment_breakdown']['positive_pct']}%, CI [{round(low2*100,1)}%, {round(high2*100,1)}%]) "
                    f"at 95% confidence (p < 0.05)."
                )
            else:
                leader_platform = None
                is_significant = False
                explanation = (
                    f"No statistically significant winner. Although {top1['platform_name']} has a higher nominal positive "
                    f"rate ({top1['sentiment_breakdown']['positive_pct']}%), its 95% confidence interval [{round(low1*100,1)}%, {round(high1*100,1)}%] "
                    f"overlaps with {top2['platform_name']} [{round(low2*100,1)}%, {round(high2*100,1)}%]."
                )
        else:
            sample_size_adequate = False
            explanation = (
                f"Sample size too small (one or more platforms have N < 30 reviews). "
                f"Statistical significance cannot be reliably established."
            )
    elif len(sorted_platforms) == 1:
        explanation = f"Only one platform ({sorted_platforms[0]['platform_name']}) has ingested reviews matching this query. Cross-platform comparison not applicable."
    else:
        explanation = "No ingested review data found matching the selected query or filters."

    return {
        "query": query,
        "applied_filters": {
            "platform_code": platform_code,
            "category": category,
            "min_rating": min_rating,
            "max_rating": max_rating,
            "sentiment": sentiment,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "total_reviews": total_reviews,
        "average_rating": avg_rating,
        "average_compound": avg_compound,
        "sentiment_breakdown": {
            "positive": pos_count,
            "neutral": neu_count,
            "negative": neg_count,
            "positive_pct": pos_pct,
            "neutral_pct": neu_pct,
            "negative_pct": neg_pct
        },
        "platforms": platform_stats_list,
        "statistical_comparison": {
            "leader_platform": leader_platform,
            "is_statistically_significant": is_significant,
            "explanation": explanation,
            "sample_size_adequate": sample_size_adequate
        },
        "data_coverage": {
            "platforms_with_data": platforms_with_data,
            "platforms_without_data": platforms_without_data,
            "is_empty": (total_reviews == 0),
            "notice": (
                "Data is restricted to locally ingested and authorized review datasets. "
                "Missing platforms indicate that no dataset has been imported for that source."
            )
        },
        "model_metadata": {
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "threshold_positive": ">= 0.05",
            "threshold_negative": "<= -0.05",
            "methodology": "Rule-based lexical sentiment analysis via VADER with 95% Wilson confidence intervals."
        }
    }

def get_paginated_reviews(
    db: Session,
    query: Optional[str] = None,
    platform_code: Optional[str] = None,
    category: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    sentiment: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    filter_clause = build_review_filter(
        db, query, platform_code, category, min_rating, max_rating, sentiment, start_date, end_date
    )

    total = db.query(func.count(Review.id)).filter(filter_clause).scalar() or 0
    total_pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    rows = db.query(Review, Platform.name.label("platform_name"), Platform.code.label("platform_code"))\
        .join(Platform, Review.platform_id == Platform.id)\
        .filter(filter_clause)\
        .order_by(Review.review_date.desc(), Review.id.desc())\
        .offset(offset)\
        .limit(page_size)\
        .all()

    reviews = []
    for rev, p_name, p_code in rows:
        reviews.append({
            "id": rev.id,
            "external_id": rev.external_id,
            "platform_code": p_code,
            "platform_name": p_name,
            "product_name": rev.product_name,
            "category": rev.category,
            "headline": rev.headline,
            "review_text": rev.review_text,
            "rating": rev.rating,
            "helpful_votes": rev.helpful_votes,
            "review_date": rev.review_date,
            "sentiment": rev.sentiment,
            "compound_score": rev.compound_score,
            "confidence": rev.confidence,
            "model_name": rev.model_name,
            "model_version": rev.model_version,
            "analyzed_at": rev.analyzed_at
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "reviews": reviews
    }
