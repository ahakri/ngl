"""Generate flat screen / paper textures for MURDER-04 with Pillow (system python3; bpy env has no PIL).
Run: python3 make_textures.py  -> writes BLENDER_PROJECTS/MURDER-04/tex/*.png (skips existing unless --force).
All glyphs are illustrative stand-ins (Latin / Greek letters, mirrored or rotated, simple shapes) - not a
reproduction of the 1969 sheet. No real logos, letterheads or screenshots.
"""
import os, sys, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "tex")
os.makedirs(OUT, exist_ok=True)
FORCE = "--force" in sys.argv
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
LET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GREEK = "ΘΦΣΔΩΓΛΠΨ"
SHAPES = ["tri", "trio", "dot", "slash", "bslash", "sq", "plus", "circ"]


def F(p, s):
    return ImageFont.truetype(p, s)


def want(name):
    p = os.path.join(OUT, name)
    return p if (FORCE or not os.path.exists(p)) else None


def glyph_specs(n=340, seed=340):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        r = rnd.random()
        if r < 0.62:
            out.append(("ch", rnd.choice(LET), rnd.choice([0, 0, 0, 1, 2, 3]), rnd.random() < 0.25))
        elif r < 0.78:
            out.append(("ch", rnd.choice(GREEK), 0, False))
        else:
            out.append(("sh", rnd.choice(SHAPES), 0, False))
    return out


