import time
import os
import tempfile
import sys
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.model_validation import gemini_api_validation, openai_api_validation
from utils.doc_extract import extract_text_from_file
from app.jobsearch_app import jobsearch_main_feature
from app.email_writer_app import emailwriter_main_feature
from app.resume_enhance_app import (structured_skills, StructuredResume, skills_rating_suggestions,resume_enhance)

# Add after the existing imports at the top
st.set_page_config(
    page_title="GetHired-AI",
    page_icon="⭕️",
    layout="wide",
    initial_sidebar_state="auto"
)
load_dotenv()
# --- Session State Initialization ---
def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ''
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ''
    if 'openai_model' not in st.session_state:
        st.session_state.openai_model = ''
    if 'gemini_model' not in st.session_state:
        st.session_state.gemini_model = ''
    if 'resume_file' not in st.session_state:
        st.session_state.resume_file = None
    if 'resume_file_name' not in st.session_state:
        st.session_state.resume_file_name = None
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = None
    if 'job_search_inputs' not in st.session_state:
        st.session_state.job_search_inputs = {}
    if 'email_inputs' not in st.session_state:
        st.session_state.email_inputs = {}
    if 'resume_inputs' not in st.session_state:
        st.session_state.resume_inputs = {}


init_session_state()

def validate_api_key(gemini_api_key, openai_api_key, gemini_model, openai_model, user_prompt):
    gemini_ok = False
    openai_ok = False
    try:
        gemini_api_validation(gemini_api_key, gemini_model, user_prompt)
        gemini_ok = True
    except Exception as e:
        st.error(f"Gemini API validation failed: {e}")
    try:
        openai_api_validation(openai_api_key, openai_model, user_prompt)
        openai_ok = True
    except Exception as e:
        st.error(f"OpenAI API validation failed: {e}")
    if gemini_ok and openai_ok:
        st.success("Both Gemini and OpenAI API keys and models validated successfully!")
        return True
    else:
        if not gemini_ok and not openai_ok:
            st.error("Both API validations Failed!!! Please check your API keys")
        elif not gemini_ok:
            st.error("Gemini API validation failed. Please check your Gemini API key and model.")
        elif not openai_ok:
            st.error("OpenAI API validation failed. Please check your OpenAI API key and model.")
        return False

# --- Landing Page ---
def render_landing_page():
    st.title("Landing Page: API & Model Setup")
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    with col1:
        openai_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key, key="openai_api_key_input")
    with col2:
        gemini_key = st.text_input("Gemini API Key", type="password", value=st.session_state.gemini_api_key, key="gemini_api_key_input")
    with col3:
        openai_model = st.selectbox("OpenAI Model", ["openai/gpt-4o", "openai/gpt-4o-mini"],
            index=["openai/gpt-4o", "openai/gpt-4o-mini"].index(st.session_state.openai_model) if st.session_state.openai_model in ["openai/gpt-4o", "openai/gpt-4o-mini"] else 0,
            key="openai_model_box")
    with col4:
        gemini_model = st.selectbox("Gemini Model", ["gemini-2.0-flash-lite", "gemini-2.0-flash"],
            index=["gemini-2.0-flash-lite", "gemini-2.0-flash"].index(st.session_state.gemini_model) if st.session_state.gemini_model in ["gemini-2.0-flash-lite", "gemini-2.0-flash"] else 0,
            key="gemini_model_box")
    prompt_text = st.text_input("Prompt for Validation", value="Hello, this is a test message to validate the API key.", key="default_prompt_input")
    # Only show button if all required fields are filled
    if openai_key and gemini_key is not None:
        if st.button("Validate API", icon= '🗝️', use_container_width=True):
            with st.spinner("Validating API keys and models..."):
                valid = validate_api_key(gemini_key, openai_key, gemini_model, openai_model, prompt_text)
            if valid:
                st.session_state["openai_api_key"] = openai_key
                st.session_state["gemini_api_key"] = gemini_key
                st.session_state["openai_model"] = openai_model
                st.session_state["gemini_model"] = gemini_model
                st.session_state["api_validated"] = True
    if st.session_state.get("api_validated"):    
        if st.button("Launch", icon='🚀', use_container_width=True):    
            st.session_state.page = 'main'
    else:
        st.info("Please enter both API keys")
    
