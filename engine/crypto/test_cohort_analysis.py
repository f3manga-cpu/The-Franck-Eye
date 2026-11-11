import sqlite3
import tempfile
import unittest
from pathlib import Path
from cohort_analysis import report

class CohortTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Path(self.tmp.name)/"test.sqlite3"
        c=sqlite3.connect(self.db)
        c.execute("CREATE TABLE cycles(id INTEGER PRIMARY KEY,observed_at TEXT,status TEXT)")
        c.execute("CREATE TABLE observations(observed_at TEXT,token_address TEXT,symbol TEXT,volume24_usd REAL,liquidity_usd REAL,boosts REAL)")
        c.executemany("INSERT INTO cycles VALUES(?,?,?)",[(1,"2026-11-11T10:00:00+00:00","success"),(2,"2026-11-11T11:00:00+00:00","success"),(3,"2026-11-11T12:00:00+00:00","error")])
        c.executemany("INSERT INTO observations VALUES(?,?,?,?,?,?)",[
            ("2026-11-11T10:00:00+00:00","A","A",100,50,0),
            ("2026-11-11T11:00:00+00:00","A","A",200,40,1),
            ("2026-11-11T11:00:00+00:00","B","B",300,20,0)])
        c.commit();c.close()
    def tearDown(self):self.tmp.cleanup()
    def test_repeat_and_coverage(self):
        x=report(self.db)
        self.assertEqual(x["successful_cycles"],2)
        self.assertEqual(x["failed_cycles"],1)
        self.assertEqual(x["unique_tokens"],2)
        self.assertEqual(x["repeated_spotlight_tokens"],1)
        self.assertEqual(x["tokens_spanning_min_hours"],1)
        self.assertEqual(x["coverage_hours"],1.0)
        self.assertTrue(x["long_span_examples"][0]["ever_boosted"])
        self.assertFalse(x["creator_fees_verified"])
    def test_min_span_filter(self):
        x=report(self.db,min_hours=2)
        self.assertEqual(x["tokens_spanning_min_hours"],0)
    def test_empty(self):
        c=sqlite3.connect(self.db);c.execute("DELETE FROM cycles");c.execute("DELETE FROM observations");c.commit();c.close()
        self.assertEqual(report(self.db)["status"],"no_successful_cycles")

if __name__=="__main__":unittest.main()
