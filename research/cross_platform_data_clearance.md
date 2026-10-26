# Cross-Platform Product Review Data Clearance Audit

**Reviewed:** 2026-10-26  
**Purpose:** Identify publicly downloadable product-review data that could extend the current Amazon-only corpus without treating public access as proof of reuse rights.

## Decision

No additional raw review text was imported during this audit. Several datasets are publicly downloadable and carry a dataset-level license, but the available records do not establish that the dataset publishers had rights to sublicense the underlying marketplace user reviews. This matters especially where the marketplace terms prohibit automated collection or data mining. Keep these sources out of the empirical database until the rights position is documented or the relevant marketplace grants permission.

The currently imported Amazon Reviews 2023 corpus remains the only active source. Its curators say they cannot assign a license and provide it primarily for research, so the existing local-only handling and restrictions remain in place.

## Candidate sources

| Source | Public availability and reported size | Research fit | Clearance outcome |
|---|---|---|---|
| UCI Turkish User Reviews | Official UCI download, 37,056 reported instances, CC BY 4.0; Turkish text organized by eight product categories. | Real product-review language for a multilingual robustness/external-domain analysis. It has no named marketplace, product IDs, ratings, or dates. | **Included as an auxiliary dataset.** Its explicit CC BY 4.0 license permits redistribution with attribution. Do not count it as a cross-platform marketplace or merge it into product-level comparisons. Archive and hash recorded in `research/data_manifest.json`. |
| Pandey et al., Amazon + Flipkart + Myntra | The paper reports 23,664 collected reviews (15,432 after deduplication) from four categories; data is available on request, not as a direct public download. | Best match to the intended India-focused marketplace comparison. Product-level matching coverage still needs to be verified. | **Request access and written reuse terms.** Authors report following platform terms, but the dataset and reuse license are not publicly available. Do not imply permission has been granted. |
| Rashid et al., Daraz + Pickaboo | Public Mendeley Data record, CC BY 4.0; paper reports 78,130 samples across 152 product categories and manually annotated sentiment/emotion. | Actual product-review text from two platforms; Bengali and English. Potential external-market validation, but platform, country, and language differ from the current Amazon corpus. | **Hold pending rights clarification.** Mendeley’s license notice says additional permission may be needed for third-party content. Daraz terms prohibit data-mining/robots and downloading or copying site content. |
| EComReviews-BD, Daraz | Public Mendeley Data record, CC BY 4.0; 20,685 reviews across 19 categories and 483 products, manually labeled for overall and aspect sentiment. | Strong annotated benchmark, but only one platform. Could validate multilingual/aspect models if rights are cleared. | **Hold pending rights clarification.** Same third-party-content caveat and Daraz terms issue. Review overlap with other Daraz corpora is unknown. |
| BanglishRev, Daraz | Public Hugging Face release; reports 1.74 million written reviews and 128,000 products; CC BY-NC-SA 4.0. | Large Bangla/English/code-mixed, single-platform corpus. Useful only for a separately scoped multilingual external validation study. | **Hold pending rights clarification.** The paper describes automated collection from Daraz; public download and a dataset-level license do not resolve the platform/content-rights question. |
| Flipkart Kaggle review corpora | Public Kaggle records report 205,053 or 363,260 rows; descriptions say data was scraped from Flipkart. | Product text and ratings are potentially useful for India-focused analysis; one dataset's sentiment labels are partly rating/VADER-derived and are not independent gold labels. | **Exclude without written permission.** Flipkart terms prohibit automated page scraping and restrict copying/reuse of site content without express written consent. A Kaggle listing does not prove that consent. |
| Flipkart Zenodo record | Public 194,276-row archive; no named creator and no license shown in the record. | Product text and ratings are claimed. | **Exclude.** Provenance, creator, and reuse rights are unverified. |
| Myntra product catalog datasets | Public files include product metadata/catalog fields, but no customer review text in the examined 15,000-row release. | Could support catalog matching only; cannot contribute sentiment observations. | **Not a review corpus.** Do not count catalog rows or aggregate rating fields as review text. |
| Meesho datasets found in search | One prominently indexed GitHub release explicitly says it is generated sample data because live review access is blocked. Other surfaced sources were app reviews or commercial extraction services. | The generated file is not real customer review evidence; app reviews measure application experience rather than product experience. | **Exclude from product-review analysis.** Do not include generated or app-store text as marketplace product reviews. |
| ShoppingAppReviews | Public Mendeley Data release, CC BY-NC 4.0, 751,500 reviews across 12 shopping apps, including Amazon, Flipkart, Meesho, and Myntra. | App-store reviews concern app usability/service, not the products sold. | **Out of scope.** Do not mix app-experience reviews with product reviews. |

