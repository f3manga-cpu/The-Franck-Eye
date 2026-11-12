#!/usr/bin/env python3
"""Generate an original silent 9:16 GTA fictional-news teaser; no borrowed game IP."""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
import math, subprocess
import imageio_ffmpeg
W,H=540,960
fps=12
secs=11
root=Path(__file__).resolve().parent
dest=root.parents[1]/'docs'/'gta'/'broadcast-001.mp4'
dest.parent.mkdir(parents=True,exist_ok=True)
font_bold='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
font_italic='/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf'
slides=[
 ('THE SIGNAL','IS LIVE','ORIGINAL NEWS / FICTION',0,2.1),
 ('ARCH','AT THE DESK','THE FICTIONAL ANCHOR',2.1,4.1),
 ('SABLE','ON THE GROUND','THE FICTIONAL FIELD REPORTER',4.1,6.1),
 ('NEW STORIES.','NEW SCENES.','AN ORIGINAL WORLD IN MOTION',6.1,8.1),
 ("DON'T JUST","WATCH. ACT.","GREATEST TOKEN ACTION",8.1,11),
]
bg=Image.new('RGB',(W,H))
p=bg.load()
for y in range(H):
 for x in range(W):
  p[x,y]=(int(4+(x/W)*8+(y/H)*9),int(16+(1-y/H)*18),int(32+(x/W)*14))
D=ImageDraw.Draw(bg)
# Original abstract city and neon signal graphics.
for i in range(17):
 x=i*36+(i%3)*2; h=110+(i*71)%220
 D.rectangle((x,725-h,x+33,740),fill=(5,19,36))
 for yy in range(739-h,721,24):
  if (i+yy//24)%3:
   D.rectangle((x+8,yy,x+13,yy+11),fill=(35,118,131))
D.line((0,742,W,742),fill=(22,208,191),width=3)
base=bg
big=ImageFont.truetype(font_italic,69)
mid=ImageFont.truetype(font_bold,25)
small=ImageFont.truetype(font_bold,16)
logo=Image.open(root/'assets'/'logo.png').convert('RGBA').resize((235,235),Image.Resampling.LANCZOS)

def center(d,text,font,y,color,stroke=0):
 b=d.textbbox((0,0),text,font=font,stroke_width=stroke)
 d.text(((W-(b[2]-b[0]))/2,y),text,font=font,fill=color,stroke_width=stroke,stroke_fill='#020a10')

def make_frame(i):
 t=i/fps
 s=next((a for a in slides if a[3]<=t<a[4]),slides[-1])
 im=base.copy()
 d=ImageDraw.Draw(im)
 # active moving signal stripes
 dx=int((t*83)%W)
 d.line((dx-160,160,dx+65,160),fill=(27,218,201),width=5)
 d.line((W-dx-80,195,W-dx+80,195),fill=(255,158,82),width=3)
 # subtle frame edges and top-left indicator
 d.rounded_rectangle((18,22,W-18,H-20),radius=15,outline=(37,113,126),width=2)
 d.rounded_rectangle((32,41,148,74),radius=6,fill=(231,85,65))
 d.text((46,47),'ON AIR',font=small,fill='white')
 d.text((W-160,48),'SIGNAL 001',font=small,fill=(87,234,223))
 im.paste(logo,(W//2-117,205),logo)
 d=ImageDraw.Draw(im)
 # spring-like text entrance, restrained motion, dark separator
 local=t-s[3]
 offset=round(14*math.exp(-3*local))
 d.rounded_rectangle((45,494,W-45,675),radius=10,fill=(4,17,29),outline=(21,206,202),width=3)
 center(d,s[0],big,508+offset,(250,249,231),3)
 center(d,s[1],big,580+offset,(255,155,86),3)
 center(d,s[2],mid,699,(180,224,234))
 d.line((65,788,W-65,788),fill=(22,204,205),width=2)
 d.text((42,805),'FICTIONAL INDEPENDENT NEWSROOM',font=small,fill=(225,234,236))
 d.text((42,838),'NO LIVE TOKEN  /  NO GAME AFFILIATION',font=small,fill=(255,164,107))
 d.text((42,870),'GREATEST TOKEN ACTION  •  SIGNAL ACTIVE',font=small,fill=(177,208,218))
 return im
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(fps),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-preset','veryfast','-crf','26','-movflags','+faststart',str(dest)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
try:
 for i in range(fps*secs):
  frame=make_frame(i)
  proc.stdin.write(frame.tobytes())
 proc.stdin.close()
 err=proc.stderr.read().decode()
 ret=proc.wait()
 if ret: raise RuntimeError(f'video encoding failed: {err[-2000:]}')
except Exception:
 proc.kill()
 raise
print(f'VIDEO_CREATED {dest} {dest.stat().st_size} bytes {secs}s {W}x{H} {fps}fps silent')
