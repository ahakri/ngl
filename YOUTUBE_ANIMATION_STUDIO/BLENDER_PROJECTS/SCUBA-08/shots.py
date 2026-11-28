"""SCUBA-08 — Shackleton's Endurance (sank 1915, found 5 March 2022, 3,008 m down in the Weddell Sea).
One builder per shot: def Sxx(L, n). New builders appended to PIPELINE/blender/lib_scuba.py: mat_ship_wood, anemone,
stern_name, barquentine, auv_torpedo, rov_drone, ice_floes. lib_cave supplies camera keys, clouds, skies; lib_murder
the snow material and small boats. Shackleton is not depicted; the crew are tiny faceless figures (S04). The drone
lamps never touch the wreck. Ship, icebreaker and robots are generic (no logos or livery). The star sits BELOW the
name, as in the fact-check."""
import sys, os, math, random, importlib
import bpy
from mathutils import Vector, noise

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_scuba as S
import lib_cave as C
import lib_murder as M
importlib.reload(S)
importlib.reload(C)

COOL = (0.82, 0.93, 1.0)
WZ = 3.0                                   # wreck root height above the seabed (keel sunk 0.4 m)
S01_P, S01_T = (-31.5, 2.2, 6.0), (-22.0, 0.0, 4.75)
S01_L = ((-22.0, 1.3, 5.4), (-22.0, -0.2, 4.6))       # lamp aims at S01 frame 1 (= S14 last frame)


def _track(obj, pos, name="tgt"):
    t = bpy.data.objects.new(name, None)
    C.L.link(t)
    t.location = pos
    con = obj.constraints.new("TRACK_TO")
    con.target = t
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    return t


def _finish(L):
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "AREA":
            o.data.volume_factor = 0.0
    L.bake_static()


def _snow(n, center, size, count=500, vel=(0.02, 0.0, -0.03), radius=0.005, seed=4, emit=0.3):
    s = C.cloud(center, size, count=count, radius=radius, color=(0.85, 0.9, 0.95), emit=emit, seed=seed, name=f"msnow{seed}")
    C.drift(s, n, vel)
    return s


def _lamp(L, pos, aim_keys, energy=3000, deg=30, cone=9.0, strength=0.5, name="lamp"):
    """Drone lamp: spot tracking a keyed target + fake cone. aim_keys [(frame, xyz)]."""
    sp = L.spot(pos, (0, 0, 0), energy=energy, size_deg=deg, blend=0.45, color=COOL, name=name, radius=0.05)
    tg = _track(sp, aim_keys[0][1], name + "_tgt")
    C.key_loc(tg, aim_keys)
    _, sock = C.beam_cone(sp, length=cone, color=COOL, strength=strength, name=name + "_beam")
    return sp, sock


def _deep(L, n, ship=True, anemones=34, density=0.012):
    """Black water 3 km down: grey seabed, thin haze, the wreck upright on the bottom."""
    S.setup(vol_end=70)
    L.set_world(color=(0.0, 0.002, 0.004), strength=1.0)
    L.seabed(size=160, mat=L.mat_noise_surface("ooze", (0.07, 0.075, 0.08), (0.2, 0.21, 0.22), scale=3, bump=0.3, voronoi=False),
             strength=0.5)
    S.world_volume(color=(0.3, 0.5, 0.6), density=density, anisotropy=0.5, center=(0, 0, 10), size=(150, 150, 40))
    P = None
    if ship:
        P = S.barquentine("end", wreck=True, silt=0.35, anemones=anemones)
        P["root"].location = (0, 0, WZ)
        P["root"].rotation_euler = (0.035, 0, 0)
    return P


