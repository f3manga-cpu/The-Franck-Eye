import json
from email.message import EmailMessage
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import executive_v2 as op
import review_task as review

def fixture():
    m=EmailMessage()
    m["From"]="buyer@example.org"
    m["Subject"]="Re: Mission Data Analyst — devis"
    m["Message-ID"]="<fixture-1@example.org>"
    m.set_content("Please confirm the work scope.")
    raw=m.as_bytes()
    head=m.as_bytes().split(b"\n\n",1)[0]+b"\n\n"
    return raw,head

class MailFake:
    def __init__(self,raw,head,validity=1):
        self.raw,self.head,self.validity=raw,head,validity
        self.closed=False
    def list(self):return "OK",[b'(\\All) "/" "[Gmail]/Tous les messages"']
    def select(self,name,readonly=False):
        assert readonly
        return "OK",[b"1"]
    def response(self,name):return name,[str(self.validity).encode()]
    def uid(self,opname,*args):
        assert opname=="fetch"
        if args[-1]=="(UID BODY.PEEK[HEADER])":
            return "OK",[(b"1 (UID 5 BODY[HEADER]",self.head)]
        if args[-1]=="(BODY.PEEK[])":
            return "OK",[(b"1 (UID 5 BODY[]",self.raw)]
        raise AssertionError("unrecognized")
    def logout(self):self.closed=True

class ReviewTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.c=op.dbopen(Path(t.name)/"state.sqlite3");self.addCleanup(self.c.close)
        self.raw,self.head=fixture()
        self.fingerprint=op.digest("gmail-header:"+op.digest(self.head))
        self.id=op.stage(self.c,self.fingerprint,op.digest(self.head),"commercial_correspondence")
        event=op.digest("event:"+self.fingerprint)
        self.c.execute("INSERT INTO mail_refs VALUES(?,?,?,?)",(event,op.digest("folder"),"1",5))
    def test_pending_contains_only_private_locator(self):
        q=review.pending(self.c)
        self.assertEqual(len(q),1)
        self.assertEqual(q[0]["uid"],5)
        self.assertNotIn("buyer@",json.dumps(q))
        self.assertEqual(q[0]["lane"],"MONEY")
    def test_verified_header_allows_private_lookup_not_external_action(self):
        fake=MailFake(self.raw,self.head)
        data=review.inspect(self.c,self.id,connect=lambda:fake)
        self.assertTrue(fake.closed)
        self.assertEqual(data["from"],"buyer@example.org")
        self.assertEqual(data["purchase_or_job_accepted"],False)
        self.assertEqual(data["trusted_person"],False)
    def test_uidvalidity_change_refuses_lookup(self):
        fake=MailFake(self.raw,self.head,2)
        with self.assertRaises(RuntimeError): review.inspect(self.c,self.id,connect=lambda:fake)
        self.assertTrue(fake.closed)
    def test_header_changed_refuses_lookup(self):
        fake=MailFake(self.raw,b"From: unknown@example.org\n\n")
        with self.assertRaises(RuntimeError): review.inspect(self.c,self.id,connect=lambda:fake)
        self.assertTrue(fake.closed)
    def test_blocked_row_cannot_reveal(self):
        self.c.execute("UPDATE work SET state='BLOCKED' WHERE id=?",(self.id,))
        with self.assertRaises(ValueError):review.inspect(self.c,self.id,connect=lambda:None)

if __name__=="__main__":unittest.main()
