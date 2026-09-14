import json
import sys
from pathlib import Path

from ai_quality import evaluate_suite, load_scenarios


def main() -> int:
    report = evaluate_suite(load_scenarios())
    output = Path("reports/latest-results.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    summary = report["summary"]
    print(
        f"AI quality gate: {summary['quality_gate']} | "
        f"{summary['passed']}/{summary['total']} passed | "
        f"{summary['critical_issues']} critical | {summary['high_issues']} high"
    )
    return 0 if summary["quality_gate"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
