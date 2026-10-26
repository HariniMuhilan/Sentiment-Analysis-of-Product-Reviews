import React from 'react';
import { BarChart3, Activity, Info } from 'lucide-react';

export default function Header({ health, onOpenModelInfo }) {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="header-container animate-fade-in" role="banner">
      <div className="header-top flex-between">
        <div className="brand flex-center" style={{ gap: '0.75rem' }}>
          <div className="brand-logo flex-center" aria-hidden="true">
            <BarChart3 size={24} color="#60a5fa" />
          </div>
          <div>
            <span className="brand-title">Cross-Platform Sentiment Analytics</span>
            <div className="brand-subtitle">Empirical Customer Review Intelligence</div>
          </div>
        </div>

        <div className="header-actions flex-center" style={{ gap: '0.75rem' }}>
          <div 
            className={`status-pill flex-center ${isHealthy ? 'online' : 'offline'}`}
            title={isHealthy ? `Backend connected: ${health.nlp_model}` : 'Backend offline'}
            aria-live="polite"
          >
            <Activity size={14} className={isHealthy ? 'pulse' : ''} />
            <span>{isHealthy ? 'API Online' : 'API Connecting...'}</span>
          </div>

          <button 
            type="button"
            className="btn-secondary flex-center"
            onClick={onOpenModelInfo}
            aria-label="View NLP Model & Evaluation Metrics"
            style={{ gap: '0.4rem', fontSize: '0.85rem', padding: '0.4rem 0.8rem' }}
          >
            <Info size={15} />
            <span>Model Details</span>
          </button>
        </div>
      </div>

      <div className="header-headline">
        <h1>Cross-Platform Review Sentiment Analysis</h1>
        <p className="header-description">
          Evaluate customer feedback across Amazon, Flipkart, Myntra, and Meesho using genuine lexical sentiment analysis with 95% Wilson confidence intervals.
        </p>
      </div>
    </header>
  );
}
