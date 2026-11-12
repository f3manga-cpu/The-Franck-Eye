import unittest
from onchain_receipt_verify import fetch_transaction, verify

SIG="3"*87
REC="4"*43
OTHER="5"*43

def tx(pre=1000000000,post=1035000000,err=None):
    return {"slot":321,"blockTime":1750000000,
            "transaction":{"message":{"accountKeys":[{"pubkey":REC},{"pubkey":OTHER}]}},
            "meta":{"err":err,"preBalances":[pre,2000],"postBalances":[post,2000]}}

class ReceiptTests(unittest.TestCase):
    def test_observed_delta(self):
        r=verify(SIG,REC,tx())
        self.assertEqual(r["recipient_net_delta_sol"],"0.035")
        self.assertFalse(r["creator_fee_attributed"])
        self.assertIsNone(r["bank_settled_eur"])
    def test_negative_delta(self):
        self.assertEqual(verify(SIG,REC,tx(post=990000000))["recipient_net_delta_sol"],"-0.01")
    def test_no_transaction(self):
        self.assertEqual(verify(SIG,REC,None)["status"],"NOT_FOUND_OR_NOT_FINALIZED")
    def test_failed_transaction(self):
        self.assertEqual(verify(SIG,REC,tx(err={"InstructionError":[0,"Custom"]}))["status"],"FAILED_TRANSACTION")
    def test_account_not_present(self):
        self.assertEqual(verify(SIG,"6"*43,tx())["status"],"ACCOUNT_NOT_IN_TRANSACTION")
    def test_bad_address(self):
        with self.assertRaises(ValueError):verify(SIG,"private key",tx())
    def test_mismatch(self):
        x=tx();x["meta"]["postBalances"]=[]
        with self.assertRaises(ValueError):verify(SIG,REC,x)
    def test_duplicate_accounts(self):
        x=tx();x["transaction"]["message"]["accountKeys"][1]={"pubkey":REC}
        with self.assertRaises(ValueError):verify(SIG,REC,x)
    def test_invalid_signature_rejected_before_network(self):
        with self.assertRaises(ValueError):fetch_transaction("bad",transport=lambda p: {})
    def test_rpc_error(self):
        with self.assertRaisesRegex(ValueError,"RPC error"):
            fetch_transaction(SIG,transport=lambda p: {"error":{"code":429}})
    def test_rpc_none(self):
        self.assertIsNone(fetch_transaction(SIG,transport=lambda p: {"result":None}))
    def test_rpc_transaction(self):
        self.assertEqual(fetch_transaction(SIG,transport=lambda p: {"result":tx()})["slot"],321)
    def test_version_one_supported(self):
        calls=[]
        def transport(payload):
            calls.append(payload)
            return {"result":tx()}
        self.assertEqual(fetch_transaction(SIG, transport=transport)["slot"],321)
        self.assertEqual(calls[0]["params"][1]["maxSupportedTransactionVersion"],1)

if __name__=="__main__":unittest.main()
