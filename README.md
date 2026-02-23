# CodeGuard - Multi-Language Code Quality Analyzer

##  Overview
CodeGuard is a modular code quality analyzer that scans source files for style issues, documentation gaps, and security risks. It integrates **AI (Ollama)** to provide human‑friendly explanations and automatic fixes.  
The project includes a **Streamlit frontend** for interactive demos and a **pre‑commit hook** to block bad code before it enters the repository.

---

##  Features
-  Static analysis for **Python, C, C++, Java, JavaScript**
-  AI-powered review with explanations + fixes
-  Metrics reporting (complexity, documentation coverage, etc.)
-  Streamlit frontend with 4 tabs (Static Issues, AI Review, Metrics, Program Output)
-  Pre-commit hooks to block commits with CRITICAL/ERROR issues
-  Demo files (error vs clean) for presentation

---

##  Project Structure

```
.github/           → GitHub Actions workflows (CI/CD automation)
.gitlab/           → GitLab CI/CD config (optional cross-platform automation)
assets/            → Static resources (architecture & screenshots)
    ├── architecture.jpeg
    └── screenshots/
        ├── op1.jpeg
        ├── op2.jpeg
        ├── op3.jpeg
        ├── op4.jpeg
        ├── op5.jpeg
        ├── op6.jpeg
        └── op7.jpeg
presentation/      → Project presentation slides
    └── CodeGuard ppt
    └── Documentation.docx
analyzers/         → Language-specific analyzers
    ├── c_analyzer.py
    ├── cpp_analyzer.py
    ├── java_analyzer.py
    ├── javascript_analyzer.py
    └── __init__.py
codeguard/         → Core engine
    ├── module1.py        (static analysis: style, docs, secrets)
    ├── module2.py        (AI review integration with Ollama)
    ├── module3.py        (reporting/metrics)
    ├── dispatcher.py     (routes files to analyzers)
    ├── analyzer.py       (base analyzer logic)
    ├── __main__.py       (entry point: python -m codeguard)
    └── __init__.py
uploaded_files/    → Demo/test files (error.py, clean.py, manual_input.java)
pyproject.toml     → Project configuration and dependencies
streamlit_app.py   → Streamlit frontend for interactive demo
README.md          → Project overview (this file)
```

---

##  Installation

```bash
# Clone the repo
git clone https://github.com/<your-username>/CodeGuard.git
cd CodeGuard

# Install dependencies
pip install -r requirements.txt
```

---

##  Usage Flow

### 1. Run Static + AI Review from CLI
```bash
python codeguard.py uploaded_files/error.py
```
- Runs static analyzers (style, docstring, security checks).
- Calls AI review (via Ollama).
- Prints issues and suggested fixes in terminal.

### 2. Launch Streamlit Frontend
```bash
streamlit run streamlit_app.py
```
- Open `http://localhost:8501` in your browser.
- Explore tabs:
  - **Static Issues**
  - **AI Review**
  - **Metrics**
  - **Program Output**

### 3. Demo Files
- `error.py` → intentionally bad code (shows issues).
- `clean.py` → corrected code (shows 0 issues).
- `manual_input.java` → demo for Java analyzer.

---

##  Flowchart

```text
User Uploads File → Dispatcher → Static Analyzers → AI Review (Ollama) → Reporting Module → Streamlit Frontend → Pre-commit Hook
```

##  System Architecture
The diagram below shows the detailed architecture of CodeGuard, including:
- User input (Streamlit frontend, pre-commit hook)
- Dispatcher for language routing
- Static analyzers (Python, Java, etc.)
- AI review (Ollama)
- Streamlit dashboard with 5 tabs
- Auto-apply fixes
- Pre-commit blocking logic

<p align="center">
  <img src="assets/CodeGuard Architecture.jpeg" width="800">
</p>



---

##  Language Support
-  Implemented: Python, C, C++, Java, JavaScript
-  Planned: TypeScript, Kotlin, Go, Rust, PHP, HTML, CSS, Shell, Ruby
