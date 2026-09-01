from typing import List, Dict, Any

class SimpleRetriever:
    """
    Lightweight document and chunk retriever for RAG application demonstration.
    Supports searching over text chunks tagged with source metadata.
    """
    def __init__(self, items: List[Dict[str, Any]]):
        self.items = items

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        scored_items = []
        
        for item in self.items:
            # Handle both chunk dicts (item['text']) and legacy doc dicts (item['content'])
            content_text = item.get("text", item.get("content", ""))
            item_words = set(content_text.lower().split())
            score = len(query_words.intersection(item_words))
            scored_items.append((score, item))
        
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored_items[:top_k]]

