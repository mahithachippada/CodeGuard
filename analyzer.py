# ==========================================
# CLI Code Quality Analyzer
# Module 4: CLI & Configuration
# ==========================================

import ast
import argparse
import json
import os
import sys

# -------------------------------
# CONFIG (can later move to pyproject.toml)
# -------------------------------
SEVERITY_LIMIT = "CRITICAL"
EXCLUDED_PATHS = [".git", ".github", "__pycache__"]

SEVERITY_WEIGHT = {
    "INFO": 5,
    "WARNING": 10,
    "CRITICAL": 20
}

# -------------------------------
# CORE ANALYSIS LOGIC
# -------------------------------
def analyze_file(file_path):
    issues = []
    complexity = 1

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
    except Exception:
        return None

    code_lower = code.lower()

    try:
        tree = ast.parse(code)
    except SyntaxError:
        issues.append({
            "issue": "Syntax error in file",
            "severity": "CRITICAL"
        })
        return build_report(file_path, issues, complexity, code)

    class Analyzer(ast.NodeVisitor):
        def visit_If(self, node):
            nonlocal complexity
            complexity += 1
            self.generic_visit(node)

        def visit_For(self, node):
            nonlocal complexity
            complexity += 1
            self.generic_visit(node)

        def visit_While(self, node):
            nonlocal complexity
            complexity += 1
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            if not ast.get_docstring(node):
                issues.append({
                    "issue": f"Missing docstring in function '{node.name}'",
                    "severity": "INFO"
                })
            if len(node.args.args) > 5:
                issues.append({
                    "issue": f"Too many parameters in function '{node.name}'",
                    "severity": "WARNING"
                })
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            if not node.name[0].isupper():
                issues.append({
                    "issue": f"Class '{node.name}' should use PascalCase",
                    "severity": "WARNING"
                })
            self.generic_visit(node)

    Analyzer().visit(tree)

    # -------- SECURITY CHECKS --------
    secrets = ["password", "api_key", "apikey", "secret", "token", "access_key"]
    for key in secrets:
        if f"{key} =" in code_lower:
            issues.append({
                "issue": f"Hardcoded {key} detected",
                "severity": "CRITICAL"
            })

    if "eval(" in code_lower or "exec(" in code_lower:
        issues.append({
            "issue": "Unsafe eval/exec usage",
            "severity": "CRITICAL"
        })

    return build_report(file_path, issues, complexity, code)


def build_report(file_path, issues, complexity, code):
    score = 100
    for i in issues:
        score -= SEVERITY_WEIGHT[i["severity"]]

    score = max(score, 0)
    loc = len(code.splitlines())
    mi = max(0, 100 - (5 * complexity) - (0.5 * loc))

    return {
        "file": file_path,
        "quality_score": score,
        "maintainability_index": round(mi, 2),
        "cyclomatic_complexity": complexity,
        "issue_count": len(issues),
        "issues": issues
    }

# -------------------------------
# CLI COMMANDS
# -------------------------------
def scan(files):
    results = []
    critical_found = False

    for file in files:
        if not file.endswith(".py"):
            continue
        if any(x in file for x in EXCLUDED_PATHS):
            continue

        report = analyze_file(file)
        if report:
            results.append(report)
            if any(i["severity"] == "CRITICAL" for i in report["issues"]):
                critical_found = True

    with open("quality_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print("Scan completed. Report saved to quality_report.json")

    if critical_found:
        print("❌ Critical issues found")
        sys.exit(1)
    else:
        print("✅ No critical issues")
        sys.exit(0)


def review(file):
    report = analyze_file(file)
    if not report:
        print("Could not analyze file")
        return

    print(f"\nReview for {file}")
    for issue in report["issues"]:
        print(f"[{issue['severity']}] {issue['issue']}")


def report():
    if not os.path.exists("quality_report.json"):
        print("No report found. Run scan first.")
        return

    with open("quality_report.json") as f:
        data = json.load(f)

    for f in data:
        print(f"\nFile: {f['file']}")
        print("Score:", f["quality_score"])
        print("MI:", f["maintainability_index"])
        print("Issues:", f["issue_count"])


# -------------------------------
# MAIN ENTRY
# -------------------------------
def main():
    parser = argparse.ArgumentParser(description="Code Quality Analyzer CLI")
    sub = parser.add_subparsers(dest="command")

    scan_cmd = sub.add_parser("scan")
    scan_cmd.add_argument("files", nargs="+")

    review_cmd = sub.add_parser("review")
    review_cmd.add_argument("file")

    sub.add_parser("report")

    args = parser.parse_args()

    if args.command == "scan":
        scan(args.files)
    elif args.command == "review":
        review(args.file)
    elif args.command == "report":
        report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()