def draw_glyph(im, cx, cy, size, spec, fill):
    kind, g, rot, mirror = spec
    tile = Image.new("L", (size * 2, size * 2), 0)
    d = ImageDraw.Draw(tile)
    c = size
    s = size * 0.42
    if kind == "ch":
        d.text((c, c), g, font=F(SANS, int(size * 0.95)), fill=255, anchor="mm")
    elif g == "tri":
        d.polygon([(c, c - s), (c + s, c + s), (c - s, c + s)], fill=255)
    elif g == "trio":
        d.polygon([(c, c - s), (c + s, c + s), (c - s, c + s)], outline=255, width=max(2, size // 12))
    elif g == "dot":
        d.ellipse((c - s * 0.35, c - s * 0.35, c + s * 0.35, c + s * 0.35), fill=255)
    elif g == "slash":
        d.line((c - s, c + s, c + s, c - s), fill=255, width=max(2, size // 9))
    elif g == "bslash":
        d.line((c - s, c - s, c + s, c + s), fill=255, width=max(2, size // 9))
    elif g == "sq":
        d.rectangle((c - s, c - s, c + s, c + s), outline=255, width=max(2, size // 12))
    elif g == "plus":
        d.line((c - s, c, c + s, c), fill=255, width=max(2, size // 9))
        d.line((c, c - s, c, c + s), fill=255, width=max(2, size // 9))
    elif g == "circ":
        d.ellipse((c - s, c - s, c + s, c + s), outline=255, width=max(2, size // 12))
        d.line((c - s, c, c + s, c), fill=255, width=max(2, size // 12))
    if mirror:
        tile = ImageOps.mirror(tile)
    if rot:
        tile = tile.rotate(90 * rot)
    col = Image.new("RGBA", tile.size, fill)
    im.paste(col, (int(cx - c), int(cy - c)), tile)


def cipher_sheet(path, w=850, h=1100, rows=20, cols=17, seed=340):
    """Aged paper with the stand-in glyph grid (for the folded sheet / thumbnails)."""
    im = Image.new("RGBA", (w, h), (226, 216, 190, 255))
    rnd = random.Random(seed)
    px = im.load()
    for _ in range(9000):
        x, y = rnd.randrange(w), rnd.randrange(h)
        c = rnd.randint(185, 220)
        px[x, y] = (c, c - 8, c - 30, 255)
    specs = glyph_specs(rows * cols, seed)
    mx, my = 70, 120
    cw, ch = (w - 2 * mx) / cols, (h - 2 * my) / rows
    for r in range(rows):
        for c in range(cols):
            draw_glyph(im, mx + (c + 0.5) * cw, my + (r + 0.5) * ch, int(ch * 0.8), specs[r * cols + c], (30, 25, 35, 255))
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    im.save(path)


def letter_scroll(path, w=512, h=2048, seed=1, color=(120, 255, 170)):
    """Columns of random capitals (monospace) on black: a tall strip that scrolls vertically."""
    im = Image.new("RGB", (w, h), (2, 6, 6))
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    f = F(MONO, 26)
    for y in range(0, h, 32):
        line = "".join(rnd.choice(LET + "   ") for _ in range(30))
        a = rnd.uniform(0.45, 1.0)
        d.text((14, y + 4), line, font=f, fill=tuple(int(c * a) for c in color))
    im.save(path)


def mosaic(path, w=1024, h=1024, cells=8, seed=2):
    """Atlas of tiny thumbnail grids, each with a different hop-pattern path (2x2 pages of cells for flicker)."""
    im = Image.new("RGB", (w, h), (3, 8, 12))
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    cw = w // cells
    for i in range(cells):
        for j in range(cells):
            x0, y0 = i * cw + 6, j * cw + 6
            x1, y1 = x0 + cw - 12, y0 + cw - 12
            d.rectangle((x0, y0, x1, y1), fill=(8, 22, 30), outline=(40, 120, 150), width=2)
            gr, gc = 10, 8
            sx, sy = (x1 - x0 - 10) / gc, (y1 - y0 - 10) / gr
            for r in range(gr):
                for c in range(gc):
                    v = rnd.randint(60, 160)
                    d.rectangle((x0 + 5 + c * sx + 2, y0 + 5 + r * sy + 2, x0 + 5 + c * sx + 5, y0 + 5 + r * sy + 5), fill=(v // 2, v, v))
            dr, dc = rnd.randint(1, 3), rnd.randint(1, 5)
            r, c = 0, rnd.randrange(gc)
            pts = []
            for k in range(rnd.randint(5, 9)):
                pts.append((x0 + 5 + (c + 0.5) * sx, y0 + 5 + (r + 0.5) * sy))
                r = (r + dr) % gr
                c = (c + dc) % gc
            col = (255, 80, 60) if rnd.random() < 0.15 else (120, 230, 255)
            d.line(pts, fill=col, width=3)
    im.save(path)


def az_window(path, w=1024, h=640, seed=3):
    """Generic solver-program window: title text 'AZdecrypt' (plain text), score panel, gibberish candidate lines."""
    im = Image.new("RGB", (w, h), (14, 18, 16))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 46), fill=(40, 48, 44))
    d.text((18, 23), "AZdecrypt", font=F(SANS, 26), fill=(220, 235, 225), anchor="lm")
    d.text((w - 20, 23), "- solver -", font=F(SANS, 20), fill=(150, 170, 160), anchor="rm")
    d.rectangle((20, 70, w - 20, 130), outline=(90, 140, 110), width=2)
    d.text((34, 100), "SCORE", font=F(MONO, 24), fill=(150, 230, 170), anchor="lm")
    d.rectangle((20, 150, w - 20, h - 20), outline=(60, 90, 75), width=2)
    rnd = random.Random(seed)
    f = F(MONO, 26)
    for k in range(13):
        line = "".join(rnd.choice(LET) for _ in range(36))
        d.text((36, 172 + k * 34), line, font=f, fill=(140, 220, 160) if k else (200, 255, 210))
    im.save(path)


def gib_scroll(path, w=1024, h=2048, seed=5):
    im = Image.new("RGB", (w, h), (14, 18, 16))
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    f = F(MONO, 26)
    for y in range(0, h, 34):
        d.text((16, y + 4), "".join(rnd.choice(LET) for _ in range(36)), font=f, fill=(130, 215, 155))
    im.save(path)


def tv_talkshow(path, w=640, h=480):
    """Grainy greyscale 1960s TV studio: two empty-chair silhouettes, a desk with a phone (no people)."""
    im = Image.new("L", (w, h), 70)
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line((0, y, w, y), fill=int(60 + 50 * (y / h)))
    d.rectangle((0, 0, w, 170), fill=50)
    for x in range(30, w, 70):
        d.rectangle((x, 20, x + 40, 160), fill=62)
    d.rectangle((190, 260, 450, 330), fill=25)          # desk
    d.rectangle((200, 330, 440, 420), fill=35)
    d.ellipse((290, 222, 350, 262), fill=15)           # phone body
    d.rectangle((284, 214, 356, 226), fill=15)
    for cx in (110, 530):                              # empty chairs
        d.rounded_rectangle((cx - 55, 200, cx + 55, 330), 18, fill=20)
        d.rectangle((cx - 65, 300, cx + 65, 350), fill=22)
        d.rectangle((cx - 50, 350, cx - 40, 420), fill=18)
        d.rectangle((cx + 40, 350, cx + 50, 420), fill=18)
    im = im.filter(ImageFilter.GaussianBlur(2.0))
    rnd = random.Random(7)
    px = im.load()
    for _ in range(30000):
        x, y = rnd.randrange(w), rnd.randrange(h)
        px[x, y] = max(0, min(255, px[x, y] + rnd.randint(-40, 40)))
    im.convert("RGB").save(path)


def tv_phone(path, w=640, h=480):
    """Big rotary-desk-phone icon + 'LIVE CALL-IN' caption bar."""
    im = Image.new("L", (w, h), 40)
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line((0, y, w, y), fill=int(35 + 40 * (y / h)))
    cx, cy = 320, 220
    d.rounded_rectangle((cx - 150, cy - 30, cx + 150, cy + 120), 40, fill=225)
    d.rounded_rectangle((cx - 190, cy - 120, cx + 190, cy - 50), 35, fill=225)
    d.rectangle((cx - 150, cy - 70, cx - 100, cy - 20), fill=225)
    d.rectangle((cx + 100, cy - 70, cx + 150, cy - 20), fill=225)
    d.ellipse((cx - 70, cy - 10, cx + 70, cy + 110), fill=60)
    for k in range(10):
        a = math.radians(-60 + k * 28)
        x, y = cx + 48 * math.cos(a), cy + 50 + 48 * math.sin(a)
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=225)
    d.ellipse((cx - 22, cy + 28, cx + 22, cy + 72), fill=225)
    d.rectangle((0, 380, w, 450), fill=15)
    d.text((w // 2, 415), "LIVE CALL-IN", font=F(SANS, 44), fill=235, anchor="mm")
    im = im.filter(ImageFilter.GaussianBlur(1.6))
    rnd = random.Random(8)
    px = im.load()
    for _ in range(30000):
        x, y = rnd.randrange(w), rnd.randrange(h)
        px[x, y] = max(0, min(255, px[x, y] + rnd.randint(-40, 40)))
    im.convert("RGB").save(path)


def newspaper(path, w=900, h=1200, seed=9):
    """Recreated 1969-style newspaper page (generic masthead, greeked columns, a small stand-in cipher box)."""
    im = Image.new("RGB", (w, h), (214, 206, 182))
    d = ImageDraw.Draw(im)
    d.text((w // 2, 70), "THE EVENING PAPER", font=F(SERIF, 64), fill=(25, 22, 20), anchor="mm")
    d.line((40, 120, w - 40, 120), fill=(25, 22, 20), width=4)
    d.text((w // 2, 140), "RECREATION  -  1969", font=F(SERIF_R, 22), fill=(60, 55, 50), anchor="mm")
    d.line((40, 160, w - 40, 160), fill=(25, 22, 20), width=2)
    d.text((w // 2, 220), "CODE MESSAGE", font=F(SERIF, 58), fill=(20, 18, 16), anchor="mm")
    rnd = random.Random(seed)
    for col in range(3):
        x0 = 50 + col * 275
        y = 290
        while y < h - 60:
            if col == 1 and 300 < y < 640:
                y += 20
                continue
            ln = rnd.randint(150, 240)
            d.line((x0, y, x0 + ln, y), fill=(95, 90, 82), width=7)
            y += 18
            if rnd.random() < 0.08:
                y += 18
    box = Image.new("RGBA", (240, 320), (226, 216, 190, 255))
    specs = glyph_specs(8 * 6, 77)
    for r in range(8):
        for c in range(6):
            draw_glyph(box, 25 + c * 38, 25 + r * 37, 28, specs[r * 6 + c], (30, 25, 35, 255))
    im.paste(box, (330, 320))
    d.rectangle((330, 320, 570, 640), outline=(25, 22, 20), width=3)
    im.save(path)


def city_glow(path, w=512, h=256, seed=11):
    im = Image.new("RGB", (w, h), (8, 12, 26))
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    for k in range(40):
        x = rnd.randrange(w)
        bw, bh = rnd.randint(20, 60), rnd.randint(40, 200)
        d.rectangle((x, h - bh, x + bw, h), fill=(12, 16, 30))
        for _ in range(rnd.randint(4, 20)):
            wx, wy = x + rnd.randrange(max(1, bw - 4)), h - rnd.randrange(bh)
            d.rectangle((wx, wy, wx + 3, wy + 4), fill=(255, 200, 120) if rnd.random() < 0.8 else (180, 200, 255))
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    im.save(path)


JOBS = [("cipher_sheet.png", cipher_sheet), ("letters_scroll.png", letter_scroll), ("mosaic.png", mosaic),
        ("az_window.png", az_window), ("gib_scroll.png", gib_scroll), ("tv_talkshow.png", tv_talkshow),
        ("tv_phone.png", tv_phone), ("newspaper.png", newspaper), ("city_glow.png", city_glow)]

if __name__ == "__main__":
    for name, fn in JOBS:
        p = want(name)
        if p:
            fn(p)
            print("wrote", p)
