import streamlit as st
import tempfile
import os
import time

from dispatcher import analyze_file
from module2 import generate_ai_review
from module3 import compute_metrics

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="CodeGuard",
    page_icon="🛡️",
    layout="wide"
)

# ==================================================
# UI THEME (GLASS + GRADIENT + ANIMATION)
# ==================================================
st.markdown("""
<style>
html, body {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    font-family: 'Segoe UI', sans-serif;
}

@keyframes fadeUp {
    from {opacity:0; transform:translateY(20px);}
    to {opacity:1; transform:translateY(0);}
}

.title {
    font-size: 48px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg,#ff6a00,#ee0979,#00c6ff,#0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: fadeUp 1s ease;
}

.subtitle {
    text-align:center;
    color:#ddd;
    font-size:18px;
    margin-bottom:25px;
}

.glass {
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    animation: fadeUp .5s ease;
}

.glass:hover {
    transform: scale(1.01);
}

.badge {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    display: inline-block;
    margin-bottom: 10px;
}

.CRITICAL {
    background: linear-gradient(90deg,#ff0844,#ff512f);
    box-shadow: 0 0 12px #ff0844;
}

.WARNING {
    background: linear-gradient(90deg,#f7971e,#ffd200);
    color:#222;
}

.INFO {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
}

.metric {
    background: rgba(255,255,255,0.18);
    border-radius: 14px;
    padding: 16px;
    text-align:center;
    font-weight:700;
    color:black;
    box-shadow: inset 0 0 10px rgba(255,255,255,0.1);
}

.lang-tag {
    display:inline-block;
    padding:6px 12px;
    border-radius:12px;
    background:rgba(255,255,255,0.25);
    font-size:12px;
    font-weight:700;
    margin-bottom:8px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown('<div class="title">🛡️ CodeGuard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-Powered Multi-Language Code Review Platform</div>',
    unsafe_allow_html=True
)
st.divider()

# ==================================================
# SIDEBAR INPUT
# ==================================================
st.sidebar.header("⚙️ Input")

input_mode = st.sidebar.radio(
    "Choose input method",
    ["📂 Upload Files", "✍️ Paste Code"]
)

LANG_EXT = {
    "Python": ".py",
    "JavaScript": ".js",
    "Java": ".java",
    "C": ".c",
    "C++": ".cpp"
}

uploaded_files = []
manual_code = ""
manual_language = None

if input_mode == "📂 Upload Files":
    uploaded_files = st.sidebar.file_uploader(
        "Upload source files",
        type=["py","js","java","c","cpp"],
        accept_multiple_files=True
    )
else:
    manual_language = st.sidebar.selectbox(
        "Select language",
        list(LANG_EXT.keys())
    )
    manual_code = st.sidebar.text_area(
        "Paste code here",
        height=260
    )

run_btn = st.sidebar.button("🚀 Run CodeGuard")

# ==================================================
# RUN ANALYSIS
# ==================================================
if run_btn:
    file_paths = []

    with tempfile.TemporaryDirectory() as tmp:
        for f in uploaded_files:
            path = os.path.join(tmp, f.name)
            with open(path, "wb") as out:
                out.write(f.read())
            file_paths.append(path)

        if manual_code.strip():
            ext = LANG_EXT[manual_language]
            manual_path = os.path.join(tmp, f"manual_input{ext}")
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

            static_results = [analyze_file(p) for p in file_paths]
            ai_results = generate_ai_review(static_results)
            metrics = compute_metrics(static_results)

            st.session_state.static = static_results
            st.session_state.ai = ai_results
            st.session_state.metrics = metrics

            st.success("✅ Analysis completed")

# ==================================================
# FILTERS
# ==================================================
st.markdown("### 🔎 Filters")
f1, f2 = st.columns(2)

with f1:
    severity_filter = st.multiselect(
        "Severity",
        ["CRITICAL","WARNING","INFO"],
        default=["CRITICAL","WARNING","INFO"]
    )

with f2:
    language_filter = st.multiselect(
        "Language",
        ["python","javascript","java","c","cpp"],
        default=["python","javascript","java","c","cpp"]
    )

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
            st.markdown(
                f"<span class='lang-tag'>{f['language'].upper()}</span>",
                unsafe_allow_html=True
            )

            shown = False
            for issue in f["issues"]:
                if issue["severity"] not in severity_filter:
                    continue
                shown = True
                st.markdown(f"""
<div class="glass">
<span class="badge {issue["severity"]}">{issue["severity"]}</span><br>
<b>{issue["issue"]}</b>
</div>
""", unsafe_allow_html=True)

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
                st.markdown(f"""
<div class="glass">
<span class="badge {r["severity"]}">{r["severity"]}</span>
<h4>🧠 What’s wrong?</h4>
<p>{r["review"]}</p>
<h4>💡 How to fix</h4>
<p>{r["suggestion"]}</p>
<p><b>Occurrences:</b> {r["occurrences"]}</p>
</div>
""", unsafe_allow_html=True)

# ---------------- METRICS ----------------
with tabs[2]:
    if "metrics" not in st.session_state:
        st.info("Run analysis to see metrics.")
    else:
        for f in st.session_state.metrics["files"]:
            cols = st.columns(4)
            cols[0].markdown(f"<div class='metric'>Quality<br>{f['quality_score']}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div class='metric'>MI<br>{f['maintainability_index']}</div>", unsafe_allow_html=True)
            cols[2].markdown(f"<div class='metric'>Complexity<br>{f['cyclomatic_complexity']}</div>", unsafe_allow_html=True)
            cols[3].markdown(f"<div class='metric'>Issues<br>{f['issue_count']}</div>", unsafe_allow_html=True)
