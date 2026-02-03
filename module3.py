# ==========================================
# Module 3: Validation & Metrics
# ==========================================
# - Reads Module 1 analysis report
# - Computes quality score per file
# - Computes maintainability index
# - Computes complexity metrics
# - Generates JSON and CSV reports
# ==========================================

import json
import csv
import os

# ------------------------------------------
# INPUT / OUTPUT FILES
# ------------------------------------------
MODULE1_REPORT = "module1_report.json"

OUTPUT_JSON = "module3_metrics.json"
OUTPUT_CSV = "module3_metrics.csv"

# ------------------------------------------
# SCORING RULES
# ------------------------------------------
SEVERITY_PENALTY = {
    "CRITICAL": 20,
    "WARNING": 10,
    "INFO": 5
}

# ------------------------------------------
# METRIC FUNCTIONS
# ------------------------------------------
def calculate_quality_score(issues):
    score = 100
    for issue in issues:
        score -= SEVERITY_PENALTY.get(issue["severity"], 0)
    return max(score, 0)


def calculate_loc(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return len(f.readlines())
    except:
        return 0


def calculate_maintainability_index(loc, complexity):
    return max(0, round(100 - (5 * complexity) - (0.5 * loc), 2))


# ------------------------------------------
# MAIN METRICS ENGINE
# ------------------------------------------
def run_metrics_engine():

    if not os.path.exists(MODULE1_REPORT):
        print("❌ module1_report.json not found")
        return

    with open(MODULE1_REPORT, "r", encoding="utf-8") as f:
        module1_data = json.load(f)

    file_metrics = []

    for file_report in module1_data:
        file_path = file_report["file"]
        issues = file_report.get("issues", [])
        complexity_map = file_report.get("complexity", {})

        total_complexity = sum(complexity_map.values()) if complexity_map else 0
        max_complexity = max(complexity_map.values()) if complexity_map else 0
        avg_complexity = round(
            total_complexity / len(complexity_map), 2
        ) if complexity_map else 0

        loc = calculate_loc(file_path)
        quality_score = calculate_quality_score(issues)
        mi = calculate_maintainability_index(loc, total_complexity)

        file_metrics.append({
            "file": file_path,
            "lines_of_code": loc,
            "issue_count": len(issues),
            "quality_score": quality_score,
            "maintainability_index": mi,
            "total_complexity": total_complexity,
            "max_function_complexity": max_complexity,
            "avg_function_complexity": avg_complexity
        })

    # --------------------------------------
    # PROJECT LEVEL SUMMARY
    # --------------------------------------
    project_summary = {
        "total_files": len(file_metrics),
        "average_quality_score": round(
            sum(f["quality_score"] for f in file_metrics) / len(file_metrics), 2
        ) if file_metrics else 0,
        "average_maintainability_index": round(
            sum(f["maintainability_index"] for f in file_metrics) / len(file_metrics), 2
        ) if file_metrics else 0
    }

    # --------------------------------------
    # SAVE JSON REPORT
    # --------------------------------------
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "files": file_metrics,
            "project_summary": project_summary
        }, f, indent=4)

    # --------------------------------------
    # SAVE CSV REPORT
    # --------------------------------------
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "File", "LOC", "Issues",
            "Quality Score", "Maintainability Index",
            "Total Complexity", "Max Complexity", "Avg Complexity"
        ])

        for m in file_metrics:
            writer.writerow([
                m["file"],
                m["lines_of_code"],
                m["issue_count"],
                m["quality_score"],
                m["maintainability_index"],
                m["total_complexity"],
                m["max_function_complexity"],
                m["avg_function_complexity"]
            ])

    print("✅ Module 3 metrics generated successfully")
    print(f"📄 Reports: {OUTPUT_JSON}, {OUTPUT_CSV}")


# ------------------------------------------
# AUTO RUN
# ------------------------------------------
if __name__ == "__main__":
    run_metrics_engine()
