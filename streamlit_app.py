#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import re
import PyPDF2
import google.generativeai as genai
import langchain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(
    page_title="Resume Project Generator",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📄"
)

# ---------------------------
# Configure Gemini API
# ---------------------------
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# ---------------------------
# Initialize LLM
# ---------------------------
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0.3,
        max_tokens=1200
    )

# ---------------------------
# Prompt Templates
# ---------------------------
job_analysis_template = '''
You are an expert career consultant. Analyze the following job description for a role at {company_name} and extract:
1. Industry (e.g., Retail, Healthcare, Technology)
2. Domain within that industry (e.g., Data Science, Project Management)
3. Seniority level (Entry-level, Mid-level, Senior, Executive)

Format exactly:
Industry: [Industry]
Domain: [Domain]
Seniority: [Level]

Job Description:
{job_description}
'''

stems_template = '''
You are a career coach. Given the text of a resume and a job description, extract the key domain and functional skills common to both. Examples include "ERP Implementation", "Project Management", "Software Development".

Output a JSON array of skill strings, without additional text.

Resume Text:
{resume_text}

Job Description:
{job_description}
'''

project_generation_template = '''
You are an industry expert in {domain}. Given the selected skills [{skills}] from a candidate, their resume text, and the job description:

Resume Text:
{resume_text}

Job Description:
{job_description}

Generate {num_projects} ATS-friendly resume projects grounded strictly in the candidate's actual experience. Use only the selected skills; do not hallucinate. For each project:
1. Create a compelling, specific project heading
2. Provide 3–4 bullet points:
   - First bullet must quantify business impact using metrics and **bold** key terms
   - Remaining bullets describe actions, methodologies, tools, and processes

Format output:
### Project {{n}}: [Title]
* [Quantified impact with **bold** terms]
* [Action/methodology with **bold** terms]
* [Action/methodology with **bold** terms]
* [Action/methodology with **bold** terms]
'''

# ---------------------------
# Prompt Initialization
# ---------------------------
job_analysis_prompt = PromptTemplate(
    input_variables=["company_name","job_description"],
    template=job_analysis_template
)
stems_prompt = PromptTemplate(
    input_variables=["resume_text","job_description"],
    template=stems_template
)
project_prompt = PromptTemplate(
    input_variables=["domain","skills","resume_text","job_description","num_projects"],
    template=project_generation_template
)

# ---------------------------
# Core Functions
# ---------------------------
def analyze_job_description(job_desc, comp_name):
    llm = get_llm()
    chain = LLMChain(prompt=job_analysis_prompt, llm=llm)
    result = chain.run(job_description=job_desc, company_name=comp_name)
    industry = re.search(r'Industry:\s*(.*)', result)
    domain = re.search(r'Domain:\s*(.*)', result)
    seniority = re.search(r'Seniority:\s*(.*)', result)
    return (
        industry.group(1).strip() if industry else "Unknown",
        domain.group(1).strip() if domain else "Unknown",
        seniority.group(1).strip() if seniority else "Mid-level"
    )


def extract_stems(res_text, job_desc):
    llm = get_llm()
    chain = LLMChain(prompt=stems_prompt, llm=llm)
    response = chain.run(resume_text=res_text, job_description=job_desc)
    try:
        stems = re.findall(r'"(.*?)"', response)
    except Exception:
        stems = []
    return stems


def generate_projects(domain, skills, resume_text, job_description, num_projects):
    llm = get_llm()
    chain = LLMChain(prompt=project_prompt, llm=llm)
    skills_str = ", ".join(skills)
    projects_md = chain.run(
        domain=domain,
        skills=skills_str,
        resume_text=resume_text,
        job_description=job_description,
        num_projects=num_projects
    )
    return projects_md

# ---------------------------
# UI Flow
# ---------------------------
st.title("📄 Resume Project Generator")
st.markdown("Generate domain-specific resume skills and projects grounded in your actual experience.")

