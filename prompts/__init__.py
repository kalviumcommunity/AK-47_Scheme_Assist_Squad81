# -*- coding: utf-8 -*-
"""
prompts package - Centralized prompt repository and templating engine.
======================================================================
Stores all system instructions, prompt templates, and rendering logic
isolated from business and application code.
"""

from prompts.templates import (
    PromptTemplate,
    TemplateRegistry,
    TemplateValidationError,
    render,
    render_template,
    registry,
    SYSTEM_SCHEME_ASSIST_TEMPLATE,
    SCHEME_QA_TEMPLATE_V1,
    SCHEME_QA_TEMPLATE_V2,
    SCHEME_BATCH_EVAL_TEMPLATE,
    SCHEME_ELIGIBILITY_TEMPLATE,
    SCHEME_SUMMARY_TEMPLATE,
)
from prompts.answer import ANSWER, ANSWER_V2

__all__ = [
    "PromptTemplate",
    "TemplateRegistry",
    "TemplateValidationError",
    "render",
    "render_template",
    "registry",
    "ANSWER",
    "ANSWER_V2",
    "SYSTEM_SCHEME_ASSIST_TEMPLATE",
    "SCHEME_QA_TEMPLATE_V1",
    "SCHEME_QA_TEMPLATE_V2",
    "SCHEME_BATCH_EVAL_TEMPLATE",
    "SCHEME_ELIGIBILITY_TEMPLATE",
    "SCHEME_SUMMARY_TEMPLATE",
]
