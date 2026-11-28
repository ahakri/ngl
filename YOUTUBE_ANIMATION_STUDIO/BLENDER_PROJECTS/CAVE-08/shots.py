"""CAVE-08 — Jacob's Well (Wimberley, Texas): the 1979 deaths and the 2000 recovery. Shot builders (def Sxx(L, n)).
No victims are depicted: swimmers and divers are generic faceless rigs. The loss is two lights going out (S08) and a
dimming dot (S14); the 1981 flood is surface water only (S13); the 2000 discovery is two beams on a dark gap (S16).
Shared builders: PIPELINE/blender/lib_cave.py (tube_along, well_mouth, creek_rock_mat, clear_water_mat, gravel_field,
gravel_mat, pebble_floor_mat, park_sign, rebar_grate, flood_water, swimmer_float, rock_room, time_rings added for
this video) and lib_scuba.hand."""
import sys, os, math, random
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "PIPELINE", "blender"))
import importlib
import lib_cave as C
importlib.reload(C)
import lib_scuba as S
import bpy
from mathutils import Vector, noise

HR = 1.9                                  # radius of the well mouth (m)
SUN = C.sun_dir(58, 300)                  # hard high sun from the upper left
CYAN_RIM = (0.35, 0.85, 1.0)
TEAL = (0.3, 0.7, 0.68)
P0, T0 = (0.0, -11.0, 8.5), (0.0, -0.5, 0.0)     # S01 frame-1 drone pose == S18 last frame (loop)
P1, T1 = (0.0, -1.2, 7.5), (0.0, -0.7, 0.0)


# ============================================================================ helpers

def _track(obj, pos, name="tgt"):
    t = bpy.data.objects.new(name, None)
    C.L.link(t)
    t.location = pos
    con = obj.constraints.new("TRACK_TO")
    con.target = t
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    return t


def _aim(o, pos, target):
    o.location = pos
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y")
    return o


def _uw(vol_end=26.0):
    C.world_black((0.0, 0.004, 0.006))
    C.render_quality(vol_end=vol_end, vol_tile="8", vol_samples=24)


def _hud(cam, lens, px, py, dist=2.0):
    """Camera-local position for a HUD element at pixel (px, py) of the 1080x1920 frame."""
    hh = dist * 18.0 / lens
    return ((px - 540.0) / 540.0 * hh * 9.0 / 16.0, (960.0 - py) / 960.0 * hh, -dist)


def _hud_text(cam, lens, body, px, py, size_px=30, color=(0.75, 0.9, 0.9), strength=1.6, align="LEFT", font=None,
              name="hud"):
    hh = 2.0 * 18.0 / lens
    t = C.text(body, _hud(cam, lens, px, py), size=size_px / 960.0 * hh, color=color, strength=strength,
               font=font or C.FONT_OSWALD, rot=(0, 0, 0), align=align, name=name)
    t.parent = cam
    return t


# ============================================================================ creek / swimming hole (S01 S04 S13 S17 S18)

def creek_cx(y):
    return 1.6 * math.sin(y * 0.045)


def creek_z(x, y):
    d = abs(x - creek_cx(y))
    nz = 0.07 * noise.noise(Vector((x * 0.22, y * 0.22, 0.3))) + 0.03 * noise.noise(Vector((x * 0.8, y * 0.8, 1.7)))
    bed = -0.34 + nz - 0.1 * C.sm((3.5 - d) / 3.5)
    bank = 1.5 + 0.7 * noise.noise(Vector((x * 0.05, y * 0.05, 2.2))) + 0.03 * max(0.0, d - 12.0)
    z = C.lerp(bed, bank, C.sm((d - 4.6) / 4.5))
    lg = C.sm((x - 3.3) / 0.35) * C.sm((8.5 - x) / 1.5) * C.sm((5.5 - abs(y + 0.5)) / 1.2)   # rock ledge, east side
    return max(z, C.lerp(z, 0.38 + 0.4 * nz, lg))


def _creek(L, n, trees=120, t0=0.0, hole=True, flood=False, y_range=(-40.0, 95.0), tree_seed=11):
    """Texas Hill Country creek: pale limestone bed, clear shallow water, cypress banks, the round well mouth at the
    origin (hole=True). flood=True: overcast, no clear water (use C.flood_water), darker trees."""
    if flood:
        bg = C.sky_world(top=(0.15, 0.16, 0.18), horizon=(0.4, 0.42, 0.44), ground=(0.07, 0.07, 0.07), strength=1.0)
        sun = C.sun_from(C.sun_dir(50, 250), energy=0.9, color=(0.75, 0.8, 0.9), angle=35)
        rock = C.creek_rock_mat("creekrock", water_z=-50.0, dark=(0.2, 0.19, 0.16), light=(0.45, 0.43, 0.38),
                                grass=(0.05, 0.08, 0.03))
    else:
        bg = C.sky_world(top=(0.16, 0.38, 0.8), horizon=(0.7, 0.82, 0.95), ground=(0.2, 0.2, 0.17), sun_dir=tuple(SUN),
                         sun_color=(1.0, 0.95, 0.85), sun_glow=1.5, strength=0.8)
        sun = C.sun_from(SUN, energy=3.0, color=(1.0, 0.96, 0.88), angle=1.2)
        rock = C.creek_rock_mat("creekrock", dark=(0.3, 0.27, 0.2), light=(0.6, 0.55, 0.43), grass=(0.06, 0.13, 0.03),
                                grass_z=(0.12, 0.7), shallow=(0.6, 0.92, 0.78), deep_range=(0.6, 3.2), glow_strength=0.7)

    def coarse(x, y):
        if hole and abs(x) < 10.5 and -12.5 < y < 18.5:      # sits under the fine patch: drop it out of the shaft
            return -16.0
        return creek_z(x, y) - 0.08

    def fine(x, y):
        r = math.hypot(x, y)
        if not hole:
            return creek_z(x, y)
        if r < 2.6:
            return -14.0
        return creek_z(x, y) - 0.7 * C.sm((2.95 - r) / 0.3)
    C.heightfield(size=(150, 210), center=(0, 45, 0), res=1.1, fn=coarse, mat=rock, name="terrain", disp=(0, 0))
    C.heightfield(size=(24, 34), center=(0, 3, 0), res=0.18, fn=fine, mat=rock, name="bed", disp=(0, 0))
    if hole:
        C.well_mouth(R=HR, depth=12.0, apron=3.1, bed_fn=creek_z, lip=0.5, mat=rock, name="well")
        cap = L.prim("cyl", loc=(0, 0, -12.9), vertices=32, radius=3.2, depth=0.1, name="wellcap")
        L.assign(cap, L.mat_principled("wellcap_m", (0.0, 0.0, 0.0), rough=1.0))
    rnd = random.Random(tree_seed)
    sdir = Vector((-SUN.x, -SUN.y)).normalized()
    pts, tries = [], 0
    while len(pts) < trees and tries < trees * 30:
        tries += 1
        y = rnd.uniform(*y_range)
        x = creek_cx(y) + rnd.choice((-1, 1)) * (6.8 + abs(rnd.gauss(0, 6.0)))
        if abs(x) > 62:
            continue
        if not flood and ((Vector((x, y)) + sdir * 6.8).length < 5.5 or math.hypot(x, y) < 7.5):
            continue                                           # keep the mouth itself in the sun
        pts.append((x, y, creek_z(x, y)))
    lf = ((0.02, 0.04, 0.015), (0.07, 0.12, 0.045)) if flood else ((0.03, 0.07, 0.02), (0.13, 0.24, 0.07))
    C.florida_woods(pts, seed=4, height=(9.0, 15.0), crown=(2.2, 3.6), trunk=(0.16, 0.13, 0.1), c1=lf[0], c2=lf[1],
                    name="cyp")
    bpts = []
    for i in range(90):
        y = rnd.uniform(max(y_range[0], -30.0), min(y_range[1], 60.0))
        x = creek_cx(y) + rnd.choice((-1, 1)) * rnd.uniform(5.2, 8.0)
        if 2.8 < x < 9.0 and abs(y + 0.5) < 6.0:
            continue
        bpts.append((x, y, creek_z(x, y)))
    C.jungle(bpts, size=(0.6, 1.5), seed=6, c1=lf[0], c2=(lf[1][0] * 1.2, lf[1][1] * 1.2, lf[1][2]), name="bush")
    wat = None
    if not flood:
        wat = L.prim("plane", loc=(0, 45, 0.0), size=1, name="creekwater")
        wat.scale = (70, 220, 1)
        L.apply_scale(wat)
        wm, _ = C.clear_water_mat("clearwater", n=n, t0=t0, alpha=0.18, glint=1.2, glint_scale=26.0, glint_cut=(0.82, 0.86))
        L.assign(wat, wm)
        wat.visible_shadow = False
    return {"sun": sun, "bg": bg, "rock": rock, "water": wat}


