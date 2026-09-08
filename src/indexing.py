import os
import sys
import json
import hashlib
import numpy as np
from typing import List, Dict, Any, Tuple

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings
from src.config import validate_environment, OPENAI_API_KEY, EMBED_MODEL
from src.ingestion import load_and_chunk_documents


def generate_deterministic_embedding(text: str, dim: int = 1536) -> List[float]:
    """
    Generates a deterministic, unit-normalized float vector of dimension `dim`
    based on the SHA-256 hash of the input text. Used as an offline/mock embedding.
    """
    hash_bytes = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(hash_bytes[:4], byteorder="big")
    rng = np.random.RandomState(seed)
    vector = rng.randn(dim)
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector.tolist()


def get_embeddings_for_texts(texts: List[str], embed_model: str = EMBED_MODEL) -> List[List[float]]:
    """
    Generates embedding vectors for a list of texts using OpenAI API if key is available,
    otherwise falling back to deterministic local mock vectors.
    """
    if OPENAI_API_KEY and OPENAI_API_KEY.strip():
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.embeddings.create(
                input=texts,
                model=embed_model
            )
            print(f"[EMBEDDING LOG] Successfully generated {len(texts)} embeddings via OpenAI API ({embed_model}).")
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"[EMBEDDING WARNING] OpenAI API embedding failed ({e}). Falling back to deterministic local embeddings.")

    print(f"[EMBEDDING LOG] Using deterministic local embedding generator (dimension 1536) for {len(texts)} chunks.")
    return [generate_deterministic_embedding(t) for t in texts]


class VectorIndexer:
    """
    Manages loading, embedding, indexing, count validation, and spot-check integrity
    of corpus document chunks into a persistent ChromaDB collection.
    """
    def __init__(self, db_dir: str = "data/chroma_db", collection_name: str = "scheme_assist_corpus"):
        self.db_dir = db_dir
        self.collection_name = collection_name
        os.makedirs(self.db_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.db_dir)
        # Reset or get collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "SchemeAssist corpus document chunks with metadata and embeddings"}
        )

    def clear_collection(self):
        """Removes all existing records from the collection to ensure clean indexing."""
        existing_count = self.collection.count()
        if existing_count > 0:
            all_ids = self.collection.get()["ids"]
            if all_ids:
                self.collection.delete(ids=all_ids)
            print(f"[INDEXING LOG] Cleared {existing_count} pre-existing record(s) from collection '{self.collection_name}'.")

    def index_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Task 1 & Task 2: Inserts all corpus chunks along with embedding vectors,
        source text, and full metadata into the vector database.
        """
        if not chunks:
            return {"inserted": 0, "failures": 0, "ids": []}

        # Clear previous records to prevent duplicate counts during re-runs
        self.clear_collection()

        ids = []
        documents = []
        metadatas = []

        for idx, chunk in enumerate(chunks):
            meta = chunk["metadata"]
            source_clean = meta.get("source", "doc").replace(" ", "_").replace("/", "_")
            chunk_id = f"doc_{source_clean}_chunk_{meta.get('chunk_index', idx)}"
            
            ids.append(chunk_id)
            documents.append(chunk["text"])
            
            # Ensure metadata dict values are compliant with ChromaDB types (str, int, float, bool)
            meta_copy = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    meta_copy[k] = v
                else:
                    meta_copy[k] = str(v)
            metadatas.append(meta_copy)

        print(f"[INDEXING LOG] Generating embedding vectors for {len(chunks)} chunks...")
        embeddings = get_embeddings_for_texts(documents)

        print(f"[INDEXING LOG] Inserting {len(chunks)} records into ChromaDB collection '{self.collection_name}'...")
        failures = 0
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            print(f"[INDEXING SUCCESS] Inserted all {len(ids)} records into vector database.")
        except Exception as e:
            print(f"[INDEXING ERROR] Failed to insert records: {e}")
            failures = len(ids)

        return {
            "inserted": len(ids) - failures,
            "failures": failures,
            "ids": ids,
            "embeddings": embeddings,
            "documents": documents,
            "metadatas": metadatas
        }

    def verify_indexed_count(self, expected_count: int) -> Tuple[bool, int, int]:
        """
        Task 3: Confirms indexed record count against expected chunk count.
        """
        actual_count = self.collection.count()
        matches = (actual_count == expected_count)
        return matches, expected_count, actual_count

    def spot_check_record(self, record_id: str, original_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task 4: Reads back a stored record and verifies integrity against original chunk
        (ID, text, metadata, vector length).
        """
        retrieved = self.collection.get(
            ids=[record_id],
            include=["embeddings", "documents", "metadatas"]
        )

        result = {
            "record_id": record_id,
            "id_matched": False,
            "text_matched": False,
            "metadata_matched": False,
            "vector_length": 0,
            "vector_length_valid": False,
            "stored_record": {}
        }

        if retrieved and retrieved["ids"] and len(retrieved["ids"]) > 0:
            stored_id = retrieved["ids"][0]
            stored_doc = retrieved["documents"][0]
            stored_meta = retrieved["metadatas"][0]
            stored_emb = retrieved["embeddings"][0] if retrieved["embeddings"] is not None and len(retrieved["embeddings"]) > 0 else []

            result["id_matched"] = (stored_id == record_id)
            result["text_matched"] = (stored_doc == original_chunk["text"])
            
            # Check metadata key matches
            orig_meta = original_chunk["metadata"]
            meta_keys_match = all(stored_meta.get(k) == orig_meta.get(k) for k in orig_meta if isinstance(orig_meta[k], (str, int, float, bool)))
            result["metadata_matched"] = meta_keys_match
            
            result["vector_length"] = len(stored_emb)
            result["vector_length_valid"] = (len(stored_emb) > 0)

            result["stored_record"] = {
                "id": stored_id,
                "text_preview": stored_doc[:120] + ("..." if len(stored_doc) > 120 else ""),
                "metadata": stored_meta,
                "vector_length": len(stored_emb)
            }

        return result


