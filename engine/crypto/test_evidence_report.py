import sqlite3
import tempfile
import unittest
from pathlib import Path
from evidence_report import report

class EvidenceReportTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.db=Path(self.t.name)/"db.sqlite3"
        c=sqlite3.connect(self.db)
        c.execute("""CREATE TABLE observations(observed_at TEXT,token_address TEXT,symbol TEXT,name TEXT,
        dex TEXT,pair_url TEXT,volume24_usd REAL,liquidity_usd REAL,buys24 INTEGER,
        sells24 INTEGER,boosts REAL,market_cap_usd REAL)""")
        for time,liq in [('2026-11-11T10:00:00+00:00',20000),('2026-11-11T11:00:00+00:00',5000)]:
            c.execute("INSERT INTO observations VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (time,'Token123','TKN','Test','pumpswap','https://dexscreener.com/solana/example',100000,liq,12,8,0,500000))
        c.commit();c.close()
    def tearDown(self):self.t.cleanup()
    def test_source_linked(self):
        r=report('Token123',self.db)
        self.assertEqual(r['observation_count'],2)
        self.assertEqual(r['first_observation']['liquidity_usd'],20000)
        self.assertEqual(r['last_observation']['liquidity_usd'],5000)
        self.assertIn('reported-liquidity-down-more-than-half-since-first-observation',r['caution_indicators'])
        self.assertFalse(r['creator_revenue_verified'])
        self.assertIn('dexscreener.com',r['evidence']['source_url'])
    def test_unknown_token(self):self.assertIsNone(report('Absent',self.db))
    def test_injection_rejected(self):
        with self.assertRaises(ValueError):report("abc' OR 1=1--",self.db)
    def test_missing_database(self):
        self.assertIsNone(report('Token123',Path(self.t.name)/'absent.sqlite3'))

if __name__=='__main__':unittest.main()
