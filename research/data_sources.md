# Research Data Source Register & Legal Rights Analysis

This document provides a transparent, authoritative accounting of all data sources considered or processed within this project, in accordance with scientific ethics and platform terms of service.

---

## 1. Candidate Dataset Ledger

| Source Identifier | Primary Provider & Source URL | License & Terms | Verification Status | Allowed Usages | Collection Limitations |
|---|---|---|---|---|---|
| **AMAZON-UCSD-SNAP** | Prof. Julian McAuley (UC San Diego) & Stanford SNAP. [UCSD Amazon Data](https://cseweb.ucsd.edu/~jmcauley/datasets.html#amazon_reviews) | Academic & Non-commercial Research Use. | **Verified Authorized** | Local academic evaluation, model benchmarking. No public re-hosting of raw dumps. | Historical data (1995–2014 / 2018). Star ratings (1-5) and text present. |
| **AMAZON-AWS-PDS** | Amazon Web Services Customer Reviews Public Dataset. [AWS Registry](https://registry.opendata.aws/amazon-reviews/) | AWS Customer Reviews Public Dataset Terms. Academic non-commercial exploration. | **Verified Authorized** | Local academic evaluation. Access via AWS S3 requester-pays or direct mirror. | English US marketplace reviews. High volume (>130M reviews). |
| **AMAZON-MARC** | Amazon Science (Keung et al., 2020). [HuggingFace MARC](https://huggingface.co/datasets/amazon_reviews_multi) | Creative Commons Attribution 4.0 International (**CC-BY-4.0**). | **Verified Open Access** | Full research use, reproducible benchmarking, public derivative release with attribution. | Balanced 5-star ratings; translated / multilingual subsets. |
| **FLIPKART-KAGGLE-COMM** | Community upload on Kaggle (`Dataset-SA.csv`). | Marked CC0 / DbCL by uploader, but **lacks authorization** from Flipkart Internet Pvt. Ltd. | ⚠️ **Unverified / Blocked** | **Blocked from public redistribution**. Flipkart Terms of Use explicitly prohibit automated scraping. | Scraped corpus of uncertain provenance, unverified dates, potential duplicate leakage. |
| **MYNTRA-KAGGLE-COMM** | Community scraping upload on Kaggle. | Uploader license claims unverified. Lacks authorization from Myntra Designs Pvt. Ltd. | ⚠️ **Unverified / Blocked** | **Blocked from public redistribution**. Myntra Terms of Service prohibit site crawling. | Highly skewed towards specific fashion brands; lack verified timestamp coverage. |
| **MEESHO-KAGGLE-COMM** | Community web scrape on Kaggle. | Lacks authorization from Fashnear Technologies Pvt. Ltd. | ⚠️ **Unverified / Blocked** | **Blocked from public redistribution**. | Small scraped sample; potential fake review spam in raw records. |
| **DEMO-FIXTURE-43** | `Datasets/sample_authorized_reviews.csv` | Synthetic test fixture created for system testing. Dedicated to Public Domain (**CC0**). | **Verified Demo Data** | Functional testing, software CI, UI demonstration. | **Zero empirical value**. Synthetic text; cannot be cited as real-world evidence. |

---

## 2. Platform Legal & Terms Analysis

### Flipkart Terms of Service (Section 10: Use of the Website)
> *"You shall not use any 'deep-link', 'page-scrape', 'robot', 'spider' or other automatic device, program, algorithm or methodology ... to access, acquire, copy or monitor any portion of the Website or any Content..."*

**Scientific Conclusion**: Web-scraped Flipkart datasets from Kaggle cannot be certified as legally authorized for redistribution. To maintain academic and legal integrity, this research project:
1. Does **not** include or scrape proprietary Flipkart records.
2. Formulates its ingestion pipeline as a generic interface: if an operator holds a direct research agreement with Flipkart or an authorized institutional data sharing license, the pipeline can process it locally.
3. Does **not** claim empirical conclusions regarding Flipkart customer sentiment without verified data authorization.

### Myntra & Meesho Terms of Service
Similar anti-scraping and data extraction clauses govern `myntra.com` and `meesho.com`. Public Kaggle dumps derived from unauthorized scraping cannot serve as the empirical foundation for peer-reviewed claims without explicit permissions.

---

## 3. Study Data Strategy & Operator Prerequisites

To execute the research protocol with full legal and scientific validity:

1. **Phase 1 (Current State - Methods & System Protocol)**:
   - The repository implements the complete research pipeline, ingestion parsers, baseline models, annotation protocol, and statistical testing framework.
   - Evaluated on verified open academic data (MARC / UCSD Amazon samples) and demo fixtures for test verification.
2. **Phase 2 (Operator Prerequisites for Cross-Platform Empirical Run)**:
   - The project owner must secure written research authorization or an institutional API license from Indian e-commerce marketplaces (Flipkart, Myntra, Meesho) before publishing comparative empirical findings.
   - Alternatively, the study must scope its empirical evaluation to verified open e-commerce corpora (e.g., MARC multilingual Amazon reviews across countries) where licenses permit reproducible analysis.
