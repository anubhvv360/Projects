#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import re
import json
import PyPDF2
import google.generativeai as genai
import langchain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

st.set_page_config(
    page_title="Resume Project Generator",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📄"
)

api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0.5,
        max_tokens=1500
    )

job_analysis_template = '''
You are an expert career consultant. Analyze the following job description for a role at {company_name} and extract:
1. Industry (e.g., Retail, Healthcare, Technology)
2. Domain within that industry (e.g., Data Science, Project Management)
3. Seniority level (Entry-level, Mid-level, Senior, Executive)

Return your answer as a JSON object with keys: "Industry", "Domain", "Seniority".

Job Description:
{job_description}
'''

stems_template = '''
You are a career coach. Given the text of a resume and a job description, extract the key domain and functional skills common to both. Examples: "ERP Implementation", "Project Management", "Software Development".

Output a JSON array of skill strings.

Resume Text:
{resume_text}

Job Description:
{job_description}
'''

core_work_template = '''
You are a career coach. Analyze the resume text and identify the candidate's core work areas—summarize in 3-5 concise phrases. Examples: "ERP Implementation", "Oracle ERP Technical Design", "PMO Process Governance".

Output a JSON array of core work strings.

Resume Text:
{resume_text}
'''

project_generation_template = '''
You are an industry expert in {domain} within the {industry} sector. The candidate's core work areas are: {core_work}. Skills: {skills}.

Using the resume, job description, and these contexts:
1. Identify 3–5 KPIs or metrics implied by the job description that the candidate could plausibly influence (e.g., cost savings %, project delivery time, process efficiency).
2. Generate {num_projects} ATS-friendly resume projects that:
   - Build on core work areas and selected skills—projects can be new but logically extend past work.
   - Integrate industry/domain keywords in titles & bullets to reinforce alignment.
   - Include a project title and 3–4 bullet points:
     * First bullet quantifies business impact using a KPI and **bold** domain/industry terms.
     * Remaining bullets describe actions, methodologies, tools, and processes, weaving in core work areas and JD terminology.

Format exactly:
### Project {{n}}: [Title reflecting core work & domain]
* [Quantified impact with **bold** KPI and domain/industry terms]
* [Action/methodology with **bold** core work keywords]
* [Action/methodology with **bold** domain-specific terms]
* [Action/methodology with **bold** tools/processes]
'''

project_backstory_template = """
You are a career coach specialising in interview preparation for the {industry} industry and {domain} domain.

For the following projects for a {seniority} level position at {company_name}, create detailed backstories that the candidate can use during interviews when questioned about their experience.

Here are the projects:
{projects}

The backstories should:
1. Be appropriate for the {seniority} level role
2. Include specific challenges faced and how they were overcome
3. Provide realistic context about stakeholders, team dynamics, and decision-making processes
4. Include technical details that demonstrate domain expertise

For each project, provide:

PROJECT BACKSTORY: [2-3 paragraphs with context, challenges, and approach. Each paragraph no more than 100 words]

"""

job_analysis_prompt = PromptTemplate(
    input_variables=["company_name", "job_description"],
    template=job_analysis_template
)
stems_prompt = PromptTemplate(
    input_variables=["resume_text", "job_description"],
    template=stems_template
)
core_work_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template=core_work_template
)
project_prompt = PromptTemplate(
    input_variables=["domain", "skills", "resume_text", "job_description", "industry", "seniority", "core_work", "num_projects"],
    template=project_generation_template
)
project_backstory_prompt = PromptTemplate(
    input_variables=["projects", "industry", "domain", "seniority", "company_name"],
    template=project_backstory_template
)

def analyze_job_description(job_desc, comp_name):
    llm = get_llm()
    chain = LLMChain(prompt=job_analysis_prompt, llm=llm)
    result = chain.run(job_description=job_desc, company_name=comp_name)
    try:
        data = json.loads(result)
        return data.get("Industry", "Unknown"), data.get("Domain", "Unknown"), data.get("Seniority", "Mid-level")
    except json.JSONDecodeError:
        ind = re.search(r'"Industry"\s*:\s*"(.*?)"', result)
        dom = re.search(r'"Domain"\s*:\s*"(.*?)"', result)
        sen = re.search(r'"Seniority"\s*:\s*"(.*?)"', result)
        return (
            ind.group(1) if ind else "Unknown",
            dom.group(1) if dom else "Unknown",
            sen.group(1) if sen else "Mid-level"
        )

def extract_stems(res_text, job_desc):
    llm = get_llm()
    chain = LLMChain(prompt=stems_prompt, llm=llm)
    resp = chain.run(resume_text=res_text, job_description=job_desc)
    try:
        return json.loads(resp)
    except json.JSONDecodeError:
        return re.findall(r'"(.*?)"', resp)

def extract_core_work(res_text):
    llm = get_llm()
    chain = LLMChain(prompt=core_work_prompt, llm=llm)
    resp = chain.run(resume_text=res_text)
    try:
        return json.loads(resp)
    except json.JSONDecodeError:
        return re.findall(r'"(.*?)"', resp)

