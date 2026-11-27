"""HAUNT-05 — The Tunnel Built to Hide the Dead (Waverly Hills). One builder per shot: def Sxx(L, n).
Stylised, not a likeness. Sets live in PIPELINE/blender/lib_haunted.py ("WAVERLY HILLS sets")."""
import importlib, sys, os, math
_LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PIPELINE", "blender")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import lib_haunted as H
importlib.reload(H)
import bpy
from mathutils import Vector

ANTON = os.path.join(os.path.dirname(_LIB), "fonts", "Anton-Regular.ttf")
MOON_DIR = (-0.6, 0.3, -0.75)
BAY = 2.4
BALL_OY = 0.0 + BAY / 2 - 15.0 + BAY * 6     # porch opening whose stripe holds the ball (S08/S12/S13)


def _dark(L, c=(0.004, 0.005, 0.008), vol_end=60):
    H.eevee_quality()
    L.set_world(c, 1.0)
    try:
        bpy.context.scene.eevee.volumetric_end = vol_end
    except Exception:
        pass


def _sun_dir(L, d, energy=0.5, color=(0.6, 0.68, 0.9), name="sun", angle=1.0):
    s = L.sun(rot=(0, 0, 0), energy=energy, color=color, angle=angle, name=name)
    s.rotation_euler = Vector(d).normalized().to_track_quat("-Z", "Y").to_euler()
    return s


# --------------------------------------------------------------------------- body chute (S01, S04, S05, S14)
def _chute_top(L, n, jolt=False):
    _dark(L, vol_end=70)
    t = H.chute_tunnel(length=60, lamp_y0=2.0, lamp_every=6.0, lamp_energy=45, dead=(6,), fog=0.02, door_glow=0.8)
    root = t["root"]
    g = H.gurney("gurney", parent=root)
    y0 = 4.0
    fps = 24.0
    keys = []
    for f in range(1, n + 1, 4):
        tt = (f - 1) / fps
        keys.append((f, (0.65, y0 + 0.4 * tt + 0.1 * tt * tt, 0.05)))
    tt = (n - 1) / fps
    keys.append((n, (0.65, y0 + 0.4 * tt + 0.1 * tt * tt, 0.05)))
    for f, p in keys:
        g.location = p
        g.keyframe_insert("location", frame=f)
    if jolt:
        for f, r in ((1, 0.0), (2, 0.012), (4, -0.006), (6, 0.0)):
            g.rotation_euler = (r, 0, r * 0.6)
            g.keyframe_insert("rotation_euler", frame=f)
    # camera: top landing, 1.0 m above the floor, follow-push down the slope
    c = H.cam((0.3, -0.4, 1.0), (0.4, 20, 0.2), lens=24)
    c.parent = root
    H.cam_move(c, [(1, (0.3, -0.4, 1.0), (0.4, 20, 0.2)), (n, (0.32, 1.4, 1.0), (0.45, 21.8, 0.25))], ease=False)
    H.handheld(c, n, amp=0.006, rate=0.5, rot_amp=0.002)
    spill = L.area((0, 0, 0), (0, 0, 0), energy=60, size=1.0, color=(0.5, 0.62, 1.0), name="doorspill")
    spill.parent = root
    H.aim(spill, (0.0, -2.6, 2.0), (0.4, 6.0, 0.6))
    fill = L.cam_light(c, energy=10, color=(0.6, 0.68, 0.85))
    d = H.dust((0.3, 6, 1.3), (2.2, 12, 2.4), n, count=420, radius=0.0025, emit=0.25, drift=(0.0, 0.03, 0.01))
    d.parent = root
    H.crisp_shadows()
    L.bake_static()


def S01(L, n):
    _chute_top(L, n)


def S14(L, n):
    _chute_top(L, n, jolt=True)


