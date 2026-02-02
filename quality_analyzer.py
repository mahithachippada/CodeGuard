# ==========================================
# Rule-Based Code Quality Analyzer
# Milestone-2 | Corrected Final Version
# ==========================================

import ast
import json
import os
import re
import csv
import sys

# ------------------------------------------
# 1. FILES TO ANALYZE (Python files only)
# ------------------------------------------
files = [
    "error.py"
]

EXCLUDE_FILES = [
    "quality_report.json",
    "quality_report.csv"
]

file_summaries = []
critical_found = False

# ------------------------------------------
# 2. ANALYZE EACH FILE
# ------------------------------------------
for file_path in files:

    filename = os.path.basename(file_path)
    if filename in EXCLUDE_FILES:
        continue

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    code_lower = code.lower()
    issues = []

    # --------------------------------------
    # PARSE CODE SAFELY
    # --------------------------------------
    try:
        tree = ast.parse(code)
    except SyntaxError:
        issues.append({
            "issue": "Syntax error in file",
            "severity": "CRITICAL"
        })
        tree = None

    # --------------------------------------
    # AST ANALYSIS & COMPLEXITY
    # --------------------------------------
    class CodeAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.complexity = 1

        def visit_If(self, node):
            self.complexity += 1
            self.generic_visit(node)

        def visit_For(self, node):
            self.complexity += 1
            self.generic_visit(node)

        def visit_While(self, node):
            self.complexity += 1
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            if not ast.get_docstring(node):
                issues.append({
                    "issue": f"Missing docstring in function '{node.name}'",
                    "severity": "INFO"
                })

            if len(node.args.args) > 5:
                issues.append({
                    "issue": f"Function '{node.name}' has too many parameters",
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

    analyzer = CodeAnalyzer()
    if tree:
        analyzer.visit(tree)

    # --------------------------------------
    # SECURITY ISSUE DETECTION
    # --------------------------------------
    secret_patterns = [
        r"password\s*=",
        r"api_key\s*=",
        r"apikey\s*=",
        r"secret\s*=",
        r"access_key\s*=",
        r"token\s*="
    ]

    if any(re.search(p, code_lower) for p in secret_patterns):
        issues.append({
            "issue": "Hardcoded secret or credential detected",
            "severity": "CRITICAL"
        })

    if "eval(" in code_lower or "exec(" in code_lower:
        issues.append({
            "issue": "Unsafe eval/exec usage detected",
            "severity": "CRITICAL"
        })

    # --------------------------------------
    # COMPLEXITY WARNING
    # --------------------------------------
    if analyzer.complexity > 10:
        issues.append({
            "issue": "High cyclomatic complexity",
            "severity": "WARNING"
        })

    # --------------------------------------
    # QUALITY SCORE
    # --------------------------------------
    def calculate_quality_score(issues):
        score = 100
        for issue in issues:
            if issue["severity"] == "CRITICAL":
                score -= 20
            elif issue["severity"] == "WARNING":
                score -= 10
            elif issue["severity"] == "INFO":
                score -= 5
        return max(score, 0)

    quality_score = calculate_quality_score(issues)

    # --------------------------------------
    # MAINTAINABILITY INDEX (MI)
    # --------------------------------------
    loc = len(code.splitlines())

    def calculate_mi(loc, complexity):
        return max(0, 100 - (5 * complexity) - (0.5 * loc))

    mi = calculate_mi(loc, analyzer.complexity)

    # --------------------------------------
    # CHECK CRITICAL ISSUES
    # --------------------------------------
    if any(i["severity"] == "CRITICAL" for i in issues):
        critical_found = True

    # --------------------------------------
    # FILE SUMMARY
    # --------------------------------------
    file_summaries.append({
        "file": file_path,
        "quality_score": quality_score,
        "maintainability_index": round(mi, 2),
        "cyclomatic_complexity": analyzer.complexity,
        "issue_count": len(issues),
        "issues": issues
    })

# ------------------------------------------
# PROJECT SUMMARY
# ------------------------------------------
project_summary = {
    "total_files": len(file_summaries),
    "project_quality_score": round(
        sum(f["quality_score"] for f in file_summaries) / len(file_summaries), 2
    ) if file_summaries else 0,
    "project_maintainability_index": round(
        sum(f["maintainability_index"] for f in file_summaries) / len(file_summaries), 2
    ) if file_summaries else 0
}

# ------------------------------------------
# REPORT GENERATION
# ------------------------------------------
final_report = {
    "files": file_summaries,
    "project_summary": project_summary
}

with open("quality_report.json", "w", encoding="utf-8") as f:
    json.dump(final_report, f, indent=4)

with open("quality_report.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["File", "Quality Score", "MI", "Complexity", "Issue Count"])
    for summary in file_summaries:
        writer.writerow([
            summary["file"],
            summary["quality_score"],
            summary["maintainability_index"],
            summary["cyclomatic_complexity"],
            summary["issue_count"]
        ])

# ------------------------------------------
# FINAL RESULT FOR PRE-COMMIT
# ------------------------------------------
print("Code analysis completed")
print("Reports generated: quality_report.json, quality_report.csv")

if critical_found:
    print("Commit blocked: Critical issues detected")
    sys.exit(1)
else:
    print("No critical issues found. Commit allowed")
    sys.exit(0)
