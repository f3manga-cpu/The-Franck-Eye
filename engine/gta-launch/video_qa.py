#!/usr/bin/env python3
"""Fail-closed, read-only production gate for GTA vertical video."""
import json, subprocess, sys
from pathlib import Path
import shutil

def inspect(path):
    path=Path(path)
    exe=shutil.which("ffmpeg") or str(Path(__file__).parent/".venv"/"lib"/"python3.12"/"site-packages"/"imageio_ffmpeg"/"binaries"/"ffmpeg-linux-x86_64-v9.0.2")
    result=subprocess.run([exe,'-hide_banner','-i',str(path),'-f','null','-'],capture_output=True,text=True,timeout=120)
    info=result.stderr
    import re
    m=re.search(r'(\d{3,4})x(\d{3,4})',info)
    width,height=(int(m.group(1)),int(m.group(2))) if m else (0,0)
    audio=bool(re.search(r'Stream #\d+:\d+.*Audio:',info))
    checks={'exists':path.is_file() and path.stat().st_size>0,'decodes':result.returncode==0,'vertical_1080p':width>=1080 and height>=1920 and height>width,'audio_present':audio}
    return {'file':str(path),'width':width,'height':height,'audio':audio,'checks':checks,'technical_checks_passed':all(checks.values()),'creative_review_passed':False,'production_ready':False}

if __name__=='__main__':
    results=[inspect(p) for p in sys.argv[1:]]
    print(json.dumps(results,indent=2))
    sys.exit(0 if results and all(r['production_ready'] for r in results) else 1)
