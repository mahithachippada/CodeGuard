# ==========================================
# Module 3: Metrics & Validation
# ==========================================

def compute_metrics(static_results):
    files = []
    total_score = 0
    total_issues = 0

    for file in static_results:
        score = 100
        severity_counts = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}

        # Deduct points based on severity
        for issue in file["issues"]:
            severity_counts[issue["severity"]] += 1
            if issue["severity"] == "CRITICAL":
                score -= 20
            elif issue["severity"] == "WARNING":
                score -= 10
            else:
                score -= 5

        score = max(score, 0)
        total_score += score
        total_issues += len(file["issues"])

        # Weighted maintainability index
        maintainability_index = max(
            0,
            100 - (file["complexity"] * 5)
                - (severity_counts["CRITICAL"] * 10
                   + severity_counts["WARNING"] * 5
                   + severity_counts["INFO"] * 2)
        )

        files.append({
            "file": file["file"],
            "quality_score": score,
            "cyclomatic_complexity": file["complexity"],
            "issue_count": len(file["issues"]),
            "severity_breakdown": severity_counts,
            "maintainability_index": maintainability_index,
            "passed_quality_gate": score >= 70 and maintainability_index >= 50
        })

    # Project-level summary
    project_summary = {
        "average_quality_score": round(total_score / len(static_results), 2) if static_results else 0,
        "total_issues": total_issues,
        "files_analyzed": len(static_results),
        "compliance_rate": round(
            sum(1 for f in files if f["passed_quality_gate"]) / len(files) * 100, 2
        ) if files else 0
    }

    return {
        "files": files,
        "summary": project_summary
    }