def S04(L, n):
    _dark(L, vol_end=130)
    t = H.chute_tunnel(length=100, lamp_y0=4.0, lamp_every=6.0, lamp_energy=40, fog=0.006, door_glow=2.5)
    root = t["root"]
    p0, p1 = (0.05, 96.5, 0.55), (0.05, 94.6, 1.55)
    tg0, tg1 = (0.0, 0.0, 1.2), (0.0, 0.0, 1.25)
    c = H.cam(p0, tg0, lens=50)
    c.parent = root
    H.cam_move(c, [(1, p0, tg0), (n, p1, tg1)])
    H.handheld(c, n, amp=0.003, rate=0.4, rot_amp=0.0008)
    L.cam_light(c, energy=8, color=(0.65, 0.7, 0.85))
    d = H.dust((0.0, 88, 1.3), (2.2, 14, 2.4), n, count=350, radius=0.003, emit=0.25)
    d.parent = root
    wm = L.mat_principled("drip_m", (0.7, 0.75, 0.8), rough=0.1, emit=(0.6, 0.65, 0.7), emit_strength=0.6)
    dr = L.particle_cloud((0.0, 90, 1.4), (2.0, 8, 2.4), count=40, radius=0.004, mat=wm, drift=(0, 0, -1.6), seed=5, nframes=n, name="drips")
    dr.parent = root
    H.crisp_shadows()
    L.bake_static()


def S05(L, n):
    _dark(L, vol_end=50)
    t = H.chute_tunnel(length=40, lamp_y0=6.0, lamp_every=8.0, lamp_energy=14, fog=0.015, door_glow=0.3)
    root = t["root"]
    h = t["h"]
    # swinging pendant bulb overhead (y=18)
    piv = H.empty("pendant", (0.0, 18.0, h - 0.05), parent=root)
    cord = L.prim("cyl", loc=(0, 0, -0.2), vertices=6, radius=0.007, depth=0.4)
    L.assign(cord, L.mat_principled("cordm", (0.03, 0.03, 0.03), rough=0.6))
    cord.parent = piv
    bm = L.mat_emission("pend_bulb", (1.0, 0.72, 0.4), 25.0)
    b = L.prim("sphere", loc=(0, 0, -0.45), segments=12, ring_count=8, radius=0.05)
    L.assign(b, bm)
    b.parent = piv
    lt = L.point((0, 0, -0.56), energy=70, color=(1.0, 0.7, 0.38), radius=0.03, name="pendant_lt")
    lt.parent = piv
    for f in range(1, n + 2, 3):
        piv.rotation_euler = (math.radians(7) * math.sin(f / 24 * 2 * math.pi * 0.45), math.radians(2.5) * math.sin(f / 24 * 2 * math.pi * 0.3), 0)
        piv.keyframe_insert("rotation_euler", frame=f)
    # gurney eased down the rails
    g = H.gurney("gurney", parent=root)
    stop = int(n * 0.68)
    ga, gb = 16.6, 19.4
    g.location = (0.62, ga, 0.05)
    g.keyframe_insert("location", frame=1)
    g.location = (0.62, gb, 0.05)
    g.keyframe_insert("location", frame=stop)
    # orderly (pale coat, faceless) walks backwards down the steps beside it, facing uphill
    o = H.figure("orderly", color=(0.42, 0.43, 0.42), height=1.78, coat=True)
    o["root"].rotation_euler = (0, 0, math.pi)
    fa = H.chute_world(t, (-0.2, ga - 0.3, 0.06))
    fb = H.chute_world(t, (-0.2, gb - 0.3, 0.06))
    H.walk(o, 1, stop - 1, stride=0.32, rate=0.85, travel=(fa, fb), skip=("armL",), bob=0.012)
    o["root"].keyframe_insert("location", frame=n)
    # left arm reaches across to the gurney rail; at the stop the head lifts toward the top doorway
    H.pose_hold(o, "L", shoulder=(math.radians(-25), math.radians(55), 0), elbow=(math.radians(-25), 0, 0), frame=1)
    o["neck"].rotation_euler = (0, 0, 0)
    o["neck"].keyframe_insert("rotation_euler", frame=stop)
    o["neck"].rotation_euler = (math.radians(24), 0, math.radians(-12))
    o["neck"].keyframe_insert("rotation_euler", frame=stop + 12)
    for tag in ("L", "R"):
        for k in ("hip", "knee"):
            o[f"{k}{tag}"].rotation_euler = (0, 0, 0)
            o[f"{k}{tag}"].keyframe_insert("rotation_euler", frame=stop + 3)
    # rim from the swinging bulb is the key; a faint blue kicker from up-slope
    kick = L.point((0.0, 0, 0), energy=25, color=(0.5, 0.62, 1.0), radius=0.1, name="kicker")
    kick.parent = root
    kick.location = (0.6, 13.0, 2.0)
    p0, tg = (-1.0, 13.2, 1.55), (0.3, 19.2, 0.85)
    c = H.cam(p0, tg, lens=28)
    c.parent = root
    p1 = tuple(p0[i] + (tg[i] - p0[i]) * 0.05 for i in range(3))
    H.cam_move(c, [(1, p0, tg), (stop, p0, tg), (n, p1, tg)])
    L.cam_light(c, energy=4, color=(0.6, 0.68, 0.85))
    d = H.dust((0.0, 18, 1.3), (2.2, 8, 2.4), n, count=260, radius=0.0025, emit=0.25)
    d.parent = root
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- sanatorium exterior (S02, S03, S06)
def _facade(L, n, lit, world=(0.035, 0.042, 0.06), sun=1.1, fog=0.012, near=None, tree_count=70):
    _dark(L, world, vol_end=160)
    s = H.sanatorium(lit=lit, near_trees=near, tree_count=tree_count)
    sn = _sun_dir(L, (0.45, 0.85, -0.22), energy=sun, color=(0.62, 0.7, 0.92), name="dusk")
    L.fog_volume(center=(0, -55, -12), size=(240, 110, 14), density=fog, color=(0.7, 0.74, 0.85))
    return s, sn


