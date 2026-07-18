import unittest
from medical_tools.extractors.llm_extractor import llm_extract

class TestLLMExtractor(unittest.TestCase):
    def test_llm_extraction_parsing(self):
        class DummyLLM:
            def __call__(self, prompt):
                return """
                [
                    {"marker": "hemoglobin", "value": 11.7, "unit": "g/dL"},
                    {"marker": "platelets", "value": 251, "unit": "10^3/uL"}
                ]
                """
        
        result = llm_extract("some text report content", DummyLLM())
        self.assertEqual(result["metadata"]["source"], "llm")
        self.assertEqual(result["metadata"]["markers_found"], 2)
        self.assertGreaterEqual(result["metadata"]["confidence"], 0.9)
        
        tests = {t["marker"]: t for t in result["tests"]}
        self.assertIn("hemoglobin", tests)
        self.assertEqual(tests["hemoglobin"]["value"], 11.7)
        self.assertIn("platelets", tests)
        self.assertEqual(tests["platelets"]["value"], 251)

if __name__ == "__main__":
    unittest.main()
