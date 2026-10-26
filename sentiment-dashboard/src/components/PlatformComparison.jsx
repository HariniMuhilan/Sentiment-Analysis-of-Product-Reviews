import React from 'react';
import { Star, AlertCircle, CheckCircle, Scale, HelpCircle } from 'lucide-react';

export default function PlatformComparison({ analysis }) {
  if (!analysis) return null;

  const {
    platforms: platformStats = [],
    statistical_comparison,
    data_coverage
  } = analysis;

  const getPlatformColor = (code) => {
    switch (code) {
      case 'amazon': return 'var(--amazon-color)';
      case 'flipkart': return 'var(--flipkart-color)';
      case 'myntra': return 'var(--myntra-color)';
      case 'meesho': return 'var(--meesho-color)';
      default: return 'var(--accent-color)';
    }
  };

  return (
    <section className="platform-comparison-section" aria-labelledby="platform-comparison-title">
      <div className="section-header flex-between">
        <div>
          <h2 id="platform-comparison-title">Platform Comparative Analysis</h2>
          <p className="section-subtitle">
            Cross-marketplace breakdown with sample size verification and 95% Wilson confidence intervals.
          </p>
        </div>
      </div>

      {/* Statistical Significance Callout */}
      <div className={`statistical-callout glass-panel ${statistical_comparison.is_statistically_significant ? 'significance-established' : 'significance-neutral'}`}>
        <div className="callout-header flex-center" style={{ gap: '0.6rem' }}>
          {statistical_comparison.is_statistically_significant ? (
            <CheckCircle size={18} style={{ color: 'var(--positive-color)' }} />
          ) : (
            <Scale size={18} style={{ color: 'var(--neutral-color)' }} />
          )}
          <span className="callout-title">
            {statistical_comparison.is_statistically_significant 
              ? `Two-Proportion Z-Test Finding: ${statistical_comparison.leader_platform}`
              : 'Statistical Comparison & Hypothesis Test Evaluation'}
          </span>
        </div>
        <p className="callout-text">{statistical_comparison.explanation}</p>
        
        {statistical_comparison.test_statistic !== null && statistical_comparison.test_statistic !== undefined && (
          <div className="test-metrics-pills flex-center" style={{ gap: '0.75rem', flexWrap: 'wrap', margin: '0.5rem 0', fontSize: '0.75rem' }}>
            <span className="badge-subtle">Method: {statistical_comparison.test_method}</span>
            <span className="badge-subtle">z-statistic: {statistical_comparison.test_statistic}</span>
            <span className="badge-subtle">p-value: {statistical_comparison.p_value}</span>
            {statistical_comparison.effect_size && (
              <span className="badge-subtle">Effect Size ({statistical_comparison.effect_size_type}): {statistical_comparison.effect_size}</span>
            )}
          </div>
        )}

        {statistical_comparison.confounder_warning && (
          <div className="callout-footer flex-center" style={{ gap: '0.4rem', color: '#f59e0b', fontSize: '0.8rem', marginTop: '0.5rem', alignItems: 'flex-start' }}>
            <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>{statistical_comparison.confounder_warning}</span>
          </div>
        )}

        {!statistical_comparison.sample_size_adequate && (
          <div className="callout-footer flex-center" style={{ gap: '0.4rem', color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.4rem' }}>
            <AlertCircle size={14} />
            <span>Hypothesis testing requires adequate sample sizes (N ≥ 30 per group) to fulfill asymptotic normality assumptions.</span>
          </div>
        )}
      </div>

      {/* Grid of Platform Cards */}
      <div className="grid-cards">
        {platformStats.map((p) => {
          const breakdown = p.sentiment_breakdown;
          const [lowCI, highCI] = p.wilson_positive_interval;

          return (
            <article key={p.platform_code} className="platform-card glass-panel" aria-labelledby={`plat-${p.platform_code}`}>
              <div className="platform-card-header flex-between">
                <div className="flex-center" style={{ gap: '0.5rem' }}>
                  <span 
                    className="platform-dot" 
                    style={{ backgroundColor: getPlatformColor(p.platform_code) }} 
                  />
                  <h3 id={`plat-${p.platform_code}`} className="platform-title">{p.platform_name}</h3>
                </div>
                <span className="badge-subtle">{p.review_count} reviews</span>
              </div>

              <div className="platform-rating-row flex-between">
                <span className="platform-metric-label">Average Star Rating</span>
                <div className="flex-center" style={{ gap: '4px' }}>
                  <Star size={14} fill="#f59e0b" stroke="#f59e0b" />
                  <span className="platform-metric-value">{p.average_rating !== null ? `${p.average_rating}` : '—'}</span>
                </div>
              </div>

              <div className="platform-rating-row flex-between">
                <span className="platform-metric-label">Mean VADER Compound</span>
                <span className="platform-metric-value" style={{ color: p.average_compound >= 0.05 ? 'var(--positive-color)' : p.average_compound <= -0.05 ? 'var(--negative-color)' : 'var(--neutral-color)' }}>
                  {p.average_compound !== null ? (p.average_compound > 0 ? `+${p.average_compound}` : p.average_compound) : '—'}
                </span>
              </div>

              {/* Progress Bar */}
              <div className="distribution-bar" style={{ height: '6px', margin: '0.75rem 0' }} role="progressbar" aria-label={`${p.platform_name} sentiment breakdown`}>
                <div className="dist-segment dist-pos" style={{ width: `${breakdown.positive_pct}%` }} />
                <div className="dist-segment dist-neu" style={{ width: `${breakdown.neutral_pct}%` }} />
                <div className="dist-segment dist-neg" style={{ width: `${breakdown.negative_pct}%` }} />
              </div>

              {/* Breakdown Labels */}
              <div className="platform-breakdown-numbers flex-between">
                <span style={{ color: 'var(--positive-color)' }}>Pos: {breakdown.positive_pct}%</span>
                <span style={{ color: 'var(--neutral-color)' }}>Neu: {breakdown.neutral_pct}%</span>
                <span style={{ color: 'var(--negative-color)' }}>Neg: {breakdown.negative_pct}%</span>
              </div>

              {/* Wilson Score Interval */}
              <div className="platform-confidence-box">
                <div className="confidence-title flex-center" style={{ gap: '0.3rem' }}>
                  <HelpCircle size={12} />
                  <span>95% Wilson Score CI (Positive Sentiment):</span>
                </div>
                <div className="confidence-interval-value">
                  [{Math.round(lowCI * 100)}% – {Math.round(highCI * 100)}%]
                </div>
                <div className="confidence-note">{p.statistical_notes}</div>
              </div>
            </article>
          );
        })}
      </div>

      {/* Platforms with 0 reviews */}
      {data_coverage.platforms_without_data.length > 0 && (
        <div className="missing-platforms-banner glass-panel" style={{ marginTop: '1.5rem' }}>
          <div className="flex-center" style={{ gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            <AlertCircle size={16} />
            <span>
              <strong>No data ingested for:</strong> {data_coverage.platforms_without_data.join(', ')}. 
              The platform comparison strictly excludes unimported platforms to prevent false representation.
            </span>
          </div>
        </div>
      )}
    </section>
  );
}
