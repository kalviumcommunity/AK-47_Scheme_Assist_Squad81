import os
from typing import List, Dict, Any

try:
    from bs4 import BeautifulSoup
    _BS4_AVAILABLE = True
except ImportError:
    _BS4_AVAILABLE = False

try:
    from pypdf import PdfReader
    _PYPDF_AVAILABLE = True
except ImportError:
    _PYPDF_AVAILABLE = False

from src.cleaning import clean_text


def load_documents_from_data_dir(data_dir: str = "data") -> List[Dict[str, str]]:
    """
    Ingests PDF, HTML, Markdown, and TXT documents from the specified data directory.
    Cleans raw extracted text of boilerplate, normalizes spaces/encoding, and skips unsupported formats.
    """
    documents = []
    if not os.path.exists(data_dir):
        print(f"[INGESTION WARNING] Data directory '{data_dir}' does not exist.")
        return documents

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        if not os.path.isfile(filepath) or filename.startswith("."):
            continue

        _, ext = os.path.splitext(filename.lower())

        # Supported format check
        if ext not in [".txt", ".md", ".html", ".htm", ".pdf"]:
            print(f"[INGESTION WARNING] Skipping unsupported file format: '{filename}'")
            continue

        try:
            content = ""
            if ext in [".txt", ".md"]:
                # Text/Markdown loading
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            elif ext in [".html", ".htm"]:
                # HTML loading and text extraction
                with open(filepath, "r", encoding="utf-8") as f:
                    html_content = f.read()
                if _BS4_AVAILABLE:
                    soup = BeautifulSoup(html_content, "html.parser")
                    # Remove script and style elements to avoid extracting code/css
                    for script_or_style in soup(["script", "style"]):
                        script_or_style.decompose()
                    # Get text with newline separators to preserve line structure for boilerplate cleaning
                    content = soup.get_text(separator="\n").strip()
                else:
                    import re
                    # Fallback basic tag stripper
                    content = re.sub(r"<[^>]+>", " ", html_content).strip()

            elif ext == ".pdf":
                # PDF loading and extraction
                if not _PYPDF_AVAILABLE:
                    raise ImportError("pypdf is required to extract text from PDF files.")
                reader = PdfReader(filepath)
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                content = "\n".join(text_parts).strip()
                if not content:
                    raise ValueError("Extracted PDF text content is empty or unreadable.")

            # Sanitize raw text through the cleaning pipeline
            cleaned_content = clean_text(content)

            # Record document and preserve source filename/identity
            documents.append({
                "filename": filename,
                "content": cleaned_content
            })

            # Confirm intake with length and preview
            preview = cleaned_content[:200].replace("\n", " ")
            if len(cleaned_content) > 200:
                preview += "..."
            print(f"[INGESTION SUCCESS] Loaded '{filename}' (Raw: {len(content)} chars, Cleaned: {len(cleaned_content)} chars) - Sample: \"{preview}\"")

        except Exception as e:
            print(f"[INGESTION ERROR] Failed to load '{filename}': {e}")

    print(f"[INGESTION LOG] Successfully ingested {len(documents)} document(s) from '{data_dir}/'.")
    return documents


def ingest_and_chunk_documents(
    data_dir: str = "data",
    strategy: str = "recursive",
    chunk_size: int = 500,
    chunk_overlap: int = 80
) -> List[Dict[str, Any]]:
    """
    Ingests documents from data directory and splits them into chunks
    using the specified chunking strategy ('recursive', 'paragraph', 'sentence', 'fixed', 'fixed_overlap').
    """
    from src.chunking import (
        fixed_size_chunks,
        fixed_size_overlap_chunks,
        paragraph_chunks,
        sentence_chunks,
        recursive_character_chunks,
    )

    documents = load_documents_from_data_dir(data_dir)
    all_chunks = []

    for doc in documents:
        filename = doc.get("filename", "unknown_doc")
        content = doc.get("content", "")

        if strategy == "fixed":
            chunks = fixed_size_chunks(content, size=chunk_size, overlap=0, source_doc=filename)
        elif strategy == "fixed_overlap":
            chunks = fixed_size_overlap_chunks(content, size=chunk_size, overlap=chunk_overlap, source_doc=filename)
        elif strategy == "paragraph":
            chunks = paragraph_chunks(content, max_size=chunk_size * 2, source_doc=filename)
        elif strategy == "sentence":
            chunks = sentence_chunks(content, max_size=chunk_size, overlap_sentences=1, source_doc=filename)
        else:  # default recursive
            chunks = recursive_character_chunks(content, chunk_size=chunk_size, chunk_overlap=chunk_overlap, source_doc=filename)

        for c in chunks:
            chunk_dict = c.to_dict()
            # Also provide 'content' key for backward compatibility with SimpleRetriever
            chunk_dict["content"] = c.text
            all_chunks.append(chunk_dict)

    print(f"[CHUNKING LOG] Generated {len(all_chunks)} total chunks using '{strategy}' strategy across {len(documents)} document(s).")
    return all_chunks
