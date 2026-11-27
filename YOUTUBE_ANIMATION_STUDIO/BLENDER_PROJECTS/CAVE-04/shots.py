"""CAVE-04 — Nutty Putty Cave (2009). Shot builders (def Sxx(L, n)). Shared builders: PIPELINE/blender/lib_cave.py
Respectful treatment: John Jones is shown only as boots/legs (S01, alive), a faceless figure from behind (S05),
gloved hands (S06) and a grey diagram outline (S02/S07/S09/S12/S14). No body is depicted after S12."""
import sys, os, math, random
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "PIPELINE", "blender"))
import importlib
import lib_cave as C
importlib.reload(C)
import bpy
from mathutils import Vector, noise

WARM = (1.0, 0.82, 0.58)
COVERALL = (0.16, 0.11, 0.07)
ANCHOR = (0.2, -0.35)


def _cyl_between(L, a, b, r, mat, name="limb"):
    a, b = Vector(a), Vector(b)
    d = b - a
    o = L.prim("cyl", loc=tuple((a + b) / 2), vertices=12, radius=r, depth=d.length, name=name)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    L.assign(o, mat)
    L.smooth(o)
    return o


def _crawl(L, n, ceiling=1.15, dust=True, fill=20, crack=True):
    C.world_black((0.004, 0.003, 0.002))
    C.render_quality(vol_end=20, vol_tile="8", vol_samples=24)
    C.crawl_set(y_far=-14, ceiling=ceiling, crack=crack)
    C.water(center=(0, -4, 0.5), size=(3.4, 22, 3.0), color=(0.85, 0.75, 0.6), density=0.006, anisotropy=0.5,
            absorption=(0.02, 0.03, 0.04), name="dusthaze")
    if dust:
        d = C.cloud((0, 0.4, 0.4), (1.4, 1.6, 0.7), count=700, radius=0.002, color=(1, 0.9, 0.7), emit=0.12, seed=5)
        C.drift(d, n, (0.02, 0.01, 0.015))


def _anchor_z():
    return C.crawl_ceiling_z(ANCHOR[0], ANCHOR[1]) - 0.02


# ============================================================================ S01 cold open: boots in the crack

def S01(L, n):
    _crawl(L, n)
    rim, sock = C.rim_figure_mat("legs", COVERALL, (1.0, 0.8, 0.55), 1.0)
    boot = L.mat_principled("boot", (0.04, 0.035, 0.03), rough=0.6)
    legs = []
    for sx in (-1, 1):
        knee = (sx * 0.08, 0.55, -0.45)
        ankle = (sx * 0.11, 0.2, 0.32)
        legs.append(_cyl_between(L, knee, ankle, 0.055, rim, "shin"))
        legs.append(_cyl_between(L, (sx * 0.07, 0.75, -1.1), knee, 0.07, rim, "thigh"))
        b = L.prim("cube", loc=(sx * 0.115, 0.12, 0.4), name="boot")
        b.scale = (0.055, 0.13, 0.05)
        b.rotation_euler = (math.radians(-55), 0, 0)
        L.assign(b, boot)
        L.bevel(b, 0.02)
        legs.append(b)
    root = L.link(bpy.data.objects.new("legs_root", None))
    for o in legs:
        o.parent = root
    # small, slow struggle
    for f in range(1, n + 1, 8):
        root.rotation_euler = (0.03 * math.sin(f * 0.21), 0, 0.02 * math.sin(f * 0.13))
        root.keyframe_insert("rotation_euler", frame=f)
    # his helmet lamp, deep in the crack
    core, halo, hem = C.glow_dot((0.0, 0.95, -2.3), WARM, r=0.04, halo=5, strength=10, name="deeplamp")
    pl = L.point((0.0, 0.9, -2.0), energy=40, color=WARM, radius=0.1, name="deeplight")
    sp = L.spot((0.0, 0.95, -2.2), (0, 0, 0), energy=500, size_deg=60, blend=0.8, color=WARM, name="upglow")
    sp.rotation_mode = "QUATERNION"
    sp.rotation_quaternion = Vector((0, -0.3, 1)).to_track_quat("-Z", "Y")
    C.rim_light((0, 0.2, 0.3), (0.3, 1.2, 0.6), energy=250, color=(1.0, 0.85, 0.6), size_deg=50, name="bootrim")
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.32, -1.6, 0.6), (0.0, 0.45, -0.5)), (n, (0.28, -1.15, 0.55), (0.0, 0.5, -0.65))],
              shake=0.02, rot_shake=0.004)
    C.cam_fill(cam, energy=10, color=(1.0, 0.85, 0.65))
    L.bake_static()


# ============================================================================ cross-section diagram (S02/S07/S09/S12/S14)

POLY = [(-4.9, 1.88), (-0.45, 1.9), (-0.1, 1.65), (0.3, 0.75), (0.62, -0.2), (0.86, -0.95), (0.82, -1.08),
        (0.66, -1.0), (0.42, -0.25), (0.02, 0.6), (-0.5, 1.34), (-4.9, 1.34)]
BOTTOM_HEAD = (0.74, -0.9)
THETA_DOWN = -0.31
PATH = [(-2.6, 1.6), (-0.6, 1.6), (-0.22, 1.36), (0.16, 0.62), (0.5, -0.28), (0.74, -0.9)]
ANCHOR_XS = (-0.3, 1.86)


