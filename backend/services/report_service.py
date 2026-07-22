import os
from typing import Dict, Any, Optional
from pathlib import Path

from backend.services.lab_service import run_lab_analysis
from backend.services.prompt_builder import build_prompt
from backend.services.llm_client import generate
from backend.services.response_cleaner import clean_response

def process_report_file(
    file_path: str,
    test_type: str = "cbc",
    age: Optional[int] = None,
    sex: Optional[str] = None
) -> Dict[str, Any]:
    """
    Complete Report Service Pipeline:
    OCR -> Extract values -> Lab analyzer -> LLM explanation -> Response Cleaner
    """
    # 1. Run OCR and Rule-Based Lab Analysis
    analysis = run_lab_analysis(file_path=file_path, test_type=test_type, age=age, sex=sex)

    # 2. Build summary string of findings
    summary_lines = [f"Lab Report Type: {test_type.upper()}"]
    if age:
        summary_lines.append(f"Patient Age: {age}")
    if sex:
        summary_lines.append(f"Patient Sex: {sex}")

    # Extract results from nested analysis dictionary
    results_list = []
    if isinstance(analysis, dict):
        if "analysis" in analysis and isinstance(analysis["analysis"], dict):
            results_list = analysis["analysis"].get("results", [])
        elif "results" in analysis:
            results_list = analysis.get("results", [])
        elif "extracted_tests" in analysis:
            results_list = analysis.get("extracted_tests", [])

    if results_list:
        summary_lines.append("Extracted Test Findings:")
        for item in results_list:
            marker = item.get("marker", item.get("display_name", "Unknown"))
            val = item.get("value", "")
            unit = item.get("unit", "")
            status = item.get("status", "NORMAL")

            range_info = ""
            norm_range = item.get("normal_range")
            if isinstance(norm_range, dict) and "min" in norm_range and "max" in norm_range:
                range_info = f" (Reference Range: {norm_range['min']} - {norm_range['max']})"

            summary_lines.append(f"- {marker}: {val} {unit} [{status}]{range_info}")
    elif "raw_text" in analysis:
        summary_lines.append(f"Extracted Raw Text Snippet:\n{analysis['raw_text'][:500]}")
    else:
        summary_lines.append("Extracted Report Text: Document processed for review.")

    context_str = "\n".join(summary_lines)

    # 3. Build LLM prompt explaining the lab report
    prompt = build_prompt(
        current_question="Please explain the clinical significance of these lab results and suggest next steps.",
        context_data=context_str
    )

    print("=" * 60)
    print("[report_service] PROMPT SENT TO LLM:")
    print(prompt)
    print("=" * 60)

    # 4. Generate LLM response & clean output
    raw_explanation = generate(prompt)
    cleaned_explanation = clean_response(raw_explanation)

    return {
        "file_name": Path(file_path).name,
        "test_type": test_type,
        "analysis_data": analysis,
        "clinical_explanation": cleaned_explanation
    }
