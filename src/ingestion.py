import os
import re
from typing import List, Dict, Any, Tuple

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


# ============================================================
# SECTION DETECTION
# ============================================================

def detect_sections(text: str) -> List[Dict[str, Any]]:
    """
    Detect section headers such as:
    - Markdown headers (#, ##)
    - Title-like lines ending with :
    - Numbered headings (1. Introduction)

    Returns section metadata with character offsets.
    """

    lines = text.splitlines(keepends=True)

    sections = []
    current_section = "General Overview"
    current_start = 0
    pos = 0

    section_header_pattern = re.compile(
        r"^(?:"
        r"#{1,6}\s+(.+)"
        r"|([A-Z][A-Za-z0-9\s—–\-]{2,50}:)"
        r"|(?:[0-9]+\.\s+([A-Z][A-Za-z0-9\s]{2,40}))"
        r")$"
    )

    for line in lines:
        stripped_line = line.strip()
        match = section_header_pattern.match(stripped_line)

        if match:
            section_title = (
                match.group(1)
                or match.group(2)
                or match.group(3)
            )

            if section_title:
                section_title = section_title.strip().rstrip(":")

                # Save previous section
                if pos > current_start:
                    sections.append({
                        "section": current_section,
                        "start": current_start,
                        "end": pos
                    })

                # Start new section
                current_section = section_title
                current_start = pos

        pos += len(line)

    # Add final section
    sections.append({
        "section": current_section,
        "start": current_start,
        "end": pos
    })

    return sections


def get_section_for_offset(
    sections: List[Dict[str, Any]],
    char_offset: int
) -> str:
    """
    Returns the section name for a given character offset.
    """

    for section in sections:
        if section["start"] <= char_offset < section["end"]:
            return section["section"]

    if sections:
        return sections[-1]["section"]

    return "General Overview"


# ============================================================
# TOKEN-BASED CHUNKING
# ============================================================

def chunk_document_by_tokens(
    doc: Dict[str, Any],
    chunk_size_tokens: int = 250,
    overlap_tokens: int = 50,
    model_name: str = "gpt-4o-mini"
) -> List[Dict[str, Any]]:
    """
    Splits a document into chunks based strictly on token count.

    Features:
    - Token-aware chunking using tokenizer
    - Configurable chunk size
    - Configurable overlap
    - Section metadata
    - Page metadata for PDFs
    - Character offsets
    """

    filename = doc.get("filename", "unknown_source")
    content = doc.get("content", "")
    page_numbers = doc.get("page_numbers")

    if not content:
        return []

    # Validate chunk configuration
    if chunk_size_tokens <= 0:
        raise ValueError("chunk_size_tokens must be greater than 0.")

    if overlap_tokens < 0:
        raise ValueError("overlap_tokens cannot be negative.")

    if overlap_tokens >= chunk_size_tokens:
        raise ValueError(
            "overlap_tokens must be smaller than chunk_size_tokens."
        )

    # Get tokenizer
    encoding = get_tokenizer(model_name)

    # Convert text to tokens
    tokens = encoding.encode(content)
    total_tokens = len(tokens)

    if total_tokens == 0:
        return []

    # Detect document sections
    sections = detect_sections(content)

    chunks = []

    # Calculate movement between chunks
    step = chunk_size_tokens - overlap_tokens

    start_token_idx = 0
    token_slices = []

    # Create token windows
    while start_token_idx < total_tokens:

        end_token_idx = min(
            start_token_idx + chunk_size_tokens,
            total_tokens
        )

        slice_tokens = tokens[
            start_token_idx:end_token_idx
        ]

        token_slices.append(
            (
                start_token_idx,
                end_token_idx,
                slice_tokens
            )
        )

        # Stop at document end
        if end_token_idx >= total_tokens:
            break

        start_token_idx += step

    total_chunks = len(token_slices)

    # ========================================================
    # BUILD CHUNK OBJECTS
    # ========================================================

    for idx, (
        token_start,
        token_end,
        slice_tokens
    ) in enumerate(token_slices):

        # Convert tokens back to text
        chunk_text = encoding.decode(slice_tokens).strip()

        if not chunk_text:
            continue

        # Calculate character offsets
        char_start = len(
            encoding.decode(tokens[:token_start])
        )

        char_end = len(
            encoding.decode(tokens[:token_end])
        )

        # Find section
        section_name = get_section_for_offset(
            sections,
            char_start
        )

        # Find PDF page number
        page_num = 1

        if page_numbers:
            for page_number, page_start in page_numbers:
                if char_start >= page_start:
                    page_num = page_number
                else:
                    break

        # Metadata
        chunk_metadata = {
            "source": filename,

            "chunk_index": idx,

            "chunk_id": f"{filename}_chunk_{idx}",

            "position": (
                f"Chunk {idx + 1} of {total_chunks} "
                f"(tokens {token_start}-{token_end})"
            ),

            "section": section_name,

            "page": page_num,

            "token_count": len(slice_tokens),

            "total_chunks": total_chunks,

            "char_start": char_start,

            "char_end": char_end,

            "overlap_tokens": (
                overlap_tokens if idx > 0 else 0
            )
        }

        chunks.append({
            "text": chunk_text,

            # Backward compatibility
            "content": chunk_text,

            "metadata": chunk_metadata
        })

    return chunks


# ============================================================
# DOCUMENT LOADING
# ============================================================

def load_documents_from_data_dir(
    data_dir: str = "data"
) -> List[Dict[str, Any]]:
    """
    Loads documents from the data directory.

    Supported formats:
    - TXT
    - Markdown
    - HTML
    - PDF

    Also cleans the extracted text.
    """

    documents = []

    if not os.path.exists(data_dir):

        print(
            f"[INGESTION WARNING] "
            f"Data directory '{data_dir}' does not exist."
        )

        return documents

    # Sort files for consistent ingestion
    filenames = sorted(os.listdir(data_dir))

    for filename in filenames:

        filepath = os.path.join(
            data_dir,
            filename
        )

        # Skip folders and hidden files
        if (
            not os.path.isfile(filepath)
            or filename.startswith(".")
        ):
            continue

        _, ext = os.path.splitext(
            filename.lower()
        )

        supported_formats = [
            ".txt",
            ".md",
            ".html",
            ".htm",
            ".pdf"
        ]

        # Skip unsupported files
        if ext not in supported_formats:

            print(
                f"[INGESTION WARNING] "
                f"Skipping unsupported file format: "
                f"'{filename}'"
            )

            continue

        try:

            content = ""
            page_numbers = None

            # =================================================
            # TXT / MARKDOWN
            # =================================================

            if ext in [".txt", ".md"]:

                with open(
                    filepath,
                    "r",
                    encoding="utf-8"
                ) as file:

                    content = file.read()

            # =================================================
            # HTML
            # =================================================

            elif ext in [".html", ".htm"]:

                with open(
                    filepath,
                    "r",
                    encoding="utf-8"
                ) as file:

                    html_content = file.read()

                if _BS4_AVAILABLE:

                    soup = BeautifulSoup(
                        html_content,
                        "html.parser"
                    )

                    # Remove unwanted HTML content
                    for element in soup(
                        ["script", "style", "nav", "footer"]
                    ):
                        element.decompose()

                    # Extract readable text
                    content = soup.get_text(
                        separator="\n"
                    ).strip()

                else:

                    # Basic HTML fallback
                    content = re.sub(
                        r"<[^>]+>",
                        " ",
                        html_content
                    )

                    content = re.sub(
                        r"\s+",
                        " ",
                        content
                    ).strip()

            # =================================================
            # PDF
            # =================================================

            elif ext == ".pdf":

                if not _PYPDF_AVAILABLE:

                    raise ImportError(
                        "pypdf is required for PDF extraction."
                    )

                reader = PdfReader(filepath)

                text_parts = []

                page_numbers = []

                current_offset = 0

                for page_index, page in enumerate(
                    reader.pages,
                    start=1
                ):

                    page_text = page.extract_text()

                    if page_text:

                        cleaned_page_text = (
                            page_text.strip()
                        )

                        # Store page offset
                        page_numbers.append(
                            (
                                page_index,
                                current_offset
                            )
                        )

                        text_parts.append(
                            cleaned_page_text
                        )

                        current_offset += (
                            len(cleaned_page_text) + 1
                        )

                content = "\n".join(
                    text_parts
                ).strip()

                if not content:

                    raise ValueError(
                        "Extracted PDF text is empty "
                        "or unreadable."
                    )

            # =================================================
            # CLEAN DOCUMENT
            # =================================================

            cleaned_content = clean_text(content)

            if not cleaned_content:

                print(
                    f"[INGESTION WARNING] "
                    f"'{filename}' contains no usable text."
                )

                continue

            # =================================================
            # STORE DOCUMENT
            # =================================================

            documents.append({

                "filename": filename,

                "content": cleaned_content,

                "page_numbers": page_numbers

            })

            # Preview
            preview = cleaned_content[
                :200
            ].replace("\n", " ")

            if len(cleaned_content) > 200:
                preview += "..."

            print(
                f"[INGESTION SUCCESS] "
                f"Loaded '{filename}' "
                f"(Raw: {len(content)} chars, "
                f"Cleaned: {len(cleaned_content)} chars)"
            )

            print(
                f"[SAMPLE] {preview}"
            )

        except Exception as error:

            print(
                f"[INGESTION ERROR] "
                f"Failed to load '{filename}': "
                f"{error}"
            )

    print(
        f"\n[INGESTION LOG] Successfully ingested "
        f"{len(documents)} document(s) "
        f"from '{data_dir}/'."
    )

    return documents


# ============================================================
# CHARACTER-BASED CHUNKING
# ============================================================

