def analyze_java(file_path):
    issues = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if "System.out.println" in code:
        issues.append({
            "issue": "Debug print statement found",
            "severity": "INFO"
        })

    if "public static void main" not in code:
        issues.append({
            "issue": "No main method detected",
            "severity": "WARNING"
        })

    if "password" in code.lower():
        issues.append({
            "issue": "Hardcoded credential detected",
            "severity": "CRITICAL"
        })

    return {
        "file": file_path,
        "language": "java",
        "issues": issues,
        "complexity": code.count("if") + 1
    }
