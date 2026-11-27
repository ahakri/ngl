"""MURDER-07 - Oetzi the Iceman (died c. 3300 BC, found 19 Sep 1991, arrowhead seen 2001, CT 2007).
Shot builders: def SXX(L, n). New reusable builders (glacier ice, abstract form, melt beads, ice axe, helicopter,
kneel pose, glow line art, X-ray back-view art, arrowhead, lightbox, film, CT gantry, copper axe, flint dagger, bow stave,
quiver, einkorn, meat strip, herb sprig, ibex outline, side outline figure, traveller) live in PIPELINE/blender/lib_murder.py.
Body rule: Oetzi is never shown. Only an unreadable dark lump deep under cloudy ice (S01/S06), a sealed case in the CT
(no covered body), a distant traveller silhouette (S14, DRAMATISATION). X-ray/CT = original stylised line art.
Glacier world: gully centred at GULLY (pass runs along Y, ridges rise on +-X, distant range at +Y).
Line art films: back view (patient's left = viewer's left), film centre FILM_C, arrowhead top-left of the film.
"""
import os, sys, math, random, importlib
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_murder as M
import studio_lib as L
importlib.reload(M)
import bpy
from mathutils import Vector, noise

R = math.radians
GULLY = (0.6, 0.9)
GULLY_ROT = R(20)
FILM_C = (0.0, 1.5)          # film centre (x, z) on the lightbox, film in XZ plane at y ~ -0.01
XRAY_COL = (0.72, 0.86, 1.0)


def lin(o):
    M.set_interp(o, "LINEAR")


def const(o):
    M.set_interp(o, "CONSTANT")


def cam_path(c0, c1, t0, t1, n, lens=35, ease=True, f0=1, f1=None):
    cam, ct = L.camera(loc=c0, target=t0, lens=lens)
    cam.data.clip_end = 3000
    f1 = f1 or n
    L.cam_keys(cam, [(f0, c0), (f1, c1)])
    ct.location = t0
    ct.keyframe_insert("location", frame=f0)
    ct.location = t1
    ct.keyframe_insert("location", frame=f1)
    if not ease:
        lin(cam)
        lin(ct)
    return cam, ct


def spot_at(loc, target, energy=400, size_deg=30, blend=0.6, color=(1, 0.9, 0.75), name="spot", radius=0.1):
    s = L.spot(loc, (0, 0, 0), energy=energy, size_deg=size_deg, blend=blend, color=color, name=name, radius=radius)
    s.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return s


def sun_dir(d, energy=3.0, color=(1, 1, 1), angle=1.0, name="sun"):
    s = L.sun(rot=(0, 0, 0), energy=energy, color=color, angle=angle, name=name)
    s.rotation_euler = Vector(d).normalized().to_track_quat("-Z", "Y").to_euler()
    return s


def face(parts, d):
    parts["root"].rotation_euler = (0, 0, math.atan2(-d[0], d[1]))


def neutral(parts, frame):
    for t in ("L", "R"):
        for k in ("hip", "knee", "shoulder", "elbow"):
            parts[k + t].rotation_euler = (0.0, 0, 0) if k != "elbow" else (0.15, 0, 0)
            parts[k + t].keyframe_insert("rotation_euler", frame=frame)


# ============================================================================= glacier world

def G(x, y, gully=True):
    ax = abs(x)
    z = 34.0 * M.smoothstep(14, 130, ax) ** 1.3
    z += 10.0 * M.smoothstep(40, 200, y) - 3.0 * M.smoothstep(-20, -200, y)
    z += 1.5 * noise.noise(Vector((x * 0.03, y * 0.03, 0.4))) + 0.35 * noise.noise(Vector((x * 0.13, y * 0.13, 1.7)))
    z += 0.03 * noise.noise(Vector((x * 0.9, y * 2.2, 3.1)))
    if gully:
        dx, dy = x - GULLY[0], y - GULLY[1]
        c, s = math.cos(GULLY_ROT), math.sin(GULLY_ROT)
        u, v = (dx * c + dy * s) / 3.0, (-dx * s + dy * c) / 1.15
        d = u * u + v * v
        z -= 0.6 * (1 - M.smoothstep(0.25, 1.0, d))
    return z


def sky_day():
    M.dawn_sky(hor=(0.62, 0.72, 0.9), mid=(0.34, 0.5, 0.82), zen=(0.07, 0.16, 0.45), strength=1.0)


def rock_mat(name="rock"):
    return M.mat_dusted(name, base=(0.045, 0.04, 0.036), snow=(0.78, 0.82, 0.9), thresh=0.62, noise_scale=3.0)


def rocks(points, mat, seed=5, size=(0.25, 0.9), sink=0.35, hf=G, name="rk"):
    rnd = random.Random(seed)
    out = []
    for i, (x, y) in enumerate(points):
        s = rnd.uniform(*size)
        o = L.prim("ico", loc=(x, y, hf(x, y) - s * sink), subdivisions=2, radius=s, name=f"{name}{i}")
        o.scale = (rnd.uniform(0.8, 1.4), rnd.uniform(0.7, 1.2), rnd.uniform(0.5, 0.85))
        o.rotation_euler = (0, 0, rnd.uniform(0, 6.28))
        L.add_displace(o, strength=s * 0.35, scale=0.5, name=f"{name}d{i}")
        L.smooth(o)
        L.assign(o, mat)
        out.append(o)
    return out


def glacier_world(L, near=(-45, 45, -45, 70), res=0.6, far=True, range_=True, gully=True, rock_count=60, seed=3, snow_tint=(0.8, 0.85, 0.95)):
    sm = M.mat_snow("snow", tint=snow_tint)
    hf = (lambda x, y: G(x, y, gully))
    x0, x1, y0, y1 = near
    M.heightfield("pass", x0, x1, y0, y1, int((x1 - x0) / res) + 1, int((y1 - y0) / res) + 1, hf, mat=sm)
    if far:
        M.heightfield("pass_far", -420, 420, -300, 420, 120, 103, lambda x, y: hf(x, y) - 0.6, mat=sm)
    if range_:
        M.mountains("range", size=1800, res=150, height=320, seed=7, center=(0, 1250, -20), mat=sm)
    rm = rock_mat()
    rnd = random.Random(seed)
    pts = []
    # rim of the gully
    for k in range(14):
        a = 2 * math.pi * k / 14 + rnd.uniform(-0.15, 0.15)
        u, v = 3.3 * math.cos(a), 1.35 * math.sin(a)
        c, s = math.cos(GULLY_ROT), math.sin(GULLY_ROT)
        pts.append((GULLY[0] + u * c - v * s, GULLY[1] + u * s + v * c))
    rocks(pts, rm, seed=seed, size=(0.18, 0.45), sink=0.3, hf=hf, name="rim")
    pts = []
    while len(pts) < rock_count:
        x, y = rnd.uniform(-40, 40), rnd.uniform(-35, 65)
        if math.hypot(x - GULLY[0], y - GULLY[1]) < 6:
            continue
        pts.append((x, y))
    rocks(pts, rm, seed=seed + 1, size=(0.3, 1.6), sink=0.45, hf=hf, name="rk")
    if gully:
        w = L.prim("cyl", loc=(GULLY[0], GULLY[1], hf(*GULLY) + 0.22), vertices=40, radius=1.0, depth=0.02, name="melt")
        w.scale = (2.9, 1.0, 1.0)
        w.rotation_euler = (0, 0, GULLY_ROT)
        L.assign(w, L.mat_principled("melt_m", (0.015, 0.03, 0.04), rough=0.04))
    return hf, rm