SWIM = {"A": dict(suit=(0.85, 0.07, 0.05), ang=165.0, ph=0.0), "B": dict(suit=(0.95, 0.75, 0.08), ang=40.0, ph=1.7)}


def _swimmers(L, n, t0=0.0, which=("A", "B"), rings=True):
    """Two generic faceless swimmers floating on their backs at the rim, legs hanging over the dark."""
    pts = []
    for k in which:
        s = SWIM[k]
        p = C.swimmer_float("swim" + k, suit=s["suit"])
        a = math.radians(s["ang"])
        out = Vector((math.cos(a), math.sin(a), 0.0))
        base = out * (HR + 0.1) - out * 0.95                  # root = feet end, 0.95 m inside the rim
        yaw = math.atan2(out.x, -out.y)
        r = p["root"]
        for f in list(range(1, n + 1, 3)) + [n]:
            t = t0 + (f - 1) / 24.0
            r.location = (base.x, base.y, 0.03 + 0.025 * math.sin(1.6 * t + s["ph"]))
            r.rotation_euler = (math.pi / 2 + 0.03 * math.sin(1.1 * t + s["ph"]), 0, yaw + 0.05 * math.sin(0.7 * t + s["ph"]))
            r.keyframe_insert("location", frame=f)
            r.keyframe_insert("rotation_euler", frame=f)
            for tag, sg in (("L", 1), ("R", -1)):
                p[f"hip{tag}"].rotation_euler = (-0.6 + 0.1 * math.sin(2.2 * t + s["ph"] + sg), sg * 0.14, 0)
                p[f"hip{tag}"].keyframe_insert("rotation_euler", frame=f)
        mid = out * (HR + 0.1) - out * 0.35
        pts.append((mid.x, mid.y, 0.012))
    if rings:
        C.time_rings(pts, n, t0=t0, period=2.2, rmax=0.5, strength=1.1, seed=5, name="ripple", minor=0.006)
    return pts


def S01(L, n):
    _creek(L, n, trees=120, t0=0.0)
    _swimmers(L, n, t0=0.0)
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, P0, T0), (n, P1, T1)], shake=0.04, rot_shake=0.003, rate=0.5, seed=3,
              shake_keys=[(1, 0.0), (12, 1.0), (n, 1.0)], fn=lambda x: 1 - (1 - x) ** 2)
    L.bake_static()


def S18(L, n):
    t0 = -(n - 1) / 24.0                                       # frame n lands on S01's frame-1 phase
    _creek(L, n, trees=120, t0=t0)
    _swimmers(L, n, t0=t0)
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (0.0, -2.4, 2.9), (0.0, 0.15, 0.0)), (n, P0, T0)], shake=0.04, rot_shake=0.003, rate=0.5,
              seed=3, shake_keys=[(1, 1.0), (n - 12, 1.0), (n, 0.0)], fn=C.sm)
    L.bake_static()


def S04(L, n):
    """Map backdrop: the creek from high above, soft."""
    _creek(L, n, trees=190, y_range=(-45.0, 70.0))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (3.0, -14.0, 46.0), (0.5, 2.0, 0.0)), (n, (-1.0, -8.0, 44.0), (0.0, 5.0, 0.0))],
              fn=lambda x: x)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 6.0
    cam.data.dof.aperture_fstop = 0.3
    L.bake_static()


def S17(L, n):
    """Present day: plain NO SCUBA DIVING sign on the ledge, the calm blue mouth behind it."""
    _creek(L, n, trees=120, t0=0.0)
    sp = (4.9, -0.95)
    c0 = Vector((7.2, -0.7, 1.95))
    d = (Vector((c0.x, c0.y)) - Vector(sp)).normalized()
    sg = C.park_sign(loc=(sp[0], sp[1], creek_z(*sp) - 0.05), rot_z=math.atan2(d.x, -d.y), w=0.8, h=0.64, post=1.05,
                     lines=("NO", "SCUBA", "DIVING"), name="psign")
    bp = sg["board"].active_material.node_tree.nodes["Principled BSDF"]
    bp.inputs["Emission Color"].default_value = (0.88, 0.86, 0.78, 1)
    bp.inputs["Emission Strength"].default_value = 0.55
    C.time_rings([(0.9, 0.5, 0.012), (-0.7, -0.9, 0.012), (-2.6, 2.2, 0.012)], n, period=2.6, rmax=0.5, strength=1.0,
                 seed=9, name="ripple", per_point=1)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, tuple(c0), (2.6, -1.0, 0.95)), (n, (7.2, -0.3, 1.9), (2.45, -0.9, 0.9))], shake=0.02,
              rot_shake=0.002, rate=0.4, seed=5, fn=C.sm)
    L.bake_static()


def S13(L, n):
    """1981: the creek in flood. Brown fast water hides the mouth completely; rain; branches race past."""
    env = _creek(L, n, trees=110, hole=False, flood=True, y_range=(-35.0, 80.0))
    C.flood_water(size=(70, 170), center=(0, 40, 0.85), n=n, flow=(0.25, 3.4), res=0.45, name="flood")
    C.rain((1.0, 4.0, 4.5), (16, 28, 9), count=2600, n=n, speed=9.5, length=0.55, width=0.006, strength=0.55, seed=3)
    wood = L.mat_noise_surface("drift_m", (0.05, 0.035, 0.02), (0.2, 0.14, 0.08), scale=14, bump=0.5, voronoi=False)
    leaf = L.mat_principled("drift_leaf", (0.05, 0.09, 0.03), rough=0.8)
    rnd = random.Random(6)
    for k in range(8):
        ln = rnd.uniform(1.4, 3.2)
        pts = [(0, 0, 0)]
        for j in range(1, 5):
            pts.append((rnd.uniform(-0.25, 0.25), ln * j / 4, rnd.uniform(-0.04, 0.12)))
        br = C.curve(pts, thickness=rnd.uniform(0.025, 0.06), mat=wood, name=f"branch{k}", smooth_pts=True)
        for j in range(2):
            tw = C.curve([pts[1 + j], (pts[1 + j][0] + rnd.uniform(-0.7, 0.7), pts[1 + j][1] + 0.5, 0.25)], thickness=0.015,
                         mat=wood, name=f"twig{k}_{j}")
            tw.parent = br
        if k % 2 == 0:
            lb = L.prim("ico", loc=(pts[3][0], pts[3][1], 0.12), subdivisions=1, radius=0.3, name=f"leaf{k}")
            lb.scale = (1.0, 1.4, 0.35)
            L.assign(lb, leaf)
            lb.parent = br
        x0 = rnd.uniform(-4.5, 5.5)
        y0 = rnd.uniform(-22.0, 6.0)
        sp = rnd.uniform(3.0, 3.8)
        rz = rnd.uniform(-0.9, 0.9)
        for f in (1, n // 2, n):
            t = (f - 1) / 24.0
            br.location = (x0 + 0.25 * t + 0.3 * math.sin(k + t), y0 + sp * t, 0.86 + 0.05 * math.sin(k * 2 + t * 3))
            br.rotation_euler = (0.05 * math.sin(k + t * 2), 0.04 * math.cos(k + t * 2), rz + 0.25 * t * (1 if k % 2 else -1))
            br.keyframe_insert("location", frame=f)
            br.keyframe_insert("rotation_euler", frame=f)
        L.linear_fcurves(br)
    # one soft double flash with the thunder sfx (0.6 s)
    C.key_energy(env["sun"], [(1, 0.9), (13, 0.9), (15, 4.5), (17, 1.2), (19, 3.5), (23, 0.9), (n, 0.9)])
    C.key_input(env["bg"].inputs[1], [(1, 1.0), (13, 1.0), (15, 2.6), (17, 1.1), (19, 2.2), (23, 1.0), (n, 1.0)])
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (-2.2, -10.0, 2.3), (1.0, 0.0, 0.75)), (n, (-1.4, -8.6, 2.15), (4.2, 6.0, 0.9))], shake=0.07,
              rot_shake=0.008, rate=0.9, seed=4, fn=lambda x: x)
    L.bake_static()


# ============================================================================ the shaft and the bend (S02 S03)

SP = [(0, 0, 0.8), (0, 0, -2.5), (0, 0, -6.0), (0, 0.25, -8.4), (0, 1.5, -10.3), (0, 4.0, -12.0), (0, 8.0, -14.2),
      (0, 12.5, -16.6)]


def _shaft_zc(y):
    pts = [(p[1], p[2]) for p in SP[3:]]
    if y <= pts[0][0]:
        return pts[0][1]
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return pts[-1][1] - 0.53 * (y - pts[-1][0])


def _sand_z(x, y):
    base = _shaft_zc(max(y, 1.5)) - 1.02 + (0.9 * (1.5 - y) if y < 1.5 else 0.0)
    return base + 0.55 * (x / 1.4) ** 2 + 0.03 * noise.noise(Vector((x * 2.0, y * 2.0, 0.5)))


