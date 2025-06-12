import streamlit as st
import time
import sys
import os
import tempfile
import pandas as pd
from dotenv import load_dotenv, find_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.linkedinsearch import search_linkedin_jobs


load_dotenv()


def jobsearch_main_feature(gemini_api_key, gemini_model, resume_upload, job_titles, locations, experience_level, date_posted, easy_apply, under_10_applicants, match_score_threshold):
    # Prepare lists and codes
    jobtitles_list = [item.strip() for item in job_titles.split(',') if item.strip()] if job_titles else []
    location_list = [item.strip() for item in locations.split(',') if item.strip()] if locations else []
    experience_code_map = {
        "Internship": "1",
        "Entry Level": "2",
        "Mid Level": "3",
        "Senior Level": "4"
    }
    experience_level_codes = ""
    if experience_level:
        experience_level_codes = ",".join([experience_code_map[exp] for exp in experience_level])
    date_posted_map = {
        "1hr": "r3600",
        "2hr": "r7200",
        "3hr": "r10800",
        "6hr": "r21600",
        "Last 24hr": "r86400",
        "Past Week": "r604800",
        "Last 30 days": "r2592000"
    }
    time_posting_codes = date_posted_map[date_posted] if date_posted else None

    print("UI Form Inputs:------------------")
    print("job titles: ", job_titles)
    print("Locations: ", locations)
    print("Experience Level: ", experience_level)
    print("Date Posted: ", date_posted)
    print("Under 10 Applicants: ", under_10_applicants)
    print("Easy Apply: ", easy_apply)
    print("---------------------------")

    # --- Run job search logic directly ---
    st.markdown("---")
    with st.spinner("Searching...", show_time=True):
        time.sleep(2)
        st.write(f"Job Titles: {job_titles},  Locations: {locations}")
        time.sleep(1)
        st.write(f"Experience: {experience_level},   Posted: {date_posted}")
        st.write(f"Easy Apply: {easy_apply},   Under 10 Applicants: {under_10_applicants}")
        if resume_upload:
            st.success(f"Using resume: {resume_upload.name}")

        st.markdown("---")
        # --- Call LinkedIn job search and display results ---
        # Only proceed if all required fields are present
        if job_titles and locations and experience_level and date_posted and resume_upload and gemini_api_key:
            st.info("Processing your resume...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_resume:
                tmp_resume.write(resume_upload.read())
                resume_path = tmp_resume.name
            st.info("Hang on!! Job search extraction, filtering, and analysis in progress...")
            st.warning("This may take 1-2 minutes depending on level of elements selected")
            st.markdown("---")
            df = search_linkedin_jobs(
                jobtitles_list,
                location_list,
                experience_level_codes,
                time_posting_codes,
                gemini_api_key,
                gemini_model,
                resume_path,
                match_score_threshold
            )

            if isinstance(df, pd.DataFrame) and not df.empty:
                st.success(f" Found {len(df)} jobs matching your criteria.")
                for idx, row in df.iterrows():
                    with st.container(border=True):
                        col1_job, col2_job = st.columns([3, 1])
                        with col1_job:
                            st.subheader(f"{row['Job_title']}")
                            st.write(f"🏢 {row['Job_company']} | 📍 {row['Job_location']}")
                            st.write(f"**Type:** {row['Job_Type']} | **Posted:** {row['Post_date']}")
                            if row['Post_link'] and row['Post_link'] != "N/A":
                                st.link_button("Apply Now 🔗", row['Post_link'], type="secondary")
                            st.markdown(f"**Description:** {row['Job_description'][:300]}{'...' if len(row['Job_description']) > 300 else ''}")
                        with col2_job:
                            st.metric("Resume Match", f"{row['score']}%")
                            st.caption(f"Match Summary: {row['match_summary']}")
                        with st.expander("🔍 Show Gemini AI Analysis", expanded=False):
                            st.markdown(f"**JD Experience:** {row['JD_exp']}")
                            st.markdown(f"**Candidate Experience:** {row['candidate_exp']}")
                            st.markdown("**Strengths:**")
                            for s in row['strengths']:
                                st.write(f"- {s}")
                            st.markdown("**Drawbacks:**")
                            for d in row['drawbacks']:
                                st.write(f"- {d}")
                            st.markdown("**Priority Needs:**")
                            for p in row['priority_needs']:
                                st.write(f"- {p}")
                            st.markdown(f"**Domain:** {row['domain']}")
                            st.markdown(f"**Sponsorship:** {row['sponsorship']}")
                            st.session_state["job_title"] = row['Job_title']
                            st.session_state["job_company"] = row['Job_company']
                            st.session_state["job_description"] = row['Job_description'][:500]
            else:
                with st.container(border=True):
                    st.warning("No jobs found matching the criteria.")
                    st.write("Please try different search parameters or check your resume file.")
        else:
            st.warning("Please fill all required fields and upload your resume.")