def _bay(block, f, b, e, m=0.8):
    return {(block, f, b): (L_emit(f"bay{block}{f}_{b}", m), e)}


def L_emit(name, s):
    import studio_lib as L
    return L.mat_emission(name, (1.0, 0.7, 0.4), s)


def S02(L, n):
    near = ([(15, 25, -54, -49)], 3)
    _facade(L, n, _bay("C", 3, 18, 25, 1.2), near=near)
    z0 = H.hill_z(20, -58) + 1.3
    p0, p1 = (20.0, -58.0, z0), (19.5, -57.0, z0 + 5.5)
    t0, t1 = (-4.0, 0.0, 9.0), (-4.0, 0.0, 10.5)
    c = H.cam(p0, t0, lens=35)
    H.cam_move(c, [(1, p0, t0), (n, p1, t1)])
    H.handheld(c, n, amp=0.01, rate=0.3, rot_amp=0.001)
    L.bake_static()


def S03(L, n):
    near = ([(-9, -3, -42, -39)], 2)
    _facade(L, n, _bay("C", 3, 18, 20, 1.0), sun=0.6, world=(0.022, 0.026, 0.038), near=near, tree_count=50)
    z = H.hill_z(-6, -45) + 1.5
    p0, t0 = (-6.0, -45.0, z), (0.0, 0.0, 9.5)
    p1 = tuple(p0[i] + (t0[i] - p0[i]) * 0.05 for i in range(3))
    c = H.cam(p0, t0, lens=35)
    H.cam_move(c, [(1, p0, t0), (n, p1, t0)], ease=False)
    L.dof(c, distance=4.0, fstop=1.4)
    dist = (Vector(t0) - Vector(p0)).length
    for f, d in ((1, 4.0), (int(n * 0.48), 4.0), (int(n * 0.62), dist), (n, dist)):
        c.data.dof.focus_distance = d
        c.data.dof.keyframe_insert("focus_distance", frame=f)
    L.bake_static()


def S06(L, n):
    bays = [(0, 19), (1, 17), (2, 20), (3, 18), (4, 19), (1, 21), (3, 16)]
    lit = {}
    for f, b in bays:
        lit.update(_bay("C", f, b, 22, 1.0))
    s, sn = _facade(L, n, lit, world=(0.03, 0.036, 0.052), sun=0.9, fog=0.01, tree_count=40)
    # night falls: sky + sun dim; bays switch off floor by floor, bottom to top
    bg = bpy.context.scene.world.node_tree.nodes["Background"].inputs[1]
    for f, v in ((1, 1.0), (n, 0.45)):
        bg.default_value = v
        bg.keyframe_insert("default_value", frame=f)
    H.key_energy(sn, [(1, 0.9), (n, 0.35)], "LINEAR")
    offs = {0: 18, 1: 32, 2: 46, 3: 60, 4: 74}
    for (blk, f, b), (m, e) in lit.items():
        off = offs[f] + (4 if b in (21, 16) else 0)
        H.key_emission(m, [(1, 1.0), (off, 1.0), (off + 1, 0.0)], "CONSTANT")
        lt = s["lights"].get((blk, f, b))
        if lt:
            H.key_energy(lt, [(1, e), (off, e), (off + 1, 0.0)], "CONSTANT")
    p0, p1 = (16.0, -30.0, 8.5), (8.0, -30.0, 8.5)
    c = H.cam(p0, (16.0, 0.0, 9.0), lens=50)
    H.cam_move(c, [(1, p0, (16.0, 0.0, 9.0)), (n, p1, (8.0, 0.0, 9.0))], ease=False)
    L.bake_static()