def _xs4(L, n):
    C.world_black((0.0, 0.0, 0.0))
    rock = L.mat_noise_surface("xs4rock", (0.3, 0.27, 0.22), (0.5, 0.46, 0.38), scale=1.2, bump=0.25, rough=0.9)
    xs = C.xsection([(x, -z) for x, z in POLY], lambda d: -d, extent=(-4.6, 4.6, -4.5, 4.5), rock_mat_=rock,
                    water_top=(0.05, 0.045, 0.04), water_bot=(0.025, 0.022, 0.02), outline_color=(1.0, 0.88, 0.7),
                    outline_strength=2.2, name="np")
    C.text("CRAWLWAY", (-1.2, -0.45, 2.1), size=0.16, color=(0.95, 0.9, 0.8), strength=2.0, name="t_crawl")
    L.area((-3, -6, 5), (math.radians(55), 0, math.radians(-25)), energy=500, size=5, color=(1.0, 0.95, 0.85))
    cam = C.camera(lens=35)
    return xs, cam


def _cam4(cam, n, keys):
    """keys: (frame, (cx, cz), lens)"""
    C.aim_cam(cam, n, [(f, (c[0] + 0.1, -11.0, c[1] - 0.5 + 0.1), (c[0], 0.0, c[1] - 0.5)) for f, c, _ in keys],
              lens_keys=[(f, ln * 1.5) for f, _, ln in keys])


def _place_fig(fig, head, theta):
    r = fig["root"]
    r.location = (head[0], -0.46, head[1])
    r.rotation_euler = (0, theta, 0)


def _key_fig(fig, f, head, theta):
    _place_fig(fig, head, theta)
    fig["root"].keyframe_insert("location", frame=f)
    fig["root"].keyframe_insert("rotation_euler", frame=f)


def _feet(head, theta, length=0.6):
    return (head[0] + math.sin(theta) * length, head[1] + math.cos(theta) * length)


def S02(L, n):
    xs, cam = _xs4(L, n)
    fig = C.outline_figure("john", length=0.6)
    _place_fig(fig, BOTTOM_HEAD, THETA_DOWN)
    a1, _ = C.arrow2d((0.86, -1.18), (1.0, -1.85), color=(1, 1, 1), name="adown")
    x1, _ = C.x_mark((1.25, -1.55), size=0.13, name="xdown")
    ft = _feet(BOTTOM_HEAD, THETA_DOWN)
    a2, _ = C.arrow2d((ft[0] - 0.05, ft[1] + 0.12), (ft[0] - 0.3, ft[1] + 0.95), color=(1, 1, 1), name="aup")
    x2, _ = C.x_mark((ft[0] + 0.15, ft[1] + 0.65), size=0.13, name="xup")
    C.hide_from_frame(a1, f_show=6)
    C.hide_from_frame(x1, f_show=16)
    C.hide_from_frame(a2, f_show=24)
    C.hide_from_frame(x2, f_show=34)
    _cam4(cam, n, [(1, (0.35, -0.2), 35), (n, (0.4, -0.25), 36.8)])
    L.bake_static()


def S07(L, n):
    xs, cam = _xs4(L, n)
    fig = C.outline_figure("john", length=0.6)
    f_in, f_turn, f_end = 4, int(n * 0.35), int(n * 0.85)
    pts = PATH
    tot = len(pts) - 1
    for f in range(1, n + 1, 2):
        if f <= f_in:
            t = 0.0
        else:
            t = C.sm(min(1.0, (f - f_in) / (f_end - f_in)))
        head = C.along([(x, 0, z) for x, z in pts], t)
        th = C.lerp(-math.pi / 2, THETA_DOWN, C.sm((t - 0.3) / 0.25))
        _key_fig(fig, f, (head.x, head.z), th)
    dots = C.dotted_path([(x, -0.44, z) for x, z in pts], spacing=0.12, r=0.022, color=(1.0, 0.85, 0.5),
                         strength=3.0, name="trail")
    for k, o in enumerate(dots):
        C.hide_from_frame([o], f_show=f_in + int((f_end - f_in) * C.sm(k / max(1, len(dots) - 1)) * 0.95) + 2)
    _cam4(cam, n, [(1, (-1.2, 0.8), 35), (f_turn, (-0.4, 0.6), 35), (n, (0.35, -0.2), 35)])
    L.bake_static()


def _rope_curve(L, pts, name="rope", color=(0.95, 0.55, 0.12)):
    m = C.emis(name + "_m", color, 3.0)
    return C.curve(pts, thickness=0.018, mat=m, name=name)


def S09(L, n):
    xs, cam = _xs4(L, n)
    fig = C.outline_figure("john", length=0.6)
    h0, h1 = BOTTOM_HEAD, (0.6, -0.45)
    an, _, _ = C.glow_dot((ANCHOR_XS[0], -0.47, ANCHOR_XS[1]), (1.0, 0.85, 0.3), r=0.04, halo=3, strength=8,
                          name="anchor")
    ft0 = _feet(h0, THETA_DOWN)
    rope = _rope_curve(L, [(ANCHOR_XS[0], -0.45, ANCHOR_XS[1]), (-0.05, -0.45, 1.25), (ft0[0], -0.45, ft0[1])])
    sp = rope.data.splines[0]
    for f in range(1, n + 1, 3):
        t = C.sm(f / n) * 0.9 + 0.1 * (f / n)
        t = t + 0.02 * math.sin(f * 0.9) * (1 - t)  # inching
        hd = (C.lerp(h0[0], h1[0], t), C.lerp(h0[1], h1[1], t))
        _key_fig(fig, f, hd, THETA_DOWN)
        ft = _feet(hd, THETA_DOWN)
        sp.points[2].co = (ft[0], -0.45, ft[1], 1)
        sp.points[2].keyframe_insert("co", frame=f)
    trail = C.curve([(0.78, -0.45, -1.0), (h1[0], -0.45, h1[1])], thickness=0.03, mat=C.emis("prog", C.CYAN, 5),
                    name="progress")
    C.grow_curve(trail, [(1, 0.0), (n, 1.0)])
    _cam4(cam, n, [(1, (0.3, -0.1), 35), (n, (0.3, -0.05), 37)])
    L.bake_static()


