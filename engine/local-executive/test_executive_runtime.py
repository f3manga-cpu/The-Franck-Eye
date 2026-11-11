#!/usr/bin/env python3
import email
from email.message import EmailMessage
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock
import executive_runtime as x

def mail(sender="buyer@example.org", subject="Re: Mission Data Analyst Webanalytics — renfort ponctuel KPI", body="Bonjour, je suis intéressé, pouvons-nous en discuter ?", ref="<prior@domain>"):
    m=EmailMessage()
    m["From"]=sender
    m["Subject"]=subject
    m["In-Reply-To"]=ref
    m["Message-ID"]="<incoming-1@example.org>"
    m.set_content(body)
    return m

RULES=[{"scope":"existing_engaged_b2b","enabled":True,"email":"buyer@example.org","subject_key":"Mission Data Analyst","message_id":"<prior@domain>"}]

class ExecutiveTests(unittest.TestCase):
    def setUp(self):
        self.dir=tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.c=x.dbopen(Path(self.dir.name)/"ledger.sqlite3")
        self.addCleanup(self.c.close)

    def test_positive_known_reply_qualifies(self):
        r=x.allowed_inbound(mail(),RULES)
        self.assertEqual(r["kind"],"qualified_reply")

    def test_negative_reply_not_sent(self):
        r=x.allowed_inbound(mail(body="Sorry, not interested; we hired someone else"),RULES)
        self.assertEqual(r["kind"],"classified_only")

    def test_not_trusted_sender_cannot_send(self):
        self.assertIsNone(x.allowed_inbound(mail(sender="attacker@example.org"),RULES))

    def test_missing_proven_thread_cannot_send(self):
        self.assertIsNone(x.allowed_inbound(mail(ref="<other@domain>"),RULES))

    def test_no_repeat_inbound_event(self):
        v=x.allowed_inbound(mail(),RULES)
        v["fingerprint"]="unique"
        with mock.patch.object(x,"send_qualified_reply",return_value="smtp_accepted") as sender:
            self.assertEqual(x.message_event(self.c,v,live=True),"smtp_accepted")
            self.assertEqual(x.message_event(self.c,v,live=True),"already_seen")
            sender.assert_called_once()

    def test_reserve_side_effect_is_atomic(self):
        self.assertTrue(x.reserve(self.c,"delivery-a","reply"))
        self.assertFalse(x.reserve(self.c,"delivery-a","reply"))

    def test_mock_cycle_records_health_not_sales(self):
        with mock.patch.object(x,"HEALTH",Path(self.dir.name)/"health.json"),\
             mock.patch.object(x,"job_sender",return_value="disabled"),\
             mock.patch.object(x,"codex_strategy",return_value="disabled"):
            result=x.cycle(self.c,scanner=lambda:(1,[]))
        self.assertEqual(result["inbox_checked"],1)
        self.assertEqual(result["qualified_replies_smtp_accepted"],0)
        self.assertEqual(result["bank_cash"],"UNKNOWN")
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM cycles").fetchone()[0],1)

    def test_forbidden_auto_send_to_negative(self):
        r=x.allowed_inbound(mail(body="Please stop contacting us"),RULES)
        self.assertEqual(r["kind"],"classified_only")

    def test_smtp_reply_is_real_idempotent_side_effect(self):
        class FakeSMTP:
            def __init__(self):self.messages=[]
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def login(self,*args):pass
            def send_message(self,msg):
                self.messages.append(msg)
                return {}
        fake=FakeSMTP()
        item=x.allowed_inbound(mail(),RULES)
        item["fingerprint"]="known_msg_digest"
        with mock.patch.object(x,"credentials",return_value=("owner@example.org","valid-app-password")),\
             mock.patch.object(x.smtplib,"SMTP_SSL",return_value=fake):
            self.assertEqual(x.send_qualified_reply(self.c,item,live=True),"smtp_accepted")
            self.assertEqual(x.send_qualified_reply(self.c,item,live=True),"duplicate_suppressed")
        self.assertEqual(len(fake.messages),1)
        self.assertEqual(fake.messages[0]["To"],"buyer@example.org")
        self.assertNotIn("advance payment",fake.messages[0].get_content().lower())
        self.assertEqual(self.c.execute("SELECT state FROM actions WHERE id=?",("reply:known_msg_digest",)).fetchone()[0],"SMTP_ACCEPTED")

    def test_no_unauthorized_job_sender(self):
        self.assertEqual(x.job_sender(self.c,False),"disabled")

if __name__ == "__main__":
    unittest.main()
