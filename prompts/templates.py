# -*- coding: utf-8 -*-
"""
prompts/templates.py - 3.18 Prompt Templates & Reusable Prompt Design
====================================================================
Decouples prompt definitions, structural placeholders, and rendering logic
from downstream application and business logic.

Key Capabilities:
  1. PromptTemplate: Class encapsulating named placeholders, validation, default values, and formatting.
  2. render / render_template: Easy functional helpers for runtime dynamic variable injection.
  3. TemplateRegistry: Version-controlled prompt catalog (v1, v2, etc.) ensuring safe updates without breaking consumers.
  4. Standardized Reusable Templates:
     - SCHEME_QA_TEMPLATE_V1 / V2
     - SCHEME_BATCH_EVAL_TEMPLATE
     - SCHEME_ELIGIBILITY_TEMPLATE
     - SCHEME_SUMMARY_TEMPLATE
     - SYSTEM_SCHEME_ASSIST_TEMPLATE
"""

import re
import string
from typing import Dict, Any, List, Optional, Set


class TemplateValidationError(ValueError):
    """Raised when required template placeholders are missing or invalid."""
    pass


class PromptTemplate:
    """
    Encapsulates a prompt string with named placeholders, metadata, default values,
    and runtime validation.
    """

    def __init__(
        self,
        template: str,
        name: str = "custom_template",
        version: str = "1.0.0",
        description: str = "",
        defaults: Optional[Dict[str, Any]] = None,
    ):
        self.template = template.strip()
        self.name = name
        self.version = version
        self.description = description
        self.defaults: Dict[str, Any] = defaults or {}
        self.placeholders: Set[str] = self._extract_placeholders(self.template)

    @staticmethod
    def _extract_placeholders(template_str: str) -> Set[str]:
        """Extracts all named placeholder keys inside curly braces e.g. {context}."""
        formatter = string.Formatter()
        placeholders = set()
        for _, field_name, _, _ in formatter.parse(template_str):
            if field_name is not None and field_name != "":
                # Strip out any format specifiers or item accesses
                base_name = field_name.split(".")[0].split("[")[0]
                placeholders.add(base_name)
        return placeholders

    def get_missing_variables(self, provided_values: Dict[str, Any]) -> List[str]:
        """Identifies any placeholders that have neither a provided value nor a default."""
        merged = {**self.defaults, **provided_values}
        return [p for p in sorted(self.placeholders) if p not in merged or merged[p] is None]

    def render(self, **values: Any) -> str:
        """
        Injects dynamic values at runtime to produce the final rendered prompt string.
        Validates all required placeholders before rendering.
        """
        merged_values = {**self.defaults, **values}
        missing = self.get_missing_variables(values)
        if missing:
            raise TemplateValidationError(
                f"Cannot render template '{self.name}' (v{self.version}). "
                f"Missing required placeholder(s): {', '.join(missing)}"
            )
        try:
            return self.template.format(**merged_values)
        except KeyError as ke:
            raise TemplateValidationError(f"Missing key during format: {ke}") from ke
        except Exception as exc:
            raise TemplateValidationError(f"Error rendering template '{self.name}': {exc}") from exc

    def partial(self, **values: Any) -> "PromptTemplate":
        """Returns a new PromptTemplate with a subset of placeholders pre-filled."""
        new_defaults = {**self.defaults, **values}
        return PromptTemplate(
            template=self.template,
            name=f"{self.name}_partial",
            version=self.version,
            description=self.description,
            defaults=new_defaults,
        )

    def to_chat_messages(
        self,
        system_template: Optional["PromptTemplate"] = None,
        system_values: Optional[Dict[str, Any]] = None,
        **user_values: Any,
    ) -> List[Dict[str, str]]:
        """
        Convenience method rendering into standard chat completion messages (system + user).
        """
        messages = []
        if system_template:
            sys_vals = system_values or {}
            messages.append({"role": "system", "content": system_template.render(**sys_vals)})
        messages.append({"role": "user", "content": self.render(**user_values)})
        return messages

    def __repr__(self) -> str:
        return (
            f"<PromptTemplate(name='{self.name}', version='{self.version}', "
            f"placeholders={sorted(list(self.placeholders))})>"
        )