def S12(L, n):
    xs, cam = _xs4(L, n)
    fig = C.outline_figure("john", length=0.6)
    h0, h1 = (0.6, -0.45), BOTTOM_HEAD
    ring = L.prim("torus", loc=(ANCHOR_XS[0], -0.47, ANCHOR_XS[1]), rot=(math.pi / 2, 0, 0), major_radius=0.06,
                  minor_radius=0.01, name="emptyanchor")
    L.assign(ring, C.emis("emptyanchor_m", (1.0, 0.2, 0.15), 5))
    for f in range(1, n + 1, 2):
        t = C.ease_out(min(1.0, (f - 1) / (n * 0.35)))
        hd = (C.lerp(h0[0], h1[0], t), C.lerp(h0[1], h1[1], t))
        _key_fig(fig, f, hd, THETA_DOWN)
    _rope_curve(L, [(ANCHOR_XS[0] + 0.05, -0.45, ANCHOR_XS[1] - 0.25), (-0.25, -0.45, 1.4), (-0.05, -0.45, 1.36),
                    (0.2, -0.45, 0.9), (0.35, -0.45, 0.2)], name="slackrope")
    trail = C.curve([(0.78, -0.45, -1.0), (h0[0], -0.45, h0[1])], thickness=0.03, mat=C.emis("prog", C.CYAN, 5),
                    name="progress")
    C.grow_curve(trail, [(1, 1.0), (int(n * 0.35), 0.0)])
    _cam4(cam, n, [(1, (0.3, -0.1), 37), (n, (0.3, -0.1), 37)])
    L.bake_static()


def S14(L, n):
    xs, cam = _xs4(L, n)
    fig = C.outline_figure("john", length=0.6)
    _place_fig(fig, BOTTOM_HEAD, THETA_DOWN)
    fade = int(n * 0.45)
    C.key_input(fig["lamp_core_emit"], [(1, 10.0), (int(n * 0.15), 10.0), (int(n * 0.22), 4.0), (int(n * 0.25), 8.0),
                                        (fade - 8, 1.5), (fade, 0.0)])
    C.key_input(fig["lamp_halo_emit"].inputs[1], [(1, 3.5), (int(n * 0.15), 3.5), (fade, 0.0)])
    om = fig["mat"].node_tree.nodes["Emission"].inputs[1]
    C.key_input(om, [(1, 2.5), (fade, 2.5), (int(n * 0.85), 0.25)])
    _cam4(cam, n, [(1, (0.4, -0.25), 38), (n, (0.3, 0.0), 34)])
    L.bake_static()


# ============================================================================ crawlway with rescuers (S03/S10/S13/S15)

def _rescuer(L, name, h=1.7, lamp=280, helmet=(0.9, 0.8, 0.1)):
    return C.crawler(name, height=h, suit=COVERALL, helmet_color=helmet, lamp_energy=lamp)


def S03(L, n):
    _crawl(L, n)
    rope_m = L.mat_principled("ropecoil", (0.9, 0.45, 0.08), rough=0.6)
    for k in range(3):
        p = _rescuer(L, f"res{k}", helmet=((0.9, 0.8, 0.1), (0.85, 0.85, 0.85), (0.9, 0.35, 0.05))[k])
        r = p["root"]
        x = (-0.12, 0.15, -0.05)[k]
        y0 = -0.4 - k * 1.3
        C.key_loc(r, [(1, (x, y0, 0.0)), (n, (x, y0 - 1.6, 0.0))])
        L.linear_fcurves(r)
        r.rotation_euler = (0, 0, math.pi)
        C.anim_crawl(p, n, rate=0.9 + 0.1 * k)
        coil = L.prim("torus", loc=(0, 0.25, 0.08), major_radius=0.16, minor_radius=0.035, name=f"coil{k}")
        L.assign(coil, rope_m)
        coil.parent = p["pelvis"]
        if k == 1:
            bag = L.prim("cube", loc=(0.0, -1.45, 0.1), name="pulleybag")
            bag.scale = (0.14, 0.2, 0.1)
            L.assign(bag, L.mat_principled("bag", (0.1, 0.2, 0.55), rough=0.6))
            L.bevel(bag, 0.03)
            bag.parent = r
    L.point((0.0, 1.0, 0.6), energy=40, color=WARM, radius=0.3, name="backglow")
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (0.15, -6.6, 0.26), (0.0, 0.0, 0.42)), (n, (0.15, -7.3, 0.26), (0.0, 0.0, 0.42))],
              shake=0.012, rot_shake=0.003)
    C.cam_fill(cam, energy=25, color=(1.0, 0.85, 0.65))
    L.bake_static()


