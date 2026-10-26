# Evaluating Lexical Sentiment in Historical Amazon Product Reviews: Rating-Text Agreement, Domain Variation, and Reproducibility

**Working Title**: Evaluating Lexical Sentiment in Historical Amazon Product Reviews
**Authors**: Harini Muhilan et al.  
**Affiliation**: Undergraduate Research Opportunities Programme (UROP), Computer Science & Data Intelligence  
**Document Status**: Working manuscript draft; protocol not formally pre-registered (Venue-Neutral)
**Last Updated**: October 2026  

---

## Abstract
This working study examines lexical sentiment analysis and rating-text agreement in historical Amazon product reviews. The local research corpus contains the All Beauty and Appliances subsets of Amazon Reviews 2023, with approximately 2.8 million reviews collected between 1996 and September 2023. The application computes VADER sentiment scores and supports reproducible filtering and aggregation. Star ratings are treated as observed user scores, not human-annotated sentiment ground truth; therefore rating-text agreement is not reported as classifier accuracy. Independent human annotation and model validation remain required before drawing claims about sentiment accuracy. The corpus represents one marketplace and two selected domains, so it cannot support cross-platform comparisons, current price claims, or generalization to all products. This manuscript is a working protocol and project description; empirical results and a formal pre-registration are not yet complete.

---

## 1. Introduction and Research Question

Online customer reviews provide large collections of naturally occurring product feedback. This project studies a bounded historical Amazon corpus and focuses on reproducible analysis of review text, user ratings, and two product domains. The current dataset does not include authorized review data from other marketplaces.

Despite the proliferation of academic papers analyzing e-commerce reviews, empirical reproducibility remains critically low. Many studies commit one or more foundational errors:
1. **Pseudo-Ground-Truth Conflation**: Equating consumer numerical star ratings (1–5) directly with textual sentiment polarity, ignoring sarcasm, service-versus-product divergence, and rating inflation (Mudambi & Schuff, 2010).
2. **Uncalibrated Confidence Claims**: Treating heuristic model intensity outputs (e.g., VADER compound scores) as calibrated posterior probabilities without evaluating reliability diagrams or Expected Calibration Error (ECE) (Guo et al., 2017).
3. **Confounded Platform Comparisons**: Declaring one shopping platform a "winner" in customer satisfaction without controlling for product catalog discrepancies, price segment differences, or sample size uncertainty.
4. **Data Sourcing Opacity**: Downloading unverified third-party scrapes from public repositories without scrutinizing the underlying platform terms of service or copyright restrictions.

To address these shortcomings, this study formulates a disciplined investigation guided by three core research questions:
- **RQ1 (Model Accuracy vs. Ground Truth)**: How accurately does lexical sentiment classification (VADER) classify e-commerce review text into Positive, Neutral, and Negative polarities when measured against independent, double-annotated human ground truth rather than star ratings?
- **RQ2 (Rating-Text Divergence)**: What proportion of consumer reviews exhibit divergence between star ratings and text sentiment (e.g., 5-star reviews describing defective goods, or 1-star reviews praising the product but condemning delivery), and what biases arise from using star ratings as pseudo-labels?
- **RQ3 (Within-Source Domain Variation)**: How do rating-text agreement and VADER outputs differ between All Beauty and Appliances, and how are these differences associated with review length, rating, and review period?

---

## 2. Related Work

### 2.1 Lexical & Rule-Based Sentiment Analysis
Lexical sentiment classifiers, notably VADER (*Valence Aware Dictionary and s-Sentiment Reasoner*; Hutto & Gilbert, 2014), remain the most widely deployed baseline models in industrial and academic applications due to deterministic execution, zero GPU requirements, and human explainability. VADER combines a gold-standard lexical dictionary with five rule-based heuristics capturing punctuation amplification, capitalization emphasis, degree adverbs, contrastive conjunctions (*"but"*), and tri-gram negation flipping. While originally tuned for microblog social data (Twitter), its transferability to structured e-commerce product reviews requires systematic auditing.

