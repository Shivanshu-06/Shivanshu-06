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
    frames=[]
    for t in range(16):
        im=Image.new("RGB",(560,208),"#FCF9F0")
        d=ImageDraw.Draw(im)
        # Sky, hill, clouds, and tiny stars: original pixel illustration
        pixel(d,0,0,140,52,"#FCF9F0")
        pixel(d,0,38,140,14,"#DDE9D8")
        pixel(d,0,45,140,7,"#B9D1B2")
        for x,y in [(10,8),(112,11),(121,26)]:
            pixel(d,x,y,2,2,"#E6CFA6")
        shift=(t//4)%4
        for x,y in [(16,13),(94,9)]:
            pixel(d,x+shift,y,18,3,"#E7E8DB")
            pixel(d,x+3+shift,y-3,10,3,"#E7E8DB")
        # Desk and notebook
        pixel(d,29,37,83,4,"#9A755E")
        pixel(d,33,41,5,11,"#846753")
        pixel(d,103,41,5,11,"#846753")
        pixel(d,49,25,40,13,"#657F72")
        pixel(d,52,28,34,8,"#E4EEDF")
        pixel(d,54,30,15,2,"#B5C9B0")
        pixel(d,54,33,24,1,"#A0B7A0")
        pixel(d,44,38,49,2,"#C4B6A0")
        # Plant pot with moving leaf
        pixel(d,100,31,9,7,"#C58D79")
        pixel(d,103,22,2,9,"#567B60")
        pixel(d,99+(t//4)%2,23,5,3,"#7FA585")
        pixel(d,105,20+(t//5)%2,5,4,"#709A7B")
        # A tiny wandering forest spirit with a lantern, original pixel character.
        bob = (t // 4) % 2
        pixel(d,15,26-bob,17,12,"#F4F1DF")
        pixel(d,18,22-bob,11,5,"#F4F1DF")
        pixel(d,21,30-bob,2,2,"#586E60")
        pixel(d,27,30-bob,2,2,"#586E60")
        pixel(d,24,34-bob,2,1,"#B98C7D")
        pixel(d,17,37-bob,4,2,"#E5DEC9")
        pixel(d,28,37-bob,4,2,"#E5DEC9")
        # A leaf hat and a little glowing lantern.
        pixel(d,19,19-bob,13,3,"#7F9D79")
        pixel(d,24,17-bob,8,3,"#94B18B")
        pixel(d,31,29-bob,6,2,"#E5DEC9")
        pixel(d,36,27-bob,6,8,"#9A7659")
        pixel(d,37,28-bob,4,5,"#E7BE75" if t%4<2 else "#F5D998")
        pixel(d,38,25-bob,2,2,"#9A7659")
        # Floating fireflies.
        for fx, fy, phase in [(9,19,0),(43,14,4),(37,9,8)]:
            if (t+phase)%12<9:
                pixel(d,fx,fy-((t+phase)//4)%2,2,2,"#EBCF83")
        frames.append(im)
    frames[0].save(OUT/"cozy-coding.gif",save_all=True,append_images=frames[1:],duration=160,loop=0,optimize=True)
    print("Created original cozy-coding.gif")

if __name__=="__main__":
    cozy_gif()
    screenshots()
