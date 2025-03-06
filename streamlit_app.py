# app_stage_basic_no_ai.py
import streamlit as st
from pdfminer.high_level import extract_text
import re
from typing import Dict, List

# Mock CV extraction (using PDFMiner.six)
def extract_cv_data(pdf_file) -> Dict[str, List[str]]:
    text = extract_text(pdf_file)
    skills = re.findall(r"Skills?: (.*?)(?:\n\n|\n|$)", text, re.DOTALL) or [""]
    experience = re.findall(r"Experience: (.*?)(?:\n\n|\n|$)", text, re.DOTALL) or [""]
    projects = re.findall(r"Projects?: (.*?)(?:\n\n|\n|$)", text, re.DOTALL) or [""]
    return {
        "skills": skills[0].split(", "),
        "experience": experience[0].split("\n"),
        "projects": projects[0].split("\n")
    }

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = "input"
if "cv_data" not in st.session_state:
    st.session_state.cv_data = None
if "match_percentage" not in st.session_state:
    st.session_state.match_percentage = 0.0  # Placeholder percentage
if "function" not in st.session_state:
    st.session_state.function = ""
if "projects" not in st.session_state:
    st.session_state.projects = []

# Stage 1: Input collection
if st.session_state.stage == "input":
    st.write("### Step 1: Upload CV and Enter Job Details")
    with st.form("input_form"):
        cv_file = st.file_uploader("Upload CV (PDF)", type="pdf")
        company = st.text_input("Target Company Name")
        job_desc = st.text_area("Target Job Description")
        submitted = st.form_submit_button("Analyze")
        if submitted and cv_file and company and job_desc:
            st.session_state.cv_data = extract_cv_data(cv_file)
            # Mock match percentage (fixed for testing)
            st.session_state.match_percentage = 50.0 if "project" in job_desc.lower() else 20.0
            st.session_state.stage = "results"

# Stage 2: Results and further processing
elif st.session_state.stage == "results":
    st.write(f"### Match Percentage: {st.session_state.match_percentage}%")
    if st.session_state.match_percentage < 30:
        st.write("Here will be the learning resources (e.g., Coursera, YouTube links).")
        st.write("All the best!")
    else:
        st.session_state.function = "Mock Function (e.g., Project Management)"
        st.write(f"Predominant Function Identified: {st.session_state.function}")
        num_projects = st.slider("How many sample projects do you want?", 1, 5, 3)
        if st.button("Generate Projects"):
            st.session_state.projects = [f"Sample Project {i+1}: [Output will be here]" for i in range(num_projects)]
            st.session_state.stage = "show_projects"

# Stage 3: Display projects
elif st.session_state.stage == "show_projects":
    st.write("### Suggested Projects for Your Resume")
    for i, project in enumerate(st.session_state.projects, 1):
        st.write(f"**Project {i}**: {project}")
    if st.button("Start Over"):
        st.session_state.stage = "input"
        st.session_state.cv_data = None
        st.session_state.match_percentage = 0.0
        st.session_state.function = ""
        st.session_state.projects = []

