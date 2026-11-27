"""SCUBA-06 — Rodney Fox, great white attack, Aldinga Beach, South Australia, 1963.
One builder per shot: def Sxx(L, n). Builders live in PIPELINE/blender/lib_scuba.py (great_white, gw_swim,
spearfisher, float_buoy, dinghy, shark_cage, film_housing, torso_diagram, film_grain ...).
The attack is IMPLIED only: silhouettes, a white flash, bubbles and silt. No wounds, no blood. People are faceless.
"""
import sys, os, math, random, importlib
import bpy
from mathutils import Vector, Matrix, Quaternion

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_scuba as S
importlib.reload(S)

PI = math.pi
WATER = (0.07, 0.28, 0.3)       # temperate South Australian blue-green
YEL = (1.0, 0.82, 0.15)
# S01 opening framing (S18 ends exactly here)
CAM01_A = Vector((0.9, -4.3, -6.2))
CAM01_T = Vector((0.1, 0.4, -0.9))
SH01_A = Vector((0.45, 2.7, -6.4))      # shark at S01 frame 1
SH01_B = Vector((0.25, 1.2, -3.0))     # shark at S01 last frame


# ----------------------------------------------------------------------------- helpers

def _finish(L):
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "AREA":
            o.data.volume_factor = 0.0
    L.bake_static()


def _upd():
    bpy.context.view_layer.update()


def _aim(o, frm, to, roll=0.0):
    o.location = frm
    q = (Vector(to) - Vector(frm)).to_track_quat("-Z", "Y")
    if roll:
        q = q @ Quaternion((0, 0, 1), roll)
    o.rotation_euler = q.to_euler()
    return o


def _fc(o):
    import studio_lib
    return studio_lib._fcurves(o.animation_data.action)


def look_keys(cam, keys, roll=0.0):
    for f, p, t in keys:
        _aim(cam, p, t, roll)
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)


def rim(L, loc, target, energy=600, size=4, color=(0.6, 0.9, 0.95), name="rim"):
    a = L.area(loc, (0, 0, 0), energy=energy, size=size, color=color, name=name)
    _aim(a, loc, target)
    return a


def key_input(sock, pairs):
    for f, v in pairs:
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=f)


def keys_loc_rot(o, ks):
    """ks: [(frame, loc, rot)]"""
    for f, p, r in ks:
        o.location = p
        o.keyframe_insert("location", frame=f)
        if r is not None:
            o.rotation_euler = r
            o.keyframe_insert("rotation_euler", frame=f)


def hide_keys(objs, pairs):
    for o in objs:
        for f, h in pairs:
            o.hide_render = h
            o.keyframe_insert("hide_render", frame=f)


def subtree(root):
    out = []

    def rec(o):
        if o.type in ("MESH", "CURVE", "FONT"):
            out.append(o)
        for c in o.children:
            rec(c)
    rec(root)
    return out


def snow(L, n, center, size, count=1200, emit=0.25, name="snow"):
    return L.particle_cloud(center, size, count=count, radius=0.005, nframes=n, drift=(0.04, 0.02, 0.01), name=name,
                            mat=L.mat_principled(name + "m", (0.85, 0.9, 0.85), rough=1, emit=(0.6, 0.75, 0.7),
                                                 emit_strength=emit))


def sa_under(L, n, depth=7.0, vol=0.07, bottom=True, rays=True, surface=True, size=110, center=(0, 0), world=WATER,
             under=(0.45, 0.75, 0.7), snow_n=1200):
    """South Australian reef water: blue-green volume, glowing surface overhead, sand/rock/weed bottom, shafts."""
    S.setup(vol_end=50)
    L.set_world(color=tuple(c * 0.12 for c in world), strength=1.0)
    vn = S.world_volume(color=world, density=vol, anisotropy=0.6, absorption=(0.3, 0.6, 0.55),
                        center=(center[0], center[1], -depth / 2), size=(size, size, depth + 0.4))
    out = {"vol": vn}
    if surface:
        surf = L.prim("plane", loc=(center[0], center[1], 0.0), size=size, name="undersurface")
        L.assign(surf, S.mat_water_surface("usurf", color=(0.3, 0.5, 0.5), rough=0.1, alpha=1.0, under_color=under,
                                           under_strength=0.8, ripple=0.5, nframes=n))
        surf.visible_shadow = False
    if bottom:
        sand = S.mat_caustic_ground("sasand", c1=(0.32, 0.3, 0.24), c2=(0.55, 0.52, 0.42), caustic=(0.8, 1.0, 0.9),
                                    strength=0.35, scale=1.3, nframes=n)
        sb = L.seabed(size=size, strength=0.3, mat=sand)
        sb.location = (center[0], center[1], -depth)
        rm = L.mat_noise_surface("reefrock", (0.08, 0.08, 0.06), (0.3, 0.28, 0.2), scale=3, bump=0.6)
        rnd = random.Random(2)
        for i in range(9):
            x, y, r = rnd.uniform(-8, 8) + center[0], rnd.uniform(-2, 10) + center[1], rnd.uniform(0.4, 1.2)
            o = L.prim("ico", loc=(x, y, -depth + r * 0.2), subdivisions=3, radius=r, name="rock")
            o.scale = (1.3, 1.0, 0.55)
            L.add_displace(o, strength=r * 0.25, scale=r * 0.6, name=f"rk{i}")
            L.assign(o, rm)
            S.seaweed_clump((x + 0.5, y, -depth + r * 0.45), count=10, seed=i, color=(0.25, 0.22, 0.06), name=f"weed{i}")
    sun = L.sun(rot=(0.3, 0.12, 0.4), energy=4.0, color=(0.85, 1.0, 0.92), angle=4)
    out["sun"] = sun
    if rays:
        S.god_rays(center=(center[0], center[1] + 3, -0.1), count=7, length=depth + 3, spread=6, tilt=(0.22, 0.1),
                   color=(0.8, 1.0, 0.9), strength=1.0, alpha=0.18, nframes=n)
    if snow_n:
        snow(L, n, (center[0], center[1] + 2, -depth / 2), (14, 14, min(depth, 10)), count=snow_n)
    return out


def sa_above(L, n, wave=0.3, size=160, sun_e=4.5, horizon=(0.75, 0.85, 0.92), deep=(0.0, 0.07, 0.1),
             shallow=(0.05, 0.3, 0.32), foam=True):
    S.setup(vol_end=80)
    S.sky_gradient(top=(0.14, 0.38, 0.78), horizon=horizon, strength=1.0, sun_dir=(0.4, -0.5, 0.65),
                   sun_col=(1, 0.95, 0.85), sun_strength=6.0, below=(0.08, 0.22, 0.24))
    sea = S.ocean(size=size, nframes=n, wave_scale=wave, choppiness=0.85, resolution=10, spatial=50, wind=8, foam=foam,
                  mat=S.mat_ocean("sea_sa", deep=deep, shallow=shallow, rough=0.08, under=(0.4, 0.75, 0.7),
                                  under_strength=1.0))
    sun = L.sun(rot=(math.radians(45), 0, math.radians(-150)), energy=sun_e, color=(1, 0.95, 0.86), angle=2)
    return sea, sun