def _stern(L, n, cam_keys, aim0, aim1, shake_keys=None):
    _deep(L, n)
    _lamp(L, (-30.0, 4.6, 7.6), [(1, aim0[0]), (n, aim1[0])], energy=3200, deg=30, name="lampA")
    _lamp(L, (-30.6, 3.0, 4.0), [(1, aim0[1]), (n, aim1[1])], energy=2400, deg=34, name="lampB")
    _snow(n, (-26.0, -3.5, 5.5), (5, 3, 6), count=260, seed=4)
    _snow(n, (-25.0, 5.0, 6.0), (4, 3, 6), count=220, seed=5)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, cam_keys, shake=0.05, rot_shake=0.003, rate=0.5, seed=2, shake_keys=shake_keys, fn=C.sm)
    C.cam_fill(cam, energy=140, color=(0.4, 0.6, 0.9))
    _finish(L)


def S01(L, n):
    _stern(L, n, [(1, S01_P, S01_T), (n, (-29.4, 0.4, 5.7), (-22.0, 0.0, 4.9))], S01_L,
           ((-22.0, -0.9, 5.5), (-22.0, 0.8, 4.7)), shake_keys=[(1, 0.0), (14, 1.0), (n, 1.0)])


def S14(L, n):
    _stern(L, n, [(1, (-34.0, -3.5, 8.0), (-22.0, 0.0, 4.4)), (n, S01_P, S01_T)], ((-22.0, -1.6, 4.2), (-22.0, 1.8, 5.8)),
           S01_L, shake_keys=[(1, 1.0), (n - 14, 1.0), (n, 0.0)])


def S02(L, n):
    """Map backdrop: slow drift along the dark hull, soft."""
    _deep(L, n)
    _lamp(L, (-14.0, -13.0, 11.0), [(1, (-8.0, -3.8, 5.0)), (n, (2.0, -3.8, 5.0))], energy=5000, deg=36, cone=12, name="lampA")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (-12.0, -16.0, 7.5), (-6.0, 0.0, 5.0)), (n, (-5.0, -16.0, 7.5), (1.0, 0.0, 5.0))], fn=lambda x: x)
    C.cam_fill(cam, energy=250, color=(0.4, 0.6, 0.9))
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 4.0
    cam.data.dof.aperture_fstop = 0.6
    _finish(L)


def S05(L, n):
    """Timeline backdrop: empty seabed, marine snow, a lamp pool drifting over nothing."""
    _deep(L, n, ship=False)
    _lamp(L, (0.0, -6.0, 9.0), [(1, (-3.0, 6.0, 0.0)), (n, (3.0, 9.0, 0.0))], energy=4000, deg=40, cone=10, name="lampA")
    _snow(n, (0.0, 6.0, 4.0), (10, 6, 7), count=500, seed=6)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.0, -9.0, 5.0), (0.0, 8.0, 0.5)), (n, (0.0, -7.5, 4.6), (0.0, 8.0, 0.5))], fn=C.sm)
    C.cam_fill(cam, energy=120, color=(0.4, 0.6, 0.9))
    _finish(L)


def S09(L, n):
    """Mid-point turn: the bow resolves out of the black in the drone lamps; the lamps stop and hold."""
    _deep(L, n)
    f_hold = int(n * 0.6)
    _lamp(L, (35.0, 4.5, 8.5), [(1, (27.0, 3.0, 3.0)), (f_hold, (20.5, 0.4, 5.6)), (n, (20.5, 0.4, 5.6))], energy=5200, deg=32,
          cone=10, name="lampA")
    _lamp(L, (35.5, 1.0, 4.5), [(1, (28.0, -3.0, 2.0)), (f_hold, (21.0, -0.8, 4.4)), (n, (21.0, -0.8, 4.4))], energy=4200, deg=34,
          cone=10, name="lampB")
    _snow(n, (29.0, -4.5, 5.5), (5, 3, 6), count=240, seed=7)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (40.0, 4.0, 7.0), (21.0, 0.0, 4.6)), (f_hold, (34.5, 2.8, 6.4), (21.0, 0.0, 4.6)),
                       (n, (34.2, 2.7, 6.4), (21.0, 0.0, 4.6))], shake=0.04, rot_shake=0.003, fn=C.sm)
    C.cam_fill(cam, energy=160, color=(0.4, 0.6, 0.9))
    _finish(L)


