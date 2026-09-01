import os
import sys
import json
import hashlib
import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Tuple, Optional

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from pypdf import PdfReader
from src.cleaning import clean_text
from src.token_counter import get_tokenizer
from src.ingestion import detect_sections, get_section_for_offset, chunk_document_by_tokens


@dataclass
class IngestionFailure:
    """
    Records explicit metadata about any document that failed to ingest or parse.
    """
    filename: str
    filepath: str
    format: str
    error_type: str
    error_message: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProcessedDocRecord:
    """
    Audit record for a successfully ingested document.
    """
    filename: str
    filepath: str
    format: str
    raw_chars: int
    cleaned_chars: int
    total_tokens: int
    chunks_created: int
    content_hash: str
    status: str = "SUCCESS"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IngestionValidationSummary:
    """
    Complete summary report capturing corpus-wide ingestion metrics and reconciliation state.
    """
    total_files_discovered: int
    total_documents_ingested: int
    total_chunks_created: int
    total_failures: int
    total_corpus_tokens: int
    avg_chunk_tokens: float
    formats_breakdown: Dict[str, int]
    completeness_reconciled: bool
    reconciliation_equation: str
    ingestion_timestamp: str
    ingested_documents: List[Dict[str, Any]] = field(default_factory=list)
    failures: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def compute_content_hash(text: str) -> str:
    """Generates SHA-256 hash for document content tracking and idempotency."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def extract_raw_text(filepath: Path) -> Tuple[str, Optional[List[Tuple[int, int]]]]:
    """
    Extracts raw text and optional page number offsets based on file extension.
    Raises ValueError or ImportError on malformed or unsupported content.
    """
    ext = filepath.suffix.lower()
    
    if ext not in [".txt", ".md", ".html", ".htm", ".pdf"]:
        raise ValueError(f"Unsupported file extension: '{ext}' (Expected .txt, .md, .html, .pdf)")

    if ext in [".txt", ".md"]:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content, None

    elif ext in [".html", ".htm"]:
        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        content = soup.get_text(separator="\n").strip()
        if not content:
            raise ValueError("HTML file contains no readable text content.")
        return content, None

    elif ext == ".pdf":
        reader = PdfReader(str(filepath))
        text_parts = []
        page_numbers = []
        offset = 0
        for p_idx, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                clean_p = page_text.strip()
                page_numbers.append((p_idx, offset))
                text_parts.append(clean_p)
                offset += len(clean_p) + 1
        content = "\n".join(text_parts).strip()
        if not content:
            raise ValueError("PDF text extraction returned empty stream or unreadable scan.")
        return content, page_numbers

    raise ValueError(f"Unhandled file extension '{ext}'")


def run_corpus_ingestion(
    data_dir: str = "data",
    chunk_size_tokens: int = 250,
    overlap_tokens: int = 50,
    model_name: str = "gpt-4o-mini"
) -> Tuple[List[Path], List[Dict[str, Any]], List[Dict[str, Any]], List[IngestionFailure], IngestionValidationSummary]:
    """
    Executes the complete End-to-End Ingestion Pipeline over the corpus:
    1. Discovery -> 2. Load -> 3. Clean -> 4. Chunk -> 5. Tag -> 6. Validate Completeness.
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"[PIPELINE ERROR] Data directory '{data_dir}' does not exist!")
        summary = IngestionValidationSummary(
            total_files_discovered=0,
            total_documents_ingested=0,
            total_chunks_created=0,
            total_failures=0,
            total_corpus_tokens=0,
            avg_chunk_tokens=0.0,
            formats_breakdown={},
            completeness_reconciled=True,
            reconciliation_equation="0 (files) == 0 (docs) + 0 (failures)",
            ingestion_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        return [], [], [], [], summary

    # 1. Discover all files recursively (ignoring hidden files / .gitkeep)
    discovered_files = [
        p for p in data_path.rglob("*") 
        if p.is_file() and not p.name.startswith(".") and not p.name.startswith(".git")
    ]

    ingested_docs = []
    all_chunks = []
    failures: List[IngestionFailure] = []
    formats_count: Dict[str, int] = {}
    total_tokens_count = 0

    encoding = get_tokenizer(model_name)

    print("=" * 80)
    print(f"  [INGESTION PIPELINE] Starting Full Corpus Ingestion on '{data_dir}/'")
    print(f"  Discovered Files on Disk: {len(discovered_files)}")
    print("=" * 80)

    for filepath in discovered_files:
        ext = filepath.suffix.lower()
        formats_count[ext] = formats_count.get(ext, 0) + 1

        try:
            # Stage 2: Load raw content
            raw_content, page_numbers = extract_raw_text(filepath)
            raw_len = len(raw_content)

            # Stage 3: Clean & Normalize
            cleaned_content = clean_text(raw_content)
            cleaned_len = len(cleaned_content)
            if not cleaned_content:
                raise ValueError("Document was empty after cleaning and boilerplate stripping.")

            doc_tokens = len(encoding.encode(cleaned_content))
            total_tokens_count += doc_tokens

            doc_dict = {
                "filename": filepath.name,
                "filepath": str(filepath),
                "content": cleaned_content,
                "page_numbers": page_numbers
            }

            # Stage 4 & 5: Chunk and Tag
            doc_chunks = chunk_document_by_tokens(
                doc_dict,
                chunk_size_tokens=chunk_size_tokens,
                overlap_tokens=overlap_tokens,
                model_name=model_name
            )

            # Augment chunks with corpus-level tagging and content hashes
            content_hash = compute_content_hash(cleaned_content)
            for c in doc_chunks:
                c["metadata"]["content_hash"] = content_hash
                c["metadata"]["doc_format"] = ext
                c["metadata"]["ingestion_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                # Ensure backward compatibility
                c["content"] = c["text"]
                all_chunks.append(c)

            doc_record = ProcessedDocRecord(
                filename=filepath.name,
                filepath=str(filepath),
                format=ext,
                raw_chars=raw_len,
                cleaned_chars=cleaned_len,
                total_tokens=doc_tokens,
                chunks_created=len(doc_chunks),
                content_hash=content_hash
            )
            ingested_docs.append(doc_record.to_dict())

            print(f"[OK] Ingested '{filepath.name}' ({ext}) -> {cleaned_len} chars, {doc_tokens} tokens, {len(doc_chunks)} chunks")

        except Exception as e:
            err_type = type(e).__name__
            failure = IngestionFailure(
                filename=filepath.name,
                filepath=str(filepath),
                format=ext,
                error_type=err_type,
                error_message=str(e)
            )
            failures.append(failure)
            print(f"[FAILED] Error loading '{filepath.name}': [{err_type}] {e}")

    # Stage 6: Validate Completeness
    total_files = len(discovered_files)
    ingested_count = len(ingested_docs)
    failures_count = len(failures)

    is_reconciled = (total_files == ingested_count + failures_count)
    reconciliation_eq = f"{total_files} (Discovered Files) == {ingested_count} (Ingested Docs) + {failures_count} (Recorded Failures)"

    avg_chunk_tokens = (
        sum(c["metadata"]["token_count"] for c in all_chunks) / len(all_chunks)
        if all_chunks else 0.0
    )

    summary = IngestionValidationSummary(
        total_files_discovered=total_files,
        total_documents_ingested=ingested_count,
        total_chunks_created=len(all_chunks),
        total_failures=failures_count,
        total_corpus_tokens=total_tokens_count,
        avg_chunk_tokens=round(avg_chunk_tokens, 2),
        formats_breakdown=formats_count,
        completeness_reconciled=is_reconciled,
        reconciliation_equation=reconciliation_eq,
        ingestion_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ingested_documents=ingested_docs,
        failures=[f.to_dict() for f in failures]
    )

    # Perform strict completeness assertion
    assert is_reconciled, f"CRITICAL: Silent document drop detected! {reconciliation_eq}"

    return discovered_files, ingested_docs, all_chunks, failures, summary


def persist_pipeline_artifacts(
    summary: IngestionValidationSummary,
    all_chunks: List[Dict[str, Any]],
    output_dir: str = "outputs"
):
    """
    Persists manifest, validation summary reports, and sample chunks to disk.
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Save Machine-Readable Validation Summary JSON
    summary_json_path = os.path.join(output_dir, "ingestion_validation_summary.json")
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary.to_dict(), f, indent=2)
    print(f"[ARTIFACT] Saved Validation Summary JSON -> '{summary_json_path}'")

    # 2. Save Resumable Ingestion Manifest JSON
    manifest_path = os.path.join(output_dir, "ingestion_manifest.json")
    manifest_payload = {
        "manifest_version": "1.0",
        "last_updated": summary.ingestion_timestamp,
        "total_files": summary.total_files_discovered,
        "processed_documents": {
            doc["filename"]: {
                "filepath": doc["filepath"],
                "format": doc["format"],
                "content_hash": doc["content_hash"],
                "chunks_count": doc["chunks_created"],
                "tokens": doc["total_tokens"],
                "status": doc["status"]
            } for doc in summary.ingested_documents
        },
        "failed_files": {
            f["filename"]: {
                "filepath": f["filepath"],
                "error_type": f["error_type"],
                "error_message": f["error_message"]
            } for f in summary.failures
        }
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2)
    print(f"[ARTIFACT] Saved Resumable Manifest JSON -> '{manifest_path}'")

    # 3. Save Sample Validated Chunks with Metadata JSON
    sample_chunks_path = os.path.join(output_dir, "sample_validated_chunks.json")
    with open(sample_chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks[:8], f, indent=2)
    print(f"[ARTIFACT] Saved Sample Validated Chunks JSON -> '{sample_chunks_path}'")

    # 4. Save Human-Readable Text Summary Report
    summary_txt_path = os.path.join(output_dir, "ingestion_validation_summary.txt")
    with open(summary_txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  SCHEMEASSIST RAG - CORPUS INGESTION & VALIDATION AUDIT REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp (UTC)            : {summary.ingestion_timestamp}\n")
        f.write(f"Total Source Files on Disk : {summary.total_files_discovered}\n")
        f.write(f"Successfully Ingested Docs : {summary.total_documents_ingested}\n")
        f.write(f"Total Chunks Generated     : {summary.total_chunks_created}\n")
        f.write(f"Total Failures / Skipped   : {summary.total_failures}\n")
        f.write(f"Total Corpus Tokens        : {summary.total_corpus_tokens}\n")
        f.write(f"Average Chunk Tokens       : {summary.avg_chunk_tokens} tokens\n")
        f.write(f"Completeness Status        : {'PASSED (Zero Silent Drops)' if summary.completeness_reconciled else 'FAILED'}\n")
        f.write(f"Reconciliation Proof       : {summary.reconciliation_equation}\n\n")

        f.write("FORMATS BREAKDOWN:\n")
        f.write("-" * 40 + "\n")
        for fmt, count in sorted(summary.formats_breakdown.items()):
            f.write(f"  • {fmt:<10} : {count} file(s)\n")

        f.write("\nSUCCESSFULLY INGESTED DOCUMENTS:\n")
        f.write("-" * 80 + "\n")
        for idx, doc in enumerate(summary.ingested_documents, start=1):
            f.write(f"{idx}. {doc['filename']} [{doc['format']}] - {doc['cleaned_chars']} chars | {doc['total_tokens']} tokens | {doc['chunks_created']} chunks (Hash: {doc['content_hash']})\n")

        if summary.failures:
            f.write("\nRECORDED INGESTION FAILURES & SKIPPED FILES:\n")
            f.write("-" * 80 + "\n")
            for idx, fail in enumerate(summary.failures, start=1):
                f.write(f"{idx}. {fail['filename']} [{fail['format']}] -> [{fail['error_type']}]: {fail['error_message']}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("SAMPLE CHUNK METADATA AUDIT (FIRST 2 CHUNKS):\n")
        f.write("=" * 80 + "\n")
        for idx, chunk in enumerate(all_chunks[:2], start=1):
            f.write(f"\n--- [SAMPLE CHUNK #{idx}] ---\n")
            f.write(f"Source Document : {chunk['metadata'].get('source')}\n")
            f.write(f"Section Heading : {chunk['metadata'].get('section')}\n")
            f.write(f"Chunk Position  : {chunk['metadata'].get('position')}\n")
            f.write(f"Token Count     : {chunk['metadata'].get('token_count')}\n")
            f.write(f"Char Offsets    : {chunk['metadata'].get('char_start')}..{chunk['metadata'].get('char_end')}\n")
            f.write(f"Content Preview : \"{chunk['text'][:150].replace(chr(10), ' ')}...\"\n")

    print(f"[ARTIFACT] Saved Text Audit Summary -> '{summary_txt_path}'")


if __name__ == "__main__":
    files, docs, chunks, failures, summary = run_corpus_ingestion("data")
    persist_pipeline_artifacts(summary, chunks)

    print("\n" + "=" * 80)
    print("  INGESTION SUMMARY REPORT:")
    print("=" * 80)
    print(f"  * Total Discovered Files: {summary.total_files_discovered}")
    print(f"  * Ingested Documents:    {summary.total_documents_ingested}")
    print(f"  * Total Chunks Created:   {summary.total_chunks_created}")
    print(f"  * Failures Recorded:      {summary.total_failures}")
    print(f"  * Reconciliation Formula: {summary.reconciliation_equation}")
    print(f"  * Completeness Status:    {'[PASSED]' if summary.completeness_reconciled else '[FAILED]'}")
    print("=" * 80)
