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
              Historical Amazon reviews plus a small cross-retailer device corpus; no live listings, prices, or inventory.
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
              <p>The local research corpus includes All Beauty and Appliances, with Electronics expanding coverage to popular audio, phone, and home-device products. Electronics selection uses the 1,000 products with the highest source metadata review counts, then includes their matching reviews. This is historical Amazon data through September 2023, not a current popularity ranking.</p>
              <span className="provenance-meta">Research use: the curators assign no license and say the files are provided primarily for research. Do not redistribute review text.</span>
            </div>

            <div className="provenance-item">
              <h4>Cross-retailer coverage and freshness</h4>
              <p>The searchable data includes 2,370 smart-device reviews from Amazon, Best Buy, eBay, Target, and Walmart. Five of ten source-provided device names appear on multiple retailers. This is a small historical benchmark, not broad marketplace coverage, and the names are not verified against global product identifiers.</p>
              <span className="provenance-meta">The research data does not provide live offers, current stock, or current prices. Do not interpret source-provided device-name groupings as independently verified product matches.</span>
            </div>

            <div className="provenance-item">
              <h4>Virtual Assistant Devices label limitation</h4>
              <p>The dataset's downloaded sentiment-label counts differ from the counts reported by its paper and record. The app runs VADER on the review text; it does not use those source labels as predictions.</p>
              <span className="provenance-meta">Do not treat the disputed source labels as a gold evaluation set unless the discrepancy is resolved.</span>
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