def _wide(L, n, cam_keys, dim=None):
    _deep(L, n, anemones=20)
    xs = [(1, 17.0), (n, -14.0)]
    for k, (yy, zz, e) in enumerate(((-12.0, 16.0, 45000), (-10.0, 11.0, 30000))):
        sp, sock = _lamp(L, (17.0, yy, zz), [(1, (15.0 - 3 * k, -1.0, 5.0)), (n, (-14.0 - 3 * k, -1.0, 5.0))], energy=e, deg=58,
                         cone=13, strength=0.3, name=f"lamp{k}")
        C.key_loc(sp, [(f, (x + 2.0 - 3 * k, yy, zz)) for f, x in xs])
        if dim:
            C.key_energy(sp, [(f, e * v) for f, v in dim])
            C.key_input(sock, [(f, 0.35 * v) for f, v in dim])
    for k, (pos, e) in enumerate((((32.0, -42.0, 38.0), 90000), ((-30.0, -36.0, 30.0), 60000))):   # blue fill: silhouette reads
        fl = L.spot(pos, (0, 0, 0), energy=e, size_deg=75, blend=0.9, color=(0.3, 0.5, 1.0), name=f"fill{k}", radius=2.0)
        _track(fl, (0, 0, 4), f"fill{k}_tgt")
        fl.data.volume_factor = 0.0
    _snow(n, (30.0, -6.0, 8.0), (8, 5, 9), count=300, seed=8)
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, cam_keys, shake=0.05, rot_shake=0.002, rate=0.4, seed=3, fn=C.sm)
    cf = C.cam_fill(cam, energy=2500, color=(0.35, 0.55, 0.95))
    cf.data.volume_factor = 0.0
    _finish(L)


def S11(L, n):
    """Wide reveal: the whole ship upright on the seabed, lamp light travelling along the hull."""
    _wide(L, n, [(1, (41.0, -17.0, 10.0), (4.0, 0.0, 6.5)), (n, (36.0, -23.0, 9.0), (2.0, 0.0, 6.5))])


def S13(L, n):
    """The lamps pull away and up; the ship sinks back into the dark, untouched."""
    _wide(L, n, [(1, (36.0, -23.0, 9.0), (2.0, 0.0, 7.5)), (n, (52.0, -34.0, 21.0), (2.0, 0.0, 9.0))],
          dim=[(1, 1.0), (int(n * 0.35), 0.8), (n, 0.07)])


def S12(L, n):
    """Macro: sound, sharp-edged rail and planks with anemones clinging to them."""
    S.setup(vol_end=12)
    L.set_world(color=(0.0, 0.002, 0.004), strength=1.0)
    wood = S.mat_ship_wood("plank", c1=(0.05, 0.035, 0.02), c2=(0.28, 0.2, 0.12), seam=10.0)
    for k in range(9):
        p = L.prim("cube", loc=(0, -0.6 + k * 0.2, -0.03), name="plank")
        p.scale = (3.0, 0.092, 0.03)
        L.bevel(p, 0.006)
        L.assign(p, wood)
    bw = L.prim("cube", loc=(0, 1.15, 0.4), name="bulwark")
    bw.scale = (3.0, 0.05, 0.43)
    L.assign(bw, S.mat_ship_wood("bulwark", c1=(0.04, 0.03, 0.018), c2=(0.22, 0.16, 0.09), seam=0.2))
    rail = L.prim("cube", loc=(0, 1.1, 0.87), name="rail")
    rail.scale = (3.0, 0.11, 0.045)
    L.bevel(rail, 0.012)
    L.assign(rail, wood)
    rnd = random.Random(5)
    for k in range(13):
        x = -1.9 + k * 0.3 + rnd.uniform(-0.1, 0.1)
        on_rail = k % 3 != 2
        loc = (x, 1.1 + rnd.uniform(-0.05, 0.05), 0.915) if on_rail else (x, rnd.uniform(-0.2, 0.7), 0.0)
        a = S.anemone(loc, scale=rnd.uniform(0.55, 1.0), color=rnd.choice(((0.85, 0.66, 0.6), (0.88, 0.52, 0.45), (0.8, 0.76, 0.68))),
                      name=f"an{k}", seed=k)
        for f in range(1, n + 1, 8):
            a.rotation_euler = (0.06 * math.sin(f * 0.08 + k), 0.06 * math.cos(f * 0.07 + k * 2), 0)
            a.keyframe_insert("rotation_euler", frame=f)
    for k in range(10):                      # small pale animals on the wood (generic blobs)
        b = L.prim("ico", loc=(rnd.uniform(-2, 2), rnd.uniform(-0.5, 0.9), 0.012), subdivisions=1, radius=rnd.uniform(0.015, 0.03),
                   name="blob")
        b.scale = (1.4, 1.0, 0.5)
        L.assign(b, L.mat_principled("blob_m", (0.9, 0.85, 0.75), rough=0.6))
    sp = L.spot((-2.8, -0.6, 1.3), (0, 0, 0), energy=450, size_deg=50, blend=0.7, color=COOL, name="rake")
    tg = _track(sp, (0, 0.8, 0.5), "rake_tgt")
    C.key_loc(tg, [(1, (-0.8, 0.9, 0.5)), (n, (0.8, 0.9, 0.5))])
    _snow(n, (0.0, 2.6, 0.9), (4, 1.2, 1.4), count=160, radius=0.003, seed=9, emit=0.2)
    cam = C.camera(lens=85)
    C.aim_cam(cam, n, [(1, (-0.75, -2.4, 1.75), (-0.45, 1.1, 0.5)), (n, (0.45, -2.4, 1.75), (0.6, 1.1, 0.5))], shake=0.004,
              rot_shake=0.0008, fn=lambda x: x)
    C.cam_fill(cam, energy=18, color=(0.4, 0.6, 0.9))
    _finish(L)


