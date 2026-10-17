# 📋 AI Document Comparison Assistant

An intelligent enterprise-grade document analysis dashboard engineered to parse, validate, and isolate critical differences across multi-page PDF documents. Built using **Streamlit** and **Google Gemini LLM**.

## ✨ Core Engineering Features
- **Deterministic Text Validation:** Checks document density page-by-page, identifying blank contents or scanned images requiring OCR prior to analysis.
- **Strict Anti-Hallucination Framework:** Enforces strict boundary prompts, ensuring variations are only isolated from provided document text.
- **Granular Page-Tracing Citations:** Automatically targets, appends, and maps source data tags (e.g., `[Page X]`) for total data auditability.
- **Side-by-Side Parameter Matrix:** Organizes granular differences (deadlines, salaries, roles) into a comparative display table.
- **Production Report Exporter:** Formats and compiles the entire markdown analysis stream into a structured Microsoft Word (.docx) file with one click.

## 📂 Project Architecture
```text
ai-document-comparison-assistant/
├── app.py                # Main Streamlit Dashboard UI & state memory coordinator
├── document_reader.py    # Density checker, validator, and page-by-page parser
├── comparison.py         # Gemini LLM connection framework & response builder
├── report_generator.py   # Word document processing (.docx) export layer
├── requirements.txt      # Production package dependency mapping
└── .gitignore            # Security filter separating local files (.env, .venv)
```

## 🛠️ Step-by-Step Local Deployment

### 1. Clone & Set Up Directory Context
```bash
git clone https://github.com
cd ai-document-comparison-assistant
```

### 2. Configure Your Security Tokens
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_actual_alphanumeric_api_key_here
```

### 3. Initialize Isolated Environment & Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Launch the Server Platform
```bash
python -m streamlit run app.py
```
The application will automatically initialize a web application session at `http://localhost:8501`.
