import React from 'react';
import { ArrowUpRight, Star, Tag } from 'lucide-react';

export default function ProductCard({ product, onOpenDetail }) {
  const sentiment = product.sentiment_breakdown;

  return (
    <article className="product-card glass-panel">
      <div className="product-card-header">
        <div>
          <h3 className="product-title">{product.name}</h3>
          {product.category && <span className="product-category"><Tag size={13} />{product.category}</span>}
        </div>
        <div className="product-rating" aria-label={product.average_rating == null ? 'No star rating' : `Average rating ${product.average_rating} out of 5`}>
          <Star size={16} aria-hidden="true" />
          <strong>{product.average_rating == null ? '—' : product.average_rating}</strong>
        </div>
      </div>

      <div className="product-card-meta">
        <span>{product.total_reviews.toLocaleString()} reviews</span>
        <span>{product.platforms.length} {product.platforms.length === 1 ? 'source' : 'sources'} with review data</span>
      </div>

      {sentiment && (
        <>
          <div className="sentiment-bar-wrapper">
            <div className="sentiment-progress-bar" role="img" aria-label={`${sentiment.positive_pct}% positive, ${sentiment.neutral_pct}% neutral, ${sentiment.negative_pct}% negative`}>
              <div className="sent-segment pos" style={{ width: `${sentiment.positive_pct}%` }} />
              <div className="sent-segment neu" style={{ width: `${sentiment.neutral_pct}%` }} />
              <div className="sent-segment neg" style={{ width: `${sentiment.negative_pct}%` }} />
            </div>
          </div>
          <div className="sentiment-summary product-sentiment-summary">
            <span><i className="sentiment-dot positive-dot" />Positive <strong>{sentiment.positive_pct}%</strong></span>
            <span><i className="sentiment-dot neutral-dot" />Neutral <strong>{sentiment.neutral_pct}%</strong></span>
            <span><i className="sentiment-dot negative-dot" />Negative <strong>{sentiment.negative_pct}%</strong></span>
          </div>
        </>
      )}

      <div className="product-platform-list" aria-label="Platforms with review data">
        {product.platforms.map((platform) => <span className="product-platform-chip" key={platform}>{platform}</span>)}
        {product.platforms.length === 0 && <span className="muted-label">No platform review data</span>}
      </div>

      <button className="product-detail-button" type="button" onClick={() => onOpenDetail(product.id)}>
        View product analysis <ArrowUpRight size={16} aria-hidden="true" />
      </button>
    </article>
  );
}
