import pytest
from backend.services.llm_client import generate

def test_llm_client_generation():
    response = generate("Tell me about fever")
    assert isinstance(response, str)
    assert len(response) > 0
