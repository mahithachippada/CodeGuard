# ==========================================
# Module 2: AI Review Engine (Auto-Run)
# ==========================================
# - Automatically reads module1_report.json
# - Generates human-like review feedback
# - Ranks issues by severity
# - Groups similar issues intelligently
# - Saves module2_ai_review.json
# - NO API required
# - NO external runner code
# ==========================================

import json
import os
from collections import defaultdict

# ------------------------------------------
# CONFIG
# ------------------------------------------
MODULE1_INPUT_FILE = "module1_report.json"
MODULE2_OUTPUT_FILE = "module2_ai_review.json"

# ------------------------------------------
# Severity Ranking (Higher priority first)
# ------------------------------------------
SEVERITY_ORDER = {
    "CRITICAL": 1,
    "WARNING": 2,
    "INFO": 3
}

# ------------------------------------------
# Human-like Explanation Templates
# ------------------------------------------
EXPLANATION_TEMPLATES = {
    "Missing Docstring": {
        "review": (
            "This function does not include a docstring, which reduces readability "
            "and makes the code harder to understand."
        ),
        "suggestion": (
            "Add a concise docstring describing the function, its parameters, "
            "and its return value."
        ),
        "auto_fix_safe": True
    },

    "Missing Type Hints": {
        "review": (
            "The function lacks type annotations, making static analysis and "
            "debugging more difficult."
        ),
        "suggestion": (
            "Add appropriate Python type hints to function parameters and return values."
        ),
        "auto_fix_safe": False
    },

    "Long Function": {
        "review": (
            "This function is quite long, which increases complexity and makes "
            "the code harder to maintain."
        ),
        "suggestion": (
            "Consider splitting this function into smaller, well-defined functions."
        ),
        "auto_fix_safe": False
    },

    "Too Many Parameters": {
        "review": (
            "The function accepts many parameters, which can reduce clarity and "
            "increase the chance of misuse."
        ),
        "suggestion": (
            "Group related parameters into a structure or reduce the parameter count."
        ),
        "auto_fix_safe": False
    },

    "Class Naming": {
        "review": (
            "The class name does not follow Python naming conventions, which "
            "reduces consistency."
        ),
        "suggestion": (
            "Rename the class using PascalCase to follow Python style guidelines."
        ),
        "auto_fix_safe": False
    },

    "Hardcoded Secret": {
        "review": (
            "Sensitive information appears to be hardcoded in the source code, "
            "which is a serious security vulnerability."
        ),
        "suggestion": (
            "Remove hardcoded secrets and use environment variables or a secure "
            "secret management system."
        ),
        "auto_fix_safe": False
    },

    "Unsafe Code Execution": {
        "review": (
            "Dynamic code execution is detected, which may lead to serious "
            "security vulnerabilities."
        ),
        "suggestion": (
            "Avoid using eval() or exec(). Use safer alternatives instead."
        ),
        "auto_fix_safe": False
    }
}

# ------------------------------------------
# Explain a Single Issue
# ------------------------------------------
def explain_issue(issue):
    issue_type = issue["type"]
    template = EXPLANATION_TEMPLATES.get(issue_type)

    if template:
        return {
            "type": issue_type,
            "severity": issue["severity"],
            "review": template["review"],
            "suggestion": template["suggestion"],
            "auto_fix_recommended": template["auto_fix_safe"]
        }

    # Fallback for unknown issues
    return {
        "type": issue_type,
        "severity": issue["severity"],
        "review": issue["message"],
        "suggestion": "Review this issue and apply an appropriate fix.",
        "auto_fix_recommended": False
    }

# ------------------------------------------
# MAIN AI REVIEW LOGIC
# ------------------------------------------
def run_ai_review_engine():
    if not os.path.exists(MODULE1_INPUT_FILE):
        print(f"❌ Input file not found: {MODULE1_INPUT_FILE}")
        return

    with open(MODULE1_INPUT_FILE, "r", encoding="utf-8") as f:
        module1_data = json.load(f)

    final_reviews = []

    for file_report in module1_data:
        issues = file_report.get("issues", [])

        # Sort issues by severity
        issues.sort(key=lambda x: SEVERITY_ORDER[x["severity"]])

        # Group issues by type (intelligence)
        grouped = defaultdict(list)
        for issue in issues:
            grouped[issue["type"]].append(issue)

        reviews = []

        for issue_type, group in grouped.items():
            base_issue = group[0]
            explanation = explain_issue(base_issue)

            explanation["occurrences"] = len(group)

            if len(group) > 1:
                explanation["review"] += (
                    f" This issue appears {len(group)} times in the file."
                )

            reviews.append(explanation)

        final_reviews.append({
            "file": file_report["file"],
            "total_issues": len(issues),
            "reviews": reviews
        })

    # Save output
    with open(MODULE2_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_reviews, f, indent=4)

    print("✅ Module 2 AI Review completed")
    print(f"📄 Output saved to: {MODULE2_OUTPUT_FILE}")

# ------------------------------------------
# AUTO-RUN (IMPORTANT PART YOU ASKED FOR)
# ------------------------------------------
if __name__ == "__main__":
    run_ai_review_engine()
