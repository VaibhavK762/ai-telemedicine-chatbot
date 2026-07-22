import os
import requests

from backend.config import settings

INFERENCE_SERVER_URL = os.getenv(
    "INFERENCE_SERVER_URL",
    "https://rake-mulch-luster.ngrok-free.dev/v1/generate"
)

HEADERS = {
    "ngrok-skip-browser-warning": "true"
}


def _build_lab_fallback_explanation(prompt: str) -> str:
    lines = prompt.splitlines()
    findings_lines = [line.strip() for line in lines if line.strip().startswith("- ")]

    if not findings_lines:
        return (
            "Lab report findings were processed. Please discuss the specific test values "
            "and reference ranges with your physician for clinical evaluation."
        )

    explanation = ["**Clinical Summary of Extracted Lab Results**:\n"]
    abnormal = []
    normal = []

    for f in findings_lines:
        if "[LOW]" in f or "[HIGH]" in f or "[ABNORMAL]" in f:
            abnormal.append(f)
        else:
            normal.append(f)

    if abnormal:
        explanation.append("### Key Out-of-Range Findings:")
        for item in abnormal:
            explanation.append(f"{item}")
        explanation.append(
            "\n*Clinical Note*: Out-of-range values (such as low hemoglobin or hematocrit) "
            "may indicate conditions like anemia, iron deficiency, or blood loss. "
            "A physician evaluation and follow-up lab review are recommended."
        )

    if normal:
        explanation.append("\n### Normal Range Findings:")
        for item in normal:
            explanation.append(f"{item}")

    explanation.append("\n*Disclaimer: This summary is provided for educational reference. Please consult your physician for clinical diagnosis.*")
    return "\n".join(explanation)


NON_MEDICAL_PATTERNS = [
    r"(?i)\bpython\b", r"(?i)\bjavascript\b", r"(?i)\bwrite\s+code\b", r"(?i)\bprogramming\b",
    r"(?i)\bmath\b", r"(?i)\bcalculus\b", r"(?i)\bequation\b", r"(?i)\bcapital\s+of\b"
]

def _is_non_medical_query(prompt: str) -> bool:
    import re
    text = prompt.lower()
    for pattern in NON_MEDICAL_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def generate(prompt: str) -> str:
    """
    Unified LLM Client interface.
    Sends HTTP POST requests to the inference service.
    """

    target_url = settings.LLM_API_URL or INFERENCE_SERVER_URL

    try:
        response = requests.post(
            target_url,
            json={"prompt": prompt},
            headers=HEADERS,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "")

    except Exception as e:
        print(f"[llm_client] Error connecting to inference server ({target_url}): {e}")

    # 1. Context-aware fallback if lab findings are present in prompt
    if "Extracted Test Findings:" in prompt:
        return _build_lab_fallback_explanation(prompt)

    # 2. Non-medical query policy response
    if _is_non_medical_query(prompt):
        return (
            "I am an AI assistant specialized exclusively in medical and health-related topics. "
            "I can assist you with understanding health symptoms, lab reports, and clinical concepts. "
            "For assistance with general programming, mathematics, or off-topic queries, please consult a general AI assistant."
        )

    # 3. General health conversation fallback response
    return (
        "Thank you for reaching out. Based on your symptom description, I recommend monitoring your symptoms closely, "
        "maintaining adequate rest and hydration, and scheduling an evaluation with a qualified healthcare professional "
        "if your symptoms persist or worsen."
    )