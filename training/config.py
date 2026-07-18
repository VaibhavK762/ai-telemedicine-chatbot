from pathlib import Path
import os
import torch

BASE_MODEL_NAME = "BioMistral/BioMistral-7B"

# ==========================
# Environment Detection
# ==========================

if Path("/kaggle").exists():
    print("Running on Kaggle")
    DATA_ROOT = Path("/kaggle/input/dataset1")   # <-- change to your dataset name
    OUTPUT_DIR = "/kaggle/working/adapters/biomistral-telemedicine"

elif Path("/content").exists():
    print("Running on Google Colab")
    DATA_ROOT = Path("/content/drive/MyDrive/AI-Telemedicine/data/final")
    OUTPUT_DIR = "/content/drive/MyDrive/AI-Telemedicine/adapters/biomistral-telemedicine"

else:
    print("Running locally")
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DATA_ROOT = PROJECT_ROOT / "data" / "final"
    OUTPUT_DIR = str(PROJECT_ROOT / "adapters" / "biomistral-telemedicine")

TRAIN_DATA_PATH = str(DATA_ROOT / "train.jsonl")
VAL_DATA_PATH = str(DATA_ROOT / "validation.jsonl")
EVALUATION_SET_PATH = str(DATA_ROOT / "evaluation_set.jsonl")

OUTPUT_DIR = "/kaggle/working/adapters/biomistral-telemedicine"

# Dataset Paths
TRAIN_DATA_PATH = "data/final/train.jsonl"
VAL_DATA_PATH = "data/final/validation.jsonl"
EVALUATION_SET_PATH = "data/evaluation_set.jsonl"

# Tokenizer Details
MAX_SEQ_LENGTH = 512  # Reduced for RTX 3050 4GB VRAM
PADDING_SIDE = "right"

# 4-bit Quantization (QLoRA)
LOAD_IN_4BIT = True
BNB_4BIT_QUANT_TYPE = "nf4"
BNB_4BIT_USE_DOUBLE_QUANT = True
BNB_4BIT_COMPUTE_DTYPE = torch.float16

# LoRA Configuration
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj"
]

# Training Hyperparameters
BATCH_SIZE = 1  # Reduced batch size for limited VRAM
GRADIENT_ACCUMULATION_STEPS = 16  # Increase to keep effective batch size
LEARNING_RATE = 2e-4
WEIGHT_DECAY = 0.001
OPTIMIZER = "paged_adamw_8bit"
LR_SCHEDULER_TYPE = "cosine"
WARMUP_RATIO = 0.03
NUM_TRAIN_EPOCHS = 2
LOGGING_STEPS = 10
SAVE_STEPS = 100
EVAL_STEPS = 100
SAVE_TOTAL_LIMIT = 3
SEED = 42

# Training Quality & Efficiency Additions
GRADIENT_CHECKPOINTING = True
MAX_GRAD_NORM = 0.3
GROUP_BY_LENGTH = True
