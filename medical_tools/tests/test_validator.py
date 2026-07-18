import unittest
from medical_tools.validator import validate_extracted_tests

class TestValidator(unittest.TestCase):
    def test_validate_valid_markers(self):
        raw_tests = [
            {"marker": "hemoglobin", "value": 14.5, "unit": "g/dL"},
            {"marker": "glucose", "value": 95.0, "unit": "mg/dL"}
        ]
        validated = validate_extracted_tests("blood", raw_tests)
        self.assertEqual(len(validated), 2)
        self.assertEqual(validated[0]["marker"], "hemoglobin")
        self.assertEqual(validated[1]["marker"], "glucose")

    def test_validate_invalid_marker(self):
        raw_tests = [
            {"marker": "unknown_nonexistent_test", "value": 100.0, "unit": "mg/dL"}
        ]
        validated = validate_extracted_tests("blood", raw_tests)
        self.assertEqual(len(validated), 0)

    def test_validate_value_type_mismatch(self):
        raw_tests = [
            {"marker": "hemoglobin", "value": "not-a-number", "unit": "g/dL"}
        ]
        validated = validate_extracted_tests("blood", raw_tests)
        self.assertEqual(len(validated), 0)

    def test_validate_unit_mismatch_warning(self):
        raw_tests = [
            # Hemoglobin expects g/dL, let's pass mg/dL.
            {"marker": "hemoglobin", "value": 14.5, "unit": "mg/dL"}
        ]
        validated = validate_extracted_tests("blood", raw_tests)
        self.assertEqual(len(validated), 1)
        self.assertEqual(validated[0]["unit"], "mg/dL")

    def test_duplicate_marker(self):
        raw_tests = [
            {"marker": "hemoglobin", "value": 14.5, "unit": "g/dL"},
            {"marker": "hemoglobin", "value": 15.0, "unit": "g/dL"}
        ]
        validated = validate_extracted_tests("blood", raw_tests)
        self.assertEqual(len(validated), 2)

    def test_missing_value(self):
        raw_tests = [
            {"marker": "hemoglobin", "value": None, "unit": "g/dL"}
        ]
        validated = validate_extracted_tests("blood", raw_tests)
        self.assertEqual(len(validated), 0)

    def test_none_marker(self):
        raw_tests = [
            {"marker": None, "value": 14.5, "unit": "g/dL"}
        ]
        validated = validate_extracted_tests("blood", raw_tests)
        self.assertEqual(len(validated), 0)

if __name__ == "__main__":
    unittest.main()
