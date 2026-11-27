"""HAUNT-01 — The Voice on the Enfield Tapes. One builder per shot: def Sxx(L, n)."""
import importlib, sys, os, math
_LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PIPELINE", "blender")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import lib_haunted as H
importlib.reload(H)

BC = H.BEDROOM_CAM


def _push_end(frac):
    return tuple(BC["start"][i] + (BC["end"][i] - BC["start"][i]) * frac for i in range(3))


# --------------------------------------------------------------------------- S01 cold open: bedroom push-in
def S01(L, n):
    H.eevee_quality()
    L.set_world((0.004, 0.006, 0.012), 1.0)
    H.enfield_bedroom(n, chair="A", rec_on=True)
    H.bedroom_camera(n, "push")
    L.bake_static()


# --------------------------------------------------------------------------- S02 street exterior
def _street(L, n, lit=("U1",), open_win=None):
    H.eevee_quality(raytrace=True)
    L.set_world((0.012, 0.018, 0.035), 1.0)
    road = L.prim("plane", loc=(0, -4.5, 0.0), size=1)
    road.scale = (80, 9, 1)
    L.assign(road, H.mat_wet_road())
    pave = H.box_mesh("pavement", [(0, -0.0 - 3.3 - 1.0, 0.07, 40, 1.0, 0.07), (0, -10.0, 0.07, 40, 1.0, 0.07)],
                      L.mat_noise_surface("pave", (0.1, 0.1, 0.1), (0.2, 0.2, 0.19), scale=6, bump=0.2, rough=0.4))
    H.box_mesh("kerb", [(0, -5.3, 0.08, 40, 0.06, 0.08), (0, -9.0, 0.08, 40, 0.06, 0.08)], L.CONCRETE())
    houses = []
    bricks = [H.mat_brick("brickA", wet=True), H.mat_brick("brickB", c1=(0.3, 0.13, 0.07), c2=(0.42, 0.2, 0.1), wet=True)]
    for i, x in enumerate((-11.0, 0.0, 11.0)):
        houses.append(H.semi_pair(f"semi{i}", (x, 0, 0), lit=(lit if i == 1 else (("U3",) if i == 0 else ())),
                                  open_win=(open_win if i == 1 else None), brick=bricks[i % 2], seed=i))
    lamp = H.streetlamp((1.6, -4.9, 0), height=5.5, energy=5000, face=math.pi, arm=1.0)
    H.streetlamp((-17.0, -4.9, 0), height=5.5, energy=500, face=math.pi, arm=1.0, name="slamp2")
    # back-row rooftops / sky glow
    L.sun(rot=(0.9, 0.0, 2.6), energy=0.25, color=(0.5, 0.6, 1.0), angle=8)
    L.fog_volume(center=(0, 0, 4), size=(70, 36, 9), density=0.018, color=(0.75, 0.72, 0.8))
    return houses, lamp


def S02(L, n):
    houses, lamp = _street(L, n)
    H.rain((1.0, -9.0, 3.0), (14, 8, 6), n, count=1800, speed=7, emit=0.35)
    c = H.cam((-3.4, -14.0, 0.8), (-2.0, 0, 1.9), lens=35)
    H.cam_move(c, [(1, (-3.4, -14.0, 0.8), (-2.0, 0, 1.9)), (n, (-0.9, -14.0, 0.85), (0.3, 0, 1.9))], ease=False)
    H.handheld(c, n, amp=0.015, rate=0.4)
    L.bake_static()