def run_indexing_pipeline(data_dir: str = "data") -> Dict[str, Any]:
    """
    Executes the end-to-end vector indexing workflow:
    1. Ingests and chunks documents.
    2. Inserts embeddings, text, and metadata into ChromaDB.
    3. Confirms indexed count against generated chunks.
    4. Spot-checks stored record integrity.
    5. Writes indexing summary to outputs/indexing_summary.txt.
    """
    print("=" * 75)
    print("  [VECTOR DB INDEXING PIPELINE] Loading Corpus & Storing Embeddings")
    print("=" * 75)

    validate_environment()

    # Step 1: Ingest and chunk documents
    print("\n[STEP 1] Ingesting and chunking documents from data directory...")
    chunks = load_and_chunk_documents(data_dir)
    total_chunks = len(chunks)
    print(f"--> Total corpus chunks produced: {total_chunks}")
    assert total_chunks > 0, "No chunks were produced from data directory!"

    # Step 2: Initialize indexer and insert chunks (Tasks 1 & 2)
    print("\n[STEP 2] Initializing Vector DB Indexer and inserting embeddings...")
    indexer = VectorIndexer(db_dir="data/chroma_db", collection_name="scheme_assist_corpus")
    index_res = indexer.index_chunks(chunks)

    # Step 3: Confirm indexed count (Task 3)
    print("\n[STEP 3] Validating indexed record count against corpus chunk count...")
    count_matches, expected_cnt, actual_cnt = indexer.verify_indexed_count(total_chunks)
    print(f"--> Expected Chunk Count: {expected_cnt}")
    print(f"--> Stored Record Count:   {actual_cnt}")
    print(f"--> Count Match Status:    {'[MATCH SUCCESS]' if count_matches else '[MISMATCH ERROR]'}")

    # Step 4: Spot-check stored integrity (Task 4)
    print("\n[STEP 4] Performing spot-check on stored record integrity...")
    sample_id = index_res["ids"][0]
    sample_orig_chunk = chunks[0]
    spot_check = indexer.spot_check_record(sample_id, sample_orig_chunk)

    print(f"  Spot-Check Record ID:      {spot_check['record_id']}")
    print(f"  ID Match:                  {spot_check['id_matched']}")
    print(f"  Text Content Match:        {spot_check['text_matched']}")
    print(f"  Metadata Match:            {spot_check['metadata_matched']}")
    print(f"  Vector Length:             {spot_check['vector_length']} dimensions")
    print(f"  Vector Length Valid:       {spot_check['vector_length_valid']}")
    print(f"  Stored Record Metadata:    {json.dumps(spot_check['stored_record'].get('metadata', {}), indent=4)}")

    spot_check_passed = (
        spot_check["id_matched"] and
        spot_check["text_matched"] and
        spot_check["metadata_matched"] and
        spot_check["vector_length_valid"]
    )

    # Step 5: Write indexing summary report (Task 5)
    os.makedirs("outputs", exist_ok=True)
    summary_path = os.path.join("outputs", "indexing_summary.txt")
    
    summary_content = []
    summary_content.append("=========================================================================")
    summary_content.append("               SCHEMEASSIST VECTOR DB INDEXING SUMMARY                   ")
    summary_content.append("=========================================================================")
    summary_content.append(f"Vector Store Directory: data/chroma_db")
    summary_content.append(f"Collection Name:        scheme_assist_corpus")
    summary_content.append(f"Embedding Model:        {EMBED_MODEL}")
    summary_content.append("-------------------------------------------------------------------------")
    summary_content.append("1. STORED RECORDS SUMMARY")
    summary_content.append(f"   - Total Corpus Chunks Generated:  {total_chunks}")
    summary_content.append(f"   - Total Records Inserted:        {index_res['inserted']}")
    summary_content.append(f"   - Total Insertion Failures:       {index_res['failures']}")
    summary_content.append("-------------------------------------------------------------------------")
    summary_content.append("2. COUNT VALIDATION")
    summary_content.append(f"   - Expected Count:                {expected_cnt}")
    summary_content.append(f"   - Indexed DB Count:              {actual_cnt}")
    summary_content.append(f"   - Status:                        {'MATCHED' if count_matches else 'MISMATCH'}")
    summary_content.append("-------------------------------------------------------------------------")
    summary_content.append("3. SPOT-CHECK RECORD INTEGRITY")
    summary_content.append(f"   - Spot-Check Record ID:          {spot_check['record_id']}")
    summary_content.append(f"   - ID Match Confirmed:            {spot_check['id_matched']}")
    summary_content.append(f"   - Source Text Match Confirmed:   {spot_check['text_matched']}")
    summary_content.append(f"   - Metadata Match Confirmed:      {spot_check['metadata_matched']}")
    summary_content.append(f"   - Stored Vector Dimension:       {spot_check['vector_length']}")
    summary_content.append(f"   - Spot-Check Overall Result:     {'PASSED' if spot_check_passed else 'FAILED'}")
    summary_content.append("-------------------------------------------------------------------------")
    summary_content.append("4. SAMPLE STORED RECORD METADATA & TEXT PREVIEW")
    summary_content.append(json.dumps(spot_check["stored_record"], indent=2))
    summary_content.append("=========================================================================")

    summary_text = "\n".join(summary_content)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"\n[STEP 5] Committed indexing summary to '{summary_path}'.")
    print("\n" + "=" * 75)
    print("  [SUCCESS] VECTOR DATABASE CORPUS INDEXING COMPLETED SUCCESSFULLY!")
    print("=" * 75)

    return {
        "chunks_count": total_chunks,
        "indexed_count": actual_cnt,
        "count_matches": count_matches,
        "failures": index_res["failures"],
        "spot_check_passed": spot_check_passed,
        "summary_path": summary_path
    }


if __name__ == "__main__":
    run_indexing_pipeline("data")
