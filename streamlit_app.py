# app_stage_langchain_pdfminer.py
import streamlit as st
from pdfminer.high_level import extract_text
import google.generativeai as genai
from langchain.llms.base import LLM
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import re
from typing import List, Dict, Optional

# Get API key from Streamlit secrets
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Initialize the Gemini model
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        google_api_key=api_key,
        temperature=0.4,
        max_tokens=2000
    )

# Load Gemini API key from secrets and initialize LangChain LLM
gemini_llm = GeminiLLM(api_key=st.secrets["GEMINI_API_KEY"])

# Get API key from Streamlit secrets
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Initialize the Gemini model
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        google_api_key=api_key,
        temperature=0.4,
        max_tokens=2000
    )

# Helper functions
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

@st.cache_resource
def initialize_conversation_chain():
    memory = ConversationBufferMemory()
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template="Given the conversation history: {history}\nUser input: {input}\nProvide a detailed, accurate response."
    )
    return ConversationChain(llm=gemini_llm, memory=memory, prompt=prompt)

chain = initialize_conversation_chain()

def calculate_match(cv_data: Dict, job_desc: str) -> float:
    prompt = f"Compare CV data (skills: {cv_data['skills']}, experience: {cv_data['experience']}, projects: {cv_data['projects']}) with Job Description: {job_desc}. Return a match percentage as a number (0-100)."
    response = chain.run(prompt)
    return float(response.strip("%"))

def generate_learning_resources() -> str:
    prompt = "Suggest learning resources (e.g., Coursera, YouTube) for improving skills based on the previous CV and job description comparison."
    return chain.run(prompt)

def identify_predominant_function(experience: List[str], job_desc: str) -> str:
    prompt = f"From experience: {experience}, identify the predominant function aligned with job description: {job_desc}."
    return chain.run(prompt)

def generate_projects(function: str, past_projects: List[str], num_projects: int) -> List[str]:
    prompt = f"Generate {num_projects} detailed, industry-convincing projects for the function '{function}' inspired by past projects: {past_projects}. Separate each project with '---'."
    response = chain.run(prompt)
    return response.split("---")

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
        st.write(f"**Project {i}**: {project.strip()}")
    if st.button("Start Over"):
        st.session_state.stage = "input"
        st.session_state.cv_data = None
        st.session_state.match_percentage = 0.0
        st.session_state.function = ""
        st.session_state.projects = []
        chain.memory.clear()  # Reset conversation memory
