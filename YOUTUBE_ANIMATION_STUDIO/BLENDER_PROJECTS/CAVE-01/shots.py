"""CAVE-01 — Dave Shaw, Boesmansgat. Shot builders (def Sxx(L, n)). Shared builders: PIPELINE/blender/lib_cave.py"""
import sys, os, math, random
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "PIPELINE", "blender"))
import importlib
import lib_cave as C
importlib.reload(C)
import bpy
from mathutils import Vector

SHAW_FINS = C.YELLOW
SHIRLEY_FINS = C.ORANGE


# ============================================================================ shared sets

def _deep(L, n, density=0.05, vol_end=30, color=(0.3, 0.62, 0.6), center=(0, 0, 2), size=(30, 30, 14)):
    C.world_black((0.0, 0.003, 0.005))
    C.render_quality(vol_end=vol_end)
    return C.water(center=center, size=size, color=color, density=density, absorption=(0.06, 0.3, 0.3))


def _bottom_set(L, n, shape=True, seed=3, wall=True):
    """Chamber floor at 270 m with optional abstract lost-diver shape at origin."""
    env = C.chamber_floor(center=(0, 0, 0), size=34, seed=seed, boulder_count=12, back_wall=wall, wall_dist=10)
    lost = None
    if shape:
        lost = C.lost_shape(loc=(0, 0, 0), rot_z=0.55)
    return env, lost


# ============================================================================ S01 cold open: torch finds the shape

def S01(L, n):
    _deep(L, n, density=0.055)
    _bottom_set(L, n)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.55, -3.5, 1.0), (0.0, -0.2, -0.5)), (n, (0.4, -2.6, 0.85), (0.0, -0.1, -0.45))],
              shake=0.02, rot_shake=0.004, rate=0.5, fn=lambda x: x)
    # torch from off-screen left, sweeping left->right, settling on the shape
    tgt = L.link(bpy.data.objects.new("torch_tgt", None))
    sp = L.spot((-2.2, -1.9, 1.35), (0, 0, 0), energy=1300, size_deg=30, blend=0.5, color=C.TORCH, name="torch",
                radius=0.03)
    con = sp.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    C.key_loc(tgt, [(1, (-2.6, 1.6, -0.2)), (14, (-1.6, 1.0, -0.1)), (34, (0.15, 0.05, 0.0)), (40, (0.0, 0.0, 0.0)),
                    (n, (0.05, 0.1, 0.0))])
    L.ease_all(tgt)
    C.beam_cone(sp, length=4.2, strength=0.22, name="torch_beam")
    # faint cyan from far above so the black isn't dead
    L.spot((0.5, 1.0, 9), (0, 0, 0), energy=160, size_deg=60, blend=1.0, color=(0.3, 0.75, 0.8), name="cyanrim")
    s = C.cloud((-0.4, 0.4, 0.6), (4.5, 3.6, 1.3), count=2200, radius=0.004, emit=0.05, seed=11)
    C.drift(s, n, (0.05, 0.02, 0.025))
    C.rim_light((0, 0.1, 0.1), (0.6, 3.5, 1.2), energy=500, color=(0.35, 0.8, 0.95), size_deg=30, name="backrim")
    C.cam_fill(cam, energy=14)
    L.bake_static()


# ============================================================================ S02 reverse: Shaw hangs above the shape

def S02(L, n):
    _deep(L, n, density=0.05)
    _bottom_set(L, n)
    d = C.diver("shaw", fins=SHAW_FINS, light_energy=2400, beam_len=2.6, beam_strength=0.18, beam_deg=26)
    r = d["root"]
    r.location = (-0.9, 0.25, 1.35)
    r.rotation_euler = (-0.1, 0, -math.pi / 2)  # facing +X, slight head-down
    d["torch"].rotation_euler = (math.pi / 2 - 1.05, 0, 0)  # beam angled steeply down onto the shape
    for f in range(1, n + 1, 3):
        r.location.z = 1.35 + 0.03 * math.sin(f / 24 * 2.2)
        r.keyframe_insert("location", frame=f)
    L.anim_swim(d, n, kick_rate=0.35, amp=0.12)
    C.rim_light((-0.9, 0.25, 1.35), (-0.6, 2.8, 2.6), energy=900, color=(0.35, 0.85, 1.0), size_deg=35, name="rimtop")
    C.rim_light((-0.9, 0.25, 1.35), (0.4, 3.0, -0.2), energy=500, color=(0.3, 0.7, 0.9), size_deg=35, name="rimlow")
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (0.55, -2.3, 0.45), (-0.55, 0.2, 0.95)), (n, (0.8, -3.3, 0.55), (-0.55, 0.2, 0.85))],
              shake=0.012, rot_shake=0.003)
    C.cam_fill(cam, energy=10)
    fins = C.cloud((-2.0, 0.25, 0.5), (1.4, 1.0, 0.7), count=700, radius=0.005, emit=0.05, seed=5)
    C.drift(fins, n, (0, 0, 0.2))
    amb = C.cloud((0, 0.5, 1.0), (5, 4, 2.4), count=1400, radius=0.004, emit=0.04, seed=9)
    C.drift(amb, n, (0.03, 0.0, 0.02))
    L.bake_static()


# ============================================================================ cross-section diagram (S03 / S09 / S13)

XS_Z0, XS_K = 2.18, 0.01082
XS_X = 0.62


def dz(d):
    return XS_Z0 - d * XS_K


BOES = [(-1.7, -45), (-1.3, -25), (-0.95, -15), (-0.6, -4), (-0.42, 0), (-0.22, 8), (-0.18, 22), (-0.2, 40),
        (-0.35, 55), (-0.8, 68), (-1.35, 90), (-1.75, 125), (-1.95, 165), (-2.0, 205), (-1.9, 240), (-1.6, 262),
        (-1.0, 272), (-0.3, 280), (0.4, 283), (1.1, 276), (1.55, 262), (1.85, 235), (1.95, 195), (1.85, 150),
        (1.6, 110), (1.15, 80), (0.55, 60), (0.25, 45), (0.2, 25), (0.25, 8), (0.42, 0), (0.6, -4), (0.95, -15),
        (1.3, -25), (1.7, -45)]


def _xs(L, n, cz=0.0):
    C.world_black((0.0, 0.0, 0.0))
    wpoly = [p for p in BOES if p[1] >= 0]
    xs = C.xsection(BOES, dz, x_scale=XS_X, extent=(-4, 4, -7.5, dz(-25)), water_poly=wpoly, name="boes")
    P = xs["P"]
    # ground surface strip (sand) and a few scrub dots
    sand = C.emis("sand_line", (0.85, 0.62, 0.35), 2.5)
    for side in (-1, 1):
        C.curve([(side * 3.2, -0.42, dz(-25)), (side * 1.3 * XS_X, -0.42, dz(-25))], thickness=0.022, mat=sand,
                name="ground")
    # surface pool line
    C.curve([tuple(P(-0.42, 0)), tuple(P(0.42, 0))], thickness=0.02, mat=C.emis("poolline", (0.7, 1, 1), 6), name="pool")
    # depth ruler (left)
    rm = C.emis("ruler", (0.75, 0.8, 0.82), 1.6)
    rx = -1.62
    C.curve([(rx, -0.43, dz(0)), (rx, -0.43, dz(283))], thickness=0.008, mat=rm, name="ruler")
    for dd in range(0, 281, 25):
        w = 0.1 if dd % 100 == 0 else 0.05
        C.curve([(rx - w, -0.43, dz(dd)), (rx, -0.43, dz(dd))], thickness=0.008, mat=rm, name="tick")
    for dd, lab in ((0, "0 M"), (100, "100"), (200, "200"), (270, "270")):
        C.text(lab, (rx - 0.14, -0.45, dz(dd)), size=0.2, color=(0.85, 0.9, 0.92), strength=2.0, align="RIGHT",
               name="lab")
    # lighting for the slab bevel / depth
    L.area((-3, -4, 4), (math.radians(60), 0, math.radians(-35)), energy=600, size=4, color=(0.7, 0.85, 1.0))
    cam = C.camera(lens=50)
    return xs, P, cam


def _cam_xs(cam, n, keys):
    # keys: (frame, cz, lens)
    C.aim_cam(cam, n, [(f, (0.9, -13.9, cz + 0.5), (0, 0, cz)) for f, cz, _ in keys],
              lens_keys=[(f, ln) for f, _, ln in keys])


