import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conversational_rag import (
    ConversationalRAG,
    build_rewrite_prompt,
    rewrite_followup,
)


CHUNKS = {
    "project submission requirements": [
        {
            "score": 0.9,
            "text": "Project submission requires a PR link and a video explanation.",
            "metadata": {"source": "submission.md", "chunk_index": 1},
        }
    ],
    "project submission video deadline": [
        {
            "score": 0.88,
            "text": "The video explanation must be submitted with the project PR.",
            "metadata": {"source": "submission.md", "chunk_index": 2},
        }
    ],
}


class TestConversationalRAG(unittest.TestCase):
    def test_rewrite_prompt_contains_history_and_followup(self):
        prompt = build_rewrite_prompt(
            [{"role": "user", "content": "What are the submission requirements?"}],
            "What about the video?",
        )
        self.assertIn("submission requirements", prompt)
        self.assertIn("What about the video?", prompt)

    def test_rewrite_followup_uses_rewriter_output(self):
        prompts = []
        rewritten = rewrite_followup(
            [{"role": "user", "content": "What are the requirements?"}],
            "What about the video?",
            lambda prompt: prompts.append(prompt) or "What video is required for project submission?",
        )
        self.assertEqual(rewritten, "What video is required for project submission?")
        self.assertEqual(len(prompts), 1)

    def test_multi_turn_followup_retrieves_using_rewritten_query(self):
        retrieved_queries = []

        def rewrite(prompt):
            if "What about the video?" in prompt:
                return "project submission video deadline"
            return "project submission requirements"

        def retrieve(query):
            retrieved_queries.append(query)
            return CHUNKS[query]

        rag = ConversationalRAG(
            rewrite,
            retrieve,
            lambda prompt: "The video explanation is submitted with the PR [1].",
            min_top_score=0.72,
        )
        first = rag.ask("What are the submission requirements?")
        second = rag.ask("What about the video?")

        self.assertEqual(first["status"], "answered")
        self.assertEqual(second["status"], "answered")
        self.assertEqual(second["rewritten_query"], "project submission video deadline")
        self.assertEqual(retrieved_queries, ["project submission requirements", "project submission video deadline"])
        self.assertEqual(len(second["history"]), 4)
        self.assertEqual(second["citations"]["[1]"]["source"], "submission.md")

    def test_weak_followup_is_refused_and_still_recorded(self):
        rag = ConversationalRAG(
            lambda prompt: "unrelated refund policy",
            lambda query: [{"score": 0.1, "text": "Unrelated text."}],
            lambda prompt: "Unsupported answer [1].",
        )
        result = rag.ask("What about the refund?")
        self.assertEqual(result["status"], "refused_weak_context")
        self.assertEqual(len(result["history"]), 2)


if __name__ == "__main__":
    unittest.main()