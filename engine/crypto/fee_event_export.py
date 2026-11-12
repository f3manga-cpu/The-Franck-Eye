#!/usr/bin/env python3
"""Export auditable public fee observations; never imply user earnings."""
import argparse
import csv
import io
import json
import sqlite3
from pathlib import Path

COLUMNS = ('signature','slot','event_index','program','event','kind','amount_raw_quote_units','quote_mint','beneficiary_public_key','observed_at_utc','attributable_to_operator','bank_settled_eur')

def rows(db):
    con = sqlite3.connect(f'file:{Path(db).resolve()}?mode=ro', uri=True)
    try:
        for sig, observed, report_json in con.execute('SELECT signature,observed_at_utc,report_json FROM samples ORDER BY observed_at_utc,signature'):
            report=json.loads(report_json)
            if report.get('signature') != sig or report.get('status') != 'FINALIZED_EVENT_DATA':
                continue
            for index, event in enumerate(report.get('events', [])):
                data=event.get('data',{})
                yield dict(signature=sig,slot=report.get('slot'),event_index=index,program=event.get('program'),
                    event=event.get('event'),kind=event.get('kind'),amount_raw_quote_units=event.get('amount_raw_quote_units'),
                    quote_mint=data.get('quote_mint','UNKNOWN'),beneficiary_public_key=data.get('recipient',data.get('coin_creator','UNKNOWN')),
                    observed_at_utc=observed,attributable_to_operator='UNVERIFIED',bank_settled_eur='UNVERIFIED')
    finally:
        con.close()

def export(db):
    out=io.StringIO()
    writer=csv.DictWriter(out,fieldnames=COLUMNS,lineterminator='\n')
    writer.writeheader()
    for record in rows(db): writer.writerow(record)
    return out.getvalue()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('db',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    content=export(a.db)
    if a.output:a.output.write_text(content)
    else:print(content,end='')

[executed on device: franck-pc-portable (f33e61fa-10ff-4a7f-845b-7dbff80d0f4f)]