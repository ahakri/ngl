"""2D motion-graphics overlays rendered per frame with Pillow (RGBA, 1080x1920).

Each overlay function signature: fn(t, dur, text, params) -> PIL.Image RGBA (full frame) or None
  t   = seconds since the overlay (shot) started, dur = shot duration.
Types: stamp, depth, timer, counter, map, timeline, document, label, text, card, title.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

W, H = 1080, 1920
FD = os.path.join(os.path.dirname(__file__), "fonts")
F_ANTON = os.path.join(FD, "Anton-Regular.ttf")
F_OSWALD = os.path.join(FD, "Oswald.ttf")
F_BEBAS = os.path.join(FD, "BebasNeue-Regular.ttf")
F_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
_fc = {}

ACCENT = {"cave": (64, 224, 208), "scuba": (70, 200, 255), "murder": (230, 40, 40), "haunted": (170, 255, 170)}
LABEL_COL = {"DOCUMENTED FACT": (60, 200, 120), "DOCUMENTED": (60, 200, 120), "EYEWITNESS CLAIM": (240, 180, 40),
             "WITNESS CLAIM": (240, 180, 40), "FOLKLORE": (170, 120, 255), "DRAMATISATION": (230, 80, 80),
             "DRAMATIZATION": (230, 80, 80), "DISPUTED": (240, 120, 40), "THEORY": (240, 180, 40)}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def shadow_text(d, xy, txt, f, fill=(255, 255, 255, 255), anchor="la", stroke=4, sfill=(0, 0, 0, 230)):
    d.text(xy, txt, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)


def typewriter(txt, t, cps=22):
    return txt[: max(0, int(t * cps))]


def ov_stamp(t, dur, text, p):
    """Location/date stamp, bottom-left-ish, typewriter reveal. text may contain \n."""
    im = blank()
    d = ImageDraw.Draw(im)
    a = ease(t / 0.3) * (1 - ease((t - dur + 0.35) / 0.35))
    y = p.get("y", 300)
    lines = text.split("\n")
    shown = typewriter(text, t, p.get("cps", 26)).split("\n")
    for i, ln in enumerate(shown):
        f = font(F_MONO, 44 if i == 0 else 36)
        shadow_text(d, (70, y + i * 60), ln, f, fill=(255, 255, 255, int(255 * a)), stroke=3, sfill=(0, 0, 0, int(200 * a)))
    if t % 1.0 < 0.5 and len("".join(shown)) < len(text.replace("\n", "")):
        pass
    acc = ACCENT.get(p.get("mood", "cave"), (255, 220, 60))
    d.rectangle((50, y + 4, 58, y + 44 + 60 * (len(lines) - 1)), fill=(*acc, int(255 * a)))
    return im


def ov_depth(t, dur, text, p):
    """Depth gauge: animates from p.from to p.to metres. Right side vertical bar."""
    im = blank()
    d = ImageDraw.Draw(im)
    a = ease(t / 0.3) * (1 - ease((t - dur + 0.3) / 0.3))
    v0, v1 = p.get("from", 0), p.get("to", 100)
    v = v0 + (v1 - v0) * ease(t / max(0.3, dur * p.get("speed", 0.85)))
    unit = p.get("unit", "m")
    acc = ACCENT.get(p.get("mood", "cave"), (64, 224, 208))
    x0, y0, y1 = W - 130, 300, 1000
    d.line((x0, y0, x0, y1), fill=(255, 255, 255, int(120 * a)), width=4)
    mx = p.get("max", max(v0, v1) * 1.1 or 1)
    for k in range(0, 11):
        yy = y0 + (y1 - y0) * k / 10
        d.line((x0 - 14, yy, x0, yy), fill=(255, 255, 255, int(120 * a)), width=3)
    yy = y0 + (y1 - y0) * min(1, v / mx)
    d.polygon([(x0 + 8, yy), (x0 + 36, yy - 16), (x0 + 36, yy + 16)], fill=(*acc, int(255 * a)))
    f = font(F_ANTON, 92)
    s = f"{int(round(v))}{unit}"
    shadow_text(d, (x0 - 30, yy), s, f, fill=(255, 255, 255, int(255 * a)), anchor="rm", stroke=5)
    if text:
        shadow_text(d, (x0 - 30, yy + 70), text, font(F_OSWALD, 38), fill=(*acc, int(255 * a)), anchor="rm", stroke=3)
    return im


def ov_timer(t, dur, text, p):
    """Clock/elapsed counter, e.g. 'AIR LEFT 08:00' counting down, or 'HOUR 0 -> 60'."""
    im = blank()
    d = ImageDraw.Draw(im)
    a = ease(t / 0.25) * (1 - ease((t - dur + 0.3) / 0.3))
    v0, v1 = p.get("from", 0), p.get("to", 60)
    v = v0 + (v1 - v0) * ease(t / max(0.3, dur * 0.9))
    fmt = p.get("fmt", "mmss")
    if fmt == "mmss":
        s = f"{int(v) // 60:02d}:{int(v) % 60:02d}"
    elif fmt == "hours":
        s = f"{int(v)} HRS"
    else:
        s = f"{int(round(v)):,}"
    acc = (255, 70, 60) if p.get("danger") else ACCENT.get(p.get("mood", "cave"), (255, 255, 255))
    y = p.get("y", 330)
    shadow_text(d, (W // 2, y), text or "", font(F_OSWALD, 44), fill=(220, 220, 220, int(255 * a)), anchor="mm", stroke=3)
    shadow_text(d, (W // 2, y + 90), s, font(F_ANTON, 150), fill=(*acc, int(255 * a)), anchor="mm", stroke=6)
    return im


def ov_counter(t, dur, text, p):
    p = dict(p)
    p["fmt"] = "int"
    return ov_timer(t, dur, text, p)


def ov_text(t, dur, text, p):
    """Big centred on-screen statement (kinetic pop)."""
    im = blank()
    d = ImageDraw.Draw(im)
    a = ease(t / 0.18) * (1 - ease((t - dur + 0.25) / 0.25))
    sc = 0.85 + 0.15 * ease(t / 0.25)
    size = int(p.get("size", 110) * sc)
    col = tuple(p.get("color", (255, 255, 255)))
    y = p.get("y", 520)
    for i, ln in enumerate(text.split("\n")):
        shadow_text(d, (W // 2, y + i * int(size * 1.1)), ln, font(F_ANTON, size), fill=(*col, int(255 * a)), anchor="mm", stroke=7)
    return im


def ov_label(t, dur, text, p):
    """Fact-label badge (DOCUMENTED FACT / EYEWITNESS CLAIM / FOLKLORE / DRAMATISATION)."""
    im = blank()
    d = ImageDraw.Draw(im)
    a = ease(t / 0.2) * (1 - ease((t - dur + 0.25) / 0.25))
    key = text.upper()
    col = LABEL_COL.get(key, (240, 180, 40))
    f = font(F_OSWALD, 40)
    tw = d.textlength(key, font=f)
    x, y = 60, p.get("y", 200)
    d.rounded_rectangle((x, y, x + tw + 60, y + 70), radius=14, fill=(*col, int(235 * a)))
    d.ellipse((x + 18, y + 27, x + 34, y + 43), fill=(255, 255, 255, int(255 * a)))
    d.text((x + 44, y + 35), key, font=f, fill=(15, 15, 15, int(255 * a)), anchor="lm")
    return im


def ov_map(t, dur, text, p):
    """Stylised map card: land blob, route line drawing on, pin drop, place name.
    params: points [[x,y]..] in 0..1 card coords, pin index, title, subtitle."""
    im = blank()
    d = ImageDraw.Draw(im)
    a = ease(t / 0.35) * (1 - ease((t - dur + 0.3) / 0.3))
    cx0, cy0, cw, ch = 90, 430, 900, 900
    card = Image.new("RGBA", (cw, ch), (12, 18, 24, int(225 * a)))
    cd = ImageDraw.Draw(card)
    for gx in range(0, cw, 90):
        cd.line((gx, 0, gx, ch), fill=(60, 80, 90, int(80 * a)), width=1)
    for gy in range(0, ch, 90):
        cd.line((0, gy, cw, gy), fill=(60, 80, 90, int(80 * a)), width=1)
    land = p.get("land")
    if land:
        cd.polygon([(x * cw, y * ch) for x, y in land], fill=(40, 52, 48, int(255 * a)), outline=(110, 140, 120, int(255 * a)))
    pts = [(x * cw, y * ch) for x, y in p.get("points", [[0.2, 0.7], [0.5, 0.5], [0.75, 0.35]])]
    acc = ACCENT.get(p.get("mood", "cave"), (255, 220, 60))
    prog = ease((t - 0.3) / max(0.4, dur * 0.6))
    total = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) or 1
    rem = prog * total
    drawn = [pts[0]]
    for i in range(len(pts) - 1):
        seg = math.dist(pts[i], pts[i + 1])
        if rem >= seg:
            drawn.append(pts[i + 1])
            rem -= seg
        else:
            f = rem / seg
            drawn.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f))
            break
    if len(drawn) > 1:
        cd.line(drawn, fill=(*acc, int(255 * a)), width=8, joint="curve")
    if prog > 0.95 or p.get("pin_first"):
        pin = pts[p.get("pin", -1)]
        pa = ease((t - 0.3 - dur * 0.6) / 0.25) if not p.get("pin_first") else a
        r = 18 + 30 * (1 - pa)
        cd.ellipse((pin[0] - r, pin[1] - r, pin[0] + r, pin[1] + r), outline=(*acc, int(255 * pa * a)), width=6)
        cd.ellipse((pin[0] - 10, pin[1] - 10, pin[0] + 10, pin[1] + 10), fill=(255, 255, 255, int(255 * pa * a)))
    im.alpha_composite(card, (cx0, cy0))
    d = ImageDraw.Draw(im)
    if text:
        lines = text.split("\n")
        shadow_text(d, (W // 2, cy0 - 70), lines[0], font(F_ANTON, 84), fill=(255, 255, 255, int(255 * a)), anchor="mm", stroke=5)
        if len(lines) > 1:
            shadow_text(d, (W // 2, cy0 + ch + 60), lines[1], font(F_OSWALD, 44), fill=(*acc, int(255 * a)), anchor="mm", stroke=3)
    return im


def ov_timeline(t, dur, text, p):
    """Horizontal timeline with events appearing in sequence. params.events = [[label, sub], ...]."""
    im = blank()
    d = ImageDraw.Draw(im)
    a = ease(t / 0.3) * (1 - ease((t - dur + 0.3) / 0.3))
    ev = p.get("events", [["1959", ""], ["1960s", ""], ["2021", ""]])
    acc = ACCENT.get(p.get("mood", "murder"), (230, 40, 40))
    y = p.get("y", 960)
    x0, x1 = 110, W - 110
    prog = ease(t / max(0.4, dur * 0.7))
    d.line((x0, y, x0 + (x1 - x0) * prog, y), fill=(255, 255, 255, int(220 * a)), width=6)
    n = len(ev)
    for i, (lab, sub) in enumerate(ev):
        fx = i / max(1, n - 1)
        if fx > prog + 1e-3:
            continue
        x = x0 + (x1 - x0) * fx
        hi = i == n - 1 and p.get("highlight_last", True)
        col = acc if hi else (255, 255, 255)
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(*col, int(255 * a)))
        up = i % 2 == 0
        shadow_text(d, (x, y - 70 if up else y + 70), lab, font(F_ANTON, 64), fill=(*col, int(255 * a)), anchor="mm", stroke=4)
        if sub:
            shadow_text(d, (x, y - 130 if up else y + 130), sub, font(F_OSWALD, 34), fill=(220, 220, 220, int(255 * a)), anchor="mm", stroke=3)
    if text:
        shadow_text(d, (W // 2, y - 330), text, font(F_ANTON, 80), fill=(255, 255, 255, int(255 * a)), anchor="mm", stroke=5)
    return im


def ov_document(t, dur, text, p):
    """Paper document / note sliding up with typed text. params: title, style ('paper'|'scrap'|'telegram')."""
    im = blank()
    a = ease(t / 0.35) * (1 - ease((t - dur + 0.3) / 0.3))
    style = p.get("style", "paper")
    pw, ph = (820, 1000) if style == "paper" else (760, 300)
    paper = Image.new("RGBA", (pw, ph), (228, 220, 196, 255) if style != "telegram" else (240, 228, 170, 255))
    pd = ImageDraw.Draw(paper)
    import random
    rnd = random.Random(5)
    for _ in range(1400):
        x, y = rnd.randrange(pw), rnd.randrange(ph)
        c = rnd.randint(170, 215)
        pd.point((x, y), fill=(c, c - 8, c - 25, 255))
    if style == "scrap":  # torn edge
        for x in range(0, pw, 12):
            pd.polygon([(x, 0), (x + 12, 0), (x + 6, rnd.randint(4, 18))], fill=(0, 0, 0, 0))
    title = p.get("title")
    yy = 60
    if title:
        pd.text((pw // 2, yy), title, font=font(F_SERIF, 46), fill=(40, 30, 25, 255), anchor="mm")
        yy += 70
    body = typewriter(text, max(0, t - 0.4), p.get("cps", 30))
    fsz = p.get("size", 54 if style == "scrap" else 38)
    fnt = font(F_SERIF if style != "telegram" else F_MONO, fsz)
    for i, ln in enumerate(body.split("\n")):
        pd.text((pw // 2 if style == "scrap" else 60, yy + i * int(fsz * 1.35) + (ph // 2 - 60 if style == "scrap" else 0)), ln,
                font=fnt, fill=(30, 25, 22, 255), anchor="mm" if style == "scrap" else "la")
    paper = paper.rotate(p.get("rot", -3), expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", paper.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 150), mask=paper.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    alpha = paper.split()[3].point(lambda v: int(v * a))
    paper.putalpha(alpha)
    sh.putalpha(sh.split()[3].point(lambda v: int(v * a)))
    oy = int((1 - ease(t / 0.45)) * 300)
    x = (W - paper.width) // 2
    y = p.get("y", (H - paper.height) // 2 - 80) + oy
    im.alpha_composite(sh, (x + 20, y + 30))
    im.alpha_composite(paper, (x, y))
    return im


def ov_card(t, dur, text, p):
    """Evidence card: small dark card with header + lines (e.g. EVIDENCE #3)."""
    im = blank()
    d = ImageDraw.Draw(im)
    a = ease(t / 0.25) * (1 - ease((t - dur + 0.3) / 0.3))
    acc = ACCENT.get(p.get("mood", "murder"), (230, 40, 40))
    hdr = p.get("header", "EVIDENCE")
    lines = text.split("\n")
    x0, y0 = 80, p.get("y", 1250)
    hgt = 110 + 62 * len(lines)
    off = int((1 - ease(t / 0.3)) * -200)
    d.rounded_rectangle((x0 + off, y0, W - 80 + off, y0 + hgt), radius=18, fill=(10, 10, 12, int(215 * a)), outline=(*acc, int(255 * a)), width=4)
    d.text((x0 + 40 + off, y0 + 50), hdr, font=font(F_OSWALD, 40), fill=(*acc, int(255 * a)), anchor="lm")
    for i, ln in enumerate(lines):
        d.text((x0 + 40 + off, y0 + 115 + i * 62), ln, font=font(F_OSWALD, 46), fill=(240, 240, 240, int(255 * a)), anchor="lm")
    return im


def ov_title(t, dur, text, p):
    return ov_text(t, dur, text, {**p, "size": p.get("size", 130), "y": p.get("y", 760)})


OVERLAYS = {"stamp": ov_stamp, "depth": ov_depth, "timer": ov_timer, "counter": ov_counter, "map": ov_map,
            "timeline": ov_timeline, "document": ov_document, "label": ov_label, "text": ov_text, "card": ov_card,
            "title": ov_title}


def render_overlay(spec, t, dur, mood):
    fn = OVERLAYS.get(spec.get("type", "text"), ov_text)
    p = dict(spec.get("params", {}))
    p.setdefault("mood", mood)
    st = spec.get("start", 0.0)
    du = spec.get("duration", dur - st)
    if t < st or t > st + du:
        return None
    return fn(t - st, du, spec.get("text", ""), p)
