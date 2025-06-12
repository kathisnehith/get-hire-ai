import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import streamlit as st
from utils.doc_extract import extract_text_from_file,count_tokens



class structured_skills(BaseModel):
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
    projects: list[str] 


def llm_call(openai_api_key,openai_model,system_instruction,user_prompt,temp,tokens,structured_output):
    client = OpenAI(base_url="https://models.github.ai/inference", api_key=openai_api_key)
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt},
    ]
    response = client.beta.chat.completions.parse(
        model=openai_model,
        messages=messages,
        temperature=temp,
        max_tokens=tokens,
        response_format=structured_output 
    )
    llm_response = response.choices[0].message.content
    return llm_response  # Return as string, not parsed


@st.cache_data(show_spinner=True)
def get_skills_from_resume(openai_api_key,openai_model,temp,tokens,structured_output, resume_text):
    system_instruction = (
        "You are a resume analysis expert. When given a resume document, analyze it to provide: "
        "1. Suggestive Changes: 3-4 specific, actionable improvements to enhance the resume's impact. "
        "2. Top 5 Skills: The most relevant technical and professional skills. "
    )
    user_prompt = f"Analyze the resume get the suggestions and top skills.\n\n{resume_text}"
    skills_extract = llm_call(openai_api_key,openai_model,system_instruction,user_prompt,temp,tokens,structured_output)
    return json.loads(skills_extract)


def write_resume(openai_api_key,openai_model,final_prompt,temp,tokens,structured_output):
    system_instruction = (
        "you are a resume writer and you will write a resume based on the external input suchas skillrating, suggestions, human input suggestions(if any), actual resume text "
    )
    user_prompt = f"{final_prompt}"
    resume_rewrite = llm_call(openai_api_key,openai_model,system_instruction,user_prompt,temp,tokens,structured_output)
    return json.loads(resume_rewrite)

# ---------------
def skills_rating_suggestions(openai_api_key,openai_model,temp,tokens,structured_output, resume_text):
    skills_rate = get_skills_from_resume(openai_api_key,openai_model,temp,tokens,structured_output, resume_text)
    # Store AI suggestions in session state for later use
    st.session_state['init_suggestion'] = {'resume_init_suggestions': skills_rate['resume_init_suggestions']}
    slider_keys = []
    for skill in skills_rate["skills"]:
        slider_key = f"skill_{skill}"
        slider_keys.append(slider_key)
        with st.container():
            st.slider(skill, min_value=0, max_value=10, value=2, key=slider_key)
    if st.button("Save Selections"):
        selected_values = {skill: st.session_state[f"skill_{skill}"] for skill in skills_rate["skills"]}
        skills_str = "\n".join([f"{skill}: {value}" for skill, value in selected_values.items()])
        result_str = f"Skill Ratings:\n{skills_str}"
        st.session_state["result_str"] = result_str
        st.session_state["selected_values"] = selected_values
        st.success("Selections saved!")
    # Always show suggestions after Save Selections
    if "result_str" in st.session_state:
        with st.container(border=True):
            st.subheader("Resume Suggestions")
            for suggestion in skills_rate['resume_init_suggestions']:
                st.write(suggestion)
            with st.expander("Skills Ratings"):
                st.text(st.session_state["result_str"])
            # Add human_input text box just below the expander
            human_input = st.text_input(
                "Your extra suggestions or feedback......(optional)",
                value="",
                max_chars=1000,
                key="human_input"
            )
            st.session_state["_human_input_temp"] = human_input


def resume_enhance(openai_api_key,openai_model,human_input,temp,tokens,structured_output, resume_text, ai_suggestions):
    if "result_str" in st.session_state:
        if st.button("Generate Resume"):
            if human_input.strip():
                writer_prompt = f"""Generate a resume based on the following inputs: \
                additional_suggestions : {human_input}\n\n
                list of suggestions by AI: {ai_suggestions}\n\n 
                skills rating by user: {st.session_state['result_str']} \n
                the Actual resume_text_extract: {resume_text}"""
            else:
                writer_prompt = f"""Generate a resume based on the following inputs: \
                list of suggestions by AI: {ai_suggestions}\n\n
                skills rating by user: {st.session_state['result_str']} \n
                the Actual resume_text_extract: {resume_text}"""
            with st.spinner("Generating resume...", show_time=True):
                st.caption("Input tokens: " + str(count_tokens(writer_prompt)))
                generated_resume = write_resume(openai_api_key,openai_model,writer_prompt,temp,tokens,structured_output)
            st.success("Resume generated successfully!")
            st.subheader("Generated Resume")
            with st.container(border=True):
                for key, value in generated_resume.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}**")
                    if isinstance(value, list):
                        for item in value:
                            st.write(item)
                    else:
                        st.write(value)
            


# load_dotenv()

# st.title("Resume Enhancer-AI")
# st.markdown(
#     "This app helps you enhance your resume by analyzing it and providing suggestions for improvement. "
#     "You can also rate your skills and generate a new resume based on your inputs."
# )
# resume_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"], key="resume_enhancer_uploader")
# resume_text = extract_text_from_file(resume_file) if resume_file else ""

# openai_api_key = os.environ.get("GITHUB_API_KEY")
# openai_model = "openai/gpt-4o-mini"
# temp = 0.7
# tokens = 350
# structured_output = structured_skills

# if resume_file:
#     skills_rating_suggestions(openai_api_key, openai_model, temp, tokens, structured_output, resume_text)
#     ai_suggestions = st.session_state.get('init_suggestion', {}).get('resume_init_suggestions')
#     # Use the human_input value from session state (set inside the container)
#     human_input = st.session_state.get('_human_input_temp', "")
#     resume_enhance(openai_api_key, "openai/gpt-4o", human_input, temp, 1500, StructuredResume, resume_text, ai_suggestions)
