import json
import unittest
from pathlib import Path
from gta_launch_gate import evaluate

class LaunchGateTests(unittest.TestCase):
    def setUp(self):
        self.candidate = json.loads(Path(__file__).with_name("gta_metadata_candidate.json").read_text())

    def test_candidate_fails_closed_on_art_rights(self):
        result = evaluate(self.candidate)
        self.assertFalse(result["offline_metadata_valid"])
        self.assertIn("image_rights_unverified", result["errors"])
        self.assertFalse(result["mainnet_launch_authorized"])

    def test_owned_art_still_never_authorizes_mainnet(self):
        self.candidate["image_rights"] = "original_owned"
        result = evaluate(self.candidate)
        self.assertTrue(result["offline_metadata_valid"])
        self.assertFalse(result["mainnet_launch_authorized"])

    def test_disclaimer_and_age_required(self):
        self.candidate["independent_disclaimer"] = False
        self.candidate["audience_18_plus"] = False
        result = evaluate(self.candidate)
        self.assertIn("independence_disclaimer_required", result["errors"])
        self.assertIn("adult_audience_gate_required", result["errors"])

    def test_fake_mint_rejected(self):
        self.candidate["mint_address"] = "FAKE"
        self.assertIn("unverified_mint_address", evaluate(self.candidate)["errors"])

if __name__ == "__main__":
    unittest.main()