def fox(L, scuba=False, gun=True, name="fox"):
    P = S.spearfisher(name, scuba=scuba, gun=gun)
    return P


def gw(L, name="gw", length=4.6, belly=(0.86, 0.86, 0.84)):
    return S.great_white(name, length=length, belly=belly)


def float_line(L, a, b, name="fline", sag=0.3):
    a, b = Vector(a), Vector(b)
    pts = [a.lerp(b, k / 4) + Vector((0, 0, -sag * math.sin(math.pi * k / 4))) for k in range(5)]
    return S.tube(pts, radius=0.008, mat=L.mat_principled(name + "m", (0.85, 0.8, 0.6), rough=0.6), name=name)


def matrix_rot(xcol, ycol, zcol):
    return Matrix((xcol, ycol, zcol)).transposed().to_euler()


# ----------------------------------------------------------------------------- S01 / S18 looking up at the surface

def surface_hunt(L, n, cam_keys, shark_keys):
    sa_under(L, n, depth=12, bottom=False, vol=0.06, under=(0.6, 0.9, 0.85))
    F = fox(L)
    r = F["root"]
    r.location = (0.0, 0.0, -0.22)
    r.rotation_euler = (0.05, 0, 0.35)
    L.anim_swim(F, n, kick_rate=0.5, amp=0.15)
    fb = S.float_buoy((1.7, 1.6, 0.0))
    S.bob(fb, n, amp=0.04, rate=0.4, tilt=0.08, base=(1.7, 1.6, 0.02))
    _upd()
    belt = F["root"].matrix_world @ Vector((0.19, -0.38, 0.0))
    float_line(L, belt, (1.7, 1.6, -0.15), sag=0.25)
    G = gw(L, belly=(0.5, 0.52, 0.52))
    g = G["root"]
    for f, p in shark_keys:
        g.location = p
        d = (Vector(cam_keys[-1][1] if False else (0, 0, 0)) - p)
        g.rotation_euler = (0.75, 0, PI + 0.25)
        g.keyframe_insert("location", frame=f)
        g.keyframe_insert("rotation_euler", frame=f)
    S.gw_swim(G, n, rate=0.45, amp=0.22)
    rim(L, (2.5, 2.5, -1.5), (0, 0, -0.3), energy=150, size=3, name="rimA")
    cam, _ = L.camera(loc=cam_keys[0][1], target=CAM01_T, lens=24)
    L.cam_keys(cam, cam_keys)
    L.cam_light(cam, energy=25, color=(0.6, 0.85, 0.85))
    L.handheld(cam, n, amp=0.03, rate=0.4, rot_amp=0.004)
    return cam


def S01(L, n):
    b = CAM01_A + (CAM01_T - CAM01_A).normalized() * 0.9
    surface_hunt(L, n, [(1, CAM01_A), (n, b)], [(1, SH01_A), (n, SH01_B)])
    _finish(L)


def S18(L, n):
    a = CAM01_A - (CAM01_T - CAM01_A).normalized() * 0.9
    surface_hunt(L, n, [(1, a), (n, CAM01_A)], [(1, SH01_A + Vector((0.3, 2.6, -3.8))), (n, SH01_A)])
    _finish(L)


# ----------------------------------------------------------------------------- S02 Aldinga Beach establishing

def S02(L, n):
    sea, sun = sa_above(L, n, wave=0.25, size=240, deep=(0.0, 0.1, 0.14), shallow=(0.08, 0.42, 0.42))
    sand = L.mat_noise_surface("beach", (0.62, 0.55, 0.42), (0.85, 0.78, 0.62), scale=0.2, bump=0.2, voronoi=False)
    bch = L.prim("plane", loc=(0, 95, 0.0), size=1, name="beach")
    bch.scale = (260, 80, 1)
    bch.rotation_euler = (-0.06, 0, 0)
    L.assign(bch, sand)
    cm = L.mat_noise_surface("cliff", (0.42, 0.28, 0.16), (0.7, 0.5, 0.3), scale=0.08, bump=0.7, voronoi=False)
    rnd = random.Random(6)
    for i in range(10):
        c = L.prim("ico", loc=(-120 + i * 26 + rnd.uniform(-6, 6), 128 + rnd.uniform(-6, 6), 0), subdivisions=3, radius=1,
                   name="cliff")
        c.scale = (rnd.uniform(16, 24), rnd.uniform(10, 16), rnd.uniform(8, 14))
        L.add_displace(c, strength=0.2, scale=0.4, name=f"cd{i}")
        L.assign(c, cm)
    reef = L.prim("plane", loc=(0, 30, 0.04), size=1, name="reef")
    reef.scale = (200, 20, 1)
    rm = L.mat_noise_surface("reefm", (0.06, 0.12, 0.08), (0.2, 0.35, 0.3), scale=0.15, rough=0.2, bump=0.1, voronoi=False)
    L.assign(reef, rm)
    for k, (x, y, yaw) in enumerate(((-9, 18, 0.4), (7, 26, -0.9), (-22, 34, 1.2))):
        B = S.dinghy(f"dg{k}")
        S.bob(B["root"], n, amp=0.05, rate=0.35, phase=k, tilt=0.03, base=(x, y, 0.05))
        B["root"].rotation_euler = (0, 0, yaw)
        F = L.char_figure(f"boatfig{k}", color=(0.04, 0.04, 0.05), height=1.7)
        F["root"].parent = B["root"]
        F["root"].location = (0, -0.6, 0.1)
        F["pelvis"].location.z -= 0.45
    for k in range(9):
        x, y = (rnd.uniform(-5, 4), rnd.uniform(2.5, 9)) if k < 3 else (rnd.uniform(-16, 16), rnd.uniform(6, 28))
        fb = S.float_buoy((x, y, 0.0), name=f"fl{k}")
        S.bob(fb, n, amp=0.05, rate=0.4, phase=k, tilt=0.1, base=(x, y, 0.03))
        if k % 2 == 0:
            W = S.swimmer(f"sw{k}", tank=False)
            S.bob(W["root"], n, amp=0.05, rate=0.35, phase=k * 0.7, tilt=0.03, base=(x + 1.2, y - 0.6, -0.05))
    cut = 46
    cam, _ = L.camera(loc=(0, -10, 80), lens=35)
    look_keys(cam, [(1, (0, -40, 70), (0, 50, 0)), (cut - 1, (0, -36, 64), (0, 50, 0)), (cut, (2.5, -6.0, 1.3), (-1.0, 22.0, 0.6)),
                    (n, (2.0, -4.8, 1.25), (-1.5, 22.0, 0.6))])
    cam.data.lens = 45
    for fc in _fc(cam):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT" if kp.co[0] == cut - 1 else "BEZIER"
    L.handheld(cam, n, amp=0.03, rate=0.5, rot_amp=0.004)
    _finish(L)


# ----------------------------------------------------------------------------- S03 split level, duck-dive

