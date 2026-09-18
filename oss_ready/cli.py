import argparse
import json
from .checker import RepoChecker


def main():
    parser = argparse.ArgumentParser(
        description="Check if your repository is ready for open source."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to repository (default: current directory)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    args = parser.parse_args()

    try:
        checker = RepoChecker(args.path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    results = checker.run_all()
    score = checker.score(results)

    if args.json:
        output = {
            "path": str(checker.path),
            "score": round(score, 2),
            "results": [
                {
                    "key": r.key,
                    "name": r.name,
                    "passed": r.passed,
                    "weight": r.weight,
                    "message": r.message,
                    "suggestion": r.suggestion,
                }
                for r in results
            ],
        }
        print(json.dumps(output, indent=2))
        return 0

    print(f"\n📦 Open Source Readiness Report for: {checker.path}\n")
    for r in results:
        icon = "✅" if r.passed else "❌"
        print(f"{icon} {r.name}: {r.message}")
        if not r.passed and r.suggestion:
            print(f"   💡 {r.suggestion}")
    print(f"\n🎯 Score: {score:.1f}/100")
    if score >= 80:
        print("🎉 Great! Your repo is well-prepared for open source.")
    elif score >= 50:
        print("👍 Good start, but there's room for improvement.")
    else:
        print("🚧 Needs work. Check the suggestions above.")
    return 0


if __name__ == "__main__":
    main()
