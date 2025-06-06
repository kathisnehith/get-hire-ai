import streamlit as st
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
import time
import tiktoken

# Setup
load_dotenv()
token = os.getenv("GITHUB_API_TOKEN")
endpoint = "https://models.inference.ai.azure.com"

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

# Streamlit UI
st.title("📬 Email Assistant (RAG Powered)")
query = st.text_input("Purpose of email (e.g. write an email...)", "")
persona = st.text_input("Writing to (persona) (optional)", "")
generate = st.button("Generate email")

if generate and query:
    final_prompt = f"{query} - {persona}"
    with st.spinner("Retrieving relevant context..."):
        import time
        start_time = time.time()
        results = vectorstore.similarity_search_with_score(final_prompt, k=2)
        elapsed = time.time() - start_time
    st.success(f"Context retrieved in {elapsed:.2f} seconds.")
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
    from openai import OpenAI
    client = OpenAI(base_url=endpoint, api_key=token)

    llm_prompt = f"""
    {final_prompt}
    ==== CONTEXT START ====
    {context}  
    ==== CONTEXT END ====
    """
    with st.spinner("Generating email..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert email assistant."},
                {"role": "user", "content": llm_prompt}
            ],
            temperature=0.7
        )
        final_email = response.choices[0].message.content
    st.markdown("---")
    with st.container(border=True):
        st.subheader("✉️ Generated Email")
        st.markdown(final_email)