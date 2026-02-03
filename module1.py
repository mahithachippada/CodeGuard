# ==========================================
# Module 1: Rule-Based Code Quality Analyzer
# ==========================================

import ast
import os
import json
import csv

# ------------------------------------------
# FILES TO ANALYZE (EDIT THIS)
# ------------------------------------------
files = [
    
    "error.py"
]

# ------------------------------------------
# ISSUE MODEL
# ------------------------------------------
class Issue:
    def __init__(self, issue_type, line, message, severity):
        self.issue_type = issue_type
        self.line = line
        self.message = message
        self.severity = severity

    def to_dict(self):
        return {
            "type": self.issue_type,
            "line": self.line,
            "message": self.message,
            "severity": self.severity
        }

# ------------------------------------------
# COMPLEXITY
# ------------------------------------------
class ComplexityVisitor(ast.NodeVisitor):
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

# ------------------------------------------
# CODE ANALYZER
# ------------------------------------------
class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.functions = []
        self.classes = []
        self.issues = []
        self.function_complexity = {}

    def visit_Import(self, node):
        for n in node.names:
            self.imports.append(n.name)

    def visit_ImportFrom(self, node):
        for n in node.names:
            self.imports.append(f"{node.module}.{n.name}")

    def visit_FunctionDef(self, node):
        start = node.lineno
        end = node.end_lineno or start
        length = end - start + 1

        counter = ComplexityVisitor()
        counter.visit(node)
        self.function_complexity[node.name] = counter.complexity

        self.functions.append({
            "name": node.name,
            "start_line": start,
            "end_line": end,
            "length": length,
            "complexity": counter.complexity
        })

        if not ast.get_docstring(node):
            self.issues.append(Issue(
                "Missing Docstring", start,
                f"Function '{node.name}' has no docstring", "INFO"
            ))

        if not node.returns or any(a.annotation is None for a in node.args.args):
            self.issues.append(Issue(
                "Missing Type Hints", start,
                f"Function '{node.name}' lacks type hints", "INFO"
            ))

        if length > 50:
            self.issues.append(Issue(
                "Long Function", start,
                f"Function '{node.name}' is too long ({length} lines)", "WARNING"
            ))

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.classes.append({
            "name": node.name,
            "line": node.lineno
        })

        if not node.name[0].isupper():
            self.issues.append(Issue(
                "Class Naming", node.lineno,
                f"Class '{node.name}' should use PascalCase", "WARNING"
            ))

        self.generic_visit(node)

# ------------------------------------------
# CRITICAL SECURITY RULES
# ------------------------------------------
SECURITY_KEYWORDS = [
    "password", "passwd", "pwd",
    "api_key", "apikey", "secret", "token"
]

def detect_security_issues(code):
    issues = []
    lower = code.lower()

    for key in SECURITY_KEYWORDS:
        if key in lower:
            issues.append(Issue(
                "Hardcoded Secret", 0,
                f"Possible hardcoded secret detected: '{key}'", "CRITICAL"
            ))

    if "eval(" in lower or "exec(" in lower:
        issues.append(Issue(
            "Unsafe Code Execution", 0,
            "Use of eval() or exec() detected", "CRITICAL"
        ))

    return issues

# ------------------------------------------
# MAIN ANALYSIS
# ------------------------------------------
file_summaries = []

for file_path in files:

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        tree = ast.parse(code)
    except SyntaxError:
        file_summaries.append({
            "file": file_path,
            "issues": [{
                "type": "Syntax Error",
                "line": 0,
                "message": "Syntax error in file",
                "severity": "CRITICAL"
            }]
        })
        continue

    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    issues = []
    issues.extend(analyzer.issues)
    issues.extend(detect_security_issues(code))

    file_summaries.append({
        "file": file_path,
        "imports": analyzer.imports,
        "functions": analyzer.functions,
        "classes": analyzer.classes,
        "complexity": analyzer.function_complexity,
        "issues": [i.to_dict() for i in issues]
    })

# ------------------------------------------
# SAVE JSON REPORT (DETAILED)
# ------------------------------------------
with open("module1_report.json", "w", encoding="utf-8") as f:
    json.dump(file_summaries, f, indent=4)

# ------------------------------------------
# SAVE CSV REPORT (SUMMARY)
# ------------------------------------------
with open("module1_report.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["File", "Total Issues", "INFO", "WARNING", "CRITICAL"])

    for summary in file_summaries:
        info = warning = critical = 0
        for issue in summary.get("issues", []):
            if issue["severity"] == "INFO":
                info += 1
            elif issue["severity"] == "WARNING":
                warning += 1
            elif issue["severity"] == "CRITICAL":
                critical += 1

        writer.writerow([
            summary["file"],
            len(summary.get("issues", [])),
            info,
            warning,
            critical
        ])

print(" Module 1 analysis completed")
print("Reports generated: module1_report.json, module1_report.csv")