def _shaft_set(L, n):
    """~30 ft vertical shaft that bends into an inclined passage (one tube), sand at the bend."""
    _uw(26.0)
    rock = C.rock_mat("shaftrock", (0.035, 0.04, 0.04), (0.36, 0.36, 0.32), scale=2.2, bump=1.0)
    C.tube_along(SP, ring=36, seg=8, seed=4, rough=0.16,
                 radius_fn=lambda t, a: C.lerp(2.05, 1.6, C.sm((t - 0.4) / 0.25)),
                 squash_fn=lambda t: (1.0, C.lerp(1.0, 0.72, C.sm((t - 0.45) / 0.2))), mat=rock, name="shaft",
                 disp=(0.3, 0.08))
    sand = L.mat_noise_surface("vent_sand", (0.2, 0.18, 0.13), (0.42, 0.38, 0.29), scale=14, bump=0.3, voronoi=False)
    C.heightfield(size=(7.0, 17.0), center=(0, 5.5, 0), res=0.12, fn=_sand_z, mat=sand, name="sand", disp=(0, 0))


def _surface_from_below(L, n):
    """The bright mouth seen from inside the shaft: an emissive, rippling aqua sheet above the swimmers."""
    o = L.prim("plane", loc=(0, 0, 0.32), size=7.5, name="surface")
    m, nd, l = L._mat("surface_m")
    for x in list(nd):
        if x.type == "BSDF_PRINCIPLED":
            nd.remove(x)
    tc = nd.new("ShaderNodeTexCoord")
    mp = nd.new("ShaderNodeMapping")
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = nd.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 2.6
    nz.inputs["Detail"].default_value = 3
    l.new(mp.outputs["Vector"], nz.inputs["Vector"])
    ramp = nd.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.38
    ramp.color_ramp.elements[0].color = (0.2, 0.75, 0.72, 1)
    ramp.color_ramp.elements[1].position = 0.62
    ramp.color_ramp.elements[1].color = (0.85, 1.0, 0.97, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    em = nd.new("ShaderNodeEmission")
    em.inputs[1].default_value = 2.0
    l.new(ramp.outputs["Color"], em.inputs[0])
    l.new(em.outputs[0], nd["Material Output"].inputs["Surface"])
    C.key_input(mp.inputs["Location"], [(1, (0, 0, 0)), (n, (0.3, 0.2, 0.5))])
    L.assign(o, m)
    o.visible_shadow = False
    return o


def S02(L, n):
    _shaft_set(L, n)
    _surface_from_below(L, n)
    _swimmers(L, n, t0=0.0, rings=False)                       # dark legs against the bright circle
    for k, (x, y, tx, ty, deg, e) in enumerate(((0.5, 0.3, 0.1, 0.9, 13, 2600), (-0.6, -0.2, -0.9, 0.3, 10, 2000),
                                                (0.1, 0.8, 0.5, 1.4, 16, 2600), (-0.2, -0.7, 0.3, -0.5, 9, 1800))):
        sp = L.spot((x, y, 3.0), (0, 0, 0), energy=e, size_deg=deg, blend=0.5, color=(0.75, 1.0, 0.95), name=f"ray{k}")
        _aim(sp, (x, y, 3.0), (tx, ty, -9.0))
    L.spot((0, 0, 2.2), (0, 0, 0), energy=1800, size_deg=75, blend=0.8, color=(0.55, 0.95, 0.9), name="daylight")
    C.water(center=(0, 2.5, -8.0), size=(7, 14, 19), color=(0.3, 0.75, 0.72), density=0.012, name="uw")
    s = C.cloud((0, 0.9, -5.5), (3.0, 1.6, 8.0), count=240, radius=0.003, color=(0.8, 0.95, 0.9), emit=0.08, seed=3)
    C.drift(s, n, (0.0, 0.0, 0.06))
    cam = C.camera(lens=20)
    C.aim_cam(cam, n, [(1, (0, -1.15, -2.2), (0, 1.2, -0.6)), (int(n * 0.55), (0, -1.1, -4.9), (0, 2.2, -6.0)),
                       (n, (0, -0.95, -6.9), (0, 2.6, -10.9))], shake=0.03, rot_shake=0.004, fn=lambda x: x)
    C.cam_fill(cam, energy=130, color=(0.5, 0.9, 0.9))
    L.bake_static()


def S03(L, n):
    """At the bend: sand and silt lifted by water welling up out of the dark opening."""
    _shaft_set(L, n)
    L.spot((0, 0.3, -3.0), (0, 0, 0), energy=1500, size_deg=50, blend=0.9, color=(0.45, 0.9, 0.85), name="daylight")
    C.water(center=(0, 3.0, -11.0), size=(6, 15, 13), color=(0.3, 0.7, 0.68), density=0.012, name="uw")
    T = Vector((0, 0.86, -0.51)).normalized()                 # down the passage
    U = Vector((0, 0.51, 0.86)).normalized()                  # passage 'up'
    c0 = Vector((0.1, 0.3, _sand_z(0.1, 0.3) + 1.0))
    tilt = math.atan2(T.z, T.y)
    grain = L.mat_principled("grain_m", (0.9, 0.85, 0.7), rough=1, emit=(0.8, 0.9, 0.85), emit_strength=0.25)
    for k, (lat, up, cnt) in enumerate(((-1.0, -0.2, 260), (1.0, -0.15, 260), (0.0, 0.75, 200))):
        cen = c0 + T * 3.6 + Vector((lat, 0, 0)) + U * up
        s = C.cloud(tuple(cen), (0.75, 6.0, 0.75), count=cnt, radius=0.003, seed=20 + k, mat=grain, name=f"up{k}")
        s.rotation_euler = (tilt, 0, 0)
        C.drift(s, n, tuple(-T * 0.9 + U * 0.12))
    lay = C.cloud(tuple(c0 + T * 4.2 - U * 0.85), (1.5, 4.6, 0.14), count=400, radius=0.003, seed=31, mat=grain, name="lift")
    lay.rotation_euler = (tilt, 0, 0)
    C.drift(lay, n, tuple(-T * 0.35 + U * 0.28))
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, tuple(c0), tuple(c0 + T * 6.5 - U * 0.55)), (n, tuple(c0 + T * 0.7), tuple(c0 + T * 7.2 - U * 0.55))],
              shake=0.015, rot_shake=0.003, fn=lambda x: x)
    C.cam_fill(cam, energy=170, color=(0.45, 0.85, 0.9))
    L.bake_static()


# ============================================================================ 2.5D side-section (S05 S14)

KFT = 0.06                                                    # diagram units per foot
ROUTE_FT = [(1.6, -0.5), (1.6, 12), (1.6, 23), (1.42, 32), (0.75, 44), (0.1, 58), (-0.6, 72), (-1.25, 84), (-1.9, 93),
            (-2.45, 101), (-3.1, 110), (-3.75, 121)]
WIDTH = [0.33, 0.33, 0.33, 0.3, 0.62, 0.2, 0.58, 0.13, 0.45, 0.12, 0.66, 0.14]
CH_IDX = (4, 6, 8, 10)                                        # control points that are the four chambers
TAIL_FT = [(-3.75, 121), (-4.1, 127), (-4.45, 133)]
SEG = 8


