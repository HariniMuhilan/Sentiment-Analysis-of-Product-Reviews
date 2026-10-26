import React from 'react';
import { SearchX, Inbox, AlertTriangle, RefreshCw } from 'lucide-react';

export function EmptyState({ type = 'no_results', query = '', onRetry }) {
  if (type === 'no_data_in_database') {
    return (
      <div className="empty-state-panel glass-panel flex-center" role="status">
        <Inbox size={48} color="#94a3b8" />
        <h3 className="empty-title">Local Review Catalog is Empty</h3>
        <p className="empty-desc">
          No authorized product reviews have been ingested into the local database yet. 
          Use the dataset importer or CLI to ingest authorized review data:
        </p>
        <code className="code-snippet">
          python backend/run_ingest.py --platform generic --file Datasets/sample_authorized_reviews.csv
        </code>
        {onRetry && (
          <button type="button" className="btn-secondary flex-center" onClick={onRetry} style={{ marginTop: '1rem', gap: '0.4rem' }}>
            <RefreshCw size={14} /> Refresh Catalog
          </button>
        )}
      </div>
    );
  }

  if (type === 'error') {
    return (
      <div className="empty-state-panel glass-panel flex-center" role="alert">
        <AlertTriangle size={48} color="var(--negative-color)" />
        <h3 className="empty-title">Failed to Retrieve Analysis</h3>
        <p className="empty-desc">
          Unable to communicate with the sentiment analysis backend service. Ensure the backend API server is running on port 8000.
        </p>
        {onRetry && (
          <button type="button" className="btn-secondary flex-center" onClick={onRetry} style={{ marginTop: '1rem', gap: '0.4rem' }}>
            <RefreshCw size={14} /> Retry Connection
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="empty-state-panel glass-panel flex-center" role="status">
      <SearchX size={48} color="#94a3b8" />
      <h3 className="empty-title">No Matching Reviews Found</h3>
      <p className="empty-desc">
        {query ? (
          <>No reviews in the catalog matched <strong>"{query}"</strong> with the active filters.</>
        ) : (
          <>No reviews match the currently selected platform or rating filters.</>
        )}
      </p>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
        Try searching for popular catalog items like <em>"Sony WH-1000XM5"</em>, <em>"Nike Air Max"</em>, or <em>"Samsung Galaxy"</em>.
      </p>
    </div>
  );
}

export function LoadingSkeleton() {
  return (
    <div className="skeleton-container" aria-label="Loading analytics data">
      <div className="skeleton-grid">
        <div className="skeleton-card glass-panel" />
        <div className="skeleton-card glass-panel" />
        <div className="skeleton-card glass-panel" />
        <div className="skeleton-card glass-panel skeleton-card-wide" />
      </div>
      <div className="skeleton-panel glass-panel" style={{ height: '220px', marginTop: '1.5rem' }} />
      <div className="skeleton-panel glass-panel" style={{ height: '350px', marginTop: '1.5rem' }} />
    </div>
  );
}
