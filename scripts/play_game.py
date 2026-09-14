from ai_quality.game import ACTIONS, GameSession, load_challenges


def main() -> None:
    session = GameSession()
    challenges = load_challenges()
    print("\nAI RED TEAM ARENA")
    print("Decide whether each AI response should be ALLOW, BLOCK or ESCALATE.\n")

    for number, challenge in enumerate(challenges, start=1):
        print(f"[{number}/{len(challenges)}] {challenge['title']} | risk: {challenge['severity']}")
        print(f"USER: {challenge['prompt']}")
        print(f"AI:   {challenge['response']}")
        while True:
            action = input("Decision [allow/block/escalate]: ").strip().lower()
            if action in ACTIONS:
                break
            print("Choose allow, block or escalate.")
        result = session.submit(challenge, action)
        verdict = "CORRECT" if result["correct"] else "MISSED"
        print(f"{verdict} | +{result['points']} | {result['explanation']}\n")

    summary = session.summary()
    print(f"FINAL SCORE: {summary['score']} | {summary['correct']}/{summary['answered']}")
    print(f"ACCURACY: {summary['accuracy']}% | RANK: {summary['rank']}")


if __name__ == "__main__":
    main()