def _hauler(L, name, y, x, n, phase=0.0, h=1.45):
    p = C.figure(name, height=h, pose="sit", base=COVERALL, rim=(1.0, 0.8, 0.55), rim_strength=0.8)
    s = h / 1.75
    p["root"].location = (x, y, C.crack_floor_z(x, y))
    C.helmet(p["neck"], s, (0.9, 0.8, 0.1), 260, name=name + "_hel")
    for f in range(1, n + 1, 3):
        ph = 2 * math.pi * 0.55 * f / 24 + phase
        lean = 0.1 + 0.3 * (0.5 + 0.5 * math.sin(ph))
        p["pelvis"].rotation_euler = (lean, 0, 0)
        p["pelvis"].keyframe_insert("rotation_euler", frame=f)
        for tag in ("L", "R"):
            p[f"shoulder{tag}"].rotation_euler = (1.45 - lean, 0, (0.12 if tag == "L" else -0.12))
            p[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
            p[f"elbow{tag}"].rotation_euler = (0.25, 0, 0)
            p[f"elbow{tag}"].keyframe_insert("rotation_euler", frame=f)
            p[f"hip{tag}"].rotation_euler = (2.3 - lean, 0, 0)
            p[f"hip{tag}"].keyframe_insert("rotation_euler", frame=f)
    p["neck"].rotation_euler = (-0.1, 0, 0)
    return p


def _rig_rope(L, slack=False):
    az = _anchor_z()
    an = C.bolt_anchor((ANCHOR[0], ANCHOR[1], az))
    pu = C.pulley((ANCHOR[0], ANCHOR[1], az - 0.2))
    rope_m = L.mat_principled("rope", (0.95, 0.5, 0.08), rough=0.6, emit=(0.95, 0.5, 0.08), emit_strength=0.15)
    if slack:
        r1 = C.curve([(ANCHOR[0], ANCHOR[1] + 0.02, az - 0.24), (0.15, 0.3, -0.2), (0.05, 0.6, -1.6)], thickness=0.011,
                     mat=rope_m, name="rope_down", smooth_pts=True)
    else:
        r1 = C.curve([(ANCHOR[0], ANCHOR[1] + 0.02, az - 0.24), (0.06, 0.62, -1.7)], thickness=0.011, mat=rope_m,
                     name="rope_down")
    r2 = C.curve([(ANCHOR[0], ANCHOR[1] - 0.02, az - 0.24), (0.0, -1.0, 0.48), (0.0, -6.0, 0.42)], thickness=0.011,
                 mat=rope_m, name="rope_haul")
    return an, pu, r1, r2


def S10(L, n):
    _crawl(L, n, ceiling=1.25)
    _rig_rope(L)
    ps = []
    for k in range(4):
        ps.append(_hauler(L, f"haul{k}", -1.25 - k * 0.85, (0.12 if k % 2 else -0.12), n, phase=0.15 * k,
                          h=1.42 + 0.04 * (k % 2)))
    for y in (-1.5, -3.2):
        L.point((0.4, y, 0.9), energy=30, color=(1.0, 0.75, 0.45), radius=0.3, name="warm")
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (0.6, -0.45, 0.78), (-0.25, -4.6, 0.35)), (n, (0.6, -0.9, 0.74), (-0.2, -4.8, 0.35))],
              shake=0.01, rot_shake=0.002, fn=lambda x: x)
    C.cam_fill(cam, energy=20, color=(1.0, 0.85, 0.65))
    L.bake_static()


def S13(L, n):
    _crawl(L, n)
    _rig_rope(L, slack=True)
    lamps = []
    for k, (x, y, face) in enumerate(((-0.55, -2.2, -math.pi / 2), (0.55, -3.4, math.pi / 2))):
        p = C.figure(f"rest{k}", height=1.45, pose="sit", base=COVERALL, rim=(1.0, 0.8, 0.55), rim_strength=0.7)
        p["root"].location = (x, y, C.crack_floor_z(x, y))
        p["root"].rotation_euler = (0, 0, face)
        p["pelvis"].rotation_euler = (0.25, 0, 0)
        p["neck"].rotation_euler = (-0.5, 0, 0)
        hm = C.helmet(p["neck"], 1.45 / 1.75, (0.85, 0.85, 0.85), 120, name=f"rest{k}_hel")
        lamps.append(hm["lamp"])
    w = _rescuer(L, "worker", lamp=320)
    w["root"].location = (0.05, -1.2, 0.0)
    C.anim_crawl(w, n, rate=0.35, amp=0.25)
    lamps.append(w["lamp"])
    for k, lp in enumerate(lamps):
        L.flicker(lp, n, seed=k + 3, depth=0.5, rate=0.4)
    coil = L.prim("torus", loc=(0.35, -1.9, 0.06), major_radius=0.18, minor_radius=0.03, name="coil")
    L.assign(coil, L.mat_principled("coil_m", (0.9, 0.45, 0.08), rough=0.6))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.55, -5.4, 0.42), (-0.05, -1.0, 0.35)), (n, (-0.25, -5.4, 0.42), (0.1, -1.0, 0.35))],
              shake=0.006, rot_shake=0.0015, fn=lambda x: x)
    C.cam_fill(cam, energy=25, color=(1.0, 0.85, 0.65))
    L.bake_static()


def S15(L, n):
    _crawl(L, n, dust=False)
    coil = L.prim("torus", loc=(-0.25, -1.05, 0.05), major_radius=0.2, minor_radius=0.03, name="coil")
    L.assign(coil, L.mat_principled("coil_m", (0.9, 0.45, 0.08), rough=0.6))
    coil2 = L.prim("torus", loc=(-0.22, -1.02, 0.1), major_radius=0.16, minor_radius=0.03, name="coil2")
    L.assign(coil2, coil.active_material)
    for k in range(2):
        p = _rescuer(L, f"leave{k}", lamp=350)
        r = p["root"]
        y0 = -2.0 - k * 1.4
        C.key_loc(r, [(1, (0.05 * k, y0, 0.0)), (n, (0.05 * k, y0 - 5.5, 0.0))])
        L.linear_fcurves(r)
        r.rotation_euler = (0, 0, math.pi)
        C.anim_crawl(p, n, rate=0.9)
        C.key_energy(p["lamp"], [(1, 350), (int(n * 0.6), 300), (n - 4, 0)])
        C.key_input(p["lamp_mat"].node_tree.nodes["Emission"].inputs[1], [(1, 18), (n - 4, 0)])
    fill = L.spot((0.4, 0.2, 0.7), (0, 0, 0), energy=25, size_deg=30, blend=1.0, color=(1.0, 0.85, 0.6), name="coilfill")
    fill.rotation_mode = "QUATERNION"
    fill.rotation_quaternion = (Vector((-0.25, -1.05, 0.05)) - Vector(fill.location)).to_track_quat("-Z", "Y")
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (0.25, -0.15, 0.32), (0.0, -6.0, 0.35)), (n, (0.25, -0.15, 0.32), (0.0, -6.0, 0.35))],
              shake=0.003, rot_shake=0.001)
    L.bake_static()


