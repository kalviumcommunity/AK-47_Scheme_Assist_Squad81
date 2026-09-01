import os
import sys
import re
from typing import List, Dict, Any, Tuple

# Ensure package imports resolve correctly when run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from pypdf import PdfReader
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

        section_name = get_section_for_offset(sections, char_start)

        page_num = 1
        if page_numbers:
            for p_num, p_start in page_numbers:
                if char_start >= p_start:
                    page_num = p_num

        chunk_metadata = {
            "source": filename,
            "chunk_index": idx,
            "position": f"Chunk {idx + 1} of {total_chunks} (tokens {t_start}-{t_end})",
            "section": section_name,
            "page": page_num,
            "token_count": len(slice_tokens),
            "total_chunks": total_chunks,
            "char_start": char_start,
            "char_end": char_end,
            "overlap_tokens": overlap_tokens if idx > 0 else 0
        }

        chunks.append({
            "text": chunk_text,
            "metadata": chunk_metadata
        })

    return chunks


def chunk_document(
    doc: Dict[str, Any],
    chunk_size: int = 350,
    overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Splits a cleaned document into text chunks based on character count with overlap.
    (Kept for backwards compatibility; token-based chunking is preferred for RAG).
    """
    return chunk_document_by_tokens(
        doc,
        chunk_size_tokens=250,
        overlap_tokens=50
    )


def load_documents_from_data_dir(data_dir: str = "data") -> List[Dict[str, Any]]:
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
                soup = BeautifulSoup(html_content, "html.parser")
                # Remove script and style elements to avoid extracting code/css
                for script_or_style in soup(["script", "style"]):
                    script_or_style.decompose()
                # Get text with newline separators to preserve line structure for boilerplate cleaning
                content = soup.get_text(separator="\n").strip()

            elif ext == ".pdf":
                # PDF loading and page-level extraction
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


def load_and_chunk_documents(
    data_dir: str = "data",
    chunk_size_tokens: int = 250,
    overlap_tokens: int = 50
) -> List[Dict[str, Any]]:
    """
    Ingests all supported documents from data_dir and splits them into token-aware chunks with attached metadata.
    """
    raw_docs = load_documents_from_data_dir(data_dir)
    all_chunks = []
    for doc in raw_docs:
        doc_chunks = chunk_document_by_tokens(
            doc,
            chunk_size_tokens=chunk_size_tokens,
            overlap_tokens=overlap_tokens
        )
        all_chunks.extend(doc_chunks)
    print(f"[INGESTION LOG] Generated {len(all_chunks)} token-aware chunks across {len(raw_docs)} document(s).")
    return all_chunks


def load_and_chunk_documents_by_tokens(
    data_dir: str = "data",
    chunk_size_tokens: int = 250,
    overlap_tokens: int = 50
) -> List[Dict[str, Any]]:
    """
    Alias for load_and_chunk_documents explicitly highlighting token-based chunking.
    """
    return load_and_chunk_documents(
        data_dir=data_dir,
        chunk_size_tokens=chunk_size_tokens,
        overlap_tokens=overlap_tokens
    )


def validate_corpus_ingestion(
    data_dir: str = "data",
    chunk_size_tokens: int = 250,
    overlap_tokens: int = 50
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes the validated corpus ingestion pipeline with strict completeness reconciliation.
    Returns (all_chunks, summary_dict).
    """
    from src.corpus_pipeline import run_corpus_ingestion, persist_pipeline_artifacts
    files, docs, chunks, failures, summary = run_corpus_ingestion(
        data_dir=data_dir,
        chunk_size_tokens=chunk_size_tokens,
        overlap_tokens=overlap_tokens
    )
    persist_pipeline_artifacts(summary, chunks)
    return chunks, summary.to_dict()


if __name__ == "__main__":
    print("=" * 60)
    print("  [INGESTION MODULE] Running token-aware ingestion & chunking test...")
    print("=" * 60)
    chunks = load_and_chunk_documents_by_tokens("data", chunk_size_tokens=250, overlap_tokens=50)
    print("-" * 60)
    print(f"Total token chunks created: {len(chunks)}")
    if chunks:
        print("\n[SAMPLE TOKEN CHUNK METADATA]:")
        import json
        print(json.dumps(chunks[0], indent=2))
    print("=" * 60)



