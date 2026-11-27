"""HAUNT-07 - Blue Bell Hill (A229, Kent): drivers report hitting a woman who isn't there.
One builder per shot: def Sxx(L, n). New builders (bbh_road, coat_figure, windscreen_rig, box_car, hazard_blink, blue_flash,
custodian_helmet, mat_tartan, blanket, hand_torch) are appended to PIPELINE/blender/lib_haunted.py.
World: dual carriageway along +Y on a 6% grade (UK, drive on the LEFT: uphill carriageway x<0, left lane centre LANE_X,
hard shoulder x -10.4..-7.9). The figure is a GENERIC faceless form in a plain light coat (coat_figure), never pale_woman(),
never a specific real person. Impact = jolt + cut to black; no body anywhere. Blanket lies flat (nothing beneath).
"""
import importlib, sys, os, math, random
_LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PIPELINE", "blender")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import lib_haunted as H
import lib_murder as M
importlib.reload(H)
import bpy
from mathutils import Vector

R = math.radians
LANE_X = -6.16
EYE = (0.35, 0.0, 1.2)
V = 13.9                      # 50 km/h
ZF = H.bbh_z
PITCH = math.atan(H.BBH_GRADE)
BLANKET = (-7.0, 54.0)
_TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")


def night(L, c=(0.004, 0.005, 0.01), vol_end=120):
    H.eevee_quality()
    L.set_world(c, 1.0)
    try:
        bpy.context.scene.eevee.volumetric_end = vol_end
    except Exception:
        pass


def sun_dir(L, d, energy=0.3, color=(0.55, 0.65, 1.0), name="sky"):
    s = L.sun(rot=(0, 0, 0), energy=energy, color=color, angle=3, name=name)
    s.rotation_euler = Vector(d).normalized().to_track_quat("-Z", "Y").to_euler()
    return s


def face(parts, d):
    parts["root"].rotation_euler = (0, 0, math.atan2(-d[0], d[1]))


def road(L, lamps=((-12.2, 40.0), (12.2, 110.0), (-12.2, 175.0)), fog=0.025, trees=170, y0=-90.0, y1=300.0):
    night(L)
    W = H.bbh_road(y0=y0, y1=y1, lamps=lamps, fog=fog, tree_count=trees)
    sun_dir(L, (0.3, -0.8, -0.5), energy=0.18)
    return W


def rig_keys(rig, frames_y, pitch_extra=None):
    """frames_y: list of (frame, y). Rig follows the road surface and grade."""
    for f, y in frames_y:
        rig.location = (LANE_X - EYE[0], y, ZF(LANE_X, y))
        rig.keyframe_insert("location", frame=f)
        rx = PITCH + (pitch_extra(f) if pitch_extra else 0.0)
        rig.rotation_euler = (rx, 0, 0)
        rig.keyframe_insert("rotation_euler", frame=f)
    M.set_interp(rig, "LINEAR")


def pov_cam(L, rig, lens=24, pitch=-3.5, name="pov"):
    cam, _ = L.camera(loc=(0, 0, 0), lens=lens, name=name)
    cam.data.clip_start = 0.02
    cam.data.clip_end = 600
    cam.parent = rig
    cam.location = EYE
    cam.rotation_euler = (R(90 + pitch), 0, 0)
    return cam


def black_card(cam, f0, f1):
    b = L_.prim("plane", loc=(0, 0, -0.03), size=1, name="blackcard")
    b.scale = (0.2, 0.2, 1)
    L_.assign(b, L_.mat_emission("black_m", (0, 0, 0), 0.0))
    b.parent = cam
    b.hide_render = True
    b.keyframe_insert("hide_render", frame=1)
    b.hide_render = False
    b.keyframe_insert("hide_render", frame=f0)
    b.hide_render = True
    b.keyframe_insert("hide_render", frame=f1 + 1)
    M.set_interp(b, "CONSTANT")
    return b


L_ = None


def _bind(L):
    global L_
    L_ = L


# ============================================================================= S01 / S13 / S02 windscreen POV

