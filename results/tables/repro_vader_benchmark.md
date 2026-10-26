# RePro Cross-Language Stress Benchmark

RePro single-polarity Brazilian Portuguese sample. Mixed labels were excluded from the three-class metrics.
VADER is English-oriented; these results are a cross-language stress baseline, not Portuguese in-language performance.
The RePro sample is stratified by star rating, so these numbers are not natural review prevalence estimates.

| Method | Accuracy | Macro F1 | Samples |
|---|---:|---:|---:|
| VADER lexical baseline | 0.2282 | 0.2414 | 7,985 |
| Star-rating heuristic | 0.8438 | 0.7020 | 7,985 |
| Majority-class baseline | 0.5168 | 0.2272 | 7,985 |

Citation: dos Santos Silva et al. (2024), *RePro: a benchmark for Opinion Mining for Brazilian Portuguese*, PROPOR, pp. 432–440.