# --------------------------------------------------------------------------- 4th-floor corridor (S07-S10, S12, S13)
def _corridor(L, moon=4.0, fog=0.015, end_glow=1.0, world=(0.004, 0.005, 0.009)):
    _dark(L, world, vol_end=40)
    cor = H.porch_corridor(length=30.0, bay=BAY, moon_dir=MOON_DIR, moon=moon, fog=fog, end_glow=end_glow, open_w=BAY - 1.1)
    return cor


def _ball_pos(cor):
    p, _ = H.moon_floor_point(cor, BALL_OY, x=0.05)
    return (p[0], p[1], 0.035)


def S07(L, n):
    cor = _corridor(L, moon=4.5, end_glow=2.5)
    hy = cor["hy"]
    p0, p1 = (0.25, -13.2, 1.6), (0.05, -6.8, 1.62)
    c = H.cam(p0, (0.0, hy, 1.25), lens=24)
    keys = []
    for k in range(9):
        u = k / 8
        f = 1 + int((n - 1) * u)
        loc = tuple(p0[i] + (p1[i] - p0[i]) * u for i in range(3))
        loc = (loc[0], loc[1], loc[2] + 0.025 * math.sin(u * 16))
        keys.append((f, loc, (0.0 + 0.15 * math.sin(u * 5), hy, 1.25)))
    H.cam_move(c, keys, ease=False)
    H.handheld(c, n, amp=0.01, rate=0.9, rot_amp=0.005)
    fl = L.spot((0.18, -0.2, 0.0), (0, 0, 0), energy=500, size_deg=24, blend=0.55, color=(1.0, 0.92, 0.8), name="flashlight", radius=0.02)
    fl.parent = c
    fl.data.volume_factor = 0.6
    # shadow figure crosses the far doorway (L08)
    fig = H.figure("shadow", color=(0.002, 0.002, 0.002), height=1.88)
    fig["root"].rotation_euler = (0, 0, -math.pi / 2)
    st = int(n * 0.5)
    a, b = (-2.6, hy + 1.3, 0.0), (2.6, hy + 1.3, 0.0)
    fig["root"].location = a
    fig["root"].keyframe_insert("location", frame=1)
    H.walk(fig, st, 26, stride=0.5, rate=1.1, travel=(a, b), bob=0.02)
    H.dust((0.0, -6.0, 1.4), (2.6, 10, 2.4), n, count=450, radius=0.0025, emit=0.2)
    H.crisp_shadows()
    L.bake_static()


def S08(L, n):
    cor = _corridor(L, moon=4.5, fog=0.01)
    bp = _ball_pos(cor)
    ball = H.rubber_ball("ball", loc=bp)
    ball.rotation_euler = (0.4, 0.2, 0.9)
    p0, p1 = (bp[0] + 0.35, bp[1] - 2.6, 0.1), (bp[0] + 0.2, bp[1] - 1.5, 0.1)
    tg = (bp[0], bp[1] + 0.6, 0.06)
    c = H.cam(p0, tg, lens=50)
    H.cam_move(c, [(1, p0, tg), (n, p1, (bp[0], bp[1] + 0.4, 0.05))])
    H.handheld(c, n, amp=0.002, rate=0.3, rot_amp=0.0008)
    L.dof(c, target=ball, fstop=2.0)
    # flashlight beam from an unseen hand, sweeping across the floor and settling on the ball
    fl = L.spot((0, 0, 0), (0, 0, 0), energy=0, size_deg=16, blend=0.5, color=(1.0, 0.92, 0.8), name="flashlight", radius=0.02)
    src = (bp[0] - 0.6, bp[1] - 2.4, 1.3)
    hit = int(n * 0.45)
    H.cam_move(fl, [(1, src, (bp[0] - 1.1, bp[1] + 1.8, 0.0)), (hit, src, (bp[0], bp[1], 0.03)), (n, src, (bp[0], bp[1], 0.03))])
    H.key_energy(fl, [(1, 220), (n, 220)], "LINEAR")
    H.dust((bp[0], bp[1] - 0.8, 0.3), (1.4, 2.4, 0.6), n, count=180, radius=0.0012, emit=0.2)
    H.crisp_shadows()
    L.bake_static()


