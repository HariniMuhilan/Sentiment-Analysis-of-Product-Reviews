"""Focused endpoint check using an isolated in-memory SQLite database."""
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Platform, Product, Review
from app.api.products import get_product_cross_platform_analysis


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=engine)
TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def add_review(db, *, product, platform, review_id, sentiment, rating):
    db.add(Review(
        id=review_id,
        external_id=f"focused-{review_id}",
        platform_id=platform.id,
        product_id=product.id,
        product_name=product.name,
        category=product.category,
        review_text=f"Isolated check review {review_id}",
        rating=rating,
        review_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        sentiment=sentiment,
        compound_score=0.0,
        positive_score=1.0 if sentiment == "POSITIVE" else 0.0,
        neutral_score=1.0 if sentiment == "NEUTRAL" else 0.0,
        negative_score=1.0 if sentiment == "NEGATIVE" else 0.0,
        confidence=1.0,
        model_name="focused-check",
        model_version="1",
    ))


def main():
    with TestSession() as db:
        amazon = Platform(code="check_amazon", name="Check Amazon")
        ebay = Platform(code="check_ebay", name="Check eBay")
        target = Product(name="Focused Check Headphones", category="Electronics")
        similar = Product(name="Focused Check Headphones Pro", category="Electronics")
        db.add_all([amazon, ebay, target, similar])
        db.flush()

        review_id = 1
        for _ in range(40):
            add_review(
                db, product=target, platform=amazon, review_id=review_id,
                sentiment="POSITIVE", rating=0.0 if review_id == 1 else None,
            )
            review_id += 1
        for _ in range(35):
            add_review(
                db, product=target, platform=ebay, review_id=review_id,
                sentiment="NEGATIVE", rating=4.0 if review_id == 41 else None,
            )
            review_id += 1
        for _ in range(38):
            add_review(
                db, product=similar, platform=amazon, review_id=review_id,
                sentiment="POSITIVE", rating=5.0,
            )
            review_id += 1
        db.flush()

        result = get_product_cross_platform_analysis(target.id, db)
        by_code = {item["platform_code"]: item for item in result.platform_stats}

        assert result.total_reviews == 75, result.total_reviews
        assert set(by_code) == {"check_amazon", "check_ebay"}, by_code.keys()
        assert by_code["check_amazon"]["review_count"] == 40
        assert by_code["check_ebay"]["review_count"] == 35
        assert by_code["check_amazon"]["average_rating"] == 0.0
        assert by_code["check_ebay"]["average_rating"] == 4.0
        assert result.average_rating == 2.0, result.average_rating
        assert result.average_compound == 0.0, result.average_compound
        assert by_code["check_amazon"]["sentiment_breakdown"]["positive_pct"] == 100.0
        assert by_code["check_ebay"]["sentiment_breakdown"]["negative_pct"] == 100.0
        assert result.leader_platform == "Check Amazon", result.leader_platform
        assert result.p_value == 0.0, result.p_value
        assert result.is_significant is True
        print("PASS: isolation, platform percentages, weighted/null ratings, zero averages, and zero p-value")


if __name__ == "__main__":
    main()
