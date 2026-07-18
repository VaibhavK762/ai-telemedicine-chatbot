import unittest
from medical_tools.unit_normalizer import normalize_extracted_tests

class TestUnitNormalizer(unittest.TestCase):
    def test_normalize_wbc_count(self):
        extraction = {
            "tests": [
                {"marker": "wbc_count", "display_name": "WBC", "value": 6.5, "unit": "10^3/uL"}
            ],
            "metadata": {"source": "test"}
        }
        normalized = normalize_extracted_tests(extraction)
        self.assertEqual(normalized["tests"][0]["value"], 6500.0)
        self.assertEqual(normalized["metadata"]["source"], "test")

    def test_normalize_platelets(self):
        extraction = {
            "tests": [
                {"marker": "platelets", "display_name": "PLT", "value": 250, "unit": "10^3/uL"}
            ],
            "metadata": {}
        }
        normalized = normalize_extracted_tests(extraction)
        self.assertEqual(normalized["tests"][0]["value"], 250000.0)

    def test_normalize_rbc_count(self):
        extraction = {
            "tests": [
                {"marker": "rbc_count", "display_name": "RBC", "value": 4.5, "unit": "million/uL"}
            ],
            "metadata": {}
        }
        normalized = normalize_extracted_tests(extraction)
        self.assertEqual(normalized["tests"][0]["value"], 4.5)

if __name__ == "__main__":
    unittest.main()
