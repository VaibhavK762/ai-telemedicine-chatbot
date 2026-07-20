import os
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class InferenceSettings(BaseSettings):
    PROJECT_NAME: str = "BioMistral Telemedicine LLM Inference Service"
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("INFERENCE_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("INFERENCE_PORT", "8001"))

    # Model & Adapter configuration
    BASE_MODEL_NAME: str = os.getenv("BASE_MODEL_NAME", "BioMistral/BioMistral-7B")
    
    # Path settings
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
    ADAPTER_PATH: str = os.getenv(
        "ADAPTER_PATH",
        str(PROJECT_ROOT / "adapters" / "biomistral-telemedicine-adapter")
    )

    # Generation defaults
    DEFAULT_MAX_NEW_TOKENS: int = 256
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 0.9
    DEFAULT_REPETITION_PENALTY: float = 1.1

    # Load options
    LOAD_IN_4BIT: bool = True
    DEVICE_MAP: str = "auto"

    model_config = ConfigDict(case_sensitive=True)

settings = InferenceSettings()
