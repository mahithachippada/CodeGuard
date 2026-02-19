import json
import os
import requests
from collections import defaultdict

# ------------------------------------------
# KNOWLEDGE BASE (Fallback Templates)
# ------------------------------------------
ISSUE_KB = {
    "documentation": {
        "category": "Documentation",
        "review": "This code is missing proper documentation.",
        "suggestion": "Add docstrings and comments to explain functionality.",
        "auto_fix": True
    },
    "style": {
        "category": "Style",
        "review": "Code style does not follow conventions.",
        "suggestion": "Fix spacing, naming, and line length issues.",
        "auto_fix": False
    },
    "security": {
        "category": "Security",
        "review": "Potential security issue detected.",
        "suggestion": "Avoid hardcoded secrets, eval/exec, and unsafe functions.",
        "auto_fix": False
    }
}

# ------------------------------------------
# CLASSIFICATION LOGIC
# ------------------------------------------
def classify_issue(category: str):
    text = category.lower()
    if "doc" in text:
        return "documentation"
    if "style" in text:
        return "style"
    if "security" in text:
        return "security"
    return "general"

# ------------------------------------------
# OLLAMA INTEGRATION
# ------------------------------------------
def ollama_generate(issue_text, code_snippet=None, model="phi3"):
    prompt = f"""
You are a code reviewer. First, explain the issue clearly for humans.
Issue: {issue_text}

Then output the corrected code, wrapped in triple backticks:
```python
{code_snippet or ''}

"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt},
            stream=True
        )
        response.raise_for_status()

        output = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    output += data.get("response", "")
                except json.JSONDecodeError:
                    continue

        return output.strip()
    except Exception as e:
        return f"[Ollama error: {e}]"

# ------------------------------------------
# MAIN REVIEW FUNCTION
# ------------------------------------------
def generate_ai_review(static_results, use_llm=True, model="phi3"):
    final_output = []

    for file_result in static_results:
        if not isinstance(file_result, dict):
            continue

        issues = file_result.get("issues", [])
        grouped_issues = defaultdict(list)

        for issue in issues:
            if isinstance(issue, dict):
                issue_type = issue.get("category", "unknown")
                grouped_issues[issue_type].append(issue)
            else:
                grouped_issues[str(issue)].append({"severity": "INFO", "category": str(issue)})

        reviews = []
        for issue_text, occurrences in grouped_issues.items():
            key = classify_issue(issue_text)
            template = ISSUE_KB.get(key)

            review_entry = {
                "type": issue_text,
                "severity": occurrences[0].get("severity", "INFO"),
                "occurrences": len(occurrences),
                "line": occurrences[0].get("line"),
                "code": occurrences[0].get("code"),
                "category": issue_text
            }

            if use_llm:
                code_snippet = occurrences[0].get("code", None)
                llm_response = ollama_generate(issue_text, code_snippet, model=model)

                # Split explanation and code
                explanation, code_fix = llm_response, None
                if "```" in llm_response:
                    parts = llm_response.split("```")
                    explanation = parts[0].strip()
                    code_fix = parts[1].replace("python", "").replace("```", "").strip()

                review_entry.update({
                    "review": f"Issue: {issue_text}\n{explanation}",   # human explanation
                    "suggestion": code_fix or (template["suggestion"] if template else "Review code and apply best practices."),  # code only
                    "auto_fix_recommended": template["auto_fix"] if template else False
                })
            else:
                if template:
                    review_entry.update({
                        "review": f"Issue: {issue_text}\nWhy: {template['review']}",
                        "suggestion": f"Fix: {template['suggestion']}",
                        "auto_fix_recommended": template["auto_fix"]
                    })
                else:
                    review_entry.update({
                        "review": f"Issue: {issue_text}\nWhy: Generic issue detected.",
                        "suggestion": "Fix: Review code and apply best practices.",
                        "auto_fix_recommended": False
                    })

            reviews.append(review_entry)

        final_output.append({
            "file": file_result.get("file", "unknown"),
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
        "decision": decision
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

# ------------------------------------------
# DEMO RUNNER
# ------------------------------------------
if __name__ == "__main__":
    static_results = [
        {
            "file": "example.py",
            "issues": [
                {"severity": "ERROR", "category": "Documentation", "line": 5, "code": "def add(a,b): return a+b"},
                {"severity": "WARNING", "category": "Style", "line": 10, "code": "print('debug')"},
                {"severity": "ERROR", "category": "Security", "line": 15, "code": "API_KEY = '12345'"}
            ]
        }
    ]

    results = generate_ai_review(static_results, use_llm=True, model="phi3")
    print(json.dumps(results, indent=2))