# ============================================================================ 1915: pack ice (S03 S04)

def _ice_z(x, y):
    return 0.3 + 0.35 * noise.noise(Vector((x * 0.03, y * 0.03, 0.4))) + 0.12 * noise.noise(Vector((x * 0.15, y * 0.15, 2.0)))


def _pack(L, n, dusk=False):
    if dusk:
        C.sky_world(top=(0.1, 0.11, 0.19), horizon=(0.7, 0.47, 0.47), ground=(0.2, 0.2, 0.25), strength=0.8)
        sun = C.sun_from(C.sun_dir(4, 20), energy=0.9, color=(1.0, 0.6, 0.55), angle=8)
    else:
        sd = C.sun_dir(9, 215)
        C.sky_world(top=(0.32, 0.45, 0.68), horizon=(0.95, 0.9, 0.82), ground=(0.5, 0.52, 0.58), sun_dir=tuple(sd),
                    sun_color=(1.0, 0.92, 0.8), sun_glow=1.2, strength=0.9)
        sun = C.sun_from(sd, energy=3.0, color=(1.0, 0.93, 0.82), angle=2)
    snow = M.mat_snow("packice")
    C.heightfield(size=(900, 900), center=(0, 0, 0), res=6.0, fn=_ice_z, mat=snow, name="pack", disp=(0, 0))
    C.heightfield(size=(120, 90), center=(0, 0, 0), res=0.9, fn=lambda x, y: _ice_z(x, y) + 0.05, mat=snow, name="packnear", disp=(0, 0))
    ice = L.mat_noise_surface("ridge", (0.5, 0.62, 0.74), (0.9, 0.93, 0.96), scale=0.6, bump=0.5, rough=0.5)
    rnd = random.Random(7)
    chunks = []
    for k in range(70):
        t = rnd.uniform(0.03, 0.97)
        x = -S.BQ_HL + 2 * S.BQ_HL * t + rnd.uniform(-1, 1)
        sy = rnd.choice((-1, 1))
        d = abs(rnd.gauss(0, 2.2))
        s = rnd.uniform(0.8, 2.6) * (1.2 - min(1.0, d / 6))
        o = L.prim("cube", loc=(x, sy * (S.bq_hw(t) + 0.3 + d), 0.4 + s * 0.35), name="ridge")
        o.scale = (s * rnd.uniform(0.8, 1.6), s * rnd.uniform(0.4, 0.9), s * rnd.uniform(0.4, 0.9))
        o.rotation_euler = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.5, 0.5), rnd.uniform(0, 3.1))
        L.assign(o, ice)
        chunks.append((o, sy, d))
    return sun, chunks