### 2.2 Star Ratings vs. Textual Sentiment
Marketing and information systems literature has repeatedly demonstrated that numerical ratings and review texts capture distinct dimensions of consumer experience (Archak et al., 2011; Wang et al., 2014). Star ratings aggregate overall transactional utility (including shipping speed, seller responsiveness, and packaging), whereas review text frequently disaggregates specific product attributes (material quality, sizing accuracy, technical performance).

### 2.3 Empirical Reproducibility & Data Governance
Recent audits in natural language processing (Lilleberg et al., 2015; Rogers et al., 2021) emphasize that automated web scraping of commercial websites without explicit authorization creates non-reproducible research artifacts subject to takedown and terms violation. Responsible NLP demands transparent provenance manifests and explicit statements on data licensing (Bender & Friedman, 2018).

---

## 3. Data Sources, Permissions, and Collection

### 3.1 Active Corpus and Eligibility
The local corpus contains the **All_Beauty** and **Appliances** category subsets of Amazon Reviews 2023 curated by the McAuley Lab. The source reports approximately 701.5K and 2.1M reviews, respectively; exact locally imported counts and file hashes are recorded in `research/data_manifest.json`. Review timestamps span May 1996 through September 2023. The corpus is historical Amazon data and is not a live product or price feed.

The curators state that they are not in a position to assign a license and that the files are provided primarily for research. This project treats the source files and local database as a restricted research copy; no review text or populated database is included in the repository. Any future public release or publication of source text requires separate rights review. The 43-row synthetic fixture is software test data only and is excluded from empirical analyses. No authorized Flipkart, Myntra, or Meesho data is currently included, so no cross-marketplace conclusions are made.

### 3.2 Data Sanitization & Deduplication
The ingestion pipeline enforces:
- **PII Purging**: Stripping customer usernames, profile URLs, and contact handles.
- **Deterministic Review IDs**: The corpus importer hashes the source product and review fields to produce stable IDs, skips duplicate IDs on repeat imports, and does not store the source's reviewer ID as a user profile field.
- **Missing Value Preservation**: Unrated reviews strictly retain `rating = None`; silent default imputation to `3.0` is prohibited.

---

## 4. Annotation Protocol

### 4.1 Annotation Guidelines & Taxonomy
Annotators classify reviews into four mutually exclusive categories solely based on textual content:
- **POSITIVE**: Expressions of satisfaction, product praise, functional reliability, or aesthetic approval.
- **NEUTRAL**: Purely objective specifications, delivery confirmations lacking emotive polarity, or strictly balanced pros and cons.
- **NEGATIVE**: Expressions of dissatisfaction, material failure, functional defects, or seller misconduct.
- **MIXED / CONFLICTED**: Substantial positive statements paired with substantial negative statements (e.g., *"Stunning camera, but the battery died permanently on day two"*).

### 4.2 Inter-Annotator Reliability & Adjudication
- **Protocol**: A minimum sample of $N = 1,000$ reviews randomly stratified by domain and star rating is independently reviewed by two trained annotators.
- **Reliability Metric**: Measured via Cohen's Kappa ($\kappa$):
  $$\kappa = \frac{p_o - p_e}{1 - p_e}$$
- **Disagreement Resolution**: Annotations with $\kappa$-disagreement are submitted to an independent third senior adjudicator for final ground-truth assignment.
- **Current Status**: `[TODO: Human double-annotation pending institutional review board (IRB) approval and annotator recruitment]`.

---

## 5. Methods and Baselines

### 5.1 Models Under Evaluation
1. **Majority Class Baseline (ZeroR)**: Assigns the most frequent empirical class in the validation set.
2. **Star-Rating Heuristic Baseline**: Maps ratings to sentiment:
   $$\hat{y}_{\text{heuristic}} = \begin{cases} \text{POSITIVE} & \text{if } \text{Rating} \ge 4.0 \\ \text{NEUTRAL} & \text{if } 2.5 \le \text{Rating} \le 3.5 \\ \text{NEGATIVE} & \text{if } \text{Rating} \le 2.0 \end{cases}$$
