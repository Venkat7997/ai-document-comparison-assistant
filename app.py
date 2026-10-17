import streamlit as st
from dotenv import load_dotenv
import os

from document_reader import extract_and_validate_pdf
from comparison import run_document_comparison
from report_generator import build_docx_report

# Load configuration layers
load_dotenv()

st.set_page_config(
    page_title="AI Document Comparison Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize critical session track components
if "evaluation_matrix" not in st.session_state:
    st.session_state.evaluation_matrix = None
if "doc_a_meta" not in st.session_state:
    st.session_state.doc_a_meta = None
if "doc_b_meta" not in st.session_state:
    st.session_state.doc_b_meta = None

# Interface Title Assembly
st.title("📋 AI Document Comparison Assistant")
st.markdown(
    "Upload two text-based PDF documents below (e.g., policies, syllabus versions, or contracts). "
    "The system will extract their text, isolate critical facts, and leverage AI to build an analytical delta view."
)

# Sidebar setup for configuration status check
with st.sidebar:
    st.header("🔧 System Configurations")
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    if has_key:
        st.success("Gemini API Key: Configured")
    else:
        st.error("Gemini API Key: Missing")
        st.info("Add GEMINI_API_KEY to your local `.env` file to enable functionality.")

# Grid design layout for upload fields
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📄 Document A (Base Version)")
    uploaded_a = st.file_uploader("Upload primary document file", type=["pdf"], key="file_uploader_a")

with col_right:
    st.subheader("📄 Document B (Updated/Alternative)")
    uploaded_b = st.file_uploader("Upload target document file", type=["pdf"], key="file_uploader_b")

# Action Bar Options Layout
st.markdown("---")
action_cols = st.columns(2)

with action_cols[0]:
    compare_triggered = st.button("⚡ Compare Documents", type="primary", use_container_width=True)

with action_cols[1]:
    clear_triggered = st.button("🔄 Clear and Reset", use_container_width=True)

if clear_triggered:
    st.session_state.evaluation_matrix = None
    st.session_state.doc_a_meta = None
    st.session_state.doc_b_meta = None
    st.rerun()

# Processing pipeline flow triggers
if compare_triggered:
    if not uploaded_a or not uploaded_b:
        st.error("Execution stalled: Please provide both required Document files before executing analysis.")
    else:
        with st.spinner("Extracting content segments and validating structures..."):
            res_a = extract_and_validate_pdf(uploaded_a)
            res_b = extract_and_validate_pdf(uploaded_b)
            
            st.session_state.doc_a_meta = res_a
            st.session_state.doc_b_meta = res_b
            
        if not res_a["success"]:
            st.error(f"Error in Document A: {res_a['error_message']}")
        elif not res_b["success"]:
            st.error(f"Error in Document B: {res_b['error_message']}")
        else:
            with st.spinner("Generating comparative analysis from Gemini LLM..."):
                analysis_output = run_document_comparison(
                    uploaded_a.name, res_a["text"],
                    uploaded_b.name, res_b["text"]
                )
                
                if analysis_output["success"]:
                    st.session_state.evaluation_matrix = analysis_output["content"]
                else:
                    st.error(analysis_output["content"])

# Render structural outputs if matrix records exist
if st.session_state.evaluation_matrix and st.session_state.doc_a_meta and st.session_state.doc_b_meta:
    st.success("Analysis Complete!")
    stat_cols = st.columns(2)
    with stat_cols[0]:
        st.info(f"**{uploaded_a.name}** Profile: {st.session_state.doc_a_meta['page_count']} Pages | {st.session_state.doc_a_meta['char_count']} Characters")
    with stat_cols[1]:
        st.info(f"**{uploaded_b.name}** Profile: {st.session_state.doc_b_meta['page_count']} Pages | {st.session_state.doc_b_meta['char_count']} Characters")

    raw_markdown = st.session_state.evaluation_matrix
    docx_stream = build_docx_report(uploaded_a.name, uploaded_b.name, raw_markdown)
    
    st.download_button(
        label="📥 Download Full Comparison Report (.DOCX)",
        data=docx_stream,
        file_name="Document_Comparison_Report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    
    st.markdown("### 📋 Analysis Results Breakdown")
    
    sections = raw_markdown.split("### ")
    tab_titles = ["Summaries", "Similarities", "Differences", "Key Details Grid", "Conclusion & Limits"]
    tabs = st.tabs(tab_titles)
    
    with tabs[0]:
        st.subheader("Document Summary Overview")
        for sec in sections:
            if "1. Summary" in sec or "2. Summary" in sec:
                st.markdown("### " + sec)
                
    with tabs[1]:
        st.subheader("Shared Similarities and Features")
        for sec in sections:
            if "3. Key Similarities" in sec:
                st.markdown(sec.replace("3. Key Similarities", ""))
                
    with tabs[2]:
        st.subheader("Identified Variations and Deltas")
        for sec in sections:
            if "4. Meaningful Differences" in sec:
                st.markdown(sec.replace("4. Meaningful Differences", ""))
                
    with tabs[3]:
        st.subheader("Parameter Comparisons and Metrics")
        for sec in sections:
            if "5. Key Details" in sec:
                st.markdown(sec.replace("5. Key Details Comparison Table", ""))
                
    with tabs[4]:
        st.subheader("Conclusions & Data Bounds")
        for sec in sections:
            if "6. Overall Conclusion" in sec or "7. Limitations" in sec:
                st.markdown("### " + sec)
