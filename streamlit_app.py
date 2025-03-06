# app_stage.py
import streamlit as st
import fitz  # PyMuPDF
from google.generativeai import GenerativeModel  # Placeholder for Gemini
import google.generativeai as genai
import re
from typing import List, Dict

# Load Gemini API key from secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = GenerativeModel("gemini-1.5-pro-latest")

# Helper functions
def extract_cv_data(pdf_file) -> Dict[str, List[str]]:
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "".join(page.get_text() for page in doc)
    skills = re.findall(r"Skills?: (.*?)(?:\n\n|\n|$)", text, re.DOTALL) or [""]
    experience = re.findall(r"Experience: (.*?)(?:\n\n|\n|$)", text, re.DOTALL) or [""]
    projects = re.findall(r"Projects?: (.*?)(?:\n\n|\n|$)", text, re.DOTALL) or [""]
    return {
        "skills": skills[0].split(", "),
        "experience": experience[0].split("\n"),
        "projects": projects[0].split("\n")
    }

def calculate_match(cv_data: Dict, job_desc: str) -> float:
    # Simulate match with Gemini (replace with actual logic)
    prompt = f"Compare CV data: {cv_data} with Job Description: {job_desc}. Return a match percentage."
    response = model.generate_content(prompt)
    return float(response.text.strip("%"))  # Assume Gemini returns "XX%"

def generate_learning_resources() -> str:
    return "Here are some resources:\n- Coursera: [Project Management Basics](https://www.coursera.org)\n- YouTube: [PM Tutorial](https://www.youtube.com)"

def identify_predominant_function(experience: List[str], job_desc: str) -> str:
    prompt = f"From experience: {experience}, identify the predominant function for job: {job_desc}."
    response = model.generate_content(prompt)
    return response.text  # e.g., "Project Management"

def generate_projects(function: str, past_projects: List[str], num_projects: int) -> List[str]:
    prompt = f"Generate {num_projects} detailed, industry-convincing projects for {function} inspired by {past_projects}."
    response = model.generate_content(prompt)
    return response.text.split("\n\n")  # Assume Gemini separates projects with double newlines

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = "input"
if "cv_data" not in st.session_state:
    st.session_state.cv_data = None
if "match_percentage" not in st.session_state:
    st.session_state.match_percentage = 0.0
if "function" not in st.session_state:
    st.session_state.function = ""
if "projects" not in st.session_state:
    st.session_state.projects = []

# Stage 1: Input collection
if st.session_state.stage == "input":
    st.write("### Upload Your CV and Job Details")
    with st.form("input_form"):
        cv_file = st.file_uploader("Upload CV (PDF)", type="pdf")
        company = st.text_input("Target Company Name")
        job_desc = st.text_area("Target Job Description")
        submitted = st.form_submit_button("Analyze")
        if submitted and cv_file and company and job_desc:
            st.session_state.cv_data = extract_cv_data(cv_file)
            st.session_state.match_percentage = calculate_match(st.session_state.cv_data, job_desc)
            st.session_state.stage = "results"

# Stage 2: Results and further processing
elif st.session_state.stage == "results":
    st.write(f"### Match Percentage: {st.session_state.match_percentage}%")
    if st.session_state.match_percentage < 30:
        st.write(generate_learning_resources())
        st.write("All the best in your learning journey!")
    else:
        st.session_state.function = identify_predominant_function(
            st.session_state.cv_data["experience"], job_desc
        )
        st.write(f"Predominant Function Identified: {st.session_state.function}")
        num_projects = st.slider("How many sample projects do you want?", 1, 5, 3)
        if st.button("Generate Projects"):
            st.session_state.projects = generate_projects(
                st.session_state.function, st.session_state.cv_data["projects"], num_projects
            )
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
