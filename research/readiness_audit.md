# Research Readiness Audit Report

**Date**: 2026-10-26  
**Auditor**: Project Research & Methods Audit Team  
**Subject**: Sentiment Analysis of Product Reviews Codebase & Artifacts  

---

## 1. Executive Summary

This audit assesses the scientific readiness, empirical validity, and legal soundness of the repository before conducting a formal research study. 

The previous implementation successfully established a working full-stack web application (FastAPI backend + React 19 dashboard). However, from a scientific research standpoint, the codebase contains several methodological, statistical, and empirical issues that must be addressed:
1. **Ad-hoc Sample Data Treated as Empirical Ground Truth**: A 43-row sample dataset (`sample_authorized_reviews.csv`) and 21 hard-coded test strings (`BENCHMARK_FIXTURES`) were exposed in endpoints as if they represented empirical multi-platform evaluations.
2. **Mathematically Invalid Significance Testing**: Marginal Wilson score confidence intervals were compared to claim $p < 0.05$ leader status without conducting two-sample hypothesis testing or controlling for product/category confounding.
3. **Uncalibrated Confidence Scores**: An ad-hoc linear transformation of VADER compound scores was labeled as "calibrated confidence," despite lacking probabilistic calibration (e.g., Platt scaling, isotonic regression, Expected Calibration Error).
4. **Silent Missing-Value Imputation**: Ingestion parsers defaulted missing review ratings to `3.0`, introducing artificial neutral bias into statistical summaries.
5. **Unverified Data Licensing Claims**: Documentation asserted that Flipkart, Myntra, and Meesho datasets were verified and authorized under platform terms, when in fact publicly floating CSVs on Kaggle lack verified platform re-use permissions.

---

## 2. Detailed Findings & Corrective Action Plan

### Finding 1: Demo Fixtures vs. Empirical Validation
- **Current State**: `backend/app/api/evaluation.py` hard-codes 21 synthetic review examples and returns an accuracy and macro-F1 score as the "model evaluation report."
- **Scientific Impact**: Presenting unit-test fixtures as empirical model performance is scientifically deceptive and produces ungrounded accuracy claims.
- **Corrective Action**:
  - Reclassify the 21 hard-coded examples strictly as internal unit-test fixtures (`TEST_FIXTURES`).
  - Update `/api/evaluation` to clearly state whether an empirical annotated validation set has been loaded or if evaluation is in "Test Fixture / Demo" mode.
  - Build a rigorous human annotation protocol for genuine ground-truth benchmarking.

### Finding 2: Statistical "Winner" Claims & Hypothesis Testing
- **Current State**: In `backend/app/crud.py`, if the lower bound of Platform A's Wilson confidence interval exceeds Platform B's upper bound, the code asserted: *"Statistically significant lead in positive sentiment ... at 95% confidence (p < 0.05)."*
- **Scientific Impact**:
  - Comparing non-overlapping marginal intervals is NOT a valid hypothesis test; it is an informal heuristic that fails to account for covariance, sample size disparities, or the actual two-sample test statistic.
  - Reporting an uncomputed $p$-value ($p < 0.05$) without calculating a test statistic (e.g., Pearson's $\chi^2$, Fisher's exact test, or two-proportion $z$-test) is mathematically invalid.
  - Attributing cross-platform sentiment differences solely to the platform ignores catalog mismatch (e.g., different product categories, price points, and review length distributions across platforms).
