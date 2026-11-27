"""MURDER-01 - Dyatlov Pass (1959) + Gaume & Puzrin slab-avalanche model (2021).
Shot builders: def SXX(L, n). Builders for snow slope / tent / diagrams live in PIPELINE/blender/lib_murder.py.
World layout for the 3D night slope: tent at origin, ridge along X, slope rises toward +Y, slit on the -Y
(downhill) roof panel, tracks lead downhill toward -Y, tree line far down at -Y.
"""
import os, sys, math, importlib
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_murder as M
importlib.reload(M)
from mathutils import Vector

R = math.radians
SLOPE = 20.0


# ----------------------------------------------------------------------------- shared environment

def night(stars=1.0, moon_rot=(R(62), 0, R(-28)), moon_e=1.6, hor=(0.018, 0.024, 0.045)):
    M.night_sky(stars=stars, hor=hor)
    return M.moon(rot=moon_rot, energy=moon_e)


def slope_terrain(x=(-30, 30), y=(-30, 40), res=0.25, platform=True, prints=None, seed=0, name="slope", lower=0.0):
    h0 = M.make_slope_h(SLOPE, seed)
    pz = h0(0, -1.25)
    h = M.make_slope_h(SLOPE, seed, platform=(0, 0, 2.3, 1.25, pz, 1.1) if platform else None, base=-lower)
    nx = int((x[1] - x[0]) / res) + 1
    ny = int((y[1] - y[0]) / res) + 1
    t = M.heightfield(name, x[0], x[1], y[0], y[1], nx, ny, h, mat=M.mat_snow(name + "_m"), prints=prints)
    return h, pz, t


def tent_at(pz, slit=True, gap=0.07, inner=12.0, crush=0.0, snow_amt=0.55, banks=True, flap_w=None):
    t = M.tent(loc=(0, 0, pz), slit=slit, gap=gap, inner_light=inner, crush=crush, snow_amt=snow_amt, flap_w=flap_w)
    if banks:
        sm = M.mat_snow("bank_m")
        M.snow_bank((0, 1.2, pz + 0.05), (2.5, 0.42, 0.36), seed=2, mat=sm, name="bankB")
        M.snow_bank((-2.15, 0.1, pz), (0.38, 1.25, 0.3), seed=3, mat=sm, name="bankL")
        M.snow_bank((2.15, 0.0, pz), (0.38, 1.25, 0.26), seed=4, mat=sm, name="bankR")
        M.snow_bank((-0.9, -1.08, pz - 0.03), (1.4, 0.16, 0.15), seed=5, mat=sm, name="bankF1")
        M.snow_bank((1.5, -1.08, pz - 0.03), (0.8, 0.16, 0.13), seed=6, mat=sm, name="bankF2")
    return t


def forest_band(h, y0, y1, x0=-60, x1=60, count=160, seed=4, hrange=(8, 15)):
    spots = M.scatter_spots((x0, x1, y0, y1), count, h, seed=seed, h=hrange)
    return M.conifer_forest("forest", spots, seed=seed)


def lin(obj):
    M.set_interp(obj, "LINEAR")


# ----------------------------------------------------------------------------- tent close-up (S01 / S20 / S21)

S01_CAM0 = (-3.3, -2.75, 1.2)
S01_CAM1 = (-2.6, -2.2, 1.08)
S01_TGT = (0.25, -0.45, 0.5)


def tent_closeup(L, n, cam_from, cam_to, tgt_from, tgt_to, torch_keys, flap_base=0.75, flap_amp=0.35, lens=38,
                 hand=0.02, snow_count=900):
    moon = night(stars=0.6, moon_rot=(R(58), 0, R(-35)), moon_e=1.3)
    h, pz, _ = slope_terrain(x=(-25, 25), y=(-25, 35), res=0.2)
    t = tent_at(pz, inner=30.0, snow_amt=0.0)
    M.anim_flaps(t, n, base=flap_base, amp=flap_amp, rate=1.8, seed=3)
    # torch from camera-left
    tr, tg = M.torch((-3.6, -1.7, 1.4 + pz), torch_keys[0][1], energy=480, size_deg=15)
    for f, p in torch_keys:
        tg.location = (p[0], p[1], p[2] + pz)
        tg.keyframe_insert("location", frame=f)
    L.flicker(tr, n, depth=0.2, rate=0.4, seed=5)
    # cold rim from upslope behind the tent (moon glow on the snow edge)
    L.area((0.5, 3.5, 3.0 + pz), (R(-60), 0, 0), energy=60, size=4, color=(0.5, 0.6, 1.0), name="rim")
    cpath = ((cam_from[0], cam_from[1], cam_from[2] + pz), (cam_to[0], cam_to[1], cam_to[2] + pz))
    M.snowfall((-0.6, -1.4, 1.0 + pz), (5, 2.5, 2.6), n, count=snow_count, radius=0.004, fall=0.5, wind=(1.4, 0.2, 0), seed=11,
               cam=cpath, clear=0.9, emit=0.15)
    M.snowfall((0.0, 6.0, 2.0 + pz), (16, 10, 5), n, count=700, radius=0.015, fall=0.5, wind=(1.6, 0, 0), seed=12, name="snowfar",
               emit=0.15)
    M.fog((0, 6, 2 + pz), (40, 30, 8), density=0.025)
    cam, ct = L.camera(loc=(cam_from[0], cam_from[1], cam_from[2] + pz), target=(tgt_from[0], tgt_from[1], tgt_from[2] + pz), lens=lens)
    L.cam_keys(cam, [(1, (cam_from[0], cam_from[1], cam_from[2] + pz)), (n, (cam_to[0], cam_to[1], cam_to[2] + pz))])
    lin(cam)
    ct.location = (tgt_from[0], tgt_from[1], tgt_from[2] + pz)
    ct.keyframe_insert("location", frame=1)
    ct.location = (tgt_to[0], tgt_to[1], tgt_to[2] + pz)
    ct.keyframe_insert("location", frame=n)
    lin(ct)
    if hand:
        L.handheld(cam, n, amp=hand, rate=0.7)
    return cam, pz


def S01(L, n):
    # torch sweeps across the canvas from the left and lands on the slit
    s = S01_TGT
    keys = [(1, (-1.75, -0.8, 0.5)), (int(n * 0.45), (-0.3, -0.62, 0.66)), (int(n * 0.62), (0.33, -0.55, 0.76)),
            (n, (0.37, -0.55, 0.74))]
    tent_closeup(L, n, S01_CAM0, S01_CAM1, S01_TGT, (0.3, -0.5, 0.52), keys)
    L.bake_static()