# --------------------------------------------------------------------------- S03 the house: mother on the phone
def S03(L, n):
    houses, lamp = _street(L, n, lit=("U1",), open_win="D0")
    # interior behind the downstairs-left window D0 (x=-3.0 in house 1)
    wx = -3.0
    H.box_mesh("int_back", [(wx, 2.6, 1.5, 2.0, 0.05, 1.5)], H.mat_wallpaper("wp_hall", base=(0.45, 0.33, 0.18), stripe=(0.35, 0.25, 0.12),
                                                                            flower=(0.55, 0.3, 0.12)))
    H.box_mesh("int_sides", [(wx - 1.6, 1.4, 1.5, 0.05, 1.2, 1.5), (wx + 1.6, 1.4, 1.5, 0.05, 1.2, 1.5), (wx, 1.4, 2.7, 1.6, 1.2, 0.05),
                             (wx, 1.4, 0.0, 1.6, 1.2, 0.05)], L.mat_principled("int_m", (0.35, 0.27, 0.17), rough=0.8))
    L.point((wx + 0.3, 2.2, 2.3), energy=260, color=(1.0, 0.68, 0.38), radius=0.3, name="hall_warm")
    L.area((wx, 2.45, 1.4), (math.pi / 2, 0, 0), energy=90, size=2.0, color=(1.0, 0.7, 0.4), name="backglow")
    m = H.figure("mother", height=1.62, coat=True)
    m["root"].location = (wx + 0.25, 1.15, 0)
    m["root"].rotation_euler = (0, 0, math.radians(200))
    H.pose_hold(m, "R", shoulder=(-2.3, 0.0, -0.35), elbow=(-1.9, 0, 0))
    hs = L.prim("cyl", loc=(0, 0, 0), vertices=10, radius=0.025, depth=0.22)
    L.assign(hs, m["torso"].data.materials[0])
    hs.parent = m["neck"]
    hs.location = (0.11, 0.03, 0.12)
    hs.rotation_euler = (0.2, 0, 0)
    tb = H.box_mesh("phone_table", [(wx - 0.35, 1.25, 0.4, 0.22, 0.18, 0.4)], L.mat_principled("pt", (0.08, 0.05, 0.03)))
    H.telephone((wx - 0.35, 1.25, 0.8))
    cord = L.guideline([(wx - 0.3, 1.2, 0.86), (wx - 0.05, 1.18, 1.0), (wx + 0.2, 1.15, 1.25), (wx + 0.33, 1.12, 1.45)],
                       mat=L.mat_principled("cordm", (0.01, 0.01, 0.01)), thickness=0.008, name="cord")
    # net curtain across the window
    net = H.curtain("net", wx, 1.62, 1.28, 2.08, axis="x", fixed=0.12, folds=10, depth=0.02, mat=H.mat_net_curtain(alpha=0.3, emit=0.1))
    p0, t0 = (-2.3, -9.0, 1.6), (-2.3, 0.0, 1.85)
    c = H.cam(p0, t0, lens=50)
    H.cam_move(c, [(1, p0, t0), (int(n * 0.35), p0, t0), (n, (-2.35, -8.55, 1.6), (-2.4, 0.0, 1.8))])
    H.handheld(c, n, amp=0.006, rate=0.3)
    H.rain((-2.0, -6.0, 3.0), (8, 6, 6), n, count=900, speed=7, emit=0.3)
    L.bake_static()


