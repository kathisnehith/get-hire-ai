# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# import pysqlite3 as sqlite3
import streamlit as st
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import tiktoken
from PyPDF2 import PdfReader


# Setup
load_dotenv()
token = os.getenv("GITHUB_API_TOKEN")
endpoint = "https://models.inference.ai.azure.com"

client = OpenAI(base_url=endpoint, api_key=token)

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=token,
    openai_api_base=endpoint
)

# Load prebuilt vectorstore
persist_dir = "chroma_persist_email_rag"
vectorstore = Chroma(
    persist_directory=persist_dir,
    embedding_function=embedding_model,
    collection_name="email_rag"
)

def count_tokens(text, encoding_name="o200k_base"):
    enc = tiktoken.get_encoding(encoding_name)
    return len(enc.encode(text))


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

# Streamlit UI
st.title("📬 Email Assistant (RAG Powered)")

#RESUME_DOC
resume = st.file_uploader("Upload your resume or CV (optional)", type=["pdf"])
resume_summary = ""
query = st.text_input("Purpose of email (e.g. write an email...)", value="asking for referral for a job opportunity at company X", max_chars=1000)
persona = st.text_input("Writing to (persona) (optional)", value="data scientist")
generate = st.button("Generate email")

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
    final_prompt = f"{query} - {persona}"
    with st.spinner("Retrieving relevant context...", show_time=True):
        results = vectorstore.similarity_search_with_score(final_prompt, k=2)
    st.success(f"Context retrieved..............")
    retrieved = [doc.page_content for doc, _ in results]
    retrieved_metadata = [doc.metadata for doc, _ in results]
    context = "\n\n---\n\n".join(retrieved)  # Uncomment to show context
    context_tokens = count_tokens(context)
    
    st.subheader("📄 Retrieved Document Metadata")
    for i, metadata in enumerate(retrieved_metadata):
        st.markdown(f"**Document {i+1} : {metadata}**")
    # st.markdown(context)  # Uncomment to show context
    st.text(f"Total context tokens: {context_tokens}")
    st.markdown("---")
    # Generate final response with OpenAI LLM

    llm_prompt = f"""
    {final_prompt}
    ==== CONTEXT START ====
    {context}  
    ==== CONTEXT END ====
    User's Resume summary: {resume_summary}
    """
    with st.spinner("Generating email...", show_time=True):
        response = client.chat.completions.create(
            model="gpt-4o",
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