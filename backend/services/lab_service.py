from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Ensure workspace root is in python path for importing existing medical_tools package
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from medical_tools.report_pipeline import process_lab_report
    from medical_tools.lab_analyzer import analyze_report
except ImportError:
    # Fallback / graceful import handling if module path differs
    process_lab_report = None
    analyze_report = None

# Maps frontend UI report types (subtypes like CBC, Lipid, Thyroid)
# to knowledge base sample categories ('blood', 'urine', 'stool')
REPORT_TO_SAMPLE_TYPE = {
    "cbc": "blood",
    "lipid": "blood",
    "metabolic": "blood",
    "thyroid": "blood",
    "general": "blood",
    "blood": "blood",
    "urine": "urine",
    "stool": "stool"
}


def run_lab_analysis(
    file_path: str,
    test_type: str = "cbc",
    age: Optional[int] = None,
    sex: Optional[str] = None
) -> Dict[str, Any]:
    """
    Service wrapper around existing medical_tools lab analyzer pipeline.
    """
    if process_lab_report is None:
        return {
            "error": "Medical tools report pipeline module is unavailable.",
            "test_type": test_type,
            "findings": []
        }

    sample_category = REPORT_TO_SAMPLE_TYPE.get(test_type.lower(), "blood")

    try:
        result = process_lab_report(
            file_path=file_path,
            test_type=sample_category,
            age=age,
            sex=sex
        )
        return result
    except Exception as e:
        return {
            "error": f"Failed to analyze lab report: {str(e)}",
            "test_type": test_type,
            "findings": []
        }
