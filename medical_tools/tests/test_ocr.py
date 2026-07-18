import unittest
from medical_tools.ocr_extractor import extract_report_text
from medical_tools.exceptions import OCRFailure

class TestOCRExtractor(unittest.TestCase):
    def test_extract_pdf(self):
        report_path = "test_reports/blood_report.pdf"
        text = extract_report_text(report_path)
        self.assertIsNotNone(text)
        self.assertGreater(len(text), 100)
        self.assertTrue(
            any(
                x.lower() in text.lower()
                for x in ["hemoglobin", "haemoglobin"]
            )
        )

    def test_extract_image_nonexistent(self):
        report_path = "test_reports/nonexistent.png"
        with self.assertRaises(OCRFailure):
            extract_report_text(report_path)

if __name__ == "__main__":
    unittest.main()
