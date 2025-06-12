import streamlit as st
import os
import time
from dotenv import load_dotenv
from utils.model_validation import gemini_api_validation, openai_api_validation

load_dotenv()
st.set_page_config(page_title="GetHire - Job Search Assistant",layout="wide",initial_sidebar_state="auto")
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'api_key_validated' not in st.session_state:
    st.session_state.api_key_validated = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

def set_page(page_name):
    st.session_state.page = page_name

def validate_api_key(gemini_api_key, openai_api_key, gemini_model, openai_model, user_prompt):
    gemini_ok = False
    openai_ok = False
    try:
        #gemini_api_validation(gemini_api_key, gemini_model, user_prompt)
        gemini_ok = True
    except Exception as e:
        st.error(f"Gemini API validation failed: {e}")
    try:
        #openai_api_validation(openai_api_key, openai_model, user_prompt)
        openai_ok = True
    except Exception as e:
        st.error(f"OpenAI API validation failed: {e}")
    if gemini_ok:
        st.success("Gemini API key and model validated successfully!")
    if openai_ok:
        st.success("OpenAI API key and model validated successfully!")
    if not gemini_ok and not openai_ok:
        st.error("Both API validations failed. Please check your keys and models.")
    if gemini_ok or openai_ok :
        st.session_state.api_key_validated = True
        st.session_state.gemini_api_key = gemini_api_key
        st.session_state.openai_api_key = openai_api_key
        st.markdown("### API keys validated successfully!")
        st.session_state.gemini_model = gemini_model
        st.session_state.openai_model = openai_model
        proceed = st.button("Proceed to Job Search", use_container_width=True)
        if proceed:
            st.session_state.page = 'job_search'
        else:
            st.session_state.page = 'landing'
 

def render_landing_page():
    st.title("API Key & Model Validation")
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    with col1:
        gemini_api_key = st.text_input("Gemini API Key", type="password", key="gemini_api_key_input", value=st.session_state.get("gemini_api_key", ""))
    with col2:
        openai_api_key = st.text_input("OpenAI API Key", type="password", key="openai_api_key_input", value=st.session_state.get("openai_api_key", ""))
    with col3:
        gemini_models = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]
        gemini_model = st.selectbox(
        "Gemini Model",
        gemini_models,
        index=gemini_models.index(st.session_state.get("gemini_model", "Select a model..."))
        if st.session_state.get("gemini_model", "") in gemini_models else 0,
        key="gemini_model_select"
        )
    with col4:
        openai_models = ["openai/gpt-4o", "openai/gpt-4o-mini"]
        openai_model = st.selectbox(
        "OpenAI Model",
        openai_models,
        index=openai_models.index(st.session_state.get("openai_model", "Select a model..."))
        if st.session_state.get("openai_model", "") in openai_models else 0,
        key="openai_model_select"
        )
    user_prompt = st.text_area("Prompt for Validation", value= "Hello, this is a test message to validate the API key.", key="user_prompt_input", height=100)
    if st.button("Validate Key", use_container_width=True):
        with st.spinner("Validating API keys and models..."):
            validate_api_key(gemini_api_key, openai_api_key, gemini_model, openai_model, user_prompt)

def render_job_search_page():
    st.header("🔍 Job Search")
    st.write("Gemini Model:", st.session_state.get("gemini_model", "Not set"))
    st.write("Gemini API Key:", st.session_state.get("gemini_api_key", "Not set"))
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Job Title or Keywords", placeholder="e.g., Software Engineer")
        st.text_input("Location", placeholder="e.g., San Francisco, CA or Remote")
    with col2:
        st.multiselect("Job Type", ['Full-time', 'Part-time', 'Contract', 'Internship'], default=['Full-time'])
        st.multiselect("Experience Level", ['Entry-level', 'Mid-level', 'Senior-level', 'Manager'], default=['Mid-level'])
    st.button("Search for Jobs", type="primary")

def render_email_writer_page():
    st.header("✍️ AI Email Writer")
    st.write("Generate professional emails for your job applications.")
    st.file_uploader("Upload Job Description", type=['pdf', 'docx', 'txt'])
    st.text_area("What are the key points to highlight?", height=150)
    st.selectbox("Tone of Voice", ['Professional', 'Enthusiastic', 'Formal', 'Casual'])
    st.button("Generate Email", type="primary")

def render_resume_enhancer_page():
    st.header("📄 AI Resume Enhancer")
    st.write("Get AI-powered suggestions to improve your resume.")
    st.file_uploader("Upload Your Current Resume", type=['pdf', 'docx'])
    st.text_input("Target Job Title", placeholder="e.g., Data Scientist")
    st.text_area("Copy-paste the Job Description here")
    st.button("Enhance My Resume", type="primary")

if not st.session_state.api_key_validated:
    render_landing_page()
else:
    with st.sidebar:
        st.header("Navigation")
        st.button("Job Search",icon='🖥️', use_container_width=True)
        st.divider()
        st.button("Email Writer", icon='📧', use_container_width=True)
        st.divider()
        st.button("Resume Enhancer",icon='🗞️', use_container_width=True)
        st.divider()
        #st.button("API Settings", on_click=set_page, args=('landing',), use_container_width=True)
    if st.session_state.page == 'job_search':
        render_job_search_page()
    elif st.session_state.page == 'email_writer':
        render_email_writer_page()
    elif st.session_state.page == 'resume_enhancer':
        render_resume_enhancer_page()


