import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Filters from './components/Filters';
import SummaryCards from './components/SummaryCards';
import PlatformComparison from './components/PlatformComparison';
import ReviewList from './components/ReviewList';
import DataProvenanceBanner from './components/DataProvenanceBanner';
import ModelEvaluationModal from './components/ModelEvaluationModal';
import { EmptyState, LoadingSkeleton } from './components/EmptyState';
import { 
  fetchHealth, 
  fetchReadiness, 
  fetchPlatforms, 
  fetchSentimentAnalysis, 
  fetchReviews 
} from './api/client';
import './index.css';

function App() {
  const [health, setHealth] = useState(null);
  const [readiness, setReadiness] = useState(null);
  const [platforms, setPlatforms] = useState([]);
  
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({
    platform: 'all',
    sentiment: 'ALL',
    minRating: null,
    category: 'all'
  });

  const [analysis, setAnalysis] = useState(null);
  const [reviewsData, setReviewsData] = useState({ reviews: [], total: 0, total_pages: 1, page: 1 });
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isModelModalOpen, setIsModelModalOpen] = useState(false);

  // Initialize status & platforms
  const initSystem = useCallback(async () => {
    try {
      const [hRes, rRes, pRes] = await Promise.allSettled([
        fetchHealth(),
        fetchReadiness(),
        fetchPlatforms()
      ]);

      if (hRes.status === 'fulfilled') setHealth(hRes.value);
      if (rRes.status === 'fulfilled') setReadiness(rRes.value);
      if (pRes.status === 'fulfilled') setPlatforms(pRes.value);
    } catch (err) {
      console.warn('System initialization warning:', err);
    }
  }, []);

  useEffect(() => {
    initSystem();
  }, [initSystem]);

  // Main data fetching
  const loadData = useCallback(async (currQuery, currFilters, currPage = 1) => {
    setLoading(true);
    setError(null);
    try {
      const analysisResult = await fetchSentimentAnalysis({
        query: currQuery,
        platform: currFilters.platform,
        sentiment: currFilters.sentiment,
        minRating: currFilters.minRating,
        category: currFilters.category
      });
      setAnalysis(analysisResult);

      // Reviews list
      setReviewsLoading(true);
      const reviewsResult = await fetchReviews({
        query: currQuery,
        platform: currFilters.platform,
        sentiment: currFilters.sentiment,
        minRating: currFilters.minRating,
        category: currFilters.category,
        page: currPage,
        pageSize: pageSize
      });
      setReviewsData(reviewsResult);
    } catch (err) {
      console.error('Error fetching sentiment data:', err);
      setError(err.message || 'Unable to connect to sentiment analysis API.');
    } finally {
      setLoading(false);
      setReviewsLoading(false);
    }
  }, [pageSize]);

  // Trigger load on query or filters change
  useEffect(() => {
    setPage(1);
    loadData(query, filters, 1);
  }, [query, filters, loadData]);

  // Page change handler
  const handlePageChange = async (newPage) => {
    if (newPage < 1 || newPage > reviewsData.total_pages) return;
    setPage(newPage);
    setReviewsLoading(true);
    try {
      const result = await fetchReviews({
        query: query,
        platform: filters.platform,
        sentiment: filters.sentiment,
        minRating: filters.minRating,
        category: filters.category,
        page: newPage,
        pageSize: pageSize
      });
      setReviewsData(result);
    } catch (err) {
      console.error('Failed to change page:', err);
    } finally {
      setReviewsLoading(false);
    }
  };

  const handleSearch = (newQuery) => {
    setQuery(newQuery);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleResetFilters = () => {
    setFilters({
      platform: 'all',
      sentiment: 'ALL',
      minRating: null,
      category: 'all'
    });
  };

  const isEmptyCatalog = readiness && readiness.total_reviews === 0;

  return (
    <div className="app-layout">
      <div className="container">
        {/* Header & Status */}
        <Header 
          health={health} 
          onOpenModelInfo={() => setIsModelModalOpen(true)} 
        />

        {/* Data Provenance & Legal Banner */}
        <DataProvenanceBanner />

        {/* Search Bar */}
        <SearchBar 
          onSearch={handleSearch} 
          initialQuery={query} 
        />

        {/* Filters */}
        <Filters 
          filters={filters} 
          onChange={handleFilterChange} 
          onReset={handleResetFilters}
          platforms={platforms}
        />

        {/* Main Content Area */}
        <main className="content-container">
          {loading ? (
            <LoadingSkeleton />
          ) : error ? (
            <EmptyState 
              type="error" 
              onRetry={() => { initSystem(); loadData(query, filters, 1); }} 
            />
          ) : isEmptyCatalog ? (
            <EmptyState 
              type="no_data_in_database" 
              onRetry={() => { initSystem(); loadData(query, filters, 1); }} 
            />
          ) : analysis?.total_reviews === 0 ? (
            <EmptyState 
              type="no_results" 
              query={query} 
            />
          ) : (
            <>
              {/* Summary Metrics */}
              <SummaryCards analysis={analysis} />

              {/* Source-level coverage and sentiment */}
              <PlatformComparison 
                analysis={analysis} 
                platforms={platforms} 
              />

              {/* Review Explorer */}
              <ReviewList 
                reviews={reviewsData.reviews}
                total={reviewsData.total}
                page={page}
                totalPages={reviewsData.total_pages}
                onPageChange={handlePageChange}
                isLoading={reviewsLoading}
              />
            </>
          )}
        </main>

        {/* Model Architecture & Evaluation Modal */}
        <ModelEvaluationModal 
          isOpen={isModelModalOpen} 
          onClose={() => setIsModelModalOpen(false)} 
        />

        {/* Footer */}
        <footer className="footer-container flex-between" role="contentinfo">
          <div>
            <span>Sentiment Analysis Review &copy; {new Date().getFullYear()}</span>
            <span style={{ margin: '0 0.5rem' }}>•</span>
            <span>Amazon Reviews 2023 Research Corpus</span>
          </div>
          <div>
            <span>Engine: VADER Lexicon NLP v1.0.0</span>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
