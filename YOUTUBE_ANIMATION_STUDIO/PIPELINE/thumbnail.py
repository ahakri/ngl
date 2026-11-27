"""Thumbnail composer.

Reads THUMBNAILS/<ID>/thumbs.json:
  [{"name": "A", "source": "RENDERS/<ID>/S05/0040.png" | "<abs path>", "text": "ONE WORD", "text2": "optional small line",
    "text_pos": "top|middle|bottom", "text_color": [255,230,0], "circle": [x, y, r] (0..1 coords, optional),
    "arrow": [x1, y1, x2, y2] (optional), "zoom": 1.0, "focus": [x, y] (0..1 crop centre), "mood": "cave",
    "exposure": 1.0 (optional brightness multiplier), "vignette": 0.55 (optional edge darkening 0..1),
    "text_glow": [r, g, b] (optional soft coloured glow behind the main text),
    "zoom_16x9" / "focus_16x9" (optional overrides for the 1280x720 version)}]
Writes THUMBNAILS/<ID>/thumb_<name>.png (1080x1920 Shorts) and thumb_<name>_16x9.png (1280x720, for long-form/search previews),
plus THUMBNAILS/<ID>/thumb_sheet.png (side-by-side for QC).
Usage: python3 thumbnail.py <ID>
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ANTON = os.path.join(HERE, "fonts", "Anton-Regular.ttf")
OSW = os.path.join(HERE, "fonts", "Oswald.ttf")


def fit_crop(im, w, h, zoom=1.0, focus=(0.5, 0.5)):
    sc = max(w / im.width, h / im.height) * zoom
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    cx, cy = focus[0] * im.width, focus[1] * im.height
    x0 = int(min(max(0, cx - w / 2), im.width - w))
    y0 = int(min(max(0, cy - h / 2), im.height - h))
    return im.crop((x0, y0, x0 + w, y0 + h))


def punch(im):
    im = ImageEnhance.Contrast(im).enhance(1.25)
    im = ImageEnhance.Color(im).enhance(1.25)
    im = ImageEnhance.Brightness(im).enhance(1.12)
    return im.filter(ImageFilter.UnsharpMask(radius=3, percent=80, threshold=2))


def vignette(im, strength=0.55):
    """Darken the edges, keep the centre at full brightness (radial, elliptical to the frame)."""
    w, h = im.size
    g = Image.radial_gradient("L").resize((w, h), Image.BICUBIC)  # 0 centre -> 255 at the edge midpoints
    m = g.point(lambda v: int(255 * (1 - strength * min(1.0, (v / 255) ** 2))))
    black = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(im, black, m)


def big_text(im, text, pos, color, text2=None, glow=None):
    d = ImageDraw.Draw(im)
    w, h = im.size
    size = int(w * (0.2 if len(text) <= 8 else 0.15 if len(text) <= 12 else 0.11))
    f = ImageFont.truetype(ANTON, size)
    while d.textlength(text, font=f) > w * 0.9 and size > 40:
        size -= 6
        f = ImageFont.truetype(ANTON, size)
    y = {"top": int(h * 0.15), "middle": int(h * 0.45), "bottom": int(h * 0.72)}[pos]
    if glow:
        gl = Image.new("L", im.size, 0)
        ImageDraw.Draw(gl).text((w // 2, y), text, font=f, fill=255, anchor="mm", stroke_width=max(6, size // 12) * 3)
        gl = gl.filter(ImageFilter.GaussianBlur(size // 5)).point(lambda v: int(v * 0.85))
        im.paste(Image.new("RGB", im.size, tuple(glow)), (0, 0), gl)
        d = ImageDraw.Draw(im)
    d.text((w // 2, y), text, font=f, fill=tuple(color), anchor="mm", stroke_width=max(6, size // 12), stroke_fill=(0, 0, 0))
    if text2:
        f2 = ImageFont.truetype(OSW, int(size * 0.32))
        d.text((w // 2, y + int(size * 0.75)), text2, font=f2, fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))


def marks(im, spec):
    d = ImageDraw.Draw(im)
    w, h = im.size
    if spec.get("circle"):
        x, y, r = spec["circle"]
        R = r * w
        for k in range(3):
            d.ellipse((x * w - R - k * 2, y * h - R - k * 2, x * w + R + k * 2, y * h + R + k * 2), outline=(255, 30, 30), width=10)
    if spec.get("arrow"):
        x1, y1, x2, y2 = spec["arrow"]
        p1, p2 = (x1 * w, y1 * h), (x2 * w, y2 * h)
        d.line((p1, p2), fill=(255, 30, 30), width=18)
        import math
        ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        L = 60
        d.polygon([p2, (p2[0] - L * math.cos(ang - 0.5), p2[1] - L * math.sin(ang - 0.5)),
                   (p2[0] - L * math.cos(ang + 0.5), p2[1] - L * math.sin(ang + 0.5))], fill=(255, 30, 30))


def make(id_):
    tdir = os.path.join(ROOT, "THUMBNAILS", id_)
    specs = json.load(open(os.path.join(tdir, "thumbs.json")))
    outs = []
    for sp in specs:
        src = sp["source"] if os.path.isabs(sp["source"]) else os.path.join(ROOT, sp["source"])
        base = Image.open(src).convert("RGB")
        for (w, h, suffix) in ((1080, 1920, ""), (1280, 720, "_16x9")):
            k = suffix.lstrip("_")  # optional per-format overrides: "zoom_16x9", "focus_16x9"
            z = sp.get(f"zoom_{k}", sp.get("zoom", 1.0)) if k else sp.get("zoom", 1.0)
            fc = sp.get(f"focus_{k}", sp.get("focus", (0.5, 0.45))) if k else sp.get("focus", (0.5, 0.45))
            im = fit_crop(base, w, h, z, tuple(fc))
            im = punch(im)
            if sp.get("exposure", 1.0) != 1.0:
                im = ImageEnhance.Brightness(im).enhance(sp["exposure"])
            im = vignette(im, sp.get("vignette", 0.55))
            marks(im, sp)
            if sp.get("text"):
                big_text(im, sp["text"].upper(), sp.get("text_pos", "top"), sp.get("text_color", [255, 230, 0]), sp.get("text2"),
                         sp.get("text_glow"))
            p = os.path.join(tdir, f"thumb_{sp['name']}{suffix}.png")
            im.save(p)
            if not suffix:
                outs.append(p)
    sheet = Image.new("RGB", (540 * len(outs), 960), (0, 0, 0))
    for i, p in enumerate(outs):
        sheet.paste(Image.open(p).resize((540, 960)), (540 * i, 0))
    sheet.save(os.path.join(tdir, "thumb_sheet.png"))
    return outs


if __name__ == "__main__":
    print(make(sys.argv[1]))
