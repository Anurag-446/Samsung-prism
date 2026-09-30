"""Integration tests for POST /v1/troubleshoot and GET /health FastAPI endpoints."""

import os

os.environ["FIXGRAPH_MODE"] = "test"
os.environ["DEEPLINKS_PATH"] = "tests/fixtures/challenge_assets/deeplinks.json"
os.environ["QUERIES_PATH"] = "tests/fixtures/challenge_assets/queries.json"
os.environ["SIIS_PATH"] = "tests/fixtures/challenge_assets/siis_responses.json"

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
    assert "query" in data
    assert "response" in data
    assert "contexts" in data["response"]

    goal = data["response"]["contexts"][0]
    assert "goal" in goal
    assert "title" in goal
    assert "score" in goal
    assert "actions" in goal

    # Verify Goal syntax requirement
    assert goal["goal"].startswith("Follow these steps to perform this")
    assert 0.0 <= goal["score"] <= 1.0
    assert len(goal["actions"]) >= 1


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
