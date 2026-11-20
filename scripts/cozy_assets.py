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
    """Original looping underwater pixel-art scene with luminous jellyfish and fish."""
    frames=[]
    W,H=720,288
    for t in range(40):
        im=Image.new("RGB",(W,H),"#071D31")
        d=ImageDraw.Draw(im)
        for y in range(H):
            p=y/H
            d.line((0,y,W,y),fill=(int(7+3*p),int(34-15*p),int(55-6*p)))
        # Surface ripples, distant shafts of light.
        for k in range(5):
            x=68+k*154
            d.polygon([(x,0),(x+18,0),(x+125,288),(x+85,288)],fill="#102F41")
        for k in range(10):
            x=(k*89+t*2)%760-20
            d.arc((x-38,-9,x+64,20),180,350,fill="#3C7C86",width=2)
        # Silhouetted rock formations and seabed.
        d.polygon([(0,251),(65,225),(130,254),(195,238),(255,267),(310,245),(405,264),(492,231),(590,260),(660,237),(720,256),(720,288),(0,288)],fill="#102B35")
        for k in range(18):
            x=(k*43+11)%720
            h=16+(k*19)%38
            d.arc((x-13,265-h,x+13,283),170,350,fill="#2C6D67",width=4)
            d.line((x,278,x+(k%3-1)*12,278-h),fill="#327B73",width=3)
        # Tiny fish shoal swimming right-to-left.
        for k in range(9):
            x=(720+(k*93)-(t*5+k*2))%850-55
            y=73+(k*37)%145+round(4*math.sin((t+k*5)*math.pi/20))
            size=5+(k%3)*3
            d.ellipse((x-size,y-4,x+size,y+4),fill="#B5D9CF")
            d.polygon([(x+size-2,y),(x+size+9,y-6),(x+size+9,y+6)],fill="#B5D9CF")
            d.point((x-size+3,y-1),fill="#183C49")
        # Three gently pulsing translucent jellyfish.
        for k,(cx,cy,r) in enumerate([(176,128,35),(379,96,26),(572,147,40)]):
            bob=round(10*math.sin(2*math.pi*(t/40+k/3)))
            yy=cy+bob
            pulse=round(4*math.sin(2*math.pi*(t/20+k/3)))
            rr=r+pulse
            color=["#85DBDA","#D5B2E8","#F0C5AA"][k]
            d.pieslice((cx-rr,yy-rr,cx+rr,yy+rr),180,360,fill=color)
            d.rectangle((cx-rr,yy,cx+rr,yy+7),fill=color)
            d.arc((cx-rr+6,yy-rr+5,cx+rr-6,yy+12),0,180,fill="#F3F0DF",width=2)
            for j in range(5):
                tx=cx-rr+10+j*(2*rr-20)//4
                sway=round(7*math.sin(2*math.pi*t/40+j+k))
                d.line((tx,yy+7,tx+sway,yy+31+(j%2)*12),fill=color,width=3)
                d.line((tx+sway,yy+31+(j%2)*12,tx-sway//2,yy+50+(j%2)*12),fill=color,width=2)
        # Rising bubbles in layered sizes.
        for k in range(25):
            x=25+(k*101)%680
            y=(260+(k*37)-t*(2+k%3))%310-8
            r=2+k%4
            d.ellipse((x-r,y-r,x+r,y+r),outline="#5B9A9C",width=1)
        # Small star-like plankton shimmer.
        for k in range(23):
            x=(k*79+17)%720
            y=(k*61+21)%247
            if (t+k*3)%12<7:
                d.point((x,y),fill="#9ACFC7")
        frames.append(im)
    frames[0].save(OUT/"deep-sea-drift.gif",save_all=True,append_images=frames[1:],duration=95,loop=0,optimize=True)
    print("Created original underwater jellyfish animation")

if __name__=="__main__":
    cozy_gif()
    screenshots()