def split_env(L, n, depth=5.0):
    """Half-over / half-under: sky + distant shore above a flat rippled surface; blue-green volume below."""
    S.setup(vol_end=40)
    S.sky_gradient(top=(0.14, 0.38, 0.78), horizon=(0.75, 0.85, 0.92), strength=1.0, sun_dir=(0.4, -0.5, 0.65),
                   sun_col=(1, 0.95, 0.85), sun_strength=6.0, below=(0.05, 0.2, 0.22))
    surf = L.prim("plane", loc=(0, 0, 0), size=200, name="surface")
    L.assign(surf, S.mat_water_surface("surf", color=(0.05, 0.25, 0.28), rough=0.08, alpha=0.75,
                                       under_color=(0.55, 0.85, 0.8), under_strength=1.2, ripple=0.5, nframes=n))
    surf.visible_shadow = False
    S.world_volume(color=WATER, density=0.07, absorption=(0.25, 0.55, 0.5), center=(0, 0, -depth / 2 - 0.02),
                   size=(40, 40, depth))
    sand = S.mat_caustic_ground("sand3", c1=(0.32, 0.3, 0.24), c2=(0.55, 0.52, 0.42), strength=0.35, nframes=n)
    sb = L.seabed(size=40, strength=0.3, mat=sand)
    sb.location.z = -depth
    for i in range(5):
        S.seaweed_clump((i * 1.5 - 3, 4 + i, -depth + 0.1), count=10, seed=i, color=(0.25, 0.22, 0.06), name=f"wd{i}")
    shore = L.prim("cube", loc=(0, 70, 1.2), name="shore")
    shore.scale = (120, 6, 1.4)
    L.add_displace(shore, strength=1.2, scale=4, name="shd")
    L.assign(shore, L.mat_noise_surface("shm", (0.45, 0.32, 0.2), (0.75, 0.6, 0.42), scale=0.3, bump=0.5, voronoi=False))
    sun = L.sun(rot=(math.radians(40), 0, math.radians(-150)), energy=4.0, color=(1, 0.95, 0.86), angle=2)
    snow(L, n, (0, 2, -2.5), (10, 10, 4.8), count=800)
    return sun


def tank_icon(L, color=(0.85, 0.95, 1.0), f0=1, f1=8):
    """Line-art scuba cylinder (outline + valve) drawing on; local XY plane."""
    pts = [(-0.18, -0.7, 0), (-0.18, 0.45, 0)]
    for k in range(9):
        a = PI - PI * k / 8
        pts.append((0.18 * math.cos(a), 0.45 + 0.18 * math.sin(a), 0))
    pts += [(0.18, -0.7, 0), (-0.18, -0.7, 0)]
    root = L.link(bpy.data.objects.new("tankicon", None))
    o = S.draw_on_curve(pts, f0, f1, color=color, width=0.02, strength=3.0, name="tankoutline")
    o.parent = root
    v = S.draw_on_curve([(0, 0.63, 0), (0, 0.8, 0), (0.12, 0.8, 0)], f1 - 2, f1, color=color, width=0.02, strength=3.0,
                        name="tankvalve")
    v.parent = root
    return root


def S03(L, n):
    split_env(L, n)
    F = fox(L)
    r = F["root"]
    dive = 49
    r.rotation_euler = (0, 0, PI / 2)
    # pitch head-down for the duck dive (rotate about the body's lateral axis via a parent pivot)
    piv = L.link(bpy.data.objects.new("divepiv", None))
    r.parent = piv
    keys_loc_rot(piv, [(1, (0, 1.2, -0.12), None), (dive - 10, (0, 1.2, -0.08), None), (dive, (0, 1.25, -0.12), None),
                       (dive + 8, (-0.5, 1.25, -0.4), None), (dive + 30, (-1.4, 1.3, -1.9), None), (n, (-1.9, 1.35, -2.6), None)])
    for f, a in ((1, 0.0), (dive, 0.0), (dive + 8, -1.1), (dive + 30, -0.9), (n, -0.75)):
        piv.rotation_euler = (0, a, 0)
        piv.keyframe_insert("rotation_euler", frame=f)
    # breathing: chest rises before the dive
    for f, s in ((1, 1.0), (14, 1.08), (26, 1.0), (36, 1.1), (dive - 2, 1.12), (dive + 4, 1.0)):
        F["torso"].scale = (0.22 * s, 0.42, 0.16 * s)
        F["torso"].keyframe_insert("scale", frame=f)
    for tag in ("L", "R"):
        for f, a in ((dive + 2, 0.0), (dive + 8, 1.3), (dive + 16, 0.2)):
            F[f"hip{tag}"].rotation_euler = (a, 0, 0)
            F[f"hip{tag}"].keyframe_insert("rotation_euler", frame=f)
    L.anim_swim(F, n - dive - 16, kick_rate=0.8, amp=0.3, start=dive + 18)
    S.bubbles_at((-0.3, 1.25, -0.3), [dive + 4 + i % 5 for i in range(12)], rise=1.0, spread=0.15, size=0.03, life=(14, 24),
                 name="splb")
    S.splash_drops((0.5, 1.2, 0.0), [dive + 14, dive + 15], count=25, speed=2.2, size=0.03)
    cam, _ = L.camera(loc=(0.2, -2.6, 0.02), lens=28)
    look_keys(cam, [(1, (0.1, -1.9, 0.02), (-0.1, 1.2, -0.05)), (dive, (0.05, -1.8, 0.0), (-0.2, 1.2, -0.15)),
                    (dive + 18, (-0.5, -1.8, -0.7), (-0.9, 1.2, -1.0)), (n, (-1.2, -1.8, -1.6), (-1.8, 1.3, -2.3))])
    L.cam_light(cam, energy=20, color=(0.7, 0.9, 0.9))
    L.handheld(cam, n, amp=0.015, rate=0.5, rot_amp=0.003)
    ic = tank_icon(L, f0=30, f1=36)
    ic.parent = cam
    for f, s in ((1, 0.001), (29, 0.001), (31, 1.0), (dive + 6, 1.0), (dive + 12, 0.001)):
        ic.scale = (s * 0.55,) * 3
        ic.keyframe_insert("scale", frame=f)
    ic.location = (-0.75, 0.15, -4.0)
    st = S.draw_on_curve([(-0.45, -0.75, 0.02), (0.45, 0.9, 0.02)], 36, 41, color=(1.0, 0.12, 0.08), width=0.05,
                         strength=6.0, name="strike")
    st.parent = ic
    _finish(L)


# ----------------------------------------------------------------------------- S04 the strike (implied)

