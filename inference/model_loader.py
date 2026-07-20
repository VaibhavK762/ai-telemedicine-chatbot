import os
import torch
import traceback
from pathlib import Path
from typing import Tuple, Optional

from inference.config import settings

class ModelLoader:
    """
    Singleton loader for BioMistral base model, tokenizer, and PEFT LoRA adapters.
    """
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.is_adapter_loaded = False
        self.is_model_loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load(self, force_reload: bool = False):
        """Loads tokenizer, 4-bit base model, and LoRA adapter weights."""
        if self.is_model_loaded and not force_reload:
            return

        print(f"[ModelLoader] Initializing model loading sequence on device: {self.device}")
        
        # Disable mmap globally to avoid swap commit issues
        original_torch_load = torch.load
        try:
            def patched_torch_load(*args, **kwargs):
                kwargs['mmap'] = False
                return original_torch_load(*args, **kwargs)
            torch.load = patched_torch_load
        finally:
            torch.load = original_torch_load

        # Skip heavy GPU load if no CUDA device available to prevent OOM
        if not torch.cuda.is_available():   
            print("[ModelLoader] Warning: CUDA is unavailable. Running in lightweight CPU fallback mode.")
            self.is_model_loaded = False
            self.is_adapter_loaded = False
            return

        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
            from peft import PeftModel

            # 1. Load Tokenizer
            print(f"[ModelLoader] Loading tokenizer for {settings.BASE_MODEL_NAME}...")
            self.tokenizer = AutoTokenizer.from_pretrained(settings.BASE_MODEL_NAME)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "right"

            # 2. Configure 4-bit Quantization
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=settings.LOAD_IN_4BIT,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16
            )

            # 3. Load Base Model
            print(f"[ModelLoader] Loading base model in 4-bit: {settings.BASE_MODEL_NAME}...")
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.BASE_MODEL_NAME,
                quantization_config=bnb_config,
                device_map=settings.DEVICE_MAP,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )

            # 4. Load LoRA Adapters
            adapter_config = os.path.join(  
                settings.ADAPTER_PATH,
                "adapter_config.json"
            )

            if os.path.isfile(adapter_config):
                print(f"[ModelLoader] Applying LoRA adapter from {settings.ADAPTER_PATH}...")
                self.model = PeftModel.from_pretrained(self.model, settings.ADAPTER_PATH)
                self.is_adapter_loaded = True
            else:
                print(f"[ModelLoader] Warning: Adapter path '{settings.ADAPTER_PATH}' not found. Using base model.")

            self.is_model_loaded = True
            print("[ModelLoader] Model and adapters successfully initialized!")

        except Exception:
            print("=" * 80)
            print("MODEL INITIALIZATION FAILED")
            traceback.print_exc()
            print("=" * 80)
            raise

model_loader = ModelLoader()
