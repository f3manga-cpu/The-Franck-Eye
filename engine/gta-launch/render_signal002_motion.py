"""Motion-study version of SIGNAL 002. Original slides and narration only; no external assets."""
from pathlib import Path
import subprocess, shutil
base=Path(__file__).resolve().parent
p=base/'production_private'
ff=shutil.which('ffmpeg') or str(base/'.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2')
for i in range(4):
    assert (p/f'slide{i}.png').is_file()
assert (p/'voice.wav').is_file()
inputs=[]
for i in range(4): inputs+=['-loop','1','-t','5','-i',str(p/f'slide{i}.png')]
inputs+=['-i',str(p/'voice.wav')]
# A subtle continuous camera push replaces hard-cut still cards; each segment moves independently.
filters=[]
for i in range(4):
    filters.append(f'[{i}:v]scale=1160:2064,crop=1080:1920:x=40+20*sin(t*0.5):y=72+25*sin(t*0.35),fps=12,setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v{i}]')
filters.append(''.join(f'[v{i}]' for i in range(4))+'concat=n=4:v=1:a=0[v]')
cmd=[ff,'-y','-hide_banner','-loglevel','error',*inputs,'-filter_complex',';'.join(filters),'-map','[v]','-map','4:a','-c:v','libx264','-preset','ultrafast','-crf','25','-c:a','aac','-b:a','128k','-t','20','-movflags','+faststart',str(p/'signal-002-motion-review.mp4')]
subprocess.run(cmd,check=True,timeout=180)
print('RENDERED', (p/'signal-002-motion-review.mp4').stat().st_size)