def S04(L, n):
    sa_under(L, n, depth=6.5, vol=0.06)
    hit = 17
    F = fox(L)
    r = F["root"]
    keys_loc_rot(r, [(1, (-0.3, 0.0, -2.0), (0, 0.0, -PI / 2 - 0.0)), (hit, (0.25, 0.0, -2.35), (0, 0, -PI / 2))])
    r.rotation_euler = (-0.45, 0, -PI / 2)
    r.keyframe_insert("rotation_euler", frame=1)
    L.anim_swim(F, hit, kick_rate=1.0, amp=0.3)
    hide_keys(subtree(r), [(hit, False), (hit + 1, True)])
    G = gw(L, length=4.8)
    g = G["root"]
    keys_loc_rot(g, [(1, (-6.2, 0.4, -2.0), (0, 0, -PI / 2)), (hit, (-1.9, 0.3, -2.3), (0.05, 0, -PI / 2)),
                     (hit + 6, (-0.6, 0.6, -2.8), (0.25, 0.1, -PI / 2 - 0.25)),
                     (hit + 30, (3.5, 2.5, -4.2), (0.3, 0.2, -PI / 2 - 0.7)), (n, (6.0, 6.0, -5.0), (0.3, 0.2, -PI / 2 - 0.9))])
    S.gw_swim(G, n, rate=1.0, amp=0.35)
    S.bubbles_at((0.3, 0.0, -2.3), [hit + i % 14 for i in range(70)], rise=1.3, spread=0.35, size=0.045, life=(30, 60),
                 name="churn")
    silt = L.particle_cloud((0.3, 0.0, -2.3), (1.6, 1.2, 1.2), count=700, radius=0.008, nframes=n, drift=(0.05, 0, 0.05),
                            name="silt", mat=L.mat_principled("siltm", (0.75, 0.75, 0.68), rough=1, emit=(0.5, 0.55, 0.5),
                                                              emit_strength=0.25))
    silt.scale = (0.001,) * 3
    silt.keyframe_insert("scale", frame=hit)
    silt.scale = (1, 1, 1)
    silt.keyframe_insert("scale", frame=hit + 20)
    # whip pan with the shark, flash at contact
    tgt = L.link(bpy.data.objects.new("tgt", None))
    for f, p in ((1, (-1.6, 0.3, -2.1)), (hit, (-0.6, 0.2, -2.3)), (hit + 10, (0.3, 0.2, -2.3)), (n, (0.6, 0.2, -2.2))):
        tgt.location = p
        tgt.keyframe_insert("location", frame=f)
    cam, _ = L.camera(loc=(0.0, -6.5, -1.9), target=tgt, lens=35)
    L.cam_keys(cam, [(1, (-0.8, -6.5, -1.9)), (n, (0.3, -6.0, -2.0))])
    L.cam_light(cam, energy=30, color=(0.7, 0.9, 0.9))
    fl = L.prim("plane", loc=(0, 0, -0.2), size=2, name="flash")
    fl.parent = cam
    L.assign(fl, L.mat_emission("flashm", (1, 1, 1), 8.0))
    hide_keys([fl], [(1, True), (hit, False), (hit + 3, True)])
    S.shake(cam, hit + 3, length=8, amp=0.12, rot=0.02)
    _finish(L)


# ----------------------------------------------------------------------------- S05 the eye

def S05(L, n):
    S.setup(vol_end=30)
    L.set_world(color=(0.02, 0.08, 0.09), strength=1.0)
    S.world_volume(color=WATER, density=0.06, absorption=(0.25, 0.55, 0.5), center=(0, 0, 0), size=(20, 20, 14))
    L.sun(rot=(0.25, 0.1, 0.3), energy=4.0, color=(0.85, 1.0, 0.92))
    S.god_rays(center=(0, 2, 6), count=5, length=10, spread=4, tilt=(0.2, 0.1), color=(0.8, 1, 0.9), strength=1.0,
               alpha=0.15, nframes=n)
    snow(L, n, (0, 1.5, 0), (8, 8, 6), count=1000)
    G = gw(L, length=4.6)
    g = G["root"]
    touch = 40
    _upd()
    eye = G["eyes"][1]
    E = eye.matrix_world.translation.copy()
    keys_loc_rot(g, [(1, (0, 0, 0), (0, 0, 0)), (touch, (0, 0.05, 0), (0, 0, 0.03)), (touch + 4, (-0.1, 0.1, 0), (0, 0, 0.12)),
                     (touch + 22, (-1.6, 1.8, 0.6), (0.2, 0.3, 0.9)), (n, (-3.0, 4.5, 1.0), (0.3, 0.3, 1.2))])
    S.gw_swim(G, n, rate=0.6, amp=0.25)
    # silhouette hand reaching for the eye
    H = S.hand("hand", color=(0.02, 0.02, 0.025), scale=1.4)
    hr = H["root"]
    hr.rotation_euler = matrix_rot((0, 0, -1), (-0.55, 0.35, 0.75), (-0.8, -0.3, -0.5))
    hr.rotation_euler = (Vector(E) - Vector((E.x + 0.5, E.y - 0.45, E.z - 0.55))).to_track_quat("Y", "Z").to_euler()
    for f, p in ((1, E + Vector((0.55, -0.5, -0.65))), (12, E + Vector((0.5, -0.45, -0.55))),
                 (touch - 2, E + Vector((0.1, -0.09, -0.11))), (touch + 4, E + Vector((0.14, -0.12, -0.14))),
                 (touch + 12, E + Vector((0.5, -0.3, -0.5)))):
        hr.location = p
        hr.keyframe_insert("location", frame=f)
    S.curl(H, 1, 0.3)
    S.curl(H, touch - 6, 0.2)
    S.curl(H, touch, 0.7)
    hide_keys(subtree(hr), [(1, False), (touch + 12, True)])
    # the diver tumbles free in bubbles after the release
    F = fox(L, gun=False)
    fr = F["root"]
    keys_loc_rot(fr, [(touch + 2, E + Vector((0.4, 0.4, -0.9)), (0.4, 0.3, 1.0)), (touch + 20, E + Vector((1.3, 0.2, -1.2)), (1.6, 1.0, 1.6)),
                      (n, E + Vector((2.0, 0.4, -1.1)), (2.6, 1.6, 2.2))])
    for tag, sx in (("L", -1), ("R", 1)):
        F[f"shoulder{tag}"].rotation_euler = (-1.0, 0, sx * 1.0)
        F[f"hip{tag}"].rotation_euler = (0.4 * sx, 0, 0)
    hide_keys(subtree(fr), [(1, True), (touch + 2, False)])
    S.bubbles_at(E + Vector((0.6, 0.3, -0.9)), [touch + 2 + i % 16 for i in range(80)], rise=1.4, spread=0.3, size=0.04,
                 life=(26, 44), name="free")
    cam = L.camera(loc=E + Vector((0.5, 0.05, 0.08)), lens=50)[0]
    look_keys(cam, [(1, E + Vector((0.46, 0.06, 0.07)), E), (touch, E + Vector((0.4, 0.04, 0.06)), E),
                    (touch + 6, E + Vector((0.7, 0.0, 0.1)), E + Vector((0.2, 0.2, -0.3))),
                    (touch + 18, E + Vector((3.4, -1.6, 0.4)), E + Vector((0.4, 0.8, -0.5))),
                    (n, E + Vector((4.0, -2.0, 0.5)), E + Vector((0.4, 1.2, -0.4)))])
    for f, l_ in ((1, 50), (touch, 52), (touch + 14, 24), (n, 24)):
        cam.data.lens = l_
        cam.data.keyframe_insert("lens", frame=f)
    gl = L.point(E + Vector((0.3, 0.1, 0.25)), energy=3, color=(0.9, 1, 1), radius=0.05, name="eyeglint")
    rim(L, E + Vector((-0.5, 1.5, 1.5)), E, energy=40, size=2, name="rimE")
    L.cam_light(cam, energy=10, color=(0.7, 0.9, 0.9))
    _finish(L)


# ----------------------------------------------------------------------------- S06 the float dragged under

