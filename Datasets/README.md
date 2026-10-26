# Datasets & Acquisition Guide

This directory documents the data sources, licensing terms, schema specifications, and acquisition guidelines for the cross-platform sentiment analysis system.

---

## ⚖️ Legal & Compliance Framework

> **Important Policy Notice**:
> This project operates exclusively on **authorized, pre-collected, or permissible research datasets**. 
> Automated web scraping of Amazon, Flipkart, Myntra, or Meesho web pages or live search results is strictly **prohibited** under their respective Terms of Service and is **not implemented** in this repository.

All sentiment calculations and platform comparisons are computed solely against records loaded into the local database via authorized ingestion tools (`backend/run_ingest.py` or the `/api/ingest` endpoint).

---

## 📦 Platform Datasets Overview

### 1. Amazon Customer Reviews Dataset
- **Provider**: Amazon Web Services (AWS Open Data Program)
- **Format**: Tab-Separated Values (`.tsv`) or compressed `.tsv.gz`
- **License / Terms**: Non-commercial academic research and educational evaluation under the AWS Customer Reviews Public Dataset Terms.
- **Attributes Mapped**:
  | Original Field | Target Column | Description |
  |---|---|---|
  | `review_id` | `external_id` | Unique alphanumeric review ID |
  | `product_title` | `product_name` | Full catalog product title |
  | `product_category` | `category` | Marketplace category (e.g., Wireless, Electronics) |
  | `star_rating` | `rating` | Customer rating (1.0 to 5.0) |
  | `review_headline` | `headline` | Review title summary |
  | `review_body` | `review_text` | Full customer review text |
  | `helpful_votes` | `helpful_votes` | Helpful community feedback votes |
  | `review_date` | `review_date` | Date of publication (ISO YYYY-MM-DD) |

### 2. Flipkart E-Commerce Reviews
- **Provider**: Curated Public E-Commerce Research Corpus (`Dataset-SA.csv`)
- **Format**: Comma-Separated Values (`.csv`)
- **License / Terms**: Open research evaluation. Direct customer identifiers are excluded.
- **Attributes Mapped**:
  | Original Field | Target Column | Description |
  |---|---|---|
  | `ProductName` | `product_name` | Product name |
  | `Rate` / `Rating` | `rating` | Star rating (1.0 to 5.0) |
  | `Summary` | `headline` | Review headline |
  | `Review` | `review_text` | Full review feedback text |
  | `Date` | `review_date` | Published timestamp |

### 3. Myntra Fashion & Apparel Reviews
- **Format**: Comma-Separated Values (`.csv`)
- **Focus**: Apparel, footwear, fitment, and fabric feedback.
- **License / Terms**: Academic evaluation. Author personal identifiers (PII) stripped.
- **Attributes Mapped**:
  `product_name`, `brand` (mapped to `category`), `rating`, `review_text`, `review_date`.

### 4. Meesho Product Reviews
- **Format**: Comma-Separated Values (`.csv`)
- **Focus**: Value-for-money customer satisfaction across home and budget apparel categories.
- **License / Terms**: Anonymized evaluation corpus for NLP benchmarking.
- **Attributes Mapped**:
  `product_name`, `category`, `rating`, `review_text`, `review_date`.

---

## 🔒 Privacy & Data Retention Guidelines

1. **PII Stripping**: All user identifying attributes (customer real names, email addresses, street addresses, IP addresses) must be purged prior to ingestion.
2. **Deduplication**: Ingestion parsers compute a cryptographic hash (`SHA-256`) of `(platform, product_name, review_text)` and enforce unique `external_id` constraints to prevent replay inflation.
3. **Storage**: Ingested records reside in local storage (`sentiment.db` or PostgreSQL). Raw datasets larger than 100MB should remain on external storage or cloud buckets and are excluded from Git via `.gitignore`.

---

## 🚀 How to Ingest Datasets

### Option A: Using the CLI Tool
```bash
# Ingest Amazon TSV reviews
python backend/run_ingest.py --platform amazon --file path/to/amazon_reviews_us_Electronics.tsv

# Ingest Flipkart CSV reviews
python backend/run_ingest.py --platform flipkart --file path/to/flipkart_reviews.csv

# Ingest Generic / Unified CSV dataset
python backend/run_ingest.py --platform generic --file Datasets/sample_authorized_reviews.csv
```

### Option B: Using the Ingestion API
```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -F "platform=generic" \
  -F "file=@Datasets/sample_authorized_reviews.csv"
```

### Option C: Sample Demo Data
A curated sample dataset of multi-platform reviews is provided in `Datasets/sample_authorized_reviews.csv`. It can be ingested at any time to initialize or restore demo catalog data.