def S03(L, n):
    xs, P, cam = _xs(L, n)
    _cam_xs(cam, n, [(1, 0.0, 50), (30, 0.0, 50), (n, -0.05, 52.5)])
    down = [P(-0.02, 0), P(-0.02, 45), P(-0.35, 100), P(-0.55, 200), P(-0.45, 268)]
    dot, halo, hem = C.glow_dot(tuple(down[0]), C.CYAN, r=0.065, light=40, name="shaw")
    trail = C.curve([tuple(p + Vector((0, 0.01, 0))) for p in down], thickness=0.016, mat=C.emis("trail", C.CYAN, 5),
                    name="trail_down")
    C.grow_curve(trail, [(1, 0.0), (4, 0.0), (28, 1.0)])
    up = [P(0.05, 268), P(0.35, 205), P(0.45, 110), P(0.12, 55), P(0.06, 20), P(0.06, 0)]
    # ascent: fast through the deep part, then crawl between many shallow stops
    tkeys = [(32, 0.0), (42, 0.35), (60, 0.7), (n - 6, 1.0)]
    C.move_along(dot, down, [(4, 0.0), (28, 1.0)])
    C.move_along(dot, up, tkeys)
    dots = C.dotted_path([tuple(p) for p in up], spacing=0.11, r=0.022, color=(0.9, 0.95, 1.0), strength=3.0,
                         name="ascdot")
    # pop dots behind the moving diver dot (path order = from bottom)
    total = len(dots)
    frames = []
    for i in range(total):
        t = i / max(1, total - 1)
        # invert the ascent timing
        f = 32
        for (f0, t0), (f1, t1) in zip(tkeys, tkeys[1:]):
            if t0 <= t <= t1:
                f = int(f0 + (f1 - f0) * (t - t0) / max(1e-6, t1 - t0))
        frames.append(f)
    C.pop_in(dots, frames, dur=4)
    # deco stop ticks near the top (stops cluster shallow)
    tick_m = C.emis("stoptick", (1.0, 0.85, 0.3), 4)
    stops = [150, 120, 95, 75, 60, 48, 39, 30, 24, 18, 12, 9, 6]
    ticks = []
    for dd in stops:
        x = 0.62 if dd > 50 else 0.42
        o = C.curve([tuple(P(x - 0.06, dd)), tuple(P(x + 0.1, dd))], thickness=0.012, mat=tick_m, name="stop")
        ticks.append(o)
    tf = []
    for dd in stops:
        t = 1 - dd / 270
        f = int(C.piecewise([(0.0, 32), (0.35, 42), (0.7, 60), (1.0, n - 6)], t, fn=lambda x: x)) if False else None
        tf.append(f)
    # ticks appear one by one in the last part
    for i, o in enumerate(ticks):
        C.hide_from_frame([o], f_show=40 + int(i * (n - 50) / len(ticks)))
    L.bake_static()


