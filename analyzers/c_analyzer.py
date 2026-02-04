def analyze_c(file_path):
    issues = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read().lower()

    if "gets(" in code:
        issues.append({
            "issue": "Use of gets() is unsafe",
            "severity": "CRITICAL"
        })

    if "strcpy(" in code:
        issues.append({
            "issue": "Use of strcpy() may cause buffer overflow",
            "severity": "WARNING"
        })

    if "malloc(" in code and "free(" not in code:
        issues.append({
            "issue": "Possible memory leak detected",
            "severity": "WARNING"
        })

    return {
        "file": file_path,
        "language": "c",
        "issues": issues,
        "complexity": code.count("if") + 1
    }
