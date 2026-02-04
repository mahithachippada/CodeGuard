def analyze_cpp(file_path):
    issues = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read().lower()

    if "using namespace std" in code:
        issues.append({
            "issue": "Avoid using namespace std",
            "severity": "INFO"
        })

    if "new " in code and "delete" not in code:
        issues.append({
            "issue": "Possible memory leak (new without delete)",
            "severity": "WARNING"
        })

    if "strcpy(" in code:
        issues.append({
            "issue": "Unsafe strcpy usage",
            "severity": "CRITICAL"
        })

    return {
        "file": file_path,
        "language": "cpp",
        "issues": issues,
        "complexity": code.count("if") + 1
    }
