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

def dismiss_cookie_dialogs(page):
    """Prefer declining optional cookies; remove leftover consent overlays for screenshots."""
    import re

    # Consent platforms often render outside the normal DOM in an iframe.
    reject = re.compile(
        r"(alle ablehnen|alles ablehnen|nur notwendige|nur essenzielle|"
        r"nur erforderliche|ablehnen|reject all|decline all|"
        r"necessary only|essential only|only necessary|continue without accepting)",
        re.IGNORECASE,
    )
    for frame in page.frames:
        try:
            button = frame.get_by_role("button", name=reject).first
            if button.count() and button.is_visible():
                button.click(timeout=2500)
                page.wait_for_timeout(400)
        except Exception:
            pass

    # Screenshot-only cleanup: preserve the actual site and never click 'accept all'.
    # Also covers cookie providers with inaccessible consent frames.
    page.evaluate("""() => {
        const selectors = [
            '#CybotCookiebotDialog', '#CybotCookiebotDialogBodyUnderlay',
            '#onetrust-banner-sdk', '.onetrust-pc-dark-filter',
            '#usercentrics-root', '#uc-center-container', '.uc-overlay',
            '#cookie-law-info-bar', '.cli-modal-backdrop',
            '.cky-consent-container', '.cky-modal', '.cky-overlay',
            '#cmplz-cookiebanner-container', '.cmplz-cookiebanner',
            '[data-testid="cookie-banner"]', '[data-testid="cookie-consent"]',
            '[id*="cookie-banner" i]', '[class*="cookie-banner" i]',
            '[id*="cookie-consent" i]', '[class*="cookie-consent" i]',
            '[id*="consent-banner" i]', '[class*="consent-banner" i]'
        ];
        for (const selector of selectors) {
            try {
                document.querySelectorAll(selector).forEach(el => el.remove());
            } catch (_) {}
        }
        // Remove generic visible fixed-position consent panels by their wording.
        const textPattern = /cookies?|cookie-einstellungen|datenschutz.einstellungen|consent|einwilligung/i;
        for (const el of document.querySelectorAll('body *')) {
            if (!el.isConnected || el.children.length > 12) continue;
            const style = getComputedStyle(el);
            if (!['fixed', 'sticky'].includes(style.position)) continue;
            const box = el.getBoundingClientRect();
            if (box.width < 180 || box.height < 45 || box.height > innerHeight * 0.85) continue;
            if (textPattern.test((el.innerText || '').slice(0, 700))) el.remove();
        }
        document.documentElement.style.overflow = 'auto';
        document.body.style.overflow = 'auto';
    }""")

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
                dismiss_cookie_dialogs(page)
                page.wait_for_timeout(350)
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
    """Original anime-comedy chibi coder: one bug, dramatic panic, then ramen break."""
    frames=[]
    W,H=720,288
    for t in range(48):
        im=Image.new("RGB",(W,H),"#FFF1DC")
        d=ImageDraw.Draw(im)
        phase=t//12
        # Manga-style speed lines and halftone backdrop.
        d.rectangle((0,0,720,288),fill="#FFF2DF" if phase!=1 else "#FBE0DE")
        for i in range(24):
            x=(i*97+23)%720
            y=(i*43+11)%288
            d.ellipse((x,y,x+3,y+3),fill="#E8D6C6")
        for i in range(13):
            yy=14+i*22
            d.line((0,yy,110+(i%3)*27,yy-12),fill="#E5CFC2",width=2)
            d.line((610-(i%3)*20,yy-8,720,yy),fill="#E5CFC2",width=2)
        # A small desk, laptop and steaming ramen.
        d.rounded_rectangle((78,218,652,234),radius=5,fill="#BD877A")
        d.rectangle((110,234,124,288),fill="#9B6D69")
        d.rectangle((610,234,624,288),fill="#9B6D69")
        d.rounded_rectangle((378,119,607,214),radius=10,fill="#526A80",outline="#2C3D54",width=4)
        d.rounded_rectangle((392,134,592,201),radius=5,fill="#1E3147")
        if phase==0:
            msg="BUILDING..."
            col="#9FE3C7"
        elif phase==1:
            msg="ERROR !!!"
            col="#FF9F9F"
        elif phase==2:
            msg="FIXED :)"
            col="#9FE3C7"
        else:
            msg="NEW BUG?!"
            col="#FFB9A0"
        d.text((416,154),msg,fill=col,stroke_width=0)
        for j in range(3):
            d.rectangle((414,177+j*7,480+((j*17+t*3)%95),180+j*7),fill="#6C9DA0")
        d.polygon([(371,215),(609,215),(628,227),(360,227)],fill="#8395A2")
        d.rounded_rectangle((496,231,579,252),radius=8,fill="#E6A78B",outline="#C78275",width=3)
        d.arc((504,213,533,241),180,350,fill="#FFF3D0",width=3)
        d.arc((525,209,553,241),180,350,fill="#FFF3D0",width=3)
        for j in range(3):
            sx=511+j*22
            d.arc((sx,199-(t%5),sx+14,228-(t%5)),100,245,fill="#C6B9B1",width=2)
        # Big expressive chibi character, original design.
        bob=round(3*math.sin(t*math.pi/6))
        cx,cy=248,138+bob
        d.ellipse((158,209,344,226),fill="#D9C8BC")
        d.rounded_rectangle((193,170+bob,307,228+bob),radius=23,fill="#718EA5",outline="#40596C",width=4)
        d.ellipse((167,53+bob,330,198+bob),fill="#F8C9AA",outline="#8A6470",width=4)
        # Distinctive tousled anime hair.
        d.polygon([(165,104+bob),(174,69+bob),(191,81+bob),(202,43+bob),(219,66+bob),(240,39+bob),(258,63+bob),(282,46+bob),(297,74+bob),(317,64+bob),(327,112+bob),(298,96+bob),(279,109+bob),(259,89+bob),(239,112+bob),(216,94+bob),(195,115+bob)],fill="#38435A")
        d.ellipse((165,122+bob,187,150+bob),fill="#F8C9AA",outline="#8A6470",width=3)
        d.ellipse((309,122+bob,332,150+bob),fill="#F8C9AA",outline="#8A6470",width=3)
        # Different anime reaction every twelve frames.
        if phase==1 or phase==3:
            for ex in (211,282):
                d.ellipse((ex-15,120+bob,ex+15,155+bob),fill="#FFFFFF",outline="#38435A",width=3)
                d.ellipse((ex-5,132+bob,ex+7,148+bob),fill="#29394D")
                d.ellipse((ex-2,132+bob,ex+2,136+bob),fill="#FFFFFF")
            d.ellipse((239,158+bob,257,181+bob),fill="#874E60")
            d.ellipse((257,151+bob,264,169+bob),fill="#7BC8E6")
            for i in range(5):
                xx=121+i*29
                d.line((xx,36,xx+15,12),fill="#DE8C8A",width=4)
            d.text((343,51),"?!",fill="#C95E76",stroke_width=1,stroke_fill="#C95E76")
        elif phase==2:
            for ex in (211,282):
                d.arc((ex-18,125+bob,ex+18,153+bob),190,350,fill="#38435A",width=5)
            d.arc((225,148+bob,274,183+bob),0,180,fill="#A86168",width=4)
            for i in range(4):
                xx=146+i*50
                d.line((xx,30,xx+8,16),fill="#D3A36B",width=3)
        else:
            for ex in (211,282):
                d.ellipse((ex-13,126+bob,ex+13,150+bob),fill="#FFFFFF")
                d.ellipse((ex-4,130+bob,ex+5,144+bob),fill="#38435A")
            d.arc((235,157+bob,266,172+bob),0,180,fill="#935E68",width=3)
        # Hands at keyboard; comic sweat droplets during panic.
        d.ellipse((316,202+bob,354,225+bob),fill="#F8C9AA",outline="#8A6470",width=2)
        d.ellipse((157,202+bob,195,225+bob),fill="#F8C9AA",outline="#8A6470",width=2)
        if phase in (1,3):
            d.ellipse((325,122+bob,338,145+bob),fill="#7BC8E6")
        frames.append(im)
    frames[0].save(OUT/"anime-coder-comedy.gif",save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=True)
    print("Created original anime comedy coding GIF")

if __name__=="__main__":
    cozy_gif()
    screenshots()