def render(template: Any, **values: Any) -> str:
    """
    Functional render helper that accepts either a PromptTemplate instance
    or a raw string with named placeholders.
    """
    if isinstance(template, PromptTemplate):
        return template.render(**values)
    elif isinstance(template, str):
        return template.format(**values)
    else:
        raise TypeError(f"Expected PromptTemplate or str, received: {type(template)}")


render_template = render


# ─── Standard Production Templates ───────────────────────────────────────────

# 1. System Prompt Template (Configurable persona, domain, and fallback)
SYSTEM_SCHEME_ASSIST_PROMPT = (
    "You are {assistant_name}, the official AI assistant specializing in {domain}.\n"
    "Tone & Style: {tone_instruction}\n"
    "Grounding Rules:\n"
    "- Answer strictly from the provided context guidelines.\n"
    "- If the answer is not present in the context, respond strictly with: '{fallback_message}'\n"
    "- Citation Requirement: {citation_rule}"
)

SYSTEM_SCHEME_ASSIST_TEMPLATE = PromptTemplate(
    template=SYSTEM_SCHEME_ASSIST_PROMPT,
    name="system_scheme_assist",
    version="1.0.0",
    description="Standard system prompt setting assistant persona, grounding rules, and fallback.",
    defaults={
        "assistant_name": "SchemeAssist",
        "domain": "government welfare schemes, eligibility rules, and application procedures",
        "tone_instruction": "Respond in concise, objective, and citizen-friendly language (2-3 sentences max).",
        "fallback_message": "I do not have sufficient verified information in the official guidelines to answer this query.",
        "citation_rule": "Cite official scheme circulars, portal links, or eligibility clauses whenever available.",
    },
)


# 2. Scheme Q&A Template V1 (Initial Baseline Template)
SCHEME_QA_PROMPT_V1 = (
    "You are a support assistant for welfare schemes. Answer ONLY from the context.\n"
    "If the answer isn't there, say you don't know.\n\n"
    "Context:\n"
    "{context}\n\n"
    "Question: {question}"
)

SCHEME_QA_TEMPLATE_V1 = PromptTemplate(
    template=SCHEME_QA_PROMPT_V1,
    name="scheme_qa",
    version="1.0.0",
    description="Baseline Q&A prompt template with context and question placeholders.",
)


# 3. Scheme Q&A Template V2 (Enhanced Production Template with Grounding & Citation)
SCHEME_QA_PROMPT_V2 = (
    "Role: {role_instruction}\n\n"
    "Context Information:\n"
    "\"\"\"\n"
    "{context}\n"
    "\"\"\"\n\n"
    "Citizen Question: {question}\n\n"
    "Instructions:\n"
    "1. Base your answer strictly on the context provided above.\n"
    "2. If the context does not contain the answer, reply with: \"{fallback_msg}\"\n"
    "3. Keep the response to {max_sentences} sentences.\n"
    "4. Format requirements: {format_guideline}"
)

SCHEME_QA_TEMPLATE_V2 = PromptTemplate(
    template=SCHEME_QA_PROMPT_V2,
    name="scheme_qa",
    version="2.0.0",
    description="Production Q&A template with citation rules, length limits, and strict grounding.",
    defaults={
        "role_instruction": "SchemeAssist welfare guidance specialist",
        "fallback_msg": "I do not have sufficient verified information to answer this question. Please consult the official department portal.",
        "max_sentences": "2 to 3",
        "format_guideline": "Plain text with bulleted points for lists of documents or criteria.",
    },
)


# 4. Scheme Batch Evaluator / CLI Inspection Template
SCHEME_BATCH_EVAL_PROMPT = (
    "[BATCH EVALUATION RUN #{batch_id}]\n"
    "Target Scheme: {scheme_name}\n"
    "Auditing Standard: {evaluation_criteria}\n\n"
    "Official Guidelines Context:\n"
    "{context}\n\n"
    "Evaluation Query / Test Scenario:\n"
    "{query}\n\n"
    "Required Output:\n"
    "- Verification Status (PASS / FAIL / INSUFFICIENT_DATA)\n"
    "- Direct Factual Findings (citing clause from context)\n"
    "- Recommendation for Citizen"
)

SCHEME_BATCH_EVAL_TEMPLATE = PromptTemplate(
    template=SCHEME_BATCH_EVAL_PROMPT,
    name="scheme_batch_eval",
    version="1.0.0",
    description="Batch evaluation prompt template for automated CLI audits and QA regression testing.",
    defaults={
        "evaluation_criteria": "Strict Compliance with Welfare Eligibility Guidelines",
    },
)


