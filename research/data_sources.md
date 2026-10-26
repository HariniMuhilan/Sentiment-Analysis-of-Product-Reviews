# Research Data Sources and Usage Boundaries

## Active corpus

The local research database uses two category subsets from the Amazon Reviews 2023 corpus curated by the McAuley Lab at UC San Diego:

| Corpus subset | Source page | Source rows | Imported unique reviews | Domain |
|---|---|---:|---:|---|
| All_Beauty | [Dataset files](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) | 701,528 | 693,547 | Beauty and personal care |
| Appliances | [Dataset files](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) | 2,128,605 | 2,103,926 | Household appliances |

The importer skipped 33,660 repeated rows, for 2,797,473 unique reviews total. Exact source-file hashes are in `research/data_manifest.json`.

The dataset spans May 1996 to September 2023. It contains Amazon review text, ratings, product identifiers, timestamps, and separate item metadata. It is historical research data, not a live product catalog or price feed.

### Rights and distribution

The dataset curators state that they are not in a position to assign a license and that the files are made available primarily for research. This project therefore treats the corpus as a local research copy only. The raw source files and derived database containing review text must not be committed, pushed, or redistributed without permission and a separate rights review. A paper should cite the dataset paper and source, report access date and subset, and follow the source terms and institutional guidance.

The repository's `.gitignore` excludes downloaded JSONL files and SQLite databases. The data manifest records the local import counts and file hashes, but does not include review text.

## Excluded datasets

- `Datasets/sample_authorized_reviews.csv` is a 43-row synthetic fixture for software tests and UI demonstration. It is excluded from the empirical research database.
- Community datasets claiming Flipkart, Myntra, or Meesho reviews are excluded unless provenance, authorization, and redistribution/use rights are independently verified. The project currently makes no empirical claims about those platforms.
- The Amazon Reviews Multi/MARC corpus is not included in the current database. Dataset mirrors carry inconsistent license metadata; do not describe it as CC-BY-4.0 without authoritative confirmation.

## Research limitations

- The active data is from one marketplace, so it cannot support cross-platform comparisons.
- Category subsets are not representative probability samples of all customers or products. They inherit the original collection and curation biases.
- Source ratings are observed labels, not human-annotated sentiment ground truth. Analyses of VADER agreement with ratings must be described as rating-text agreement, not validated sentiment accuracy.
- Products are matched to source metadata by parent ASIN. Missing metadata is retained as an explicit fallback product name and should be counted in quality checks.
- Prices in source metadata are missing for many products and may be historical. The app must not treat them as current offers.
- The source dataset ends in September 2023. Do not call the imported reviews live or continuously updated.

## Citation

Hou, Y., Li, J., He, Z., Yan, A., Chen, X., and McAuley, J. (2024). *Bridging Language and Items for Retrieval and Recommendation*. arXiv:2403.03952. Dataset: [Amazon Reviews 2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023).