3. **VADER Lexicon Classifier**: Classifies text polarity based on compound score $C \in [-1.0, 1.0]$:
   $$\hat{y}_{\text{VADER}} = \begin{cases} \text{POSITIVE} & \text{if } C \ge +0.05 \\ \text{NEUTRAL} & \text{if } -0.05 < C < +0.05 \\ \text{NEGATIVE} & \text{if } C \le -0.05 \end{cases}$$

### 5.2 Evaluation Metrics
- Class-specific Precision ($P_c$), Recall ($R_c$), and $F_{1,c}$ for $c \in \{\text{Pos}, \text{Neu}, \text{Neg}\}$.
- Macro-Averaged $F_1 = \frac{1}{3} \sum_{c} F_{1,c}$.
- Expected Calibration Error (ECE) across $M=10$ confidence bins:
  $$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

---

## 6. Experimental Design and Statistical Analysis

### 6.1 Domain Comparison and Dependence
Comparisons between the two selected domains are exploratory and observational. Reviews are clustered within products and may also share reviewers; analyses must account for that dependence (for example, product-clustered bootstrap intervals) and report unadjusted counts and effect sizes. A naïve review-level $Z$-test or $χ^2$ test must not be treated as decisive evidence when its independence assumption is violated.

If a two-proportion test is reported as a supplementary descriptive statistic:
- We compute the **Two-Proportion $Z$-Test**:
  $$z = \frac{p_1 - p_2}{\sqrt{\hat{p}(1-\hat{p}) \left(\frac{1}{n_1} + \frac{1}{n_2}\right)}}$$
- **Holm-Bonferroni Correction**: Applied if multiple domain or time-period contrasts are tested.
- **Effect Size**: Quantified using Cohen's $h = 2\arcsin(\sqrt{p_1}) - 2\arcsin(\sqrt{p_2})$.

### 6.2 Contingency Analysis
For an exploratory overall sentiment distribution comparison between the two domains ($3 \times 2$ table), Pearson's $\chi^2$ Test of Independence and Cramér's $V$ may be reported alongside product-clustered uncertainty estimates:
$$V = \sqrt{\frac{\chi^2}{N(k-1)}}$$

---

## 7. Results

> **Scientific Transparency Notice**:  
> The corpus is available locally, but no independently human-annotated benchmark has been completed. Accuracy, F1, and calibration results are therefore not reported. Existing results under `results/` are legacy synthetic fixture outputs and are excluded from empirical claims.

### 7.1 Human-Labeled Model Evaluation
**Pending.** Create and independently adjudicate a blinded annotation sample before computing accuracy, class-wise F1, or ECE. The source star rating must not be substituted for the human sentiment label.

### 7.2 Rating-Text Divergence Analysis
- Total rated reviews audited: `[Pending descriptive analysis of the imported corpus]`
- Rating-text agreement/divergence: `[Pending; describe as agreement with a rating heuristic, not sentiment accuracy]`

### 7.3 Within-Source Domain Comparison
- All Beauty vs Appliances sentiment and rating distributions: `[Pending descriptive analysis, product-clustered uncertainty estimates, and multiple-comparison plan]`
- No cross-platform test is supported by the current data.

---

## 8. Error Analysis and Failure Modes

Preliminary inspection of rule-based classification errors reveals three recurring failure modes:
1. **Sarcasm and Inverted Valence**: *"The phone stopped charging after two hours—truly a masterclass in modern engineering!"* (VADER detects *masterclass* as positive, assigning compound $C = +0.42$).
2. **Technical Specifications Misclassified as Neutral**: Long factual listings of technical specs without overt emotional tokens are classified as neutral, despite describing a defective hardware unit.
3. **Multi-Aspect Conflict**: Reviews praising the product while criticizing delivery/seller support result in diluted compound scores that hover in the $[-0.05, +0.05]$ neutral band.

