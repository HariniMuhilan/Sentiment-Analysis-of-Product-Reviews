from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.ingestion.importer import import_records_from_stream, reanalyze_all_reviews
from app.config import settings

router = APIRouter(tags=["Ingestion & Maintenance"])

@router.post("/ingest")
async def ingest_dataset_file(
    platform: str = Form(..., description="Platform code (amazon, flipkart, myntra, meesho, generic)"),
    file: UploadFile = File(..., description="CSV, TSV, or JSONL review dataset file"),
    db: Session = Depends(get_db)
):
    """
    Ingests an authorized dataset file, validates records, runs sentiment classification,
    and updates catalog aggregations.
    """
    # Check file size limit
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds max allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    try:
        text_content = contents.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to decode uploaded file as text: {str(e)}"
        )

    result = import_records_from_stream(
        db,
        content_str=text_content,
        platform_code=platform
    )
    return result

@router.post("/reanalyze")
def trigger_reanalysis(db: Session = Depends(get_db)):
    """
    Re-runs sentiment analysis across all existing records with the active model.
    """
    return reanalyze_all_reviews(db)
