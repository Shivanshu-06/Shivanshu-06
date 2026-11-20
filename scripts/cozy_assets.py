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
        # Cat: ears, body, eyes, gently swishing tail
        pixel(d,13,29,22,9,"#D8BDA3")
        pixel(d,16,25,5,5,"#D8BDA3")
        pixel(d,28,25,5,5,"#D8BDA3")
        pixel(d,19,31,2,2,"#514B48")
        pixel(d,28,31,2,2,"#514B48")
        pixel(d,24,34,2,1,"#C38386")
        pixel(d,11-(t//4)%3,32,5,2,"#D8BDA3")
        # floating warm heart
        if t%8<6:
            pixel(d,39,15-(t//3)%3,2,2,"#D99E9E")
            pixel(d,42,15-(t//3)%3,2,2,"#D99E9E")
            pixel(d,40,17-(t//3)%3,3,2,"#D99E9E")
        frames.append(im)
    frames[0].save(OUT/"cozy-coding.gif",save_all=True,append_images=frames[1:],duration=160,loop=0,optimize=True)
    print("Created original cozy-coding.gif")

if __name__=="__main__":
    cozy_gif()
    screenshots()
