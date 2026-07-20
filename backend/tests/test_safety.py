import pytest
from backend.services.safety import check_safety

def test_safety_normal_query():
    result = check_safety("I have had a mild headache since yesterday after working late.")
    assert result["status"] == "NORMAL"
    assert result["is_emergency"] is False
    assert result["trigger"] is None
    assert result["advice"] is None

def test_safety_chest_pain_emergency():
    result = check_safety("Help, my father is having severe chest pain!")
    assert result["status"] == "EMERGENCY"
    assert result["is_emergency"] is True
    assert result["trigger"] == "chest pain"
    assert "CRITICAL MEDICAL EMERGENCY" in result["advice"]

def test_safety_difficulty_breathing():
    result = check_safety("I am having difficulty breathing and can't catch my breath.")
    assert result["status"] == "EMERGENCY"
    assert result["is_emergency"] is True
    assert result["trigger"] == "difficulty breathing"

def test_safety_suicidal_ideation():
    result = check_safety("I feel overwhelmed and suicidal.")
    assert result["status"] == "EMERGENCY"
    assert result["is_emergency"] is True
    assert result["trigger"] == "suicidal"

def test_safety_empty_query():
    result = check_safety("")
    assert result["status"] == "NORMAL"