def S20(L, n):
    # medium close, torch beam resting on the slit, very slow push
    s = S01_TGT
    keys = [(1, (0.31, -0.55, 0.74)), (n, (0.35, -0.55, 0.77))]
    tent_closeup(L, n, (-0.35, -2.6, 0.95), (-0.25, -2.3, 0.92), (0.3, -0.5, 0.68), (0.32, -0.5, 0.7), keys,
                 flap_base=0.55, flap_amp=0.2, lens=40, hand=0.01)
    L.bake_static()


def S21(L, n):
    # loop: pushes in and ends exactly on S01 frame-1 framing
    keys = [(1, (-1.95, -0.85, 0.45)), (n, (-1.75, -0.8, 0.5))]
    back = tuple(S01_CAM0[i] + (S01_CAM0[i] - S01_CAM1[i]) * 0.9 for i in range(3))
    tent_closeup(L, n, back, S01_CAM0, S01_TGT, S01_TGT, keys)
    L.bake_static()


# ----------------------------------------------------------------------------- S02 footprints

def S02(L, n):
    night(stars=0.8, moon_rot=(R(66), 0, R(70)), moon_e=2.0)
    prints = []
    prints += M.trail((-0.15, -1.2), (-0.6, -22), seed=1, depth=0.03)
    prints += M.trail((0.55, -1.6), (0.9, -22), seed=2, depth=0.028, rx=0.06, ry=0.14)
    prints += M.trail((-1.1, -2.5), (-1.8, -22), seed=3, depth=0.025, skip=0.1)
    h, pz, _ = slope_terrain(x=(-4.5, 4.5), y=(-24, 2.0), res=0.045, prints=prints, name="patch")
    # wider low-res surroundings, slightly lowered beneath the detailed patch
    hb = M.make_slope_h(SLOPE, 0, base=-0.06)
    for nm, xr in (("sideL", (-40, -4.4)), ("sideR", (4.4, 40))):
        M.heightfield(nm, xr[0], xr[1], -60, 30, 60, 90, hb, mat=M.mat_snow(nm + "_m"))
    M.heightfield("far", -40, 40, -120, -23.9, 60, 60, hb, mat=M.mat_snow("far_m"))
    forest_band(hb, -110, -80, count=120)
    M.snowfall((0, -3.5, 0.6 + pz), (4, 6, 1.6), n, count=1400, radius=0.004, fall=0.35, wind=(1.8, -0.3, 0), seed=21,
               cam=((0, -0.4, pz + 0.3), (0, -3.2, pz - 0.6)), clear=0.8, emit=0.12)
    M.snowfall((0, -12, 2 + pz), (16, 14, 5), n, count=900, radius=0.015, fall=0.4, wind=(2.0, 0, 0), seed=22, name="snowfar", emit=0.12)
    M.fog((0, -30, -5 + pz), (80, 70, 25), density=0.045)
    y0, y1 = -0.4, -3.2
    c0 = (0.05, y0, h(0.05, y0) + 0.32)
    c1 = (0.0, y1, h(0.0, y1) + 0.42)
    cam, ct = L.camera(loc=c0, target=(-0.2, y0 - 3.0, h(-0.2, y0 - 3) - 0.1), lens=24)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    lin(cam)
    ct.keyframe_insert("location", frame=1)
    ct.location = (-0.4, y1 - 6.0, h(-0.4, y1 - 6) + 0.9)
    ct.keyframe_insert("location", frame=n)
    L.handheld(cam, n, amp=0.012, rate=0.5)
    L.bake_static()


# ----------------------------------------------------------------------------- S03 map plate (aerial Urals)

def S03(L, n):
    night(stars=1.2, moon_rot=(R(66), 0, R(55)), moon_e=1.6, hor=(0.05, 0.065, 0.11))
    L.sun(rot=(R(50), 0, R(-130)), energy=0.25, color=(0.4, 0.5, 0.8), name="fillsun")
    o, h = M.mountains("urals", size=900, res=230, height=80, seed=3)
    spots = []
    import random
    rnd = random.Random(3)
    while len(spots) < 500:
        x, y = rnd.uniform(-450, 450), rnd.uniform(-450, 200)
        z = h(x, y)
        if z < 12:
            spots.append((x, y, z - 1, rnd.uniform(8, 14)))
    M.conifer_forest("taiga", spots, seed=3, bare_frac=0.0)
    M.snowfall((0, -300, 160), (60, 40, 50), n, count=500, radius=0.05, fall=1.5, wind=(4, 0, 0), seed=31,
               cam=((-10, -380, 190), (10, -330, 170)), clear=12, emit=0.1)
    cam, ct = L.camera(loc=(0, -380, 190), target=(0, 0, 10), lens=24)
    L.cam_keys(cam, [(1, (-10, -380, 190)), (n, (10, -330, 170))])
    lin(cam)
    L.bake_static()


# ----------------------------------------------------------------------------- S04 drone top-down to the trees

def S04(L, n):
    night(stars=0, moon_rot=(R(68), 0, R(70)), moon_e=2.4)
    h0 = M.make_slope_h(13, 4, macro=1.0)
    pz = h0(0, -1.25)
    h = M.make_slope_h(13, 4, macro=1.0, platform=(0, 0, 2.3, 1.25, pz, 1.1))
    prints = []
    for k, (dx, sd) in enumerate(((-1.2, 1), (0.0, 2), (1.3, 3))):
        prints += M.trail((dx * 0.4, -2), (dx * 3 - 4, -200), step=1.25, gap=0.3, seed=sd, wobble=1.5, rx=0.22, ry=0.42,
                          skip=0.15)
    M.heightfield("slopeB", -60, 60, -280, 40, 120, 320, h, mat=M.mat_snow("slopeB_m"))
    M.print_decals(prints, h, name="tracks", color=(0.05, 0.07, 0.12), lift=0.05, scale=1.0)
    t = M.tent(loc=(0, 0, pz), slit=False, snow_amt=0.0, inner_light=60)
    glow = L.point((0, -2.5, pz + 1.0), energy=400, color=(1.0, 0.6, 0.3), radius=0.5, name="tentglow")
    spots = M.scatter_spots((-60, 60, -280, -180), 560, h, seed=5, h=(9, 16))
    spots += M.scatter_spots((-60, 60, -185, -165), 50, h, seed=6, h=(6, 11))
    M.conifer_forest("forest", spots, seed=5)
    M.fog((0, -215, h(0, -215) + 6), (140, 70, 18), density=0.03)
    M.snowfall((0, -60, h(0, -60) + 40), (90, 120, 40), n, count=700, radius=0.1, fall=3, wind=(8, 0, 0), seed=41, emit=0.1)
    z = 150
    cam, _ = L.camera(loc=(0, -38, h(0, -38) + z), lens=50)
    cam.rotation_euler = (0, 0, 0)
    L.cam_keys(cam, [(1, (0, -36, h(0, -36) + z)), (n, (-3, -150, h(0, -150) + z))])
    cam.rotation_euler = (0, 0, R(2))
    cam.keyframe_insert("rotation_euler", frame=1)
    cam.rotation_euler = (0, 0, R(-3))
    cam.keyframe_insert("rotation_euler", frame=n)
    L.bake_static()