def hikers_pair(L, n, stopA=(1.4, 2.5), stopB=(2.5, 3.1), walk_from=(6.0, 7.5), stop_f=74, hf=G):
    A = M.hiker("hikerA", color=(0.42, 0.035, 0.025))
    B = M.hiker("hikerB", color=(0.035, 0.08, 0.34))
    for P, st, off in ((A, stopA, (0, 0)), (B, stopB, (0.9, 0.7))):
        s0 = (walk_from[0] + off[0], walk_from[1] + off[1])
        face(P, (st[0] - s0[0], st[1] - s0[1]))
        L.anim_walk(P, 1, stop_f, stride=0.45, rate=0.95,
                    travel=((s0[0], s0[1], hf(*s0)), (st[0], st[1], hf(*st))))
        neutral(P, stop_f + 5)
    # after stopping, both turn toward the gully; A points down at it
    for P, st in ((A, stopA), (B, stopB)):
        d = (GULLY[0] - st[0], GULLY[1] - st[1])
        r = P["root"]
        r.keyframe_insert("rotation_euler", frame=stop_f)
        face(P, d)
        r.keyframe_insert("rotation_euler", frame=stop_f + 10)
    sh = A["shoulderR"]
    sh.rotation_euler = (0, 0, 0)
    sh.keyframe_insert("rotation_euler", frame=stop_f + 6)
    sh.rotation_euler = (1.15, 0, -0.1)
    sh.keyframe_insert("rotation_euler", frame=stop_f + 16)
    A["elbowR"].rotation_euler = (0.05, 0, 0)
    A["elbowR"].keyframe_insert("rotation_euler", frame=stop_f + 16)
    A["neck"].rotation_euler = (-0.35, 0, 0)
    A["neck"].keyframe_insert("rotation_euler", frame=stop_f + 16)
    B["neck"].rotation_euler = (-0.3, 0, 0)
    B["neck"].keyframe_insert("rotation_euler", frame=stop_f + 18)
    return A, B


# ============================================================================= S01 ice macro (cold open)

def ice_macro_set(L, n, form=True):
    M.dawn_sky(hor=(0.62, 0.48, 0.42), mid=(0.24, 0.3, 0.42), zen=(0.05, 0.08, 0.16), strength=1.0, sun_dir=(0.8, 0.6, 0.05))
    sun_dir((-0.8, -0.55, -0.12), energy=2.2, color=(1.0, 0.66, 0.42), angle=2.0, name="rimsun")
    sun_dir((0.2, 0.3, -1.0), energy=0.6, color=(0.6, 0.72, 1.0), angle=20, name="skyfill")
    ice = M.mat_glacier_ice("ice", alpha=0.72, glow=0.25)
    S = M.ice_sheet((0, 0, 0), size=(7, 7), thick=0.36, mat=ice, glow=(0.04, 0.26, 0.55), glow_strength=0.9, form=form,
                    form_loc=(0.12, 0.32), form_rot=0.4)
    M.melt_beads((0.0, 0.1, 0.004), size=(1.6, 1.8), count=90, seed=4, rmin=0.003, rmax=0.012)
    return S, ice


def S01(L, n):
    ice_macro_set(L, n)
    # a few beads sliding downhill (toward camera) = meltwater running
    bm = L.mat_principled("run_m", (0.5, 0.65, 0.75), rough=0.03)
    rnd = random.Random(9)
    for i in range(6):
        x, y = rnd.uniform(-0.3, 0.5), rnd.uniform(0.0, 0.6)
        b = L.prim("sphere", loc=(x, y, 0.004), segments=10, ring_count=6, radius=0.012, name=f"run{i}")
        b.scale = (1.0, 1.7, 0.4)
        L.assign(b, bm)
        b.keyframe_insert("location", frame=1)
        b.location = (x + rnd.uniform(-0.02, 0.02), y - rnd.uniform(0.08, 0.16), 0.004)
        b.keyframe_insert("location", frame=n)
        lin(b)
    # red evidence-tag string across the ice + a small manila tag
    pts = [(-0.75 + 1.6 * t, -0.25 + 0.95 * t + 0.04 * math.sin(t * 6), 0.012 + 0.004 * math.sin(t * 9)) for t in [k / 24 for k in range(25)]]
    M.red_string(pts, name="tagstring", strength=0.9)
    tag = L.prim("plane", loc=(-0.62, -0.2, 0.006), size=1, name="tag")
    tag.scale = (0.07, 0.04, 1)
    tag.rotation_euler = (0, 0, 0.5)
    L.assign(tag, M.mat_paper("tag_m", (0.62, 0.5, 0.3)))
    c0, c1 = (-0.62, -1.5, 0.78), (-0.22, -1.12, 0.66)
    cam, ct = cam_path(c0, c1, (0.02, 0.18, -0.12), (0.18, 0.3, -0.14), n, lens=85, ease=False)
    L.handheld(cam, n, amp=0.004, rate=0.4)
    L.bake_static()


# ============================================================================= S02 hikers find the gully

def S02(L, n):
    sky_day()
    sun_dir((-0.25, -0.75, -0.6), energy=4.0, color=(1.0, 0.96, 0.9), angle=0.6, name="sun")
    hf, rm = glacier_world(L)
    # foreground boulder the camera pushes past
    b = L.prim("ico", loc=(-2.1, -2.7, hf(-2.1, -2.7) + 0.1), subdivisions=3, radius=0.75, name="fgrock")
    b.scale = (1.1, 0.9, 0.95)
    L.add_displace(b, strength=0.3, scale=0.5, name="fgd")
    L.assign(b, rm)
    hikers_pair(L, n, stop_f=78)
    c0 = (-2.9, -5.4, hf(-2.9, -5.4) + 2.4)
    c1 = (-1.2, -3.0, hf(-1.2, -3.0) + 2.0)
    t0 = (1.4, 2.9, hf(1.4, 2.9) + 0.55)
    t1 = (1.3, 2.6, hf(1.3, 2.6) + 0.45)
    cam, ct = cam_path(c0, c1, t0, t1, n, lens=32)
    L.handheld(cam, n, amp=0.01, rate=0.4)
    L.bake_static()


# ============================================================================= S03 map plate (dusk range)

def S03(L, n):
    M.dawn_sky(hor=(0.62, 0.36, 0.3), mid=(0.2, 0.18, 0.27), zen=(0.03, 0.04, 0.1), strength=1.0, sun_dir=(0.3, 1.0, 0.04))
    sun_dir((-0.3, -1.0, -0.18), energy=2.5, color=(1.0, 0.55, 0.32), angle=1.0)
    sun_dir((0.4, 0.2, -1.0), energy=0.35, color=(0.45, 0.55, 0.9), angle=10, name="fill")
    M.mountains("alps", size=1600, res=190, height=330, seed=11, center=(0, 300, 0), mat=M.mat_snow("asnow", tint=(0.78, 0.8, 0.88)))
    c0, c1 = (-40, -520, 430), (30, -440, 380)
    cam, ct = cam_path(c0, c1, (0, 200, 40), (10, 220, 30), n, lens=30, ease=False)
    L.bake_static()


# ============================================================================= S04 recovery (no body)

