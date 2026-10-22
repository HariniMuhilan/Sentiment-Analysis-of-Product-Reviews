import React, { useState } from 'react';
import { Search, TrendingUp, Award, BarChart2 } from 'lucide-react';
import { getMockAnalysis, mockPlatforms } from './mockData';
import './index.css';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    // Simulate API call
    const data = await getMockAnalysis(query);
    setResults(data);
    setLoading(false);
  };

  return (
    <>
      <div className="container">
        <header className="animate-fade-in flex-center" style={{ flexDirection: 'column', textAlign: 'center', marginBottom: '2rem' }}>
          <h1>Cross-Platform Sentiment Analysis</h1>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', lineHeight: '1.6' }}>
            Compare product reviews across Amazon, Flipkart, Myntra, and Meesho instantly. 
            Powered by advanced machine learning models (Prototype).
          </p>
        </header>

        <form onSubmit={handleSearch} className="search-container animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <Search className="search-icon" size={20} />
          <input 
            type="text" 
            className="search-input" 
            placeholder="Enter a product name (e.g., 'iPhone 15 Pro', 'Nike Air Max')"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </form>

        {loading && (
          <div className="flex-center" style={{ padding: '3rem', color: 'var(--accent-color)' }}>
            <div style={{ animation: 'spin 1s linear infinite' }}>
              <TrendingUp size={32} />
            </div>
            <span style={{ marginLeft: '1rem', fontWeight: '500' }}>Analyzing sentiments...</span>
          </div>
        )}

        {results && !loading && (
          <div className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
            
            <div className="glass-panel" style={{ marginBottom: '2rem', display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
              <div style={{ flex: '1', minWidth: '200px' }}>
                <h3 style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>Overall Verdict</h3>
                <div className="flex-center" style={{ justifyContent: 'flex-start', marginTop: '0.5rem', gap: '0.5rem' }}>
                  <Award color="var(--accent-color)" size={24} />
                  <span style={{ fontSize: '1.25rem', fontWeight: '600' }}>Platform Winner: {results.overall.platformWinner}</span>
                </div>
              </div>
              <div style={{ flex: '1', minWidth: '200px' }}>
                <h3 style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>Dominant Sentiment</h3>
                <div style={{ marginTop: '0.5rem' }}>
                  <span className={`badge ${results.overall.dominantSentiment.toLowerCase()}`}>
                    {results.overall.dominantSentiment}
                  </span>
                </div>
              </div>
              <div style={{ flex: '1', minWidth: '200px' }}>
                <h3 style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>Total Reviews Analyzed</h3>
                <div style={{ marginTop: '0.5rem', fontSize: '1.25rem', fontWeight: '600' }}>
                  {results.overall.totalAnalyzed.toLocaleString()}
                </div>
              </div>
            </div>

            <h2 style={{ marginTop: '3rem' }}>Platform Breakdown</h2>
            <div className="grid-cards">
              {mockPlatforms.map((platform) => {
                const data = results.platforms[platform];
                const positiveWidth = `${data.sentiment.positive}%`;
                const neutralWidth = `${data.sentiment.neutral}%`;
                const negativeWidth = `${data.sentiment.negative}%`;

                return (
                  <div key={platform} className="glass-panel">
                    <div className="flex-between" style={{ marginBottom: '1rem' }}>
                      <h3 style={{ color: `var(--${platform.toLowerCase()}-color)` }}>{platform}</h3>
                      <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                        ★ {data.averageRating.toFixed(1)} / 5
                      </span>
                    </div>

                    <div style={{ marginBottom: '1.5rem' }}>
                      <div className="flex-between" style={{ fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                        <span>Sentiment Distribution</span>
                        <span style={{ color: 'var(--text-secondary)' }}>{data.totalReviews.toLocaleString()} reviews</span>
                      </div>
                      <div className="bar-chart">
                        <div className="bar-segment" style={{ width: positiveWidth, backgroundColor: 'var(--positive-color)' }} title={`Positive: ${positiveWidth}`} />
                        <div className="bar-segment" style={{ width: neutralWidth, backgroundColor: 'var(--neutral-color)' }} title={`Neutral: ${neutralWidth}`} />
                        <div className="bar-segment" style={{ width: negativeWidth, backgroundColor: 'var(--negative-color)' }} title={`Negative: ${negativeWidth}`} />
                      </div>
                      <div className="flex-between" style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        <span><span style={{ color: 'var(--positive-color)' }}>■</span> {data.sentiment.positive}%</span>
                        <span><span style={{ color: 'var(--neutral-color)' }}>■</span> {data.sentiment.neutral}%</span>
                        <span><span style={{ color: 'var(--negative-color)' }}>■</span> {data.sentiment.negative}%</span>
                      </div>
                    </div>

                    <div>
                      <h4 style={{ fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Sample Reviews</h4>
                      {data.recentReviews.map(review => (
                        <div key={review.id} style={{ 
                          padding: '0.75rem', 
                          backgroundColor: 'rgba(255,255,255,0.03)', 
                          borderRadius: '8px', 
                          marginBottom: '0.5rem',
                          fontSize: '0.875rem'
                        }}>
                          <div style={{ marginBottom: '0.25rem' }}>{review.text}</div>
                          <div className="flex-between">
                            <span className={`badge ${review.sentiment}`} style={{ fontSize: '0.65rem' }}>
                              {review.sentiment}
                            </span>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                              Conf: {(review.score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>

                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}} />
    </>
  );
}

export default App;