def S09(L, n):
    xs, P, cam = _xs(L, n)
    _cam_xs(cam, n, [(1, 0.55, 50), (n, 0.0, 50)])
    down = [P(-0.05, 0), P(-0.05, 45), P(-0.4, 100), P(-0.65, 200), P(-0.55, 268)]
    sdot, _, _ = C.glow_dot(tuple(down[0]), C.CYAN, r=0.065, light=30, name="shaw")
    C.move_along(sdot, down, [(4, 0.0), (85, 1.0)])
    tr = C.curve([tuple(p) for p in down], thickness=0.014, mat=C.emis("trail", C.CYAN, 4), name="trail_s")
    C.grow_curve(tr, [(1, 0), (4, 0), (85, 1)])
    sh = [P(0.08, 0), P(0.08, 45), P(0.3, 100), P(0.35, 220)]
    odot, _, _ = C.glow_dot(tuple(sh[0]), C.ORANGE, r=0.065, light=30, name="shirley")
    C.move_along(odot, sh, [(20, 0.0), (100, 1.0)])
    tr2 = C.curve([tuple(p) for p in sh], thickness=0.014, mat=C.emis("trail2", C.ORANGE, 4), name="trail_o")
    C.grow_curve(tr2, [(1, 0), (20, 0), (100, 1)])
    # rendezvous line at 220 m
    rv = C.dotted_path([tuple(P(-1.95, 220)), tuple(P(1.95, 220))], spacing=0.1, r=0.018, color=(1, 0.7, 0.3),
                       strength=4, name="rv")
    C.pop_in(rv, [60 + i // 2 for i in range(len(rv))], dur=4)
    lab = C.text("220 M", (-1.76, -0.45, dz(220) + 0.13), size=0.17, color=(1, 0.75, 0.4), strength=4, align="RIGHT",
                 name="rvlab")
    C.hide_from_frame([lab], f_show=60)
    L.bake_static()


def S13(L, n):
    xs, P, cam = _xs(L, n)
    _cam_xs(cam, n, [(1, 0.0, 50), (n, 0.0, 51)])
    down = [P(-0.05, 0), P(-0.05, 45), P(-0.4, 100), P(-0.65, 200), P(-0.55, 268)]
    C.curve([tuple(p) for p in down], thickness=0.014, mat=C.emis("trail", (0.15, 0.45, 0.45), 2), name="trail_s")
    sdot, shalo, shem = C.glow_dot(tuple(down[-1]), C.CYAN, r=0.065, light=0, name="shaw")
    core_em = sdot.active_material.node_tree.nodes["Emission"].inputs[1]
    C.key_input(core_em, [(1, 10.0), (14, 10.0), (40, 0.4), (n, 0.0)])
    C.key_input(shem.inputs[1], [(1, 3.5), (14, 3.5), (40, 0.1), (n, 0.0)])
    C.key_loc(sdot, [(1, tuple(down[-1])), (14, tuple(down[-1] + Vector((0.02, 0, -0.02)))), (n, tuple(down[-1] + Vector((0.03, 0, -0.03))))])
    sh = [P(0.08, 0), P(0.08, 45), P(0.3, 100), P(0.35, 220)]
    C.curve([tuple(p) for p in sh], thickness=0.014, mat=C.emis("trail2", (0.5, 0.25, 0.05), 2), name="trail_o")
    odot, ohalo, ohem = C.glow_dot(tuple(sh[-1]), C.ORANGE, r=0.065, light=0, name="shirley")
    # Shirley waits: tiny bob
    for f in range(1, n + 1, 4):
        odot.location = sh[-1] + Vector((0, 0, 0.015 * math.sin(f * 0.25)))
        odot.keyframe_insert("location", frame=f)
    # rendezvous line pulsing red, empty
    rvm = C.emis("rv_m", (1, 0.15, 0.1), 4)
    rv = C.dotted_path([tuple(P(-1.95, 220)), tuple(P(1.95, 220))], spacing=0.1, r=0.018, name="rv",
                       color=(1, 0.15, 0.1))
    for o in rv:
        L.assign(o, rvm)
    em = rvm.node_tree.nodes["Emission"].inputs[1]
    C.key_input(em, [(f, 6.0 if (f // 9) % 2 == 0 else 0.6) for f in range(1, n + 1, 9)])
    C.constant_keys(rvm.node_tree)
    C.text("220 M", (-1.76, -0.45, dz(220) + 0.13), size=0.17, color=(1, 0.3, 0.2), strength=4, align="RIGHT", name="rvlab")
    # empty marker ring where Shaw should be
    ring = L.prim("torus", loc=tuple(P(-0.25, 220) + Vector((0, -0.02, 0))), rot=(math.pi / 2, 0, 0),
                  major_radius=0.12, minor_radius=0.008, name="emptyring")
    L.assign(ring, C.emis("ringm", (1, 0.3, 0.2), 3))
    C.key_scale(ring, [(1, 0.6), (20, 1.0), (40, 0.8), (n, 1.0)])
    L.bake_static()


# ============================================================================ desert exterior (S04 / S08 / S19)

def _desert(L, n, tod="dawn"):
    C.render_quality(vol_end=120, vol_tile="8", vol_samples=32)
    if tod == "dawn":
        sd = C.sun_dir(11, 115)
        C.sky_world(top=(0.32, 0.48, 0.7), horizon=(1.0, 0.8, 0.6), ground=(0.18, 0.13, 0.09), sun_dir=sd,
                    sun_color=(1.0, 0.75, 0.45), sun_glow=3.0, strength=1.0)
        C.sun_from(sd, energy=4.5, color=(1.0, 0.78, 0.55), angle=1.0)
    elif tod == "dusk":
        sd = C.sun_dir(2.5, 0)  # sun straight ahead (+Y), behind the figure
        C.sky_world(top=(0.06, 0.05, 0.14), horizon=(1.0, 0.3, 0.04), ground=(0.03, 0.02, 0.015), sun_dir=sd,
                    sun_color=(1.0, 0.45, 0.1), sun_glow=1.2, strength=1.0, glow_pow=60)
        C.sun_from(sd, energy=2.5, color=(1.0, 0.55, 0.25), angle=2.0)
    else:  # sunrise gold
        sd = C.sun_dir(7, 60)
        C.sky_world(top=(0.35, 0.45, 0.65), horizon=(1.0, 0.7, 0.35), ground=(0.15, 0.1, 0.06), sun_dir=sd,
                    sun_color=(1.0, 0.7, 0.35), sun_glow=4.0, strength=1.0)
        C.sun_from(sd, energy=5.0, color=(1.0, 0.72, 0.45), angle=1.0)
    cr = C.crater(R=9.0, depth=22.0, seed=2,
                  ground_mat=L.mat_noise_surface("desert_sand", (0.2, 0.11, 0.05), (0.5, 0.33, 0.17), scale=0.8,
                                                 bump=0.3, voronoi=False),
                  pool_mat=L.mat_principled("pool_m", (0.005, 0.05, 0.045), rough=0.03, emit=(0.01, 0.12, 0.1),
                                            emit_strength=0.5))
    C.bushes(count=90, rmin=11.5, rmax=60, seed=4, size=(0.5, 1.3), color=(0.1, 0.1, 0.04))
    for i, (x, y) in enumerate(((-14, 6), (15, -4), (-11, -12), (19, 13), (-22, -3))):
        L.tree((x, y, 0), height=random.Random(i).uniform(2.5, 4), seed=i + 3)
    return cr, sd


def S04(L, n):
    cr, sd = _desert(L, n, "dawn")
    pz = cr["pool_z"]
    # dive platform + line drop
    plat = L.prim("cube", loc=(2.2, -3.6, pz + 0.12), name="platform")
    plat.scale = (0.9, 0.6, 0.08)
    L.assign(plat, L.mat_principled("plat_m", (0.75, 0.55, 0.12), rough=0.6))
    for k in range(3):
        b = L.prim("cyl", loc=(2.2 - 0.6 + k * 0.6, -3.6, pz + 0.04), rot=(math.pi / 2, 0, 0), vertices=12, radius=0.12,
                   depth=1.2, name="float")
        L.assign(b, L.mat_principled("float_m", (0.8, 0.8, 0.78), rough=0.5))
    C.line([(2.0, -3.1, pz + 0.3), (2.0, -3.1, pz - 6)], thickness=0.02, emit=1.0, name="shotline")
    # line from rim down to platform
    C.line([(4.5, -8.2, 0.5), (3.6, -6.5, -4), (2.6, -4.0, pz + 0.2)], thickness=0.018, emit=0.3, name="rimline")
    dust = C.cloud((0, -4, 2), (30, 24, 6), count=1600, radius=0.008, color=(1.0, 0.85, 0.6), emit=0.4, seed=3)
    C.drift(dust, n, (0.4, 0.1, 0.05))
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (-5.5, -27, 21), (0, -1, -5)), (n, (-2.0, -14, 10.5), (0.8, -1.2, -19))],
              shake=0.03, rot_shake=0.002, rate=0.3)
    L.bake_static()


def _team_props(L, base):
    metal = L.mat_principled("tank_m", (0.6, 0.6, 0.62), rough=0.3, metal=0.8)
    bx, by = base
    for i in range(6):
        t = L.prim("cyl", loc=(bx + (i % 3) * 0.24, by + (i // 3) * 0.24, 0.45), vertices=14, radius=0.1, depth=0.8,
                   name="tank")
        L.assign(t, metal)
    coil = L.prim("torus", loc=(bx + 0.9, by - 0.4, 0.08), major_radius=0.3, minor_radius=0.05, name="coil")
    L.assign(coil, L.mat_principled("coil_m", (0.85, 0.85, 0.8), rough=0.6))
    crate = L.prim("cube", loc=(bx - 0.6, by + 0.2, 0.25), name="crate")
    crate.scale = (0.3, 0.25, 0.25)
    L.assign(crate, L.mat_principled("crate_m", (0.15, 0.12, 0.1)))


def S08(L, n):
    cr, sd = _desert(L, n, "dusk")
    R = 9.0
    rim_y = -cr["rim"](math.radians(270)) * 1.0
    shaw = L.char_figure("shaw_fig", color=(0.01, 0.01, 0.012))
    shaw["root"].location = (0.2, rim_y - 0.9, 0.3)
    shaw["root"].rotation_euler = (0, 0, 0)  # faces +Y into the hole
    shaw["neck"].rotation_euler = (0.35, 0, 0)  # head tilted down
    team = []
    for i, (x, y, rz) in enumerate(((1.5, rim_y - 2.4, 0.9), (2.3, rim_y - 1.4, -1.2), (-1.6, rim_y - 1.9, 2.0))):
        f = L.char_figure(f"team{i}", color=(0.012, 0.012, 0.014), height=1.7 + 0.06 * i)
        f["root"].location = (x, y, 0.25)
        f["root"].rotation_euler = (0, 0, rz)
        team.append(f)
    # one teammate bends to the tank stack, one walks with a coil
    t0 = team[0]
    for fr, a in ((1, 0.1), (int(n * 0.5), 0.6), (n, 0.35)):
        t0["pelvis"].rotation_euler = (a, 0, 0)
        t0["pelvis"].keyframe_insert("rotation_euler", frame=fr)
    L.anim_walk(team[2], 1, n, stride=0.35, rate=0.7,
                travel=((-1.6, rim_y - 1.9, 0.25), (-1.3, rim_y - 2.6, 0.25)))
    _team_props(L, (1.7, rim_y - 3.0))
    dust = C.cloud((0, rim_y - 3, 1.2), (14, 10, 3), count=900, radius=0.012, color=(1, 0.7, 0.4), emit=0.4, seed=8)
    C.drift(dust, n, (0.25, 0.05, 0.02))
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.6, rim_y - 7.5, 1.9), (0.0, rim_y + 10.0, -1.2)),
                       (n, (0.5, rim_y - 5.8, 1.8), (0.0, rim_y + 10.0, -1.4))], shake=0.015, rot_shake=0.002)
    L.bake_static()


def S19(L, n):
    cr, sd = _desert(L, n, "sunrise")
    pz = cr["pool_z"]
    cut = n - 12
    # --- loop-back cave set far away (match of S01 framing, silt now empty)
    OFF = Vector((600, 0, -200))
    C.water(center=tuple(OFF + Vector((0, 0, 2))), size=(30, 30, 14), color=(0.3, 0.62, 0.6), density=0.055,
            absorption=(0.06, 0.3, 0.3), name="cavewater")
    C.floor(size=(34, 34), center=tuple(OFF), strength=0.45, name="loopfloor")
    C.rocks([tuple(OFF + Vector(p)) for p in ((3, 4, 0), (-4, 6, 0), (5, -1, 0), (-3, -5, 0), (6, 8, 0))], count=5,
            size=(0.5, 1.4))
    sp = L.spot(tuple(OFF + Vector((-2.2, -1.9, 1.35))), (0, 0, 0), energy=0, size_deg=25, blend=0.5, color=C.TORCH,
                name="loop_torch")
    tgt = L.link(bpy.data.objects.new("lt_tgt", None))
    tgt.location = tuple(OFF + Vector((0.05, 0.1, 0)))
    con = sp.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    C.key_energy(sp, [(1, 0), (cut - 1, 0), (cut, 1300), (n, 1300)])
    C.constant_keys(sp.data)
    s = C.cloud(tuple(OFF + Vector((0, -0.6, 0.55))), (4.5, 5, 1.3), count=1800, radius=0.0055, emit=0.03, seed=11)
    C.drift(s, n, (0.05, 0.02, 0.025))
    # kill the desert light at the cut
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "SUN":
            C.key_energy(o, [(1, o.data.energy), (cut - 1, o.data.energy), (cut, 0.0)])
            C.constant_keys(o.data)
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    C.key_input(bg.inputs[1], [(1, 1.0), (cut - 1, 1.0), (cut, 0.0)])
    C.constant_keys(bpy.context.scene.world.node_tree)
    # mist over the pool catching the sunrise
    mist = C.cloud((0, 0, pz + 1.0), (14, 14, 1.5), count=900, radius=0.02, color=(1, 0.85, 0.65), emit=0.25, seed=4)
    C.drift(mist, n, (0.1, 0.05, 0.01))
    cam = C.camera(lens=28)
    o1 = tuple(OFF + Vector((0.55, -3.5, 1.0)))
    t1 = tuple(OFF + Vector((0.0, -0.2, -0.5)))
    o2 = tuple(OFF + Vector((0.5, -3.2, 0.95)))
    t2 = tuple(OFF + Vector((0.0, -0.15, -0.5)))
    C.aim_cam(cam, n, [(1, (1.2, -4.5, 12), (0, 0.5, pz)), (cut - 1, (0.6, -3.0, pz + 2.2), (0, 1.0, pz - 0.5)),
                       (cut, o1, t1), (n, o2, t2)], shake=0.015, rot_shake=0.002)
    lens = cam.data
    lens.lens = 28
    lens.keyframe_insert("lens", frame=cut - 1)
    lens.lens = 35
    lens.keyframe_insert("lens", frame=cut)
    C.constant_keys(lens)
    L.bake_static()


# ============================================================================ S05 vertical shaft descent

def S05(L, n):
    C.world_black((0.0, 0.004, 0.008))
    C.render_quality(vol_end=40)
    C.water(center=(0, 0, -20), size=(16, 16, 56), color=(0.3, 0.6, 0.65), density=0.035, absorption=(0.12, 0.35, 0.3))
    C.shaft(6, -46, lambda z, a: 4.6 + 0.8 * math.sin(a * 2 + z * 0.08) + 0.4 * math.sin(a * 5), step=0.8, ring=40,
            seed=7, rough=0.3, name="bshaft", disp=(0.7, 0.2),
            mat=C.rock_mat("shaftrock", (0.03, 0.04, 0.045), (0.25, 0.3, 0.3), scale=1.3))
    C.sun_from((0.25, 0.1, 1.0), energy=3.0, color=(0.55, 0.9, 1.0), angle=3)
    # shotline with distance tags
    lx, ly = 0.42, 0.0
    C.line([(lx, ly, 6), (lx, ly, -46)], thickness=0.012, emit=1.2, name="shotline")
    tagm = L.mat_principled("tag_m", (0.95, 0.95, 0.9), emit=(0.9, 0.9, 0.85), emit_strength=0.8)
    for k in range(18):
        t = L.prim("cube", loc=(lx + 0.03, ly, 4 - k * 2.8), name="tag")
        t.scale = (0.04, 0.012, 0.07)
        L.assign(t, tagm)
    d = C.diver("shaw", fins=SHAW_FINS, light_energy=3500, beam_len=10, beam_strength=0.5, beam_deg=20)
    r = d["root"]
    r.rotation_euler = (-math.pi / 2 + 0.25, 0, 0.0)  # head-down, slight angle
    z0, z1 = 0.0, -15.0
    for f in range(1, n + 1, 2):
        t = (f - 1) / (n - 1)
        r.location = (0.05, -0.15, z0 + (z1 - z0) * (0.15 * t + 0.85 * t * t * (3 - 2 * t)))
        r.keyframe_insert("location", frame=f)
    L.anim_swim(d, n, kick_rate=0.6, amp=0.2)
    p = C.cloud((0, 0, -9), (6, 6, 24), count=3600, radius=0.006, emit=0.08, seed=3)
    keys = []
    for f in range(1, n + 1, 6):
        t = (f - 1) / (n - 1)
        zz = z0 + (z1 - z0) * (0.15 * t + 0.85 * t * t * (3 - 2 * t))
        keys.append((f, (0.05, -0.15 + 1.9, zz + 3.4), (0.05, -0.35, zz - 3.5), 5.0 * t))
    cam = C.camera(lens=20)
    C.aim_cam(cam, n, keys, shake=0.02, rot_shake=0.004, fn=lambda x: x)
    C.cam_fill(cam, energy=60, color=(0.5, 0.85, 0.95))
    L.bake_static()


# ============================================================================ S06 helmet POV: torch snaps onto a fin

def S06(L, n):
    _deep(L, n, density=0.06)
    env = C.chamber_floor(center=(0, 0, 0), size=34, seed=6, boulder_count=16, back_wall=True, wall_dist=8)
    # silt slope: tilt a second floor patch
    C.rocks([(2.0, 2.5, 0), (-2.4, 3.0, 0), (1.4, 0.2, 0), (-1.8, -0.4, 0), (3.2, 5, 0), (0.6, 4.5, 0)], count=6,
            size=(0.35, 0.9), seed=12)
    fin = C.fin_blade((-0.6, 0.75, -0.08), (1.05, 0.25, 0.35), mat=L.mat_principled("lostfin_m", (0.14, 0.145, 0.15),
                                                                                     rough=0.5), name="lostfin")
    strap = L.prim("torus", loc=(-0.6, 0.72, 0.03), rot=(0.4, 0.3, 0), major_radius=0.07, minor_radius=0.012,
                   name="strap")
    L.assign(strap, L.mat_principled("strap_m", (0.1, 0.1, 0.1)))
    cam = C.camera(lens=24)
    eye = (0.2, -2.6, 1.55)
    fin_t = (-0.5, 0.95, 0.05)
    C.aim_cam(cam, n, [(1, eye, (2.4, 1.6, -0.3)), (16, (0.2, -2.6, 1.5), (1.6, 2.2, -0.2)),
                       (27, (0.15, -2.55, 1.48), fin_t), (n, (0.1, -2.2, 1.4), fin_t)],
              shake=0.012, rot_shake=0.006, shake_keys=[(1, 1.0), (27, 0.4), (n, 1.0)],
              fn=lambda x: x * x * (3 - 2 * x))
    torch = L.spot((0.16, 0.1, 0.0), (0, 0, 0), energy=2400, size_deg=22, blend=0.35, color=C.TORCH, name="helmet",
                   radius=0.02)
    torch.parent = cam
    torch.rotation_euler = (0.03, -0.05, 0)
    s = C.cloud((0, 0, 0.9), (6, 6, 2.2), count=2600, radius=0.006, emit=0.03, seed=13)
    C.drift(s, n, (0.03, 0.01, 0.02))
    L.bake_static()


# ============================================================================ S07 blurred chamber behind memorial card

def S07(L, n):
    _deep(L, n, density=0.06)
    _bottom_set(L, n, shape=True)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (1.2, -3.6, 0.9), (0, 0, 0.3)), (n, (0.6, -3.2, 0.8), (0, 0, 0.3))], shake=0.01)
    L.dof(cam, distance=0.6, fstop=0.7)
    tgt = L.link(bpy.data.objects.new("tt", None))
    sp = L.spot((-2.0, -2.0, 1.6), (0, 0, 0), energy=2200, size_deg=28, blend=0.6, color=C.TORCH, name="torch")
    con = sp.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    C.key_loc(tgt, [(1, (0.6, 0.6, 0)), (n, (-0.2, -0.1, 0))])
    near = C.cloud((0.5, -2.2, 0.8), (2, 1.2, 1.6), count=500, radius=0.006, emit=0.15, seed=21)
    C.drift(near, n, (0.04, 0, 0.03))
    L.spot((0, 0, 6), (0, 0, 0), energy=400, size_deg=50, blend=1, color=(0.3, 0.8, 0.85), name="cyan")
    C.rim_light((0, 0.1, 0.1), (0.5, 3.5, 1.0), energy=500, color=(0.35, 0.8, 0.95), size_deg=30, name="backrim")
    L.bake_static()


