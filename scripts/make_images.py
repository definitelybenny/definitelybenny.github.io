#!/usr/bin/env python3
"""Draw the site's raster images from code, so they stay in sync with the notebook look.

Makes:
  favicon.ico            16 and 32 px tab icons (favicon.svg is the main one)
  apple-touch-icon.png   180 px phone home-screen icon
  assets/og.png          1200x630 link preview for the home page

Each tool page's own preview image is drawn by scripts/build.py, using og_image() from here.

Needs Pillow (python3 -m pip install pillow). Fonts are fetched from Google Fonts
into scripts/.fonts the first time it runs.

  python3 scripts/make_images.py
"""
import math
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(__file__).resolve().parent / ".fonts"

PAPER = "#F3F4EE"
LINE = "#D2DDCA"
MARGIN = "#8DB58A"
INK = "#1F251D"
CARD = "#FBFCF7"
MOSS = "#3D7643"
PEN = "#B4552E"
TAPE = (160, 180, 140, 140)

FONT_URLS = {
    "caslon": "https://fonts.googleapis.com/css2?family=Libre+Caslon+Display",
    "caveat": "https://fonts.googleapis.com/css2?family=Caveat:wght@700",
}


def font_path(name):
    FONTS.mkdir(exist_ok=True)
    path = FONTS / f"{name}.ttf"
    if not path.exists():
        # An old user agent makes Google Fonts answer with plain TTF files.
        req = urllib.request.Request(FONT_URLS[name], headers={"User-Agent": "Mozilla/4.0"})
        css = urllib.request.urlopen(req).read().decode()
        ttf = re.search(r"url\((https://[^)]+\.ttf)\)", css).group(1)
        path.write_bytes(urllib.request.urlopen(ttf).read())
    return str(path)


def font(name, size):
    return ImageFont.truetype(font_path(name), size)


# --- a tiny SVG path flattener (M, L, C and their relative forms), enough for our hand-drawn marks ---

def flatten(d, scale=1.0, dx=0.0, dy=0.0, steps=24):
    tokens = re.findall(r"[MmLlCc]|-?\d*\.?\d+", d)
    pts, cur, cmd, i = [], (0.0, 0.0), None, 0
    strokes = []
    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
            continue
        if cmd in "Mm":
            x, y = float(tokens[i]), float(tokens[i + 1])
            i += 2
            cur = (cur[0] + x, cur[1] + y) if cmd == "m" else (x, y)
            if pts:
                strokes.append(pts)
            pts = [cur]
            cmd = "l" if cmd == "m" else "L"
        elif cmd in "Ll":
            x, y = float(tokens[i]), float(tokens[i + 1])
            i += 2
            cur = (cur[0] + x, cur[1] + y) if cmd == "l" else (x, y)
            pts.append(cur)
        elif cmd in "Cc":
            v = [float(tokens[i + k]) for k in range(6)]
            i += 6
            if cmd == "c":
                v = [v[k] + (cur[0] if k % 2 == 0 else cur[1]) for k in range(6)]
            p0, p1, p2, p3 = cur, (v[0], v[1]), (v[2], v[3]), (v[4], v[5])
            for s in range(1, steps + 1):
                u = s / steps
                a, b, c, e = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u ** 2, u ** 3
                pts.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
            cur = p3
    if pts:
        strokes.append(pts)
    return [[(x * scale + dx, y * scale + dy) for x, y in s] for s in strokes]


def stroke(draw, d, width, fill, scale=1.0, dx=0.0, dy=0.0):
    for pts in flatten(d, scale, dx, dy):
        draw.line(pts, fill=fill, width=round(width), joint="curve")
        # a round dab at every vertex hides seams between segments and gives round caps
        r = width / 2
        for x, y in pts:
            draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def rotated_layer(size, draw_fn, angle_deg, center):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    # PIL rotates counter-clockwise for positive angles; SVG rotate() is clockwise.
    return layer.rotate(-angle_deg, resample=Image.BICUBIC, center=center)


# --- icons ---

QMARK = "M23 25c0-7 5-12 11-12 7 0 11 5 11 10 0 6-4 8-8 11-3 2-4 4-4 8"
TICKS = ["M48 9l3-4", "M53 15l5-1"]


def favicon(px):
    S = 8  # supersample
    n = 64 * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    img.alpha_composite(rotated_layer((n, n), lambda d: d.rounded_rectangle((5 * S, 5 * S, 59 * S, 59 * S), radius=14 * S, fill=MOSS), -6, (32 * S, 32 * S)))
    d = ImageDraw.Draw(img)
    stroke(d, QMARK, 5.5 * S, PAPER, S)
    d.ellipse(((33 - 3.6) * S, (50 - 3.6) * S, (33 + 3.6) * S, (50 + 3.6) * S), fill=PAPER)
    for t in TICKS:
        stroke(d, t, 3 * S, PEN, S)
    return img.resize((px, px), Image.LANCZOS)


