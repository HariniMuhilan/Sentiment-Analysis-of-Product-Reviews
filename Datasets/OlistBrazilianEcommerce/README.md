# Olist Brazilian E-Commerce Public Dataset

## Source and license

The primary dataset is published by Olist and collaborators on [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). The Kaggle record identifies the license as **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**. The dataset is separate from this repository's MIT-licensed code: the noncommercial and share-alike conditions apply to these data files and derivatives. Cite Olist and link to the dataset and license when using them.

The four included source files are the review table, order-item table, product table, and product-category translation table. They were obtained from a public mirror at <https://github.com/ductransponster/olist-brazilian-ecommerce> which identifies the Olist Kaggle dataset as its source. The Kaggle record remains the primary citation; the mirror is recorded here for retrieval provenance.

## Contents and preparation

The full Olist source reports 99,224 order-level reviews from Brazilian e-commerce activity during 2016–2018. Reviews link to an order rather than directly to a product. Product mapping is ambiguous for orders containing multiple distinct products, so the included preparation script keeps only orders with one distinct product ID and a non-empty review title or body. It generated **40,317** eligible review-text records from this snapshot. It excludes 3,997 rows with missing or multi-product links and 54,910 rows without written review text.

From the repository root, run:

```powershell
python research/prepare_olist_reviews.py
```

The script writes `processed/olist_single_product_reviews.csv` and `processed/preparation_summary.json` under this folder. Generated files are ignored by Git; the source CSVs and reproducible preparation script are tracked.

## Research limits

- This is Olist Brazil data, distinct from Amazon, but it cannot support same-model cross-retailer comparisons. Product IDs are internal identifiers and the source has no human-readable product titles or global product identifiers.
- Olist records an order-level review. Restricting analysis to single-product orders reduces misattribution but introduces selection bias; report this rule and excluded counts.
- Review text is primarily Portuguese. The application's current VADER lexicon is English-oriented; do not use its scores on this corpus as valid Portuguese sentiment. Use a Portuguese-capable multilingual model and report it separately.
- The 1–5 values are observed order ratings, not human-annotated text sentiment labels. Rating-derived classes must be labeled as weak satisfaction proxies.
- This historical dataset has no live inventory or current-price information.

## Attribution

“Brazilian E-Commerce Public Dataset by Olist,” Olist and collaborators, Kaggle, <https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>, CC BY-NC-SA 4.0, <https://creativecommons.org/licenses/by-nc-sa/4.0/>. Retrieved copy: <https://github.com/ductransponster/olist-brazilian-ecommerce>.

SHA-256 hashes for each included source file are recorded in `research/data_manifest.json`.
