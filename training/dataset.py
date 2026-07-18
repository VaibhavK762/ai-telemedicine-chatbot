import json
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer

from .prompts import format_prompt
from .config import MAX_SEQ_LENGTH, BASE_MODEL_NAME


class MedicalInstructionDataset(Dataset):
    """
    Pre-tokenized instruction tuning dataset.

    - Loads JSONL once
    - Tokenizes once
    - Creates tensors once
    - Masks prompt tokens with -100
    """

    def __init__(
        self,
        file_path: str,
        tokenizer: AutoTokenizer,
        max_length: int = MAX_SEQ_LENGTH,
        limit: int | None = None,
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.features = []

        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        records = []

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        if limit is not None:
            records = records[:limit]

        print(f"Pre-tokenizing {len(records)} samples from {file_path}...")

        for record in records:

            instruction = record.get("instruction", "")
            input_text = record.get("input", "")
            output_text = record.get("output", "")

            full_text = format_prompt(
                tokenizer=self.tokenizer,
                instruction=instruction,
                input_text=input_text,
                output_text=output_text
            )

            prompt_text = format_prompt(
                tokenizer=self.tokenizer,
                instruction=instruction,
                input_text=input_text,
                output_text=None
            )

            tokenized_full = self.tokenizer(
                full_text,
                truncation=True,
                max_length=self.max_length,
                add_special_tokens=False
            )

            tokenized_prompt = self.tokenizer(
                prompt_text,
                truncation=True,
                max_length=self.max_length,
                add_special_tokens=False
            )

            input_ids = tokenized_full["input_ids"]
            attention_mask = tokenized_full["attention_mask"]

            labels = input_ids.copy()

            prompt_length = min(
                len(tokenized_prompt["input_ids"]),
                len(labels)
            )

            labels[:prompt_length] = [-100] * prompt_length

            self.features.append(
                {
                    "input_ids": torch.tensor(
                        input_ids,
                        dtype=torch.long
                    ),
                    "attention_mask": torch.tensor(
                        attention_mask,
                        dtype=torch.long
                    ),
                    "labels": torch.tensor(
                        labels,
                        dtype=torch.long
                    )
                }
            )

        print("Dataset preprocessing complete.")

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx]


if __name__ == "__main__":

    print("Testing MedicalInstructionDataset...")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)

    dataset = MedicalInstructionDataset(
        "data/final/validation.jsonl",
        tokenizer
    )

    print(f"Dataset size : {len(dataset)}")

    sample = dataset[0]

    print("\nSample Shapes")

    for key, value in sample.items():
        print(
            f"{key:15} {tuple(value.shape)} {value.dtype}"
        )

    labels = sample["labels"].tolist()
    input_ids = sample["input_ids"].tolist()

    prompt_tokens = labels.count(-100)

    print(f"\nMasked Prompt Tokens : {prompt_tokens}")

    print("\nDecoded Response:\n")

    response = [
        token
        for token, label
        in zip(input_ids, labels)
        if label != -100
    ]

    print(tokenizer.decode(response))