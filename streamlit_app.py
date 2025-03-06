# app_stage_basic.py
import streamlit as st

# Mock functions (no external dependencies)
def extract_cv_data_mock():
    return {
        "skills": ["Python", "Project Management", "ERP"],
        "experience": ["ERP Implementation", "PMO Support"],
        "projects": ["ERP Rollout for Company X", "PMO Dashboard Creation"]
    }

def calculate_match_mock(cv_data, job_desc):
    # Simulate a match percentage based on simple keyword overlap
    job_keywords = job_desc.lower().split()
    cv_text = " ".join(cv_data["skills"] + cv_data["experience"] + cv_data["projects"]).lower()
    overlap = sum(1 for word in job_keywords if word in cv_text)
    return min(100, overlap * 10)  # Rough percentage

def generate_learning_resources_mock():
    return "Mock Resources:\n- Coursera: Project Management\n- YouTube: PM Basics"

def identify_function_mock(experience, job_desc):
    return "Project Management" if "project" in job_desc.lower() else "Generic Function"

def generate_projects_mock(function, num_projects):
    return [f"Mock {function} Project {i+1}: Led a team to success." for i in range(num_projects)]

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
    st.write("### Step 1: Enter Job Details")
    with st.form("input_form"):
        company = st.text_input("Target Company Name")
        job_desc = st.text_area("Target Job Description")
        submitted = st.form_submit_button("Analyze")
        if submitted and company and job_desc:
            st.session_state.cv_data = extract_cv_data_mock()
            st.session_state.match_percentage = calculate_match_mock(st.session_state.cv_data, job_desc)
            st.session_state.stage = "results"

# Stage 2: Results and further processing
elif st.session_state.stage == "results":
    st.write(f"### Match Percentage: {st.session_state.match_percentage}%")
    if st.session_state.match_percentage < 30:
        st.write(generate_learning_resources_mock())
        st.write("All the best!")
    else:
        st.session_state.function = identify_function_mock(st.session_state.cv_data["experience"], job_desc)
        st.write(f"Predominant Function: {st.session_state.function}")
        num_projects = st.slider("How many projects?", 1, 5, 3)
        if st.button("Generate Projects"):
            st.session_state.projects = generate_projects_mock(st.session_state.function, num_projects)
            st.session_state.stage = "show_projects"

# Stage 3: Display projects
elif st.session_state.stage == "show_projects":
    st.write("### Suggested Projects")
    for i, project in enumerate(st.session_state.projects, 1):
        st.write(f"**Project {i}**: {project}")
    if st.button("Start Over"):
        st.session_state.stage = "input"
        st.session_state.cv_data = None
        st.session_state.match_percentage = 0.0
        st.session_state.function = ""
        st.session_state.projects = []

