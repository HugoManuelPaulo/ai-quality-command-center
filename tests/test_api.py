import pytest
from fastapi.testclient import TestClient

from api.main import app

pytestmark = pytest.mark.api
client = TestClient(app)


def test_health_contract():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_summary_exposes_quality_gate():
    response = client.get("/api/summary")
    assert response.status_code == 200
    assert response.json()["quality_gate"] == "PASS"
    assert response.json()["pass_rate"] == 90.0


def test_evaluations_return_versioned_results():
    payload = client.get("/api/evaluations").json()
    assert payload["model_version"] == "support-assistant-v1.4.0"
    assert len(payload["results"]) == 20


def test_single_evaluation_can_be_retrieved():
    response = client.get("/api/evaluations/AIQ-005")
    assert response.status_code == 200
    assert response.json()["checks"]["security"] is True


def test_unknown_evaluation_returns_404():
    response = client.get("/api/evaluations/UNKNOWN")
    assert response.status_code == 404


def test_custom_payload_is_evaluated():
    response = client.post("/api/evaluate", json={
        "id": "LIVE-001", "category": "performance", "risk_level": "medium",
        "prompt": "Hello", "response": "I am an AI assistant.",
        "latency_ms": 300, "cost_usd": 0.001,
    })
    assert response.status_code == 200
    assert response.json()["passed"] is True


def test_incomplete_payload_is_rejected():
    response = client.post("/api/evaluate", json={"id": "LIVE-002"})
    assert response.status_code == 422
