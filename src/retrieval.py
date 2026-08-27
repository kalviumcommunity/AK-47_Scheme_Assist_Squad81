from typing import List, Dict

class SimpleRetriever:
    """
    Lightweight document retriever for RAG application demonstration.
    """
    def __init__(self, documents: List[Dict[str, str]]):
        self.documents = documents

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, str]]:
        query_words = set(query.lower().split())
        scored_docs = []
        
        for doc in self.documents:
            doc_words = set(doc["content"].lower().split())
            score = len(query_words.intersection(doc_words))
            scored_docs.append((score, doc))
        
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]