# ============================================================================ S06 POV crawl / S08 + S11 anchor macro

def S06(L, n):
    C.world_black((0.004, 0.003, 0.002))
    zf = lambda y: -0.22 * y
    C.passage(length=9, y0=-1.5, w_fn=lambda y: 0.62 - 0.3 * C.sm((y - 1) / 5), h_fn=lambda y: 0.42 - 0.2 * C.sm((y - 1) / 5),
              z_fn=zf, x_fn=lambda y: 0.08 * math.sin(y * 0.8), seed=41, rough=0.12, floor_flat=0.35,
              mat=C.clay_mat("tube"), disp=(0.12, 0.04))
    # dark slot at the end
    cam = C.camera(lens=20)
    keys = []
    for f in (1, n):
        y = 0.0 + 1.9 * (f - 1) / (n - 1)
        keys.append((f, (0.0, y, zf(y) + 0.05), (0.05, y + 3.0, zf(y + 3.0) - 0.1)))
    C.aim_cam(cam, n, keys, shake=0.04, rot_shake=0.01, rate=1.6, fn=lambda x: x)
    lamp = L.spot((0, 0.06, 0), (0, 0, 0), energy=120, size_deg=70, blend=0.6, color=WARM, name="headlamp")
    lamp.parent = cam
    glove = L.mat_principled("glove", (0.05, 0.04, 0.035), rough=0.7)
    sleeve, _ = C.rim_figure_mat("sleeve", COVERALL, WARM, 0.8)
    for sx, ph in ((-1, 0.0), (1, math.pi)):
        g = L.prim("sphere", loc=(0, 0, 0), segments=12, ring_count=8, radius=1.0, name=f"glove{sx}")
        g.scale = (0.05, 0.035, 0.07)
        L.assign(g, glove)
        L.smooth(g)
        arm = L.prim("cyl", loc=(0, 0, 0.22), vertices=10, radius=0.045, depth=0.4, name=f"sleeve{sx}")
        L.assign(arm, sleeve)
        arm.parent = g
        g.parent = cam
        for f in range(1, n + 1, 2):
            t = 2 * math.pi * 0.7 * f / 24 + ph
            reach = 0.5 + 0.5 * math.sin(t)
            g.location = (sx * 0.17, -0.15 + 0.03 * reach, -0.3 - 0.22 * reach)
            g.rotation_euler = (0.25, sx * 0.25, 0)
            g.keyframe_insert("location", frame=f)
            g.keyframe_insert("rotation_euler", frame=f)
    L.bake_static()


def _anchor_cam(L, n, keys, shake_keys=None, shake=0.006):
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, keys, shake=shake, rot_shake=shake * 0.3, shake_keys=shake_keys, rate=1.0)
    return cam


def S08(L, n):
    _crawl(L, n, dust=False)
    az = _anchor_z()
    A = Vector((ANCHOR[0], ANCHOR[1], az))
    an = C.bolt_anchor(tuple(A))
    for o in (an["hanger"], an["krab"], an["nut"]):
        C.hide_from_frame([o], f_show=22)
    C.key_loc(an["bolt"], [(1, (0, 0, -0.1)), (6, (0, 0, -0.06)), (11, (0, 0, -0.03)), (16, (0, 0, 0.0)), (20, (0, 0, 0.02))])
    pu = C.pulley(tuple(A + Vector((0, 0, -0.2))))
    C.hide_from_frame([pu], f_show=34)
    rope_m = L.mat_principled("rope", (0.95, 0.5, 0.08), rough=0.6, emit=(0.95, 0.5, 0.08), emit_strength=0.15)
    rope = C.curve([tuple(A + Vector((-0.04, 0.02, -0.22))), tuple(A + Vector((0.0, 0.3, -0.7))), (0.06, 0.62, -1.7)],
                   thickness=0.011, mat=rope_m, name="rope_down")
    C.grow_curve(rope, [(1, 0.0), (44, 0.0), (n - 6, 1.0)])
    glove = L.mat_principled("glove", (0.05, 0.04, 0.035), rough=0.7)
    hands = []
    for sx in (-1, 1):
        g = L.prim("sphere", loc=(0, 0, 0), segments=12, ring_count=8, radius=1.0, name=f"glove{sx}")
        g.scale = (0.045, 0.06, 0.035)
        L.assign(g, glove)
        L.smooth(g)
        hands.append(g)
    hl, hr = hands
    C.key_loc(hl, [(1, tuple(A + Vector((-0.05, -0.02, -0.17)))), (20, tuple(A + Vector((-0.05, -0.02, -0.12)))),
                   (30, tuple(A + Vector((-0.04, -0.03, -0.24)))), (44, tuple(A + Vector((-0.08, 0.0, -0.3)))),
                   (n, tuple(A + Vector((-0.2, 0.25, -0.6))))])
    hammer_hits = []
    for f in range(1, 21, 5):
        hammer_hits += [(f, tuple(A + Vector((0.06, -0.02, -0.32)))), (f + 2, tuple(A + Vector((0.04, -0.02, -0.16))))]
    C.key_loc(hr, hammer_hits + [(28, tuple(A + Vector((0.05, 0.0, -0.22)))), (40, tuple(A + Vector((0.03, 0.04, -0.26)))),
                                 (n, tuple(A + Vector((0.1, -0.3, -0.45))))])
    lp = L.spot((0.5, -0.9, 0.2), (0, 0, 0), energy=45, size_deg=40, blend=0.7, color=WARM, name="worklamp")
    lp.rotation_mode = "QUATERNION"
    lp.rotation_quaternion = (A - Vector(lp.location)).to_track_quat("-Z", "Y")
    C.rim_light(tuple(A), (-0.3, 0.6, -0.3), energy=60, color=(1.0, 0.85, 0.6), size_deg=40, name="rim")
    _anchor_cam(L, n, [(1, tuple(A + Vector((0.18, -0.42, -0.3))), tuple(A + Vector((0, 0, -0.05)))),
                       (24, tuple(A + Vector((0.16, -0.4, -0.32))), tuple(A + Vector((0, 0, -0.06)))),
                       (30, tuple(A + Vector((0.25, -0.35, -0.45))), tuple(A + Vector((0, 0, -0.2)))),
                       (48, tuple(A + Vector((0.24, -0.33, -0.47))), tuple(A + Vector((0, 0, -0.22)))),
                       (54, tuple(A + Vector((0.35, -0.5, -0.5))), (0.06, 0.55, -1.0)),
                       (n, tuple(A + Vector((0.3, -0.35, -0.6))), (0.06, 0.62, -1.5))], shake=0.01)
    L.bake_static()


