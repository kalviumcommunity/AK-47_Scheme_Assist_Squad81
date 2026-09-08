# -*- coding: utf-8 -*-
"""
tests/test_prompt_templates.py - Unit tests for 3.18 Prompt Templates & Reusable Design
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.templates import (
    PromptTemplate,
    TemplateRegistry,
    TemplateValidationError,
    render,
    render_template,
    registry,
    SCHEME_QA_TEMPLATE_V1,
    SCHEME_QA_TEMPLATE_V2,
    SCHEME_BATCH_EVAL_TEMPLATE,
    SYSTEM_SCHEME_ASSIST_TEMPLATE,
)
from prompts.answer import ANSWER, ANSWER_V2


class TestPromptTemplates(unittest.TestCase):

    def test_placeholder_extraction(self):
        tmpl = PromptTemplate(
            template="Context: {context}\nQuestion: {question}\nTone: {tone}",
            name="test_extract",
        )
        self.assertEqual(tmpl.placeholders, {"context", "question", "tone"})

    def test_render_with_valid_dynamic_values(self):
        tmpl = PromptTemplate(
            template="Hello {name}, your scheme is {scheme_name}.",
            name="greeting",
        )
        rendered = tmpl.render(name="Aarav", scheme_name="PM-Kisan")
        self.assertEqual(rendered, "Hello Aarav, your scheme is PM-Kisan.")

    def test_missing_placeholder_raises_validation_error(self):
        tmpl = PromptTemplate(
            template="Context: {context}\nQuestion: {question}",
            name="strict_qa",
        )
        with self.assertRaises(TemplateValidationError) as ctx:
            tmpl.render(context="Some context only")
        self.assertIn("question", str(ctx.exception))

    def test_default_values_injection(self):
        tmpl = PromptTemplate(
            template="Assistant: {assistant_name}\nQuestion: {question}",
            name="with_defaults",
            defaults={"assistant_name": "SchemeAssist"},
        )
        # Call without providing assistant_name
        rendered = tmpl.render(question="How to apply?")
        self.assertEqual(rendered, "Assistant: SchemeAssist\nQuestion: How to apply?")

        # Override default
        rendered_override = tmpl.render(assistant_name="HelpdeskBot", question="How to apply?")
        self.assertEqual(rendered_override, "Assistant: HelpdeskBot\nQuestion: How to apply?")

    def test_functional_render_helper(self):
        # Raw string
        raw = "User {user_id} requested {topic}"
        res1 = render(raw, user_id=42, topic="Scholarships")
        self.assertEqual(res1, "User 42 requested Scholarships")

        # PromptTemplate instance
        tmpl = PromptTemplate("User {user_id} requested {topic}")
        res2 = render(tmpl, user_id=42, topic="Scholarships")
        self.assertEqual(res2, "User 42 requested Scholarships")

    def test_answer_module_integration(self):
        # Exact pattern from assignment:
        # from prompts.answer import ANSWER, render
        # msg = render(ANSWER, context=chunks, question=user_q)
        chunks = "Eligible age is 18 to 35 years."
        user_q = "What is the age limit?"
        msg = render(ANSWER, context=chunks, question=user_q)
        self.assertIn(chunks, msg)
        self.assertIn(user_q, msg)
        self.assertTrue(msg.startswith("You are a support assistant."))

    def test_cross_feature_reuse(self):
        # Feature A (Chat) and Feature B (Batch / CLI) reusing the same template logic
        chat_prompt = render(
            SCHEME_QA_TEMPLATE_V1,
            context="Income must be under 2 Lakhs.",
            question="What is the income cap?",
        )
        batch_prompt = render(
            SCHEME_QA_TEMPLATE_V1,
            context="Income must be under 2 Lakhs.",
            question="[TEST_CASE_102] Verify income cap validation.",
        )
        self.assertIn("What is the income cap?", chat_prompt)
        self.assertIn("[TEST_CASE_102] Verify income cap validation.", batch_prompt)

    def test_template_registry_versioning(self):
        reg = TemplateRegistry()
        v1 = PromptTemplate("V1: {q}", name="test", version="1.0.0")
        v2 = PromptTemplate("V2: {q} with more details", name="test", version="2.0.0")

        reg.register(v1, is_default=False)
        reg.register(v2, is_default=True)

        self.assertEqual(reg.get("test").version, "2.0.0")
        self.assertEqual(reg.get("test", version="1.0.0").version, "1.0.0")
        self.assertEqual(reg.get("test", version="2.0.0").version, "2.0.0")

    def test_partial_template(self):
        base = PromptTemplate("Role: {role}\nQuery: {query}")
        partial_tmpl = base.partial(role="Auditor")
        rendered = partial_tmpl.render(query="Check doc count")
        self.assertEqual(rendered, "Role: Auditor\nQuery: Check doc count")


if __name__ == "__main__":
    unittest.main()
