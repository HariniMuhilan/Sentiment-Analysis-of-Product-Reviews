import csv
import io
import json
from datetime import datetime
from typing import List, Dict, Any, Generator

def parse_date(date_str: Any) -> datetime | None:
    if not date_str:
        return None
    date_str = str(date_str).strip()
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d, %Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def parse_rating(rating_val: Any) -> float | None:
    if rating_val is None:
        return None
    try:
        r = float(str(rating_val).strip())
        if 1.0 <= r <= 5.0:
            return r
        # Some datasets scale to 10 or 100:
        if 5.0 < r <= 10.0:
            return round(r / 2.0, 1)
        if 10.0 < r <= 100.0:
            return round(r / 20.0, 1)
    except (ValueError, TypeError):
        return None
    return None

def parse_amazon_record(row: Dict[str, str]) -> Dict[str, Any] | None:
    """Parses an Amazon TSV or CSV row."""
    # Columns may include: product_title, review_headline, review_body, star_rating, review_date, review_id
    product_name = row.get("product_title") or row.get("product_name") or row.get("title")
    text = row.get("review_body") or row.get("review_text") or row.get("text")
    if not product_name or not text:
        return None
    
    rating = parse_rating(row.get("star_rating") or row.get("rating"))
    if rating is None:
        rating = 3.0 # Default neutral mid-point if unrated

    return {
        "external_id": row.get("review_id"),
        "platform_code": "amazon",
        "product_name": product_name.strip(),
        "category": (row.get("product_category") or row.get("category") or "General").strip(),
        "headline": (row.get("review_headline") or "").strip()[:500],
        "review_text": text.strip(),
        "rating": rating,
        "helpful_votes": int(row.get("helpful_votes") or 0) if str(row.get("helpful_votes", "")).isdigit() else 0,
        "review_date": parse_date(row.get("review_date"))
    }

def parse_flipkart_record(row: Dict[str, str]) -> Dict[str, Any] | None:
    """Parses a Flipkart CSV row."""
    product_name = row.get("product_name") or row.get("ProductName") or row.get("Product_Name")
    text = row.get("review_text") or row.get("Review") or row.get("Summary") or row.get("Review_Text")
    if not product_name or not text:
        return None
    
    rating = parse_rating(row.get("rating") or row.get("Rate") or row.get("Rating"))
    if rating is None:
        rating = 3.0

    return {
        "external_id": row.get("review_id") or row.get("id"),
        "platform_code": "flipkart",
        "product_name": product_name.strip(),
        "category": (row.get("category") or "General").strip(),
        "headline": (row.get("review_title") or row.get("Summary") or "").strip()[:500],
        "review_text": text.strip(),
        "rating": rating,
        "helpful_votes": 0,
        "review_date": parse_date(row.get("review_date") or row.get("Date"))
    }

def parse_myntra_record(row: Dict[str, str]) -> Dict[str, Any] | None:
    """Parses a Myntra CSV row."""
    product_name = row.get("product_name") or row.get("ProductName") or row.get("Product_Title")
    text = row.get("review_text") or row.get("Review") or row.get("Review_Text")
    if not product_name or not text:
        return None
    
    rating = parse_rating(row.get("rating") or row.get("Rating"))
    if rating is None:
        rating = 3.0

    return {
        "external_id": row.get("review_id"),
        "platform_code": "myntra",
        "product_name": product_name.strip(),
        "category": (row.get("category") or row.get("brand") or "Fashion & Apparel").strip(),
        "headline": (row.get("review_title") or row.get("headline") or "").strip()[:500],
        "review_text": text.strip(),
        "rating": rating,
        "helpful_votes": 0,
        "review_date": parse_date(row.get("review_date") or row.get("Date"))
    }

def parse_meesho_record(row: Dict[str, str]) -> Dict[str, Any] | None:
    """Parses a Meesho CSV row."""
    product_name = row.get("product_name") or row.get("ProductName") or row.get("Product")
    text = row.get("review_text") or row.get("Review") or row.get("Comment")
    if not product_name or not text:
        return None
    
    rating = parse_rating(row.get("rating") or row.get("Rating") or row.get("star_rating"))
    if rating is None:
        rating = 3.0

    return {
        "external_id": row.get("review_id"),
        "platform_code": "meesho",
        "product_name": product_name.strip(),
        "category": (row.get("category") or "Affordable Fashion & Home").strip(),
        "headline": (row.get("headline") or "").strip()[:500],
        "review_text": text.strip(),
        "rating": rating,
        "helpful_votes": 0,
        "review_date": parse_date(row.get("review_date") or row.get("Date"))
    }

def parse_generic_record(row: Dict[str, str], default_platform: str = "amazon") -> Dict[str, Any] | None:
    """Parses a generic or unified CSV/JSON review row."""
    product_name = (
        row.get("product_name") or row.get("product_title") or 
        row.get("product") or row.get("title")
    )
    text = (
        row.get("review_text") or row.get("review_body") or 
        row.get("review") or row.get("text") or row.get("comment")
    )
    if not product_name or not text:
        return None

    platform_code = (
        row.get("platform") or row.get("platform_code") or default_platform
    ).strip().lower()

    rating = parse_rating(row.get("rating") or row.get("star_rating") or row.get("rate"))
    if rating is None:
        rating = 3.0

    return {
        "external_id": row.get("external_id") or row.get("review_id") or row.get("id"),
        "platform_code": platform_code,
        "product_name": product_name.strip(),
        "category": (row.get("category") or row.get("product_category") or "General").strip(),
        "headline": (row.get("headline") or row.get("review_headline") or row.get("summary") or "").strip()[:500],
        "review_text": text.strip(),
        "rating": rating,
        "helpful_votes": int(row.get("helpful_votes") or 0) if str(row.get("helpful_votes", "")).isdigit() else 0,
        "review_date": parse_date(row.get("review_date") or row.get("date"))
    }

def parse_stream(
    content_str: str, 
    platform_code: str = "generic",
    delimiter: str = ","
) -> Generator[Dict[str, Any], None, None]:
    """Yields parsed and normalized records from CSV, TSV, or JSON lines."""
    content_str = content_str.strip()
    if not content_str:
        return

    # Auto-detect JSON lines vs CSV/TSV
    if content_str.startswith("{"):
        for line in content_str.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                rec = parse_generic_record(row, default_platform=platform_code)
                if rec:
                    yield rec
            except json.JSONDecodeError:
                continue
        return

    # Auto-detect TSV if delimiter wasn't explicitly changed and tab is present in header
    first_line = content_str.splitlines()[0]
    if "\t" in first_line and delimiter == ",":
        delimiter = "\t"

    reader = csv.DictReader(io.StringIO(content_str), delimiter=delimiter)
    parser_dispatch = {
        "amazon": parse_amazon_record,
        "flipkart": parse_flipkart_record,
        "myntra": parse_myntra_record,
        "meesho": parse_meesho_record,
    }
    parser = parser_dispatch.get(platform_code.lower(), lambda r: parse_generic_record(r, default_platform=platform_code))

    for row in reader:
        rec = parser(row)
        if rec:
            yield rec