def S03(L, n):
    """1915: the ship locked in the pack; pressure ridges heave against the hull, it lists, a yard snaps."""
    sun, chunks = _pack(L, n)
    P = S.barquentine("end", wreck=False)
    r = P["root"]
    f_snap = int(n * 0.74)
    for f, rx in ((1, 0.02), (f_snap, 0.1), (f_snap + 3, 0.125), (n, 0.14)):
        r.rotation_euler = (rx, 0, 0)
        r.keyframe_insert("rotation_euler", frame=f)
    y = P["yard"]
    for f, a in ((1, 0.0), (f_snap - 1, 0.02), (f_snap + 4, 0.5), (f_snap + 9, 0.38), (n, 0.44)):
        y.rotation_euler = (a, 0, 0)
        y.keyframe_insert("rotation_euler", frame=f)
    for o, sy, d in chunks:
        if d < 3.5:
            p = Vector(o.location)
            C.key_loc(o, [(1, tuple(p)), (n, (p.x, p.y - sy * 0.5, p.z + 0.35))])
            o.keyframe_insert("rotation_euler", frame=1)
            o.rotation_euler.x += 0.18 * sy
            o.keyframe_insert("rotation_euler", frame=n)
    s = C.cloud((30.0, -12.0, 6.0), (30, 14, 12), count=700, radius=0.008, color=(1, 1, 1), emit=0.5, seed=3, name="drift")
    C.drift(s, n, (-2.0, 1.2, -0.3))
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (58.0, -22.0, 3.2), (4.0, 0.0, 11.0)), (n, (50.0, -19.0, 3.0), (4.0, 0.0, 11.0))], shake=0.25,
              rot_shake=0.006, rate=3.0, seed=4, shake_keys=[(1, 0.05), (f_snap - 1, 0.08), (f_snap + 2, 1.0), (n, 0.1)], fn=C.sm)
    _finish(L)


def S04(L, n):
    """Dusk: the crew, tiny and faceless, watch from the floe as the stern tilts up and slides under."""
    sun, chunks = _pack(L, n, dusk=True)
    gap = L.prim("cyl", loc=(-6, -45, 0.42), vertices=14, radius=1.0, depth=0.05, name="lead")
    gap.scale = (40, 13, 1)
    L.assign(gap, L.mat_principled("lead_m", (0.005, 0.012, 0.02), rough=0.12))
    P = S.barquentine("end", wreck=False)
    r = P["root"]
    for f, ry, z, x in ((1, 0.2, -2.5, 0.0), (n // 2, 0.5, -8.0, 2.5), (n, 0.85, -17.0, 5.0)):
        r.location = (x - 6.0, -45.0, z)
        r.rotation_euler = (0.1, ry, 0)
        r.keyframe_insert("location", frame=f)
        r.keyframe_insert("rotation_euler", frame=f)
    rnd = random.Random(3)
    fm = L.mat_principled("crew_m", (0.012, 0.012, 0.016), rough=0.8)
    for k in range(28):
        p = L.char_figure(f"crew{k}", color=(0.012, 0.012, 0.016), height=rnd.uniform(1.66, 1.82))
        for o in p.values():
            if o.type == "MESH":
                o.data.materials.clear()
                o.data.materials.append(fm)
        x = -22.0 + k * 0.92 + rnd.uniform(-0.25, 0.25)
        yy = -134.0 + rnd.uniform(-1.3, 1.3)
        p["root"].location = (x, yy, _ice_z(x, yy))
        p["root"].rotation_euler = (0, 0, rnd.uniform(-0.25, 0.25))
    for k, bx in enumerate((-27.5, -13.0, 5.5)):
        b, _ = M.lifeboat(loc=(bx, -130.0 + k * 0.8, _ice_z(bx, -130.0) + 0.55), length=6.5, name=f"boat{k}", people=0)
        b.rotation_euler = (0.06, 0, 0.2 - 0.25 * k)
    s = C.cloud((-10.0, -120.0, 3.5), (40, 14, 7), count=700, radius=0.008, color=(1, 0.95, 0.95), emit=0.4, seed=5, name="blow")
    C.drift(s, n, (2.2, 0.3, -0.2))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (-9.5, -152.0, 2.6), (-6.0, -100.0, -4.6)), (n, (-9.0, -149.0, 2.6), (-6.0, -97.0, -4.6))], fn=C.sm)
    _finish(L)


