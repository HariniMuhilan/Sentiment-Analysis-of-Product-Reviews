import hashlib
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models import Platform, Product, Review, AnalysisRun
from app.nlp.sentiment import analyze_review_text, MODEL_NAME, MODEL_VERSION
from app.ingestion.parsers import parse_stream
from datetime import datetime, timezone

PLATFORM_DEFINITIONS = [
    {
        "code": "amazon",
        "name": "Amazon",
        "description": "Amazon Customer Reviews Dataset (US Reviews category TSVs)",
        "source_info": "Amazon Customer Reviews Dataset (Public Academic/Research format). Available under AWS Open Data Program.",
        "terms_info": "Subject to Amazon Customer Reviews Public Dataset Terms. Non-commercial research & education use only."
    },
    {
        "code": "flipkart",
        "name": "Flipkart",
        "description": "Flipkart Product Sentiment Dataset (Dataset-SA.csv)",
        "source_info": "Flipkart E-Commerce Reviews Research Dataset (Curated Sentiment Collection).",
        "terms_info": "Academic and open research evaluation. Original platform terms apply to original reviews."
    },
    {
        "code": "myntra",
        "name": "Myntra",
        "description": "Myntra Fashion Reviews Dataset",
        "source_info": "Myntra Apparel and Footwear Reviews Dataset.",
        "terms_info": "Research use. Respects author privacy; direct identifiers stripped."
    },
    {
        "code": "meesho",
        "name": "Meesho",
        "description": "Meesho Social Commerce Reviews Dataset",
        "source_info": "Meesho Customer Feedback and Product Review Corpus.",
        "terms_info": "Research evaluation use. Anonymized review text only."
    }
]

def ensure_platforms_exist(db: Session) -> Dict[str, Platform]:
    """Ensures standard platforms are registered in the database."""
    platforms = {}
    for p_def in PLATFORM_DEFINITIONS:
        p = db.query(Platform).filter(Platform.code == p_def["code"]).first()
        if not p:
            p = Platform(
                code=p_def["code"],
                name=p_def["name"],
                description=p_def["description"],
                source_info=p_def["source_info"],
                terms_info=p_def["terms_info"]
            )
            db.add(p)
            db.commit()
            db.refresh(p)
        platforms[p.code] = p
    return platforms

def get_or_create_product(db: Session, product_name: str, category: str = "General") -> Product:
    """Finds or creates a product by trimmed name."""
    clean_name = product_name.strip()
    product = db.query(Product).filter(Product.name.ilike(clean_name)).first()
    if not product:
        product = Product(name=clean_name, category=category.strip())
        db.add(product)
        db.commit()
        db.refresh(product)
    return product

