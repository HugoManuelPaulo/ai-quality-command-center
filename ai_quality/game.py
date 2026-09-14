import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ACTIONS = ("allow", "block", "escalate")


def load_challenges(path: str | Path | None = None) -> list[dict[str, Any]]:
    source = Path(path) if path else Path(__file__).parents[1] / "data" / "game_challenges.json"
    return json.loads(source.read_text(encoding="utf-8"))


def judge_challenge(challenge: dict[str, Any], action: str, streak: int = 0) -> dict[str, Any]:
    normalized = action.strip().lower()
    if normalized not in ACTIONS:
        raise ValueError(f"Action must be one of: {', '.join(ACTIONS)}")
    correct = normalized == challenge["correct_action"]
    next_streak = streak + 1 if correct else 0
    points = 100 + min(next_streak, 5) * 10 if correct else 0
    return {
        "challenge_id": challenge["id"],
        "correct": correct,
        "correct_action": challenge["correct_action"],
        "selected_action": normalized,
        "points": points,
        "streak": next_streak,
        "severity": challenge["severity"],
        "control": challenge["control"],
        "explanation": challenge["explanation"],
    }


@dataclass
class GameSession:
    score: int = 0
    streak: int = 0
    correct: int = 0
    answered: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    def submit(self, challenge: dict[str, Any], action: str) -> dict[str, Any]:
        result = judge_challenge(challenge, action, self.streak)
        self.answered += 1
        self.streak = result["streak"]
        self.score += result["points"]
        self.correct += int(result["correct"])
        self.history.append(result)
        return result

    def summary(self) -> dict[str, Any]:
        accuracy = round(100 * self.correct / self.answered, 1) if self.answered else 0.0
        if accuracy >= 90:
            rank = "AI Guardian"
        elif accuracy >= 70:
            rank = "Risk Analyst"
        else:
            rank = "Security Trainee"
        return {
            "score": self.score,
            "correct": self.correct,
            "answered": self.answered,
            "accuracy": accuracy,
            "rank": rank,
        }
