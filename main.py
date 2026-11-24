"""World news in one image: Tuesday 24 November 2026.

Draws a 1024x1024 newspaper-style front page with the five biggest
stories of the day, using only the Python standard library. The image is
rasterised from a small built-in 5x7 bitmap font and encoded as PNG by
hand (zlib + struct), so the program runs with no network and no third
party packages, and two runs write identical bytes.

Stories (all reported 23-24 November 2026, sources in the image):
  1. COP31 climate talks collapse with no deal (CNN / Reuters)
  2. NATO sends AWACS early-warning jets to Poland (Reuters)
  3. Ukraine says it sank a Russian warship off Libya (Reuters)
  4. Indonesia candy-factory fire kills 24 (Reuters)
  5. Russian aircraft prompts a brief evacuation alert in South Korea
     (Reuters)
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font ----
# A 5x7 bitmap font, drawn for this entry. Each glyph is 7 rows; each row
# is a 5-bit integer, bit 4 = leftmost column. Only the characters the
# poster uses are defined; anything else renders as a blank.
FONT = {
    "A": [14, 17, 17, 31, 17, 17, 17],
    "B": [30, 17, 17, 30, 17, 17, 30],
    "C": [15, 16, 16, 16, 16, 16, 15],
    "D": [30, 17, 17, 17, 17, 17, 30],
    "E": [31, 16, 16, 30, 16, 16, 31],
    "F": [31, 16, 16, 30, 16, 16, 16],
    "G": [15, 16, 16, 23, 17, 17, 14],
    "H": [17, 17, 17, 31, 17, 17, 17],
    "I": [31, 4, 4, 4, 4, 4, 31],
    "J": [7, 2, 2, 2, 2, 18, 12],
    "K": [17, 18, 20, 24, 20, 18, 17],
    "L": [16, 16, 16, 16, 16, 16, 31],
    "M": [17, 27, 21, 21, 17, 17, 17],
    "N": [17, 25, 25, 21, 19, 19, 17],
    "O": [14, 17, 17, 17, 17, 17, 14],
    "P": [30, 17, 17, 30, 16, 16, 16],
    "Q": [14, 17, 17, 17, 21, 18, 13],
    "R": [30, 17, 17, 30, 20, 18, 17],
    "S": [15, 16, 16, 14, 1, 1, 30],
    "T": [31, 4, 4, 4, 4, 4, 4],
    "U": [17, 17, 17, 17, 17, 17, 14],
    "V": [17, 17, 17, 17, 17, 10, 4],
    "W": [17, 17, 17, 21, 21, 27, 17],
    "X": [17, 17, 10, 4, 10, 17, 17],
    "Y": [17, 17, 10, 4, 4, 4, 4],
    "Z": [31, 1, 2, 4, 8, 16, 31],
    "0": [14, 19, 21, 25, 17, 17, 14],
    "1": [4, 12, 4, 4, 4, 4, 14],
    "2": [14, 17, 1, 2, 4, 8, 31],
    "3": [30, 1, 1, 14, 1, 1, 30],
    "4": [2, 6, 10, 18, 31, 2, 2],
    "5": [31, 16, 30, 1, 1, 17, 14],
    "6": [14, 16, 16, 30, 17, 17, 14],
    "7": [31, 1, 2, 4, 4, 4, 4],
    "8": [14, 17, 17, 14, 17, 17, 14],
    "9": [14, 17, 17, 15, 1, 1, 14],
    " ": [0, 0, 0, 0, 0, 0, 0],
    ".": [0, 0, 0, 0, 0, 12, 12],
    ",": [0, 0, 0, 0, 12, 12, 8],
    ":": [0, 12, 12, 0, 12, 12, 0],
    ";": [0, 12, 12, 0, 12, 12, 8],
    "'": [4, 4, 8, 0, 0, 0, 0],
    "-": [0, 0, 0, 14, 0, 0, 0],
    "/": [1, 1, 2, 4, 8, 16, 16],
    "(": [6, 4, 8, 8, 8, 4, 6],
    ")": [12, 4, 2, 2, 2, 4, 12],
    "%": [17, 18, 2, 4, 8, 9, 17],
    "!": [4, 4, 4, 4, 4, 0, 4],
    "?": [14, 17, 1, 2, 4, 0, 4],
    "&": [12, 18, 20, 8, 21, 18, 13],
    "+": [0, 4, 4, 31, 4, 4, 0],
    "=": [0, 0, 31, 0, 31, 0, 0],
    '"': [10, 10, 10, 0, 0, 0, 0],
    "\u2022": [0, 14, 14, 14, 0, 0, 0],
}

BLANK = [0, 0, 0, 0, 0, 0, 0]
ADVANCE = 6  # glyph columns (5) + 1 column of spacing


def text_width(text, scale):
    """Pixel width of text at the given scale (trailing space trimmed)."""
    if not text:
        return 0
    return (len(text) * ADVANCE - 1) * scale


# ------------------------------------------------------------- canvas -----
PAPER = (245, 241, 230)
INK = (20, 24, 31)
NAVY = (14, 42, 71)
NAVY_LIGHT = (31, 78, 121)
GOLD = (232, 179, 60)
RED = (192, 57, 43)
TEAL = (14, 124, 107)
AMBER = (183, 121, 31)
PLUM = (142, 59, 70)
RULE = (216, 210, 194)
WHITE = (245, 241, 230)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def fill_rect(self, x, y, w, h, color):
        r, g, b = color
        row = bytes((r, g, b)) * w
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                off = (yy * self.w + max(x, 0)) * 3
                self.buf[off:off + w * 3] = row

    def hline(self, y, x0, x1, color, thick=1):
        self.fill_rect(x0, y, x1 - x0, thick, color)

    def draw_char(self, ch, x, y, scale, color):
        glyph = FONT.get(ch, BLANK)
        r, g, b = color
        for row_idx, bits in enumerate(glyph):
            if not bits:
                continue
            for col in range(5):
                if bits & (1 << (4 - col)):
                    px = x + col * scale
                    py = y + row_idx * scale
                    cell = bytes((r, g, b)) * scale
                    for dy in range(scale):
                        off = ((py + dy) * self.w + px) * 3
                        self.buf[off:off + scale * 3] = cell

    def draw_text(self, text, x, y, scale, color):
        cx = x
        for ch in text:
            self.draw_char(ch, cx, y, scale, color)
            cx += ADVANCE * scale
        return cx

    def draw_text_centered(self, text, cx, y, scale, color):
        self.draw_text(text, cx - text_width(text, scale) // 2, y, scale, color)

    def draw_text_right(self, text, x_right, y, scale, color):
        self.draw_text(text, x_right - text_width(text, scale), y, scale, color)

    def wrap(self, text, scale, max_w):
        """Greedy word wrap; returns a list of lines fitting max_w."""
        lines = []
        cur = ""
        for word in text.split(" "):
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def png_bytes(canvas):
    """Encode the RGB buffer as a PNG (filter 0, zlib level 9)."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# -------------------------------------------------------------- layout ----
