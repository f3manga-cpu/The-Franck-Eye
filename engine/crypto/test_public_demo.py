import tempfile
import unittest
from pathlib import Path
from public_demo import build, landing, choose_tokens

class PublicDemoTests(unittest.TestCase):
    def test_html_escapes_untrusted_symbol(self):
        x=landing([{"symbol":'<script>alert(1)</script>',"observations":2,"liquidity":100}], "now")
        self.assertNotIn("<script>",x)
        self.assertIn("&lt;script&gt;",x)
    def test_no_wallet_or_checkout(self):
        x=landing([{"symbol":"ABC","observations":2,"liquidity":100}],"now")
        self.assertNotIn("<form",x)
        self.assertNotIn("<script",x)
        self.assertNotIn("wallet-adapter",x)
    def test_build_creates_offline_bundle(self):
        db=Path(__file__).resolve().parent/"observations.sqlite3"
        if not db.exists():self.skipTest("No local dataset")
        with tempfile.TemporaryDirectory() as t:
            r=build(db,Path(t),2)
            self.assertEqual(r["cases"],2)
            self.assertEqual(len(list(Path(t).glob("case-*.html"))),2)
            self.assertIn("No wallet connection",(Path(t)/"index.html").read_text())
            self.assertIn('"external_users_verified": 0',(Path(t)/"manifest.json").read_text())
    def test_real_tokens_have_repeated_snapshots(self):
        db=Path(__file__).resolve().parent/"observations.sqlite3"
        if not db.exists():self.skipTest("No local dataset")
        self.assertTrue(all(x["observations"]>=2 for x in choose_tokens(db)))
if __name__=="__main__":unittest.main()
