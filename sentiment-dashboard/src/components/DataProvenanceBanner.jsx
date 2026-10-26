import React, { useState } from 'react';
import { Shield, ChevronDown, ChevronUp } from 'lucide-react';

export default function DataProvenanceBanner() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <aside className="provenance-banner glass-panel" aria-label="Data Provenance and Terms Notice">
      <div className="provenance-header flex-between" onClick={() => setIsExpanded(!isExpanded)} style={{ cursor: 'pointer' }}>
        <div className="flex-center" style={{ gap: '0.6rem' }}>
          <Shield size={18} style={{ color: '#60a5fa' }} />
          <div>
            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Data Integrity, Licensing & Compliance Notice</span>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              The research database contains historical Amazon reviews; it is not live inventory or cross-platform data.
            </div>
          </div>
        </div>

        <button 
          type="button" 
          className="btn-icon" 
          aria-expanded={isExpanded}
          aria-label={isExpanded ? 'Collapse data provenance details' : 'Expand data provenance details'}
        >
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {isExpanded && (
        <div className="provenance-details animate-fade-in">
          <div className="provenance-grid">
            <div className="provenance-item">
              <h4>Amazon Reviews 2023 (UCSD McAuley Lab)</h4>
              <p>Local research copy of the All Beauty and Appliances category review and item metadata files. Source reviews are historical (collection through September 2023).</p>
              <span className="provenance-meta">Research use: the curators assign no license and say the files are provided primarily for research. Do not redistribute review text.</span>
            </div>

            <div className="provenance-item">
              <h4>Coverage and freshness</h4>
              <p>This corpus represents one marketplace. It does not provide live offers, current stock, current prices, or reviews from Flipkart, Myntra, or Meesho.</p>
              <span className="provenance-meta">Use available prices only if independently verified as current; this corpus's metadata prices may be missing or historical.</span>
            </div>

            <div className="provenance-item">
              <h4>Research fixture</h4>
              <p>The 43-row sample CSV contains synthetic records for testing only and is kept separate from the empirical research database.</p>
              <span className="provenance-meta">Do not use the fixture as real customer feedback or empirical evidence.</span>
            </div>
          </div>

          <div className="provenance-footer flex-between" style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <span>Research database: <code>backend/sentiment_research.db</code> (local, ignored by Git).</span>
            <span>See <code>research/data_sources.md</code> for limitations and citation details.</span>
          </div>
        </div>
      )}
    </aside>
  );
}
