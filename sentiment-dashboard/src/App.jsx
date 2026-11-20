import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Filters from './components/Filters';
import SummaryCards from './components/SummaryCards';
import PlatformComparison from './components/PlatformComparison';
import ReviewList from './components/ReviewList';
import ProductCard from './components/ProductCard';
import ProductDetailModal from './components/ProductDetailModal';
import DataProvenanceBanner from './components/DataProvenanceBanner';
import ModelEvaluationModal from './components/ModelEvaluationModal';
import { EmptyState, LoadingSkeleton } from './components/EmptyState';
import {
  fetchHealth,
  fetchReadiness,
  fetchPlatforms,
  fetchCategories,
  fetchSentimentAnalysis,
  fetchReviews,
  searchCatalog,
  getProductDetail
} from './api/client';
import './index.css';

function App() {
  const [health, setHealth] = useState(null);
  const [readiness, setReadiness] = useState(null);
  const [platforms, setPlatforms] = useState([]);
  const [categories, setCategories] = useState([]);
  
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

  const [catalogResults, setCatalogResults] = useState([]);
  const [catalogLoading, setCatalogLoading] = useState(false);
  const [catalogError, setCatalogError] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [productDetail, setProductDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState(null);

  // Initialize status & platforms
  const initSystem = useCallback(async () => {
    try {
      const [hRes, rRes, pRes, cRes] = await Promise.allSettled([
        fetchHealth(),
        fetchReadiness(),
        fetchPlatforms(),
        fetchCategories()
      ]);

      if (hRes.status === 'fulfilled') setHealth(hRes.value);
      if (rRes.status === 'fulfilled') setReadiness(rRes.value);
      if (pRes.status === 'fulfilled') setPlatforms(pRes.value);
      if (cRes.status === 'fulfilled') setCategories(cRes.value);
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

  useEffect(() => {
    const normalizedQuery = query.trim();
    const selectedCategory = filters.category;
    if (normalizedQuery.length < 2 && (!selectedCategory || selectedCategory === 'all')) {
      setCatalogResults([]);
      setCatalogError(null);
      setCatalogLoading(false);
      return undefined;
    }

    let active = true;
    const timer = setTimeout(async () => {
      setCatalogLoading(true);
      setCatalogError(null);
      try {
        const results = await searchCatalog(normalizedQuery, selectedCategory);
        if (active) setCatalogResults(results);
      } catch (err) {
        if (active) setCatalogError(err.message || 'Could not load matching products.');
      } finally {
        if (active) setCatalogLoading(false);
      }
    }, 250);

    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [query, filters.category]);

  const openProductDetail = async (productId) => {
    setSelectedProduct(productId);
    setProductDetail(null);
    setDetailError(null);
    setDetailLoading(true);
    try {
      const details = await getProductDetail(productId);
      setProductDetail(details);
    } catch (err) {
      setDetailError(err.message || 'Could not load this product’s review analysis.');
    } finally {
      setDetailLoading(false);
    }
  };

  const closeProductDetail = () => {
    setSelectedProduct(null);
    setProductDetail(null);
    setDetailError(null);
  };

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
          category={filters.category}
        />

        {/* Filters */}
        <Filters 
          filters={filters} 
          onChange={handleFilterChange} 
          onReset={handleResetFilters}
          platforms={platforms}
          categories={categories}
        />

        {/* Main Content Area */}
        <main className="content-container">
          {(query.trim().length >= 2 || (filters.category && filters.category !== 'all')) && (
            <section className="catalog-results" aria-labelledby="catalog-results-title">
              <div className="catalog-results-heading">
                <div>
                  <p className="eyebrow">LOCAL PRODUCT CATALOG</p>
                  <h2 id="catalog-results-title">Products matching your search</h2>
                </div>
                {!catalogLoading && <span className="catalog-result-count">{catalogResults.length} shown</span>}
              </div>
              {catalogLoading ? (
                <p className="catalog-message" role="status">Finding matching products…</p>
              ) : catalogError ? (
                <p className="catalog-message catalog-error" role="alert">{catalogError}</p>
              ) : catalogResults.length ? (
                <div className="product-grid">
                  {catalogResults.map((product) => (
                    <ProductCard key={product.id} product={product} onOpenDetail={openProductDetail} />
                  ))}
                </div>
              ) : (
                <p className="catalog-message">No matching catalog products were found.</p>
              )}
            </section>
          )}

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

        <ProductDetailModal
          product={productDetail}
          loading={detailLoading}
          error={detailError}
          isOpen={selectedProduct !== null}
          onClose={closeProductDetail}
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