def S01(L, n):
    _bind(L)
    road(L)
    P = H.windscreen_rig(n, name="car")
    rig = P["root"]
    f_hit, f_black1 = 33, 40
    ys, y, v = [], 0.0, V
    for f in range(1, n + 1):
        ys.append((f, y))
        if f >= f_black1:
            v = max(0.0, v - 13.9 / 24 * 0.95)
        elif f > f_hit:
            v = max(0.0, v - 13.9 / 24 * 0.6)
        y += v / 24
    jolt = lambda f: (R(-1.6) if f == f_hit + 1 else R(0.9) if f == f_hit + 2 else 0.0) + (R(-1.2) * max(0, 1 - abs(f - 50) / 12) if f > f_black1 else 0)
    rig_keys(rig, ys, jolt)
    cam = pov_cam(L, rig)
    H.handheld(cam, n, amp=0.006, rate=2.0, rot_amp=0.003)
    M.shake(cam, [f_hit + 1], amp=0.05, decay=4)
    black_card(cam, f_hit + 1, f_black1)
    # the figure: steps out of the hard shoulder into the left lane, in frame < 0.5 s, gone at the cut
    yfig = ys[f_hit - 1][1] + EYE[1] + 2.4
    fg = H.coat_figure("walker", emit=0.18)
    r = fg["root"]
    face(fg, (1, -0.15))
    a, b = (-9.0, yfig), (-6.6, yfig)
    H.walk(fg, 20, f_hit - 20, stride=0.5, rate=1.3, travel=((a[0], a[1], ZF(*a)), (b[0], b[1], ZF(*b))), bob=0.02)
    H.key_vis([r] + list(r.children_recursive), [(1, False), (20, True), (f_hit + 1, False)])
    L.bake_static()


def S13(L, n):
    _bind(L)
    road(L)
    P = H.windscreen_rig(n, name="car")
    rig = P["root"]
    ys = [(f, -V * (n - f) / 24.0) for f in range(1, n + 1, 4)] + [(n, 0.0)]
    rig_keys(rig, ys)
    cam = pov_cam(L, rig)
    H.handheld(cam, n, amp=0.006, rate=2.0, rot_amp=0.003)
    L.bake_static()


def S02(L, n):
    _bind(L)
    road(L)
    wk = [(1, 0), (10, 0), (19, 78), (28, 0)]
    P = H.windscreen_rig(n, name="car", wiper_keys=wk)
    rig = P["root"]
    y_stop = 27.5
    rig_keys(rig, [(1, y_stop - 0.25), (8, y_stop), (n, y_stop)], lambda f: R(-0.8) * max(0, 1 - (f - 1) / 8))
    cam = pov_cam(L, rig)
    cam.keyframe_insert("location", frame=1)
    cam.location = (EYE[0], 0.12, EYE[2])
    cam.keyframe_insert("location", frame=n)
    H.handheld(cam, n, amp=0.002, rate=0.6, rot_amp=0.001)
    # hazards: dash tell-tale + amber spill at the front corners
    am = L.mat_emission("haz_dash", (1.0, 0.5, 0.08), 0.2)
    tt = L.prim("cube", loc=(0.35, 0.42, 1.03))
    tt.scale = (0.02, 0.005, 0.012)
    L.assign(tt, am)
    tt.parent = rig
    lights = []
    for sx in (-0.85, 0.85):
        li = L.point((sx, 2.2, 0.7), energy=0.0, color=(1.0, 0.5, 0.08), radius=0.15, name="haz")
        li.parent = rig
        lights.append(li)
    H.hazard_blink({"ind_mat": am, "ind_lights": lights}, n, hz=1.5, energy=40.0, start=14)
    L.bake_static()


# ============================================================================= S03 drone down the hill

