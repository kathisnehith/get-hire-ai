import os
from dotenv import load_dotenv, find_dotenv
import time
import tiktoken
from PyPDF2 import PdfReader
import pinecone
import streamlit as st
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings


# Setup
load_dotenv()
GITHUB_API_KEY = os.environ.get("GITHUB_API_KEY")#st.secrets["GITHUB_API_KEY"]
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")#st.secrets["PINECONE_API_KEY"]
endpoint = "https://models.inference.ai.azure.com"

client = OpenAI(base_url=endpoint, api_key=GITHUB_API_KEY)

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large", ## Embedding model
    openai_api_key=GITHUB_API_KEY,
    openai_api_base=endpoint
)
# Load prebuilt vectorstore index of PINECONE
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index(name='email')
# View index stats
index.describe_index_stats()


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


def count_tokens(text, encoding_name="o200k_base"):
    enc = tiktoken.get_encoding(encoding_name)
    return len(enc.encode(text))

# Streamlit UI
st.title("📬 Email Assistant (RAG Powered)")

#RESUME_DOC
resume = st.file_uploader("Upload your resume or CV (optional)", type=["pdf"])
resume_summary = ""
query = st.text_input("Purpose of email (e.g. write an email...)", value="asking for referral for a job opportunity at company X", max_chars=1000)
persona = st.text_input("Writing to (persona) (optional)", value="data scientist")
generate = st.button("Generate email")

# simple email writer functionality
def job_email_writer(resume, user_query, persona, job_title, job_company, job_description):
    resume_text = extract_text_from_pdf(resume)
    final_query = f"{user_query} - {persona}"
    final_query_embedding = embedding_model.embed_query(final_query)
    searchresults = index.query(namespace="email_guide",
                                    vector= final_query_embedding,
                                    top_k=2,
                                    include_metadata=True
                                    )
    retrieved_text = [match['metadata']['text'] for match in searchresults['matches']]
    retrieved_metadata = [match['metadata']['section'] for match in searchresults['matches']]
    context = "\n-----\n".join(retrieved_text)
    llm_prompt = f"""
    {final_query}
    ==== CONTEXT START ====
    {context}  
    ==== CONTEXT END ====
    User's Resume text: {resume_text}
    job details: {job_title}, {job_company}, {job_description}
    """
    response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert email writing assistant, using the provided external context for personalized email generation."},
                {"role": "user", "content": llm_prompt}
            ],
            temperature=0.7
    )
    final_email = response.choices[0].message.content
    return final_email

if generate and query:
    if resume is not None:
        progress_bar = st.progress(15, text="Extracting resume...")
        resume_text = extract_text_from_pdf(resume)
        progress_bar.progress(34, text="Summarizing resume...")
        resume_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
            {"role": "system", "content": "you would summarize the resume or cv doc provided and summarize based on the context of doc"},
            {"role": "user", "content": resume_text }
        ],
        temperature=0.7
        )
        progress_bar.progress(75, text="Processing summary...")
        resume_summary = resume_response.choices[0].message.content
        time.sleep(0.7)
        progress_bar.progress(100, text="Resume summarized successfully!")
        st.success("Resume summarized successfully!")
    final_query = f"{query} - {persona}"
    final_query_embedding = embedding_model.embed_query(final_query)
    with st.spinner("Retrieving relevant context...", show_time=True):
        searchresults = index.query(namespace="email_guide",
                                    vector= final_query_embedding,
                                    top_k=2,
                                    include_metadata=True
                                    )
    st.success(f"Context retrieved..............")
    retrieved_text = [match['metadata']['text'] for match in searchresults['matches']]
    retrieved_metadata = [match['metadata']['section'] for match in searchresults['matches']]
    context = "\n-----\n".join(retrieved_text)
    context_tokens = count_tokens(context)
    
    st.subheader("📄 Retrieved Document Metadata")
    for i, metadata in enumerate(retrieved_metadata):
        st.markdown(f"**Document {i+1} : {metadata}**")
    # st.markdown(context)  # Uncomment to show context
    st.markdown("---")
    st.caption(f"Total retrived_context tokens: {context_tokens}")
    
    # Generate final response with OpenAI LLM

    llm_prompt = f"""
    {final_query}
    ==== CONTEXT START ====
    {context}  
    ==== CONTEXT END ====
    User's Resume summary: {resume_summary}
    """
    st.caption(f"LLM input_prompt tokens: {count_tokens(llm_prompt)}")
    with st.spinner("Generating email...", show_time=True):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert email writing assistant, using the provided external context for personalized email generation."},
                {"role": "user", "content": llm_prompt}
            ],
            temperature=0.7
        )
        final_email = response.choices[0].message.content
    st.markdown("---")
    with st.container(border=True):
        st.subheader("✉️ Generated Email")
        st.markdown(final_email)