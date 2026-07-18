import unittest
from medical_tools import process_lab_report

class TestIntegration(unittest.TestCase):
    def test_pipeline_regression_suite(self):
        reports = [
            ("test_reports/blood_report.pdf", "blood"),
            ("test_reports/urine_report.pdf", "urine")
        ]
        
        for report_path, test_type in reports:
            with self.subTest(report_path=report_path, test_type=test_type):
                result = process_lab_report(
                    file_path=report_path,
                    test_type=test_type,
                    age=45,
                    sex="female",
                    extractor="auto"
                )
                self.assertNotIn("error", result)
                self.assertIn("metadata", result)
                self.assertIn("extracted_tests", result)
                self.assertIn("analysis", result)
                
                # Check structure of extraction
                metadata = result["metadata"]
                self.assertEqual(metadata["report_type"], test_type)
                
                # Check analysis results
                analysis = result["analysis"]
                self.assertIn("summary", analysis)
                self.assertIn("results", analysis)

if __name__ == "__main__":
    unittest.main()
