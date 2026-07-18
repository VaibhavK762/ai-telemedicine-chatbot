from .lab_analyzer import find_marker
from .logger import logger

def validate_extracted_tests(test_type: str, tests: list[dict]) -> list[dict]:
    """
    Validates extracted tests against the laboratory knowledge base.
    Filters out markers that don't exist, invalid value types, and logs warnings for unit mismatches.
    """
    valid_tests = []
    
    for test in tests:
        marker_name = test.get("marker")
        if not marker_name:
            logger.warning("Extraction contains an entry without a marker name.")
            continue
            
        marker_data = find_marker(test_type, marker_name)
        if not marker_data:
            logger.warning("Validation failed: Marker '%s' not found in knowledge base for test type '%s'.", marker_name, test_type)
            continue
            
        value = test.get("value")
        if value is None:
            logger.warning("Validation failed: Marker '%s' has a null/missing value.", marker_name)
            continue
            
        marker_type = marker_data.get("type", "numeric")
        
        # Check Value Type
        if marker_type == "numeric":
            try:
                # Ensure it can be represented as a numeric value
                float(value)
            except (TypeError, ValueError):
                logger.warning("Validation failed: Numeric marker '%s' has non-numeric value: %s.", marker_name, value)
                continue
        elif marker_type == "categorical":
            # For categorical markers, make sure it is a non-empty string or standard representation
            if not str(value).strip():
                logger.warning("Validation failed: Categorical marker '%s' has empty value.", marker_name)
                continue
                
        # Check Unit
        expected_unit = marker_data.get("unit")
        unit = test.get("unit")
        if expected_unit and unit:
            if unit.lower().strip() != expected_unit.lower().strip():
                logger.warning("Unit mismatch for marker '%s': expected '%s', got '%s'.", marker_name, expected_unit, unit)
                
        valid_tests.append({
            "marker": marker_name,
            "display_name": marker_data.get("display_name", marker_name),
            "value": value,
            "unit": unit or expected_unit
        })
        
    return valid_tests