def _rock_world(name):
    """Dark diagram rock keyed on world position (the cover plates must match the slab exactly)."""
    m, n, l = C.L._mat(name)
    p = n["Principled BSDF"]
    geo = n.new("ShaderNodeNewGeometry")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.2
    nz.inputs["Detail"].default_value = 8
    l.new(geo.outputs["Position"], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.03, 0.033, 0.036, 1)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (0.115, 0.12, 0.125, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.9
    return m


def _section(L, name="xs"):
    """Generic side-section (not traced from a survey): ~30 ft entrance shaft, a passage angling down through four
    chambers, depth marks at the two narrated depths, dashed continuation past chamber 4.
    Returns dict(route [Vector], chambers [(x, z)], cam helpers)."""
    C.world_black((0.0, 0.0, 0.0))
    ctrl = [(x, 0.0, -ft * KFT) for x, ft in ROUTE_FT]
    cen = C.catmull(ctrl, SEG)
    hw = []
    for i in range(len(cen)):
        k, t = divmod(i, SEG)
        hw.append(WIDTH[k] if k >= len(WIDTH) - 1 else C.lerp(WIDTH[k], WIDTH[k + 1], C.sm(t / SEG)))
    band = C.offset_band([(p.x, p.z) for p in cen], hw)
    rock = _rock_world(name + "_rk")
    xs = C.xsection([(x, -z) for x, z in band], lambda d: -d, extent=(-9.5, 9.5, -17.0, 0.0), water_top=(0.03, 0.24, 0.3),
                    water_bot=(0.0, 0.035, 0.07), outline_color=C.CYAN, outline_strength=3.0, name=name, rock_mat_=rock)
    # creek surface, banks, trees
    gl = C.emis(name + "_gl", (0.45, 0.6, 0.35), 2.2)
    C.curve([(-9.5, -0.42, 0.0), (1.27, -0.42, 0.0)], thickness=0.02, mat=gl, name=name + "_gl1")
    C.curve([(1.93, -0.42, 0.0), (9.5, -0.42, 0.0)], thickness=0.02, mat=gl, name=name + "_gl2")
    C.curve([(1.27, -0.43, 0.0), (1.93, -0.43, 0.0)], thickness=0.022, mat=C.emis(name + "_wl", (0.5, 1.0, 0.95), 3.0),
            name=name + "_waterline")
    rnd = random.Random(3)
    tm = C.emis(name + "_tree", (0.25, 0.45, 0.2), 1.2)
    for i in range(16):
        x = rnd.choice((-1, 1)) * rnd.uniform(1.4, 7.5) + 1.6
        o = L.prim("sphere", loc=(x, -0.42, 0.42), segments=10, ring_count=6, radius=rnd.uniform(0.2, 0.36),
                   name=name + "_tree")
        o.scale = (1.0, 0.3, 1.5)
        L.assign(o, tm)
    # depth marks: only the two narrated depths
    dm = C.emis(name + "_dm", (0.55, 0.7, 0.7), 1.1)
    for ft, x1 in ((30, 1.15), (100, -3.9)):
        z = -ft * KFT
        C.curve([(-5.9, -0.44, z), (x1, -0.44, z)], thickness=0.008, mat=dm, name=f"{name}_d{ft}")
        C.text(f"{ft} FT", (-5.9, -0.45, z + 0.22), size=0.34, color=(0.75, 0.9, 0.9), strength=2.0, align="LEFT",
               name=f"{name}_t{ft}")
    L.area((-3, -8, 1), (math.radians(60), 0, math.radians(-25)), energy=1100, size=10, color=(0.7, 0.85, 1.0))
    L.area((2, -8, -9), (math.radians(75), 0, math.radians(25)), energy=800, size=10, color=(0.8, 0.85, 0.9))
    route = [Vector((p.x, -0.46, p.z)) for p in cen]
    chambers = [(ROUTE_FT[i][0], -ROUTE_FT[i][1] * KFT) for i in CH_IDX]
    return {"xs": xs, "route": route, "chambers": chambers, "rock": rock, "cen": cen}


def _route_frac(route, upto_idx):
    lens = [(b - a).length for a, b in zip(route, route[1:])]
    return sum(lens[:upto_idx]) / sum(lens)


def S05(L, n):
    sec = _section(L, "s5")
    full = sec["route"]
    end_i = CH_IDX[3] * SEG                                   # the dot stops in chamber 4
    route = full[:end_i + 1]
    keys = [(4, 0.0), (n - 12, 1.0)]
    dot, _, _ = C.glow_dot(tuple(route[0]), C.CYAN, r=0.085, halo=2.6, strength=7, name="dot")
    C.move_along(dot, route, keys, step=1)
    trail = C.curve([tuple(p) for p in route], thickness=0.022, mat=C.emis("trail", C.CYAN, 2.2), name="trail")
    trail.data.bevel_factor_mapping_end = "SPLINE"
    for f in range(1, n + 1):
        trail.data.bevel_factor_end = C.piecewise(keys, f)
        trail.data.keyframe_insert("bevel_factor_end", frame=f)
    # chambers pop in (cover plates hide them until the dot gets near), numbered 1-4
    for k, ci in enumerate(CH_IDX):
        cx, cz = sec["chambers"][k]
        frac = _route_frac(route, ci * SEG) if ci * SEG < len(route) else 1.0
        fpop = next((f for f in range(1, n + 1) if C.piecewise(keys, f) >= frac - 0.13), n - 14)
        r = WIDTH[ci] + 0.2
        ring = [(cx + r * 1.12 * math.cos(a), cz + r * math.sin(a)) for a in [2 * math.pi * j / 28 for j in range(28)]]
        cov = C.flat_poly(ring, -0.435, sec["rock"], name=f"cover{k}")
        cov.visible_shadow = False
        C.hide_from_frame([cov], f_hide=fpop)
        num = C.text(str(k + 1), (cx - 0.75, -0.5, cz + 0.42), size=0.62, color=(1, 1, 1), strength=3.5, name=f"num{k}")
        C.hide_from_frame([num], f_show=max(2, fpop))
    tail = C.dotted_path([(x, -0.46, -ft * KFT) for x, ft in TAIL_FT], spacing=0.16, r=0.03, color=C.CYAN, strength=2.5,
                         name="tail")
    C.pop_in(tail, [n - 13 + 2 * i for i in range(len(tail))], dur=3, overshoot=1.2)
    cam = C.camera(lens=30)
    C.aim_cam(cam, n, [(1, (0.25, -20.9, -7.0), (0.25, 0.0, -7.0)), (n, (0.2, -19.2, -6.6), (0.2, 0.0, -6.6))], fn=C.sm)
    _hud_text(cam, 30, "SCHEMATIC, NOT TO SCALE", 60, 262, size_px=30, name="note")
    L.bake_static()


def S14(L, n):
    """Mid-point turn: one dot left in the deepest chamber dims to an ember while the years run 1979 -> 2000."""
    sec = _section(L, "s14")
    end_i = CH_IDX[3] * SEG
    route = sec["route"][:end_i + 1]
    C.curve([tuple(p) for p in route], thickness=0.018, mat=C.emis("trail", C.CYAN, 0.9), name="trail")
    for k, (cx, cz) in enumerate(sec["chambers"]):
        C.text(str(k + 1), (cx, -0.5, cz + (0.0 if k < 3 else 0.42)), size=0.42 if k < 3 else 0.32, color=(1, 1, 1),
               strength=2.0 if k < 3 else 1.4, name=f"num{k}")
    C.dotted_path([(x, -0.46, -ft * KFT) for x, ft in TAIL_FT], spacing=0.16, r=0.03, color=C.CYAN, strength=1.6, name="tail")
    cx, cz = sec["chambers"][3]
    dot, halo, hem = C.glow_dot((cx, -0.47, cz - 0.12), C.CYAN, r=0.085, halo=3.0, strength=8, name="dot")
    core = dot.active_material.node_tree.nodes["Emission"].inputs[1]
    f1 = int(n * 0.78)
    C.key_input(core, [(1, 8.0), (10, 8.0), (f1, 0.25), (n, 0.12)])
    C.key_input(hem.inputs[1], [(1, 2.8), (10, 2.8), (f1, 0.03), (n, 0.0)])
    ember, _, ehem = C.glow_dot((cx, -0.48, cz - 0.12), (1.0, 0.45, 0.12), r=0.04, halo=2.2, strength=0.0, name="ember")
    ecore = ember.active_material.node_tree.nodes["Emission"].inputs[1]
    C.key_input(ecore, [(1, 0.0), (int(n * 0.45), 0.0), (f1, 1.6), (n, 1.1)])
    C.key_input(ehem.inputs[1], [(1, 0.0), (int(n * 0.45), 0.0), (f1, 0.35), (n, 0.25)])
    cam = C.camera(lens=30)
    C.aim_cam(cam, n, [(1, (-1.6, -17.4, -5.6), (-1.6, 0.0, -5.6)), (n, (-3.1, -9.9, -7.07), (-3.1, 0.0, -7.07))], fn=C.sm)
    _hud_text(cam, 30, "SCHEMATIC, NOT TO SCALE", 60, 262, size_px=30, name="note")
    # calendar strip under the counter: 1979 ... 2000, in step with the 'YEARS MISSING' overlay
    dur = 3.5
    xa, xb, py = 170.0, 910.0, 668.0
    a, b = Vector(_hud(cam, 30, xa, py)), Vector(_hud(cam, 30, xb, py))
    base = C.curve([tuple(a), tuple(b)], thickness=0.0022, mat=C.emis("cal_base", (0.6, 0.65, 0.65), 1.0), name="cal_base")
    base.parent = cam
    prog = C.curve([tuple(a), tuple(b)], thickness=0.0042, mat=C.emis("cal_prog", C.CYAN, 3.0), name="cal_prog")
    prog.parent = cam
    prog.data.bevel_factor_mapping_end = "SPLINE"
    tick_m = C.emis("cal_tick", (0.8, 0.85, 0.85), 1.4)
    for k in range(22):
        p = a.lerp(b, k / 21.0)
        h = 0.014 if k in (0, 21) else 0.007
        tk = C.curve([(p.x, p.y - h, p.z), (p.x, p.y + h, p.z)], thickness=0.0016, mat=tick_m, name=f"cal_t{k}")
        tk.parent = cam
    mk, _, _ = C.glow_dot(tuple(a), C.CYAN, r=0.009, halo=2.4, strength=6, name="cal_dot")
    mk.parent = cam
    for f in range(1, n + 1):
        x = min(1.0, ((f - 1) / 24.0) / (dur * 0.9))
        pr = 1 - (1 - x) ** 3                                 # same easing as overlays.ov_timer
        prog.data.bevel_factor_end = max(0.001, pr)
        prog.data.keyframe_insert("bevel_factor_end", frame=f)
        mk.location = a.lerp(b, pr)
        mk.keyframe_insert("location", frame=f)
    _hud_text(cam, 30, "1979", xa, py + 46, size_px=40, color=(0.9, 0.95, 0.95), strength=2.2, align="CENTER",
              font=C.FONT_ANTON, name="y1979")
    _hud_text(cam, 30, "2000", xb, py + 46, size_px=40, color=(0.9, 0.95, 0.95), strength=2.2, align="CENTER",
              font=C.FONT_ANTON, name="y2000")
    L.bake_static()


# ============================================================================ S06 the disputed count (paper backdrop)

def S06(L, n):
    C.world_black((0.0, 0.003, 0.004))
    wet = L.mat_noise_surface("wetrock", (0.035, 0.035, 0.033), (0.3, 0.28, 0.24), scale=2.6, bump=0.9, rough=0.32)
    C.heightfield(size=(3.4, 4.4), center=(0, 0, 0), res=0.05,
                  fn=lambda x, y: 0.035 * noise.noise(Vector((x * 1.2, y * 1.2, 0.4))) + 0.012 * noise.noise(Vector((x * 5, y * 5, 2.0))),
                  mat=wet, name="slab", disp=(0, 0))
    lm = L.mat_principled("coil_m", (0.95, 0.9, 0.7), rough=0.45, emit=(0.95, 0.9, 0.7), emit_strength=0.35)
    cx, cy = -0.27, -0.62
    coil = [(cx + (0.06 + 0.0011 * i) * math.cos(i * 0.3), cy + (0.06 + 0.0011 * i) * math.sin(i * 0.3), 0.05 + 0.0002 * i)
            for i in range(130)]
    coil += [(cx + 0.21, cy + 0.12, 0.05), (cx + 0.1, cy + 0.42, 0.045), (cx - 0.25, cy + 0.6, 0.05), (cx - 0.5, cy + 1.3, 0.05)]
    C.curve(coil, thickness=0.006, mat=lm, name="coil", smooth_pts=True)
    C.dive_torch((0.3, -0.7, 0.085), (-0.3, 0.5, 0.06), energy=120, size_deg=34, beam_len=1.2, beam_strength=0.07)
    key = L.spot((-0.9, -1.3, 1.9), (0, 0, 0), energy=260, size_deg=40, blend=0.7, color=(1.0, 0.86, 0.62), name="sweep")
    tg = _track(key, (-0.5, 0.2, 0.0), "sweep_tgt")
    C.key_loc(tg, [(1, (-0.55, 0.3, 0.0)), (n // 2, (0.2, -0.45, 0.0)), (n, (0.4, -0.75, 0.0))])
    C.drip_rings([(-0.4, -0.2, 0.05), (0.38, -0.42, 0.045), (0.02, -0.85, 0.045), (0.42, 0.5, 0.05)], n, period=28, seed=2,
                 color=(1.0, 0.9, 0.7), strength=1.6, rmax=0.13, name="drip")
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.0, -0.03, 2.6), (0.0, 0.0, 0.0), -2.5), (n, (0.03, -0.03, 2.42), (0.03, 0.0, 0.0), 3.0)], fn=C.sm)
    C.cam_fill(cam, energy=14, color=(0.6, 0.8, 0.9))
    L.bake_static()


