import unittest
from datetime import datetime,timedelta,timezone
from forward_validation import assess

BASE=datetime(2026,11,11,tzinfo=timezone.utc)
def row(address,minute,liquidity,volume=0,boost=0):
    return {"token_address":address,"observed_at":(BASE+timedelta(minutes=minute)).isoformat(),
       "liquidity_usd":liquidity,"volume24_usd":volume,"boosts":boost}

class ForwardValidationTests(unittest.TestCase):
    def test_no_lookahead(self):
        r=assess([row("a",0,20000),row("a",40,1000,999999,100)])
        self.assertEqual(r["unflagged_assets"],1)
        self.assertEqual(r["unflagged_decline_rate"],1)
    def test_minimum_horizon(self):
        r=assess([row("a",0,1000),row("a",20,1),row("a",40,900)])
        self.assertEqual(r["flagged_decline_rate"],0)
    def test_missing_future_not_counted(self):
        r=assess([row("a",0,2000),row("a",10,100),row("b",0,20000),row("b",50,30000)])
        self.assertEqual(r["eligible_assets"],1)
        self.assertEqual(r["skipped_without_followup"],1)
    def test_missing_liquidity(self):
        r=assess([row("a",0,0),row("a",40,100)])
        self.assertEqual(r["eligible_assets"],0)
    def test_threshold(self):
        r=assess([row("a",0,20000,400001),row("a",40,5000),row("b",0,20000),row("b",40,25000)])
        self.assertEqual(r["flagged_decline_rate"],1)
        self.assertEqual(r["unflagged_decline_rate"],0)
    def test_reject_invalid_horizon(self):
        with self.assertRaises(ValueError):assess([],0)

if __name__=="__main__":unittest.main()