# ============================================================================ 2019: under the ice (S06)

def S06(L, n):
    """A torpedo-shaped robot glides away under the ice; its lamp shrinks into the blue-black and goes out."""
    S.setup(vol_end=60)
    L.set_world(color=(0.0, 0.006, 0.014), strength=1.0)
    C.ice_sheet(z=0.0, size=90, thickness=0.6, seed=3)
    S.world_volume(color=(0.1, 0.3, 0.5), density=0.018, anisotropy=0.5, center=(0, 20, -12), size=(90, 110, 24))
    for k, (x, y) in enumerate(((-6, 6), (7, 16), (-4, 30), (6, 44))):
        L.point((x, y, -1.6), energy=900, color=(0.35, 0.7, 1.0), radius=3.0, name=f"icelight{k}")
    P = S.auv_torpedo("auv", lamp=1200)
    r = P["root"]
    f_out = int(n * 0.8)
    pts = [(1, (1.6, 5.0, -3.4)), (int(n * 0.4), (2.2, 12.0, -3.2)), (f_out, (3.4, 27.0, -3.3)), (n, (3.8, 32.0, -3.4))]
    for (f, p), (f2, p2) in zip(pts, pts[1:] + [(n + 1, (4.0, 34.0, -3.4))]):
        r.location = p
        r.rotation_euler = (Vector(p2) - Vector(p)).to_track_quat("Y", "Z").to_euler()
        r.keyframe_insert("location", frame=f)
        r.keyframe_insert("rotation_euler", frame=f)
    C.key_energy(P["lamp"], [(1, 1200), (f_out - 10, 1200), (f_out, 0.0), (n, 0.0)])
    C.key_input(P["lens_mat"].node_tree.nodes["Emission"].inputs[1], [(1, 20.0), (f_out - 10, 20.0), (f_out, 0.0), (n, 0.0)])
    _snow(n, (3.0, 12.0, -4.0), (10, 14, 5), count=420, seed=3, vel=(0.03, 0.02, -0.02))
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.0, -1.5, -5.6), (2.0, 14.0, -3.6)), (n, (0.0, -1.2, -5.6), (2.6, 14.0, -3.4))], shake=0.03,
              rot_shake=0.003, fn=C.sm)
    C.cam_fill(cam, energy=260, color=(0.5, 0.75, 1.0))
    _finish(L)


# ============================================================================ 2022: icebreaker (S07 S10)

def _breaker(L, n, travel=14.0):
    C.sky_world(top=(0.42, 0.45, 0.5), horizon=(0.72, 0.74, 0.77), ground=(0.3, 0.32, 0.35), strength=1.0)
    C.sun_from(C.sun_dir(40, 200), energy=1.6, color=(0.92, 0.95, 1.0), angle=40)
    sea = L.prim("plane", loc=(0, 0, -0.3), size=2400, name="sea")
    L.assign(sea, L.mat_principled("sea_m", (0.008, 0.02, 0.035), rough=0.15))
    S.ice_floes(size=(620, 760), cell=17.0, seed=2, gap=1.6, keep=lambda x, y: not (abs(x) < 15 and y < 62 + travel))
    S.ice_floes(size=(34, 420), cell=5.0, seed=5, gap=1.4, name="brash", jitter=0.9,
                keep=lambda x, y: y < -70 and abs(x) > 4 and abs(x) < 15)
    P = S.dsv("breaker", length=120.0, beam=22.0, hull=(0.6, 0.06, 0.04), house=(0.92, 0.92, 0.9), floods=False)
    for o in list(bpy.data.objects):
        if any(k in o.name for k in ("_tleg", "_tbr", "_ttop", "_crane", "_jib")):
            bpy.data.objects.remove(o, do_unlink=True)
    P["bridge_mat"].node_tree.nodes["Emission"].inputs[0].default_value = (0.05, 0.08, 0.1, 1)
    P["bridge_mat"].node_tree.nodes["Emission"].inputs[1].default_value = 0.6
    C.key_loc(P["root"], [(1, (0, 0, 0)), (n, (0, travel, 0))])
    L.linear_fcurves(P["root"])
    return P


