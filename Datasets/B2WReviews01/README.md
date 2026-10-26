# B2W-Reviews01 (Americanas.com, Brazil)

## Source and license

This is an open corpus of more than 130,000 product reviews collected from Americanas.com between January and May 2018. The [Americanas Tech source repository](https://github.com/americanas-tech/b2w-reviews01) identifies B2W Digital as the dataset rights holder and licenses B2W-Reviews01 under **CC BY-NC-SA 4.0**. The data is separate from this repository's MIT-licensed code; the noncommercial and share-alike conditions apply to the corpus and its derivatives.

The source also includes reviewer ID and demographic fields. The tracked derivative, [`processed/B2W-Reviews01-clean.csv.gz`](processed/B2W-Reviews01-clean.csv.gz), removes reviewer ID, birth year, gender, and state. It retains product IDs/names, product category, review title/text, rating, recommendation response, review date, and a non-reversible deterministic row key. The full source CSV is not tracked; download it from the official repository and regenerate the derivative as described below.

## Prepare the derivative again

From the repository root in PowerShell:

```powershell
New-Item -ItemType Directory -Force Datasets/B2WReviews01/raw | Out-Null
curl.exe -L --fail --retry 3 -o Datasets/B2WReviews01/raw/B2W-Reviews01.csv `
  "https://raw.githubusercontent.com/americanas-tech/b2w-reviews01/main/B2W-Reviews01.csv"
python research/prepare_b2w_reviews.py
```

The current source snapshot contains 132,373 rows; the derivative keeps 132,301 rows with review text and valid 1–5 ratings. It excludes 72 rows without written text. The derivative's SHA-256 is in `research/data_manifest.json`.

## Research limits

- This is a named second e-commerce source alongside Amazon. Its product names and categories can support category-level analysis and conservative candidate matching, but it has no shared global product identifier with Amazon; do not claim same-model matches without a separately documented match protocol.
- Reviews are Brazilian Portuguese. The application's current VADER lexicon is English-oriented and has not been validated for Portuguese. Do not interpret its VADER outputs as valid sentiment for this corpus; use a Portuguese-capable model and report results separately.
- The 1–5 rating and recommendation response are observed customer signals, not human-annotated text sentiment ground truth.
- The source authors warn that product reviews can also discuss purchase, payment, and delivery experiences.
- The collection is historical (2018), not a live review or price feed.

## Attribution

B2W Digital. *B2W-Reviews01*. Americanas Tech GitHub repository, <https://github.com/americanas-tech/b2w-reviews01>, CC BY-NC-SA 4.0, <https://creativecommons.org/licenses/by-nc-sa/4.0/>. See the source repository and its associated paper for the complete citation and methodology.

## RePro human-annotation benchmark

The repository also includes a privacy-minimized copy of **RePro**, a human-annotated sample drawn from B2W-Reviews01. The paper describes 10,000 Brazilian Portuguese reviews, selected stratified by star rating. The public CSV currently contains **10,003 rows**; that release-versus-paper count difference is recorded rather than silently corrected. The labels cover positive, negative, neutral, and mixed positive/negative sentiment, plus review topics. The paper reports at least two annotators per sample, expert adjudication, and mean sentiment Cohen's kappa of 0.71.

`processed/RePro-clean.csv` retains the complete release and removes reviewer IDs and demographic fields. `processed/RePro-3class-evaluation.csv` contains **7,985 single-polarity examples** for the app's existing three-class benchmark; it excludes 2,018 mixed-polarity records rather than forcing them into a single class. Use the full file for work that supports a mixed class. Because RePro is a sample of B2W-Reviews01, do not add its row count to B2W as if these were independent reviews. RePro was stratified by star rating, so its class proportions are not a natural marketplace prevalence estimate.

Prepare the files from the author-hosted release:

```powershell
New-Item -ItemType Directory -Force Datasets/B2WReviews01/raw | Out-Null
curl.exe -L --fail --retry 3 -o Datasets/B2WReviews01/raw/RePro.csv `
  "https://raw.githubusercontent.com/lucasnil/repro/main/RePro.csv"
python research/prepare_repro_benchmark.py
```

Load the single-polarity subset into the API's separate empirical benchmark table (not the searchable product-review table):

```powershell
cd backend
python ingest_repro_benchmark.py
```

Run the reproducible lexical baseline:

```powershell
python research/run_repro_benchmark.py
```

**Language limitation:** the current VADER pipeline is English-oriented and has not been validated for Brazilian Portuguese. RePro results from VADER are a cross-language stress baseline, not Portuguese in-language performance. The source is CC BY-NC-SA 4.0; noncommercial and share-alike conditions apply to this data and derivatives. The project's MIT code license does not replace them.

The RePro author repository and conference paper identify CC BY-NC-SA 4.0. The Hugging Face mirror's license metadata has differed; use the author's repository and paper notice, and retain the more restrictive CC BY-NC-SA terms for this copy.

**Citation:** dos Santos Silva, L. N., Real, L., Zandavalle, A. C., Rodrigues, C. F. G., da Silva Gama, T., Souza, F. G., and Zaidan, P. D. S. (2024). *RePro: a benchmark for Opinion Mining for Brazilian Portuguese*. Proceedings of the 16th International Conference on Computational Processing of Portuguese, 432–440. <https://aclanthology.org/2024.propor-1.44/>.

Credit B2W Digital as required by the RePro repository's license notice: <https://github.com/lucasnil/repro>.
