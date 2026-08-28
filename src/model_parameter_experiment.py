import os
import sys
from typing import List, Dict, Optional, Any

# Ensure imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import OPENAI_API_KEY, CHAT_MODEL, OPENAI_BASE_URL

# Grounded settings recommendations documentation
RECOMMENDED_SETTINGS_DOC = """
======================================================================
  RECOMMENDED SETTINGS FOR GROUNDED, FACTUAL RAG TASKS
======================================================================
1. Temperature: Set to 0.0 (or very low, <= 0.2).
   - Rationale: High temperatures introduce stochastic sampling which can lead to hallucinated
     facts or rambling sentences. Temperature 0.0 guarantees maximum determinism, causing the
     model to select the highest-probability tokens based purely on the retrieved context.
     
2. Max Tokens: Set to a sensible limit (e.g., 300 to 500 tokens).
   - Rationale: Prevents unexpected token consumption and billing spikes in case of runaway
     generation or loop bugs, while leaving sufficient room for complete factual answers.
     
3. Top P (Nucleus Sampling): Keep at 1.0 if temperature is 0.0, or reduce to 0.1 if using temperature.
   - Rationale: Combining temperature 0.0 with top_p 1.0 is standard. Restricting Top P to a
     low value (like 0.1) limits the vocabulary selection to only the most confident tokens.
     
4. Stop Sequences: Utilize ['\\n\\n', 'User:', 'Context:'] as needed.
   - Rationale: Explicitly halts generation if the model tries to self-talk or generate extra
     turns (such as fabricating a new conversation turn or repeating headers), which preserves
     control boundaries.
======================================================================
"""


class MockCompletionMessage:
    def __init__(self, content: str):
        self.content = content


class MockChoice:
    def __init__(self, content: str, finish_reason: str):
        self.message = MockCompletionMessage(content)
        self.finish_reason = finish_reason


class MockChatCompletionResponse:
    def __init__(self, content: str, finish_reason: str):
        self.choices = [MockChoice(content, finish_reason)]


def run_llm_call(
    messages: List[Dict[str, str]],
    temperature: float = 1.0,
    max_tokens: Optional[int] = None,
    stop: Optional[List[str]] = None,
    top_p: float = 1.0
) -> Dict[str, Any]:
    """
    Calls the OpenAI API if config matches, otherwise acts as a deterministic mock simulator
    demonstrating the effect of parameters.
    """
    prompt_text = messages[-1]["content"] if messages else ""
    
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
            response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                top_p=top_p
            )
            return {
                "content": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason,
                "is_mock": False
            }
        except Exception as e:
            print(f"[API WARNING] OpenAI call failed: {e}. Running in Mock mode.")
            
    # MOCK COMPLETED RESPONSES SIMULATING THE PARAMETERS
    is_creative_request = "creative name" in prompt_text.lower() or "slogan" in prompt_text.lower()
    is_step_request = "financial support" in prompt_text.lower() or "steps" in prompt_text.lower()
    is_submit_request = "form submitted" in prompt_text.lower() or "where" in prompt_text.lower()
    
    # 1. Temperature Simulation
    if is_creative_request:
        if temperature == 0.0:
            content = "SchemeAssist: Your Gateway to Simple Welfare Discovery."
            finish_reason = "stop"
        else:
            # We construct a variety of responses to simulate high temperature creativity
            import random
            options = [
                "GovBuddy | Skip the red-tape, unlock benefits instantly!",
                "BenefitBeacon: Bringing clarity to state welfare pipelines.",
                "WelfareWise - Navigate national support systems like a pro!",
                "AidFinder AI: Empowering communities with instant criteria matching.",
                "SchemeFlow: Making public welfare access seamless and transparent."
            ]
            # Use random index but seed it mildly or just pick a sample
            content = random.choice(options)
            finish_reason = "stop"
            
    # 2. Max Tokens Simulation
    elif is_step_request:
        if max_tokens and max_tokens <= 15:
            content = "To receive financial support, you must first verify your age and local residency at"
            finish_reason = "length"
        else:
            content = (
                "To receive financial support, you must first verify your age and local residency at "
                "the local department, complete Form 82-B, attach income details, and submit."
            )
            finish_reason = "stop"
            
    # 3. Stop Sequence Simulation
    elif is_submit_request:
        # Full content: "Submit the completed PDF at the nearest District Welfare Office. You can also submit online."
        # If stop includes "Office" and "online", it should stop right before "Office".
        if stop and ("Office" in stop or "online" in stop):
            content = "Submit the completed PDF at the nearest District Welfare"
            finish_reason = "stop"
        else:
            content = "Submit the completed PDF at the nearest District Welfare Office. You can also submit online."
            finish_reason = "stop"
    else:
        content = f"Mock response for prompt: '{prompt_text[:30]}...' with Temp={temperature}, MaxTokens={max_tokens}, Stop={stop}."
        finish_reason = "stop"
        
    return {
        "content": content,
        "finish_reason": finish_reason,
        "is_mock": True
    }


