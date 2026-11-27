"""CAVE-07 — Sheck Exley & Jim Bowden, Zacatón (Mexico, April 1994). Shot builders (def Sxx(L, n)).
Shared builders: PIPELINE/blender/lib_cave.py (grass_island, wildflower, tripod appended for this video).
No body is ever modelled: the loss is told with a light that dims, an empty line, a diagram coil and a coiled line."""
import sys, os, math, random
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "PIPELINE", "blender"))
import importlib
import lib_cave as C
importlib.reload(C)
import bpy
from mathutils import Vector

EXLEY = C.YELLOW
BOWDEN = C.ORANGE
EXLEY_HELMET = (0.85, 0.68, 0.08)
BOWDEN_HELMET = (0.9, 0.42, 0.08)
CYAN_RIM = (0.35, 0.85, 1.0)
SULPHUR = (0.75, 0.85, 0.45)
LX = 1.2  # half-spacing of the two descent lines in the shaft


# ============================================================================ helpers

def _diver(name, fins, energy=1800, beam_len=6.0, beam=0.4, deg=22, tanks="doubles", suit=(0.03, 0.03, 0.035)):
    return C.diver(name, fins=fins, tanks=tanks, rebreather=False, light_energy=energy, beam_len=beam_len,
                   beam_strength=beam, beam_deg=deg, suit=suit)


def _head_down(d, loc, tilt=0.0, yaw=0.0):
    r = d["root"]
    r.location = loc
    r.rotation_euler = (-math.pi / 2 + tilt, 0, yaw)
    return r


def _upright(d, loc, face_deg=0.0, tilt=0.2, helmet=EXLEY_HELMET, kit=True):
    """Head up, belly toward +Y rotated by face_deg (0 = faces +Y, -90 = faces +X)."""
    if kit:
        C.upright_head_kit(d, helmet=helmet)
    r = d["root"]
    r.location = loc
    r.rotation_euler = (math.pi / 2 - tilt, 0, math.radians(face_deg))
    for tag, sg in (("L", -1), ("R", 1)):
        d[f"shoulder{tag}"].rotation_euler = (-1.25, 0, sg * 0.3)
        d[f"knee{tag}"].rotation_euler = (0.35, 0, 0)
    return r


def _seat(d, edge_pt, face_deg=0.0, tilt=0.25, helmet=EXLEY_HELMET):
    """Sit a diver() rig on a ledge edge: thighs level on the rock, shins and fins hanging over the water.
    edge_pt = point on the ledge top edge between the knees. Faces +Y rotated by face_deg."""
    C.upright_head_kit(d, helmet=helmet)
    r = d["root"]
    yaw = math.radians(face_deg)
    fwd = Vector((-math.sin(yaw), math.cos(yaw), 0))
    hip_back = 0.42
    r.location = Vector(edge_pt) - fwd * (hip_back - 0.55 * math.sin(tilt)) + Vector((0, 0, 0.55 * math.cos(tilt) + 0.07))
    r.rotation_euler = (math.pi / 2 - tilt, 0, yaw)
    for tag, sg in (("L", -1), ("R", 1)):
        d[f"hip{tag}"].rotation_euler = (math.pi / 2 + tilt, 0, sg * 0.08)
        d[f"knee{tag}"].rotation_euler = (-math.pi / 2 + 0.15, 0, 0)
        d[f"shoulder{tag}"].rotation_euler = (-1.3, 0, sg * 0.25)
    return r


def _track(obj, pos, name="tgt"):
    t = bpy.data.objects.new(name, None)
    C.L.link(t)
    t.location = pos
    con = obj.constraints.new("TRACK_TO")
    con.target = t
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    return t


def _specks(n, center, size, count=2200, seed=4, vel=(0.0, 0.0, 0.2), color=SULPHUR, emit=0.04, radius=0.0025):
    s = C.cloud(center, size, count=count, radius=radius, color=color, emit=emit, seed=seed)
    C.drift(s, n, vel)
    return s


# ============================================================================ the shaft (S01 / S02 / S09 / S11 / S17)

def _shaft(L, n, density=0.035, z_top=4.0, z_bot=-70.0, sun=2.5, vol_end=40, center_z=-25, vol_h=64, R=7.0):
    C.world_black((0.0, 0.006, 0.008))
    C.render_quality(vol_end=vol_end, vol_tile="8", vol_samples=32)
    C.water(center=(0, 0, center_z), size=(22, 22, vol_h), color=(0.32, 0.62, 0.55), density=density,
            absorption=(0.08, 0.25, 0.3))
    C.shaft(z_top, z_bot, lambda z, a: R + 0.16 * R * math.sin(2 * a + z * 0.05) + 0.07 * R * math.sin(5 * a + 1.0),
            step=1.0, ring=40, seed=7, rough=0.22, name="zshaft", disp=(0.8, 0.25),
            mat=C.rock_mat("zrock", (0.035, 0.045, 0.04), (0.3, 0.32, 0.26), scale=1.3))
    C.sun_from((0.2, 0.12, 1.0), energy=sun, color=(0.55, 0.9, 0.85), angle=3)


def _lines(z_top=4.0, z_bot=-70.0, xs=(-LX, LX), emit=1.0):
    out = []
    for k, x in enumerate(xs):
        out.append(C.line([(x, 0.0, z_top), (x, 0.0, z_bot)], thickness=0.01, emit=emit, name=f"dline{k}"))
    return out


S01_CAM0 = ((0.0, -2.4, 0.8), (0.0, 0.9, -4.6))
S01_CAM1 = ((0.0, -2.3, -3.3), (0.0, 0.9, -8.8))


def S01(L, n):
    _shaft(L, n, R=6.0)
    _lines()
    divers = []
    for nm, fins, x, z0, z1, deg, col, tanks in (("exley", EXLEY, -LX + 0.3, -1.4, -6.2, 22, (1.0, 0.93, 0.8), "sidemount"),
                                                 ("bowden", BOWDEN, LX + 0.3, -1.6, -6.0, 24, (0.85, 0.92, 1.0), "doubles")):
        d = _diver(nm, fins, energy=2600, beam_len=9.0, beam=0.5, deg=deg, tanks=tanks)
        d["torch"].data.color = col
        r = _head_down(d, (x, 0.25, z0), tilt=0.3, yaw=math.pi)
        C.key_loc(r, [(1, (x, 0.25, z0)), (n, (x, 0.3, z1))])
        L.linear_fcurves(r)
        L.anim_swim(d, n, kick_rate=0.55, amp=0.22)
        divers.append((d, x, z0, z1))
    for k, (d, x, z0, z1) in enumerate(divers):
        C.bubble_trail(lambda f, x=x, z0=z0, z1=z1: Vector((x - 0.1, 0.1, z0 + (z1 - z0) * (f - 1) / (n - 1) + 0.55)),
                       n, count=22, rise=1.6, size=0.018, seed=3 + k, name=f"bub{k}")
    _specks(n, (0, 0.2, -2.5), (5.0, 4.0, 10.0), count=2400, seed=5, vel=(0.02, 0.0, 0.35))
    C.rim_light((0, 0.3, -3), (0.5, 3.0, 4.0), energy=1500, color=CYAN_RIM, size_deg=60, name="toprim")
    cam = C.camera(lens=20)
    C.aim_cam(cam, n, [(1, *S01_CAM0), (n, *S01_CAM1)], shake=0.02, rot_shake=0.004, rate=0.5, fn=lambda x: x)
    C.cam_fill(cam, energy=60, color=(0.5, 0.85, 0.8))
    L.bake_static()


