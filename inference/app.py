from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from inference.config import settings
from inference.schemas import GenerateRequest, GenerateResponse, HealthResponse
from inference.model_loader import model_loader
from inference.generator import generate_text

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load model and adapters
    print(f"[InferenceApp] Starting up {settings.PROJECT_NAME}...")
    model_loader.load()
    yield
    print("[InferenceApp] Shutting down inference service.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Standalone LLM Inference Service for BioMistral + LoRA Adapter",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health & Status Endpoint."""
    return HealthResponse(
        status="healthy",
        device=model_loader.device,
        base_model=settings.BASE_MODEL_NAME,
        adapter_path=settings.ADAPTER_PATH,
        adapter_loaded=model_loader.is_adapter_loaded
    )

@app.post("/v1/generate", response_model=GenerateResponse)
@app.post("/generate", response_model=GenerateResponse)
def generate_endpoint(request: GenerateRequest):
    """
    Main Text Generation Endpoint (Versioned as /v1/generate).
    Accepts input prompt and generation settings, returns model output.
    """
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt text cannot be empty.")

    output_text, duration_ms = generate_text(
        prompt=request.prompt,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        top_p=request.top_p
    )

    return GenerateResponse(
        response=output_text,
        model=settings.BASE_MODEL_NAME,
        is_adapter_applied=model_loader.is_adapter_loaded,
        generation_time_ms=round(duration_ms, 2)
    )
