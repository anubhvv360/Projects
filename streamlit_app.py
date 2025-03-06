# app_form_basic_no_ai.py
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

# Main app
st.write("### CV-Job Match Analyzer")
with st.form("main_form"):
    cv_file = st.file_uploader("Upload CV (PDF)", type="pdf")
    company = st.text_input("Target Company Name")
    job_desc = st.text_area("Target Job Description")
    submitted = st.form_submit_button("Analyze")

if submitted and cv_file and company and job_desc:
    cv_data = extract_cv_data(cv_file)
    # Mock match percentage (fixed for testing)
    match_percentage = 50.0 if "project" in job_desc.lower() else 20.0
    st.write(f"### Match Percentage: {match_percentage}%")

    if match_percentage < 30:
        st.write("Here will be the learning resources (e.g., Coursera, YouTube links).")
        st.write("All the best!")
    else:
        function = "Mock Function (e.g., Project Management)"
        st.write(f"Predominant Function Identified: {function}")
        with st.form("project_form"):
            num_projects = st.slider("How many sample projects do you want?", 1, 5, 3)
            project_submitted = st.form_submit_button("Generate Projects")
            if project_submitted:
                projects = [f"Sample Project {i+1}: [Output will be here]" for i in range(num_projects)]
                st.write("### Suggested Projects for Your Resume")
                for i, project in enumerate(projects, 1):
                    st.write(f"**Project {i}**: {project}")
