import pytest
from fastapi.testclient import TestClient
from inference.app import app

client = TestClient(app)

def test_inference_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "device" in data
    assert "base_model" in data

def test_v1_generate_endpoint():
    payload = {
        "prompt": "Explain the causes of high blood pressure.",
        "max_new_tokens": 100,
        "temperature": 0.7
    }
    response = client.post("/v1/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0
    assert "model" in data
    assert "is_adapter_applied" in data

def test_generate_backward_compatible_endpoint():
    payload = {"prompt": "What are symptoms of diabetes?"}
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    assert "response" in response.json()

def test_generate_empty_prompt():
    payload = {"prompt": ""}
    response = client.post("/v1/generate", json=payload)
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]