def S03(L, n):
    _bind(L)
    W = road(L, lamps=((-12.2, 40.0), (12.2, 110.0), (-12.2, 175.0), (12.2, 240.0)), fog=0.02, trees=220)
    car = H.box_car("crawl", style="hatch", lamp_energy=3000)
    r = car["root"]
    for f, y in ((1, 10.0), (n, 10.0 + 9.0 * n / 24)):
        r.location = (LANE_X, y, ZF(LANE_X, y))
        r.rotation_euler = (PITCH, 0, 0)
        r.keyframe_insert("location", frame=f)
    M.set_interp(r, "LINEAR")
    p0 = (16.0, 205.0, ZF(0, 205) + 55.0)
    p1 = (12.0, 185.0, ZF(0, 185) + 40.0)
    c = H.cam(p0, (-3.0, 60.0, ZF(0, 60)), lens=35)
    H.cam_move(c, [(1, p0, (-3.0, 60.0, ZF(0, 60))), (n, p1, (-4.0, 50.0, ZF(0, 50)))])
    L.bake_static()


# ============================================================================= S04 1974: saloon on the hard shoulder

def S04(L, n):
    _bind(L)
    road(L, lamps=((12.2, 100.0), (-12.2, 165.0)))
    car = H.box_car("saloon74", loc=(-9.0, 60.0, ZF(-9.0, 60.0)), rot_z=R(10), style="saloon", body=(0.12, 0.09, 0.05),
                    door_open=1.0, lamp_energy=2600)
    car["root"].rotation_euler = (PITCH, 0, R(10))
    man = H.figure("bricklayer", color=(0.035, 0.04, 0.05), height=1.78)
    mx, my = -7.3, 58.6
    man["root"].location = (mx, my, ZF(mx, my))
    face(man, (0.15, -1.0))
    man["neck"].rotation_euler = (0.05, 0, R(12))
    man["neck"].keyframe_insert("rotation_euler", frame=1)
    man["neck"].rotation_euler = (0.08, 0, R(-6))
    man["neck"].keyframe_insert("rotation_euler", frame=n)
    for t in ("L", "R"):
        man["shoulder" + t].rotation_euler = (0.1, 0, R(8) if t == "L" else R(-8))
    # exhaust vapour: a small slow puff behind the car
    try:
        M.volume_puff((-9.6, 57.2, ZF(-9.6, 57.2) + 0.35), 1, n, size=0.9, density=0.08, color=(0.6, 0.6, 0.65), dur=n, name="exhaust")
    except Exception:
        pass
    # rim from the far sodium lamp + soft back-glow so the figure separates from the road
    L.point((-6.0, 66.0, ZF(-6, 66) + 2.5), energy=160, color=(1.0, 0.6, 0.3), radius=0.8, name="rimglow")
    p0 = (-10.0, 49.5, ZF(-10.0, 49.5) + 0.75)
    p1 = (-9.6, 53.6, ZF(-9.6, 53.6) + 0.85)
    t0 = (-8.0, 59.5, ZF(-8, 59.5) + 1.05)
    c = H.cam(p0, t0, lens=40)
    H.cam_move(c, [(1, p0, t0), (n, p1, (-7.9, 59.5, ZF(-7.9, 59.5) + 1.05))])
    H.handheld(c, n, amp=0.004, rate=0.4)
    L.bake_static()


# ============================================================================= S05 the blanket is laid down (nothing beneath)

