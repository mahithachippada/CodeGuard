import argparse
import os
import sys
import json

from codeguard.dispatcher import analyze_file
from codeguard.module2 import generate_ai_review
from codeguard.module3 import compute_metrics


SEVERITY_ORDER = {"CRITICAL": 3, "WARNING": 2, "INFO": 1}

def load_config():
    config = {"severity_threshold": "WARNING", "exclude_paths": []}
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            config.update(data.get("tool", {}).get("codeguard", {}))
    return config

def should_block(results, threshold):
    for file in results:
        for issue in file["issues"]:
            if SEVERITY_ORDER[issue["severity"]] >= SEVERITY_ORDER[threshold]:
                return True
    return False

def run_scan(config, target):
    results = []
    for root, dirs, files in os.walk(target):
        if any(ex in root for ex in config.get("exclude_paths", [])):
            continue
        for f in files:
            results.append(analyze_file(os.path.join(root, f)))

    with open("module1_report.json", "w", encoding="utf-8") as out:
        json.dump(results, out, indent=2)

    # Always save last_results.json
    with open("last_results.json", "w", encoding="utf-8") as out:
        json.dump(results, out, indent=2)

    if should_block(results, config["severity_threshold"]):
        print("[ERROR] Quality gate failed")
        sys.exit(1)

    print("[OK] Scan passed")
    return results


def run_review(results, use_llm=False):
    ai_reviews = generate_ai_review(results, use_llm=use_llm)
    with open("ai_review.json", "w", encoding="utf-8") as out:
        json.dump(ai_reviews, out, indent=2)
    print("[OK] AI Review completed")
    return ai_reviews

def run_report(results):
    metrics = compute_metrics(results)
    with open("module3_metrics.json", "w", encoding="utf-8") as out:
        json.dump(metrics, out, indent=2)
    print("[OK] Metrics computed")
    return metrics

def main():
    parser = argparse.ArgumentParser(prog="codeguard")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("path", nargs="?", default=".")

    review_parser = subparsers.add_parser("review")
    review_parser.add_argument("--llm", action="store_true")

    subparsers.add_parser("report")

    args = parser.parse_args()
    config = load_config()
    print("Configuration loaded:", config)

    if args.command == "scan":
        results = run_scan(config, args.path)
        with open("last_results.json", "w", encoding="utf-8") as out:
            json.dump(results, out, indent=2)
    elif args.command == "review":
        if not os.path.exists("last_results.json"):
            print("⚠️ Run scan first")
            sys.exit(1)
        with open("last_results.json", "r", encoding="utf-8") as f:
            results = json.load(f)
        run_review(results, use_llm=args.llm)
    elif args.command == "report":
        if not os.path.exists("last_results.json"):
            print("⚠️ Run scan first")
            sys.exit(1)
        with open("last_results.json", "r", encoding="utf-8") as f:
            results = json.load(f)
        run_report(results)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
