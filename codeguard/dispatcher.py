import os
from codeguard.analyzer import analyze_python_file, analyze_js_file

def analyze_file(path):
    static_results = []
    if os.path.isfile(path):
        files_to_check = [path]
    else:
        files_to_check = []
        for root, _, files in os.walk(path):
            for fname in files:
                if fname.endswith((".py", ".js")):
                    files_to_check.append(os.path.join(root, fname))

    for file_path in files_to_check:
        if file_path.endswith(".py"):
            static_results.append(analyze_python_file(file_path))
        elif file_path.endswith(".js"):
            static_results.append(analyze_js_file(file_path))

    return static_results