# --------------------------------------------------------------------------- S04 living room: the sliding chair
def S04(L, n):
    H.eevee_quality()
    L.set_world((0.004, 0.004, 0.006), 1.0)
    W, D, Hh = 4.2, 4.6, 2.45
    wp = H.mat_wallpaper("wp_liv", base=(0.22, 0.25, 0.14), stripe=(0.16, 0.18, 0.09), flower=(0.42, 0.33, 0.14), leaf=(0.3, 0.2, 0.08),
                         freq=3.0, fscale=4.0)
    fl = L.prim("plane", loc=(0, 0, 0), size=1)
    fl.scale = (W + 0.4, D + 0.4, 1)
    L.assign(fl, H.mat_carpet("carpet_liv", (0.12, 0.05, 0.02), (0.26, 0.12, 0.04)))
    cl = L.prim("plane", loc=(0, 0, Hh), size=1, rot=(math.pi, 0, 0))
    cl.scale = (W + 0.4, D + 0.4, 1)
    L.assign(cl, L.mat_principled("ceil2", (0.4, 0.38, 0.34)))
    door = (0.9, 0.85, 0.0, 2.02)
    H.wall_with_openings("lwN", "x", D / 2, W + 0.2, Hh, [], mat=wp, outward=1)
    H.wall_with_openings("lwS", "x", -D / 2, W + 0.2, Hh, [], mat=wp, outward=-1)
    H.wall_with_openings("lwW", "y", -W / 2, D, Hh, [door], mat=wp, outward=-1)
    H.wall_with_openings("lwE", "y", W / 2, D, Hh, [(0.3, 1.4, 0.9, 2.0)], mat=wp, outward=1)
    trim = L.mat_principled("trim", (0.55, 0.52, 0.46), rough=0.5)
    H.window_frame("lwin", "y", W / 2 + 0.05, 0.3, 1.4, 0.9, 2.0, mat=trim)
    H.curtain("lcurt1", -0.3, 0.5, 1.3, 2.15, axis="y", fixed=W / 2 - 0.08, folds=4, mat=L.mat_principled("lc", (0.3, 0.12, 0.05), rough=1))
    H.curtain("lcurt2", 0.95, 0.5, 1.3, 2.15, axis="y", fixed=W / 2 - 0.08, folds=4, mat=L.mat_principled("lc2", (0.3, 0.12, 0.05), rough=1))
    # doorway frame + hall behind (bright, the officer is back-lit)
    H.box_mesh("dframe", [(-W / 2, door[0] - door[1] / 2 - 0.04, 1.02, 0.08, 0.04, 1.02), (-W / 2, door[0] + door[1] / 2 + 0.04, 1.02, 0.08, 0.04, 1.02),
                          (-W / 2, door[0], 2.06, 0.08, door[1] / 2 + 0.08, 0.04)], trim)
    H.box_mesh("hall", [(-W / 2 - 1.3, door[0], 0.0, 1.2, 1.2, 0.02), (-W / 2 - 2.5, door[0], 1.3, 0.05, 1.2, 1.3),
                        (-W / 2 - 1.3, door[0] + 1.2, 1.3, 1.2, 0.05, 1.3), (-W / 2 - 1.3, door[0] - 1.2, 1.3, 1.2, 0.05, 1.3)],
                L.mat_principled("hallw", (0.5, 0.42, 0.3), rough=0.8))
    L.area((-W / 2 - 1.6, door[0], 2.3), (0, 0, 0), energy=500, size=1.2, color=(0.85, 0.85, 1.0), name="hallkey")
    L.point((-W / 2 - 0.9, door[0], 1.4), energy=120, color=(0.8, 0.85, 1.0), radius=0.5, name="hallrim")
    off = H.figure("officer", height=1.85, cap=True)
    off["root"].location = (-W / 2 - 0.25, door[0], 0)
    off["root"].rotation_euler = (0, 0, math.radians(-75))
    H.pose_hold(off, "L", shoulder=(0, 0, 0.05))
    # sofa (bed prop with low back) against the north wall, TV in the corner
    sofa_m = L.mat_noise_surface("sofa_m", (0.18, 0.1, 0.04), (0.3, 0.18, 0.07), scale=30, bump=0.2, voronoi=False, rough=1)
    H.box_mesh("sofa", [(0.3, D / 2 - 0.5, 0.22, 1.0, 0.42, 0.22), (0.3, D / 2 - 0.15, 0.6, 1.0, 0.13, 0.32),
                        (-0.72, D / 2 - 0.5, 0.42, 0.13, 0.42, 0.2), (1.32, D / 2 - 0.5, 0.42, 0.13, 0.42, 0.2)], sofa_m, bevel=0.04)
    tvm = L.mat_principled("tv", (0.05, 0.035, 0.02), rough=0.5)
    H.box_mesh("tv", [(W / 2 - 0.45, D / 2 - 0.45, 0.55, 0.33, 0.3, 0.27), (W / 2 - 0.45, D / 2 - 0.45, 0.14, 0.3, 0.27, 0.14)], tvm)
    H.box_mesh("tvscreen", [(W / 2 - 0.56, D / 2 - 0.75, 0.58, 0.2, 0.005, 0.17, -0.0)], L.mat_principled("tvs", (0.03, 0.04, 0.04), rough=0.1))
    H.box_mesh("rug2", [(0.0, 0.0, 0.006, 1.2, 0.9, 0.006)], L.mat_noise_surface("rug2m", (0.25, 0.18, 0.08), (0.4, 0.3, 0.12), scale=25, bump=0.1, voronoi=False))
    # pendant bulb (flickers twice)
    H.box_mesh("flex", [(0, 0, Hh - 0.25, 0.005, 0.005, 0.25)], L.mat_principled("flexm", (0.02, 0.02, 0.02)))
    bulb_m = L.mat_emission("bulb", (1.0, 0.8, 0.55), 18)
    bulb = L.prim("sphere", loc=(0, 0, Hh - 0.55), segments=16, ring_count=10, radius=0.045)
    L.assign(bulb, bulb_m)
    shade = L.prim("cone", loc=(0, 0, Hh - 0.5), vertices=20, radius1=0.2, radius2=0.06, depth=0.16, end_fill_type="NOTHING")
    L.assign(shade, L.mat_principled("pshade", (0.5, 0.36, 0.2), rough=1, emit=(1, 0.7, 0.4), emit_strength=0.6))
    bl = L.point((0, 0, Hh - 0.62), energy=110, color=(1.0, 0.75, 0.48), radius=0.05, name="bulb_l")
    # flicker: steady with two short dips
    dips = [(int(n * 0.28), int(n * 0.28) + 3), (int(n * 0.66), int(n * 0.66) + 4)]
    pairs_l, pairs_m = [], []
    for f in range(1, n + 1):
        k = 1.0
        for a, b in dips:
            if a <= f <= b:
                k = 0.08 if (f - a) % 2 == 0 else 0.35
        pairs_l.append((f, 110 * k))
        pairs_m.append((f, 18 * k))
    H.key_energy(bl, pairs_l)
    H.key_emission(bulb_m, pairs_m)
    # the chair slides ~1.1 m by itself, slow and smooth
    ch = H.wood_chair((0.75, -0.3, 0), math.radians(20))
    r = ch["root"]
    s0 = int(n * 0.14)
    r.keyframe_insert("location", frame=1)
    r.keyframe_insert("rotation_euler", frame=1)
    r.keyframe_insert("location", frame=s0)
    r.keyframe_insert("rotation_euler", frame=s0)
    r.location = (-0.35, -0.05, 0)
    r.rotation_euler = (0, 0, math.radians(-5))
    r.keyframe_insert("location", frame=n - 6)
    r.keyframe_insert("rotation_euler", frame=n - 6)
    H.dust((0, 0, 1.2), (3, 3, 2), n, count=120, radius=0.0025, emit=0.03)
    H.room_fog((0, 0, Hh / 2), (W, D, Hh), density=0.02, color=(0.8, 0.75, 0.7))
    c = H.cam((1.75, -2.15, 1.55), (-0.45, 0.6, 0.75), lens=24)
    L.cam_light(c, energy=15, color=(0.8, 0.85, 1.0))
    L.bake_static()


