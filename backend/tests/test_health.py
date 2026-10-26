def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data
    assert "nlp_model" in data

def test_ready_endpoint(client):
    response = client.get("/api/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert data["total_reviews"] > 0
    assert data["total_products"] > 0
    assert data["platforms_active"] >= 4
