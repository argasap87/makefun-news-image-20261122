#!/usr/bin/env python3
"""Build entry.png for make.fun news-image-20261122.

Layout (1024x1024, dark news-poster style):
  - top banner: title + date
  - centre: AI-generated cracked globe (hero art, no text in it)
  - bottom: five story rows, each with a number chip, a small
    hand-drawn PIL icon, a bold headline and one short fact line.

Run: python3 draw.py  -> writes entry.png next to this file.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

BG = (8, 13, 18)
BANNER_BG = (26, 5, 5)
AMBER = (255, 179, 71)
RED = (255, 69, 58)
WHITE = (245, 245, 240)
FADE = (196, 208, 216)
ROW_A = (16, 24, 32)
ROW_B = (11, 17, 24)
LINE = (48, 60, 72)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def banner(draw):
    draw.rectangle([0, 0, W, 118], fill=BANNER_BG)
    draw.rectangle([0, 118, W, 122], fill=RED)
    title = font(FONT_BOLD, 62)
    date = font(FONT_BOLD, 33)
    tag = font(FONT_BOLD, 30)
    draw.text((32, 8), "THE WORLD CRACKS", font=title, fill=WHITE)
    tag_txt = "WORLD NEWS"
    draw.text((W - 32 - draw.textlength(tag_txt, font=tag), 20),
              tag_txt, font=tag, fill=AMBER)
    draw.text((32, 72), "SUNDAY  22  NOVEMBER  2026  ·  AS REPORTED", font=date, fill=AMBER)


def hero(base):
    """Crop the middle band of the square hero art and paste it."""
    art = Image.open(os.path.join(HERE, "assets", "hero.webp")).convert("RGB")
    # Globe centre is near the middle; take a 1024x378 band through it.
    top = (art.height - 378) // 2
    band = art.crop((0, top, art.width, top + 378))
    band = band.resize((W, 378), Image.LANCZOS)
    base.paste(band, (0, 122))


def strip(base):
    """Five small scene thumbnails, one per story, with number chips."""
    tw, th, gap = 200, 120, 5
    x0 = 2
    for i in range(5):
        art = Image.open(
            os.path.join(HERE, "assets", f"scene{i + 1}.webp")).convert("RGB")
        # cover-crop to tw x th
        scale = max(tw / art.width, th / art.height)
        nw, nh = int(art.width * scale + 0.5), int(art.height * scale + 0.5)
        art = art.resize((nw, nh), Image.LANCZOS)
        left = (nw - tw) // 2
        top = (nh - th) // 2
        thumb = art.crop((left, top, left + tw, top + th))
        x = x0 + i * (tw + gap)
        base.paste(thumb, (x, 500))
        draw = ImageDraw.Draw(base)
        colour = STORIES[i][1]
        draw.ellipse([x + 8, 508, x + 44, 544], fill=colour)
        num = str(i + 1)
        chip = font(FONT_BOLD, 26)
        nw2 = draw.textlength(num, font=chip)
        draw.text((x + 26 - nw2 / 2, 510), num, font=chip, fill=(10, 10, 10))


def star(draw, cx, cy, r, colour, points=8):
    pts = []
    for i in range(points * 2):
        ang = math.pi * i / points - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=colour)


def icon(draw, kind, x, y, s, colour):
    """Draw a simple bold icon inside a square of side s at (x, y)."""
    cx, cy = x + s // 2, y + s // 2
    if kind == "blast":  # missile / drone strike: explosion burst
        star(draw, cx, cy, s // 2 - 2, colour, 8)
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=BG)
    elif kind == "badge":  # capture: sheriff star badge
        star(draw, cx, cy, s // 2 - 2, colour, 5)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=BG)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=colour)
    elif kind == "quake":  # trembling mountain with a crack
        draw.polygon(
            [(x + 4, y + s - 6), (cx - 6, y + 12), (cx + 2, y + s - 20),
             (cx + 10, y + 22), (x + s - 4, y + s - 6)],
            fill=colour,
        )
        draw.line([(cx - 2, y + 10), (cx + 6, y + 26), (cx - 4, y + 40)],
                  fill=BG, width=4)
    elif kind == "clock":  # frozen clock: COP31 overtime
        draw.ellipse([x + 4, y + 4, x + s - 4, y + s - 4],
                     outline=colour, width=5)
        draw.line([(cx, cy), (cx, y + 12)], fill=colour, width=5)
        draw.line([(cx, cy), (cx + 14, cy + 6)], fill=colour, width=5)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=colour)
    elif kind == "ship":  # burning cargo ship
        draw.polygon([(x + 6, y + s - 14), (x + s - 6, y + s - 14),
                      (x + s - 14, y + s - 34), (x + 14, y + s - 34)],
                     fill=colour)
        draw.rectangle([cx - 8, y + 8, cx + 8, y + s - 34], fill=colour)
        draw.line([(cx, y + 8), (cx + 10, y - 2)], fill=RED, width=4)


STORIES = [
    # (icon, chip colour, headline, fact line)
    ("blast", (255, 69, 58),
     "IRAN CLAIMS STRIKE ON US RADARS",
     "IRGC says missiles + drones hit two Patriot sites in Bahrain"),
    ("badge", (255, 179, 71),
     "EL CHAPO ISIDRO CAPTURED",
     "Mexican forces capture kingpin in Sinaloa raid; 11 killed"),
    ("quake", (94, 234, 212),
     "PERU QUAKE SHAKES THE ANDES",
     "Lima residents flee homes; no casualties reported yet"),
    ("clock", (163, 230, 53),
     "COP31 STALLS IN OVERTIME",
     "Talks run past deadline, deadlocked on fossil fuels and finance"),
    ("ship", (96, 165, 250),
     "DRONE HITS RUSSIAN SHIP SPARTA II",
     "Gulf of Finland; Finland says Ukraine likely behind it, crew rescued"),
]


def rows(draw):
    y0 = 620
    rh = 80
    head = font(FONT_BOLD, 33)
    fact = font(FONT_REG, 23)
    chip = font(FONT_BOLD, 30)
    for i, (kind, colour, headline, factline) in enumerate(STORIES):
        y = y0 + i * rh
        draw.rectangle([0, y, W, y + rh], fill=ROW_A if i % 2 == 0 else ROW_B)
        draw.rectangle([0, y, W, y + 1], fill=LINE)
        # number chip
        draw.ellipse([18, y + 16, 66, y + 64], fill=colour)
        num = str(i + 1)
        tw = draw.textlength(num, font=chip)
        draw.text((42 - tw / 2, y + 19), num, font=chip, fill=(10, 10, 10))
        # icon
        icon(draw, kind, 84, y + 14, 52, colour)
        # text
        draw.text((152, y + 7), headline, font=head, fill=WHITE)
        draw.text((152, y + 44), factline, font=fact, fill=FADE)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    banner(draw)
    hero(img)
    strip(img)
    rows(ImageDraw.Draw(img))
    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print(out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