# ----------------------------------------------------------------------------- S05 timeline plate (lateral pan)

def S05(L, n):
    night(stars=1.0, moon_rot=(R(70), 0, R(-60)), moon_e=1.4)
    prints = M.trail((0, -1.5), (-6, -60), step=0.7, gap=0.12, seed=7, wobble=0.6)
    h, pz, _ = slope_terrain(x=(-60, 60), y=(-120, 60), res=0.6)
    M.print_decals(prints, h, color=(0.1, 0.13, 0.2))
    tent_at(pz, inner=6.0, banks=False)
    forest_band(h, -130, -95, count=160)
    cy = 9.0
    c0, c1 = (-7, cy, h(-7, cy) + 3.5), (5, cy, h(5, cy) + 3.5)
    M.snowfall((0, -6, h(0, -6) + 2), (24, 14, 8), n, count=900, radius=0.02, fall=0.6, wind=(1.0, 0, 0), seed=51, cam=(c0, c1), clear=2.5,
               emit=0.12)
    M.fog((0, -60, h(0, -60)), (120, 120, 30), density=0.012)
    cam, ct = L.camera(loc=c0, target=(-7, -50, h(-7, -50) + 2), lens=30)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    lin(cam)
    ct.keyframe_insert("location", frame=1)
    ct.location = (5, -50, h(5, -50) + 2)
    ct.keyframe_insert("location", frame=n)
    lin(ct)
    L.bake_static()


# ----------------------------------------------------------------------------- S06 nine markers

def S06(L, n):
    night(stars=0.9, moon_rot=(R(72), 0, R(-150)), moon_e=1.2)
    h, pz, _ = slope_terrain(x=(-60, 60), y=(-170, 30), res=0.6, platform=False)
    forest_band(h, -170, -110, count=320, hrange=(9, 15))
    M.fog((0, -80, h(0, -80)), (140, 160, 30), density=0.012)
    M.snowfall((0, -10, h(0, -10) + 3), (20, 20, 8), n, count=700, radius=0.02, fall=0.6, wind=(0.8, 0, 0), seed=61,
               cam=((0.5, 6.0, h(0.5, 6) + 3.4), (0.4, 3.5, h(0.4, 3.5) + 3.0)), clear=3.0, emit=0.12)
    pole_m = L.mat_principled("pole", (0.22, 0.22, 0.23), rough=0.6)
    flag_m = L.mat_principled("flag", (0.25, 0.06, 0.05), rough=0.8)
    spots = [(-1.5, -6), (2.2, -11), (-3.5, -17), (0.8, -24), (4.5, -33), (-5.0, -44), (1.5, -58), (-2.5, -78), (3.0, -98)]
    for i, (x, y) in enumerate(spots):
        z = h(x, y)
        sc = 1.0 + max(0, -y - 20) * 0.015
        p = L.prim("cyl", loc=(x, y, z + 0.7 * sc), vertices=6, radius=0.022 * sc, depth=1.4 * sc)
        L.assign(p, pole_m)
        fl = M.mesh_obj(f"flag{i}", [(x, y, z + 1.38 * sc), (x + 0.32 * sc, y, z + 1.3 * sc), (x, y, z + 1.18 * sc)], [(0, 1, 2)], mat=flag_m)
        f_on = 4 + i * int((n - 20) / 9)
        lt = L.point((x, y - 0.4, z + 0.5 * sc), energy=0, color=(1.0, 0.7, 0.42), radius=0.2, name=f"mk{i}")
        e = 25 * sc * sc
        lt.data.energy = 0
        lt.data.keyframe_insert("energy", frame=max(1, f_on - 1))
        lt.data.energy = e * 1.6
        lt.data.keyframe_insert("energy", frame=f_on + 3)
        lt.data.energy = e
        lt.data.keyframe_insert("energy", frame=f_on + 9)
    c0, c1 = (0.5, 6.0, h(0.5, 6) + 3.4), (0.4, 3.5, h(0.4, 3.5) + 3.0)
    cam, ct = L.camera(loc=c0, target=(0, -30, h(0, -30) + 1.0), lens=35)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    lin(cam)
    L.bake_static()


# ----------------------------------------------------------------------------- S07 / S08 evidence board

CARDS = [("ALIENS", (-0.55, -0.01, 1.05), R(-5)), ("WEAPONS\nTEST", (0.5, -0.01, 0.05), R(4)), ("ATTACK", (-0.4, -0.01, -1.0), R(-3))]


def board_scene(L, n):
    L.set_world((0.002, 0.002, 0.003), 1.0)
    b = M.evidence_board(lamp_energy=200)
    L.particle_cloud((0, -1.2, 1.0), (2.5, 1.5, 2.5), count=140, radius=0.0025, drift=(0.03, 0, -0.03), nframes=n,
                     mat=L.mat_principled("dust", (0.9, 0.8, 0.6), emit=(1, 0.8, 0.5), emit_strength=0.25))
    # some faint old clippings / string around for texture
    old = [(-1.1, 2.0, 0.08), (1.05, 1.7, -0.1), (1.1, -1.9, 0.06), (-1.15, -1.8, -0.12), (1.15, 1.0, 0.05)]
    for i, (x, z, r) in enumerate(old):
        p = L.prim("plane", loc=(x, -0.006, z), size=1, rot=(math.pi / 2, r, 0))
        p.scale = (0.55, 0.42, 1)
        L.assign(p, M.mat_paper(f"oldp{i}", (0.16, 0.15, 0.13)))
    roots = []
    for i, (txt, loc, rot) in enumerate(CARDS):
        roots.append(M.paper_card(txt, loc, rot_y=rot, name=f"card{i}", size=(1.25, 0.8), text_size=0.3 if "\n" not in txt else 0.23))
    string_m = L.mat_principled("string", (0.5, 0.02, 0.02), rough=0.6)
    return b, roots, string_m


def S07(L, n):
    b, roots, sm = board_scene(L, n)
    hits = [10, 29, 50]
    for r, f in zip(roots, hits):
        M.hide_until(r, f - 6)
        M.slam_in(r, f, lead=6)
    cam, ct = L.camera(loc=(0.0, -4.4, 0.1), target=(0, 0, 0.05), lens=35)
    keys = [(1, (0.0, -4.4, 0.1))]
    y = -4.4
    for f in hits:
        keys.append((f, (0, y, 0.1)))
        y += 0.18
        keys.append((f + 4, (0, y, 0.1)))
    keys.append((n, (0, y + 0.05, 0.1)))
    L.cam_keys(cam, keys)
    M.shake(cam, hits, amp=0.02, decay=6)
    L.bake_static()


def S08(L, n):
    b, roots, sm = board_scene(L, n)
    red = L.mat_principled("stampred", (0.6, 0.03, 0.03), rough=0.7, emit=(0.8, 0.05, 0.04), emit_strength=0.6)
    stamps = [("NO EVIDENCE", CARDS[0][1], 15, R(-12)), ("NO EVIDENCE", CARDS[2][1], 21, R(9)), ("UNPROVEN", CARDS[1][1], 28, R(-7))]
    hits = []
    for i, (txt, loc, f, rot) in enumerate(stamps):
        t = L.text3d(txt, loc=(loc[0], -0.03, loc[2] - 0.05), rot=(math.pi / 2, rot, 0), size=0.26 if txt != "UNPROVEN" else 0.3,
                     extrude=0.0, mat=red, name=f"stamp{i}")
        t.data.font = M._font(M.F_ANTON)
        t.data.align_y = "CENTER"
        # frame around the stamp
        M.hide_until(t, f - 3)
        t.scale = (2.4, 2.4, 2.4)
        t.keyframe_insert("scale", frame=f - 3)
        t.scale = (0.95, 0.95, 0.95)
        t.keyframe_insert("scale", frame=f)
        t.scale = (1, 1, 1)
        t.keyframe_insert("scale", frame=f + 2)
        M.snow_burst((loc[0], -0.12, loc[2]), n, f, count=60, radius=0.004, spread=0.9, rise=0.12, seed=80 + i, name=f"dust{i}",
                     emit=0.1, dur=14)
        hits.append(f)
    cam, ct = L.camera(loc=(-0.05, -3.9, 0.1), target=(0, 0, 0.05), lens=35)
    L.cam_keys(cam, [(1, (-0.05, -3.9, 0.1)), (n, (0.05, -3.7, 0.1))])
    lin(cam)
    M.shake(cam, hits, amp=0.035, decay=7)
    L.bake_static()


# ----------------------------------------------------------------------------- S09 document plate

def S09(L, n):
    night(stars=0.3, moon_rot=(R(60), 0, R(-40)), moon_e=1.1)
    h, pz, _ = slope_terrain(x=(-25, 25), y=(-20, 35), res=0.3)
    tent_at(pz, inner=30.0, snow_amt=0.0)
    M.snowfall((0, -2.5, 1 + pz), (5, 4, 3), n, count=900, radius=0.008, fall=0.5, wind=(1.0, 0, 0), seed=91, emit=0.15,
               cam=((-1.6, -4.4, 1.2 + pz), (-1.2, -4.4, 1.15 + pz)), clear=0.6)
    M.fog((0, 6, 2 + pz), (40, 30, 8), density=0.03)
    cam, ct = L.camera(loc=(-1.6, -4.4, 1.2 + pz), target=(0.2, 0, 0.5 + pz), lens=40)
    L.cam_keys(cam, [(1, (-1.6, -4.4, 1.2 + pz)), (n, (-1.2, -4.4, 1.15 + pz))])
    lin(cam)
    L.dof(cam, distance=1.6, fstop=1.4)
    L.bake_static()


# ----------------------------------------------------------------------------- S10 gentle slope side view

def S10(L, n):
    night(stars=1.0, moon_rot=(R(62), 0, R(-25)), moon_e=1.8)
    h, pz, _ = slope_terrain(x=(-40, 30), y=(-60, 120), res=0.6)
    tent_at(pz, inner=8.0)
    M.snowfall((-8, 6, pz + 3), (20, 25, 8), n, count=700, radius=0.025, fall=0.5, wind=(1.5, 0, 0), seed=101, emit=0.12,
               cam=((-26, 5, pz + 3.0), (-26, 9, pz + 3.2)), clear=4)
    M.fog((0, 0, pz), (100, 200, 12), density=0.012)
    # angle arc graphic: horizontal reference + slope line + arc, drawing on
    gm = L.mat_emission("arc_m", (1.0, 0.85, 0.3), 6.0)
    px, py, pz2 = -3.0, 2.5, h(-3.0, 2.5) + 0.05
    ln = 9.0
    tg = math.tan(R(SLOPE))

    def curve(pts, name):
        cu = M.bpy.data.curves.new(name, "CURVE")
        cu.dimensions = "3D"
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            sp.points[i].co = (*p, 1)
        cu.bevel_depth = 0.035
        o = L.link(M.bpy.data.objects.new(name, cu))
        o.data.materials.append(gm)
        cu.bevel_factor_end = 0.0
        cu.keyframe_insert("bevel_factor_end", frame=12)
        cu.bevel_factor_end = 1.0
        cu.keyframe_insert("bevel_factor_end", frame=40)
        return o
    curve([(px, py, pz2), (px, py + ln, pz2)], "horiz")
    curve([(px, py, pz2), (px, py + ln, pz2 + ln * tg)], "slopeline")
    arc = [(px, py + 4 * math.cos(a), pz2 + 4 * math.sin(a)) for a in [R(SLOPE) * k / 16 for k in range(17)]]
    curve(arc, "arc")
    cam, ct = L.camera(loc=(-26, 7, pz + 3.0), target=(0, 6, pz + 1.6), lens=50)
    L.cam_keys(cam, [(1, (-26, 5, pz + 3.0)), (n, (-26, 9, pz + 3.2))])
    lin(cam)
    ct.keyframe_insert("location", frame=1)
    ct.location = (0, 9, pz + 1.8)
    ct.keyframe_insert("location", frame=n)
    lin(ct)
    L.bake_static()


# ----------------------------------------------------------------------------- S11 computer sim (Frozen code)

def S11(L, n):
    L.set_world((0.0, 0.004, 0.012), 1.0)
    gm, gem = M.mat_grid("grid", color=(0.12, 0.45, 1.0), scale=1.0, width=0.035, strength=2.5)
    g = L.prim("plane", loc=(0, 0, 0), size=40, name="grid")
    L.assign(g, gm)
    gem.inputs[0].default_value = (0.1, 0.3, 1.0, 1)
    gem.inputs[0].keyframe_insert("default_value", frame=1)
    gem.inputs[0].default_value = (0.5, 0.95, 1.0, 1)
    gem.inputs[0].keyframe_insert("default_value", frame=n)
    pm = L.mat_principled("grain", (0.9, 0.95, 1.0), emit=(0.8, 0.92, 1.0), emit_strength=2.0)
    for i, (r, h, cnt, spin, rad) in enumerate(((3.0, 1.2, 2000, 1.6, 0.007), (4.5, 2.0, 2000, -1.1, 0.008), (2.0, 0.8, 1700, 2.2, 0.006))):
        piv = M.empty(f"swirl{i}", (0, 0, 0.6))
        c = L.particle_cloud((0, 0, 0), (r * 2, r * 2, h), count=cnt, radius=rad, mat=pm, drift=(0, 0, 0), seed=110 + i, nframes=n,
                             name=f"grains{i}")
        c.animation_data_clear()
        c.parent = piv
        # swirl in from a tall chaotic column to a settled tilted slab layer
        piv.rotation_euler = (0, 0, 0)
        piv.scale = (1.4, 1.4, 4.0)
        piv.location = (0, 0, 2.5)
        piv.keyframe_insert("rotation_euler", frame=1)
        piv.keyframe_insert("scale", frame=1)
        piv.keyframe_insert("location", frame=1)
        piv.rotation_euler = (R(18) * (0.4 + 0.3 * i), 0, spin * 3.0)
        piv.scale = (1.0, 1.4, 0.12)
        piv.location = (0, 0, 0.35 + 0.18 * i)
        piv.keyframe_insert("rotation_euler", frame=int(n * 0.7))
        piv.keyframe_insert("scale", frame=int(n * 0.7))
        piv.keyframe_insert("location", frame=int(n * 0.7))
        piv.rotation_euler = (R(18) * (0.4 + 0.3 * i), 0, spin * 3.0 + 0.15)
        piv.keyframe_insert("rotation_euler", frame=n)
    L.point((0, 0, 3), energy=200, color=(0.5, 0.8, 1.0))
    cam, ct = L.camera(loc=(0, -14, 7), target=(0, 0, 0.6), lens=28)
    L.cam_keys(cam, [(1, (0, -15, 7.5)), (int(n * 0.35), (0, -9.5, 4.6)), (n, (0.4, -8.8, 4.2))])
    L.bake_static()


# ----------------------------------------------------------------------------- S12 wireframe slope

def wire_mat(n, color=(0.15, 0.75, 1.0), strength=2.0, x0=-16, x1=16):
    """Emissive cyan with a bright scan band sweeping along X (keyframed)."""
    m, nd, l = M.L._mat("wire_m")
    for k in list(nd):
        if k.type == "BSDF_PRINCIPLED":
            nd.remove(k)
    tc = nd.new("ShaderNodeTexCoord")
    sep = nd.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sep.inputs[0])
    sub = nd.new("ShaderNodeMath"); sub.operation = "SUBTRACT"
    l.new(sep.outputs["X"], sub.inputs[0])
    sub.inputs[1].default_value = x0
    sub.inputs[1].keyframe_insert("default_value", frame=1)
    sub.inputs[1].default_value = x1
    sub.inputs[1].keyframe_insert("default_value", frame=n)
    ab = nd.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"
    l.new(sub.outputs[0], ab.inputs[0])
    mr = nd.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 1.6
    mr.inputs["To Min"].default_value = 6.0
    mr.inputs["To Max"].default_value = 1.0
    l.new(ab.outputs[0], mr.inputs["Value"])
    mul = nd.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    l.new(mr.outputs[0], mul.inputs[0])
    mul.inputs[1].default_value = strength
    em = nd.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    l.new(mul.outputs[0], em.inputs[1])
    l.new(em.outputs[0], nd["Material Output"].inputs["Surface"])
    return m


def S12(L, n):
    L.set_world((0, 0, 0), 0)
    h = M.make_slope_h(SLOPE, 2, macro=1.2)
    t = M.heightfield("wire", -20, 20, -20, 25, 46, 52, h)
    w = t.modifiers.new("wf", "WIREFRAME")
    w.thickness = 0.05
    L.assign(t, wire_mat(n))
    base = M.heightfield("wirebase", -20, 20, -20, 25, 30, 30, lambda x, y: h(x, y) - 0.06)
    L.assign(base, L.mat_emission("wirebase_m", (0.0, 0.015, 0.03), 1.0))
    tb = L.prim("cube", loc=(0, 0, h(0, 0) + 0.45), name="tentmark")
    tb.scale = (1.0, 0.55, 0.45)
    L.assign(tb, L.mat_emission("tentmark_m", (1.0, 0.35, 0.05), 2.5))
    ring = L.prim("torus", loc=(0, 0, h(0, 0) + 0.1), major_radius=1.8, minor_radius=0.05)
    L.assign(ring, L.mat_emission("ring_m", (1.0, 0.4, 0.08), 3))
    ring.scale = (0.8, 0.8, 0.8)
    ring.keyframe_insert("scale", frame=1)
    ring.scale = (1.3, 1.3, 1.3)
    ring.keyframe_insert("scale", frame=n)
    piv = M.empty("orbit", (0, 0, h(0, 0)))
    cam, ct = L.camera(loc=(0, -17, 9), target=(0, 1.5, h(0, 0) + 0.5), lens=35)
    cam.parent = piv
    piv.rotation_euler = (0, 0, R(-20))
    piv.keyframe_insert("rotation_euler", frame=1)
    piv.rotation_euler = (0, 0, R(20))
    piv.keyframe_insert("rotation_euler", frame=n)
    lin(piv)
    L.bake_static()


# ----------------------------------------------------------------------------- S13-S15 cross-section diagrams

def diagram_base(L, n, ortho_scale=8.5, slab=False, slab_full=True, with_fill=False):
    L.set_world((0.012, 0.016, 0.03), 1.0)
    P = M.section_diagram(slope_deg=24, slab=slab, slab_full=slab_full)
    if not with_fill:
        M.bpy.data.objects.remove(P["fill"])
        P.pop("fill")
    gm, _ = M.mat_grid("dgrid", color=(0.15, 0.3, 0.55), bg=(0.008, 0.012, 0.025), scale=2.0, width=0.025, strength=0.5)
    bg = L.prim("plane", loc=(0, 3, 0), size=1, rot=(math.pi / 2, 0, 0), name="bg")
    bg.scale = (40, 40, 1)
    L.apply_scale(bg)
    L.assign(bg, gm)
    L.sun(rot=(R(50), 0, R(-25)), energy=2.0, color=(0.9, 0.95, 1.0))
    L.set_world((0.05, 0.06, 0.09), 1.0)
    zc = P["zp"] - 1.4
    cam, _ = L.camera(loc=(0.2, -20, zc), lens=50)
    cam.rotation_euler = (math.pi / 2, 0, 0)
    M.ortho(cam, ortho_scale)
    # small label line: "tent" marker dot
    return P, cam, zc


def S13(L, n):
    P, cam, zc = diagram_base(L, n, ortho_scale=10.0, with_fill=True)
    a, b, zp, zs = P["a"], P["b"], P["zp"], P["zs"]
    fill = P["fill"]
    # the dug-out wedge lifts away (shovelled out), then the tent drops into the notch
    fill.keyframe_insert("location", frame=1)
    fill.keyframe_insert("location", frame=10)
    fill.location = (0.8, 0, 3.2)
    fill.keyframe_insert("location", frame=32)
    fill.scale = (1, 1, 1)
    fill.keyframe_insert("scale", frame=10)
    fill.scale = (0.01, 1, 0.01)
    fill.keyframe_insert("scale", frame=32)
    # glowing cut outline (red) draws while digging
    red = L.mat_emission("cut_m", (1.0, 0.25, 0.15), 6)
    for nm, (x0, z0, x1, z1) in (("cutV", (a, zs(a), a, zp)), ("cutH", (a, zp, b, zp))):
        mid = ((x0 + x1) / 2, -0.85, (z0 + z1) / 2)
        o = L.prim("cube", loc=mid, name=nm)
        o.scale = (max(0.025, abs(x1 - x0) / 2), 0.02, max(0.025, abs(z1 - z0) / 2))
        L.assign(o, red)
        sx = o.scale.copy()
        o.scale = (sx.x * (0.0 if nm == "cutH" else 1), sx.y, sx.z * (0.0 if nm == "cutV" else 1))
        o.keyframe_insert("scale", frame=4)
        o.scale = sx
        o.keyframe_insert("scale", frame=16 if nm == "cutV" else 26)
    tent = P["tent"]
    cx, _ = P["tent_c"]
    tent.location = (0, 0, 2.5)
    tent.keyframe_insert("location", frame=1)
    tent.keyframe_insert("location", frame=34)
    tent.location = (0, 0, 0)
    tent.keyframe_insert("location", frame=46)
    M.hide_until(tent, 34)
    cam.data.ortho_scale = 11.0
    cam.data.keyframe_insert("ortho_scale", frame=1)
    cam.data.ortho_scale = 8.0
    cam.data.keyframe_insert("ortho_scale", frame=n)
    cam.location = (-0.6, -20, zp - 1.3)
    cam.keyframe_insert("location", frame=1)
    cam.location = (-0.2, -20, zp - 0.9)
    cam.keyframe_insert("location", frame=n)
    L.bake_static()


def S14(L, n):
    P, cam, zc = diagram_base(L, n, ortho_scale=10.5, slab=True, slab_full=False)
    k = P["slab_key"]
    k.value = 0.0
    k.keyframe_insert("value", frame=1)
    k.value = 1.0
    k.keyframe_insert("value", frame=n - 4)
    tg = P["tg"]
    # wind-blown snow streaming over the ridge left-to-right, settling above the notch
    a = P["a"]
    zs = P["zs"]
    pm = L.mat_principled("wind_m", (0.9, 0.95, 1.0), emit=(0.8, 0.9, 1.0), emit_strength=1.5)
    import random
    rnd = random.Random(14)
    pts = []
    T = n / 24.0
    for i in range(1500):
        x = rnd.uniform(-11.0, 1.0)
        pts.append((x, rnd.uniform(-0.95, -0.75), max(P["zg"](x) + 1.35, zs(x)) + rnd.uniform(0.12, 1.1) * (0.4 + 0.6 * rnd.random())))
    wc = M.cloud_points(pts, radius=0.016, name="wind", mat=pm)
    wc.keyframe_insert("location", frame=1)
    wc.location = (3.4 * T, 0, -3.4 * T * tg * 0.8)
    wc.keyframe_insert("location", frame=n)
    lin(wc)
    for i, (x0, dz) in enumerate(((-4.2, 1.6), (-3.2, 2.2), (-2.4, 1.3))):
        ar = M.arrow((x0 + a, zs(x0 + a) + dz), (x0 + a + 1.4, zs(x0 + a + 1.4) + dz - 0.35), y=-1.0, name=f"arr{i}", strength=3)
        ar.location = (-0.8, 0, 0.3)
        ar.keyframe_insert("location", frame=1)
        ar.location = (0.9, 0, -0.3)
        ar.keyframe_insert("location", frame=n)
        lin(ar)
    cam.location = (-0.8, -20, P["zp"] - 1.0)
    L.bake_static()


def S15(L, n):
    P, cam, zc = diagram_base(L, n, ortho_scale=10.5, slab=True, slab_full=True)
    sl = P["slab"]
    a, zs, tg = P["a"], P["zs"], P["tg"]
    sx0 = P["slab_x0"]
    cam.location = (-0.8, -20, P["zp"] - 1.0)
    f_crack, f_go = int(n * 0.45), int(n * 0.62)
    # crack line: crown fracture (upslope end) + base, glowing red, draws on
    red = L.mat_emission("crack_m", (1.0, 0.12, 0.06), 9)
    xs = [sx0 + 0.3 + (a - sx0 - 0.3) * i / 10 for i in range(11)]
    verts, faces = [], []
    for i, x in enumerate(xs):
        z = zs(x) + 0.0 + 0.03 * math.sin(i * 2.1)
        verts += [(x, -0.86, z - 0.035), (x, -0.86, z + 0.035)]
    for i in range(len(xs) - 1):
        faces.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    base_crack = M.mesh_obj("crackbase", verts, faces, mat=red)
    cx = sx0 + 0.6
    crown = M.mesh_obj("crown", [(cx - 0.04, -0.87, zs(cx) - 0.02), (cx + 0.04, -0.87, zs(cx) - 0.02), (cx + 0.1, -0.87, zs(cx) + 0.8),
                                 (cx + 0.02, -0.87, zs(cx) + 0.8)], [(0, 1, 2, 3)], mat=red)
    for o in (base_crack, crown):
        M.hide_until(o, f_crack)
    # slab slides down-slope and slumps into the notch onto the tent
    d = Vector((1, 0, -tg)).normalized()
    sl.keyframe_insert("location", frame=f_go)
    sl.location = d * 1.6
    sl.keyframe_insert("location", frame=f_go + 14)
    sl.location = d * 2.0 + Vector((0.2, 0, -0.45))
    sl.rotation_euler = (0, R(6), 0)
    sl.keyframe_insert("location", frame=n)
    sl.keyframe_insert("rotation_euler", frame=n)
    sl.rotation_euler = (0, 0, 0)
    sl.keyframe_insert("rotation_euler", frame=f_go + 14)
    for o in (base_crack, crown):
        o.keyframe_insert("location", frame=f_go)
        o.location = d * 1.6
        o.keyframe_insert("location", frame=f_go + 14)
    tent = P["tent"]
    cxp, zp = P["tent_c"]
    # squash tent block about its base when hit
    tent.keyframe_insert("scale", frame=f_go + 12)
    tent.keyframe_insert("location", frame=f_go + 12)
    tent.scale = (1.05, 1, 0.55)
    tent.location = (cxp * (1 - 1.05), 0, zp * (1 - 0.55))
    tent.keyframe_insert("scale", frame=f_go + 18)
    tent.keyframe_insert("location", frame=f_go + 18)
    M.snow_burst((a + 0.6, -0.9, zs(a) + 0.2), n, f_go + 13, count=500, radius=0.012, spread=1.4, rise=0.6, seed=151, emit=1.0)
    M.shake(cam, [f_crack, f_go + 13], amp=0.06, decay=8)
    L.bake_static()


# ----------------------------------------------------------------------------- S16 / S17 3D slab onto tent

def slab_block(name, size=(4.2, 3.0, 0.55), seed=1, mat=None):
    bm = M.bmesh.new()
    M.bmesh.ops.create_cube(bm, size=1.0)
    M.bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=6, use_grid_fill=True)
    for v in bm.verts:
        x, y, z = v.co
        v.co = Vector((x * size[0], y * size[1], z * size[2]))
        if z > 0:
            v.co.z += 0.12 * M.noise.noise(Vector((x * 3 + seed, y * 3, 0)))
        v.co.x += 0.06 * M.noise.noise(Vector((y * 4, z * 4, seed)))
    me = M.bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = L_link(M.bpy.data.objects.new(name, me))
    me.polygons.foreach_set("use_smooth", [False] * len(me.polygons))
    if mat:
        o.data.materials.append(mat)
    return o


def L_link(o):
    return M.L.link(o)


def S16(L, n):
    # side-on: the slab slides down from the right (uphill) onto the tent's gable end
    night(stars=0.5, moon_rot=(R(62), 0, R(-60)), moon_e=1.7)
    h, pz, _ = slope_terrain(x=(-25, 25), y=(-25, 35), res=0.2)
    t = tent_at(pz, inner=12.0, snow_amt=0.0)
    M.anim_flaps(t, n, base=0.2, amp=0.1)
    tg = math.tan(R(SLOPE))
    sm = M.mat_snow("slab_m", tint=(0.86, 0.9, 1.0))
    slab = slab_block("slab", size=(4.4, 2.4, 0.65), mat=sm)
    y_start, y_end = 4.4, 1.2
    p0 = Vector((0.0, y_start, h(0, y_start) + 0.28))
    p1 = Vector((0.0, y_end + 0.2, pz + 1.05))
    slab.rotation_euler = (math.atan(tg), 0, 0)
    f_hit = int(n * 0.45)
    slab.location = p0 + Vector((0, 0.5, 0.18))
    slab.keyframe_insert("location", frame=1)
    slab.keyframe_insert("rotation_euler", frame=1)
    slab.location = p1
    slab.rotation_euler = (math.atan(tg) * 0.4, 0, 0)
    slab.keyframe_insert("location", frame=f_hit)
    slab.keyframe_insert("rotation_euler", frame=f_hit)
    slab.location = p1 + Vector((0, -0.45, -0.32))
    slab.rotation_euler = (math.atan(tg) * 0.15, R(2), 0)
    slab.keyframe_insert("location", frame=n)
    slab.keyframe_insert("rotation_euler", frame=n)
    lin(slab)
    # torn crown: dark step in the snow where the slab broke away
    gm = L.mat_principled("gap_m", (0.03, 0.045, 0.08), rough=1)
    yy = y_start + 1.6
    M.mesh_obj("crown", [(-2.3, yy, h(-2.3, yy) + 0.02), (2.3, yy, h(2.3, yy) + 0.02), (2.3, yy - 0.5, h(2.3, yy - 0.5) - 0.3),
                         (-2.3, yy - 0.5, h(-2.3, yy - 0.5) - 0.3)], [(0, 1, 2, 3)], mat=gm)
    r = t["root"]
    r.keyframe_insert("scale", frame=f_hit - 1)
    r.scale = (1.02, 1.05, 0.6)
    r.keyframe_insert("scale", frame=f_hit + 4)
    rim = L.area((-3.0, 6.5, pz + 3.0), (R(-60), 0, R(-150)), energy=400, size=3, color=(0.55, 0.65, 1.0), name="rimslab")
    rim.data.specular_factor = 0.0
    M.snow_burst((0, 0.6, pz + 1.0), n, f_hit, count=900, radius=0.012, spread=3.0, rise=0.9, seed=161, emit=0.3)
    M.volume_puff((0, 0.5, pz + 1.0), f_hit, n, size=2.6, density=0.5)
    c0, c1 = (6.4, -1.6, pz + 1.3), (5.9, -1.4, pz + 1.25)
    M.snowfall((2.5, 0.5, pz + 1.5), (5, 8, 4), n, count=800, radius=0.01, fall=0.6, wind=(-1.0, 0, 0), seed=163, cam=(c0, c1), clear=1.2,
               emit=0.12)
    M.fog((0, 4, pz + 2), (40, 30, 8), density=0.02)
    cam, ct = L.camera(loc=c0, target=(0, 1.3, pz + 0.85), lens=35)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    lin(cam)
    L.handheld(cam, n, amp=0.02, rate=0.8)
    M.shake(cam, [f_hit], amp=0.05, decay=10)
    L.bake_static()