def S02(L, n):
    _shaft(L, n, density=0.04, sun=1.2)
    _lines(emit=0.35)
    out = []
    for nm, fins, x, keys, col in (("exley", EXLEY, -LX, [(1, -1.0), (n, -3.6)], (1.0, 0.93, 0.8)),
                                   ("bowden", BOWDEN, LX, [(1, -1.2), (int(n * 0.55), -2.3), (n, -2.0)], (0.85, 0.92, 1.0))):
        d = _diver(nm, fins, energy=3000, beam_len=8.0, beam=0.55, deg=24, tanks="sidemount" if nm == "exley" else "doubles")
        d["torch"].data.color = col
        r = _head_down(d, (x + 0.3, 0.3, keys[0][1]), tilt=0.25, yaw=(0.3 if x < 0 else -0.3))
        C.key_loc(r, [(f, (x + 0.3, 0.3, z)) for f, z in keys])
        L.anim_swim(d, n, kick_rate=0.5, amp=0.2)
        out.append(d)
    ex = out[0]
    C.key_energy(ex["torch"], [(1, 3000), (8, 2600), (int(n * 0.8), 120), (n, 0.0)])
    C.key_input(ex["beam_sock"], [(1, 0.55), (8, 0.5), (int(n * 0.8), 0.03), (n, 0.0)])
    lens = ex["lens"].active_material.node_tree.nodes["Emission"].inputs[1]
    C.key_input(lens, [(1, 30), (int(n * 0.8), 1.0), (n, 0.0)])
    # silhouettes in black: only a faint cyan rim from above so the lights read as the subject
    C.rim_light((0, 0.3, -2), (0.0, 2.5, 5.0), energy=300, color=CYAN_RIM, size_deg=60, name="toprim")
    _specks(n, (0, 0, -2), (5, 4, 7), count=1500, seed=8, vel=(0.0, 0.0, 0.2))
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.0, -5.2, -1.6), (0.0, 0.3, -2.6)), (n, (0.0, -4.7, -1.8), (0.0, 0.3, -2.8))],
              shake=0.008, rot_shake=0.002)
    C.cam_fill(cam, energy=25, color=(0.45, 0.75, 0.8))
    L.bake_static()


# ============================================================================ ranchland cenote from above (S03 / S15)

def _ranch(L, n, tod="day", R=18.0):
    if tod == "day":
        sd = C.sun_dir(48, 110)
        C.sky_world(top=(0.18, 0.36, 0.7), horizon=(0.75, 0.72, 0.62), ground=(0.22, 0.18, 0.1), sun_dir=sd,
                    sun_color=(1.0, 0.85, 0.6), sun_glow=2.0, strength=1.0)
        C.sun_from(sd, energy=5.0, color=(1.0, 0.9, 0.75), angle=1.0)
    else:
        sd = C.sun_dir(5, 285)
        C.sky_world(top=(0.12, 0.14, 0.3), horizon=(1.0, 0.45, 0.15), ground=(0.06, 0.04, 0.03), sun_dir=sd,
                    sun_color=(1.0, 0.5, 0.18), sun_glow=2.5, strength=1.0, glow_pow=50)
        C.sun_from(sd, energy=3.5, color=(1.0, 0.6, 0.3), angle=1.5)
    cr = C.crater(R=R, depth=14.0, outer=420.0, seed=6, ang_seg=96,
                  ground_mat=L.mat_noise_surface("ranch", (0.11, 0.1, 0.05), (0.36, 0.3, 0.17), scale=0.06, bump=0.3,
                                                 voronoi=False),
                  wall_mat=L.mat_noise_surface("cwall", (0.16, 0.14, 0.11), (0.52, 0.47, 0.38), scale=0.12, bump=1.0),
                  pool_mat=L.mat_principled("pool_m", (0.004, 0.035, 0.03), rough=0.08))
    C.bushes(count=420, rmin=R * 1.12, rmax=95, seed=4, size=(1.0, 2.6), color=(0.1, 0.13, 0.04))
    rr = random.Random(40)
    pts = []
    for i in range(30):
        a = rr.uniform(0, 6.28)
        rad = rr.uniform(R * 1.3, 85)
        pts.append((math.cos(a) * rad, math.sin(a) * rad, 0.0))
    C.florida_woods(pts, seed=5, c1=(0.04, 0.06, 0.02), c2=(0.16, 0.2, 0.07), height=(3.5, 6.0), crown=(1.4, 2.6),
                    name="ranchtree")
    pz = cr["pool_z"]
    for k, (x, y, r) in enumerate(((-4.5, 3.0, 1.6), (3.5, -5.0, 1.1), (6.0, 4.5, 0.8), (-2.0, -6.5, 0.7),
                                   (1.0, 7.5, 1.0))):
        C.grass_island((x, y, pz + 0.05), radius=r, seed=k + 2, name=f"isl{k}")
    return cr, sd


def S03(L, n):
    cr, sd = _ranch(L, n, "day")
    haze = C.cloud((0, -10, 6), (40, 40, 10), count=1500, radius=0.008, color=(1.0, 0.92, 0.7), emit=0.3, seed=3)
    C.drift(haze, n, (0.3, 0.1, 0.05))
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (6.0, -62.0, 48.0), (0.0, -2.0, -6.0)), (n, (2.0, -30.0, 20.0), (0.0, 1.5, -12.5))],
              shake=0.08, rot_shake=0.002, rate=0.3)
    L.bake_static()


def S15(L, n):
    cr, sd = _ranch(L, n, "dusk")
    a = math.radians(270)
    rim = cr["rim"](a)
    fl = C.wildflower((0.35, -rim * 1.05, 0.22), height=0.42, n=n, sway=0.16)
    fl.scale = (1.6, 1.6, 1.6)
    for k, (dx, dy) in enumerate(((-0.25, -0.18), (0.6, -0.3), (-0.55, -0.45))):
        g = L.prim("cone", loc=(dx, -rim * 1.05 + dy, 0.25), vertices=5, radius1=0.05, radius2=0.0, depth=0.22,
                   name=f"grass{k}")
        L.assign(g, L.mat_principled("grass_m", (0.3, 0.25, 0.1), rough=0.8))
    for k in range(3):
        b = L.prim("cone", loc=(0.6 + 0.18 * k, -rim * 1.05 - 0.15, 0.32), vertices=4, radius1=0.02, radius2=0.0,
                   depth=0.4, rot=(0.15 * (k - 1), 0.25, 0), name=f"blade{k}")
        L.assign(b, L.mat_principled("grass_m2", (0.35, 0.3, 0.12), rough=0.8))
    cam = C.camera(lens=24)
    y0 = -rim * 1.05
    C.aim_cam(cam, n, [(1, (0.6, y0 - 1.6, 2.6), (0.0, y0 + 14.0, -8.5)), (n, (0.45, y0 - 1.45, 1.3), (0.0, y0 + 14.0, -7.5))],
              shake=0.01, rot_shake=0.002, rate=0.3)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 8.0
    cam.data.dof.focus_distance = 3.0
    L.point((0.35, y0 - 0.5, 0.8), energy=6, color=(1.0, 0.6, 0.3), radius=0.4, name="flowerfill")
    L.bake_static()


