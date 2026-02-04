def analyze_javascript(file_path):
    issues = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read().lower()

    if "eval(" in code:
        issues.append({
            "issue": "Use of eval() detected",
            "severity": "CRITICAL"
        })

    if "var " in code:
        issues.append({
            "issue": "Use of var instead of let/const",
            "severity": "WARNING"
        })

    if "console.log" in code:
        issues.append({
            "issue": "Debug console.log found",
            "severity": "INFO"
        })

    return {
        "file": file_path,
        "language": "javascript",
        "issues": issues,
        "complexity": code.count("if") + 1
    }