# Inputs
resume_file = st.file_uploader("Upload Your Resume (PDF only)", type=["pdf"])
company_name = st.text_input("Target Company Name")
job_description = st.text_area("Paste Job Description", height=250)

# Analyze button
if resume_file and company_name and job_description:
    if st.button("Analyze Resume & Extract Skills"):
        with st.spinner("Analyzing job description and resume..."):
            reader = PyPDF2.PdfReader(resume_file)
            res_text = "".join([p.extract_text() or "" for p in reader.pages])
            st.session_state['resume_text'] = res_text
            ind, dom, sen = analyze_job_description(job_description, company_name)
            st.session_state['domain'] = dom
            stems = extract_stems(res_text, job_description)
            st.session_state['stems'] = stems
        st.success("Skill extraction complete.")

# Display stems and project options
if 'stems' in st.session_state:
    st.subheader("Select Key Skills to Emphasize")
    selected_skills = st.multiselect("Relevant Skills", options=st.session_state['stems'])
    if selected_skills:
        st.markdown("**You selected:**")
        for skill in selected_skills:
            st.write(f"- {skill}")
        num_projects = st.slider("How many projects to generate?", 1, 5, 3)
        if st.button("Generate Projects"):
            with st.spinner("Generating projects..."):
                projects_md = generate_projects(
                    domain=st.session_state['domain'],
                    skills=selected_skills,
                    resume_text=st.session_state['resume_text'],
                    job_description=job_description,
                    num_projects=num_projects
                )
            st.subheader("Generated Projects")
            st.markdown(projects_md)
            st.download_button(
                label="Download Projects as Text",
                data=projects_md,
                file_name=f"projects_{company_name.replace(' ', '_')}.txt",
                mime="text/plain"
            )

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("ℹ️ About This App")
st.sidebar.markdown(
    """
    Resume Pivot Tool helps you generate ATS-friendly, domain-specific projects grounded in your actual experience.
    Upload your resume and a target job description to extract key skills and generate tailored projects.
    """
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📦 Library Versions")
st.sidebar.markdown(f"🔹 **Streamlit**: {st.__version__}")
st.sidebar.markdown(f"🔹 **LangChain**: {langchain.__version__}")
st.sidebar.markdown(f"🔹 **PyPDF2**: {PyPDF2.__version__}")

st.sidebar.title("Usage Statistics")
st.sidebar.write(f"Total Tokens Consumed: {st.session_state.tokens_consumed}")
st.sidebar.write(f"Query Tokens: {st.session_state.query_tokens}")
st.sidebar.write(f"Response Tokens: {st.session_state.response_tokens}")

st.sidebar.title("Tips for Best Results")
st.sidebar.markdown(
    """
    - Upload a text-based PDF resume for accurate extraction
    - Provide the full job description for better skill matching
    - Select only the skills you’ve demonstrated in your career
    - Limit projects to those grounded in your past roles
    """
)

st.sidebar.title("Example Output Format")
st.sidebar.markdown(
    """
    ### Project Title
    * First bullet with **bold keywords** and impact metrics
    * Second bullet with **technical skills** used
    * Third bullet explaining the **methodology** applied
    """
)

if st.sidebar.button("Reset Usage Counters"):
    st.session_state.tokens_consumed = 0
    st.session_state.query_tokens = 0
    st.session_state.response_tokens = 0
    st.sidebar.success("Counters reset successfully!")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    Have feedback? [Reach out!](mailto:anubhav.verma360@gmail.com) 😊
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Footer
# ---------------------------
st.markdown(
    """
    <style>
    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .animated-gradient {
        background: linear-gradient(90deg, blue, purple, blue);
        background-size: 300% 300%;
        animation: gradientAnimation 8s ease infinite;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-top: 20px;
        color: white;
        font-weight: normal;
        font-size: 18px;
    }
    </style>

    <div class="animated-gradient">
        Made with ❤️ by Anubhav Verma
    </div>
    """,
    unsafe_allow_html=True
)
