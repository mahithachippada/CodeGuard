import os

from analyzers.python_analyzer import analyze_python
from analyzers.javascript_analyzer import analyze_javascript
from analyzers.java_analyzer import analyze_java
from analyzers.c_analyzer import analyze_c
from analyzers.cpp_analyzer import analyze_cpp


def detect_language(file_path):
    ext = os.path.splitext(file_path)[1]

    if ext == ".py":
        return "python"
    if ext == ".js":
        return "javascript"
    if ext == ".java":
        return "java"
    if ext == ".c":
        return "c"
    if ext in [".cpp", ".cc", ".cxx"]:
        return "cpp"

    return "unknown"


def analyze_file(file_path):
    language = detect_language(file_path)

    if language == "python":
        return analyze_python(file_path)
    elif language == "javascript":
        return analyze_javascript(file_path)
    elif language == "java":
        return analyze_java(file_path)
    elif language == "c":
        return analyze_c(file_path)
    elif language == "cpp":
        return analyze_cpp(file_path)
    else:
        return {
            "file": file_path,
            "language": "unknown",
            "issues": [],
            "complexity": 0
        }
