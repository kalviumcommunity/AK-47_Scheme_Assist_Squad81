from typing import List, Dict, Any


class SimpleRetriever:
    """
    Lightweight document and chunk retriever for SchemeAssist RAG.
    Supports both full document dictionaries and chunk dictionaries.
    """
    def __init__(self, items: List[Dict[str, Any]]):
        self.items = items

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Performs keyword overlap ranking across indexed documents or chunks.
        Returns top_k most relevant items augmented with retrieval score.
        """
        if not self.items or not query:
            return []

        query_words = set(query.lower().split())
        scored_items = []

        for item in self.items:
            content = item.get("content") or item.get("text", "")
            item_words = set(content.lower().split())
            score = len(query_words.intersection(item_words))

            # Store score without modifying original dict
            enriched_item = dict(item)
            enriched_item["retrieval_score"] = score
            scored_items.append((score, enriched_item))

        scored_items = [pair for pair in scored_items if pair[0] > 0]
        if not scored_items:
            return []
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored_items[:top_k]]