def S05(L, n):
    _bind(L)
    road(L, lamps=((12.2, 110.0),), fog=0.02)
    bx, by = BLANKET
    bz = ZF(bx, by)
    B = H.blanket((bx, by, bz), size=(1.4, 1.0), rot_z=R(8), name="blanket", flap=False)
    root = B["root"]
    root.rotation_euler = (PITCH, R(3), R(8))
    root.location = (bx, by, bz + 0.3)
    root.keyframe_insert("location", frame=1)
    root.rotation_euler = (PITCH, 0, R(8))
    root.location = (bx, by, bz)
    root.keyframe_insert("location", frame=26)
    root.keyframe_insert("rotation_euler", frame=26)
    root.scale = (0.85, 0.7, 1)
    root.keyframe_insert("scale", frame=1)
    root.scale = (1, 1, 1)
    root.keyframe_insert("scale", frame=24)
    # the stopped car beyond, facing away up the hill: reversing lamp lights the blanket, then it pulls away
    car = H.box_car("saloon74", style="saloon", body=(0.12, 0.09, 0.05), lamp_energy=2600)
    cr = car["root"]
    for f, y in ((1, 62.0), (44, 62.0), (n, 80.0)):
        cr.location = (-8.0, y, ZF(-8.0, y))
        cr.rotation_euler = (PITCH, 0, R(4))
        cr.keyframe_insert("location", frame=f)
    rv = L.spot((0, -2.4, 0.7), (0, 0, 0), energy=800, size_deg=40, blend=0.7, color=(1.0, 0.9, 0.75), name="reverse")
    rv.parent = cr
    rv.rotation_euler = (R(-104), 0, 0)
    for f, e in ((1, 800), (42, 800), (52, 0)):
        rv.data.energy = e
        rv.data.keyframe_insert("energy", frame=f)
    L.point((bx - 2.0, by - 3.0, bz + 2.2), energy=14, color=(0.5, 0.6, 0.9), radius=1.0, name="cool")
    p0 = (bx + 0.6, by - 2.6, bz + 1.7)
    t0 = (bx - 0.1, by + 0.9, bz - 0.15)
    c = H.cam(p0, t0, lens=35)
    H.cam_move(c, [(1, p0, t0), (n, (bx + 0.5, by - 2.2, bz + 1.55), (bx - 0.1, by + 1.0, bz - 0.15))])
    H.handheld(c, n, amp=0.002, rate=0.4)
    H.rain((bx, by, bz + 2), (6, 6, 4), n, count=300, speed=7, emit=0.2)
    L.bake_static()


# ============================================================================= S06 police: torches find only the blanket

def S06(L, n):
    _bind(L)
    road(L, lamps=((12.2, 110.0),), fog=0.03)
    bx, by = BLANKET
    bz = ZF(bx, by)
    B = H.blanket((bx, by, bz), size=(1.4, 1.0), rot_z=R(8), name="blanket", flap=True)
    B["root"].rotation_euler = (PITCH, 0, R(8))
    hg = B["flap_hinge"]
    hg.keyframe_insert("rotation_euler", frame=60)
    hg.rotation_euler = (R(115), 0, hg.rotation_euler.z)
    hg.keyframe_insert("rotation_euler", frame=80)
    pol = H.box_car("panda", loc=(-9.2, 45.5, ZF(-9.2, 45.5)), style="saloon", body=(0.55, 0.56, 0.6), police=True, lamp_energy=2200)
    pol["root"].rotation_euler = (PITCH, 0, R(8))
    H.blue_flash(pol["blue"], pol["blue_mat"], n, hz=1.6, energy=1600)
    offs = []
    for k, (a, b, sf) in enumerate((((-5.2, 47.5), (-5.95, 53.4), 50), ((-8.8, 47.8), (-8.3, 52.3), 56))):
        o = H.figure(f"officer{k}", color=(0.012, 0.014, 0.02), height=1.82, coat=True)
        H.custodian_helmet(o)
        face(o, (b[0] - a[0], b[1] - a[1]))
        H.walk(o, 1, sf, stride=0.38, rate=0.85, travel=((a[0], a[1], ZF(*a)), (b[0], b[1], ZF(*b))), skip=("armR",), bob=0.015)
        o["shoulderR"].rotation_euler = (R(62), 0, R(-6))
        o["elbowR"].rotation_euler = (R(10), 0, 0)
        H.hand_torch(o, "R", energy=1100, size_deg=20)
        r = o["root"]
        r.keyframe_insert("rotation_euler", frame=sf)
        face(o, (bx + 0.6 - b[0], by + 0.4 - b[1]) if k == 0 else (bx - b[0], by - b[1]))
        r.keyframe_insert("rotation_euler", frame=sf + 8)
        offs.append(o)
    # officer 0 bends to lift the corner
    o = offs[0]
    pel = o["pelvis"]
    pel.keyframe_insert("rotation_euler", frame=56)
    pel.rotation_euler = (R(-38), 0, 0)
    pel.keyframe_insert("rotation_euler", frame=66)
    o["shoulderL"].keyframe_insert("rotation_euler", frame=56)
    o["shoulderL"].rotation_euler = (R(70), 0, 0)
    o["shoulderL"].keyframe_insert("rotation_euler", frame=66)
    drv = H.figure("driver", color=(0.035, 0.04, 0.05), height=1.78)
    drv["root"].location = (-10.0, 51.0, ZF(-10, 51))
    face(drv, (1, 0.6))
    p0 = (-3.6, 47.2, ZF(-3.6, 47.2) + 1.7)
    t0 = (-7.0, 53.0, ZF(-7, 53) + 0.6)
    c = H.cam(p0, t0, lens=35)
    H.cam_move(c, [(1, p0, t0), (n, (-5.0, 50.6, ZF(-5.0, 50.6) + 1.4), (-6.9, 54.0, ZF(-6.9, 54) + 0.2))])
    H.handheld(c, n, amp=0.004, rate=0.5)
    H.rain((bx, by - 2, bz + 2), (10, 10, 4), n, count=450, speed=7, emit=0.2)
    L.bake_static()