def S06(L, n):
    sa_under(L, n, depth=12, bottom=False, vol=0.06, under=(0.6, 0.9, 0.85))
    seize = 33
    fb = S.float_buoy((0, 0, 0))
    keys_loc_rot(fb, [(1, (0, 0, 0.02), (0, 0, 0)), (seize - 4, (0, 0, 0.0), (0.1, 0, 0)), (seize, (-0.05, 0.0, -0.15), (0.3, 0.2, 0)),
                      (seize + 4, (-0.3, -0.05, -0.8), (0.8, 0.4, 0)), (n, (-1.6, -0.4, -3.4), (1.4, 0.6, 0))])
    G = gw(L, length=4.6, belly=(0.55, 0.57, 0.57))
    g = G["root"]
    keys_loc_rot(g, [(1, (4.8, 1.8, -3.2), (0.4, 0, PI / 2 + 0.4)), (seize, (0.4, 0.6, -1.95), (0.95, 0, PI / 2 + 0.6)),
                     (seize + 6, (-0.2, 0.3, -2.4), (0.4, 0, PI / 2 + 0.9)), (n, (-1.9, -0.6, -5.2), (-0.3, 0, PI / 2 + 1.2))])
    S.gw_swim(G, n, rate=0.9, amp=0.35)
    # taut float line running down out of frame toward the diver
    line = S.tube([(0, 0, -0.15), (-0.3, -0.6, -2.5), (-0.6, -1.2, -5), (-1.0, -2.0, -9)], radius=0.01,
                  mat=L.mat_principled("flm", (0.85, 0.8, 0.6), rough=0.6), name="fline", order=3)
    for f, top in ((1, Vector((0, 0, -0.15))), (seize, Vector((-0.05, 0, -0.3))), (seize + 4, Vector((-0.3, -0.05, -0.95))),
                   (n, Vector((-1.6, -0.4, -3.55)))):
        bot = Vector((-1.0, -2.0, -9))
        S.tube_keys(line, f, [top, top.lerp(bot, 0.33), top.lerp(bot, 0.66), bot])
    S.bubbles_at((0, 0, -0.2), [seize + i % 10 for i in range(40)], rise=0.8, spread=0.3, size=0.04, life=(18, 34), name="tug")
    S.splash_drops((0, 0, 0.1), [seize, seize + 1], count=20, speed=2.0, size=0.04)
    tgt = L.link(bpy.data.objects.new("tgt", None))
    for f, p in ((1, (0.2, 0.2, -0.4)), (seize, (0.0, 0.1, -0.8)), (n, (-1.0, -0.4, -3.2))):
        tgt.location = p
        tgt.keyframe_insert("location", frame=f)
    cam, _ = L.camera(loc=(1.6, -4.4, -4.2), target=tgt, lens=24)
    L.cam_keys(cam, [(1, (1.6, -4.4, -4.2)), (n, (1.2, -4.6, -5.0))])
    L.cam_light(cam, energy=20, color=(0.6, 0.85, 0.85))
    L.handheld(cam, n, amp=0.03, rate=0.6, rot_amp=0.005)
    _finish(L)


# ----------------------------------------------------------------------------- S07 freeing the line

