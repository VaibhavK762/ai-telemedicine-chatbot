import json
from pathlib import Path

from .ocr_extractor import extract_report_text
from .extractors.regex_extractor import regex_extract
from .extractors.llm_extractor import llm_extract
from .unit_normalizer import normalize_extracted_tests
from .lab_analyzer import analyze_report
from .validator import validate_extracted_tests
from .config import CONFIDENCE_THRESHOLD
from .logger import logger
from .exceptions import OCRFailure, ExtractionError, AnalyzerError

def process_lab_report(
    file_path,
    test_type,
    age=None,
    sex=None,
    llm=None,
    extractor="auto"
):
    """
    Complete laboratory report pipeline.

    Flow:

    OCR
      ↓
    Extraction
      ↓
    Validation
      ↓
    Unit Normalization
      ↓
    Rule-based Analysis
      ↓
    Structured Result
    """
    logger.info("Processing lab report for file: %s, test_type: %s", file_path, test_type)

    try:
        # -------------------------
        # OCR
        # -------------------------
        text = extract_report_text(file_path)
        if not text:
            raise OCRFailure("Unable to extract text from report.")

        logger.info("OCR completed successfully. Length of extracted text: %d characters.", len(text))

        # -------------------------
        # Extraction
        # -------------------------
        extraction = None
        if extractor == "regex":
            extraction = regex_extract(
                text=text,
                test_type=test_type
            )
        elif extractor == "llm":
            if llm is None:
                raise ExtractionError("LLM extractor requested but no model supplied.")
            extraction = llm_extract(
                text=text,
                llm=llm
            )
        else:
            # AUTO MODE
            logger.info("Running in auto extractor mode. Starting with regex extractor.")
            extraction = regex_extract(
                text=text,
                test_type=test_type
            )
            confidence = extraction["metadata"].get("confidence", 0.0)

            if confidence < CONFIDENCE_THRESHOLD:
                if llm is not None:
                    logger.warning("Regex extraction confidence (%.2f) below threshold (%.2f). Falling back to LLM extractor.", confidence, CONFIDENCE_THRESHOLD)
                    extraction = llm_extract(
                        text=text,
                        llm=llm
                    )
                else:
                    logger.warning("Regex extraction confidence (%.2f) below threshold (%.2f), but no LLM model supplied. Continuing with regex results.", confidence, CONFIDENCE_THRESHOLD)

        if not extraction or not extraction.get("tests"):
            logger.warning("No tests were extracted from the report.")

        # -------------------------
        # Validation
        # -------------------------
        tests_dict_list = extraction.get("tests", [])
        validated_dict_list = validate_extracted_tests(test_type, tests_dict_list)

        extraction_for_norm = {
            "tests": validated_dict_list,
            "metadata": extraction.get("metadata", {})
        }

        # -------------------------
        # Normalize Units
        # -------------------------
        normalized_extraction = normalize_extracted_tests(
            extraction_for_norm
        )

        # -------------------------
        # Analyze
        # -------------------------
        normalized_extraction["metadata"]["report_type"] = test_type

        logger.info("Running clinical analysis.")
        analysis = analyze_report(
            test_type=test_type,
            tests=normalized_extraction,
            age=age,
            sex=sex
        )

        # -------------------------
        # Final Response
        # -------------------------
        logger.info("Pipeline processing completed successfully.")
        return {
            "metadata": analysis["metadata"],
            "extracted_tests": normalized_extraction["tests"],
            "analysis": analysis
        }

    except (OCRFailure, ExtractionError, AnalyzerError) as e:
        logger.exception("Pipeline execution failed: %s", str(e))
        return {"error": str(e)}


if __name__ == "__main__":
    result = process_lab_report(
        file_path="test_reports/blood_report.pdf",
        test_type="blood",
        age=46,
        sex="female",
        extractor="auto",
        llm=None
    )

    print(json.dumps(result, indent=4))