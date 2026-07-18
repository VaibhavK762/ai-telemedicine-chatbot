import json
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer
from .prompts import format_prompt
from .config import MAX_SEQ_LENGTH, BASE_MODEL_NAME

class MedicalInstructionDataset(Dataset):
    def __init__(self, file_path: str, tokenizer: AutoTokenizer, max_length: int = MAX_SEQ_LENGTH, limit: int = None):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.features = []
        
        # Load raw records
        records = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        
        # Apply subset limit if specified
        if limit is not None:
            records = records[:limit]
            
        # Ensure tokenizer has pad token
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        print(f"Pre-tokenizing {len(records)} samples from {file_path}...")
        for record in records:
            instruction = record.get("instruction", "")
            input_text = record.get("input", "")
            output_text = record.get("output", "")
            
            # Format the full sequence (prompt + response) and just the prompt prefix
            # Note: prompts.py format_prompt will add bos and eos tokens appropriately
            full_text = format_prompt(tokenizer, instruction, input_text, output_text)
            prompt_text = format_prompt(tokenizer, instruction, input_text, None)
            
            tokenized_full = self.tokenizer(
                full_text,
                max_length=self.max_length,
                truncation=True,
                add_special_tokens=False  # BOS/EOS are added by format_prompt fallback/template
            )
            
            tokenized_prompt = self.tokenizer(
                prompt_text,
                max_length=self.max_length,
                truncation=True,
                add_special_tokens=False
            )
            
            input_ids = tokenized_full["input_ids"]
            attention_mask = tokenized_full["attention_mask"]
            
            # Create labels targeting cross-entropy calculation ignoring the prompt
            labels = list(input_ids)
            prompt_len = len(tokenized_prompt["input_ids"])
            
            for i in range(min(prompt_len, len(labels))):
                labels[i] = -100
                
            self.features.append({
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "labels": labels
            })
            
    def __len__(self):
        return len(self.features)
        
    def __getitem__(self, idx):
        feature = self.features[idx]
        return {
            "input_ids": torch.tensor(feature["input_ids"], dtype=torch.long),
            "attention_mask": torch.tensor(feature["attention_mask"], dtype=torch.long),
            "labels": torch.tensor(feature["labels"], dtype=torch.long)
        }


if __name__ == "__main__":
    print("Testing MedicalInstructionDataset loader...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
        # Use validation set as verification sample
        dataset = MedicalInstructionDataset("data/final/validation.jsonl", tokenizer)
        print(f"Successfully loaded dataset with {len(dataset)} records.")
        sample = dataset[0]
        print("\nDataset sample fields:")
        for k, v in sample.items():
            print(f"  {k}: shape {v.shape}, dtype {v.dtype}")
        
        # Print decoded tokens
        input_ids = sample["input_ids"].tolist()
        labels = sample["labels"].tolist()
        
        print("\nSample Decoded Prompt (Masked Labels -100):")
        decoded_prompt = tokenizer.decode([x for x in input_ids[:labels.count(-100)] if x != -100])
        print(f"Prompt Length: {labels.count(-100)} tokens.")
        
        print("\nSample Decoded Response (Active Labels):")
        decoded_response = tokenizer.decode([x for x in labels if x != -100])
        print(decoded_response)
        
    except Exception as e:
        print(f"Dataset test failed: {e}")
