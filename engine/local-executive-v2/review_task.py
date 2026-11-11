#!/usr/bin/env python3
"""Private read-only work queue inspection; NEVER publishes private messages."""
from __future__ import annotations
import argparse
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
import json
from pathlib import Path
import re
import executive_v2 as op

def pending(c,limit=30):
    rows=c.execute('''
      SELECT w.id,w.lane,w.kind,w.gate,w.state,w.deadline,w.engaged,w.created,
             r.uid,r.validity, w.attempts
      FROM work w LEFT JOIN mail_refs r ON r.event_id=w.event_id
      WHERE w.state NOT IN ('BLOCKED','STAGED')
      ORDER BY (w.lane='JOB' AND w.kind='questionnaire' AND w.deadline IS NOT NULL) DESC,
               w.engaged DESC,w.created DESC,w.id
      LIMIT ?''',(limit,)).fetchall()
    return [dict(r) for r in rows]

def inspect(c,work_id,connect=op.connect):
    row=c.execute('''
      SELECT w.id,w.lane,w.kind,w.state,
             r.uid,r.validity,e.evidence
      FROM work w JOIN events e ON e.id=w.event_id
      JOIN mail_refs r ON r.event_id=e.id
      WHERE w.id=?''',(work_id,)).fetchone()
    if not row:
        raise ValueError("unknown_or_not_mail_linked")
    if row["state"]=="BLOCKED":
        raise ValueError("blocked_work_not_actionable")
    client=connect()
    try:
        folder=op.all_mail(client)
        ok,_=client.select(folder,readonly=True)
        if ok!="OK":raise RuntimeError("select_failed")
        if str(op.response_number(client,"UIDVALIDITY"))!=str(row["validity"]):
            raise RuntimeError("uidvalidity_changed_relink_required")
        uid=str(row["uid"])
        ok,data=client.uid("fetch",uid,"(UID BODY.PEEK[HEADER])")
        heads=[x[1] for x in data or [] if isinstance(x,tuple) and isinstance(x[1],bytes)]
        if ok!="OK" or len(heads)!=1 or op.digest(heads[0])!=row["evidence"]:
            raise RuntimeError("header_evidence_mismatch_no_disclosure")
        ok,data=client.uid("fetch",uid,"(BODY.PEEK[])")
        full=[x[1] for x in data or [] if isinstance(x,tuple) and isinstance(x[1],bytes)]
        if ok!="OK" or len(full)!=1:
            raise RuntimeError("message_unavailable")
        msg=BytesParser(policy=policy.default).parsebytes(full[0])
        body=""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type()=="text/plain" and part.get_content_disposition()!="attachment":
                    body=str(part.get_content())[:1800]
                    break
        else:
            if msg.get_content_type()=="text/plain":
                body=str(msg.get_content())[:1800]
        return {"work_id":row["id"],"lane":row["lane"],"kind":row["kind"],
                "state":row["state"],"gmail_uid":row["uid"],
                "from":parseaddr(msg.get("From",""))[1],
                "subject":str(msg.get("Subject",""))[:250],
                "body_excerpt":body,
                "message_id":str(msg.get("Message-ID",""))[:350],
                "evidence":"private_gmail_header_digest_verified",
                "trusted_person":False,"purchase_or_job_accepted":False}
    finally:
        try:client.logout()
        except Exception:pass

def main():
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=("pending","inspect"))
    p.add_argument("--work-id")
    p.add_argument("--limit",type=int,default=30)
    p.add_argument("--reveal-private",action="store_true")
    args=p.parse_args()
    c=op.dbopen()
    try:
        if args.command=="pending":
            print(json.dumps({"work":pending(c,max(1,min(args.limit,100)))},sort_keys=True))
        else:
            if not args.work_id or not re.fullmatch("[a-f0-9]{64}",args.work_id):
                p.error("valid --work-id required")
            if not args.reveal_private:
                p.error("--reveal-private required; never pipe private output into public logs")
            print(json.dumps(inspect(c,args.work_id),sort_keys=True))
    finally:c.close()

if __name__=="__main__":
    main()
