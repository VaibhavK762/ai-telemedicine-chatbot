import unittest
from medical_tools.confidence import calculate_confidence

class TestConfidence(unittest.TestCase):
    def test_zero_matches(self):
        self.assertEqual(calculate_confidence(0, 0, 0), 0.0)

    def test_perfect_matches(self):
        self.assertEqual(calculate_confidence(1, 1, 0), 1.0)

    def test_duplicate_penalty(self):
        self.assertEqual(calculate_confidence(2, 1, 1), 0.25)

    def test_negative_clamped(self):
        self.assertEqual(calculate_confidence(2, 0, 5), 0.0)

if __name__ == "__main__":
    unittest.main()
