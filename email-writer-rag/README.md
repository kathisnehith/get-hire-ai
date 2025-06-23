# Email Writer RAG 📬

A Retrieval-Augmented Generation (RAG) system for intelligent email composition using vector databases and Large Language Models (LLMs).

## Overview

This project implements an AI-powered email writing assistant that uses RAG to generate personalized emails based on context retrieved from a knowledge base. The system supports both Pinecone and ChromaDB as vector databases for storing and retrieving relevant email writing guidance.

## Features

- **RAG-Powered Email Generation**: Uses vector similarity search to retrieve relevant context for email composition
- **Resume Integration**: Optionally incorporates user's resume/CV for personalized email content
- **Dual Vector Database Support**: 
  - Pinecone (cloud-based vector database)
  - ChromaDB (local vector database)
- **Interactive Streamlit Interface**: User-friendly web interface for email generation
- **Token Counting**: Monitors and displays token usage for cost optimization

## Files Description

### Core Applications
- **`email_pinecone_rag_app.py`** - Main Streamlit application using Pinecone as the vector database
- **`email_chroma_rag_app.py`** - Local alternative Streamlit application using ChromaDB as the vector database

### Jupyter Notebooks
- **`pinecone_init.ipynb`** - Notebook for initializing and populating the Pinecone vector database
- **`chroma_init_dev.ipynb`** - Notebook for initializing and populating the ChromaDB vector database
- **`email_pinecone_query.ipynb`** - Development notebook for testing Pinecone queries and RAG functionality

### Data Storage
- **`chroma_persist_email_rag/`** - Directory containing the storage persisted ChromaDB vectors database



### Using the Interface

1. **Upload Resume (Optional)**: Upload a PDF resume/CV for personalized email generation
2. **Enter Email Purpose**: Describe what kind of email you want to write (e.g., "asking for referral for a job opportunity at company X")
3. **Specify Persona (Optional)**: Define who you're writing to (e.g., "data scientist", "hiring manager")
4. **Generate Email**: Click the generate button to create your personalized email

## Technical Architecture

### RAG Pipeline
1. **Query Embedding**: User input is converted to vector embeddings using OpenAI's text-embedding-3-large model
2. **Similarity Search**: Vector database retrieves the most relevant context based on semantic similarity
3. **Context Augmentation**: Retrieved context is combined with user input and resume summary
4. **Email Generation**: GPT-4o-mini generates the final email using the augmented prompt

### Models Used
- **Embedding Model**: OpenAI text-embedding-3-large
- **Language Model**: GPT-4o-mini(Azure AI Models endpoint via GitHub)

## Development Notes

- The system uses tiktoken for accurate token counting
- Progress bars provide user feedback during processing
- Both vector database implementations offer similar functionality
- ChromaDB version is suitable for local development and deployment
- Pinecone version is better for production deployments requiring scalability

## Troubleshooting

- Ensure all API keys are correctly set in environment variables
- For ChromaDB issues, check that the persist directory exists and has proper permissions
- For Pinecone issues, verify the index name and namespace are correctly configured
- Check token limits if experiencing API errors

## Future Enhancements

- Support for additional file formats (DOCX, TXT)
- Email template customization
- Batch email generation
- Integration with gmail client
- Advanced automated persona input