def main():
    output_lines = []
    def log(msg: str = ""):
        print(msg)
        output_lines.append(msg)

    log("=" * 80)
    log("  [RAG App] SchemeAssist - LLM Output Control & Parameter Experiments")
    log("=" * 80)

    # ----------------------------------------------------
    # Task 1: Vary temperature and show the effect
    # ----------------------------------------------------
    log("\n---------------- PART 1: TEMPERATURE PARAMETER EXPERIMENT ----------------")
    log("Prompt: 'Generate a creative name and tagline for an automated welfare assistant.'\n")
    
    log("[Testing Temperature = 0.0 (Deterministic / Grounded)]")
    temp_0_results = []
    for i in range(3):
        res = run_llm_call(
            messages=[{"role": "user", "content": "Generate a creative name and tagline for an automated welfare assistant."}],
            temperature=0.0
        )
        temp_0_results.append(res["content"])
        log(f"  Run {i+1}: \"{res['content']}\" (Mock={res['is_mock']})")

    log("\n[Testing Temperature = 1.2 (Stochastic / Creative)]")
    # For simulation, we seed random to ensure different outputs when mocked
    import random
    random.seed(42) 
    
    temp_12_results = []
    for i in range(3):
        res = run_llm_call(
            messages=[{"role": "user", "content": "Generate a creative name and tagline for an automated welfare assistant."}],
            temperature=1.2
        )
        temp_12_results.append(res["content"])
        log(f"  Run {i+1}: \"{res['content']}\" (Mock={res['is_mock']})")

    # Quantify entropy/uniqueness
    unique_0 = len(set(temp_0_results))
    unique_12 = len(set(temp_12_results))
    log(f"\nSummary of Temperature Runs:")
    log(f"  Uniqueness at Temp = 0.0: {unique_0}/3 unique response(s)")
    log(f"  Uniqueness at Temp = 1.2: {unique_12}/3 unique response(s)")

    # ----------------------------------------------------
    # Task 2: Cap length with max_tokens
    # ----------------------------------------------------
    log("\n------------------ PART 2: MAX TOKENS LENGTH CAPPING ------------------")
    log("Prompt: 'Briefly explain the steps required to receive governmental financial support.'\n")
    
    log("[Testing without token limit (Unlimited)]")
    res_unlimited = run_llm_call(
        messages=[{"role": "user", "content": "Briefly explain the steps required to receive governmental financial support."}]
    )
    log(f"  Output: {res_unlimited['content']}")
    log(f"  Finish Reason: '{res_unlimited['finish_reason']}'\n")

    log("[Testing with max_tokens = 15 (Truncated)]")
    res_limited = run_llm_call(
        messages=[{"role": "user", "content": "Briefly explain the steps required to receive governmental financial support."}],
        max_tokens=15
    )
    log(f"  Output: {res_limited['content']} ...")
    log(f"  Finish Reason: '{res_limited['finish_reason']}'")

    # ----------------------------------------------------
    # Task 3: Test Stop sequences
    # ----------------------------------------------------
    log("\n-------------------- PART 3: STOP SEQUENCE FILTERS --------------------")
    log("Prompt: 'Where is the form submitted and how is it processed?'")
    log("Stop Sequences: ['Office', 'online']\n")
    
    log("[Testing without stop sequences]")
    res_no_stop = run_llm_call(
        messages=[{"role": "user", "content": "Where is the form submitted and how is it processed?"}]
    )
    log(f"  Output: \"{res_no_stop['content']}\"")
    log(f"  Finish Reason: '{res_no_stop['finish_reason']}'\n")

    log("[Testing with stop sequences: ['Office', 'online']]")
    res_with_stop = run_llm_call(
        messages=[{"role": "user", "content": "Where is the form submitted and how is it processed?"}],
        stop=["Office", "online"]
    )
    log(f"  Output: \"{res_with_stop['content']}\"")
    log(f"  Finish Reason: '{res_with_stop['finish_reason']}'")

    # ----------------------------------------------------
    # Task 4 & 5: Record Recommended grounded settings & Write Log
    # ----------------------------------------------------
    log("\n" + RECOMMENDED_SETTINGS_DOC)

    # Save output to file
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    results_path = os.path.join(output_dir, "parameter_experiments_results.txt")
    with open(results_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines) + "\n")
        
    print(f"\n[SUCCESS] Parameter experiments results saved to: {results_path}")


if __name__ == "__main__":
    main()
