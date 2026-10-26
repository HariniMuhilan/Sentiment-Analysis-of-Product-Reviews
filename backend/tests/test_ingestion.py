from app.ingestion.parsers import (
    parse_amazon_record,
    parse_flipkart_record,
    parse_myntra_record,
    parse_meesho_record,
    parse_generic_record,
    parse_rating,
    parse_date,
    parse_stream
)
from datetime import datetime

def test_parse_rating():
    assert parse_rating("4.5") == 4.5
    assert parse_rating(5) == 5.0
    assert parse_rating("10") == 5.0 # Scaled down from 10
    assert parse_rating("invalid") is None
    assert parse_rating(None) is None

def test_parse_date():
    d = parse_date("2025-01-15")
    assert isinstance(d, datetime)
    assert d.year == 2025 and d.month == 1 and d.day == 15
    assert parse_date(None) is None

def test_parse_amazon_record():
    row = {
        "product_title": "Test Camera",
        "review_body": "Clear lens and sharp images.",
        "star_rating": "5.0",
        "review_id": "AMZ-999",
        "review_headline": "Great camera",
        "review_date": "2025-03-01"
    }
    rec = parse_amazon_record(row)
    assert rec is not None
    assert rec["platform_code"] == "amazon"
    assert rec["product_name"] == "Test Camera"
    assert rec["rating"] == 5.0
    assert rec["external_id"] == "AMZ-999"

def test_parse_stream_csv():
    csv_data = """external_id,platform,product_name,category,rating,headline,review_text,review_date,helpful_votes
T-1,amazon,Test Widget,Gadgets,5.0,Superb,Works like a charm,2025-01-01,2
T-2,flipkart,Test Widget,Gadgets,1.0,Bad,Broke instantly,2025-01-02,0
"""
    records = list(parse_stream(csv_data, platform_code="generic"))
    assert len(records) == 2
    assert records[0]["platform_code"] == "amazon"
    assert records[1]["platform_code"] == "flipkart"
