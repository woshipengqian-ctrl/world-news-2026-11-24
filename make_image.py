#!/usr/bin/env python3
"""Render news.png: a newspaper-style front page summing up the world news
of Tuesday 24 November 2026 in one 1024x1024 image.

Build-time tool only (uses Pillow). The submitted program, main.py, is
standard-library only and simply copies the news.png produced here.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "news.png")

W = H = 1024
PAPER = (247, 243, 234)        # #f7f3ea
INK = (26, 26, 26)             # #1a1a1a
PANEL_BG = (255, 253, 246)
PANEL_EDGE = (120, 110, 92)
DETAIL_INK = (52, 48, 40)
ACCENT = (140, 43, 29)         # masthead red

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines, each <= max_w wide."""
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_spaced(draw, cx, y, s, f, fill, spacing):
    """Draw letter-spaced text centred on cx; returns total width."""
    widths = [text_w(draw, ch, f) for ch in s]
    total = sum(widths) + spacing * (len(s) - 1)
    x = cx - total / 2
    for ch, wch in zip(s, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += wch + spacing
    return total


def fit_font(draw, s, path, max_w, start, minimum=20):
    """Largest size <= start whose single-line width fits max_w."""
    size = start
    while size > minimum and text_w(draw, s, font(path, size)) > max_w:
        size -= 2
    return font(path, size)


# ---------------------------------------------------------------- icons
# Each icon is drawn in a box (x0, y0, x1, y1) in the panel's tag colour.

def icon_wave(draw, box, c):
    x0, y0, x1, y1 = box
    mid = (y0 + y1) / 2
    for k, yy in enumerate((mid - 11, mid, mid + 11)):
        pts = []
        for i in range(41):
            x = x0 + (x1 - x0) * i / 40
            y = yy + 5 * math.sin(i / 40 * math.pi * 2 + k)
            pts.append((x, y))
        draw.line(pts, fill=c, width=3)


def icon_dome(draw, box, c):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    draw.line([(cx, y0 + 2), (cx, y0 + 10)], fill=c, width=3)
    draw.arc([cx - 17, y0 + 6, cx + 17, y0 + 40], 180, 360, fill=c, width=3)
    draw.line([(x0 + 4, y0 + 24), (x1 - 4, y0 + 24)], fill=c, width=3)
    for dx in (-14, -5, 5, 14):
        draw.line([(cx + dx, y0 + 28), (cx + dx, y1 - 8)], fill=c, width=3)
    draw.line([(x0 + 2, y1 - 5), (x1 - 2, y1 - 5)], fill=c, width=3)


def icon_satellite(draw, box, c):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # body
    draw.rectangle([cx - 7, cy - 10, cx + 7, cy + 10], outline=c, width=3)
    # solar panels with a centre strut and one cross line each
    draw.rectangle([x0 + 2, cy - 7, cx - 12, cy + 7], outline=c, width=3)
    draw.rectangle([cx + 12, cy - 7, x1 - 2, cy + 7], outline=c, width=3)
    draw.line([(x0 + 14, cy - 7), (x0 + 14, cy + 7)], fill=c, width=2)
    draw.line([(x1 - 14, cy - 7), (x1 - 14, cy + 7)], fill=c, width=2)
    # dish antenna below the body
    draw.line([(cx, cy + 10), (cx, cy + 15)], fill=c, width=3)
    draw.arc([cx - 8, cy + 8, cx + 8, cy + 24], 20, 160, fill=c, width=3)


def icon_jet(draw, box, c):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    jet = [
        (cx + 24, cy), (cx + 6, cy - 4), (cx - 2, cy - 16), (cx - 8, cy - 16),
        (cx - 6, cy - 4), (cx - 18, cy - 12), (cx - 23, cy - 12),
        (cx - 19, cy), (cx - 23, cy + 12), (cx - 18, cy + 12),
        (cx - 6, cy + 4), (cx - 8, cy + 16), (cx - 2, cy + 16),
        (cx + 6, cy + 4),
    ]
    draw.polygon(jet, fill=c)


def icon_chip(draw, box, c):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    draw.rectangle([cx - 14, cy - 14, cx + 14, cy + 14], outline=c, width=3)
    draw.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], outline=c, width=2)
    for d in (-9, 0, 9):
        draw.line([(cx + d, cy - 14), (cx + d, y0 + 3)], fill=c, width=3)
        draw.line([(cx + d, cy + 14), (cx + d, y1 - 3)], fill=c, width=3)
        draw.line([(cx - 14, cy + d), (x0 + 3, cy + d)], fill=c, width=3)
        draw.line([(cx + 14, cy + d), (x1 - 3, cy + d)], fill=c, width=3)


def icon_ball(draw, box, c):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = 20
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=3)
    pent = [(cx + 8 * math.cos(math.radians(-90 + 72 * k)),
             cy + 8 * math.sin(math.radians(-90 + 72 * k))) for k in range(5)]
    draw.polygon(pent, fill=c)
    for px, py in pent:
        ex = cx + (px - cx) / 8 * r
        ey = cy + (py - cy) / 8 * r
        draw.line([(px, py), (ex, ey)], fill=c, width=2)


