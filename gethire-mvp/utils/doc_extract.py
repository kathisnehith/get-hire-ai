import tiktoken
from PyPDF2 import PdfReader
import io

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


def count_tokens(text, encoding_name="o200k_base"):
    enc = tiktoken.get_encoding(encoding_name)
    return len(enc.encode(text))

def extract_text_from_file(file):
    """
    Extract text from a file-like object (PDF or DOCX in-memory upload).
    Currently supports PDF only.
    """
    if hasattr(file, 'name') and file.name.lower().endswith('.pdf'):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    # Add DOCX/text support here if needed
    return "Unsupported file type. Only PDF supported."