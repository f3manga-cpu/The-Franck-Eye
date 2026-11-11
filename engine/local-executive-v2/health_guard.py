#!/usr/bin/env python3
"""Resource-light health watchdog. Checks liveness, never counts work as outcomes."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parent
PVT=ROOT/"executive_v2_private"
STATE=PVT/"watchdog_state.json"
STATUS=PVT/"watchdog_health.json"
TARGETS={
 "outcome-executive-v2.service": PVT/"heartbeat.json",
 "outcome-operator.service": ROOT/"health.json",
}
RESTART_INTERVAL_SECONDS=3600
MAX_RESTARTS_PER_INTERVAL=2
STALE_AFTER_SECONDS=900

def timestamp(value):
    if isinstance(value,(int,float)):
        return float(value)
    if not isinstance(value,str):return None
    try:return datetime.fromisoformat(value.replace("Z","+00:00")).timestamp()
    except (ValueError,OverflowError,TypeError):return None

def load(path,default):
    try:
        d=json.loads(Path(path).read_text())
        return d if isinstance(d,dict) else default
    except (OSError,ValueError):return default

def atomic(path,record):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(path.parent,0o700)
    fd,tmp=tempfile.mkstemp(prefix=".health-",dir=path.parent)
    try:
        with os.fdopen(fd,"w") as f:
            json.dump(record,f,sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def systemctl(*args):
    p=subprocess.run(["systemctl","--user",*args],capture_output=True,text=True,timeout=18)
    return p.returncode, (p.stdout or "").strip()[:60]

def cycle(now=None,runner=systemctl,targets=TARGETS,state_path=STATE,status_path=STATUS):
    now=time.time() if now is None else now
    state=load(state_path,{"restarts":{}})
    restarts=state.get("restarts",{}) if isinstance(state.get("restarts"),dict) else {}
    results={}
    for name,path in targets.items():
        rc,active=runner("is-active",name)
        record=load(path,{})
        tick=timestamp(record.get("last_cycle") or record.get("at"))
        recent=[t for t in restarts.get(name,[]) if isinstance(t,(float,int)) and 0<=now-t<RESTART_INTERVAL_SECONDS]
        restarts[name]=recent
        age=None if tick is None else max(0,int(now-tick))
        outcome_status=record.get("status","UNKNOWN")
        reason=("inactive" if rc or active!="active" else
                "missing_heartbeat" if tick is None else
                "stale_heartbeat" if age>STALE_AFTER_SECONDS else
                "active")
        result={"process":active,"heartbeat_age_seconds":age,
                "reported_outcome_status":outcome_status,
                "liveness":reason,"restart":"none"}
        if reason!="active":
            if len(recent)>=MAX_RESTARTS_PER_INTERVAL:
                result["restart"]="rate_limit_exhausted"
            else:
                code,_=runner("restart",name)
                result["restart"]="attempted" if code==0 else "failed"
                recent.append(now)
        results[name]=result
    state["restarts"]=restarts
    state["checked_at"]=now
    snapshot={"checked_at":now,"services":results,
              "healthy":all(x["liveness"]=="active" for x in results.values()),
              "financial_outcome":"UNKNOWN_NOT_BANK_VERIFIED",
              "employment_outcome":"UNKNOWN_NOT_ACCEPTED_WORK"}
    atomic(state_path,state)
    atomic(status_path,snapshot)
    return snapshot

def main():
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=("once","status"),nargs="?",default="once")
    a=p.parse_args()
    if a.command=="status":
        print(json.dumps(load(STATUS,{"status":"unknown"}),sort_keys=True))
        return 0
    result=cycle()
    print(json.dumps(result,sort_keys=True))
    return 0 if result["healthy"] else 1

if __name__=="__main__":
    raise SystemExit(main())
