# Cross-Platform Product Review Data Clearance Audit

**Reviewed:** 2026-10-26  
**Purpose:** Identify publicly downloadable product-review data that could extend the current Amazon-only corpus without treating public access as proof of reuse rights.

## Decision

Only sources with a named platform, documented provenance, and a stated corpus license were added as separate supplementary datasets. Public downloads from other sources may carry a dataset-level license without establishing that the publisher had rights to sublicense underlying marketplace reviews. This matters especially where platform terms prohibit automated collection or data mining. Keep those sources out of the empirical database until the rights position is documented or the relevant marketplace grants permission.

Amazon Reviews 2023 and the Virtual Assistant Devices dataset are loaded into the local searchable product-review table. Amazon Reviews 2023 remains a local-only research copy because its curators say they cannot assign a license and provide it primarily for research. The Virtual Assistant source labels remain separate; the app re-analyzes its English review text with VADER. Olist and B2W-Reviews01 are supplementary research files. RePro labels are loaded only into the separate model-evaluation benchmark table; its reviews overlap the B2W source corpus.

Two additional Mendeley datasets are tracked as separate research benchmarks under the CC BY 4.0 licenses stated on their records. They are not loaded into the searchable Amazon database. The smart-device file has a sentiment-count discrepancy versus its article and must not be treated as gold evaluation data until resolved. The Bangla corpus has no per-row platform or product identifiers and is suitable only for separate language/model validation.

## Candidate sources

