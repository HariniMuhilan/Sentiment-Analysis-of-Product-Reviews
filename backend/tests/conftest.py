import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base, get_db
from app.main import app
from app.ingestion.importer import ensure_platforms_exist, import_records_from_stream

TEST_DB_URL = "sqlite:///./test_sentiment.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        ensure_platforms_exist(db)
        # Import sample records
        sample_path = Path(__file__).resolve().parent.parent.parent / "Datasets" / "sample_authorized_reviews.csv"
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                content = f.read()
            import_records_from_stream(db, content, platform_code="generic")
    finally:
        db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_sentiment.db"):
        try:
            os.remove("./test_sentiment.db")
        except Exception:
            pass

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
