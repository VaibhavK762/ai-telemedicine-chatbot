import os
import argparse
import torch
from threading import Thread
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TextIteratorStreamer
)
from peft import PeftModel

from .config import BASE_MODEL_NAME, OUTPUT_DIR
from .prompts import format_prompt

def parse_args():
    parser = argparse.ArgumentParser(description="Inference interface for fine-tuned BioMistral model")
    parser.add_argument("--adapter-path", type=str, default=OUTPUT_DIR, help="Path to saved LoRA adapter model.")
    parser.add_argument("--base-only", action="store_true", help="Run base model only without applying adapter.")
    return parser.parse_args()


def format_history(tokenizer, messages) -> str:
    """
    Format the complete multi-turn message history using tokenizer's chat
    template, falling back to Mistral instruct style.
    """
    try:
        if getattr(tokenizer, "default_chat_template", None) is not None or getattr(tokenizer, "chat_template", None) is not None:
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    except Exception:
        pass

    # Fallback to Mistral multi-turn instruct formatting
    bos = tokenizer.bos_token or "<s>"
    eos = tokenizer.eos_token or "</s>"
    
    prompt = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            prompt += f"{bos}[INST] {content.strip()} [/INST]"
        else:
            prompt += f" {content.strip()}{eos}"
    return prompt


def main():
    args = parse_args()
    
    # Monkey-patch torch.load to disable mmap globally. This prevents memory
    # mapping issues on hosts with limited virtual memory/swap commits.
    original_torch_load = torch.load
    def patched_torch_load(*args, **kwargs):
        kwargs['mmap'] = False
        return original_torch_load(*args, **kwargs)
    torch.load = patched_torch_load
    
    print("=" * 70)
    print("Initializing BioMistral Inference Engine")
    print("=" * 70)
    print(f"Base Model  : {BASE_MODEL_NAME}")
    
    # 1. Quantization Configuration (NF4)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16
    )

    # 2. Load Tokenizer
    print("\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    
    # 3. Load Model
    print("Loading base model in 4-bit...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        quantization_config=bnb_config,
        device_map={"": 0} if torch.cuda.is_available() else "auto",
        low_cpu_mem_usage=True,
        trust_remote_code=True
    )

    # 4. Apply LoRA adapter if requested and exists
    if not args.base_only and os.path.exists(args.adapter_path):
        print(f"Applying LoRA adapter from {args.adapter_path}...")
        model = PeftModel.from_pretrained(model, args.adapter_path)
    elif not args.base_only:
        print(f"Warning: Adapter path '{args.adapter_path}' not found. Defaulting to base model only.")

    print("\nInitialization complete! Enter your medical query below.")
    print("Type 'reset' to clear history, or 'exit'/'quit' to end the session.")
    print("-" * 70)

    # Default instruction prompt
    default_instruction = "You are a safe medical assistant. Provide educational medical information, explain clearly, and recommend professional medical care when appropriate."
    messages = []

    while True:
        try:
            user_input = input("\nUser: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting inference session. Stay healthy!")
                break
            if user_input.lower() == "reset":
                messages = []
                print("Conversation history cleared.")
                continue
            
            # Format message turn content
            if not messages:
                # Prepend the default system instruction for the first user query
                user_content = f"{default_instruction}\n\n{user_input}"
            else:
                user_content = user_input
                
            messages.append({"role": "user", "content": user_content})
            
            # Format prompt string using conversation history
            prompt = format_history(tokenizer, messages)
            
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            
            # Stream token response
            streamer = TextIteratorStreamer(
                tokenizer,
                skip_prompt=True,
                skip_special_tokens=True
            )
            
            generation_kwargs = dict(
                inputs,
                streamer=streamer,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                do_sample=True
            )
            
            # Run generation in a background thread to allow streaming to stdout
            thread = Thread(target=model.generate, kwargs=generation_kwargs)
            thread.start()
            
            print("Assistant: ", end="", flush=True)
            assistant_response = ""
            for new_text in streamer:
                print(new_text, end="", flush=True)
                assistant_response += new_text
            print()
            
            # Append generated response to chat history
            messages.append({"role": "assistant", "content": assistant_response.strip()})
            
        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred during generation: {e}")


if __name__ == "__main__":
    main()
