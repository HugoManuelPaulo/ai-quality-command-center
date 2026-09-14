import pytest

from ai_quality.game import GameSession, judge_challenge, load_challenges


@pytest.fixture
def challenge():
    return {
        "id": "TEST-RT",
        "correct_action": "block",
        "severity": "critical",
        "control": "Secret protection",
        "explanation": "The response exposes a secret.",
    }


def test_game_loads_twelve_versioned_challenges():
    challenges = load_challenges()
    assert len(challenges) == 12
    assert {item["correct_action"] for item in challenges} == {"allow", "block", "escalate"}


def test_correct_decision_scores_and_builds_streak(challenge):
    result = judge_challenge(challenge, "BLOCK", streak=2)
    assert result["correct"] is True
    assert result["points"] == 130
    assert result["streak"] == 3


def test_wrong_decision_resets_streak(challenge):
    result = judge_challenge(challenge, "allow", streak=4)
    assert result["correct"] is False
    assert result["points"] == 0
    assert result["streak"] == 0


def test_invalid_action_is_rejected(challenge):
    with pytest.raises(ValueError):
        judge_challenge(challenge, "delete")


def test_session_tracks_history_and_summary(challenge):
    session = GameSession()
    session.submit(challenge, "block")
    summary = session.summary()
    assert summary["correct"] == 1
    assert summary["accuracy"] == 100.0
    assert summary["rank"] == "AI Guardian"
    assert len(session.history) == 1


@pytest.mark.parametrize(
    ("correct", "answered", "rank"),
    [(0, 0, "Security Trainee"), (7, 10, "Risk Analyst"), (9, 10, "AI Guardian")],
)
def test_rank_reflects_accuracy(correct, answered, rank):
    session = GameSession(correct=correct, answered=answered)
    assert session.summary()["rank"] == rank
