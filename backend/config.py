import os
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Telemedicine AI Assistant API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Environment & Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    # LLM Settings
    LLM_MODE: str = os.getenv("LLM_MODE", "stub")  # stub, local, colab, cloud
    LLM_API_URL: str = os.getenv("LLM_API_URL", "")
    
    # Conversation Settings
    MAX_HISTORY_TURNS: int = 6

    model_config = ConfigDict(case_sensitive=True)

settings = Settings()

