# Research data

## Amazon Reviews 2023 (UCSD McAuley Lab)

The local research database now contains **8,349,286 Amazon reviews**: 2,797,473 from the full **All_Beauty** and **Appliances** subsets, plus **5,551,813 reviews** for the **1,000 Electronics products with the highest source metadata review counts**. It also includes **2,370** reviews from the five-retailer Virtual Assistant Devices benchmark, for **8,351,656 total records**. Electronics files are stored in `%LOCALAPPDATA%\SentimentAnalysisReview\raw`, outside the OneDrive checkout, and are not committed. Selection uses 2023 source metadata counts; it is not a current popularity ranking or a representative sample of all Electronics products. Exact counts and hashes are in `research/data_manifest.json`.

- Dataset page and downloads: <https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023>
- Dataset paper: Hou et al., *Bridging Language and Items for Retrieval and Recommendation* (2024), <https://arxiv.org/abs/2403.03952>
- Source collection period: May 1996 through September 2023; records are historical, not live marketplace data.
- Curator's licensing statement: no license is assigned by the curators; the files are provided primarily for research. Use only for research after reviewing the source terms and applicable law. Do not publish or redistribute the raw corpus or a database containing its review text without permission.
- The Amazon records represent Amazon only. Cross-retailer reviews come from the separate Virtual Assistant Devices dataset documented below. Neither source provides current stock or current prices. Item metadata prices are often missing and are historical; they must not be presented as current prices.

The original Amazon review text and item metadata are stored under `Datasets/research/raw/`; the new Electronics files are under `%LOCALAPPDATA%\SentimentAnalysisReview\raw`. `.gitignore` excludes files kept in the checkout, and the local SQLite database is excluded as well. Keep Amazon files and the populated database local; do not commit or push them to GitHub.

## Download the research files

From the repository root in PowerShell. The Electronics files go outside the OneDrive checkout:

```powershell
New-Item -ItemType Directory -Force Datasets/research/raw | Out-Null
curl.exe -L --fail --retry 3 -o Datasets/research/raw/All_Beauty.jsonl `
  "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/review_categories/All_Beauty.jsonl?download=true"
curl.exe -L --fail --retry 3 -o Datasets/research/raw/meta_All_Beauty.jsonl `
  "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/meta_categories/meta_All_Beauty.jsonl?download=true"
curl.exe -L --fail --retry 3 -o Datasets/research/raw/Appliances.jsonl `
  "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/review_categories/Appliances.jsonl?download=true"
curl.exe -L --fail --retry 3 -o Datasets/research/raw/meta_Appliances.jsonl `
  "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/meta_categories/meta_Appliances.jsonl?download=true"
$dataDir = Join-Path $env:LOCALAPPDATA 'SentimentAnalysisReview\raw'
New-Item -ItemType Directory -Force $dataDir | Out-Null
curl.exe -L --fail --retry 3 --retry-delay 2 --continue-at - -o (Join-Path $dataDir 'Electronics.jsonl') `
  "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/review_categories/Electronics.jsonl?download=true"
curl.exe -L --fail --retry 3 --retry-delay 2 --continue-at - -o (Join-Path $dataDir 'meta_Electronics.jsonl') `
  "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/meta_categories/meta_Electronics.jsonl?download=true"
```

## Import into the local application

The default database path is `backend/sentiment_research.db`. On this PC, `backend/.env` points the application to `%LOCALAPPDATA%\SentimentAnalysisReview\sentiment_research.db` so the growing research database stays outside OneDrive. From the repository root:

```powershell
cd backend
..\.venv\Scripts\python.exe ingest_ucsd_amazon_2023.py --categories All_Beauty Appliances
..\.venv\Scripts\python.exe ingest_ucsd_amazon_2023.py --data-dir "$env:LOCALAPPDATA\SentimentAnalysisReview\raw" --categories Electronics --top-products 1000
```