# ============================================================================ the ledge inside the cenote (S04 / S05 / S12 / S16)

LEDGE_Y = -16.8
LEDGE_TOP = 0.3
EDGE_Y = -15.2  # front (water-side) edge of the ledge


def _ledge(L, n, sun_e=4.5, overcast=False, sky=1.0):
    if overcast:
        sd = C.sun_dir(40, 15)
        C.sky_world(top=(0.42, 0.48, 0.55), horizon=(0.7, 0.7, 0.68), ground=(0.15, 0.14, 0.12), sun_dir=sd,
                    sun_color=(0.9, 0.9, 0.85), sun_glow=0.6, strength=1.2 * sky)
        C.sun_from(sd, energy=sun_e, color=(0.95, 0.93, 0.88), angle=8.0)
    else:
        sd = C.sun_dir(55, 0)
        C.sky_world(top=(0.16, 0.34, 0.7), horizon=(0.75, 0.75, 0.68), ground=(0.12, 0.1, 0.08), sun_dir=sd,
                    sun_color=(1.0, 0.85, 0.6), sun_glow=2.0, strength=sky)
        C.sun_from(sd, energy=sun_e, color=(1.0, 0.88, 0.7), angle=1.2)
    C.shaft(-4.0, 24.0, lambda z, a: 20.0 + 0.8 * math.sin(3 * a + 0.5) + 0.4 * math.sin(7 * a + z * 0.2),
            step=1.0, ring=72, seed=3, rough=0.08, name="cwall", disp=(0.6, 0.2),
            mat=L.mat_noise_surface("cwall_m", (0.1, 0.085, 0.065), (0.5, 0.44, 0.34), scale=0.18, bump=1.0,
                                    voronoi=False))
    C.ledge((0, LEDGE_Y, LEDGE_TOP), size=(6.0, 3.4, 1.6), seed=3,
            mat=C.rock_mat("ledge_m", (0.07, 0.06, 0.05), (0.42, 0.37, 0.3), scale=2.4))
    C.rocks([(-3.2, -17.5, 0.0), (3.4, -17.2, 0.0), (-2.6, -15.6, -0.1), (2.9, -15.4, -0.1), (0.0, -18.6, 0.2)],
            count=5, size=(0.5, 1.0), seed=9)
    ws, _ = C.water_surface(size=(46, 46), center=(0, 0, 0), color=(0.01, 0.07, 0.06), rough=0.1, wave_scale=1.0,
                            bump=0.1, n=n, flow=(0.02, 0.03))
    try:
        ws.active_material.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.25
    except Exception:
        pass
    for k, (x, y, r) in enumerate(((5.0, -8.0, 1.4), (-6.0, -4.0, 1.8), (8.0, 4.0, 1.2), (-3.0, 6.0, 1.0),
                                   (2.5, -11.5, 0.8))):
        isl = C.grass_island((x, y, 0.03), radius=r, seed=k + 11, name=f"isl{k}")
        for o in isl:
            C.drift(o, n, (0.03, 0.02, 0.0))
    # tree/scrub tufts hanging over the rim
    C.bushes(count=40, rmin=19.5, rmax=23, seed=8, z=23.5, color=(0.1, 0.14, 0.05), size=(0.8, 1.6))
    return ws, sd


def S04(L, n):
    _ledge(L, n)
    d = _diver("bowden", BOWDEN, energy=300, beam=0.0, tanks="doubles", suit=(0.035, 0.035, 0.04))
    edge = Vector((0.0, EDGE_Y + 0.15, LEDGE_TOP))
    r = _seat(d, edge, face_deg=0, tilt=0.42, helmet=BOWDEN_HELMET)
    # stage cylinder across his thighs; right hand works the valve, left hand steadies it
    tk = C.tank((0.05, EDGE_Y - 0.1, LEDGE_TOP + 0.2), rot=(0, math.pi / 2, 0.15), length=0.75, r=0.09, band=BOWDEN,
                name="stage")
    for f in range(1, n + 1, 3):
        d["shoulderR"].rotation_euler = (-1.75 + 0.1 * math.sin(f * 0.4), 0, -0.15)
        d["shoulderL"].rotation_euler = (-1.7, 0, 0.25)
        for tag in ("L", "R"):
            d[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
    C.tank((-0.9, EDGE_Y - 1.1, LEDGE_TOP + 0.38), rot=(0.05, 0.08, 0), length=0.7, r=0.085, band=(0.9, 0.9, 0.9),
           name="spare")
    C.rim_light((0.0, EDGE_Y, 1.1), (-1.0, -2.5, 1.8), energy=1600, color=(1.0, 0.78, 0.5), size_deg=40, name="wallrim")
    C.rim_light((0.0, EDGE_Y, 1.1), (2.0, -1.0, 1.2), energy=700, color=(0.6, 0.9, 1.0), size_deg=40, name="siderim")
    cam = C.camera(lens=35)
    tgt = (0.0, EDGE_Y - 0.35, 0.85)
    C.aim_cam(cam, n, [(1, (2.0, EDGE_Y + 2.3, 0.85), tgt), (n, (0.7, EDGE_Y + 2.9, 0.9), (-0.05, EDGE_Y - 0.35, 0.85))],
              shake=0.01, rot_shake=0.002)
    C.cam_fill(cam, energy=25, color=(1.0, 0.85, 0.7))
    L.bake_static()


def S05(L, n):
    _ledge(L, n, sun_e=5.0, sky=0.55)
    d = _diver("exley", EXLEY, energy=300, beam=0.0, tanks="sidemount", suit=(0.03, 0.03, 0.035))
    r = _upright(d, (0.5, -13.9, 0.4), face_deg=8, tilt=0.05, helmet=EXLEY_HELMET)
    # both hands up behind the head pulling the mask strap
    for f in range(1, n + 1, 2):
        t = (f - 1) / (n - 1)
        pull = 0.5 + 0.5 * math.sin(t * math.pi * 2.0 - 1.2)
        d["shoulderL"].rotation_euler = (0.15 + 0.3 * pull, 0, -0.75 + 0.2 * pull)
        d["shoulderR"].rotation_euler = (0.15 + 0.3 * pull, 0, 0.75 - 0.2 * pull)
        for tag in ("L", "R"):
            d[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
    C.drip_rings([(0.2, -13.6, 0.01), (0.85, -13.7, 0.01), (0.5, -13.3, 0.01)], n, period=30, seed=2,
                 color=(0.9, 0.95, 0.9), strength=0.6, rmax=0.5)
    C.rim_light((0.5, -13.9, 1.1), (0.4, 4.0, 1.6), energy=3500, color=(1.0, 0.85, 0.6), size_deg=35, name="backrim")
    C.rim_light((0.5, -13.9, 1.1), (-2.0, 1.5, 0.8), energy=1400, color=(0.6, 0.9, 1.0), size_deg=35, name="siderimL")
    C.rim_light((0.5, -13.9, 1.1), (2.0, 1.5, 0.8), energy=1400, color=(0.6, 0.9, 1.0), size_deg=35, name="siderimR")
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.0, -17.2, 0.65), (0.6, -10.0, 1.35)), (n, (0.25, -15.9, 0.6), (0.6, -10.0, 1.3))],
              shake=0.012, rot_shake=0.003)
    C.cam_fill(cam, energy=60, color=(1.0, 0.85, 0.7))
    L.bake_static()


def S12(L, n):
    _ledge(L, n, sun_e=3.0, overcast=True, sky=0.5)
    apex = Vector((0.4, EDGE_Y - 0.25, LEDGE_TOP + 2.1))
    C.tripod(tuple(apex), height=2.1, spread=0.85)
    entry = Vector((0.4, EDGE_Y + 0.9, 0.0))
    lm = L.mat_principled("haul_m", (0.95, 0.95, 0.9), rough=0.4, emit=(0.9, 0.9, 0.85), emit_strength=0.6)
    C.curve([tuple(entry + Vector((0, 0.6, -3.0))), tuple(entry), tuple(apex)], thickness=0.012, mat=lm, name="haul_in")
    tail = Vector((-4.6, EDGE_Y - 1.0, LEDGE_TOP + 1.0))
    C.curve([tuple(apex), tuple(tail), (-5.5, EDGE_Y - 1.2, LEDGE_TOP + 0.05)], thickness=0.012, mat=lm, name="haul_out")
    # coil building up on the rock behind the haulers
    coil = C.helix((-5.3, EDGE_Y - 1.3, LEDGE_TOP + 0.08), (0, 0, 1), 0.28, 6, 0.12, pts_per_turn=20)
    C.curve(coil, thickness=0.012, mat=lm, name="coil")
    # three faceless haulers along the out line, leaning back, hand over hand
    for k, x in enumerate((-1.3, -2.4, -3.5)):
        t = (x - apex.x) / (tail.x - apex.x)
        lz = apex.z + (tail.z - apex.z) * t
        ly = apex.y + (tail.y - apex.y) * t
        p = C.figure(f"hauler{k}", height=1.74 + 0.04 * k, base=(0.04, 0.04, 0.045), rim=(0.85, 0.9, 1.0),
                     rim_strength=0.7)
        rt = p["root"]
        rt.location = (x - 0.35, ly - 0.05, LEDGE_TOP)
        rt.rotation_euler = (0, 0, math.radians(-90))
        p["pelvis"].rotation_euler = (-0.28, 0, 0)
        for tag, sg in (("L", 1), ("R", -1)):
            p[f"hip{tag}"].rotation_euler = (0.35 if tag == "L" else -0.1, 0, 0)
        for f in range(1, n + 1, 3):
            ph = f * 0.28 + k * 1.3
            for tag, sg in (("L", 1), ("R", -1)):
                p[f"shoulder{tag}"].rotation_euler = (1.25 + 0.3 * sg * math.sin(ph), 0, 0)
                p[f"elbow{tag}"].rotation_euler = (0.35 + 0.25 * max(0, -sg * math.sin(ph)), 0, 0)
                p[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
                p[f"elbow{tag}"].keyframe_insert("rotation_euler", frame=f)
    # tanks clipped to the line come up out of the water toward the pulley
    seg = apex - entry
    for k, (t0, t1, band) in enumerate(((-0.25, 0.42, (0.9, 0.9, 0.9)), (-0.6, 0.12, EXLEY))):
        tk = C.tank(tuple(entry), rot=(0, 0, 0), length=0.65, r=0.08, band=band, name=f"cliptank{k}")
        rot = seg.to_track_quat("Z", "Y")
        tk.rotation_mode = "QUATERNION"
        tk.rotation_quaternion = rot
        keys = []
        for f in range(1, n + 1, 3):
            tt = t0 + (t1 - t0) * (f - 1) / (n - 1)
            pos = entry + seg * tt if tt >= 0 else entry + Vector((0, 0.6, -3.0)) * (-tt / 0.6 * 0.6)
            keys.append((f, tuple(pos + Vector((0.11, 0, 0)))))
        C.key_loc(tk, keys)
    C.drip_rings([tuple(entry + Vector((0.1, 0.05, 0.01))), tuple(entry + Vector((-0.2, 0.3, 0.01)))], n, period=22,
                 seed=4, color=(0.85, 0.9, 0.9), strength=0.5, rmax=0.6)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (2.6, -12.4, 0.45), (-1.6, -15.6, 1.45)), (n, (1.8, -12.2, 0.5), (-2.0, -15.7, 1.4))],
              shake=0.01, rot_shake=0.002)
    C.cam_fill(cam, energy=60, color=(0.85, 0.9, 1.0))
    C.rim_light((-2.3, -15.6, 1.3), (-2.5, -1.5, 2.0), energy=700, color=(0.85, 0.9, 1.0), size_deg=60, name="haulrim")
    L.bake_static()


def S16(L, n):
    _ledge(L, n, sun_e=5.0)
    d = _diver("modern", (0.92, 0.92, 0.92), energy=300, beam=0.0, tanks="sidemount", suit=(0.04, 0.045, 0.06))
    edge = Vector((0.2, EDGE_Y + 0.15, LEDGE_TOP))
    r = _seat(d, edge, face_deg=0, tilt=0.3, helmet=(0.92, 0.92, 0.9))
    p0 = Vector(r.location)
    slide = int(n * 0.5)
    C.key_loc(r, [(1, tuple(p0)), (slide, tuple(p0 + Vector((0, 0.08, 0)))), (n, tuple(p0 + Vector((0, 1.3, -1.35))))])
    for f, rx in ((1, math.pi / 2 - 0.3), (slide, math.pi / 2 - 0.45), (n, math.pi / 2 - 0.9)):
        r.rotation_euler = (rx, 0, 0)
        r.keyframe_insert("rotation_euler", frame=f)
    # reel in the right hand, clipping onto the new line (bolt on the ledge edge)
    for f in range(1, n + 1, 3):
        clip = 0.1 * math.sin(f * 0.5) if f < slide else 0.0
        d["shoulderR"].rotation_euler = (-1.45 + clip, 0, -0.25)
        d["shoulderL"].rotation_euler = (-1.2 if f < slide else -0.6, 0, -0.35)
        for tag in ("L", "R"):
            d[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
    reel = L.prim("cyl", loc=(0, 0.46, 0.0), vertices=16, radius=0.06, depth=0.04, rot=(0, math.pi / 2, 0), name="reel")
    L.assign(reel, L.mat_principled("reel_m", (0.85, 0.85, 0.82), rough=0.5))
    reel.parent = d["shoulderR"]
    bolt = Vector((0.6, EDGE_Y + 0.05, LEDGE_TOP + 0.02))
    C.line([tuple(bolt), tuple(bolt + Vector((0.05, 0.7, -0.32))), tuple(bolt + Vector((0.1, 2.5, -1.0)))],
           thickness=0.007, emit=1.0, name="newline")
    C.drip_rings([(0.2, EDGE_Y + 1.3, 0.01), (0.5, EDGE_Y + 1.1, 0.01)], n, period=26, seed=6, color=(0.9, 0.95, 0.95),
                 strength=0.6, rmax=0.55)
    C.rim_light((0.2, EDGE_Y, 1.0), (0.5, 3.5, 1.6), energy=1500, color=(1.0, 0.85, 0.6), size_deg=40, name="backrim")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (-1.25, EDGE_Y - 2.7, 2.0), (0.5, EDGE_Y + 2.6, -0.1)),
                       (n, (-0.95, EDGE_Y - 2.1, 1.75), (0.4, EDGE_Y + 3.0, -0.3))],
              shake=0.01, rot_shake=0.002)
    C.cam_fill(cam, energy=50, color=(1.0, 0.88, 0.75))
    L.bake_static()


# ============================================================================ S06 dive-log counter graphic

def S06(L, n):
    C.world_black((0.0, 0.01, 0.012))
    bg = L.prim("plane", loc=(0, 3.0, 0), rot=(math.pi / 2, 0, 0), size=1, name="bg")
    bg.scale = (14, 20, 1)
    m, nd, lk = L._mat("bg_m")
    for x in list(nd):
        if x.type == "BSDF_PRINCIPLED":
            nd.remove(x)
    tc = nd.new("ShaderNodeTexCoord")
    sep = nd.new("ShaderNodeSeparateXYZ")
    lk.new(tc.outputs["Generated"], sep.inputs[0])
    rmp = nd.new("ShaderNodeValToRGB")
    rmp.color_ramp.elements[0].color = (0.0, 0.02, 0.025, 1)
    rmp.color_ramp.elements[1].color = (0.02, 0.16, 0.16, 1)
    lk.new(sep.outputs["Y"], rmp.inputs["Fac"])
    em = nd.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.0
    lk.new(rmp.outputs[0], em.inputs[0])
    lk.new(em.outputs[0], nd["Material Output"].inputs["Surface"])
    L.assign(bg, m)
    # ledger: log lines scroll upward fast behind the counter
    holder = L.link(bpy.data.objects.new("ledger", None))
    rows = 34
    lm = C.emis("rule_m", (0.25, 0.6, 0.6), 0.7)
    for i in range(rows):
        num = 967 + i
        z = -i * 0.34
        hi = num == 1000
        t = C.text(f"DIVE {num:04d}", (-0.88, 0.0, z), size=0.17, color=(1.0, 0.85, 0.3) if hi else (0.6, 0.85, 0.85),
                   strength=3.5 if hi else 0.9, font=C.FONT_MONO, align="LEFT", name=f"row{i}")
        t.parent = holder
        t2 = C.text("CAVE" if i % 3 else "SUMP", (0.42, 0.0, z), size=0.12, color=(0.5, 0.75, 0.75),
                    strength=0.6, font=C.FONT_MONO, align="LEFT", name=f"rowb{i}")
        t2.parent = holder
        rl = C.curve([(-0.95, 0.02, z - 0.16), (0.95, 0.02, z - 0.16)], thickness=0.004, mat=lm, name=f"rule{i}")
        rl.parent = holder
    # rows travel up; DIVE 1000 settles mid-low in frame at the end
    z0, z_end = 1.7, 33 * 0.34 - 0.4
    for f in range(1, n + 1, 2):
        t = (f - 1) / (n - 1)
        holder.location = (0, 0, z0 + (z_end - z0) * C.ease_out(t / 0.85))
        holder.keyframe_insert("location", frame=f)
    _specks(n, (0, -0.5, 0), (4, 2, 7), count=1400, seed=12, vel=(0.02, 0, 0.12), color=(0.6, 0.9, 0.85), emit=0.15)
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.0, -5.6, -0.3), (0.0, 0, -0.3)), (n, (0.0, -5.0, -0.3), (0.0, 0, -0.3))])
    L.bake_static()


# ============================================================================ wet rock slab for documents (S07 / S14)

def _slab(L, n, cool=False):
    C.world_black((0.0, 0.0, 0.0))
    rk = L.mat_noise_surface("wetrock", (0.03, 0.03, 0.03), (0.3, 0.27, 0.22) if not cool else (0.22, 0.25, 0.28),
                             scale=7.0, bump=1.0, rough=0.2)
    C.floor(size=(6, 8), center=(0, 0, 0), mat=rk, strength=0.12, levels=7, name="slab", ripples=True)
    C.rocks([(-1.2, -1.9, 0), (1.3, 1.8, 0), (1.25, -2.2, 0), (-1.3, 2.0, 0)], count=4, size=(0.25, 0.5), seed=4,
            mat=rk)
    return rk


def S07(L, n):
    _slab(L, n)
    lm = L.mat_principled("coil_m", (0.95, 0.95, 0.9), rough=0.4, emit=(0.9, 0.9, 0.85), emit_strength=0.3)
    coil = C.helix((0.25, -1.55, 0.04), (0, 0, 1), 0.22, 5, 0.04, pts_per_turn=20, wobble=0.15, seed=2)
    C.curve(coil, thickness=0.008, mat=lm, name="coil")
    C.dive_torch((-0.55, -1.55, 0.05), (-0.1, -1.3, 0.05), energy=0, beam_len=0, name="torchprop")
    # a warm torch beam sweeps across the slab (handheld, off frame)
    sp = L.spot((-1.6, -2.6, 1.5), (0, 0, 0), energy=900, size_deg=32, blend=0.6, color=C.TORCH, name="sweep",
                radius=0.03)
    tgt = _track(sp, (0, 0, 0), "sweep_t")
    C.key_loc(tgt, [(1, (-1.2, 1.6, 0)), (int(n * 0.5), (0.6, 0.2, 0)), (n, (0.3, -1.2, 0))])
    L.ease_all(tgt)
    L.area((0, 0, 3), (0, 0, 0), energy=70, size=4, color=(0.6, 0.7, 0.75), name="ambient")
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.0, 0.0, 4.6), (0.0, 0.01, 0.0), 0.0), (n, (0.0, 0.0, 4.3), (0.0, 0.01, 0.0), -5.0)])
    L.bake_static()


