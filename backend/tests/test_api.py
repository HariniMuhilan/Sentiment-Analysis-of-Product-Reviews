def test_list_platforms(client):
    response = client.get("/api/platforms")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4
    platform_codes = [p["code"] for p in data]
    assert "amazon" in platform_codes
    assert "flipkart" in platform_codes
    assert "myntra" in platform_codes
    assert "meesho" in platform_codes

def test_search_products(client):
    response = client.get("/api/products?q=Sony")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "Sony" in data[0]["name"]
    assert data[0]["total_reviews"] > 0

def test_analysis_aggregation(client):
    response = client.get("/api/analysis?q=Sony")
    assert response.status_code == 200
    data = response.json()
    assert data["total_reviews"] > 0
    assert data["average_rating"] is not None
    assert "sentiment_breakdown" in data
    assert data["sentiment_breakdown"]["positive"] >= 0
    assert "platforms" in data
    assert len(data["platforms"]) > 0
    assert "statistical_comparison" in data
    assert "model_metadata" in data
    assert "vader" in data["model_metadata"]["model_name"]

def test_reviews_pagination(client):
    response = client.get("/api/reviews?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "reviews" in data
    assert len(data["reviews"]) <= 5
    if len(data["reviews"]) > 0:
        rev = data["reviews"][0]
        assert "sentiment" in rev
        assert "compound_score" in rev
        assert "rating" in rev
        assert "model_name" in rev

def test_empty_search_returns_valid_structure(client):
    response = client.get("/api/analysis?q=NonExistentProductXYZ1234567")
    assert response.status_code == 200
    data = response.json()
    assert data["total_reviews"] == 0
    assert data["data_coverage"]["is_empty"] is True
    assert data["statistical_comparison"]["is_statistically_significant"] is False
