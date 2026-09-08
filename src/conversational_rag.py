"""Conversational RAG orchestration for history-aware follow-up questions."""

from typing import Any, Callable, Dict, Iterable, List

from src.guardrails import guarded_answer

DEFAULT_MAX_TURNS = 6


def format_history(history: Iterable[Dict[str, str]]) -> str:
    """Format recent turns for a query rewriter without exposing extra state."""
    return "\n".join(
        f"{turn.get('role', 'unknown')}: {turn.get('content', '')}"
        for turn in history
    )


def build_rewrite_prompt(history: Iterable[Dict[str, str]], question: str) -> str:
    """Build instructions for rewriting a follow-up as a standalone query."""
    return (
        "Rewrite the latest user question as a standalone search query.\n"
        "Use conversation history only to resolve references. Do not answer the question.\n\n"
        f"History:\n{format_history(history)}\n\n"
        f"Latest question:\n{question}"
    )


def rewrite_followup(
    history: Iterable[Dict[str, str]],
    question: str,
    rewrite_fn: Callable[[str], str],
) -> str:
    """Rewrite a follow-up using recent history and return a clean query."""
    rewritten = rewrite_fn(build_rewrite_prompt(history, question))
    rewritten = (rewritten or question).strip()
    return rewritten or question.strip()


class ConversationalRAG:
    """Coordinate history, query rewriting, retrieval, guardrails, and answers."""

    def __init__(
        self,
        rewrite_fn: Callable[[str], str],
        retrieve_fn: Callable[[str], List[Dict[str, Any]]],
        answer_fn: Callable[[str], str],
        *,
        max_turns: int = DEFAULT_MAX_TURNS,
        min_top_score: float = 0.72,
        min_supporting_chunks: int = 1,
    ):
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1")
        self.rewrite_fn = rewrite_fn
        self.retrieve_fn = retrieve_fn
        self.answer_fn = answer_fn
        self.max_history_messages = max_turns * 2
        self.min_top_score = min_top_score
        self.min_supporting_chunks = min_supporting_chunks
        self.history: List[Dict[str, str]] = []

    def _remember(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})
        self.history = self.history[-self.max_history_messages :]

    def ask(self, question: str, *, answer_question: str | None = None) -> Dict[str, Any]:
        """Answer one turn, retrieving with a history-aware standalone query."""
        if not question or not question.strip():
            raise ValueError("question must not be empty")

        history_before_turn = list(self.history)
        rewritten_query = rewrite_followup(history_before_turn, question, self.rewrite_fn)
        chunks = list(self.retrieve_fn(rewritten_query))
        result = guarded_answer(
            answer_question or question,
            chunks,
            self.answer_fn,
            min_top_score=self.min_top_score,
            min_supporting_chunks=self.min_supporting_chunks,
        )
        self._remember("user", question)
        self._remember("assistant", result["answer"])
        return {
            **result,
            "question": question,
            "rewritten_query": rewritten_query,
            "retrieved_chunks": chunks,
            "history": list(self.history),
        }