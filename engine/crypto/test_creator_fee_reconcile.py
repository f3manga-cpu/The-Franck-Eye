import csv
import tempfile
import unittest
from pathlib import Path
from creator_fee_reconcile import reconcile

HEADER = ["transaction_signature","token_address","timestamp_utc","fee_sol"]
class ReconcileTests(unittest.TestCase):
    def check(self, entries):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/"fees.csv"
            with p.open("w", newline="") as stream:
                w=csv.writer(stream); w.writerow(HEADER); w.writerows(entries)
            return reconcile(p)
    def test_totals_and_per_token(self):
        r=self.check([["sig1","tokenA","2026-11-12T00:00:00Z","0.1"],["sig2","tokenA","2026-11-12T01:00:00+00:00","0.2"],["sig3","tokenB","2026-11-12T00:00:00Z","0.05"]])
        self.assertEqual(r["total_reported_sol"],"0.35")
        self.assertEqual(r["by_token_reported_sol"]["tokenA"],"0.3")
        self.assertIsNone(r["bank_settled_eur"])
    def test_duplicate_rejected(self):
        r=self.check([["sig1","A","2026-11-12T00:00:00Z","1"],["sig1","A","2026-11-12T00:00:00Z","1"]])
        self.assertEqual((r["accepted_rows"],r["rejected_rows"]),(1,1))
    def test_negative_rejected(self):
        self.assertEqual(self.check([["s","A","2026-11-12T00:00:00Z","-1"]])["accepted_rows"],0)
    def test_nan_rejected(self):
        self.assertEqual(self.check([["s","A","2026-11-12T00:00:00Z","NaN"]])["accepted_rows"],0)
    def test_naive_time_rejected(self):
        self.assertEqual(self.check([["s","A","2026-11-12T00:00:00","1"]])["accepted_rows"],0)
    def test_overprecision_rejected(self):
        self.assertEqual(self.check([["s","A","2026-11-12T00:00:00Z","0.0000000001"]])["accepted_rows"],0)
    def test_missing_columns(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"a.csv";p.write_text("transaction_signature,fee_sol\na,1\n")
            with self.assertRaises(ValueError):reconcile(p)
    def test_hash_stable(self):
        x=self.check([["s","A","2026-11-12T00:00:00Z","1"]])
        y=self.check([["s","A","2026-11-12T00:00:00Z","1"]])
        self.assertEqual(x["source_sha256"],y["source_sha256"])
if __name__=="__main__": unittest.main()
