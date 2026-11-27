"""MURDER-01 thumbnail hero stills (NOT part of the video; shots.py is the video source).
Purpose-built compositions for the custom Shorts thumbnail, rendered with a copy of render_shot.py pointed at this file.
THUMB_A: the whole orange tent on blue moonlit snow, its downhill roof slit open with the flaps pushed OUT,
  warm light pouring through the cut onto the snow ("CUT FROM INSIDE"). Empty tent, no people.
THUMB_B: the small lit tent on real snow; the slope above it turns into a cyan simulation wireframe, with one red
  crack line across the slope just above the tent ("FROZEN?"). Poses the 2021 model as a question, not a verdict.
World layout as in shots.py: tent at origin, ridge along X, slope rises toward +Y, slit on the -Y roof panel.
"""
import os, sys, math, importlib
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_murder as M
importlib.reload(M)
from mathutils import Vector

R = math.radians
SLOPE = 20.0


def _night(stars=1.0, moon_rot=(R(62), 0, R(-28)), moon_e=1.6, hor=(0.018, 0.024, 0.045)):
    M.night_sky(stars=stars, hor=hor)
    return M.moon(rot=moon_rot, energy=moon_e)


def _terrain(x=(-30, 30), y=(-30, 40), res=0.25, seed=0, name="slope"):
    h0 = M.make_slope_h(SLOPE, seed)
    pz = h0(0, -1.25)
    h = M.make_slope_h(SLOPE, seed, platform=(0, 0, 2.3, 1.25, pz, 1.1))
    nx = int((x[1] - x[0]) / res) + 1
    ny = int((y[1] - y[0]) / res) + 1
    M.heightfield(name, x[0], x[1], y[0], y[1], nx, ny, h, mat=M.mat_snow(name + "_m"))
    return h, pz


def _banks(pz):
    sm = M.mat_snow("bank_m")
    M.snow_bank((0, 1.2, pz + 0.05), (2.5, 0.42, 0.36), seed=2, mat=sm, name="bankB")
    M.snow_bank((-2.15, 0.1, pz), (0.38, 1.25, 0.3), seed=3, mat=sm, name="bankL")
    M.snow_bank((2.15, 0.0, pz), (0.38, 1.25, 0.26), seed=4, mat=sm, name="bankR")


def _open_flaps(t, a=1.05):
    for tag, sg in (("L", -1), ("R", 1)):
        t["flap" + tag].rotation_euler = (0, sg * a, 0)


def THUMB_A(L, n):
    _night(stars=0.7, moon_rot=(R(58), 0, R(-35)), moon_e=1.4)
    h, pz = _terrain(x=(-25, 25), y=(-25, 35), res=0.2)
    t = M.tent(loc=(0, 0, pz), slit=True, slit_x=-0.55, gap=0.14, inner_light=160.0, snow_amt=0.0, flap_w=0.13)
    _open_flaps(t, 1.35)
    # glowing interior seen through the gash (lantern-lit canvas floor and back wall)
    gm = L.mat_emission("inside_m", (1.0, 0.42, 0.12), 7.0)
    M.mesh_obj("inside_back", [(-1.5, 0.2, pz + 0.02), (0.5, 0.2, pz + 0.02), (0.5, 0.2, pz + 1.0), (-1.5, 0.2, pz + 1.0)], [(0, 1, 2, 3)], mat=gm)
    M.mesh_obj("inside_floor", [(-1.5, -0.9, pz + 0.02), (0.5, -0.9, pz + 0.02), (0.5, 0.2, pz + 0.02), (-1.5, 0.2, pz + 0.02)], [(0, 1, 2, 3)], mat=gm)
    _banks(pz)
    # hot core just behind the cut so the slit is the brightest thing in frame
    L.point((-0.55, -0.2, pz + 0.55), energy=70, color=(1.0, 0.55, 0.22), radius=0.06, name="slitcore")
    # light escaping through the cut, laying a warm tongue on the snow downhill
    sp = L.spot((-0.55, 0.3, pz + 0.85), (0, 0, 0), energy=900, size_deg=24, blend=0.5, color=(1.0, 0.6, 0.28), name="spill",
                radius=0.02)
    M.aim(sp, M.empty("spill_tgt", (-0.6, -2.4, h(-0.6, -2.4))))
    # cold rim from upslope so the tent ridge separates from the sky
    L.area((0.5, 3.5, pz + 3.0), (R(-60), 0, 0), energy=60, size=4, color=(0.5, 0.6, 1.0), name="rim")
    cam_loc = (-2.9, -4.3, pz + 1.4)
    tgt = (-0.45, -0.25, pz + 0.85)
    M.snowfall((-0.8, -1.8, pz + 1.0), (5, 3, 2.6), n, count=500, radius=0.005, fall=0.5, wind=(1.4, 0.2, 0), seed=11,
               cam=(cam_loc, cam_loc), clear=1.0, emit=0.15)
    M.snowfall((0.0, 6.0, pz + 2.0), (16, 10, 5), n, count=600, radius=0.015, fall=0.5, wind=(1.6, 0, 0), seed=12, name="snowfar",
               emit=0.15)
    M.fog((0, 6, pz + 2), (40, 30, 8), density=0.02)
    cam, ct = L.camera(loc=cam_loc, target=tgt, lens=28)
    L.cam_light(cam, energy=10, color=(0.6, 0.72, 1.0), size_deg=80)
    L.bake_static()


