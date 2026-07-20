import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_chat_normal_flow():
    payload = {
        "message": "What should I eat when I have a mild cold?",
        "session_id": "test_api_session_1"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NORMAL"
    assert data["is_emergency"] is False
    assert len(data["response"]) > 0
    assert data["session_id"] == "test_api_session_1"

def test_chat_emergency_flow():
    payload = {
        "message": "I am experiencing severe chest pain and cannot breathe!",
        "session_id": "test_api_session_emergency"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "EMERGENCY"
    assert data["is_emergency"] is True
    assert "CRITICAL MEDICAL EMERGENCY" in data["response"]
