import datetime as dt
import tempfile
import unittest
from pathlib import Path
from engine.buyer_intent import classify, run
NOW = dt.datetime(2026,11,5,tzinfo=dt.timezone.utc)
def issue(**updates):
    x={"state":"open","title":"Paid task: correct invoice parser","body":"Reward €250 for completed work",
       "html_url":"https://github.com/example/repo/issues/45","updated_at":"2026-11-04T11:00:00Z","labels":[{"name":"bounty"}]}
    x.update(updates)
    return x
class BuyerIntentTests(unittest.TestCase):
    def test_paid_signal(self):
        x=classify(issue(),NOW)
        self.assertEqual(x["budget_mentioned"],"€250")
        self.assertEqual(x["state"],"unverified_public_lead")
    def test_reject_closed(self): self.assertIsNone(classify(issue(state="closed"),NOW))
    def test_reject_expired(self): self.assertIsNone(classify(issue(updated_at="2025-01-01T00:00:00Z"),NOW))
    def test_reject_unpaid(self): self.assertIsNone(classify(issue(title="Fix docs",body="Quick fix",labels=[]),NOW))
    def test_reject_phishing(self): self.assertIsNone(classify(issue(body="Bounty €250 for phishing"),NOW))
    def test_dedup(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            x=run(fetch=lambda url:{"items":[issue(),issue()]},now=NOW,output=d/"results.json",report=d/"report.md")
            self.assertEqual(len(x["candidates"]),1)
            self.assertEqual(x["proven_sales"],0)
    def test_api_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            def fail(url): raise OSError("network failed")
            x=run(fetch=fail,now=NOW,output=d/"results.json",report=d/"report.md")
            self.assertEqual(len(x["source_errors"]),3)
            self.assertEqual(len(x["candidates"]),0)
