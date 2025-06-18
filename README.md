# GetHired AI

AI-powered job search assistant with automated job matching, email generation, and resume analysis.

## Features

- **Job Search**: LinkedIn job scraping with AI-powered resume matching
- **Email Writer**: Generate personalized job application emails using AI
- **Resume Enhancer**: AI-driven resume analysis and improvement suggestions

## Additional Components

- **Email RAG Apps**: Standalone email generation with vector databases
  - `email_chroma_rag_app.py` - ChromaDB-powered email generation
  - `email_pinecone_rag_app.py` - Pinecone-powered email generation
- **Development Notebooks**: Database initialization and testing
  - `chroma_init_dev.ipynb` - ChromaDB setup and email knowledge base creation
  - `pinecone_init.ipynb` - Pinecone vector database initialization
  - `email_pinecone_query.ipynb` - Email query testing with Pinecone

## Tech Stack

- **Frontend**: Streamlit
- **AI Models**: OpenAI GPT-4, Google Gemini
- **Vector DB**: Pinecone, ChromaDB
- **Languages**: Python

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Google Gemini API Key
- Pinecone API Key

### Installation
```bash
git clone <repository-url>
cd get-hire-ai
pip install -r requirements.txt
```

### Setup
1. Create `.env` file:
```env
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
```

2. Run the application:
```bash
streamlit run gethire-mvp/app/main_app.py
```

## Usage

1. **API Setup**: Enter your API keys on the landing page
2. **Upload Resume**: Upload your PDF resume (shared across all features)
3. **Job Search**: Search for jobs with AI matching scores
4. **Generate Emails**: Create personalized application emails
5. **Enhance Resume**: Get AI-powered improvement suggestions

## RAG Components Usage

### Standalone Email Apps
If you prefer to use the RAG email generation separately:

**ChromaDB Version:**
```bash
streamlit run email_chroma_rag_app.py
```

**Pinecone Version:**
```bash
streamlit run email_pinecone_rag_app.py
```

### Database Setup (Development)
Initialize vector databases for email knowledge base:

**ChromaDB Setup:**
```bash
jupyter notebook chroma_init_dev.ipynb
```

**Pinecone Setup:**
```bash
jupyter notebook pinecone_init.ipynb
```

## Project Structure

```
gethire-mvp/
├── app/
│   ├── main_app.py           # Main application
│   ├── jobsearch_app.py      # Job search feature
│   ├── email_writer_app.py   # Email generation
│   └── resume_enhance_app.py # Resume analysis
├── backend/
│   └── linkedinsearch.py     # LinkedIn scraper
└── utils/
    ├── doc_extract.py        # Document processing
    └── model_validation.py   # API validation

# Additional RAG Components
├── email_chroma_rag_app.py   # ChromaDB email app
├── email_pinecone_rag_app.py # Pinecone email app
├── chroma_init_dev.ipynb     # ChromaDB setup notebook
├── pinecone_init.ipynb       # Pinecone setup notebook
└── chroma_persist_email_rag/ # Local ChromaDB storage
```

## License

MIT License
