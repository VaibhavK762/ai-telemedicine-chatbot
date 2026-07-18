from .logger import logger

def normalize_numeric_units(marker: str, value: float, unit: str | None = None) -> float:
    """
    Convert extracted numeric values into the units expected by lab_analyzer.py.
    """
    if value is None:
        return value

    # White Blood Cell Count
    # Expected: cells/uL
    # Report may contain: 6.43 (10^3/uL)
    if marker == "wbc_count":
        try:
            val = float(value)
            if val < 100:
                return val * 1000
        except (TypeError, ValueError):
            pass

    # Platelets
    # Expected: cells/uL
    # Reports often write: 251 (10^3/uL)
    if marker == "platelets":
        try:
            val = float(value)
            if val < 1000:
                return val * 1000
        except (TypeError, ValueError):
            pass

    # RBC Count
    # Usually already in million/uL
    if marker == "rbc_count":
        try:
            return float(value)
        except (TypeError, ValueError):
            pass

    return value


def normalize_extracted_tests(extraction: dict) -> dict:
    """
    Normalize every extracted marker.
    """
    logger.info("Normalizing extracted tests.")
    tests = extraction.get("tests", [])
    normalized_tests = []
    for test in tests:
        normalized_value = normalize_numeric_units(
            marker=test.get("marker"),
            value=test.get("value"),
            unit=test.get("unit")
        )
        normalized_tests.append({
            **test,
            "value": normalized_value
        })
    return {
        **extraction,
        "tests": normalized_tests
    }