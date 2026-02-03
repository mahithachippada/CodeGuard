# ==========================================
# Module 4: CLI & Configuration
# ==========================================
# - Command-line interface for CodeGuard
# - Commands: scan, review, report, apply, diff
# - Reads config from pyproject.toml
# ==========================================

import argparse
import os
import sys
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python < 3.11
  # Python 3.11+

# ------------------------------------------
# CONFIG LOADING
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
# SEVERITY COMPARISON
# ------------------------------------------
SEVERITY_ORDER = {
    "CRITICAL": 3,
    "WARNING": 2,
    "INFO": 1
}

def severity_exceeded(issue_severity, threshold):
    return SEVERITY_ORDER[issue_severity] >= SEVERITY_ORDER[threshold]


# ------------------------------------------
# COMMAND HANDLERS
# ------------------------------------------
def run_scan(config):
    print("🔍 Running static analysis (Module 1)...")
    os.system("module1.py")
    print("✅ Scan completed")


def run_review(config):
    print("🤖 Running AI review (Module 2)...")
    os.system("module2.py")
    print("✅ Review completed")


def run_report(config):
    print("📊 Generating validation metrics (Module 3)...")
    os.system("module3.py")
    print("✅ Report generated")


def run_apply(config):
    print("🛠️ Auto-fix is currently limited to safe fixes")
    print("ℹ️ (Feature placeholder for future extension)")


def run_diff(config):
    print("📄 Diff view not implemented yet")
    print("ℹ️ (Placeholder command)")


# ------------------------------------------
# MAIN CLI
# ------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="CodeGuard – AI-assisted Code Review Tool"
    )

    parser.add_argument(
        "command",
        choices=["scan", "review", "report", "apply", "diff"],
        help="Command to run"
    )

    args = parser.parse_args()
    config = load_config()

    print("⚙️ Configuration loaded:")
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
