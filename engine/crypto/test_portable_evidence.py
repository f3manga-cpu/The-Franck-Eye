import sqlite3
import tempfile
import unittest
from pathlib import Path
from portable_evidence import html_report,export

class PortableEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"obs.sqlite3"
        c=sqlite3.connect(self.db)
        c.execute("""CREATE TABLE observations (observed_at TEXT, token_address TEXT, symbol TEXT, name TEXT, dex TEXT, pair_url TEXT, volume24_usd REAL, liquidity_usd REAL, buys24 INTEGER, sells24 INTEGER, boosts REAL, market_cap_usd REAL)""")
        c.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",("2026-11-11T20:00:00+00:00","A"*40,"<script>alert(1)</script>","Test","raydium","javascript:alert(1)",500,1000,2,3,0,10000))
        c.commit();c.close()
    def test_export_no_scripts(self):
        out=Path(self.tmp.name)/"report.html"
        export("A"*40,self.db,out)
        html=out.read_text()
        self.assertIn("&lt;script&gt;",html)
        self.assertNotIn("<script>",html)
        self.assertNotIn("href=\"javascript:",html)
        self.assertIn("Not investment advice",html)
    def test_no_unknown_token(self):
        with self.assertRaises(ValueError):
            export("B"*40,self.db,Path(self.tmp.name)/"report.html")
    def test_no_path_traversal_identifier(self):
        with self.assertRaises(ValueError):
            export("../secret",self.db,Path(self.tmp.name)/"report.html")
    def test_allowed_source(self):
        from evidence_report import report
        c=sqlite3.connect(self.db)
        c.execute("UPDATE observations SET pair_url='https://dexscreener.com/solana/example'")
        c.commit();c.close()
        self.assertIn("View original market source",html_report(report("A"*40,self.db)))

if __name__=="__main__":
    unittest.main()
