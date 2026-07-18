from pathlib import Path
import torch

BASE_MODEL_NAME = "BioMistral/BioMistral-7B"

# ============================================================
# Environment Detection
# ============================================================

if Path("/kaggle").exists():
    print("Running on Kaggle")
    DATA_ROOT = Path("/kaggle/input/datasets/vaibhavkumar1202/dataset1")
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

# ============================================================
# Tokenizer
# ============================================================

MAX_SEQ_LENGTH = 384          # CHANGED (512 → 384)
PADDING_SIDE = "right"

# ============================================================
# QLoRA Quantization
# ============================================================

LOAD_IN_4BIT = True
BNB_4BIT_QUANT_TYPE = "nf4"
BNB_4BIT_USE_DOUBLE_QUANT = True
BNB_4BIT_COMPUTE_DTYPE = torch.float16

# ============================================================
# LoRA
# ============================================================

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

# ============================================================
# Training
# ============================================================

BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4

LEARNING_RATE = 2e-4
WEIGHT_DECAY = 0.001

OPTIMIZER = "paged_adamw_8bit"

LR_SCHEDULER_TYPE = "cosine"
WARMUP_RATIO = 0.03

NUM_TRAIN_EPOCHS = 1          # CHANGED (3 → 1)

LOGGING_STEPS = 25            # CHANGED (10 → 25)

SAVE_STEPS = 250
EVAL_STEPS = 250
SAVE_TOTAL_LIMIT = 3

SEED = 42

# ============================================================
# Memory Optimizations
# ============================================================

GRADIENT_CHECKPOINTING = False
MAX_GRAD_NORM = 0.3
GROUP_BY_LENGTH = True