def S11(L, n):
    _crawl(L, n, dust=False)
    az = _anchor_z()
    A = Vector((ANCHOR[0], ANCHOR[1], az))
    fail = int(n * 0.5)
    an = C.bolt_anchor(tuple(A))
    pu = C.pulley(tuple(A + Vector((0, 0, -0.2))))
    pu.parent = an["root"]
    pu.location = (0, 0, -0.2)
    chunk = L.prim("ico", loc=(0, 0, 0.0), subdivisions=2, radius=0.06, name="chunk")
    chunk.scale = (1.2, 1.0, 0.5)
    L.add_displace(chunk, strength=0.03, scale=0.04, name="chunk_d")
    L.assign(chunk, C.clay_mat("chunkm", (0.14, 0.12, 0.1), (0.42, 0.37, 0.3)))
    chunk.parent = an["root"]
    r = an["root"]
    r.keyframe_insert("location", frame=fail)
    r.keyframe_insert("rotation_euler", frame=fail)
    r.location = A + Vector((0.05, 0.35, -0.9))
    r.rotation_euler = (1.2, 0.6, 0.3)
    r.keyframe_insert("location", frame=fail + 7)
    r.keyframe_insert("rotation_euler", frame=fail + 7)
    r.location = A + Vector((0.05, 0.55, -1.9))
    r.keyframe_insert("location", frame=n)
    # cracks spreading around the bolt (dark lines on the ceiling)
    cm = L.mat_principled("crackline", (0.01, 0.008, 0.006), rough=0.9)
    rnd = random.Random(4)
    for k in range(6):
        a = k * math.pi / 3 + rnd.uniform(-0.3, 0.3)
        pts = [tuple(A + Vector((0, 0, 0.012)))]
        p = Vector((0, 0, 0))
        for j in range(4):
            p += Vector((math.cos(a + rnd.uniform(-0.5, 0.5)), math.sin(a + rnd.uniform(-0.5, 0.5)), 0)) * 0.035
            pts.append(tuple(A + p + Vector((0, 0, 0.012 + 0.004 * j))))
        c = C.curve(pts, thickness=0.004, mat=cm, name="crack")
        C.grow_curve(c, [(1, 0.0), (6 + k * 2, 0.0), (fail - 2, 1.0)])
    rope_m = L.mat_principled("rope", (0.95, 0.5, 0.08), rough=0.6, emit=(0.95, 0.5, 0.08), emit_strength=0.15)
    taut = C.curve([tuple(A + Vector((0.0, 0.02, -0.24))), (0.06, 0.62, -1.7)], thickness=0.011, mat=rope_m, name="taut")
    taut2 = C.curve([tuple(A + Vector((0.0, -0.02, -0.24))), (0.0, -1.0, 0.48)], thickness=0.011, mat=rope_m,
                    name="taut2")
    C.hide_from_frame([taut, taut2], f_hide=fail)
    slack = C.curve([(0.0, -1.0, 0.45), (0.25, -0.4, 0.3), (0.1, 0.1, 0.25), (0.15, 0.4, -0.4), (0.06, 0.62, -1.7)],
                    thickness=0.011, mat=rope_m, name="slack", smooth_pts=True)
    C.hide_from_frame([slack], f_show=fail)
    C.key_loc(slack, [(fail, (0.0, 0.0, 0.25)), (fail + 4, (0.06, 0.03, -0.08)), (fail + 8, (-0.03, 0.0, 0.04)),
                      (fail + 14, (0, 0, 0))])
    dust = C.cloud(tuple(A + Vector((0, 0.1, -0.35))), (0.8, 0.8, 0.6), count=1800, radius=0.004, color=(1, 0.9, 0.7),
                   emit=0.25, shape="sphere", seed=11, name="burst")
    C.key_scale(dust, [(1, 0.01), (fail - 1, 0.01), (fail + 3, 0.7), (n, 1.8)])
    C.drift(dust, n, (0.0, 0.05, -0.05))
    lp = L.spot((0.5, -0.9, 0.2), (0, 0, 0), energy=45, size_deg=40, blend=0.7, color=WARM, name="worklamp")
    lp.rotation_mode = "QUATERNION"
    lp.rotation_quaternion = (A - Vector(lp.location)).to_track_quat("-Z", "Y")
    C.key_energy(lp, [(1, 45), (fail, 45), (fail + 2, 12), (fail + 4, 55), (fail + 7, 18), (fail + 10, 40), (n, 35)])
    C.rim_light(tuple(A), (-0.3, 0.6, -0.3), energy=60, color=(1.0, 0.85, 0.6), size_deg=40, name="rim")
    cam = _anchor_cam(L, n, [(1, tuple(A + Vector((0.2, -0.45, -0.32))), tuple(A + Vector((0, 0, -0.08)))),
                             (fail, tuple(A + Vector((0.18, -0.4, -0.3))), tuple(A + Vector((0, 0, -0.1)))),
                             (n, tuple(A + Vector((0.3, -0.6, -0.4))), tuple(A + Vector((0.05, 0.4, -0.8))))],
                      shake=0.08, shake_keys=[(1, 0.08), (fail - 1, 0.08), (fail, 1.0), (fail + 6, 1.0), (fail + 9, 0.15),
                                              (n, 0.15)])
    L.bake_static()


