from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timezone
from app.database import get_db
from app.schemas import HealthResponse, ReadyResponse
from app.config import settings
from app.models import Review, Product, Platform
from app.nlp.sentiment import MODEL_NAME, MODEL_VERSION

router = APIRouter(tags=["Health & Status"])

@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    """Health check endpoint for liveness probes."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "database": db_status}
        )

    return HealthResponse(
        status="healthy",
        database=db_status,
        timestamp=datetime.now(timezone.utc),
        version=settings.APP_VERSION,
        nlp_model=f"{MODEL_NAME} (v{MODEL_VERSION})"
    )

@router.get("/ready", response_model=ReadyResponse)
def get_readiness(db: Session = Depends(get_db)):
    """Readiness probe checking database connectivity and data availability."""
    try:
        total_reviews = db.query(func.count(Review.id)).scalar() or 0
        total_products = db.query(func.count(Product.id)).scalar() or 0
        active_platforms = db.query(func.count(Platform.id)).scalar() or 0

        ready = True
        msg = "Ready to serve traffic" if total_reviews > 0 else "Ready, but review database is empty (no datasets ingested yet)"
        
        return ReadyResponse(
            ready=ready,
            total_reviews=total_reviews,
            total_products=total_products,
            platforms_active=active_platforms,
            message=msg
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )
