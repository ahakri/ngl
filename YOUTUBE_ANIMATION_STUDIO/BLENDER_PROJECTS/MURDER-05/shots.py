"""MURDER-05 - Hinterkaifeck farm, Upper Bavaria, March 1922.
Shot builders: def SXX(L, n). Reusable builders (farmstead, plank material, fence, lantern, cattle, iron key,
question-mark cards, newspaper, oil lamp, laptop, case folder) live in PIPELINE/blender/lib_murder.py.
World layout: house centred at the origin, front gable (windows) faces -Y; barn wing attached on +X (x 4.5..18.5).
Lit window = house ground floor at x=3. Footprints run from the south tree line (y~-70) to the barn wall at (7.2, -3.9).
Child-victim rule: no victims, no violence, no night reconstruction. S09 = a lit window going dark, nothing else.
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
MOON_COL = (0.5, 0.6, 1.0)


def lin(o):
    M.set_interp(o, "LINEAR")


def const(o):
    M.set_interp(o, "CONSTANT")


def cam_path(n, c0, c1, t0, t1, lens=35, ease=True, f0=1):
    cam, ct = L.camera(loc=c0, target=t0, lens=lens)
    cam.data.clip_end = 1500
    L.cam_keys(cam, [(f0, c0), (n, c1)])
    ct.location = t0
    ct.keyframe_insert("location", frame=f0)
    ct.location = t1
    ct.keyframe_insert("location", frame=n)
    if not ease:
        lin(cam)
        lin(ct)
    return cam, ct


# ============================================================================= shared farm world

def H(x, y):
    base = 1.4 * noise.noise(Vector((x * 0.012, y * 0.012, 0.5))) + 0.3 * noise.noise(Vector((x * 0.05, y * 0.05, 1.3)))
    base += 0.025 * noise.noise(Vector((x * 0.5, y * 1.8, 2.0)))
    w = (1 - M.smoothstep(16, 32, abs(x - 4))) * (1 - M.smoothstep(14, 30, abs(y + 2)))
    return base * (1 - w) + 0.025 * noise.noise(Vector((x * 0.5, y * 1.8, 2.0))) * w


TRAIL_A = (8.6, -72.0)
TRAIL_B = (7.2, -3.95)
STRIP = (5.6, 10.4, -42.0, -3.4)  # fine footprint strip x0, x1, y0, y1


def trail_prints():
    return M.trail(TRAIL_A, TRAIL_B, step=0.75, gap=0.15, seed=11, wobble=0.18, rx=0.09, ry=0.2, depth=0.06)


def night_env(moon_e=0.9, stars=0.6, rot=(R(66), 0, R(-35)), hor=(0.022, 0.03, 0.055)):
    M.night_sky(stars=stars, hor=hor, zen=(0.003, 0.004, 0.01))
    return M.moon(rot=rot, energy=moon_e, color=MOON_COL, angle=1.0)


def ground(fine=False, decals=True, area=(-160, 160, -160, 160), res=2.0, snowmat=None):
    sm = snowmat or M.mat_snow("snow", tint=(0.8, 0.85, 0.95))
    pr = trail_prints()
    x0, x1, y0, y1 = area
    if fine:
        sx0, sx1, sy0, sy1 = STRIP
        nxf = int((sx1 - sx0) / 0.05) + 1
        nyf = int((sy1 - sy0) / 0.05) + 1
        near = [p for p in pr if p[1] > sy0 + 0.3]
        M.heightfield("snow_fine", sx0, sx1, sy0, sy1, nxf, nyf, H, mat=sm, prints=near)
        M.heightfield("snow_w", x0, sx0, y0, y1, int((sx0 - x0) / res) + 1, int((y1 - y0) / res) + 1, H, mat=sm)
        M.heightfield("snow_e", sx1, x1, y0, y1, int((x1 - sx1) / res) + 1, int((y1 - y0) / res) + 1, H, mat=sm)
        M.heightfield("snow_s", sx0, sx1, y0, sy0, 4, int((sy0 - y0) / res) + 1, H, mat=sm)
        M.heightfield("snow_n", sx0, sx1, sy1, y1, 4, int((y1 - sy1) / res) + 1, H, mat=sm)
        M.print_decals(near, H, name="print_core", color=(0.1, 0.13, 0.22), lift=-0.028, scale=0.75)
        M.print_decals([p for p in pr if p[1] <= sy0 + 0.3], H, name="print_far", color=(0.12, 0.15, 0.25), lift=0.015, scale=1.15)
    else:
        M.heightfield("snow", x0, x1, y0, y1, int((x1 - x0) / res) + 1, int((y1 - y0) / res) + 1, H, mat=sm)
        if decals:
            M.print_decals(pr, H, name="prints", color=(0.12, 0.15, 0.25), lift=0.03, scale=1.25)
    return sm


def forests(seed=4, south=True, north=True, sides=True, count=1.0):
    spots = []
    rnd = random.Random(seed)
    def band(x0, x1, y0, y1, c, h=(9, 16)):
        for _ in range(int(c * count)):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            spots.append((x, y, H(x, y) - 0.3, rnd.uniform(*h)))
    if north:
        band(-160, 160, 45, 120, 520)
    if south:
        band(-160, 160, -125, -74, 420)
    if sides:
        band(-160, -45, -74, 45, 160)
        band(55, 160, -74, 45, 160)
    m = M.mat_dusted("conifer_m", base=(0.01, 0.018, 0.016), snow=(0.55, 0.6, 0.7), thresh=0.6)
    return M.fast_conifers("forest", spots, mat=m, seed=seed)


def yard_trees(extra=()):
    bark = L.mat_noise_surface("bark", (0.015, 0.014, 0.013), (0.06, 0.05, 0.045), scale=6, bump=0.4, voronoi=False)
    for i, (x, y, h) in enumerate(((-9.5, -8.0, 9), (24, -7.5, 10), (-8.0, 9.0, 11), (-15, -2, 8)) + tuple(extra)):
        L.tree((x, y, H(x, y) - 0.1), height=h, seed=20 + i, mat=bark)


def farm_set(lit=True, fence_on=True, trees=True, **kw):
    F = M.farmstead(lit=lit, **kw)
    if fence_on:
        M.fence(-12.0, 4.0, -12.0, z_of=H, gate=(-1.0, 1.2), name="fence")
    if trees:
        yard_trees()
    # woodpile + cart shapes by the barn (scale cues)
    wood = M.mat_dusted("woodpile_m", base=(0.06, 0.04, 0.025), thresh=0.5)
    wp = L.prim("cube", loc=(19.6, -1.5, 0.6))
    wp.scale = (0.6, 2.2, 0.65)
    L.assign(wp, wood)
    return F


def farmer(name="farmer", hat=True, coat=True, color=(0.022, 0.022, 0.026)):
    p = L.char_figure(name, color=color, coat=coat)
    if hat:
        hm = L.mat_principled(name + "_hat", color, rough=0.8)
        b = L.prim("cyl", loc=(0, 0, 0.2), vertices=16, radius=0.17, depth=0.02)
        c = L.prim("cyl", loc=(0, 0, 0.27), vertices=16, radius=0.1, depth=0.13)
        for o in (b, c):
            L.assign(o, hm)
            o.parent = p["neck"]
    return p


def maid(name="maid", color=(0.03, 0.025, 0.028), bundle=True):
    p = L.char_figure(name, color=color, coat=True, height=1.62)
    m = L.mat_principled(name + "_shawl", (0.05, 0.035, 0.03), rough=0.9)
    sh = L.prim("sphere", loc=(0, 0, 0.55), segments=16, ring_count=8)
    sh.scale = (0.25, 0.17, 0.14)
    L.assign(sh, m)
    sh.parent = p["pelvis"]
    hood = L.prim("sphere", loc=(0, -0.01, 0.13), segments=12, ring_count=8)
    hood.scale = (0.12, 0.13, 0.14)
    L.assign(hood, m)
    hood.parent = p["neck"]
    sk = p["coat"]
    sk.scale = (sk.scale[0] * 1.05, sk.scale[1] * 1.1, sk.scale[2] * 1.25)
    sk.location.z -= 0.08
    if bundle:
        bd = L.prim("sphere", loc=(0, 0.0, -0.36), segments=10, ring_count=6)
        bd.scale = (0.14, 0.12, 0.1)
        L.assign(bd, L.mat_principled(name + "_bundle", (0.2, 0.17, 0.13), rough=0.9))
        bd.parent = p["elbowR"]
    return p


def snow_near(n, cam0, cam1, center, size, count=700, seed=3, clear=1.6):
    M.snowfall(center, size, n, count=count, radius=0.006, fall=0.6, wind=(0.4, 0.0, 0.0), seed=seed, cam=(cam0, cam1),
               clear=clear, emit=0.18)


def snow_far(n, center, size, count=1200, seed=9):
    M.snowfall(center, size, n, count=count, radius=0.008, fall=0.6, wind=(0.4, 0, 0), seed=seed, name="snowfar", emit=0.3)


# ============================================================================= S01 / S20 the footprints

S01_C0 = (8.15, -23.0, 0.55)
S01_C1 = (7.85, -13.0, 1.35)
S01_T0 = (7.5, -3.5, 0.95)
S01_T1 = (6.9, -3.5, 1.9)


def footprints_set(L, n, c0, c1, t0, t1, linear=True):
    night_env(moon_e=1.0, rot=(R(72), 0, R(-62)))
    ground(fine=True)
    forests()
    F = farm_set()
    # cold rim behind the farm so roof lines separate from the forest
    L.area((6, 25, 14), (R(-60), 0, R(180)), energy=900, size=30, color=(0.45, 0.55, 0.95), name="rim")
    cam, ct = cam_path(n, c0, c1, t0, t1, lens=28, ease=not linear)
    L.handheld(cam, n, amp=0.015, rate=0.8, rot_amp=0.004)
    snow_near(n, c0, c1, ((c0[0] + c1[0]) / 2, (c0[1] + c1[1]) / 2 + 4, 2.0), (8, 14, 4), count=600, seed=5, clear=1.4)
    snow_far(n, (7, -2, 6), (40, 30, 12), count=900)
    M.fog((7, -10, 3), (80, 60, 10), density=0.012)
    return cam


def S01(L, n):
    footprints_set(L, n, S01_C0, S01_C1, S01_T0, S01_T1)
    L.bake_static()


def S20(L, n):
    back = tuple(S01_C0[i] + (S01_C0[i] - S01_C1[i]) * (n / 89.0) for i in range(3))
    backt = tuple(S01_T0[i] + (S01_T0[i] - S01_T1[i]) * (n / 89.0) for i in range(3))
    footprints_set(L, n, back, S01_C0, backt, S01_T0)
    L.bake_static()


# ============================================================================= wide night farm (S03, S09, S10, S11, S02 plate)

W_C0 = (-14.0, -58.0, 4.0)
W_C1 = (-11.0, -46.0, 3.6)
W_T = (3.5, -2.0, 3.6)


def wide_night(L, n, lit=True, figures=False, fog_d=0.008, moon_e=0.9):
    night_env(moon_e=moon_e, rot=(R(64), 0, R(-25)))
    ground()
    forests()
    F = farm_set(lit=lit)
    L.area((6, 30, 16), (R(-55), 0, R(180)), energy=1500, size=40, color=(0.45, 0.55, 0.95), name="rim")
    M.fog((0, -10, 4), (120, 120, 14), density=fog_d)
    return F


def S03(L, n):
    F = wide_night(L, n)
    # farmer at the gate with a lantern, neighbour at the fence line (anonymous silhouettes)
    fa = farmer("farmer")
    fa["root"].location = (-1.0, -12.6, H(-1, -12.6))
    fa["root"].rotation_euler = (0, 0, R(200))
    fa["shoulderR"].rotation_euler = (0.25, 0, 0)
    lr, lp = M.lantern((0, 0, 0), energy=60, name="lantern", flicker_n=n)
    lr.parent = fa["elbowR"]
    lr.location = (0, 0.02, -0.62)
    nb = farmer("neighbour", hat=False, coat=True, color=(0.03, 0.028, 0.03))
    nb["root"].location = (-2.2, -15.0, H(-2.2, -15))
    nb["root"].rotation_euler = (0, 0, R(20))
    for t, s in (("L", 1), ("R", -1)):
        nb["shoulder" + t].rotation_euler = (0.1, 0, 0)
    # small gestures
    for f, a in ((1, 0.25), (40, 0.5), (70, 0.2), (n, 0.35)):
        fa["shoulderL"].rotation_euler = (a, 0, 0)
        fa["shoulderL"].keyframe_insert("rotation_euler", frame=f)
    cam, ct = cam_path(n, W_C0, W_C1, W_T, (3.0, -3.0, 3.3), lens=50)
    snow_far(n, (-5, -30, 6), (40, 50, 14), count=1500)
    L.bake_static()


def S09(L, n):
    # RESPECT BEAT: locked-off wide, the lit window goes dark. Nothing else happens.
    F = wide_night(L, n)
    k = 29
    M.window_keys(F, [(1, 1.0), (k - 1, 1.0), (k, 0.12), (k + 2, 0.85), (k + 4, 0.08), (k + 6, 0.6), (k + 8, 0.0), (n, 0.0)])
    for o in (bpy.data.materials["win_glow"].node_tree, F["win_light"].data):
        ad = o.animation_data
        for fc in L._fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    cam, ct = L.camera(loc=W_C1, target=(3.0, -3.0, 3.3), lens=50)
    cam.data.clip_end = 1500
    snow_far(n, (-5, -30, 6), (40, 50, 14), count=1500)
    L.bake_static()


def S10(L, n):
    F = wide_night(L, n, lit=False, moon_e=0.7)
    cam, ct = cam_path(n, (-20.0, -48.0, 3.5), (-8.0, -48.0, 3.5), (-2.0, 0.0, 3.5), (10.0, 0.0, 3.5), lens=40, ease=False)
    snow_far(n, (-5, -30, 6), (40, 50, 14), count=1200)
    L.bake_static()


def S11(L, n):
    F = wide_night(L, n, lit=False)
    top = F["chimney_top"]
    cam, ct = cam_path(n, (-9.0, -52.0, 3.0), (-1.2, -16.0, 8.4), (3.5, 0.0, 4.0), (top.x, top.y, top.z - 0.9), lens=35)
    cam.data.lens = 35
    cam.data.keyframe_insert("lens", frame=1)
    cam.data.lens = 85
    cam.data.keyframe_insert("lens", frame=n)
    # accelerate: ease-in towards the end (crash zoom)
    for o in (cam, ct, cam.data):
        for fc in L._fcurves(o.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "EXPO"
                kp.easing = "EASE_IN"
    L.handheld(cam, n, amp=0.02, rate=1.4, rot_amp=0.003)
    L.point((top.x - 1.5, top.y - 2.5, top.z + 1.0), energy=150, color=(0.55, 0.65, 1.0), radius=1, name="chim_rim")
    snow_far(n, (-3, -25, 7), (30, 50, 14), count=1300)
    L.bake_static()


def S02(L, n):
    # map plate: dim, defocused farm, slow 3% zoom
    F = wide_night(L, n, fog_d=0.012, moon_e=0.6)
    cam, ct = cam_path(n, W_C0, W_C0, W_T, W_T, lens=50)
    cam.data.lens = 50
    cam.data.keyframe_insert("lens", frame=1)
    cam.data.lens = 51.5
    cam.data.keyframe_insert("lens", frame=n)
    L.dof(cam, distance=20.0, fstop=0.9)
    snow_far(n, (-8, -40, 6), (30, 40, 14), count=1500)
    L.bake_static()


# ============================================================================= S04 attic

def S04(L, n):
    L.set_world((0.012, 0.014, 0.022), 1.0)
    floor = M.mat_planks("attic_floor", c1=(0.05, 0.035, 0.022), c2=(0.14, 0.095, 0.06), width=0.24, axis="X")
    boards = M.mat_planks("attic_roof", c1=(0.035, 0.025, 0.017), c2=(0.1, 0.07, 0.045), width=0.2, axis="Y")
    beam = L.mat_noise_surface("beam", (0.05, 0.035, 0.022), (0.13, 0.09, 0.055), scale=10, bump=0.3, voronoi=False)
    Wd, Ln, Hr, Kn = 5.0, 9.0, 3.0, 0.35
    fl = L.prim("plane", loc=(0, 0, 0), size=1)
    fl.scale = (Wd, Ln, 1)
    L.assign(fl, floor)
    hx = Wd / 2
    for s in (-1, 1):  # roof planes
        rv = [(s * hx, -Ln / 2, Kn), (s * hx, Ln / 2, Kn), (0, Ln / 2, Hr), (0, -Ln / 2, Hr)]
        M.mesh_obj(f"roof{s}", rv, [(0, 1, 2, 3)], mat=boards)
        kw = L.prim("cube", loc=(s * hx, 0, Kn / 2))
        kw.scale = (0.05, Ln / 2, Kn / 2)
        L.assign(kw, boards)
    end = M.mesh_obj("gable", [(-hx, Ln / 2, 0), (hx, Ln / 2, 0), (hx, Ln / 2, Kn), (0, Ln / 2, Hr), (-hx, Ln / 2, Kn)],
                     [(0, 1, 2, 3, 4)], mat=boards)
    rb = L.prim("cube", loc=(0, 0, Hr - 0.08))
    rb.scale = (0.08, Ln / 2, 0.09)
    L.assign(rb, beam)
    y = -Ln / 2 + 0.4
    while y < Ln / 2:
        for s in (-1, 1):
            ln = math.hypot(hx, Hr - Kn)
            ang = math.atan2(Hr - Kn, hx)
            r = L.prim("cube", loc=(s * hx / 2, y, (Kn + Hr) / 2 - 0.08))
            r.scale = (ln / 2, 0.05, 0.075)
            r.rotation_euler = (0, s * ang, 0)
            L.assign(r, beam)
        cb = L.prim("cube", loc=(0, y, 2.05))
        cb.scale = (hx * 0.34, 0.04, 0.06)
        L.assign(cb, beam)
        y += 0.8
    # moonlight slits between roof boards + a gable vent
    slit = L.mat_emission("slit", (0.45, 0.55, 0.9), 4.0)
    rnd = random.Random(4)
    for i in range(5):
        s = rnd.choice((-1, 1))
        yy = rnd.uniform(-1.5, 4.0)
        t = rnd.uniform(0.3, 0.75)
        x, z = s * hx * (1 - t), Kn + (Hr - Kn) * t
        sl = L.prim("cube", loc=(x * 0.995, yy, z - 0.01))
        sl.scale = (0.012, rnd.uniform(0.4, 1.1), 0.01)
        sl.rotation_euler = (0, s * math.atan2(Hr - Kn, hx), 0)
        L.assign(sl, slit)
        sl.visible_shadow = False
    vent = L.prim("cube", loc=(0, Ln / 2 - 0.02, 1.9))
    vent.scale = (0.25, 0.02, 0.06)
    L.assign(vent, slit)
    L.spot((0, Ln / 2 + 0.5, 1.95), (R(90), 0, R(180)), energy=60, size_deg=25, blend=0.6, color=(0.5, 0.6, 1.0), name="ventlight")
    # hay bales, a crate and old junk on the left; the right far corner stays empty
    hay = (0.32, 0.25, 0.12)
    for i, (x, y, z, rz) in enumerate(((-1.7, 0.5, 0.25, 0.05), (-1.65, 1.4, 0.25, -0.04), (-1.7, 0.95, 0.75, 0.1),
                                        (-1.6, 2.4, 0.25, 0.2), (-1.0, 3.6, 0.25, 0.0))):
        M.rounded_box((x, y, z), (0.9, 0.5, 0.48), hay, bevel=0.18, name=f"bale{i}", rot=(0, 0, rz))
    M.rounded_box((1.6, -1.6, 0.22), (0.55, 0.45, 0.44), (0.12, 0.08, 0.05), bevel=0.05, name="crate")
    # hatch frame in the floor around the camera
    hm = L.mat_principled("hatch", (0.03, 0.02, 0.012), rough=0.8)
    for (x, y, sx, sy) in ((0, -3.0, 0.5, 0.05), (-0.5, -3.45, 0.05, 0.5), (0.5, -3.45, 0.05, 0.5)):
        hb = L.prim("cube", loc=(x, y, 0.03))
        hb.scale = (sx, sy, 0.05)
        L.assign(hb, hm)
    lid = L.prim("cube", loc=(-0.95, -3.45, 0.04))
    lid.scale = (0.45, 0.5, 0.03)
    L.assign(lid, floor)
    # camera: head through the hatch, handheld, pan left -> right
    c0, c1 = (0.05, -3.55, 0.6), (0.1, -3.45, 0.66)
    cam, ct = cam_path(n, c0, c1, (-1.8, 1.5, 0.7), (1.9, 3.9, 0.45), lens=24)
    L.handheld(cam, n, amp=0.03, rate=0.9, rot_amp=0.01)
    # flashlight beam (warm) from just below-right of the camera, sweeping and stopping on the empty corner
    tg = M.empty("beam_tgt", (-1.9, 0.8, 0.6))
    for f, p in ((1, (-1.9, 0.8, 0.6)), (int(n * 0.35), (-0.6, 3.0, 1.2)), (int(n * 0.6), (1.3, 3.8, 0.6)), (int(n * 0.72), (1.95, 4.2, 0.35)),
                 (n, (1.95, 4.25, 0.35))):
        tg.location = p
        tg.keyframe_insert("location", frame=f)
    sp, _ = M.torch((0.25, -3.5, 0.5), (0, 0, 0), energy=900, size_deg=22)
    for c in list(sp.constraints):
        sp.constraints.remove(c)
    M.aim(sp, tg)
    L.flicker(sp, n, depth=0.05, rate=0.6, seed=2)
    L.cam_light(cam, energy=140, color=(0.6, 0.7, 0.95))
    L.area((0, 2.0, 2.6), (0, 0, 0), energy=160, size=4, color=(0.45, 0.55, 0.9), name="roofglow")
    L.water_volume(center=(0, 0.5, 1.5), size=(5.2, 9.5, 3.2), color=(0.8, 0.75, 0.65), density=0.02, anisotropy=0.5, name="dust")
    L.particle_cloud((0, 1.8, 1.3), (4.5, 5, 2.4), count=700, radius=0.0025, drift=(0.02, 0, -0.02), seed=7, nframes=n, name="motes",
                     mat=L.mat_principled("motes_m", (0.9, 0.82, 0.7), rough=1, emit=(0.9, 0.8, 0.65), emit_strength=0.4))
    # dust falling from a rafter at ~1.6 s (creak)
    fall = L.particle_cloud((0.9, 3.2, 2.35), (0.5, 0.4, 0.15), count=220, radius=0.005, drift=(0, 0, 0), seed=9, nframes=n, name="dustfall",
                            mat=L.mat_principled("df_m", (0.9, 0.85, 0.75), rough=1, emit=(0.9, 0.85, 0.7), emit_strength=0.6))
    fall.animation_data_clear()
    f0 = int(1.6 * 24)
    fall.location = (0, 0, 0)
    fall.scale = (1, 1, 0.01)
    fall.keyframe_insert("location", frame=f0)
    fall.keyframe_insert("scale", frame=f0)
    fall.location = (0, 0, -1.2)
    fall.scale = (1.3, 1.3, 6.0)
    fall.keyframe_insert("location", frame=n)
    fall.keyframe_insert("scale", frame=n)
    M.hide_until(fall, f0)
    L.bake_static()


# ============================================================================= S05 newspaper on the kitchen table

def S05(L, n):
    L.set_world((0.002, 0.002, 0.003), 1.0)
    M.desk(size=(3.0, 2.2))
    np_ = M.newspaper((0.02, 0.02, 0.0), rot_z=R(-8), name="news")
    for f, p, r in ((1, (-0.5, -0.22, 0.0), R(-24)), (14, (-0.04, 0.0, 0.0), R(-10)), (18, (0.02, 0.02, 0.0), R(-8))):
        np_.location = p
        np_.rotation_euler = (0, 0, r)
        np_.keyframe_insert("location", frame=f)
        np_.keyframe_insert("rotation_euler", frame=f)
    lr, lp = M.oil_lamp((0.42, 0.34, 0.0), energy=25, flicker_n=n)
    cup = M.coffee_cup((-0.36, 0.3, 0.0), color=(0.55, 0.52, 0.46))
    bread = M.rounded_box((-0.45, -0.28, 0.04), (0.22, 0.12, 0.08), (0.3, 0.17, 0.07), bevel=0.4, name="bread")
    L.area((0, 0, 3), (0, 0, 0), energy=6, size=2, color=(0.5, 0.6, 0.9), name="coldfill")
    cam, ct = L.camera(loc=(0.0, -0.05, 1.25), target=(0.0, 0.0, 0.0), lens=50)
    cam.constraints.clear()
    cam.rotation_euler = (0, 0, R(-2))
    cam.keyframe_insert("rotation_euler", frame=1)
    cam.rotation_euler = (0, 0, R(2))
    cam.keyframe_insert("rotation_euler", frame=n)
    cam.location = (0.0, -0.02, 1.2)
    cam.keyframe_insert("location", frame=n)
    L.bake_static()


# ============================================================================= S06 door, key hook, one key missing

def S06(L, n):
    L.set_world((0.004, 0.005, 0.009), 1.0)
    wallm = L.mat_noise_surface("wall", (0.16, 0.15, 0.13), (0.3, 0.28, 0.24), scale=4, bump=0.3, voronoi=False)
    wall = L.prim("plane", loc=(0, 0.02, 1.2), size=1, rot=(R(90), 0, 0))
    wall.scale = (4, 3, 1)
    L.assign(wall, wallm)
    door = L.prim("cube", loc=(-0.55, 0.0, 1.05))
    door.scale = (0.5, 0.03, 1.05)
    L.assign(door, M.mat_planks("door_m", c1=(0.05, 0.03, 0.018), c2=(0.14, 0.09, 0.05), width=0.14, axis="X"))
    iron = L.mat_principled("iron", (0.05, 0.048, 0.045), rough=0.45, metal=0.85)
    lp = L.prim("cube", loc=(-0.17, -0.04, 1.02))
    lp.scale = (0.07, 0.012, 0.13)
    L.assign(lp, iron)
    kh = L.prim("cube", loc=(-0.17, -0.055, 1.0))
    kh.scale = (0.012, 0.004, 0.03)
    L.assign(kh, L.mat_principled("keyhole", (0.0, 0.0, 0.0), rough=1))
    for z in (0.35, 1.75):
        hg = L.prim("cube", loc=(-0.75, -0.04, z))
        hg.scale = (0.3, 0.008, 0.025)
        L.assign(hg, iron)
    # key board: two painted outlines, one key hanging
    kb = L.prim("cube", loc=(0.42, -0.01, 1.42))
    kb.scale = (0.2, 0.015, 0.14)
    L.assign(kb, M.mat_planks("kb_m", c1=(0.08, 0.05, 0.03), c2=(0.2, 0.13, 0.07), width=0.08, axis="Z"))
    paint = (0.75, 0.72, 0.62)
    for i, x in enumerate((0.33, 0.51)):
        hook = L.prim("cyl", loc=(x, -0.045, 1.5), vertices=8, radius=0.005, depth=0.05, rot=(R(90), 0, 0))
        L.assign(hook, iron)
        ring = [(x + 0.028 * math.cos(a), -0.0265, 1.465 + 0.028 * math.sin(a)) for a in [2 * math.pi * k / 16 for k in range(17)]]
        M.glow_poly(ring, color=paint, strength=0.25, bevel=0.0025, name=f"outl_ring{i}")
        M.glow_poly([(x - 0.006, -0.0265, 1.437), (x - 0.006, -0.0265, 1.31), (x + 0.025, -0.0265, 1.31), (x + 0.025, -0.0265, 1.335),
                     (x + 0.006, -0.0265, 1.335), (x + 0.006, -0.0265, 1.437)], color=paint, strength=0.25, bevel=0.0025,
                    name=f"outl_shaft{i}")
    key = M.iron_key((0.33, -0.04, 1.472), rot=(0, 0, 0), scale=1.0)
    key.rotation_euler = (0, R(3), 0)
    key.keyframe_insert("rotation_euler", frame=1)
    key.rotation_euler = (0, R(-2), 0)
    key.keyframe_insert("rotation_euler", frame=n)
    # light: cold moon through a window off-frame left + warm practical off-frame right
    L.spot((-1.6, -1.2, 2.0), (R(70), 0, R(-55)), energy=120, size_deg=40, blend=0.5, color=(0.5, 0.6, 1.0), name="moonwin")
    L.spot((1.2, -1.0, 1.6), (R(85), 0, R(50)), energy=25, size_deg=50, blend=0.8, color=(1.0, 0.65, 0.35), name="warm")
    fk, fo = M.empty("f_key", (0.33, -0.04, 1.42)), M.empty("f_out", (0.51, -0.03, 1.4))
    cam, ct = cam_path(n, (0.3, -1.35, 1.45), (0.36, -1.25, 1.45), (0.4, 0, 1.42), (0.46, 0, 1.42), lens=85)
    L.dof(cam, distance=1.3, fstop=1.6)
    cam.data.dof.focus_distance = 1.3
    cam.data.dof.keyframe_insert("focus_distance", frame=6)
    cam.data.dof.focus_distance = 1.22
    cam.data.dof.keyframe_insert("focus_distance", frame=20)
    cam.data.dof.focus_distance = 1.23
    cam.data.dof.keyframe_insert("focus_distance", frame=n)
    L.particle_cloud((0.4, -0.5, 1.4), (0.8, 0.8, 0.6), count=180, radius=0.0015, drift=(0.005, 0, 0.005), seed=6, nframes=n, name="motes")
    L.bake_static()


# ============================================================================= S07 the previous maid leaves

def S07(L, n):
    night_env(moon_e=0.8, rot=(R(62), 0, R(-150)))
    ground(decals=False)
    forests()
    F = farm_set()
    bark = L.mat_noise_surface("bark2", (0.015, 0.014, 0.013), (0.06, 0.05, 0.045), scale=6, bump=0.4, voronoi=False)
    for i, y in enumerate((-20, -27, -34, -42, -50, -60)):
        for s in (-1, 1):
            x = -1.0 + s * (3.2 + 0.6 * math.sin(i * 2.1 + s))
            L.tree((x, y, H(x, y) - 0.1), height=7 + (i % 3), seed=40 + i * 2 + (s > 0), mat=bark)
    # warm light from the farm behind the camera: long shadow forward, warm rim on her back
    L.area((-0.6, -7.0, 2.0), (R(80), 0, R(180)), energy=600, size=1.5, color=(1.0, 0.6, 0.3), name="farmglow")
    md = maid()
    st, en = (-1.0, -13.4), (-1.25, -19.4)
    md["root"].rotation_euler = (0, 0, R(180))
    L.anim_walk(md, 1, n, stride=0.32, rate=0.85, travel=((st[0], st[1], H(*st)), (en[0], en[1], H(*en))))
    c0, c1 = (-0.4, -8.6, 2.3), (-0.45, -9.4, 2.25)
    cam, ct = cam_path(n, c0, c1, (-1.0, -24.0, 0.9), (-1.1, -25.0, 0.85), lens=35)
    L.handheld(cam, n, amp=0.008, rate=0.4, rot_amp=0.002)
    snow_near(n, c0, c1, (-1, -16, 2.0), (8, 12, 4), count=600, seed=6, clear=1.4)
    snow_far(n, (-1, -35, 5), (30, 30, 10), count=1000)
    M.fog((-1, -40, 3), (60, 60, 10), density=0.02)
    L.bake_static()


# ============================================================================= S08 the new maid arrives (dusk)

def S08(L, n):
    M.dawn_sky(hor=(0.2, 0.17, 0.18), mid=(0.11, 0.115, 0.14), zen=(0.035, 0.04, 0.055), strength=0.55)
    L.sun(rot=(R(70), 0, R(-30)), energy=0.35, color=(0.65, 0.7, 0.9), angle=R(30), name="dusk")
    ground(decals=False)
    forests()
    F = farm_set(window_energy=4.0, spill=40)
    m = bpy.data.materials["win_glow"]
    w2 = L.prim("cube", loc=(-3.0, -3.555, 1.5))
    w2.scale = (0.44, 0.02, 0.69)
    L.assign(w2, m)
    w3 = L.prim("cube", loc=(3.0, -3.555, 4.5))
    w3.scale = (0.44, 0.02, 0.69)
    L.assign(w3, m)
    L.point((-3.0, -4.3, 1.5), energy=30, color=(1.0, 0.62, 0.3), radius=0.4, name="spill2")
    md = maid("newmaid", color=(0.035, 0.03, 0.03), bundle=False)
    md["root"].rotation_euler = (0, 0, R(-90))
    st, en = (-8.2, -15.0), (-2.6, -14.4)
    L.anim_walk(md, 1, n, stride=0.32, rate=0.85, travel=((st[0], st[1], H(*st)), (en[0], en[1], H(*en))))
    cs = M.suitcase((0, 0, 0), size=(0.48, 0.16, 0.34), color=(0.22, 0.11, 0.05), name="case")
    cs.parent = md["elbowL"]
    cs.location = (0.0, 0.0, -0.62)
    cs.rotation_euler = (0, 0, R(90))
    c0, c1 = (-7.6, -20.6, 1.25), (-2.2, -20.4, 1.25)
    cam, ct = cam_path(n, c0, c1, (-8.0, -9.0, 2.0), (-2.6, -9.0, 2.0), lens=35, ease=False)
    L.area((-3, -9, 2.5), (R(-80), 0, 0), energy=300, size=3, color=(1.0, 0.65, 0.35), name="rimwarm")
    L.handheld(cam, n, amp=0.006, rate=0.5, rot_amp=0.002)
    L.area((-6, -24, 3), (R(70), 0, 0), energy=200, size=6, color=(0.55, 0.62, 0.85), name="fill")
    snow_near(n, c0, c1, (-5, -15, 2), (14, 10, 4), count=500, seed=8, clear=1.4)
    snow_far(n, (0, -5, 6), (40, 30, 12), count=900)
    M.fog((0, -10, 4), (120, 120, 14), density=0.01, color=(0.5, 0.5, 0.56))
    L.bake_static()


# ============================================================================= S12 smoke from the chimney (grey day)

def S12(L, n):
    M.dawn_sky(hor=(0.5, 0.52, 0.56), mid=(0.38, 0.4, 0.45), zen=(0.22, 0.25, 0.31), strength=0.9)
    L.sun(rot=(R(55), 0, R(-30)), energy=0.8, color=(0.85, 0.88, 0.95), angle=R(40), name="overcast")
    ground(decals=False, snowmat=M.mat_snow("daysnow", tint=(0.68, 0.7, 0.74)))
    forests()
    F = farm_set(lit=False)
    top = F["chimney_top"]
    M.cloud_volume((top.x + 0.9, top.y + 0.3, top.z + 5.2), (2.6, 2.6, 10.5), density=0.45, scale=1.2, contrast=(0.3, 0.78),
                   drift=(0.5, 0, 1.4), n=n, color=(0.85, 0.86, 0.9), name="smoke", emit=(0.55, 0.56, 0.6), emit_strength=0.5)
    M.fog((0, -10, 4), (140, 140, 16), density=0.012, color=(0.7, 0.72, 0.76))
    # two passers-by on the road stop and look up at the farm
    for i, (x, y) in enumerate(((-4.2, -16.0), (-3.3, -16.5))):
        p = farmer(f"walker{i}", hat=(i == 0), coat=True, color=(0.03, 0.03, 0.035))
        stop = int(n * 0.35) + i * 3
        p["root"].rotation_euler = (0, 0, R(-90))
        L.anim_walk(p, 1, stop, stride=0.3, rate=0.85, travel=((x - 1.8, y, H(x - 1.8, y)), (x, y, H(x, y))))
        p["root"].keyframe_insert("rotation_euler", frame=stop)
        p["root"].rotation_euler = (0, 0, R(-20 + 15 * i))
        p["root"].keyframe_insert("rotation_euler", frame=stop + 10)
        p["neck"].rotation_euler = (0, 0, 0)
        p["neck"].keyframe_insert("rotation_euler", frame=stop + 6)
        p["neck"].rotation_euler = (R(-18), 0, 0)
        p["neck"].keyframe_insert("rotation_euler", frame=stop + 16)
        for t in ("L", "R"):
            for k in ("hip", "knee", "shoulder"):
                p[k + t].rotation_euler = (0, 0, 0)
                p[k + t].keyframe_insert("rotation_euler", frame=stop + 6)
    cam, ct = cam_path(n, (-6.5, -27.0, 1.7), (-6.5, -27.0, 1.9), (-3.0, -15.0, 1.2), (top.x, top.y, top.z + 1.5), lens=50)
    L.bake_static()


# ============================================================================= S13 barn: someone fed the cattle

def S13(L, n):
    L.set_world((0.02, 0.022, 0.026), 1.0)
    planks = M.mat_planks("bplanks", c1=(0.05, 0.035, 0.022), c2=(0.13, 0.09, 0.055), width=0.2, axis="X")
    floor = L.mat_noise_surface("bfloor", (0.06, 0.045, 0.03), (0.16, 0.12, 0.07), scale=10, bump=0.3, voronoi=False)
    fl = L.prim("plane", loc=(0, 1.0, 0), size=1)
    fl.scale = (14, 9, 1)
    L.assign(fl, floor)
    # back wall of planks with light gaps
    x = -6.0
    while x < 6.0:
        w = random.Random(int(x * 10)).uniform(0.18, 0.26)
        pk = L.prim("cube", loc=(x + w / 2, 3.9, 1.6))
        pk.scale = (w / 2 - 0.03, 0.03, 1.6)
        L.assign(pk, planks)
        x += w
    for s in (-1, 1):
        sw = L.prim("cube", loc=(s * 6.0, 1.0, 1.6))
        sw.scale = (0.05, 3.5, 1.6)
        L.assign(sw, planks)
    roof = L.prim("cube", loc=(0, 1.0, 3.25))
    roof.scale = (6.2, 3.5, 0.05)
    L.assign(roof, planks)
    front = L.prim("cube", loc=(0, -2.6, 1.6))
    front.scale = (6.2, 0.05, 1.6)
    L.assign(front, planks)
    front.visible_camera = False
    beam = L.mat_noise_surface("bbeam", (0.05, 0.035, 0.022), (0.13, 0.09, 0.055), scale=10, bump=0.3, voronoi=False)
    for xx in (-3.3, -1.1, 1.1, 3.3):  # stall partitions
        p = L.prim("cube", loc=(xx, 2.3, 0.65))
        p.scale = (0.04, 1.4, 0.65)
        L.assign(p, planks)
        post = L.prim("cube", loc=(xx, 0.85, 0.75))
        post.scale = (0.07, 0.07, 0.75)
        L.assign(post, beam)
    rail = L.prim("cube", loc=(0, 0.85, 1.45))
    rail.scale = (6, 0.05, 0.05)
    L.assign(rail, beam)
    # trough with fresh hay
    tr = L.prim("cube", loc=(0, 0.0, 0.35))
    tr.scale = (5.6, 0.32, 0.25)
    L.assign(tr, beam)
    hay = L.mat_noise_surface("hay", (0.3, 0.22, 0.09), (0.62, 0.5, 0.24), scale=40, bump=0.6, voronoi=False, rough=0.9)
    hy = M.heightfield("hay", -5.5, 5.5, -0.27, 0.27, 140, 8,
                       lambda x, y: 0.62 + 0.08 * (1 - (y / 0.3) ** 2) + 0.04 * noise.noise(Vector((x * 6, y * 6, 0))), mat=hay)
    # cattle, heads down in the trough
    cows = []
    for i, (x, hd) in enumerate(((-2.2, 0.75), (0.0, 0.65), (2.2, 0.8))):
        c = M.cow((x, 1.65, 0), rot_z=R(-90), color=(0.28 + 0.05 * i, 0.16, 0.08), name=f"cow{i}", head_down=hd, seed=i)
        cows.append(c)
        for f in range(1, n + 1, 6):
            c["neck"].rotation_euler = (0, hd + 0.06 * math.sin(f * 0.35 + i * 2), 0.04 * math.sin(f * 0.2 + i))
            c["neck"].keyframe_insert("rotation_euler", frame=f)
            c["tail"].rotation_euler = (0.15 * math.sin(f * 0.25 + i), 0.12, 0)
            c["tail"].keyframe_insert("rotation_euler", frame=f)
    # grey daylight through the gaps (volumetric shafts) + soft fill
    L.sun(rot=(R(-58), 0, R(12)), energy=9.0, color=(0.8, 0.85, 0.95), angle=R(2), name="daylight")
    L.area((0, -1.8, 2.8), (R(20), 0, 0), energy=260, size=5, color=(0.7, 0.75, 0.85), name="fill")
    L.water_volume(center=(0, 1.0, 1.6), size=(12, 6, 3.2), color=(0.85, 0.82, 0.75), density=0.06, anisotropy=0.7, name="barnair")
    L.particle_cloud((0, 2.2, 1.6), (8, 2.6, 2.4), count=700, radius=0.002, drift=(0.02, 0, 0.01), seed=4, nframes=n, name="dust",
                     mat=L.mat_principled("dust_m", (0.9, 0.85, 0.75), rough=1, emit=(0.8, 0.75, 0.6), emit_strength=0.25))
    cam, ct = cam_path(n, (-2.8, -1.7, 1.15), (0.9, -1.7, 1.2), (-1.6, 1.2, 0.75), (2.0, 1.2, 0.8), lens=35, ease=False)
    L.handheld(cam, n, amp=0.006, rate=0.5, rot_amp=0.002)
    L.bake_static()


# ============================================================================= evidence board (S14, S15, S17)

def board_room(L, lamp_energy=220):
    L.set_world((0.003, 0.003, 0.004), 1.0)
    B = M.evidence_board(w=3.2, h=5.0, lamp_energy=lamp_energy)
    L.area((-2.5, -3.5, 1.0), (R(75), 0, R(-35)), energy=20, size=3, color=(0.5, 0.6, 0.85), name="coldfill")
    return B


def S14(L, n):
    B = board_room(L)
    hits = [8, 25, 42]
    specs = (("SMOKE", (-0.5, 1.95)), ("CATTLE FED", (0.5, 1.62)), ("BREAD EATEN", (-0.48, 1.2)))
    cards = []
    for i, ((txt, (x, z)), f) in enumerate(zip(specs, hits)):
        c = M.paper_card(txt, (x, -0.012, z), size=(0.92, 0.5), rot_y=(-0.05, 0.04, 0.03)[i], badge=None, name=f"c{i}", text_size=0.15)
        M.slam_in(c, f, lead=5)
        M.hide_until(c, f - 5)
        cards.append(c)
    big = M.paper_card("SOMEONE\nSTAYED", (0.3, -0.014, 0.6), size=(1.1, 0.66), rot_y=-0.03, badge=None, name="cbig", text_size=0.17,
                       paper=(0.72, 0.6, 0.5))
    fbig = 58
    M.slam_in(big, fbig, lead=6)
    M.hide_until(big, fbig - 6)
    for i, c in enumerate(cards):
        p = c.location
        s = M.red_string([(p.x, -0.045, p.z + 0.19), (0.3, -0.045, 0.6 + 0.27)], name=f"str{i}")
        M.hide_until(s, (hits[i] if i < 2 else hits[2]) + 2 if False else fbig + 2)
    cam, ct = cam_path(n, (0.0, -5.0, 0.75), (0.0, -4.4, 0.75), (0.0, 0, 0.62), (0.0, 0, 0.62), lens=50)
    M.shake(cam, [h for h in hits] + [fbig], amp=0.012, decay=7)
    L.bake_static()


def grid_positions(cols, rows, x0, x1, z0, z1, seed=2, skip=()):
    rnd = random.Random(seed)
    out = []
    for j in range(rows):
        for i in range(cols):
            if (i, j) in skip:
                continue
            x = x0 + (x1 - x0) * (i + 0.5) / cols + rnd.uniform(-0.03, 0.03)
            z = z1 - (z1 - z0) * (j + 0.5) / rows + rnd.uniform(-0.03, 0.03)
            out.append((x, z))
    return out


def S15(L, n):
    B = board_room(L, lamp_energy=240)
    pos = grid_positions(6, 8, -1.5, 1.5, -2.3, 2.3, seed=5)
    cards = M.qmark_cards(pos, size=(0.38, 0.46))
    rnd = random.Random(3)
    order = list(range(len(cards)))
    rnd.shuffle(order)
    for k, i in enumerate(order):
        M.pop_in(cards[i], 2 + int(k * 38 / len(cards)), dur=3)
    # red rubber stamp hits at 1.8 s
    ink = L.mat_principled("stamp_ink", (0.6, 0.03, 0.02), rough=0.6, emit=(0.6, 0.03, 0.02), emit_strength=0.6)
    st = M.empty("stamp", (0, -0.05, 0.9))
    t = L.text3d("NO CONVICTION", loc=(0, 0, 0), size=0.32, extrude=0.0, mat=ink, name="stamp_t")
    t.data.font = M._font(M.F_ANTON) or t.data.font
    t.data.align_y = "CENTER"
    t.parent = st
    fr = M.glow_poly(M.rect_pts(0, 0, 2.85, 0.5, y=0.0), color=(0.6, 0.03, 0.02), strength=0.6, bevel=0.018, closed=True, name="stamp_box")
    fr.parent = st
    st.rotation_euler = (0, R(-8), 0)
    f = 44
    st.scale = (2.2,) * 3
    st.keyframe_insert("scale", frame=f - 3)
    st.scale = (0.96,) * 3
    st.keyframe_insert("scale", frame=f)
    st.scale = (1.0,) * 3
    st.keyframe_insert("scale", frame=f + 3)
    M.hide_until(st, f - 3)
    cam, ct = cam_path(n, (0.0, -4.4, 0.95), (0.0, -6.6, 0.8), (0.0, 0, 0.95), (0.0, 0, 0.75), lens=50)
    cam.data.lens = 50
    cam.data.keyframe_insert("lens", frame=1)
    cam.data.lens = 35
    cam.data.keyframe_insert("lens", frame=n)
    M.shake(cam, [f], amp=0.02, decay=8)
    L.particle_cloud((0, -0.6, 0.6), (3, 0.8, 3), count=250, radius=0.002, drift=(0.01, 0, 0.01), seed=3, nframes=n, name="motes")
    L.bake_static()


def S17(L, n):
    B = board_room(L, lamp_energy=240)
    keep = (2, 3)
    pos = grid_positions(6, 8, -1.5, 1.5, -2.3, 2.3, seed=5, skip=(keep,))
    cards = M.qmark_cards(pos, size=(0.38, 0.46))
    rnd = random.Random(7)
    for i, c in enumerate(cards):
        p = c.location.copy()
        f0 = 4 + int(rnd.uniform(0, 26))
        c.keyframe_insert("location", frame=f0)
        side = -1 if p.x < 0 else 1
        c.location = (p.x + side * rnd.uniform(4.5, 6.0), p.y - 0.05, p.z + rnd.uniform(-0.4, 0.4))
        c.keyframe_insert("location", frame=f0 + 10)
    # the one remaining card, face down (blank back), then a black sheet slides over it
    kx = -1.5 + 3.0 * (keep[0] + 0.5) / 6
    kz = 2.3 - 4.6 * (keep[1] + 0.5) / 8
    back = L.prim("plane", loc=(kx, -0.012, kz), size=1, rot=(R(90), 0, 0), name="facedown")
    back.scale = (0.38, 0.46, 1)
    L.assign(back, M.mat_paper("back_m", (0.3, 0.3, 0.3)))
    pin = L.prim("sphere", loc=(kx, -0.03, kz + 0.18), radius=0.018, segments=8, ring_count=5)
    L.assign(pin, L.mat_principled("pin_m", (0.6, 0.04, 0.03), rough=0.3))
    sroot = M.empty("sheetroot", (kx, -0.04, kz + 1.6))
    sheet = L.prim("plane", loc=(0, 0, 0), size=1, rot=(R(90), 0, 0), name="blacksheet")
    sheet.scale = (0.46, 0.56, 1)
    sheet.parent = sroot
    L.assign(sheet, L.mat_principled("black_m", (0.006, 0.006, 0.007), rough=0.5))
    fs = int(1.3 * 24)
    sroot.keyframe_insert("location", frame=1)
    sroot.keyframe_insert("location", frame=fs)
    sroot.location = (kx, -0.04, kz - 0.03)
    sroot.keyframe_insert("location", frame=fs + 9)
    tag = M.paper_card("NOT NAMED", (0, -0.006, -0.12), size=(0.36, 0.2), badge=None, name="tag", text_size=0.055,
                       paper=(0.72, 0.68, 0.58))
    tag.parent = sroot
    tag.rotation_euler = (0, R(-4), 0)
    pin2 = L.prim("sphere", loc=(0, -0.02, 0.24), radius=0.02, segments=8, ring_count=5)
    L.assign(pin2, L.mat_principled("pin2_m", (0.6, 0.04, 0.03), rough=0.3))
    pin2.parent = sroot
    M.hide_until(sroot, fs)
    # lamp narrows to a spot on the single card
    sp = L.spot((kx, -2.2, kz + 1.3), (0, 0, 0), energy=700, size_deg=60, blend=0.35, color=(1.0, 0.75, 0.45), name="narrow")
    M.aim(sp, M.empty("narrow_t", (kx, 0, kz)))
    sp.data.spot_size = R(60)
    sp.data.keyframe_insert("spot_size", frame=1)
    sp.data.spot_size = R(16)
    sp.data.keyframe_insert("spot_size", frame=int(n * 0.6))
    for lt, e0 in ((B["lamp"], B["lamp"].data.energy), (B["fill"], B["fill"].data.energy)):
        lt.data.keyframe_insert("energy", frame=10)
        lt.data.energy = e0 * 0.25
        lt.data.keyframe_insert("energy", frame=int(n * 0.6))
    cam, ct = cam_path(n, (kx * 0.4, -5.2, kz * 0.4 + 0.3), (kx, -2.6, kz - 0.05), (kx * 0.4, 0, kz * 0.4 + 0.3), (kx, 0, kz - 0.05), lens=50)
    cam.data.lens = 50
    cam.data.keyframe_insert("lens", frame=1)
    cam.data.lens = 85
    cam.data.keyframe_insert("lens", frame=n)
    L.particle_cloud((kx, -0.5, kz), (1.0, 0.6, 1.0), count=120, radius=0.0015, drift=(0.01, 0, 0.01), seed=3, nframes=n, name="motes")
    L.bake_static()


# ============================================================================= S16 2007 archive desk

def S16(L, n):
    L.set_world((0.004, 0.004, 0.006), 1.0)
    M.desk(size=(3.0, 2.2))
    fd = M.case_folder((0.02, -0.12, 0.0), rot_z=R(4), size=(0.36, 0.27))
    cv = fd["cover"]
    cv.rotation_euler = (0, 0, 0)
    cv.keyframe_insert("rotation_euler", frame=12)
    cv.rotation_euler = (0, R(-178), 0)
    cv.keyframe_insert("rotation_euler", frame=40)
    lap, hinge = M.laptop((0.1, 0.3, 0.0), rot_z=R(-8), open_deg=125, strength=2.6)
    pm = M.mat_paper("oldpaper", (0.58, 0.5, 0.33))
    rnd = random.Random(3)
    for i in range(5):
        pg = L.prim("plane", loc=(rnd.uniform(-0.55, -0.3), rnd.uniform(-0.3, 0.3), 0.001 + i * 0.0008), size=1,
                    rot=(0, 0, rnd.uniform(-0.4, 0.4)))
        pg.scale = (0.21, 0.297, 1)
        L.assign(pg, pm)
    M.desk_lamp((-0.55, 0.45, 0.0), (-0.1, 0.0, 0.0), energy=35, rot_z=R(200))
    L.point((0.1, 0.15, 0.25), energy=4, color=(0.5, 0.65, 1.0), radius=0.2, name="screenglow")
    cam, ct = cam_path(n, (0.08, -0.45, 1.5), (0.08, -0.35, 1.25), (0.08, 0.04, 0.0), (0.08, 0.06, 0.0), lens=50)
    L.bake_static()


# ============================================================================= S18 memorial

def S18(L, n):
    night_env(moon_e=0.6, stars=0.8, rot=(R(60), 0, R(-150)))
    ground(decals=False)
    forests()
    stone_m = L.mat_noise_surface("stone", (0.2, 0.2, 0.2), (0.4, 0.39, 0.37), scale=8, bump=0.4)
    sx, sy = -24.0, -40.0
    z = H(sx, sy)
    st = M.headstone((sx, sy, z - 0.05), w=0.75, h=1.25, d=0.2, mat=stone_m, kind=0, name="memorial")
    st.rotation_euler = (0, 0, R(-8))
    iron = L.mat_principled("iron", (0.03, 0.03, 0.032), rough=0.5, metal=0.8)
    cr = M.empty("cross", (sx, sy, z + 1.2))
    cr.rotation_euler = (0, 0, R(-8))
    for (lz, scl) in ((0.32, (0.018, 0.018, 0.32)), (0.42, (0.15, 0.018, 0.018))):
        b = L.prim("cube", loc=(0, 0, lz))
        b.scale = scl
        L.assign(b, iron)
        b.parent = cr
    snowcap = M.rounded_box((sx, sy, z + 1.18), (0.6, 0.18, 0.06), (0.8, 0.84, 0.92), bevel=0.4, name="cap",
                            mat=M.mat_snow("cap_m"), rot=(0, 0, R(-8)))
    snowcap.hide_render = True
    lr, lp = M.lantern((sx + 0.55, sy - 0.25, z - 0.02), energy=12, name="lantern", flicker_n=n)
    L.area((sx + 1.5, sy - 4, z + 1.5), (R(70), 0, R(20)), energy=25, size=2, color=(0.5, 0.6, 0.95), name="front")
    L.area((sx - 2, sy + 4, z + 3), (R(-50), 0, R(200)), energy=150, size=3, color=(0.5, 0.6, 1.0), name="rim")
    c0 = (sx + 0.9, sy - 4.2, z + 0.85)
    c1 = (sx + 0.6, sy - 3.0, z + 0.8)
    cam, ct = cam_path(n, c0, c1, (sx + 0.1, sy, z + 0.35), (sx + 0.05, sy, z + 0.4), lens=50)
    snow_near(n, c0, c1, (sx, sy - 1, z + 1.5), (5, 5, 3), count=400, seed=4, clear=1.0)
    snow_far(n, (sx, sy + 8, z + 3), (20, 16, 8), count=600)
    M.fog((sx, sy + 30, z + 3), (80, 60, 10), density=0.015)
    L.bake_static()


# ============================================================================= S19 from the forest edge

def S19(L, n):
    night_env(moon_e=0.7, rot=(R(64), 0, R(-25)))
    ground()
    forests(south=False)
    F = farm_set(lit=False)
    L.area((6, 30, 16), (R(-55), 0, R(180)), energy=1500, size=40, color=(0.45, 0.55, 0.95), name="rim")
    # foreground tree line: trunks + low branches the camera pushes past
    bark = M.mat_dusted("trunk_m", base=(0.02, 0.018, 0.016), thresh=0.6)
    sp = []
    rnd = random.Random(8)
    for i in range(60):
        x, y = rnd.uniform(-30, 40), rnd.uniform(-110, -73)
        if abs(x - 6.5) < 4 and y > -80:
            continue
        sp.append((x, y, H(x, y) - 0.3, rnd.uniform(10, 16)))
    M.conifer_forest("treeline", sp, mat=bark, seed=3)
    trunk = L.prim("cyl", loc=(6.2, -70.8, H(6.2, -70.8) + 5), vertices=14, radius=0.32, depth=10)
    L.assign(trunk, bark)
    c0, c1 = (6.6, -72.6, 1.8), (6.5, -69.0, 2.0)
    cam, ct = cam_path(n, c0, c1, (6.0, -2.0, 3.0), (6.0, -2.0, 3.0), lens=50)
    L.handheld(cam, n, amp=0.01, rate=0.5, rot_amp=0.002)
    snow_far(n, (6, -50, 5), (30, 40, 12), count=1200)
    M.fog((6, -35, 4), (120, 80, 14), density=0.01)
    L.bake_static()
