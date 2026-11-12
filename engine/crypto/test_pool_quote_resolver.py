import unittest
import base64
from pool_quote_resolver import decode_pool, fetch_pool
from pump_fee_event_audit import PROGRAMS

PROGRAM = next(k for k,v in PROGRAMS.items() if v=="pump_amm.json")
IDL={"accounts":[{"name":"Pool","discriminator":[1,2,3,4,5,6,7,8]}],
"types":[{"name":"Pool","type":{"fields":[{"name":"pool_bump","type":"u8"},{"name":"index","type":"u16"},{"name":"creator","type":"pubkey"},{"name":"base_mint","type":"pubkey"},{"name":"quote_mint","type":"pubkey"},{"name":"coin_creator","type":"pubkey"},{"name":"is_holder_reward","type":"bool"},{"name":"creator_fee_bps","type":"u64"}]}}]}
def account():
    blob=bytes(range(1,9))+bytes([1])+bytes([2,0])+bytes(32)*4+bytes([0])+bytes(8)
    return {"owner":PROGRAM,"executable":False,"data":[base64.b64encode(blob).decode(),"base64"]}
class Tests(unittest.TestCase):
    def test_verified(self):
        result=decode_pool(account(),IDL)
        self.assertEqual(result["status"],"POOL_ACCOUNT_VERIFIED")
        self.assertFalse(result["fee_entitlement_verified"])
        self.assertFalse(result["receipt_verified"])
    def test_wrong_owner(self):
        a=account();a["owner"]="1"*32
        with self.assertRaises(ValueError):decode_pool(a,IDL)
    def test_wrong_discriminator(self):
        a=account();a["data"][0]=base64.b64encode(b"badstuff"+base64.b64decode(a["data"][0])[8:]).decode()
        with self.assertRaises(ValueError):decode_pool(a,IDL)
    def test_bad_encoding(self):
        a=account();a["data"][1]="base58"
        with self.assertRaises(ValueError):decode_pool(a,IDL)
    def test_invalid_pool_rejected_before_rpc(self):
        with self.assertRaises(ValueError):fetch_pool("not-a-key",IDL)
if __name__=="__main__":unittest.main()