def ingest_and_chunk_documents(
    data_dir: str = "data",
    strategy: str = "recursive",
    chunk_size: int = 500,
    chunk_overlap: int = 80
) -> List[Dict[str, Any]]:
    """
    Ingest documents and split them using character-based
    chunking strategies.

    Available strategies:

    - fixed
    - fixed_overlap
    - paragraph
    - sentence
    - recursive
    """

    from src.chunking import (
        fixed_size_chunks,
        fixed_size_overlap_chunks,
        paragraph_chunks,
        sentence_chunks,
        recursive_character_chunks,
    )

    documents = load_documents_from_data_dir(
        data_dir
    )

    all_chunks = []

    for doc in documents:

        filename = doc.get(
            "filename",
            "unknown_doc"
        )

        content = doc.get(
            "content",
            ""
        )

        if not content:
            continue

        # ================================================
        # FIXED
        # ================================================

        if strategy == "fixed":

            chunks = fixed_size_chunks(
                content,
                size=chunk_size,
                overlap=0,
                source_doc=filename
            )

        # ================================================
        # FIXED WITH OVERLAP
        # ================================================

        elif strategy == "fixed_overlap":

            chunks = fixed_size_overlap_chunks(
                content,
                size=chunk_size,
                overlap=chunk_overlap,
                source_doc=filename
            )

        # ================================================
        # PARAGRAPH
        # ================================================

        elif strategy == "paragraph":

            chunks = paragraph_chunks(
                content,
                max_size=chunk_size * 2,
                source_doc=filename
            )

        # ================================================
        # SENTENCE
        # ================================================

        elif strategy == "sentence":

            chunks = sentence_chunks(
                content,
                max_size=chunk_size,
                overlap_sentences=1,
                source_doc=filename
            )

        # ================================================
        # RECURSIVE DEFAULT
        # ================================================

        else:

            chunks = recursive_character_chunks(
                content,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                source_doc=filename
            )

        # Convert chunk objects
        for chunk in chunks:

            chunk_dict = chunk.to_dict()

            # Backward compatibility
            chunk_dict["content"] = chunk.text

            all_chunks.append(
                chunk_dict
            )

    print(
        f"[CHUNKING LOG] Generated "
        f"{len(all_chunks)} total chunks "
        f"using '{strategy}' strategy "
        f"across {len(documents)} document(s)."
    )

    return all_chunks


# ============================================================
# TOKEN-BASED LOAD AND CHUNK
# ============================================================

def load_and_chunk_documents(
    data_dir: str = "data",
    chunk_size_tokens: int = 250,
    overlap_tokens: int = 50,
    model_name: str = "gpt-4o-mini"
) -> List[Dict[str, Any]]:
    """
    Load documents and split them using token-based chunking.

    This is the recommended function for the RAG pipeline.

    Example:

        chunks = load_and_chunk_documents(
            data_dir="data",
            chunk_size_tokens=250,
            overlap_tokens=50
        )
    """

    documents = load_documents_from_data_dir(
        data_dir
    )

    all_chunks = []

    print(
        f"\n[TOKEN CHUNKING] "
        f"Chunk Size: {chunk_size_tokens} tokens | "
        f"Overlap: {overlap_tokens} tokens"
    )

    for doc in documents:

        filename = doc.get(
            "filename",
            "unknown_document"
        )

        chunks = chunk_document_by_tokens(

            doc=doc,

            chunk_size_tokens=chunk_size_tokens,

            overlap_tokens=overlap_tokens,

            model_name=model_name
        )

        all_chunks.extend(chunks)

        print(
            f"[TOKEN CHUNKING SUCCESS] "
            f"'{filename}' → "
            f"{len(chunks)} chunk(s)"
        )

    print(
        f"\n[TOKEN CHUNKING LOG] "
        f"Generated {len(all_chunks)} "
        f"token-based chunks "
        f"from {len(documents)} document(s)."
    )

    return all_chunks


# ============================================================
# CORPUS VALIDATION
# ============================================================

def validate_corpus_ingestion(
    data_dir: str = "data",
    chunk_size_tokens: int = 250,
    overlap_tokens: int = 50
) -> Tuple[
    List[Dict[str, Any]],
    Dict[str, Any]
]:
    """
    Runs the validated corpus ingestion pipeline.

    Returns:

        (
            chunks,
            summary
        )
    """

    from src.corpus_pipeline import (
        run_corpus_ingestion,
        persist_pipeline_artifacts
    )

    (
        files,
        docs,
        chunks,
        failures,
        summary
    ) = run_corpus_ingestion(

        data_dir=data_dir,

        chunk_size_tokens=chunk_size_tokens,

        overlap_tokens=overlap_tokens
    )

    persist_pipeline_artifacts(
        summary,
        chunks
    )

    return (
        chunks,
        summary.to_dict()
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 65)

    print(
        "  [INGESTION MODULE] "
        "Running Token-Based Document Ingestion Test"
    )

    print("=" * 65)

    chunks = load_and_chunk_documents(

        data_dir="data",

        chunk_size_tokens=250,

        overlap_tokens=50
    )

    print("-" * 65)

    print(
        f"Total token-based chunks created: "
        f"{len(chunks)}"
    )

    if chunks:

        print(
            "\n[SAMPLE CHUNK]:"
        )

        import json

        print(
            json.dumps(
                chunks[0],
                indent=2,
                ensure_ascii=False
            )
        )

    print("=" * 65)