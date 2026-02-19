import streamlit as st
import os
import time
import json
import plotly.express as px
import plotly.graph_objects as go
import zipfile
from io import BytesIO
import difflib
import subprocess

from codeguard.module1 import analyze_file
from codeguard.module2 import generate_ai_review, log_feedback
from codeguard.module3 import compute_metrics

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="CodeGuard",
    page_icon="🛡️",
    layout="wide"
)

# ==================================================
# THEME TOGGLE
# ==================================================
theme = st.sidebar.radio("Theme", ["🌙 Dark", "☀️ Light", "🌈 Rainbow"])
if theme == "🌙 Dark":
    bg_css = "linear-gradient(135deg,#0f2027,#203a43,#2c5364)"
    text_color = "#ddd"
elif theme == "☀️ Light":
    bg_css = "#f5f5f5"
    text_color = "#222"
elif theme == "🌈 Rainbow":
    bg_css = "linear-gradient(90deg,#ff6a00,#ee0979,#00c6ff,#0072ff)"
    text_color = "#fff"

st.markdown(f"""
<style>
html, body {{
    background: {bg_css};
    font-family: 'Poppins', sans-serif;
    color: {text_color};
}}
.title {{
    font-size: 48px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg,#ff6a00,#ee0979,#00c6ff,#0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.subtitle {{
    text-align:center;
    color:{text_color};
    font-size:18px;
    margin-bottom:25px;
}}
.badge {{
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    display: inline-block;
    margin-bottom: 10px;
}}
.CRITICAL {{background: linear-gradient(90deg,#ff0844,#ff512f);}}
.WARNING {{background: linear-gradient(90deg,#f7971e,#ffd200); color:#222;}}
.INFO {{background: linear-gradient(90deg,#00c6ff,#0072ff);}}
.metric {{
    background: rgba(255,255,255,0.18);
    border-radius: 14px;
    padding: 16px;
    text-align:center;
    font-weight:700;
    color:black;
}}
.metric:hover {{ transform: scale(1.05); }}
.lang-tag {{
    display:inline-block;
    padding:6px 12px;
    border-radius:12px;
    background:rgba(255,255,255,0.25);
    font-size:12px;
    font-weight:700;
    margin-bottom:8px;
}}
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown('<div class="title">🛡️ CodeGuard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Multi-Language Code Review Platform</div>', unsafe_allow_html=True)
st.divider()

# ==================================================
# SIDEBAR INPUT
# ==================================================
st.sidebar.header("⚙️ Input")
input_mode = st.sidebar.radio("Choose input method", ["📂 Upload Files", "✍️ Paste Code"])

LANG_EXT = {
    "Python": ".py", "JavaScript": ".js", "TypeScript": ".ts",
    "Java": ".java", "Kotlin": ".kt", "C": ".c", "C++": ".cpp",
    "Go": ".go", "Rust": ".rs", "PHP": ".php",
    "HTML": ".html", "CSS": ".css", "Shell": ".sh", "Ruby": ".rb"
}
uploaded_files, manual_code, manual_language = [], "", None

if input_mode == "📂 Upload Files":
    uploaded_files = st.sidebar.file_uploader(
        "Upload source files",
        type=list(ext.strip('.') for ext in LANG_EXT.values()),
        accept_multiple_files=True
    )
else:
    manual_language = st.sidebar.selectbox("Select language", list(LANG_EXT.keys()))
    manual_code = st.sidebar.text_area("Paste code here", height=260)

run_btn = st.sidebar.button("🚀 Run CodeGuard")
reset_btn = st.sidebar.button("🔄 Reset")

if reset_btn:
    st.session_state.clear()
    st.experimental_rerun()

# ==================================================
# RUN ANALYSIS + EXECUTION
# ==================================================
def run_code(file_path, language):
    try:
        if language.lower() == "python":
            result = subprocess.run(["python", file_path], capture_output=True, text=True, timeout=5)
            return result.stdout, result.stderr
        elif language.lower() == "javascript":
            result = subprocess.run(["node", file_path], capture_output=True, text=True, timeout=5)
            return result.stdout, result.stderr
        elif language.lower() == "java":
            compile_result = subprocess.run(["javac", file_path], capture_output=True, text=True, timeout=5)
            if compile_result.returncode != 0:
                return "", compile_result.stderr
            class_name = os.path.splitext(os.path.basename(file_path))[0]
            result = subprocess.run(["java", class_name], capture_output=True, text=True, timeout=5)
            return result.stdout, result.stderr
        elif language.lower() in ["c", "c++"]:
            exe_file = os.path.splitext(file_path)[0]
            compiler = "gcc" if language.lower() == "c" else "g++"
            compile_result = subprocess.run([compiler, file_path, "-o", exe_file], capture_output=True, text=True, timeout=5)
            if compile_result.returncode != 0:
                return "", compile_result.stderr
            result = subprocess.run([exe_file], capture_output=True, text=True, timeout=5)
            return result.stdout, result.stderr
        elif language.lower() == "html":
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=400, scrolling=True)
            return "Rendered HTML above.", ""
        else:
            return "", f"Execution for {language} not supported yet."
    except Exception as e:
        return "", str(e)


def detect_language(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".py":
        return "python"
    elif ext == ".js":
        return "javascript"
    elif ext in [".c", ".cpp"]:
        return "c"
    elif ext == ".java":
        return "java"
    else:
        return "unknown"


def auto_apply_fixes(file_path, issues, ai_results):
    import json
    applied_code = None
    from codeguard.module2 import ollama_generate

    prompt = f"""
Analyze these issues in {os.path.basename(file_path)}.
1. Explain the problems clearly for humans.
2. Then output ONLY the corrected code (no explanation, no markdown fences).
Issues:
{json.dumps(issues, indent=2)}
"""
    llm_response = ollama_generate("Security/Style/Docs", code_snippet=open(file_path).read(), model="phi3")

    # Extract code only
    code_fix = None
    if "```" in llm_response:
        parts = llm_response.split("```")
        code_fix = parts[1].replace("python", "").replace("```", "").strip()
    else:
        code_fix = llm_response.strip()

    if code_fix and "def " in code_fix:  # crude check for Python code
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_fix)
        os.system(f"black {file_path}")
        applied_code = code_fix

    return applied_code

def generate_ai_review_batched(static_results, use_llm=True):
    from codeguard.module2 import ollama_generate
    ai_results = []

    for f in static_results:
        issues = f["issues"]
        if not issues:
            ai_results.append({"file": f["file"], "reviews": []})
            continue

        # Stronger prompt to force explanation first
        prompt = f"""
Analyze the following issues in {os.path.basename(f['file'])}.
For each issue:
- First, write a clear explanation of what’s wrong (plain text, no code).
- Then output ONLY the corrected code inside a code block.
Issues:
{json.dumps(issues, indent=2)}
"""

        llm_response = ollama_generate(
            "Security/Style/Docs",
            code_snippet=open(f["file"], "r", encoding="utf-8").read(),
            model="phi3"
        )

        explanation, suggestion = llm_response.strip(), ""

        if "```" in llm_response:
            parts = llm_response.split("```")
            explanation = parts[0].strip()
            suggestion = parts[1].replace("python", "").strip()
        else:
            explanation = llm_response.strip()
            suggestion = ""

        # Fallback if explanation is empty
        if not explanation:
            explanation = "AI generated fixes but did not provide a detailed explanation."

        # Map severity based on static issues
        sev = "CRITICAL" if any(i.get("severity") == "CRITICAL" for i in issues) else "INFO"

        reviews = [{
            "severity": sev,
            "type": "batched_fix",
            "review": explanation,
            "suggestion": suggestion,
            "occurrences": len(issues)
        }]

        ai_results.append({"file": f["file"], "reviews": reviews})

    return ai_results


# ==================================================
# MAIN RUN BLOCK
# ==================================================
if run_btn:
    file_paths = []
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)

    for f in uploaded_files:
        path = os.path.join(upload_dir, f.name)
        with open(path, "wb") as out:
            out.write(f.read())
        file_paths.append(path)

    if manual_code.strip():
        ext = LANG_EXT[manual_language]
        manual_path = os.path.join(upload_dir, f"manual_input{ext}")
        with open(manual_path, "w", encoding="utf-8") as f:
            f.write(manual_code)
        file_paths.append(manual_path)

    if not file_paths:
        st.warning("⚠️ Please provide code input.")
    else:
        with st.spinner("⚡ CodeGuard is analyzing your code..."):
            time.sleep(2)

        static_results = [
            {
                "file": p,
                "issues": analyze_file(p),
                "language": detect_language(p),
                "lines": sum(1 for _ in open(p, "r", encoding="utf-8"))
            }
            for p in file_paths
        ]

        ai_results = generate_ai_review_batched(static_results, use_llm=True)
        metrics = compute_metrics(static_results)
        outputs = {}
        for f in static_results:
            outputs[f["file"]] = run_code(f["file"], f["language"])

        st.session_state.static = static_results
        st.session_state.ai = ai_results
        st.session_state.metrics = metrics
        st.session_state.outputs = outputs

        if all(len(f["issues"]) == 0 for f in static_results):
            st.success("🎉 Congratulations! No issues found.")
            st.balloons()
            st.snow()
            st.markdown("<h3 style='text-align:center;'>🌸 Your code is clean and beautiful! 🌸</h3>", unsafe_allow_html=True)
        else:
            st.success("✅ Analysis completed successfully!")

# ==================================================
# FILTERS
# ==================================================
st.markdown("### 🔎 Filters")
f1, f2 = st.columns(2)

severity_filter = f1.multiselect(
    "Severity",
    ["CRITICAL", "ERROR", "WARNING", "INFO","AI"],
    default=["CRITICAL", "ERROR", "WARNING", "INFO","AI"]
)

language_filter = f2.multiselect(
    "Language",
    [l.lower() for l in LANG_EXT.keys()],
    default=[l.lower() for l in LANG_EXT.keys()]
)

# ==================================================
# TABS
# ==================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🐞 Static Issues",
    "🤖 AI Review",
    "📊 Metrics",
    "🖥️ Program Output",
    "⚡ Apply Fixes"
])

# ---------------- STATIC ISSUES ----------------
with tab1:
    if "static" not in st.session_state:
        st.info("Run analysis to see issues.")
    else:
        for f in st.session_state.static:
            if f["language"].lower() not in language_filter:
                continue
            st.markdown(f"### 📄 `{os.path.basename(f['file'])}`")
            st.markdown(f"<span class='lang-tag'>{f['language'].upper()}</span>", unsafe_allow_html=True)
            shown = False
            for issue in f["issues"]:
                sev = issue.get("severity", "INFO") if isinstance(issue, dict) else "INFO"
                iss = issue.get("issue", issue.get("category", "Unknown")) if isinstance(issue, dict) else str(issue)
                line = issue.get("line", "N/A") if isinstance(issue, dict) else "N/A"
                code = issue.get("code") if isinstance(issue, dict) else None
                if sev not in severity_filter:
                    continue
                shown = True
                with st.expander(f"{sev} - {iss}"):
                    st.markdown(f"<span class='badge {sev}'> {sev} </span><br><b>{iss}</b>", unsafe_allow_html=True)
                    st.write(f"Line: {line}")
                    if code:
                        st.code(code, language=f["language"])
            if not shown:
                st.info("No issues match current filters.")

# ---------------- AI REVIEW ----------------
with tab2:
    if "ai" not in st.session_state:
        st.info("Run analysis to see AI review.")
    else:
        for f in st.session_state.ai:
            st.markdown(f"### 📄 `{os.path.basename(f['file'])}`")
            for r in f["reviews"]:
                if r["severity"] not in severity_filter:
                    continue
                with st.expander(f"{r['severity']} - {r['type']}"):
                    st.markdown(f"<span class='badge {r['severity']}'> {r['severity']} </span>", unsafe_allow_html=True)
                    st.write("🧠 What’s wrong?")
                    st.write(r["review"])
                    st.write("💡 How to fix")
                    st.write(r["suggestion"])
                    st.write(f"Occurrences: {r['occurrences']}")
                    # Diff highlighting
                    try:
                        with open(f["file"], "r", encoding="utf-8") as orig_file:
                            original_code = orig_file.read()
                        diff = difflib.unified_diff(
                            original_code.splitlines(),
                            r["suggestion"].splitlines(),
                            fromfile="Original",
                            tofile="AI Fix",
                            lineterm=""
                        )
                        st.code("\n".join(diff), language=f.get("language","python"))
                    except Exception:
                        st.warning("Diff view not available.")
                    # Feedback buttons
                    colf1, colf2 = st.columns(2)
                    if colf1.button(f"✅ Accept {r['type']}", key=f"{f['file']}_{r['type']}_accept"):
                        log_feedback(f["file"], r["type"], "accepted")
                        st.success("Feedback logged: accepted")
                    if colf2.button(f"❌ Reject {r['type']}", key=f"{f['file']}_{r['type']}_reject"):
                        log_feedback(f["file"], r["type"], "rejected")
                        st.warning("Feedback logged: rejected")

# ---------------- METRICS ----------------
with tab3:
    if "metrics" not in st.session_state:
        st.info("Run analysis to see metrics.")
    else:
        metrics_data = st.session_state.metrics["files"]
        for f in metrics_data:
            st.markdown(f"### 📄 `{os.path.basename(f['file'])}`")
            cols = st.columns(4)
            cols[0].markdown(f"<div class='metric'>Quality<br>{f['quality_score']}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div class='metric'>MI<br>{f['maintainability_index']}</div>", unsafe_allow_html=True)
            cols[2].markdown(f"<div class='metric'>Complexity<br>{f['cyclomatic_complexity']}</div>", unsafe_allow_html=True)
            cols[3].markdown(f"<div class='metric'>Issues<br>{f['issue_count']}</div>", unsafe_allow_html=True)
        # Charts
        fig = px.bar(
            metrics_data,
            x=[os.path.basename(f["file"]) for f in metrics_data],
            y=[f["issue_count"] for f in metrics_data],
            color=[f["quality_score"] for f in metrics_data],
            labels={"x": "File", "y": "Issue Count", "color": "Quality Score"},
            title="📊 Issues per File vs Quality Score"
        )
        st.plotly_chart(fig, use_container_width=True)
        severity_totals = {}
        for f in metrics_data:
            for sev, count in f["severity_breakdown"].items():
                severity_totals[sev] = severity_totals.get(sev, 0) + count
        fig_pie = px.pie(
            names=list(severity_totals.keys()),
            values=list(severity_totals.values()),
            title="Severity Distribution Across Project"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        compliance = st.session_state.metrics["summary"]["compliance_rate"]
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=compliance,
            title={'text': "Compliance Rate (%)"},
            gauge={'axis': {'range': [0, 100]}}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

# ---------------- PROGRAM OUTPUT ----------------
with tab4:
    if "outputs" not in st.session_state:
        st.info("Run analysis to see program output.")
    else:
        for file, out in st.session_state.outputs.items():
            st.markdown(f"### 📄 `{os.path.basename(file)}`")
            if out[0]:
                st.success("Program Output:")
                st.code(out[0], language="text")
            if out[1]:
                st.error("Errors:")
                st.code(out[1], language="text")

# ---------------- APPLY FIXES ----------------
with tab5:
    if "static" in st.session_state and "ai" in st.session_state:
        if st.button("⚡ Apply AI Fixes"):
            for f in st.session_state.static:
                applied_code = auto_apply_fixes(f["file"], f["issues"], st.session_state.ai)
                if applied_code:
                    st.success(f"✅ Applied AI fix to {os.path.basename(f['file'])}")
                    # Show diff before vs after
                    with open(f["file"], "r", encoding="utf-8") as orig_file:
                        new_code = orig_file.read()
                    diff = difflib.unified_diff(
                        applied_code.splitlines(),
                        new_code.splitlines(),
                        fromfile="Before",
                        tofile="After",
                        lineterm=""
                    )
                    st.code("\n".join(diff), language=f["language"])
                else:
                    st.warning(f"No AI fix applied for {os.path.basename(f['file'])}")


# ==================================================
# DOWNLOAD REPORTS (SIDEBAR)
# ==================================================
st.sidebar.header("📥 Export Reports")
if "static" in st.session_state:
    st.sidebar.download_button(
        "Download Static Issues JSON",
        data=json.dumps(st.session_state.static, indent=2),
        file_name="module1_report.json",
        mime="application/json"
    )
if "ai" in st.session_state:
    st.sidebar.download_button(
        "Download AI Review JSON",
        data=json.dumps(st.session_state.ai, indent=2),
        file_name="ai_review.json",
        mime="application/json"
    )
if "metrics" in st.session_state:
    st.sidebar.download_button(
        "Download Metrics JSON",
        data=json.dumps(st.session_state.metrics, indent=2),
        file_name="module3_metrics.json",
        mime="application/json"
    )

    # Unified ZIP export
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr("module1_report.json", json.dumps(st.session_state.static, indent=2))
        z.writestr("ai_review.json", json.dumps(st.session_state.ai, indent=2))
        z.writestr("module3_metrics.json", json.dumps(st.session_state.metrics, indent=2))
    st.sidebar.download_button(
        "📦 Download All Reports (ZIP)",
        data=buffer.getvalue(),
        file_name="codeguard_reports.zip",
        mime="application/zip"
    )
