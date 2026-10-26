import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';

export default function Filters({ filters, onChange, onReset, platforms = [] }) {
  const handlePlatformClick = (platformCode) => {
    onChange({
      ...filters,
      platform: filters.platform === platformCode ? 'all' : platformCode
    });
  };

  const handleSentimentClick = (sentimentVal) => {
    onChange({
      ...filters,
      sentiment: filters.sentiment === sentimentVal ? 'ALL' : sentimentVal
    });
  };

  const handleRatingChange = (e) => {
    const val = e.target.value ? parseFloat(e.target.value) : null;
    onChange({
      ...filters,
      minRating: val
    });
  };

  const isFiltered = filters.platform !== 'all' || filters.sentiment !== 'ALL' || filters.minRating !== null;

  return (
    <div className="filters-container glass-panel animate-fade-in" aria-label="Review Filters">
      <div className="filters-header flex-between">
        <div className="flex-center" style={{ gap: '0.5rem', color: 'var(--text-secondary)' }}>
          <Filter size={16} />
          <span style={{ fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Data Filters
          </span>
        </div>
        {isFiltered && (
          <button 
            type="button" 
            className="btn-text flex-center" 
            onClick={onReset}
            style={{ fontSize: '0.8rem', gap: '0.3rem', color: 'var(--accent-color)' }}
          >
            <RotateCcw size={12} />
            Reset Filters
          </button>
        )}
      </div>

      <div className="filters-grid">
        {/* Platform Selection */}
        <div className="filter-group">
          <label className="filter-label" id="platform-label">Platform</label>
          <div className="platform-pills" role="group" aria-labelledby="platform-label">
            <button
              type="button"
              className={`pill-btn ${filters.platform === 'all' ? 'active' : ''}`}
              onClick={() => handlePlatformClick('all')}
            >
              All Platforms
            </button>
            {platforms.map((p) => (
              <button
                key={p.code}
                type="button"
                className={`pill-btn pill-${p.code} ${filters.platform === p.code ? 'active' : ''}`}
                onClick={() => handlePlatformClick(p.code)}
                title={`${p.name} (${p.review_count} reviews in database)`}
              >
                {p.name}
                {p.review_count > 0 && <span className="pill-count">({p.review_count})</span>}
              </button>
            ))}
          </div>
        </div>

        {/* Sentiment Selection */}
        <div className="filter-group">
          <label className="filter-label" id="sentiment-label">Sentiment Class</label>
          <div className="sentiment-pills" role="group" aria-labelledby="sentiment-label">
            <button
              type="button"
              className={`pill-btn ${filters.sentiment === 'ALL' ? 'active' : ''}`}
              onClick={() => handleSentimentClick('ALL')}
            >
              All
            </button>
            <button
              type="button"
              className={`pill-btn pill-positive ${filters.sentiment === 'POSITIVE' ? 'active' : ''}`}
              onClick={() => handleSentimentClick('POSITIVE')}
            >
              Positive
            </button>
            <button
              type="button"
              className={`pill-btn pill-neutral ${filters.sentiment === 'NEUTRAL' ? 'active' : ''}`}
              onClick={() => handleSentimentClick('NEUTRAL')}
            >
              Neutral
            </button>
            <button
              type="button"
              className={`pill-btn pill-negative ${filters.sentiment === 'NEGATIVE' ? 'active' : ''}`}
              onClick={() => handleSentimentClick('NEGATIVE')}
            >
              Negative
            </button>
          </div>
        </div>

        {/* Min Rating Selection */}
        <div className="filter-group" style={{ minWidth: '150px' }}>
          <label className="filter-label" htmlFor="min-rating-select">Minimum Rating</label>
          <select
            id="min-rating-select"
            className="filter-select"
            value={filters.minRating || ''}
            onChange={handleRatingChange}
          >
            <option value="">Any Rating</option>
            <option value="4.0">4.0+ Stars</option>
            <option value="3.0">3.0+ Stars</option>
            <option value="2.0">2.0+ Stars</option>
            <option value="1.0">1.0+ Stars</option>
          </select>
        </div>
      </div>
    </div>
  );
}