# ============================================================================ the angled passage (S07 S08)

SLOPE = 0.36


def _pz(y):
    return -SLOPE * y


def _px(y):
    b = 0.0 if y < 14.0 else (0.3 * (y - 14.0) ** 2 if y < 16.0 else 1.2 + 1.2 * (y - 16.0))
    return 0.5 * math.sin(y * 0.16) + b


def _slope_passage(L, n, density=0.035):
    _uw(26.0)
    rock = C.rock_mat("pas", (0.04, 0.045, 0.045), (0.36, 0.35, 0.31), scale=1.1, bump=0.9)
    pas, info = C.passage(length=36, y0=-8, half_w=1.9, half_h=1.35, seed=7, rough=0.14, floor_flat=0.3, x_fn=_px,
                          z_fn=_pz, mat=rock, disp=(0.25, 0.07))
    fz = lambda x, y: (info["floor"](y) + 0.1 + 0.04 * noise.noise(Vector((x * 1.5, y * 1.5, 0.3)))
                       + 0.22 * ((x - _px(y)) / 1.9) ** 2)
    C.heightfield(size=(22, 36), center=(8.0, 10.0, 0), res=0.22, fn=fz,
                  mat=C.silt_mat("pfloor", (0.2, 0.18, 0.13), (0.42, 0.38, 0.3)), name="pfloor", disp=(0, 0))
    w = C.water(center=(7.0, 10.0, _pz(10.0)), size=(24, 38, 5.6), color=TEAL, density=density, name="uw")
    w.rotation_euler = (-math.atan(SLOPE), 0, 0)
    return info


def _hand_torch(d, side="R"):
    """Move the rig's head lamp to the right hand (the 1979 pair carried handheld lights)."""
    sx = 1 if side == "R" else -1
    d[f"shoulder{side}"].rotation_euler = (0.0, 0, 0)
    d["lamp"].location = (sx * 0.2, 0.8, 0.02)
    d["lens"].location = (sx * 0.2, 0.87, 0.02)
    d["torch"].location = (sx * 0.2, 0.9, 0.02)


def _pair(L, n, y_fn, energy=1500, beam_len=5.0, bubbles=True):
    """The 1979 pair: generic single-tank divers, blue / white fins, handheld lights, side by side."""
    out = []
    for name, fins, dx, dz, ph in (("dvA", (0.1, 0.3, 0.95), -0.55, -0.25, 0.0), ("dvB", (0.92, 0.92, 0.9), 0.55, -0.38, 1.4)):
        d = C.diver(name, fins=fins, suit=(0.1, 0.11, 0.13), tanks="single", rebreather=False, light_energy=energy, beam_len=beam_len,
                    beam_strength=0.5, beam_deg=20)
        _hand_torch(d)
        r = d["root"]

        def pos(f, dx=dx, dz=dz, ph=ph):
            y = y_fn(f)
            return Vector((_px(y) + dx, y, _pz(y) + dz + 0.04 * math.sin(f * 0.13 + ph)))
        for f in list(range(1, n + 1, 3)) + [n]:
            p0, p1 = pos(f), pos(f + 1)
            r.location = p0
            r.rotation_euler = (p1 - p0).to_track_quat("Y", "Z").to_euler()
            r.keyframe_insert("location", frame=f)
            r.keyframe_insert("rotation_euler", frame=f)
        L.linear_fcurves(r)
        L.anim_swim(d, n, kick_rate=0.9, amp=0.3)
        t = d["torch"]
        for f in range(1, n + 1, 6):
            t.rotation_euler = (math.pi / 2 + 0.1 * math.sin(f * 0.11 + ph), 0, 0.28 * math.sin(f * 0.07 + ph * 2))
            t.keyframe_insert("rotation_euler", frame=f)
        if bubbles:
            C.bubble_trail(lambda f, pos=pos: pos(f) + Vector((0, 0.5, 0.1)), n, count=22, rise=0.9, size=0.02,
                           seed=5 + int(ph * 3), name=name + "_bub")
        d["pos"] = pos
        out.append(d)
    return out


