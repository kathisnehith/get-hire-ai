import os
from dotenv import load_dotenv, find_dotenv
import time
import json
import tiktoken
from PyPDF2 import PdfReader
import streamlit as st
from openai import OpenAI
from pydantic import BaseModel, Field
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()
token = st.secrets["GITHUB_API_KEY"]
endpoint = "https://models.github.ai/inference"
client = OpenAI(base_url=endpoint,
    api_key=token)

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


def count_tokens(text, encoding_name="o200k_base"):
    enc = tiktoken.get_encoding(encoding_name)
    return len(enc.encode(text))


def llm_call_openai(model_name, messages, max_tokens, output_format):
    response = client.beta.chat.completions.parse(
        messages=messages,
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=0.9,
        model=model_name,
        response_format=output_format
    )
    return response.choices[0].message.content

def llm_resumewriter_openai(writer_prompt, output_format):
    response = client.beta.chat.completions.parse(
        messages=[
        {"role": "system", "content": "you are a resume writer and you will write a resume based on the external input suchas skillrating, suggestions, human input suggestions(if any), actual resume text"},
        {"role": "user", "content": writer_prompt},
    ],
        temperature=0.8,
        top_p=0.9,
        model='openai/gpt-4o',
        response_format=output_format
    )
    return response.choices[0].message.content


class structured_output(BaseModel):
    skills: list[str]
    resume_init_suggestions: list[str]

class StructuredResume(BaseModel):
    name: str
    contact_email: str
    phone: str
    linkedin:str
    skills: list[str]
    work_experience: list[str]  # Each dict: {job_title, company, location, start_date, end_date, achievements, technologies}
    education: list[str]        # Each dict: {degree, institution, location, start_year, end_year, gpa}
    projects: list[str]     # Each dict: {title, description, technologies}

#st.set_page_config(page_title="Resume Analyzer", page_icon=":mag_right:")
st.title("Resume Analyzer")

resume_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])

## ------------------------


## ------------------------
@st.cache_data(show_spinner=True)
def get_skills_from_resume(resume_text):
    user_prompt = f"Analyze the resume get the suggestions and top skills. \n\n{resume_text}"
    system_instruction = """ You are a resume analysis expert. When given a resume document, analyze it to provide:

    1. **Suggestive Changes**: 3-4 specific, actionable improvements to enhance the resume's impact. Focus on:
       - Quantifying achievements with metrics/numbers
       - Using Harvard-style action verbs and result-oriented language
       - Improving structure, formatting, or section organization
       - Strengthening weak bullet points with specific accomplishments
       - Adding missing technical keywords relevant to their field

    2. **Top 5 Skills**: The most relevant technical and professional skills based on frequency, recency, and industry importance.

    For each job in work experience, identify:
    - Job title, company, and duration
    - Key technologies and skills used
    - Quantifiable achievements and impact

    Output format: (in given structured format requested)"""
    model_name = "openai/gpt-4o-mini"
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt},
    ]
    skills_extract = llm_call_openai(model_name, messages, 350, structured_output)
    return json.loads(skills_extract)

if resume_file:
    resume_text = extract_text_from_pdf(resume_file)
    s = get_skills_from_resume(resume_text)
    st.subheader("Rate your top skills")
    slider_keys = []
    for skill in s["skills"]:
        slider_key = f"skill_{skill}"
        slider_keys.append(slider_key)
        st.slider(skill, min_value=0, max_value=10, value=1, key=slider_key)

    user_notes = st.text_area("Add your notes or context", key="user_notes")

    if st.button("Save Selections"):
        selected_values = {skill: st.session_state[f"skill_{skill}"] for skill in s["skills"]}
        notes = st.session_state["user_notes"]
        skills_str = "\n".join([f"{skill}: {value}" for skill, value in selected_values.items()])
        result_str = f"Skill Ratings:\n{skills_str}\n\nUser Notes:\n{notes}"
        # Save to session state for later use
        st.session_state["result_str"] = result_str
        st.session_state["selected_values"] = selected_values
        st.session_state["notes"] = notes
        st.success("Selections saved!")

    # Always show the summary and suggestions if selections are saved
    if "result_str" in st.session_state:
        with st.container(border=True):
            st.subheader("Your Skill Ratings")
            st.text(st.session_state["result_str"])
            with st.expander("Resume Suggestions"):
                for suggestion in s['resume_init_suggestions']:
                    st.write(suggestion)

    # Human input and Generate Resume button are always available after selections
    if "result_str" in st.session_state:
        human_input = st.text_input(
            "Your extra suggestions or feedback......(optional)", value="", max_chars=1000, key="human_input"
        )
        if st.button("Generate Resume"):
            if human_input.strip():
                writer_prompt = f"""Generate a resume based on the following inputs: \
Human_custom_suggestions: {human_input}\n\nskills rating by user: {st.session_state['result_str']} 
the Actual resume_text_extract: {resume_text}"""
            else:
                writer_prompt = f"""Generate a resume based on the following inputs: \
AI_suggestions: {s['resume_init_suggestions']}\n\nskills rating by user: {st.session_state['result_str']} 
the Actual resume_text_extract: {resume_text}"""
            with st.spinner("Generating resume..."):
                generated_resume = llm_resumewriter_openai(writer_prompt, output_format=StructuredResume)
            st.success("Resume generated successfully!")
            st.subheader("Generated Resume")
            with st.container(border=True):
                st.write(generated_resume)
                # st.json(generated_resume.model_dump())
                # st.download_button(
                #     label="Download Resume",
                #     data=json.dumps(generated_resume.model_dump(), indent=2),
                #     file_name="generated_resume.json",
                #     mime="application/json"
                # )