STORIES = [
    # (number, accent, kicker, headline, summary, source)
    ("2", NAVY_LIGHT, "EUROPE",
     "NATO SENDS AWACS TO POLAND",
     "EARLY-WARNING JETS DEPLOYED AFTER THREE RUSSIAN MISSILES "
     "LANDED ON POLISH SOIL.",
     "REUTERS"),
    ("3", TEAL, "WAR IN UKRAINE",
     "UKRAINE SINKS RUSSIAN WARSHIP",
     "KYIV SAYS SEA DRONES SANK A RUSSIAN CORVETTE IN A LIBYAN "
     "PORT.",
     "REUTERS"),
    ("4", AMBER, "ASIA",
     "INDONESIA FACTORY FIRE KILLS 24",
     "CANDY FACTORY BLAZE IN SERANG LEAVES ABOUT 30 WORKERS "
     "STILL MISSING.",
     "REUTERS"),
    ("5", PLUM, "ASIA-PACIFIC",
     "RUSSIAN JET SPARKS KOREA ALERT",
     "SEOUL WARNS ULLEUNG ISLAND AFTER A RUSSIAN AIRCRAFT "
     "ENTERS ITS AIRSPACE.",
     "REUTERS"),
]

LEAD_SUMMARY = (
    "NEARLY 200 NATIONS LEAVE ANTALYA WITHOUT A DEAL AS THE "
    "FOSSIL-FUEL RIFT SPLITS THE SUMMIT. THE FIRST CLIMATE "
    "SUMMIT TO FAIL SINCE 2009."
)


def build():
    c = Canvas(W, H, PAPER)
    mx = 36  # side margin

    # ---- header band -------------------------------------------------
    c.fill_rect(0, 0, W, 168, NAVY)
    c.draw_text_centered("THE WORLD IN ONE IMAGE", W // 2, 30, 3, GOLD)
    c.draw_text_centered("TUESDAY, 24 NOVEMBER 2026", W // 2, 66, 5, WHITE)
    c.draw_text_centered("FIVE STORIES THAT DEFINED THE DAY",
                         W // 2, 126, 2, (200, 214, 228))
    c.fill_rect(0, 168, W, 4, GOLD)

    # ---- lead story: COP31 collapses --------------------------------
    y0 = 172
    c.fill_rect(mx, y0 + 14, 14, 214, RED)
    c.draw_text("TOP STORY: CLIMATE", mx + 30, y0 + 16, 2, RED)
    c.draw_text("COP31 COLLAPSES: NO DEAL", mx + 30, y0 + 46, 6, INK)
    lines = c.wrap(LEAD_SUMMARY, 3, W - mx - (mx + 30))
    ly = y0 + 118
    for line in lines:
        c.draw_text(line, mx + 30, ly, 3, (58, 64, 74))
        ly += 26
    # source chip
    chip = "REUTERS / CNN / BBC"
    cw = text_width(chip, 2) + 24
    cy = y0 + 200
    c.fill_rect(mx + 30, cy, cw, 28, RED)
    c.draw_text(chip, mx + 30 + 12, cy + 7, 2, WHITE)

    c.hline(412, mx, W - mx, RULE, 2)

    # ---- stories 2-5 --------------------------------------------------
    row_y = 428
    row_h = 132
    for num, accent, kicker, headline, summary, source in STORIES:
        # big number block
        c.fill_rect(mx, row_y + 8, 96, 96, accent)
        c.draw_text_centered(num, mx + 48, row_y + 31, 7, WHITE)
        # kicker + source, then headline
        tx = mx + 120
        c.draw_text(kicker + " - " + source, tx, row_y + 10, 2, accent)
        c.draw_text(headline, tx, row_y + 34, 4, INK)
        # summary, up to two lines
        slines = c.wrap(summary, 3, W - mx - tx)
        sy = row_y + 72
        for line in slines[:2]:
            c.draw_text(line, tx, sy, 3, (58, 64, 74))
            sy += 26
        row_y += row_h
        if num != "5":
            c.hline(row_y, mx, W - mx, RULE, 2)

    # ---- footer -------------------------------------------------------
    c.fill_rect(0, 960, W, H - 960, NAVY)
    c.draw_text_centered("SOURCES: REUTERS, CNN, BBC, THE TIMES",
                         W // 2, 984, 2, (200, 214, 228))
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
