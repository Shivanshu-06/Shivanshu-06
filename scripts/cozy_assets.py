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
    """Original looping pixel-art arcade racer through a neon synthwave city."""
    frames = []
    W, H = 720, 288
    for t in range(36):
        im = Image.new("RGB", (W, H), "#101429")
        d = ImageDraw.Draw(im)
        # Deep violet-to-indigo sky.
        for y in range(188):
            p = y / 188
            d.line((0,y,W,y),fill=(int(17+53*p),int(19+12*p),int(45+47*p)))
        # Sunset disk with distinctive retro scanlines.
        d.ellipse((277,24,445,192),fill="#FFB17B")
        for yy in range(118,190,12):
            d.rectangle((276,yy,447,yy+3+(yy-118)//15),fill="#432453")
        # Layered skyline with glowing windows.
        for i in range(27):
            x=i*30-10
            h=32+(i*37)%76
            d.rectangle((x,188-h,x+26,190),fill="#272643")
            for yy in range(188-h+9,185,14):
                for xx in range(x+6,x+23,10):
                    if (xx+yy+i)%4:
                        d.rectangle((xx,yy,xx+3,yy+5),fill="#7B80B6")
        # Racing highway and vanishing point.
        d.polygon([(0,288),(720,288),(397,182),(323,182)],fill="#1D233A")
        d.line((323,182,0,288),fill="#ED7BA2",width=5)
        d.line((397,182,720,288),fill="#79D9E2",width=5)
        for j in range(12):
            # Road dashes grow in perspective and loop smoothly.
            depth=((j*26+t*8)%310)/310
            yy=184+int(104*depth*depth)
            half=2+int(12*depth)
            d.rectangle((360-half,yy,360+half,yy+2+int(10*depth)),fill="#F6D3A4")
        # Scrolling side grids.
        for side in (-1,1):
            for j in range(9):
                dep=((j*38+t*10)%360)/360
                yy=187+int(102*dep*dep)
                xx=360+side*(45+int(340*dep))
                d.line((xx,yy,xx+side*(10+int(34*dep)),yy),fill="#765078",width=2)
        # Arcade car: chunky, low silhouette, taillights and exhaust.
        bob = int(2*math.sin(t*math.pi/6))
        cy=222+bob
        d.polygon([(294,cy+27),(309,cy-6),(326,cy-17),(395,cy-17),(413,cy-6),(428,cy+27)],fill="#101626")
        d.rounded_rectangle((308,cy-14,413,cy+28),radius=12,fill="#54B4C3",outline="#C5EFF0",width=3)
        d.polygon([(329,cy-13),(342,cy-29),(380,cy-29),(394,cy-13)],fill="#1D2945")
        d.line((343,cy-25,380,cy-25),fill="#9DE1DF",width=3)
        d.rectangle((316,cy+3,344,cy+12),fill="#FF779A")
        d.rectangle((377,cy+3,405,cy+12),fill="#FF779A")
        d.rectangle((340,cy+18,381,cy+23),fill="#203044")
        d.rectangle((314,cy+26,340,cy+36),fill="#101322")
        d.rectangle((381,cy+26,407,cy+36),fill="#101322")
        for dx in (326,394):
            ex=dx+(t%4)*2
            d.ellipse((ex-5,cy+33,ex+5,cy+39),fill="#8ED6F0" if t%3 else "#FFD2B3")
        # Floating HUD: game-inspired but no decorative slogan.
        d.rounded_rectangle((22,22,171,66),radius=8,fill="#1E2540",outline="#6479A0",width=2)
        d.text((37,31),"SHIV // 06",fill="#E8F2F5",stroke_width=0)
        d.rectangle((36,52,154,55),fill="#385069")
        d.rectangle((36,52,36+int(118*(0.45+0.5*(t%36)/36)),55),fill="#74DBCF")
        # Twinkling stars.
        for k in range(20):
            xx=(k*97+19)%W
            yy=(k*43+13)%112
            if (t+k)%6<4:
                d.point((xx,yy),fill="#D9D2E7")
        frames.append(im)
    frames[0].save(OUT/"cozy-coding.gif",save_all=True,append_images=frames[1:],duration=85,loop=0,optimize=True)
    print("Created original looping synthwave arcade racer GIF")

if __name__=="__main__":
    cozy_gif()
    screenshots()
