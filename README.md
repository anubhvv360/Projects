# Resume Pivot Tool

A Gen AI app that helps job‑seekers pivot into a new domain by generating ATS‑friendly, experience‑grounded résumé projects and interview backstories based on their actual PDF résumé and a target job description. Powered by LangChain + Google Gemini 2.0 Flash.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://jdprojects2.streamlit.app/)

---

## 🚀 Features

- **Resume & JD Analysis**  
  Upload your PDF résumé and paste a full job description to automatically extract:
  - **Industry**  
  - **Domain**  
  - **Seniority Level**

- **Core Work Extraction**  
  Distil your top 3–5 “core work areas” from your résumé.

- **Skill Stem Extraction**  
  Identify domain & functional skills you’ve used that overlap with the JD (e.g., “Project Management,” “Supply Chain Optimisation”).

- **Project Generation**  
  Pick 1–5 projects to generate. Each project:
  1. Builds on your real core work and selected skills  
  2. Uses KPIs/metrics implied by the JD  
  3. Bolds key terms & integrates industry/domain language  
  4. Outputs Markdown‑formatted title + 3–4 bullets

- **Project Backstories**  
  For each generated project, produce a 2–3‑paragraph narrative you can use in interviews — covering challenges, solutions, stakeholders and technical depth.

- **One‑Click Download**  
  Export both **Projects** and **Backstories** as plain `.txt` files.

---

## 🛠️ Tech Stack

- **Streamlit** — UI  
- **PyPDF2** — PDF parsing  
- **LangChain** + **langchain‑google‑genai** — Prompt chaining  
- **Google Generative AI SDK** — Gemini 2.0 Flash integration  

---

## 📦 Installation

```bash
git clone https://github.com/your‑username/resume-pivot-tool.git
cd resume-pivot-tool

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