# --------------------------------------------------------------------------- S05 hallway: the investigators arrive
def S05(L, n):
    H.eevee_quality()
    L.set_world((0.004, 0.005, 0.008), 1.0)
    W, D, Hh = 1.9, 5.0, 2.5
    wp = H.mat_wallpaper("wp_hallw", base=(0.4, 0.3, 0.17), stripe=(0.3, 0.21, 0.11), flower=(0.5, 0.25, 0.1), freq=4.5)
    fl = L.prim("plane", loc=(0, 0, 0), size=1)
    fl.scale = (W + 0.4, D + 0.4, 1)
    L.assign(fl, H.mat_carpet("carpet_h", (0.1, 0.04, 0.03), (0.22, 0.09, 0.05)))
    cl = L.prim("plane", loc=(0, 0, Hh), size=1, rot=(math.pi, 0, 0))
    cl.scale = (W + 0.4, D + 0.4, 1)
    L.assign(cl, L.mat_principled("ceil3", (0.4, 0.38, 0.34)))
    door = (-0.2, 0.9, 0.0, 2.05)
    H.wall_with_openings("hwN", "x", D / 2, W + 0.2, Hh, [door], mat=wp, outward=1)
    H.wall_with_openings("hwW", "y", -W / 2, D, Hh, [], mat=wp, outward=-1)
    H.wall_with_openings("hwE", "y", W / 2, D, Hh, [], mat=wp, outward=1)
    trim = L.mat_principled("trimh", (0.6, 0.57, 0.5), rough=0.5)
    # open front door swung inward against the west wall
    H.door_slab("frontdoor", (door[0] - 0.45, D / 2 - 0.02, 0), width=0.88, height=2.02, angle=-math.radians(105),
                mat=L.mat_principled("fdoor", (0.3, 0.07, 0.05), rough=0.5))
    # stairs along the east wall rising toward camera (foreground right)
    st_m = L.mat_principled("stairs", (0.2, 0.12, 0.06), rough=0.6)
    steps = []
    for k in range(5):
        y = -1.5 - k * 0.26
        top = 0.2 * (k + 1)
        steps.append((W / 2 - 0.42, y, top / 2, 0.42, 0.13, top / 2))
    H.box_mesh("stairs", steps, st_m)
    H.box_mesh("banister", [(W / 2 - 0.86, -1.5 - k * 0.26, 0.2 * (k + 1) + 0.45, 0.018, 0.018, 0.45) for k in range(0, 5)] +
               [(W / 2 - 0.86, -1.42, 0.55, 0.045, 0.045, 0.55)], trim)
    # outside: cold street light, fog spilling in
    H.box_mesh("outside", [(0, D / 2 + 4.0, 2.0, 5.0, 0.1, 3.0)], L.mat_emission("nightout", (0.06, 0.09, 0.16), 1.0))
    H.box_mesh("outground", [(0, D / 2 + 2.0, -0.01, 5, 2.0, 0.01)], L.mat_principled("og", (0.05, 0.05, 0.06), rough=0.3))
    L.prim("sphere", loc=(1.5, D / 2 + 3.8, 3.2), radius=0.12, segments=12, ring_count=8)
    L.assign(bpy_last(), L.mat_emission("farlamp", (1.0, 0.55, 0.2), 25))
    L.spot((door[0], D / 2 + 2.2, 2.6), (0, 0, 0), energy=900, size_deg=50, blend=0.6, color=(0.6, 0.72, 1.0), name="streetcold")
    sc = [o for o in __import__("bpy").data.objects if o.name == "streetcold"][0]
    H.aim(sc, (door[0], D / 2 + 2.2, 2.6), (door[0], 0.0, 0.0))
    H.room_fog((door[0], D / 2 + 0.2, 1.2), (2.4, 3.0, 2.4), density=0.12, color=(0.7, 0.8, 1.0), name="fogspill")
    H.room_fog((0, 0, Hh / 2), (W, D, Hh), density=0.02, color=(0.8, 0.75, 0.7), name="hallfog")
    # warm hall bulb
    hb_m = L.mat_emission("hbulb", (1.0, 0.8, 0.55), 15)
    hb = L.prim("sphere", loc=(-0.1, 0.3, Hh - 0.4), segments=12, ring_count=8, radius=0.04)
    L.assign(hb, hb_m)
    L.point((-0.1, 0.3, Hh - 0.5), energy=60, color=(1.0, 0.72, 0.45), radius=0.05, name="hbulb_l")
    # investigators enter (walk toward camera)
    a = H.figure("invA", height=1.88, coat=True)
    b = H.figure("invB", height=1.76, coat=False)
    for p in (a, b):
        p["root"].rotation_euler = (0, 0, math.pi)
    H.walk(a, 1, n, stride=0.42, rate=0.9, travel=((door[0] - 0.05, D / 2 + 0.6, 0), (door[0] - 0.15, 0.2, 0)))
    H.walk(b, 1, n, stride=0.4, rate=0.95, travel=((door[0] + 0.2, D / 2 + 1.8, 0), (door[0] + 0.25, 1.4, 0)), skip=("armR",))
    H.pose_hold(b, "R", shoulder=(0.12, 0, 0.12), elbow=(0, 0, 0))
    rec = H.tape_recorder((0, 0, 0), 0, n=n, rec_on=False, name="carried")
    rec["root"].parent = b["elbowR"]
    rec["root"].location = (0.04, 0.0, -0.58)
    rec["root"].rotation_euler = (0, 0, math.pi / 2)
    H.box_mesh("handle", [(0, 0, 0.17, 0.01, 0.08, 0.05)], L.mat_principled("hdl", (0.02, 0.02, 0.02)), parent=rec["root"])
    c = H.cam((0.5, -2.2, 1.02), (-0.15, 2.5, 1.45), lens=28)
    H.cam_move(c, [(1, (0.5, -2.2, 1.02), (-0.15, 2.5, 1.45)), (n, (0.45, -2.1, 1.0), (-0.2, 2.5, 1.35))])
    H.handheld(c, n, amp=0.012, rate=0.5)
    L.cam_light(c, energy=10, color=(0.9, 0.85, 0.8))
    H.dust((0, 1.0, 1.2), (1.8, 3.5, 2.0), n, count=400, emit=0.1)
    L.bake_static()


