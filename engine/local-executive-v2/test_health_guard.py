import json
from pathlib import Path
import tempfile
import unittest
import health_guard as g

class GuardTests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
  self.root=Path(t.name);self.a=self.root/"service-heartbeat.json"
  self.state=self.root/"state.json";self.status=self.root/"status.json"
  self.target={"example.service":self.a}
  self.calls=[]
 def runner(self,*args):
  self.calls.append(args)
  if args[0]=="is-active":return (0,"active")
  return (0,"")
 def cycle(self,t):
  return g.cycle(now=t,runner=self.runner,targets=self.target,state_path=self.state,status_path=self.status)
 def test_active_no_restart(self):
  self.a.write_text(json.dumps({"at":100,"status":"STALLED"}))
  r=self.cycle(110)
  self.assertTrue(r["healthy"]);self.assertEqual(len(self.calls),1)
  self.assertEqual(r["services"]["example.service"]["reported_outcome_status"],"STALLED")
  self.assertEqual(r["financial_outcome"],"UNKNOWN_NOT_BANK_VERIFIED")
 def test_stale_restart_rate_limit(self):
  self.a.write_text(json.dumps({"at":100}))
  self.cycle(2000);self.cycle(2001);r=self.cycle(2002)
  self.assertEqual([x for x in self.calls if x[0]=="restart"],[("restart","example.service")]*2)
  self.assertEqual(r["services"]["example.service"]["restart"],"rate_limit_exhausted")
 def test_missing_heartbeat_restart(self):
  r=self.cycle(100)
  self.assertFalse(r["healthy"]);self.assertEqual(r["services"]["example.service"]["liveness"],"missing_heartbeat")
 def test_recent_progress_but_no_money_not_success(self):
  self.a.write_text(json.dumps({"last_cycle":"2026-11-11T01:00:00+00:00","external_actions":0}))
  time=g.timestamp("2026-11-11T01:03:00+00:00")
  r=self.cycle(time)
  self.assertTrue(r["healthy"]);self.assertEqual(r["financial_outcome"],"UNKNOWN_NOT_BANK_VERIFIED")
 def test_persistent_history(self):
  self.a.write_text(json.dumps({"at":1}))
  self.cycle(10000)
  self.assertEqual(len(g.load(self.state,{}).get("restarts",{}).get("example.service",[])),1)
  self.assertEqual(self.status.stat().st_mode & 0o777,0o600)

if __name__=="__main__":unittest.main()
