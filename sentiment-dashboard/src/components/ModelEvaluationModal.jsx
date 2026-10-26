import React, { useState, useEffect } from 'react';
import { X, BarChart2, Loader2, RefreshCw } from 'lucide-react';
import { fetchEvaluationMetrics } from '../api/client';

export default function ModelEvaluationModal({ isOpen, onClose }) {
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadMetrics();
    }
  }, [isOpen]);

  const loadMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchEvaluationMetrics();
      setEvaluation(data);
    } catch (err) {
      setError(err.message || 'Failed to load model evaluation metrics.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const overall = evaluation?.overall;
  const cm = overall?.confusion_matrix;

  return (
    <div className="modal-backdrop flex-center" role="dialog" aria-modal="true" aria-labelledby="eval-modal-title">
      <div className="modal-container glass-panel animate-fade-in" style={{ maxWidth: '800px', width: '95%', maxHeight: '90vh', overflowY: 'auto' }}>
        <div className="modal-header flex-between">
          <div className="flex-center" style={{ gap: '0.6rem' }}>
            <BarChart2 size={20} color="#60a5fa" />
            <h2 id="eval-modal-title" style={{ margin: 0, fontSize: '1.25rem' }}>NLP Model Architecture & Evaluation Report</h2>
          </div>
          <button type="button" className="btn-icon" onClick={onClose} aria-label="Close dialog">
            <X size={18} />
          </button>
        </div>

        {loading ? (
          <div className="flex-center" style={{ padding: '4rem', flexDirection: 'column', gap: '1rem' }}>
            <Loader2 size={32} className="spin" color="var(--accent-color)" />
            <span>Computing live model performance metrics...</span>
          </div>
        ) : error ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--negative-color)' }}>
            <p>{error}</p>
            <button type="button" className="btn-secondary" onClick={loadMetrics} style={{ marginTop: '1rem' }}>
              <RefreshCw size={14} /> Retry
            </button>
          </div>
        ) : overall ? (
          <div className="modal-body" style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Overview Banner */}
            <div className="eval-summary-box glass-panel" style={{ background: 'rgba(15, 23, 42, 0.4)' }}>
              <div className="flex-between" style={{ flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Model Identifier</span>
                  <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>{evaluation.model_name} (v{evaluation.model_version})</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Macro F1-Score</span>
                  <div style={{ fontWeight: 700, fontSize: '1.2rem', color: 'var(--positive-color)' }}>
                    {Math.round(overall.macro_f1 * 100)}%
                  </div>
                </div>
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Overall Accuracy</span>
                  <div style={{ fontWeight: 700, fontSize: '1.2rem', color: '#60a5fa' }}>
                    {Math.round(overall.accuracy * 100)}%
                  </div>
                </div>
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Evaluation Samples</span>
                  <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>{overall.total_samples} records</div>
                </div>
              </div>
              <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {evaluation.methodology}
              </p>
            </div>

            {/* Classification Rules */}
            <div>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Classification Thresholds & Confidence Calibration</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                Sentiment classification maps the continuous VADER compound score C ∈ [-1.0, 1.0] to discrete categories:
              </p>
              <div className="thresholds-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', marginTop: '0.5rem' }}>
                <div className="glass-panel" style={{ padding: '0.75rem' }}>
                  <span className="badge positive">POSITIVE</span>
                  <div style={{ marginTop: '0.25rem', fontSize: '0.85rem' }}>Compound score C ≥ +0.05</div>
                </div>
                <div className="glass-panel" style={{ padding: '0.75rem' }}>
                  <span className="badge neutral">NEUTRAL</span>
                  <div style={{ marginTop: '0.25rem', fontSize: '0.85rem' }}>-0.05 &lt; C &lt; +0.05</div>
                </div>
                <div className="glass-panel" style={{ padding: '0.75rem' }}>
                  <span className="badge negative">NEGATIVE</span>
                  <div style={{ marginTop: '0.25rem', fontSize: '0.85rem' }}>Compound score C ≤ -0.05</div>
                </div>
              </div>
            </div>

            {/* Per-Class Metrics Table */}
            <div>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Per-Class Precision, Recall, and F1 Metrics</h3>
              <table className="metrics-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '0.5rem' }}>Sentiment Class</th>
                    <th style={{ padding: '0.5rem' }}>Precision</th>
                    <th style={{ padding: '0.5rem' }}>Recall</th>
                    <th style={{ padding: '0.5rem' }}>F1-Score</th>
                    <th style={{ padding: '0.5rem' }}>Validation Support</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(overall.per_class).map(([className, m]) => (
                    <tr key={className} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '0.5rem', fontWeight: 600 }}>{className}</td>
                      <td style={{ padding: '0.5rem' }}>{Math.round(m.precision * 100)}%</td>
                      <td style={{ padding: '0.5rem' }}>{Math.round(m.recall * 100)}%</td>
                      <td style={{ padding: '0.5rem', fontWeight: 600, color: 'var(--positive-color)' }}>{Math.round(m.f1_score * 100)}%</td>
                      <td style={{ padding: '0.5rem' }}>{m.support}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Confusion Matrix Table */}
            {cm && (
              <div>
                <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>3×3 Confusion Matrix (Actual vs. Predicted)</h3>
                <table className="cm-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                      <th style={{ padding: '0.5rem', textAlign: 'left' }}>Actual \ Predicted</th>
                      <th style={{ padding: '0.5rem' }}>Pred: POSITIVE</th>
                      <th style={{ padding: '0.5rem' }}>Pred: NEUTRAL</th>
                      <th style={{ padding: '0.5rem' }}>Pred: NEGATIVE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {['POSITIVE', 'NEUTRAL', 'NEGATIVE'].map((actualClass) => (
                      <tr key={actualClass} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                        <td style={{ padding: '0.5rem', fontWeight: 600, textAlign: 'left' }}>Actual: {actualClass}</td>
                        <td style={{ padding: '0.5rem', background: actualClass === 'POSITIVE' ? 'rgba(16, 185, 129, 0.15)' : 'transparent' }}>
                          {cm[actualClass]?.['POSITIVE'] || 0}
                        </td>
                        <td style={{ padding: '0.5rem', background: actualClass === 'NEUTRAL' ? 'rgba(245, 158, 11, 0.15)' : 'transparent' }}>
                          {cm[actualClass]?.['NEUTRAL'] || 0}
                        </td>
                        <td style={{ padding: '0.5rem', background: actualClass === 'NEGATIVE' ? 'rgba(239, 68, 68, 0.15)' : 'transparent' }}>
                          {cm[actualClass]?.['NEGATIVE'] || 0}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ) : null}

        <div className="modal-footer flex-between" style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Reproducible offline via <code>backend/app/nlp/evaluate.py</code>
          </span>
          <button type="button" className="btn-secondary" onClick={onClose}>
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
}
