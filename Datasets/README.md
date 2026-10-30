# Research data

## Amazon Reviews 2023 (UCSD McAuley Lab)

The local database contains **2,797,473 unique Amazon Reviews 2023 reviews** from the **All_Beauty** and **Appliances** categories, plus **2,370** smart-device reviews from the cross-retailer Virtual Assistant Devices benchmark. Its current total is 2,799,843 reviews. The Amazon source files contained 2,830,133 rows; deterministic duplicate checks skipped 33,660 repeats. Dataset and database counts and SHA-256 hashes are recorded in `research/data_manifest.json`.

- Dataset page and downloads: <https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023>
- Dataset paper: Hou et al., *Bridging Language and Items for Retrieval and Recommendation* (2024), <https://arxiv.org/abs/2403.03952>
- Source collection period: May 1996 through September 2023; records are historical, not live marketplace data.
- Curator's licensing statement: no license is assigned by the curators; the files are provided primarily for research. Use only for research after reviewing the source terms and applicable law. Do not publish or redistribute the raw corpus or a database containing its review text without permission.
- The Amazon records represent Amazon only. Cross-retailer reviews come from the separate Virtual Assistant Devices dataset documented below. Neither source provides current stock or current prices. Item metadata prices are often missing and are historical; they must not be presented as current prices.

The Amazon review text and item metadata are stored under `Datasets/research/raw/`. `.gitignore` excludes these files and the local SQLite database. Keep the Amazon files and database local; do not commit or push them to GitHub.

## Download the research files

From the repository root in PowerShell:

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
```

## Import into the local application

The project uses `backend/sentiment_research.db` by default. From the repository root:

```powershell
cd backend
..\.venv\Scripts\python.exe ingest_ucsd_amazon_2023.py
```

The importer reads JSONL incrementally, matches reviews to item titles from the metadata, computes the project's documented VADER scores, and commits in batches. It is safe to rerun: deterministic review IDs are used to skip records already imported. For a quick smoke run, use `--max-records 1000`; use `--categories Appliances` or `--categories All_Beauty` to import one domain.

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
