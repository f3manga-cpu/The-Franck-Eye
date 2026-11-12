#!/usr/bin/env python3
"""Generate an original, silent 9-second 576x1024 faceless newsroom teaser."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parents[1]/"docs"/"gta"/"teaser.mp4"
W,H,FPS,DURATION=576,1024,12,9
FF="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(size,bold=True):
    return ImageFont.truetype(FF if bold else FR,size)

def centered(d,text,y,size,color,stroke=0):
    f=font(size)
    bounds=d.textbbox((0,0),text,font=f,stroke_width=stroke)
    d.text(((W-(bounds[2]-bounds[0]))/2,y),text,font=f,fill=color,
           stroke_width=stroke,stroke_fill=(2,13,23))

bg=Image.new("RGB",(W,H))
pix=bg.load()
for y in range(H):
  for x in range(W):
    edge=math.sqrt(((x-W*.52)/(W*.95))**2+((y-H*.47)/(H*.85))**2)
    glow=max(0,1-edge)
    pix[x,y]=(int(4+11*glow),int(13+29*glow),int(25+36*glow))
D=ImageDraw.Draw(bg)
# Independently authored skyline, no game screenshots/art.
buildings=[(0,820,55),(48,690,105),(93,735,164),(167,580,225),
 (229,690,279),(283,510,335),(339,630,390),(391,575,446),
 (449,690,515),(517,760,576)]
for x,top,end in buildings:
    D.rectangle((x,top,end,940),fill=(6,18,30))
    for xx in range(x+11,end,23):
        for yy in range(top+19,915,36):
            if ((xx*3+yy)//17)%5!=0:
                D.rectangle((xx,yy,xx+7,yy+12),fill=(11,64,76))
D.line((40,916,536,916),fill=(255,157,83),width=4)
D.line((41,923,535,923),fill=(36,174,189),width=2)
# Dark overlaid news ticker is constant.
D.rounded_rectangle((20,938,556,998),radius=12,fill=(3,15,24),outline=(29,173,187),width=2)
D.text((35,956),"GTA  //  INDEPENDENT FICTION",font=font(19),fill=(218,241,244))

def frame(i):
    t=i/FPS
    im=bg.copy()
    d=ImageDraw.Draw(im)
    for k in range(6):
        pos=int((i*9+k*156)%940)-182
        d.line((pos,-80,pos+290,850),fill=(7,86,105),width=2)
    d.rounded_rectangle((33,64,543,112),radius=7,fill=(5,37,52),outline=(76,212,207),width=2)
    d.text((50,76),"GTA / LIVE FICTION DESK",font=font(20),fill=(204,237,239))
    idx=min(int(t//2.25),3)
    fade=min(1,(t%2.25)/.35,(2.25-t%2.25)/.35)
    col=(int(235*fade),int(243*fade),int(232*fade))
    accent=(int(255*fade),int(162*fade),int(80*fade))
    cyan=(int(111*fade),int(224*fade),int(224*fade))
    if idx==0:
        centered(d,"SIGNAL",300,81,cyan)
        centered(d,"DETECTED",404,67,col)
        centered(d,"001",538,93,accent)
    elif idx==1:
        centered(d,"GREATEST",283,56,col)
        centered(d,"TOKEN",382,81,cyan)
        centered(d,"ACTION",495,76,accent)
    elif idx==2:
        centered(d,"MEET",290,67,col)
        centered(d,"ARCH",392,89,cyan)
        centered(d,"& SABLE",515,65,accent)
        centered(d,"FICTIONAL NEWSROOM",620,26,col)
    else:
        centered(d,"THE",310,68,col)
        centered(d,"SWITCH",410,82,cyan)
        centered(d,"IS ON",540,78,accent)
    centered(d,"NO TOKEN IS LIVE",839,22,(178,207,213))
    return im

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    writer=imageio_ffmpeg.write_frames(
        str(OUT), (W,H), fps=FPS, codec="libx264",
        output_params=["-pix_fmt","yuv420p","-crf","28","-preset","ultrafast","-movflags","+faststart"],
        ffmpeg_log_level="error")
    writer.send(None)
    try:
        for i in range(FPS*DURATION):
            writer.send(frame(i).tobytes())
    finally:
        writer.close()
    print(str(OUT),OUT.stat().st_size,"bytes",FPS*DURATION,"frames")

if __name__=="__main__": main()
