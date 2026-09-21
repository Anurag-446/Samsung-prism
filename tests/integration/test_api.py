"""Integration tests for POST /v1/troubleshoot and GET /health FastAPI endpoints."""

from fastapi.testclient import TestClient
from fixgraph.app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_troubleshoot_endpoint_battery_query():
    payload = {"query": "battery drain fast after update"}
    response = client.post("/v1/troubleshoot", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "goal" in data
    assert "title" in data
    assert "score" in data
    assert "actions" in data
    assert "query_variations" in data

    # Verify Goal syntax requirement
    assert data["goal"].startswith("Follow these steps to perform this")
    assert 0.0 <= data["score"] <= 1.0
    assert len(data["actions"]) >= 1
    assert 8 <= len(data["query_variations"]) <= 10


def test_troubleshoot_endpoint_cache_hit():
    payload = {"query": "phone location accuracy issues"}
    
    # First request -> Cold path
    res1 = client.post("/v1/troubleshoot", json=payload)
    assert res1.status_code == 200
    data1 = res1.json()

    # Second request -> Fast path cache hit
    res2 = client.post("/v1/troubleshoot", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()

    # Verify deterministic response matching
    assert data1 == data2
