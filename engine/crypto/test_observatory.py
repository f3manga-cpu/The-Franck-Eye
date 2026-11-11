#!/usr/bin/env python3
"""Tests for read-only observatory. Run: python3 -m unittest -v test_observatory.py"""
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from urllib.request import urlopen
from http.server import ThreadingHTTPServer
from observatory import Handler,page,snapshot

class ObservatoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Path(self.tmp.name)/"test.sqlite3"
        c=sqlite3.connect(self.db)
        c.execute("CREATE TABLE cycles(id INTEGER PRIMARY KEY,observed_at TEXT,status TEXT,error TEXT)")
        c.execute("""CREATE TABLE observations(observed_at TEXT,token_address TEXT,symbol TEXT,name TEXT,
            dex TEXT,pair_url TEXT,volume24_usd REAL,liquidity_usd REAL,buys24 INTEGER,
            sells24 INTEGER,boosts REAL,market_cap_usd REAL)""")
        c.execute("INSERT INTO cycles VALUES(1,'2026-11-11T15:00:00+00:00','success','')")
        c.execute("INSERT INTO observations VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            ('2026-11-11T15:00:00+00:00','token','<script>','Test','pumpfun',
             'javascript:alert(1)',200000,500,10,10,50,1000000))
        c.commit();c.close()
    def tearDown(self):self.tmp.cleanup()
    def test_snapshot_risk_flags(self):
        s=snapshot(self.db)
        self.assertEqual(s["cycles"],1)
        self.assertEqual(len(s["assets"]),1)
        self.assertEqual(s["assets"][0]["volume_liquidity_ratio"],400)
        self.assertIn("thin-liquidity",s["assets"][0]["cautions"])
        self.assertIn("paid-boost-observed",s["assets"][0]["cautions"])
        self.assertFalse(s["revenue_verified"])
    def test_html_escapes_untrusted_fields_and_bad_links(self):
        html=page(snapshot(self.db))
        self.assertNotIn("<script>",html)
        self.assertNotIn('href="javascript:',html)
        self.assertIn("&lt;script&gt;",html)
    def test_no_database(self):
        s=snapshot(Path(self.tmp.name)/"missing.sqlite3")
        self.assertEqual(s["status"],"no_data")
    def test_http_read_only_routes(self):
        server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/api/summary",timeout=3) as r:
                x=json.load(r)
                self.assertIn("revenue_verified",x)
                self.assertEqual(x["financial_transactions"],0)
            with urlopen(f"http://127.0.0.1:{server.server_port}/",timeout=3) as r:
                self.assertIn(b"Research only",r.read())
        finally:server.shutdown();server.server_close();thread.join(2)

if __name__=="__main__":unittest.main()
