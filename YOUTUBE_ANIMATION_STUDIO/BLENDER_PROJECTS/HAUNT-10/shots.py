"""HAUNT-10 - The staircase that leads into the ceiling (Winchester Mystery House, San Jose). One builder per shot: def Sxx(L, n).
Everything is generic and our own: the mansion is NOT a replica of the real house, no logos or signage, rifles carry no marks.
Legend beats (S06, S07) get a sepia compositor grade (lib_murder.legend_grade) and carry FOLKLORE badges; the documented
counterpoint (S08-S11) is in plain daylight / desk light. Sarah Winchester appears only as a small faceless silhouette (S04, S06).
The S12 figure is a generic pale coat figure, badged DRAMATISATION.
Builders: lib_haunted.py HAUNT-10 block (papered_stairwell, qa_block, qa_turret, rambling_mansion, grow_in, scaffold,
lever_rifle_rack, seat_pose, hat_on, vintage_car, picket_fence, ticket_booth, wisp).
Layouts. STAIR: flight rises +Y from y=0 between walls at x=+-0.475, ceiling z=3.0 meets the top tread at y=3.75.
MANSION: front faces -Y, about x -27..26, tower at (0.5, 8)."""
import importlib, sys, os, math, random
_LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PIPELINE", "blender")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import lib_haunted as H
import lib_murder as M
import studio_lib as L
importlib.reload(H)
import bpy
from mathutils import Vector

R = math.radians
MARKS = {}



def _bake(L):
    """QC fix 2026-11-28: the wall-sconce lamps (*_gas_l) sit almost against the stairwell paper and their shadow maps
    speckled every wall (shadow acne). Shadows off for those lamps, energy x0.55 to keep the dim mood; then bake."""
    import bpy
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.endswith("_gas_l"):
            o.data.use_shadow = False
            ad = o.data.animation_data
            fcs = []
            if ad and ad.action:
                fcs = [fc for fc in L._fcurves(ad.action) if fc.data_path == "energy"]
            if fcs:
                for fc in fcs:
                    for kp in fc.keyframe_points:
                        kp.co[1] *= 0.55
                        kp.handle_left[1] *= 0.55
                        kp.handle_right[1] *= 0.55
            else:
                o.data.energy *= 0.55
    L.bake_static()

def mark(**pts):
    MARKS.update(pts)


def shot_cam(n, p0, t0, p1, t1, lens=35, ease=False, roll1=None):
    c = H.cam(p0, t0, lens=lens)
    H.cam_move(c, [(1, p0, t0), (n, p1, t1, roll1)], ease=ease)
    return c


def area_at(loc, target, energy, size, color, name, shadow=False):
    a = L.area(loc, (0, 0, 0), energy=energy, size=size, color=color, name=name)
    H.aim(a, loc, target)
    a.data.use_shadow = shadow
    return a


def lawn(size=260, col=((0.02, 0.035, 0.015), (0.06, 0.09, 0.035))):
    return H.ground_box("lawn", -size, size, -size, size, -0.02, L.mat_noise_surface("lawn_m", col[0], col[1], scale=1.5, bump=0.2, voronoi=False, rough=1))


def hedge(x0, x1, y, gate=None, h=1.2, name="hedge"):
    m = L.mat_noise_surface(name + "_m", (0.008, 0.02, 0.008), (0.03, 0.06, 0.025), scale=5, bump=0.5, voronoi=True, rough=1.0)
    segs = [(x0, x1)] if not gate else [(x0, gate[0] - gate[1]), (gate[0] + gate[1], x1)]
    o = H.box_mesh(name, [((a + b) / 2, y, h / 2, (b - a) / 2, 0.5, h / 2) for a, b in segs], m, bevel=0.12)
    return o


# ============================================================================= the staircase (S01, S02, S13, S09)

S01_P0, S01_T0 = (0.06, -2.3, 0.75), (0.0, 2.6, 1.75)
S01_P1, S01_T1 = (0.03, -1.3, 1.0), (0.0, 3.4, 2.2)
S01_N = 67


