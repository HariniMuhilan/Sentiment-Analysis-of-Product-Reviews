# Research Data Sources and Usage Boundaries

## Active corpus

The local research database contains two datasets. Its large corpus uses two category subsets from Amazon Reviews 2023, curated by the McAuley Lab at UC San Diego:

| Corpus subset | Source page | Source rows | Imported unique reviews | Domain |
|---|---|---:|---:|---|
| All_Beauty | [Dataset files](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) | 701,528 | 693,547 | Beauty and personal care |
| Appliances | [Dataset files](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) | 2,128,605 | 2,103,926 | Household appliances |

The importer skipped 33,660 repeated rows, for 2,797,473 unique Amazon reviews. The searchable database also contains 2,370 English reviews from the Virtual Assistant Devices cross-retailer benchmark (Amazon, Best Buy, eBay, Target, and Walmart), for a current total of 2,799,843 review records. The dataset's hand labels remain in its separate source/processed files; the application stores only its VADER-generated analysis. Exact source-file hashes and platform counts are in `research/data_manifest.json`.

The dataset spans May 1996 to September 2023. It contains Amazon review text, ratings, product identifiers, timestamps, and separate item metadata. It is historical research data, not a live product catalog or price feed.

### Rights and distribution

The dataset curators state that they are not in a position to assign a license and that the files are made available primarily for research. This project therefore treats the corpus as a local research copy only. The raw source files and derived database containing review text must not be committed, pushed, or redistributed without permission and a separate rights review. A paper should cite the dataset paper and source, report access date and subset, and follow the source terms and institutional guidance.

The repository's `.gitignore` excludes downloaded JSONL files and SQLite databases. The data manifest records the local import counts and file hashes, but does not include review text.

## Excluded datasets

- `Datasets/sample_authorized_reviews.csv` is a 43-row synthetic fixture for software tests and UI demonstration. It is excluded from the empirical research database.
- The cross-platform source search and rights decisions are recorded in [`cross_platform_data_clearance.md`](cross_platform_data_clearance.md). Public downloads from Flipkart, Daraz, Pickaboo, and other marketplaces are not automatically cleared for reuse; the reviewed candidate corpora remain excluded pending documented rights for the underlying review text.
- The project currently makes no empirical claims about Flipkart, Myntra, Meesho, Daraz, or Pickaboo.
- The Amazon Reviews Multi/MARC corpus is not included in the current database. Dataset mirrors carry inconsistent license metadata; do not describe it as CC-BY-4.0 without authoritative confirmation.

## Supplementary dataset included in the repository

The repository now contains a separate Olist Brazil corpus under CC BY-NC-SA 4.0. It is not yet imported into the application's Amazon database. A reproducible preparation script filters to text-bearing reviews from single-distinct-product orders, producing 40,317 records from the 99,224 source order-review rows. Product IDs are internal to Olist and cannot be joined to Amazon product models. Portuguese text must be analyzed with a suitable Portuguese-capable model; the current VADER output is not valid evidence for it. See [`Datasets/OlistBrazilianEcommerce/README.md`](../Datasets/OlistBrazilianEcommerce/README.md) and the manifest for details.

The repository also contains a privacy-minimized derivative of **B2W-Reviews01**, an Americanas.com product-review corpus under CC BY-NC-SA 4.0. It retains 132,301 reviews and their product/category metadata while removing reviewer ID and demographic columns. It is not loaded into the main Amazon database. Portuguese text is outside the validated coverage of the current VADER model, and same-product cross-platform matching is not established. See [`Datasets/B2WReviews01/README.md`](../Datasets/B2WReviews01/README.md).

Two additional Mendeley Data corpora are tracked under the CC BY 4.0 licenses stated on their records. The **Virtual Assistant Devices Dataset** contains 2,370 English smart-device reviews from five named retailers and five device models with more than one retailer source. Its review text is imported into the searchable database and analyzed by VADER. The downloaded source labels are 842 positive, 774 negative, and 754 neutral, conflicting with the paper/record's reported 842/800/728 split; do not treat those labels as gold evaluation data before the authors clarify the difference. The **BanglaEcomReviewCorpus** contains 8,685 Bangla review sentences and English translations with three-class labels. Its row schema has no retailer or product identifier, so it remains a separate multilingual benchmark and cannot support platform-level or matched-product comparisons. See the dataset cards under [`Datasets/VirtualAssistantDevices`](../Datasets/VirtualAssistantDevices/README.md) and [`Datasets/BanglaEcomReviewCorpus`](../Datasets/BanglaEcomReviewCorpus/README.md).

The same directory contains **RePro**, a human-annotated Brazilian Portuguese subset of B2W-Reviews01. The downloaded release has 10,003 rows, although its paper reports 10,000. The full privacy-minimized file retains four sentiment labels, including mixed polarity; the API evaluation subset contains 7,985 single-polarity rows and omits 2,018 mixed rows for three-class scoring. Its source annotation process reports average sentiment Cohen's kappa of 0.71. The `BenchmarkReview` table stores these labels separately from searchable reviews. VADER scores on this Portuguese benchmark are only a cross-language stress baseline, not validated in-language performance. Since RePro is drawn from B2W, the two corpora are overlapping, not independent samples.

The recorded RePro stress run is in [`results/repro_vader_benchmark.json`](../results/repro_vader_benchmark.json) and [`results/tables/repro_vader_benchmark.md`](../results/tables/repro_vader_benchmark.md). It reports VADER accuracy 0.2282 and macro F1 0.2414 on the 7,985 non-mixed examples. These are out-of-language measurements and should be used to motivate a Portuguese-capable model, not as that model's performance estimate.

## Research limitations

- The main searchable product database is Amazon-dominated and includes 2,370 smart-device reviews from five retailers; this small benchmark provides cross-retailer observations for five device names. It has no GTIN or global product IDs, so those groups reflect the dataset's own device-name grouping rather than independently verified entity resolution. BanglaEcom is pooled multi-source data without row-level platform/product IDs. Neither supports a general matched-product marketplace effect across the full searchable corpus. RePro supplies separate human labels for Americanas, but product IDs do not link to Amazon.
- Category subsets are not representative probability samples of all customers or products. They inherit the original collection and curation biases.
- Source ratings are observed labels, not human-annotated sentiment ground truth. Analyses of VADER agreement with ratings must be described as rating-text agreement, not validated sentiment accuracy.
- Products are matched to source metadata by parent ASIN. Missing metadata is retained as an explicit fallback product name and should be counted in quality checks.
- Prices in source metadata are missing for many products and may be historical. The app must not treat them as current offers.
- The source dataset ends in September 2023. Do not call the imported reviews live or continuously updated.

## Citation

Hou, Y., Li, J., He, Z., Yan, A., Chen, X., and McAuley, J. (2024). *Bridging Language and Items for Retrieval and Recommendation*. arXiv:2403.03952. Dataset: [Amazon Reviews 2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023).
