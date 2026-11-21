#!/usr/bin/env python3
"""THE WORLD TODAY - Friday 20 November 2026, on one page.

A program that draws a one-page newspaper front page summing up the
world's news of Friday 20 November 2026: 40 stories (3 big, 12 small
in a 4-per-row grid) with flat vector illustrations drawn in code,
a world map drawn from real longitude/latitude outlines, and the
remaining 25 stories as a two-column list with coloured bullets.

Python 3.13, standard library only. No network, no clock, no randomness.
Two runs write byte-identical files.
"""

import os
import struct
import zlib

W, H = 768, 1024

# ---------------------------------------------------------------- palette
PAPER_TOP = (250, 242, 226)
PAPER_BOT = (250, 242, 226)
INK = (30, 36, 48)
NAVY = (28, 58, 96)
GREEN_DARK = (25, 80, 65)
RED = (179, 39, 46)
GOLD = (232, 180, 40)
CREAM = (255, 255, 255)
ROSE = (242, 218, 140)
OCEAN = (110, 165, 210)
GRID = (200, 210, 220)
BOX = (120, 120, 128)

REGION = {
    "ASIA": (205, 60, 60),
    "EUROPE": (60, 110, 190),
    "MIDEAST": (185, 130, 40),
    "AMERICAS": (50, 150, 85),
    "AFRICA": (175, 110, 55),
    "OCEANIA": (135, 95, 180),
    "GLOBAL": (40, 65, 100),
}
REGION_NAME = {
    "ASIA": "ASIA", "EUROPE": "EUROPE", "MIDEAST": "MIDEAST",
    "AMERICAS": "AMERICAS", "AFRICA": "AFRICA", "OCEANIA": "OCEANIA",
    "GLOBAL": "GLOBAL",
}