# ============================================================================ S10 Shaw kneels, unfolds the bag

def S10(L, n):
    _deep(L, n, density=0.05)
    env, (lost, lp) = _bottom_set(L, n, shape=True)
    lost.rotation_euler = (0, 0, 0.0)
    d = C.diver("shaw", fins=SHAW_FINS, light_energy=1500, beam=False, beam_deg=40)
    r = d["root"]
    C.pose_upright_kneel(d, lean=0.45)
    r.rotation_euler.z = -math.pi / 2
    r.location = (-0.95, -0.15, 0.95)
    d["torch"].rotation_euler = (-0.6, 0, 0)
    # breathing / working motion
    for f in range(1, n + 1, 3):
        r.location.z = 0.95 + 0.02 * math.sin(f * 0.16)
        r.rotation_euler.x = math.pi / 2 - 0.45 - 0.05 * math.sin(f * 0.1)
        r.keyframe_insert("location", frame=f)
        r.keyframe_insert("rotation_euler", frame=f)
        for tag, ph in (("L", 0), ("R", 1.3)):
            sh = d[f"shoulder{tag}"]
            sh.rotation_euler = (-1.05 - 0.2 * math.sin(f * 0.12 + ph), 0, (-0.3 if tag == "L" else 0.3))
            sh.keyframe_insert("rotation_euler", frame=f)
    # body bag: dark cloth unfolding beside the shape
    bm_ = L.mat_principled("bag_m", (0.08, 0.085, 0.1), rough=0.35)
    bag = L.prim("plane", loc=(-0.35, -0.05, 0.06), size=1, name="bag")
    sub = bag.modifiers.new("sub", "SUBSURF")
    sub.subdivision_type = "SIMPLE"
    sub.levels = sub.render_levels = 4
    L.add_displace(bag, strength=0.05, scale=0.12, name="bagfold")
    L.assign(bag, bm_)
    C.key_scale(bag, [(1, (0.18, 0.35, 1)), (20, (0.2, 0.45, 1)), (int(n * 0.75), (0.55, 1.6, 1)), (n, (0.6, 1.7, 1))])
    C.key_loc(bag, [(1, (-0.55, -0.1, 0.1)), (int(n * 0.75), (-0.3, -0.05, 0.05)), (n, (-0.28, -0.05, 0.05))])
    # second light set on the floor
    lamp = L.prim("cyl", loc=(-0.2, -1.15, 0.07), rot=(math.pi / 2, 0, 0.9), vertices=12, radius=0.045, depth=0.22,
                  name="floorlamp")
    L.assign(lamp, L.mat_principled("lamp_m", (0.1, 0.1, 0.1), metal=0.5, rough=0.3))
    fl = L.spot((-0.15, -1.05, 0.1), (math.radians(85), 0, math.radians(-25)), energy=900, size_deg=50, blend=0.6,
                color=(1.0, 0.9, 0.75), name="floorspot")
    lens = L.prim("cyl", loc=(-0.13, -1.03, 0.08), rot=(math.pi / 2, 0, 0.9), vertices=12, radius=0.04, depth=0.01)
    L.assign(lens, C.emis("lamplens", (1, 0.95, 0.85), 25))
    # silt lifting at the knees
    knees = C.cloud((-0.8, -0.15, 0.12), (1.0, 1.0, 0.35), count=1400, radius=0.006, emit=0.06, shape="sphere",
                    seed=4)
    C.key_scale(knees, [(1, 0.6), (n, 1.4)])
    C.drift(knees, n, (0.02, 0, 0.12))
    puff, dens, _ = C.noisy_volume((-0.7, -0.1, 0.2), (1.6, 1.6, 0.7), density=2.0, scale=2.5, name="kneepuff")
    C.key_input(dens, [(1, 0.2), (n, 3.5)])
    amb = C.cloud((0, 0, 1.0), (5, 5, 2.4), count=1200, radius=0.005, emit=0.03, seed=9)
    C.drift(amb, n, (0.02, 0, 0.02))
    cam = C.camera(lens=35)
    keys = []
    ctr = Vector((-0.45, -0.05, 0.5))
    for f, ang in ((1, -0.18), (n, 0.17)):
        pos = ctr + Vector((math.sin(ang) * 3.6, -math.cos(ang) * 3.6, 0.35))
        keys.append((f, tuple(pos), tuple(ctr + Vector((-0.1, 0, -0.45)))))
    C.aim_cam(cam, n, keys, shake=0.01, rot_shake=0.002)
    C.cam_fill(cam, energy=30)
    C.rim_light((-0.95, -0.15, 0.9), (-1.2, 2.6, 2.2), energy=1100, color=(0.35, 0.85, 1.0), size_deg=35, name="rim1")
    C.rim_light((-0.95, -0.15, 0.9), (-2.4, -0.5, 1.4), energy=500, color=(0.3, 0.7, 0.9), size_deg=35, name="rim2")
    L.bake_static()


