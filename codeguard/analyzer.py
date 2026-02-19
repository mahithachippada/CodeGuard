import re

def analyze_python_file(file_path):
    """Analyze a Python file and return issues."""
    issues = []
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        if len(line) > 80:
            issues.append({"severity": "WARNING", "category": "Style", "line": i})
        if "TODO" in line:
            issues.append({"severity": "INFO", "category": "Documentation", "line": i})
        if re.match(r"^\s*def ", line) and '"""' not in line:
            issues.append({"severity": "ERROR", "category": "Documentation", "line": i})

    complexity = sum(1 for line in lines if "if" in line or "for" in line or "while" in line)

    return {
        "file": file_path,
        "issues": issues,
        "complexity": complexity,
        "lines": len(lines)
    }


def analyze_js_file(file_path):
    """Analyze a JavaScript file and return issues."""
    issues = []
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        if len(line) > 100:
            issues.append({"severity": "WARNING", "category": "Style", "line": i})
        if "TODO" in line:
            issues.append({"severity": "INFO", "category": "Documentation", "line": i})

    complexity = sum(1 for line in lines if "if" in line or "for" in line or "while" in line)

    return {
        "file": file_path,
        "issues": issues,
        "complexity": complexity,
        "lines": len(lines)
    }
