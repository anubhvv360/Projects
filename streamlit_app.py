#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import re
import PyPDF2
import google.generativeai as genai
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
        max_tokens=1000
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
You are a career coach. Given the text of a resume and a job description, extract the key domain and functional skills common to both. Examples of such skills include "ERP Implementation", "Project Management", "Software Development".

Output a JSON array of skills (strings), without additional text.

Resume Text:
{resume_text}

Job Description:
{job_description}
'''

project_generation_template = '''
You are an industry expert in {domain}. Given the selected skills {skills} from a candidate with resume:
{resume_text}
and job description:
{job_description}

For each project:
1. Create a compelling, specific project heading (not generic)
2. Create 3-4 bullet points that describe the project:
   - First bullet MUST include a quantifiable business impact with specific metrics (use realistic numbers)
   - Remaining bullets should describe the specific actions, methodologies, tools, and processes used
   - Use industry-specific terminology, frameworks, and metrics that would be recognized by hiring managers
   - Include specific company types, product categories, or technical details that show deep domain knowledge
   - Avoid vague or generic statements; be detailed and specific enough to be convincing to industry insiders
   - BOLD key terms, tools, metrics, and industry-specific terminology by surrounding them with ** (e.g., **KPI**)

Generate {num_projects} ATS-friendly resume projects. For each project, output:

### Project {{n}}: [Title]
* [Quantifiable impact with **bold** key terms]
* [Action/methodology with **bold** key terms]
* [Action/methodology with **bold** key terms]
* [Action/methodology with **bold** key terms]
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
    # Prepare skills list string
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
st.markdown("Generate domain-specific resume stems and projects based on your resume and a target job description.")

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

# Display stems selection
if 'stems' in st.session_state:
    st.subheader("Select Key Skills to Emphasize")
    selected_skills = st.multiselect("Relevant Skills", options=st.session_state['stems'])

    if selected_skills:
        st.markdown("**You selected:**")
        for skill in selected_skills:
            st.write(f"- {skill}")

        # Slider for number of projects
        num_projects = st.slider("How many projects to generate?", 1, 5, 3)

        # Generate projects button
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
                label="Download Projects as Markdown",
                data=projects_md,
                file_name=f"projects_{company_name.replace(' ', '_')}.md",
                mime="text/markdown"
            )

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Anubhav Verma | Issues? anubhav.verma360@gmail.com")