def S07(L, n):
    info = _slope_passage(L, n)
    yf = lambda f: 2.0 + 5.2 * (f - 1) / (n - 1)
    pair = _pair(L, n, yf)
    rim = L.spot((-0.3, 3.8, 1.1), (0, 0, 0), energy=450, size_deg=45, blend=0.7, color=CYAN_RIM, parent=pair[0]["root"],
                 name="rim")
    rim.rotation_mode = "QUATERNION"
    rim.rotation_quaternion = Vector((0.6, -3.8, -1.2)).to_track_quat("-Z", "Y")
    # silt puffs lifted by the fin kicks (floor level, well below the lens)
    for k, f0 in enumerate((6, 20, 34, 48, 62, 74)):
        d = pair[k % 2]
        p = d["pos"](f0)
        y = p.y - 1.25
        c = (p.x, y, info["floor"](y) + 0.3)
        s = C.cloud(c, (0.5, 0.5, 0.25), count=160, radius=0.003, color=(0.75, 0.68, 0.5), emit=0.1, shape="sphere",
                    seed=40 + k, name=f"puff{k}")
        C.hide_from_frame([s], f_show=max(2, f0), f_hide=f0 + 26)
        C.key_scale(s, [(max(1, f0 - 1), 0.05), (f0 + 10, 1.0), (f0 + 44, 1.5)])
        C.key_loc(s, [(f0, c), (f0 + 44, (c[0], c[1], c[2] + 0.22))])
    cam = C.camera(lens=35)
    keys = []
    for f in (1, n // 2, n):
        yd = yf(f)
        keys.append((f, (_px(yd - 4.0) * 0.6, yd - 4.0, _pz(yd - 4.0) + 0.75), (_px(yd - 0.6) * 0.8, yd - 0.6, _pz(yd - 0.6) - 0.95)))
    C.aim_cam(cam, n, keys, shake=0.03, rot_shake=0.004, rate=0.6, seed=2, fn=lambda x: x)
    C.cam_fill(cam, energy=300, color=(0.65, 0.88, 0.92))
    L.bake_static()


def S08(L, n):
    """The two lights shrink away around the bend and go out. Nothing comes back."""
    _slope_passage(L, n, density=0.04)
    f_out = int(n * 0.62)
    yf = lambda f: 10.0 + 8.7 * min(1.0, (f - 1) / (f_out + 4.0)) + 0.02 * f
    pair = _pair(L, n, yf, energy=2200, beam_len=4.0, bubbles=False)
    for d in pair:
        C.key_energy(d["torch"], [(1, 2200), (f_out - 8, 2200), (f_out, 0.0), (n, 0.0)])
        C.key_input(d["beam_sock"], [(1, 0.5), (f_out - 8, 0.5), (f_out, 0.0), (n, 0.0)])
        lens = d["lens"].active_material.node_tree.nodes["Emission"].inputs[1]
        C.key_input(lens, [(1, 30.0), (f_out - 6, 30.0), (f_out, 0.0), (n, 0.0)])
    # their glow lingers on the silt for a moment after they are gone
    yb = 17.2
    glow = L.point((_px(yb) - 0.4, yb, _pz(yb) - 0.2), energy=0.0, color=(1.0, 0.9, 0.7), radius=0.5, name="linger")
    C.key_energy(glow, [(1, 0.0), (f_out - 10, 0.0), (f_out - 2, 420.0), (f_out + 5, 260.0), (n - 4, 0.0), (n, 0.0)])
    L.point((0.3, 6.0, _pz(6.0) + 0.9), energy=22, color=(0.3, 0.8, 0.8), radius=1.0, name="amb1")
    L.point((0.4, 13.0, _pz(13.0) + 0.9), energy=26, color=(0.3, 0.8, 0.8), radius=1.0, name="amb2")
    s = C.cloud((0.3, 7.5, _pz(7.5) - 0.2), (2.6, 9.0, 1.6), count=700, radius=0.004, color=(0.75, 0.8, 0.75), emit=0.12, seed=8)
    C.drift(s, n, (0.0, 0.0, -0.03))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.15, 0.4, _pz(0.4) + 0.55), (0.75, 12.0, _pz(12.0) + 0.15)),
                       (n, (0.15, 0.85, _pz(0.85) + 0.55), (0.75, 12.4, _pz(12.4) + 0.15))], shake=0.012, rot_shake=0.002, fn=C.sm)
    C.cam_fill(cam, energy=30, color=(0.35, 0.8, 0.8))
    L.bake_static()


# ============================================================================ S09 the squeeze (POV in a low gravel slot)

def _slot_floor(x, y):
    return -0.03 * y + 0.035 * noise.noise(Vector((x * 1.7, y * 1.7, 0.2))) + 0.5 * max(0.0, abs(x) - 1.25) ** 1.5


def _slot_gap(x, y):
    g = C.lerp(0.62, 0.2, C.sm(y / 6.5)) + 0.07 * noise.noise(Vector((x * 0.9, y * 0.9, 3.1)))
    return max(0.02, g * (1 - 0.85 * C.sm((abs(x) - 0.7) / 0.9)))


def S09(L, n):
    _uw(12.0)
    rock = C.rock_mat("slotrock", (0.05, 0.05, 0.048), (0.4, 0.38, 0.33), scale=2.2, bump=1.0)
    C.heightfield(size=(3.4, 9.5), center=(0, 3.4, 0), res=0.06, fn=_slot_floor,
                  mat=C.pebble_floor_mat("slotbed", scale=70.0), name="slotfloor", disp=(0, 0))
    C.heightfield(size=(3.4, 9.5), center=(0, 3.4, 0), res=0.07, fn=lambda x, y: _slot_floor(x, y) + _slot_gap(x, y),
                  mat=rock, name="slotceil", disp=(0, 0))
    gm = C.gravel_mat("gravel_m")
    C.gravel_field(_slot_floor, center=(0, 1.2), size=(2.6, 3.6), count=9000, psize=(0.008, 0.03), seed=3, subdiv=1, mat=gm,
                   name="gravel_near")
    C.gravel_field(_slot_floor, center=(0, 5.2), size=(2.6, 4.6), count=5000, psize=(0.012, 0.04), seed=4, subdiv=1, mat=gm,
                   name="gravel_far")
    C.water(center=(0, 3.5, 0.2), size=(4, 10, 2), color=(0.32, 0.6, 0.58), density=0.05, name="uw")
    s = C.cloud((0, 3.2, 0.2), (1.6, 3.4, 0.22), count=260, radius=0.003, color=(0.85, 0.8, 0.65), emit=0.15, seed=6)
    C.drift(s, n, (0.01, -0.03, 0.0))
    cam = C.camera(lens=18)
    C.aim_cam(cam, n, [(1, (0.0, -0.35, _slot_floor(0, -0.35) + 0.3), (0.0, 5.0, -0.42)),
                       (n, (0.05, 0.95, _slot_floor(0, 0.95) + 0.25), (0.0, 6.3, -0.46))], shake=0.012, rot_shake=0.006,
              rate=0.8, seed=5, fn=lambda x: x)
    torch = L.spot((0.1, -0.06, 0.02), (0, 0, 0), energy=45, size_deg=80, blend=0.8, color=C.TORCH, parent=cam, name="pov_torch")
    for f in range(1, n + 1, 5):
        torch.rotation_euler = (0.05 + 0.03 * math.sin(f * 0.21), 0.04 * math.sin(f * 0.13), 0)
        torch.keyframe_insert("rotation_euler", frame=f)
    L.bake_static()


# ============================================================================ the gravel slope at the restriction (S10 S11)

def _gs(y):
    """Floor profile: antechamber, then ~32 deg of loose gravel down into a low slot."""
    if y < -1.2:
        return -1.0
    if y < 1.8:
        s = (y + 1.2) / 3.0
        return -1.0 - 1.85 * (0.5 * s + 0.5 * C.sm(s))
    return -2.85 - 0.08 * (y - 1.8)


def _gc(y):
    """Ceiling profile: room height, coming down hard over the slope to a ~0.4 m slot."""
    return C.lerp(0.9, _gs(2.0) + 0.42, C.sm((y + 1.5) / 3.5)) - (0.08 * (y - 2.0) if y > 2.0 else 0.0)


def _gfloor(x, y):
    return _gs(y) + 0.13 + 0.035 * noise.noise(Vector((x * 1.4, y * 1.4, 0.6))) + 0.16 * (x / 2.0) ** 2


SLIDE_U = Vector((0.0, 3.0, -1.85)).normalized()              # downhill


def _gravel_set(L, n, dense=True):
    _uw(14.0)
    ff = 0.3
    H = lambda y: (_gc(y) - _gs(y)) / (2 - ff)
    rock = C.rock_mat("restr", (0.045, 0.045, 0.045), (0.38, 0.36, 0.31), scale=1.4, bump=1.0)
    C.passage(length=15, y0=-9, half_w=2.4, seed=9, rough=0.1, floor_flat=ff, mat=rock, disp=(0.12, 0.04),
              w_fn=lambda y: C.lerp(2.4, 1.5, C.sm((y + 0.5) / 2.5)), h_fn=H, z_fn=lambda y: _gc(y) - H(y), name="restr")
    C.heightfield(size=(5.4, 15), center=(0, -1.5, 0), res=0.09, fn=_gfloor, mat=C.pebble_floor_mat("slopebed", scale=55.0),
                  name="slopebed", disp=(0, 0))
    gm = C.gravel_mat("gravel_m")
    C.gravel_field(_gfloor, center=(0, 0.4), size=(3.4, 4.2), count=14000 if dense else 9000, psize=(0.01, 0.04), seed=3,
                   subdiv=1, mat=gm, name="gravel")
    if dense:
        C.gravel_field(_gfloor, center=(0.1, 0.9), size=(1.5, 1.9), count=2200, psize=(0.012, 0.04), seed=5, subdiv=2, mat=gm,
                       name="gravel_hero")
    return gm


