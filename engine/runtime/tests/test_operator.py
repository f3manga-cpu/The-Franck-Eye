import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from engine.runtime.operator import cycle,verify

NOW=dt.datetime(2026,11,10,15,tzinfo=dt.timezone.utc)
URL="https://github.com/real/repository/issues/42"
def issue(**opts):
    d={"state":"open","title":"Bounty: fix CSV bug €100","body":"Paid task",
       "updated_at":"2026-11-10T12:00:00Z","comments":2}
    d.update(opts)
    return d
class OperatorTests(unittest.TestCase):
    def test_no_fake_funded_assumption(self):
        self.assertEqual(verify(URL,lambda u:issue(),NOW)[0],"payment_proof_needed")
    def test_reject_closed(self):
        self.assertEqual(verify(URL,lambda u:issue(state="closed"),NOW)[0],"closed")
    def test_reject_many_comments(self):
        self.assertEqual(verify(URL,lambda u:issue(comments=200),NOW)[0],"crowded")
    def test_reject_crypto(self):
        self.assertEqual(verify(URL,lambda u:issue(body="crypto token airdrop"),NOW)[0],"excluded")
    def test_invalid_url(self):
        self.assertEqual(verify("https://example.com",now=NOW)[0],"invalid_source")
    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); source=d/"source.json"; state=d/"state.json"; report=d/"report.md"
            source.write_text(json.dumps({"candidates":[{"id":"a","title":"Fix","url":URL}]}))
            a=cycle(source,state,report,lambda u:issue(),NOW)
            b=cycle(source,state,report,lambda u:issue(),NOW)
            self.assertEqual((a["new_public_leads"],a["live_source_checks"]),(1,1))
            self.assertEqual((b["new_public_leads"],b["live_source_checks"]),(0,0))
            self.assertIsNone(json.loads(state.read_text())["sales_verified_by_this_worker"])