def S14(L, n):
    _slab(L, n, cool=True)
    sl = L.prim("cube", loc=(0.55, -1.45, 0.03), rot=(0, 0, 0.35), name="slate")
    sl.scale = (0.2, 0.14, 0.008)
    L.assign(sl, L.mat_principled("slate_m", (0.85, 0.85, 0.8), rough=0.5))
    C.tank((-0.6, -1.6, 0.1), rot=(math.pi / 2, 0, 1.2), length=0.75, r=0.09, band=EXLEY, name="stage")
    sp = L.spot((1.8, -2.4, 1.6), (0, 0, 0), energy=700, size_deg=40, blend=0.7, color=(0.7, 0.85, 1.0), name="cool",
                radius=0.05)
    tgt = _track(sp, (0, 0, 0), "cool_t")
    C.key_loc(tgt, [(1, (0.3, -0.6, 0)), (n, (-0.2, -0.9, 0))])
    L.area((0, 0, 3), (0, 0, 0), energy=80, size=4, color=(0.5, 0.65, 0.8), name="ambient")
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.0, 0.0, 4.7), (0.0, 0.01, 0.0), 3.0), (n, (0.0, 0.0, 4.35), (0.0, 0.01, 0.0), 2.0)])
    L.bake_static()


# ============================================================================ the section diagram (S08 / S10 / S13)

K = 0.006  # metres of diagram per foot


def dz(d):
    return -d * K


def _hw(d):
    """Half-width of the section (diagram metres) at depth d ft: narrower throat, belled below."""
    keys = [(-80, 0.72), (0, 0.72), (120, 0.7), (300, 0.86), (550, 1.0), (850, 1.05), (1050, 1.0), (1200, 0.9)]
    return C.piecewise(keys, d)


XL, XR = -0.3, 0.3  # Exley line (cyan), Bowden line (orange)


def _xs(L, n):
    C.world_black((0.0, 0.0, 0.0))
    ds = [-80, -40, 0, 60, 120, 200, 300, 420, 550, 700, 850, 950, 1050, 1150, 1200]
    left = [(-_hw(d) * (1 + 0.04 * math.sin(d * 0.03)), d) for d in ds]
    right = [(_hw(d) * (1 + 0.04 * math.sin(d * 0.027 + 1)), d) for d in reversed(ds)]
    poly = left + right
    wpoly = [p for p in poly if p[1] >= 0]
    xs = C.xsection(poly, dz, extent=(-3.2, 3.2, dz(1320), dz(-65)), water_poly=wpoly, name="zx",
                    water_top=(0.03, 0.22, 0.24), water_bot=(0.0, 0.0, 0.0), outline_color=C.CYAN, outline_strength=0.0,
                    rock_mat_=L.mat_noise_surface("zx_rk", (0.07, 0.065, 0.055), (0.26, 0.24, 0.2), scale=1.2, bump=0.2,
                                                  rough=0.9))
    xs["outline"].hide_render = True
    om = C.emis("zx_out", C.CYAN, 3.0)
    for side, pts in (("L", left), ("R", list(reversed(right)))):
        C.curve([(x, -0.42, dz(d)) for x, d in pts if -65 <= d <= 1040], thickness=0.014, mat=om, name="zx_out" + side)
    # unknown bottom: dashed arc + "?"
    arc = []
    for k in range(13):
        a = math.pi * k / 12
        arc.append((-_hw(1040) * math.cos(a), -0.42, dz(1040) - 0.4 * math.sin(a)))
    C.dotted_path(arc, spacing=0.09, r=0.016, color=C.CYAN, strength=3.0, name="zx_dash")
    C.text("?", (0.0, -0.44, dz(1040) - 0.18), size=0.42, color=(0.7, 1.0, 0.95), strength=3.0, name="zx_q")
    # ground and water line
    gm = C.emis("zx_ground", (0.75, 0.6, 0.35), 2.5)
    for sgn in (-1, 1):
        C.curve([(sgn * 3.2, -0.42, dz(-65)), (sgn * _hw(-65), -0.42, dz(-65))], thickness=0.016, mat=gm, name="zx_g")
    C.curve([(-_hw(0), -0.42, dz(0)), (_hw(0), -0.42, dz(0))], thickness=0.012, mat=C.emis("zx_wl", (0.7, 1, 1), 4),
            name="zx_wline")
    # depth ruler (left)
    rm = C.emis("zx_ruler", (0.75, 0.8, 0.82), 1.5)
    rx = -1.45
    C.curve([(rx, -0.43, dz(0)), (rx, -0.43, dz(1000))], thickness=0.006, mat=rm, name="ruler")
    for dd in range(0, 1001, 100):
        w = 0.09 if dd % 250 == 0 else 0.045
        C.curve([(rx - w, -0.43, dz(dd)), (rx, -0.43, dz(dd))], thickness=0.006, mat=rm, name="tick")
    for dd in (0, 250, 500, 750, 1000):
        C.text(f"{dd} FT", (rx - 0.12, -0.45, dz(dd)), size=0.11, color=(0.85, 0.9, 0.92), strength=2.0, align="RIGHT",
               font=C.FONT_OSWALD, name="lab")
    # the two descent lines
    lm = C.emis("zx_lines", (0.92, 0.92, 0.88), 1.6)
    C.curve([(XL, -0.43, dz(-10)), (XL, -0.43, dz(1010))], thickness=0.005, mat=lm, name="lineL")
    C.curve([(XR, -0.43, dz(-10)), (XR, -0.43, dz(960))], thickness=0.005, mat=lm, name="lineR")
    L.area((-3, -4, 1), (math.radians(60), 0, math.radians(-35)), energy=500, size=5, color=(0.7, 0.85, 1.0))
    cam = C.camera(lens=50)
    return xs, cam


def _dot(x, d, color, name):
    o, h, hem = C.glow_dot((x, -0.47, dz(d)), color, r=0.055, halo=3.0, strength=8, name=name)
    return o, hem


def _xcam(cam, n, keys, dist=8.0):
    """keys: [(frame, z_centre, lens)]"""
    C.aim_cam(cam, n, [(f, (0.0, -dist, zc), (0.0, 0.0, zc)) for f, zc, _ in keys],
              lens_keys=[(f, ln) for f, _, ln in keys])


