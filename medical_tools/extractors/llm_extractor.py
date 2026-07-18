import json
import re
from ..logger import logger

SYSTEM_PROMPT = """
You are an expert medical laboratory information extraction system.

Your ONLY task is to extract laboratory test results from medical reports.

Rules:
1. Do NOT diagnose.
2. Do NOT explain.
3. Do NOT infer diseases.
4. Do NOT guess missing values.
5. Extract ONLY values explicitly present.
6. Return ONLY valid JSON.
7. If a field is unavailable, use null.
8. Never include markdown or code fences.

Output format:

[
    {
        "marker": "",
        "value": "",
        "unit": ""
    }
]
"""


def extract_json(response):
    """
    Extract JSON array from model output.
    """
    match = re.search(
        r"\[[\s\S]*\]",
        response
    )

    if not match:
        logger.warning("No JSON array found in LLM response.")
        return []
    try:
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        logger.error("Failed to decode JSON from LLM response: %s", str(e))
        return []


def validate_tests(tests):
    """
    Remove malformed entries returned by the LLM.
    """
    cleaned = []

    for item in tests:
        if not isinstance(item, dict):
            continue

        if "marker" not in item:
            continue

        if "value" not in item:
            continue

        cleaned.append(
            {
                "marker": item["marker"],
                "display_name": item.get("display_name") or item["marker"],
                "value": item["value"],
                "unit": item.get("unit")
            }
        )
    return cleaned


def llm_extract(text, llm) -> dict:
    """
    Extract biomarkers using an LLM.
    """
    logger.info("Starting LLM extraction.")
    prompt = f"""{SYSTEM_PROMPT}

Medical Report:

{text}
"""

    response = llm(prompt)
    extracted = extract_json(response)
    tests = validate_tests(extracted)

    confidence = 0.98 if tests else 0.0
    logger.info("LLM extraction finished. Found %d markers. Confidence: %.2f", len(tests), confidence)

    return {
        "tests": tests,
        "metadata": {
            "source": "llm",
            "confidence": confidence,
            "markers_found": len(tests)
        }
    }


if __name__ == "__main__":
    class DummyLLM:
        def __call__(self, prompt):
            return """
            [
                {
                    "marker":"hemoglobin",
                    "value":11.7,
                    "unit":"g/dL"
                },
                {
                    "marker":"platelets",
                    "value":251,
                    "unit":"10^3/uL"
                }
            ]
            """

    result = llm_extract(
        "Hb 11.7 Platelets 251",
        DummyLLM()
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )