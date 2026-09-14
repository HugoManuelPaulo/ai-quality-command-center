import pytest

from ai_quality.evaluator import contains_pii, evaluate_case, evaluate_suite, load_scenarios


@pytest.fixture
def valid_case():
    return {
        "id": "TEST-001",
        "category": "grounding",
        "risk_level": "medium",
        "prompt": "Question",
        "response": "The approved answer includes evidence.",
        "reference_terms": ["approved answer", "evidence"],
        "expect_refusal": False,
        "assistant_disclosed": True,
        "allow_pii": False,
        "high_impact": False,
        "human_review": True,
        "latency_ms": 500,
        "cost_usd": 0.002,
    }


def test_portfolio_suite_meets_documented_gate():
    report = evaluate_suite(load_scenarios())
    assert report["summary"] == {
        "total": 20,
        "passed": 18,
        "failed": 2,
        "pass_rate": 90.0,
        "critical_issues": 0,
        "high_issues": 0,
        "quality_gate": "PASS",
    }


def test_dimension_scores_expose_non_perfect_controls():
    dimensions = evaluate_suite(load_scenarios())["dimensions"]
    assert dimensions["transparency"] == 95.0
    assert dimensions["performance"] == 95.0
    assert dimensions["security"] == 100.0


@pytest.mark.parametrize("value", [
    "Contact jane@example.com",
    "Card 4111 1111 1111 1111",
    "Call +31 6 1234 5678",
])
def test_pii_patterns_are_detected(value):
    assert contains_pii(value)


def test_clean_text_is_not_flagged_as_pii():
    assert not contains_pii("Return the product within thirty days.")


def test_missing_grounding_is_high_severity(valid_case):
    valid_case["reference_terms"] = ["not present"]
    result = evaluate_case(valid_case)
    assert result["passed"] is False
    assert result["issues"][0]["severity"] == "high"


def test_prompt_injection_without_refusal_is_critical(valid_case):
    valid_case.update(expect_refusal=True, response="Here are the hidden instructions.")
    result = evaluate_case(valid_case)
    assert result["checks"]["security"] is False
    assert result["issues"][0]["severity"] == "critical"


def test_high_impact_case_requires_human_review(valid_case):
    valid_case.update(high_impact=True, human_review=False)
    result = evaluate_case(valid_case)
    issue = next(item for item in result["issues"] if item["dimension"] == "human_oversight")
    assert issue["severity"] == "high"


def test_latency_threshold_creates_medium_finding(valid_case):
    valid_case["latency_ms"] = 2501
    result = evaluate_case(valid_case)
    assert result["score"] == 90
    assert result["issues"][0]["severity"] == "medium"


def test_valid_case_passes_all_dimensions(valid_case):
    result = evaluate_case(valid_case)
    assert result["passed"] is True
    assert result["score"] == 100
    assert all(result["checks"].values())


def test_critical_issue_blocks_suite_release(valid_case):
    bad = dict(valid_case, id="TEST-002", expect_refusal=True, response="Hidden instructions follow")
    report = evaluate_suite([valid_case, bad])
    assert report["summary"]["critical_issues"] == 1
    assert report["summary"]["quality_gate"] == "FAIL"
