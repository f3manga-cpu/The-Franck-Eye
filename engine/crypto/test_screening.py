import sqlite3
import tempfile
import unittest
from pathlib import Path
from screening import screen

class ScreeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Path(self.tmp.name)/"test.sqlite3"
        con=sqlite3.connect(self.db)
        con.execute("CREATE TABLE observations(observed_at TEXT,token_address TEXT,symbol TEXT,liquidity_usd REAL,volume24_usd REAL,boosts REAL,buys24 INTEGER,sells24 INTEGER)")
        con.executemany("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?)",[
            ("2026-01-01T00:00:00Z","A","A",10000,100,0,5,4),
            ("2026-01-01T00:15:00Z","A","A",1500,40000,2,20,10),
            ("2026-01-01T00:00:00Z","B","B",0,0,0,0,0),
            ("2026-01-01T00:15:00Z","B","B",0,0,0,0,0),
            ("2026-01-01T00:00:00Z","C","C",20000,100,0,1,1)])
        con.commit();con.close()
    def tearDown(self):self.tmp.cleanup()
    def test_decline_and_boost(self):
        r=screen(self.db);a=next(x for x in r["candidates"] if x["symbol"]=="A")
        self.assertEqual(a["decline_from_observed_peak_pct"],85)
        self.assertIn("paid-promotion-observed",a["cautions"])
        self.assertIn("24h-volume-to-current-liquidity-over-20",a["cautions"])
    def test_zero_liquidity_not_decline(self):
        r=screen(self.db);b=next(x for x in r["candidates"] if x["symbol"]=="B")
        self.assertIsNone(b["decline_from_observed_peak_pct"])
        self.assertIn("liquidity-unavailable",b["cautions"])
    def test_singleton_excluded(self):
        r=screen(self.db);self.assertNotIn("C",[x["symbol"] for x in r["candidates"]])
    def test_bad_min_points(self):
        with self.assertRaises(ValueError):screen(self.db,1)
    def test_missing_db(self):
        self.assertEqual(screen(Path(self.tmp.name)/"missing.sqlite3")["status"],"no_data")

if __name__=="__main__":unittest.main()