def _wire_slope(h, y0, y1, x=(-20, 20)):
    t = M.heightfield("wire", x[0], x[1], y0, y1, 41, int((y1 - y0) / 0.9) + 1, lambda a, b: h(a, b) + 0.12)
    w = t.modifiers.new("wf", "WIREFRAME")
    w.thickness = 0.035
    L_ = M.L
    L_.assign(t, L_.mat_emission("wire_m", (0.1, 0.65, 1.0), 1.1))
    base = M.heightfield("wirebase", x[0], x[1], y0, y1, 30, 30, lambda a, b: h(a, b) + 0.09)
    L_.assign(base, L_.mat_emission("wirebase_m", (0.0, 0.012, 0.03), 1.0))
    return t


def THUMB_B(L, n):
    _night(stars=1.0, moon_rot=(R(62), 0, R(-40)), moon_e=1.5)
    h, pz = _terrain(x=(-30, 30), y=(-30, 45), res=0.3)
    t = M.tent(loc=(0, 0, pz), slit=True, gap=0.12, inner_light=70.0, snow_amt=0.0, flap_w=0.14)
    _open_flaps(t, 0.7)
    _banks(pz)
    # the slope above the tent becomes the simulation grid
    _wire_slope(h, 2.2, 40)
    # crack line across the slope just above the tent (where a slab would release), jagged, glowing red
    import random
    rnd = random.Random(5)
    pts, x = [], -9.0
    while x <= 9.0:
        y = 3.0 + 0.25 * math.sin(x * 0.9) + rnd.uniform(-0.12, 0.12)
        pts.append((x, y, h(x, y) + 0.15))
        x += 0.35
    cu = M.bpy.data.curves.new("crack", "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    cu.bevel_depth = 0.09
    o = M.L.link(M.bpy.data.objects.new("crack", cu))
    o.data.materials.append(L.mat_emission("crack_m", (1.0, 0.02, 0.01), 3.0))
    L.point((0, -1.6, pz + 0.6), energy=10, color=(1.0, 0.55, 0.25), radius=0.3, name="tentspill")
    M.snowfall((0, -4, pz + 2), (14, 10, 6), n, count=700, radius=0.012, fall=0.5, wind=(1.5, 0, 0), seed=21, emit=0.15)
    M.fog((0, 10, pz + 3), (60, 40, 12), density=0.012)
    cam_loc = (-2.6, -6.2, pz + 1.6)
    cam, ct = L.camera(loc=cam_loc, target=(0.0, 2.2, pz + 1.9), lens=24)
    L.cam_light(cam, energy=8, color=(0.6, 0.72, 1.0), size_deg=80)
    L.bake_static()