def S08(L, n):
    xs, cam = _xs(L, n)
    ex, _ = _dot(XL, 160, C.CYAN, "exley")
    bo, _ = _dot(XR, 160, BOWDEN, "bowden")
    ke = [(1, 160), (n, 700)]
    kb = [(1, 150), (n, 680)]
    for o, x, kk in ((ex, XL, ke), (bo, XR, kb)):
        for f in range(1, n + 1, 2):
            o.location = (x, -0.47, dz(C.piecewise(kk, f, fn=lambda t: t)))
            o.keyframe_insert("location", frame=f)
    # light trails grow behind each dot
    for nm, x, kk, col in (("trL", XL, ke, C.CYAN), ("trR", XR, kb, BOWDEN)):
        tr = C.curve([(x, -0.45, dz(0)), (x, -0.45, dz(700))], thickness=0.012, mat=C.emis(nm + "_m", col, 2.0), name=nm)
        C.grow_curve(tr, [(1, 160 / 700), (n, 1.0)])
        for fc in L._fcurves(tr.data.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    _xcam(cam, n, [(1, dz(160) - 0.9, 50), (n, dz(700) + 0.3, 50)], dist=10.0)
    L.bake_static()


def S10(L, n):
    xs, cam = _xs(L, n)
    ex, _ = _dot(XL, 935, C.CYAN, "exley")
    bo, _ = _dot(XR, 900, BOWDEN, "bowden")
    turn = 16
    for f in range(1, n + 1, 2):
        ex.location = (XL, -0.47, dz(C.piecewise([(1, 935), (n, 1000)], f, fn=lambda t: t)))
        ex.keyframe_insert("location", frame=f)
        bo.location = (XR, -0.47, dz(C.piecewise([(1, 900), (turn, 925), (turn + 8, 925), (n, 810)], f)))
        bo.keyframe_insert("location", frame=f)
    # record flag at 925 ft on Bowden's line
    fm = C.emis("flag_m", (1.0, 0.78, 0.24), 4.0)
    flag = C.flat_poly([(XR + 0.02, dz(925) + 0.2), (XR + 0.3, dz(925) + 0.13), (XR + 0.02, dz(925) + 0.06)], -0.47, fm,
                       name="flag")
    pole = C.curve([(XR + 0.02, -0.47, dz(925)), (XR + 0.02, -0.47, dz(925) + 0.22)], thickness=0.006, mat=fm,
                   name="pole")
    lab = C.text("925 FT", (XR + 0.36, -0.47, dz(925) + 0.13), size=0.17, color=(1.0, 0.85, 0.4), strength=3.0,
                 align="LEFT", font=C.FONT_OSWALD, name="flag_t")
    C.hide_from_frame([flag, pole], f_show=turn + 2)
    C.pop_in([lab], [turn + 4], dur=5)
    _xcam(cam, n, [(1, dz(925) + 0.5, 52), (n, dz(925) + 0.6, 45)], dist=10.0)
    L.bake_static()


def S13(L, n):
    cut = 41
    xs, cam = _xs(L, n)
    ex, hem = _dot(XL, 900, C.CYAN, "exley")
    C.key_input(hem.inputs[1], [(1, 2.8), (cut - 1, 2.0)])
    cm = C.emis("wrap_m", (0.95, 0.95, 0.9), 3.0)
    coil = C.curve(C.helix((0, 0, 0), (0, 0, 1), 0.1, 5, 0.26, pts_per_turn=18), thickness=0.007, mat=cm, name="wrap")
    coil.parent = ex
    coil.location = (0, 0, 0)
    for f in range(1, cut, 2):
        dd = C.piecewise([(1, 900), (cut - 1, 300)], f)
        ex.location = (XL, -0.47, dz(dd))
        ex.keyframe_insert("location", frame=f)
        coil.rotation_euler = (0, 0, f * 0.25)
        coil.keyframe_insert("rotation_euler", frame=f)
    # insert set: coil of white line on wet rock (far off to the side; camera cuts to it)
    ox = 60.0
    rk = L.mat_noise_surface("ins_rock", (0.03, 0.03, 0.03), (0.3, 0.28, 0.24), scale=6.0, bump=0.8, rough=0.25)
    C.floor(size=(3, 3), center=(ox, 0, -0.02), mat=rk, strength=0.04, levels=5, name="insrock", ripples=False)
    lm = L.mat_principled("insline_m", (0.95, 0.95, 0.9), rough=0.45, emit=(0.9, 0.9, 0.85), emit_strength=0.15)
    for k in range(3):
        hp = C.helix((ox + 0.02 * k, 0.01 * k, 0.012 + 0.012 * k), (0, 0, 1), 0.13 - 0.012 * k, 3, 0.01,
                     pts_per_turn=24, wobble=0.12, seed=k + 3, phase=k * 0.8)
        C.curve(hp, thickness=0.006, mat=lm, name=f"inscoil{k}")
    C.curve([(ox + 0.12, 0.02, 0.012), (ox + 0.35, -0.12, 0.01), (ox + 0.7, -0.05, 0.008)], thickness=0.006, mat=lm,
            name="instail", smooth_pts=True)
    sp = L.spot((ox - 0.6, -0.8, 1.2), (0, 0, 0), energy=120, size_deg=45, blend=0.8, color=(1.0, 0.95, 0.88),
                name="insspot")
    _track(sp, (ox, 0, 0), "ins_t")
    L.area((ox + 0.6, 0.6, 1.2), (math.radians(-35), math.radians(30), 0), energy=30, size=1.5, color=(0.7, 0.85, 1.0),
           name="insfill")
    # camera: section pull-up, then hard cut to the macro insert
    keys = []
    for f in list(range(1, cut, 3)) + [cut - 1]:
        dd = C.piecewise([(1, 900), (cut - 1, 300)], f)
        keys.append((f, (0.0, -9.0, dz(dd) + 0.4), (0.0, 0.0, dz(dd) + 0.4)))
    keys.append((cut, (ox - 0.05, -0.48, 0.36), (ox, 0.0, 0.0)))
    keys.append((n, (ox - 0.03, -0.38, 0.29), (ox, 0.0, 0.0)))
    C.aim_cam(cam, n, keys)
    for fc in L._fcurves(cam.animation_data.action):
        for kp in fc.keyframe_points:
            if kp.co[0] in (cut - 1,):
                kp.interpolation = "CONSTANT"
    cam.data.lens = 50
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 2.8
    cam.data.dof.focus_distance = 9.0
    cam.data.dof.keyframe_insert("focus_distance", frame=cut - 1)
    cam.data.dof.focus_distance = 0.6
    cam.data.dof.keyframe_insert("focus_distance", frame=cut)
    C.constant_keys(cam.data)
    L.bake_static()


# ============================================================================ S09 Bowden at 925 ft

def S09(L, n):
    _shaft(L, n, density=0.05, sun=0.0, center_z=-30, vol_h=20)
    z = -30.0
    C.line([(LX, 0.0, z + 8), (LX, 0.0, z - 8)], thickness=0.01, emit=1.0, name="bline")
    d = _diver("bowden", BOWDEN, energy=1500, beam_len=4.0, beam=0.3, deg=26, tanks="doubles", suit=(0.06, 0.06, 0.07))
    pos = Vector((LX + 0.32, 0.12, z))
    r = _upright(d, tuple(pos), face_deg=115, tilt=0.12, helmet=BOWDEN_HELMET)
    for f in range(1, n + 1, 3):
        r.location = pos + Vector((0, 0, 0.04 * math.sin(f * 0.12)))
        r.keyframe_insert("location", frame=f)
        d["shoulderR"].rotation_euler = (-0.75 + 0.05 * math.sin(f * 0.3), 0, 0.15)
        d["shoulderR"].keyframe_insert("rotation_euler", frame=f)
    d["shoulderL"].rotation_euler = (-1.0, 0, -0.75)  # left hand on the line
    L.anim_swim(d, n, kick_rate=0.3, amp=0.1)
    # torch aims down past the line
    tt = _track(d["torch"], tuple(pos + Vector((-0.8, 1.5, -2.2))), "torch_t")
    g = C.gauge("wrist", radius=0.05, face_emit=2.5)
    g["root"].parent = d["shoulderR"]
    g["root"].location = (0.0, 0.36, -0.06)
    g["root"].rotation_euler = (math.pi / 2, 0, 0)
    for f in range(1, n + 1, 4):
        g["pivot"].rotation_euler = (0, -C.lerp(0.2, 1.5, (f - 1) / (n - 1)), 0)
        g["pivot"].keyframe_insert("rotation_euler", frame=f)
    gl = L.point((0, 0, 0), energy=12, color=(0.9, 1.0, 0.85), radius=0.05, name="gaugeglow")
    gl.parent = g["root"]
    gl.location = (0, -0.08, 0)
    gd, _, _ = C.glow_dot((0, 0, 0), (0.75, 1.0, 0.8), r=0.012, halo=3.0, strength=2.5, name="gaugehalo")
    gd.parent = g["root"]
    gd.location = (0, -0.03, 0)
    C.bubble_trail(lambda f: pos + Vector((0.05, 0.0, 0.6)), n, count=70, every=1.7, rise=2.0, size=0.02, seed=7,
                   spread=0.08, life=(18, 32), name="exhale")
    _specks(n, (LX, 0.5, z), (4, 4, 4), count=1500, seed=14, vel=(0.0, 0.0, 0.08))
    C.rim_light(tuple(pos + Vector((0, 0, 0.3))), (0.9, 2.4, 1.2), energy=2600, color=CYAN_RIM, size_deg=45, name="rim")
    C.rim_light(tuple(pos + Vector((0, 0, 0.0))), (1.8, 0.6, -0.6), energy=1200, color=CYAN_RIM, size_deg=45, name="rim2")
    C.rim_light(tuple(pos + Vector((0, 0, 0.6))), (-1.6, -0.6, 2.2), energy=300, color=(1.0, 0.8, 0.55), size_deg=35,
                name="key")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (LX - 1.55, -1.7, z + 0.75), tuple(pos + Vector((0, 0, 0.45)))),
                       (n, (LX - 1.15, -1.25, z + 0.7), tuple(pos + Vector((0, 0, 0.5))))],
              shake=0.02, rot_shake=0.006, rate=0.8)
    C.cam_fill(cam, energy=140, color=(0.55, 0.8, 0.85))
    L.bake_static()


