from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

XML_URL="https://ladderslasher.d2jsp.org/xmlChar.php?i=473341"
ROOT=Path(__file__).resolve().parent
BG=ROOT/"assets/signature_background.png"
OUT=ROOT/"signature.png"

def fetch():
    req=Request(XML_URL,headers={"User-Agent":"d2jsp-friend-signature/1.0"})
    with urlopen(req,timeout=20) as r:return r.read()

def parse(raw):
    out={}
    for e in (raw or "").split(";"):
        p=e.split(",")
        if len(p)>=2:
            try: out[int(p[0])]={"rank":int(p[1]),"progress":int(p[2]) if len(p)>=3 else 0}
            except: pass
    return out

def req(rank): return (rank+1)*1000
def pct(x): return max(0,min((x["progress"]/req(x["rank"]))*100,100)) if req(x["rank"]) else 0
def prof(d,i): return d.get(i,{"rank":0,"progress":0})
def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]:
        if Path(p).exists(): return ImageFont.truetype(p,sz)
    return ImageFont.load_default()
def center(draw,cx,y,t,f,fill,sw=0):
    b=draw.textbbox((0,0),t,font=f,stroke_width=sw); w=b[2]-b[0]
    draw.text((cx-w//2,y),t,font=f,fill=fill,stroke_width=sw,stroke_fill=(0,0,0,255))

x=ET.fromstring(fetch())
w=parse(x.findtext("wprof","")); s=parse(x.findtext("sprof",""))
items=[("DAGGER",prof(w,3)),("AXE",prof(w,2)),("SWORD",prof(w,0)),("TRANSMUTING",prof(s,3))]
name=x.findtext("name","Ladder Slasher")
level=x.findtext("level","?")
core="Original" if x.findtext("core","0")=="0" else "Hardcore"

img=Image.open(BG).convert("RGBA").resize((400,150),Image.Resampling.LANCZOS)
dr=ImageDraw.Draw(img)
center(dr,210,10,name,font(18),(255,220,0,255),2)
center(dr,210,31,f"Level {level} | Core: {core}",font(8),(255,255,255,255),1)
for cx,(label,p) in zip([122,181,239,299],items):
    center(dr,cx,59,label,font(8),(255,255,255,255),1)
    center(dr,cx,118,str(p["rank"]),font(11),(255,220,0,255),2)
    center(dr,cx,134,f"{pct(p):.1f}%",font(7),(255,255,255,255),1)
img.convert("RGB").save(OUT,"PNG",optimize=True)
