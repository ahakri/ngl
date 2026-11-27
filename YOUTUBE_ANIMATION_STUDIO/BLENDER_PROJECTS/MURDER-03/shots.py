"""MURDER-03 - D.B. Cooper: Northwest Orient Flight 305 (24 Nov 1971) and the Tena Bar money find (10 Feb 1980).
Shot builders: def SXX(L, n). Reusable builders (stylised 727, rain, storm cloud, lightning, parachute, money, cabin,
apron, riverbank, hangar, suspect wall) live in PIPELINE/blender/lib_murder.py.
Jet layout: nose +X, tail -X, belly -Z; ventral aft airstair hinge at local (-14, 0, -1.78).
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


def lin(o):
    M.set_interp(o, "LINEAR")


def cam_path(L, n, c0, c1, t0, t1, lens=35, ease=True):
    cam, ct = L.camera(loc=c0, target=t0, lens=lens)
    cam.data.clip_end = 3000
    L.cam_keys(cam, [(1, c0), (n, c1)])
    ct.location = t0
    ct.keyframe_insert("location", frame=1)
    ct.location = t1
    ct.keyframe_insert("location", frame=n)
    if not ease:
        lin(cam)
        lin(ct)
    return cam, ct


def figure_on(parts, loc, rot_z):
    r = parts["root"]
    r.location = loc
    r.rotation_euler = (0, 0, rot_z)


# ============================================================================= tail-at-night set (S01 / S23)
# open stair: hinge (-14, 0, -1.78), angle 16-35 = -19 deg -> lowest step approx (-18.9, 0, -3.45)
STEP_LOW = (-18.75, 0.0, -3.33)
STEP_MID = (-16.6, 0.0, -2.62)
S01_CAM0 = (-25.0, -4.6, -6.2)
S01_CAM1 = (-23.6, -4.0, -5.5)
S01_TGT0 = (-17.6, 0.0, -2.0)
S01_TGT1 = (-17.8, 0.0, -2.3)


def tail_night(L, n, cam0, cam1, tgt0, tgt1, flashes, fig_keys=None, stair_keys=None, hand=0.03):
    bg = M.storm_sky(zen=(0.006, 0.009, 0.018), hor=(0.03, 0.04, 0.065), strength=1.0)
    jet = M.jet727("jet", stair_open=35)
    if stair_keys:
        M.stair_anim(jet, stair_keys)
    M.beacon_blink(jet, n, every=26, on=3)
    # cool moon fill from above-behind + rim behind the stair (silhouette read)
    L.sun(rot=(R(-35), R(20), R(-60)), energy=0.6, color=(0.45, 0.55, 0.85), name="moonfill")
    L.area((-24, 6, 2), (R(70), 0, R(-140)), energy=2500, size=8, color=(0.5, 0.6, 0.95), name="rim")
    M.lightning(n, flashes, rot=(R(-55), R(15), R(-100)), energy=9.0, world_bg=bg, world_base=1.0, world_peak=6.0)
    # cloud deck streaming aft below the jet, ceiling above
    M.cloud_volume((-30, 0, -26), (160, 110, 18), density=0.35, scale=0.7, drift=(-40, 0, 0), n=n, color=(0.3, 0.34, 0.45),
                   name="deck")
    M.cloud_volume((-20, 30, 26), (160, 80, 22), density=0.25, scale=0.6, drift=(-35, 0, 0), n=n, color=(0.35, 0.4, 0.55),
                   name="ceiling")
    M.rain((-20, -1, -3), (36, 18, 16), (-34, 0, -9), n, count=1100, length=0.7, width=0.006, period=8, seed=3,
           cam=cam0, clear=2.5, emit=0.45)
    fig = L.char_figure("hijacker", color=(0.02, 0.02, 0.024), coat=True)
    figure_on(fig, STEP_LOW, R(90))
    for t in ("L", "R"):
        fig["shoulder" + t].rotation_euler = (0.15, 0, 0.25 if t == "L" else -0.25)
        fig["elbow" + t].rotation_euler = (0.6, 0, 0)
    bag = M.money_bag((0, 0.17, 1.25), name="chestbag")
    bag.scale = (0.75, 0.75, 0.75)
    bag.parent = fig["root"]
    # coat flap
    coat = fig["coat"]
    for f in range(1, n + 1, 3):
        coat.rotation_euler = (0.12 * math.sin(f * 0.9), 0.08 * math.sin(f * 1.3 + 1), 0)
        coat.keyframe_insert("rotation_euler", frame=f)
    if fig_keys:
        r = fig["root"]
        for f, p in fig_keys:
            r.location = p
            r.keyframe_insert("location", frame=f)
    cam, ct = cam_path(L, n, cam0, cam1, tgt0, tgt1, lens=28)
    cam.rotation_euler = (0, 0, 0)
    L.handheld(cam, n, amp=hand, rate=0.9, rot_amp=0.012)
    return jet, fig, cam


def S01(L, n):
    # figure stands on the lowest step; drops on "jumped" (~f56); stair springs up when the weight leaves
    hit = 56
    lo = Vector(STEP_LOW)
    fk = [(1, tuple(lo)), (hit - 6, tuple(lo + Vector((-0.1, 0, 0.02)))), (hit, tuple(lo + Vector((-0.5, 0, 0.05)))),
          (hit + 6, tuple(lo + Vector((-3.5, 0, -2.6)))), (hit + 14, tuple(lo + Vector((-11, 0, -9.5)))),
          (n, tuple(lo + Vector((-24, 0, -22))))]
    sk = [(1, 35), (hit, 35), (hit + 3, 27), (hit + 7, 37), (hit + 11, 33), (hit + 16, 35.5), (hit + 22, 35)]
    jet, fig, cam = tail_night(L, n, S01_CAM0, S01_CAM1, S01_TGT0, S01_TGT1, flashes=[hit + 1, 14], fig_keys=fk, stair_keys=sk)
    # crouch / lean out just before the jump
    for f, lean in ((1, 0.0), (hit - 8, 0.0), (hit - 2, -0.35), (hit + 4, -0.9)):
        fig["pelvis"].rotation_euler = (lean, 0, 0)
        fig["pelvis"].keyframe_insert("rotation_euler", frame=f)
    L.bake_static()


def S23(L, n):
    # loop: the silhouette walks down onto the lowest step; camera ends on S01 frame-1 framing
    back = tuple(S01_CAM0[i] + (S01_CAM0[i] - S01_CAM1[i]) * 0.9 for i in range(3))
    fk = [(1, STEP_MID), (int(n * 0.7), STEP_LOW), (n, STEP_LOW)]
    jet, fig, cam = tail_night(L, n, back, S01_CAM0, S01_TGT0, S01_TGT0, flashes=[20], fig_keys=fk, hand=0.02)
    L.anim_walk(fig, 1, int(n * 0.7), stride=0.3, rate=0.8)
    for t in ("L", "R"):
        for k in ("hip", "knee"):
            fig[k + t].rotation_euler = (0, 0, 0)
            fig[k + t].keyframe_insert("rotation_euler", frame=int(n * 0.7) + 4)
    L.bake_static()


# ============================================================================= S02 freefall with the bag

def S02(L, n):
    bg = M.storm_sky(zen=(0.006, 0.008, 0.016), hor=(0.035, 0.042, 0.065))
    fig = L.char_figure("hijacker", color=(0.02, 0.02, 0.024), coat=True)
    r = fig["root"]
    r.location = (0, 0, -1.2)
    r.rotation_euler = (R(-25), 0, 0)  # pitched forward, falling
    for t, s in (("L", 1), ("R", -1)):
        fig["shoulder" + t].rotation_euler = (0.9, 0, s * 1.1)
        fig["elbow" + t].rotation_euler = (0.9, 0, 0)
        fig["hip" + t].rotation_euler = (0.25, 0, s * 0.15)
        fig["knee" + t].rotation_euler = (-0.6, 0, 0)
    bag = M.money_bag((0, 0.21, 1.27 - 0.95), name="bag")
    bag.parent = fig["pelvis"]
    bag.location = (0, 0.21, 0.3)
    strap_m = L.mat_principled("strap", (0.05, 0.045, 0.035), rough=0.7)
    for sx in (-0.12, 0.12):
        s = L.prim("cube", loc=(sx, 0.11, 0.5))
        s.scale = (0.02, 0.01, 0.28)
        s.rotation_euler = (0.25, 0, -sx * 2)
        L.assign(s, strap_m)
        s.parent = fig["pelvis"]
    # flapping coat + arms in the wind
    for f in range(1, n + 1, 2):
        fig["coat"].rotation_euler = (0.25 + 0.12 * math.sin(f * 1.7), 0.1 * math.sin(f * 2.3), 0)
        fig["coat"].keyframe_insert("rotation_euler", frame=f)
        fig["shoulderL"].rotation_euler = (0.9 + 0.06 * math.sin(f * 1.1), 0, 1.1)
        fig["shoulderL"].keyframe_insert("rotation_euler", frame=f)
    # wind: rain and cloud stream upward past the falling man
    M.rain((0, 0, 0), (40, 12, 12), (2, 0, 34), n, count=1200, length=0.6, width=0.004, period=8, seed=7, cam=(0.9, 2.0, 0.0),
           clear=0.9, emit=0.7)
    M.cloud_volume((0, 0, 0), (60, 60, 60), density=0.12, scale=1.4, drift=(0, 0, 30), n=n, color=(0.3, 0.33, 0.42), name="cloudfall")
    M.loose_bills((0.2, 0.3, -1.6), 5, n, area=(1.6, 1.6, 0.6), vel=(0.2, -0.3, 2.6), spin=5, seed=5)
    L.sun(rot=(R(-20), R(30), R(10)), energy=0.8, color=(0.5, 0.6, 0.9), name="moonfill")
    M.lightning(n, [8, 44], rot=(R(-10), R(-10), R(0)), energy=10.0, world_bg=bg, world_peak=5)
    tgt = M.empty("focus", (0, 0.2, 0.25))
    cam, ct = L.camera(loc=(0.8, 1.1, 0.5), target=tgt, lens=40)
    L.area((-1.5, -2.0, 2.5), (R(-50), 0, R(-35)), energy=400, size=2, color=(0.55, 0.65, 1.0), name="rim")
    pts = []
    for k, f in enumerate((1, n)):
        a = R(-35) + R(55) * k
        cam.location = (2.3 * math.sin(a), 2.3 * math.cos(a), -0.05 + 0.15 * k)
        cam.keyframe_insert("location", frame=f)
    L.cam_light(cam, energy=160, color=(0.7, 0.8, 1.0))
    L.handheld(cam, n, amp=0.04, rate=1.2, rot_amp=0.015)
    L.bake_static()


# ============================================================================= S03 rain on the window (map plate)

def S03(L, n):
    M.storm_sky(zen=(0.01, 0.014, 0.022), hor=(0.05, 0.06, 0.08))
    glass = L.prim("plane", loc=(0, 0, 0), size=1, rot=(R(90), 0, 0))
    glass.scale = (6, 8, 1)
    L.assign(glass, L.mat_principled("glass", (0.02, 0.025, 0.03), rough=0.05, alpha=0.18))
    glass.data.materials[0].surface_render_method = "BLENDED"
    M.glass_drops((0, -0.02, 0), size=(3.0, 5.0), count=420, seed=3)
    # a few drops trickling down
    for i in range(7):
        rnd = random.Random(i)
        d = L.prim("sphere", loc=(rnd.uniform(-0.9, 0.9), -0.025, rnd.uniform(0.2, 1.8)), radius=0.04, segments=10, ring_count=6)
        d.scale = (1, 0.4, 1.6)
        L.assign(d, L.mat_principled(f"trk{i}", (0.6, 0.65, 0.72), rough=0.02, emit=(0.4, 0.45, 0.55), emit_strength=0.3))
        z0 = d.location.z
        d.keyframe_insert("location", frame=1)
        d.location.z = z0 - rnd.uniform(0.6, 1.6)
        d.keyframe_insert("location", frame=n)
    M.bokeh_lights((0, 30, 0), (40, 30, 18), count=45, seed=4, strength=15)
    # window frame edges
    fm = L.mat_principled("frame", (0.02, 0.02, 0.022), rough=0.6)
    for (x, z, sx, sz) in ((-1.55, 0, 0.12, 4), (1.55, 0, 0.12, 4)):
        b = L.prim("cube", loc=(x, -0.05, z))
        b.scale = (sx, 0.05, sz)
        L.assign(b, fm)
    L.area((0, -3, 2), (R(60), 0, 0), energy=60, size=3, color=(0.5, 0.6, 0.8), name="roomglow")
    cam, ct = cam_path(L, n, (0, -2.6, 0.3), (0, -2.2, 0.32), (0, 0, 0.3), (0, 0, 0.32), lens=40)
    L.dof(cam, distance=2.4, fstop=1.4)
    cam.data.dof.focus_distance = 2.6
    cam.data.dof.keyframe_insert("focus_distance", frame=1)
    cam.data.dof.focus_distance = 2.2
    cam.data.dof.keyframe_insert("focus_distance", frame=n)
    L.bake_static()


# ============================================================================= S04 / S05 cabin

def cabin_set(L, light=1.0):
    L.set_world(color=(0.02, 0.025, 0.035), strength=1.0)
    c = M.cabin_727(length=16, rows=12, light=light)
    return c


def S04(L, n):
    c = cabin_set(L)
    xr = c["row_x"][6]
    hj = L.char_figure("hijacker", color=(0.025, 0.025, 0.03), height=1.78)
    M.seated_pose(hj, slump=0.0, lean=-0.1)
    hj["pelvis"].location.z = 0.55
    for t in ("L", "R"):
        hj["hip" + t].rotation_euler = (R(85), 0, 0)
        hj["knee" + t].rotation_euler = (R(-80), 0, 0)
    hj["neck"].rotation_euler = (0, 0, 0)
    figure_on(hj, (xr - 0.05, -0.45, 0), R(-90))
    fa = L.char_figure("attendant", color=(0.16, 0.2, 0.3), height=1.66)
    figure_on(fa, (xr - 0.3, 0.18, 0), R(-157))
    # arms: hijacker reaches into the aisle (toward +Y local is forward = +X world; aisle is +Y world -> use shoulder z)
    sh = hj["shoulderL"]
    for f, v in ((1, (0.3, 0, 0)), (18, (0.3, 0, 0)), (40, (1.2, 0, 0.7)), (n, (1.25, 0, 0.75))):
        sh.rotation_euler = v
        sh.keyframe_insert("rotation_euler", frame=f)
    hj["elbowL"].rotation_euler = (0.2, 0, 0)
    sa = fa["shoulderR"]
    for f, v in ((1, (0.1, 0, 0)), (36, (0.1, 0, 0)), (58, (1.05, 0, 0.2)), (n, (1.0, 0, 0.2))):
        sa.rotation_euler = v
        sa.keyframe_insert("rotation_euler", frame=f)
    fa["elbowR"].rotation_euler = (0.35, 0, 0)
    # note: follows the hijacker's hand, then moves into the attendant's hand
    note = L.prim("plane", loc=(0, 0, 0), size=1, name="note")
    note.scale = (0.07, 0.045, 1)
    L.assign(note, L.mat_principled("note_m", (0.85, 0.83, 0.75), rough=0.8, emit=(0.8, 0.78, 0.7), emit_strength=0.4))
    sc = bpy.context.scene

    def hand(parts, side, f):
        sc.frame_set(f)
        bpy.context.view_layer.update()
        return parts["elbow" + side].matrix_world @ Vector((0, 0.02, -0.32 * 1.78 / 1.75))
    seq = [(f, hand(hj, "L", f)) for f in (1, 18, 30, 40, 52)]
    seq += [(62, hand(fa, "R", 62)), (72, hand(fa, "R", 72)), (n, hand(fa, "R", n))]
    for f, p in seq:
        note.location = p
        note.rotation_euler = (R(70), 0, R(20))
        note.keyframe_insert("location", frame=f)
    sc.frame_set(1)
    fe = M.empty("focus", seq[3][1])
    cam, ct = cam_path(L, n, (xr + 2.3, 0.85, 1.6), (xr + 1.75, 0.7, 1.52), (xr + 0.2, -0.25, 1.0), (xr + 0.25, -0.2, 1.0), lens=40)
    L.area((xr + 1.2, 0.6, 2.1), (R(30), 0, R(120)), energy=15, size=1.0, color=(1.0, 0.85, 0.65), name="key")
    L.dof(cam, target=fe, fstop=2.2)
    L.fog_volume(center=(0, 0, 1.2), size=(16, 3.6, 2.6), density=0.04, color=(0.9, 0.8, 0.65))
    L.bake_static()


def S05(L, n):
    c = cabin_set(L, light=0.2)
    xr = c["row_x"][6]
    case = M.rounded_box((xr, -0.45, 0.66), (0.48, 0.14, 0.34), (0.05, 0.035, 0.025), bevel=0.12, name="briefcase")
    case.rotation_euler = (0, R(-8), 0)
    hdl = L.prim("torus", loc=(xr, -0.45, 0.86), major_radius=0.06, minor_radius=0.012, rot=(R(90), 0, R(90)))
    L.assign(hdl, L.mat_principled("hdl", (0.02, 0.015, 0.01), rough=0.4))
    for dy in (-0.15, 0.15):
        lk = L.prim("cube", loc=(xr + dy * 0.0 + dy, -0.45 - 0.075, 0.78))
        lk.scale = (0.02, 0.006, 0.015)
        L.assign(lk, L.mat_principled("lock", (0.7, 0.6, 0.35), rough=0.2, metal=1.0))
    L.spot((xr, -0.45, 2.3), (0, 0, 0), energy=260, size_deg=30, blend=0.5, color=(1.0, 0.85, 0.65), name="topspot", radius=0.05)
    L.particle_cloud((xr, -0.45, 1.4), (0.8, 0.8, 1.4), count=120, radius=0.0015, drift=(0.01, 0, -0.01), nframes=n, name="motes",
                     mat=L.mat_principled("motes_m", (0.9, 0.85, 0.7), emit=(1, 0.9, 0.7), emit_strength=0.8))
    L.fog_volume(center=(xr, -0.45, 1.2), size=(2, 2, 2.4), density=0.08, color=(0.9, 0.85, 0.7))
    cam, ct = cam_path(L, n, (xr + 0.55, 0.55, 1.3), (xr + 0.45, 0.4, 1.2), (xr, -0.45, 0.68), (xr, -0.45, 0.7), lens=35)
    L.dof(cam, distance=2.4, fstop=2.8)
    L.bake_static()


# ============================================================================= S06 demands on the table

def S06(L, n):
    L.set_world(color=(0.004, 0.004, 0.005), strength=1.0)
    M.desk(size=(4, 4))
    hits = [4, 18, 32, 46]
    spots = [(-0.3, 0.55), (0.3, 0.6), (-0.32, 0.05), (0.3, 0.0)]
    cols = [(0.18, 0.2, 0.1), (0.7, 0.7, 0.66), (0.18, 0.2, 0.1), (0.7, 0.7, 0.66)]
    for i, (h, (x, y), c) in enumerate(zip(hits, spots, cols)):
        p = M.parachute_pack((x, y, 0), color=c, rot_z=random.Random(i).uniform(-0.25, 0.25), name=f"pack{i}")
        M.slam_in(p, h, frm=(0.0, 0.0, 0.9), rot0=0.3, scale0=1.25, lead=5)
        M.hide_until(p, h - 5)
        M.snow_burst((x, y, 0.03), n, h, count=160, radius=0.006, spread=0.5, rise=0.08, seed=10 + i, name=f"dust{i}",
                     emit=0.05, dur=18)
    bm = M.mat_bill("brick_m")
    for k in range(10):
        M.bill_brick((0.0 + (k % 2) * 0.165 - 0.08, -0.32 + (k // 4) * 0.07, 0.025 + ((k // 2) % 2) * 0.05), rot_z=R(90) * 0 + 0.02 * k,
                     mat=bm, name=f"brick{k}")
    L.spot((0, 0.2, 3.0), (0, 0, 0), energy=380, size_deg=45, blend=0.4, color=(1.0, 0.95, 0.88), name="top", radius=0.1)
    L.area((0, -2.5, 0.15), (R(88), 0, 0), energy=60, size=3, color=(1.0, 0.08, 0.05), name="redrim")
    cam, ct = cam_path(L, n, (0, 0.05, 2.4), (0, 0.1, 2.15), (0, 0.15, 0), (0, 0.2, 0), lens=35)
    cam.constraints[0].up_axis = "UP_Y"
    M.shake(cam, hits, amp=0.015, decay=6)
    L.bake_static()


# ============================================================================= S07 Seattle apron

def S07(L, n):
    M.storm_sky(zen=(0.01, 0.01, 0.016), hor=(0.08, 0.06, 0.05))
    g = L.prim("plane", loc=(0, 0, 0), size=1)
    g.scale = (400, 400, 1)
    L.assign(g, M.mat_wet_apron())
    tl = L.prim("plane", loc=(5, -9, 0.005), size=1)
    tl.scale = (120, 0.15, 1)
    L.assign(tl, L.mat_principled("taxi", (0.7, 0.5, 0.05), rough=0.3, emit=(0.6, 0.4, 0.03), emit_strength=0.4))
    jet = M.jet727("jet", loc=(0, 0, 3.6), stair_open=0, door_open=True, stair_light=False)
    gm = L.mat_principled("gear", (0.03, 0.03, 0.03), rough=0.6)
    for (x, y) in ((16, 0), (-1.5, 2.6), (-1.5, -2.6)):
        st = L.prim("cyl", loc=(x, y, 1.2), vertices=8, radius=0.12, depth=2.2)
        L.assign(st, gm)
        for dy in (-0.25, 0.25):
            w = L.prim("cyl", loc=(x, y + dy, 0.5), vertices=16, radius=0.5, depth=0.3, rot=(R(90), 0, 0))
            L.assign(w, gm)
    M.boarding_stairs((15.2, -1.95 - 0.85 - 2.25, 0), rot_z=R(90), height=2.85, length=4.5)
    M.flood_mast((30, -25, 0), (10, -4, 0), height=16, energy=90000)
    M.flood_mast((-12, -28, 0), (2, -2, 0), height=16, energy=70000)
    M.flood_mast((5, 30, 0), (5, 0, 0), height=16, energy=40000)
    L.sun(rot=(R(60), 0, R(30)), energy=0.15, color=(0.5, 0.55, 0.8), name="skyfill")
    # passengers walking away from the stair foot, toward camera-left
    rnd = random.Random(7)
    for i in range(9):
        p = L.char_figure(f"pax{i}", color=(0.025, 0.025, 0.03), height=rnd.uniform(1.6, 1.85), coat=rnd.random() < 0.5)
        start = Vector((15.2 + rnd.uniform(-0.4, 0.4), -8.2 - i * 1.3, 0))
        end = start + Vector((7.0, -3.0, 0))
        p["root"].rotation_euler = (0, 0, math.atan2(-(end - start).x, (end - start).y))
        L.anim_walk(p, 1, n, stride=0.4, rate=0.95, travel=(tuple(start), tuple(end)))
    cour = L.char_figure("courier", color=(0.03, 0.03, 0.035), height=1.8, coat=True)
    s0, s1 = Vector((6, -7.0, 0)), Vector((0.5, -6.2, 0))
    cour["root"].rotation_euler = (0, 0, math.atan2(-(s1 - s0).x, (s1 - s0).y))
    L.anim_walk(cour, 1, n, stride=0.4, rate=0.85, travel=(tuple(s0), tuple(s1)))
    b = M.money_bag((0.22, 0, -0.4), name="cbag")
    b.parent = cour["shoulderR"]
    M.rain((12, -16, 5), (26, 26, 14), (1.5, 0, -14), n, count=2400, length=0.45, width=0.008, period=6, seed=11,
           cam=(27, -19, 2.0), clear=2.0, emit=0.9, color=(0.9, 0.7, 0.5))
    L.fog_volume(center=(10, 0, 6), size=(90, 70, 14), density=0.005, color=(0.9, 0.75, 0.55))
    cam, ct = cam_path(L, n, (27, -19, 2.0), (29, -16.5, 2.0), (12, -5, 3.0), (12, -4.5, 3.0), lens=35, ease=False)
    L.area((14, -9, 15), (0, 0, 0), energy=9000, size=24, color=(1.0, 0.62, 0.3), name="sodiumwash")
    L.handheld(cam, n, amp=0.01, rate=0.4)
    L.bake_static()


# ============================================================================= map plates (S08, S15)

def S08(L, n):
    bg = M.storm_sky(zen=(0.004, 0.006, 0.012), hor=(0.02, 0.026, 0.04))
    L.sun(rot=(R(60), 0, R(-30)), energy=1.0, color=(0.5, 0.6, 0.9), name="moon")
    M.cloud_volume((0, 0, -20), (400, 400, 30), density=0.25, scale=0.25, drift=(0, 8, 0), n=n, color=(0.45, 0.5, 0.65), name="tops")
    jet = M.jet727("jet", loc=(0, 30, 0), rot_z=R(-90), stair_light=False)
    M.beacon_blink(jet, n, every=20, on=3, strength=200)
    M.lightning(n, [30], rot=(R(10), 0, 0), energy=4, world_bg=bg, world_peak=3)
    cam, ct = cam_path(L, n, (0, -90, 50), (0, -90, 40), (0, 20, -15), (0, 20, -18), lens=35, ease=False)
    jr = jet["root"]
    jr.keyframe_insert("location", frame=1)
    jr.location = (0, 10, 0)
    jr.keyframe_insert("location", frame=n)
    lin(jr)
    L.bake_static()


def S15(L, n):
    M.night_sky(stars=0.5, hor=(0.05, 0.06, 0.09), strength=1.5)
    L.sun(rot=(R(50), 0, R(40)), energy=3.0, color=(0.5, 0.6, 0.9), name="moon")
    def h(x, y):
        river = math.sin(y * 0.02) * 40
        d = abs(x - river)
        return 6 * M.smoothstep(25, 60, d) + 3 * noise.noise(Vector((x * 0.01, y * 0.01, 2))) - 1.5
    M.heightfield("land", -300, 300, -300, 300, 120, 120, h,
                  mat=L.mat_noise_surface("landm", (0.01, 0.014, 0.01), (0.03, 0.04, 0.03), scale=0.05, bump=0.3, voronoi=False))
    M.sea(size=(600, 600), loc=(0, 0, 0), color=(0.03, 0.04, 0.055), n=n, speed=(0.0, 1.0), name="river")
    spots = M.scatter_spots((-300, 300, -300, 300), 1200, h, seed=3, h=(14, 22), exclude=lambda x, y: h(x, y) < 3)
    M.fast_conifers("forest", spots, mat=L.mat_principled("tree_m", (0.008, 0.016, 0.01), rough=0.9), seed=3, bare_frac=0.0)
    cam, ct = cam_path(L, n, (0, -60, 320), (0, -40, 300), (0, 10, 0), (0, 20, 0), lens=35, ease=False)
    L.bake_static()


# ============================================================================= S09 side view: stair lowers in the storm

def S09(L, n):
    bg = M.storm_sky(zen=(0.006, 0.009, 0.018), hor=(0.035, 0.045, 0.07))
    jet = M.jet727("jet", stair_open=0)
    M.stair_anim(jet, [(1, 0), (14, 0), (int(n * 0.85), 35), (n, 35)])
    M.beacon_blink(jet, n, every=26, on=3)
    sp = jet["spill"].data
    for f, e in ((1, 0), (14, 0), (40, 900), (n, 900)):
        sp.energy = e
        sp.keyframe_insert("energy", frame=f)
    pt = jet["spill_pt"].data
    for f, e in ((1, 0), (14, 0), (40, 180), (n, 180)):
        pt.energy = e
        pt.keyframe_insert("energy", frame=f)
    L.sun(rot=(R(-40), R(10), R(-20)), energy=0.5, color=(0.45, 0.55, 0.85), name="moonfill")
    L.area((-10, 25, 6), (R(-80), 0, 0), energy=4000, size=20, color=(0.45, 0.55, 0.9), name="backrim")
    M.lightning(n, [20, 56, 88], rot=(R(-60), 0, R(180)), energy=8, world_bg=bg, world_peak=6)
    M.cloud_volume((-10, 40, -6), (200, 40, 40), density=0.3, scale=0.5, drift=(-45, 0, 0), n=n, color=(0.35, 0.4, 0.55),
                   name="behind")
    M.cloud_volume((-10, 0, -24), (200, 80, 16), density=0.35, scale=0.6, drift=(-45, 0, 0), n=n, color=(0.3, 0.34, 0.45),
                   name="deck")
    M.rain((-14, -12, -1), (40, 22, 20), (-36, 0, -8), n, count=1300, length=0.9, width=0.008, period=8, seed=5, emit=0.5,
           cam=(-34, -22, -5), clear=3)
    cam, ct = cam_path(L, n, (-36, -24, -5.5), (-31, -19, -4.6), (-14, 0, -0.5), (-16, 0, -1.6), lens=50)
    L.handheld(cam, n, amp=0.05, rate=0.8)
    L.bake_static()


# ============================================================================= S10 straight down: the canopy blooms

def S10(L, n):
    bg = M.storm_sky(zen=(0.005, 0.007, 0.012), hor=(0.02, 0.025, 0.035))
    L.sun(rot=(R(15), R(10), 0), energy=1.6, color=(0.5, 0.6, 0.9), name="moon")
    # forest far below
    def h(x, y):
        return -420 + 25 * noise.noise(Vector((x * 0.004, y * 0.004, 1))) + 6 * noise.noise(Vector((x * 0.02, y * 0.02, 3)))
    M.heightfield("ground", -500, 500, -500, 500, 90, 90, h, mat=L.mat_principled("gm", (0.006, 0.01, 0.007), rough=0.9))
    spots = M.scatter_spots((-260, 260, -260, 260), 2600, h, seed=4, h=(22, 34))
    M.fast_conifers("forest", spots, mat=L.mat_principled("tm", (0.012, 0.03, 0.018), rough=0.9), seed=4, bare_frac=0.0)
    M.cloud_volume((0, 0, -95), (500, 500, 40), density=0.2, scale=0.3, contrast=(0.5, 0.65), drift=(5, 0, 25), n=n,
                   color=(0.5, 0.55, 0.7), name="clouds")
    fig = L.char_figure("jumper", color=(0.02, 0.02, 0.024), coat=True)
    r = fig["root"]
    for t, s in (("L", 1), ("R", -1)):
        fig["shoulder" + t].rotation_euler = (0, 0, s * 2.4)
        fig["hip" + t].rotation_euler = (0, s * 0.3, 0)
    can_root, can = M.parachute((0, 0, 0), radius=3.2, line_len=5.5, color=(0.85, 0.82, 0.72))
    # figure falls away; canopy opens at f_open and the fall slows
    fo = 22
    keys = [(1, -6), (fo, -28), (fo + 6, -34), (n, -40)]
    for f, z in keys:
        r.location = (0.3 * (f / n), 0.2 * (f / n), z)
        r.keyframe_insert("location", frame=f)
        can_root.location = (0.3 * (f / n), 0.2 * (f / n), z + 6.2)
        can_root.keyframe_insert("location", frame=f)
    for f, s in ((1, 0.001), (fo - 1, 0.001), (fo + 2, 0.35), (fo + 6, 1.05), (fo + 9, 1.0)):
        can_root.scale = (s, s, s)
        can_root.keyframe_insert("scale", frame=f)
    for f, rz in ((fo, 0), (n, R(40))):
        can_root.rotation_euler = (0, 0, rz)
        can_root.keyframe_insert("rotation_euler", frame=f)
    M.rain((0, 0, -20), (30, 8, 8), (0, 0, -16), n, count=600, length=0.6, width=0.008, period=8, seed=2, emit=0.4)
    M.lightning(n, [fo + 3], rot=(R(10), R(-15), 0), energy=12, world_bg=bg, world_peak=4)
    cam, ct = L.camera(loc=(0, 0, 0), target=None, lens=24)
    cam.data.clip_end = 3000
    cam.rotation_euler = (0, 0, 0)  # looking straight down (-Z)
    cam.keyframe_insert("rotation_euler", frame=1)
    cam.rotation_euler = (0, 0, R(25))
    cam.keyframe_insert("rotation_euler", frame=n)
    sp = L.spot((0, 0, 0), (0, 0, 0), energy=12000, size_deg=12, blend=0.6, color=(1.0, 0.65, 0.35), name="stairspill")
    L.handheld(cam, n, amp=0.02, rate=1.0, rot_amp=0.01)
    L.bake_static()


# ============================================================================= S11 overcast search

def forest_floor(name, h, area, seed=5, count=700):
    """Fern / undergrowth clumps (flattened cones) in one mesh."""
    import bmesh
    from mathutils import Matrix
    rnd = random.Random(seed)
    bm = bmesh.new()
    for i in range(count):
        x, y = rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3])
        s = rnd.uniform(0.3, 0.8)
        for k in range(4):
            a = rnd.uniform(0, 6.28)
            m = Matrix.Translation((x, y, h(x, y) + 0.1 * s)) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(1.1, 4, "X") @ \
                Matrix.Diagonal((0.25 * s, 0.05 * s, 0.7 * s, 1))
            bmesh.ops.create_cone(bm, cap_ends=False, segments=4, radius1=1.0, radius2=0.0, depth=1.0, matrix=m)
    o = L.mesh_from_bm(name, bm)
    L.assign(o, L.mat_noise_surface(name + "_m", (0.03, 0.06, 0.02), (0.07, 0.12, 0.04), scale=3, bump=0.2, voronoi=False))
    return o


def S11(L, n):
    M.dawn_sky(hor=(0.42, 0.45, 0.44), mid=(0.33, 0.36, 0.38), zen=(0.22, 0.25, 0.28), strength=2.0)
    L.sun(rot=(R(30), R(20), R(40)), energy=2.5, color=(0.8, 0.85, 0.9), angle=20, name="overcast")
    bpy.context.scene.eevee.use_volumetric_shadows = False
    def h(x, y):
        return 1.2 * noise.noise(Vector((x * 0.05, y * 0.05, 4)))
    M.heightfield("floor", -60, 60, -60, 60, 120, 120, h,
                  mat=L.mat_noise_surface("floorm", (0.03, 0.035, 0.02), (0.09, 0.09, 0.05), scale=1.5, bump=0.3, voronoi=False))
    spots = M.scatter_spots((-50, 50, -10, 60), 260, h, seed=2, h=(14, 24), exclude=lambda x, y: abs(x) < 7 and y < 12)
    spots += M.scatter_spots((-50, 50, -60, -10), 120, h, seed=3, h=(14, 24), exclude=lambda x, y: abs(x) < 14)
    M.fast_conifers("forest", spots, mat=M.mat_dusted("trees", base=(0.02, 0.04, 0.025), snow=(0.05, 0.08, 0.05)), seed=2,
                     bare_frac=0.1)
    forest_floor("ferns", h, (-12, 12, -8, 14), count=500)
    jm = L.mat_principled("jacket", (0.5, 0.36, 0.05), rough=0.6)
    for i in range(3):
        f = L.char_figure(f"searcher{i}", color=(0.05, 0.05, 0.045), height=1.78, coat=True)
        L.assign(f["coat"], jm)
        x = -2.4 + i * 2.4
        start = (x, -1.5 + i * 0.4, h(x, 0))
        end = (x + 0.3, 2.0 + i * 0.4, h(x, 3))
        L.anim_walk(f, 1, n, stride=0.35, rate=0.8, travel=(start, end))
        f["shoulderR"].rotation_euler = (1.0, 0, 0)
        tl = L.spot((0, 0.4, -0.3), (R(-80), 0, 0), energy=300, size_deg=25, blend=0.4, color=(1, 0.9, 0.7), parent=f["shoulderR"],
                    name=f"torch{i}")
        tl.rotation_euler = (R(-90), 0, 0)
        bulb = L.prim("sphere", loc=(0, 0, -0.62), radius=0.035, segments=8, ring_count=6)
        L.assign(bulb, L.mat_emission(f"tb{i}", (1, 0.9, 0.7), 30))
        bulb.parent = f["shoulderR"]
        tl.location = (0, 0, -0.62)
    L.fog_volume(center=(0, 14, 5), size=(60, 50, 10), density=0.03, color=(0.75, 0.8, 0.78))
    M.rain((0, 2, 4), (12, 16, 14), (0.4, 0, -6), n, count=900, length=0.12, width=0.004, period=8, seed=9, emit=0.4,
           color=(0.8, 0.85, 0.85), cam=(0, -10, 6), clear=1.5)
    cam, ct = cam_path(L, n, (0.5, -9, 5.0), (0, -8.0, 2.4), (0, 4, 3.5), (0, 1.5, 1.0), lens=35)
    L.bake_static()


# ============================================================================= S12 / S13 Tena Bar, 1980

def winter_day(L, sun_elev=11, sun_az=-55, sun_e=3.0):
    bg = M.dawn_sky(hor=(0.75, 0.74, 0.72), mid=(0.52, 0.56, 0.62), zen=(0.28, 0.35, 0.48), strength=1.0,
                    sun_dir=(math.sin(R(sun_az)), math.cos(R(sun_az)), 0.2))
    s = L.sun(rot=(R(90 - sun_elev), 0, R(180 + sun_az)), energy=sun_e, color=(1.0, 0.9, 0.78), angle=1.5, name="wsun")
    return s


def S12(L, n):
    winter_day(L, sun_elev=10, sun_az=-60)
    h, g, w = M.riverbank(x=(-40, 40), y=(-30, 8), res=0.2, water_y=6.0, seed=2)
    # far shore: low wooded bank
    far = L.prim("cube", loc=(0, 150, 1.5))
    far.scale = (300, 20, 2.5)
    L.assign(far, L.mat_principled("farbank", (0.12, 0.12, 0.11), rough=0.9))
    spots = [(random.Random(i).uniform(-250, 250), random.Random(i + 99).uniform(140, 165), 3.5, random.Random(i + 7).uniform(10, 18))
             for i in range(500)]
    M.fast_conifers("farforest", spots, mat=L.mat_principled("ffm", (0.08, 0.09, 0.08), rough=0.9), seed=5, bare_frac=0.3)
    # child kneeling, sweeping sand flat
    kid = L.char_figure("child", color=(0.03, 0.03, 0.035), height=1.25, coat=True)
    s = 1.25 / 1.75
    kx, ky = 0.0, -2.0
    kid["root"].location = (kx, ky, h(kx, ky) - 0.46 * s)
    kid["root"].rotation_euler = (0, 0, R(160))
    for t in ("L", "R"):
        kid["hip" + t].rotation_euler = (-0.25, 0, 0)
        kid["knee" + t].rotation_euler = (R(-95), 0, 0)
    kid["pelvis"].rotation_euler = (0.45, 0, 0)
    for f in range(1, n + 1, 2):
        ph = f * 0.28
        kid["shoulderL"].rotation_euler = (1.2, 0, 0.45 * math.sin(ph))
        kid["shoulderR"].rotation_euler = (1.2, 0, 0.45 * math.sin(ph + 0.6))
        for t in ("L", "R"):
            kid["shoulder" + t].keyframe_insert("rotation_euler", frame=f)
    # parent in the background carrying driftwood along the waterline
    ad = L.char_figure("adult", color=(0.03, 0.03, 0.035), height=1.8, coat=True)
    a0, a1 = Vector((6.5, 3.0, 0)), Vector((3.5, 2.6, 0))
    ad["root"].rotation_euler = (0, 0, math.atan2(-(a1 - a0).x, (a1 - a0).y))
    a0.z, a1.z = h(a0.x, a0.y), h(a1.x, a1.y)
    L.anim_walk(ad, 1, n, stride=0.35, rate=0.7, travel=(tuple(a0), tuple(a1)))
    lg = M.driftwood((0, 0.25, 1.05), length=1.8, r=0.07, rot=(0, R(90), 0), name="carried")
    lg.parent = ad["pelvis"]
    lg.location = (0, 0.25, 0.1)
    for sd in ("L", "R"):
        ad["shoulder" + sd].rotation_euler = (0.8, 0, 0)
    for i, (x, y, rz) in enumerate(((2.5, 1.2, 0.3), (2.8, 1.5, 1.2), (2.2, 1.6, -0.5), (2.6, 1.3, 2.0))):
        M.driftwood((x, y, h(x, y) + 0.08 + 0.1 * (i // 2)), length=1.8, r=0.08, rot=(R(90), 0, rz), name=f"log{i}")
    L.fog_volume(center=(0, 30, 2), size=(200, 60, 6), density=0.02, color=(0.85, 0.88, 0.92))
    cam, ct = cam_path(L, n, (-1.2, -12.5, 1.9), (-0.6, -7.8, 1.5), (0.3, 0, 0.6), (0.2, -1.5, 0.5), lens=35)
    L.handheld(cam, n, amp=0.01, rate=0.4)
    L.bake_static()


def S13(L, n):
    winter_day(L, sun_elev=14, sun_az=-75, sun_e=4.0)
    # sand patch with a mound over the bundles; shape key sweeps it into a shallow dip
    N = 120
    S = 0.7
    rnd = random.Random(3)
    def base(x, y):
        return 0.004 * math.sin(x * 60 + 4 * noise.noise(Vector((x * 6, y * 6, 1)))) + 0.006 * noise.noise(Vector((x * 9, y * 9, 2)))
    def mound(x, y):
        d = math.hypot(x / 1.2, y)
        return 0.035 * (1 - M.smoothstep(0.08, 0.2, d))
    def dip(x, y):
        d = math.hypot(x / 1.2, y)
        return -0.04 * (1 - M.smoothstep(0.12, 0.2, d)) + 0.012 * M.smoothstep(0.12, 0.17, d) * (1 - M.smoothstep(0.17, 0.24, d))
    xs = [-S / 2 + S * i / (N - 1) for i in range(N)]
    verts = [(x, y, base(x, y) + mound(x, y)) for y in xs for x in xs]
    faces = [(j * N + i, j * N + i + 1, (j + 1) * N + i + 1, (j + 1) * N + i) for j in range(N - 1) for i in range(N - 1)]
    sand = M.mesh_obj("sand", verts, faces, mat=L.mat_noise_surface("sandm", (0.3, 0.26, 0.19), (0.52, 0.46, 0.35), scale=90,
                                                                       bump=0.4, voronoi=False, rough=0.7), smooth=True)
    sand.shape_key_add(name="basis")
    sk = sand.shape_key_add(name="swept")
    for k, (x, y, z) in enumerate(verts):
        sk.data[k].co = (x, y, base(x, y) + dip(x, y))
    sk.value = 0.0
    sk.keyframe_insert("value", frame=1)
    sk.keyframe_insert("value", frame=6)
    sk.value = 1.0
    sk.keyframe_insert("value", frame=int(n * 0.6))
    for i, (x, y, rz) in enumerate(((-0.06, 0.035, 0.15), (0.07, 0.03, -0.2), (0.0, -0.045, 0.05))):
        M.rotten_bundle((x, y, -0.024 + i * 0.002), rot_z=rz, size=(0.156, 0.066, 0.03), name=f"bundle{i}")
    grains = L.particle_cloud((0, 0, 0.05), (0.3, 0.25, 0.08), count=120, radius=0.0012, drift=(0.0, 0.0, -0.04), nframes=n,
                              name="grains", mat=L.mat_principled("grm", (0.5, 0.44, 0.32), rough=0.8))
    for f, s in ((1, 1.0), (int(n * 0.6), 1.0), (n, 0.001)):
        grains.scale = (s, s, s)
        grains.keyframe_insert("scale", frame=f)
    cam, ct = cam_path(L, n, (0.02, -0.25, 0.75), (0.01, -0.2, 0.62), (0, 0.0, 0), (0, 0.0, 0), lens=85)
    L.dof(cam, distance=0.8, fstop=2.0)
    cam.data.dof.focus_distance = 0.79
    cam.data.dof.keyframe_insert("focus_distance", frame=1)
    cam.data.dof.focus_distance = 0.65
    cam.data.dof.keyframe_insert("focus_distance", frame=n)
    L.bake_static()


# ============================================================================= S14 serial match

def S14(L, n):
    L.set_world(color=(0.004, 0.004, 0.005), strength=1.0)
    M.desk(size=(3, 3))
    font = M._font(M.F_MONO)
    ink = L.mat_principled("ink", (0.03, 0.03, 0.03), rough=0.8)
    # bill fragment (left)
    bill = L.prim("plane", loc=(-0.22, 0.3, 0.002), size=1, rot=(0, 0, R(-6)))
    bill.scale = (0.32, 0.14, 1)
    L.assign(bill, M.mat_bill("billfrag", c=(0.16, 0.24, 0.15)))
    t = L.text3d("L 00000004 A", loc=(-0.22, 0.32, 0.004), rot=(0, 0, R(-6)), size=0.03, extrude=0, mat=ink, name="billserial")
    t.data.font = font or t.data.font
    t.data.align_y = "CENTER"
    # microfilm strip (right): rows of placeholder serials
    film = L.prim("plane", loc=(0.24, 0.12, 0.003), size=1, rot=(0, 0, R(3)))
    film.scale = (0.3, 0.75, 1)
    L.assign(film, L.mat_principled("film", (0.015, 0.015, 0.018), rough=0.2))
    rows = []
    for k in range(10):
        y = 0.42 - k * 0.068
        tr = L.text3d(f"L 0000000{k} A", loc=(0.24, y, 0.005), rot=(0, 0, R(3)), size=0.026, extrude=0,
                      mat=L.mat_emission(f"row{k}", (0.75, 0.85, 0.8), 1.5), name=f"row{k}")
        tr.data.font = font or tr.data.font
        tr.data.align_y = "CENTER"
        rows.append((y, tr))
    # highlight bar scanning down to the matching row (k=4)
    hb = L.prim("plane", loc=(0.24, 0.42, 0.0045), size=1, rot=(0, 0, R(3)))
    hb.scale = (0.28, 0.05, 1)
    hm = L.mat_principled("hbar", (1.0, 0.8, 0.1), emit=(1.0, 0.75, 0.1), emit_strength=1.2, alpha=0.35)
    hm.surface_render_method = "BLENDED"
    L.assign(hb, hm)
    ym = rows[4][0]
    for f, y in ((1, 0.42), (10, 0.42), (32, ym), (n, ym)):
        hb.location.y = y
        hb.keyframe_insert("location", frame=f)
    # red connector line from bill serial to matching row
    red = M.glow_poly([(-0.05, 0.31, 0.008), (0.03, 0.31, 0.008), (0.06, ym, 0.008), (0.1, ym, 0.008)], color=(1.0, 0.08, 0.05),
                      strength=6, bevel=0.003, name="link")
    M.curve_draw(red, 30, 40)
    for (x, y) in ((-0.22, 0.32), (0.24, ym)):
        c = M.glow_poly([(x + 0.16 * math.cos(a), y + 0.045 * math.sin(a), 0.008) for a in [i * 2 * math.pi / 24 for i in range(24)]],
                        color=(1.0, 0.08, 0.05), strength=6, bevel=0.003, name="ring", closed=True)
        M.curve_draw(c, 38, 46)
    M.desk_lamp((-0.7, 0.9, 0), (0, 0.25, 0), energy=14, rot_z=R(200))
    L.area((0, 0.2, 1.5), (0, 0, 0), energy=8, size=1, color=(0.8, 0.85, 1.0), name="fill")
    cam, ct = cam_path(L, n, (0.06, -0.2, 1.95), (0.08, -0.1, 1.6), (0.06, 0.16, 0), (0.08, 0.16, 0), lens=40)
    L.bake_static()


# ============================================================================= S16 theory board

def mat_photo_sandbar(name="photo"):
    m, nn, l = L._mat(name)
    p = nn["Principled BSDF"]
    tc = nn.new("ShaderNodeTexCoord")
    sp = nn.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sp.inputs[0])
    nz = nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 12
    l.new(tc.outputs["Generated"], nz.inputs["Vector"])
    a = nn.new("ShaderNodeMath"); a.operation = "ADD"
    l.new(sp.outputs["Y"], a.inputs[0])
    mm = nn.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.inputs[1].default_value = 0.08
    l.new(nz.outputs["Fac"], mm.inputs[0]); l.new(mm.outputs[0], a.inputs[1])
    ramp = nn.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.1; cr.elements[0].color = (0.5, 0.42, 0.3, 1)
    cr.elements[1].position = 0.95; cr.elements[1].color = (0.55, 0.6, 0.65, 1)
    e = cr.elements.new(0.5); e.color = (0.45, 0.4, 0.32, 1)
    e2 = cr.elements.new(0.56); e2.color = (0.25, 0.3, 0.33, 1)
    e3 = cr.elements.new(0.7); e3.color = (0.2, 0.23, 0.22, 1)
    l.new(a.outputs[0], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.3
    return m


def S16(L, n):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0)
    B = M.evidence_board(w=3.2, h=5.0, lamp_energy=220)
    # photo card of the sandbar (white border)
    pr = M.empty("photo", (0.0, -0.03, 1.45))
    bd = L.prim("plane", loc=(0, 0, 0), size=1, rot=(R(90), 0, 0))
    bd.scale = (1.15, 0.85, 1)
    L.assign(bd, M.mat_paper("photoborder", (0.75, 0.72, 0.65)))
    bd.parent = pr
    ph = L.prim("plane", loc=(0, -0.003, 0.04), size=1, rot=(R(90), 0, 0))
    ph.scale = (1.0, 0.65, 1)
    L.assign(ph, mat_photo_sandbar())
    ph.parent = pr
    pr.rotation_euler = (0, R(2), 0)
    cap = L.text3d("TENA BAR, 1980", loc=(0, -0.005, -0.36), size=0.08, extrude=0, mat=L.mat_principled("capink", (0.05, 0.04, 0.03)),
                   name="cap")
    cap.data.font = M._font(M.F_MONO) or cap.data.font
    cap.parent = pr
    pin = L.prim("sphere", loc=(0, -0.03, 0.4), radius=0.03, segments=10, ring_count=6)
    L.assign(pin, L.mat_principled("pinm", (0.6, 0.04, 0.03), rough=0.3))
    pin.parent = pr
    cards = [("WASHED\nDOWNSTREAM?", (-0.9, -0.05, 0.25), 3, 0.08), ("BURIED?", (0.95, -0.05, 0.1), 31, -0.06),
             ("?", (0.0, -0.05, -0.55), 58, 0.03)]
    roots = []
    for i, (txt, loc, hit, rot) in enumerate(cards):
        c = M.paper_card(txt, loc, size=(1.0, 0.68), rot_y=rot, badge="THEORY", name=f"card{i}", text_size=0.19 if i == 0 else 0.32)
        M.slam_in(c, hit, frm=(0.0, -1.2, 0.2), rot0=0.25, scale0=1.4, lead=5)
        M.hide_until(c, max(2, hit - 5))
        s = M.red_string([(loc[0], -0.06, loc[2] + 0.28), (0.0, -0.06, 1.85)], name=f"str{i}")
        M.curve_draw(s, hit + 2, hit + 12)
    cam, ct = cam_path(L, n, (0.0, -4.6, 0.9), (0.0, -3.7, 0.95), (0.0, 0, 0.55), (0.0, 0, 0.65), lens=35)
    L.handheld(cam, n, amp=0.01, rate=0.5)
    L.particle_cloud((0, -1.5, 1.5), (3, 2, 2.5), count=300, radius=0.004, drift=(0.01, 0, -0.01), nframes=n, name="dust")
    L.bake_static()


# ============================================================================= S17 empty sky over the forest

def S17(L, n):
    bg = M.storm_sky(zen=(0.006, 0.008, 0.014), hor=(0.03, 0.04, 0.06))
    L.sun(rot=(R(65), 0, R(-150)), energy=2.2, color=(0.5, 0.6, 0.9), name="moon")
    def h(x, y):
        return 20 * noise.noise(Vector((x * 0.006, y * 0.006, 5))) + 5 * noise.noise(Vector((x * 0.03, y * 0.03, 1)))
    M.heightfield("hills", -400, 400, -100, 700, 120, 120, h, mat=L.mat_principled("hm", (0.006, 0.01, 0.007), rough=0.9))
    spots = M.scatter_spots((-250, 250, 0, 500), 2600, h, seed=6, h=(16, 26))
    M.fast_conifers("forest", spots, mat=M.mat_dusted("trees", base=(0.01, 0.02, 0.014), snow=(0.05, 0.06, 0.07)), seed=6,
                     bare_frac=0.0)
    M.cloud_volume((0, 250, 110), (700, 500, 60), density=0.06, scale=0.25, drift=(10, 0, 0), n=n, color=(0.4, 0.45, 0.6),
                   name="ceiling")
    L.fog_volume(center=(0, 250, 15), size=(700, 500, 30), density=0.004, color=(0.6, 0.65, 0.8))
    M.rain((0, 0, 60), (20, 20, 20), (1, 0, -14), n, count=1400, length=0.7, width=0.01, period=8, seed=13, emit=0.5,
           cam=(0, -20, 70), clear=2)
    M.lightning(n, [12], rot=(R(-70), 0, 0), energy=4, world_bg=bg, world_peak=4)
    cam, ct = cam_path(L, n, (0, -20, 70), (0, -20, 66), (0, 140, 140), (0, 120, 20), lens=35)
    L.bake_static()


# ============================================================================= S18 / S19 hangar + Cooper vane

def hangar_jet(L, n):
    L.set_world(color=(0.01, 0.012, 0.016), strength=1.0)
    M.hangar(size=(90, 60, 20), light=1.0)
    jet = M.jet727("jet", loc=(0, 0, 4.0), stair_open=0, vane=True, stair_light=False, nav_lights=False)
    gm = L.mat_principled("gear", (0.03, 0.03, 0.03), rough=0.6)
    for (x, y) in ((16, 0), (-1.5, 2.6), (-1.5, -2.6)):
        st = L.prim("cyl", loc=(x, y, 1.6), vertices=8, radius=0.14, depth=3.0)
        L.assign(st, gm)
        for dy in (-0.25, 0.25):
            w = L.prim("cyl", loc=(x, y + dy, 0.55), vertices=16, radius=0.55, depth=0.3, rot=(R(90), 0, 0))
            L.assign(w, gm)
    L.area((-14, -12, 2), (R(70), 0, R(-20)), energy=3000, size=8, color=(0.7, 0.8, 1.0), name="key")
    return jet


def S18(L, n):
    jet = hangar_jet(L, n)
    vh = jet["vane_hinge"]
    fv = 24
    for f, a in ((1, 85), (fv - 2, 85), (fv + 2, -5), (fv + 5, 4), (fv + 8, 0)):
        vh.rotation_euler = (0, R(a), 0)
        vh.keyframe_insert("rotation_euler", frame=f)
    M.stair_anim(jet, [(1, 0), (fv + 4, 0), (fv + 10, 4), (fv + 13, 0.5), (fv + 16, 3), (fv + 20, 0), (n, 0)])
    # blueprint: airflow line + vane outline (world coords; jet root z=4)
    bz = 4.0 - 1.78
    hx = -14.0 + 0.55
    flow = M.glow_poly([(-4, -1.2, bz - 0.6), (-24, -1.2, bz - 0.6)], color=(0.3, 0.65, 1.0), strength=5, bevel=0.02, name="flow")
    M.curve_draw(flow, 4, 22)
    for k, dz in enumerate((-0.35, -0.85)):
        ar = M.glow_poly([(-8, -1.2, bz + dz), (-20, -1.2, bz + dz), (-19.4, -1.2, bz + dz + 0.25), (-20, -1.2, bz + dz),
                          (-19.4, -1.2, bz + dz - 0.25)], color=(0.3, 0.65, 1.0), strength=4, bevel=0.015, name=f"flowar{k}")
        M.curve_draw(ar, 6 + 4 * k, 26 + 4 * k)
    box = M.glow_poly(M.rect_pts(hx, bz - 0.3, 0.9, 0.9, y=-1.2), color=(0.3, 0.65, 1.0), strength=6, bevel=0.015, name="vbox",
                      closed=True)
    M.curve_draw(box, 20, 34)
    L.particle_cloud((-14, -6, 3), (14, 8, 6), count=400, radius=0.006, drift=(0.02, 0, 0.01), nframes=n, name="dust")
    # orbit 20 deg around the tail
    tgt = (-14.5, 0, 2.6)
    r_ = 9.0
    tgt = (-15.0, 0, 2.1)
    cam, ct = L.camera(loc=(0, 0, 0), target=tgt, lens=40)
    for f, a in ((1, R(-30)), (n, R(-10))):
        cam.location = (tgt[0] + r_ * math.sin(a), -r_ * math.cos(a), 0.7)
        cam.keyframe_insert("location", frame=f)
    L.bake_static()


def S19(L, n):
    jet = hangar_jet(L, n)
    vh = jet["vane_hinge"]
    fv = 6
    for f, a in ((1, 60), (fv - 1, 60), (fv + 2, -6), (fv + 4, 3), (fv + 7, 0)):
        vh.rotation_euler = (0, R(a), 0)
        vh.keyframe_insert("rotation_euler", frame=f)
    vm = jet["vane_mat"]
    p = vm.node_tree.nodes["Principled BSDF"]
    p.inputs["Emission Color"].default_value = (1.0, 0.1, 0.05, 1)
    for f, s in ((1, 0.0), (fv + 2, 0.0), (fv + 6, 1.2), (n, 0.6)):
        p.inputs["Emission Strength"].default_value = s
        p.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
    bz = 4.0 - 1.78
    hx = -14.0 + 0.55
    outline = M.glow_poly([(hx - 0.12, -0.92, bz + 0.02), (hx + 0.12, -0.92, bz + 0.02), (hx + 0.12, -0.92, bz - 0.6),
                           (hx - 0.12, -0.92, bz - 0.6)], color=(1.0, 0.08, 0.04), strength=10, bevel=0.008, name="outline", closed=True)
    M.curve_draw(outline, fv + 2, fv + 16)
    blue = []
    for k in range(4):
        z = bz - 0.15 - k * 0.15
        b = M.glow_poly([(hx + 1.6, -0.95, z), (hx - 1.6, -0.95, z)], color=(0.3, 0.65, 1.0), strength=3, bevel=0.004, name=f"bp{k}")
        em = [nd for nd in b.data.materials[0].node_tree.nodes if nd.type == "EMISSION"][0].inputs[1]
        for f, s in ((1, 3.0), (fv + 4, 3.0), (fv + 20, 0.0)):
            em.default_value = s
            em.keyframe_insert("default_value", frame=f)
    L.spot((hx, -3, bz - 1.0), (R(70), 0, 0), energy=35, size_deg=40, blend=0.6, color=(0.8, 0.88, 1.0), name="macrokey")
    cam, ct = cam_path(L, n, (hx + 0.9, -4.6, bz - 0.9), (hx + 0.5, -3.3, bz - 0.6), (hx, -0.75, bz - 0.25), (hx, -0.75, bz - 0.25),
                       lens=85)
    L.dof(cam, distance=3.4, fstop=2.8)
    cam.data.dof.focus_distance = 3.9
    cam.data.dof.keyframe_insert("focus_distance", frame=1)
    cam.data.dof.focus_distance = 2.65
    cam.data.dof.keyframe_insert("focus_distance", frame=12)
    L.bake_static()


# ============================================================================= S20 case-file desk (document plate)

def S20(L, n):
    L.set_world(color=(0.003, 0.003, 0.004), strength=1.0)
    M.desk(size=(3, 2))
    fold = L.prim("cube", loc=(0.05, 0.1, 0.01), name="folder")
    fold.scale = (0.24, 0.31, 0.008)
    fold.rotation_euler = (0, 0, R(-5))
    L.assign(fold, M.mat_paper("manila", (0.55, 0.42, 0.22)))
    tab = L.prim("cube", loc=(0.2, 0.43, 0.01))
    tab.scale = (0.07, 0.03, 0.008)
    tab.rotation_euler = (0, 0, R(-5))
    L.assign(tab, M.mat_paper("manila2", (0.55, 0.42, 0.22)))
    lbl = L.text3d("NORJAK", loc=(0.05, 0.2, 0.02), rot=(0, 0, R(-5)), size=0.06, extrude=0,
                   mat=L.mat_principled("lblink", (0.05, 0.04, 0.03)), name="lbl")
    lbl.data.font = M._font(M.F_MONO) or lbl.data.font
    M.book((-0.45, 0.25, 0), size=(0.16, 0.24, 0.03), rot_z=R(15), name="ledger")
    M.desk_lamp((0.55, 0.6, 0), (0.05, 0.1, 0), energy=45, rot_z=R(150))
    cam, ct = cam_path(L, n, (0.0, -0.55, 0.85), (0.02, -0.42, 0.75), (0.05, 0.12, 0), (0.05, 0.12, 0), lens=35)
    L.bake_static()


# ============================================================================= S21 suspect wall

def S21(L, n):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0)
    wall = L.prim("plane", loc=(0, 0.03, 0), size=1, rot=(R(90), 0, 0))
    wall.scale = (40, 30, 1)
    L.assign(wall, L.mat_noise_surface("wallm", (0.015, 0.015, 0.017), (0.04, 0.04, 0.045), scale=5, bump=0.2, voronoi=False))
    M.suspect_wall(cols=30, rows=18, origin=(0, 0, 3.2), seed=3)
    L.spot((0, -9, 9), (R(42), 0, 0), energy=4500, size_deg=70, blend=0.7, color=(0.75, 0.85, 1.0), name="coldlamp", radius=0.3)
    L.point((0, -2.5, 4.5), energy=70, color=(0.8, 0.88, 1.0), radius=0.4, name="near")
    cam, ct = cam_path(L, n, (0.25, -1.1, 4.0), (0.0, -14.0, 3.6), (0.25, 0, 4.1), (0.0, 0, 3.2), lens=24)
    L.particle_cloud((0, -3, 4), (6, 4, 4), count=300, radius=0.004, drift=(0.01, 0, -0.01), nframes=n, name="dust")
    L.bake_static()


# ============================================================================= S22 dawn forest, open question

def S22(L, n):
    M.dawn_sky(hor=(0.5, 0.45, 0.45), mid=(0.22, 0.25, 0.32), zen=(0.06, 0.08, 0.14), strength=2.5, sun_dir=(0.6, 0.8, 0.1))
    bpy.context.scene.eevee.use_volumetric_shadows = False
    L.sun(rot=(R(72), 0, R(-160)), energy=4.0, color=(1.0, 0.78, 0.6), angle=2, name="dawnsun")
    L.sun(rot=(R(20), 0, R(30)), energy=0.8, color=(0.6, 0.7, 0.9), angle=20, name="skyfill")
    def h(x, y):
        return 1.5 * noise.noise(Vector((x * 0.03, y * 0.03, 7))) + 0.15 * noise.noise(Vector((x * 0.4, y * 0.4, 2)))
    prints = M.trail((0.0, -2.0), (0.4, 3.0), step=0.6, gap=0.12, seed=4, rx=0.06, ry=0.14, depth=0.03)
    M.heightfield("floor", -12, 12, -10, 14, 160, 160, h, prints=prints,
                  mat=L.mat_noise_surface("floorm", (0.04, 0.04, 0.03), (0.12, 0.11, 0.08), scale=3, bump=0.3, voronoi=False))
    M.heightfield("floorfar", -150, 150, -150, 250, 80, 80, lambda x, y: h(x, y) - 0.05,
                  mat=L.mat_noise_surface("floorm2", (0.03, 0.035, 0.025), (0.08, 0.08, 0.06), scale=1, bump=0.3, voronoi=False))
    tm = M.mat_dusted("trees", base=(0.015, 0.03, 0.02), snow=(0.04, 0.06, 0.045))
    spots = M.scatter_spots((-60, 60, -20, 120), 700, h, seed=8, h=(14, 24), exclude=lambda x, y: math.hypot(x, y - 1) < 7)
    spots += M.scatter_spots((-150, 150, 120, 250), 900, h, seed=9, h=(14, 24))
    M.fast_conifers("forest", spots, mat=tm, seed=8, bare_frac=0.05)
    forest_floor("ferns", h, (-9, 9, -6, 10), count=280, seed=6)
    L.fog_volume(center=(0, 30, 3), size=(80, 70, 6), density=0.03, color=(0.8, 0.8, 0.85))
    cam, ct = L.camera(loc=(0, -6.5, 0.7), target=(0.2, 3, 0.4), lens=24)
    cam.data.clip_end = 3000
    fq = int(n * 0.58)
    for f, p in ((1, (0, -6.5, 0.7)), (fq, (0.1, -3.6, 0.75)), (n, (0.2, -1.5, 26))):
        cam.location = p
        cam.keyframe_insert("location", frame=f)
    for f, p in ((1, (0.2, 3, 0.3)), (fq, (0.3, 3.5, 0.2)), (n, (0.5, 80, 16))):
        ct.location = p
        ct.keyframe_insert("location", frame=f)
    L.bake_static()