def touch_icon():
    # Full bleed: phones round the corners themselves and paint transparency black.
    S, n = 4, 180 * 4
    img = Image.new("RGB", (n, n), MOSS)
    d = ImageDraw.Draw(img)
    k = n / 64 * 0.92
    off = (n - 64 * k) / 2
    stroke(d, QMARK, 5.5 * k, PAPER, k, off, off + 2 * S)
    cx, cy, r = 33 * k + off, 50 * k + off + 2 * S, 3.6 * k
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PAPER)
    for t in TICKS:
        stroke(d, t, 3 * k, PEN, k, off - 2 * S, off + 2 * S)
    return img.resize((180, 180), Image.LANCZOS)


# --- link previews ---

def wrap(text, f, max_w, draw):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def og_image(lines_or_text, scrawl):
    S = 2
    W, H = 1200 * S, 630 * S
    img = Image.new("RGBA", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    for y in range(63, 630, 63):
        d.line((0, y * S, W, y * S), fill=LINE, width=2 * S)
    d.line((70 * S, 0, 70 * S, H), fill=MARGIN, width=4 * S)

    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    if isinstance(lines_or_text, list):
        size, lines = 54, lines_or_text
    else:
        for size in (56, 50, 44, 40):
            f = font("caslon", size * S)
            lines = wrap(lines_or_text, f, 600 * S, measure)
            if len(lines) <= 3:
                # balance the lines: shrink the width until another line would appear
                w = 600 * S
                while w > 200 * S and len(wrap(lines_or_text, f, w - 10 * S, measure)) == len(lines):
                    w -= 10 * S
                lines = wrap(lines_or_text, f, w, measure)
                break
    caslon = font("caslon", size * S)
    caveat = font("caveat", 40 * S)
    lh = size * 1.22
    block = lh * (len(lines) - 1) + 40 + 30  # text lines, gap, scrawl
    top = 300 - block / 2 + size * 0.35
    card_h = max(340, block + 150)

    def card(cd):
        x0, y0 = 130 * S, (300 - card_h / 2) * S
        cd.rounded_rectangle((x0, y0, x0 + 680 * S, y0 + card_h * S), radius=30 * S, fill=CARD)
        for k, line in enumerate(lines):
            cd.text((470 * S, (top + k * lh) * S), line, font=caslon, fill=INK, anchor="ms")
        cd.text((470 * S, (top + (len(lines) - 1) * lh + 72) * S), scrawl, font=caveat, fill=PEN, anchor="ms")

    shadow = rotated_layer((W, H), lambda cd: cd.rounded_rectangle((136 * S, (306 - card_h / 2) * S, 816 * S, (306 + card_h / 2) * S), radius=30 * S, fill=(0, 0, 0, 28)), -3, (470 * S, 300 * S))
    img.alpha_composite(shadow)
    img.alpha_composite(rotated_layer((W, H), card, -3, (470 * S, 300 * S)))
    tape_y = 300 - card_h / 2 - 16
    img.alpha_composite(rotated_layer((W, H), lambda cd: cd.rectangle((420 * S, tape_y * S, 540 * S, (tape_y + 34) * S), fill=TAPE), -7, (480 * S, (tape_y + 17) * S)))

    d = ImageDraw.Draw(img)
    stroke(d, "M920 210c0-58 46-94 100-94 62 0 100 40 100 90 0 46-32 68-64 90-26 16-36 32-36 60", 16 * S, MOSS, S)
    d.ellipse((1006 * S, 456 * S, 1034 * S, 484 * S), fill=MOSS)
    d.text((140 * S, 575 * S), "definitelybenny.dev", font=font("caveat", 48 * S), fill=MOSS, anchor="ls")
    return img.convert("RGB").resize((1200, 630), Image.LANCZOS)


def main():
    """The site-wide images. Each tool's preview image is drawn by scripts/build.py."""
    fav32, fav16 = favicon(32), favicon(16)
    fav32.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32)], append_images=[fav16])
    touch_icon().save(ROOT / "apple-touch-icon.png", optimize=True)
    og_image(["Which furniture keeps", "four Pokémon happy?"], "tap to find out").save(ROOT / "assets" / "og.png", optimize=True)
    print("wrote favicon.ico, apple-touch-icon.png, assets/og.png")


if __name__ == "__main__":
    main()