def S04(L, n):
    M.dawn_sky(hor=(0.6, 0.63, 0.68), mid=(0.46, 0.5, 0.57), zen=(0.3, 0.34, 0.42), strength=1.0)
    sun_dir((0.3, -0.4, -1.0), energy=1.4, color=(0.9, 0.93, 1.0), angle=25)
    hf, rm = glacier_world(L, rock_count=40)
    team = []
    spots = [((-1.6, 1.9), 0.4), ((2.4, 2.4), 0.3), ((0.2, 2.6), 0.5)]
    for i, ((x, y), lean) in enumerate(spots):
        P = M.hiker(f"rescuer{i}", color=(0.55, 0.16, 0.03) if i != 1 else (0.06, 0.07, 0.09))
        P["root"].location = (x, y, hf(x, y))
        face(P, (GULLY[0] - x, GULLY[1] - y))
        M.kneel_pose(P, lean=lean, reach=0.2, frame=1)
        # slow working motion: lean in and out
        pel = P["pelvis"]
        for f, dl in ((1, 0), (30 + i * 9, 0.18), (60 + i * 7, 0.02), (n, 0.15)):
            pel.rotation_euler = (-(lean + dl), 0, 0)
            pel.keyframe_insert("rotation_euler", frame=f)
        team.append(P)
        M.ice_axe((x + 0.5 * (GULLY[0] - x) / 3, y + 0.5 * (GULLY[1] - y) / 3, hf(x, y) + 0.02), rot=(R(88), 0, R(30 * i)), name=f"axe{i}")
    # standing figure, back to camera (over-shoulder anchor, left)
    S = M.hiker("standby", color=(0.05, 0.055, 0.07))
    S["root"].location = (-2.3, -2.6, hf(-2.3, -2.6))
    face(S, (1, 1.4))
    # foreground ice axe planted in the snow (rack-focus start)
    fx, fy = -1.12, -3.6
    fr = L.prim("ico", loc=(fx, fy + 0.15, hf(fx, fy) + 0.05), subdivisions=3, radius=0.42, name="fgrock")
    fr.scale = (1.0, 0.8, 0.9)
    L.add_displace(fr, strength=0.12, scale=0.4, name="fgrd")
    L.smooth(fr)
    L.assign(fr, rm)
    M.ice_axe((fx, fy, hf(fx, fy) + 0.3), rot=(R(-6), R(8), R(25)), name="fgaxe", length=0.75)
    H = M.helicopter((7.5, 21.0, hf(7.5, 21.0) + 0.05), rot_z=R(160), name="heli")
    rot = H["rotor"]
    rot.keyframe_insert("rotation_euler", frame=1)
    rot.rotation_euler = (0, 0, 2.2 * n / 24)
    rot.keyframe_insert("rotation_euler", frame=n)
    lin(rot)
    M.snowfall((4, 20, hf(4, 20) + 6), (40, 22, 14), n, count=500, radius=0.007, fall=0.7, wind=(0.6, 0, 0), seed=12, emit=0.2)
    c0 = (-1.2, -5.4, hf(-1.2, -5.4) + 1.2)
    c1 = (-0.95, -4.7, hf(-0.95, -4.7) + 1.3)
    t = (0.6, 2.3, hf(0.6, 2.3) + 0.55)
    cam, ct = cam_path(c0, c1, t, (0.6, 2.3, hf(0.6, 2.3) + 0.45), n, lens=40)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 1.8
    d0 = (Vector((fx, fy, hf(fx, fy) + 1.0)) - Vector(c0)).length
    d1 = (Vector(t) - Vector(c1)).length
    cam.data.dof.focus_distance = d0
    cam.data.dof.keyframe_insert("focus_distance", frame=1)
    cam.data.dof.keyframe_insert("focus_distance", frame=14)
    cam.data.dof.focus_distance = d1
    cam.data.dof.keyframe_insert("focus_distance", frame=34)
    L.handheld(cam, n, amp=0.006, rate=0.5)
    L.bake_static()


# ============================================================================= S05 lab desk radiocarbon readout

YEARS = ["AD 1991", "AD 1500", "AD 1000", "AD 500", "AD 1", "500 BC", "1000 BC", "1500 BC", "2000 BC", "2500 BC", "3000 BC", "3300 BC"]


