from pathlib import Path


def test_dashboard_contains_release_evidence():
    html = Path("docs/index.html").read_text(encoding="utf-8")
    assert "release quality gate" in html
    assert "Evaluation evidence" in html
    assert "Assurance boundary" in html


def test_dashboard_data_matches_evaluation_scope():
    import json
    payload = json.loads(Path("docs/data/results.json").read_text(encoding="utf-8"))
    assert payload["summary"]["total"] == 20
    assert set(payload["dimensions"]) == {
        "grounding", "security", "privacy", "transparency", "human_oversight", "performance"
    }
