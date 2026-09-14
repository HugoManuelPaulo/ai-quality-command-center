# Model card: support-assistant-v1.4.0

## Intended use

A controlled customer-support assistant fixture used to demonstrate repeatable AI evaluation. Responses are stored in the scenario dataset so CI remains deterministic and provider-neutral.

## Evaluation scope

- Grounding against required reference terms
- Prompt-injection refusal
- Personal-data patterns
- AI transparency
- Human oversight for high-impact decisions
- Latency and cost thresholds

## Current result

18 of 20 evaluation scenarios pass. The release quality gate passes because the pass rate is 90% and there are no critical or high-severity findings. Two medium findings remain visible: missing AI disclosure and excessive latency.

## Limitations

Keyword and pattern checks do not prove semantic correctness, fairness, legal compliance or production safety. A real deployment requires representative datasets, human expert review, adversarial testing, monitoring and incident processes.
