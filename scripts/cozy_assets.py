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
    """Original neon-night coding scene: hovering mini robot, glowing terminal, shooting stars."""
    frames = []
    for t in range(24):
        im = Image.new("RGB", (720, 288), "#101827")
        d = ImageDraw.Draw(im)
        # Midnight sky, stars and faraway skyline
        d.rectangle((0, 220, 720, 288), fill="#172D35")
        for x, y in [(42,36),(103,64),(189,25),(274,53),(361,22),(445,68),(537,28),(648,57),(693,21)]:
            d.rectangle((x,y,x+3,y+3),fill="#A6D9D0" if (t+x)%7<5 else "#F4D59A")
        d.ellipse((564,36,644,116),fill="#E9D9AE")
        d.ellipse((580,28,653,104),fill="#101827")
        for i,x in enumerate(range(0,720,38)):
            height=30+(i*17)%65
            d.rectangle((x,220-height,x+28,220),fill="#203E47")
            for wy in range(220-height+12,214,18):
                d.rectangle((x+8,wy,x+12,wy+5),fill="#7BAFA1")
        # Neon terminal and desk
        d.rounded_rectangle((214,92,508,238),radius=12,fill="#38565C",outline="#8AB7A5",width=4)
        d.rectangle((229,107,493,217),fill="#0B1F2A")
        d.rounded_rectangle((160,235,560,247),radius=4,fill="#A47C70")
        d.rectangle((194,247,209,288),fill="#6E5B58")
        d.rectangle((512,247,527,288),fill="#6E5B58")
        # Animated terminal code and a small heart pulse
        for j in range(6):
            line_y=119+j*15
            line_len=60+((j*29+t*5)%110)
            d.rounded_rectangle((248,line_y,248+line_len,line_y+4),radius=2,fill="#75C9B1" if j%2==0 else "#D4B18A")
        cursor_x=248+((t//2)%15)*10
        d.rectangle((cursor_x,209,cursor_x+7,214),fill="#E9D9AE")
        # Floating original robot mascot, blinking eyes and subtle hover
        bob=round(5*math.sin(2*math.pi*t/24))
        cy=127+bob
        d.rounded_rectangle((43,cy,159,cy+86),radius=24,fill="#E7D8B9",outline="#86BBAF",width=5)
        d.rounded_rectangle((56,cy+22,146,cy+63),radius=14,fill="#213E46")
        for ex in [81,119]:
            if t in [10,11]:
                d.line((ex-7,cy+44,ex+7,cy+44),fill="#9BE7D2",width=4)
            else:
                d.ellipse((ex-7,cy+36,ex+7,cy+50),fill="#9BE7D2")
        d.line((102,cy-4,102,cy-17),fill="#B8CFBA",width=5)
        d.ellipse((96,cy-25,108,cy-13),fill="#EAC68C")
        d.ellipse((65,cy+83,90,cy+95),fill="#6AACA1")
        d.ellipse((114,cy+83,139,cy+95),fill="#6AACA1")
        # Tiny orbiting fireflies
        for k in range(4):
            angle=2*math.pi*(t/24+k/4)
            x=106+87*math.cos(angle)
            y=166+48*math.sin(angle)
            d.ellipse((x-3,y-3,x+3,y+3),fill="#E9C58B")
        # A moving shooting star
        sx=610-(t*17)%560
        sy=48+(t*5)%85
        d.line((sx+22,sy-10,sx,sy),fill="#B5D8CF",width=3)
        d.ellipse((sx-3,sy-3,sx+3,sy+3),fill="#F7E8C3")
        frames.append(im)
    frames[0].save(OUT / "cozy-coding.gif",save_all=True,append_images=frames[1:],duration=90,loop=0,optimize=True)
    print("Created original neon robot GIF")

if __name__=="__main__":
    cozy_gif()
    screenshots()