def bpy_last():
    import bpy
    return bpy.context.active_object


# --------------------------------------------------------------------------- S06 macro: the recorder
def S06(L, n):
    H.eevee_quality()
    L.set_world((0.004, 0.006, 0.012), 1.0)
    set_ = H.enfield_bedroom(n, chair="A", rec_on=True, fog=True, dust_count=500)
    rc = (0.25, 1.5, 0.6)
    keys = []
    for f, th in ((1, -80), (n, -58)):
        a = math.radians(th)
        keys.append((f, (rc[0] + 0.8 * math.cos(a), rc[1] + 0.8 * math.sin(a), rc[2] + 0.72), (rc[0], rc[1] + 0.0, rc[2] - 0.1)))
    c = H.cam(keys[0][1], keys[0][2], lens=70)
    H.cam_move(c, keys, ease=False)
    L.dof(c, distance=1.07, fstop=2.2)
    L.cam_light(c, energy=6, color=(0.6, 0.7, 1.0), size_deg=40)
    L.spot((rc[0] + 0.6, rc[1] + 0.25, 1.4), (0, 0, 0), energy=25, size_deg=50, blend=1, color=(0.55, 0.68, 1.0), name="rim")
    rim = [o for o in __import__("bpy").data.objects if o.name == "rim"][0]
    H.aim(rim, (rc[0] + 0.6, rc[1] + 0.25, 1.4), rc)
    H.dust(rc, (0.8, 0.6, 0.5), n, count=250, radius=0.0015, emit=0.15, name="macrodust")
    L.bake_static()


# --------------------------------------------------------------------------- S07 the bedroom after: toppled, flicker
def S07(L, n):
    H.eevee_quality()
    L.set_world((0.004, 0.006, 0.012), 1.0)
    s = H.enfield_bedroom(n, chair="toppled", rec_on=True, lamp_on=True, lamp_energy=30, toppled=True, moon=0.8)
    H.flicker_lamp(s["lamp"], n, 30, 1.6, seed=5, depth=0.55, rate=0.5, blackouts=((12, 16), (22, 27)))
    st, tg = (0.55, -2.0, 1.15), (-0.05, 1.0, 0.6)
    c = H.cam(st, (-1.7, -0.4, 1.4), lens=22)
    H.cam_move(c, [(1, st, (-1.7, -0.4, 1.4)), (6, st, tg), (n, (0.35, -1.6, 1.05), (0.0, 1.2, 0.6))])
    H.handheld(c, n, amp=0.02, rate=0.7, rot_amp=0.012)
    L.cam_light(c, energy=30, color=(0.65, 0.75, 1.0), size_deg=80)
    L.bake_static()