- **Corrective Action**:
  - Replace the ad-hoc comparison with valid statistical tests (Two-sample proportion test, Pearson's $\chi^2$ test of independence, and contingency tables with Holm-Bonferroni correction).
  - Explicitly report test statistics ($z$, $\chi^2$, degrees of freedom, and calculated $p$-values) and effect sizes (Cohen's $h$ or Cramér's $V$).
  - Never declare a platform "winner" unless a controlled experiment with matched products and confounder controls supports that conclusion.

### Finding 3: Uncalibrated Confidence Metric
- **Current State**: `calculate_confidence` in `backend/app/nlp/sentiment.py` uses the formula $0.50 + (|C| \times 0.50)$, where $C$ is the VADER compound score.
- **Scientific Impact**: This is an ad-hoc heuristic that maps intensity to $[0.5, 1.0]$. It does not represent the posterior probability $P(\hat{y} = y \mid x)$ or calibrated uncertainty.
- **Corrective Action**:
  - Rename the metric to `compound_intensity` or `heuristic_confidence` in documentation and code.
  - Document that true probabilistic calibration requires a labeled validation dataset with calibration curves (reliability diagrams) and Expected Calibration Error (ECE) metrics.

### Finding 4: Ingestion Normalization & Missing Values
- **Current State**: `parse_amazon_record`, `parse_flipkart_record`, etc. in `backend/app/ingestion/parsers.py` contained `if rating is None: rating = 3.0`.
- **Scientific Impact**: Silently converting missing ratings into neutral ratings distorts rating distributions and creates artificial correlations between unrated reviews and neutral sentiment.
- **Corrective Action**:
  - Preserve `rating = None` when missing.
  - Update database models, schemas, and SQL aggregations to handle null ratings without imputation.
  - Log rejected or malformed rows without leaking sensitive review text.

### Finding 5: Data Provenance & Legal Rights
- **Current State**: Documentation claimed coverage of Amazon, Flipkart, Myntra, and Meesho reviews based on Kaggle datasets.
- **Scientific Impact**:
  - Amazon reviews have authorized academic releases (e.g., Stanford SNAP / McAuley et al., AWS Open Data Amazon Customer Reviews).
  - Flipkart, Myntra, and Meesho datasets hosted on Kaggle are community-uploaded web scrapes. Neither Kaggle nor the uploaders possess authorization from Flipkart Internet Pvt. Ltd., Myntra Designs Pvt. Ltd., or Fashnear Technologies (Meesho) to grant re-distribution rights.
  - Claiming that these datasets are "authorized under platform terms" is legally inaccurate.
- **Corrective Action**:
  - Categorize data sources into **Verified Research Datasets** (permissibly licensed academic corpora) vs. **Unverified / Blocked Sources** (third-party platform scrapes lacking redistribution rights).
  - Provide a transparent Data Manifest (`research/data_manifest.json`) and clear legal disclaimers.
  - The study must frame cross-platform comparisons on data where permission is verifiable, or document data access as an explicit study blocker.

---

## 3. Audit Conclusion

The application infrastructure is well-engineered and operational. However, the scientific and empirical claims must be downgraded to reflect actual evidence. 

By implementing the corrective actions above, the repository will transition from an application claiming unverified findings into a credible research framework with reproducible methods, valid statistical tests, and transparent data governance.

## 4. Status After the Local Research Corpus Was Added (2026-10-26)

The project now has a local import path for the All Beauty and Appliances subsets of the Amazon Reviews 2023 corpus. This improves the empirical data volume, but does not resolve the following research requirements:

- The corpus curators state that no license is assigned and that the files are provided primarily for research. Treat it as a local research copy; do not redistribute source review text or the populated database without separate permission.
- The corpus covers Amazon only and historical records through September 2023. Cross-marketplace analysis, current price tracking, and live inventory are outside the supported evidence.
- Star ratings are not human-annotated sentiment labels. VADER agreement with ratings is descriptive agreement, not classifier accuracy.
- The protocol and manuscript have been re-scoped to these two domains and remain drafts. They are not formally pre-registered and contain no completed human annotation study.
- Before paper submission, report exact imported counts and hashes from `research/data_manifest.json`, inspect duplicates/missing metadata, predefine sampling, annotate a blinded sample with at least two people, report inter-annotator agreement, and validate sentiment models against adjudicated labels.
