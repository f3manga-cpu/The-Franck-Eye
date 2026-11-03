import importlib.util
import pathlib
import unittest

FILE = pathlib.Path(__file__).resolve().parents[1] / "audit.py"
spec = importlib.util.spec_from_file_location("auditor", FILE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def base(self):
        return {"id": "t1", "state": "distributed", "channel": "marketplace",
                "offer_url": "https://example.org", "purchases_verified": 0,
                "attributable_gross_eur": 0, "attributable_net_eur": None}

    def test_zero_revenue_is_not_a_sale(self):
        r = audit.audit_experiment(self.base())
        self.assertFalse(r["issues"])
        self.assertIn("ZERO_CONFIRMED_PURCHASES_IN_RECORDED_STATE", r["warnings"])

    def test_payment_claim_rejected_if_no_transaction(self):
        e = self.base()
        e["attributable_gross_eur"] = 49
        self.assertIn("gross_without_verified_purchase",
                      audit.audit_experiment(e)["issues"])

    def test_scales_only_after_payment(self):
        e = self.base()
        e["state"] = "scale"
        self.assertIn("advanced_without_verified_payment",
                      audit.audit_experiment(e)["issues"])

    def test_no_spend_creep(self):
        with self.assertRaises(ValueError):
            audit.audit_state({"schema_version": 2, "spend_ceiling_eur": 20,
                               "experiments": []})


if __name__ == "__main__":
    unittest.main()