def stair_set(L, n, dips=(), lamp_e=260.0):
    H.eevee_quality()
    L.set_world((0.004, 0.0045, 0.006), 1.0)
    S = H.papered_stairwell(hall=5.0)
    lt = S["lamp"]["light"]
    for ch in S["lamp"]["root"].children:   # the lamp's heat-shimmer volume blows out the narrow well: off
        if ch.name.endswith("_shimmer"):
            ch.hide_render = True
    rnd = random.Random(4)
    gm = S["lamp"]["glass"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for f in range(1, n + 1):
        k = 1.0 if f in (1, n) else 1.0 - 0.12 * rnd.random()
        for a, b, lv in dips:
            if a <= f <= b:
                k = lv * (0.8 + 0.4 * rnd.random())
        lt.data.energy = lamp_e * k
        lt.data.keyframe_insert("energy", frame=f)
        gm.default_value = 1.6 * k
        gm.keyframe_insert("default_value", frame=f)
    lt.data.shadow_soft_size = 0.03
    cold = L.point((0.0, 2.6, 2.6), energy=22.0, color=(0.55, 0.65, 0.95), radius=0.1, name="coldtop")
    cold.data.use_shadow = False
    H.dust((0, 1.2, 1.7), (0.8, 3.0, 2.0), n, count=260, radius=0.0018, drift=(0.0, 0.01, 0.012), emit=0.35)
    return S


def S01(L, n):
    # COLD OPEN: from the bottom step, tilt and push up the flight to where it meets the ceiling
    stair_set(L, n, dips=((24, 26, 0.55),))
    c = shot_cam(n, S01_P0, S01_T0, S01_P1, S01_T1, lens=28)
    L.cam_light(c, energy=45, color=(0.7, 0.78, 0.95))
    mark(top=(0, 3.75, 3.0), step8=(0, 2.0, 1.6), foot=(0, 0, 0.2), lamp=(-0.24, 0.95, 2.15))
    H.crisp_shadows()
    _bake(L)


def S13(L, n):
    # LOOP FRAME: linear settle that ends exactly on S01 frame 1 (same per-frame speed)
    stair_set(L, n, dips=((40, 42, 0.6),))
    k = (n - 1) / (S01_N - 1)
    p = tuple(S01_P0[i] + (S01_P0[i] - S01_P1[i]) * k for i in range(3))
    t = tuple(S01_T0[i] + (S01_T0[i] - S01_T1[i]) * k for i in range(3))
    c = shot_cam(n, p, t, S01_P0, S01_T0, lens=28)
    L.cam_light(c, energy=45, color=(0.7, 0.78, 0.95))
    mark(top=(0, 3.75, 3.0), foot=(0, 0, 0.2))
    H.crisp_shadows()
    _bake(L)


def S02(L, n):
    # at the top step: plaster inches from the lens; the lamp below dips and recovers
    stair_set(L, n, dips=((28, 36, 0.3),), lamp_e=200.0)
    c = shot_cam(n, (0.0, 1.5, 2.25), (0.0, 3.75, 2.6), (0.05, 2.75, 2.7), (0.0, 3.75, 2.8), lens=28, roll1=R(5))
    L.cam_light(c, energy=4, color=(0.7, 0.78, 0.95))
    mark(top=(0, 3.75, 3.0), step13=(0, 3.3, 2.8))
    H.crisp_shadows()
    _bake(L)


def S09(L, n):
    # cut-away in flat daylight: a later floor comes down over the top of the old flight
    L.set_world((0.5, 0.52, 0.55), 1.0)
    S = H.papered_stairwell(ceiling=False, east_wall=False, lamp=False, hall=1.5)
    L.sun(rot=(R(50), 0, R(60)), energy=2.5, color=(1.0, 0.97, 0.92), angle=8.0)
    area_at((8, 1.5, 4), (0, 1.5, 2), 500.0, 6.0, (0.9, 0.93, 1.0), "front9")
    root = H.empty("later_floor", (0, 0, 4.6))
    joist = H.mat_oak("joist9", 1.4)
    pl = L.mat_noise_surface("pl9", (0.42, 0.4, 0.34), (0.6, 0.57, 0.5), scale=3, bump=0.05, voronoi=False, rough=0.9)
    H.box_mesh("slab9", [(0, 1.15, 3.11, 0.62, 2.85, 0.1)], joist, parent=root)
    H.box_mesh("room9", [(-0.57, 1.15, 4.5, 0.05, 2.85, 1.3), (0, 4.0, 4.5, 0.62, 0.05, 1.3), (0, -1.7, 4.5, 0.62, 0.05, 1.3), (0, 1.15, 5.85, 0.62, 2.9, 0.05)],
               pl, parent=root)
    H.box_mesh("rug9", [(0, 1.3, 3.22, 0.45, 1.2, 0.01)], H.mat_carpet("rug9m", (0.12, 0.03, 0.025), (0.25, 0.08, 0.05)), parent=root)
    H.box_mesh("bed9", [(-0.1, 2.9, 3.5, 0.4, 0.9, 0.22), (-0.1, 3.75, 3.9, 0.4, 0.04, 0.4)], H.mat_oak("bed9m", 0.9), parent=root)
    H.box_mesh("win9", [(-0.51, 0.6, 4.6, 0.01, 0.45, 0.7)], L.mat_emission("win9m", (0.8, 0.88, 1.0), 2.0), parent=root)
    root.keyframe_insert("location", frame=16)
    root.location = (0, 0, 0)
    root.keyframe_insert("location", frame=46)
    red = L.mat_emission("hl9", (0.95, 0.12, 0.06), 3.0)
    hl = H.box_mesh("hl9", [(0.6, 3.25, 3.02, 0.01, 0.62, 0.012), (0.6, 3.25, 2.3, 0.01, 0.62, 0.012), (0.6, 2.63, 2.66, 0.01, 0.012, 0.37), (0.6, 3.87, 2.66, 0.01, 0.012, 0.37)], red)
    hl.visible_shadow = False
    H.key_vis(hl, [(1, False), (50, True), (54, False), (58, True)])
    c = H.cam((14.0, 1.15, 1.0), (0.0, 1.15, 1.0), lens=50)
    H.box_mesh("earth9", [(0, 1.15, -3.5, 0.62, 2.9, 3.48)], L.mat_noise_surface("earth9m", (0.03, 0.025, 0.02), (0.08, 0.065, 0.05), scale=2, bump=0.3, rough=1.0))
    c.data.type = "ORTHO"
    c.data.ortho_scale = 10.8
    c.data.keyframe_insert("ortho_scale", frame=1)
    c.data.ortho_scale = 11.8
    c.data.keyframe_insert("ortho_scale", frame=n)
    mark(top=(0.5, 3.75, 3.0), foot=(0.5, 0, 0), room_top=(0.5, 1.15, 5.9), hall=(0.5, -1.5, 0), end=(0.5, 3.85, 1.5))
    _bake(L)


# ============================================================================= the mansion exteriors

def dusk_env(strength=1.0, sun_e=0.6, fog=0.006):
    M.dawn_sky(hor=(0.5, 0.3, 0.42), mid=(0.2, 0.17, 0.36), zen=(0.04, 0.04, 0.13), strength=strength)
    L.sun(rot=(R(80), 0, R(-150)), energy=sun_e, color=(0.75, 0.65, 1.0), angle=4.0, name="dusk")
    if fog:
        L.fog_volume(center=(0, -20, 6), size=(260, 200, 14), density=fog, color=(0.7, 0.68, 0.85))
        bpy.context.scene.eevee.volumetric_end = 160


def day_env(strength=1.0, sun_e=3.2, sun_rot=(R(52), 0, R(-140)), col=(1.0, 0.95, 0.85), hor=(0.75, 0.78, 0.8)):
    M.dawn_sky(hor=hor, mid=(0.5, 0.6, 0.75), zen=(0.22, 0.36, 0.62), strength=strength)
    return L.sun(rot=sun_rot, energy=sun_e, color=col, angle=3.0, name="daysun")


def S03(L, n):
    # dusk: the whole rambling house behind its hedge, a few amber windows; push in over the hedge
    H.eevee_quality()
    dusk_env(strength=0.7, sun_e=0.3)
    lawn()
    Mn = H.rambling_mansion(mats=H.mansion_mats("qa", lit_strength=9.0))
    hedge(-40, 40, -15.0)
    area_at((-10, -40, 14), (0, 0, 7), 2600.0, 14.0, (0.6, 0.55, 0.95), "wash")
    H.bare_forest("trees3", [(-80, -34, -5, 40), (34, 80, -5, 40), (-70, 70, 26, 60)], count=40, seed=7, height=(10, 17))
    c = shot_cam(n, (3.0, -74.0, 1.9), (0.0, 0.0, 3.5), (1.5, -50.0, 2.4), (0.0, 0.0, 6.5), lens=35)
    mark(base=(0, 0, 0), tower_top=(0.5, 8, 24.4), roof_l=(-23, 0, 12), roof_r=(21, 0, 9), hedge=(0, -15, 1.2))
    H.crisp_shadows()
    _bake(L)


def S04(L, n):
    # the 1880s: a modest farmhouse among young fruit trees; a small faceless woman in a long dress at the gate (from behind)
    day_env(strength=0.8, sun_e=2.0, sun_rot=(R(62), 0, R(-125)), col=(1.0, 0.9, 0.72))
    lawn(col=((0.05, 0.07, 0.025), (0.13, 0.15, 0.06)))
    Mn = H.rambling_mansion(parts=("core",), tower_levels=0, lit=False)
    gm = H.grove_mats()
    H.leafy_trees("orchard", [(-26, -8, -6, 12), (6, 26, -6, 12), (-20, 20, 12, 30)], gm, count=26, seed=4, height=(3.0, 4.6))
    H.picket_fence("fence4", -30, 30, -9.0, gate=(-1.0, 0.7))
    H.ground_box("path4", -1.7, -0.3, -30, -2, 0.0, H.mat_gravel("path4m"))
    s = H.figure("sarah", height=1.5, dress=True, color=(0.012, 0.012, 0.016))
    s["root"].location = (-1.0, -10.2, 0)
    for f, yaw in ((1, -8), (n, 6)):
        s["neck"].rotation_euler = (R(12), 0, R(yaw))
        s["neck"].keyframe_insert("rotation_euler", frame=f)
    c = shot_cam(n, (-5.5, -18.5, 1.45), (-1.2, 0.0, 0.2), (-1.2, -18.5, 1.5), (-0.9, 0.0, 0.3), lens=35)
    H.dust((-1, -13, 1.5), (5, 3, 2), n, count=200, radius=0.002, drift=(0.02, 0, 0.01), emit=0.3)
    mark(head=(-1, -10.2, 1.5), feet=(-1, -10.2, 0), ridge=(-1, 0, 9.0), door=(-1, 0, 1.1))
    _bake(L)


def S05(L, n):
    # time-lapse from a hill: the farmhouse sprouts wings, turrets and a tower; scaffolds come and go; days flicker to nights
    sun = day_env(sun_e=3.0)
    bg = next(nd for nd in bpy.context.scene.world.node_tree.nodes if nd.type == "BACKGROUND")
    lawn(col=((0.045, 0.065, 0.025), (0.12, 0.14, 0.055)))
    Mn = H.rambling_mansion()
    sched = {"wingL1": 10, "wingR1": 22, "back": 34, "wingL2": 58, "wingR2": 72, "extras": 86}
    for k, f in sched.items():
        H.grow_in(Mn["objs"][k], f)
    for i, lv in enumerate(Mn["tower"]):
        H.grow_in([lv], 44 + i * 4, dur=3)
    H.grow_in([Mn["tower_cap"]], 44 + 7 * 4, dur=3)
    for i, (x0, x1, y, z1, fa, fb) in enumerate(((-15, -5, 1, 7, 5, 16), (3, 12, 0.5, 9, 17, 28), (-10, 14, -1.5, 9, 29, 40), (-2.5, 3.5, 5.6, 21, 41, 76),
                                                (-23, -15, -1, 9, 53, 64), (12, 21, -2, 7, 67, 78), (21, 26, 0, 4, 81, 92))):
        sc = H.scaffold(f"scaf{i}", x0, x1, y, z1, bay=2.5, lift=2.5)
        H.key_vis(sc, [(1, False), (fa, True), (fb, False)])
    lit = Mn["mats"][4]
    for f in range(1, n + 1):
        u = ((f - 1) / 19.0 + 0.5) % 1.0
        day = math.sin(math.pi * u) ** 1.3
        sun.data.energy = 3.0 * (0.04 + 0.96 * day)
        sun.rotation_euler = (R(50 + 22 * abs(2 * u - 1)), 0, R(-210 + 140 * u))
        sun.data.keyframe_insert("energy", frame=f)
        sun.keyframe_insert("rotation_euler", frame=f)
        bg.inputs[1].default_value = 0.1 + 0.9 * day
        bg.inputs[1].keyframe_insert("default_value", frame=f)
    H.key_emission(lit, [(f, 4.0 if (math.sin(math.pi * (((f - 1) / 19.0 + 0.5) % 1.0)) < 0.45) else 0.6) for f in range(1, n + 1)])
    H.bare_forest("trees5", [(-90, -36, -10, 50), (36, 90, -10, 50), (-80, 80, 30, 80)], count=45, seed=7, height=(8, 14))
    c = shot_cam(n, (6.0, -92.0, 40.0), (0.0, 0.0, -19.0), (5.0, -86.0, 38.0), (0.0, 0.0, -17.0), lens=35)
    mark(base=(0, 0, 0), tower_top=(0.5, 8, 24.4), left=(-27, 0, 3), right=(26, 0, 3))
    _bake(L)


def S07(L, n):
    # LEGEND (sepia): lantern-lit carpenters hammer on the scaffold as a new gable rises - the endless building of the story
    M.night_sky(stars=0.6, hor=(0.03, 0.035, 0.06), zen=(0.004, 0.005, 0.012))
    L.sun(rot=(R(55), 0, R(-150)), energy=0.9, color=(0.55, 0.65, 1.0), angle=3.0, name="moon7")
    lawn()
    Mn = H.rambling_mansion(parts=("core", "wingL1", "wingR1", "back"), tower_levels=0, lit=False)
    H.scaffold("scaf7", 2.5, 12.5, 0.4, 10.0, bay=2.5, lift=2.0)
    newg = H.qa_block("newgable", 6.0, 10.0, -0.6, 3.0, 10.5, 2.4, "Y", Mn["mats"], floor_h=10.5, seed=31, band=False, front=False)
    for f, sz in ((1, 0.62), (n, 1.0)):
        newg.scale = (1, 1, sz)
        newg.keyframe_insert("scale", frame=f)
    spots = ((4.2, 4.04, 0), (7.6, 6.04, 9), (10.8, 2.04, 17))
    for i, (x, z, off) in enumerate(spots):
        p = H.figure(f"carp{i}", height=1.75, cap=(i != 1), color=(0.012, 0.012, 0.014))
        p["root"].location = (x, -0.15, z)
        p["root"].rotation_euler = (0, 0, R(-10 + 12 * i))
        f = 1
        while f <= n:
            hit = f + 5 + off % 17
            for ff, sh, el in ((hit - 5, 150, 70), (hit, 62, 20), (hit + 3, 80, 30)):
                H.pose_hold(p, "R", shoulder=(R(sh), 0, 0), elbow=(R(el), 0, 0), frame=ff)
            f += 17
        H.box_mesh(f"hammer{i}", [(0, 0.0, -0.4, 0.012, 0.012, 0.13), (0, 0.04, -0.52, 0.025, 0.06, 0.025)], L.mat_principled(f"ham{i}", (0.02, 0.02, 0.02), rough=0.5),
                   parent=p["elbowR"])
        M.lantern((x - 0.7, -0.3, z + 0.02), energy=1600.0, name=f"lan7_{i}", flicker_n=n)
    area_at((-6, -30, 10), (6, 0, 6), 14000.0, 10.0, (0.5, 0.6, 1.0), "moonwash7")
    c = shot_cam(n, (9.5, -19.0, 1.8), (7.4, 0.0, 3.6), (8.6, -16.5, 6.6), (7.4, 0.0, 7.4), lens=35)
    H.handheld(c, n, amp=0.01, rate=0.4, rot_amp=0.0015)
    M.legend_grade(sepia=1.0, grain=0.06)
    mark(carp0=(4.2, -0.15, 5.8), carp1=(7.6, -0.15, 7.8), carp2=(10.8, -0.15, 3.8), gable=(8, -0.6, 12.5), ground=(7.5, -1, 0))
    H.crisp_shadows()
    _bake(L)


def S08(L, n):
    # 1906: the tower shudders and its top three storeys come down in dust - seven floors to four
    day_env(sun_e=2.6, sun_rot=(R(58), 0, R(-160)), col=(1.0, 0.96, 0.9), hor=(0.72, 0.72, 0.7))
    lawn(col=((0.045, 0.06, 0.025), (0.11, 0.13, 0.055)))
    Mn = H.rambling_mansion(lit=False)
    tx, ty = Mn["tower_xy"]
    f0 = 20
    rnd = random.Random(5)
    falling = [(Mn["tower_cap"], 0), (Mn["tower"][6], 4), (Mn["tower"][5], 9), (Mn["tower"][4], 14)]
    for o, d in falling:
        z = o.location.z
        o.keyframe_insert("location", frame=f0 + d)
        o.keyframe_insert("rotation_euler", frame=f0 + d)
        dx, dy = rnd.uniform(1.5, 4.0) * rnd.choice((-1, 1)), rnd.uniform(0.5, 2.5)
        o.location = (tx + dx * 0.4, ty + dy * 0.4, z - 1.5)
        o.rotation_euler = (rnd.uniform(-0.25, 0.25), rnd.uniform(-0.3, 0.3), 0)
        o.keyframe_insert("location", frame=f0 + d + 8)
        o.keyframe_insert("rotation_euler", frame=f0 + d + 8)
        o.location = (tx + dx, ty + dy, 9.0)
        o.rotation_euler = (rnd.uniform(-0.9, 0.9), rnd.uniform(-1.0, 1.0), rnd.uniform(-0.4, 0.4))
        o.keyframe_insert("location", frame=f0 + d + 26)
        o.keyframe_insert("rotation_euler", frame=f0 + d + 26)
        for fc in L._fcurves(o.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "QUAD"
                kp.easing = "EASE_IN"
        H.key_vis(o, [(1, True), (f0 + d + 27, False)])
    for o in Mn["tower"]:  # shudder before and during
        if o.animation_data is None:
            pass
    dm = L.mat_noise_surface("debris", (0.2, 0.18, 0.14), (0.4, 0.36, 0.28), scale=3, bump=0.2, voronoi=False)
    for i in range(16):
        ch = L.prim("cube", loc=(tx, ty, 16 + rnd.uniform(0, 6)))
        ch.scale = (rnd.uniform(0.15, 0.5), rnd.uniform(0.15, 0.5), rnd.uniform(0.1, 0.35))
        L.assign(ch, dm)
        fa = f0 + rnd.randint(2, 22)
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(3, 8)
        ch.keyframe_insert("location", frame=fa)
        ch.keyframe_insert("rotation_euler", frame=fa)
        ch.location = (tx + r * math.cos(a), ty + r * math.sin(a) * 0.6 - 2.0, rnd.uniform(6, 11))
        ch.rotation_euler = (rnd.uniform(-4, 4), rnd.uniform(-4, 4), rnd.uniform(-4, 4))
        ch.keyframe_insert("location", frame=fa + rnd.randint(18, 28))
        ch.keyframe_insert("rotation_euler", frame=fa + 28)
        H.key_vis(ch, [(1, False), (fa, True), (fa + 29, False)])
    dust = H.room_fog((tx, ty - 1.0, 15.0), (10, 9, 9), density=0.0, color=(0.75, 0.72, 0.66), anis=0.2, name="dust8")
    vn = next(nd for nd in dust.active_material.node_tree.nodes if nd.type == "PRINCIPLED_VOLUME")
    for f, d in ((1, 0.0), (f0, 0.0), (f0 + 10, 0.16), (f0 + 34, 0.3), (n, 0.14)):
        vn.inputs["Density"].default_value = d
        vn.inputs["Density"].keyframe_insert("default_value", frame=f)
    for f, s in ((f0, (0.5, 0.5, 0.5)), (f0 + 34, (1.3, 1.2, 1.0)), (n, (2.0, 1.7, 1.25))):
        dust.scale = (5 * s[0], 4.5 * s[1], 4.5 * s[2])
        dust.keyframe_insert("scale", frame=f)
    dust.keyframe_insert("location", frame=f0)
    dust.location = (tx, ty - 1.0, 12.5)
    dust.keyframe_insert("location", frame=n)
    bpy.context.scene.eevee.volumetric_end = 120
    c = shot_cam(n, (7.0, -31.0, 1.5), (0.5, 8.0, 12.5), (6.6, -29.5, 1.5), (0.5, 8.0, 11.0), lens=35)
    H.handheld(c, n, amp=0.07, rate=3.0, seed=5, rot_amp=0.006)
    M.shake(c, [f0, f0 + 14], amp=0.18, decay=10)
    mark(tower_top=(tx, ty, 24.4), lvl4=(tx, ty - 2.1, 12.0), base=(0, 0, 0), l=(-23, 0, 6), r=(21, 0, 6))
    _bake(L)


def visitor(name, kind, x, y, rz, height=1.72, coat=True):
    p = H.figure(name, height=height, coat=coat, color=(0.016, 0.016, 0.02))
    H.hat_on(p, kind)
    p["root"].location = (x, y, 0)
    p["root"].rotation_euler = (0, 0, rz)
    return p


def S11(L, n):
    # 1923: gate, a plain ticket booth with a blank board, a short queue of faceless visitors, two boxy cars; the house behind
    day_env(strength=0.85, sun_e=2.2, sun_rot=(R(50), 0, R(-150)))
    lawn(col=((0.05, 0.07, 0.025), (0.13, 0.15, 0.06)))
    Mn = H.rambling_mansion(lit=False, tower_levels=4)
    hedge(-40, 40, -15.0, gate=(0.0, 1.6))
    H.ground_box("drive", -40, 40, -26, -15.6, 0.0, H.mat_gravel("drive_m"))
    H.ground_box("path11", -1.4, 1.4, -15.6, -2, 0.0, H.mat_gravel("path11m"))
    H.ticket_booth((2.4, -17.2, 0), rot_z=R(180 - 25))
    q = []
    for i, (kind, h) in enumerate((("fedora", 1.78), ("cloche", 1.62), ("boater", 1.74), ("cloche", 1.58), ("fedora", 1.8))):
        x = 1.6 - i * 0.95
        p = visitor(f"vis{i}", kind, x, -18.6 - 0.12 * (i % 2), R(-78), height=h)
        q.append(p)
        for f, dx in ((1, -0.35), (int(n * 0.45), -0.35), (int(n * 0.7), 0.0), (n, 0.0)):
            p["root"].location.x = x + dx
            p["root"].keyframe_insert("location", frame=f)
        for f, yaw in ((1, 10 * (i % 2)), (n, 25 - 20 * (i % 3))):
            p["neck"].rotation_euler = (R(8), 0, R(yaw))
            p["neck"].keyframe_insert("rotation_euler", frame=f)
    H.vintage_car("car1", loc=(-3.6, -16.7, 0), rot_z=R(-90))
    H.vintage_car("car2", loc=(-8.6, -16.9, 0), rot_z=R(-84), body=(0.07, 0.03, 0.025))
    c = shot_cam(n, (-6.0, -27.5, 1.6), (-1.5, -18.0, 1.0), (-0.5, -27.5, 1.6), (0.5, -18.0, 1.0), lens=35)
    mark(vis_head=(0.6, -18.6, 1.75), vis_feet=(0.6, -18.6, 0), booth=(3, -17.4, 2.6), tower4=(0.5, 8, 15.4), car=(-9, -17.6, 1.8))
    _bake(L)


# ============================================================================= S06 the legend: the medium's warning (sepia)

def S06(L, n):
    H.eevee_quality()
    L.set_world((0.003, 0.003, 0.004), 1.0)
    paper = H.mat_wallpaper("parlour_paper", base=(0.12, 0.085, 0.05), stripe=(0.07, 0.05, 0.03), flower=(0.2, 0.11, 0.05), leaf=(0.07, 0.075, 0.04))
    H.box_mesh("walls6", [(0, 2.25, 1.7, 3.6, 0.05, 1.7), (-3.6, 0, 1.7, 0.05, 3.2, 1.7), (3.6, 0, 1.7, 0.05, 3.2, 1.7)], paper)
    H.box_mesh("dado6", [(0, 2.18, 0.5, 3.6, 0.03, 0.5)], H.mat_oak("dado6m", 0.6))
    H.box_mesh("floor6", [(0, 0, -0.02, 3.7, 3.3, 0.02)], H.mat_oak("floor6m", 0.7))
    tb = L.prim("cyl", loc=(0, 0, 0.4), vertices=28, radius=0.62, depth=0.8)
    L.assign(tb, H.mat_carpet("cloth6", (0.06, 0.012, 0.012), (0.13, 0.03, 0.025)))
    top = L.prim("cyl", loc=(0, 0, 0.805), vertices=28, radius=0.66, depth=0.02)
    L.assign(top, tb.active_material)
    cd = H.candle(loc=(0, 0, 0.82), name="candle6", energy=320)
    H.flicker_mat_with_light(cd["light"], cd["flame"], n, 320, 25, seed=3, depth=0.25, rate=0.5)
    med = H.figure("medium", height=1.72, coat=True, color=(0.012, 0.011, 0.012))
    med["root"].location = (-0.78, 0, 0)
    med["root"].rotation_euler = (0, 0, R(-90))
    H.seat_pose(med)
    sar = H.figure("sarah6", height=1.5, dress=True, color=(0.012, 0.012, 0.015))
    sar["root"].location = (0.78, 0, 0)
    sar["root"].rotation_euler = (0, 0, R(90))
    H.seat_pose(sar, hands_on_table=False)
    for f, a in ((1, 42), (50, 58), (n, 46)):
        H.pose_hold(med, "R", shoulder=(R(a), 0, R(-6)), elbow=(R(60), 0, 0), frame=f)
    for x, rz in ((-0.95, R(-90)), (0.95, R(90))):
        H.wood_chair((x, 0, 0), rot_z=rz, name=f"chair{int(x)}")
    H.lever_rifle_rack((0.0, 2.18, 1.2), count=5)
    for i, (x, z, fa, fb) in enumerate(((-0.9, 1.5, 12, 70), (0.7, 1.9, 34, 96), (-0.2, 2.3, 56, n), (1.3, 1.4, 70, n + 10))):
        if i == 3:
            break
        w = L.prim("sphere", loc=(x, 1.75, z), segments=14, ring_count=10, radius=1.0, name=f"wisp{i}")
        w.scale = (0.22, 0.2, 0.6)
        w.visible_shadow = False
        vm = L.mat_volume(f"wisp{i}_m", (0.85, 0.87, 0.82), 0.0, 0.2)
        L.assign(w, vm)
        vn = next(nd for nd in vm.node_tree.nodes if nd.type == "PRINCIPLED_VOLUME")
        for f, d in ((1, 0.0), (fa, 0.0), (fa + (fb - fa) * 0.45, 2.2), (fb, 0.0), (n + 12, 0.0)):
            vn.inputs["Density"].default_value = d
            vn.inputs["Density"].keyframe_insert("default_value", frame=f)
        w.keyframe_insert("location", frame=fa)
        w.location = (x + 0.3 * (1 if i % 2 else -1), 1.2, z + 0.45)
        w.keyframe_insert("location", frame=fb)
    area_at((0, 2.0, 3.2), (0, 1.0, 1.2), 110.0, 1.2, (0.5, 0.6, 0.95), "rim6", shadow=False)
    area_at((0, -3.5, 2.6), (0, 2.2, 1.7), 170.0, 2.0, (0.55, 0.62, 0.9), "rackfill", shadow=False)
    c = shot_cam(n, (-1.2, -6.3, 1.45), (0.0, 0.6, 0.85), (1.0, -5.8, 1.55), (0.0, 0.9, 0.95), lens=50)
    H.dust((0, -0.5, 1.4), (2.4, 1.6, 1.4), n, count=180, radius=0.0018, drift=(0.005, 0, 0.012), emit=0.3)
    M.legend_grade(sepia=1.0, grain=0.06)
    mark(candle=(0, 0, 0.98), med_head=(-0.78, 0, 1.3), sar_head=(0.78, 0, 1.2), rack_top=(0, 2.18, 2.6), rack_bot=(0, 2.18, 1.2), floor=(0, 0, 0))
    H.crisp_shadows()
    _bake(L)


# ============================================================================= S10 the biographer's desk

def S10(L, n):
    L.set_world((0.002, 0.002, 0.003), 1.0)
    M.desk(size=(1.8, 1.4))
    M.rounded_box((0.0, 0.0, 0.002), (0.6, 0.44, 0.004), (0.05, 0.035, 0.03), bevel=0.2, name="blotter10")
    card = M.empty("card10", (0.0, 0.02, 0.006))
    H.box_mesh("card10p", [(0, 0, 0.0005, 0.076, 0.051, 0.0005)], M.mat_paper("card10m", (0.7, 0.67, 0.56)), parent=card)
    bars = [(0.0, 0.034, 0.0012, 0.05, 0.0025, 0.0002)] + [(-0.012 + 0.006 * (i % 2), 0.016 - i * 0.011, 0.0012, 0.052 - 0.01 * (i % 3), 0.0016, 0.0002) for i in range(5)]
    H.box_mesh("card10b", bars, L.mat_principled("card10i", (0.1, 0.09, 0.08), rough=0.9), parent=card)
    H.box_mesh("card10r", [(0, 0.026, 0.0012, 0.07, 0.0004, 0.0002)], L.mat_principled("card10red", (0.5, 0.08, 0.06), rough=0.9), parent=card)
    for f, p, rz in ((1, (-0.3, -0.12, 0.006), R(-28)), (16, (-0.01, 0.01, 0.006), R(-7)), (20, (0.0, 0.02, 0.006), R(-5)), (n, (0.0, 0.02, 0.006), R(-5))):
        card.location = p
        card.rotation_euler = (0, 0, rz)
        card.keyframe_insert("location", frame=f)
        card.keyframe_insert("rotation_euler", frame=f)
    M.book((0.2, 0.1, 0.0), size=(0.15, 0.22, 0.035), cover=(0.07, 0.03, 0.025), rot_z=R(14), name="book10")
    M.desk_lamp((0.34, 0.3, 0.0), (0.0, 0.0, 0.0), energy=10.0, rot_z=R(-45))
    L.area((-0.2, -0.1, 0.9), (0, 0, 0), energy=2.0, size=0.8, color=(0.55, 0.65, 0.95), name="cool10").data.use_shadow = False
    c = H.cam((0.0, -0.1, 0.62), (0.0, -0.1, 0.0), lens=50)
    for f, z, roll in ((1, 0.62, R(-2)), (n, 0.5, R(2))):
        c.location = (0.0, -0.1, z)
        c.rotation_euler = (0, 0, roll)
        c.keyframe_insert("location", frame=f)
        c.keyframe_insert("rotation_euler", frame=f)
    L.linear_fcurves(c)
    mark(card=(0, 0.02, 0.006))
    _bake(L)


# ============================================================================= S12 the door to nowhere (from the garden)

def S12(L, n):
    H.eevee_quality()
    M.night_sky(stars=0.7, hor=(0.03, 0.035, 0.065), zen=(0.004, 0.005, 0.014))
    L.sun(rot=(R(50), 0, R(-35)), energy=0.5, color=(0.5, 0.62, 1.0), angle=2.0, name="moon12")
    lawn()
    mats = H.mansion_mats("w12")
    DZ, DW, DH = 4.0, 0.95, 2.15
    wall = H.wall_with_openings("wall12", "x", 0.0, 16.0, 11.5, [(0.0, DW, DZ, DZ + DH)], t=0.3, mat=mats[0], outward=1)
    H.box_mesh("trim12", [(0, -0.03, 3.3, 8.0, 0.04, 0.07), (0, -0.03, 7.4, 8.0, 0.04, 0.07), (0, -0.04, DZ + DH + 0.08, DW / 2 + 0.12, 0.05, 0.08),
                          (-DW / 2 - 0.06, -0.04, DZ + DH / 2, 0.06, 0.05, DH / 2), (DW / 2 + 0.06, -0.04, DZ + DH / 2, 0.06, 0.05, DH / 2),
                          (0, -0.06, DZ - 0.05, DW / 2 + 0.14, 0.08, 0.05), (0, -0.25, 11.5, 8.3, 0.4, 0.12)], mats[2])
    H.box_mesh("roof12", [(0, 1.5, 12.6, 8.4, 2.0, 1.0)], mats[1])
    H.box_mesh("glass12", [(x, -0.01, z, 0.45, 0.02, 0.8) for x, z in ((-5.0, 1.9), (5.0, 1.9), (-5.0, 6.3), (5.0, 9.6), (-5.0, 9.6))], mats[3])
    H.box_mesh("room12", [(0, 1.6, DZ + DH / 2, 1.2, 0.05, DH / 2 + 0.2), (-1.2, 0.9, DZ + DH / 2, 0.05, 0.7, DH / 2 + 0.2), (1.2, 0.9, DZ + DH / 2, 0.05, 0.7, DH / 2 + 0.2),
                          (0, 0.9, DZ - 0.05, 1.2, 0.7, 0.05), (0, 0.9, DZ + DH + 0.2, 1.2, 0.7, 0.05)],
               H.mat_wallpaper("room12p", base=(0.3, 0.22, 0.12), stripe=(0.2, 0.14, 0.07)))
    hinge, slab = H.door_slab("door12", (-DW / 2, -0.03, DZ), width=DW, height=DH, angle=0.0, axis="x", mat=H.mat_oak("door12m", 0.9))
    f_open0, f_open1 = 8, 30
    for f, a in ((1, 0.0), (f_open0, 0.0), (f_open1, R(-104)), (f_open1 + 8, R(-98)), (n, R(-100))):
        hinge.rotation_euler = (0, 0, a)
        hinge.keyframe_insert("rotation_euler", frame=f)
    lan = L.point((0.25, 0.75, DZ + 1.25), energy=0.0, color=(1.0, 0.66, 0.32), radius=0.06, name="lantern12")
    H.key_energy(lan, [(1, 30), (f_open0, 30), (f_open1, 140), (n, 140)], "LINEAR")
    lg = L.prim("sphere", loc=(0.25, 0.75, DZ + 1.25), radius=0.06, segments=10, ring_count=6)
    L.assign(lg, L.mat_emission("lan12g", (1.0, 0.7, 0.35), 12.0))
    lg.visible_shadow = False
    FIG = (1.9, -1.8, 0.0)
    beam = L.spot((0.2, 0.2, DZ + 1.3), (0, 0, 0), energy=0.0, size_deg=30, blend=0.6, color=(1.0, 0.8, 0.55), name="beam12", radius=0.03)
    tg = M.empty("beam12t", (0.0, -1.5, 0.0))
    for f, p in ((1, (0.0, -1.0, 0.5)), (f_open1, (-1.0, -3.0, 0.3)), (40, (FIG[0], FIG[1], 1.0)), (n, (FIG[0], FIG[1], 1.0))):
        tg.location = p
        tg.keyframe_insert("location", frame=f)
    M.aim(beam, tg)
    f_see, f_gone = 38, 60
    H.key_energy(beam, [(1, 0), (f_open1 - 6, 0), (f_open1, 2600), (n, 2600)], "LINEAR")
    fig = H.coat_figure("pale12", height=1.66, emit=0.1)
    fig["root"].location = FIG
    fig["root"].rotation_euler = (0, 0, R(-18))
    fig["neck"].rotation_euler = (R(28), 0, 0)
    H.key_vis(fig["root"].children_recursive + [fig["root"]], [(1, False), (f_see, True), (f_gone, False)])
    hedge(-12, -2.5, -5.5, name="hedge12a")
    hedge(4.5, 12, -4.5, name="hedge12b")
    H.bare_forest("tree12", [(-12, -6, -6, -2)], count=2, seed=3, height=(7, 9))
    L.fog_volume(center=(0, -6, 1.2), size=(40, 26, 2.6), density=0.035, color=(0.6, 0.66, 0.85))
    area_at((-8, -14, 9), (0, 0, 5), 1300.0, 6.0, (0.45, 0.55, 1.0), "moonwash12")
    c = shot_cam(n, (2.6, -16.2, 1.3), (0.4, 0.0, 2.2), (2.4, -15.0, 1.3), (0.6, 0.0, 1.45), lens=35, ease=True)
    H.handheld(c, n, amp=0.006, rate=0.5, rot_amp=0.0015)
    mark(door_top=(0, 0, DZ + DH), door_bot=(0, 0, DZ), fig_head=(FIG[0], FIG[1], 1.66), fig_feet=FIG, wall_top=(0, 0, 11.5), ground=(0, 0, 0))
    H.crisp_shadows()
    _bake(L)
