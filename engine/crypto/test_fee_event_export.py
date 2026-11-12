import csv
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from fee_event_export import export

class ExportTests(unittest.TestCase):
    def test_export_real_schema_and_unverified(self):
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/'sample.sqlite3'
            con=sqlite3.connect(db)
            con.execute('CREATE TABLE samples(signature TEXT PRIMARY KEY, observed_at_utc TEXT, sample_mint TEXT,event_count INTEGER,report_json TEXT)')
            record={'signature':'sig1','status':'FINALIZED_EVENT_DATA','slot':123,'events':[{'event':'BuyEvent','kind':'TRADE_FEE_FIELD_UNATTRIBUTED','program':'pump','amount_raw_quote_units':3419,'data':{'coin_creator':'creator'}}]}
            con.execute('INSERT INTO samples VALUES(?,?,?,?,?)',('sig1','2026-11-12T00:00:00Z','mint',1,json.dumps(record)))
            con.commit();con.close()
            data=list(csv.DictReader(io.StringIO(export(db))))
            self.assertEqual(len(data),1)
            self.assertEqual(data[0]['amount_raw_quote_units'],'3419')
            self.assertEqual(data[0]['quote_mint'],'UNKNOWN')
            self.assertEqual(data[0]['attributable_to_operator'],'UNVERIFIED')
            self.assertEqual(data[0]['bank_settled_eur'],'UNVERIFIED')
    def test_empty_db_is_header_only(self):
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/'sample.sqlite3'
            con=sqlite3.connect(db)
            con.execute('CREATE TABLE samples(signature TEXT, observed_at_utc TEXT, report_json TEXT)')
            con.close()
            self.assertEqual(len(export(db).splitlines()),1)
if __name__=='__main__':unittest.main()

[executed on device: franck-pc-portable (f33e61fa-10ff-4a7f-845b-7dbff80d0f4f)]