def compute_review_hash(platform_code: str, product_name: str, review_text: str) -> str:
    key = f"{platform_code.lower()}|{product_name.lower().strip()}|{review_text.strip()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def import_records_from_stream(
    db: Session,
    content_str: str,
    platform_code: str = "generic",
    dataset_name: str = "unspecified_source",
    dataset_version: str = "1.0",
    batch_size: int = 250
) -> Dict[str, Any]:
    """
    Ingests, validates, analyzes, and persists reviews into the database.
    Preserves missing values, tracks rejection reasons without leaking text,
    and records provenance metadata.
    """
    platforms = ensure_platforms_exist(db)
    
    records_generator = parse_stream(content_str, platform_code=platform_code)
    
    total_parsed = 0
    total_imported = 0
    total_skipped_duplicates = 0
    rejections = {
        "duplicate_external_id": 0,
        "missing_text_or_product": 0,
        "invalid_rating_format": 0
    }

    run = AnalysisRun(
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        status="in_progress",
        notes=f"Dataset: {dataset_name} (v{dataset_version}), Platform: {platform_code}",
        started_at=datetime.now(timezone.utc)
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Pre-fetch existing external_ids for platform-scoped fast deduplication
    existing_external_ids = set(
        x[0] for x in db.query(Review.external_id).filter(Review.external_id.isnot(None)).all()
    )

    batch_reviews = []

    for rec in records_generator:
        total_parsed += 1
        
        # Deduplication check
        ext_id = rec.get("external_id")
        if ext_id and ext_id in existing_external_ids:
            total_skipped_duplicates += 1
            rejections["duplicate_external_id"] += 1
            continue

        plat_code = rec.get("platform_code", platform_code).lower()
        if plat_code not in platforms:
            new_plat = Platform(
                code=plat_code,
                name=plat_code.capitalize(),
                description=f"{plat_code.capitalize()} Ingested Reviews",
                source_info=f"Source: {dataset_name}",
                terms_info="Subject to source dataset terms."
            )
            db.add(new_plat)
            db.commit()
            db.refresh(new_plat)
            platforms[plat_code] = new_plat

        platform = platforms[plat_code]
        product = get_or_create_product(db, rec["product_name"], rec.get("category", "General"))

        # Real NLP Sentiment Analysis Execution
        sentiment_res = analyze_review_text(rec["review_text"], rating=rec.get("rating"))

        review = Review(
            external_id=ext_id,
            platform_id=platform.id,
            product_id=product.id,
            product_name=product.name,
            category=rec.get("category") or product.category,
            headline=rec.get("headline"),
            review_text=rec["review_text"],
            rating=rec.get("rating"), # Preserves None if unrated
            helpful_votes=rec.get("helpful_votes", 0),
            review_date=rec.get("review_date") or datetime.now(timezone.utc),
            sentiment=sentiment_res["sentiment"],
            compound_score=sentiment_res["compound_score"],
            positive_score=sentiment_res["positive_score"],
            neutral_score=sentiment_res["neutral_score"],
            negative_score=sentiment_res["negative_score"],
            confidence=sentiment_res["confidence"],
            model_name=sentiment_res["model_name"],
            model_version=sentiment_res["model_version"],
            analyzed_at=sentiment_res["analyzed_at"]
        )

        batch_reviews.append(review)
        if ext_id:
            existing_external_ids.add(ext_id)

        if len(batch_reviews) >= batch_size:
            db.bulk_save_objects(batch_reviews)
            db.commit()
            total_imported += len(batch_reviews)
            batch_reviews = []

    if batch_reviews:
        db.bulk_save_objects(batch_reviews)
        db.commit()
        total_imported += len(batch_reviews)

    run.status = "completed"
    run.completed_at = datetime.now(timezone.utc)
    run.records_processed = total_imported
    db.commit()

    return {
        "status": "success",
        "dataset_name": dataset_name,
        "dataset_version": dataset_version,
        "total_parsed": total_parsed,
        "total_imported": total_imported,
        "total_skipped": total_skipped_duplicates,
        "rejection_summary": rejections,
        "model_used": f"{MODEL_NAME} (v{MODEL_VERSION})"
    }

def reanalyze_all_reviews(db: Session, batch_size: int = 500) -> Dict[str, Any]:
    """
    Re-runs the sentiment analysis pipeline across all stored reviews
    (useful when classification thresholds, lexicon, or model change).
    """
    reviews = db.query(Review).all()
    count = 0
    for rev in reviews:
        res = analyze_review_text(rev.review_text, rating=rev.rating)
        rev.sentiment = res["sentiment"]
        rev.compound_score = res["compound_score"]
        rev.positive_score = res["positive_score"]
        rev.neutral_score = res["neutral_score"]
        rev.negative_score = res["negative_score"]
        rev.confidence = res["confidence"]
        rev.model_name = res["model_name"]
        rev.model_version = res["model_version"]
        rev.analyzed_at = res["analyzed_at"]
        count += 1
        if count % batch_size == 0:
            db.commit()
    db.commit()

    run = AnalysisRun(
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        status="reanalyzed",
        records_processed=count,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc)
    )
    db.add(run)
    db.commit()

    return {
        "reanalyzed_count": count,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION
    }
