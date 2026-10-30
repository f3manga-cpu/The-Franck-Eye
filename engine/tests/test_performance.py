import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

FILE=pathlib.Path(__file__).resolve().parents[1]/"performance.py"
spec=importlib.util.spec_from_file_location("performance",FILE)
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
class TestEngine(unittest.TestCase):
    def test_scoring_and_guardrails(self):
        self.assertGreater(p.rank("Creator marketplace revenue API"),0)
        self.assertLess(p.rank("rug pull marketplace"),0)
    def test_ledger_no_fake_revenue(self):
        with tempfile.TemporaryDirectory() as t:
            with patch.object(p,"DATA",pathlib.Path(t)),patch.object(p,"EVENTS",pathlib.Path(t)/"events.jsonl"):
                self.assertEqual(p.report()["gross_confirmed_eur"],0)
                with self.assertRaises(ValueError): p.record("payment_confirmed","x",amount=5900)
                p.record("published","x")
                self.assertEqual(p.report()["gross_confirmed_eur"],0)
                p.record("payment_confirmed","x",amount=5900,evidence="Stripe verified",reference="pi_example")
                self.assertEqual(p.report()["gross_confirmed_eur"],59)
                with self.assertRaises(ValueError):
                    p.record("payment_confirmed","x",amount=5900,evidence="Stripe verified",reference="pi_example")
    def test_discover_dedupe(self):
        with tempfile.TemporaryDirectory() as t:
            with patch.object(p,"DATA",pathlib.Path(t)),patch.object(p,"OPPORTUNITIES",pathlib.Path(t)/"opportunities.json"):
                now=p.now().replace("+00:00","Z")
                hit={"hits":[{"title":"New creator marketplace monetization API","url":"https://example.org/a","created_at":now,"objectID":"123"}]}
                with patch.object(p,"SOURCES",[("test","https://example.org/feed")]):
                    p.discover(fetch=lambda _:hit)
                    p.discover(fetch=lambda _:hit)
                self.assertEqual(len(json.loads((pathlib.Path(t)/"opportunities.json").read_text())["candidates"]),1)
if __name__=="__main__": unittest.main()
