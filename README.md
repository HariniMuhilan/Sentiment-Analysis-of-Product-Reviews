# Sentiment Analysis Review

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.1-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end product review sentiment analysis application and reproducible research framework. The main searchable product corpus contains historical Amazon reviews from the UCSD McAuley Lab Amazon Reviews 2023 dataset in the All Beauty and Appliances categories. Separate research files include RePro, Brazilian Olist and B2W corpora, a small five-retailer smart-device benchmark, and a Bengali multilingual review benchmark. These datasets have different languages, sampling frames, and identifiers; they are kept separate from the searchable Amazon database. See [`Datasets/README.md`](Datasets/README.md) for sources, reuse terms, and limitations.

---

## 📌 Architecture & Research Structure

```
Sentiment-Analysis-of-Product-Reviews/
├── research/                    # Reproducible Research Specification & Protocol
│   ├── readiness_audit.md       # Research readiness audit and methodology corrections
│   ├── research_protocol.md     # Pre-registered hypotheses, annotation guide, & baselines
│   ├── data_sources.md          # Primary source ledger, licensing terms, & access blockers
│   ├── data_manifest.json       # SHA-256 data manifest and provenance records
│   ├── run_experiments.py       # Experiment reproduction runner & baseline benchmark script
│   ├── prepare_repro_benchmark.py # Privacy-minimized RePro corpus preparation
│   ├── run_repro_benchmark.py  # RePro cross-language benchmark runner
│   └── manuscript.md            # Venue-neutral academic research manuscript draft
├── results/                     # Machine-readable experiment outputs & tables
│   ├── experiment_summary.json  # Comprehensive metric outputs (VADER, ZeroR, ECE)
│   └── tables/                  # Markdown tables for manuscript reproduction
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, security headers, CORS, routing
│   │   ├── config.py            # Pydantic BaseSettings environment configuration
│   │   ├── database.py          # SQLAlchemy 2.0 engine & session management
│   │   ├── models.py            # Platform, Product, Review, AnalysisRun models
│   │   ├── schemas.py           # Strict Pydantic v2 request/response schemas
│   │   ├── crud.py              # Dynamic SQL aggregations, Z-tests, & Chi-Square tests
│   │   ├── nlp/
│   │   │   ├── sentiment.py     # VADER sentiment engine & intensity calibration
│   │   │   └── evaluate.py      # Precision, recall, macro F1, ECE, & baselines
│   │   ├── ingestion/
│   │   │   ├── parsers.py       # Amazon TSV, Flipkart CSV, Myntra, Meesho parsers
│   │   │   └── importer.py      # Normalization, validation, deduplication, batch DB insert
│   │   └── api/                 # Endpoints (/health, /products, /analysis, /reviews, etc.)
│   ├── tests/                   # 26 automated tests (pytest + httpx)
│   ├── run_ingest.py            # Dataset ingestion CLI tool
│   ├── ingest_repro_benchmark.py # Load the 3-class RePro gold subset for API evaluation
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
│   └── sample_authorized_reviews.csv # Curated demonstration fixture dataset
├── docker-compose.yml           # Production multi-container orchestration
├── .env.example                 # Environment variables template
└── LICENSE                      # MIT Open Source License
```

### Core Design Principles
1. **Zero Fabricated Data**: All numbers, averages, sentiment percentages, and platform distributions are computed via SQL aggregation (`COUNT`, `AVG`, `SUM(CASE ...)`) against persisted, locally ingested review records.
2. **Defensible Comparative Statistics**: Avoids arbitrary "winner" declarations. Employs formal **Two-Proportion $Z$-Tests**, **Pearson $\chi^2$ Tests of Independence**, and **95% Wilson Score Confidence Intervals**. Confounders (product mix, category disparity) are explicitly surfaced.
3. **No Live Web Scraping**: In compliance with marketplace terms of service, analysis runs solely on authorized, pre-collected datasets. Live platform scraping is strictly excluded and prohibited.
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