# --- Helper Functions ---
def render_resume_uploader(key_suffix=""):
    """Centralized resume uploader component that syncs across all features"""
    # Show current resume status if one exists
    if st.session_state.resume_file is not None:
        st.success(f"✅ Resume already uploaded: **{st.session_state.resume_file_name}** ({st.session_state.resume_file.size / 1024 / 1024:.2f} MB)")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💡 This resume will be used across all features (Job Search, Email Writer, Resume Enhancer)")
        with col2:
            if st.button("🗑️ Remove Resume", key=f"remove_resume_{key_suffix}"):
                st.session_state.resume_file = None
                st.session_state.resume_file_name = None
                st.session_state.resume_text = None
                st.rerun()
    
    # File uploader (only show if no resume is uploaded)
    if st.session_state.resume_file is None:
        uploaded_file = st.file_uploader(
            "📄 Upload your resume (will be shared across all features)",
            type=["pdf"],
            help="Limit 32MB per file. This resume will be automatically available in Job Search, Email Writer, and Resume Enhancer.",
            key=f"global_resume_uploader_{key_suffix}"
        )
        
        if uploaded_file is not None:
            # Store in session state
            st.session_state.resume_file = uploaded_file
            st.session_state.resume_file_name = uploaded_file.name
            try:
                st.session_state.resume_text = extract_text_from_file(uploaded_file)
                st.success(f"✅ Resume uploaded successfully: **{uploaded_file.name}**")
                st.info("🔄 This resume is now available across all features!")
                st.rerun()
            except Exception as e:
                st.error(f"Error processing resume: {e}")
                st.session_state.resume_file = None
                st.session_state.resume_file_name = None
                st.session_state.resume_text = None
    
    return st.session_state.resume_file

# --- Helper Functions ---
def get_resume_extract():
    if st.session_state.resume_text is not None:
        return st.session_state.resume_text
    elif st.session_state.resume_file is not None:
        try:
            resume_text = extract_text_from_file(st.session_state.resume_file)
            st.session_state.resume_text = resume_text  # Cache it
            return resume_text
        except Exception as e:
            return f"Error extracting resume: {e}"
    return "No resume uploaded."

# --- Sidebar Navigation ---
def render_sidebar():
    st.sidebar.header("Navigation")
    # Show resume status in sidebar
    if st.session_state.resume_file is not None:
        st.sidebar.caption(f"📄 Resume: {st.session_state.resume_file_name}")
    else:
        st.sidebar.caption("📄 No resume uploaded")
    st.sidebar.divider()
    if st.sidebar.button("Job Search",icon='🖥️', use_container_width=True):
        st.session_state.page = 'job_search'
    if st.sidebar.button("Email Writer", icon='📧', use_container_width=True):
        st.session_state.page = 'email_writer'
    if st.sidebar.button("Resume Enhancer", icon='🗞️', use_container_width=True):
        st.session_state.page = 'resume_enhancer'
    st.sidebar.divider()
    st.sidebar.button("API/Model Settings", icon='🔐', use_container_width=True, on_click=lambda: st.session_state.update(page='landing'))

# --- Job Search Page ---
def render_job_search_page():
    st.header("🔍 Job Search")
    # Use centralized resume uploader
    uploaded_resume_file = st.file_uploader("Drag and drop file here",type=["pdf"],help="Limit 32MB per file.PDF",key="resume_jobsearch_uploader")
    if uploaded_resume_file is not None:
        st.session_state.resume_file = uploaded_resume_file
        st.session_state.resume_file_name = uploaded_resume_file.name
        st.write(f"Uploaded: {uploaded_resume_file.name} ({uploaded_resume_file.size / 1024 / 1024:.2f} MB)")
        render_resume_uploader("job_search")
    st.markdown("---") 
    prev_inputs= st.session_state.get('job_search_inputs', {})
    
    # Create two rows of columns
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    with col1:
        job_titles = st.text_input("Enter job titles separated by commas",placeholder="e.g., Data Engineer, \"ML Engineer\"....",
        help="Use quotes for precise job titles scrape",key="jobtitle_input",value=prev_inputs.get("job_title", ""))
    with col2:
        locations = st.text_input("Enter locations separated by commas",placeholder="e.g., New York, Texas, California, USA",
        help="use locations of states or countries",key="location_input",value=prev_inputs.get("location", ""))
    # Second row inputs
    with col3:
        experience_level = st.multiselect("Experience level",["Internship","Entry Level", "Mid Level", "Senior Level"],
        help="Select one or more experience levels",key="experience_select",default=prev_inputs.get("experience", []))
    with col4:
        date_posted = st.selectbox("Date Posted",["1hr", "2hr", "3hr", "6hr", "Last 24hr","Past Week", "Last 30 days"],
        help="Select the time frame-focused for todau's job postings",index=(["1hr", "2hr", "3hr", "6hr", "Last 24hr", "Past Week", "Last 30 days"].index(prev_inputs.get("date_posted")) if prev_inputs.get("date_posted") in ["1hr", "2hr", "3hr", "6hr", "Last 24hr", "Past Week", "Last 30 days"] else 0),
        key="date_posted_select")
    # Toggle options (outside form)
    with col5:
        easy_apply = st.toggle("Easy Apply", value=prev_inputs.get("easy_apply", False), key="easy_apply_form_toggle")
    with col6:
        under_10_applicants = st.toggle("Under 10 Applicants", value=prev_inputs.get("under_10_applicants", False), key="under_10_form_toggle")
    match_score_threshold = st.slider("Minimum Match Score", min_value=0, max_value=100, value=prev_inputs.get("match_score_threshold", 44))

    if st.button("Search for Jobs", key="search_jobs_btn"):
        st.session_state.job_search_inputs = {
            'job_title': job_titles,
            'location': locations,
            'experience': experience_level,
            'date_posted': date_posted,
            'easy_apply': easy_apply,
            'under_10_applicants': under_10_applicants,
            'match_score_threshold': match_score_threshold
        }
        #st.success("Job search submitted!")
        jobsearch_main_feature(
            st.session_state.gemini_api_key,
            st.session_state.gemini_model,
            uploaded_resume_file,
            job_titles,
            locations,
            experience_level,
            date_posted,
            easy_apply,
            under_10_applicants,
            match_score_threshold
        )
