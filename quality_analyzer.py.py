# ==========================================
# Rule-Based Code Quality Analyzer
# Milestone-2
# ==========================================

import ast
import json
import os
import csv

# ------------------------------------------
# 1. LIST OF PYTHON FILES TO ANALYZE
# ------------------------------------------
files = [
    "py.py"
]

file_summaries = []

# ------------------------------------------
# 2. ANALYZE EACH FILE
# ------------------------------------------
for file_path in files:

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    code_lower = code.lower()
    issues = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        issues.append({
            "issue": "Syntax error in file",
            "severity": "CRITICAL"
        })
        tree = None

    # --------------------------------------
    # 3. AST ANALYSIS & COMPLEXITY
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
    # 4. SECURITY ISSUE DETECTION
    # --------------------------------------
    if "password" in code_lower:
        issues.append({
            "issue": "Hardcoded password detected",
            "severity": "CRITICAL"
        })

    if "api_key" in code_lower or "apikey" in code_lower:
        issues.append({
            "issue": "Hardcoded API key detected",
            "severity": "CRITICAL"
        })

    if any(x in code_lower for x in ["token", "secret", "access_key"]):
        issues.append({
            "issue": "Hardcoded secret or token detected",
            "severity": "CRITICAL"
        })

    if "eval(" in code_lower or "exec(" in code_lower:
        issues.append({
            "issue": "Unsafe eval/exec usage detected",
            "severity": "CRITICAL"
        })

    # --------------------------------------
    # 5. COMPLEXITY WARNING
    # --------------------------------------
    if analyzer.complexity > 10:
        issues.append({
            "issue": "High cyclomatic complexity",
            "severity": "WARNING"
        })

    # --------------------------------------
    # 6. QUALITY SCORE CALCULATION
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
    # 7. MAINTAINABILITY INDEX (MI)
    # --------------------------------------
    loc = len(code.splitlines())

    def calculate_mi(loc, complexity):
        return max(0, 100 - (5 * complexity) - (0.5 * loc))

    mi = calculate_mi(loc, analyzer.complexity)

    # --------------------------------------
    # 8. FILE-LEVEL AGGREGATION
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
# 9. PROJECT-LEVEL AGGREGATION
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
# 10. REPORT GENERATION (JSON + CSV)
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
# 12. PRE-COMMIT DECISION LOGIC
# ------------------------------------------
critical_found = False

for file in file_summaries:
    for issue in file["issues"]:
        if issue["severity"] == "CRITICAL":
            critical_found = True

if critical_found:
    print("❌ Commit blocked: Critical issues detected")
    exit(1)
else:
    print("✅ No critical issues found. Commit allowed")
    exit(0)


# ------------------------------------------
# 13. FINAL OUTPUT
# ------------------------------------------
print("✅ Code analysis completed successfully")
print("📄 Reports generated: quality_report.json, quality_report.csv")
print(f"📁 Files analyzed: {len(file_summaries)}")
