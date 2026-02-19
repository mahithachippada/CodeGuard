import os
import ast

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1
        self.max_depth = 0
        self.current_depth = 0

    def generic_visit(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        super().generic_visit(node)
        self.current_depth -= 1

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)


def analyze_python(file_path):
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception:
        return [{"issue": "Unable to read file", "severity": "CRITICAL", "category": "io"}]

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [{"issue": f"Syntax error: {e}", "severity": "CRITICAL", "category": "syntax"}]

    visitor = ComplexityVisitor()
    visitor.visit(tree)
    complexity = visitor.complexity

    if complexity > 10:
        issues.append({
            "issue": "High cyclomatic complexity",
            "severity": "WARNING",
            "line": None,
            "category": "complexity"
        })

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            length = node.body[-1].lineno - node.lineno + 1
            if length > 50:
                issues.append({
                    "issue": f"Function '{node.name}' too long ({length} lines)",
                    "severity": "WARNING",
                    "line": node.lineno,
                    "category": "maintainability"
                })

            if not ast.get_docstring(node):
                issues.append({
                    "issue": f"Missing docstring in function '{node.name}'",
                    "severity": "INFO",
                    "line": node.lineno,
                    "category": "documentation"
                })

            if not node.returns:
                issues.append({
                    "issue": f"Missing return type hint in function '{node.name}'",
                    "severity": "INFO",
                    "line": node.lineno,
                    "category": "type hint"
                })

        if isinstance(node, ast.ClassDef):
            if not node.name[0].isupper():
                issues.append({
                    "issue": f"Class '{node.name}' should use PascalCase",
                    "severity": "WARNING",
                    "line": node.lineno,
                    "category": "naming"
                })

    lowered = code.lower()
    if any(k in lowered for k in ["password", "api_key", "apikey", "secret", "token"]):
        issues.append({
            "issue": "Possible hardcoded secret detected",
            "severity": "CRITICAL",
            "line": None,
            "category": "security"
        })

    if "eval(" in lowered or "exec(" in lowered:
        issues.append({
            "issue": "Unsafe use of eval/exec detected",
            "severity": "CRITICAL",
            "line": None,
            "category": "security"
        })

    return issues


def analyze_file(file_path):
    """Wrapper that dispatches to the right analyzer based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".py":
        return analyze_python(file_path)
    else:
        return [{"issue": "Language not supported yet", "severity": "INFO", "category": "general"}]
