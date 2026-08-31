import os
from typing import List, Dict

from bs4 import BeautifulSoup
from pypdf import PdfReader

def load_documents_from_data_dir(data_dir: str = "data") -> List[Dict[str, str]]:
    """
    Ingests PDF, HTML, Markdown, and TXT documents from the specified data directory.
    Handles unreadable/malformed files and skips unsupported formats.
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
                soup = BeautifulSoup(html_content, "html.parser")
                # Remove script and style elements to avoid extracting code/css
                for script_or_style in soup(["script", "style"]):
                    script_or_style.decompose()
                # Get text with whitespace separators
                content = soup.get_text(separator=" ").strip()
                # Clean up excessive duplicate whitespace/newlines
                content = " ".join(content.split())
            elif ext == ".pdf":
                # PDF loading and extraction
                reader = PdfReader(filepath)
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                content = "\n".join(text_parts).strip()
                if not content:
                    raise ValueError("Extracted PDF text content is empty or unreadable.")

            # Record document and preserve source filename/identity
            documents.append({
                "filename": filename,
                "content": content
            })
            
            # Confirm intake with length and preview
            preview = content[:200].replace("\n", " ")
            if len(content) > 200:
                preview += "..."
            print(f"[INGESTION SUCCESS] Loaded '{filename}' (length: {len(content)} chars) - Sample: \"{preview}\"")

        except Exception as e:
            print(f"[INGESTION ERROR] Failed to load '{filename}': {e}")

    print(f"[INGESTION LOG] Successfully ingested {len(documents)} document(s) from '{data_dir}/'.")
    return documents

