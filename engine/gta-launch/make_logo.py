#!/usr/bin/env python3
"""Original Greatest Token Action logo artwork, drawn locally without outside IP."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math
S=1024
I=Image.new('RGB',(S,S))
p=I.load()
for y in range(S):
  for x in range(S):
    z=y/S
    p[x,y]=(int(5+18*z),int(13+16*z),int(29+25*z))
d=ImageDraw.Draw(I,'RGBA')
# Abstract original energy arcs and warm sunset, not a video-game logo recreation.
cx,cy=512,485
for r in range(380,145,-3):
  k=(r-145)/235
  d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(7,int(172+72*(1-k)),int(210+45*(1-k)),int(140*(1-k))+40),width=4)
d.ellipse((220,170,804,754),fill=(205,58,94,185))
d.ellipse((260,210,764,714),fill=(246,139,72,210))
for y in range(330,720,26):
  w=math.sqrt(max(0,1-((y-465)/310)**2))*250
  d.line((512-w,y,512+w,y),fill=(16,27,50,112),width=5)
# Urban skyline silhouettes, wholly original.
heights=[190,250,340,305,440,385,485,420,305,380,255,185]
for i,h in enumerate(heights):
  x=80+i*74
  d.rectangle((x,760-h,x+58,805),fill=(10,19,38,255))
  for yy in range(800-h,785,29):
    for xx in (x+15,x+38):
      d.rectangle((xx,yy,xx+8,yy+13),fill=(26,195,205,185))
# energetic slash
d.polygon([(130,705),(675,650),(910,745),(380,800)],fill=(4,13,27,242))
font='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
font2='/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf'
f=ImageFont.truetype(font2,285)
b=d.textbbox((0,0),'GTA',font=f,stroke_width=11)
x=(S-(b[2]-b[0]))//2
d.text((x,435),'GTA',font=f,fill=(251,250,229,255),stroke_width=11,stroke_fill=(4,16,31,255))
d.line((180,757,850,690),fill=(249,116,36,255),width=18)
small=ImageFont.truetype(font,59)
text='GREATEST TOKEN ACTION'
bb=d.textbbox((0,0),text,font=small)
if bb[2]-bb[0] > 885:
  small=ImageFont.truetype(font,50)
bb=d.textbbox((0,0),text,font=small)
d.rounded_rectangle((49,816,975,920),radius=25,fill=(3,13,30,245),outline=(18,208,209,255),width=5)
d.text(((S-(bb[2]-bb[0]))/2,835),text,font=small,fill=(243,245,240,255))
# vignette outline
d.ellipse((34,34,990,990),outline=(14,236,218,255),width=19)
d.ellipse((51,51,973,973),outline=(252,125,30,255),width=8)
dest=Path(__file__).parent/'assets'/'logo.png'
dest.parent.mkdir(parents=True,exist_ok=True)
I.resize((512,512),Image.Resampling.LANCZOS).save(dest,optimize=True)
print(dest, dest.stat().st_size, 'bytes')
