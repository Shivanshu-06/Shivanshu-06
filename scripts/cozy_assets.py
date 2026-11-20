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
    """Draw an original animated pastel railway landscape with cherry blossoms."""
    frames = []
    width, height = 720, 288
    for t in range(32):
        im = Image.new("RGB", (width, height), "#F8DED5")
        d = ImageDraw.Draw(im)
        # Hand-painted-style twilight gradient.
        for y in range(0, height):
            ratio = y / height
            if ratio < 0.62:
                k = ratio / 0.62
                col = (int(250-21*k), int(219-19*k), int(207+12*k))
            else:
                k = (ratio-0.62)/0.38
                col = (int(229-73*k), int(200-22*k), int(219-62*k))
            d.line((0, y, width, y), fill=col)
        # Sunset, cloud ribbons and mountain silhouettes.
        d.ellipse((508, 52, 620, 164), fill="#FFF1BE")
        for cx,cy,cw in [(74,58,118),(342,30,106),(588,86,104)]:
            d.ellipse((cx,cy,cx+cw,cy+19),fill="#FFE8DB")
            d.ellipse((cx+17,cy-10,cx+cw-17,cy+15),fill="#FFE8DB")
        d.polygon([(0,177),(80,107),(157,184),(239,139),(346,193),(456,121),(558,189),(652,115),(720,176),(720,226),(0,226)],fill="#9FB8AD")
        d.polygon([(0,208),(105,166),(225,213),(337,176),(449,228),(565,165),(720,216),(720,288),(0,288)],fill="#698F82")
        d.rectangle((0,222,720,288),fill="#5C8275")
        # Narrow river framed by greenery.
        d.polygon([(0,244),(280,227),(435,288),(0,288)],fill="#83A9A0")
        for lineY in [251,267,280]:
            d.line((25,lineY,156,lineY-3),fill="#B4D3C9",width=2)
        # Rail bridge and sleepers.
        d.rectangle((0,205,720,214),fill="#75675E")
        d.rectangle((0,215,720,222),fill="#554E4D")
        for xx in range(0,720,36):
            d.rectangle((xx,214,xx+8,226),fill="#594C4A")
        # Smooth-moving compact train, deliberately no animal/robot mascot.
        x = -308 + t*35
        d.rounded_rectangle((x,139,x+311,203),radius=18,fill="#FFF6E8",outline="#476F6C",width=4)
        d.rectangle((x+17,145,x+269,159),fill="#C77F7F")
        d.rounded_rectangle((x+22,162,x+75,187),radius=7,fill="#668E93")
        for j in range(3):
            wx=x+91+j*54
            d.rounded_rectangle((wx,162,wx+42,187),radius=6,fill="#668E93")
            d.line((wx+8,166,wx+28,185),fill="#B8D2D0",width=3)
        d.line((x+23,193,x+282,193),fill="#BB9D81",width=3)
        for wx in (x+49,x+257):
            d.ellipse((wx-11,196,wx+11,217),fill="#3D5050")
            d.ellipse((wx-5,202,wx+5,212),fill="#A8B9B1")
        # Blooming branches across the upper left.
        d.line((-13,-6,177,81),fill="#735A56",width=11)
        d.line((85,38,95,103),fill="#735A56",width=7)
        d.line((143,63,205,28),fill="#735A56",width=6)
        for j in range(28):
            bx=15+(j*43)%200
            by=6+(j*29)%106
            if (bx-90)**2 + (by-52)**2 < 11000:
                d.ellipse((bx-8,by-6,bx+8,by+7),fill="#F4B5B6" if j%3 else "#FFE0D6")
                d.ellipse((bx+3,by-8,bx+13,by+3),fill="#FFE6DE")
        # Soft falling petals add motion across the full composition.
        for j in range(21):
            px=(j*79+t*(2+j%3))%755-15
            py=(j*53+t*(3+j%2))%305-8
            d.ellipse((px,py,px+6,py+3),fill="#F6B6BE" if j%2 else "#FFE5D9")
        frames.append(im)
    frames[0].save(OUT / "cozy-coding.gif",save_all=True,append_images=frames[1:],duration=95,loop=0,optimize=True)
    print("Created animated cherry-blossom train landscape")

if __name__=="__main__":
    cozy_gif()
    screenshots()
