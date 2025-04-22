# Resume Project Generator

A Gen AI tool that helps job‑seekers pivot their careers by extracting their core domain/functional skills and generating ATS‑friendly, experience‑grounded projects based on their actual resume and a target job description. Built with LangChain + Google Gemini 2.0 Flash.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://jdprojects2.streamlit.app/)

---

## 🚀 Features

- **PDF Resume Upload** – Parses your existing resume at the paragraph‑level.  
- **Job Description Analysis** – Uses Gemini to identify industry, domain, and seniority.  
- **Skill Extraction** – Automatically extracts key domain/functional skills common to both your resume and the JD (e.g., ERP Implementation, Project Management).  
- **Interactive Selection** – Pick which of your own skills to emphasize via a Streamlit multiselect.  
- **Slider Control** – Choose how many project entries (1–5) to generate.  
- **Experience‑Grounded Project Generation** – Produces quantifiable, ATS‑friendly project bullet points strictly based on your real experience (no hallucinations).  
- **Download as Text** – Export your tailored projects as a `.txt` snippet ready for copy‑paste.

---

## 🛠️ Tech Stack

- **Streamlit** for the web UI  
- **PyPDF2** for PDF parsing  
- **LangChain** + **langchain‑google‑genai** for chaining prompts  
- **Google Generative AI SDK** (`google.generativeai`) with **Gemini 2.0 Flash**
