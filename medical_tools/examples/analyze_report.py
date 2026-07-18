import json
from pathlib import Path
import sys

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from medical_tools.report_pipeline import process_lab_report


# ======================================================
# CONFIGURATION
# ======================================================

REPORT_PATH = "test_reports/blood_report.pdf"

TEST_TYPE = "blood"      # blood | urine | stool

AGE = 46

SEX = "female"

EXTRACTOR = "auto"       # auto | regex | llm


# Set only if using the LLM extractor.
# Example:
# from my_llm import model
# LLM = model

LLM = None


# ======================================================
# MAIN
# ======================================================

def main():

    print("=" * 70)
    print("Medical Report Analysis")
    print("=" * 70)

    print(f"Report      : {REPORT_PATH}")
    print(f"Test Type   : {TEST_TYPE}")
    print(f"Age         : {AGE}")
    print(f"Sex         : {SEX}")
    print(f"Extractor   : {EXTRACTOR}")

    print("\nRunning pipeline...\n")

    result = process_lab_report(
        file_path=REPORT_PATH,
        test_type=TEST_TYPE,
        age=AGE,
        sex=SEX,
        extractor=EXTRACTOR,
        llm=LLM
    )

    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()