# ============================================================================ S11 looking up: one light rises

def S11(L, n):
    C.world_black((0.0, 0.006, 0.01))
    C.render_quality(vol_end=60, vol_tile="8", vol_samples=32)
    C.water(center=(0, 0, -25), size=(22, 22, 60), color=(0.35, 0.68, 0.62), density=0.022, absorption=(0.06, 0.2, 0.22))
    C.shaft(4.0, -60.0, lambda z, a: 7.0 + 1.1 * math.sin(2 * a + z * 0.05) + 0.5 * math.sin(5 * a + 1.0),
            step=1.0, ring=40, seed=7, rough=0.22, name="zshaft", disp=(0.8, 0.25),
            mat=C.rock_mat("zrock", (0.035, 0.05, 0.045), (0.3, 0.36, 0.3), scale=1.3))
    C.sun_from((0.15, 0.1, 1.0), energy=3.0, color=(0.6, 0.95, 0.9), angle=3)
    disc = L.prim("cyl", loc=(0, 0, 2.0), vertices=64, radius=8.5, depth=0.02, name="daylight")
    L.assign(disc, C.emis("daylight_m", (0.5, 0.92, 0.88), 1.2))
    for zb, e in ((-8, 1600), (-18, 1300), (-28, 900), (-38, 500)):
        L.point((0.4, 0.3, zb), energy=e, color=(0.4, 0.8, 0.75), radius=1.5, name="bounce")
    # two lines up the shaft: Bowden's carries his rising light, Exley's runs down past camera into the black
    _lines(z_top=2.0, z_bot=-70.0, emit=1.4)
    z0, z1 = -37.0, -29.0
    dot, _, hem = C.glow_dot((LX + 0.15, 0.0, z0), (1.0, 0.92, 0.75), r=0.12, halo=5.0, strength=14, light=120,
                             name="bowden_light")
    C.key_loc(dot, [(1, (LX + 0.15, 0.0, z0)), (n, (LX + 0.15, 0.0, z1))])
    L.linear_fcurves(dot)
    sp = L.spot((0, 0, 0), (math.pi, 0, 0), energy=2500, size_deg=40, blend=0.6, color=C.TORCH, name="bowden_sp",
                radius=0.05)
    sp.parent = dot
    C.beam_cone(sp, length=6.0, strength=0.25, name="bowden_beam")
    _specks(n, (0, 0, -42), (6, 6, 10), count=2000, seed=21, vel=(0.0, 0.0, 0.1), color=(0.7, 0.85, 0.7), emit=0.1)
    cam = C.camera(lens=18)
    up = Vector((0.0, math.sin(math.radians(24)), math.cos(math.radians(24)))) * 20
    c0, c1 = Vector((0.4, -4.6, -46.5)), Vector((0.4, -4.5, -45.9))
    C.aim_cam(cam, n, [(1, tuple(c0), tuple(c0 + up)), (n, tuple(c1), tuple(c1 + up))],
              shake=0.006, rot_shake=0.0015, rate=0.3)
    C.cam_fill(cam, energy=60, color=(0.45, 0.8, 0.75))
    L.bake_static()


# ============================================================================ S17 loop: one diver on one line, back to S01 framing

def S17(L, n):
    _shaft(L, n, R=6.0)
    _lines(xs=(-LX, LX), emit=1.0)
    d = _diver("modern", (0.92, 0.92, 0.92), energy=2600, beam_len=9.0, beam=0.5, deg=22, tanks="sidemount",
               suit=(0.04, 0.045, 0.06))
    x = -LX + 0.35
    r = _head_down(d, (x, 0.25, -1.2), tilt=0.3, yaw=math.pi)
    C.key_loc(r, [(1, (x, 0.25, 3.0)), (n, (x, 0.3, -1.6))])
    L.linear_fcurves(r)
    L.anim_swim(d, n, kick_rate=0.55, amp=0.22)
    C.bubble_trail(lambda f: Vector((x - 0.1, 0.1, 3.0 + (-1.6 - 3.0) * (f - 1) / (n - 1) + 0.55)), n, count=22,
                   rise=1.6, size=0.018, seed=9, name="bub")
    _specks(n, (0, 0.2, 1.0), (5.0, 4.0, 12.0), count=2400, seed=5, vel=(0.02, 0.0, 0.35))
    C.rim_light((0, 0.3, 0), (0.5, 3.0, 4.0), energy=1500, color=CYAN_RIM, size_deg=60, name="toprim")
    cam = C.camera(lens=20)
    p0 = Vector(S01_CAM0[0]) + Vector((0, 0, 4.6))
    t0 = Vector(S01_CAM0[1]) + Vector((0, 0, 4.6))
    C.aim_cam(cam, n, [(1, tuple(p0), tuple(t0)), (n, *S01_CAM0)], shake=0.02, rot_shake=0.004, rate=0.5,
              fn=lambda x: x, shake_keys=[(1, 1.0), (n - 6, 1.0), (n, 0.0)])
    C.cam_fill(cam, energy=60, color=(0.5, 0.85, 0.8))
    L.bake_static()
