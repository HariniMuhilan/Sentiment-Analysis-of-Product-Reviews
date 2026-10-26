# Research Protocol & Methodology Specification

**Project Title**: Evaluating Lexical Sentiment in Historical Amazon Product Reviews: Rating-Text Agreement, Domain Variation, and Reproducibility
**Version**: 1.0.0 (Pre-Registration Draft)  
**Status**: Working protocol draft; this document has not been externally time-stamped or formally pre-registered

---

## 1. Research Questions & Hypotheses

### Primary Research Questions
- **RQ1 (Empirical Validity of Rule-Based Lexical Sentiment)**: How reliably does an unsupervised, rule-based lexical classifier (VADER) classify e-commerce product review sentiment into Positive, Neutral, and Negative categories when evaluated against independent, double-annotated human ground truth?
- **RQ2 (Star Rating vs. Text Sentiment Divergence)**: How frequently and under what circumstances do numerical star ratings (1–5) diverge from semantic text sentiment, and does treating star ratings as pseudo-labels introduce systematic measurement error?
- **RQ3 (Within-Amazon Domain Variation)**: How do rating-text agreement and VADER sentiment distributions differ between the included All Beauty and Appliances domains, and how are those differences associated with review length, rating, and review period?
- **RQ4 (Methodological Rigor & Reproducibility)**: What minimal data governance and statistical verification standards are necessary to prevent invalid significance claims in e-commerce review research?

### Formal Hypotheses
- **$H_1$ (Star-Rating Divergence)**: At least 10% of 1-star/2-star and 4-star/5-star reviews exhibit mixed or conflicting text sentiment (e.g., positive product feedback paired with negative delivery/service complaints, or sarcastic phrasing), rendering star ratings an imperfect surrogate for textual sentiment.
- **$H_2$ (VADER Neutral Class Weakness)**: VADER will exhibit significantly lower F1 scores on the *Neutral* class ($F_1 < 0.60$) compared to *Positive* and *Negative* classes, due to lexical dictionaries favoring strong polarity tokens and struggling with descriptive, non-emotive technical feedback.
- **$H_3$ (Domain Composition)**: Any raw sentiment-distribution difference between the two sampled domains will change after stratifying by star rating and review length. Treat this as an exploratory within-source comparison; it cannot establish a causal marketplace effect or generalize to other categories.

---

## 2. Experimental Design & Baselines

### 2.1 Model Baselines
To assess VADER rigorously, we establish three comparative reference baselines:
1. **Majority Class Baseline (ZeroR)**: Predicts the most frequent class in the evaluation set for all instances. Establishes the lower bound of non-informative classification.
2. **Star-Rating Heuristic Baseline**:
   - $\text{Rating} \in \{4.0, 5.0\} \implies \text{POSITIVE}$
   - $\text{Rating} = 3.0 \implies \text{NEUTRAL}$
   - $\text{Rating} \in \{1.0, 2.0\} \implies \text{NEGATIVE}$
   - Unrated reviews $\implies \text{Excluded or mapped to Majority}$
   This baseline quantifies the agreement between customer numerical ratings and textual sentiment.
3. **Lexical Rule-Based Model (VADER)**:
   - Compound score $C \ge +0.05 \implies \text{POSITIVE}$
   - $-0.05 < C < +0.05 \implies \text{NEUTRAL}$
   - $C \le -0.05 \implies \text{NEGATIVE}$
4. **Supervised Linear Baseline (TF-IDF + Logistic Regression)**:
   - Evaluated under 5-fold cross-validation or held-out train/test split (when labeled training data is available).

### 2.2 Data Split & Leakage Prevention
- **Unit of Splitting**: Splitting must occur at the **Product Level** (`product_id` / normalized name) rather than random review-level sampling. This prevents data leakage where identical phrasing or duplicate reviews appear in both training and test partitions.
- **Temporal Hold-Out**: When review timestamps are present, the most recent 20% of reviews chronologically are designated as the evaluation set to measure performance drift.

---

## 3. Human Annotation Protocol

### 3.1 Class Definitions & Guidelines
Annotators must read the review text independently of the numerical rating to avoid anchoring bias.

| Class | Definition | Exemplar Phrases |
|---|---|---|
| **POSITIVE** | The reviewer expresses clear satisfaction, admiration, praise, or enthusiasm about the product's performance, quality, aesthetics, or value. | *"Battery lasts two full days", "Excellent sound quality", "Exceeded expectations"* |
| **NEUTRAL** | The review is strictly factual, balanced with equal minor pros and cons, or lacks emotional polarity. | *"Device arrived on Tuesday in brown packaging", "Standard cotton shirt, fits as sized"* |
| **NEGATIVE** | The reviewer expresses dissatisfaction, frustration, disappointment, functional defects, or poor build quality. | *"Screen cracked after two days", "Terrible audio distortion", "Complete waste of money"* |
| **MIXED** | The review contains strong positive elements about the product alongside strong negative elements (e.g., product is great, but arrived broken or seller was unhelpful). | *"The sound is 10/10 but the headband broke in one week", "Love the shoes but courier was 3 weeks late"* |

