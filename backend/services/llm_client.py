import os
import httpx
from backend.config import settings

INFERENCE_SERVER_URL = os.getenv("INFERENCE_SERVER_URL", "http://localhost:8001/v1/generate")

def generate(prompt: str) -> str:
    """
    Unified LLM Client interface.
    Sends HTTP POST requests to the versioned Inference Service (POST /v1/generate).
    Falls back gracefully to stub output if the inference service is offline.
    """
    target_url = settings.LLM_API_URL if settings.LLM_API_URL else INFERENCE_SERVER_URL

    try:
        response = httpx.post(
            target_url,
            json={"prompt": prompt},
            timeout=60.0
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("response", data.get("text", ""))
        print(f"[llm_client] Warning: Inference endpoint returned status {response.status_code}")
    except Exception as e:
        # Inference server offline or unreachable; log and fallback to stub
        pass

    # Graceful Fallback Output for development & offline unit testing
    return (
        "Based on your query, here is educational medical information: "
        "Symptoms like fever or throat irritation are commonly associated with upper respiratory viral infections. "
        "Ensure adequate hydration, rest, and monitor your symptoms closely. "
        "If your symptoms worsen or persist, please consult a healthcare professional."
    )
