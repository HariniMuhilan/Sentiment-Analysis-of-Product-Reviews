# Sentiment Analysis of Product Reviews

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.1-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end, cross-platform product review sentiment analysis system comparing customer feedback across **Amazon**, **Flipkart**, **Myntra**, and **Meesho**. Powered by a real Python FastAPI backend, rule-based NLP pipeline (VADER), statistical Wilson score confidence intervals, and a modern React 19 analytics dashboard.

---

## 📌 Architecture & Design Principles

```
Sentiment-Analysis-of-Product-Reviews/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, security headers, CORS, routing
│   │   ├── config.py            # Pydantic BaseSettings environment configuration
│   │   ├── database.py          # SQLAlchemy 2.0 engine & session management
│   │   ├── models.py            # Platform, Product, Review, AnalysisRun models
│   │   ├── schemas.py           # Strict Pydantic v2 request/response schemas
│   │   ├── crud.py              # Dynamic SQL aggregations & Wilson CI calculations
│   │   ├── nlp/
│   │   │   ├── sentiment.py     # VADER sentiment engine & valence calibration
│   │   │   └── evaluate.py      # Precision, recall, macro F1, and confusion matrix
│   │   ├── ingestion/
│   │   │   ├── parsers.py       # Amazon TSV, Flipkart CSV, Myntra, Meesho parsers
│   │   │   └── importer.py      # Normalization, validation, deduplication, batch DB insert
│   │   └── api/                 # Endpoints (/health, /products, /analysis, /reviews, etc.)
│   ├── tests/                   # 19 automated tests (pytest + httpx)
│   ├── run_ingest.py            # Dataset ingestion CLI tool
│   └── requirements.txt         # Pinned backend dependencies
├── sentiment-dashboard/         # React 19 + Vite frontend
│   ├── src/
│   │   ├── api/client.js        # Strongly typed API client connecting to backend
│   │   ├── components/          # SearchBar, Filters, SummaryCards, PlatformComparison,
│   │   │                        # ReviewList, ModelEvaluationModal, DataProvenanceBanner
│   │   ├── App.jsx              # Responsive dashboard analytics state
│   │   └── index.css            # Accessible dark glassmorphism styling tokens
│   ├── nginx.conf               # Production Nginx reverse proxy configuration
│   └── Dockerfile               # Multi-stage production container build
├── Datasets/
│   ├── README.md                # Platform source documentation, licenses & acquisition
│   └── sample_authorized_reviews.csv # Curated authorized demo dataset
├── docker-compose.yml           # Production multi-container orchestration
├── .env.example                 # Environment variables template
└── LICENSE                      # MIT Open Source License
```

### Core Design Principles
1. **Zero Fabricated Data**: All numbers, averages, sentiment percentages, and platform distributions are computed via SQL aggregation (`COUNT`, `AVG`, `SUM(CASE ...)`) against persisted, locally ingested review records.
2. **Defensible Comparative Statistics**: Avoids arbitrary "winner" declarations. Employs 95% Wilson score confidence intervals for positive sentiment proportions. Differences are only labeled statistically significant if sample sizes satisfy $N \ge 30$ and confidence intervals do not overlap ($p < 0.05$).
3. **No Live Web Scraping**: In compliance with marketplace terms of service, analysis runs solely on authorized, pre-collected datasets. Live platform scraping is strictly excluded.
4. **Boundary Validation & Security**: Request validation using Pydantic v2 schemas, strict CORS settings, rate limits, and security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`).

---

## 🔬 NLP Sentiment Methodology

### Lexical Valence Engine
The sentiment engine utilizes the **VADER** (*Valence Aware Dictionary and s-Sentiment Reasoner*) lexicon:
- **Compound Score ($C \in [-1.0, 1.0]$)**: Normalized metric representing text sentiment intensity.
- **Classification Boundaries**:
  - $\mathbf{C \ge +0.05} \implies$ **POSITIVE**
  - $\mathbf{-0.05 < C < +0.05} \implies$ **NEUTRAL**
  - $\mathbf{C \le -0.05} \implies$ **NEGATIVE**
- **Confidence Metric**: Delineated from valence; measures categorical decisiveness and degree of separation from neutrality ($[0.50, 1.00]$).
- **Model Tracking**: Every stored review records `model_name="vader-lexicon-v3.3"`, `model_version="1.0.0"`, and the processing timestamp.

### Statistical Wilson Confidence Interval
Given positive review count $X$ and sample size $N$ with proportion $\hat{p} = X/N$:
$$w = \frac{\hat{p} + \frac{z^2}{2N} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{N} + \frac{z^2}{4N^2}}}{1 + \frac{z^2}{N}} \quad (z = 1.96 \text{ for } 95\% \text{ confidence})$$

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** and `npm`

### 1. Set Up Backend
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Pre-download VADER lexicon
python -c "import nltk; nltk.download('vader_lexicon')"

# Ingest sample authorized dataset into local SQLite database
python run_ingest.py --platform generic --file ../Datasets/sample_authorized_reviews.csv

# Launch the FastAPI backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

### 2. Set Up Frontend Dashboard
In a new terminal:
```bash
# Navigate to dashboard directory
cd sentiment-dashboard

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📥 Ingesting Custom Datasets

