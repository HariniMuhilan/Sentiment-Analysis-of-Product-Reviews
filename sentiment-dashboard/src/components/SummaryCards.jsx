import React from 'react';
import { Star, MessageSquare, Award, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';

export default function SummaryCards({ analysis }) {
  if (!analysis) return null;

  const {
    total_reviews,
    average_rating,
    average_compound,
    sentiment_breakdown
  } = analysis;

  const renderStars = (rating) => {
    if (!rating) return <span style={{ color: 'var(--text-secondary)' }}>N/A</span>;
    const rounded = Math.round(rating);
    return (
      <div className="flex-center" style={{ gap: '2px', color: '#f59e0b' }} aria-label={`${rating} out of 5 stars`}>
        {[1, 2, 3, 4, 5].map((i) => (
          <Star
            key={i}
            size={16}
            fill={i <= rounded ? '#f59e0b' : 'transparent'}
            stroke="#f59e0b"
          />
        ))}
        <span style={{ marginLeft: '6px', fontWeight: 600, color: 'var(--text-primary)' }}>{rating}</span>
      </div>
    );
  };

  const getCompoundLabel = (score) => {
    if (score === null || score === undefined) return 'N/A';
    if (score >= 0.25) return 'Strongly Positive';
    if (score >= 0.05) return 'Mildly Positive';
    if (score > -0.05) return 'Neutral';
    if (score > -0.25) return 'Mildly Negative';
    return 'Strongly Negative';
  };

  return (
    <div className="summary-cards-container" aria-label="Key Performance Indicators">
      {/* 1. Total Reviews */}
      <div className="stat-card glass-panel">
        <div className="stat-card-header flex-between">
          <span className="stat-title">Catalog Reviews</span>
          <div className="stat-icon-wrap" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>
            <MessageSquare size={18} />
          </div>
        </div>
        <div className="stat-value">{total_reviews.toLocaleString()}</div>
        <div className="stat-subtitle">Locally stored and analyzed</div>
      </div>

      {/* 2. Average Rating */}
      <div className="stat-card glass-panel">
        <div className="stat-card-header flex-between">
          <span className="stat-title">Average Rating</span>
          <div className="stat-icon-wrap" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' }}>
            <Star size={18} />
          </div>
        </div>
        <div className="stat-value">{average_rating !== null ? `${average_rating} / 5.0` : '—'}</div>
        <div className="stat-subtitle">{renderStars(average_rating)}</div>
      </div>

      {/* 3. Average Compound Score */}
      <div className="stat-card glass-panel">
        <div className="stat-card-header flex-between">
          <span className="stat-title">Mean VADER Valence</span>
          <div className="stat-icon-wrap" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>
            <Award size={18} />
          </div>
        </div>
        <div className="stat-value">
          {average_compound !== null ? (average_compound > 0 ? `+${average_compound}` : average_compound) : '—'}
        </div>
        <div className="stat-subtitle" style={{ color: average_compound >= 0.05 ? 'var(--positive-color)' : average_compound <= -0.05 ? 'var(--negative-color)' : 'var(--neutral-color)' }}>
          {getCompoundLabel(average_compound)}
        </div>
      </div>

      {/* 4. Sentiment Breakdown */}
      <div className="stat-card glass-panel stat-card-wide">
        <div className="stat-card-header flex-between">
          <span className="stat-title">Sentiment Distribution</span>
          <span className="stat-badge">{total_reviews} total</span>
        </div>
        
        {/* Progress Bar */}
        <div className="distribution-bar" role="progressbar" aria-label="Sentiment distribution progress bar">
          <div 
            className="dist-segment dist-pos" 
            style={{ width: `${sentiment_breakdown.positive_pct}%` }} 
            title={`Positive: ${sentiment_breakdown.positive_pct}% (${sentiment_breakdown.positive})`}
          />
          <div 
            className="dist-segment dist-neu" 
            style={{ width: `${sentiment_breakdown.neutral_pct}%` }} 
            title={`Neutral: ${sentiment_breakdown.neutral_pct}% (${sentiment_breakdown.neutral})`}
          />
          <div 
            className="dist-segment dist-neg" 
            style={{ width: `${sentiment_breakdown.negative_pct}%` }} 
            title={`Negative: ${sentiment_breakdown.negative_pct}% (${sentiment_breakdown.negative})`}
          />
        </div>

        {/* Legend */}
        <div className="distribution-legend flex-between">
          <div className="legend-item flex-center">
            <span className="legend-dot dot-positive" />
            <ThumbsUp size={12} style={{ color: 'var(--positive-color)', marginRight: '4px' }} />
            <span>Positive: <strong>{sentiment_breakdown.positive_pct}%</strong> ({sentiment_breakdown.positive})</span>
          </div>
          <div className="legend-item flex-center">
            <span className="legend-dot dot-neutral" />
            <Minus size={12} style={{ color: 'var(--neutral-color)', marginRight: '4px' }} />
            <span>Neutral: <strong>{sentiment_breakdown.neutral_pct}%</strong> ({sentiment_breakdown.neutral})</span>
          </div>
          <div className="legend-item flex-center">
            <span className="legend-dot dot-negative" />
            <ThumbsDown size={12} style={{ color: 'var(--negative-color)', marginRight: '4px' }} />
            <span>Negative: <strong>{sentiment_breakdown.negative_pct}%</strong> ({sentiment_breakdown.negative})</span>
          </div>
        </div>
      </div>
    </div>
  );
}