# ============================================================================ S11 macro breathing loop

def S11(L, n):
    """Two breathing loops (rings of gas): surface = sparse, fast; 270 m = packed tight, crawling."""
    C.world_black((0.003, 0.006, 0.01))
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0, -6.2, 0.9), (0, 0, -0.45)), (n, (0, -5.6, 0.85), (0, 0, -0.42))])
    L.dof(cam, distance=6.0, fstop=2.8)
    glass = C.rim_glass_mat("tube_glass", (0.55, 0.95, 1.0), strength=2.2, power=2.5, base=0.05)
    mouth_m = L.mat_principled("mouth", (0.06, 0.065, 0.07), rough=0.35)
    rings = []
    for k, (z, count, rad, rev, emit) in enumerate(((0.42, 70, 0.008, 1.6, 6.0), (-0.42, 1500, 0.0055, 0.12, 3.0))):
        piv = L.link(bpy.data.objects.new(f"loop{k}", None))
        piv.location = (0, 0, z)
        piv.rotation_euler = (0.38, 0, 0)
        tor = L.prim("torus", loc=(0, 0, 0), major_radius=0.85, minor_radius=0.13, major_segments=64,
                     minor_segments=16, name=f"tube{k}")
        L.assign(tor, glass)
        L.smooth(tor)
        tor.parent = piv
        mp = L.prim("cube", loc=(0, -0.85, 0), name=f"mouthpiece{k}")
        mp.scale = (0.2, 0.09, 0.11)
        L.bevel(mp, 0.03)
        L.assign(mp, mouth_m)
        mp.parent = piv
        gas = C.cloud((0, 0, 0), (0.85, 0.1, 0), count=count, radius=rad, color=C.CYAN, emit=emit, shape="torus",
                      seed=3 + k, name=f"gas{k}")
        gas.parent = piv
        gas.location = (0, 0, 0)
        gas.rotation_euler = (0, 0, 0)
        gas.keyframe_insert("rotation_euler", frame=1)
        gas.rotation_euler = (0, 0, rev * 2 * math.pi * n / 24 / 3.0)
        gas.keyframe_insert("rotation_euler", frame=n)
        L.linear_fcurves(gas)
        rings.append((piv, tor, gas))
    # laboured breaths (0.0 s and 1.8 s): the dense loop squeezes
    b2 = int(1.8 * 24)
    for o in (rings[1][1], rings[1][2]):
        C.key_scale(o, [(1, 1.0), (12, (1.0, 1.0, 1.25)), (28, 1.0), (b2, 1.0), (b2 + 12, (1.0, 1.0, 1.25)), (n, 1.0)])
    C.curve([(-3, 0.5, 0.0), (3, 0.5, 0.0)], thickness=0.004, mat=C.emis("div", (0.6, 0.7, 0.75), 1.2), name="divider")
    L.area((0, 1.5, 2.5), (math.radians(-130), 0, 0), energy=120, size=5, color=(0.6, 0.9, 1.0))
    L.area((0, 1.5, -2.5), (math.radians(-50), 0, 0), energy=120, size=5, color=(0.6, 0.9, 1.0))
    L.area((0, -4, 0), (math.radians(90), 0, 0), energy=40, size=6, color=(0.8, 0.9, 1.0))
    bg = L.prim("plane", loc=(0, 3.5, -0.5), rot=(math.pi / 2, 0, 0), size=14, name="backdrop")
    L.assign(bg, L.mat_principled("bd", (0.01, 0.02, 0.03), rough=0.9))
    L.bake_static()


# ============================================================================ S12 snag: lines, pull, silt swallows the torch

