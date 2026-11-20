import React, { useEffect, useState } from 'react';
import { ArrowLeft, ChevronLeft, ChevronRight, LoaderCircle, Star, X } from 'lucide-react';
import { fetchProductReviews } from '../api/client';

function SentimentBar({ breakdown, label }) {
  if (!breakdown) return null;
  return (
    <div className="detail-sentiment">
      <div className="sentiment-progress-bar" role="img" aria-label={`${label}: ${breakdown.positive_pct}% positive, ${breakdown.neutral_pct}% neutral, ${breakdown.negative_pct}% negative`}>
        <div className="sent-segment pos" style={{ width: `${breakdown.positive_pct}%` }} />
        <div className="sent-segment neu" style={{ width: `${breakdown.neutral_pct}%` }} />
        <div className="sent-segment neg" style={{ width: `${breakdown.negative_pct}%` }} />
      </div>
      <div className="detail-sentiment-legend">
        <span className="positive-text">Positive {breakdown.positive_pct}% <small>({breakdown.positive})</small></span>
        <span className="neutral-text">Neutral {breakdown.neutral_pct}% <small>({breakdown.neutral})</small></span>
        <span className="negative-text">Negative {breakdown.negative_pct}% <small>({breakdown.negative})</small></span>
      </div>
    </div>
  );
}