# ------------------------------------------------------------------- font
# Fresh 5x7 bitmap font, drawn for this entry: a clean sans-serif in the
# spirit of Arial (straight strokes, no serifs, no handwriting hooks).
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is empty. Lowercase
# bowls sit at x-height (rows 2-4) with descenders in rows 5-6, so g, p,
# q and y read as lowercase and never as capitals mid-word.
FONT = {
" ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
"A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
"C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
"D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
"E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
"F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
"G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
"H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"I": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
"J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
"K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
"L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
"M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
"N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
"O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
"Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
"R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
"S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
"T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
"U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
"X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
"Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
"Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
"0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
"1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
"2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
"3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
"4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
"5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
"6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
"7": ("#####", "....#", "....#", "...#.", "...#.", "..#..", "..#.."),
"8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
"9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
"a": (".....", ".....", ".###.", "#...#", ".####", "#...#", ".###."),
"b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
"c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
"d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
"e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
"f": ("..##.", "..#..", "..#..", "####.", "..#..", "..#..", "..#.."),
"g": (".....", ".....", ".###.", "#...#", ".###.", "....#", ".###."),
"h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
"i": ("..#..", ".....", "..#..", "..#..", "..#..", "..#..", "..#.."),
"j": ("...#.", ".....", "...#.", "...#.", "...#.", "#..#.", ".##.."),
"k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
"l": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
"m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
"n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
"o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
"p": (".....", ".....", "####.", "#...#", "####.", "#....", "#...."),
"q": (".....", ".....", ".###.", "#...#", ".####", "....#", "....#"),
"r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
"s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
"t": ("..#..", "..#..", "####.", "..#..", "..#..", "..#..", "..##."),
"u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
"v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
"x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
"y": (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
"z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
";": (".....", ".##..", ".....", ".##..", ".##..", "..#..", ".#..."),
":": (".....", ".##..", ".....", ".....", ".##..", ".....", "....."),
"!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
"?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
"'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
"\u2019": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
'"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
"\u201c": (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
"\u201d": (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
"-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
"\u2013": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
"\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
"(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
"/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
"%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
"$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
"&": (".###.", "#...#", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
"+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
"@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
"*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
"#": ("#.#.#", "#.#.#", "#####", "#.#.#", "#####", "#.#.#", "#.#.#"),
"=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
"_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
"\u00a3": ("..#..", ".#.#.", ".#...", "####.", ".#...", "#.#..", ".###."),
"\u20ac": (".###.", "#....", "#....", "####.", "#....", "#....", ".###."),
}

CHAR_W = 6  # glyph cell width incl. 1px gap, at scale 1


def text_width(s, scale=1):
    return len(s) * CHAR_W * scale - scale


def draw_text(img, x, y, s, scale=1, color=INK):
    """Draw s at (x, y); top-left of the first glyph cell."""
    cx = x
    for ch in s:
        g = FONT.get(ch)
        if g is None:
            cx += CHAR_W * scale
            continue
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == "#":
                    img.rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += CHAR_W * scale


def draw_text_bold(img, x, y, s, scale=1, color=INK):
    """Draw s twice, 1px apart, for a bolder stroke."""
    draw_text(img, x, y, s, scale, color)
    draw_text(img, x + 1, y, s, scale, color)


def wrap_text(s, max_w, scale=1):
    """Split s into lines that fit max_w pixels at the given scale."""
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Img:
    def __init__(self, w, h, top, bot):
        self.w, self.h = w, h
        self.pix = bytearray(w * h * 3)
        for y in range(h):
            t = y / max(1, h - 1)
            r = round(top[0] + (bot[0] - top[0]) * t)
            g = round(top[1] + (bot[1] - top[1]) * t)
            b = round(top[2] + (bot[2] - top[2]) * t)
            base = y * w * 3
            for x in range(w):
                o = base + x * 3
                self.pix[o] = r
                self.pix[o + 1] = g
                self.pix[o + 2] = b

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (y * self.w + x) * 3
            self.pix[o] = c[0]
            self.pix[o + 1] = c[1]
            self.pix[o + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            o = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.pix[o] = c[0]
                self.pix[o + 1] = c[1]
                self.pix[o + 2] = c[2]
                o += 3

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        if fill:
            for dy in range(-r, r + 1):
                dx = int((r * r - dy * dy) ** 0.5)
                self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)
        else:
            for a in range(360):
                import math
                x = round(cx + r * math.cos(math.radians(a)))
                y = round(cy + r * math.sin(math.radians(a)))
                self.set(x, y, c)

    def poly(self, pts, c):
        """Fill a polygon (scanline fill)."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    def ring(self, cx, cy, r, c, w=2):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in (cx - dx, cx + dx):
                for k in range(w):
                    self.set(xx - k if xx < cx else xx + k, cy + dy, c)


def write_png(img, path):
    raw = bytearray()
    stride = img.w * 3
    for y in range(img.h):
        raw.append(0)
        raw += img.pix[y * stride:(y + 1) * stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", img.w, img.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------ illustrations
# Every scene is drawn from shapes only - no text inside any picture,
# so nothing can come out garbled. Each takes the box it may use.
SKY = (150, 195, 235)
PALE = (255, 240, 180)
SAND = (240, 200, 120)
SEA = (40, 120, 200)


def scene_strike(img, x, y, w, h):
    # night sky over Kyiv: gradient dusk, moon, stars, missile streaks,
    # layered explosions and a lit skyline with searchlights
    for i, band in enumerate(((18, 22, 48), (24, 30, 62), (32, 38, 74), (40, 46, 84))):
        img.rect(x, y + i * h // 4, w, h // 4 + 1, band)
    # moon with a soft halo, top right
    mx, my = x + int(w * 0.82), y + int(h * 0.16)
    img.circle(mx, my, 12, (255, 240, 190))
    img.circle(mx, my, 8, (255, 250, 220))
    img.circle(mx - 2, my - 2, 3, (235, 220, 180))
    # stars, varied sizes
    for sx, sy, r in ((0.08, 0.10, 2), (0.22, 0.06, 1), (0.38, 0.12, 2), (0.55, 0.07, 1),
                      (0.68, 0.14, 2), (0.92, 0.08, 1), (0.12, 0.28, 1), (0.48, 0.22, 1),
                      (0.74, 0.26, 1), (0.30, 0.32, 1)):
        img.circle(x + int(w * sx), y + int(h * sy), r, (255, 255, 255))
    # searchlight beams rising from the rooftops
    for bx in (0.18, 0.72):
        img.line(x + int(w * bx), y + h, x + int(w * (bx - 0.10)), y + int(h * 0.30), (255, 240, 180))
        img.line(x + int(w * bx), y + h, x + int(w * (bx - 0.08)), y + int(h * 0.30), (255, 240, 180))
    # missile streaks: long trails with bright glowing heads
    for sx, sy, ln in ((0.16, 0.34, 0.24), (0.50, 0.20, 0.28), (0.78, 0.38, 0.20)):
        hx, hy = x + int(w * sx), y + int(h * sy)
        img.line(hx, hy, hx - int(w * ln), hy + int(h * 0.14), (255, 190, 80))
        img.line(hx, hy, hx - int(w * ln), hy + int(h * 0.14) + 1, (255, 220, 140))
        img.circle(hx, hy, 5, (255, 240, 180))
        img.circle(hx, hy, 2, (255, 255, 255))
    # explosions: layered glow (outer haze, orange, yellow core, white heart)
    for ex, ey, r in ((0.28, 0.66, 13), (0.64, 0.58, 15), (0.86, 0.70, 10)):
        cx, cy = x + int(w * ex), y + int(h * ey)
        img.circle(cx, cy, r + 6, (255, 120, 40))
        img.circle(cx, cy, r, (255, 150, 50))
        img.circle(cx, cy, r * 2 // 3, (255, 210, 90))
        img.circle(cx, cy, r // 3, (255, 250, 200))
    # skyline: varied rooftops with lit windows and antennas
    for i, (bw, bh) in enumerate(((0.20, 0.30), (0.22, 0.42), (0.18, 0.34), (0.20, 0.46), (0.16, 0.28))):
        bx = x + int(w * (0.02 + 0.195 * i))
        img.rect(bx, y + h - int(h * bh), int(w * bw), int(h * bh), (45, 50, 70))
        img.rect(bx, y + h - int(h * bh), int(w * bw), 2, (70, 76, 100))
        for wy in range(2):
            for wx in range(2):
                img.rect(bx + 5 + wx * 12, y + h - int(h * bh) + 8 + wy * 14, 4, 5, (255, 220, 120))
        if i in (1, 3):
            img.rect(bx + int(w * bw) // 2, y + h - int(h * bh) - 10, 2, 10, (70, 76, 100))
            img.circle(bx + int(w * bw) // 2 + 1, y + h - int(h * bh) - 11, 2, (255, 80, 80))
    # smoke puffs drifting above the fires
    for dx, dy, r in ((0.28, 0.52, 10), (0.64, 0.44, 12), (0.86, 0.58, 8), (0.40, 0.48, 7)):
        img.circle(x + int(w * dx), y + int(h * dy), r, (110, 110, 125))
        img.circle(x + int(w * dx) - 3, y + int(h * dy) - 3, r // 2, (130, 130, 145))
    img.rect(x, y + int(h * 0.94), w, int(h * 0.06), (179, 39, 46))


def scene_cyclone(img, x, y, w, h):
    # a cyclone churning over the Bay of Bengal: spiral bands, a calm
    # eye, towering clouds, a rough sea and a bending palm
    for i, band in enumerate(((170, 210, 245), (150, 195, 240), (130, 180, 235), (110, 165, 225))):
        img.rect(x, y + i * h // 4, w, h // 4 + 1, band)
    cx, cy = x + w // 2, y + int(h * 0.40)
    # spiral arms: thick curved bands winding into the eye
    for k in range(1, 5):
        r = int(h * 0.09 * k)
        img.ring(cx, cy, r, (255, 255, 255), 4)
    for a0 in (20, 110, 200, 290):
        import math
        for k in range(1, 4):
            r = int(h * 0.09 * k)
            ax = cx + int(r * math.cos(math.radians(a0 + k * 25)))
            ay = cy + int(r * math.sin(math.radians(a0 + k * 25)))
            img.circle(ax, ay, 4, (255, 255, 255))
    # the eye: bright centre ringed in dark cloud
    img.circle(cx, cy, int(h * 0.08), (70, 100, 140))
    img.circle(cx, cy, int(h * 0.05), (240, 245, 255))
    # cloud banks at the edges
    for ccx, ccy, cr in ((0.08, 0.12, 12), (0.22, 0.08, 9), (0.85, 0.10, 11), (0.94, 0.20, 8)):
        img.circle(x + int(w * ccx), y + int(h * ccy), cr, (255, 255, 255))
        img.circle(x + int(w * ccx) + 8, y + int(h * ccy) + 3, cr - 3, (245, 245, 255))
    # rough sea with whitecaps
    img.rect(x, y + int(h * 0.76), w, int(h * 0.24), (25, 90, 170))
    img.rect(x, y + int(h * 0.76), w, 3, (120, 180, 230))
    for i in range(6):
        px = x + int(w * (0.05 + 0.17 * i))
        py = y + int(h * (0.82 + 0.05 * (i % 2)))
        img.line(px, py, px + 14, py + 4, (255, 255, 255))
        img.line(px + 4, py + 8, px + 18, py + 12, (200, 225, 245))
    # a palm bending hard in the wind, on a small strip of shore
    img.rect(x, y + int(h * 0.74), int(w * 0.30), int(h * 0.04), (210, 180, 120))
    img.line(x + int(w * 0.14), y + int(h * 0.76), x + int(w * 0.11), y + int(h * 0.56), (120, 82, 52))
    img.line(x + int(w * 0.11), y + int(h * 0.56), x + int(w * 0.04), y + int(h * 0.50), (30, 132, 73))
    img.line(x + int(w * 0.11), y + int(h * 0.56), x + int(w * 0.18), y + int(h * 0.50), (30, 132, 73))
    img.line(x + int(w * 0.11), y + int(h * 0.56), x + int(w * 0.11), y + int(h * 0.46), (30, 132, 73))
    img.line(x + int(w * 0.11), y + int(h * 0.56), x + int(w * 0.16), y + int(h * 0.60), (30, 132, 73))
    # driving rain, slanted
    for i in range(8):
        rx = x + int(w * (0.08 + 0.12 * i))
        ry = y + int(h * (0.04 + 0.06 * (i % 3)))
        img.line(rx, ry, rx - 4, ry + 10, (200, 220, 245))


def scene_globe(img, x, y, w, h):
    # a warming earth for COP31: a blue globe with continents, cloud
    # wisps, a radiant sun and a young sprout at its base
    for i, band in enumerate(((205, 228, 245), (215, 233, 248), (225, 238, 250), (235, 242, 252))):
        img.rect(x, y + i * h // 4, w, h // 4 + 1, band)
    # sun with rays, top right
    sx, sy = x + int(w * 0.80), y + int(h * 0.16)
    for a in range(0, 360, 30):
        import math
        ex = sx + int(16 * math.cos(math.radians(a)))
        ey = sy + int(16 * math.sin(math.radians(a)))
        img.line(sx, sy, ex, ey, (255, 200, 60))
    img.circle(sx, sy, 10, (255, 205, 70))
    img.circle(sx, sy, 6, (255, 225, 130))
    cx, cy = x + int(w * 0.45), y + int(h * 0.50)
    r = int(h * 0.34)
    # soft shadow under the globe
    img.circle(cx, cy + int(h * 0.42), int(r * 0.85), (200, 215, 230))
    # the globe: deep blue sea, green continents, white cloud wisps
    img.circle(cx, cy, r, (35, 110, 195))
    img.circle(cx - int(r * 0.38), cy - int(r * 0.28), int(r * 0.30), (55, 155, 85))
    img.circle(cx + int(r * 0.42), cy + int(r * 0.22), int(r * 0.24), (55, 155, 85))
    img.circle(cx + int(r * 0.05), cy - int(r * 0.58), int(r * 0.18), (80, 175, 100))
    img.circle(cx - int(r * 0.55), cy + int(r * 0.35), int(r * 0.16), (55, 155, 85))
    for ccx, ccy, cr in ((-0.30, -0.10, 7), (0.25, -0.42, 6), (0.45, 0.05, 5), (-0.05, 0.45, 6)):
        img.circle(cx + int(r * ccx), cy + int(r * ccy), cr, (255, 255, 255))
    img.ring(cx, cy, r, (255, 255, 255), 2)
    img.ring(cx, cy, r + 3, (180, 210, 235), 1)
    # a young sprout with two leaves at the base of the globe
    px = x + int(w * 0.45)
    img.line(px, y + int(h * 0.92), px, y + int(h * 0.80), (30, 132, 73))
    img.poly([(px, y + int(h * 0.86)), (px - 16, y + int(h * 0.78)), (px - 4, y + int(h * 0.74))], (40, 160, 80))
    img.poly([(px, y + int(h * 0.84)), (px + 16, y + int(h * 0.76)), (px + 4, y + int(h * 0.72))], (50, 175, 90))
    img.rect(x + int(w * 0.08), y + int(h * 0.94), int(w * 0.84), 3, (30, 132, 73))
    # small birds in the sky
    for bx, by in ((0.14, 0.14), (0.24, 0.20), (0.62, 0.10)):
        px, py = x + int(w * bx), y + int(h * by)
        img.line(px - 4, py, px, py - 3, (90, 110, 140))
        img.line(px, py - 3, px + 4, py, (90, 110, 140))


def scene_summit(img, x, y, w, h):
    # UK and EU flags behind a table, two seated figures in talks
    for i, band in enumerate(((150, 195, 235), (165, 205, 240), (180, 215, 245))):
        img.rect(x, y + i * h // 3, w, h // 3 + 1, band)
    # UK flag (Union Jack) on the left, EU flag on the right
    for fx, flag in ((0.12, "uk"), (0.62, "eu")):
        px = x + int(w * fx)
        img.rect(px, y + int(h * 0.10), 3, int(h * 0.48), INK)
        fw = int(w * 0.22)
        if flag == "uk":
            img.rect(px + 3, y + int(h * 0.10), fw, int(h * 0.20), (0, 36, 125))
            img.rect(px + 3, y + int(h * 0.10) + int(h * 0.08), fw, int(h * 0.04), (255, 255, 255))
            img.rect(px + 3 + int(fw * 0.40), y + int(h * 0.10), int(fw * 0.20), int(h * 0.20), (255, 255, 255))
            img.rect(px + 3, y + int(h * 0.10) + int(h * 0.09), fw, 2, (200, 16, 46))
            img.rect(px + 3 + int(fw * 0.45), y + int(h * 0.10), 2, int(h * 0.20), (200, 16, 46))
        else:
            img.rect(px + 3, y + int(h * 0.10), fw, int(h * 0.20), (0, 51, 153))
            for a in range(0, 360, 30):
                import math
                sx = px + 3 + fw // 2 + int(8 * math.cos(math.radians(a)))
                sy = y + int(h * 0.20) + int(5 * math.sin(math.radians(a)))
                img.circle(sx, sy, 1, (255, 215, 0))
    # table with papers and two microphones
    img.rect(x + int(w * 0.06), y + int(h * 0.66), int(w * 0.88), int(h * 0.28), (120, 50, 40))
    img.rect(x + int(w * 0.06), y + int(h * 0.66), int(w * 0.88), 3, (150, 110, 70))
    img.rect(x + int(w * 0.12), y + int(h * 0.70), int(w * 0.16), int(h * 0.10), (255, 255, 255))
    img.rect(x + int(w * 0.72), y + int(h * 0.70), int(w * 0.16), int(h * 0.10), (255, 255, 255))
    for i, suit in enumerate(((27, 42, 74), (0, 51, 153))):
        cx = x + int(w * (0.30 + 0.40 * i))
        img.circle(cx, y + int(h * 0.48), int(h * 0.12), (233, 196, 164))
        img.poly([(cx - int(w * 0.11), y + int(h * 0.66)), (cx + int(w * 0.11), y + int(h * 0.66)),
                  (cx + int(w * 0.07), y + int(h * 0.56)), (cx - int(w * 0.07), y + int(h * 0.56))], suit)
        mx = cx + int(w * 0.08)
        img.line(mx, y + int(h * 0.66), mx, y + int(h * 0.56), (40, 40, 48))
        img.circle(mx, y + int(h * 0.55), 3, (40, 40, 48))
    img.rect(x + int(w * 0.06), y + int(h * 0.94), int(w * 0.88), int(h * 0.06), (179, 39, 46))


def scene_tanker(img, x, y, w, h):
    # a tanker at sea in the strait, a mine below and a flame on the water
    for i, band in enumerate(((255, 200, 140), (255, 190, 120), (250, 180, 110))):
        img.rect(x, y + i * h // 3, w, h // 3 + 1, band)
    img.circle(x + int(w * 0.82), y + int(h * 0.16), int(h * 0.14), (255, 220, 120))
    img.circle(x + int(w * 0.82), y + int(h * 0.16), int(h * 0.09), (255, 235, 170))
    img.rect(x, y + int(h * 0.62), w, int(h * 0.38), SEA)
    img.rect(x, y + int(h * 0.62), w, 3, (140, 190, 235))
    for i in range(5):
        px = x + int(w * (0.04 + 0.20 * i))
        img.line(px, y + int(h * 0.68), px + 12, y + int(h * 0.74), (255, 255, 255))
        img.line(px + 8, y + int(h * 0.86), px + 20, y + int(h * 0.92), (200, 225, 245))
    # hull and deck, red with a white stripe and containers
    hx = x + int(w * 0.08)
    img.rect(hx, y + int(h * 0.44), int(w * 0.72), int(h * 0.20), (140, 30, 30))
    img.rect(hx, y + int(h * 0.44), int(w * 0.72), 3, (255, 255, 255))
    img.rect(hx + int(w * 0.56), y + int(h * 0.26), int(w * 0.16), int(h * 0.20), (230, 230, 235))
    img.rect(hx + int(w * 0.58), y + int(h * 0.20), 4, int(h * 0.08), (60, 60, 70))
    for i in range(4):
        img.rect(hx + int(w * (0.12 + 0.15 * i)), y + int(h * 0.48), int(w * 0.10), int(h * 0.12), (90, 30, 30))
    # a mine just under the surface, spiked, with a flame above it
    mx, my = x + int(w * 0.88), y + int(h * 0.70)
    img.circle(mx, my, 6, (40, 40, 48))
    for ang in range(0, 360, 45):
        import math
        ex = mx + int(9 * math.cos(math.radians(ang)))
        ey = my + int(9 * math.sin(math.radians(ang)))
        img.line(mx, my, ex, ey, (40, 40, 48))
    img.circle(mx, y + int(h * 0.56), 6, (255, 140, 40))
    img.circle(mx, y + int(h * 0.54), 3, (255, 220, 120))
    img.circle(mx, y + int(h * 0.52), 2, (255, 255, 255))


def scene_police(img, x, y, w, h):
    # a night street raid: dark buildings, a police car light bar, a shield
    for i, band in enumerate(((38, 46, 68), (44, 52, 76), (50, 58, 84))):
        img.rect(x, y + i * h // 3, w, h // 3 + 1, band)
    for i, (bw, bh) in enumerate(((0.24, 0.38), (0.26, 0.52), (0.22, 0.44), (0.20, 0.34))):
        bx = x + int(w * (0.04 + 0.24 * i))
        img.rect(bx, y + h - int(h * bh), int(w * bw), int(h * bh), (68, 76, 98))
        for wy in range(3):
            img.rect(bx + 4, y + h - int(h * bh) + 6 + wy * 12, 4, 5, (255, 220, 120))
    img.rect(x, y + int(h * 0.80), w, int(h * 0.20), (22, 26, 38))
    img.line(x, y + int(h * 0.80), x + w, y + int(h * 0.80), (90, 95, 115))
    # police car: body, windows, light bar flashing red and blue
    cx = x + int(w * 0.50)
    img.rect(cx - int(w * 0.32), y + int(h * 0.64), int(w * 0.64), int(h * 0.16), (230, 230, 235))
    img.rect(cx - int(w * 0.32), y + int(h * 0.64), int(w * 0.64), 3, (255, 255, 255))
    img.rect(cx - int(w * 0.20), y + int(h * 0.54), int(w * 0.40), int(h * 0.12), (200, 200, 210))
    img.rect(cx - int(w * 0.20), y + int(h * 0.54), int(w * 0.40), 2, (255, 255, 255))
    img.rect(cx - int(w * 0.14), y + int(h * 0.50), int(w * 0.12), 4, (220, 30, 30))
    img.rect(cx + int(w * 0.02), y + int(h * 0.50), int(w * 0.12), 4, (30, 90, 220))
    img.circle(cx - int(w * 0.22), y + int(h * 0.80), 6, (30, 30, 36))
    img.circle(cx + int(w * 0.22), y + int(h * 0.80), 6, (30, 30, 36))
    img.circle(cx - int(w * 0.22), y + int(h * 0.80), 2, (120, 120, 130))
    img.circle(cx + int(w * 0.22), y + int(h * 0.80), 2, (120, 120, 130))
    # a shield emblem above the car
    img.poly([(cx, y + int(h * 0.32)), (cx + 12, y + int(h * 0.24)), (cx + 12, y + int(h * 0.38)),
              (cx, y + int(h * 0.46)), (cx - 12, y + int(h * 0.38)), (cx - 12, y + int(h * 0.24))], (255, 200, 0))
    img.poly([(cx, y + int(h * 0.30)), (cx + 8, y + int(h * 0.26)), (cx + 8, y + int(h * 0.36)),
              (cx, y + int(h * 0.42)), (cx - 8, y + int(h * 0.36)), (cx - 8, y + int(h * 0.26))], (40, 48, 70))
    img.circle(cx, y + int(h * 0.33), 3, (255, 200, 0))


def scene_chart(img, x, y, w, h):
    # a market chart with rising bars and a red trend line
    img.rect(x, y, w, h, PALE)
    for gy in range(1, 4):
        yy = y + int(h * gy / 4)
        img.line(x + int(w * 0.10), yy, x + int(w * 0.92), yy, (220, 210, 180))
    img.line(x + int(w * 0.10), y + int(h * 0.85), x + int(w * 0.92), y + int(h * 0.85), INK)
    img.line(x + int(w * 0.10), y + int(h * 0.85), x + int(w * 0.10), y + int(h * 0.10), INK)
    bars = [0.20, 0.34, 0.48, 0.66]
    for i, b in enumerate(bars):
        bx = x + int(w * (0.18 + 0.18 * i))
        bh = int(h * b)
        col = (30, 120, 220) if i < 3 else (0, 180, 90)
        img.rect(bx, y + int(h * 0.85) - bh, int(w * 0.10), bh, col)
        img.rect(bx, y + int(h * 0.85) - bh, int(w * 0.10), 3, (255, 255, 255))
    img.line(x + int(w * 0.16), y + int(h * 0.68), x + int(w * 0.84), y + int(h * 0.16), (179, 39, 46))
    img.line(x + int(w * 0.84), y + int(h * 0.16), x + int(w * 0.74), y + int(h * 0.16), (179, 39, 46))
    img.line(x + int(w * 0.84), y + int(h * 0.16), x + int(w * 0.84), y + int(h * 0.26), (179, 39, 46))
    img.circle(x + int(w * 0.86), y + int(h * 0.12), 5, (255, 200, 0))
    img.circle(x + int(w * 0.86), y + int(h * 0.12), 2, (255, 255, 255))
    img.poly([(x + int(w * 0.12), y + int(h * 0.10)), (x + int(w * 0.16), y + int(h * 0.04)),
              (x + int(w * 0.20), y + int(h * 0.10))], (30, 132, 73))


def scene_tents(img, x, y, w, h):
    img.rect(x, y, w, h, (120, 180, 235))
    img.rect(x, y + int(h * 0.72), w, int(h * 0.28), SAND)
    for i, tc in enumerate(((255, 120, 40), (0, 165, 175), (255, 255, 255))):
        tx = x + int(w * (0.10 + 0.30 * i))
        tw = int(w * 0.26)
        img.poly([(tx, y + int(h * 0.72)), (tx + tw, y + int(h * 0.72)), (tx + tw // 2, y + int(h * 0.40))], tc)
        img.poly([(tx + tw // 2 - 5, y + int(h * 0.72)), (tx + tw // 2 + 5, y + int(h * 0.72)),
                  (tx + tw // 2, y + int(h * 0.56))], (120, 82, 52))
    img.rect(x + int(w * 0.72), y + int(h * 0.58), int(w * 0.18), int(h * 0.14), (150, 110, 70))
    img.rect(x + int(w * 0.79), y + int(h * 0.58), 3, int(h * 0.14), (255, 255, 255))
    img.rect(x + int(w * 0.72), y + int(h * 0.63), int(w * 0.18), 3, (255, 255, 255))
    img.circle(x + int(w * 0.50), y + int(h * 0.20), 8, (255, 200, 0))
    img.circle(x + int(w * 0.86), y + int(h * 0.14), 8, (255, 240, 180))
    img.circle(x + int(w * 0.88), y + int(h * 0.12), 7, (120, 180, 235))
    for i in range(5):
        img.rect(x + int(w * (0.05 + 0.18 * i)), y + int(h * 0.86), 2, int(h * 0.10), (120, 82, 52))
    img.rect(x + int(w * 0.03), y + int(h * 0.30), int(w * 0.04), int(h * 0.42), (190, 170, 140))
    img.circle(x + int(w * 0.05), y + int(h * 0.28), 4, (190, 170, 140))
    img.rect(x + int(w * 0.02), y + int(h * 0.38), int(w * 0.06), 3, (160, 140, 110))
    img.poly([(x + int(w * 0.55), y + int(h * 0.60)), (x + int(w * 0.69), y + int(h * 0.60)),
              (x + int(w * 0.62), y + int(h * 0.44))], (170, 110, 210))
    img.rect(x + int(w * 0.90), y + int(h * 0.58), int(w * 0.07), int(h * 0.14), (90, 110, 145))
    img.rect(x + int(w * 0.90), y + int(h * 0.58), int(w * 0.07), 3, (90, 110, 130))
    img.line(x + int(w * 0.38), y + int(h * 0.72), x + int(w * 0.38), y + int(h * 0.60), (120, 82, 52))
    img.circle(x + int(w * 0.38), y + int(h * 0.56), 5, (60, 140, 80))


def scene_plane(img, x, y, w, h):
    # a grey military jet over a runway, with clouds and a control tower
    for i, band in enumerate(((150, 195, 235), (165, 205, 240), (180, 215, 245))):
        img.rect(x, y + i * h // 3, w, h // 3 + 1, band)
    for ccx, ccy, cr in ((0.15, 0.18, 9), (0.35, 0.10, 11), (0.70, 0.16, 8), (0.88, 0.08, 10), (0.52, 0.22, 7)):
        img.circle(x + int(w * ccx), y + int(h * ccy), cr, (255, 255, 255))
    # control tower at the left
    img.rect(x + int(w * 0.06), y + int(h * 0.44), int(w * 0.06), int(h * 0.36), (90, 100, 120))
    img.rect(x + int(w * 0.04), y + int(h * 0.36), int(w * 0.10), int(h * 0.08), (70, 80, 100))
    img.rect(x + int(w * 0.05), y + int(h * 0.38), int(w * 0.08), 3, (255, 220, 120))
    # runway with centre line
    img.rect(x, y + int(h * 0.80), w, int(h * 0.20), (60, 60, 70))
    img.rect(x, y + int(h * 0.80), w, 2, (140, 140, 150))
    for i in range(6):
        img.rect(x + int(w * (0.06 + 0.17 * i)), y + int(h * 0.88), int(w * 0.08), 3, (255, 255, 255))
    # the jet, side on, nose to the right, with a contrail
    jx, jy = x + int(w * 0.30), y + int(h * 0.42)
    img.line(jx - int(w * 0.12), jy + 2, jx, jy + 2, (255, 255, 255))
    img.line(jx - int(w * 0.12), jy + 5, jx, jy + 5, (230, 230, 240))
    img.poly([(jx, jy), (jx + int(w * 0.42), jy - 4), (jx + int(w * 0.50), jy + 2),
              (jx + int(w * 0.42), jy + 8), (jx, jy + 6)], (120, 125, 135))
    img.poly([(jx, jy), (jx + int(w * 0.42), jy - 4), (jx + int(w * 0.50), jy + 2),
              (jx + int(w * 0.42), jy + 8), (jx, jy + 6)], (120, 125, 135))
    img.poly([(jx + int(w * 0.10), jy), (jx + int(w * 0.20), jy - int(h * 0.16)),
              (jx + int(w * 0.26), jy)], (90, 95, 105))
    img.poly([(jx + int(w * 0.30), jy + 6), (jx + int(w * 0.38), jy + int(h * 0.14)),
              (jx + int(w * 0.44), jy + 6)], (90, 95, 105))
    img.rect(jx + int(w * 0.34), jy - 2, int(w * 0.10), 4, (255, 220, 120))
    img.circle(jx - int(w * 0.02), jy + 3, 3, (255, 180, 60))


def scene_flags(img, x, y, w, h):
    # two flags (South Africa and Germany) over a table, a handshake below
    img.rect(x, y, w, h, PALE)
    img.rect(x, y + int(h * 0.78), w, 3, INK)
    for i, pole in enumerate((0.22, 0.66)):
        px = x + int(w * pole)
        img.rect(px, y + int(h * 0.16), 3, int(h * 0.62), INK)
        img.circle(px + 1, y + int(h * 0.15), 2, (255, 200, 0))
        fw = int(w * 0.24)
        if i == 0:
            img.rect(px + 3, y + int(h * 0.16), fw, int(h * 0.22), (65, 137, 221))
            img.rect(px + 3, y + int(h * 0.16), fw, int(h * 0.07), (255, 255, 255))
            img.rect(px + 3, y + int(h * 0.31), fw, int(h * 0.07), (255, 255, 255))
            img.circle(px + 3 + fw // 2, y + int(h * 0.27), 5, (255, 255, 255))
        else:
            img.rect(px + 3, y + int(h * 0.16), fw, int(h * 0.07), (0, 122, 61))
            img.rect(px + 3, y + int(h * 0.23), fw, int(h * 0.07), (255, 255, 255))
            img.rect(px + 3, y + int(h * 0.30), fw, int(h * 0.07), (0, 0, 0))
            img.rect(px + 3, y + int(h * 0.16), int(w * 0.05), int(h * 0.21), (200, 16, 46))
    # a handshake: two clasped hands over a document
    mx = x + w // 2
    img.circle(mx - 8, y + int(h * 0.52), 6, (233, 196, 164))
    img.circle(mx + 8, y + int(h * 0.52), 6, (222, 184, 150))
    img.line(mx - 2, y + int(h * 0.52), mx + 2, y + int(h * 0.52), (179, 39, 46))
    img.line(mx - 5, y + int(h * 0.44), mx + 5, y + int(h * 0.60), (200, 160, 120))
    img.rect(x + int(w * 0.38), y + int(h * 0.64), int(w * 0.24), int(h * 0.12), (255, 255, 255))
    img.rect(x + int(w * 0.38), y + int(h * 0.64), int(w * 0.24), 2, (179, 39, 46))
    img.rect(x + int(w * 0.40), y + int(h * 0.67), int(w * 0.20), 2, (180, 180, 190))
    img.rect(x + int(w * 0.40), y + int(h * 0.71), int(w * 0.20), 2, (180, 180, 190))


def scene_cricket(img, x, y, w, h):
    # a green outfield, a pitch strip, stumps, a bat and a red ball
    for i, band in enumerate(((140, 190, 240), (155, 200, 245), (170, 210, 248))):
        img.rect(x, y + i * h // 3, w, h // 3 + 1, band)
    img.circle(x + int(w * 0.88), y + int(h * 0.12), 7, (255, 220, 120))
    img.circle(x + int(w * 0.88), y + int(h * 0.12), 4, (255, 235, 170))
    img.rect(x, y + int(h * 0.60), w, int(h * 0.40), (60, 150, 80))
    img.rect(x, y + int(h * 0.60), w, 3, (255, 255, 255))
    # the pitch strip, lighter, with a crease line
    img.rect(x + int(w * 0.36), y + int(h * 0.60), int(w * 0.28), int(h * 0.40), (220, 200, 150))
    img.rect(x + int(w * 0.36), y + int(h * 0.60), int(w * 0.28), 2, (255, 255, 255))
    # stumps at each end
    for sx in (0.42, 0.58):
        for k in range(3):
            img.rect(x + int(w * sx) + k * 4, y + int(h * 0.64), 2, int(h * 0.12), (240, 220, 140))
        img.rect(x + int(w * sx), y + int(h * 0.64), 10, 2, (240, 220, 140))
    # a bat leaning on the stumps
    bx = x + int(w * 0.46)
    img.line(bx, y + int(h * 0.60), bx + 8, y + int(h * 0.42), (200, 170, 110))
    img.rect(bx + 6, y + int(h * 0.40), 6, int(h * 0.08), (200, 170, 110))
    # the red ball, high in the sky, with a motion arc
    img.circle(x + int(w * 0.72), y + int(h * 0.20), 6, (200, 30, 30))
    img.circle(x + int(w * 0.72), y + int(h * 0.20), 3, (255, 120, 120))
    for i, (ax, ay) in enumerate(((0.58, 0.30), (0.62, 0.26), (0.66, 0.23))):
        img.circle(x + int(w * ax), y + int(h * ay), 2, (255, 255, 255))
    # a fielder, small, at the boundary
    fx = x + int(w * 0.12)
    img.circle(fx, y + int(h * 0.70), 4, (233, 196, 164))
    img.rect(fx - 5, y + int(h * 0.74), 10, int(h * 0.14), (20, 40, 90))
    img.rect(fx - 5, y + int(h * 0.74), 10, 2, (255, 255, 255))


def scene_drone(img, x, y, w, h):
    # a drone over desert mountains, its target marker below
    for i, band in enumerate(((255, 195, 125), (255, 185, 105), (250, 175, 95))):
        img.rect(x, y + i * h // 3, w, h // 3 + 1, band)
    img.circle(x + int(w * 0.85), y + int(h * 0.14), 7, (255, 220, 120))
    img.poly([(x, y + h), (x + int(w * 0.32), y + int(h * 0.48)), (x + int(w * 0.58), y + h)], (120, 100, 80))
    img.poly([(x + int(w * 0.44), y + h), (x + int(w * 0.76), y + int(h * 0.58)), (x + w, y + h)], (100, 85, 68))
    img.poly([(x + int(w * 0.58), y + h), (x + int(w * 0.82), y + int(h * 0.70)), (x + w, y + h)], (135, 115, 95))
    # the drone, centre, with spinning rotors
    cx, cy = x + w // 2, y + int(h * 0.30)
    img.rect(cx - int(w * 0.09), cy - 5, int(w * 0.18), 10, (60, 60, 70))
    img.rect(cx - int(w * 0.09), cy - 5, int(w * 0.18), 3, (90, 90, 100))
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex, ey = cx + sx * int(w * 0.22), cy + sy * int(h * 0.16)
        img.line(cx, cy, ex, ey, (60, 60, 70))
        img.circle(ex, ey, 6, (90, 90, 100))
        img.line(ex - 11, ey, ex + 11, ey, (150, 150, 160))
    img.circle(cx, cy + 8, 3, (255, 80, 80))
    # target marker on the ground, with a blast glow
    tx, ty = cx, y + int(h * 0.80)
    for ang in range(0, 360, 45):
        import math
        ex = tx + int(13 * math.cos(math.radians(ang)))
        ey = ty + int(13 * math.sin(math.radians(ang)))
        img.line(tx, ty, ex, ey, (255, 140, 40))
    img.circle(tx, ty, 6, (255, 100, 30))
    img.circle(tx, ty, 3, (255, 220, 120))
    img.ring(tx, y + int(h * 0.90), 9, (255, 255, 255), 2)
    img.ring(tx, y + int(h * 0.90), 5, (255, 100, 30), 2)


def scene_chip(img, x, y, w, h):
    # a computer chip on a circuit board, for the DeepSeek funding story
    img.rect(x, y, w, h, (30, 40, 60))
    for i in range(5):
        img.rect(x + int(w * (0.08 + 0.18 * i)), y + int(h * 0.10), 2, int(h * 0.12), (0, 200, 120))
        img.rect(x + int(w * (0.08 + 0.18 * i)), y + int(h * 0.78), 2, int(h * 0.12), (0, 200, 120))
    for i in range(4):
        img.rect(x + int(w * 0.06), y + int(h * (0.18 + 0.20 * i)), int(w * 0.10), 2, (0, 200, 120))
        img.rect(x + int(w * 0.84), y + int(h * (0.18 + 0.20 * i)), int(w * 0.10), 2, (0, 200, 120))
    img.rect(x + int(w * 0.30), y + int(h * 0.28), int(w * 0.40), int(h * 0.44), (20, 60, 90))
    img.rect(x + int(w * 0.30), y + int(h * 0.28), int(w * 0.40), 3, (0, 200, 120))
    img.rect(x + int(w * 0.30), y + int(h * 0.69), int(w * 0.40), 3, (0, 200, 120))
    img.rect(x + int(w * 0.38), y + int(h * 0.40), int(w * 0.24), int(h * 0.20), (0, 200, 120))
    img.rect(x + int(w * 0.44), y + int(h * 0.46), int(w * 0.12), int(h * 0.08), (30, 40, 60))
    img.circle(x + int(w * 0.50), y + int(h * 0.50), 2, (255, 200, 0))
    for i in range(3):
        img.circle(x + int(w * (0.20 + 0.30 * i)), y + int(h * 0.88), 2, (255, 200, 0))


def scene_crate(img, x, y, w, h):
    # stacked munitions crates in a warehouse, one open with shells
    for i, band in enumerate(((200, 190, 160), (210, 200, 172), (220, 210, 184))):
        img.rect(x, y + i * h // 3, w, h // 3 + 1, band)
    img.rect(x, y + int(h * 0.76), w, int(h * 0.24), (120, 100, 70))
    img.line(x, y + int(h * 0.76), x + w, y + int(h * 0.76), (150, 130, 95))
    # three crates in front, with straps and stencil marks
    for i, (cx, cw) in enumerate(((0.06, 0.26), (0.36, 0.26), (0.66, 0.26))):
        bx = x + int(w * cx)
        bw = int(w * cw)
        img.rect(bx, y + int(h * 0.50), bw, int(h * 0.28), (150, 110, 60))
        img.rect(bx, y + int(h * 0.50), bw, 3, (100, 70, 30))
        img.rect(bx, y + int(h * 0.64), bw, 2, (100, 70, 30))
        img.rect(bx + bw // 2 - 1, y + int(h * 0.50), 2, int(h * 0.28), (100, 70, 30))
        img.rect(bx + 4, y + int(h * 0.56), 6, 4, (255, 220, 120))
    # open crate at the back, shells standing in it
    bx = x + int(w * 0.30)
    img.rect(bx, y + int(h * 0.28), int(w * 0.40), int(h * 0.24), (170, 130, 80))
    img.rect(bx, y + int(h * 0.28), int(w * 0.40), 3, (120, 90, 50))
    for i in range(5):
        sx = bx + 5 + i * 11
        img.rect(sx, y + int(h * 0.16), 6, int(h * 0.14), (90, 95, 105))
        img.poly([(sx, y + int(h * 0.16)), (sx + 3, y + int(h * 0.10)), (sx + 6, y + int(h * 0.16))], (60, 65, 75))
    img.rect(x + int(w * 0.06), y + int(h * 0.10), int(w * 0.20), 3, (90, 95, 105))
    img.circle(x + int(w * 0.85), y + int(h * 0.14), 5, (255, 200, 0))


def scene_down(img, x, y, w, h):
    # a market chart falling hard: red bars and a plunging arrow
    img.rect(x, y, w, h, PALE)
    for gy in range(1, 4):
        yy = y + int(h * gy / 4)
        img.line(x + int(w * 0.10), yy, x + int(w * 0.92), yy, (220, 210, 180))
    img.line(x + int(w * 0.10), y + int(h * 0.85), x + int(w * 0.92), y + int(h * 0.85), INK)
    img.line(x + int(w * 0.10), y + int(h * 0.85), x + int(w * 0.10), y + int(h * 0.10), INK)
    bars = [0.60, 0.46, 0.32, 0.16]
    for i, b in enumerate(bars):
        bx = x + int(w * (0.18 + 0.18 * i))
        bh = int(h * b)
        img.rect(bx, y + int(h * 0.85) - bh, int(w * 0.10), bh, (200, 40, 40))
        img.rect(bx, y + int(h * 0.85) - bh, int(w * 0.10), 3, (255, 120, 120))
    img.line(x + int(w * 0.16), y + int(h * 0.16), x + int(w * 0.84), y + int(h * 0.68), (179, 39, 46))
    img.line(x + int(w * 0.84), y + int(h * 0.68), x + int(w * 0.74), y + int(h * 0.68), (179, 39, 46))
    img.line(x + int(w * 0.84), y + int(h * 0.68), x + int(w * 0.84), y + int(h * 0.58), (179, 39, 46))
    img.circle(x + int(w * 0.86), y + int(h * 0.12), 5, (255, 200, 0))
    img.circle(x + int(w * 0.86), y + int(h * 0.12), 2, (255, 255, 255))
    img.rect(x + int(w * 0.10), y + int(h * 0.92), int(w * 0.80), 2, (200, 40, 40))


def scene_march(img, x, y, w, h):
    # a street protest: a crowd with placards under a grey sky
    for i, band in enumerate(((175, 185, 200), (185, 195, 210), (195, 205, 218))):
        img.rect(x, y + i * h // 3, w, h // 3 + 1, band)
    img.rect(x, y + int(h * 0.76), w, int(h * 0.24), (90, 90, 100))
    img.line(x, y + int(h * 0.76), x + w, y + int(h * 0.76), (120, 120, 130))
    # buildings behind the crowd
    for i, (bw, bh) in enumerate(((0.24, 0.32), (0.26, 0.44), (0.22, 0.36), (0.20, 0.28))):
        bx = x + int(w * (0.04 + 0.24 * i))
        img.rect(bx, y + int(h * 0.76) - int(h * bh), int(w * bw), int(h * bh), (120, 125, 140))
        for wy in range(2):
            img.rect(bx + 4, y + int(h * 0.76) - int(h * bh) + 6 + wy * 12, 4, 5, (255, 220, 120))
    # the crowd: heads and shoulders, varied
    for i in range(7):
        cx = x + int(w * (0.08 + 0.14 * i))
        img.circle(cx, y + int(h * 0.60), 5, (233, 196, 164) if i % 2 == 0 else (210, 175, 140))
        img.rect(cx - 7, y + int(h * 0.66), 14, int(h * 0.12), (40, 60, 120) if i % 3 == 0 else ((179, 39, 46) if i % 3 == 1 else (30, 120, 90)))
    # placards on sticks above the crowd
    for i, pc in enumerate(((255, 200, 0), (255, 255, 255), (255, 200, 0), (255, 255, 255))):
        px = x + int(w * (0.12 + 0.24 * i))
        img.rect(px, y + int(h * 0.28), 3, int(h * 0.34), (60, 60, 70))
        img.rect(px - 9, y + int(h * 0.20), 21, int(h * 0.10), pc)
        img.rect(px - 9, y + int(h * 0.20), 21, 2, INK)
        img.rect(px - 9, y + int(h * 0.20) + int(h * 0.10) - 2, 21, 2, INK)
    img.circle(x + int(w * 0.86), y + int(h * 0.10), 6, (255, 220, 120))


def scene_radar(img, x, y, w, h):
    # a radar screen sweeping the sky, with blips and warning lights
    img.rect(x, y, w, h, (18, 38, 28))
    cx, cy = x + w // 2, y + int(h * 0.48)
    for k in range(1, 4):
        r = int(h * 0.11 * k)
        img.ring(cx, cy, r, (0, 200, 120), 2)
    img.line(cx, cy, cx, cy - int(h * 0.34), (0, 200, 120))
    img.line(cx, cy, cx - int(w * 0.30), cy, (0, 200, 120))
    img.line(cx, cy, cx + int(w * 0.30), cy + int(h * 0.12), (0, 200, 120))
    # the sweep line, bright, with a fading trail
    img.line(cx, cy, cx + int(w * 0.28), cy - int(h * 0.28), (0, 255, 150))
    img.line(cx, cy, cx + int(w * 0.20), cy - int(h * 0.20), (0, 220, 140))
    # blips: one red (the object), one white
    img.circle(cx + int(w * 0.20), cy - int(h * 0.20), 4, (255, 80, 80))
    img.circle(cx + int(w * 0.20), cy - int(h * 0.20), 2, (255, 255, 255))
    img.circle(cx - int(w * 0.14), cy + int(h * 0.12), 3, (255, 255, 255))
    img.circle(cx, cy, 3, (0, 255, 150))
    # warning lights at the base
    for i, lc in enumerate(((255, 200, 0), (255, 80, 80), (255, 200, 0))):
        img.circle(x + int(w * (0.20 + 0.30 * i)), y + int(h * 0.88), 4, lc)
        img.circle(x + int(w * (0.20 + 0.30 * i)), y + int(h * 0.88), 2, (255, 255, 255))
    img.rect(x + int(w * 0.08), y + int(h * 0.94), int(w * 0.84), 2, (0, 200, 120))


def scene_podium(img, x, y, w, h):
    # a White House briefing: a speaker at a podium with the seal,
    # two microphones, and a US flag behind
    img.rect(x, y, w, h, NAVY)
    # curtain folds, slightly darker
    for i in range(6):
        fx = x + int(w * (0.05 + 0.16 * i))
        img.rect(fx, y, 2, h, (20, 45, 78))
    # US flag on a pole, left
    px = x + int(w * 0.10)
    img.rect(px, y + int(h * 0.10), 2, int(h * 0.55), (220, 220, 220))
    img.circle(px + 1, y + int(h * 0.09), 2, (255, 200, 0))
    fw, fh = int(w * 0.22), int(h * 0.30)
    for i in range(5):
        img.rect(px + 2, y + int(h * 0.10) + i * (fh // 5), fw, fh // 5 + 1,
                 (200, 40, 40) if i % 2 == 0 else (255, 255, 255))
    img.rect(px + 2, y + int(h * 0.10), fw // 2, fh // 2, (30, 60, 140))
    # the speaker: head and shoulders behind the podium
    cx = x + w // 2
    img.rect(cx - int(w * 0.20), y + int(h * 0.42), int(w * 0.40), int(h * 0.22), (30, 36, 48))
    img.rect(cx - 3, y + int(h * 0.42), 6, int(h * 0.10), (255, 255, 255))
    img.rect(cx - 2, y + int(h * 0.44), 4, int(h * 0.18), (179, 39, 46))
    img.circle(cx, y + int(h * 0.30), int(h * 0.13), (233, 196, 164))
    # blond hair, swept back
    img.rect(cx - int(h * 0.13), y + int(h * 0.18), int(h * 0.26), int(h * 0.06), (235, 215, 160))
    # two microphones leaning in
    for sx in (-1, 1):
        img.line(cx + sx * int(w * 0.16), y + int(h * 0.52), cx + sx * 6, y + int(h * 0.40), (200, 200, 210))
        img.circle(cx + sx * 6, y + int(h * 0.40), 3, (40, 40, 45))
    # the podium, dark wood with the gold seal
    img.rect(cx - int(w * 0.30), y + int(h * 0.60), int(w * 0.60), int(h * 0.40), (70, 50, 35))
    img.rect(cx - int(w * 0.30), y + int(h * 0.60), int(w * 0.60), 3, (110, 80, 50))
    img.ring(cx, y + int(h * 0.76), 8, (255, 200, 0), 2)
    img.circle(cx, y + int(h * 0.76), 5, (255, 255, 255))
    img.circle(cx, y + int(h * 0.76), 2, (30, 60, 140))


SCENES = {
    "strike": scene_strike, "cyclone": scene_cyclone, "globe": scene_globe,
    "summit": scene_summit, "tanker": scene_tanker, "police": scene_police,
    "chart": scene_chart, "tents": scene_tents, "plane": scene_plane,
    "flags": scene_flags, "cricket": scene_cricket, "drone": scene_drone,
    "chip": scene_chip, "crate": scene_crate, "down": scene_down,
    "march": scene_march, "radar": scene_radar, "podium": scene_podium,
}


def tint(c, f=0.85):
    """Lighten a colour toward white (f = fraction of white)."""
    return (round(c[0] + (255 - c[0]) * f), round(c[1] + (255 - c[1]) * f),
            round(c[2] + (255 - c[2]) * f))


def pill(img, x, y, w, h, c):
    """A filled pill (rounded rectangle) with radius h/2."""
    r = h // 2
    img.rect(x + r, y, w - 2 * r, h, c)
    img.circle(x + r, y + r, r, c)
    img.circle(x + w - r - 1, y + r, r, c)


# The map is navy and cream: a navy ocean, cream land; the region
# colours live only in the markers, so the numbers stay readable.
MAP_OCEAN = (28, 58, 96)
MAP_LAND = (245, 235, 205)
MAP_GRID = (90, 110, 140)

# Local time each main story broke, Friday 20 November 2026 (researched).
# Brussels and Jazan are approximate (mid-morning / publication time).
CLOCKS = [
    ("KYIV", 1, 25), ("ODISHA", 7, 30), ("HORMUZ", 3, 41),
    ("SYDNEY", 5, 50), ("TAIPEI", 9, 0), ("BRUSSELS", 10, 0),
    ("TOKYO", 15, 0), ("WARSAW", 7, 30), ("JAZAN", 6, 30),
    ("WASHINGTON", 12, 0),
]
CLOCK_MAP = {city: "%02d:%02d" % (h, m) for city, h, m in CLOCKS}

# The day in numbers: six big stats, one per top story.
STATS = [
    ("370,000+", "evacuated", "as Akvan lands", "ASIA"),
    ("-5.1%", "Nikkei falls", "in market rout", "ASIA"),
    ("100,000", "youth visas", "in UK-EU deal", "EUROPE"),
    ("80", "paragraphs", "in COP31 draft", "EUROPE"),
    ("35", "man charged", "over Sydney plot", "OCEANIA"),
    ("138", "seats", "in Joburg pact", "AFRICA"),
]


# --------------------------------------------------------------- world map
# Continents as longitude/latitude outlines, drawn on an equirectangular
# projection, so the map reads like a real world map rather than blobs.
# Latitudes run 90 (top) to -55 (bottom); Antarctica is left out.
MAP_LAT_TOP, MAP_LAT_BOT = 85.0, -55.0

NORTH_AMERICA = [
    (-168, 66), (-162, 60), (-155, 58), (-148, 60), (-141, 60), (-135, 57),
    (-130, 53), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-112, 27), (-110, 24), (-107, 22),
    (-105, 20), (-100, 17), (-95, 16), (-91, 14), (-87, 13), (-83, 9),
    (-79, 9), (-77, 7), (-80, 9), (-83, 10), (-86, 13), (-88, 15), (-88, 17),
    (-87, 16), (-90, 21), (-93, 19), (-96, 19), (-97, 22), (-97, 26),
    (-94, 29), (-90, 29), (-84, 30), (-82, 27), (-80, 25), (-81, 31),
    (-76, 35), (-74, 39), (-70, 42), (-68, 44), (-66, 45), (-60, 46),
    (-55, 47), (-53, 49), (-56, 52), (-60, 55), (-65, 58), (-68, 58),
    (-72, 62), (-78, 55), (-80, 52), (-85, 55), (-88, 60), (-90, 64), (-92, 66),
    (-95, 68), (-100, 68), (-110, 68), (-120, 69), (-130, 69), (-140, 70),
    (-150, 70), (-158, 71), (-165, 68), (-168, 66),
]
GREENLAND = [
    (-58, 64), (-52, 60), (-44, 60), (-40, 64), (-32, 68), (-24, 70),
    (-20, 74), (-22, 76), (-28, 78), (-38, 80), (-48, 80), (-56, 77),
    (-60, 74), (-58, 70), (-58, 64),
]
SOUTH_AMERICA = [
    (-79, 9), (-77, 4), (-80, -3), (-81, -6), (-78, -12), (-73, -18),
    (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
    (-66, -55), (-68, -50), (-65, -45), (-62, -40), (-58, -35), (-52, -32),
    (-48, -28), (-41, -23), (-35, -20), (-35, -15), (-35, -8), (-40, -5),
    (-44, -2), (-50, 0), (-55, 5), (-60, 8), (-64, 10), (-69, 11),
    (-73, 11), (-76, 10), (-79, 9),
]
AFRICA = [
    (-17, 15), (-17, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36), (10, 37),
    (11, 34), (15, 32), (20, 32), (25, 32), (30, 31), (32, 31), (34, 28),
    (35, 23), (37, 18), (39, 15), (43, 11), (48, 11), (51, 11), (49, 8), (46, 5),
    (42, 0), (40, -5), (40, -10), (38, -15), (35, -20), (32, -26),
    (28, -32), (20, -35), (17, -32), (15, -27), (12, -18), (12, -12),
    (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12), (-17, 15),
]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (50, -20), (47, -24), (44, -25), (43, -21), (44, -16)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-3, 50), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36), (141, 38),
         (142, 40), (143, 42), (145, 44), (142, 44), (140, 40), (138, 37), (136, 35),
         (133, 34), (130, 31)]
SUMATRA = [(95, 5), (98, 3), (101, 0), (104, -3), (106, -5), (103, -6), (100, -3), (97, 1), (95, 5)]
BORNEO = [(109, 1), (111, 3), (114, 4), (117, 2), (118, -1), (116, -4), (112, -4), (110, -1), (109, 1)]
JAVA = [(105, -6), (108, -6), (111, -7), (114, -7), (112, -8), (108, -8), (105, -7), (105, -6)]
NEW_GUINEA = [(131, -1), (134, -2), (137, -3), (140, -4), (143, -6), (146, -8),
              (147, -9), (143, -8), (139, -6), (135, -4), (131, -1)]
AUSTRALIA = [
    (114, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
    (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
    (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
    (140, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14),
    (122, -17), (118, -20), (114, -22),
]
NEW_ZEALAND = [(167, -45), (169, -43), (171, -41), (173, -40), (175, -38),
               (176, -37), (174, -39), (172, -41), (170, -43), (167, -45)]
# Europe and Asia share one border (Urals, then Caucasus); the two lists
# carry the same border points so no gap shows between them.
EUROPE = [
    (-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50), (0, 51),
    (3, 53), (8, 55), (8, 57), (10, 59), (5, 60), (5, 62), (10, 64),
    (12, 66), (18, 69), (25, 71), (30, 70), (35, 68), (40, 67), (45, 68),
    (50, 69), (55, 68), (60, 69), (60, 60), (55, 51), (50, 47), (45, 44),
    (40, 42), (38, 41), (36, 41), (33, 42), (30, 41), (28, 41), (27, 40),
    (26, 38), (23, 36), (22, 37), (23, 39), (21, 40), (19, 42), (16, 44),
    (14, 45), (12, 44), (14, 42), (17, 40), (16, 38), (15, 41), (13, 41),
    (11, 43), (8, 44), (3, 43), (0, 40), (-2, 37), (-5, 36), (-9, 37),
]
ASIA = [
    (60, 69), (65, 69), (70, 72), (75, 73), (80, 73), (85, 74), (90, 75),
    (95, 76), (100, 77), (105, 78), (110, 76), (115, 73), (120, 72),
    (125, 71), (130, 71), (135, 70), (140, 72), (145, 72), (150, 70),
    (155, 69), (158, 66), (162, 62), (162, 58), (158, 55), (155, 52),
    (150, 50), (145, 45), (142, 40), (140, 35), (138, 32), (135, 30),
    (132, 28), (130, 25), (128, 22), (125, 20), (122, 18), (120, 15),
    (118, 12), (115, 10), (112, 8), (110, 5), (108, 2), (105, 1), (103, 1),
    (100, 7), (98, 12), (95, 16), (92, 20), (91, 22), (88, 22), (85, 19),
    (80, 15), (79, 11), (77, 8), (75, 11), (73, 15), (72, 18), (70, 20), (67, 23),
    (66, 25), (61, 25), (57, 26), (54, 27), (51, 28), (50, 29), (48, 30),
    (48, 29), (50, 26), (55, 24), (58, 22), (59, 20), (55, 17), (52, 15),
    (48, 14), (44, 13), (43, 12), (42, 14), (40, 17), (39, 20), (38, 24), (36, 28),
    (34, 28), (35, 31), (36, 36), (40, 42), (45, 44), (50, 47), (55, 51),
    (60, 60), (60, 69),
]

LAND = [
    (NORTH_AMERICA, "AMERICAS"), (GREENLAND, "AMERICAS"), (SOUTH_AMERICA, "AMERICAS"),
    (AFRICA, "AFRICA"), (MADAGASCAR, "AFRICA"), (UK, "EUROPE"), (JAPAN, "ASIA"),
    (SUMATRA, "ASIA"), (BORNEO, "ASIA"), (JAVA, "ASIA"), (NEW_GUINEA, "OCEANIA"),
    (AUSTRALIA, "OCEANIA"), (NEW_ZEALAND, "OCEANIA"), (EUROPE, "EUROPE"), (ASIA, "ASIA"),
]


def project(x, y, w, h, lon, lat):
    px = x + int((lon + 180.0) / 360.0 * w)
    py = y + int((MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * h)
    return (px, py)


def draw_map(img, x, y, w, h, markers, badges):
    """markers: list of (number, lon, lat, region); badges: list of (region, count, lon, lat)."""
    img.rect(x, y, w, h, MAP_OCEAN)
    for poly_ll, region in LAND:
        pts = [project(x, y, w, h, lon, lat) for lon, lat in poly_ll]
        img.poly(pts, MAP_LAND)
    # graticule, light
    for lon in range(-150, 151, 30):
        px = x + int((lon + 180.0) / 360.0 * w)
        for yy in range(y, y + h, 4):
            img.set(px, yy, MAP_GRID)
    # story markers: round points filled with the region colour, the
    # number in black or white, whichever reads best on that colour
    for num, lon, lat, region in markers:
        cx, cy = project(x, y, w, h, lon, lat)
        rc = REGION[region]
        lum = 0.299 * rc[0] + 0.587 * rc[1] + 0.114 * rc[2]
        tc = INK if lum > 130 else (255, 255, 255)
        img.circle(cx, cy, 7, rc)
        img.ring(cx, cy, 7, (255, 255, 255), 1)
        s = str(num)
        draw_text(img, cx - text_width(s, 1) // 2, cy - 3, s, 1, tc)
    # ring badges: stories per region
    for region, count, lon, lat in badges:
        cx, cy = project(x, y, w, h, lon, lat)
        img.circle(cx, cy, 11, (255, 255, 255))
        img.ring(cx, cy, 11, REGION[region], 2)
        s = str(count)
        draw_text(img, cx - text_width(s, 1) // 2, cy - 3, s, 1, REGION[region])


# ------------------------------------------------------------------- data
# 15 main stories. Each: number, place, region, headline, standfirst,
# scene key, and (lon, lat) for the map marker (None = global, off map).
# Paris, Brussels and Warsaw are nudged apart on the map so
# their markers do not overlap (true positions are ~3-7 degrees away).
MAINS = [
    (1, "WASHINGTON", "AMERICAS", "TRUMP VOWS DATA CENTER TAX ABROAD",
     "Defends Putin as 'friend'.",
     "podium", (-77.04, 38.9)),
    (2, "KYIV", "EUROPE", "RUSSIA'S MASS STRIKE HITS KYIV",
     "Nine killed, three bridges hit.",
     "strike", (30.52, 50.45)),
    (3, "ODISHA", "ASIA", "CYCLONE AKVAN SLAMS INTO INDIA",
     "370,000 evacuated, no deaths.",
     "cyclone", (84.9, 19.3)),
    (4, "ANTALYA", "EUROPE", "COP31 DRAFT DROPS FOSSIL TEXT",
     "No deal as talks run into overtime.",
     "globe", (30.7, 36.9)),
    (5, "BRUSSELS", "EUROPE", "UK AND EU AGREE 100,000 VISAS",
     "Visas agreed, fees row stalls.",
     "summit", (5.0, 53.0)),
    (6, "HORMUZ", "MIDEAST", "IRAN SAYS TANKER HIT MINE",
     "Tanker catches fire in strait.",
     "tanker", (56.5, 26.5)),
    (7, "JAZAN", "MIDEAST", "SAUDI INTERCEPTS MISSILE",
     "Three missiles, five drones downed",
     "drone", (42.55, 16.9)),
    (8, "SYDNEY", "OCEANIA", "SYDNEY RAIDS FOIL TERROR PLOT",
     "Charged, 35, bail refused.",
     "police", (151.2, -33.87)),
    (9, "TAIPEI", "ASIA", "TAIWAN CURBS SHORT-SELLING",
     "Five rescue measures unveiled.",
     "chart", (121.56, 25.03)),
    (10, "KUALA LUMPUR", "ASIA", "AIR FORCE MEN HELD IN DRUG RING",
     "11 held, 96.6kg of meth seized.",
     "plane", (101.69, 3.14)),
    (11, "JOHANNESBURG", "AFRICA", "ANC NEARS JOBURG COALITION",
     "138 seats in new council pact.",
     "flags", (28.05, -26.2)),
    (12, "WELLINGTON", "OCEANIA", "PHILLIPS TON POWERS NEW ZEALAND",
     "118 runs in first Test vs India.",
     "cricket", (172.0, -41.29)),
    (13, "TOKYO", "ASIA", "ASIAN STOCKS PLUNGE",
     "Nikkei -5.1%, Taiex -6.2%.",
     "down", (139.69, 35.68)),
    (14, "PARIS", "EUROPE", "EUROPE PROTESTS HIGH PRICES",
     "Vests return for 8th year.",
     "march", (-3.0, 41.0)),
    (15, "WARSAW", "EUROPE", "RUSSIAN MISSILES HIT POLAND",
     "Tusk: deliberate provocation.",
     "radar", (17.0, 56.0)),
]

# The other 25 stories: number, place, region, headline.
REST = [
    (16, "WELLINGTON", "OCEANIA", "US sanctions Comancheros"),
    (17, "CAIRO", "AFRICA", "Egypt repays $38.2bn debt"),
    (18, "PRETORIA", "AFRICA", "SA holds rates at 7.25%"),
    (19, "NAIROBI", "AFRICA", "Kenya judiciary report out"),
    (20, "LILONGWE", "AFRICA", "Malawi fuel crisis bites"),
    (21, "DAKAR", "AFRICA", "Senegal boat capsizes, 4 dead"),
    (22, "OSOGBO", "AFRICA", "Mob kills crash survivor"),
    (23, "NAIROBI", "AFRICA", "Kenya opposition walks out"),
    (24, "BUENOS AIRES", "AMERICAS", "Senate passes disability law"),
    (25, "SAN SALVADOR", "AMERICAS", "Bukele seeks third term"),
    (26, "BRASILIA", "AMERICAS", "Lula visits ailing Chief Raoni"),
    (27, "CHICAGO", "AMERICAS", "Temple plot plea: not guilty"),
    (28, "WASHINGTON", "AMERICAS", "Iran war hit US munitions"),
    (29, "MENLO PARK", "AMERICAS", "Meta rethinks 2030 climate goal"),
    (30, "WASHINGTON", "AMERICAS", "880k AI chips okayed for China"),
    (31, "NOUMEA", "OCEANIA", "Quake hits New Caledonia"),
    (32, "BRUSSELS", "EUROPE", "EU summons Russian envoy"),
    (33, "TBILISI", "EUROPE", "Gas blast kills six in Georgia"),
    (34, "PARIS", "EUROPE", "Fire kills one in Fontenay"),
    (35, "SEOUL", "ASIA", "Samsung names new mobile chief"),
    (36, "GOA", "ASIA", "Goa film festival opens"),
    (37, "BEIJING", "ASIA", "DeepSeek raises $15bn"),
    (38, "JERUSALEM", "MIDEAST", "Czechs visit Israel on defence"),
    (39, "BEIRUT", "MIDEAST", "Israel hits Hezbollah site"),
    (40, "GLOBAL", "GLOBAL", "Gemini gains Mac control"),
]

COUNTS = {"ASIA": 7, "EUROPE": 8, "MIDEAST": 4, "AMERICAS": 8,
          "AFRICA": 8, "OCEANIA": 4, "GLOBAL": 1}


# ------------------------------------------------------------------ layout
def card(img, x, y, w, h, fill=(255, 255, 255)):
    img.rect(x, y, w, h, fill)
    img.rect(x, y, w, 1, GRID)
    img.rect(x, y + h - 1, w, 1, GRID)
    img.rect(x, y, 1, h, GRID)
    img.rect(x + w - 1, y, 1, h, GRID)


def build():
    img = Img(W, H, PAPER_TOP, PAPER_BOT)
    RULE = (150, 150, 150)

    # ---- header: simple, with colour. A slim red band across the top,
    # ---- then the date as the masthead and a short description below.
    img.rect(0, 0, W, 8, RED)
    mast = "FRIDAY 20 NOVEMBER 2026"
    draw_text(img, (W - text_width(mast, 3)) // 2, 16, mast, 3, INK)
    # tagline (top-left corner): navy badge, cream text, still readable
    tag = "all world in one day"
    img.rect(14, 16, 125, 21, NAVY)
    draw_text(img, 20, 23, tag, 1, (245, 235, 205))
    # story count (right): stacked, "40" over "STORIES", in a red badge
    img.rect(703, 16, 51, 21, RED)
    draw_text(img, 723, 19, "40", 1, (255, 255, 255))
    draw_text(img, 708, 27, "STORIES", 1, (255, 255, 255))
    desc = "Trump vows data center tax - Kyiv mass strike - Akvan lands"
    draw_text(img, (W - text_width(desc, 1)) // 2, 46, desc, 1, INK)
    img.rect(14, 58, 740, 2, RED)
    img.rect(14, 61, 740, 1, INK)

    # ---- region chips, counts sum to exactly 40, joined into one
    # ---- continuous strip: no gaps, each segment in its region colour
    widths = []
    base = 740 // 7
    rem = 740 % 7
    for i in range(7):
        widths.append(base + 1 if i < rem else base)
    cx = 14
    for i, region in enumerate(("ASIA", "EUROPE", "MIDEAST", "AMERICAS", "AFRICA", "OCEANIA", "GLOBAL")):
        label = "%s %d" % (REGION_NAME[region], COUNTS[region])
        img.rect(cx, 68, widths[i], 22, REGION[region])
        draw_text(img, cx + (widths[i] - text_width(label, 1)) // 2, 74, label, 1, (255, 255, 255))
        cx += widths[i]

    # ---- the day in numbers: big black figures, bold, no boxes,
    # ---- thin rules between
    widths = []
    base = 740 // 6
    rem = 740 % 6
    for i in range(6):
        widths.append(base + 1 if i < rem else base)
    cx = 14
    for i, (num, l1, l2, region) in enumerate(STATS):
        wcell = widths[i]
        draw_text_bold(img, cx + (wcell - text_width(num, 2)) // 2, 98, num, 2, INK)
        draw_text(img, cx + (wcell - text_width(l1, 1)) // 2, 116, l1, 1, INK)
        draw_text(img, cx + (wcell - text_width(l2, 1)) // 2, 125, l2, 1, (90, 90, 96))
        cx += wcell
        if i < 5:
            img.rect(cx, 98, 1, 36, RULE)
    img.rect(14, 140, 740, 3, INK)
    img.rect(14, 145, 740, 1, INK)

    # ---- the three big main stories, each in its own 2px-bordered box:
    # ---- label bar, big illustration with its own sharp border, then text
    for k in range(3):
        num, place, region, head, stand, _scene, _ll = MAINS[k]
        x0 = 14 + k * 250
        y0 = 152
        img.rect(x0, y0, 244, 2, BOX)
        img.rect(x0, y0 + 214, 244, 2, BOX)
        img.rect(x0, y0, 2, 216, BOX)
        img.rect(x0 + 242, y0, 2, 216, BOX)
        lab = "%s - %s" % (place, {"WASHINGTON": "PRESS CONFERENCE", "KYIV": "MISSILE STRIKE", "ODISHA": "CYCLONE"}[place])
        img.rect(x0 + 2, y0 + 2, 240, 16, REGION[region])
        draw_text(img, x0 + 2 + (240 - text_width(lab, 1)) // 2, y0 + 6, lab, 1, (255, 255, 255))
        SCENES[_scene](img, x0 + 7, y0 + 20, 230, 118)
        img.rect(x0 + 7, y0 + 20, 230, 1, BOX)
        img.rect(x0 + 7, y0 + 137, 230, 1, BOX)
        img.rect(x0 + 7, y0 + 20, 1, 118, BOX)
        img.rect(x0 + 236, y0 + 20, 1, 118, BOX)
        pline = "%d. %s" % (num, place)
        if place in CLOCK_MAP:
            pline += " - " + CLOCK_MAP[place]
        draw_text(img, x0 + 7, y0 + 144, pline, 1, REGION[region])
        for i, ln in enumerate(wrap_text(head, 230, 2)[:2]):
            draw_text(img, x0 + 7, y0 + 156 + i * 17, ln, 2, INK)
        for i, ln in enumerate(wrap_text(stand, 230, 1)[:2]):
            draw_text(img, x0 + 7, y0 + 192 + i * 9, ln, 1, (90, 90, 96))

    # ---- twelve small stories, six per row, two rows: each box has a
    # ---- label bar, a wide illustration on top, headline + standfirst
    # ---- below it (full width, stacked)
    for k in range(3, 15):
        num, place, region, head, stand, _scene, _ll = MAINS[k]
        r, c = (k - 3) // 6, (k - 3) % 6
        x0 = 14 + c * 124
        y0 = 374 + r * 126
        img.rect(x0, y0, 120, 1, BOX)
        img.rect(x0, y0 + 123, 120, 1, BOX)
        img.rect(x0, y0, 1, 124, BOX)
        img.rect(x0 + 119, y0, 1, 124, BOX)
        lab = "%d. %s" % (num, place)
        if place in CLOCK_MAP:
            lab += " - " + CLOCK_MAP[place]
        img.rect(x0 + 1, y0 + 1, 118, 13, REGION[region])
        draw_text(img, x0 + 1 + (118 - text_width(lab, 1)) // 2, y0 + 4, lab, 1, (255, 255, 255))
        SCENES[_scene](img, x0 + 5, y0 + 17, 110, 60)
        img.rect(x0 + 5, y0 + 17, 110, 1, BOX)
        img.rect(x0 + 5, y0 + 76, 110, 1, BOX)
        img.rect(x0 + 5, y0 + 17, 1, 60, BOX)
        img.rect(x0 + 114, y0 + 17, 1, 60, BOX)
        for i, ln in enumerate(wrap_text(head, 110, 1)[:2]):
            draw_text(img, x0 + 5, y0 + 80 + i * 9, ln, 1, INK)
        for i, ln in enumerate(wrap_text(stand, 110, 1)[:2]):
            draw_text(img, x0 + 5, y0 + 100 + i * 9, ln, 1, (90, 90, 96))

    # ---- where it happened: map left, the other 22 stories right.
    # ---- each section gets its own label bar; the list items are plain
    # ---- (v17 style, no boxes): number, place, headline, two lines
    img.rect(14, 632, 740, 1, RULE)
    img.rect(14, 638, 320, 16, INK)
    draw_text(img, 14 + (320 - text_width("WHERE IT HAPPENED", 1)) // 2, 642, "WHERE IT HAPPENED", 1, (255, 255, 255))
    img.rect(348, 638, 406, 16, RED)
    lab2 = "ALSO ON FRIDAY 20 NOVEMBER 2026"
    draw_text(img, 348 + (406 - text_width(lab2, 1)) // 2, 642, lab2, 1, (255, 255, 255))
    markers = [(m[0], m[6][0], m[6][1], m[2]) for m in MAINS if m[6] is not None]
    draw_map(img, 14, 658, 320, 200, markers, [])
    for i, (num, place, region, head) in enumerate(REST):
        col = i // 13
        row = i % 13
        x0 = 348 + col * 210
        y0 = 658 + row * 22
        num_s = "%d" % num
        pw = text_width(num_s, 1) + 6
        img.rect(x0, y0 + 5, pw, 10, REGION[region])
        draw_text(img, x0 + 3, y0 + 5, num_s, 1, (255, 255, 255))
        px = x0 + pw + 4
        draw_text(img, px, y0 + 2, place, 1, REGION[region])
        draw_text(img, px, y0 + 11, head, 1, INK)
    img.rect(341, 658, 1, 286, RULE)

    # ---- map key, compact, under the map (no card)
    draw_text(img, 14, 868, "MAP KEY", 1, INK)
    lx, ly = 14, 882
    for region in ("ASIA", "EUROPE", "MIDEAST", "AMERICAS"):
        img.rect(lx, ly, 8, 8, REGION[region])
        lx += 11
        draw_text(img, lx, ly + 1, REGION_NAME[region], 1, INK)
        lx += text_width(REGION_NAME[region], 1) + 10
    lx, ly = 14, 898
    for region in ("AFRICA", "OCEANIA", "GLOBAL"):
        img.rect(lx, ly, 8, 8, REGION[region])
        lx += 11
        draw_text(img, lx, ly + 1, REGION_NAME[region], 1, INK)
        lx += text_width(REGION_NAME[region], 1) + 10
    draw_text(img, 14, 922, "Numbers on the map match the 15 main stories.", 1, (90, 90, 96))
    draw_text(img, 14, 931, "All 40 stories are from 20 November 2026.", 1, (90, 90, 96))
    draw_text(img, 14, 940, "Wires: Reuters, AP, BBC, AFP, Xinhua, IMD.", 1, (90, 90, 96))
    draw_text(img, 14, 949, "Pictures and map: original, drawn in code.", 1, (90, 90, 96))

    # ---- date check box + left-out line + sources
    img.rect(14, 962, 740, 36, INK)
    img.rect(15, 963, 738, 34, PAPER_TOP)
    dc = "DATE CHECK - Every story on this page happened, or was first reported, on Friday 20 November 2026."
    draw_text(img, 22, 970, dc, 1, INK)
    lo = "LEFT OUT AS OTHER DAYS' NEWS: 19 NOV - EU Ukraine loan, Nvidia scandal, Anthropic IPO, Gaza scorecard."
    draw_text(img, 22, 982, lo, 1, (90, 90, 96))
    foot = "Sources: Reuters, AP, BBC, AFP, Xinhua, IMD, ESPNcricinfo and the day's wires - 20 November 2026"
    draw_text(img, (W - text_width(foot, 1)) // 2, 1006, foot, 1, (70, 80, 95))
    return img



def main():
    out = os.environ.get("OUTPUT", "/output/entry.png")
    img = build()
    n = write_png(img, out)
    print("wrote %s (%d bytes)" % (out, n))


if __name__ == "__main__":
    main()