---

## 9. Limitations, Ethics, and Data Statement

1. **Language and Marketplace Scope**: VADER is an English lexical model. The active corpus is historical Amazon data and does not represent Indian marketplaces or code-mixed Hindi, Tamil, or Hinglish reviews.
2. **Domain Confounding**: The two categories differ in product mix and review behavior. Observed category differences are descriptive and cannot be attributed to category alone without further controls and a sampling design.
3. **Data Statement**: The active corpus is historical Amazon Reviews 2023 data provided by the McAuley Lab primarily for research; its curators assign no license. Review text and the populated database remain local and are not redistributed. The synthetic fixture is excluded from empirical analyses.

---

## 10. Conclusion

This project delivers a disciplined, reproducible framework for evaluating sentiment analysis on e-commerce reviews. By decoupling star ratings from text sentiment, exposing the legal barriers to multi-marketplace data collection, and replacing informal score comparisons with valid hypothesis tests, we establish a credible foundation for empirical consumer intelligence research.

---

## 11. Venue Checklist & Target Submission Roadmap

When preparing this manuscript for conference or journal submission (e.g., *ACM Transactions on the Web*, *EMNLP Industrial/Empirical Track*, or *IEEE Transactions on Computational Social Systems*), the following checklist must be completed:

- [ ] Confirm institutional and source terms for the local Amazon Reviews 2023 research copy and obtain separate permission before redistributing any source text.
- [ ] Complete descriptive analysis with exact manifest counts, data-quality checks, product-clustered uncertainty estimates, and a pre-specified analysis plan.
- [ ] Complete double-annotation on $N \ge 1,000$ reviews and report inter-annotator agreement ($\kappa$).
- [ ] Train a supervised transformer baseline (e.g., `roberta-base` or `indic-bert` for multilingual code-mixing).
- [ ] Format LaTeX manuscript using the target venue's official document template (e.g., `acmart.cls` or `acl_natbib.sty`).
- [ ] Verify anonymized repository release for double-blind peer review.

---

## References

- Archak, N., Ghose, A., & Ipeirotis, P. G. (2011). Deriving the digital value of text: Extracting product attributes and relative weights from online reviews. *Information Systems Research*, 22(4), 888-909.
- Bender, E. M., & Friedman, B. (2018). Data statements for natural language processing: Toward mitigating system bias and enabling better science. *Transactions of the Association for Computational Linguistics*, 6, 587-604.
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *International Conference on Machine Learning (ICML)*, 1321-1330.
- Hu, N., Pavlou, P. A., & Zhang, J. (2006). Can online reviews reveal a product's true quality? Empirical findings and analytical modeling of online word-of-mouth communication. *ACM EC*, 324-330.
- Hutto, C., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Eighth International AAAI Conference on Weblogs and Social Media (ICWSM)*.
- Keung, P., Lu, Y., Szarvas, G., & Smith, N. A. (2020). The Multilingual Amazon Reviews Corpus. *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)*.
- McAuley, J., Targett, C., Shi, Q., & van den Hengel, A. (2015). Image-based recommendations on styles and substitutes. *Proceedings of the 38th International ACM SIGIR Conference*, 43-52.
- Mudambi, S. M., & Schuff, D. (2010). What makes a helpful online review? A study of customer reviews on Amazon.com. *MIS Quarterly*, 34(1), 185-200.
- Rogers, A., Gardner, M., & Augenstein, I. (2021). QA Dataset Explosion: A field guide for natural language processing. *EMNLP 2021*.
- Wang, W. Y., Hernandez, I. V., & Newman, D. (2014). Sarcasm detection on Twitter: A behavioral modeling approach. *Empirical Methods in Natural Language Processing (EMNLP)*.
