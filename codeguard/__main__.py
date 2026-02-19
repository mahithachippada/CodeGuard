import click
import json
import os
from codeguard.module1 import analyze_file
from codeguard.module2 import generate_ai_review
from codeguard.module3 import compute_metrics

@click.group()
def main():
    """CodeGuard CLI - AI-Powered Multi-Language Code Review Tool"""
    pass

# -------------------------------
# Command: scan
# -------------------------------
@main.command()
@click.argument("path", type=click.Path(exists=True))
def scan(path):
    """Scan files for issues."""
    results = analyze_file(path)
    click.echo(json.dumps(results, indent=2))

# -------------------------------
# Command: review
# -------------------------------
@main.command()
@click.argument("path", type=click.Path(exists=True))
def review(path):
    """AI-powered review using Ollama."""
    static_results = [{"file": path, "issues": analyze_file(path)}]
    ai_results = generate_ai_review(static_results, use_llm=True)
    click.echo(json.dumps(ai_results, indent=2))

# -------------------------------
# Command: apply
# -------------------------------
import os
import json
import click
from codeguard.module1 import analyze_file
from codeguard.module2 import generate_ai_review

@main.command()
@click.argument("path", type=click.Path(exists=True))
def apply(path):
    """Auto-fix code using AI suggestions + Black."""

    # Step 1: Run static analysis
    static_results = [{"file": path, "issues": analyze_file(path)}]

    # Step 2: Get AI review suggestions
    ai_results = generate_ai_review(static_results, use_llm=True)

    applied = False

    # Step 3: Apply AI fixes (only corrected code, not explanation)
    for review in ai_results[0]["reviews"]:
        suggestion = review.get("suggestion")
        if suggestion:
            with open(path, "w", encoding="utf-8") as f:
                f.write(suggestion)   # only corrected code
            click.echo(f"[APPLY] Applied AI fix for issue type: {review['type']}")
            applied = True

    # Step 4: Always run Black afterwards
    if path.endswith(".py"):
        os.system(f"black {path}")
        click.echo("[APPLY] Auto-fix complete (AI + Black).")
    else:
        click.echo("[APPLY] Only Python files are supported for auto-fix right now.")

    if not applied:
        click.echo("[APPLY] No AI fix applied (suggestion was not code).")



# -------------------------------
# Command: report
# -------------------------------
@main.command()
@click.argument("path", type=click.Path(exists=True))
def report(path):
    """Generate metrics report."""
    static_results = [{"file": path, "issues": analyze_file(path)}]
    metrics = compute_metrics(static_results)

    click.echo("\n=== File Metrics ===")
    click.echo(json.dumps(metrics["files"], indent=2))

    click.echo("\n=== Project Summary ===")
    click.echo(json.dumps(metrics["summary"], indent=2))

# -------------------------------
# Command: diff
# -------------------------------
@main.command()
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
def diff(file1, file2):
    """Compare two files line by line."""
    with open(file1, encoding="utf-8", errors="ignore") as f1, open(file2, encoding="utf-8", errors="ignore") as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    click.echo(f"--- {file1}")
    click.echo(f"+++ {file2}")
    for i, (l1, l2) in enumerate(zip(lines1, lines2), start=1):
        if l1 != l2:
            click.echo(f"Line {i}:\n- {l1.strip()}\n+ {l2.strip()}")

if __name__ == "__main__":
    main()
