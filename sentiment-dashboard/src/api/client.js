const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function handleResponse(res) {
  if (!res.ok) {
    let errorDetail = 'API request failed';
    try {
      const data = await res.json();
      errorDetail = data.detail || errorDetail;
    } catch {
      errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return handleResponse(res);
}

export async function fetchReadiness() {
  const res = await fetch(`${API_BASE}/ready`);
  return handleResponse(res);
}

export async function fetchPlatforms() {
  const res = await fetch(`${API_BASE}/platforms`);
  return handleResponse(res);
}

export async function searchCatalog(query) {
  const params = new URLSearchParams();
  if (query) params.append('q', query);
  params.append('limit', '10');
  const res = await fetch(`${API_BASE}/products?${params.toString()}`);
  return handleResponse(res);
}

export async function fetchSentimentAnalysis({
  query,
  platform,
  category,
  minRating,
  maxRating,
  sentiment,
  startDate,
  endDate
} = {}) {
  const params = new URLSearchParams();
  if (query) params.append('q', query);
  if (platform && platform !== 'all') params.append('platform', platform);
  if (category && category !== 'all') params.append('category', category);
  if (minRating) params.append('min_rating', minRating);
  if (maxRating) params.append('max_rating', maxRating);
  if (sentiment && sentiment !== 'ALL') params.append('sentiment', sentiment);
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const res = await fetch(`${API_BASE}/analysis?${params.toString()}`);
  return handleResponse(res);
}

export async function fetchReviews({
  query,
  platform,
  category,
  minRating,
  maxRating,
  sentiment,
  startDate,
  endDate,
  page = 1,
  pageSize = 10
} = {}) {
  const params = new URLSearchParams();
  if (query) params.append('q', query);
  if (platform && platform !== 'all') params.append('platform', platform);
  if (category && category !== 'all') params.append('category', category);
  if (minRating) params.append('min_rating', minRating);
  if (maxRating) params.append('max_rating', maxRating);
  if (sentiment && sentiment !== 'ALL') params.append('sentiment', sentiment);
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  params.append('page', page);
  params.append('page_size', pageSize);

  const res = await fetch(`${API_BASE}/reviews?${params.toString()}`);
  return handleResponse(res);
}

export async function fetchEvaluationMetrics() {
  const res = await fetch(`${API_BASE}/evaluation`);
  return handleResponse(res);
}

export async function ingestDatasetFile(platform, file) {
  const formData = new FormData();
  formData.append('platform', platform);
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    body: formData
  });
  return handleResponse(res);
}