# ============================================================================= S07 timeline plate (dark road, defocused lateral)

def S07(L, n):
    _bind(L)
    road(L, lamps=((-12.2, 40.0), (12.2, 70.0)), fog=0.03)
    p0 = (-13.5, 30.0, ZF(-13.5, 30) + 1.3)
    p1 = (-13.5, 36.0, ZF(-13.5, 36) + 1.3)
    c = H.cam(p0, (0.0, 44.0, ZF(0, 44) + 0.5), lens=35)
    H.cam_move(c, [(1, p0, (0.0, 44.0, ZF(0, 44) + 0.5)), (n, p1, (0.0, 50.0, ZF(0, 50) + 0.5))], ease=False)
    L.dof(c, distance=4.0, fstop=1.2)
    L.bake_static()


# ============================================================================= S08 / S09 1992: torch search

HATCH = (-9.0, 80.0)


def search_set(L, n, cam_mode):
    road(L, lamps=((-12.2, 40.0), (12.2, 110.0)), fog=0.028)
    car = H.box_car("hatch92", loc=(HATCH[0], HATCH[1], ZF(*HATCH)), style="hatch", body=(0.25, 0.04, 0.04), lamp_energy=2400)
    car["root"].rotation_euler = (PITCH, 0, R(4))
    H.hazard_blink(car, n, hz=1.5, energy=450.0)
    d = H.figure("driver92", color=(0.04, 0.06, 0.1), height=1.76, coat=True)
    a = (-10.0, 76.0)
    b = (-9.6, 66.5) if cam_mode == "follow" else (-9.4, 64.0)
    face(d, (b[0] - a[0], b[1] - a[1]))
    walk_f = n - 10 if cam_mode == "follow" else 40
    if cam_mode == "wide":
        a = (-9.6, 66.5)
    H.walk(d, 1, walk_f, stride=0.36, rate=0.85, travel=((a[0], a[1], ZF(*a)), (b[0], b[1], ZF(*b))), skip=("armR",), bob=0.015)
    sh = d["shoulderR"]
    for f in range(1, n + 1, 6):
        sw = math.sin(f / 24 * 2 * math.pi * 0.35)
        lowered = cam_mode == "wide" and f > 44
        sh.rotation_euler = (R(25) if lowered else R(68), 0, R(-35) * sw if not lowered else 0)
        sh.keyframe_insert("rotation_euler", frame=f)
    d["elbowR"].rotation_euler = (R(8), 0, 0)
    H.hand_torch(d, "R", energy=2600, size_deg=18)
    L.point((-7.5, 60.0, ZF(-7.5, 60) + 3.0), energy=60, color=(0.5, 0.6, 0.9), radius=2.0, name="skyfill")
    return car, d