def S07(L, n):
    sa_under(L, n, depth=9, bottom=False, vol=0.07, rays=False)
    F = fox(L, gun=False)
    r = F["root"]
    r.location = (0, 0, -2.2)
    r.rotation_euler = (0.0, 0.0, 0.0)
    for tag in ("L", "R"):
        F[f"shoulder{tag}"].rotation_euler = (-2.4, 0, 0)   # own arms toward the belt (hidden behind gloves)
        F[f"hip{tag}"].rotation_euler = (0.3, 0, 0)
    _upd()
    M = r.matrix_world
    belt = M @ Vector((0.2, -0.38, 0.0))
    far = M @ Vector((1.6, -3.5, 2.8))
    slip = 31
    line = S.tube([belt, belt.lerp(far, 0.33), belt.lerp(far, 0.66), far], radius=0.012,
                  mat=L.mat_principled("flm", (0.88, 0.82, 0.62), rough=0.6), name="fline", order=3)
    for f, jit in ((1, 0.0), (8, 0.03), (16, -0.03), (24, 0.03), (slip, 0.0)):
        b2 = belt + Vector((jit, 0, jit))
        S.tube_keys(line, f, [b2, b2.lerp(far, 0.33), b2.lerp(far, 0.66), far])
    away = far + Vector((0.5, -1.0, 0.8))
    S.tube_keys(line, slip + 5, [belt.lerp(far, 0.45), belt.lerp(far, 0.7) + Vector((0.2, 0, 0.1)), far + Vector((0.1, 0, 0.1)), away])
    S.tube_keys(line, n, [far + Vector((0.2, -0.3, 0.6)), far + Vector((0.5, -0.6, 0.8)), away + Vector((0.2, -0.3, 0.3)),
                          away + Vector((0.6, -0.8, 0.6))])
    knot = L.prim("sphere", loc=belt, segments=10, ring_count=6, radius=0.03, name="knot")
    L.assign(knot, line.data.materials[0])
    keys_loc_rot(knot, [(slip, belt, None), (slip + 5, belt.lerp(far, 0.45), None), (n, far + Vector((0.2, -0.3, 0.6)), None)])
    for k, (off, yaw) in enumerate(((Vector((0.1, 0.12, 0.06)), 0.0), (Vector((0.12, -0.15, 0.07)), 0.0))):
        H = S.hand(f"gl{k}", color=(0.02, 0.02, 0.025), scale=1.2)
        hr = H["root"]
        hr.rotation_euler = (Vector(belt) - (belt + off)).to_track_quat("Y", "Z").to_euler()
        for f in range(1, n + 1, 6):
            j = 0.02 * math.sin(f * 0.9 + k * 2)
            hr.location = belt + off * (1.4 if f > slip + 2 else 1.0) + Vector((j, j, 0))
            hr.keyframe_insert("location", frame=f)
        for f in range(1, slip, 5):
            S.curl(H, f, 0.5 + 0.4 * ((f // 5 + k) % 2))
        S.curl(H, slip + 3, 0.2)
    cam = L.camera(loc=belt + Vector((0.75, -0.25, 0.35)), lens=40)[0]
    look_keys(cam, [(1, belt + Vector((0.75, -0.25, 0.35)), belt + Vector((0.0, -0.05, 0.0))),
                    (n, belt + Vector((0.8, -0.35, 0.45)), belt + Vector((0.2, -0.3, 0.3)))])
    L.handheld(cam, n, amp=0.03, rate=1.3, rot_amp=0.02)
    L.cam_light(cam, energy=30, color=(0.7, 0.9, 0.9))
    rim(L, belt + Vector((-1, 1, 1.5)), belt, energy=60, size=1.5, name="rimB")
    _finish(L)


# ----------------------------------------------------------------------------- S08 hauled into the dinghy

def S08(L, n):
    sea, sun = sa_above(L, n, wave=0.2, size=120)
    B = S.dinghy("rescue", length=4.2)
    br = B["root"]
    keys_loc_rot(br, [(1, (-3.2, 0.0, 0.05), (0, 0, -PI / 2)), (24, (0.0, 0.0, 0.05), (0, 0, -PI / 2)),
                      (n, (0.25, 0.0, 0.05), (0, 0, -PI / 2 + 0.03))])
    # two crew silhouettes leaning over the near gunwale (boat local -X = world -Y after yaw)
    crew = []
    for k, x in enumerate((-0.25, 0.45)):
        C = L.char_figure(f"crew{k}", color=(0.035, 0.035, 0.04), height=1.75)
        C["root"].parent = br
        C["root"].location = (-0.15, x * 2 - 0.3, -0.25)
        C["root"].rotation_euler = (0, 0, PI / 2)
        for f, lean, arm in ((1, 0.15, 0.3), (24, 0.5, 1.2), (34, 0.9, 2.2), (48, 0.6, 1.6), (n, 0.3, 1.0)):
            C["pelvis"].rotation_euler = (-lean, 0, 0)
            C["pelvis"].keyframe_insert("rotation_euler", frame=f)
            for tag in ("L", "R"):
                C[f"shoulder{tag}"].rotation_euler = (arm, 0, 0)
                C[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
                C[f"hip{tag}"].rotation_euler = (1.2, 0, 0)
                C[f"knee{tag}"].rotation_euler = (-1.6, 0, 0)
        crew.append(C)
    Fx = L.char_figure("foxfig", color=(0.025, 0.025, 0.03), height=1.78)
    fr = Fx["root"]
    keys_loc_rot(fr, [(1, (0.5, -1.15, -1.25), (0.15, 0, 0)), (30, (0.25, -1.1, -1.2), (0.15, 0, 0)),
                      (44, (0.25, -0.95, -0.55), (-0.25, 0, 0)), (n, (0.25, -0.6, -0.15), (-1.1, 0, 0))])
    for tag, sx in (("L", -1), ("R", 1)):
        Fx[f"shoulder{tag}"].rotation_euler = (2.6, 0, sx * 0.2)
    S.foam_patch((0.4, -1.1), 0.15, 0.45, 28, n, name="hfoam", z=0.03)
    S.splash_drops((0.3, -1.1, 0.1), [36, 40], count=25, speed=2.0, size=0.04)
    cam, _ = L.camera(loc=(1.0, -7.0, 0.55), target=(0.0, 0.0, 0.7), lens=35)
    L.cam_keys(cam, [(1, (1.6, -7.0, 0.55)), (n, (0.6, -6.5, 0.5))])
    L.handheld(cam, n, amp=0.04, rate=0.6)
    _finish(L)


# ----------------------------------------------------------------------------- S09 / S10 injury schematic

def diagram_set(L, n, ortho=(1.9, 1.8)):
    L.set_world(color=(0, 0, 0), strength=0)
    bg = L.prim("plane", loc=(0, 2, 0), rot=(PI / 2, 0, 0), size=1, name="bg")
    bg.scale = (20, 20, 1)
    L.assign(bg, S.flat_mat("bgm", (0.004, 0.006, 0.01), 1))
    T = S.torso_diagram("tor")
    cam, _ = L.camera(loc=(0.0, -10, 0.09), lens=50)
    cam.rotation_euler = (PI / 2, 0, 0)
    cam.data.type = "ORTHO"
    for f, s in ((1, ortho[0]), (n, ortho[1])):
        cam.data.ortho_scale = s
        cam.data.keyframe_insert("ortho_scale", frame=f)
    cam.keyframe_insert("location", frame=1)
    return T, cam


RED = (1.0, 0.15, 0.1)


def S09(L, n):
    T, cam = diagram_set(L, n)
    for k, (o, m) in enumerate(T["ribs"]["L"]):
        f0 = 3 + k * 4
        S.emit_keys(m, [(f0 - 1, 2.2), (f0, 7.0), (f0 + 2, 3.0), (f0 + 3, 6.0), (n, 5.0)],
                    [(f0 - 1, (0.9, 0.95, 1.0)), (f0, RED)], "CONSTANT")
    lu = T["lungL"]
    for f, sx, sz in ((1, 1, 1), (32, 1, 1), (55, 0.55, 0.62), (n, 0.5, 0.58)):
        lu.scale = (sx, 1, sz)
        lu.keyframe_insert("scale", frame=f)
    S.emit_keys(T["lungmL"], [(32, 2.5), (55, 4.0)], [(32, (0.4, 0.8, 1.0)), (55, RED)])
    _finish(L)


def S10(L, n):
    T, cam = diagram_set(L, n, ortho=(1.9, 1.72))
    for o, m in T["ribs"]["L"]:
        S.emit_keys(m, [(1, 3.0)], [(1, (0.9, 0.35, 0.3))])
    T["lungL"].scale = (0.5, 1, 0.58)
    S.emit_keys(T["lungmL"], [(1, 3.0)], [(1, (0.9, 0.35, 0.3))])
    # stitch path: across the chest (patient's left side) then down the left upper arm
    path = [Vector(p) for p in ((-0.04, -0.03, 0.4), (0.1, -0.03, 0.3), (0.2, -0.03, 0.14), (0.24, -0.03, -0.02),
                                (0.33, -0.03, 0.36), (0.35, -0.03, 0.15), (0.35, -0.03, -0.08))]
    segs = [(path[0], path[1]), (path[1], path[2]), (path[2], path[3]), (path[4], path[5]), (path[5], path[6])]
    ticks = []
    for a, b in segs:
        k = max(2, int((b - a).length / 0.022))
        for i in range(k):
            ticks.append((a.lerp(b, i / k), (b - a).normalized()))
    tm = L.mat_emission("stitchm", (1, 1, 1), 5.0)
    f0, f1 = 5, 96
    for i, (p, d) in enumerate(ticks):
        o = L.prim("cube", loc=p, name="stitch")
        perp = Vector((-d.z, 0, d.x))
        o.rotation_euler = perp.to_track_quat("X", "Y").to_euler()
        o.scale = (0.022, 0.004, 0.004)
        L.assign(o, tm)
        fa = int(f0 + (f1 - f0) * i / len(ticks))
        o.scale = (0.0001, 0.0001, 0.0001)
        o.keyframe_insert("scale", frame=fa - 1)
        o.scale = (0.022, 0.004, 0.004)
        o.keyframe_insert("scale", frame=fa)
    S.shake(cam, 98, length=6, amp=0.02, rot=0.006)
    _finish(L)


# ----------------------------------------------------------------------------- S11 back to the water

def S11(L, n):
    sea, sun = sa_above(L, n, wave=0.18, size=140, horizon=(0.95, 0.82, 0.62), sun_e=3.5)
    sun.data.color = (1.0, 0.82, 0.6)
    sun.rotation_euler = (math.radians(72), 0, math.radians(175))
    reef = L.prim("plane", loc=(0, 14, 0.03), size=1, name="reef")
    reef.scale = (60, 10, 1)
    L.assign(reef, L.mat_noise_surface("reefm", (0.05, 0.1, 0.07), (0.15, 0.28, 0.22), scale=0.3, rough=0.25, bump=0.1,
                                       voronoi=False))
    F = L.char_figure("foxstand", color=(0.03, 0.03, 0.035), height=1.8)
    F["root"].location = (0, 0, -0.95)
    F["neck"].rotation_euler = (0.1, 0, 0)
    for tag, sx in (("L", -1), ("R", 1)):
        F[f"shoulder{tag}"].rotation_euler = (0.1, sx * 0.12, 0)
    rim(L, (0, 6, 2.5), (0, 0, 0.6), energy=150, size=3, color=(1.0, 0.8, 0.55), name="rimS")
    cam, _ = L.camera(loc=(0.35, -3.8, 1.05), target=(0.0, 3.0, 0.75), lens=35)
    L.cam_keys(cam, [(1, (0.4, -4.0, 1.05)), (n, (0.3, -3.2, 1.0))])
    L.handheld(cam, n, amp=0.02, rate=0.4)
    _finish(L)


# ----------------------------------------------------------------------------- S12 the cage goes in

def S12(L, n):
    sea, sun = sa_above(L, n, wave=0.18, size=120, foam=False)
    S.world_volume(color=WATER, density=0.07, absorption=(0.25, 0.55, 0.5), center=(0, 0, -5.1), size=(30, 30, 10))
    B = S.lobster_boat("lb")
    br = B["root"]
    br.location = (-1.0, 0, 0.1)
    boom = L.prim("cyl", loc=(1.7, -1.5, 3.2), rot=(0, PI / 2 - 0.35, 0), vertices=10, radius=0.07, depth=3.2, name="davit")
    L.assign(boom, L.mat_principled("davm", (0.85, 0.85, 0.82), rough=0.4, metal=0.5))
    post = L.prim("cyl", loc=(0.4, -1.5, 2.2), vertices=10, radius=0.09, depth=2.4, name="davpost")
    L.assign(post, boom.data.materials[0])
    tip = Vector((3.2, -1.5, 3.75))
    C = S.shark_cage("cage")
    land = 20
    for f, z, rx in ((1, 1.6, 0.08), (6, 1.6, -0.08), (11, 1.55, 0.06), (land - 4, 0.6, 0.0), (land, -0.6, 0.0),
                     (land + 10, -2.4, 0.03), (n, -2.7, 0.0)):
        C.location = (3.2, -1.5, z)
        C.rotation_euler = (rx, 0, 0)
        C.keyframe_insert("location", frame=f)
        C.keyframe_insert("rotation_euler", frame=f)
    wire = S.tube([tip, tip + Vector((0, 0, -0.5)), tip + Vector((0, 0, -1))], radius=0.012,
                  mat=L.mat_principled("wirem", (0.3, 0.3, 0.32), rough=0.4), name="wire", order=2)
    for f, z in ((1, 1.6), (land - 4, 0.6), (land, -0.6), (land + 10, -2.4), (n, -2.7)):
        top = z + 1.8 + 0.6
        S.tube_keys(wire, f, [tip, tip.lerp(Vector((3.2, -1.5, top)), 0.5), Vector((3.2, -1.5, top))])
    S.splash_drops((3.2, -1.5, 0.1), [land, land + 1, land + 2], count=60, speed=4.0, size=0.05)
    S.foam_patch((3.2, -1.5), 0.6, 2.2, land, n, name="cfoam", z=0.03)
    S.bubbles_at((3.2, -1.5, -1.0), [land + 2 + i % 10 for i in range(40)], rise=1.0, spread=0.5, size=0.04, life=(14, 26),
                 name="cb")
    cam, _ = L.camera(loc=(7.5, -6.8, 0.8), target=(3.2, -1.5, 0.6), lens=28)
    tgt = cam.constraints[0].target
    for f, cz, tz in ((1, 0.9, 1.8), (land - 2, 0.6, 0.4), (land + 8, -0.6, -1.2), (n, -0.9, -1.9)):
        cam.location = (7.2, -6.5, cz)
        cam.keyframe_insert("location", frame=f)
        tgt.location = (3.2, -1.5, tz)
        tgt.keyframe_insert("location", frame=f)
    L.cam_light(cam, energy=25, color=(0.7, 0.9, 0.9))
    _finish(L)


# ----------------------------------------------------------------------------- S13 / S14 / S15 / S17 cage dives

def cage_set(L, n, cage_at=(0, 0, -3.4), world=(0.06, 0.25, 0.32), vol=0.06):
    sa_under(L, n, depth=14, bottom=False, vol=vol, world=world, snow_n=1400, center=(0, 2))
    C = S.shark_cage("cage", h=2.4)
    C.location = cage_at
    S.bob(C, n, amp=0.04, rate=0.2, tilt=0.01, base=cage_at)
    top = Vector(cage_at) + Vector((0, 0, 3.0))
    S.tube([top, top + Vector((0, 0, 1.0)), Vector((0, 0, 0))], radius=0.012,
           mat=L.mat_principled("ropem", (0.75, 0.72, 0.6), rough=0.6), name="cageline", order=2)
    return C


def S13(L, n):
    C = cage_set(L, n)
    F = fox(L, scuba=True, gun=False)
    r = F["root"]
    S.pose_upright(F, yaw=0.0, reach=())
    r.location = (0.12, 0.05, -2.0)
    for tag, sx in (("L", -1), ("R", 1)):
        F[f"shoulder{tag}"].rotation_euler = (-1.55, 0, sx * -0.3)
    S.bubbles_at((0.12, -0.1, -1.35), [6 + i % 4 for i in range(7)] + [40 + i % 4 for i in range(7)], rise=1.0, spread=0.06,
                 size=0.03, life=(26, 40), name="br")
    G = gw(L, length=4.4)
    g = G["root"]
    keys_loc_rot(g, [(1, (-6.5, 3.2, -2.0), (0, 0, -PI / 2 + 0.1)), (n, (5.5, 2.8, -1.9), (0.0, 0, -PI / 2 - 0.05))])
    L.linear_fcurves(g)
    S.gw_swim(G, n, rate=0.55, amp=0.25)
    rim(L, (2, 6, 1), (0.3, 0, -0.8), energy=300, size=3, name="rimA")
    cam = L.camera(loc=(-0.3, -0.5, -1.25), lens=24)[0]
    look_keys(cam, [(1, (-0.3, -0.5, -1.25), (0.5, 3.0, -2.0)), (n, (-0.26, -0.4, -1.27), (0.8, 3.0, -2.0))])
    L.cam_light(cam, energy=25, color=(0.7, 0.9, 0.9))
    L.handheld(cam, n, amp=0.01, rate=0.4)
    _finish(L)


def S14(L, n):
    C = cage_set(L, n)
    T = fox(L, scuba=True, gun=False, name="taylor")
    r = T["root"]
    S.pose_upright(T, yaw=0.0, reach=())
    r.location = (-0.25, -0.05, -2.05)
    for tag, sx in (("L", -1), ("R", 1)):
        T[f"shoulder{tag}"].rotation_euler = (-1.25, 0, sx * -0.45)
    H = S.film_housing("cine")
    H.parent = r
    H.location = (0.0, 0.72, -0.32)
    H.rotation_euler = (-PI / 2, 0, 0)
    H.scale = (1.15, 1.15, 1.15)
    S.bubbles_at((-0.25, -0.15, -1.4), [10 + i % 4 for i in range(7)] + [60 + i % 4 for i in range(7)], rise=1.0, spread=0.06,
                 size=0.03, life=(26, 40), name="br")
    G = gw(L, length=4.4)
    g = G["root"]
    keys_loc_rot(g, [(1, (-3.0, 9.0, -2.3), (0, 0, PI + 0.5)), (50, (-0.6, 4.6, -2.1), (0, 0, PI + 0.25)),
                     (n, (2.2, 2.6, -1.9), (0, 0, PI - 0.6))])
    S.gw_swim(G, n, rate=0.55, amp=0.25)
    rim(L, (2, 6, 1), (0, 0, -0.8), energy=300, size=3, name="rimA")
    cam = L.camera(loc=(0.35, -0.5, -1.2), lens=35)[0]
    look_keys(cam, [(1, (0.4, -0.55, -1.15), (-0.4, 2.5, -1.95)), (n, (0.28, -0.3, -1.22), (-0.35, 2.5, -1.95))])
    L.cam_light(cam, energy=25, color=(0.7, 0.9, 0.9))
    L.handheld(cam, n, amp=0.01, rate=0.4)
    _finish(L)


def S15(L, n):
    C = cage_set(L, n, world=(0.42, 0.45, 0.33), vol=0.07)
    G = gw(L, length=4.4)
    g = G["root"]
    keys_loc_rot(g, [(1, (-4.5, 4.5, -2.0), (0, 0, -PI / 2 - 0.35)), (34, (-0.4, 1.7, -1.8), (0, 0, -PI / 2 + 0.1)),
                     (n, (1.0, 4.5, -1.9), (0.0, 0, -PI / 2 + 1.2))])
    S.gw_swim(G, n, rate=0.6, amp=0.28)
    cam = L.camera(loc=(-0.1, 0.2, -1.9), lens=18)[0]
    look_keys(cam, [(1, (-0.1, 0.2, -1.9), (-0.6, 3.0, -1.9)), (n, (-0.05, 0.25, -1.9), (0.4, 3.0, -1.9))])
    L.handheld(cam, n, amp=0.012, rate=1.6, rot_amp=0.008)
    S.film_grain(cam, lens=18, strength=0.22, nframes=n)
    L.cam_light(cam, energy=20, color=(0.9, 0.8, 0.6))
    _finish(L)


def S17(L, n):
    cage_set(L, n, cage_at=(-1.6, 4.2, -2.6))
    G = gw(L, length=4.5)
    g = G["root"]
    keys_loc_rot(g, [(1, (-3.0, 1.6, -1.2), (0, 0, -PI / 2)), (n, (3.2, 1.8, -1.15), (0, 0, -PI / 2 + 0.06))])
    L.linear_fcurves(g)
    S.gw_swim(G, n, rate=0.4, amp=0.2)
    # small satellite tag on the dorsal fin
    tg = L.prim("cyl", loc=(0, 0.1, 0.62), vertices=8, radius=0.025, depth=0.12, rot=(PI / 2, 0, 0), name="sattag")
    L.assign(tg, L.mat_principled("tagm", (0.9, 0.6, 0.1), rough=0.4))
    tg.parent = g
    ant = L.prim("cyl", loc=(0, 0.0, 0.75), vertices=6, radius=0.004, depth=0.2, rot=(-0.8, 0, 0), name="ant")
    L.assign(ant, L.mat_principled("antm", (0.05, 0.05, 0.05), rough=0.4))
    ant.parent = g
    cam = L.camera(loc=(-2.6, -4.2, -1.05), lens=35)[0]
    look_keys(cam, [(1, (-2.6, -4.2, -1.0), (-2.6, 1.7, -1.3)), (n, (2.9, -4.0, -1.05), (2.9, 1.8, -1.3))])
    L.cam_light(cam, energy=25, color=(0.7, 0.9, 0.9))
    # research readout: corner brackets + pulsing dot + label, camera-parented around the shark
    bm = L.mat_emission("brm", (0.35, 1.0, 0.9), 4.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = S.polyline([(sx * 0.62, sy * 0.24 - 0.05 + sy * -0.1, 0), (sx * 0.62, sy * 0.34 - 0.05, 0),
                            (sx * 0.5, sy * 0.34 - 0.05, 0)], bm, width=0.008, name="bracket")
            c.parent = cam
            c.location = (0, 0.15, -2.5)
    dot = L.prim("ico", loc=(0, 0, 0), subdivisions=2, radius=0.018, name="pulse")
    L.assign(dot, L.mat_emission("pulsem", (1.0, 0.3, 0.2), 6.0))
    dot.parent = cam
    dot.location = (-0.5, 0.56, -2.5)
    for f in range(1, n + 1, 12):
        dot.scale = (1, 1, 1)
        dot.keyframe_insert("scale", frame=f)
        dot.scale = (0.3, 0.3, 0.3)
        dot.keyframe_insert("scale", frame=f + 6)
    tx = L.text3d("TRACKING", loc=(-0.45, 0.535, -2.5), rot=(0, 0, 0), size=0.06, align="LEFT",
                  mat=L.mat_emission("trkm", (0.35, 1.0, 0.9), 3.0), name="trk")
    tx.parent = cam
    _finish(L)


# ----------------------------------------------------------------------------- S16 cage-diving trips (time-lapse)

def S16(L, n):
    sea, sun = sa_above(L, n, wave=0.35, size=220, deep=(0.0, 0.07, 0.16), shallow=(0.03, 0.3, 0.42))
    rm = L.mat_noise_surface("coast", (0.2, 0.16, 0.12), (0.5, 0.42, 0.32), scale=0.06, bump=0.8)
    rnd = random.Random(9)
    for i in range(11):
        o = L.prim("ico", loc=(-60 + rnd.uniform(-8, 8), -40 + i * 14, -3), subdivisions=3, radius=1, name="headland")
        o.scale = (rnd.uniform(14, 22), rnd.uniform(9, 14), rnd.uniform(10, 22))
        L.add_displace(o, strength=0.25, scale=0.4, name=f"hl{i}")
        L.assign(o, rm)
    broot, _ = S.dive_boat("db")
    C = S.shark_cage("cage")
    C.parent = broot
    C.location = (4.0, -2.5, -1.4)
    for f, p, yaw in ((1, (0, 0, 0.1), 0.0), (16, (0, 0, 0.1), 0.0), (32, (6, 55, 0.1), -0.1), (44, (6, 55, 0.1), PI),
                      (60, (0.5, 3, 0.1), PI - 0.1), (n, (0, 0, 0.1), PI)):
        broot.location = p
        broot.rotation_euler = (0, 0, yaw)
        broot.keyframe_insert("location", frame=f)
        broot.keyframe_insert("rotation_euler", frame=f)
    # light cycles (time-lapse)
    for f, el, az, e, col in ((1, 50, -150, 4.5, (1, 0.95, 0.86)), (20, 25, -110, 3.0, (1, 0.75, 0.5)),
                              (36, 55, -170, 4.5, (1, 0.95, 0.86)), (52, 22, -100, 2.8, (1, 0.72, 0.48)),
                              (n, 48, -150, 4.5, (1, 0.95, 0.86))):
        sun.rotation_euler = (math.radians(90 - el), 0, math.radians(az))
        sun.data.energy = e
        sun.data.color = col
        sun.keyframe_insert("rotation_euler", frame=f)
        sun.data.keyframe_insert("energy", frame=f)
        sun.data.keyframe_insert("color", frame=f)
    cam, _ = L.camera(loc=(18, -26, 16), target=(2, 6, 0), lens=28)
    L.cam_keys(cam, [(1, (18, -26, 16)), (n, (14, -22, 22))])
    _finish(L)
