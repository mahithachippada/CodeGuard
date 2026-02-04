import json
from collections import defaultdict
import os
import streamlit
# ------------------------------------------
# KNOWLEDGE BASE (Fallback Templates)
# ------------------------------------------
ISSUE_KB = {
    "hardcoded secret": {
        "review": "Sensitive credentials are hardcoded directly in the source code.",
        "suggestion": "Remove hardcoded credentials and use environment variables or a secret manager.",
        "auto_fix": False
    },
    "eval": {
        "review": "Use of eval()/exec() allows execution of arbitrary code at runtime.",
        "suggestion": "Avoid eval()/exec(). Use safer alternatives such as explicit function calls.",
        "auto_fix": False
    },
    "missing docstring": {
        "review": "This function does not contain a docstring.",
        "suggestion": "Add a docstring explaining the purpose, parameters, and return value.",
        "auto_fix": True
    },
    "type hint": {
        "review": "The function lacks type annotations.",
        "suggestion": "Add appropriate type hints to parameters and return values.",
        "auto_fix": False
    },
    "complexity": {
        "review": "The code has high cyclomatic complexity.",
        "suggestion": "Refactor into smaller, simpler functions.",
        "auto_fix": False
    },
    "naming": {
        "review": "Naming convention does not follow style guidelines.",
        "suggestion": "Rename identifiers to follow language-specific conventions.",
        "auto_fix": False
    },
    "debug": {
        "review": "Debug/logging statements found in code.",
        "suggestion": "Remove debug prints/logs before deploying.",
        "auto_fix": True
    },
    "memory": {
        "review": "Possible memory leak due to improper memory management.",
        "suggestion": "Ensure all allocated memory is properly released.",
        "auto_fix": False
    },
    "buffer overflow": {
        "review": "Unsafe functions may cause buffer overflow vulnerabilities.",
        "suggestion": "Replace unsafe functions with safer alternatives and validate input sizes.",
        "auto_fix": False
    }
}

# ------------------------------------------
# CLASSIFICATION LOGIC
# ------------------------------------------
def classify_issue(issue_text: str):
    text = issue_text.lower()
    if any(k in text for k in ["password", "secret", "token", "api key", "apikey"]):
        return "hardcoded secret"
    if "eval" in text or "exec" in text:
        return "eval"
    if "docstring" in text:
        return "missing docstring"
    if "type" in text:
        return "type hint"
    if "complexity" in text:
        return "complexity"
    if "class" in text or "naming" in text:
        return "naming"
    if "console.log" in text or "debug" in text or "print" in text:
        return "debug"
    if "malloc" in text or "free" in text or "memory" in text:
        return "memory"
    if "strcpy" in text or "gets" in text:
        return "buffer overflow"
    return "unknown"

# ------------------------------------------
# OPTIONAL LLM INTEGRATION
# ------------------------------------------
def llm_generate_suggestion(issue_text, code_snippet=None):
    """
    Replace this stub with actual LLM API call (e.g., OpenAI, Azure OpenAI).
    For now, it simulates dynamic suggestions.
    """
    return {
        "review": f"LLM suggests: {issue_text} may reduce code quality.",
        "suggestion": f"LLM recommends refactoring or fixing: {issue_text}.",
        "auto_fix_recommended": False
    }

# ------------------------------------------
# MAIN REVIEW FUNCTION
# ------------------------------------------
def generate_ai_review(static_results, use_llm=False):
    final_output = []

    for file_result in static_results:
        grouped_issues = defaultdict(list)
        for issue in file_result["issues"]:
            grouped_issues[issue["issue"]].append(issue)

        reviews = []
        for issue_text, occurrences in grouped_issues.items():
            key = classify_issue(issue_text)
            template = ISSUE_KB.get(key)

            if use_llm:
                # Try LLM first
                llm_response = llm_generate_suggestion(issue_text)
                if llm_response:
                    reviews.append({
                        "type": issue_text,
                        "severity": occurrences[0]["severity"],
                        "review": llm_response["review"],
                        "suggestion": llm_response["suggestion"],
                        "auto_fix_recommended": llm_response["auto_fix_recommended"],
                        "occurrences": len(occurrences)
                    })
                    continue  # skip fallback if LLM worked

            # Fallback to template
            if template:
                reviews.append({
                    "type": issue_text,
                    "severity": occurrences[0]["severity"],
                    "review": template["review"],
                    "suggestion": template["suggestion"],
                    "auto_fix_recommended": template["auto_fix"],
                    "occurrences": len(occurrences)
                })
            else:
                reviews.append({
                    "type": issue_text,
                    "severity": occurrences[0]["severity"],
                    "review": "Issue detected that may affect quality or security.",
                    "suggestion": "Review code and apply best practices.",
                    "auto_fix_recommended": False,
                    "occurrences": len(occurrences)
                })

        final_output.append({
            "file": file_result["file"],
            "reviews": reviews
        })

    return final_output

# ------------------------------------------
# FEEDBACK LOOP (ACCEPT/REJECT)
# ------------------------------------------
def log_feedback(file, issue_type, decision, log_file="feedback_log.json"):
    feedback_entry = {
        "file": file,
        "issue": issue_type,
        "decision": decision  # "accepted" or "rejected"
    }

    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        data.append(feedback_entry)

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Could not log feedback: {e}")