The importer reads JSONL incrementally, matches reviews to item titles from the metadata, computes the project's documented VADER scores, and commits in batches. It is safe to rerun: deterministic review IDs are used to skip records already imported. `--top-products 1000` ranks items by the source metadata `rating_number` field and imports every matching text-bearing review for the selected products; it does not claim current popularity. The source Electronics files are about 22.6 GB of reviews plus 5.2 GB of metadata. The importer scans the full review file to find selected products, but analyzes sentiment only for matching reviews. Add `--max-records 1000` for a quick smoke run; that limited run is not the final catalog.

The original 43-row synthetic fixture remains available at `Datasets/sample_authorized_reviews.csv` for tests and UI demos only. It is not part of the research database. Do not use it as empirical evidence.

## Other marketplaces

No authorized Flipkart, Myntra, or Meesho review corpus is currently included. Community uploads with unclear provenance or scraping-derived data are excluded. Cross-platform claims require licensed data or written research access from each marketplace.

## Olist Brazil (supplementary marketplace corpus)

The project includes four source tables from the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), published under **CC BY-NC-SA 4.0**. It provides a second named e-commerce source alongside Amazon. Only orders with an unambiguous one-product link and written review text are prepared: the current snapshot yields 40,317 records from 99,224 order-level review rows. Product names are not included, so this supports separate platform/category-level analysis, not matching the same product model across Amazon and Olist.

The reviews are primarily Portuguese, so the current VADER model must not be treated as valid for this corpus. The 1–5 order rating is a weak satisfaction signal, not human-annotated sentiment. See [`OlistBrazilianEcommerce/README.md`](OlistBrazilianEcommerce/README.md) for the license, provenance, preparation command, hashes, and limits. The prepared rows are kept out of the main application database until Portuguese-capable sentiment analysis is added.

## Americanas.com / B2W-Reviews01

The repository also includes a cleaned derivative of the real B2W-Reviews01 product-review corpus: **132,301** text-bearing reviews from Americanas.com, with product IDs/names, categories, 1–5 ratings, and review dates. Its CC BY-NC-SA 4.0 source is published by B2W Digital through the Americanas Tech repository. Reviewer IDs and demographic fields are omitted from the included derivative. The current VADER model is not validated for Portuguese. The related **RePro** dataset adds 10,003 released, human-annotated records from the B2W corpus; 7,985 single-polarity rows form a three-class evaluation subset, while 2,018 mixed reviews are preserved separately. Since RePro overlaps B2W, do not count it as additional independent review volume. See [`B2WReviews01/README.md`](B2WReviews01/README.md) for citation, preparation, benchmark loading, and licensing details.

## Additional human-labeled review benchmarks

Two separately licensed datasets have been added as source spreadsheets with reproducible CSV derivatives:

- **Virtual Assistant Devices:** 2,370 labeled reviews from Amazon, Best Buy, eBay, Target, and Walmart; ten smart-device models, with five represented on at least two platforms. The Mendeley record lists CC BY 4.0. The downloaded file's negative/neutral counts differ from the paper and dataset description, so do not use it as gold evaluation data until clarified. Details: [`VirtualAssistantDevices/README.md`](VirtualAssistantDevices/README.md).
- **BanglaEcomReviewCorpus:** 8,685 labeled Bangla reviews with English translations, collected across several Bangladesh commerce sites. The Mendeley record lists CC BY 4.0. The released rows omit platform and product identifiers, so this is an external multilingual sentiment benchmark, not a platform-comparison corpus. Details: [`BanglaEcomReviewCorpus/README.md`](BanglaEcomReviewCorpus/README.md).

Regenerate both normalized CSV files and their SHA-256 summary from the checked-in spreadsheets with:

```powershell
python research/prepare_external_benchmarks.py
```

Keep these corpora distinct by dataset in analysis; they have different languages, sampling processes, platform metadata, and label provenance.

The Virtual Assistant Devices reviews are loaded into the local searchable database, where the application's VADER model generates its analysis labels. The source human labels remain in the separate CSV and are not used as model predictions. The Bangla corpus remains a separate benchmark because its source file has no row-level retailer/product identity and the application's current sentiment model is English-oriented.