def S05(L, n):
    L.set_world((0.004, 0.005, 0.008), 1.0)
    z = 0.9
    M.desk(size=(3.0, 2.0), z=z)
    wall = L.prim("plane", loc=(0, 1.2, 1.5), size=1, rot=(R(90), 0, 0))
    wall.scale = (6, 4, 1)
    L.assign(wall, L.mat_noise_surface("labwall", (0.03, 0.035, 0.04), (0.06, 0.065, 0.07), scale=6, bump=0.1, voronoi=False))
    M.hanging_lamp((-0.3, -0.05, z + 0.85), energy=260, cord=1.5)
    scr, sn, sl = L._mat("screen_m")
    p = sn["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    p.inputs["Emission Color"].default_value = (0.01, 0.03, 0.06, 1)
    p.inputs["Emission Strength"].default_value = 1.0
    mon = M.monitor((0.25, 0.4, z), rot_z=R(-8), w=0.72, h=0.44, screen_mat=scr, name="mon")
    mon = mon["root"] if isinstance(mon, dict) else mon
    M.test_tube((-0.18, -0.12, z), glow=(0.35, 0.85, 1.0), strength=2.5, name="vial")
    M.test_tube((-0.1, -0.05, z), glow=(0.35, 0.85, 1.0), strength=1.0, name="vial2")
    # readout: header + switching year text on the screen
    sc_z = 0.12 + 0.22
    hdr = L.text3d("RADIOCARBON DATE", loc=(0, -0.03, sc_z + 0.12), size=0.04, extrude=0, mat=L.mat_emission("hdr_m", (0.45, 0.75, 1.0), 3),
                   font=M.F_OSWALD, name="hdr")
    hdr.parent = mon
    sw = [10 + int(33 * (1 - (1 - k / 11) ** 1.6)) for k in range(12)]
    ym = L.mat_emission("yr_m", (0.75, 0.9, 1.0), 6)
    rm = L.mat_emission("yr_red", (1.0, 0.16, 0.1), 9)
    for k, yr in enumerate(YEARS):
        t = L.text3d(yr, loc=(0, -0.03, sc_z - 0.06), size=0.12, extrude=0, mat=rm if k == len(YEARS) - 1 else ym, font=M.F_ANTON, name=f"yr{k}")
        t.parent = mon
        f_on = 1 if k == 0 else sw[k]
        f_off = sw[k + 1] if k + 1 < len(YEARS) else n + 1
        t.hide_render = k != 0
        t.keyframe_insert("hide_render", frame=1)
        if k:
            t.hide_render = False
            t.keyframe_insert("hide_render", frame=f_on)
        if f_off <= n:
            t.hide_render = True
            t.keyframe_insert("hide_render", frame=f_off)
        const(t)
    bar_m = L.mat_emission("bar_m", (0.3, 0.6, 1.0), 4)
    bar = L.prim("cube", loc=(0, -0.03, sc_z - 0.15))
    bar.scale = (0.3, 0.002, 0.006)
    L.assign(bar, bar_m)
    bar.parent = mon
    bar.scale.x = 0.001
    bar.keyframe_insert("scale", frame=8)
    bar.scale.x = 0.3
    bar.keyframe_insert("scale", frame=44)
    L.area((0.6, -1.2, z + 1.2), (R(60), 0, R(30)), energy=12, size=2, color=(0.6, 0.75, 1.0), name="fill")
    c0, c1 = (-0.34, -0.62, z + 0.28), (0.24, -0.5, z + 0.42)
    cam, ct = cam_path(c0, c1, (-0.16, -0.1, z + 0.08), (0.27, 0.38, z + 0.33), n, lens=35)
    L.handheld(cam, n, amp=0.004, rate=0.5)
    L.bake_static()


# ============================================================================= S06 golden-hour crane out from the ice

def S06(L, n):
    M.dawn_sky(hor=(0.85, 0.55, 0.32), mid=(0.35, 0.36, 0.48), zen=(0.06, 0.1, 0.24), strength=1.0, sun_dir=(0.9, 0.35, 0.05))
    sun_dir((-0.9, -0.38, -0.16), energy=3.2, color=(1.0, 0.6, 0.32), angle=0.8)
    sun_dir((0.3, 0.2, -1.0), energy=0.45, color=(0.5, 0.6, 0.95), angle=15, name="fill")
    hf, rm = glacier_world(L, gully=True, rock_count=90, snow_tint=(0.82, 0.84, 0.9))
    gz = hf(*GULLY)
    ice = M.mat_glacier_ice("ice6", alpha=0.62, glow=0.3, scale=3.0)
    S = M.ice_sheet((GULLY[0], GULLY[1], gz + 0.3), size=(4.6, 1.9), thick=0.3, mat=ice, glow=(0.04, 0.26, 0.55), glow_strength=0.7,
                    form=True, form_loc=(0.1, 0.0), form_rot=0.2, name="ice6s")
    for k in ("top", "deep"):
        S[k].rotation_euler = (0, 0, GULLY_ROT)
    S["form"].scale = (0.8, 0.8, 0.8)
    c0 = (GULLY[0] - 0.5, GULLY[1] - 2.2, gz + 1.6)
    c1 = (-22.0, -60.0, gz + 34.0)
    cam, ct = cam_path(c0, c1, (GULLY[0], GULLY[1], gz), (GULLY[0], GULLY[1] + 20, gz + 6), n, lens=24)
    for fc in L._fcurves(cam.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "SINE"
    L.bake_static()


# ============================================================================= S07 artefact turntables

def S07(L, n):
    L.set_world((0.0, 0.0, 0.0), 1.0)
    floor = L.prim("plane", loc=(1.6, 0, 0), size=1)
    floor.scale = (20, 20, 1)
    L.assign(floor, L.mat_principled("floor", (0.01, 0.01, 0.012), rough=0.35))
    pm = L.mat_principled("plinth", (0.02, 0.02, 0.022), rough=0.3, metal=0.4)
    xs = (0.0, 1.6, 3.2)
    tables = []
    for i, x in enumerate(xs):
        t = L.prim("cyl", loc=(x, 0, 0.04), vertices=48, radius=0.32, depth=0.08, name=f"tt{i}")
        L.assign(t, pm)
        root = M.empty(f"spin{i}", (x, 0, 0.08))
        tables.append(root)
        root.rotation_euler = (0, 0, R(-30))
        root.keyframe_insert("rotation_euler", frame=1)
        root.rotation_euler = (0, 0, R(-30) + 0.9 * n / 24)
        root.keyframe_insert("rotation_euler", frame=n)
        lin(root)
    ax = M.copper_axe((0, 0, 0), name="axe", haft_len=0.6)
    bpy.data.materials["axe_c"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.55
    ax.parent = tables[0]
    stand = L.prim("cyl", loc=(1.6, 0, 0.1), vertices=12, radius=0.02, depth=0.04)
    L.assign(stand, pm)
    dg = M.flint_dagger((0, 0, 0.04), name="dagger", scale=1.0)
    dg.parent = tables[1]
    bw = M.bow_stave((0, 0, 0.93), length=1.82, rot=(0, R(3), 0), name="bow")
    bw.parent = tables[2]
    qv = M.quiver((0.22, 0.05, 0.0), rot=(0, R(-8), 0), name="quiver")
    qv.parent = tables[2]
    # lights: warm key + cool rim per artefact
    for x, h, d in ((0.0, 0.45, 1.2), (1.6, 0.18, 0.7), (3.2, 1.0, 2.2)):
        spot_at((x - 0.9 * d, -1.2 * d, h + 0.8 * d), (x, 0, h), energy=45 * d * d, size_deg=34, color=(1.0, 0.78, 0.52), name=f"key{x}")
        spot_at((x + 0.8 * d, 1.0 * d, h + 0.5 * d), (x, 0, h), energy=160 * d * d, size_deg=30, color=(0.7, 0.82, 1.0), name=f"rim{x}")
    # camera: three quick slides
    frames = [1, 26, 31, 56, 61, n]
    poses = [((0.05, -1.25, 0.42), (0.0, 0, 0.5)), ((-0.05, -1.15, 0.46), (0.0, 0, 0.48)),
             ((1.62, -0.55, 0.2), (1.6, 0, 0.17)), ((1.58, -0.5, 0.19), (1.6, 0, 0.16)),
             ((3.22, -3.0, 1.25), (3.2, 0, 1.15)), ((3.18, -2.75, 1.2), (3.2, 0, 1.12))]
    cam, ct = L.camera(loc=poses[0][0], target=poses[0][1], lens=50)
    for f, (c, t) in zip(frames, poses):
        cam.location = c
        cam.keyframe_insert("location", frame=f)
        ct.location = t
        ct.keyframe_insert("location", frame=f)
    L.bake_static()


# ============================================================================= evidence board office (S08, S16)

def board_room(L, lamp_energy=200):
    L.set_world((0.003, 0.003, 0.004), 1.0)
    B = M.evidence_board(w=3.0, h=4.4, lamp=True, lamp_energy=lamp_energy)
    return B


def S08(L, n):
    board_room(L)
    c = M.paper_card("CAUSE OF\nDEATH", (0.0, -0.01, 1.35), size=(1.3, 0.85), badge=None, name="cod", text_size=0.26)
    q = L.text3d("?", loc=(0.0, -0.03, 0.25), size=1.2, extrude=0.0, mat=L.mat_principled("q_m", (0.6, 0.02, 0.02), rough=0.5,
                 emit=(0.8, 0.03, 0.02), emit_strength=0.6), font=M.F_ANTON, name="qmark")
    q.data.align_y = "CENTER"
    M.pop_in(q, 14, dur=5)
    # supporting pinned cards (generic): glacier photo + location card
    ph = L.prim("plane", loc=(-1.0, -0.012, 0.6), size=1, rot=(R(90), 0, R(4)))
    ph.scale = (0.62, 0.46, 1)
    L.assign(ph, L.mat_noise_surface("photo", (0.35, 0.42, 0.5), (0.75, 0.8, 0.86), scale=4, bump=0.0, voronoi=False))
    M.paper_card("TISENJOCH\n1991", (1.0, -0.012, 0.65), size=(0.72, 0.5), badge=None, name="loc", text_size=0.12)
    M.paper_card("FOUND", (-0.95, -0.012, -0.45), size=(0.6, 0.36), badge=None, name="found", text_size=0.12)
    M.red_string([(-1.0, -0.035, 0.85), (0.0, -0.035, 1.72)], name="s1")
    M.red_string([(1.0, -0.035, 0.85), (0.0, -0.035, 1.72)], name="s2")
    L.particle_cloud((0, -0.9, 1.2), (2.4, 1.0, 2.0), count=60, radius=0.003, drift=(0.02, 0, -0.01), nframes=n, name="dust")
    c0, c1 = (0.1, -4.6, 1.05), (0.05, -3.7, 1.15)
    cam, ct = cam_path(c0, c1, (0, 0, 0.75), (0, 0, 0.85), n, lens=35)
    L.handheld(cam, n, amp=0.012, rate=0.5)
    L.bake_static()


# ============================================================================= X-ray lightbox (S09, S10, S11)

def xray_room(L, w=1.05, h=1.3, x=0.0, energy=3.5, extra_box=True):
    L.set_world((0.002, 0.003, 0.005), 1.0)
    wall = L.prim("plane", loc=(0, 0.14, 1.5), size=1, rot=(R(90), 0, 0))
    wall.scale = (8, 6, 1)
    L.assign(wall, L.mat_noise_surface("rwall", (0.025, 0.03, 0.035), (0.05, 0.055, 0.06), scale=5, bump=0.1, voronoi=False))
    flo = L.prim("plane", loc=(0, -2, 0), size=1)
    flo.scale = (8, 8, 1)
    L.assign(flo, L.mat_principled("rfloor", (0.03, 0.03, 0.035), rough=0.4))
    lb = M.lightbox((x, 0, FILM_C[1]), w=w, h=h, energy=energy, name="lb")
    if extra_box:
        M.lightbox((x - w - 0.25, 0, FILM_C[1]), w=w, h=h, energy=0.15, name="lb_off")
        M.lightbox((x + w + 0.25, 0, FILM_C[1]), w=w, h=h, energy=0.15, name="lb_off2")
    return lb


def xray_film(cx, name="x", col=XRAY_COL, strength=2.6, tint=(0.015, 0.03, 0.05), film_glow=1.0, arrow_strength=3.5, y=-0.012):
    film, fe = M.film_sheet((cx, y + 0.004, FILM_C[1]), w=0.9, h=1.12, tint=tint, glow=film_glow, name=name + "_film")
    X = M.xray_back_lines(s=1.0, cx=cx, cz=FILM_C[1], y=y)
    polys = X["spine"] + X["ribs"] + X["clav"] + X["scap"] + X["hum"]
    art, ae = M.glow_lines(name + "_art", polys, color=col, strength=strength, bevel=0.0032)
    ah, ahe = M.arrowhead((X["arrow"][0], y - 0.002, X["arrow"][2]), size=0.042, rot_y=R(-12), color=(1.0, 0.97, 0.9),
                          strength=arrow_strength, name=name + "_ah")
    return {"film": film, "fe": fe, "art": art, "ae": ae, "ah": ah, "ahe": ahe, "tip": X["arrow"]}


def S09(L, n):
    lb = xray_room(L)
    F = xray_film(0.0, name="x9", arrow_strength=3.2)
    # flicker on (never black: frame 1 is a dim glow)
    fl = [(1, 0.25), (3, 0.9), (4, 0.15), (6, 1.0), (7, 0.4), (9, 1.0)]
    M.key_strength(lb["node"], [(f, v * 3.5) for f, v in fl], interp="CONSTANT")
    M.key_strength(F["ae"], [(f, v * 2.6) for f, v in fl], interp="CONSTANT")
    M.key_strength(F["ahe"], [(f, v * 3.2) for f, v in fl], interp="CONSTANT")
    M.key_strength(F["fe"], [(f, max(0.3, v)) for f, v in fl], interp="CONSTANT")
    ld = lb["light"].data
    for f, v in fl:
        ld.energy = v * 42
        ld.keyframe_insert("energy", frame=f)
    const_data(ld)
    tip = F["tip"]
    c0, c1 = (0.08, -2.3, 1.42), (-0.12, -1.25, 1.62)
    cam, ct = cam_path(c0, c1, (0.02, 0, 1.4), (-0.17, 0, 1.68), n, lens=50)
    L.handheld(cam, n, amp=0.004, rate=0.4)
    L.bake_static()


def const_data(idb):
    ad = idb.animation_data
    if ad and ad.action:
        for fc in L._fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def S10(L, n):
    lb = xray_room(L, extra_box=False)
    F = xray_film(0.0, name="x10", arrow_strength=4.0)
    tip = Vector(F["tip"])
    ahc = tip + Vector((0, 0, -0.02))
    # arrowhead brightens + pulses
    M.key_strength(F["ahe"], [(1, 4), (6, 4), (12, 16), (18, 10), (24, 16), (30, 10), (36, 14), (46, 0.0)])
    # red circle draws around it
    ring, re = M.glow_lines("ring", [M.circle_pts((ahc.x, ahc.z), 0.05, n=48, y=-0.02, a0=R(100), a1=R(100) + 2 * math.pi)],
                            color=(1.0, 0.08, 0.05), strength=8.0, bevel=0.0035)
    M.curve_draw(ring, 8, 22)
    M.key_strength(re, [(1, 8.0), (38, 8.0), (48, 0.0)])
    # morph: line art + film fade, diagram (side outline, faceless) fades in
    M.key_strength(F["ae"], [(1, 2.6), (38, 2.6), (50, 0.0)])
    M.key_strength(F["fe"], [(1, 1.0), (38, 1.0), (52, 0.35)])
    M.key_strength(lb["node"], [(1, 3.5), (38, 3.5), (52, 0.8)])
    s = 1.0 / 1.75
    polys, back = M.side_figure_outline(1.75)
    ox, oz = ahc.x - back[0] * s, ahc.z - back[1] * s
    dpolys = [[(ox + x * s, -0.02, oz + z * s) for (x, z) in pl] for pl in polys]
    fig, fe = M.glow_lines("diag", dpolys, color=(0.8, 0.9, 1.0), strength=0.0, bevel=0.0045)
    M.key_strength(fe, [(1, 0.0), (40, 0.0), (54, 3.0)])
    M.hide_until(fig, 40)
    # dotted trajectory: from behind and below, arcing up into the upper back (dashes appear in sequence)
    A, C, B = Vector((ahc.x - 0.36, 0, ahc.z - 0.5)), Vector((ahc.x - 0.3, 0, ahc.z - 0.05)), Vector((ahc.x - 0.012, 0, ahc.z))
    dm = L.mat_emission("dash_m", (1.0, 0.25, 0.15), 6.0)
    K = 12
    for k in range(K):
        t0, t1 = k / K, (k + 0.55) / K
        q0 = (1 - t0) ** 2 * A + 2 * (1 - t0) * t0 * C + t0 ** 2 * B
        q1 = (1 - t1) ** 2 * A + 2 * (1 - t1) * t1 * C + t1 ** 2 * B
        d, _ = M.glow_lines(f"dash{k}", [[(q0.x, -0.022, q0.z), (q1.x, -0.022, q1.z)]], mat=dm, bevel=0.005)
        M.hide_until(d, 50 + k)
    dot = L.prim("sphere", loc=(ahc.x, -0.024, ahc.z), radius=0.016, segments=16, ring_count=8, name="impact")
    L.assign(dot, L.mat_emission("impact_m", (1.0, 0.3, 0.2), 10))
    M.pop_in(dot, 63, dur=4)
    M.hide_until(dot, 62)
    # camera: snap-zoom in (7 frames), hold, then pull back to the diagram
    cam, ct = L.camera(loc=(-0.1, -1.15, 1.7), target=(-0.15, 0, 1.72), lens=50)
    keysC = [(1, (-0.1, -1.15, 1.7), (-0.15, 0, 1.72)), (8, (ahc.x, -0.3, ahc.z), (ahc.x, 0, ahc.z)),
             (38, (ahc.x + 0.01, -0.27, ahc.z), (ahc.x, 0, ahc.z)), (60, (ahc.x + 0.02, -1.45, oz + 0.5 + 0.02), (ahc.x + 0.02, 0, oz + 0.52)),
             (n, (ahc.x + 0.02, -1.55, oz + 0.52), (ahc.x + 0.02, 0, oz + 0.52))]
    for f, c, t in keysC:
        cam.location = c
        cam.keyframe_insert("location", frame=f)
        ct.location = t
        ct.keyframe_insert("location", frame=f)
    M.shake(cam, [8], amp=0.004, decay=6)
    L.bake_static()


def S11(L, n):
    lb = xray_room(L, w=2.1, h=1.3, x=0.0, energy=3.2, extra_box=False)
    A = xray_film(-0.52, name="new", arrow_strength=6.0)
    ring, _ = M.glow_lines("ringA", [M.circle_pts((A["tip"][0], A["tip"][2] - 0.02), 0.05, n=48, y=-0.02)], color=(1.0, 0.08, 0.05),
                           strength=7.0, bevel=0.0035)
    old = M.empty("oldfilm", (0, 0, 0))
    B = xray_film(0.52, name="old", col=(1.0, 0.82, 0.55), strength=1.3, tint=(0.07, 0.045, 0.02), film_glow=1.0, arrow_strength=1.7)
    for k in ("film", "art", "ah"):
        B[k].parent = old
    lab_m = L.mat_emission("lab_m", (1.0, 0.92, 0.75), 2.5)
    t1 = L.text3d("26 SEP 1991", loc=(0.52 + 0.24, -0.02, FILM_C[1] - 0.5), size=0.045, extrude=0, mat=lab_m, font=M.F_MONO, name="lab1")
    t1.parent = old
    t2 = L.text3d("2001", loc=(-0.52 + 0.3, -0.02, FILM_C[1] - 0.5), size=0.045, extrude=0, mat=L.mat_emission("lab2_m", (0.8, 0.9, 1.0), 2.5),
                  font=M.F_MONO, name="lab2")
    old.location = (1.4, -0.004, 0)
    old.keyframe_insert("location", frame=1)
    old.location = (0, 0, 0)
    old.keyframe_insert("location", frame=18)
    ringB, _ = M.glow_lines("ringB", [M.circle_pts((B["tip"][0], B["tip"][2] - 0.02), 0.05, n=48, y=-0.022, a0=R(100), a1=R(460))],
                            color=(1.0, 0.08, 0.05), strength=7.0, bevel=0.0035)
    M.curve_draw(ringB, 32, 46)
    c0, c1 = (-0.5, -1.55, 1.42), (0.5, -1.55, 1.42)
    cam, ct = cam_path(c0, c1, (-0.5, 0, 1.48), (0.5, 0, 1.48), n, lens=35, f0=8, f1=n - 6)
    L.handheld(cam, n, amp=0.004, rate=0.4)
    L.bake_static()


# ============================================================================= S12 CT room (no body)

def S12(L, n):
    L.set_world((0.02, 0.025, 0.03), 1.0)
    flo = L.prim("plane", loc=(0, 0, 0), size=1)
    flo.scale = (14, 14, 1)
    L.assign(flo, L.mat_principled("ctfloor", (0.35, 0.38, 0.42), rough=0.25))
    wall = L.prim("plane", loc=(0, 2.6, 2), size=1, rot=(R(90), 0, 0))
    wall.scale = (14, 6, 1)
    L.assign(wall, L.mat_principled("ctwall", (0.3, 0.34, 0.38), rough=0.6))
    C = M.ct_gantry((0, 0, 0), name="ct", color=(0.55, 0.58, 0.62))
    spin = C["spin"]
    spin.keyframe_insert("rotation_euler", frame=1)
    spin.rotation_euler = (2.5 * n / 24 * 2 * math.pi / 4, 0, 0)
    spin.keyframe_insert("rotation_euler", frame=n)
    lin(spin)
    # sealed storage case on the table slides into the bore
    case = M.rounded_box((-1.4, 0, 0.98), (0.95, 0.42, 0.28), (0.62, 0.66, 0.7), rough=0.35, bevel=0.15, name="case")
    case.keyframe_insert("location", frame=1)
    case.location = (-0.75, 0, 0.98)
    case.keyframe_insert("location", frame=n)
    # side monitor with flickering slices
    mon_root = M.empty("ctmon", (1.35, -0.9, 1.25))
    mon_root.rotation_euler = (0, 0, R(-35))
    fr = L.prim("cube", loc=(0, 0.02, 0))
    fr.scale = (0.36, 0.02, 0.24)
    L.assign(fr, L.mat_principled("monf", (0.02, 0.02, 0.025), rough=0.3))
    fr.parent = mon_root
    scr = L.prim("plane", loc=(0, -0.002, 0), size=1, rot=(R(90), 0, 0))
    scr.scale = (0.68, 0.44, 1)
    L.assign(scr, L.mat_emission("monbg", (0.01, 0.025, 0.04), 1.0))
    scr.parent = mon_root
    leg = L.prim("cyl", loc=(1.35, -0.88, 0.55), vertices=8, radius=0.03, depth=1.1)
    L.assign(leg, L.mat_principled("leg", (0.2, 0.2, 0.22), metal=0.8, rough=0.3))
    rnd = random.Random(4)
    for k in range(6):
        polys = []
        rx, rz = 0.16 + rnd.uniform(-0.03, 0.03), 0.11 + rnd.uniform(-0.02, 0.02)
        polys.append([(rx * math.cos(a), -0.004, rz * math.sin(a)) for a in [2 * math.pi * i / 40 for i in range(41)]])
        for j in range(3):
            cx, cz, r = rnd.uniform(-0.08, 0.08), rnd.uniform(-0.05, 0.05), rnd.uniform(0.015, 0.04)
            polys.append([(cx + r * math.cos(a), -0.004, cz + r * math.sin(a)) for a in [2 * math.pi * i / 20 for i in range(21)]])
        sl, _ = M.glow_lines(f"slice{k}", polys, color=(0.6, 0.85, 1.0), strength=3.0, bevel=0.002)
        sl.parent = mon_root
        f0 = 1 + k * (n // 6)
        f1 = f0 + n // 6
        sl.hide_render = k != 0
        sl.keyframe_insert("hide_render", frame=1)
        if k:
            sl.hide_render = False
            sl.keyframe_insert("hide_render", frame=f0)
        if f1 < n:
            sl.hide_render = True
            sl.keyframe_insert("hide_render", frame=f1)
        const(sl)
    for x in (-1.5, 1.5):
        pnl = L.prim("plane", loc=(x, 0, 3.2), size=1, rot=(R(180), 0, 0))
        pnl.scale = (1.4, 0.8, 1)
        L.assign(pnl, L.mat_emission(f"ceil{x}", (0.8, 0.9, 1.0), 4))
        a = L.area((x, 0, 3.15), (0, 0, 0), energy=200, size=1.4, color=(0.78, 0.88, 1.0), name=f"ca{x}")
        a.data.use_shadow = False
    sun_dir((0.4, 0.5, -1.0), energy=1.2, color=(0.8, 0.88, 1.0), angle=3, name="ctsun")
    c0, c1 = (-2.9, -2.6, 1.75), (0.4, -3.3, 1.55)
    cam, ct = cam_path(c0, c1, (-0.5, 0, 1.0), (-0.1, 0, 1.05), n, lens=28)
    L.bake_static()


# ============================================================================= S13 CT diagram (clavicle, artery)

def S13(L, n):
    L.set_world((0.0, 0.0, 0.0), 1.0)
    gm, _ = M.mat_grid("dgrid", color=(0.1, 0.35, 0.6), bg=(0.004, 0.01, 0.022), scale=5.0, width=0.03, strength=0.6)
    bg = L.prim("plane", loc=(0, 1.0, 0), size=1, rot=(R(90), 0, 0))
    bg.scale = (8, 8, 1)
    L.apply_scale(bg)
    L.assign(bg, gm)
    # monitor bezel (pushed through)
    bz = L.mat_principled("bezel", (0.02, 0.02, 0.024), rough=0.3)
    for (x, z, sx, sz) in ((0, 0.62, 0.62, 0.05), (0, -0.62, 0.62, 0.05), (-0.6, 0, 0.05, 0.62), (0.6, 0, 0.05, 0.62)):
        b = L.prim("cube", loc=(x, -0.7, z))
        b.scale = (sx, 0.03, sz)
        L.assign(b, bz)
    cl = [(-0.55 + 1.0 * t, 0.02 * math.sin(t * 3), 0.33 + 0.07 * t + 0.03 * math.sin(2 * math.pi * t)) for t in [k / 30 for k in range(31)]]
    clav, ce = M.glow_lines("clav", [cl], color=XRAY_COL, strength=2.4, bevel=0.022)
    ribs = []
    for i in range(4):
        z0 = 0.18 - 0.17 * i
        ribs.append([(-0.6 + 1.1 * t, 0.12 + 0.12 * math.sin(t * math.pi), z0 + 0.1 * math.sin(t * math.pi) - 0.1 * t) for t in [k / 24 for k in range(25)]])
    rb, _ = M.glow_lines("ribs", ribs, color=XRAY_COL, strength=1.1, bevel=0.012)
    sc = [(0.05, 0.3, 0.4), (0.42, 0.3, 0.34), (0.3, 0.3, -0.45), (0.0, 0.3, 0.25), (0.05, 0.3, 0.4)]
    sp, _ = M.glow_lines("scap", [sc], color=XRAY_COL, strength=0.9, bevel=0.01)
    hm, _ = M.glow_lines("hum", [[(0.52 + 0.1 * math.cos(a), 0.05, 0.3 + 0.1 * math.sin(a)) for a in [2 * math.pi * k / 30 for k in range(31)]],
                                 [(0.47, 0.05, 0.22), (0.5, 0.05, -0.5)], [(0.6, 0.05, 0.24), (0.62, 0.05, -0.5)]],
                         color=XRAY_COL, strength=1.6, bevel=0.012)
    brk = -0.12
    def art_pts(xa, xb):
        return [(x, -0.05, 0.24 + 0.03 * math.sin((x + 0.6) * 3)) for x in [xa + (xb - xa) * k / 20 for k in range(21)]]
    am = L.mat_emission("artery_m", (0.9, 0.02, 0.01), 2.2)
    a1, _ = M.glow_lines("art1", [art_pts(-0.75, brk)], mat=am, bevel=0.016)
    a2, _ = M.glow_lines("art2", [art_pts(brk, 0.55)], mat=am, bevel=0.016)
    for o, dx in ((a1, -0.035), (a2, 0.035)):
        o.keyframe_insert("location", frame=36)
        o.location = (dx, 0, 0)
        o.keyframe_insert("location", frame=42)
    zb = 0.24 + 0.03 * math.sin((brk + 0.6) * 3)
    ah, ahe = M.arrowhead((brk, -0.09, zb + 0.07), size=0.07, rot_y=R(160), color=(1.0, 0.97, 0.9), strength=5.0, name="ah13")
    ah.keyframe_insert("location", frame=1)
    ah.keyframe_insert("location", frame=28)
    ah.location = (brk, -0.09, zb + 0.015)
    ah.keyframe_insert("location", frame=37)
    glow = L.point((brk, -0.2, zb), energy=0.0, color=(1.0, 0.15, 0.1), radius=0.05, name="brkglow")
    for f, e in ((1, 0), (36, 0), (39, 6), (50, 1.5), (n, 1.5)):
        glow.data.energy = e
        glow.data.keyframe_insert("energy", frame=f)
    cam, ct = L.camera(loc=(0, -2.7, 0.15), target=(0, 0, 0.12), lens=50)
    for f, c, t in ((1, (0, -2.7, 0.15), (0, 0, 0.12)), (26, (-0.02, -1.15, 0.2), (-0.05, 0, 0.18)),
                    (n, (-0.62, -0.95, 0.32), (-0.08, 0, 0.2))):
        cam.location = c
        cam.keyframe_insert("location", frame=f)
        ct.location = t
        ct.keyframe_insert("location", frame=f)
    L.bake_static()


# ============================================================================= S14 dramatisation: lone traveller on the ridge

def RIDGE(x, y):
    z = 3.2 * math.exp(-((y - 2.0) / 7.0) ** 2) + 0.06 * x
    z += 0.5 * noise.noise(Vector((x * 0.08, y * 0.08, 0.2))) + 0.05 * noise.noise(Vector((x * 0.6, y * 0.6, 1.1)))
    if y > 2.0:
        z -= 0.12 * (y - 2.0)
    return z


def S14(L, n):
    M.dawn_sky(hor=(0.7, 0.4, 0.3), mid=(0.17, 0.18, 0.3), zen=(0.025, 0.035, 0.09), strength=1.0, sun_dir=(0.15, 1.0, 0.03))
    sun_dir((-0.12, -1.0, -0.14), energy=2.6, color=(1.0, 0.52, 0.3), angle=1.5, name="rimsun")
    sun_dir((0.3, 0.6, -1.0), energy=0.3, color=(0.45, 0.55, 0.9), angle=20, name="fill")
    sm = M.mat_snow("snow14", tint=(0.72, 0.76, 0.86))
    M.heightfield("ridge", -30, 30, -25, 40, 151, 163, RIDGE, mat=sm)
    M.mountains("range14", size=1800, res=140, height=300, seed=7, center=(0, 1100, -150), mat=M.mat_snow("rsnow", tint=(0.7, 0.72, 0.8)))
    rm = M.mat_dusted("rock14", base=(0.03, 0.028, 0.026), snow=(0.7, 0.74, 0.84), thresh=0.7, noise_scale=3.0)
    rocks([(1.5, 2.6), (-4, 5), (5, 1), (-7, 0.5), (8, 4.5), (2.5, -3)], rm, seed=21, size=(0.35, 0.9), sink=0.35, hf=RIDGE, name="r14")
    big = L.prim("ico", loc=(1.2, 2.4, RIDGE(1.2, 2.4) + 0.2), subdivisions=3, radius=0.62, name="restrock")
    big.scale = (1.2, 0.8, 0.95)
    L.add_displace(big, strength=0.2, scale=0.4, name="rrd")
    L.assign(big, rm)
    P = M.traveller("trav", height=1.65)
    a, b = (-1.6, -1.6), (0.75, 1.55)
    d = (b[0] - a[0], b[1] - a[1])
    face(P, d)
    stop = 48
    L.anim_walk(P, 1, stop, stride=0.32, rate=0.62, travel=((a[0], a[1], RIDGE(*a)), (b[0], b[1], RIDGE(*b))))
    r = P["root"]
    # slow down near the end: re-time the travel with an ease-out
    for fc in L._fcurves(r.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "SINE"
            kp.easing = "EASE_OUT"
    neutral(P, stop + 3)
    M.pose_keys(P, stop + 6)
    # turn toward the rock and sink down to sit against it
    r.keyframe_insert("rotation_euler", frame=stop + 6)
    r.rotation_euler = (0, 0, r.rotation_euler.z + R(150))
    r.keyframe_insert("rotation_euler", frame=stop + 18)
    M.seated_pose(P, slump=0.4, lean=0.25)
    M.pose_keys(P, min(n, stop + 24))
    snow = M.snowfall((0.5, 3.0, RIDGE(0.5, 3) + 3), (14, 10, 8), n, count=420, radius=0.006, fall=0.9, wind=(0.8, 0, 0), seed=14, emit=0.15)
    M.hide_until(snow, 30)
    c0, c1 = (-3.2, -6.8, RIDGE(-3.2, -6.8) + 1.25), (-1.4, -3.4, RIDGE(-1.4, -3.4) + 1.15)
    cam, ct = cam_path(c0, c1, (0.3, 1.5, RIDGE(0.3, 1.5) + 0.9), (0.6, 1.8, RIDGE(0.6, 1.8) + 0.75), n, lens=35)
    L.bake_static()


# ============================================================================= S15 last meal still life

def S15(L, n):
    L.set_world((0.003, 0.003, 0.004), 1.0)
    st = M.rounded_box((0, 0, -0.05), (1.2, 0.8, 0.1), (0.07, 0.065, 0.06), rough=0.8, bevel=0.3, name="stone",
                       mat=L.mat_noise_surface("stone_m", (0.03, 0.028, 0.026), (0.1, 0.095, 0.09), scale=8, bump=0.6, voronoi=True))
    for k, (x, y, rz) in enumerate(((-0.2, -0.05, 0.5), (-0.17, 0.0, 0.62), (-0.24, 0.02, 0.4))):
        e_ = M.einkorn_ear((x + 0.2, y - 0.04, 0.006), rot=(R(-90), 0, rz), name=f"ear{k}", seed=k)
        e_.scale = (1.6, 1.6, 1.6)
    M.meat_strip((0.12, -0.02, 0.012), rot_z=R(-20), name="meat")
    M.meat_strip((0.16, 0.08, 0.012), rot_z=R(10), size=(0.17, 0.05, 0.011), name="meat2")
    M.herb_sprig((-0.05, -0.16, 0.004), rot_z=R(15), name="herb")
    fire = L.point((0.65, -0.25, 0.12), energy=55, color=(1.0, 0.5, 0.2), radius=0.15, name="fire")
    L.flicker(fire, n, base=55, depth=0.35, rate=0.5, seed=3)
    L.point((-0.6, -0.5, 0.5), energy=4, color=(0.5, 0.6, 0.9), radius=0.5, name="cool")
    # ibex line art drawn above the props (vertical plane behind)
    s = 0.24
    polys = [[(-0.02 + x * s, 0.3, 0.1 + z * s) for (x, z) in pl] for pl in M.ibex_outline()]
    ib, ie = M.glow_lines("ibex", polys, color=(0.95, 0.95, 0.9), strength=3.0, bevel=0.0028)
    M.curve_draw(ib, 4, 46)
    # a few embers drifting up at the right edge (away from the props)
    em = L.mat_emission("ember_m", (1.0, 0.45, 0.12), 12)
    rnd = random.Random(7)
    for i in range(7):
        x, y = rnd.uniform(0.33, 0.45), rnd.uniform(-0.2, 0.05)
        e = L.prim("ico", loc=(x, y, 0.02), subdivisions=1, radius=0.004, name=f"ember{i}")
        L.assign(e, em)
        f0 = rnd.randint(1, n // 2)
        e.keyframe_insert("location", frame=f0)
        e.location = (x + rnd.uniform(-0.05, 0.05), y, 0.4 + rnd.uniform(0, 0.2))
        e.keyframe_insert("location", frame=f0 + 40)
        lin(e)
        M.hide_until(e, f0)
    c0, c1 = (-0.18, -0.78, 0.5), (0.06, -0.74, 0.5)
    cam, ct = cam_path(c0, c1, (-0.04, 0.08, 0.03), (0.05, 0.08, 0.03), n, lens=45, ease=False)
    L.bake_static()


# ============================================================================= S16 board: answered + open question

def S16(L, n):
    board_room(L, lamp_energy=170)
    M.paper_card("CAUSE OF DEATH\nARROW", (-0.7, -0.01, 1.4), size=(1.25, 0.72), badge=None, name="cod", text_size=0.16)
    M.paper_card("SHOOTER\nUNKNOWN", (0.75, -0.01, 1.3), size=(1.0, 0.68), badge=None, name="shooter", text_size=0.16)
    # arrowhead card (drawn flint triangle)
    ac = M.paper_card("", (-0.75, -0.01, 0.25), size=(0.7, 0.6), badge=None, name="ahcard")
    tri = M.mesh_obj("ahdraw", [(0, 0, 0.18), (-0.09, 0, -0.08), (-0.05, 0, -0.16), (0.05, 0, -0.16), (0.09, 0, -0.08)], [(0, 1, 2, 3, 4)],
                     mat=L.mat_principled("flint_ink", (0.12, 0.11, 0.1), rough=0.7))
    tri.location = (-0.75, -0.016, 0.22)
    # red string from the arrowhead card to an empty pin (nothing at the end)
    pin_loc = (0.75, -0.03, -0.75)
    M.red_string([(-0.75, -0.035, 0.5), (0.0, -0.035, -0.2), pin_loc], name="toempty", strength=0.9)
    pin = L.prim("sphere", loc=pin_loc, radius=0.035, segments=10, ring_count=6)
    L.assign(pin, L.mat_principled("pin_m", (0.6, 0.04, 0.03), rough=0.3))
    # faint outline where a card would be
    M.glow_lines("emptyslot", [[(0.4, -0.012, -0.8), (1.1, -0.012, -0.8), (1.1, -0.012, -1.3), (0.4, -0.012, -1.3), (0.4, -0.012, -0.8)]],
                 color=(0.5, 0.45, 0.4), strength=0.25, bevel=0.004)
    L.particle_cloud((0, -0.9, 0.5), (2.4, 1.0, 2.0), count=60, radius=0.003, drift=(0.02, 0, -0.01), nframes=n, name="dust")
    c0, c1 = (-0.1, -4.2, 0.6), (0.6, -2.2, -0.5)
    cam, ct = cam_path(c0, c1, (0.0, 0, 0.35), (0.75, 0, -0.85), n, lens=35)
    L.handheld(cam, n, amp=0.008, rate=0.5)
    L.bake_static()


# ============================================================================= S17 museum cold cell -> frost (loop)

def S17(L, n):
    L.set_world((0.004, 0.006, 0.01), 1.0)
    wm = L.mat_noise_surface("cellwall", (0.12, 0.13, 0.14), (0.2, 0.21, 0.22), scale=4, bump=0.1, voronoi=False)
    W, Hh, zc = 1.0, 0.7, 1.45
    for (x, z, sx, sz) in ((0, zc + Hh / 2 + 1.5, 3, 1.5), (0, zc - Hh / 2 - 1.5, 3, 1.5), (-W / 2 - 1.5, zc, 1.5, Hh / 2), (W / 2 + 1.5, zc, 1.5, Hh / 2)):
        b = L.prim("cube", loc=(x, 0.15, z))
        b.scale = (sx, 0.15, sz)
        L.assign(b, wm)
    fm = L.mat_principled("winframe", (0.25, 0.27, 0.3), rough=0.3, metal=0.9)
    for (x, z, sx, sz) in ((0, zc + Hh / 2, W / 2 + 0.06, 0.05), (0, zc - Hh / 2, W / 2 + 0.06, 0.05), (-W / 2, zc, 0.05, Hh / 2), (W / 2, zc, 0.05, Hh / 2)):
        b = L.prim("cube", loc=(x, -0.02, z))
        b.scale = (sx, 0.05, sz)
        L.assign(b, fm)
    frost = M.mat_glacier_ice("frost", deep=(0.08, 0.3, 0.52), surf=(0.7, 0.85, 0.95), alpha=0.55, glow=0.5, crack=0.3, scale=6.0)
    g = L.prim("plane", loc=(0, 0.05, zc), size=1, rot=(R(90), 0, 0), name="glass")
    g.scale = (W, Hh, 1)
    L.assign(g, frost)
    # cell interior: blue light, steel walls, empty-looking steel tray (contents hidden by frost)
    im = L.mat_principled("cellin", (0.5, 0.6, 0.7), rough=0.3, metal=0.6)
    for (x, y, z, sx, sy, sz) in ((0, 2.4, zc, 1.6, 0.05, 1.2), (-1.6, 1.3, zc, 0.05, 1.1, 1.2), (1.6, 1.3, zc, 0.05, 1.1, 1.2), (0, 1.3, zc - 1.0, 1.6, 1.1, 0.05)):
        b = L.prim("cube", loc=(x, y, z))
        b.scale = (sx, sy, sz)
        L.assign(b, im)
    tray = L.prim("cube", loc=(0, 1.3, zc - 0.35))
    tray.scale = (0.9, 0.35, 0.03)
    L.assign(tray, L.mat_principled("tray", (0.7, 0.72, 0.75), rough=0.2, metal=1.0))
    L.area((0, 1.3, zc + 0.9), (0, 0, 0), energy=60, size=1.5, color=(0.45, 0.7, 1.0), name="cellA")
    L.point((0, 1.0, zc), energy=25, color=(0.4, 0.7, 1.0), radius=0.4, name="cellP")
    L.area((0, -1.5, 2.6), (R(30), 0, 0), energy=8, size=2, color=(0.6, 0.7, 0.9), name="outside")
    L.particle_cloud((0, 1.3, zc), (2.6, 1.8, 1.8), count=120, radius=0.004, drift=(0.01, 0, 0.01), nframes=n, name="haze",
                     mat=L.mat_principled("haze_m", (0.7, 0.85, 1.0), rough=1, emit=(0.5, 0.7, 1.0), emit_strength=0.4))
    c0, c1 = (0.0, -2.6, 1.4), (0.02, -0.42, zc + 0.02)
    cam, ct = cam_path(c0, c1, (0, 0.05, zc), (0.02, 0.05, zc + 0.02), n, lens=50)
    for fc in L._fcurves(cam.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "SINE"
            kp.easing = "EASE_IN_OUT"
    L.bake_static()
