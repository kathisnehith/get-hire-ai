# Resume Writer 📄

A simple AI-powered resume analyzer and writer that helps improve your resume using GPT-4.

## Introduction

This tool analyzes your existing resume, extracts key skills, provides improvement suggestions, and generates an enhanced version based on your input and AI recommendations.

## Workflow

1. **Upload Resume** - Upload your PDF resume
2. **Skill Analysis** - AI extracts top 5 skills from your resume
3. **Rate Skills** - Rate your skills on a scale of 1-10
4. **Get Suggestions** - AI provides specific improvement recommendations
5. **Add Input** - Optionally add your own suggestions or feedback
6. **Generate Resume** - AI creates an improved structured resume

## Files

- **`resume_writer_app.py`** - Main Streamlit application
- **`resume_writer_dev.ipynb`** - Development notebook for testing

## Technologies Used

- **Streamlit** - Web interface
- **OpenAI GPT-4** - AI analysis and resume generation
- **Pydantic** - Structured data validation
- **PyPDF2** - PDF text extraction
- **tiktoken** - Token counting

## Features

- PDF resume upload and text extraction
- LLM-powered skill identification
- Interactive skill rating system
- Improvement suggestions
- Structured resume generation
- Human-in-the-loop Inputs

## Usage

Run the app:
```bash
streamlit run resume_writer_app.py
```

Upload your resume PDF and follow the interactive workflow to get an improved version.