def S12(L, n):
    _deep(L, n, density=0.05, center=(0, 0, 0), size=(14, 14, 8))
    C.floor(size=(14, 14), center=(0, 0, -0.55), strength=0.25, name="snagfloor")
    rig = L.link(bpy.data.objects.new("armrig", None))
    suit = L.mat_principled("sleeve", (0.03, 0.03, 0.035), rough=0.6)
    metal = L.mat_principled("canister", (0.55, 0.57, 0.6), rough=0.25, metal=1.0)
    arm = L.prim("cyl", loc=(-0.15, 0, 0), rot=(0, math.pi / 2, 0), vertices=24, radius=0.06, depth=0.7, name="forearm")
    L.assign(arm, suit)
    L.smooth(arm)
    arm.parent = rig
    glove = L.prim("sphere", loc=(0.24, 0, -0.01), segments=16, ring_count=10, name="glove")
    glove.scale = (0.08, 0.06, 0.05)
    L.assign(glove, suit)
    L.smooth(glove)
    glove.parent = rig
    can = L.prim("cyl", loc=(-0.05, 0, 0.1), rot=(0, math.pi / 2, 0), vertices=24, radius=0.045, depth=0.28,
                 name="canister")
    L.assign(can, metal)
    L.smooth(can)
    can.parent = rig
    head = L.prim("cyl", loc=(0.12, 0, 0.1), rot=(0, math.pi / 2, 0), vertices=24, radius=0.05, depth=0.06, name="lamphead")
    L.assign(head, metal)
    head.parent = rig
    lens = L.prim("cyl", loc=(0.153, 0, 0.1), rot=(0, math.pi / 2, 0), vertices=24, radius=0.042, depth=0.006,
                  name="lens")
    L.assign(lens, C.emis("lensm", (1, 0.95, 0.85), 40))
    lens.parent = rig
    torch = L.spot((0.16, 0, 0.1), (0, math.radians(100), 0), energy=2600, size_deg=24, blend=0.4, color=C.TORCH,
                   name="torch", radius=0.02)
    torch.parent = rig
    cone, sock = C.beam_cone(torch, length=3.0, strength=0.25, name="snagbeam")
    # lines looping around the arm + canister and trailing off taut
    lm = L.mat_principled("snagline", (0.95, 0.93, 0.85), rough=0.4, emit=(0.8, 0.8, 0.75), emit_strength=0.8)
    h1 = C.curve(C.helix((-0.12, 0, 0.04), (1, 0, 0), 0.1, 2.3, 0.45, phase=0.3, wobble=0.25, seed=2),
                 thickness=0.0045, mat=lm, name="loop1", smooth_pts=True)
    h2 = C.curve(C.helix((-0.02, 0, 0.06), (1, 0.15, 0.1), 0.13, 1.4, 0.35, phase=2.0, wobble=0.3, seed=5),
                 thickness=0.0045, mat=lm, name="loop2", smooth_pts=True)
    for h in (h1, h2):
        h.parent = rig
    tail1 = C.curve([(0.25, 0, 0.0), (0.9, 0.3, 0.6), (3.0, 1.2, 1.9)], thickness=0.0045, mat=lm, name="tail1")
    tail2 = C.curve([(-0.45, 0, 0.0), (-1.2, 0.4, -0.3), (-3.5, 1.0, -0.6)], thickness=0.0045, mat=lm, name="tail2")
    rig.location = (0, 0, 0.45)
    rig.rotation_euler = (0.0, -0.18, 0.12)
    # pulls: sharp jerks, increasingly frantic
    pulls = [(1, 0.0), (18, 0.0), (22, 1.0), (30, 0.2), (44, 0.2), (48, 1.0), (54, 0.1), (66, 0.1), (69, 1.0),
             (74, 0.3), (82, 1.0), (86, 0.2), (94, 1.0), (98, 0.3), (106, 1.0), (n, 0.5)]
    for f, a in pulls:
        if f > n:
            continue
        rig.location = (-0.08 * a, 0.02 * a, 0.45 + 0.03 * a)
        rig.rotation_euler = (0.08 * a, -0.18 - 0.12 * a, 0.12 + 0.1 * a)
        rig.keyframe_insert("location", frame=f)
        rig.keyframe_insert("rotation_euler", frame=f)
    # torch flicker, then swallowed
    L.flicker(torch, n, base=2600, seed=4, depth=0.35, rate=0.9, blackouts=((88, 90), (101, 102)))
    C.key_input(sock, [(1, 0.25), (60, 0.2), (n, 0.05)])
    # silt explodes from the floor and engulfs the beam
    plume, dens, nz = C.noisy_volume((0.9, 0.2, 0.0), (3.2, 2.6, 2.2), color=(0.55, 0.48, 0.38), density=1.0,
                                     scale=1.6, name="plume")
    C.key_input(dens, [(1, 0.0), (20, 0.1), (50, 2.5), (85, 7.0), (n, 12.0)])
    C.key_scale(plume, [(1, 0.5), (50, 0.9), (n, 1.3)])
    # QC fix (2026-11-27): the burst used to expand around the lens, so near particles read as big confetti squares.
    # Finer particles, kept >= ~0.5 m from the camera; the noisy volume above does the actual silt-out.
    burst = C.cloud((0.5, 0.6, -0.3), (2.4, 1.7, 1.2), count=7000, radius=0.002, emit=0.08, shape="sphere", seed=8)
    C.key_scale(burst, [(1, 0.25), (22, 0.4), (60, 0.95), (n, 1.25)])
    C.drift(burst, n, (0.1, 0.05, 0.25))
    cam = C.camera(lens=50)
    # micro-pushes on each sentence start (~0, 1.6 s, 3.1 s)
    C.aim_cam(cam, n, [(1, (0.15, -1.55, 0.62), (0.05, 0, 0.42)), (36, (0.13, -1.45, 0.62), (0.05, 0, 0.42)),
                       (40, (0.12, -1.3, 0.6), (0.06, 0, 0.42)), (72, (0.11, -1.25, 0.6), (0.07, 0, 0.42)),
                       (76, (0.1, -1.1, 0.58), (0.08, 0, 0.42)), (n, (0.1, -1.05, 0.58), (0.1, 0, 0.42))],
              shake=0.012, rot_shake=0.01, rate=1.4, shake_keys=[(1, 0.4), (n, 2.2)])
    C.cam_fill(cam, energy=25)
    C.rim_light((0, 0, 0.5), (-0.6, 2.0, 1.6), energy=600, color=(0.35, 0.85, 1.0), size_deg=40, name="armrim")
    L.bake_static()


# ============================================================================ S14 Shirley searches deeper

