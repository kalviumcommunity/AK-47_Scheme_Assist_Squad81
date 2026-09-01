import os
import sys
import re
from typing import List, Dict, Any

# Ensure package imports resolve correctly when run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from pypdf import PdfReader
from src.cleaning import clean_text


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


def chunk_document(
    doc: Dict[str, Any],
    chunk_size: int = 350,
    overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Splits a cleaned document into overlapping text chunks, attaching consistent
    metadata (source, section, position, page, etc.) to every chunk.
    """
    filename = doc.get("filename", "unknown_source")
    content = doc.get("content", "")
    page_numbers = doc.get("page_numbers", None)  # List of (page_num, char_offset) for PDFs

    if not content:
        return []

    sections = detect_sections(content)
    chunks = []
    content_len = len(content)

    start = 0
    raw_chunks = []

    # Sliding window chunking
    while start < content_len:
        end = min(start + chunk_size, content_len)
        
        # Try to break at a sentence or word boundary if not at end of text
        if end < content_len:
            boundary = content.rfind(". ", start + chunk_size // 2, end)
            if boundary != -1:
                end = boundary + 1
            else:
                space_boundary = content.rfind(" ", start + chunk_size // 2, end)
                if space_boundary != -1:
                    end = space_boundary

        chunk_text = content[start:end].strip()
        if chunk_text:
            raw_chunks.append((chunk_text, start, end))

        if end >= content_len:
            break
        start = max(end - overlap, start + 1)

    total_chunks = len(raw_chunks)

    for idx, (text_chunk, char_start, char_end) in enumerate(raw_chunks):
        # Determine section metadata
        section_name = get_section_for_offset(sections, char_start)

        # Determine page metadata (if page_numbers available, e.g. for PDFs)
        page_num = 1
        if page_numbers:
            for p_num, p_start in page_numbers:
                if char_start >= p_start:
                    page_num = p_num

        chunk_metadata = {
            "source": filename,
            "chunk_index": idx,
            "position": f"Chunk {idx + 1} of {total_chunks} (chars {char_start}-{char_end})",
            "section": section_name,
            "page": page_num,
            "total_chunks": total_chunks,
            "char_start": char_start,
            "char_end": char_end
        }

        chunks.append({
            "text": text_chunk,
            "metadata": chunk_metadata
        })

    return chunks


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


def load_and_chunk_documents(data_dir: str = "data", chunk_size: int = 350, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Ingests all supported documents from data_dir and splits them into chunks with attached metadata.
    """
    raw_docs = load_documents_from_data_dir(data_dir)
    all_chunks = []
    for doc in raw_docs:
        doc_chunks = chunk_document(doc, chunk_size=chunk_size, overlap=overlap)
        all_chunks.extend(doc_chunks)
    print(f"[INGESTION LOG] Generated {len(all_chunks)} chunks across {len(raw_docs)} document(s).")
    return all_chunks


if __name__ == "__main__":
    print("=" * 60)
    print("  [INGESTION MODULE] Running direct file ingestion & chunking test...")
    print("=" * 60)
    # Run ingestion & chunking from standard data directory
    chunks = load_and_chunk_documents("data")
    print("-" * 60)
    print(f"Total chunks created: {len(chunks)}")
    if chunks:
        print("\n[SAMPLE CHUNK METADATA STRUCTURE]:")
        import json
        print(json.dumps(chunks[0], indent=2))
    print("=" * 60)