# --------------------------------------------------------------------------- S08 waveform graphic
def S08(L, n):
    import bpy
    L.set_world((0, 0, 0), 0)
    wf = H.waveform_curve("wave", length=16, pts=900, amp=0.42, z=0.35, thickness=0.009, strength=9,
                          bursts=((0.18, 0.42), (0.5, 0.7), (0.78, 0.95)))
    glow = H.waveform_curve("waveglow", length=16, pts=900, amp=0.42, z=0.35, y=0.02, thickness=0.02, strength=0.5,
                            bursts=((0.18, 0.42), (0.5, 0.7), (0.78, 0.95)))
    for o in (wf, glow):
        o.location = (-0.9, 0, 0)
        o.keyframe_insert("location", frame=1)
        o.location = (-0.9 - 1.45 * n / 24.0, 0, 0)
        o.keyframe_insert("location", frame=n)
        L.linear_fcurves(o)
    grid_m = L.mat_emission("grid", (0.3, 0.7, 0.4), 0.18)
    lines = []
    for k in range(-6, 7):
        lines.append((k * 0.25, 0.05, 0.35, 0.002, 0.002, 1.3))
    for k in range(-5, 6):
        lines.append((0, 0.05, 0.35 + k * 0.25, 1.0, 0.002, 0.002))
    lines.append((0, 0.05, 0.35, 1.0, 0.002, 0.004))
    H.box_mesh("grid", lines, grid_m)
    # scanline sweep
    sm = L.mat_emission("scan", (0.5, 1.0, 0.6), 0.6)
    sl = H.box_mesh("scanline", [(0, -0.02, 0, 1.0, 0.001, 0.01)], sm)
    sl.location = (0, 0, 1.7)
    sl.keyframe_insert("location", frame=1)
    sl.location = (0, 0, -1.2)
    sl.keyframe_insert("location", frame=n)
    L.linear_fcurves(sl)
    # the girl's bed, barely visible behind
    bed = H.single_bed((0.15, 4.0, -1.35), math.radians(80), name="ghostbed")
    L.spot((1.8, 2.6, 1.0), (0, 0, 0), energy=25, size_deg=60, blend=1, color=(0.5, 1.0, 0.6), name="bedrim")
    br = bpy.data.objects["bedrim"]
    H.aim(br, (1.8, 2.6, 1.0), (0.15, 4.0, -1.0))
    c = H.cam((0, -3.6, 0.15), (0, 0, 0.2), lens=46)
    c.data.keyframe_insert("lens", frame=1)
    c.data.lens = 52
    c.data.keyframe_insert("lens", frame=n)
    L.dof(c, distance=3.6, fstop=4)
    L.bake_static()


# --------------------------------------------------------------------------- S09 the shadow of the chair
def S09(L, n):
    import bpy
    H.eevee_quality()
    L.set_world((0.003, 0.004, 0.008), 1.0)
    s = H.enfield_bedroom(n, chair="A", rec_on=True, moon=0.45, jumper=True, dust_count=500)
    # 'bedside lamp low': a lamp knocked to the floor by the left bed, throwing the chair's shadow onto the east wall
    lp = H.bedside_lamp((-1.05, 1.35, 0.55), on=True, energy=0.0, name="lowlamp")
    lp["root"].rotation_euler = (0, math.radians(-70), 0.1)
    key = L.spot((-1.15, 1.12, 0.72), (0, 0, 0), energy=280, size_deg=70, blend=0.35, color=(1.0, 0.7, 0.4), name="lowkey", radius=0.015)
    H.aim(key, (-1.15, 1.12, 0.72), (1.65, 1.0, 1.3))
    H.flicker_lamp({"light": key, "shade_mat": lp["shade_mat"]}, n, 280, 1.6, seed=9, depth=0.12, rate=0.2)
    st, tg0, tg1 = (-1.45, -1.62, 2.28), (1.0, 0.9, 1.75), (1.0, 0.9, 1.4)
    c = H.cam(st, tg0, lens=20)
    H.cam_move(c, [(1, st, tg0), (n, (-1.4, -1.55, 2.25), tg1)])
    L.cam_light(c, energy=10, color=(0.65, 0.75, 1.0), size_deg=80)
    L.bake_static()


