import unittest
from medical_tools import process_lab_report

class TestPipeline(unittest.TestCase):
    def test_pipeline_blood_report(self):
        report_path = "test_reports/blood_report.pdf"
        result = process_lab_report(
            file_path=report_path,
            test_type="blood",
            age=46,
            sex="female"
        )
        self.assertNotIn("error", result)
        self.assertEqual(result["metadata"]["report_type"], "blood")
        self.assertGreaterEqual(len(result["extracted_tests"]), 5)
        
        analysis = result["analysis"]
        self.assertGreaterEqual(analysis["summary"]["total_tests"], 5)
        self.assertGreaterEqual(analysis["summary"]["normal"], 1)
        self.assertGreaterEqual(analysis["summary"]["abnormal"], 1)

    def test_pipeline_urine_report(self):
        report_path = "test_reports/urine_report.pdf"
        result = process_lab_report(
            file_path=report_path,
            test_type="urine",
            age=25,
            sex="female"
        )
        self.assertNotIn("error", result)
        self.assertEqual(result["metadata"]["report_type"], "urine")
        self.assertGreaterEqual(len(result["extracted_tests"]), 1)

if __name__ == "__main__":
    unittest.main()
