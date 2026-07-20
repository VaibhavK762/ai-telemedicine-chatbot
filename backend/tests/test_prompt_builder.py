import pytest
from backend.services.prompt_builder import build_prompt

def test_build_prompt_simple():
    prompt = build_prompt("What are common flu symptoms?")
    assert "[INST] What are common flu symptoms? [/INST]" in prompt
    assert "[SYSTEM INSTRUCTION]" in prompt

def test_build_prompt_with_history():
    history = [
        {"role": "user", "content": "I have a sore throat."},
        {"role": "assistant", "content": "A sore throat can be caused by viral infections like cold or flu."}
    ]
    prompt = build_prompt("How long does it usually last?", history=history)
    assert "[INST] I have a sore throat. [/INST]" in prompt
    assert "A sore throat can be caused by viral infections" in prompt
    assert "[INST] How long does it usually last? [/INST]" in prompt

def test_build_prompt_with_context():
    context = "Lab Report Analysis: Hemoglobin 11.2 g/dL (LOW)"
    prompt = build_prompt("Should I take iron supplements?", context_data=context)
    assert "[ADDITIONAL CLINICAL CONTEXT]" in prompt
    assert "Hemoglobin 11.2 g/dL (LOW)" in prompt
