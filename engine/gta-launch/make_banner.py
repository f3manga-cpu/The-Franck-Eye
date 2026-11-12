#!/usr/bin/env python3
"""Original 1500x500 coin-page brand banner: no videogame footage/assets."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math,random
random.seed(814)
W,H=1500,500
bg=Image.new('RGB',(W,H))
p=bg.load()
for y in range(H):
 for x in range(W):
  t=x/W;v=y/H
  p[x,y]=(int(4+8*t+7*v),int(14+11*t),int(29+17*v+6*t))
top=Image.new('RGBA',(W,H),(0,0,0,0))
d=ImageDraw.Draw(top)
for k in range(9):
 r=115+k*30
 d.arc((1030-r,250-r,1030+r,250+r),220,365,fill=(14,216,200,115-k*10),width=5)
 d.arc((1030-r,250-r,1030+r,250+r),17,138,fill=(255,139,73,100-k*10),width=4)
for i in range(35):
 x= i*48-10; ht= 45+((i*37)%138)
 d.rectangle((x,420-ht,x+35,450),fill=(5,16,30,255))
 for yy in range(425-ht,430,25):
  for xx in (x+8,x+23):
   if ((xx+yy)//3+i)%3:
    d.rectangle((xx,yy,xx+5,yy+8),fill=(34,165,166,130))
d.line((0,451,W,451),fill=(19,223,203,230),width=3)
for i in range(75):
 x=random.randrange(700,W-20); y=random.randrange(23,210);r=random.randrange(1,3)
 d.ellipse((x-r,y-r,x+r,y+r),fill=(67,181,187,150))
glow=top.filter(ImageFilter.GaussianBlur(17))
bg=Image.alpha_composite(bg.convert('RGBA'),glow)
bg=Image.alpha_composite(bg,top)
d=ImageDraw.Draw(bg)
lib='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
italic='/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf'
big=ImageFont.truetype(italic,111)
medium=ImageFont.truetype(lib,41)
tiny=ImageFont.truetype(lib,22)
d.rounded_rectangle((54,51,143,86),radius=6,fill=(235,90,69))
d.text((65,55),'LIVE',font=tiny,fill='#ffffff')
d.text((53,115),'GREATEST TOKEN',font=big,fill='#f9fbf6',stroke_width=4,stroke_fill='#061422')
d.text((56,240),'ACTION',font=big,fill='#ffad68',stroke_width=4,stroke_fill='#061422')
d.line((57,368,715,368),fill='#51e1d4',width=5)
d.text((56,390),'ORIGINAL FICTIONAL NEWSROOM',font=medium,fill='#cce6e7')
d.text((1010,406),'THE CITY IS ON AIR',font=tiny,fill='#e1edf0')
d.text((55,464),'INDEPENDENT CREATIVE PROJECT',font=tiny,fill='#99b7c4')
out=Path('/home/franck/mission-c-checkout/docs/gta-staging/banner.png')
out.parent.mkdir(parents=True,exist_ok=True)
bg.convert('RGB').save(out,optimize=True)
print('BANNER_GENERATED',out, bg.size, out.stat().st_size)
