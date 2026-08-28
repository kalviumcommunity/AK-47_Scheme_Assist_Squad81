import os
import sys
import tiktoken
from typing import List, Dict, Callable

# Ensure imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import OPENAI_API_KEY, CHAT_MODEL

class ChatHistoryManager:
    def __init__(self, system_prompt: str, token_budget: int = 300, model: str = "gpt-4o-mini", strategy: str = "trim", logger: Callable[[str], None] = print):
        """
        Initializes the budget-aware chat history manager.
        - system_prompt: The overarching system prompt, which is always preserved.
        - token_budget: The maximum allowed tokens for the entire message list.
        - model: The model identifier used for tokenizer selection.
        - strategy: Either 'trim' or 'summarize'.
        - logger: Callable function used for logging outputs (defaults to print).
        """
        self.system_prompt = system_prompt
        self.token_budget = token_budget
        self.model = model
        self.strategy = strategy.lower()
        self.logger = logger
        
        # Initialize internal message structure
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Load tokenizer
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self) -> int:
        """
        Calculates exact chat completion tokens for the message history list,
        accounting for OpenAI chat template syntax overhead.
        """
        tokens_per_message = 3
        tokens_per_name = 1
        num_tokens = 0
        
        for message in self.messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(self.encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # Prima elements for the assistant reply wrapper
        return num_tokens

    def add_message(self, role: str, content: str):
        """
        Adds a new message to the history and automatically enforces the token budget constraint.
        """
        self.messages.append({"role": role, "content": content})
        self.enforce_budget()

    def enforce_budget(self):
        """
        Ensures the current token count of the history remains under the budget limit.
        """
        current_tokens = self.count_tokens()
        if current_tokens <= self.token_budget:
            return

        self.logger(f"\n[BUDGET EXCEEDED] Current tokens: {current_tokens} > Budget: {self.token_budget}")
        self.logger(f"Applying strategy: '{self.strategy.upper()}' to reduce token footprint...")

        if self.strategy == "trim":
            self._apply_trimming()
        elif self.strategy == "summarize":
            self._apply_summarization()
        else:
            self.logger(f"[ERROR] Unknown budget enforcement strategy: {self.strategy}")

    def _apply_trimming(self):
        """
        Trimming strategy: Removals are performed in User-Assistant pairs to preserve turn cohesion.
        The initial system message is never deleted.
        """
        while self.count_tokens() > self.token_budget:
            if len(self.messages) > 3:
                # Remove oldest user-assistant pair (index 1 & 2)
                removed_1 = self.messages.pop(1)
                removed_2 = self.messages.pop(1)
                self.logger(f"  -> Trimmed oldest conversation turn:\n     User:   {removed_1['content'][:40]}...\n     Assist: {removed_2['content'][:40]}...")
            elif len(self.messages) > 1:
                # If only one message left, trim it
                removed = self.messages.pop(1)
                self.logger(f"  -> Trimmed last single message: {removed['role']} - {removed['content'][:40]}...")
            else:
                break
        
        self.logger(f"  -> Trimming complete. New token count: {self.count_tokens()}")

    def _apply_summarization(self):
        """
        Summarization strategy: Condenses older message turns into a single summary block,
        which is placed as a system instruction metadata block directly after the system prompt.
        """
        if len(self.messages) <= 3:
            self.logger("  -> Not enough turns to summarize. Trimming instead.")
            self._apply_trimming()
            return

        # Separate system prompt, candidate turns to summarize, and active context (last 2 messages)
        system_msg = self.messages[0]
        recent_msgs = self.messages[-2:]
        middle_msgs = self.messages[1:-2]

        # Extract dialogue summary
        turns_text = []
        for msg in middle_msgs:
            turns_text.append(f"{msg['role'].upper()}: {msg['content']}")
        conversation_transcript = "\n".join(turns_text)

        summary_text = self._generate_summary(conversation_transcript)

        # Build new history: system + summary message + active context turns
        summary_msg = {
            "role": "system",
            "content": f"[Summary of earlier discussion: {summary_text}]"
        }

        self.messages = [system_msg, summary_msg] + recent_msgs
        new_tokens = self.count_tokens()
        self.logger(f"  -> Summarization complete. New token count: {new_tokens}")

        # If we are STILL exceeding budget (e.g. the summary itself or recent turns are too large),
        # we will have to trim.
        if new_tokens > self.token_budget:
            self.logger("  -> Summary + recent turns still exceed budget. Applying fallback trimming.")
            self._apply_trimming()

    def _generate_summary(self, transcript: str) -> str:
        """
        Generates a summary of the transcript. Calls OpenAI's ChatCompletion API
        if keys are present, otherwise falls back to a deterministic local/mock summarizer.
        """
        if OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful system utility. Write a highly concise, 1-sentence summary of the following chat history transcript."},
                        {"role": "user", "content": transcript}
                    ],
                    max_tokens=60,
                    temperature=0.3
                )
                raw_summary = response.choices[0].message.content.strip()
                return raw_summary
            except Exception as e:
                self.logger(f"  [API SUMMARIZE WARNING] API call failed: {e}. Falling back to mock summarizer.")
        
        # Local/Mock summarizer logic
        items = []
        if "welfare" in transcript.lower():
            items.append("government welfare scheme details")
        if "eligibility" in transcript.lower():
            items.append("eligibility requirements")
        if "income" in transcript.lower() or "limit" in transcript.lower():
            items.append("income thresholds")
        if "document" in transcript.lower() or "proof" in transcript.lower():
            items.append("documentation checklists")
            
        topics = ", ".join(items) if items else "general queries"
        return f"User and Assistant discussed {topics} including qualifications."