def _roll(L, gm, k, x, y, f0, dist, dur, size, n):
    """One pebble ticking loose: starts at rest on the slope at frame f0, rolls `dist` m downhill in `dur` frames."""
    o = C.gravel_field(_gfloor, center=(x, y), size=(0.0, 0.0), count=1, psize=(size, size), seed=100 + k, subdiv=2, mat=gm,
                       name=f"roll{k}", sink=0.1)
    p0 = Vector(o.location) + Vector((0, 0, size * 0.25))
    hop = Vector((0, 0, size * 0.9))
    for f, t, h in ((f0, 0.0, 0.0), (f0 + dur * 0.35, 0.16, 0.6), (f0 + dur * 0.7, 0.62, 1.0), (f0 + dur, 1.0, 0.0)):
        o.location = p0 + SLIDE_U * dist * t + hop * h
        o.keyframe_insert("location", frame=f)
    o.rotation_euler = (0, 0, 0)
    o.keyframe_insert("rotation_euler", frame=f0)
    o.rotation_euler = (dist / max(size, 0.01) * 0.6, 0.7, 0.3)
    o.keyframe_insert("rotation_euler", frame=f0 + dur)
    return o


def _plume(L, n, center, size, keys_density, keys_scale, color=(0.5, 0.4, 0.27), name="plume"):
    o, dens, _ = C.noisy_volume(center, size, color=color, density=0.0, scale=1.7, name=name, anisotropy=0.3,
                                contrast=(0.35, 0.7))
    C.key_input(dens, keys_density)
    base = tuple(o.scale)
    for f, s in keys_scale:
        o.scale = (base[0] * s, base[1] * s, base[2] * s)
        o.keyframe_insert("scale", frame=f)
    return o


def S10(L, n):
    """Macro on the loose slope: pebbles tick loose, a small slide pours into the slot, silt swallows the beam."""
    gm = _gravel_set(L, n, dense=True)
    rnd = random.Random(8)
    f_slide = int(n * 0.4)
    for k, (x, y, f0) in enumerate(((0.28, 0.5, 3), (-0.1, 0.95, 8), (0.42, 0.85, 13), (0.05, 0.6, 17), (0.3, 1.1, 21))):
        _roll(L, gm, k, x, y, f0, rnd.uniform(0.25, 0.5), rnd.randint(9, 13), rnd.uniform(0.03, 0.05), n)
    for k in range(34):
        x, y = rnd.uniform(-0.35, 0.6), rnd.uniform(0.35, 1.25)
        _roll(L, gm, 10 + k, x, y, f_slide + rnd.randint(0, 9), min(1.9 - y, rnd.uniform(0.5, 1.2)) + 0.25,
              rnd.randint(11, 17), rnd.uniform(0.025, 0.05), n)
    c = (0.12, 0.8)
    sheet = C.gravel_field(lambda x, y: _gfloor(x, y) + 0.05 * max(0.0, 1 - ((x - c[0]) / 0.42) ** 2 - ((y - c[1]) / 0.36) ** 2),
                           center=c, size=(0.84, 0.7), count=900, psize=(0.012, 0.04), seed=7, subdiv=2, mat=gm, name="slump",
                           keep=lambda x, y: ((x - c[0]) / 0.42) ** 2 + ((y - c[1]) / 0.35) ** 2 < 1.0)
    p0 = Vector(sheet.location)
    for f, t, sc in ((1, 0.0, (1, 1, 1)), (f_slide - 1, 0.0, (1, 1, 1)), (f_slide + 4, 0.1, (1.03, 1.06, 0.97)),
                     (f_slide + 12, 0.62, (1.16, 1.3, 0.8)), (f_slide + 20, 1.0, (1.28, 1.5, 0.6))):
        sheet.location = p0 + SLIDE_U * 0.85 * t
        sheet.scale = sc
        sheet.keyframe_insert("location", frame=f)
        sheet.keyframe_insert("scale", frame=f)
    _plume(L, n, (0.1, 1.2, -2.25), (1.6, 1.8, 1.3), [(1, 0.0), (f_slide + 4, 0.0), (f_slide + 14, 3.0), (n, 7.0)],
           [(1, 0.25), (f_slide + 4, 0.25), (f_slide + 16, 0.8), (n, 1.55)])
    tp = C.dive_torch((-1.25, 0.15, -1.05), (0.25, 1.3, -2.52), energy=420, size_deg=46, beam_len=2.4, beam_strength=0.3)
    q0 = tp["root"].rotation_quaternion.copy()
    for f, aim in ((1, (0.35, 1.2, -2.45)), (f_slide, (0.15, 1.35, -2.55)), (n, (0.0, 1.5, -2.6))):
        tp["root"].rotation_quaternion = (Vector(aim) - Vector((-1.25, 0.15, -1.05))).to_track_quat("-Z", "Y")
        tp["root"].keyframe_insert("rotation_quaternion", frame=f)
    C.key_energy(tp["spot"], [(1, 420), (f_slide + 8, 420), (n, 300)])
    C.key_input(tp["beam_sock"], [(1, 0.42), (f_slide + 8, 0.42), (n, 0.1)])
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.5, -0.95, _gfloor(0.5, -0.95) + 0.8), (0.05, 0.9, -2.3)),
                       (n, (0.45, -0.75, _gfloor(0.45, -0.75) + 0.75), (0.05, 0.95, -2.3))], shake=0.004, rot_shake=0.0015,
              shake_keys=[(1, 0.2), (f_slide, 0.3), (f_slide + 6, 1.0), (n, 0.5)], rate=2.0, seed=3, fn=C.sm)
    C.cam_fill(cam, energy=70, color=(0.7, 0.8, 0.8))
    L.bake_static()


def S11(L, n):
    """Two recovery divers reach the slope, gravel trickles, silt boils into their beams, the lights pull back."""
    gm = _gravel_set(L, n, dense=False)
    aim = Vector((0.0, 1.35, -2.5))
    f_in, f_back = int(n * 0.4), int(n * 0.62)
    for name, fins, a, b, c, lag in (("recA", C.ORANGE, (0.6, -5.6, -0.25), (0.42, -2.2, -0.5), (0.5, -3.2, -0.4), 0),
                                     ("recB", (0.92, 0.92, 0.9), (-0.4, -6.2, -0.15), (-0.55, -3.5, -0.4), (-0.45, -4.3, -0.3), 4)):
        d = C.diver(name, fins=fins, suit=(0.1, 0.11, 0.13), tanks="doubles", rebreather=False, light_energy=1100, beam_len=4.5, beam_strength=0.5,
                    beam_deg=22)
        r = d["root"]
        for f, p in ((1, a), (f_in + lag, b), (f_back + lag, b), (n, c)):
            r.location = p
            r.rotation_euler = (aim - Vector(p)).to_track_quat("Y", "Z").to_euler()
            r.keyframe_insert("location", frame=f)
            r.keyframe_insert("rotation_euler", frame=f)
        L.anim_swim(d, n, kick_rate=0.7, amp=0.2)
        pa, pb = Vector(a), Vector(b)
        C.bubble_trail(lambda f, pa=pa, pb=pb, lag=lag: pa.lerp(pb, C.sm((f - 1) / (f_in + lag))) + Vector((0, 0.45, 0.2)), n,
                       count=20, rise=0.8, size=0.02, seed=3 + lag, name=name + "_bub")
    rnd = random.Random(4)
    for k in range(12):
        _roll(L, gm, k, rnd.uniform(-0.7, 0.8), rnd.uniform(-0.3, 1.2), int(n * 0.28) + rnd.randint(0, 34),
              rnd.uniform(0.4, 1.0), rnd.randint(11, 17), rnd.uniform(0.03, 0.06), n)
    _plume(L, n, (0.05, 1.2, -2.2), (2.4, 2.4, 1.9), [(1, 0.0), (int(n * 0.3), 0.0), (int(n * 0.55), 3.0), (n, 5.0)],
           [(1, 0.3), (int(n * 0.3), 0.3), (int(n * 0.6), 0.85), (n, 1.3)], color=(0.55, 0.46, 0.32))
    L.point((1.6, -3.4, 0.5), energy=260, color=(0.45, 0.85, 0.9), radius=0.8, name="amb1")
    L.point((-1.7, -4.6, 0.5), energy=200, color=(0.45, 0.85, 0.9), radius=0.8, name="amb2")
    C.rim_light((0.0, -2.8, -0.4), (0.4, 4.2, 0.3), energy=700, color=CYAN_RIM, size_deg=55, name="rim")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (-1.5, -7.2, 0.25), (0.0, -1.5, -0.85)), (n, (-1.0, -7.5, 0.25), (0.05, -1.5, -0.85))],
              shake=0.02, rot_shake=0.003, rate=0.6, seed=6, fn=C.sm)
    C.cam_fill(cam, energy=150, color=(0.55, 0.82, 0.88))
    L.bake_static()


# ============================================================================ S12 the grate

def _wall_h(x, z):
    """Passage wall as a height map over (x, z): bulges toward the camera, with a deep dark pocket at the origin."""
    h = 0.25 * noise.noise(Vector((x * 0.5, z * 0.5, 0.3))) + 0.07 * noise.noise(Vector((x * 2.0, z * 2.0, 1.2)))
    q = math.hypot(x / 0.5, z / 0.4)
    if q < 1.0:
        h -= 4.0 * C.sm((1.0 - q) / 0.35)
    return h


