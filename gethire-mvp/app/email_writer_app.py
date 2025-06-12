import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from utils.doc_extract import extract_text_from_file, count_tokens

def knowledge_retrieval(pinecone_api_key, openai_api_key, final_query):
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(name='email')
    index.describe_index_stats()
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=openai_api_key,
        openai_api_base="https://models.inference.ai.azure.com"
    )
    final_query_embedding = embedding_model.embed_query(final_query)
    searchresults = index.query(namespace="email_guide",
                               vector=final_query_embedding,
                               top_k=2,
                               include_metadata=True)
    retrieved_text = [match['metadata']['text'] for match in searchresults['matches']]
    final_context = "\n-----\n".join(retrieved_text)
    return final_context

def emailwriter_main_feature(
    openai_model,
    openai_api_key,
    pinecone_api_key,
    resume_text,  # file-like object
    user_query,
    persona,
    job_details
):
    load_dotenv()
    # Compose final query
    final_query = f"{user_query} - {persona}" if persona else user_query
    # Retrieve context
    context = knowledge_retrieval(pinecone_api_key, openai_api_key, final_query)
    # Compose LLM prompt
    llm_prompt = f"""
{final_query}
==== CONTEXT START ====
{context}
==== CONTEXT END ====
User's Resume text: {resume_text}
job details: {job_details}
"""
    client = OpenAI(base_url="https://models.github.ai/inference", api_key=openai_api_key)
    response = client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": "You are an expert email writing assistant, using the provided external context for personalized email generation."},
            {"role": "user", "content": llm_prompt}
        ],
        temperature=0.7
    )
    final_email = response.choices[0].message.content
    return final_email