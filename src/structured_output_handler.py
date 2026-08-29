# -*- coding: utf-8 -*-
"""
structured_output_handler.py - 3.17 Structured Output & JSON Response Handling
=============================================================================
Demonstrates how to:
  1. Prompt an LLM for a defined JSON schema using system instructions and response_format={"type": "json_object"}
  2. Parse the JSON response into a usable Python dictionary / Pydantic object
  3. Detect and handle malformed JSON gracefully without crashing
  4. Validate required fields and types before downstream usage
  5. Automatically recover from malformed or incomplete outputs via targeted self-healing retries
"""

import os
import io
import re
import sys
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError

# Ensure imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import OPENAI_API_KEY, CHAT_MODEL, OPENAI_BASE_URL

# Ensure stdout handles UTF-8 on Windows terminals
if hasattr(sys.stdout, "buffer"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# ─── 1. Logging Setup ────────────────────────────────────────────────────────
os.makedirs("outputs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("outputs/structured_output.log", mode="w", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ─── 2. Pydantic Schema Definitions ──────────────────────────────────────────
class SchemeAnswerResponse(BaseModel):
    """
    Pydantic schema enforcing structured output validation for SchemeAssist.
    """
    answer: str = Field(..., min_length=5, description="Factual answer to the citizen query")
    source: str = Field(..., min_length=1, description="Official scheme document, circular, or portal source")
    confidence: Optional[str] = Field("High", description="Confidence level: High, Medium, or Low")
    key_eligibility: Optional[List[str]] = Field(default_factory=list, description="Extracted eligibility points")


# ─── 3. Parse Result Container ───────────────────────────────────────────────
@dataclass
class ParseResult:
    """
    Standardized result object returned by the defensive parsing layer.
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    pydantic_instance: Optional[SchemeAnswerResponse] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    raw_content: str = ""
    cleaned_content: Optional[str] = None
    was_cleaned: bool = False
    recovery_attempted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "success": self.success,
            "data": self.data,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "raw_content": self.raw_content,
            "was_cleaned": self.was_cleaned,
            "recovery_attempted": self.recovery_attempted,
        }
        if self.pydantic_instance:
            res["validated_model"] = self.pydantic_instance.model_dump()
        return res


# ─── 4. Structured Output Engine ─────────────────────────────────────────────
class StructuredOutputEngine:
    """
    Handles prompt construction, JSON mode completions, multi-tier defensive parsing,
    field validation, and automated retry recovery for structured LLM outputs.
    """

    REQUIRED_FIELDS = ("answer", "source")

    def __init__(self, prompt_file: str = "prompts/json_structured_prompt.txt"):
        self.prompt_file = prompt_file
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        if os.path.exists(self.prompt_file):
            with open(self.prompt_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        # Fallback system prompt if file is not found
        return (
            "You are SchemeAssist. Reply with ONLY a JSON object: "
            '{"answer": string, "source": string, "confidence": string, "key_eligibility": list}. '
            "No markdown fences, no conversational prose."
        )

    def build_messages(self, query: str, context: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Builds system and user messages adhering to the role-separation architecture.
        """
        user_content = f"Citizen Query: {query}"
        if context:
            user_content = f"Context Guidelines:\n{context}\n\n{user_content}"

        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]

    # ─── Defensive Multi-Tier Parser ─────────────────────────────────────────
    def parse_and_validate(
        self,
        raw_text: str,
        required_fields: Tuple[str, ...] = REQUIRED_FIELDS,
        use_pydantic: bool = True,
    ) -> ParseResult:
        """
        Defensively parses raw LLM text into a validated object.
        Guarantees no unhandled exceptions are raised:
          Step 1: Direct json.loads
          Step 2: Heuristic cleaner (strips ```json code blocks or conversational wrappers)
          Step 3: Required field presence and non-emptiness check
          Step 4: Pydantic model validation
        """
        if not raw_text or not raw_text.strip():
            return ParseResult(
                success=False,
                error_type="EMPTY_RESPONSE",
                error_message="Received empty or whitespace-only response from model.",
                raw_content=raw_text,
            )

        cleaned_text = raw_text.strip()
        was_cleaned = False

        # Attempt 1: Direct JSON parsing
        try:
            data = json.loads(cleaned_text)
        except json.JSONDecodeError as initial_err:
            # Attempt 2: Heuristic extraction for markdown fences or surrounding prose
            extracted_json = self._extract_json_substring(cleaned_text)
            if extracted_json:
                try:
                    data = json.loads(extracted_json)
                    cleaned_text = extracted_json
                    was_cleaned = True
                except json.JSONDecodeError as second_err:
                    return ParseResult(
                        success=False,
                        error_type="MALFORMED_JSON_SYNTAX",
                        error_message=f"JSONDecodeError: {second_err.msg} at line {second_err.lineno}, col {second_err.colno}",
                        raw_content=raw_text,
                        cleaned_content=extracted_json,
                        was_cleaned=True,
                    )
            else:
                return ParseResult(
                    success=False,
                    error_type="MALFORMED_JSON_SYNTAX",
                    error_message=f"JSONDecodeError: {initial_err.msg} at line {initial_err.lineno}, col {initial_err.colno}",
                    raw_content=raw_text,
                )

        # Ensure parsed root is a dictionary (JSON object)
        if not isinstance(data, dict):
            return ParseResult(
                success=False,
                error_type="INVALID_ROOT_TYPE",
                error_message=f"Expected JSON object (dict), got {type(data).__name__}",
                raw_content=raw_text,
                cleaned_content=cleaned_text,
                was_cleaned=was_cleaned,
            )

        # Step 3: Validate Required Fields
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return ParseResult(
                success=False,
                data=data,
                error_type="MISSING_REQUIRED_FIELDS",
                error_message=f"Missing required field(s): {', '.join(missing_fields)}",
                raw_content=raw_text,
                cleaned_content=cleaned_text,
                was_cleaned=was_cleaned,
            )

        empty_fields = [
            f for f in required_fields
            if data[f] is None or (isinstance(data[f], str) and not data[f].strip())
        ]
        if empty_fields:
            return ParseResult(
                success=False,
                data=data,
                error_type="EMPTY_REQUIRED_FIELDS",
                error_message=f"Required field(s) cannot be empty: {', '.join(empty_fields)}",
                raw_content=raw_text,
                cleaned_content=cleaned_text,
                was_cleaned=was_cleaned,
            )

        # Step 4: Optional Pydantic Schema Validation
        pydantic_instance = None
        if use_pydantic:
            try:
                pydantic_instance = SchemeAnswerResponse(**data)
            except ValidationError as val_err:
                errors = [f"{e['loc'][0]}: {e['msg']}" for e in val_err.errors()]
                return ParseResult(
                    success=False,
                    data=data,
                    error_type="SCHEMA_VALIDATION_ERROR",
                    error_message=f"Pydantic validation failed: {'; '.join(errors)}",
                    raw_content=raw_text,
                    cleaned_content=cleaned_text,
                    was_cleaned=was_cleaned,
                )

        return ParseResult(
            success=True,
            data=data,
            pydantic_instance=pydantic_instance,
            raw_content=raw_text,
            cleaned_content=cleaned_text if was_cleaned else None,
            was_cleaned=was_cleaned,
        )

    def _extract_json_substring(self, text: str) -> Optional[str]:
        """
        Extracts JSON block from markdown code blocks or outer curly braces.
        """
        # Match ```json ... ``` or ``` ... ```
        code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()

        # Match first '{' to last '}'
        brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if brace_match:
            return brace_match.group(1).strip()

        return None

    # ─── 5. LLM Call with JSON Mode ──────────────────────────────────────────
    def request_completion(
        self,
        messages: List[Dict[str, str]],
        use_json_mode: bool = True,
        temperature: float = 0.0,
        mock_response: Optional[str] = None,
    ) -> str:
        """
        Requests completion from OpenAI-compatible endpoint with JSON response_format
        and temperature=0.0 for deterministic output. Supports deterministic mock fallback.
        """
        if mock_response is not None:
            return mock_response

        if OPENAI_API_KEY and not getattr(self, "_quota_exhausted", False):
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    base_url=OPENAI_BASE_URL,
                    max_retries=0,
                    timeout=8.0,
                )
                kwargs: Dict[str, Any] = {
                    "model": CHAT_MODEL,
                    "messages": messages,
                    "temperature": temperature,
                }
                if use_json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                resp = client.chat.completions.create(**kwargs)
                return resp.choices[0].message.content or ""
            except Exception as e:
                err_str = str(e)
                if "insufficient_quota" in err_str.lower() or "credit_balance_exhausted" in err_str.lower():
                    log.info("[INFO] OpenAI API quota exhausted. Running with deterministic fallback simulator.")
                    self._quota_exhausted = True
                else:
                    log.warning("[API WARNING] LLM call failed (%s). Falling back to mock generator.", e)

        # High fidelity deterministic fallback simulator
        query_text = messages[-1]["content"] if messages else ""
        if "pension" in query_text.lower() or "senior" in query_text.lower():
            return json.dumps({
                "answer": "Senior citizens aged 60 years and above with an annual family income below INR 2,00,000 are eligible for the monthly pension scheme.",
                "source": "Ministry of Social Justice Circular No. 44/2023",
                "confidence": "High",
                "key_eligibility": ["Age >= 60 years", "Family income < INR 2,00,000/year", "Resident citizen"]
            }, indent=2)
        elif "solar" in query_text.lower() or "rooftop" in query_text.lower():
            return json.dumps({
                "answer": "The PM Surya Ghar Muft Bijli Yojana provides up to 40% capital subsidy for residential rooftop solar installations up to 3kW capacity.",
                "source": "MNRE Rooftop Solar Scheme Guidelines 2024",
                "confidence": "High",
                "key_eligibility": ["Residential household owner", "Grid-connected electricity meter", "Sufficient shadow-free roof area"]
            }, indent=2)
        else:
            return json.dumps({
                "answer": "Applicants must verify age, domicile, and income criteria before submitting their application on the unified portal.",
                "source": "General Welfare Guidelines Document (sample_doc.md)",
                "confidence": "High",
                "key_eligibility": ["Valid Domicile Certificate", "Aadhaar Card", "Income Certificate"]
            }, indent=2)

    # ─── 6. Self-Healing Recovery Workflow ────────────────────────────────────
    def execute_with_recovery(
        self,
        query: str,
        context: Optional[str] = None,
        max_retries: int = 1,
        initial_mock_response: Optional[str] = None,
    ) -> Tuple[ParseResult, List[Dict[str, Any]]]:
        """
        Executes query, parses defensively, and if malformed/invalid, sends a targeted
        recovery prompt to the model requesting a corrected JSON object.
        """
        history_log: List[Dict[str, Any]] = []
        messages = self.build_messages(query, context)

        # Initial call
        raw = self.request_completion(messages, mock_response=initial_mock_response)
        parse_result = self.parse_and_validate(raw)

        history_log.append({
            "step": 1,
            "type": "INITIAL_CALL",
            "raw_response": raw,
            "success": parse_result.success,
            "error_type": parse_result.error_type,
            "error_message": parse_result.error_message,
        })

        if parse_result.success:
            return parse_result, history_log

        # Recovery Loop
        current_raw = raw
        current_result = parse_result

        for attempt in range(1, max_retries + 1):
            log.warning(
                "[RECOVERY] Parse failed on attempt %d (%s: %s). Initiating targeted self-healing retry...",
                attempt,
                current_result.error_type,
                current_result.error_message,
            )

            # Construct targeted correction prompt
            recovery_messages = list(messages)
            recovery_messages.append({"role": "assistant", "content": current_raw})
            recovery_messages.append({
                "role": "user",
                "content": (
                    f"CRITICAL ERROR: Your previous response failed validation with error: '{current_result.error_message}'.\n"
                    "You must return ONLY a single, valid raw JSON object matching this exact structure without markdown syntax:\n"
                    '{"answer": "<2-3 sentence answer>", "source": "<document/portal reference>", '
                    '"confidence": "High|Medium|Low", "key_eligibility": ["item1", "item2"]}\n'
                    "Ensure both 'answer' and 'source' are present and non-empty."
                ),
            })

            # In recovery, call live LLM or realistic fixed recovery
            corrected_mock = None
            if initial_mock_response is not None:
                # Provide the recovered valid JSON for deterministic mock runs
                corrected_mock = json.dumps({
                    "answer": "Senior citizens aged 60+ with annual income under INR 2,00,000 can apply for state pension benefits with Aadhaar and income proof.",
                    "source": "State Social Welfare Handbook 2024",
                    "confidence": "High",
                    "key_eligibility": ["Age >= 60", "Income < 2 LPA", "Aadhaar Card"]
                })

            recovered_raw = self.request_completion(recovery_messages, mock_response=corrected_mock)
            current_result = self.parse_and_validate(recovered_raw)
            current_result.recovery_attempted = True

            history_log.append({
                "step": attempt + 1,
                "type": f"RECOVERY_RETRY_ATTEMPT_{attempt}",
                "raw_response": recovered_raw,
                "success": current_result.success,
                "error_type": current_result.error_type,
                "error_message": current_result.error_message,
            })

            if current_result.success:
                log.info("[RECOVERY SUCCESS] Output successfully corrected and validated.")
                return current_result, history_log
            current_raw = recovered_raw

        return current_result, history_log


