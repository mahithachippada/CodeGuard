import streamlit as st
import os
import time
import json
import plotly.express as px

from codeguard.dispatcher import analyze_file
from codeguard.module2 import generate_ai_review
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
theme = st.sidebar.radio("Theme", ["🌙 Dark", "☀️ Light"])
if theme == "🌙 Dark":
    bg_css = "linear-gradient(135deg,#0f2027,#203a43,#2c5364)"
    text_color = "#ddd"
else:
    bg_css = "#f5f5f5"
    text_color = "#222"

st.markdown(f"""
<style>
html, body {{
    background: {bg_css};
    font-family: 'Segoe UI', sans-serif;
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

LANG_EXT = {"Python": ".py", "JavaScript": ".js", "Java": ".java", "C": ".c", "C++": ".cpp"}
uploaded_files, manual_code, manual_language = [], "", None

if input_mode == "📂 Upload Files":
    uploaded_files = st.sidebar.file_uploader("Upload source files", type=["py","js","java","c","cpp"], accept_multiple_files=True)
else:
    manual_language = st.sidebar.selectbox("Select language", list(LANG_EXT.keys()))
    manual_code = st.sidebar.text_area("Paste code here", height=260)

run_btn = st.sidebar.button("🚀 Run CodeGuard")

# ==================================================
# RUN ANALYSIS
# ==================================================
# ==================================================
# RUN ANALYSIS
# ==================================================
if run_btn:
    file_paths = []
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)

    # Save uploaded files permanently
    for f in uploaded_files:
        path = os.path.join(upload_dir, f.name)
        with open(path, "wb") as out:
            out.write(f.read())
        file_paths.append(path)

    # Save manual code if provided
    if manual_code.strip():
        ext = LANG_EXT[manual_language]
        manual_path = os.path.join(upload_dir, f"manual_input{ext}")
        with open(manual_path, "w", encoding="utf-8") as f:
            f.write(manual_code)
        file_paths.append(manual_path)

    if not file_paths:
        st.warning("⚠️ Please provide code input.")
    else:
        bar = st.progress(0)
        for i in range(0,101,10):
            time.sleep(0.04)
            bar.progress(i)

        # 👉 This is the block you asked about
        static_results = [analyze_file(p) for p in file_paths]
        ai_results = generate_ai_review(static_results)
        metrics = compute_metrics(static_results)

        st.session_state.static = static_results
        st.session_state.ai = ai_results
        st.session_state.metrics = metrics

        st.success("✅ Analysis completed successfully!")

        # Debug lines to inspect raw results
        st.write("DEBUG static results:", st.session_state.static)
        st.write("DEBUG ai results:", st.session_state.ai)


# ==================================================
# FILTERS
# ==================================================
st.markdown("### 🔎 Filters")
f1, f2 = st.columns(2)
severity_filter = f1.multiselect("Severity", ["CRITICAL","WARNING","INFO"], default=["CRITICAL","WARNING","INFO"])
language_filter = f2.multiselect("Language", ["python","javascript","java","c","cpp"], default=["python","javascript","java","c","cpp"])

# ==================================================
# TABS
# ==================================================
tabs = st.tabs(["🐞 Static Issues","🤖 AI Review","📊 Metrics"])

# ---------------- STATIC ISSUES ----------------
with tabs[0]:
    if "static" not in st.session_state:
        st.info("Run analysis to see issues.")
    else:
        for f in st.session_state.static:
            if f["language"] not in language_filter:
                continue
            st.markdown(f"### 📄 `{os.path.basename(f['file'])}`")
            st.markdown(f"<span class='lang-tag'>{f['language'].upper()}</span>", unsafe_allow_html=True)
            shown = False
            for issue in f["issues"]:
                if issue["severity"] not in severity_filter:
                    continue
                shown = True
                with st.expander(f"{issue['severity']} - {issue['issue']}"):
                    st.markdown(f"<span class='badge {issue['severity']}'> {issue['severity']} </span><br><b>{issue['issue']}</b>", unsafe_allow_html=True)
            if not shown:
                st.info("No issues match current filters.")

# ---------------- AI REVIEW ----------------
with tabs[1]:
    if "ai" not in st.session_state:
        st.info("Run analysis to see AI review.")
    else:
        for f in st.session_state.ai:
            st.markdown(f"### 📄 `{os.path.basename(f['file'])}`")
            for r in f["reviews"]:
                if r["severity"] not in severity_filter:
                    continue
                with st.expander(f"{r['severity']} - {r['review']}"):
                    st.markdown(f"<span class='badge {r['severity']}'> {r['severity']} </span>", unsafe_allow_html=True)
                    st.write("🧠 What’s wrong?")
                    st.write(r["review"])
                    st.write("💡 How to fix")
                    st.write(r["suggestion"])
                    st.write(f"Occurrences: {r['occurrences']}")

                    # Side-by-side diff view
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Original Code")
                        try:
                            st.code(open(f.get("file","")).read(), language=f.get("language","python"))
                        except Exception:
                            st.warning("Original file not available.")
                    with col2:
                        st.subheader("AI Suggested Fix")
                        st.code(r["suggestion"], language=f.get("language","python"))

# ---------------- METRICS ----------------
with tabs[2]:
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

        fig = px.bar(
            metrics_data,
            x=[os.path.basename(f["file"]) for f in metrics_data],
            y=[f["issue_count"] for f in metrics_data],
            color=[f["quality_score"] for f in metrics_data],
            labels={"x": "File", "y": "Issue Count", "color": "Quality Score"},
                        title="📊 Issues per File vs Quality Score"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Download metrics JSON
        st.download_button(
            "📥 Download Metrics JSON",
            data=json.dumps(st.session_state.metrics, indent=2),
            file_name="module3_metrics.json",
            mime="application/json"
        )

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