export default function ProductDetailModal({ product, loading, error, isOpen, onClose }) {
  const [reviewPlatform, setReviewPlatform] = useState('all');
  const [reviewPage, setReviewPage] = useState(1);
  const [reviewsData, setReviewsData] = useState(null);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [reviewsError, setReviewsError] = useState(null);
  const [reviewsRefresh, setReviewsRefresh] = useState(0);

  useEffect(() => {
    if (!isOpen) return undefined;
    const onKeyDown = (event) => { if (event.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (!isOpen || !product?.id || product.total_reviews === 0) {
      setReviewsData(null);
      return undefined;
    }
    let active = true;
    setReviewsLoading(true);
    setReviewsError(null);
    fetchProductReviews(product.id, { platform: reviewPlatform, page: reviewPage, pageSize: 10 })
      .then((data) => { if (active) setReviewsData(data); })
      .catch((err) => { if (active) setReviewsError(err.message || 'Could not load reviews.'); })
      .finally(() => { if (active) setReviewsLoading(false); });
    return () => { active = false; };
  }, [isOpen, product?.id, product?.total_reviews, reviewPlatform, reviewPage, reviewsRefresh]);

  useEffect(() => {
    setReviewPlatform('all');
    setReviewPage(1);
    setReviewsData(null);
  }, [product?.id]);

  if (!isOpen) return null;

  return (
    <div className="product-modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <section className="product-modal glass-panel" role="dialog" aria-modal="true" aria-labelledby="product-detail-title">
        <div className="product-modal-topbar">
          <button className="product-back-button" type="button" onClick={onClose}><ArrowLeft size={16} /> Back to products</button>
          <button className="product-modal-close" type="button" aria-label="Close product details" onClick={onClose}><X size={20} /></button>
        </div>

        {loading ? (
          <div className="product-detail-state" role="status"><LoaderCircle className="spin" size={24} /> Loading product analysis…</div>
        ) : error ? (
          <div className="product-detail-state product-detail-error" role="alert"><h2>Couldn’t load this product</h2><p>{error}</p></div>
        ) : product ? (
          <>
            <header className="product-detail-header">
              <p className="eyebrow">PRODUCT REVIEW ANALYSIS</p>
              <h2 id="product-detail-title">{product.name}</h2>
              <p>{product.category || 'General'} <span aria-hidden="true">·</span> {product.total_reviews.toLocaleString()} reviews in this dataset</p>
            </header>

            {product.total_reviews === 0 ? (
              <div className="product-detail-empty">
                <h3>No reviews are linked to this catalog product yet</h3>
                <p>Platform coverage reflects imported review data, not current product availability.</p>
              </div>
            ) : (
              <>
                <div className="product-overview-grid">
                  <div className="product-overview-metric">
                    <span>Average star rating</span>
                    <strong><Star size={19} /> {product.average_rating == null ? '—' : product.average_rating}<small> / 5</small></strong>
                    <small>From reviews that include a rating</small>
                  </div>
                  <div className="product-overview-metric">
                    <span>Average VADER sentiment</span>
                    <strong>{product.average_compound == null ? '—' : product.average_compound > 0 ? `+${product.average_compound}` : product.average_compound}</strong>
                    <small>Lexicon score from −1 to +1</small>
                  </div>
                  <div className="product-overview-metric">
                    <span>Review sources</span>
                    <strong>{product.platform_stats.length}</strong>
                    <small>Platforms with reviews for this exact product record</small>
                  </div>
                </div>

                <section className="product-detail-section">
                  <div className="product-detail-section-heading"><div><p className="eyebrow">ALL SOURCES COMBINED</p><h3>Sentiment distribution</h3></div><span>{product.total_reviews.toLocaleString()} reviews</span></div>
                  <SentimentBar breakdown={product.sentiment_breakdown} label="Overall sentiment" />
                </section>

                <section className="product-detail-section">
                  <div className="product-detail-section-heading"><div><p className="eyebrow">SOURCE BREAKDOWN</p><h3>Reviews by platform</h3></div></div>
                  {product.platform_stats.length ? (
                    <div className="platform-detail-grid">
                      {product.platform_stats.map((platform) => (
                        <article className="platform-detail-card" key={platform.platform_code}>
                          <div className="platform-detail-title"><div><h4>{platform.platform_name}</h4><span>{platform.review_count.toLocaleString()} reviews in dataset</span></div><div className="platform-detail-rating"><Star size={15} /> {platform.average_rating ?? '—'}</div></div>
                          <SentimentBar breakdown={platform.sentiment_breakdown} label={`${platform.platform_name} sentiment`} />
                          {platform.review_count < 30 && <p className="small-sample-note">Small sample (under 30 reviews); interpret percentages cautiously.</p>}
                        </article>
                      ))}
                    </div>
                  ) : <p className="catalog-message">No platform breakdown is available for this product.</p>}
                </section>

                <section className="product-detail-section product-reviews-section">
                  <div className="product-detail-section-heading">
                    <div><p className="eyebrow">IMPORTED REVIEW TEXT</p><h3>Product reviews</h3></div>
                    <label className="review-platform-filter">
                      <span>Platform</span>
                      <select value={reviewPlatform} onChange={(event) => { setReviewPlatform(event.target.value); setReviewPage(1); }}>
                        <option value="all">All sources</option>
                        {product.platform_stats.map((platform) => <option key={platform.platform_code} value={platform.platform_code}>{platform.platform_name}</option>)}
                      </select>
                    </label>
                  </div>

                  {reviewsLoading ? (
                    <div className="product-review-state" role="status"><LoaderCircle className="spin" size={20} /> Loading reviews…</div>
                  ) : reviewsError ? (
                    <div className="product-review-state product-detail-error" role="alert"><p>{reviewsError}</p><button type="button" className="product-back-button" onClick={() => setReviewsRefresh((value) => value + 1)}>Try again</button></div>
                  ) : reviewsData?.reviews?.length ? (
                    <>
                      <p className="product-review-count">Showing {reviewsData.reviews.length} of {reviewsData.total.toLocaleString()} matching reviews</p>
                      <div className="product-review-list">
                        {reviewsData.reviews.map((review) => (
                          <article className="product-review-card" key={review.id}>
                            <div className="product-review-meta">
                              <span className="product-platform-chip">{review.platform_name}</span>
                              <span className="product-review-rating">{review.rating == null ? 'No star rating' : <><Star size={14} /> {review.rating} / 5</>}</span>
                              <span className={`badge ${review.sentiment === 'POSITIVE' ? 'positive' : review.sentiment === 'NEGATIVE' ? 'negative' : 'neutral'}`}>{review.sentiment}</span>
                            </div>
                            {review.headline && <h4>{review.headline}</h4>}
                            <p className="product-review-text">{review.review_text}</p>
                            <time className="product-review-date" dateTime={review.review_date || undefined}>{review.review_date ? new Date(review.review_date).toLocaleDateString() : 'Date not provided'}</time>
                          </article>
                        ))}
                      </div>
                      {reviewsData.total_pages > 1 && (
                        <nav className="product-review-pagination" aria-label="Product review pages">
                          <button type="button" className="product-back-button" disabled={reviewPage <= 1 || reviewsLoading} onClick={() => setReviewPage((page) => Math.max(1, page - 1))}><ChevronLeft size={16} /> Previous</button>
                          <span>Page {reviewsData.page} of {reviewsData.total_pages}</span>
                          <button type="button" className="product-back-button" disabled={reviewPage >= reviewsData.total_pages || reviewsLoading} onClick={() => setReviewPage((page) => page + 1)}>Next <ChevronRight size={16} /></button>
                        </nav>
                      )}
                    </>
                  ) : (
                    <p className="product-review-state">No reviews found for this product and platform filter.</p>
                  )}
                  <p className="product-review-disclaimer">These are reviews present in the imported research data for this exact product record; this does not indicate current availability.</p>
                </section>
              </>
            )}

            <p className="product-coverage-note">{product.data_coverage.notice}</p>
          </>
        ) : null}
      </section>
    </div>
  );
}
