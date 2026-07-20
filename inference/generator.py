import time
import torch
from typing import Tuple

from inference.config import settings
from inference.model_loader import model_loader

def generate_text(
    prompt: str,
    max_new_tokens: int = None,
    temperature: float = None,
    top_p: float = None
) -> Tuple[str, float]:
    """
    Executes model generation given a prompt.
    Returns (generated_response, generation_time_ms).
    """
    start_time = time.time()

    max_new_tokens = max_new_tokens or settings.DEFAULT_MAX_NEW_TOKENS
    temperature = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
    top_p = top_p if top_p is not None else settings.DEFAULT_TOP_P

    # If model is loaded on GPU, run true inference
    if model_loader.is_model_loaded and model_loader.model is not None and model_loader.tokenizer is not None:
        try:
            inputs = model_loader.tokenizer(prompt, return_tensors="pt").to(model_loader.model.device)
            with torch.no_grad():
                outputs = model_loader.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    repetition_penalty=settings.DEFAULT_REPETITION_PENALTY,
                    do_sample=True,
                    pad_token_id=model_loader.tokenizer.eos_token_id
                )
            
            full_decoded = model_loader.tokenizer.decode(outputs[0], skip_special_tokens=True)
            prompt_decoded = model_loader.tokenizer.decode(inputs["input_ids"][0], skip_special_tokens=True)
            
            # Isolate generated response after prompt
            if full_decoded.startswith(prompt_decoded):
                generated_response = full_decoded[len(prompt_decoded):].strip()
            else:
                generated_response = full_decoded.strip()

            elapsed_ms = (time.time() - start_time) * 1000
            return generated_response, elapsed_ms
        except Exception as e:
            print(f"[Generator] Execution error: {e}")

    # Fallback response for CPU/Offline mode
    elapsed_ms = (time.time() - start_time) * 1000
    mock_output = (
        "BioMistral Medical Response: "
        "Symptoms described suggest a common respiratory condition. "
        "Please rest, drink plenty of fluids, and consult your primary care doctor if symptoms persist."
    )
    return mock_output, elapsed_ms
