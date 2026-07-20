from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Full input prompt text formatted for generation")
    max_new_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=None, description="Sampling temperature")
    top_p: Optional[float] = Field(default=None, description="Nucleus sampling top_p")

class GenerateResponse(BaseModel):
    response: str = Field(..., description="Generated completion text")
    model: str = Field(..., description="Base model name")
    is_adapter_applied: bool = Field(..., description="Whether LoRA adapter was applied")
    generation_time_ms: Optional[float] = Field(default=None, description="Generation execution time in milliseconds")

class HealthResponse(BaseModel):
    status: str
    device: str
    base_model: str
    adapter_path: str
    adapter_loaded: bool