# --------------------------------------------------------------------------- S10 / S11 evidence board
def _board(L, n, slide=True):
    import bpy
    H.eevee_quality()
    L.set_world((0.01, 0.01, 0.012), 1.0)
    H.box_mesh("bwall", [(0, 0.2, 0, 4, 0.05, 4)], L.mat_principled("bw", (0.05, 0.05, 0.055), rough=0.9))
    H.evidence_board("board", 2.4, 4.0)
    ink = L.mat_principled("ink2", (0.04, 0.035, 0.03), rough=0.6)
    H.pinned_card("c_hdr", (0.0, -0.01, 1.3), 1.45, 0.36, [], header="WHAT SCEPTICS SAY", size=0.1, font_size_header=0.125,
                  color=(0.86, 0.83, 0.72), rot=math.radians(-1.5))
    sp = H.pinned_card("c_spoon", (-0.08, -0.012, 0.33), 1.1, 1.0, ["caught on camera,", "next room"], size=0.085, rot=math.radians(2.5))
    L.guideline([(-0.38, -0.009, -0.4), (0.0, -0.009, -0.2), (0.12, -0.009, -0.03)], mat=ink, thickness=0.02, name="spoon_handle").parent = sp
    bowl = L.prim("sphere", loc=(0.17, -0.01, 0.07), segments=16, ring_count=8, radius=0.1, rot=(0, math.radians(-28), 0))
    bowl.scale = (0.62, 0.05, 1.05)
    L.assign(bowl, ink)
    bowl.parent = sp
    vc = H.pinned_card("c_vent", (0.12, -0.012, -0.72), 1.15, 0.78, ["VENTRILOQUISM?"], size=0.11, rot=math.radians(-2),
                       color=(0.86, 0.83, 0.7))
    head = L.prim("sphere", loc=(-0.24, -0.01, -0.12), segments=16, ring_count=8, radius=0.11)
    head.scale = (0.85, 0.05, 1.0)
    L.assign(head, ink)
    head.parent = vc
    H.box_mesh("neckic", [(-0.26, -0.008, -0.27, 0.05, 0.002, 0.07)], ink, parent=vc)
    redm = L.mat_principled("wv", (0.6, 0.05, 0.04), rough=0.6)
    for k in range(3):
        r = 0.08 + k * 0.065
        pts = [(-0.1 + r * math.cos(a), -0.01, -0.13 + r * math.sin(a)) for a in [math.radians(-50 + 10 * j) for j in range(11)]]
        L.guideline(pts, mat=redm, thickness=0.012, name=f"wave{k}").parent = vc
    red = L.mat_principled("string", (0.6, 0.02, 0.02), rough=0.5)
    L.guideline([(0.0, -0.05, 1.43), (-0.08, -0.05, 0.78)], mat=red, thickness=0.005, name="str1")
    L.guideline([(-0.08, -0.05, 0.78), (0.12, -0.05, -0.38)], mat=red, thickness=0.005, name="str2")
    H.box_mesh("scraps", [(0.95, -0.006, 0.55, 0.2, 0.002, 0.26, 0.1), (-0.95, -0.006, -0.5, 0.22, 0.002, 0.16, -0.08),
                          (-0.85, -0.006, 1.0, 0.2, 0.002, 0.15, 0.05), (0.9, -0.006, -1.4, 0.25, 0.002, 0.2, -0.05)],
               H.mat_paper("scrap", (0.6, 0.57, 0.48)))
    H.box_mesh("photos", [(0.95, -0.009, 0.55, 0.15, 0.002, 0.19, 0.1), (-0.85, -0.009, 1.0, 0.14, 0.002, 0.1, 0.05)],
               L.mat_principled("photo", (0.07, 0.07, 0.07), rough=0.3))
    if slide:
        tgt = tuple(sp.location)
        sp.location = (tgt[0] + 2.4, tgt[1], tgt[2] + 0.1)
        sp.keyframe_insert("location", frame=1)
        sp.keyframe_insert("location", frame=5)
        sp.location = tgt
        sp.keyframe_insert("location", frame=13)
        sp.rotation_euler = (0, math.radians(-8), 0)
        sp.keyframe_insert("rotation_euler", frame=5)
        sp.rotation_euler = (0, math.radians(2.5), 0)
        sp.keyframe_insert("rotation_euler", frame=16)
    k = L.spot((-2.2, -1.8, 3.2), (0, 0, 0), energy=1000, size_deg=50, blend=0.5, color=(1.0, 0.78, 0.5), name="desklamp", radius=0.1)
    H.aim(k, (-2.2, -1.8, 3.2), (0.1, 0, 0.3))
    L.area((0, -3, 0.5), (math.pi / 2, 0, 0), energy=8, size=3, color=(0.6, 0.7, 0.9), name="boardfill")
    return sp, vc