def generate_projects(domain, skills, resume_text, job_description, industry, seniority, core_work, num_projects):
    llm = get_llm()
    chain = LLMChain(prompt=project_prompt, llm=llm)
    return chain.run(
        domain=domain,
        skills=json.dumps(skills),
        resume_text=resume_text,
        job_description=job_description,
        industry=industry,
        seniority=seniority,
        core_work=json.dumps(core_work),
        num_projects=num_projects
    )

def generate_backstories(industry, domain, seniority, company_name, projects):
    llm = get_llm()
    chain = LLMChain(prompt=project_backstory_prompt, llm=llm)
    return chain.run(
        industry=industry,
        domain=domain,
        seniority=seniority,
        company_name=company_name,
        projects=projects
    )

st.title("📄 Resume Project Generator")
st.markdown("Generate domain-specific projects grounded in your core work, experience, and JD metrics.")

resume_file = st.file_uploader("Upload Your Resume (PDF only)", type=["pdf"])
company_name = st.text_input("Target Company Name")
job_description = st.text_area("Paste Job Description", height=250)

if resume_file and company_name and job_description:
    if st.button("🔍 Analyze & Extract"):
        with st.spinner("Analyzing resume & job description..."):
            reader = PyPDF2.PdfReader(resume_file)
            res_text = "".join([p.extract_text() or "" for p in reader.pages])
            st.session_state['resume_text'] = res_text
            ind, dom, sen = analyze_job_description(job_description, company_name)
            st.session_state['industry'], st.session_state['domain'], st.session_state['seniority'] = ind, dom, sen
            st.session_state['stems'] = extract_stems(res_text, job_description)
            st.session_state['core_work'] = extract_core_work(res_text)
        st.success("Analysis complete.")

if 'stems' in st.session_state:
    st.subheader("Job Analysis Summary")
    st.markdown(f"**Industry:** {st.session_state['industry']}")
    st.markdown(f"**Domain:** {st.session_state['domain']}")
    st.markdown(f"**Seniority:** {st.session_state['seniority']}")

    st.subheader("Core Work Areas")
    for cw in st.session_state['core_work']:
        st.write(f"- {cw}")

    st.subheader("Select Key Skills to Emphasize")
    selected_skills = st.multiselect("Relevant Skills", options=st.session_state['stems'])

    if selected_skills:
        num_projects = st.slider("How many projects?", 1, 5, 3)
        if st.button("🚀 Generate Projects"):
            with st.spinner("Generating projects..."):
                st.session_state['projects_md'] = generate_projects(
                    domain=st.session_state['domain'],
                    skills=selected_skills,
                    resume_text=st.session_state['resume_text'],
                    job_description=job_description,
                    industry=st.session_state['industry'],
                    seniority=st.session_state['seniority'],
                    core_work=st.session_state['core_work'],
                    num_projects=num_projects
                )
        if 'projects_md' in st.session_state:
            st.subheader("Generated Projects")
            st.markdown(st.session_state['projects_md'])
            st.download_button(
                label="Download Projects",
                data=st.session_state['projects_md'],
                file_name=f"projects_{company_name.replace(' ','_')}.txt",
                mime="text/plain"
            )
            if st.button("📖 Generate Project Backstories"):
                with st.spinner("Generating project backstories..."):
                    st.session_state['backstories'] = generate_backstories(
                        industry=st.session_state['industry'],
                        domain=st.session_state['domain'],
                        seniority=st.session_state['seniority'],
                        company_name=company_name,
                        projects=st.session_state['projects_md']
                    )
        if 'backstories' in st.session_state:
            st.subheader("Project Backstories")
            st.markdown(st.session_state['backstories'])
            st.download_button(
                label="Download Backstories",
                data=st.session_state['backstories'],
                file_name=f"backstories_{company_name.replace(' ','_')}.txt",
                mime="text/plain"
            )

st.sidebar.title("ℹ️ About This App")
st.sidebar.markdown("""
    Resume Pivot Tool helps you generate ATS‑friendly, domain‑specific projects grounded in your actual experience.
    Upload your resume and a target job description to extract core work, skills, and JD insights.
""")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📦 Library Versions")
st.sidebar.markdown(f"🔹 **Streamlit**: {st.__version__}")
st.sidebar.markdown(f"🔹 **LangChain**: {langchain.__version__}")
st.sidebar.markdown(f"🔹 **PyPDF2**: {PyPDF2.__version__}")

st.sidebar.title("💡 Tips for Best Results")
st.sidebar.markdown("""
    - Use a machine-readable PDF resume
    - Provide the complete job description for accurate analysis
    - Select only skills you’ve actually used
    - Generated projects should logically extend from your core work
""")
st.sidebar.markdown("---")
st.sidebar.markdown("""
    Have feedback? [Reach out!](mailto:anubhav.verma360@gmail.com) 😊
""", unsafe_allow_html=True)
st.caption("Disclaimer: This tool just provides assistance. The creator is not responsible for any errors or consequences resulting from its use.")

st.markdown("""
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
""", unsafe_allow_html=True)