def S17(L, n):
    night(stars=0.6, moon_rot=(R(64), 0, R(-50)), moon_e=1.5)
    h, pz, _ = slope_terrain(x=(-25, 25), y=(-25, 35), res=0.2)
    t = tent_at(pz, inner=0.0, crush=0.5, snow_amt=0.0)
    sm = M.mat_snow("debris_m", tint=(0.84, 0.88, 0.98))
    tg = math.tan(R(SLOPE))
    s = slab_block("slab", size=(4.2, 2.0, 0.5), mat=sm, seed=3)
    s.location = (0.1, 0.9, pz + 0.95)
    s.rotation_euler = (math.atan(tg) * 0.3, R(3), R(-2))
    M.smooth_obj(s)
    import random
    rnd = random.Random(7)
    for i in range(10):
        b = slab_block(f"chunk{i}", size=(rnd.uniform(0.3, 0.7), rnd.uniform(0.25, 0.5), rnd.uniform(0.15, 0.3)), mat=sm, seed=i)
        M.smooth_obj(b)
        x, y = rnd.choice((-1, 1)) * rnd.uniform(2.1, 3.0), rnd.uniform(-1.8, 1.0)
        b.location = (x, y, max(pz, h(x, y)) + 0.08)
        b.rotation_euler = (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 3))
    c0, c1 = (1.4, -4.4, pz + 1.5), (2.2, -7.8, pz + 2.5)
    M.snowfall((0, -1, pz + 1.5), (9, 8, 4), n, count=1200, radius=0.008, fall=0.25, wind=(0.3, 0, 0), seed=171, cam=(c0, c1), clear=1.0,
               emit=0.15)
    M.fog((0, 0, pz + 1), (40, 40, 5), density=0.045)
    rim = L.area((-3.0, 6.5, pz + 3.0), (R(-60), 0, R(-150)), energy=300, size=3, color=(0.55, 0.65, 1.0), name="rimslab")
    rim.data.specular_factor = 0.0
    cam, ct = L.camera(loc=c0, target=(0, 0.3, pz + 0.55), lens=35)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    lin(cam)
    L.handheld(cam, n, amp=0.01)
    L.bake_static()


# ----------------------------------------------------------------------------- S18 inside the tent, hikers step out

def S18(L, n):
    night(stars=0.6, moon_rot=(R(58), 0, R(-20)), moon_e=2.6)
    h, pz, _ = slope_terrain(x=(-25, 25), y=(-40, 30), res=0.25)
    sx = 0.35
    t = M.tent(loc=(0, 0, pz), slit=True, slit_x=sx, gap=0.2, slit_len=(0.03, 0.95), inner_light=0, snow_amt=0.0, flap_w=0.2)
    M.anim_flaps(t, n, base=1.15, amp=0.2, open_from=1, open_to=14)
    # warm torch inside, aimed at the canvas beside the slit
    tr, tg = M.torch((0.0, 0.7, pz + 0.3), (sx - 0.5, -0.55, pz + 0.65), energy=45, size_deg=55)
    tg.keyframe_insert("location", frame=1)
    tg.location = (sx + 0.45, -0.55, pz + 0.7)
    tg.keyframe_insert("location", frame=n)
    L.flicker(tr, n, depth=0.25, rate=0.5)
    L.point((sx - 0.6, 0.2, pz + 0.25), energy=4, color=(1.0, 0.6, 0.3), radius=0.1, name="glow")
    pack_m = L.mat_principled("pack", (0.05, 0.045, 0.04), rough=0.9)
    for i, (x, y) in enumerate(((-1.4, 0.5), (-0.9, -0.5), (1.3, 0.4), (1.6, -0.4))):
        b = L.prim("cyl", loc=(x, y, pz + 0.12), rot=(0, math.pi / 2, 0.2 * i), vertices=12, radius=0.14, depth=0.6)
        L.assign(b, pack_m)
    # hikers just outside the slit, walking away downhill one after another
    for i in range(5):
        p = M.hiker(f"hiker{i}", height=1.72 + 0.05 * ((i * 7) % 3 - 1))
        r = p["root"]
        r.rotation_euler = (0, 0, math.pi + 0.2 * (i - 2))
        x0 = sx + 0.35 * ((i % 3) - 1)
        ya = -1.25 - 0.15 * i
        f0 = 1 + i * 9
        L.anim_walk(p, 1, n, stride=0.5, rate=1.1)
        rt = p["root"]
        rt.animation_data_clear()
        pa = (x0, ya, h(x0, ya) - 0.05)
        pb = (x0 - 0.4 * (i - 2), ya - 3.0, h(x0, ya - 3.0) - 0.05)
        rt.location = pa
        rt.keyframe_insert("location", frame=1)
        rt.keyframe_insert("location", frame=f0)
        rt.location = pb
        rt.keyframe_insert("location", frame=f0 + 60)
        lin(rt)
    c0, c1 = (sx - 0.05, 0.62, pz + 0.3), (sx - 0.02, 0.42, pz + 0.32)
    M.snowfall((sx, -2.5, pz + 1.0), (5, 4, 3), n, count=1200, radius=0.008, fall=0.4, wind=(0.8, 1.2, 0), seed=181, cam=(c0, c1),
               clear=0.8, emit=0.2)
    M.fog((0, -10, pz), (40, 30, 8), density=0.03)
    cam, ct = L.camera(loc=c0, target=(sx, -0.5, pz + 0.78), lens=22)
    L.cam_keys(cam, [(1, c0), (int(n * 0.35), c0), (n, c1)])
    L.handheld(cam, n, amp=0.008)
    L.bake_static()


# ----------------------------------------------------------------------------- S19 forest edge

def S19(L, n):
    night(stars=0.4, moon_rot=(R(74), 0, R(175)), moon_e=1.6)
    h = M.make_slope_h(8, 5, macro=1.0)
    M.heightfield("edge", -60, 60, -160, 20, 100, 140, h, mat=M.mat_snow("edge_m"))
    spots = M.scatter_spots((-60, 60, -140, -72), 360, h, seed=9, h=(9, 16))
    M.conifer_forest("forest", spots, seed=9)
    M.fog((0, -80, h(0, -80) + 2), (120, 80, 22), density=0.045)
    for i in range(4):
        p = M.hiker(f"far{i}", height=1.75)
        r = p["root"]
        r.rotation_euler = (0, 0, math.pi)
        x0 = -2.0 + 1.3 * i + (0.5 if i % 2 else 0)
        y0 = -56 - 2.5 * i
        L.anim_walk(p, 1, n, stride=0.45, rate=0.9, travel=((x0, y0, h(x0, y0)), (x0 - 0.3, y0 - 4.5, h(x0, y0 - 4.5))))
    c0, c1 = (0.4, -12, h(0, -12) + 2.0), (0.1, -12.5, h(0, -12) + 2.0)
    M.snowfall((0, -45, h(0, -45) + 3), (14, 20, 10), n, count=700, radius=0.03, fall=0.8, wind=(1.4, 0, 0), seed=191, cam=(c0, c1),
               clear=22, emit=0.1)
    cam, ct = L.camera(loc=c0, target=(0, -62, h(0, -62) + 3.2), lens=85)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    lin(cam)
    L.bake_static()