def _wide_cam(L, cor, n, push=0.0):
    bp = _ball_pos(cor)
    p0 = (bp[0] + 0.25, bp[1] - 4.0, 1.6)
    pitch = math.radians(16)
    tg = (bp[0] + 0.1, p0[1] + 10 * math.cos(pitch), 1.6 - 10 * math.sin(pitch))
    c = H.cam(p0, tg, lens=28)
    p1 = tuple(p0[i] + (tg[i] - p0[i]) * push for i in range(3))
    H.cam_move(c, [(1, p0, tg), (n, p1, tg)], ease=False)
    return c, bp


def S12(L, n):
    cor = _corridor(L, moon=4.5, fog=0.012)
    c, bp = _wide_cam(L, cor, n, push=0.005)
    # slow cloud pass over the moon (stripes breathe), dust barely moving
    H.key_energy(cor["moon"], [(1, 4.5), (int(n * 0.5), 3.4), (n, 4.2)], "BEZIER")
    H.dust((0.0, bp[1] + 1, 1.3), (2.6, 8, 2.4), n, count=300, radius=0.002, emit=0.2, drift=(0, 0, 0.004))
    H.crisp_shadows()
    L.bake_static()


def S13(L, n):
    cor = _corridor(L, moon=4.5, fog=0.012)
    c, bp = _wide_cam(L, cor, n, push=0.02)
    ball = H.rubber_ball("ball", loc=bp)
    stop = int(n * 0.8)
    y0 = bp[1] + 7.2
    keys = []
    for k in range(13):
        u = k / 12
        e = 1 - (1 - u) ** 2.2            # decelerating roll
        keys.append((1 + int((stop - 1) * u), (bp[0] + 0.02 * math.sin(u * 3), y0 + (bp[1] - y0) * e, 0.035)))
    keys.append((n, keys[-1][1]))
    H.roll_along(ball, keys, radius=0.035, axis_rot=lambda a: (-a, 0, 0))
    H.dust((0.0, bp[1] + 1, 1.3), (2.6, 8, 2.4), n, count=300, radius=0.002, emit=0.2, drift=(0, 0, 0.004))
    H.crisp_shadows()
    L.bake_static()


def _counter_bg(L, n, moon_keys, end_glow=0.4):
    cor = _corridor(L, moon=moon_keys[0][1], fog=0.012, end_glow=end_glow, world=(0.002, 0.0025, 0.004))
    H.key_energy(cor["moon"], moon_keys, "LINEAR")
    hy = cor["hy"]
    return cor, hy


def S09(L, n):
    cor, hy = _counter_bg(L, n, [(1, 1.0), (n, 0.8)])
    p0 = (0.0, -12.0, 1.55)
    c = H.cam(p0, (0.0, hy, 1.3), lens=28)
    H.cam_move(c, [(1, p0, (0.0, hy, 1.3)), (n, (0.0, -10.2, 1.55), (0.0, hy, 1.3))], ease=False)
    H.dust((0.0, -8.0, 1.4), (2.6, 8, 2.4), n, count=250, radius=0.002, emit=0.15)
    L.bake_static()