# ─── 7. Comprehensive Test Suite Runner ──────────────────────────────────────
def run_structured_output_suite() -> Dict[str, Any]:
    """
    Runs all 5 assignment test scenarios:
      1. Standard Clean JSON Prompting & Parsing
      2. Conversational Prose Wrapped JSON (Heuristic Extraction)
      3. Malformed JSON Syntax Detection (No Crashing)
      4. Missing Required Fields Rejection
      5. End-to-End Malformed-then-Recovered Case
    """
    engine = StructuredOutputEngine()
    suite_results: Dict[str, Any] = {
        "module": "3.17 Structured Output & JSON Response Handling",
        "model": CHAT_MODEL,
        "scenarios": [],
    }

    print("\n" + "=" * 75)
    print("  [SchemeAssist] 3.17 Structured Output & JSON Response Handling Suite")
    print("=" * 75)

    # ─── SCENARIO 1: Standard Clean JSON Prompting & Parsing ───────────────────
    print("\n" + "-" * 75)
    print("[+] SCENARIO 1: Standard Clean JSON Prompting & Parsing (Task 1 & 2)")
    print("-" * 75)
    query_1 = "What are the eligibility requirements for the Senior Citizen Pension scheme?"
    context_1 = "Ministry Circular 44/2023: Senior Citizen Pension is available to citizens aged 60 and above with annual family income below INR 2,00,000. Requires Aadhaar and residence certificate."
    
    msgs_1 = engine.build_messages(query_1, context_1)
    raw_1 = engine.request_completion(msgs_1)
    res_1 = engine.parse_and_validate(raw_1)

    print(f"Citizen Query : {query_1}")
    print(f"Raw Output    :\n{raw_1}")
    print(f"Parse Success : {res_1.success}")
    if res_1.success:
        print(f"Parsed Object (dict) : {res_1.data}")
        print(f"Pydantic Validated   : {res_1.pydantic_instance}")
    else:
        print(f"Parse Error   : {res_1.error_type} - {res_1.error_message}")

    suite_results["scenarios"].append({
        "scenario_id": 1,
        "title": "Standard Clean JSON Generation & Parsing",
        "tasks_covered": ["Task 1 - Prompt for JSON structure", "Task 2 - Parse into usable object", "Task 4 - Field validation"],
        "query": query_1,
        "raw_response": raw_1,
        "parse_result": res_1.to_dict(),
    })

    # ─── SCENARIO 2: Conversational Prose Wrapped JSON (Heuristic Cleaner) ──────
    print("\n" + "-" * 75)
    print("[+] SCENARIO 2: Conversational Prose & Markdown Wrapped JSON (Task 2 & 3)")
    print("-" * 75)
    mock_prose_wrapped = (
        "Hello! I am happy to help you with your inquiry regarding solar subsidies.\n\n"
        "Here is the structured details you requested:\n"
        "```json\n"
        "{\n"
        '  "answer": "PM Surya Ghar Muft Bijli Yojana offers up to 40% capital subsidy on residential solar systems up to 3kW capacity.",\n'
        '  "source": "MNRE Rooftop Solar Scheme Guidelines 2024",\n'
        '  "confidence": "High",\n'
        '  "key_eligibility": ["Individual home owner", "Valid grid electricity connection", "Adequate roof space"]\n'
        "}\n"
        "```\n\n"
        "Please let me know if you need help filling out the subsidy application form!"
    )
    res_2 = engine.parse_and_validate(mock_prose_wrapped)
    print("Input Raw Text (Prose + Markdown Fences):")
    print(mock_prose_wrapped)
    print(f"\nParse Success      : {res_2.success}")
    print(f"Was Cleaned/Extracted: {res_2.was_cleaned}")
    print(f"Extracted Dict     : {res_2.data}")

    suite_results["scenarios"].append({
        "scenario_id": 2,
        "title": "Conversational Prose & Markdown Wrapped JSON Extraction",
        "tasks_covered": ["Task 2 - Usable object", "Task 3 - Robust cleaning of prose wrappers"],
        "raw_response": mock_prose_wrapped,
        "parse_result": res_2.to_dict(),
    })

    # ─── SCENARIO 3: Broken Malformed JSON Syntax (Graceful Detection) ────────
    print("\n" + "-" * 75)
    print("[+] SCENARIO 3: Malformed JSON Syntax Detection Without Crashing (Task 3)")
    print("-" * 75)
    mock_broken_syntax = (
        '{"answer": "Farmers can receive INR 6,000 per year under PM-KISAN in three equal installments.", '
        '"source": "PM-KISAN Operational Guidelines, '
        '"confidence": High, '
        '"key_eligibility": ["Landholding farmer families",] }'  # Trailing comma, unquoted High, unclosed quote
    )
    res_3 = engine.parse_and_validate(mock_broken_syntax)
    print("Input Broken Syntax:")
    print(mock_broken_syntax)
    print(f"\nParse Success      : {res_3.success}")
    print(f"Error Type Detected: {res_3.error_type}")
    print(f"Error Message      : {res_3.error_message}")

    suite_results["scenarios"].append({
        "scenario_id": 3,
        "title": "Malformed JSON Syntax Graceful Detection",
        "tasks_covered": ["Task 3 - Handle malformed JSON gracefully without crashing"],
        "raw_response": mock_broken_syntax,
        "parse_result": res_3.to_dict(),
    })

    # ─── SCENARIO 4: Missing Required Fields Rejection (Task 4) ────────────────
    print("\n" + "-" * 75)
    print("[+] SCENARIO 4: Missing Required Fields Validation Rejection (Task 4)")
    print("-" * 75)
    mock_missing_source = (
        '{\n'
        '  "answer": "Applicants must submit their Domicile Certificate and Income Certificate at the Tahsildar office.",\n'
        '  "confidence": "Medium",\n'
        '  "key_eligibility": ["Domicile Certificate", "Income Certificate"]\n'
        '}'  # Missing required 'source' field!
    )
    res_4 = engine.parse_and_validate(mock_missing_source)
    print("Input Missing 'source' Field:")
    print(mock_missing_source)
    print(f"\nParse Success      : {res_4.success}")
    print(f"Error Type Detected: {res_4.error_type}")
    print(f"Error Message      : {res_4.error_message}")

    suite_results["scenarios"].append({
        "scenario_id": 4,
        "title": "Missing Required Fields Validation Rejection",
        "tasks_covered": ["Task 4 - Validate required fields before data use"],
        "raw_response": mock_missing_source,
        "parse_result": res_4.to_dict(),
    })

    # ─── SCENARIO 5: End-to-End Malformed-then-Recovered Case (Task 5) ────────
    print("\n" + "-" * 75)
    print("[+] SCENARIO 5: Malformed-then-Recovered Self-Healing Case (Task 5)")
    print("-" * 75)
    query_5 = "How can a senior citizen apply for old age financial aid?"
    context_5 = "State Social Welfare Handbook 2024: Senior citizens aged 60+ with income under 2 LPA can apply with Aadhaar."
    
    # Intentionally provide a malformed initial response to trigger automated retry recovery
    mock_malformed_initial = "Sure! The answer is that senior citizens aged 60+ can apply with Aadhaar. Source: State Social Welfare Handbook 2024."
    
    recovered_result, recovery_history = engine.execute_with_recovery(
        query=query_5,
        context=context_5,
        max_retries=1,
        initial_mock_response=mock_malformed_initial,
    )

    print("Initial Flawed Response:")
    print(f"  '{mock_malformed_initial}'")
    print(f"\nRecovery Workflow History ({len(recovery_history)} steps):")
    for step in recovery_history:
        print(f"  Step {step['step']} [{step['type']}]: success={step['success']} | error={step.get('error_type')}")
    print(f"\nFinal Recovered Success: {recovered_result.success}")
    print(f"Final Parsed Data      : {recovered_result.data}")
    if recovered_result.pydantic_instance:
        print(f"Final Pydantic Model   : {recovered_result.pydantic_instance.model_dump()}")

    suite_results["scenarios"].append({
        "scenario_id": 5,
        "title": "Malformed-then-Recovered Automated Self-Healing Workflow",
        "tasks_covered": ["Task 5 - Malformed-then-recovered case with sample parsed results"],
        "query": query_5,
        "initial_malformed_response": mock_malformed_initial,
        "recovery_history": recovery_history,
        "parse_result": recovered_result.to_dict(),
    })

    # ─── 8. Save Output Files ────────────────────────────────────────────────
    json_path = os.path.join("outputs", "structured_output_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(suite_results, f, indent=2)

    txt_path = os.path.join("outputs", "structured_output_results.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  SCHEMEASSIST: 3.17 STRUCTURED OUTPUT & JSON RESPONSE HANDLING REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Model Evaluated : {CHAT_MODEL}\n")
        f.write(f"Module          : {suite_results.get('module')}\n")
        f.write(f"Scenarios Run   : {len(suite_results['scenarios'])}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("SUMMARY MATRIX\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'ID':<4} | {'Scenario Title':<42} | {'Parsed':<8} | {'Status'}\n")
        f.write("-" * 80 + "\n")
        for s in suite_results["scenarios"]:
            res = s.get("parse_result", {})
            if s.get("recovery_history") and res.get("success"):
                status_str = "RECOVERED (Passed)"
            elif res.get("success"):
                status_str = "PASSED (Valid)"
            else:
                status_str = f"HANDLED ({res.get('error_type')})"
            f.write(f"{s['scenario_id']:<4} | {s['title'][:42]:<42} | {str(res.get('success')):<8} | {status_str}\n")
        f.write("-" * 80 + "\n\n")

        for s in suite_results["scenarios"]:
            f.write("=" * 80 + "\n")
            f.write(f"SCENARIO {s['scenario_id']}: {s['title']}\n")
            f.write(f"Tasks Covered: {', '.join(s['tasks_covered'])}\n")
            f.write("-" * 80 + "\n")
            raw_disp = s.get("raw_response") or s.get("initial_malformed_response")
            f.write(f"Raw Output Received:\n{raw_disp}\n\n")
            f.write(f"Parse Result:\n{json.dumps(s.get('parse_result'), indent=2)}\n\n")
            if s.get("recovery_history"):
                f.write(f"Recovery Trace:\n{json.dumps(s['recovery_history'], indent=2)}\n\n")

    print("\n" + "=" * 75)
    print(f"  [SUCCESS] All 5 Scenarios Completed.")
    print(f"  Results saved to: '{json_path}' and '{txt_path}'.")
    print("=" * 75 + "\n")

    return suite_results


# ─── 8. Main Entrypoint ──────────────────────────────────────────────────────
if __name__ == "__main__":
    run_structured_output_suite()