def S10(L, n):
    _board(L, n, slide=True)
    c = H.cam((0.0, -4.7, 0.15), (0.0, 0, 0.1), lens=50)
    H.cam_move(c, [(1, (0.0, -4.8, 0.15), (-0.02, 0, 0.12)), (n, (-0.05, -4.25, 0.2), (-0.06, 0, 0.15))], ease=False)
    L.bake_static()


def S11(L, n):
    _board(L, n, slide=False)
    c = H.cam((0.1, -3.6, -0.6), (0.12, 0, -0.95), lens=50)
    H.cam_move(c, [(1, (0.1, -3.6, -0.6), (0.12, 0, -0.95)), (n, (0.14, -3.25, -0.62), (0.14, 0, -0.98))])
    L.bake_static()


# --------------------------------------------------------------------------- S12 document reveal backdrop
def S12(L, n):
    import bpy
    H.eevee_quality()
    L.set_world((0.006, 0.005, 0.004), 1.0)
    H.box_mesh("desk", [(0, 0, -0.03, 3, 3, 0.03)], L.WOOD_OLD())
    H.box_mesh("page", [(0, 0, 0.002, 0.42, 0.58, 0.002, 0.06)], H.mat_paper("news", (0.62, 0.6, 0.52)))
    ink = L.mat_principled("newsink", (0.1, 0.09, 0.08), rough=0.8)
    bars = []
    for col in range(3):
        for row in range(13):
            bars.append((-0.27 + col * 0.27, 0.3 - row * 0.062, 0.006, 0.11, 0.01, 0.001))
    g = H.box_mesh("columns", bars, ink)
    g.rotation_euler = (0, 0, 0.06)
    t = L.text3d("ABOUT 2% WAS FAKED", loc=(-0.03, 0.43, 0.006), rot=(0, 0, 0.06), size=0.07, extrude=0.0005, mat=ink, name="headline")
    t2 = L.text3d("2016 INTERVIEW", loc=(-0.02, 0.37, 0.006), rot=(0, 0, 0.06), size=0.03, extrude=0.0005, mat=ink, name="sub")
    H.box_mesh("pencil", [(0.5, -0.2, 0.01, 0.006, 0.18, 0.006, 0.4)], L.mat_principled("pen", (0.5, 0.35, 0.05), rough=0.5))
    L.spot((-0.8, -0.6, 1.6), (0, 0, 0), energy=120, size_deg=50, blend=0.7, color=(1.0, 0.8, 0.55), name="paperlamp")
    pl = bpy.data.objects["paperlamp"]
    H.aim(pl, (-0.8, -0.6, 1.6), (0, 0.1, 0))
    c = H.cam((0.05, -0.75, 1.5), (0.0, 0.05, 0.0), lens=38)
    H.cam_move(c, [(1, (0.05, -0.8, 1.5), (0.0, 0.0, 0.0)), (n, (0.0, -0.6, 1.45), (-0.02, 0.2, 0.0))], ease=False)
    L.dof(c, distance=1.6, fstop=4)
    L.bake_static()


# --------------------------------------------------------------------------- S13 still: chair back against the wall
def S13(L, n):
    H.eevee_quality()
    L.set_world((0.004, 0.006, 0.012), 1.0)
    H.enfield_bedroom(n, chair="B", rec_on=False, dust_count=400)
    c = H.cam(BC["start"], BC["target"], lens=BC["lens"] / 1.1)
    L.cam_light(c, energy=30, color=(0.65, 0.75, 1.0), size_deg=80)
    L.bake_static()


# --------------------------------------------------------------------------- S14 the reveal: chair moved, REC pops on
def S14(L, n):
    H.eevee_quality()
    L.set_world((0.004, 0.006, 0.012), 1.0)
    H.enfield_bedroom(n, chair="A", rec_on=True, rec_on_frame=18, dust_count=400)
    lens0 = BC["lens"] / 1.1
    c = H.cam(BC["start"], BC["target"], lens=lens0)
    c.data.keyframe_insert("lens", frame=8)
    c.data.lens = lens0 * 1.03
    c.data.keyframe_insert("lens", frame=n)
    L.cam_light(c, energy=30, color=(0.65, 0.75, 1.0), size_deg=80)
    L.bake_static()


# --------------------------------------------------------------------------- S15 loop: = S01 start
def S15(L, n):
    H.eevee_quality()
    L.set_world((0.004, 0.006, 0.012), 1.0)
    H.enfield_bedroom(n, chair="A", rec_on=True)
    H.bedroom_camera(n, "push", push=n / 143.0)
    L.bake_static()