# Import the local research copy (download instructions: ../Datasets/README.md)
python ingest_ucsd_amazon_2023.py --categories All_Beauty Appliances

# Launch the FastAPI backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`. The research database is stored in `backend/sentiment_research.db` and is excluded from Git.

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

## 📥 Research Data and Additional Imports

Dataset sources, separate licenses, preparation steps, and limitations are documented in [`Datasets/README.md`](Datasets/README.md). Amazon review text and the populated application database remain local-only. The privacy-minimized B2W and RePro data files are tracked under their separate CC BY-NC-SA 4.0 terms; Olist data is kept separate from the searchable application database. The synthetic fixture is for software checks only and must not be mixed into empirical analysis.

---

## 🧪 Automated Testing & Research Reproduction

### 1. Research Experiment Runner & Baseline Comparisons
```bash
python research/run_experiments.py
```
Requires `Datasets/research/benchmark_annotated.csv` with independently adjudicated labels before producing accuracy, F1, or calibration results. It intentionally stops if no valid human-labeled benchmark exists. Star ratings are not ground-truth sentiment labels. The old 20-row synthetic fixture output in `results/` is marked and excluded from research claims.

RePro has its own reproducible cross-language stress benchmark:

```bash
python research/prepare_repro_benchmark.py
python research/run_repro_benchmark.py
```

The first command recreates privacy-minimized RePro files from the author release stored under `Datasets/B2WReviews01/raw/`. The second evaluates VADER on 7,985 non-mixed, human-labeled Brazilian Portuguese reviews and writes `results/repro_vader_benchmark.json` and `results/tables/repro_vader_benchmark.md`. Since VADER is English-oriented, the result is a cross-language stress baseline, not validated Portuguese performance. To expose these records in the API evaluation endpoint, run `python ingest_repro_benchmark.py` from `backend/`; it writes only to the separate benchmark table, not the product review table.

### 2. Backend Unit & Integration Tests (26 Tests)
```bash
cd backend
pytest -v
```
Tests cover:
- Health and readiness probes (`/api/health`, `/api/ready`)
- VADER classification thresholds, compound score bounds, and rating reconciliation
- Ingestion parsers (Amazon TSV, Flipkart CSV, Myntra, Meesho, generic streams)
- Missing value preservation (ensuring null ratings are never silently converted to 3.0)
- Statistical hypothesis testing (Two-Proportion Z-Test, Pearson $\chi^2$ 2x3 test, Holm-Bonferroni correction)
- Expected Calibration Error (ECE) and comparative baseline models (Majority Class ZeroR, Rating Heuristic)
- Cryptographic deduplication and corrupted record handling
- Dynamic SQL sentiment aggregations and search query filtering
- Paginated review querying and out-of-bounds boundary validation
- Model evaluation runner and confusion matrix calculation

### 3. Frontend Linting & Build
```bash
cd sentiment-dashboard
npm.cmd run lint    # Verifies oxlint rules (0 errors, 0 warnings)
npm.cmd run build   # Validates production bundle compilation
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
1. **Dataset rights**: Review the corpus curator's statement and applicable data terms before any public deployment or redistribution. The research copy is local and is not cleared for public data hosting; see [`research/data_sources.md`](research/data_sources.md).
2. **Reverse Proxy & TLS**: Ensure an SSL/TLS certificate (e.g., Let's Encrypt / Certbot) terminates HTTPS traffic before reaching Nginx.
3. **Environment Settings**: Set `ENVIRONMENT=production`, adjust `CORS_ORIGINS` to your public domain name, and configure `DATABASE_URL` (PostgreSQL recommended for high-concurrency production).
4. **Data Backups**: Establish a regular backup schedule for the local research database or PostgreSQL volume. Do not publish a backup containing source review text.

---

## 📄 License
This project is open-source under the terms of the [MIT License](LICENSE).
