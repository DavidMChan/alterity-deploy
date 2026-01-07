import os
import openai
from typing import List, Dict, Any

# Configuration
# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL") # e.g., http://vllm:8000/v1

# Primary Client (OpenAI)
openai_client = openai.OpenAI(
    api_key=OPENAI_API_KEY
)

# Local Client (vLLM)
from modules.config_manager import config_manager

vllm_client = None
if VLLM_BASE_URL:
    vllm_client = openai.OpenAI(
        api_key="EMPTY",
        base_url=VLLM_BASE_URL
    )

def get_local_models():
    return config_manager.get_local_models()

def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Wrapper for OpenAI-compatible chat completion with routing.
    """
    try:
        client = openai_client

        # Check if model should be routed to vLLM
        local_models = get_local_models()
        if model in local_models or model.startswith("local/"):
            if vllm_client:
                client = vllm_client
                print(f"[LLM] Routing to vLLM for model: {model}")
            else:
                print(f"[LLM Warning] Local model {model} requested but VLLM_BASE_URL not set. Falling back to OpenAI (this will likely fail).")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return {
            "content": f"[Error generating response: {str(e)}]",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }

def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Wrapper for embeddings.
    """
    try:
        response = client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[Embedding ERROR] {e}")
        return []
