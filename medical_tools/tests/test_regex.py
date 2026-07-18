import unittest
from medical_tools.extractors.regex_extractor import regex_extract

class TestRegexExtractor(unittest.TestCase):
    def test_regex_blood_extraction(self):
        sample = """
        Hemoglobin 14.5 g/dL
        RBC Count 4.8 million/uL
        Platelets 250 cells/uL
        """
        result = regex_extract(sample, "blood")
        self.assertEqual(result["metadata"]["source"], "regex")
        self.assertEqual(result["metadata"]["markers_found"], 3)
        
        tests = {t["marker"]: t for t in result["tests"]}
        self.assertIn("hemoglobin", tests)
        self.assertEqual(tests["hemoglobin"]["value"], 14.5)
        self.assertIn("rbc_count", tests)
        self.assertEqual(tests["rbc_count"]["value"], 4.8)
        self.assertIn("platelets", tests)
        self.assertEqual(tests["platelets"]["value"], 250.0)

    def test_regex_urine_extraction(self):
        sample = """
        pH 6.5
        SG 1.020
        Protein trace
        """
        result = regex_extract(sample, "urine")
        self.assertEqual(result["metadata"]["markers_found"], 3)
        
        tests = {t["marker"]: t for t in result["tests"]}
        self.assertIn("ph", tests)
        self.assertEqual(tests["ph"]["value"], 6.5)
        self.assertIn("protein", tests)
        self.assertEqual(tests["protein"]["value"], "trace")

    def test_high_confidence(self):
        sample = "Hemoglobin 14.5"
        result = regex_extract(sample, "blood")
        self.assertGreaterEqual(result["metadata"]["confidence"], 0.95)

    def test_low_confidence(self):
        sample = "Hemoglobin\nHemoglobin 14.5"
        result = regex_extract(sample, "blood")
        self.assertLess(result["metadata"]["confidence"], 0.8)


if __name__ == "__main__":
    unittest.main()