# 5. Scheme Eligibility Assessment Template
SCHEME_ELIGIBILITY_PROMPT = (
    "Evaluate eligibility for the following applicant against the official scheme guidelines.\n\n"
    "Scheme: {scheme_name}\n\n"
    "Official Scheme Rules:\n"
    "{context}\n\n"
    "Applicant Profile:\n"
    "- Age: {applicant_age}\n"
    "- Annual Family Income: {applicant_income}\n"
    "- Category / Demographics: {applicant_category}\n"
    "- Occupation / Status: {applicant_occupation}\n\n"
    "Determine:\n"
    "1. Is the applicant Eligible, Ineligible, or Needs Verification?\n"
    "2. Highlight matching / failing criteria based strictly on the scheme rules."
)

SCHEME_ELIGIBILITY_TEMPLATE = PromptTemplate(
    template=SCHEME_ELIGIBILITY_PROMPT,
    name="scheme_eligibility_eval",
    version="1.0.0",
    description="Applicant profiling and qualification evaluation prompt template.",
)


# 6. Scheme Executive Summary Template
SCHEME_SUMMARY_PROMPT = (
    "Generate an executive briefing summary for the scheme below.\n\n"
    "Scheme Title: {scheme_title}\n"
    "Target Audience: {target_audience}\n\n"
    "Context:\n"
    "{context}\n\n"
    "Provide a {max_points}-point bulleted summary highlighting objective, key benefits, and essential documents."
)

SCHEME_SUMMARY_TEMPLATE = PromptTemplate(
    template=SCHEME_SUMMARY_PROMPT,
    name="scheme_summary",
    version="1.0.0",
    description="Executive summary template for portal briefings and helpdesk digests.",
    defaults={
        "target_audience": "Citizens and Frontline Helpdesk Officers",
        "max_points": "3",
    },
)


# ─── Template Registry ────────────────────────────────────────────────────────
class TemplateRegistry:
    """
    Central catalog storing prompt templates across versions.
    Allows features to look up templates safely by name and optional version.
    """

    def __init__(self) -> None:
        self._registry: Dict[str, Dict[str, PromptTemplate]] = {}
        self._default_versions: Dict[str, str] = {}

    def register(self, template: PromptTemplate, is_default: bool = True) -> None:
        """Registers a template into the catalog."""
        if template.name not in self._registry:
            self._registry[template.name] = {}
        self._registry[template.name][template.version] = template
        if is_default or template.name not in self._default_versions:
            self._default_versions[template.name] = template.version

    def get(self, name: str, version: Optional[str] = None) -> PromptTemplate:
        """Retrieves a template by name and optional version (defaults to latest/default)."""
        if name not in self._registry:
            raise KeyError(
                f"Template '{name}' not found in registry. Available templates: {list(self._registry.keys())}"
            )
        versions_dict = self._registry[name]
        selected_version = version or self._default_versions.get(name)
        if selected_version not in versions_dict:
            raise KeyError(
                f"Version '{selected_version}' for template '{name}' not found. "
                f"Available versions: {list(versions_dict.keys())}"
            )
        return versions_dict[selected_version]

    def list_templates(self) -> List[Dict[str, Any]]:
        """Returns catalog metadata for all registered templates."""
        listing = []
        for name, versions in self._registry.items():
            for ver, tmpl in versions.items():
                listing.append({
                    "name": name,
                    "version": ver,
                    "is_default": (ver == self._default_versions.get(name)),
                    "description": tmpl.description,
                    "placeholders": sorted(list(tmpl.placeholders)),
                    "defaults": tmpl.defaults,
                })
        return listing


# Global Catalog Instance & Pre-Registration
registry = TemplateRegistry()
registry.register(SYSTEM_SCHEME_ASSIST_TEMPLATE)
registry.register(SCHEME_QA_TEMPLATE_V1, is_default=False)
registry.register(SCHEME_QA_TEMPLATE_V2, is_default=True)
registry.register(SCHEME_BATCH_EVAL_TEMPLATE)
registry.register(SCHEME_ELIGIBILITY_TEMPLATE)
registry.register(SCHEME_SUMMARY_TEMPLATE)
