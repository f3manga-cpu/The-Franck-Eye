import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("lab_analytics", Path(__file__).resolve().parents[1] / "analytics.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

class MetricsTests(unittest.TestCase):
    def test_empty_data_is_not_a_win_rate(self):
        out = lab.calculate([])
        self.assertIsNone(out["verified_hit_rate"])
        self.assertIsNone(out["brier_score"])

    def test_reported_not_mixed_with_verified(self):
        rows = [{"grade_status": "reported_hit", "market": "PTS"},
                {"grade_status": "miss", "market": "REB"}]
        out = lab.calculate(rows)
        self.assertEqual(out["verified_sample"], 1)
        self.assertEqual(out["reported_sample_not_independently_audited"], 1)
        self.assertEqual(out["verified_hit_rate"], 0.0)

    def test_calibration_only_verified_probabilities(self):
        rows = [{"grade_status": "hit", "model_probability": 0.8, "market": "AST"},
                {"grade_status": "miss", "model_probability": 0.2, "market": "AST"},
                {"grade_status": "reported_hit", "model_probability": 0.99}]
        out = lab.calculate(rows)
        self.assertEqual(out["probability_scored_sample"], 2)
        self.assertAlmostEqual(out["brier_score"], 0.04)
        self.assertEqual(out["by_market_verified"]["AST"], {"hit": 1, "miss": 1})

    def test_no_phantom_cash_return(self):
        out = lab.calculate([{"grade_status": "hit", "market": "PTS", "odds_american": 120}])
        self.assertIsNone(out["actual_bet_roi"])
        self.assertIsNone(out["closing_line_value"])

    def test_american_odds_break_even(self):
        self.assertAlmostEqual(lab.implied_probability(-113), 113/213)
        self.assertAlmostEqual(lab.implied_probability(124), 100/224)

if __name__ == "__main__":
    unittest.main()