def S10(L, n):
    cor, hy = _counter_bg(L, n, [(1, 0.8), (n, 3.2)], end_glow=1.0)
    p0 = (0.0, -10.2, 1.55)
    c = H.cam(p0, (0.0, hy, 1.3), lens=35)
    H.cam_move(c, [(1, p0, (0.0, hy, 1.3)), (n, (0.0, -9.6, 1.62), (0.0, hy, 1.4))], ease=False)
    # the legend figure, struck through (3D, parented to camera; matches the S09 counter position)
    num_m = L.mat_emission("legend_num", (0.4, 1.0, 0.4), 1.3)
    tx = L.text3d("63,000", loc=(0, -0.012, -1.0), rot=(0, 0, 0), size=0.105, extrude=0.0, mat=num_m, font=ANTON, name="legend")
    tx.data.align_y = "CENTER"
    tx.parent = c
    red = L.mat_emission("strike_m", (1.0, 0.04, 0.03), 4.0)
    sk = H.box_mesh("strike", [(0.0, 0, 0, 0.5, 0.006, 0.001)], red)
    sk.parent = c
    sk.location = (-0.135, -0.012, -0.995)
    sk.rotation_euler = (0, 0, math.radians(-8))
    sk.scale = (0.001, 1, 1)
    sk.keyframe_insert("scale", frame=1)
    sk.keyframe_insert("scale", frame=4)
    sk.scale = (0.27, 1, 1)
    sk.keyframe_insert("scale", frame=11)
    # strike grows from the left edge: offset the box so its origin is its left end
    me = sk.data
    for v in me.vertices:
        v.co.x += 0.5
    H.dust((0.0, -6.0, 1.4), (2.6, 8, 2.4), n, count=250, radius=0.002, emit=0.15)
    L.bake_static()


# --------------------------------------------------------------------------- S11 evidence board: ghost tours
def S11(L, n):
    _dark(L, (0.01, 0.01, 0.012))
    H.box_mesh("bwall", [(0, 0.2, 0, 4, 0.05, 4)], L.mat_principled("bw", (0.05, 0.05, 0.055), rough=0.9))
    H.evidence_board("board", 2.4, 4.0)
    H.pinned_card("c_hdr", (0.0, -0.01, 1.32), 1.5, 0.36, [], header="WHAT SCEPTICS SAY", size=0.1, font_size_header=0.125,
                  color=(0.86, 0.83, 0.72), rot=math.radians(-1.5))
    tc = H.pinned_card("c_tour", (0.0, -0.012, 0.25), 1.6, 1.25, ["PAID", "GHOST TOURS"], size=0.1, rot=math.radians(2))
    H.ticket_icon("ticket", (0.0, -0.008, 0.02), w=0.9, h=0.4, parent=tc)
    redst = L.mat_principled("string", (0.6, 0.02, 0.02), rough=0.5)
    L.guideline([(0.0, -0.05, 1.45), (0.0, -0.05, 0.9)], mat=redst, thickness=0.005, name="str1")
    H.box_mesh("scraps", [(0.95, -0.006, 0.55, 0.2, 0.002, 0.26, 0.1), (-0.95, -0.006, -0.6, 0.22, 0.002, 0.16, -0.08),
                          (-0.9, -0.006, 1.0, 0.2, 0.002, 0.15, 0.05)], H.mat_paper("scrap", (0.6, 0.57, 0.48)))
    tgt = tuple(tc.location)
    tc.location = (tgt[0] + 2.6, tgt[1], tgt[2] + 0.1)
    tc.keyframe_insert("location", frame=1)
    tc.location = tgt
    tc.keyframe_insert("location", frame=12)
    tc.rotation_euler = (0, math.radians(2), 0)
    tc.keyframe_insert("rotation_euler", frame=12)
    tc.rotation_euler = (0, math.radians(3.2), 0)
    tc.keyframe_insert("rotation_euler", frame=15)
    tc.rotation_euler = (0, math.radians(2), 0)
    tc.keyframe_insert("rotation_euler", frame=19)
    lamp = L.spot((-1.6, -2.2, 2.6), (0, 0, 0), energy=900, size_deg=60, blend=0.8, color=(1.0, 0.78, 0.5), name="desklamp")
    H.aim(lamp, (-1.6, -2.2, 2.6), (0.0, 0, 0.5))
    c = H.cam((0.0, -4.6, 0.75), (0.0, 0, 0.7), lens=50)
    H.cam_move(c, [(1, (0.0, -4.6, 0.75), (0.0, 0, 0.7)), (n, (0.0, -4.0, 0.72), (0.0, 0, 0.68))], ease=False)
    H.crisp_shadows()
    L.bake_static()
