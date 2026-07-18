import os
import json
import argparse
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)
from peft import PeftModel

from .config import BASE_MODEL_NAME, OUTPUT_DIR, VAL_DATA_PATH, EVALUATION_SET_PATH
from .prompts import format_prompt

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate fine-tuned BioMistral model")
    parser.add_argument("--adapter-path", type=str, default=OUTPUT_DIR, help="Path to saved LoRA adapter model.")
    parser.add_argument("--base-only", action="store_true", help="Evaluate base model only.")
    parser.add_argument("--limit", type=int, default=30, help="Number of samples to evaluate quantitatively from the validation split.")
    parser.add_argument("--output-qual", type=str, default="data/eval_qualitative_predictions.jsonl", help="Output path for qualitative predictions.")
    parser.add_argument("--output-quant", type=str, default="data/eval_quantitative_results.json", help="Output path for quantitative metrics.")
    return parser.parse_args()


def compute_lcs(x, y):
    """
    Computes the Longest Common Subsequence (LCS) length of two token lists.
    """
    m, n = len(x), len(y)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if x[i-1] == y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]


def score_rouge_l(ref: str, gen: str):
    """
    Computes precision, recall, and F1 ROUGE-L metrics.
    """
    ref_tokens = ref.lower().split()
    gen_tokens = gen.lower().split()
    if not ref_tokens or not gen_tokens:
        return 0.0, 0.0, 0.0
    lcs_len = compute_lcs(ref_tokens, gen_tokens)
    recall = lcs_len / len(ref_tokens)
    precision = lcs_len / len(gen_tokens)
    if recall + precision == 0:
        return 0.0, 0.0, 0.0
    f1 = (2 * recall * precision) / (recall + precision)
    return precision, recall, f1


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
    print("Initializing BioMistral Evaluation Suite")
    print("=" * 70)
    
    # 1. Quantization Configuration (NF4)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16
    )

    # 2. Load Tokenizer & Model
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    
    print("Loading base model in 4-bit...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        quantization_config=bnb_config,
        device_map={"": 0} if torch.cuda.is_available() else "auto",
        low_cpu_mem_usage=True,
        trust_remote_code=True
    )

    # Apply LoRA adapter if applicable
    is_adapted = False
    if not args.base_only and os.path.exists(args.adapter_path):
        print(f"Applying LoRA adapter from {args.adapter_path}...")
        model = PeftModel.from_pretrained(model, args.adapter_path)
        is_adapted = True
    else:
        print("Running base model evaluation only.")

    print("\n" + "=" * 70)
    print("Running Qualitative Evaluation (evaluation_set.jsonl)")
    print("=" * 70)
    
    # Ensure parent output directory exists
    os.makedirs(os.path.dirname(args.output_qual), exist_ok=True)
    
    qual_samples = []
    if os.path.exists(EVALUATION_SET_PATH):
        with open(EVALUATION_SET_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    qual_samples.append(json.loads(line))
    else:
        print(f"Error: Evaluation set not found at {EVALUATION_SET_PATH}")
        return

    print(f"Loaded {len(qual_samples)} qualitative clinical scenarios.")
    qual_predictions = []
    
    for idx, sample in enumerate(qual_samples):
        category = sample.get("category", "unknown")
        instruction = sample.get("instruction", "")
        input_text = sample.get("input", "")
        
        # Format SFT prompt
        prompt = format_prompt(tokenizer, instruction, input_text, None)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
            
        # Decode and isolate response
        full_decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Isolate target generated response after the prompt text
        prompt_decoded = tokenizer.decode(inputs["input_ids"][0], skip_special_tokens=True)
        response_text = full_decoded[len(prompt_decoded):].strip()
        
        print(f"[{idx+1}/{len(qual_samples)}] [{category.upper()}] Query: {input_text[:50]}...")
        print(f"Response: {response_text[:80]}...\n")
        
        qual_predictions.append({
            "category": category,
            "instruction": instruction,
            "input": input_text,
            "generated_output": response_text
        })

    with open(args.output_qual, "w", encoding="utf-8") as f:
        for pred in qual_predictions:
            f.write(json.dumps(pred) + "\n")
    print(f"Saved qualitative generation outputs to {args.output_qual}")

    print("\n" + "=" * 70)
    print("Running Quantitative Evaluation (validation split)")
    print("=" * 70)
    
    val_samples = []
    if os.path.exists(VAL_DATA_PATH):
        with open(VAL_DATA_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    val_samples.append(json.loads(line))
    else:
        print(f"Error: Validation split not found at {VAL_DATA_PATH}")
        return

    # Select sub-batch of validation data
    eval_batch = val_samples[:args.limit]
    print(f"Running quantitative metrics on first {len(eval_batch)} validation samples...")
    
    total_rouge_p = 0.0
    total_rouge_r = 0.0
    total_rouge_f1 = 0.0
    total_length = 0
    total_words = 0
    
    for idx, sample in enumerate(eval_batch):
        instruction = sample.get("instruction", "")
        input_text = sample.get("input", "")
        reference_output = sample.get("output", "")
        
        prompt = format_prompt(tokenizer, instruction, input_text, None)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
            
        full_decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        prompt_decoded = tokenizer.decode(inputs["input_ids"][0], skip_special_tokens=True)
        generated_output = full_decoded[len(prompt_decoded):].strip()
        
        # Calculate ROUGE-L metrics
        p, r, f1 = score_rouge_l(reference_output, generated_output)
        total_rouge_p += p
        total_rouge_r += r
        total_rouge_f1 += f1
        
        total_length += len(generated_output)
        total_words += len(generated_output.split())
        print(f"  Sample {idx+1}/{len(eval_batch)} | ROUGE-L F1: {f1:.4f} | Words: {len(generated_output.split())}")

    avg_p = total_rouge_p / len(eval_batch)
    avg_r = total_rouge_r / len(eval_batch)
    avg_f1 = total_rouge_f1 / len(eval_batch)
    avg_len_chars = total_length / len(eval_batch)
    avg_len_words = total_words / len(eval_batch)
    
    metrics = {
        "is_adapted": is_adapted,
        "adapter_path": args.adapter_path if is_adapted else None,
        "base_model": BASE_MODEL_NAME,
        "evaluated_samples": len(eval_batch),
        "rouge_l_precision": avg_p,
        "rouge_l_recall": avg_r,
        "rouge_l_f1": avg_f1,
        "average_generation_length_chars": avg_len_chars,
        "average_generation_length_words": avg_len_words
    }
    
    with open(args.output_quant, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)
        
    print("\n" + "=" * 70)
    print("Evaluation Report Summary")
    print("=" * 70)
    print(f"Model Mode                   : {'Adapter (Fine-Tuned)' if is_adapted else 'Base Model (Unadapted)'}")
    print(f"Evaluated Samples            : {len(eval_batch)}")
    print(f"Average Generation Length    : {avg_len_words:.1f} words ({avg_len_chars:.1f} characters)")
    print(f"Average ROUGE-L Precision    : {avg_p:.4f}")
    print(f"Average ROUGE-L Recall       : {avg_r:.4f}")
    print(f"Average ROUGE-L F1 Score     : {avg_f1:.4f}")
    print("=" * 70)
    print(f"Quantitative metrics results saved to {args.output_quant}\n")


if __name__ == "__main__":
    main()
