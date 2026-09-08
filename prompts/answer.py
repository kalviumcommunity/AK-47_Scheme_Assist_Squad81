# -*- coding: utf-8 -*-
"""
prompts/answer.py - Direct modular prompt definition matching assignment standard.
==================================================================================
Keeps prompts strictly separate from business logic.
"""

from prompts.templates import (
    SCHEME_QA_TEMPLATE_V1,
    SCHEME_QA_TEMPLATE_V2,
    PromptTemplate,
    render as render_helper,
)

# Standard ANSWER template with named placeholders
ANSWER = (
    "You are a support assistant. Answer ONLY from the context.\n"
    "If the answer isn't there, say you don't know.\n\n"
    "Context:\n"
    "{context}\n\n"
    "Question: {question}"
)

# Production ANSWER Template (V2 with structured guidelines and grounding)
ANSWER_V2 = (
    "You are SchemeAssist, an official government welfare support assistant.\n"
    "Answer ONLY from the context provided below. If the answer is not present, reply strictly with: "
    "'I do not have sufficient verified information to answer this question.'\n\n"
    "Context:\n"
    "{context}\n\n"
    "Question: {question}"
)

def render(template, **values):
    """
    Renders a prompt template string or PromptTemplate instance
    by injecting dynamic runtime values.
    """
    return render_helper(template, **values)

__all__ = ["ANSWER", "ANSWER_V2", "render"]