def S12(L, n):
    _uw(14.0)
    rock = C.rock_mat("wallrock", (0.045, 0.05, 0.05), (0.36, 0.36, 0.32), scale=1.5, bump=1.0)
    wall = C.heightfield(size=(8, 5.6), center=(0, 0, 0), res=0.06, fn=_wall_h, mat=rock, name="wall", disp=(0, 0))
    wall.rotation_euler = (math.pi / 2, 0, 0)                   # local (x, y, h) -> world (x, -h, y)
    C.floor(size=(9, 7), center=(0, -2.6, -1.3), strength=0.25, name="siltfloor")
    C.rebar_grate(loc=(0, -0.2, 0.0), w=1.0, h=0.8, nx=6, nz=5, collar=0.2, depth=0.34, name="grate")
    C.water(center=(0, -1.6, 0.2), size=(9, 8, 5), color=TEAL, density=0.045, name="uw")
    tl = Vector((-1.2, -2.5, 0.42))
    tp = C.dive_torch(tuple(tl), (-0.6, 0.0, 0.1), energy=520, size_deg=26, beam_len=3.4, beam_strength=0.38)
    for f, a in ((1, (-1.05, 0.0, 0.3)), (int(n * 0.55), (0.25, 0.0, -0.05)), (n, (0.02, 0.6, 0.02))):
        tp["root"].rotation_quaternion = (Vector(a) - tl).to_track_quat("-Z", "Y")
        tp["root"].keyframe_insert("rotation_quaternion", frame=f)
    s = C.cloud((0.0, -0.35, 0.05), (1.5, 0.9, 1.1), count=200, radius=0.003, color=(0.85, 0.82, 0.7), emit=0.08, seed=5)
    C.drift(s, n, (0.012, 0.06, 0.012))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.3, -2.75, 0.02), (0.0, 0.0, -0.3)), (n, (0.12, -1.95, 0.05), (0.0, 0.0, -0.22))], shake=0.02,
              rot_shake=0.004, rate=0.6, seed=7, fn=C.sm)
    C.cam_fill(cam, energy=34, color=(0.4, 0.8, 0.8))
    L.bake_static()


# ============================================================================ the fourth chamber (S15 S16)

def _pale():
    return C.rock_mat("pale", (0.3, 0.29, 0.25), (0.8, 0.77, 0.69), scale=1.0, bump=0.45)


def S15(L, n):
    """2000: two recovery divers squeeze through a tight gap into a small pale chamber."""
    _uw(18.0)
    C.rock_room(R=(3.0, 2.7), H=2.1, below=1.3, seed=5, mat=_pale(), name="chamber", door=(-90.0, 1.3, -1.0, 0.7))
    C.passage(length=6.2, y0=-8.4, half_w=0.95, half_h=0.5, zc=-0.25, seed=3, rough=0.1, floor_flat=0.3, disp=(0.1, 0.04),
              mat=C.rock_mat("gaprock", (0.05, 0.05, 0.048), (0.42, 0.4, 0.35), scale=1.6, bump=0.9), name="gap")
    C.water(center=(0, -2.2, 0.1), size=(7.5, 14, 4.6), color=(0.34, 0.7, 0.68), density=0.03, name="uw")
    # diver C already inside, sweeping the pale walls
    c = C.diver("recC", fins=C.YELLOW, tanks="doubles", rebreather=False, light_energy=2600, beam_len=3.2, beam_strength=0.45,
                beam_deg=30)
    c["root"].location = (0.75, 0.2, 0.2)
    for f, yaw, pt in ((1, 0.9, 0.12), (n // 2, 0.25, 0.2), (n, -0.4, 0.08)):
        c["root"].rotation_euler = (pt, 0, yaw)
        c["root"].keyframe_insert("rotation_euler", frame=f)
    L.anim_swim(c, n, kick_rate=0.4, amp=0.12)
    # diver D pushes through the gap ahead of the lens
    d = C.diver("recD", fins=(0.92, 0.92, 0.9), tanks="doubles", rebreather=False, light_energy=2200, beam_len=3.0,
                beam_strength=0.35, beam_deg=26)
    C.key_loc(d["root"], [(1, (0.05, -5.3, -0.3)), (n, (0.0, -2.9, -0.22))])
    L.linear_fcurves(d["root"])
    L.anim_swim(d, n, kick_rate=0.8, amp=0.13)
    C.bubble_trail(lambda f: Vector((0.05, -5.2 + 2.8 * (f - 1) / (n - 1), -0.1)), n, count=16, rise=0.5, size=0.018, seed=4,
                   name="d_bub")
    L.point((0.0, 0.6, 0.9), energy=160, color=(1.0, 0.95, 0.85), radius=1.5, name="bounce")
    C.rim_light((0.0, -4.2, -0.2), (0.25, 3.8, 0.55), energy=1000, color=CYAN_RIM, size_deg=40, name="rim")
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.05, -8.25, -0.12), (0.1, 0.5, 0.2)), (n, (0.0, -6.5, -0.1), (0.1, 0.5, 0.2))], shake=0.012,
              rot_shake=0.003, rate=0.6, seed=4, fn=lambda x: x)
    C.cam_fill(cam, energy=70, color=(0.5, 0.82, 0.88))
    L.bake_static()


def _chfloor(x, y):
    z = -0.95 + 0.05 * noise.noise(Vector((x * 0.8, y * 0.8, 0.7))) + 0.015 * noise.noise(Vector((x * 4.0, y * 4.0, 1.3)))
    u = x * 0.94 + (y - 0.45) * 0.34
    v = -x * 0.34 + (y - 0.45) * 0.94
    w = 0.085 * max(0.0, 1 - (u / 0.5) ** 2) ** 0.6
    if abs(v) < w:
        z -= min(1.6, 16.0 * (w - abs(v)))
    return z


def S16(L, n):
    """Two beams converge on a narrow dark gap in the chamber floor; one gloved hand rests on the rock beside it.
    Nothing else is shown."""
    _uw(12.0)
    pale = _pale()
    C.rock_room(R=(3.0, 2.7), H=2.1, below=1.3, seed=5, mat=pale, name="chamber")
    C.heightfield(size=(4.4, 4.4), center=(0, 0.3, 0), res=0.03, fn=_chfloor, mat=pale, name="chfloor", disp=(0, 0))
    C.water(center=(0, 0, 0), size=(6.5, 6, 4), color=(0.34, 0.7, 0.68), density=0.03, name="uw")
    for k, (loc, aim, e) in enumerate((((-1.3, -0.8, 0.2), (-0.12, 0.42, -0.97), 230), ((1.2, -1.0, 0.1), (0.12, 0.5, -0.97), 200))):
        tp = C.dive_torch(loc, aim, energy=e, size_deg=24, beam_len=1.9, beam_strength=0.22, name=f"torch{k}")
        a0, a1 = Vector(aim) + Vector(((-0.35 if k == 0 else 0.4), -0.25, 0)), Vector(aim)
        for f, a in ((1, a0), (int(n * 0.6), a1), (n, a1)):
            tp["root"].rotation_quaternion = (a - Vector(loc)).to_track_quat("-Z", "Y")
            tp["root"].keyframe_insert("rotation_quaternion", frame=f)
    # gloved hand resting on the rock beside the gap
    h = S.hand("glove", color=(0.02, 0.02, 0.024), scale=1.5, glove=True)
    hx, hy = 0.3, 0.2
    hz = _chfloor(hx, hy) + 0.03
    h["root"].rotation_euler = (0.08, 0, 0.6)
    C.key_loc(h["root"], [(1, (hx + 0.08, hy - 0.1, hz + 0.09)), (16, (hx, hy, hz)), (n, (hx, hy, hz))])
    S.curl(h, 1, 0.05)
    S.curl(h, 18, 0.22)
    arm = L.prim("cyl", loc=(0, -0.62, 0.05), rot=(math.pi / 2 - 0.12, 0, 0), vertices=12, radius=0.058, depth=0.7, name="glove_arm")
    L.assign(arm, L.mat_principled("glove_arm_m", (0.02, 0.02, 0.024), rough=0.5))
    arm.parent = h["root"]
    for k, (cx, cy) in enumerate(((-0.75, 0.75), (0.78, 0.85))):
        s = C.cloud((cx, cy, -0.45), (0.6, 0.7, 0.6), count=170, radius=0.0035, color=(0.9, 0.86, 0.75), emit=0.25, seed=12 + k,
                    name=f"silt{k}")
        C.drift(s, n, (0.01 * (1 if k else -1), 0.005, 0.015))
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.1, -1.55, 0.4), (0.03, 0.3, -1.08)), (n, (0.08, -1.3, 0.25), (0.03, 0.32, -1.08))],
              shake=0.008, rot_shake=0.002, rate=0.5, seed=8, fn=C.sm)
    C.cam_fill(cam, energy=28, color=(0.5, 0.82, 0.88))
    L.bake_static()
