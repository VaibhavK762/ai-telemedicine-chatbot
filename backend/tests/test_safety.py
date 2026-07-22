import pytest
from backend.services.safety import check_safety

def test_safety_normal_query():
    result = check_safety("I have had a mild headache since yesterday after working late.")
    assert result["status"] == "NORMAL"
    assert result["is_emergency"] is False
    assert result["is_urgent"] is False
    assert result["trigger"] is None
    assert result["advice"] is None

def test_safety_urgent_kidney_stones():
    result = check_safety("I think I have symptoms of kidney stones.")
    assert result["status"] == "URGENT"
    assert result["is_emergency"] is False
    assert result["is_urgent"] is True
    assert "kidney stone" in result["trigger"]
    assert "URGENT MEDICAL EVALUATION RECOMMENDED" in result["advice"]

def test_safety_urgent_appendicitis():
    result = check_safety("I am worried about severe stomach pain and appendicitis.")
    assert result["status"] == "URGENT"
    assert result["is_emergency"] is False
    assert result["is_urgent"] is True

def test_safety_chest_pain_emergency():
    result = check_safety("Help, my father is having severe chest pain!")
    assert result["status"] == "EMERGENCY"
    assert result["is_emergency"] is True
    assert result["is_urgent"] is False
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

def test_safety_urgent_vaginal_bleeding():
    result = check_safety("I have vaginal bleeding down there")
    assert result["status"] == "URGENT"
    assert result["is_urgent"] is True
    assert result["is_emergency"] is False
    assert "URGENT MEDICAL EVALUATION RECOMMENDED" in result["advice"]

def test_safety_emergency_vaginal_bleeding_pregnant():
    result = check_safety("I am pregnant and have vaginal bleeding")
    assert result["status"] == "EMERGENCY"
    assert result["is_emergency"] is True
    assert "CRITICAL MEDICAL EMERGENCY" in result["advice"]

def test_safety_emergency_heavy_bleeding_soaking_pads():
    result = check_safety("I am soaking a pad every hour and passing clots")
    assert result["status"] == "EMERGENCY"
    assert result["is_emergency"] is True

def test_safety_urgent_lower_right_abdominal_pain():
    result = check_safety("27-year-old woman, lower right abdominal pain getting worse, nausea")
    assert result["status"] == "URGENT"
    assert result["is_urgent"] is True
    assert result["is_emergency"] is False
    assert len(result["questions"]) > 0

def test_safety_empty_query():
    result = check_safety("")
    assert result["status"] == "NORMAL"