# --- Email Writer Page ---
def render_email_writer_page():
    st.header("✍️ AI Email Writer")
    
    # Use centralized resume uploader
    resume_file = render_resume_uploader("email")
    resume_extract = get_resume_extract()
    
    prev_email_inputs = st.session_state.get('email_inputs', {})
    with st.container(border=True):
        emailpurpose = st.text_area("What's the purpose of email?", height=68, value=prev_email_inputs.get("emailpurpose","asking for referral for a job opportunity at company X"), max_chars=1000,key="email_purpos_input")
        col1, col2 = st.columns(2)
        with col1: 
            persona = st.text_input("Writing to (persona) (optional)", placeholder="data scientist or Hiring Manager", value=prev_email_inputs.get("persona", ""), key="persona_input")
        with col2:
            tone = st.selectbox("Tone of Email", ['Professional', 'Enthusiastic', 'Formal', 'Casual'], index=['Professional', 'Enthusiastic', 'Formal', 'Casual'].index(prev_email_inputs.get("tone", "Professional")), key="tone_input")
        job_details = st.text_input("Job Details(optional)", placeholder="e.g., job title, company name, job description", value="", key="job_details_input")
    if st.button("Generate Email", key="generate_email_btn"):
        if not resume_file:
            st.error("Please upload your resume first.")
            return
        if not emailpurpose:
            st.error("Please enter the email purpose.")
            return
        with st.spinner("Generating email...", show_time=True):
            email = emailwriter_main_feature(
                openai_model=st.session_state.openai_model,
                openai_api_key=st.session_state.openai_api_key,
                pinecone_api_key=st.secrets["PINECONE_API_KEY"],
                resume_text=resume_extract,
                user_query=emailpurpose,
                persona=persona,
                job_details=job_details
            )
            st.session_state.email_inputs = {
                'resume_file': resume_file,
                'resume_extract': resume_extract,
                'emailpurpose': emailpurpose,
                'persona': persona,
                'tone': tone,
                'job_details': job_details
            }
        st.success("Email generated!")
        with st.container(border=True):
            st.markdown(f"**Generated Email:**\n\n{email}")

# --- Resume Enhancer Page ---
def render_resume_enhancer_page():
    st.header("Resume Analyzer")
    # Use centralized resume uploader
    resume_file = render_resume_uploader("resume")
    resume_text = get_resume_extract()

    openai_api_key = st.session_state.get("openai_api_key")
    openai_model = st.session_state.get("openai_model")
    temp = 0.7
    tokens = 350
    structured_output = structured_skills

    if resume_file:
        # Call the skills rating and suggestions UI
        skills_rating_suggestions(openai_api_key, openai_model, temp, tokens, structured_output, resume_text)
        ai_suggestions = st.session_state.get('init_suggestion', {}).get('resume_init_suggestions')
        # Use the human_input value from session state (set inside the container)
        human_input = st.session_state.get('_human_input_temp', "")
        resume_enhance(openai_api_key, "openai/gpt-4o", human_input, temp, 1500, StructuredResume, resume_text, ai_suggestions)

# --- Main Page Controller ---
if st.session_state.page == 'landing':
    render_landing_page()
else:
    render_sidebar()
    if st.session_state.page == 'main' or st.session_state.page == 'job_search':
        render_job_search_page()
    elif st.session_state.page == 'email_writer':
        render_email_writer_page()
    elif st.session_state.page == 'resume_enhancer':
        render_resume_enhancer_page()