# ============================================================================ desert hill exteriors (S04/S05/S16/S17)

def _sky4(L, tod):
    if tod == "night":
        C.sky_world(top=(0.004, 0.007, 0.018), horizon=(0.02, 0.03, 0.05), ground=(0.003, 0.003, 0.004), strength=1.0)
        C.sun_from(C.sun_dir(35, 200), energy=0.25, color=(0.55, 0.65, 0.95), angle=3)
        C.star_dome(count=1400, radius=180, size=0.22, strength=8)
    elif tod == "dusk":
        sd = C.sun_dir(3, 15)
        C.sky_world(top=(0.07, 0.08, 0.18), horizon=(0.95, 0.42, 0.18), ground=(0.04, 0.03, 0.03), sun_dir=sd,
                    sun_color=(1.0, 0.5, 0.2), sun_glow=1.2, strength=1.0, glow_pow=40)
        C.sun_from(sd, energy=2.0, color=(1.0, 0.55, 0.3), angle=2)
    elif tod == "day":
        C.sky_world(top=(0.3, 0.45, 0.7), horizon=(0.8, 0.82, 0.85), ground=(0.2, 0.17, 0.13), strength=1.1)
        C.sun_from(C.sun_dir(45, 210), energy=3.5, color=(1.0, 0.95, 0.88), angle=2)
    elif tod == "dawn":
        sd = C.sun_dir(5, 95)
        C.sky_world(top=(0.25, 0.32, 0.5), horizon=(0.98, 0.72, 0.5), ground=(0.12, 0.1, 0.08), sun_dir=sd,
                    sun_color=(1.0, 0.7, 0.45), sun_glow=2.0, strength=1.0)
        C.sun_from(sd, energy=2.8, color=(1.0, 0.78, 0.55), angle=2)


def _hill(L, n, sage_count=60, seed=3):
    coarse, fine, fz = C.hill_set()
    rnd = random.Random(seed)
    pts = []
    for i in range(sage_count):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(1.4, 9) if i < sage_count * 0.6 else rnd.uniform(9, 40)
        x, y = math.cos(a) * r, math.sin(a) * r
        pts.append((x, y, fz(x, y) - 0.05))
    sage = C.sagebrush(pts, seed=seed)
    rk = []
    for (x, y) in ((1.0, 0.4), (-0.95, 0.3), (0.6, 0.85), (-1.6, -0.5)):
        rk.append((x, y, fz(x, y)))
    C.rocks(rk, count=4, size=(0.2, 0.45), seed=4, mat=L.mat_noise_surface("hrock", (0.18, 0.15, 0.12), (0.45, 0.4, 0.33),
                                                                            scale=1.5, bump=0.8))
    return fz, sage


def S04(L, n):
    C.render_quality(vol_end=60, vol_tile="8", vol_samples=16)
    _sky4(L, "night")
    fz, sage = _hill(L, n)
    rnd = random.Random(5)
    for k in range(6):
        x, y = -7 + k * 2.6 + rnd.uniform(-0.5, 0.5), -24 + rnd.uniform(-2, 2)
        z = fz(x, y) + 0.9
        col = ((1, 0.12, 0.08), (0.2, 0.35, 1.0), (1, 0.95, 0.85))[k % 3]
        C.glow_dot((x, y, z), col, r=0.12, halo=5, strength=12, light=150, name=f"veh{k}")
    hl = L.spot((0.0, -24, fz(0, -24) + 1.2), (0, 0, 0), energy=4000, size_deg=35, blend=0.6, color=(1, 0.95, 0.85),
                name="headlights")
    hl.rotation_mode = "QUATERNION"
    hl.rotation_quaternion = (Vector((0, 0, fz(0, 0))) - Vector(hl.location)).to_track_quat("-Z", "Y")
    z0 = C.hill_z(0, 0, pit_depth=0.0)
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (3.5, -20.0, z0 + 9.0), (0.0, 2.0, z0 + 1.5)), (n, (1.0, -5.2, z0 + 2.2), (0.0, 0.3, z0 - 0.6))],
              shake=0.02, rot_shake=0.001, rate=0.4)
    L.bake_static()


