import base64
import struct
import unittest
from pump_fee_event_audit import PROGRAMS, inspect_logs, audit, b58

PUMP_AMM="pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
SWEEP=bytes([130,164,36,97,228,130,135,165])
FIELDS=[{"name":"timestamp","type":"i64"},{"name":"pool","type":"pubkey"},
        {"name":"base_mint","type":"pubkey"},{"name":"quote_mint","type":"pubkey"},
        {"name":"recipient","type":"pubkey"},{"name":"payer","type":"pubkey"},
        {"name":"amount","type":"u64"},{"name":"bucket","type":"u8"}]
IDL={(PUMP_AMM,SWEEP):("SweepPoolFeeEvent",FIELDS)}
SIG="3"*87
def record(program=PUMP_AMM,bucket=1):
    payload=SWEEP+struct.pack("<q",1794448526)+b"\0"*32*5+struct.pack("<QB",12345,bucket)
    return [f"Program {program} invoke [1]",
            "Program data: "+base64.b64encode(payload).decode(),
            f"Program {program} success"]
def tx(logs):
    return {"slot":777,"version":1,"meta":{"err":None,"logMessages":logs}}
class FeeEventTests(unittest.TestCase):
    def test_sweep_creator_vault(self):
        r=inspect_logs(tx(record()),IDL)
        self.assertEqual(len(r),1)
        self.assertEqual(r[0]["kind"],"FEE_SWEPT_TO_VAULT")
        self.assertEqual(r[0]["amount_raw_quote_units"],12345)
        self.assertEqual(r[0]["data"]["quote_mint"],"1"*32)
    def test_protocol_sweep_excluded(self):
        self.assertEqual(inspect_logs(tx(record(bucket=0)),IDL),[])
    def test_spoofed_other_program_excluded(self):
        self.assertEqual(inspect_logs(tx(record(program="11111111111111111111111111111111")),IDL),[])
    def test_bad_payload_ignored(self):
        lines=record(); lines[1]="Program data: not-base64???"
        self.assertEqual(inspect_logs(tx(lines),IDL),[])
    def test_audit_not_user_revenue(self):
        r=audit(SIG,fetch=lambda _:tx(record()),idls=IDL)
        self.assertEqual(r["status"],"FINALIZED_EVENT_DATA")
        self.assertFalse(r["revenue_attributable_to_user"])
        self.assertIsNone(r["bank_settled_eur"])
    def test_no_program_logs_fails(self):
        with self.assertRaisesRegex(ValueError,"no program logs"):
            inspect_logs({"meta":{"err":None,"logMessages":None}},IDL)
    def test_zero_key_base58(self):
        self.assertEqual(b58(b"\0"*32),"1"*32)
if __name__=="__main__":unittest.main()
