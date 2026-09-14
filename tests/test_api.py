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


def test_game_challenges_hide_answers():
    response = client.get("/api/game/challenges")
    assert response.status_code == 200
    assert len(response.json()) == 12
    assert "correct_action" not in response.json()[0]


def test_game_answer_returns_scored_feedback():
    response = client.post("/api/game/answer", json={
        "challenge_id": "RT-001", "action": "block", "streak": 1,
    })
    assert response.status_code == 200
    assert response.json()["correct"] is True
    assert response.json()["points"] == 120


def test_game_rejects_invalid_action_and_unknown_challenge():
    invalid = client.post("/api/game/answer", json={
        "challenge_id": "RT-001", "action": "ignore",
    })
    missing = client.post("/api/game/answer", json={
        "challenge_id": "UNKNOWN", "action": "allow",
    })
    assert invalid.status_code == 422
    assert missing.status_code == 404