*Annotation Rule for Mixed Reviews*: Annotators are instructed to record a secondary tag `IS_MIXED = True`. For 3-class classification, mixed reviews are categorized based on overall product functional verdict, or labeled `NEUTRAL` if pros and cons are balanced.

### 3.2 Annotation Procedure & Quality Control
1. **Double Annotation**: A minimum of 2 independent annotators label each review in the validation sample.
2. **Inter-Annotator Agreement**: Measured using **Cohen's Kappa ($\kappa$)** for pairs, or **Fleiss' Kappa** for $>2$ annotators:
   $$\kappa = \frac{p_o - p_e}{1 - p_e}$$
   Target threshold: $\kappa \ge 0.70$ (substantial agreement). If $\kappa < 0.70$, guidelines are clarified and annotators undergo retraining.
3. **Adjudication**: Disagreements ($\approx 10-15\%$ anticipated) are reviewed by a third senior adjudicator to produce the final consensus label.
4. **Blinding**: Annotators are blinded to:
   - Star rating
   - Platform name (to prevent platform bias)
   - Brand name / seller identity

### 3.3 Ethical Governance & Data Privacy
- No personally identifiable information (PII) is presented to annotators.
- All reviewers' usernames, profile links, and direct contact details are stripped prior to creating annotation packs.
- Human annotation must follow institutional research ethics guidelines (IRB / Ethics Committee waiver or exemption for non-sensitive public feedback data).

---

## 4. Evaluation Metrics & Calibration

### 4.1 Categorical Performance
For each class $c \in \{\text{POSITIVE}, \text{NEUTRAL}, \text{NEGATIVE}\}$:
- **Precision**: $P_c = \frac{TP_c}{TP_c + FP_c}$
- **Recall**: $R_c = \frac{TP_c}{TP_c + FN_c}$
- **$F_1$-Score**: $F_{1,c} = \frac{2 P_c R_c}{P_c + R_c}$
- **Macro-Averaged $F_1$**:
  $$\text{Macro } F_1 = \frac{1}{3} \sum_{c \in \{\text{Pos}, \text{Neu}, \text{Neg}\}} F_{1,c}$$
- **Confusion Matrix**: Full $3 \times 3$ contingency table reporting $N_{ij}$ (true class $i$, predicted class $j$).

### 4.2 Probability Calibration
Model outputs must not be labeled as "calibrated probabilities" without empirical verification:
- **Expected Calibration Error (ECE)**: Group predictions into $M$ bins by confidence $B_m$:
  $$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$
- **Brier Score**: Multi-class quadratic loss measuring mean squared difference between predicted probabilities and one-hot true labels.

---

## 5. Valid Statistical Comparison Methodology

To prevent false claims of statistical significance:
1. **Hypothesis Testing for Category Proportions**:
   - When comparing sentiment distributions between two platforms, use **Pearson's $\chi^2$ Test of Independence** on the $2 \times 3$ contingency table.
   - For pairwise proportion comparisons, use the **Two-Proportion $Z$-Test** with **Holm-Bonferroni correction** to control Family-Wise Error Rate ($\alpha = 0.05$).
2. **Effect Size Quantification**:
   - Report **Cramér's $V$** for $\chi^2$ contingency tables:
     $$V = \sqrt{\frac{\chi^2}{N \cdot \min(r-1, c-1)}}$$
   - Report **Cohen's $h$** for difference between two proportions:
     $$h = 2 \arcsin(\sqrt{p_1}) - 2 \arcsin(\sqrt{p_2})$$
3. **Controlling for Product Confounders**:
   - If Platform A sells primarily consumer electronics and Platform B sells primarily apparel, raw sentiment differences reflect category expectations, not platform superiority.
   - Statistical comparisons must stratify by category or use **multivariable logistic regression** controlling for:
     $$\text{logit}(P(\text{Positive})) = \beta_0 + \beta_{\text{platform}} X_{\text{platform}} + \beta_{\text{category}} X_{\text{category}} + \beta_{\text{length}} X_{\text{length}} + \epsilon$$
   - A platform difference is only claimed if $\beta_{\text{platform}}$ remains statistically significant ($p < 0.05$) after conditioning on category and length.
