import os
from typing import List, Dict

def load_documents_from_data_dir(data_dir: str = "data") -> List[Dict[str, str]]:
    """
    Ingests text/markdown documents from the specified data directory.
    """
    documents = []
    if not os.path.exists(data_dir):
        print(f"[INGESTION WARNING] Data directory '{data_dir}' does not exist.")
        return documents

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        if os.path.isfile(filepath) and not filename.startswith("."):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    documents.append({
                        "filename": filename,
                        "content": content
                    })
            except Exception as e:
                print(f"[INGESTION ERROR] Failed reading {filename}: {e}")

    print(f"[INGESTION LOG] Successfully ingested {len(documents)} document(s) from '{data_dir}/'.")
    return documents
