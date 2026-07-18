import unittest
from medical_tools.lab_analyzer import analyze_report, get_range

class TestLabAnalyzer(unittest.TestCase):
    def test_get_range(self):
        marker = {
            "sex_based": True,
            "age_based": False,
            "ranges": {
                "male": {"min": 13.5, "max": 17.5},
                "female": {"min": 12.0, "max": 15.5}
            }
        }
        male_range = get_range(marker, sex="male")
        self.assertEqual(male_range["min"], 13.5)
        female_range = get_range(marker, sex="female")
        self.assertEqual(female_range["min"], 12.0)

    def test_analyze_report_blood(self):
        report = {
            "tests": [
                {"marker": "Hb", "value": 10},
                {"marker": "LDL-C", "value": 180},
                {"marker": "Glucose", "value": 90}
            ],
            "metadata": {"source": "test_regex"}
        }
        res = analyze_report("blood", report, age=25, sex="male")
        
        self.assertEqual(res["summary"]["total_tests"], 3)
        self.assertEqual(res["summary"]["normal"], 1)
        self.assertEqual(res["summary"]["abnormal"], 2)
        self.assertIn("analysis_version", res["summary"])
        self.assertIn("processed_markers", res["summary"])
        self.assertEqual(res["metadata"]["source"], "test_regex")

        results = {r["marker"]: r for r in res["results"]}
        self.assertEqual(results["Hemoglobin"]["status"], "LOW")
        self.assertEqual(results["Low Density Lipoprotein Cholesterol"]["status"], "HIGH")
        self.assertEqual(results["Blood Glucose"]["status"], "NORMAL")

if __name__ == "__main__":
    unittest.main()