def simulate_conversation(strategy: str, budget: int = 180) -> List[str]:
    """
    Simulates a multi-turn conversation that exceeds the specified token budget.
    """
    output_lines = []
    def log(msg: str = ""):
        print(msg)
        output_lines.append(msg)

    system_prompt = "You are SchemeAssist, a helpful government welfare scheme RAG assistant."
    
    log("*" * 80)
    log(f"   STARTING SIMULATION WITH STRATEGY: {strategy.upper()} (Budget: {budget})")
    log("*" * 80)

    manager = ChatHistoryManager(
        system_prompt=system_prompt,
        token_budget=budget,
        model=CHAT_MODEL,
        strategy=strategy,
        logger=log
    )

    # 1. Turn 1 (Within budget)
    log("\n--- TURN 1 ---")
    user_q1 = "What eligibility rules apply for the Senior Citizen Support scheme?"
    log(f"User: {user_q1}")
    manager.add_message("user", user_q1)
    
    assistant_a1 = (
        "The Senior Citizen Support scheme requires applicants to be 60+ years old "
        "and have an annual income under $2,500. Documentation includes proof of age and income."
    )
    log(f"Assistant: {assistant_a1}")
    manager.add_message("assistant", assistant_a1)
    log(f"Current History Token Count: {manager.count_tokens()}")

    # 2. Turn 2 (Retrieving extra documentation chunk, leading to budget expansion)
    log("\n--- TURN 2 ---")
    user_q2 = "Can you show me the exact documentation guidelines and proof of income requirements?"
    log(f"User: {user_q2}")
    manager.add_message("user", user_q2)

    retrieved_chunk = (
        "Official Income Verification circular and guidelines: "
        "All applicants must submit a certified copy of tax returns or a salary certificate "
        "issued by a recognized local gazetted authority. Self-employed individuals need "
        "an affidavit from a notary public confirming average monthly income limits. "
        "The government reserves the right to audit bank accounts."
    )
    
    assistant_a2 = (
        f"Based on the official circular: '{retrieved_chunk}', you can submit either tax returns, "
        "a salary certificate, or an affidavit from a notary public."
    )
    log(f"Assistant: {assistant_a2}")
    manager.add_message("assistant", assistant_a2)
    log(f"Current History Token Count: {manager.count_tokens()}")

    # 3. Turn 3 (This turn will definitely overflow the small budget of 180 tokens)
    log("\n--- TURN 3 (Will overflow budget) ---")
    user_q3 = "What is the processing time and where should I submit my completed form?"
    log(f"User: {user_q3}")
    manager.add_message("user", user_q3)
    
    assistant_a3 = (
        "Applications are processed in 15 business days at the District Welfare Office. "
        "You can submit it in person or online via the official scheme portal: schemeassist.gov.in."
    )
    log(f"Assistant: {assistant_a3}")
    manager.add_message("assistant", assistant_a3)
    log(f"Final History Token Count: {manager.count_tokens()}")

    log("\nFinal Message History State:")
    for i, msg in enumerate(manager.messages):
        log(f"  [{i}] {msg['role'].upper()}: {msg['content'][:120]}...")

    log("*" * 80)
    log(f"   COMPLETED SIMULATION FOR STRATEGY: {strategy.upper()}")
    log("*" * 80 + "\n")

    return output_lines

def main():
    all_output = []
    
    # Run Trimming Simulation
    trim_log = simulate_conversation(strategy="trim", budget=180)
    all_output.extend(trim_log)
    
    # Run Summarization Simulation
    sum_log = simulate_conversation(strategy="summarize", budget=180)
    all_output.extend(sum_log)

    # Save simulation results to file
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    results_path = os.path.join(output_dir, "history_management_results.txt")
    with open(results_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_output) + "\n")
    
    print(f"[SUCCESS] History Management simulation results saved to: {results_path}")

if __name__ == "__main__":
    main()
