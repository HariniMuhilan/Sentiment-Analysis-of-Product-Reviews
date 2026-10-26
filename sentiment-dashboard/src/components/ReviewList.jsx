import React from 'react';
import { Star, ThumbsUp, Calendar, ChevronLeft, ChevronRight, Tag } from 'lucide-react';

export default function ReviewList({ 
  reviews = [], 
  total = 0, 
  page = 1, 
  totalPages = 1, 
  onPageChange,
  isLoading = false 
}) {
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Date unknown';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const getSentimentBadgeClass = (sentiment) => {
    switch (sentiment) {
      case 'POSITIVE': return 'badge positive';
      case 'NEGATIVE': return 'badge negative';
      default: return 'badge neutral';
    }
  };

  const getPlatformBadgeClass = (code) => {
    return `badge-platform platform-${code.toLowerCase()}`;
  };

  return (
    <section className="review-list-section" aria-labelledby="review-explorer-title">
      <div className="section-header flex-between">
        <div>
          <h2 id="review-explorer-title">Ingested Review Explorer</h2>
          <p className="section-subtitle">
            Showing {reviews.length} of {total.toLocaleString()} validated reviews from local catalog.
          </p>
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <nav className="pagination-controls flex-center" aria-label="Review pagination">
            <button
              type="button"
              className="pagination-btn"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1 || isLoading}
              aria-label="Previous page"
            >
              <ChevronLeft size={16} />
            </button>
            <span className="pagination-info">
              Page <strong>{page}</strong> of <strong>{totalPages}</strong>
            </span>
            <button
              type="button"
              className="pagination-btn"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages || isLoading}
              aria-label="Next page"
            >
              <ChevronRight size={16} />
            </button>
          </nav>
        )}
      </div>

      {reviews.length === 0 ? (
        <div className="glass-panel flex-center" style={{ padding: '3rem', flexDirection: 'column', color: 'var(--text-secondary)' }}>
          <p>No reviews match the selected query and filters.</p>
        </div>
      ) : (
        <div className="reviews-stack">
          {reviews.map((rev) => (
            <article key={rev.id} className="review-card glass-panel" tabIndex={0}>
              <div className="review-card-top flex-between">
                <div className="flex-center" style={{ gap: '0.6rem', flexWrap: 'wrap' }}>
                  <span className={getPlatformBadgeClass(rev.platform_code)}>
                    {rev.platform_name}
                  </span>
                  <span className="review-product-name">{rev.product_name}</span>
                  {rev.category && (
                    <span className="review-category-tag flex-center">
                      <Tag size={12} />
                      {rev.category}
                    </span>
                  )}
                </div>

                <div className="flex-center" style={{ gap: '0.75rem' }}>
                  <div className="review-rating flex-center" aria-label={`Rating: ${rev.rating} out of 5 stars`}>
                    <Star size={14} fill="#f59e0b" stroke="#f59e0b" />
                    <span>{rev.rating}</span>
                  </div>
                  <span className={getSentimentBadgeClass(rev.sentiment)}>
                    {rev.sentiment}
                  </span>
                </div>
              </div>

              {rev.headline && (
                <h4 className="review-headline">{rev.headline}</h4>
              )}

              <p className="review-text">{rev.review_text}</p>

              <div className="review-footer flex-between">
                <div className="review-nlp-meta flex-center" style={{ gap: '0.8rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  <span>Compound Valence: <strong>{rev.compound_score > 0 ? `+${rev.compound_score}` : rev.compound_score}</strong></span>
                  <span>Confidence: <strong>{Math.round(rev.confidence * 100)}%</strong></span>
                  <span className="model-tag">{rev.model_name}</span>
                </div>

                <div className="review-source-meta flex-center" style={{ gap: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {rev.helpful_votes > 0 && (
                    <span className="flex-center" style={{ gap: '4px' }}>
                      <ThumbsUp size={13} />
                      {rev.helpful_votes} helpful
                    </span>
                  )}
                  <span className="flex-center" style={{ gap: '4px' }}>
                    <Calendar size={13} />
                    {formatDate(rev.review_date)}
                  </span>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}

      {/* Bottom Pagination */}
      {totalPages > 1 && (
        <div className="pagination-bottom flex-center" style={{ marginTop: '1.5rem' }}>
          <button
            type="button"
            className="pagination-btn-large flex-center"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1 || isLoading}
          >
            <ChevronLeft size={16} /> Previous
          </button>
          <span style={{ margin: '0 1.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            className="pagination-btn-large flex-center"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages || isLoading}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      )}
    </section>
  );
}
