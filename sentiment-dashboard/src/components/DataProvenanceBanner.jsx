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
              All analysis is performed strictly on locally authorized datasets. Live marketplace scraping is prohibited.
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
              <h4>Amazon Reviews</h4>
              <p>Amazon Customer Reviews Dataset (US TSV format), made available for academic & research exploration under the AWS Open Data Program.</p>
              <span className="provenance-meta">License: Non-commercial educational research only.</span>
            </div>

            <div className="provenance-item">
              <h4>Flipkart Reviews</h4>
              <p>Curated product review sentiment collection (Dataset-SA.csv) containing verified consumer ratings and summaries.</p>
              <span className="provenance-meta">License: Open research benchmarking. Original content terms apply.</span>
            </div>

            <div className="provenance-item">
              <h4>Myntra Fashion Reviews</h4>
              <p>Specialized apparel and footwear feedback corpus. Personal customer identifiers have been irreversibly redacted.</p>
              <span className="provenance-meta">License: Academic sentiment evaluation and sizing analytics.</span>
            </div>

            <div className="provenance-item">
              <h4>Meesho Product Reviews</h4>
              <p>Social commerce review corpus focusing on customer sentiment and value satisfaction in home and apparel categories.</p>
              <span className="provenance-meta">License: Educational evaluation. Anonymized textual records.</span>
            </div>
          </div>

          <div className="provenance-footer flex-between" style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <span>Privacy Note: Direct PII (customer names, emails, addresses) is purged at ingestion.</span>
            <span>Refer to <code>Datasets/README.md</code> for dataset acquisition and documentation.</span>
          </div>
        </div>
      )}
    </aside>
  );
}