## Research design consequences

1. Public download availability, a repository license, and a platform's authorization are separate facts. Record each separately for every source.
2. Do not combine separate corpora as if they were a balanced sample. Preserve source, marketplace, country, language, collection period, and annotation method on every row.
3. Product comparisons require defensible cross-platform product matching (prefer model numbers/GTINs). Similar titles alone are not enough. Report match confidence and the unmatched share.
4. Manually annotated labels can support validation only after reviewing the annotation protocol, class definitions, annotator agreement, and provenance. Ratings or automatic labels are not human ground truth.
5. The current Amazon dataset plus any Bangladesh corpora would introduce marketplace, country, language, and category differences. Analyze these as stratified/external validation data unless matched products and comparable sampling are established.
6. Do not put raw review text or populated databases in Git. Retain citations, licenses, source hashes, import logs, aggregate counts, and reproducible download instructions where permitted.

## Sources checked

- Amazon Reviews 2023 curator license statement: <https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/discussions/1>
- Three-marketplace study and data-on-request statement: <https://www.sciencedirect.com/org/science/article/pii/S106273752500109X>
- Daraz + Pickaboo dataset (Mendeley, CC BY 4.0): <https://data.mendeley.com/datasets/rzjfg7t9kf/1>
- Daraz + Pickaboo dataset article: <https://pmc.ncbi.nlm.nih.gov/articles/PMC11888917/>
- EComReviews-BD dataset (Mendeley, CC BY 4.0): <https://data.mendeley.com/datasets/77dpfy4h9p/1>
- BanglishRev dataset (CC BY-NC-SA 4.0): <https://huggingface.co/datasets/BanglishRev/bangla-english-and-code-mixed-ecommerce-review-dataset>
- Flipkart terms: <https://stories.flipkart.com/terms-of-use>
- Daraz terms: <https://www.daraz.com.bd/terms-conditions/>
- Myntra catalog example (metadata, not reviews): <https://huggingface.co/datasets/Gssmc/myntra_dataset>
- Meesho generated sample-data note: <https://github.com/Neelx/meesho_dataset/blob/main/DATASET_SUMMARY.md>
- ShoppingAppReviews (app reviews, CC BY-NC 4.0): <https://data.mendeley.com/datasets/chr5b94c6y/2>

## Next clearance step

Request written confirmation from the academic dataset authors for the Amazon/Flipkart/Myntra corpus and for the Daraz/Pickaboo releases. Ask whether the underlying review text may be processed for this student research project, what may be reported in a paper, and whether platform/third-party authorization is in place. Integrate only after the rights terms are documented. A future paper should disclose any source that remains unavailable and avoid cross-platform claims unsupported by the cleared data.

## Added dataset

- UCI Machine Learning Repository, **Turkish User Reviews**, DOI [10.24432/C5HK72](https://doi.org/10.24432/C5HK72), CC BY 4.0. Downloaded from the official UCI archive on 2026-10-26 and stored at `Datasets/TurkishUserReviews/turkish_user_review_dataset.zip`. SHA-256: `34edb4e14ae2fbea0ecce0c31d9830d2361bb4adc5db25258be6a20ff6242142`. UCI reports 37,056 instances. Because the plain-text file is grouped by category and does not identify a marketplace or product, it is an auxiliary linguistic corpus only; no cross-platform or product-level conclusions can be drawn from it.