def S07(L, n):
    """Aerial: a red-hulled icebreaker grinds through broken sea ice, a dark lane behind it."""
    _breaker(L, n)
    s = C.cloud((30.0, 0.0, 45.0), (120, 140, 50), count=900, radius=0.008, color=(1, 1, 1), emit=0.6, seed=4, name="lightsnow")
    C.drift(s, n, (-3.0, -2.0, -2.5))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (105.0, -95.0, 95.0), (0.0, 0.0, -18.0)), (n, (92.0, -62.0, 88.0), (0.0, 22.0, -18.0))], shake=0.3,
              rot_shake=0.002, rate=0.4, fn=lambda x: x)
    _finish(L)


def S10(L, n):
    """Map backdrop: the sea ice from high above, soft."""
    _breaker(L, n, travel=8.0)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (20.0, -60.0, 260.0), (0.0, 10.0, 0.0)), (n, (5.0, -45.0, 250.0), (0.0, 18.0, 0.0))], fn=lambda x: x)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 30.0
    cam.data.dof.aperture_fstop = 0.25
    _finish(L)


# ============================================================================ S08 the descent

def S08(L, n):
    """The yellow drone descends through black water; marine snow streams upward past it; lamps point into nothing."""
    S.setup(vol_end=40)
    L.set_world(color=(0.0, 0.002, 0.005), strength=1.0)
    S.world_volume(color=(0.3, 0.5, 0.65), density=0.02, anisotropy=0.5, center=(0, 2, -4), size=(30, 30, 40))
    P = S.rov_drone("rov", lamp=2600)
    r = P["root"]
    for f in list(range(1, n + 1, 4)) + [n]:
        t = (f - 1) / 24.0
        r.location = (-0.9 + 0.12 * math.sin(t * 1.1), 0.0, 0.2 * math.sin(t * 0.8) - 0.25 * t / 4.0)
        r.rotation_euler = (-0.5 + 0.03 * math.sin(t * 1.3), 0.04 * math.sin(t * 0.9), 0.5 + 0.05 * math.sin(t * 0.6))
        r.keyframe_insert("location", frame=f)
        r.keyframe_insert("rotation_euler", frame=f)
    C.rim_light((-0.9, 0.0, 0.0), (-2.5, 3.5, 2.5), energy=900, color=(0.35, 0.6, 1.0), size_deg=50, name="rim")
    C.rim_light((-0.9, 0.0, 0.0), (1.5, -2.0, 3.5), energy=500, color=(0.5, 0.7, 1.0), size_deg=50, name="top")
    for k, (cx, cy) in enumerate(((-3.2, 2.5), (1.6, 3.0), (-0.5, 5.0))):
        s = C.cloud((cx, cy, -9.0), (3.2, 2.4, 34.0), count=380, radius=0.006, color=(0.85, 0.9, 0.95), emit=0.45, seed=10 + k,
                    name=f"up{k}")
        C.drift(s, n, (0.0, 0.0, 2.6))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (-4.2, -6.6, 1.5), (-0.2, 0.0, -0.9)), (n, (-3.9, -6.0, 1.3), (-0.2, 0.0, -1.1))], shake=0.05,
              rot_shake=0.004, rate=0.5, seed=5, fn=C.sm)
    C.cam_fill(cam, energy=110, color=(0.4, 0.6, 0.95))
    _finish(L)
