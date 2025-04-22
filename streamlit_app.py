#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import PyPDF2
import re
import json
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Page configuration
st.set_page_config(
    page_title="Resume Pivot Project Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        google_api_key=st.secrets["GEMINI_API_KEY"],
        temperature=0.4,
        max_tokens=2000
    )

# Prompt to analyze job description
job_analysis_template = """
You are an expert career consultant. Analyze the following job description for a role at {company_name} and extract:
1. Industry (e.g., Retail, Healthcare, Technology)
2. Domain within that industry (e.g., Data Science, Project Management)
3. Seniority level of the role (Entry-level, Mid-level, Senior, Executive)

Format exactly as:
Industry: [Industry]
Domain: [Domain]
Seniority: [Level]

Job Description:
{job_description}
"""
job_analysis_prompt = PromptTemplate(
    input_variables=["company_name", "job_description"],
    template=job_analysis_template
)

# Prompt to extract relevant resume stems
stems_template = """
You are a career coach. Given the resume bullet points and a job description, extract only those bullet points most relevant to the job. Return as a JSON array of strings.

Resume Bullets:
{resume_bullets}

Job Description:
{job_description}
"""
stems_prompt = PromptTemplate(
    input_variables=["resume_bullets", "job_description"],
    template=stems_template
)

# Prompt to generate projects blending stems and job context
generation_template = """
You are an industry expert in {industry} (domain: {domain}). The candidate has {years_experience} years of experience and wants to pivot to {pivot_domain}. Given the selected stems:
{stems}
and the job description for {company_name}:
{job_description}

Generate {num_projects} ATS-friendly resume projects. For each project, use this Markdown format:

### Project {{n}}: [Title]
* [Quantifiable business impact with metrics and **bold** key terms]
* [Action or methodology with **bold** key terms]
* [Action or methodology with **bold** key terms]
* [Action or methodology with **bold** key terms]

Ensure each bullet starts with an asterisk and each project is separated by a blank line.
"""
project_generation_prompt = PromptTemplate(
    input_variables=[
        "industry", "domain", "company_name", "job_description",
        "pivot_domain", "years_experience", "stems", "num_projects"
    ],
    template=generation_template
)

# Utility functions
def analyze_job_description(job_description: str, company_name: str):
    llm = get_llm()
    chain = LLMChain(prompt=job_analysis_prompt, llm=llm)
    result = chain.run(job_description=job_description, company_name=company_name)
    # Parse output
    industry = re.search(r'Industry:\s*(.*)', result)
    domain = re.search(r'Domain:\s*(.*)', result)
    seniority = re.search(r'Seniority:\s*(.*)', result)
    return (
        industry.group(1).strip() if industry else "Unknown",
        domain.group(1).strip() if domain else "Unknown",
        seniority.group(1).strip() if seniority else "Mid-level"
    )


def extract_stems(bullets: list, job_description: str) -> list:
    llm = get_llm()
    chain = LLMChain(prompt=stems_prompt, llm=llm)
    bullets_text = "\n".join(f"- {b}" for b in bullets)
    response = chain.run(resume_bullets=bullets_text, job_description=job_description)
    # Attempt JSON parse
    try:
        stems = json.loads(response)
    except Exception:
        # Fallback to line parsing
        stems = [line.strip('- ').strip() for line in response.splitlines() if line.strip().startswith('-')]
    return stems


def generate_projects(industry, domain, company_name, job_description,
                      pivot_domain, years_experience, stems, num_projects):
    llm = get_llm()
    chain = LLMChain(prompt=project_generation_prompt, llm=llm)
    stems_text = "\n".join(f"- {s}" for s in stems)
    return chain.run(
        industry=industry,
        domain=domain,
        company_name=company_name,
        job_description=job_description,
        pivot_domain=pivot_domain,
        years_experience=years_experience,
        stems=stems_text,
        num_projects=num_projects
    )

# Streamlit App UI
st.title("📄 Resume Pivot Project Generator")

# Inputs
resume_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
company_name = st.text_input("Target Company Name")
job_description = st.text_area("Paste Job Description", height=200)
pivot_domain = st.text_input("Desired Pivot Domain (Target Role)")
years_experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=3)

if resume_file and company_name and job_description and pivot_domain:
    with st.spinner("Extracting resume text..."):
        reader = PyPDF2.PdfReader(resume_file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        bullets = [line.strip() for line in text.split("\n") if line.strip()]

    # Analyze JD
    industry, domain, seniority = analyze_job_description(job_description, company_name)
    st.subheader("Job Analysis")
    st.markdown(f"**Industry:** {industry}")
    st.markdown(f"**Domain:** {domain}")
    st.markdown(f"**Seniority:** {seniority}")

    # Extract stems
    with st.spinner("Identifying relevant experience stems..."):
        stems = extract_stems(bullets, job_description)
    selected_stems = st.multiselect("Select Relevant Experience Stems", options=stems)

    # Number of projects
    num_projects = st.slider("Number of Projects to Generate", 1, 5, 3)

    # Generate
    if st.button("Generate Projects"):
        with st.spinner("Generating tailored resume projects..."):
            projects_md = generate_projects(
                industry, domain, company_name, job_description,
                pivot_domain, years_experience, selected_stems, num_projects
            )
        st.subheader("Generated Projects")
        st.markdown(projects_md)

        # Download
        st.download_button(
            label="Download Projects as Markdown",
            data=projects_md,
            file_name=f"projects_{company_name.replace(' ', '_')}.md",
            mime="text/markdown"
        )
else:
    st.info("Please provide all inputs above to generate your tailored projects.")

# Sidebar Tips
st.sidebar.title("💡 Tips for Best Results")
st.sidebar.markdown("""
- Upload a clear, text-based PDF resume.
- Provide the full job description for accurate analysis.
- Select the experience stems that best match your target role.
- Adjust the number of projects to fit your resume length.
""
)
