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
# Initialize Token Counters
# ---------------------------
if 'tokens_consumed' not in st.session_state:
    st.session_state.tokens_consumed = 0
if 'query_tokens' not in st.session_state:
    st.session_state.query_tokens = 0
if 'response_tokens' not in st.session_state:
    st.session_state.response_tokens = 0

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
    """
    Extract domain and functional skills common to resume and job description.
    """
    llm = get_llm()
    chain = LLMChain(prompt=stems_prompt, llm=llm)
    response = chain.run(resume_text=res_text, job_description=job_desc)
    # parse JSON array
    try:
        stems = re.findall(r'"(.*?)"', response)
    except Exception:
        stems = []
    return stems

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
    if st.button("Analyze Resume & Extract Skills" ):
        with st.spinner("Analyzing job description and resume..."):
            # Extract resume text
            reader = PyPDF2.PdfReader(resume_file)
            res_text = "".join([p.extract_text() or "" for p in reader.pages])
            st.session_state['resume_text'] = res_text
            # Analyze job description
            ind, dom, sen = analyze_job_description(job_description, company_name)
            st.session_state['industry'] = ind
            st.session_state['domain'] = dom
            st.session_state['seniority'] = sen
            # Extract stems (skills)
            stems = extract_stems(res_text, job_description)
            st.session_state['stems'] = stems
        st.success("Skill extraction complete.")

# Display analysis results
if 'industry' in st.session_state:
    st.subheader("Job Analysis")
    st.markdown(f"**Industry:** {st.session_state['industry']}")
    st.markdown(f"**Domain:** {st.session_state['domain']}")
    st.markdown(f"**Seniority:** {st.session_state['seniority']}" )

# Display stems selection
if 'stems' in st.session_state:
    st.subheader("Select Key Skills to Emphasize")
    selected = st.multiselect("Relevant Skills", options=st.session_state['stems'])
    if selected:
        st.markdown("**You selected:**")
        for s in selected:
            st.write(f"- {s}")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Anubhav Verma | Issues? anubhav.verma360@gmail.com")