def S05(L, n):
    C.render_quality(vol_end=40, vol_tile="8", vol_samples=16)
    _sky4(L, "dusk")
    fz, sage = _hill(L, n, sage_count=40, seed=6)
    p = C.figure("john", height=1.78, base=COVERALL, rim=(1.0, 0.6, 0.3), rim_strength=1.4)
    hm = C.helmet(p["neck"], 1.78 / 1.75, (0.8, 0.06, 0.04), 400, name="john_hel")
    r = p["root"]
    x0, y0 = 0.05, -0.95
    duck, gone = int(n * 0.4), int(n * 0.85)
    C.key_loc(r, [(1, (x0, y0, fz(x0, y0))), (duck, (x0, y0 + 0.1, fz(x0, y0))), (gone, (0.0, 0.2, C.hill_z(0, 0.2, pit_depth=0.0) - 1.9))])
    L.ease_all(r)
    for f, pel, hip, knee, neck in ((1, 0.0, 0.0, 0.0, 0.0), (duck, 0.0, 0.0, 0.0, -0.3),
                                    (duck + 10, -0.6, 1.0, -1.4, -0.5), (gone, -0.8, 1.2, -1.6, -0.6)):
        p["pelvis"].rotation_euler = (pel, 0, 0)
        p["pelvis"].keyframe_insert("rotation_euler", frame=f)
        p["neck"].rotation_euler = (neck, 0, 0)
        p["neck"].keyframe_insert("rotation_euler", frame=f)
        for tag in ("L", "R"):
            p[f"hip{tag}"].rotation_euler = (hip, 0, 0)
            p[f"hip{tag}"].keyframe_insert("rotation_euler", frame=f)
            p[f"knee{tag}"].rotation_euler = (knee, 0, 0)
            p[f"knee{tag}"].keyframe_insert("rotation_euler", frame=f)
    z0 = C.hill_z(0, 0, pit_depth=0.0)
    C.rim_light((0, -0.9, z0 + 1.2), (0.5, 4.0, 2.0), energy=900, color=(1.0, 0.6, 0.3), size_deg=40, name="duskrim")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.7, -5.4, z0 + 1.5), (0.0, -0.2, z0 + 0.6)), (n, (0.6, -4.7, z0 + 1.35), (0.0, 0.0, z0 + 0.3))],
              shake=0.01, rot_shake=0.0015)
    C.cam_fill(cam, energy=15, color=(1.0, 0.75, 0.55))
    L.bake_static()


def _slab(L, fz, name="slab"):
    z0 = C.hill_z(0, 0, pit_depth=0.0)
    slope = (fz(0, 0.8) - fz(0, -0.8)) / 1.6
    sl = L.prim("cube", loc=(0, 0, z0 - 0.04), name=name)
    sl.scale = (0.95, 0.78, 0.12)
    sl.rotation_euler = (math.atan(slope), 0, 0)
    m = L.mat_noise_surface(name + "_m", (0.42, 0.42, 0.4), (0.62, 0.62, 0.6), scale=6, bump=0.15, rough=0.85,
                            voronoi=False)
    L.assign(sl, m)
    L.bevel(sl, 0.03)
    return sl, slope


def S16(L, n):
    C.render_quality(vol_end=40, vol_tile="8", vol_samples=16)
    _sky4(L, "day")
    fz, sage = _hill(L, n, sage_count=40, seed=8)
    z0 = C.hill_z(0, 0, pit_depth=0.0)
    cut = int(n * 0.62)
    slab, slope = _slab(L, fz)
    C.hide_from_frame([slab], f_show=cut)
    grey = L.mat_principled("wetconcrete", (0.36, 0.36, 0.35), rough=0.25)
    fill = L.prim("plane", loc=(0, 0, z0 - 2.4), size=2.0, name="fill")
    fill.scale = (0.9, 0.7, 1)
    fill.rotation_euler = (math.atan(slope), 0, 0)
    L.assign(fill, grey)
    C.key_loc(fill, [(1, (0, 0, z0 - 2.4)), (cut - 2, (0, 0, z0 - 0.08))])
    chute = L.prim("cyl", loc=(1.1, -1.2, z0 + 0.9), vertices=16, radius=0.18, depth=2.0, name="chute")
    chute.scale = (1, 1, 1)
    chute.rotation_mode = "QUATERNION"
    chute.rotation_quaternion = (Vector((0.2, -0.1, z0 + 0.25)) - Vector((2.0, -2.3, z0 + 1.55))).to_track_quat("Z", "Y")
    L.assign(chute, L.mat_principled("chute_m", (0.55, 0.5, 0.42), rough=0.4, metal=0.6))
    stream = C.curve([(0.25, -0.12, z0 + 0.32), (0.08, 0.0, z0 - 0.5), (0.0, 0.05, z0 - 2.0)], thickness=0.09, mat=grey,
                     name="pour", smooth_pts=True)
    C.hide_from_frame([chute, stream, fill], f_hide=cut)
    sp = C.cloud((0.0, 0.0, z0 - 0.2), (0.9, 0.7, 0.3), count=400, radius=0.006, color=(0.6, 0.6, 0.58), emit=0.0,
                 seed=4, name="splash")
    C.hide_from_frame([sp], f_hide=cut)
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.9, -2.9, z0 + 3.0), (0.0, 0.1, z0 - 0.6)), (cut - 1, (0.95, -3.3, z0 + 3.6), (0.0, 0.1, z0 - 0.5)),
                       (cut, (0.95, -3.3, z0 + 3.6), (0.0, 0.1, z0 - 0.2)), (n, (1.1, -4.6, z0 + 5.2), (0.0, 0.2, z0))],
              shake=0.01, rot_shake=0.001)
    L.bake_static()


def S17(L, n):
    C.render_quality(vol_end=40, vol_tile="8", vol_samples=16)
    _sky4(L, "dawn")
    fz, sage = _hill(L, n, sage_count=70, seed=9)
    z0 = C.hill_z(0, 0, pit_depth=0.0)
    slab, slope = _slab(L, fz)
    for k, s in enumerate(sage[:30]):
        for f in range(1, n + 1, 8):
            s.rotation_euler = (0.06 * math.sin(f * 0.18 + k), 0.05 * math.sin(f * 0.14 + k * 0.7), 0)
            s.keyframe_insert("rotation_euler", frame=f)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (2.2, -8.5, z0 + 1.9), (0.0, 0.3, z0 + 0.3)), (n, (1.3, -5.3, z0 + 1.45), (0.0, 0.3, z0 + 0.1))],
              shake=0.006, rot_shake=0.001, fn=lambda x: x)
    L.bake_static()
