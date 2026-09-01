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
from src.token_counter import get_tokenizer


def detect_sections(text: str) -> List[Dict[str, Any]]:
    """
    Detects section headers (e.g., Markdown headers '#', '##', HTML tags, or title-like lines)
    and returns a list of section metadata with character offset ranges.
    """
    lines = text.splitlines(keepends=True)
    sections = []
    current_section = "General Overview"
    current_start = 0
    pos = 0

    section_header_pattern = re.compile(
        r"^(?:#{1,6}\s+(.+)|([A-Z][A-Za-z0-9\s—–\-]{2,50}:)|(?:[0-9]+\.\s+([A-Z][A-Za-z0-9\s]{2,40})))$"
    )

    for line in lines:
        match = section_header_pattern.match(line.strip())
        if match:
            # New section header found
            section_title = match.group(1) or match.group(2) or match.group(3)
            if section_title:
                section_title = section_title.strip().rstrip(":")
                if pos > current_start:
                    sections.append({
                        "section": current_section,
                        "start": current_start,
                        "end": pos
                    })
                current_section = section_title
                current_start = pos
        pos += len(line)

    sections.append({
        "section": current_section,
        "start": current_start,
        "end": pos
    })

    return sections


def get_section_for_offset(sections: List[Dict[str, Any]], char_offset: int) -> str:
    """
    Finds the section title covering a given character offset.
    """
    for sec in sections:
        if sec["start"] <= char_offset < sec["end"]:
            return sec["section"]
    return sections[-1]["section"] if sections else "General Overview"


def chunk_document_by_tokens(
    doc: Dict[str, Any],
    chunk_size_tokens: int = 250,
    overlap_tokens: int = 50,
    model_name: str = "gpt-4o-mini"
) -> List[Dict[str, Any]]:
    """
    Splits a cleaned document into chunks sized strictly by token count using tiktoken,
    incorporating controlled token overlap to preserve boundary context.
    """
    filename = doc.get("filename", "unknown_source")
    content = doc.get("content", "")
    page_numbers = doc.get("page_numbers", None)

    if not content:
        return []

    encoding = get_tokenizer(model_name)
    tokens = encoding.encode(content)
    total_tokens = len(tokens)

    if total_tokens == 0:
        return []

    sections = detect_sections(content)
    chunks = []
    
    step = chunk_size_tokens - overlap_tokens if chunk_size_tokens > overlap_tokens else chunk_size_tokens
    
    start_token_idx = 0
    token_slices = []

    while start_token_idx < total_tokens:
        end_token_idx = min(start_token_idx + chunk_size_tokens, total_tokens)
        slice_tokens = tokens[start_token_idx:end_token_idx]
        token_slices.append((start_token_idx, end_token_idx, slice_tokens))
        
        if end_token_idx >= total_tokens:
            break
        start_token_idx += step

    total_chunks = len(token_slices)

    for idx, (t_start, t_end, slice_tokens) in enumerate(token_slices):
        chunk_text = encoding.decode(slice_tokens).strip()
        
        # Calculate character offsets by decoding prefix
        char_start = len(encoding.decode(tokens[:t_start]))
        char_end = len(encoding.decode(tokens[:t_end]))


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
            page_numbers = None

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
                page_numbers = []
                current_offset = 0
                for p_idx, page in enumerate(reader.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        cleaned_page_text = page_text.strip()
                        page_numbers.append((p_idx, current_offset))
                        text_parts.append(cleaned_page_text)
                        current_offset += len(cleaned_page_text) + 1
                content = "\n".join(text_parts).strip()
                if not content:
                    raise ValueError("Extracted PDF text content is empty or unreadable.")

            # Sanitize raw text through the cleaning pipeline
            cleaned_content = clean_text(content)

            # Record document metadata and preserve source filename/identity
            documents.append({
                "filename": filename,
                "content": cleaned_content,
                "page_numbers": page_numbers
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