| Source | Public availability and reported size | Research fit | Clearance outcome |
|---|---|---|---|
| B2W-Reviews01 (Americanas.com) | Official Americanas Tech repository; over 130,000 real product reviews from Jan–May 2018; CC BY-NC-SA 4.0. | Named Brazilian platform, Portuguese review text, product names/IDs, category, dates, ratings, and recommendation label. | **Included as a supplementary corpus.** A derivative retaining 132,301 text-bearing rows and dropping reviewer ID/demographics is tracked. Use a Portuguese-capable model; treat cross-site product matching as unverified absent a documented match protocol. |
| RePro (Americanas.com / B2W subset) | Author repository and PROPOR 2024 paper; paper reports 10,000 manually annotated examples; released CSV contains 10,003; CC BY-NC-SA 4.0. | Human sentiment and topic annotations for Brazilian Portuguese product reviews; mean sentiment Cohen's kappa reported as 0.71. | **Included as an evaluation benchmark.** Full 4-label corpus is retained; 7,985 single-polarity rows are imported into the separate 3-class benchmark table; 2,018 mixed rows are excluded from 3-class scoring. RePro overlaps B2W and is not extra independent review volume. VADER results are cross-language stress results only. |
| Olist Brazilian E-Commerce Public Dataset | Olist-published Kaggle dataset, 99,224 order-review rows, 2016–2018; CC BY-NC-SA 4.0. | Named Brazilian e-commerce source with review text, ratings, product IDs, and categories. Product title is absent; reviews attach to orders, not directly to products. | **Included as a supplementary corpus.** The preparation script yields 40,317 written reviews linked to a single distinct product. Keep separate from the main Amazon corpus; Portuguese VADER scores are unsupported and product models cannot be matched across retailers. |
| Virtual Assistant Devices Dataset | Mendeley Data, 2,370 English reviews, 2018–2023; record states CC BY 4.0. The article reports five source sites: Amazon, Target, Walmart, eBay, and Best Buy. | Device, retailer, review text, sentiment, and aspect fields; five of ten device models occur on multiple retailers. | **Included in the repository and local searchable database.** The app re-analyzes review text with VADER; source labels remain separate. Actual file labels are 842/774/754 positive/negative/neutral, versus 842/800/728 in the article/record. Hold gold-label evaluation pending author clarification. The article states platform redistribution policies were followed. |
| BanglaEcomReviewCorpus | Mendeley Data version 2, 8,685 Bengali review sentences; record states CC BY 4.0. The article describes Daraz, Bikroy.com, Pickaboo, Shajgoj, and other sources. | Human-labeled three-class sentiment with English translations; multi-source collection, but no row-level retailer or product ID. | **Included in the repository as a separate multilingual benchmark.** Do not use for platform comparison or matched-product analysis. Use a Bangla-capable model; translation provenance is insufficiently documented for English gold-label evaluation. |
| Pandey et al., Amazon + Flipkart + Myntra | The paper reports 23,664 collected reviews (15,432 after deduplication) from four categories; data is available on request, not as a direct public download. | Best match to the intended India-focused marketplace comparison. Product-level matching coverage still needs to be verified. | **Request access and written reuse terms.** Authors report following platform terms, but the dataset and reuse license are not publicly available. Do not imply permission has been granted. |
| Rashid et al., Daraz + Pickaboo | Public Mendeley Data record, CC BY 4.0; paper reports 78,130 samples across 152 product categories and manually annotated sentiment/emotion. | Actual product-review text from two platforms; Bengali and English. Potential external-market validation, but platform, country, and language differ from the current Amazon corpus. | **Hold pending rights clarification.** Mendeley’s license notice says additional permission may be needed for third-party content. Daraz terms prohibit data-mining/robots and downloading or copying site content. |
| EComReviews-BD, Daraz | Public Mendeley Data record, CC BY 4.0; 20,685 reviews across 19 categories and 483 products, manually labeled for overall and aspect sentiment. | Strong annotated benchmark, but only one platform. Could validate multilingual/aspect models if rights are cleared. | **Hold pending rights clarification.** Same third-party-content caveat and Daraz terms issue. Review overlap with other Daraz corpora is unknown. |
| BanglishRev, Daraz | Public Hugging Face release; reports 1.74 million written reviews and 128,000 products; CC BY-NC-SA 4.0. | Large Bangla/English/code-mixed, single-platform corpus. Useful only for a separately scoped multilingual external validation study. | **Hold pending rights clarification.** The paper describes automated collection from Daraz; public download and a dataset-level license do not resolve the platform/content-rights question. |
| Flipkart Kaggle review corpora | Public Kaggle records report 205,053 or 363,260 rows; descriptions say data was scraped from Flipkart. | Product text and ratings are potentially useful for India-focused analysis; one dataset's sentiment labels are partly rating/VADER-derived and are not independent gold labels. | **Exclude without written permission.** Flipkart terms prohibit automated page scraping and restrict copying/reuse of site content without express written consent. A Kaggle listing does not prove that consent. |
| Flipkart Zenodo record | Public 194,276-row archive; no named creator and no license shown in the record. | Product text and ratings are claimed. | **Exclude.** Provenance, creator, and reuse rights are unverified. |
| Myntra product catalog datasets | Public files include product metadata/catalog fields, but no customer review text in the examined 15,000-row release. | Could support catalog matching only; cannot contribute sentiment observations. | **Not a review corpus.** Do not count catalog rows or aggregate rating fields as review text. |
| Meesho datasets found in search | One prominently indexed GitHub release explicitly says it is generated sample data because live review access is blocked. Other surfaced sources were app reviews or commercial extraction services. | The generated file is not real customer review evidence; app reviews measure application experience rather than product experience. | **Exclude from product-review analysis.** Do not include generated or app-store text as marketplace product reviews. |
| ShoppingAppReviews | Public Mendeley Data release, CC BY-NC 4.0, 751,500 reviews across 12 shopping apps, including Amazon, Flipkart, Meesho, and Myntra. | App-store reviews concern app usability/service, not the products sold. | **Out of scope.** Do not mix app-experience reviews with product reviews. |
| UCI Turkish User Reviews | Public UCI release, CC BY 4.0, 37,056 reported Turkish-language instances grouped by product category. | UCI does not identify the marketplace, and the records lack product identifiers and ratings. | **Excluded from this project.** It cannot support the required named-platform or cross-platform product comparison. |
| Customer Sentiment Dataset (Kaggle, Kundan Sagar Bedmutha) | Public Kaggle listing, CC BY 4.0, claims 25,000 rows across Amazon, Flipkart, Meesho, Myntra, and other sources. | The listing says review text was generated to match assigned sentiment and rating. | **Excluded as synthetic.** It is not authentic customer-review evidence. |

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
- Olist Brazilian E-Commerce Public Dataset (Kaggle; CC BY-NC-SA 4.0): <https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>
- Olist retrieval mirror used for the four source tables: <https://github.com/ductransponster/olist-brazilian-ecommerce>
- Synthetic Customer Sentiment Dataset (Kaggle): <https://www.kaggle.com/datasets/kundanbedmutha/customer-sentiment-dataset>
- B2W-Reviews01 official source and license: <https://github.com/americanas-tech/b2w-reviews01>
- B2W-Reviews01 associated paper PDF linked from the official source repository: <https://github.com/americanas-tech/b2w-reviews01/blob/main/b2wreviews01_stil2019.pdf>
- RePro author repository and CC BY-NC-SA terms: <https://github.com/lucasnil/repro>
- RePro annotation paper: <https://aclanthology.org/2024.propor-1.44/>
- Virtual Assistant Devices Mendeley record and CC BY 4.0: <https://data.mendeley.com/datasets/d5vsgcxrk5/1>
- Virtual Assistant Devices dataset paper: <https://doi.org/10.1016/j.dib.2024.110642>
- BanglaEcomReviewCorpus Mendeley record and CC BY 4.0: <https://data.mendeley.com/datasets/kkzfrvhbhp/2>
- BanglaEcomReviewCorpus dataset paper: <https://doi.org/10.1016/j.dib.2026.112663>

## Next clearance step

Request written confirmation from the academic dataset authors for the Amazon/Flipkart/Myntra corpus and for the Daraz/Pickaboo releases. Ask whether the underlying review text may be processed for this student research project, what may be reported in a paper, and whether platform/third-party authorization is in place. Integrate only after the rights terms are documented. A future paper should disclose any source that remains unavailable and avoid cross-platform claims unsupported by the cleared data.
