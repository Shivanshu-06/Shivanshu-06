#!/usr/bin/env python3
"""Capture public site screenshots and draw an original cozy pixel-art animation."""
from pathlib import Path
import math
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "cozy"
OUT.mkdir(parents=True, exist_ok=True)

SITES = {
    "pce-controls": "https://www.pce-ei.de/",
    "pce-energy": "https://www.pce-es.de/de/",
    "data-know-how": "https://data-know-how.de/",
}

def screenshots():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        for name, url in SITES.items():
            page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1, locale="en-US", reduced_motion="reduce")
            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                if not response or response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status if response else 'no response'}")
                page.wait_for_timeout(2200)
                page.screenshot(path=str(OUT / f"{name}.png"), full_page=False, animations="disabled")
                # Use a fixed-size crop for identical card aspect ratios on GitHub.
                with Image.open(OUT / f"{name}.png") as shot:
                    shot = shot.convert("RGB")
                    target_ratio = 4 / 3
                    w, h = shot.size
                    crop_h = min(h, round(w / target_ratio))
                    crop_w = min(w, round(crop_h * target_ratio))
                    shot = shot.crop((0, 0, crop_w, crop_h))
                    shot = shot.resize((640, 480), Image.Resampling.LANCZOS)
                    shot.save(OUT / f"{name}-card.png", optimize=True)
                print(f"Captured {name}: {page.url}")
            except Exception as exc:
                print(f"WARNING: screenshot failed for {name}: {exc}")
            finally:
                page.close()
        browser.close()

def pixel(draw, x, y, w, h, color, scale=4):
    draw.rectangle((x*scale, y*scale, (x+w)*scale-1, (y+h)*scale-1), fill=color)

def cozy_gif():
    """Looping original isometric pixel-art robot exploring a tiny futuristic workspace."""
    frames=[]
    W,H=720,288
    for t in range(36):
        im=Image.new("RGB",(W,H),"#111C29")
        d=ImageDraw.Draw(im)
        # Calm midnight-blue backdrop with a precise dot grid.
        for yy in range(14,H,24):
            for xx in range(14,W,24):
                d.ellipse((xx,yy,xx+2,yy+2),fill="#293C4A")
        # Floating hexagonal platform.
        d.polygon([(146,199),(350,104),(570,198),(366,286)],fill="#365B62")
        d.polygon([(146,199),(366,286),(366,271),(146,184)],fill="#243D4B")
        d.polygon([(366,286),(570,198),(570,183),(366,271)],fill="#1C3440")
        d.polygon([(146,184),(350,89),(570,183),(366,271)],fill="#527D79")
        for k in range(7):
            x=190+k*49
            y=181-abs(k-3)*12
            d.line((x,y,x+95,y+40),fill="#618E88",width=2)
        # Tiny monitor, desk and terminal lights on the platform.
        d.polygon([(352,143),(423,111),(487,140),(417,172)],fill="#2B444F")
        d.polygon([(352,143),(417,172),(417,182),(352,153)],fill="#182B38")
        d.polygon([(417,172),(487,140),(487,150),(417,182)],fill="#1A3440")
        d.polygon([(366,106),(430,76),(474,97),(409,127)],fill="#7AB9B2")
        d.polygon([(374,106),(430,81),(465,98),(410,122)],fill="#152936")
        for j in range(4):
            d.line((397,101+j*5,430+(j*7)%18,86+j*5),fill="#90DCC8" if j%2 else "#E4B68F",width=2)
        d.line((410,127,417,172),fill="#9AB4A5",width=5)
        # Isometric walking robot with animated steps and antenna.
        hop=round(4*math.sin(t*math.pi/9))
        x=269+round(32*math.sin(t*math.pi/18))
        y=155+hop
        d.ellipse((x-37,205,x+53,221),fill="#314C53")
        leg=round(8*math.sin(t*math.pi/6))
        d.line((x-9,y+51,x-19-leg,y+69),fill="#9EB6AE",width=8)
        d.line((x+23,y+50,x+28+leg,y+69),fill="#9EB6AE",width=8)
        d.ellipse((x-32-leg,y+65,x-6-leg,y+74),fill="#D9D6BC")
        d.ellipse((x+15+leg,y+65,x+43+leg,y+74),fill="#D9D6BC")
        d.rounded_rectangle((x-24,y+13,x+43,y+56),radius=12,fill="#D8E4D8",outline="#8BBDB5",width=3)
        d.rounded_rectangle((x-32,y-35,x+52,y+25),radius=17,fill="#E5E9DC",outline="#94BEB4",width=4)
        d.rounded_rectangle((x-23,y-23,x+43,y+10),radius=11,fill="#233D4B")
        if t%18 in (9,10):
            for ex in (x-4,x+24):
                d.line((ex-6,y-5,ex+6,y-5),fill="#9AE6CE",width=3)
        else:
            for ex in (x-4,x+24):
                d.ellipse((ex-5,y-10,ex+5,y),fill="#A0F3D8")
        d.line((x+10,y-35,x+10,y-48),fill="#D7E0D3",width=4)
        d.ellipse((x+5,y-56,x+15,y-46),fill="#F3C58F")
        # Gentle holographic orbiting data particles.
        for k in range(8):
            angle=(t/36+k/8)*2*math.pi
            px=355+round(122*math.cos(angle))
            py=159+round(41*math.sin(angle))
            d.ellipse((px-3,py-3,px+3,py+3),fill="#9BE8D2" if k%2 else "#F1BF9C")
        # A pulsing drone on the right, above the platform.
        dy=round(6*math.sin(t*math.pi/18))
        d.ellipse((527,104+dy,576,115+dy),fill="#1D303D")
        d.rounded_rectangle((529,90+dy,574,108+dy),radius=8,fill="#D7A99A",outline="#F1D1B8",width=2)
        d.ellipse((548,95+dy,556,103+dy),fill="#A6F2DE")
        d.line((536,87+dy,565,87+dy),fill="#A5D9CF",width=3)
        frames.append(im)
    frames[0].save(OUT/"robot-diorama.gif",save_all=True,append_images=frames[1:],duration=90,loop=0,optimize=True)
    print("Created original isometric robot workspace animation")

if __name__=="__main__":
    cozy_gif()
    screenshots()
