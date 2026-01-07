from typing import Dict, Any
import sys
import os

# Add parent directory to path to find llm module if running as script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import chat_completion

def construct_system_prompt(demographics: Dict[str, Any], prompt_template: str = None) -> str:
    """
    Constructs a system prompt forcing the model to adopt specific demographics.
    """
    age = demographics.get("age", "unknown")
    gender = demographics.get("gender", "unknown")
    party = demographics.get("political_party", "unknown")

    base_prompt = (
        f"You are a {age} year old {gender} who identifies as a {party}."
    )

    if prompt_template:
        return f"{base_prompt} {prompt_template}"

    return base_prompt

def run_demographic_forcing(probe_question: str, demographics: Dict[str, Any], model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
    """
    Executes a probe using simple demographic forcing.
    """
    system_prompt = construct_system_prompt(demographics)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": probe_question}
    ]

    print(f"[LLM CALL] System: {system_prompt}")

    # Real LLM Call
    response_data = chat_completion(messages, model=model)
    return response_data # Returns dict with 'content' and 'usage'