def S08(L, n):
    _bind(L)
    car, d = search_set(L, n, "follow")
    r = d["root"]
    c = H.cam((-9.0, 80.0, 6.0), (-9.6, 60.0, 4.0), lens=35)
    # simple analytic follow (driver path is linear)
    a, b = Vector((-10.0, 76.0, 0)), Vector((-9.6, 66.5, 0))
    def pos(f):
        t = min(1.0, max(0.0, (f - 1) / (n - 11)))
        q = a.lerp(b, t)
        return q
    for f in (1, n // 3, 2 * n // 3, n):
        q = pos(f)
        cp = (q.x + 1.6, q.y + 5.5, ZF(q.x, q.y + 5.5) + 2.9)
        tg = (q.x - 0.2, q.y - 5.0, ZF(q.x, q.y - 5.0) + 0.2)
        H.aim(c, cp, tg, frame=f)
    H.handheld(c, n, amp=0.012, rate=0.9, rot_amp=0.004)
    H.rain((-9.0, 68.0, ZF(-9, 68) + 2.5), (10, 18, 5), n, count=1100, speed=9, emit=0.3)
    L.bake_static()


def S09(L, n):
    _bind(L)
    car, d = search_set(L, n, "wide")
    p0 = (-4.0, 72.0, ZF(-4, 72) + 7.0)
    p1 = (3.0, 82.0, ZF(3, 82) + 24.0)
    t0 = (-9.0, 60.0, ZF(-9, 60))
    c = H.cam(p0, t0, lens=28)
    H.cam_move(c, [(1, p0, t0), (n, p1, (-8.0, 55.0, ZF(-8, 55)))])
    H.rain((-8.0, 64.0, ZF(-8, 64) + 3), (16, 22, 6), n, count=900, speed=9, emit=0.25)
    L.bake_static()


# ============================================================================= S10 sceptics' board

CONTINENTS = {
    "namerica": [(0.08, 0.72), (0.18, 0.82), (0.32, 0.8), (0.33, 0.66), (0.26, 0.56), (0.22, 0.48), (0.17, 0.52), (0.1, 0.62)],
    "samerica": [(0.25, 0.44), (0.32, 0.4), (0.34, 0.3), (0.29, 0.14), (0.26, 0.16), (0.24, 0.34)],
    "europe": [(0.45, 0.72), (0.52, 0.8), (0.58, 0.76), (0.55, 0.66), (0.47, 0.64)],
    "africa": [(0.46, 0.6), (0.57, 0.6), (0.6, 0.48), (0.56, 0.3), (0.52, 0.28), (0.47, 0.46)],
    "asia": [(0.58, 0.78), (0.75, 0.84), (0.9, 0.76), (0.88, 0.6), (0.78, 0.52), (0.66, 0.56), (0.6, 0.66)],
    "australia": [(0.8, 0.34), (0.88, 0.36), (0.9, 0.26), (0.83, 0.22), (0.78, 0.27)],
}
PINS = [(0.49, 0.74), (0.2, 0.66), (0.55, 0.36), (0.85, 0.3), (0.83, 0.68), (0.3, 0.3)]


def world_map(loc, w=1.2, h=0.7, name="wmap"):
    root = M.empty(name, loc)
    pm = L_.mat_principled(name + "_p", (0.62, 0.6, 0.52), rough=0.85)
    pl = L_.prim("plane", loc=(0, 0, 0), size=1, rot=(R(90), 0, 0))
    pl.scale = (w, h, 1)
    L_.assign(pl, pm)
    pl.parent = root
    lm = L_.mat_principled(name + "_l", (0.2, 0.26, 0.22), rough=0.9)
    for k, pts in CONTINENTS.items():
        vs = [((x - 0.5) * w, -0.003, (y - 0.5) * h) for x, y in pts]
        o = M.mesh_obj(name + k, vs, [list(range(len(vs)))], mat=lm)
        o.parent = root
    pins = []
    for i, (x, y) in enumerate(PINS):
        p = L_.prim("sphere", loc=((x - 0.5) * w, -0.02, (y - 0.5) * h), radius=0.018, segments=10, ring_count=6)
        L_.assign(p, L_.mat_principled(name + "_pin", (0.7, 0.04, 0.03), rough=0.3))
        p.parent = root
        pins.append((loc[0] + (x - 0.5) * w, loc[1] - 0.025, loc[2] + (y - 0.5) * h))
    return root, pins


def S10(L, n):
    _bind(L)
    night(L, (0.003, 0.003, 0.004))
    H.evidence_board("board", w=3.0, h=3.6)
    wall = L.prim("plane", loc=(0, 0.06, 0), size=1, rot=(R(90), 0, 0))
    wall.scale = (12, 10, 1)
    L.assign(wall, L.mat_noise_surface("wallm", (0.02, 0.02, 0.022), (0.045, 0.045, 0.05), scale=5, bump=0.1, voronoi=False))
    H.pinned_card("c1", (-0.75, -0.03, 1.15), 1.2, 0.55, ["VANISHING", "HITCHHIKER"], size=0.14)
    H.pinned_card("c2", (0.72, -0.03, 1.2), 1.15, 0.55, ["PHANTOM ON", "THE ROAD"], size=0.13, rot=R(3))
    mroot, pins = world_map((0.0, -0.03, 0.35), w=1.5, h=0.85)
    order = [0, 1, 5, 2, 3, 4, 0]
    M.red_string([pins[i] for i in order], name="worldstring", strength=0.6)
    sp = L.spot((0.3, -2.2, 2.6), (0, 0, 0), energy=900, size_deg=55, blend=0.8, color=(1.0, 0.72, 0.42), name="desklamp")
    sp.rotation_euler = (Vector((0, 0, 0.8)) - Vector((0.3, -2.2, 2.6))).to_track_quat("-Z", "Y").to_euler()
    L.point((-1.5, -1.5, 1.5), energy=12, color=(0.5, 0.6, 0.9), radius=1.0, name="cool")
    L.particle_cloud((0, -0.9, 0.9), (2.4, 1.0, 1.8), count=50, radius=0.003, drift=(0.02, 0, -0.01), nframes=n, name="dust")
    p0, p1 = (-0.9, -3.2, 0.55), (0.8, -3.0, 0.6)
    c = H.cam(p0, (-0.6, 0, 0.5), lens=35)
    H.cam_move(c, [(1, p0, (-0.6, 0, 0.5)), (n, p1, (0.6, 0, 0.5))])
    H.handheld(c, n, amp=0.004, rate=0.4)
    L.bake_static()


# ============================================================================= S11 desk plate under the document

def S11(L, n):
    _bind(L)
    night(L, (0.003, 0.003, 0.004))
    M.desk(size=(3.0, 2.0), z=0.0)
    M.desk_lamp((0.7, 0.45, 0.0), (0.0, 0.0, 0.0), energy=90, rot_z=R(150))
    M.case_folder((-0.1, 0.05, 0.003), rot_z=R(-6), label="A229")
    M.coffee_cup((0.42, -0.25, 0.0))
    M.newspaper((-0.45, -0.3, 0.004), rot_z=R(20), masthead="LOCAL NEWS")
    c = H.cam((0.0, -0.05, 1.3), (0.0, 0.0, 0.0), lens=50)
    H.cam_move(c, [(1, (0.0, -0.05, 1.3), (0.0, 0.0, 0.0)), (n, (0.0, -0.04, 1.15), (0.0, 0.0, 0.0))])
    L.dof(c, distance=0.6, fstop=1.4)
    L.bake_static()


# ============================================================================= S12 rear-view mirror (DRAMATISATION)

def _prerender(L, cam_o, path, res=(432, 130)):
    sc = bpy.context.scene
    keep = (sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.render.filepath, sc.view_settings.view_transform,
            sc.view_settings.look, sc.eevee.taa_render_samples)
    sc.camera = cam_o
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.eevee.taa_render_samples = 16
    sc.frame_set(1)
    bpy.ops.render.render(write_still=True)
    sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.render.filepath = keep[:4]
    sc.view_settings.view_transform, sc.view_settings.look, sc.eevee.taa_render_samples = keep[4:]


def S12(L, n):
    _bind(L)
    road(L, lamps=((-12.2, 40.0), (12.2, 110.0), (-12.2, -40.0)), fog=0.028, y0=-160.0)
    P = H.windscreen_rig(n, name="car", drops=False)
    rig = P["root"]
    y0 = 20.0
    rig_keys(rig, [(1, y0), (n, y0 + 2.2 * n / 24)])
    # tail-light glow behind the car (lights the road behind red)
    for sx in (-0.6, 0.6):
        tl = L.point((sx, -2.4, 0.7), energy=90, color=(1.0, 0.04, 0.02), radius=0.2, name="tailglow")
        tl.parent = rig
    fg = H.coat_figure("walker", emit=0.2)
    fy = y0 - 15.0
    fg["root"].location = (LANE_X + 0.2, fy, ZF(LANE_X, fy))
    face(fg, (0, 1))
    bpy.context.view_layer.update()
    # mirror camera: from the mirror looking back over the car
    mw = P["mirror"].matrix_world.translation.copy()
    mc, _ = L.camera(loc=tuple(mw), lens=30, name="mirrorcam")
    mc.rotation_euler = (R(90 - 2.0) + PITCH * 0, 0, R(180))
    mc.data.clip_start = 0.3
    os.makedirs(_TEX, exist_ok=True)
    tag = f"{os.getpid()}"
    pa, pb = os.path.join(_TEX, f"mirror_{tag}_a.png"), os.path.join(_TEX, f"mirror_{tag}_b.png")
    objs = [fg["root"]] + list(fg["root"].children_recursive)
    for o in objs:
        o.hide_render = True
    _prerender(L, mc, pa)
    for o in objs:
        o.hide_render = False
    _prerender(L, mc, pb)
    for o in objs:
        o.hide_render = True   # never in the main view (it is behind the car)
    # mirror face material: flipped image A -> B switch at f_show
    f_show = 80
    m, nd, lk = L._mat("mirror_m")
    for x in list(nd):
        if x.type == "BSDF_PRINCIPLED":
            nd.remove(x)
    tc = nd.new("ShaderNodeTexCoord")
    mp = nd.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (-1, 1, 1)
    mp.inputs["Location"].default_value = (1, 0, 0)
    lk.new(tc.outputs["UV"], mp.inputs["Vector"])
    ta, tb = nd.new("ShaderNodeTexImage"), nd.new("ShaderNodeTexImage")
    ta.image, tb.image = bpy.data.images.load(pa), bpy.data.images.load(pb)
    for t in (ta, tb):
        lk.new(mp.outputs["Vector"], t.inputs["Vector"])
    mx = nd.new("ShaderNodeMix"); mx.data_type = "RGBA"
    lk.new(ta.outputs["Color"], mx.inputs[6]); lk.new(tb.outputs["Color"], mx.inputs[7])
    fac = mx.inputs[0]
    fac.default_value = 0.0
    fac.keyframe_insert("default_value", frame=1)
    fac.keyframe_insert("default_value", frame=f_show - 1)
    fac.default_value = 1.0
    fac.keyframe_insert("default_value", frame=f_show)
    H._interp_data(m.node_tree, "CONSTANT")
    em = nd.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.1
    lk.new(mx.outputs[2], em.inputs[0])
    lk.new(em.outputs[0], nd["Material Output"].inputs["Surface"])
    L.assign(P["mirror_face"], m)
    # driver camera: road ahead, then tilt up to the mirror and hold; slowest push
    cam, tgt = L.camera(loc=(0, 0, 0), target=(0, 0, 0), lens=70, name="pov")
    cam.data.clip_start = 0.02
    cam.parent = rig
    tgt.parent = rig
    mloc = P["mirror"].location
    for f, cl, tl_ in ((1, EYE, (0.25, 6.0, 0.75)), (52, EYE, (0.25, 6.0, 0.75)), (74, EYE, (mloc.x, mloc.y, mloc.z - 0.07)),
                       (n, (EYE[0] - 0.02, 0.06, EYE[2] + 0.01), (mloc.x, mloc.y, mloc.z - 0.07))):
        cam.location = cl
        cam.keyframe_insert("location", frame=f)
        tgt.location = tl_
        tgt.keyframe_insert("location", frame=f)
    bpy.context.scene.camera = cam
    H.handheld(cam, n, amp=0.002, rate=1.5, rot_amp=0.0015)
    L.bake_static()