STORIES = [
    ("WAR", (147, 50, 31), icon_wave,
     "Ukraine sinks Russian warship off Libya",
     "Sea drones hit the corvette Merkury near Benghazi, Kyiv says"),
    ("US POLITICS", (36, 80, 126), icon_dome,
     "Democrats clinch biggest House majority since 1992",
     "Recount win takes the party to at least 258 seats"),
    ("SPACE", (70, 58, 143), icon_satellite,
     "NATO vows space defence over Russian satellite fears",
     "Allies warn Moscow may launch a nuclear space weapon"),
    ("ASIA", (3, 105, 161), icon_jet,
     "South Korea scrambles jets as Russian warplanes enter air zone",
     "Seoul responds as bombers cross its air defence zone"),
    ("TECH", (15, 118, 110), icon_chip,
     "Nvidia rehires Jensen Huang as CEO",
     "Stunning reversal follows a Trump-backed push at the chip giant"),
    ("SPORT", (161, 98, 7), icon_ball,
     "US, Mexico, Costa Rica & Jamaica to host 2031 Women's World Cup",
     "FIFA also awards the 2035 edition to the UK"),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    margin = 48
    content_w = W - 2 * margin
    cx = W / 2

    # ---------------------------------------------------------- masthead
    f_kicker = font(SANS_BOLD, 27)
    draw_spaced(draw, cx, 34, "THE WORLD IN ONE PICTURE", f_kicker, INK, 7)
    draw.line([(margin, 82), (W - margin, 82)], fill=INK, width=2)

    f_day = font(SANS_BOLD, 34)
    draw_spaced(draw, cx, 96, "TUESDAY", f_day, ACCENT, 12)

    f_date = fit_font(draw, "24 NOVEMBER 2026", SERIF_BOLD, content_w, 118)
    date_s = "24 NOVEMBER 2026"
    dw = text_w(draw, date_s, f_date)
    draw.text((cx - dw / 2, 138), date_s, font=f_date, fill=INK)

    # double rule under the masthead
    draw.line([(margin, 246), (W - margin, 246)], fill=INK, width=6)
    draw.line([(margin, 258), (W - margin, 258)], fill=INK, width=2)

    # ---------------------------------------------------------- panels
    grid_top = 272
    grid_bottom = 952
    gap = 22
    cols, rows = 2, 3
    pw = (content_w - gap) // 2
    ph = (grid_bottom - grid_top - gap * (rows - 1)) // rows

    report = []
    for i, (tag, colour, icon, headline, detail) in enumerate(STORIES):
        r, c = divmod(i, cols)
        x0 = margin + c * (pw + gap)
        y0 = grid_top + r * (ph + gap)
        x1, y1 = x0 + pw, y0 + ph
        draw.rectangle([x0, y0, x1, y1], fill=PANEL_BG, outline=PANEL_EDGE, width=2)

        pad = 20
        ix0, ix1 = x0 + pad, x1 - pad
        inner_w = ix1 - ix0

        # category tag chip
        f_tag = font(SANS_BOLD, 20)
        tag_w = text_w(draw, tag, f_tag) + 22
        draw.rectangle([ix0, y0 + 16, ix0 + tag_w, y0 + 48], fill=colour)
        draw.text((ix0 + 11, y0 + 22), tag, font=f_tag, fill=(255, 255, 255))

        # icon, top-right
        icon(draw, (x1 - 76, y0 + 10, x1 - 16, y0 + 62), colour)

        # headline: largest serif bold that wraps to <= 3 lines
        size = 35
        while size > 22:
            f_h = font(SERIF_BOLD, size)
            lines = wrap(draw, headline, f_h, inner_w)
            if len(lines) <= 3:
                break
            size -= 1
        lh = int(size * 1.13)
        hy = y0 + 56
        for ln in lines:
            draw.text((ix0, hy), ln, font=f_h, fill=INK)
            hy += lh

        # detail line(s): shrink until the whole panel fits
        dsize = 19
        while dsize > 15:
            f_d = font(SANS, dsize)
            dlines = wrap(draw, detail, f_d, inner_w)
            if hy + 6 + len(dlines) * (dsize + 4) <= y1 - 8:
                break
            dsize -= 1
        dy = hy + 6
        for ln in dlines:
            draw.text((ix0, dy), ln, font=f_d, fill=DETAIL_INK)
            dy += dsize + 4

        used_bottom = dy
        report.append(
            f"panel {i + 1} ({tag}): headline {size}px x{len(lines)} lines, "
            f"detail x{len(dlines)}, content ends y={used_bottom}, panel bottom y={y1}"
        )
        assert used_bottom <= y1 - 8, f"panel {i + 1} overflows: {used_bottom} > {y1 - 8}"
        for ln in lines:
            assert text_w(draw, ln, f_h) <= inner_w

    # ---------------------------------------------------------- footer
    draw.line([(margin, 966), (W - margin, 966)], fill=INK, width=2)
    f_foot = font(SERIF, 23)
    foot = "The day's biggest stories · Tuesday 24 November 2026"
    fw = text_w(draw, foot, f_foot)
    draw.text((cx - fw / 2, 978), foot, font=f_foot, fill=INK)

    img.save(OUT, optimize=True)
    size = os.path.getsize(OUT)
    for line in report:
        print(line)
    print(f"saved {OUT}: {img.size[0]}x{img.size[1]}, {size} bytes "
          f"({size / 1048576:.3f} MiB)")
    assert size <= 1048576, "PNG over 1 MiB"


if __name__ == "__main__":
    main()