The repository includes a reproducible ingestion CLI capable of parsing, validating, deduplicating, and analyzing dataset files:

```bash
# Ingest Amazon Customer Reviews TSV
python backend/run_ingest.py --platform amazon --file path/to/amazon_reviews.tsv

# Ingest Flipkart CSV
python backend/run_ingest.py --platform flipkart --file path/to/flipkart_reviews.csv

# Ingest Myntra CSV
python backend/run_ingest.py --platform myntra --file path/to/myntra_reviews.csv

# Ingest Meesho CSV
python backend/run_ingest.py --platform meesho --file path/to/meesho_reviews.csv

# Ingest unified multi-platform CSV
python backend/run_ingest.py --platform generic --file Datasets/sample_authorized_reviews.csv
```

---

## 🧪 Automated Testing

### Backend Unit & Integration Tests (19 Tests)
```bash
cd backend
pytest -v
```
Tests cover:
- Health and readiness probes (`/api/health`, `/api/ready`)
- VADER classification thresholds, compound score bounds, and rating reconciliation
- Ingestion parsers (Amazon TSV, Flipkart CSV, Myntra, Meesho, generic streams)
- Cryptographic deduplication and corrupted record handling
- Dynamic SQL sentiment aggregations and search query filtering
- Paginated review querying and out-of-bounds boundary validation
- Model evaluation runner and confusion matrix calculation

### Frontend Linting & Build
```bash
cd sentiment-dashboard
npm run lint    # Verifies oxlint rules (0 errors, 0 warnings)
npm run build   # Validates production bundle compilation
```

---

## 🐳 Docker & Production Deployment

### Multi-Container Deployment via Docker Compose
```bash
# Build and launch both backend and frontend containers
docker compose up --build -d
```
- **Frontend Dashboard**: Serves on `http://localhost:80` via Nginx.
- **Backend API**: Serves on `http://localhost:8000` via Uvicorn.
- **Persistent Volume**: SQLite database is persisted in the `backend_data` volume.

---

## 📡 API Contract Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Liveness probe returning status, database connectivity, and model version |
| `GET` | `/api/ready` | Readiness probe checking review counts and active platforms |
| `GET` | `/api/platforms` | Returns supported platforms, review counts, and date ranges |
| `GET` | `/api/products` | Case-insensitive catalog product search with review volume |
| `GET` | `/api/analysis` | Dynamic sentiment breakdown, Wilson intervals, and platform comparisons |
| `GET` | `/api/reviews` | Paginated reviews with filtering by platform, rating, and sentiment |
| `POST`| `/api/ingest` | Multipart upload for importing and analyzing dataset files |
| `POST`| `/api/reanalyze` | Re-runs sentiment analysis across catalog when thresholds update |
| `GET` | `/api/evaluation`| Model evaluation report (Macro F1, Precision, Recall, Confusion Matrix) |

---

## 📋 Operator Prerequisites for Public Deployment

Before deploying this application to a public server or cloud provider:
1. **Dataset Authorization**: Confirm that you have obtained research data licenses or permission for all imported review collections. Refer to [`Datasets/README.md`](Datasets/README.md).
2. **Reverse Proxy & TLS**: Ensure an SSL/TLS certificate (e.g., Let's Encrypt / Certbot) terminates HTTPS traffic before reaching Nginx.
3. **Environment Settings**: Set `ENVIRONMENT=production`, adjust `CORS_ORIGINS` to your public domain name, and configure `DATABASE_URL` (PostgreSQL recommended for high-concurrency production).
4. **Data Backups**: Establish a regular backup schedule for the database (`sentiment.db` or PostgreSQL volume).

---

## 📄 License
This project is open-source under the terms of the [MIT License](LICENSE).