def S14(L, n):
    C.world_black((0.0, 0.003, 0.008))
    C.render_quality(vol_end=30)
    C.water(center=(0, 0, -4), size=(30, 30, 20), color=(0.25, 0.5, 0.65), density=0.045, absorption=(0.1, 0.25, 0.2))
    C.shaft(6, -16, lambda z, a: 9 + 2.0 * math.sin(a * 3 + 0.5) + 0.8 * math.sin(a * 7), step=1.2, ring=40, seed=5,
            rough=0.3, name="chamberwall", disp=(1.0, 0.25),
            mat=C.rock_mat("cwall", (0.02, 0.025, 0.03), (0.18, 0.2, 0.22)))
    lx = 0.35
    C.line([(lx, 0, 6), (lx, 0, -16)], thickness=0.01, emit=0.9, name="shotline")
    # rendezvous marker at 220 m: orange tag + strobe
    tag = L.prim("cube", loc=(lx + 0.05, 0, 0.0), name="rvtag")
    tag.scale = (0.08, 0.02, 0.12)
    L.assign(tag, L.mat_principled("rvt", (1, 0.45, 0.1), emit=(1, 0.4, 0.05), emit_strength=3))
    strobe = L.point((lx + 0.08, 0, 0.15), energy=0, color=(1, 0.5, 0.2), radius=0.03, name="strobe")
    C.key_energy(strobe, [(f, 30 if (f // 6) % 4 == 0 else 0) for f in range(1, n + 1, 3)])
    C.constant_keys(strobe.data)
    d = C.diver("shirley", fins=SHIRLEY_FINS, light_energy=3000, beam_len=9, beam_strength=0.45, beam_deg=20)
    r = d["root"]
    path = []
    for f in range(1, n + 1, 2):
        t = (f - 1) / (n - 1)
        z = 0.3 - 5.5 * t
        r.location = (0.0, 0.0, z)
        sweep = 0.75 * math.sin(t * 2 * math.pi * 1.1)
        r.rotation_euler = (-1.0, 0.0, sweep)
        r.keyframe_insert("location", frame=f)
        r.keyframe_insert("rotation_euler", frame=f)
        path.append((f, z))
    L.anim_swim(d, n, kick_rate=0.6, amp=0.22)
    dust = C.cloud((0, 0, -3), (7, 7, 10), count=3000, radius=0.008, emit=0.05, seed=17)
    C.drift(dust, n, (0.05, 0.02, 0.06))
    cam = C.camera(lens=28)
    keys = []
    for f, z in path[::3] + [path[-1]]:
        t = (f - 1) / (n - 1)
        keys.append((f, (0.35, -1.35, z + 1.55), (0.0, 0.5, z - 0.9), 8.0 * C.sm(t)))
    C.aim_cam(cam, n, keys, shake=0.015, rot_shake=0.004, fn=lambda x: x)
    L.dof(cam, target=d["torso"], fstop=1.2)
    C.cam_fill(cam, energy=40, color=(0.4, 0.6, 0.9))
    rl = L.spot((0, 2.2, 1.8), (0, 0, 0), energy=900, size_deg=40, blend=0.7, color=(0.35, 0.8, 1.0), name="srim")
    rl.parent = r
    con = rl.constraints.new("TRACK_TO")
    con.target = d["torso"]
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    L.bake_static()


# ============================================================================ S15 helmet-cam UI

def S15(L, n):
    _deep(L, n, density=0.08, center=(0, 0, 0), size=(14, 14, 8), color=(0.45, 0.8, 0.55))
    C.floor(size=(14, 14), center=(0, 0, -0.9), strength=0.3, name="hcfloor")
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (0, -1.6, 0.3), (0.1, 2, -0.2)), (n, (0, -1.6, 0.3), (0.1, 2, -0.25))], shake=0.01,
              rot_shake=0.006, rate=1.2, lens_keys=[(1, 24), (n, 30)])
    sp = L.spot((0.15, 0.1, 0), (0.05, 0, 0), energy=1800, size_deg=26, blend=0.5, color=(0.75, 1.0, 0.8), name="hct")
    sp.parent = cam
    L.flicker(sp, n, base=1800, seed=9, depth=0.25, rate=0.8)
    plume, dens, nz = C.noisy_volume((0, 1.6, -0.2), (4, 3.5, 2.5), color=(0.6, 0.7, 0.5), density=2.5, scale=1.4,
                                     name="hcplume")
    C.key_scale(plume, [(1, 1.0), (n, 1.15)])
    s = C.cloud((0, 0.8, 0), (3, 3, 2), count=2000, radius=0.006, emit=0.08, color=(0.7, 1, 0.75), seed=3)
    C.drift(s, n, (0.08, -0.05, 0.05))
    # viewfinder brackets, centre cross and blinking REC dot, parented to camera (z = -0.5 in front)
    ui = C.emis("ui", (0.85, 1.0, 0.85), 3.0)
    zf = -0.5
    hw, hh = 0.19, 0.33  # half frame at 24mm, d=0.5 is ~0.21 x 0.375
    arm = 0.05
    def seg(a, b, name="ui"):
        o = C.curve([a, b], thickness=0.0016, mat=ui, name=name)
        o.parent = cam
        return o
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * hw, sy * (hh * 0.62 if sy < 0 else hh * 0.78)
            seg((cx, cy, zf), (cx - sx * arm, cy, zf))
            seg((cx, cy, zf), (cx, cy - sy * arm, zf))
    seg((-0.015, 0.06, zf), (0.015, 0.06, zf))
    seg((0, 0.045, zf), (0, 0.075, zf))
    dot = L.prim("sphere", loc=(-0.15, hh * 0.78 - 0.035, zf), segments=12, ring_count=6, radius=0.009, name="recdot")
    L.assign(dot, C.emis("recm", (1, 0.1, 0.08), 8))
    dot.parent = cam
    for f in range(1, n + 1, 12):
        dot.hide_render = (f // 12) % 2 == 1
        dot.keyframe_insert("hide_render", frame=f)
    C.constant_keys(dot)
    # battery + timecode-ish ticks (stylised, no real data)
    for i in range(4):
        b = L.prim("cube", loc=(0.12 + i * 0.012, hh * 0.78 - 0.035, zf), name="bat")
        b.scale = (0.004, 0.008, 0.001)
        L.assign(b, ui)
        b.parent = cam
    # static / scanlines plate
    pl = L.prim("plane", loc=(0, 0, zf + 0.01), size=1, name="static")
    pl.scale = (0.45, 0.8, 1)
    pl.parent = cam
    m, nn, ll = L._mat("static_m")
    for nd in list(nn):
        if nd.type == "BSDF_PRINCIPLED":
            nn.remove(nd)
    tc = nn.new("ShaderNodeTexCoord")
    nz2 = nn.new("ShaderNodeTexNoise")
    nz2.noise_dimensions = "4D"
    nz2.inputs["Scale"].default_value = 160
    ll.new(tc.outputs["Object"], nz2.inputs["Vector"])
    C.key_input(nz2.inputs["W"], [(1, 0.0), (n, 40.0)])
    wave = nn.new("ShaderNodeTexWave")
    wave.inputs["Scale"].default_value = 60
    wave.wave_profile = "SAW"
    wave.bands_direction = "Y" if hasattr(wave, "bands_direction") else wave.bands_direction
    ll.new(tc.outputs["Object"], wave.inputs["Vector"])
    mx = nn.new("ShaderNodeMath")
    mx.operation = "MULTIPLY"
    ll.new(nz2.outputs["Fac"], mx.inputs[0])
    ll.new(wave.outputs["Fac"], mx.inputs[1])
    mx2 = nn.new("ShaderNodeMath")
    mx2.operation = "MULTIPLY"
    mx2.inputs[1].default_value = 0.25
    ll.new(mx.outputs[0], mx2.inputs[0])
    em = nn.new("ShaderNodeEmission")
    em.inputs[0].default_value = (0.7, 1, 0.75, 1)
    ll.new(mx2.outputs[0], em.inputs[1])
    tr = nn.new("ShaderNodeBsdfTransparent")
    ad = nn.new("ShaderNodeAddShader")
    ll.new(tr.outputs[0], ad.inputs[0])
    ll.new(em.outputs[0], ad.inputs[1])
    ll.new(ad.outputs[0], nn["Material Output"].inputs["Surface"])
    C._blended(m)
    L.assign(pl, m)
    L.bake_static()


# ============================================================================ S16 case report page (3D)

def S16(L, n):
    C.world_black((0.01, 0.012, 0.016))
    paper = L.mat_noise_surface("paper", (0.78, 0.8, 0.82), (0.88, 0.9, 0.92), scale=40, bump=0.05, voronoi=False,
                                rough=0.8)
    page = L.link(bpy.data.objects.new("page", None))
    sheet = L.prim("plane", loc=(0, 0, 0), rot=(math.pi / 2, 0, 0), size=1, name="sheet")
    sheet.scale = (2.1, 2.8, 1)
    L.assign(sheet, paper)
    sheet.parent = page
    ink = L.mat_principled("ink", (0.03, 0.035, 0.05), rough=0.6)
    grey = L.mat_principled("ink2", (0.35, 0.37, 0.4), rough=0.7)
    t1 = C.text("CASE REPORT", (-0.9, -0.01, 1.15), size=0.16, font=C.FONT_SERIF, align="LEFT", mat=ink, name="h1")
    t1.parent = page
    t2 = C.text("(2007)  Deep rebreather diving fatality", (-0.9, -0.01, 0.95), size=0.07, font=C.FONT_SERIF,
                align="LEFT", mat=grey, name="h2")
    t2.parent = page
    rnd = random.Random(3)
    z = 0.75
    hi_z = None
    for i in range(16):
        if i == 8:
            hi_z = z
            z -= 0.3
            continue
        w = rnd.uniform(1.3, 1.8) if i % 5 != 4 else rnd.uniform(0.6, 1.0)
        b = L.prim("cube", loc=(-0.9 + w / 2, -0.005, z), name="txtbar")
        b.scale = (w / 2, 0.002, 0.018)
        L.assign(b, grey)
        b.parent = page
        z -= 0.1
    hl = L.prim("cube", loc=(-0.95, -0.006, hi_z), name="highlight")
    hl.scale = (0.0, 0.002, 0.075)
    L.assign(hl, L.mat_principled("hl", (1.0, 0.85, 0.1), emit=(1, 0.8, 0.1), emit_strength=0.6))
    hl.parent = page
    # grow highlight from left edge
    for f, w in ((1, 0.0), (int(n * 0.35), 0.0), (int(n * 0.7), 1.65), (n, 1.65)):
        hl.scale = (w / 2, 0.002, 0.075)
        hl.location = (-0.95 + w / 2, -0.006, hi_z)
        hl.keyframe_insert("scale", frame=f)
        hl.keyframe_insert("location", frame=f)
    ht = C.text("EXTREME HYPERCAPNIA", (-0.9, -0.012, hi_z), size=0.12, font=C.FONT_SANS_B, align="LEFT", mat=ink,
                name="hline")
    ht.parent = page
    ht2 = C.text("\u2192 UNCONSCIOUSNESS", (-0.9, -0.012, hi_z - 0.17), size=0.1, font=C.FONT_SANS_B, align="LEFT",
                 mat=ink, name="hline2")
    ht2.parent = page
    # page slides in with a small 3D tilt and settles flat
    C.key_loc(page, [(1, (0.2, 0, -2.6)), (16, (0, 0, 0)), (n, (0, 0, 0.05))])
    page.rotation_euler = (0.35, 0, -0.12)
    page.keyframe_insert("rotation_euler", frame=1)
    page.rotation_euler = (0, 0, -0.02)
    page.keyframe_insert("rotation_euler", frame=18)
    L.area((-1.5, -3, 2.5), (math.radians(55), 0, math.radians(-25)), energy=900, size=3, color=(0.85, 0.92, 1.0))
    L.area((2, -2, -1), (math.radians(110), 0, math.radians(40)), energy=150, size=3, color=(0.6, 0.75, 1.0))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.2, -5.2, 0.4), (0.0, 0, 0.3)), (16, (0.1, -4.8, 0.4), (0.0, 0, 0.3)),
                       (n, (-0.05, -3.1, hi_z - 0.05), (-0.05, 0, hi_z - 0.12))], shake=0.004, rot_shake=0.001)
    L.bake_static()


