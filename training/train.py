import os
import argparse
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training
)

from .config import *
from .dataset import MedicalInstructionDataset
from torch.nn.utils.rnn import pad_sequence

def parse_args():
    parser = argparse.ArgumentParser(description="QLoRA SFT fine-tuning pipeline for BioMistral-7B")
    parser.add_argument("--dry-run", action="store_true", help="Perform configuration checks and load the model without running the training loop.")
    parser.add_argument("--epochs", type=int, default=NUM_TRAIN_EPOCHS, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Learning rate")
    parser.add_argument("--subset-size", type=int, default=30000, help="Train on a small subset of the dataset for validation/debug runs.")
    parser.add_argument("--resume-from-checkpoint", type=str, default=None, help="Path to checkpoint directory to resume training from.")
    return parser.parse_args()



def print_trainable_parameters(model):
    """
    Print the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"Trainable params: {trainable_params} || All params: {all_param} || "
        f"Trainable%: {100 * trainable_params / all_param:.4f}%"
    )


def train():
    args = parse_args()
    
    # Enable TF32 for execution performance on supported GPUs (Ampere+)
    torch.backends.cuda.matmul.allow_tf32 = True
    
    # Monkey-patch torch.load to disable mmap globally. This prevents memory
    # mapping issues on hosts with limited virtual memory/swap commits.
    original_torch_load = torch.load
    def patched_torch_load(*args, **kwargs):
        kwargs['mmap'] = False
        return original_torch_load(*args, **kwargs)
    torch.load = patched_torch_load
    
    print("=" * 70)
    print("Initializing QLoRA Supervised Fine-Tuning (SFT) Pipeline")
    print("=" * 70)
    print(f"Base Model    : {BASE_MODEL_NAME}")
    print(f"Output Adapter: {OUTPUT_DIR}")
    print(f"Max Seq Length: {MAX_SEQ_LENGTH}")
    
    # 1. Quantization Configuration (NF4)
    print("\n[1/5] Configuring 4-bit double quantization...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=LOAD_IN_4BIT,
        bnb_4bit_quant_type=BNB_4BIT_QUANT_TYPE,
        bnb_4bit_use_double_quant=BNB_4BIT_USE_DOUBLE_QUANT,
        bnb_4bit_compute_dtype=BNB_4BIT_COMPUTE_DTYPE
    )

    # 2. Load Model and Tokenizer
    print("\n[2/5] Loading tokenizer and base model in 4-bit...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = PADDING_SIDE

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        quantization_config=bnb_config,
        device_map={"": 0} if torch.cuda.is_available() else "auto",
        low_cpu_mem_usage=True,
        trust_remote_code=True
    )

    # Prepare model for training
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)
    model.enable_input_require_grads()

    # 3. LoRA / PEFT Configuration
    print("\n[3/5] Applying LoRA PEFT adapters...")
    peft_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=LORA_TARGET_MODULES,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, peft_config)
    print_trainable_parameters(model)

    # 4. Load Datasets
    print("\n[4/5] Loading train and validation datasets...")
    val_limit = None
    if args.subset_size is not None:
        # Scale down validation set size proportionally for subset runs
        val_limit = max(10, args.subset_size // 5)
        
    train_dataset = MedicalInstructionDataset(TRAIN_DATA_PATH, tokenizer, MAX_SEQ_LENGTH, limit=args.subset_size)
    val_dataset = MedicalInstructionDataset(VAL_DATA_PATH, tokenizer, MAX_SEQ_LENGTH, limit=val_limit)
    print(f"Loaded {len(train_dataset)} train records, {len(val_dataset)} validation records.")

    # 5. Training Arguments & Trainer Initialization
    print("\n[5/5] Configuring SFT trainer...")
    training_args = TrainingArguments(
        dataloader_num_workers=2,
        dataloader_persistent_workers=True,
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=args.lr,
        weight_decay=WEIGHT_DECAY,
        optim=OPTIMIZER,
        lr_scheduler_type=LR_SCHEDULER_TYPE,
        warmup_ratio=WARMUP_RATIO,
        num_train_epochs=args.epochs,
        logging_steps=LOGGING_STEPS,
        save_steps=SAVE_STEPS,
        eval_steps=EVAL_STEPS,
        eval_strategy="steps",
        save_strategy="steps",
        save_total_limit=SAVE_TOTAL_LIMIT,
        fp16=True,
        logging_first_step=True,
        remove_unused_columns=False,
        seed=SEED,
        report_to="none",  # Disable wandb/tensorboard reporting for simplicity
        gradient_checkpointing=GRADIENT_CHECKPOINTING,
        max_grad_norm=MAX_GRAD_NORM,
        group_by_length=GROUP_BY_LENGTH,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False
    )

    # Use DataCollatorForSeq2Seq to handle pad collations dynamically
    def data_collator(features):

        input_ids = pad_sequence(
            [f["input_ids"] for f in features],
            batch_first=True,
            padding_value=tokenizer.pad_token_id
        )

        attention_mask = pad_sequence(
            [f["attention_mask"] for f in features],
            batch_first=True,
            padding_value=0
        )

        labels = pad_sequence(
            [f["labels"] for f in features],
            batch_first=True,
            padding_value=-100
        )

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator
    )

    # Disable cache to avoid warnings and ensure gradient checkpointing stability
    model.config.use_cache = False

    if args.dry_run:
        print("\nDry-run check completed successfully! Model layout, LoRA adaptation, and dataloading are validated.")
        print("Model configuration:")
        print(model.config)
        return

    print("\nStarting SFT training loop...")
    trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)


    print(f"\nTraining finished! Saving final adapter model weights to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Done.")


if __name__ == "__main__":
    train()
