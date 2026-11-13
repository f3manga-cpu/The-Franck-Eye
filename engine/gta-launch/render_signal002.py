from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import subprocess, json, wave
base=Path('/home/franck/mission-c-checkout/engine/gta-launch')
out=base/'production_private'
out.mkdir(exist_ok=True)
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
slides=[
('GTA / SIGNAL 002','A CITY BUILT\nBY ATTENTION','FICTIONAL FIELD REPORT'),
('SABLE / FIELD DESK','ANYONE CAN BUILD\nA BILLBOARD.','NOT EVERYONE CAN MAKE SOMEONE STOP.'),
('ARCH / NEWSROOM','NO INVENTED\nAUDIENCE.','REAL READERS. REAL RESPONSES.'),
('GREATEST TOKEN ACTION','THE CITY IS\nIMAGINARY.','THE WORK IS REAL. NO LIVE TOKEN.')
]
for i,(eyebrow,headline,footer) in enumerate(slides):
 im=Image.new('RGB',(1080,1920),(9,17,31))
 d=ImageDraw.Draw(im)
 for y in range(1920):
  d.line((0,y,1080,y),fill=(9+int(y/1920*9),17+int(y/1920*9),31+int(y/1920*14)))
 for x in range(0,1080,90):
  d.line((x,0,x,1920),fill=(24,37,51),width=1)
 for y in range(0,1920,90):
  d.line((0,y,1080,y),fill=(24,37,51),width=1)
 d.rectangle((65,160,1015,171),fill=(12,218,204))
 d.text((68,230),eyebrow,font=ImageFont.truetype(bold,47),fill=(12,218,204))
 font=ImageFont.truetype(bold,82)
 for k,line in enumerate(headline.split('\n')):
  d.text((65,650+k*120),line,font=font,fill=(241,245,249))
 d.rectangle((65,1260,1015,1266),fill=(12,218,204))
 d.text((65,1315),footer,font=ImageFont.truetype(regular,32),fill=(228,233,238))
 d.text((65,1750),'INDEPENDENT FICTION / NOT AFFILIATED WITH ANY GAME',font=ImageFont.truetype(regular,22),fill=(170,180,195))
 im.save(out/f'slide{i}.png',optimize=True)
narration='Signal zero zero two. A city built by attention. Sable reporting. Anyone can build a billboard. Not everyone can make someone stop. We count real readers, not invented audiences. Greatest Token Action. The city is imaginary. The work is real. No live token.'
subprocess.run(['espeak','-s','135','-w',str(out/'voice.wav'),narration],check=True)
ff=base/'.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2'
concat=out/'slides.txt'
concat.write_text(''.join(f"file '{out}/slide{i}.png'\nduration 5\n" for i in range(4))+f"file '{out}/slide3.png'\n")
cmd=[str(ff),'-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-i',str(out/'voice.wav'),'-vf','fps=12,format=yuv420p','-c:v','libx264','-preset','ultrafast','-crf','26','-c:a','aac','-b:a','96k','-t','20','-movflags','+faststart',str(out/'signal-002-review.mp4')]
print('RENDER_START',flush=True)
subprocess.run(cmd,check=True,timeout=180)
print('RENDER_DONE', (out/'signal-002-review.mp4').stat().st_size,flush=True)
