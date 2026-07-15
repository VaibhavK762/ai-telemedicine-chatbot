import json

from report_parser import parse_report_text
from lab_analyzer import analyze_report
from ocr_extractor import extract_report_text



def process_lab_report(
        text,
        test_type,
        age=None,
        sex=None
):
    """
    Complete report flow:

    OCR/Text
        ↓
    Extract markers
        ↓
    Analyze values
        ↓
    Return report
    """


    extracted_tests = parse_report_text(
        text,
        test_type
    )


    analysis = analyze_report(
        test_type=test_type,
        tests=extracted_tests,
        age=age,
        sex=sex
    )


    return {

        "extracted_tests": extracted_tests,

        "analysis": analysis
    }





if __name__ == "__main__":


    text = extract_report_text(
        "test_reports/blood_report.pdf"
    )


    result = process_lab_report(
        text=text,
        test_type="blood",
        age=46,
        sex="female"
    )


    print(
        json.dumps(
            result,
            indent=4
        )
    )