# ============================================================================ S17 / S18 shaft looking up to daylight

def _upshaft(L, n, density=0.04, sun_e=6.0):
    """Looking up the Boesmansgat throat: rock tube lit cyan from above, bright surface disc, light shafts."""
    C.world_black((0.0, 0.01, 0.015))
    C.render_quality(vol_end=40, vol_samples=64)
    C.water(center=(0, 0, -15), size=(14, 14, 32), color=(0.4, 0.75, 0.8), density=density, absorption=(0.06, 0.2, 0.18))
    C.shaft(1.0, -34, lambda z, a: 2.6 + 0.6 * math.sin(a * 2 + 0.4) + 0.3 * math.sin(a * 5 + z * 0.2) +
            (0.06 * (z + 34) if z < -14 else 1.2), step=0.8, ring=36, seed=9, rough=0.25, name="upshaft",
            disp=(0.6, 0.18), mat=C.rock_mat("uprock", (0.03, 0.06, 0.065), (0.3, 0.42, 0.42), scale=1.3))
    C.sun_from((0.18, 0.12, 1.0), energy=sun_e, color=(0.8, 0.95, 1.0), angle=2)
    # surface: smooth bright disc with gentle ripple (no speckle)
    surf = L.prim("cyl", loc=(0, 0, 0.6), vertices=64, radius=6, depth=0.02, name="surface")
    m, nn, ll = L._mat("surface_m")
    for nd in list(nn):
        if nd.type == "BSDF_PRINCIPLED":
            nn.remove(nd)
    tc = nn.new("ShaderNodeTexCoord")
    vr = nn.new("ShaderNodeTexVoronoi")
    vr.inputs["Scale"].default_value = 0.9
    mp = nn.new("ShaderNodeMapping")
    ll.new(tc.outputs["Object"], mp.inputs["Vector"])
    ll.new(mp.outputs[0], vr.inputs["Vector"])
    C.key_input(mp.inputs["Location"], [(1, (0, 0, 0)), (n, (0.6, 0.4, 0))])
    ramp = nn.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
    ramp.color_ramp.elements[1].color = (0.55, 0.85, 0.95, 1)
    ramp.color_ramp.elements[1].position = 0.35
    ll.new(vr.outputs["Distance"], ramp.inputs["Fac"])
    em = nn.new("ShaderNodeEmission")
    em.inputs[1].default_value = 9.0
    ll.new(ramp.outputs[0], em.inputs[0])
    ll.new(em.outputs[0], nn["Material Output"].inputs["Surface"])
    L.assign(surf, m)
    # cyan bounce down the shaft so the rock tube reads
    for z, e in ((-2, 600), (-7, 450), (-12, 300)):
        L.point((0.3, 0.2, z), energy=e, color=(0.45, 0.85, 0.95), radius=1.0, name="bounce")
    # fake god rays from the surface
    rnd = random.Random(4)
    for i in range(7):
        sp = L.spot((rnd.uniform(-1.6, 1.6), rnd.uniform(-1.6, 1.6), 0.4), (rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12), 0),
                    energy=0, size_deg=rnd.uniform(5, 9), name="ray")
        cone, sock = C.beam_cone(sp, length=rnd.uniform(9, 15), color=(0.75, 0.95, 1.0), strength=rnd.uniform(0.25, 0.45),
                                 name="rayc")
        C.key_input(sock, [(1, sock.default_value), (n // 2, sock.default_value * rnd.uniform(0.5, 1.4)), (n, sock.default_value)])
    return surf


def S17(L, n):
    _upshaft(L, n, density=0.035, sun_e=5)
    top = Vector((0.2, 0.3, 0.5))
    lm = L.mat_principled("haul", (0.95, 0.95, 0.9), rough=0.4, emit=(0.9, 0.9, 0.85), emit_strength=1.0)
    tagm = L.mat_principled("haultag", (1.0, 0.6, 0.15), emit=(1, 0.55, 0.1), emit_strength=2.0)
    for i, b in enumerate(((-0.9, -0.6, -34), (0.7, -0.9, -34), (1.4, 0.8, -34))):
        pts = [tuple(Vector(b)), tuple(top + Vector((0.05 * i, 0, 0)))]
        C.curve(pts, thickness=0.012, mat=lm, name=f"haul{i}")
        tags = []
        for k in range(14):
            t = L.prim("cube", loc=(0, 0, 0), name="ht")
            t.scale = (0.03, 0.03, 0.06)
            L.assign(t, tagm if k % 3 == 0 else lm)
            tags.append(t)
        for k, t in enumerate(tags):
            base = k / 14.0
            prog = 0.0
            for f in range(1, n + 1, 2):
                cyc = (f + i * 7) % 22
                if cyc < 12:
                    prog += 0.0065
                tt = (base + prog) % 1.0
                t.location = C.along(pts, 0.45 + tt * 0.55)
                t.keyframe_insert("location", frame=f)
    p = C.cloud((0, 0, -16), (5, 5, 10), count=2400, radius=0.006, emit=0.1, seed=5)
    C.drift(p, n, (0.02, 0.01, 0.12))
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (1.1, -1.3, -19.5), (0.2, 0.3, 0)), (n, (1.0, -1.1, -18.6), (0.2, 0.3, 0))],
              shake=0.02, rot_shake=0.003)
    L.bake_static()


def S18(L, n):
    _upshaft(L, n, density=0.05, sun_e=7)
    sil = L.mat_principled("sil", (0.01, 0.012, 0.014), rough=0.8)
    cam_p = Vector((1.6, -1.8, -15.0))
    tgt = Vector((0.0, 0.3, 0.0))
    mid0 = cam_p.lerp(tgt, 0.42)
    grp = L.link(bpy.data.objects.new("pair", None))
    for i, (x, rz) in enumerate(((-0.17, 0.18), (0.17, -0.12))):
        o = L.prim("sphere", loc=(x, 0, 0), segments=20, ring_count=12, name=f"shape{i}")
        o.scale = (0.2, 0.17, 0.85)
        o.rotation_euler = (0.1, rz, 0)
        L.assign(o, sil)
        L.smooth(o)
        o.parent = grp
    lm = L.mat_principled("loopm", (0.95, 0.95, 0.9), emit=(0.95, 0.95, 0.9), emit_strength=2.0)
    for z, rr in ((0.25, 0.42), (-0.3, 0.4)):
        loop = L.prim("torus", loc=(0, 0, z), major_radius=rr, minor_radius=0.012, name="loop")
        loop.scale = (1, 0.6, 1)
        L.assign(loop, lm)
        loop.parent = grp
    haul = C.curve([(0, 0, 0.85), (0.1, 0.15, 14)], thickness=0.01, mat=lm, name="haulline")
    haul.parent = grp
    C.key_loc(grp, [(1, tuple(mid0)), (n, tuple(mid0 + Vector((0, 0, 1.0))))])
    L.linear_fcurves(grp)
    grp.rotation_euler = (0.25, -0.35, 0)
    grp.keyframe_insert("rotation_euler", frame=1)
    grp.rotation_euler = (0.25, -0.35, 0.3)
    grp.keyframe_insert("rotation_euler", frame=n)
    p = C.cloud((0, 0, -10), (5, 5, 8), count=2000, radius=0.006, emit=0.1, seed=7)
    C.drift(p, n, (0.02, 0.0, 0.08))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, tuple(cam_p), tuple(tgt)), (n, tuple(cam_p + Vector((0, 0, 0.3))), tuple(tgt))],
              shake=0.012, rot_shake=0.002)
    L.bake_static()
