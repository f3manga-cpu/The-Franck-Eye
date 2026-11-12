import sqlite3
import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from onchain_fee_probe import collect,latest_mints,signatures_for

MINT="4"*43
SIG="3"*87
class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.market=Path(self.tmp.name)/"market.sqlite3"
        self.evidence=Path(self.tmp.name)/"evidence.sqlite3"
        c=sqlite3.connect(self.market)
        c.execute("CREATE TABLE observations(observed_at TEXT,token_address TEXT,dex TEXT,volume24_usd REAL)")
        c.execute("INSERT INTO observations VALUES (?,?,?,?)",("2026-11-12T02:00:00Z",MINT,"pumpswap",250))
        c.commit();c.close()
    def tearDown(self):
        self.tmp.cleanup()
    def test_latest_mints(self):
        self.assertEqual(latest_mints(self.market),[MINT])
    def test_collect_and_deduplicate(self):
        def fake(sig,idls):
            return {"signature":sig,"event_count":1,"revenue_attributable_to_user":False}
        opts=dict(market=self.market,evidence=self.evidence,
            clock=datetime(2026,11,12,tzinfo=timezone.utc),
            fetch_signatures=lambda mint:[SIG],audit_func=fake,idls={})
        one=collect(**opts);self.assertEqual(one["new_fee_events_observed"],1)
        two=collect(**opts);self.assertEqual(two["new_signatures_stored"],0)
        self.assertEqual(two["stored_signatures"],1)
        self.assertFalse(two["creator_revenue_to_user_verified"])
    def test_no_mints(self):
        c=sqlite3.connect(self.market);c.execute("DELETE FROM observations");c.commit();c.close()
        with self.assertRaisesRegex(RuntimeError,"No recent"):
            collect(market=self.market,evidence=self.evidence)
    def test_bad_mint_no_network(self):
        with self.assertRaises(ValueError):
            signatures_for("private-key-text")
if __name__=="__main__":unittest.main()
