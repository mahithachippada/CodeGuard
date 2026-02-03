# -*- coding: utf-8 -*-
# ==========================================
# CodeGuard CLI
# Module 4: CLI & Configuration
# + Quality Gate Enforcement (Module 5)
# ==========================================

import argparse
import os
import sys
import json

# ------------------------------------------
# TOML CONFIG LOADING (Python 3.8+ safe)
# ------------------------------------------
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python < 3.11


# ------------------------------------------
# SEVERITY RANKING
# ------------------------------------------
SEVERITY_ORDER = {
    "CRITICAL": 3,
    "WARNING": 2,
    "INFO": 1
}


# ------------------------------------------
# LOAD CONFIG FROM pyproject.toml
# ------------------------------------------
def load_config():
    config = {
        "severity_threshold": "INFO",
        "exclude_paths": []
    }

    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            tool_cfg = data.get("tool", {}).get("codeguard", {})
            config.update(tool_cfg)

    return config


# ------------------------------------------
# QUALITY GATE CHECK
# ------------------------------------------
def should_block_commit(report_file, threshold):
    if not os.path.exists(report_file):
        return False

    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for file_report in data:
        for issue in file_report.get("issues", []):
            if SEVERITY_ORDER[issue["severity"]] >= SEVERITY_ORDER[threshold]:
                return True

    return False


# ------------------------------------------
# COMMAND IMPLEMENTATIONS
# ------------------------------------------
def run_scan(config):
    print("[SCAN] Running static analysis (Module 1)...")
    os.system("module1.py")

    report_file = "module1_report.json"
    threshold = config["severity_threshold"]

    if should_block_commit(report_file, threshold):
        print("[ERROR] Quality gate failed.")
        print(f"[ERROR] Issues exceed severity threshold: {threshold}")
        sys.exit(1)

    print("[OK] Scan completed. Quality gate passed.")


def run_review(_config):
    print("[REVIEW] Running AI review (Module 2)...")
    os.system("module2.py")
    print("[OK] Review completed.")


def run_report(_config):
    print("[REPORT] Generating validation metrics (Module 3)...")
    os.system("module3.py")
    print("[OK] Report generated.")


def run_apply(_config):
    print("[APPLY] Auto-fix feature is a placeholder.")
    print("[INFO] Only safe fixes will be supported in future.")


def run_diff(_config):
    print("[DIFF] Diff view feature is a placeholder.")


# ------------------------------------------
# MAIN CLI
# ------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="CodeGuard - AI-assisted Code Review Tool"
    )

    parser.add_argument(
        "command",
        choices=["scan", "review", "report", "apply", "diff"],
        help="Command to run"
    )

    args = parser.parse_args()
    config = load_config()

    print("Configuration loaded:")
    print(config)
    print("-" * 40)

    if args.command == "scan":
        run_scan(config)
    elif args.command == "review":
        run_review(config)
    elif args.command == "report":
        run_report(config)
    elif args.command == "apply":
        run_apply(config)
    elif args.command == "diff":
        run_diff(config)


# ------------------------------------------
# ENTRY POINT
# ------------------------------------------
if __name__ == "__main__":
    main()
