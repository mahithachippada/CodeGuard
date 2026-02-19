# ==========================================
# Module 3: Metrics & Validation
# ==========================================

def compute_metrics(static_results):
    severity_weights = {"CRITICAL": 20, "ERROR": 15, "WARNING": 10, "INFO": 5}
    files = []
    total_score = 0
    total_issues = 0
    category_counts = {}

    for file in static_results:
        score = 100
        severity_counts = {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}

        # Deduct points based on severity
        for issue in file.get("issues", []):
            if isinstance(issue, dict):
                sev = issue.get("severity", "INFO").upper()
                cat = issue.get("category", "General")
            else:
                # If analyzer returned a string, treat as INFO
                sev = "INFO"
                cat = "General"

            if sev not in severity_counts:
                severity_counts[sev] = 0
            severity_counts[sev] += 1
            score -= severity_weights.get(sev, 5)

            # Track category distribution
            category_counts[cat] = category_counts.get(cat, 0) + 1

        score = max(score, 0)
        total_score += score
        total_issues += len(file.get("issues", []))

        # Weighted maintainability index
        maintainability_index = max(
            0,
            100 - (file.get("complexity", 0) * 5)
                - (severity_counts["CRITICAL"] * 10
                   + severity_counts["ERROR"] * 7
                   + severity_counts["WARNING"] * 5
                   + severity_counts["INFO"] * 2)
        )

        # Extra metrics
        avg_severity = (
            (severity_counts["CRITICAL"] * 4 +
             severity_counts["ERROR"] * 3 +
             severity_counts["WARNING"] * 2 +
             severity_counts["INFO"] * 1) / max(len(file.get("issues", [])), 1)
        )
        issue_density = round(len(file.get("issues", [])) / max(file.get("lines", 100), 100) * 100, 2)

        files.append({
            "file": file.get("file", "unknown"),
            "quality_score": score,
            "cyclomatic_complexity": file.get("complexity", 0),
            "issue_count": len(file.get("issues", [])),
            "severity_breakdown": severity_counts,
            "maintainability_index": maintainability_index,
            "average_severity": round(avg_severity, 2),
            "issue_density_per_100_lines": issue_density,
            "passed_quality_gate": score >= 70 and maintainability_index >= 50
        })

    # Project-level summary
    project_summary = {
        "average_quality_score": round(total_score / len(static_results), 2) if static_results else 0,
        "average_maintainability_index": round(sum(f["maintainability_index"] for f in files) / len(files), 2) if files else 0,
        "total_issues": total_issues,
        "files_analyzed": len(static_results),
        "compliance_rate": round(
            sum(1 for f in files if f["passed_quality_gate"]) / len(files) * 100, 2
        ) if files else 0,
        "worst_file": min(files, key=lambda f: f["quality_score"])["file"] if files else None,
        "best_file": max(files, key=lambda f: f["quality_score"])["file"] if files else None,
        "category_distribution": category_counts
    }

    return {
        "files": files,
        "summary": project_summary
    }
