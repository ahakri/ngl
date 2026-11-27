"""CAVE-06 — Eagle's Nest sinkhole, Florida. Shot builders (def Sxx(L, n)). No victims are depicted or named:
divers are generic faceless rigs, the 2016 divers appear only as torches/dots.
Shared builders: PIPELINE/blender/lib_cave.py (air_bell(hole_r), warning_sign, hooded_icon, florida_woods, pond_mat,
upright_head_kit added for CAVE-05/06)."""
import sys, os, math, random
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "PIPELINE", "blender"))
import importlib
import lib_cave as C
importlib.reload(C)
import bpy
from mathutils import Vector, noise

PR = 7.0          # pond radius (m)
WZ = -0.5         # pond water level
BLUE = (0.15, 0.4, 1.0)
CYAN_RIM = (0.35, 0.85, 1.0)
GREEN_W = (0.3, 0.5, 0.25)


def _track(obj, pos, name="tgt"):
    t = bpy.data.objects.new(name, None)
    C.L.link(t)
    t.location = pos
    con = obj.constraints.new("TRACK_TO")
    con.target = t
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    return t


# ============================================================================ pond exterior

def pond_z(x, y, shaft=False):
    r = math.hypot(x, y)
    g = 0.12 * noise.noise(Vector((x * 0.08, y * 0.08, 0.3))) + 0.05 * noise.noise(Vector((x * 0.3, y * 0.3, 1.1)))
    sand = C.sm((-y - 2.0) / 3.0) * C.sm((3.5 - abs(x)) / 1.5)
    ramp_w = 1.4 + 4.0 * sand
    if r >= PR + ramp_w:
        return g + 0.01 * max(0.0, r - 18)
    if r >= PR:
        return C.lerp(WZ - 0.12, g, C.sm((r - PR) / ramp_w))
    z = WZ - 0.12 - 1.6 * C.sm((PR - r) / 4.0)
    if shaft and r < 1.45:
        return WZ - 30.0
    if r < 2.0:
        z -= 1.2 * C.sm((2.0 - r) / 1.0)
    return z


def _sky(L, tod):
    if tod == "morning":
        C.sky_world(top=(0.32, 0.48, 0.72), horizon=(0.85, 0.78, 0.66), ground=(0.1, 0.1, 0.08), strength=1.0)
        return C.sun_from(C.sun_dir(32, 120), energy=3.2, color=(1.0, 0.88, 0.7), angle=3)
    if tod == "afternoon":
        C.sky_world(top=(0.3, 0.45, 0.7), horizon=(0.9, 0.75, 0.55), ground=(0.1, 0.09, 0.07), strength=0.9)
        return C.sun_from(C.sun_dir(13, 200), energy=3.6, color=(1.0, 0.72, 0.45), angle=2)
    if tod == "dusk":
        C.sky_world(top=(0.06, 0.08, 0.18), horizon=(0.55, 0.32, 0.25), ground=(0.03, 0.03, 0.03), strength=0.8)
        return C.sun_from(C.sun_dir(3, 260), energy=1.0, color=(1.0, 0.45, 0.25), angle=3)
    if tod == "dawn":
        C.sky_world(top=(0.18, 0.26, 0.45), horizon=(0.85, 0.62, 0.5), ground=(0.05, 0.05, 0.05), strength=0.85)
        return C.sun_from(C.sun_dir(6, 80), energy=1.6, color=(1.0, 0.7, 0.5), angle=3)


def _pond(L, n, tod="morning", trees=110, shaft=False, coarse=True, knees=True):
    sun = _sky(L, tod)
    gm = L.mat_noise_surface("fl_ground", (0.06, 0.05, 0.03), (0.2, 0.17, 0.1), scale=1.2, bump=0.5, voronoi=False)
    fn = lambda x, y: pond_z(x, y, shaft)
    if coarse:
        C.heightfield(size=(110, 110), center=(0, 0, 0), res=0.9, fn=lambda x, y: fn(x, y) - 0.06, mat=gm,
                      name="ground", disp=(0.0, 0.0))
    C.heightfield(size=(24, 24), center=(0, 0, 0), res=0.16, fn=fn, mat=gm, name="bank", disp=(0.0, 0.0))
    sand = L.mat_noise_surface("sand", (0.42, 0.36, 0.26), (0.7, 0.62, 0.48), scale=2.0, bump=0.3, voronoi=False)
    C.heightfield(size=(5.6, 6.5), center=(0, -PR - 2.6, 0), res=0.12, fn=lambda x, y: fn(x, y) + 0.012, mat=sand,
                  name="entry", disp=(0.0, 0.0))
    wat = L.prim("plane", loc=(0, 0, WZ), size=2 * PR + 4, name="pond")
    L.assign(wat, C.pond_mat("pond_m"))
    rnd = random.Random(5)
    pts = []
    while len(pts) < trees:
        a = rnd.uniform(0, 2 * math.pi)
        r = PR + 3.5 + rnd.random() ** 0.7 * 38
        x, y = math.cos(a) * r, math.sin(a) * r
        if y < 0 and abs(x) < 4.0 and r < 17:
            continue
        pts.append((x, y, fn(x, y)))
    woods = C.florida_woods(pts, seed=4)
    # palmetto understory just above the bank
    under = []
    for i in range(60):
        a = rnd.uniform(0, 2 * math.pi)
        r = PR + rnd.uniform(1.8, 5.5)
        x, y = math.cos(a) * r, math.sin(a) * r
        if y < 0 and abs(x) < 3.2:
            continue
        under.append((x, y, fn(x, y)))
    C.jungle(under, size=(0.45, 1.0), seed=6, c1=(0.03, 0.05, 0.015), c2=(0.12, 0.17, 0.05), name="palmetto")
    if knees:
        km = L.mat_noise_surface("knee_m", (0.07, 0.05, 0.035), (0.22, 0.17, 0.12), scale=8, bump=0.6, voronoi=False)
        for i in range(26):
            a = rnd.uniform(math.radians(150), math.radians(250))
            r = PR + rnd.uniform(-0.3, 0.6)
            x, y = math.cos(a) * r, math.sin(a) * r
            h = rnd.uniform(0.12, 0.4)
            o = L.prim("cone", loc=(x, y, max(WZ, fn(x, y)) + h / 2 - 0.05), vertices=8, radius1=rnd.uniform(0.05, 0.1),
                       radius2=0.015, depth=h, name="knee")
            L.assign(o, km)
    return {"water": wat, "sun": sun, "fn": fn}


def _dive_line(L, a_deg=235, length=3.2):
    """Line tied to an exposed root on the bank, running down into the water toward the pond centre."""
    a = math.radians(a_deg)
    bx, by = math.cos(a) * (PR + 0.35), math.sin(a) * (PR + 0.35)
    bz = pond_z(bx, by)
    root = C.curve([(bx - 0.35 * math.sin(a), by + 0.35 * math.cos(a), bz - 0.05), (bx, by, bz + 0.18),
                    (bx + 0.35 * math.sin(a), by - 0.35 * math.cos(a), bz - 0.05)], thickness=0.05,
                   mat=L.mat_noise_surface("root_m", (0.06, 0.045, 0.03), (0.2, 0.15, 0.1), scale=8, bump=0.6,
                                           voronoi=False), name="root", smooth_pts=True)
    lm = L.mat_principled("diveline_m", (0.95, 0.85, 0.2), rough=0.4, emit=(0.95, 0.85, 0.2), emit_strength=0.6)
    ix, iy = -math.cos(a), -math.sin(a)
    pts = [(bx, by, bz + 0.15), (bx + ix * 0.6, by + iy * 0.6, WZ + 0.12), (bx + ix * 1.3, by + iy * 1.3, WZ - 0.05),
           (bx + ix * length, by + iy * length, WZ - 1.6)]
    ln = C.curve(pts, thickness=0.006, mat=lm, name="diveline", smooth_pts=True)
    return (bx, by, bz), (bx + ix * 1.3, by + iy * 1.3, WZ)


S01_POSE = ((0.25, -0.4, 44.0), (0.0, 0.0, WZ), 12.0)


def S01(L, n):
    C.render_quality(vol_end=80, vol_tile="8", vol_samples=16)
    _pond(L, n, "morning")
    cam = C.camera(lens=28, clip_end=600)
    C.aim_cam(cam, n, [(1, *S01_POSE), (n, (0.15, -0.25, 37.0), (0.0, 0.0, WZ), 14.0)], shake=0.04, rot_shake=0.0008,
              rate=0.3, fn=lambda x: x)
    L.bake_static()


def S16(L, n):
    """Rise out of the water to S01's first-frame pose."""
    C.render_quality(vol_end=80, vol_tile="8", vol_samples=16)
    P = _pond(L, n, "morning", shaft=True)
    cross = 14
    under = L.prim("plane", loc=(0, 0, WZ - 0.003), size=2 * PR + 4, name="underside")
    L.assign(under, C.emis("underside_m2", (0.45, 0.75, 0.4), 1.6))
    C.hide_from_frame([under], f_hide=cross + 1)
    C.hide_from_frame([P["water"]], f_show=cross + 1)
    uw = C.water(center=(0, 0, WZ - 3.0), size=(2 * PR, 2 * PR, 5.9), color=GREEN_W, density=0.12,
                 absorption=(0.3, 0.15, 0.35), name="uw")
    C.hide_from_frame([uw], f_hide=cross + 1)
    rnd = random.Random(3)
    motes = C.cloud((0, 0, WZ - 1.2), (3, 3, 2), count=500, radius=0.003, color=(0.8, 0.9, 0.7), emit=0.1, seed=4)
    C.hide_from_frame([motes], f_hide=cross + 1)
    cam = C.camera(lens=28, clip_end=600)
    C.aim_cam(cam, n, [(1, (0.25, -0.4, WZ - 1.3), (0.0, 0.0, WZ + 10), 12.0),
                       (cross, (0.25, -0.4, WZ - 0.05), (0.0, 0.0, WZ + 10), 12.0),
                       (cross + 1, (0.25, -0.4, WZ + 0.6), (0.0, 0.0, WZ), 12.0),
                       (n - 12, *S01_POSE), (n, *S01_POSE)],
              shake=0.02, rot_shake=0.0008, rate=0.3, shake_keys=[(1, 1.0), (n - 12, 0.0), (n, 0.0)])
    L.bake_static()


def S02(L, n):
    C.render_quality(vol_end=60, vol_tile="8", vol_samples=16)
    _pond(L, n, "morning", trees=110)
    root, entry = _dive_line(L, 235)
    # dragonfly-sized speck skimming
    sp = L.prim("sphere", loc=(0, 0, 0), segments=8, ring_count=6, radius=0.012, name="speck")
    L.assign(sp, L.mat_principled("speck_m", (0.02, 0.03, 0.04), rough=0.3))
    keys = []
    for k, f in enumerate(range(1, n + 1, 4)):
        t = f / n
        keys.append((f, (-4.6 + 2.2 * t + 0.15 * math.sin(k * 1.7), -3.4 - 1.0 * t + 0.1 * math.cos(k * 2.3),
                         WZ + 0.25 + 0.06 * math.sin(k))))
    C.key_loc(sp, keys)
    a0, a1 = math.radians(196), math.radians(207)
    cam = C.camera(lens=35)
    c0 = Vector((math.cos(a0) * (PR + 0.9), math.sin(a0) * (PR + 0.9), 0))
    c1 = Vector((math.cos(a1) * (PR + 0.9), math.sin(a1) * (PR + 0.9), 0))
    c0.z = pond_z(c0.x, c0.y) + 0.45
    c1.z = pond_z(c1.x, c1.y) + 0.45
    tgt = (root[0] + 0.6, root[1] + 0.8, WZ + 0.05)
    C.aim_cam(cam, n, [(1, tuple(c0), tgt), (n, tuple(c1), tgt)], shake=0.008, rot_shake=0.002, fn=lambda x: x)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 2.0
    d_near = 1.6
    d_far = (Vector(entry) - c1).length
    for f, d in ((1, d_near), (int(n * 0.35), d_near), (int(n * 0.75), d_far), (n, d_far)):
        cam.data.dof.focus_distance = d
        cam.data.dof.keyframe_insert("focus_distance", frame=f)
    L.bake_static()


def S09(L, n):
    C.render_quality(vol_end=60, vol_tile="8", vol_samples=16)
    _pond(L, n, "dusk", knees=False)
    cam = C.camera(lens=28, clip_end=600)
    C.aim_cam(cam, n, [(1, (-1.5, -12.5, 2.6), (0.0, 4.0, 0.6)), (n, (1.5, -12.0, 2.5), (0.0, 4.0, 0.6))],
              shake=0.01, rot_shake=0.001, fn=lambda x: x)
    L.bake_static()


def S10(L, n):
    C.render_quality(vol_end=60, vol_tile="8", vol_samples=16)
    _pond(L, n, "dawn")
    root, entry = _dive_line(L, 235)
    mist = C.cloud((0, 0, WZ + 0.35), (14, 14, 0.5), count=1800, radius=0.006, color=(0.9, 0.85, 0.8), emit=0.15,
                   seed=11, name="mist")
    C.drift(mist, n, (0.1, 0.03, 0.0))
    cam = C.camera(lens=32, clip_end=600)
    C.aim_cam(cam, n, [(1, (-7.0, -10.5, 1.6), (root[0] + 0.5, root[1] + 1.5, WZ)),
                       (n, (-6.0, -9.3, 1.4), (root[0] + 0.5, root[1] + 1.5, WZ))], shake=0.008, rot_shake=0.001)
    L.bake_static()


def _figure_tank(L, p, s=1.0):
    t = C.tank((0, 0.12, -0.05), rot=(0.2, 0, 0), length=0.65, r=0.08, name=p["root"].name + "_tk")
    t.parent = p["pelvis"]
    return t


def S11(L, n):
    C.render_quality(vol_end=60, vol_tile="8", vol_samples=16)
    P = _pond(L, n, "afternoon")
    fn = P["fn"]
    spots = [(-1.3, -8.6, math.radians(10), "stand"), (0.4, -8.2, math.radians(-20), "crouch"),
             (1.7, -8.9, math.radians(30), "crouch")]
    for k, (x, y, rz, pose) in enumerate(spots):
        p = C.figure(f"team{k}", height=1.74 + 0.03 * k, base=(0.03, 0.03, 0.035), rim=(1.0, 0.78, 0.5),
                     rim_strength=0.5)
        p["root"].location = (x, y, fn(x, y))
        p["root"].rotation_euler = (0, 0, math.pi + rz)
        if pose == "crouch":
            C.pose_sit(p, 1.75, lean=0.5)
            p["pelvis"].location.z = 0.45
            for tag in ("L", "R"):
                p[f"shoulder{tag}"].rotation_euler = (1.2, 0, (0.15 if tag == "L" else -0.15))
                p[f"elbow{tag}"].rotation_euler = (0.3, 0, 0)
            p["neck"].rotation_euler = (-0.6, 0, 0)
            # arms working on a cylinder valve
            for f in range(1, n + 1, 8):
                p["shoulderR"].rotation_euler = (1.2 + 0.18 * math.sin(f * 0.4 + k), 0, -0.15)
                p["shoulderR"].keyframe_insert("rotation_euler", frame=f)
        else:
            p["shoulderR"].rotation_euler = (0.5, 0, -0.1)
            p["elbowR"].rotation_euler = (1.2, 0, 0)
            t = C.tank((0, 0.18, -0.2), rot=(0, 0, 0), length=0.65, r=0.08, name=f"carry{k}")
            t.parent = p["pelvis"]
    rnd = random.Random(2)
    for k in range(7):
        x, y = rnd.uniform(-2.4, 2.6), rnd.uniform(-9.6, -7.8)
        lying = k % 2 == 0
        C.tank((x, y, fn(x, y) + (0.09 if lying else 0.36)), rot=((math.pi / 2, 0, rnd.uniform(0, 3)) if lying else (0, 0, 0)),
               length=0.65, r=0.08, band=(0.95, 0.95, 0.9) if k % 3 else (1.0, 0.78, 0.1), name=f"tk{k}")
    cam = C.camera(lens=40, clip_end=600)
    C.aim_cam(cam, n, [(1, (0.5, -1.2, WZ + 1.0), (0.2, -8.6, 0.55)), (n, (0.35, -2.6, WZ + 0.95), (0.2, -8.6, 0.55))],
              shake=0.01, rot_shake=0.001)
    L.bake_static()


def S13(L, n):
    C.render_quality(vol_end=60, vol_tile="8", vol_samples=16)
    P = _pond(L, n, "afternoon", knees=False)
    sun = P["sun"]
    C.key_energy(sun, [(1, 3.4), (n, 0.35)])
    for f, col in ((1, (1.0, 0.75, 0.5)), (n, (1.0, 0.42, 0.22))):
        sun.data.color = col
        sun.data.keyframe_insert("color", frame=f)
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    C.key_input(bg.inputs[1], [(1, 0.9), (n, 0.18)])
    # bubbles breaking the surface over the chimney: rings that grow sparse, then stop
    m = C.emis("bring_m", (0.85, 0.9, 0.85), 0.6)
    events = [2, 6, 11, 17, 25, 36, 50]
    rnd = random.Random(6)
    for i, f0 in enumerate(events):
        o = L.prim("torus", loc=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), WZ + 0.004), major_radius=1.0,
                   minor_radius=0.008, major_segments=40, minor_segments=4, name=f"bring{i}")
        L.assign(o, m)
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=max(1, f0 - 1))
        o.scale = (0.03, 0.03, 1)
        o.keyframe_insert("scale", frame=f0)
        o.scale = (0.7, 0.7, 1)
        o.keyframe_insert("scale", frame=f0 + 26)
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=f0 + 27)
        b = L.prim("sphere", loc=(o.location.x, o.location.y, WZ + 0.01), segments=10, ring_count=6, radius=0.03,
                   name=f"bub{i}")
        L.assign(b, C.rim_glass_mat("bub_m", (0.9, 0.95, 1.0), strength=1.5, power=1.5, base=0.15))
        b.scale = (0.001,) * 3
        b.keyframe_insert("scale", frame=max(1, f0 - 3))
        b.scale = (1, 1, 0.6)
        b.keyframe_insert("scale", frame=f0 - 1)
        b.scale = (0.001,) * 3
        b.keyframe_insert("scale", frame=f0 + 1)
    cam = C.camera(lens=35, clip_end=600)
    C.aim_cam(cam, n, [(1, (0.6, -PR - 1.2, WZ + 0.55), (0.0, 0.0, WZ - 0.15)),
                       (n, (0.6, -PR - 1.2, WZ + 0.55), (0.0, 0.0, WZ - 0.15))], shake=0.003, rot_shake=0.0005)
    L.bake_static()


# ============================================================================ the Chimney (S03, S12)

def _chimney(L, n, light=320):
    C.world_black((0.0, 0.002, 0.002))
    sh = C.shaft(WZ - 1.3, WZ - 18.0, lambda z, a: 1.25 + 0.15 * math.sin(3 * a + z * 0.7), step=0.5, ring=36, seed=3,
                 rough=0.18, mat=C.rock_mat("chim", (0.03, 0.035, 0.025), (0.24, 0.24, 0.18), scale=1.5),
                 name="chimney", disp=(0.18, 0.06))
    day = L.area((0, 0, WZ + 0.3), (0, 0, 0), energy=light, size=3.0, color=(0.55, 0.9, 0.5), name="daylight")
    vol = C.water(center=(0, 0, WZ - 9.0), size=(3.2, 3.2, 17.0), color=(0.35, 0.55, 0.3), density=0.07,
                  absorption=(0.25, 0.12, 0.3), name="chimwater")
    C.line([(0.75, 0.2, WZ - 1.3), (0.7, 0.35, WZ - 8.0), (0.6, 0.25, WZ - 17.5)], thickness=0.006, emit=0.8,
           name="guideline")
    return sh, day


def S03(L, n):
    C.render_quality(vol_end=30, vol_tile="8", vol_samples=24)
    P = _pond(L, n, "morning", trees=40, shaft=True, knees=False)
    sh, day = _chimney(L, n)
    cross = 16
    C.hide_from_frame([P["water"]], f_hide=cross + 1)
    d = C.diver("diverA", fins=BLUE, tanks="doubles", rebreather=False, light_energy=1800, beam_len=4.5,
                beam_strength=0.35, beam_deg=26)
    r = d["root"]
    r.rotation_euler = (-math.pi / 2 + 0.35, 0, 0)
    z0, z1 = WZ - 1.9, WZ - 9.5
    C.key_loc(r, [(1, (0.0, -0.1, z0 + 0.6)), (cross, (0.0, -0.1, z0)), (n, (0.0, -0.05, z1))])
    L.ease_all(r)
    L.anim_swim(d, n, kick_rate=0.7, amp=0.2)
    dt = _track(d["torch"], (0, 0, 0), "dt")
    dt.parent = r
    dt.location = (0.0, 3.0, -0.6)
    C.rim_light((0, 0, z0), (0.0, 0.8, 2.5), energy=600, color=(0.55, 0.9, 0.55), size_deg=50, name="toprim")
    motes = C.cloud((0, 0, WZ - 6), (2.0, 2.0, 10), count=1200, radius=0.003, color=(0.8, 0.9, 0.75), emit=0.06, seed=5)
    C.drift(motes, n, (0.0, 0.0, 0.05))
    cam = C.camera(lens=20)
    keys = [(1, (0.0, 0.55, WZ + 2.8), (0.0, 0.2, WZ - 6.0)), (cross, (0.0, 0.55, WZ - 0.15), (0.0, 0.2, WZ - 6.0))]
    for f in range(cross + 4, n + 1, 6):
        t = C.sm((f - cross) / (n - cross))
        z = C.piecewise([(cross, z0), (n, z1)], f)
        keys.append((f, (0.05, 0.6, z + 2.1), (0.0, -0.1, z - 3.0)))
    keys.append((n, (0.05, 0.6, z1 + 2.1), (0.0, -0.1, z1 - 3.0)))
    C.aim_cam(cam, n, keys, shake=0.02, rot_shake=0.004, rate=0.6)
    C.cam_fill(cam, energy=60, color=(0.6, 0.9, 0.6))
    L.bake_static()


def S12(L, n):
    C.render_quality(vol_end=30, vol_tile="8", vol_samples=24)
    _pond(L, n, "afternoon", trees=0, shaft=True, coarse=False, knees=False)
    bpy.data.objects["pond"].hide_render = True
    sky = L.prim("plane", loc=(0, 0, WZ + 0.01), size=2 * PR + 4, name="underside")
    L.assign(sky, C.emis("underside_m", (0.45, 0.75, 0.4), 1.2))
    sh, day = _chimney(L, n, light=500)
    C.water(center=(0, 0, WZ - 0.8), size=(2 * PR, 2 * PR, 1.5), color=GREEN_W, density=0.08,
            absorption=(0.3, 0.15, 0.35), name="poolwater")
    c = C.diver("diverC", fins=(0.2, 0.75, 0.3), tanks="doubles", rebreather=False, light_energy=600, beam_len=2.0,
                beam_strength=0.2)
    rc = c["root"]
    rc.location = (0.35, 0.95, WZ - 1.35)
    rc.rotation_euler = (0.15, 0, math.radians(200))
    C.key_loc(rc, [(1, (0.35, 0.95, WZ - 1.35)), (n, (0.3, 0.9, WZ - 1.3))])
    L.anim_swim(c, n, kick_rate=0.35, amp=0.12)
    # the two deep divers: torches only (generic), shrinking down the shaft
    for k, (x, ph) in enumerate(((-0.3, 0), (0.25, 6))):
        g, _, hem = C.glow_dot((x, 0.0, WZ - 3.0), C.TORCH, r=0.03, halo=6, strength=10, name=f"deep{k}")
        sp = L.spot((0, 0, 0), (0, 0, 0), energy=1500, size_deg=28, blend=0.5, color=C.TORCH, name=f"deepsp{k}")
        sp.parent = g
        C.key_loc(g, [(1, (x, 0.05 * k, WZ - 3.0 - 0.6 * k)), (n, (x * 0.6, 0.0, WZ - 13.0 - 0.8 * k))])
        em = g.active_material.node_tree.nodes["Emission"].inputs[1]
        C.key_input(em, [(1, 10), (int(n * 0.7), 6), (n, 2.5)])
        C.key_input(hem.inputs[1], [(1, 3.5), (int(n * 0.7), 2.0), (n, 0.8)])
        C.key_energy(sp, [(1, 1500), (n, 400)])
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (0.5, 1.6, WZ - 0.35), (0.0, 0.0, WZ - 9.0)), (n, (0.45, 1.5, WZ - 0.45), (0.0, 0.0, WZ - 10.0))],
              shake=0.015, rot_shake=0.003)
    C.cam_fill(cam, energy=40, color=(0.6, 0.9, 0.6))
    L.bake_static()


# ============================================================================ the Ballroom (S04, S05, S07, S08)

def _ballroom(L, n, vol=True):
    C.world_black((0.0, 0.002, 0.004))
    C.render_quality(vol_end=60, vol_tile="8", vol_samples=24)
    rock = C.rock_mat("ball_m", (0.025, 0.028, 0.03), (0.2, 0.2, 0.19), scale=0.35)
    dome = C.air_bell(R=(16, 14), H=7.0, below=17.0, seed=8, rough=0.15, mat=rock, name="ballroom", res=(72, 36),
                      disp=(1.6, 0.4), hole_r=1.6)
    C.shaft(18.0, 6.2, lambda z, a: 1.15 + 0.12 * math.sin(3 * a + z), step=0.6, ring=28, seed=4, rough=0.15,
            mat=rock, name="chimney", disp=(0.15, 0.05))
    debris = L.mat_noise_surface("debris", (0.07, 0.055, 0.035), (0.3, 0.24, 0.16), scale=1.4, bump=0.7, voronoi=False)
    mound = L.prim("cone", loc=(0.0, 0.0, -12.5), vertices=48, radius1=10.0, radius2=0.8, depth=8.0, name="mound")
    sub = mound.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 2
    L.add_displace(mound, strength=0.9, scale=2.0, name="mound_d")
    L.smooth(mound)
    L.assign(mound, debris)
    sp = L.spot((0, 0, 9.0), (0, 0, 0), energy=9000, size_deg=12, blend=0.4, color=(0.55, 0.95, 0.55), name="dayshaft",
                radius=0.4)
    for k, (x, y, z) in enumerate(((-9, -4, -2), (8, 5, -4), (2, -9, -8), (-4, 8, -10))):
        L.point((x, y, z), energy=1200, color=(0.35, 0.55, 0.75), radius=3.0, name=f"amb{k}")
    w = None
    if vol:
        w = C.water(center=(0, 0, -4.0), size=(30, 26, 22), color=(0.45, 0.6, 0.55), density=0.012,
                    absorption=(0.1, 0.06, 0.04), name="ballwater")
    return {"dome": dome, "mound": mound}


def S04(L, n):
    _ballroom(L, n)
    d = C.diver("diverA", fins=BLUE, tanks="doubles", rebreather=False, light_energy=5000, beam_len=12, beam_strength=0.25,
                beam_deg=20)
    r = d["root"]
    r.rotation_euler = (-math.pi / 2 + 0.5, 0, 0.3)
    C.key_loc(r, [(1, (0.0, 0.0, 6.9)), (n, (0.1, -0.2, 5.4))])
    L.anim_swim(d, n, kick_rate=0.6, amp=0.18)
    t = _track(d["torch"], (2.0, -6.0, -6.0), "dt")
    C.key_loc(t, [(1, (1.0, -5.0, -4.0)), (n, (4.0, -7.0, -8.0))])
    C.rim_light((0, 0, 6.5), (0.0, 0.0, 3.0), energy=800, color=(0.55, 0.95, 0.55), size_deg=30, name="toprim")
    cam = C.camera(lens=18, clip_end=200)
    C.aim_cam(cam, n, [(1, (1.6, -2.4, 4.6), (0.0, 0.0, 6.0)), (int(n * 0.45), (4.0, -8.0, 1.0), (0.0, 0.0, 2.0)),
                       (n, (6.0, -12.5, -3.0), (0.0, 0.0, -3.5))], shake=0.02, rot_shake=0.002, fn=C.sm)
    L.bake_static()


def S05(L, n):
    _ballroom(L, n)
    d = C.diver("diverA", fins=BLUE, tanks="doubles", rebreather=False, light_energy=5000, beam_len=12, beam_strength=0.25,
                beam_deg=20)
    r = d["root"]
    r.rotation_euler = (-math.pi / 2 + 0.6, 0, 0.3)
    C.key_loc(r, [(1, (0.1, -0.2, 5.3)), (n, (0.2, -0.4, 4.6))])
    _track(d["torch"], (3.0, -6.0, -7.0), "dt")
    cam = C.camera(lens=24, clip_end=200)
    C.aim_cam(cam, n, [(1, (5.5, -11.5, -2.5), (0.0, 0.0, -1.0)), (n, (4.5, -11.0, -2.2), (0.0, 0.0, -1.0))],
              shake=0.02, rot_shake=0.001)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 0.8
    cam.data.dof.focus_distance = 2.0
    L.bake_static()


def _slope_z(x, y):
    return 0.32 * y + 0.08 * x + 0.12 * noise.noise(Vector((x * 0.6, y * 0.6, 0.5))) + 0.03 * noise.noise(
        Vector((x * 2.5, y * 2.5, 2.0)))


def _sign_set(L, n, density=0.035):
    C.world_black((0.0, 0.002, 0.004))
    C.render_quality(vol_end=20, vol_tile="8", vol_samples=24)
    debris = L.mat_noise_surface("debris", (0.07, 0.055, 0.035), (0.3, 0.24, 0.16), scale=2.0, bump=0.7, voronoi=False)
    C.heightfield(size=(16, 16), center=(0, 4, 0), res=0.14, fn=_slope_z, mat=debris, name="slope", disp=(0.0, 0.0))
    rnd = random.Random(7)
    stick = L.mat_principled("stick_m", (0.08, 0.06, 0.04), rough=0.8)
    for i in range(60):
        x, y = rnd.uniform(-5, 5), rnd.uniform(0.5, 9)
        ln = rnd.uniform(0.3, 1.1)
        o = L.prim("cyl", loc=(x, y, _slope_z(x, y) + 0.02), vertices=6, radius=rnd.uniform(0.01, 0.03), depth=ln,
                   rot=(math.pi / 2 + rnd.uniform(-0.2, 0.2), 0, rnd.uniform(0, 3.14)), name="stick")
        L.assign(o, stick)
    sx, sy = 0.35, 4.0
    sg = C.warning_sign((sx, sy, _slope_z(sx, sy) - 0.15), rot_z=0.05, w=0.72, h=0.86, post=0.85)
    cz = _slope_z(sx, sy) - 0.15 + 0.85 + 0.86 * 0.15
    C.water(center=(0, 4, 1.5), size=(12, 12, 6), color=(0.3, 0.45, 0.55), density=density, absorption=(0.12, 0.1, 0.06),
            name="deepwater")
    return Vector((sx, sy, cz)), sg


def S07(L, n):
    sc, sg = _sign_set(L, n)
    stop = 62
    eye0 = Vector((-0.2, -1.6, _slope_z(-0.2, -1.6) + 1.7))
    tgt = sc + Vector((0, 0, -0.05))
    torch = L.spot((0, 0, 0), (0, 0, 0), energy=2600, size_deg=22, blend=0.35, color=C.TORCH, name="pov_torch",
                   radius=0.03)
    cone, _ = C.beam_cone(torch, length=5.0, strength=0.25, name="pov_beam")
    aim = _track(torch, (0, 0, 0), "aim")
    sweep = [(1, (-3.6, 3.0, _slope_z(-3.6, 3.0) + 0.2)), (int(stop * 0.55), (-1.8, 4.6, _slope_z(-1.8, 4.6) + 0.3)),
             (stop, tuple(tgt)), (n, tuple(tgt))]
    C.key_loc(aim, sweep)
    L.ease_all(aim)
    cam = C.camera(lens=24)
    ck = [(f, tuple(eye0), p) for f, p in sweep[:2]]
    ck.append((stop, tuple(eye0), tuple(tgt + Vector((0, 0, -0.25)))))
    ck.append((n, tuple(eye0 + (Vector(sc) - eye0) * 0.32), tuple(tgt + Vector((0, 0, -0.25)))))
    C.aim_cam(cam, n, ck, shake=0.02, rot_shake=0.006, rate=0.8, shake_keys=[(1, 1.0), (stop, 1.0), (stop + 4, 0.35),
                                                                               (n, 0.35)])
    torch.parent = cam
    torch.location = (0.22, -0.18, 0.05)
    s = C.cloud((0, 2.5, 1.2), (5, 5, 2.5), count=1400, radius=0.003, color=(0.8, 0.75, 0.6), emit=0.05, seed=8)
    C.drift(s, n, (0.12, 0.0, 0.02))
    C.cam_fill(cam, energy=25, color=(0.55, 0.7, 0.85))
    L.bake_static()


def S08(L, n):
    sc, sg = _sign_set(L, n, density=0.02)
    tl = L.spot((sc.x - 1.0, sc.y - 2.0, sc.z + 0.8), (0, 0, 0), energy=900, size_deg=30, blend=0.4, color=C.TORCH,
                name="torch", radius=0.03)
    tl.rotation_mode = "QUATERNION"
    tl.rotation_quaternion = (Vector(sc) - Vector(tl.location)).to_track_quat("-Z", "Y")
    fl = 40
    C.key_energy(tl, [(1, 900), (fl - 1, 900), (fl, 120), (fl + 2, 650), (fl + 3, 200), (fl + 5, 900), (n, 900)])
    C.constant_keys(tl.data)
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (sc.x + 0.05, sc.y - 1.85, sc.z + 0.05), (sc.x, sc.y, sc.z - 0.22)),
                       (n, (sc.x + 0.03, sc.y - 1.55, sc.z + 0.04), (sc.x, sc.y, sc.z - 0.19))],
              shake=0.006, rot_shake=0.002)
    C.cam_fill(cam, energy=6, color=(0.55, 0.7, 0.85))
    s = C.cloud((sc.x, sc.y - 0.9, sc.z), (1.6, 1.2, 1.2), count=500, radius=0.002, color=(0.8, 0.75, 0.6), emit=0.04,
                seed=9)
    C.drift(s, n, (0.06, 0.0, 0.01))
    L.bake_static()


# ============================================================================ S15 deep empty tunnel

def S15(L, n):
    C.world_black((0.0, 0.001, 0.004))
    C.render_quality(vol_end=18, vol_tile="8", vol_samples=24)
    C.passage(length=26, y0=-4, half_w=1.6, half_h=1.2, zc=0.0, seed=21, rough=0.12, floor_flat=0.3,
              x_fn=lambda y: 0.35 * math.sin(y * 0.2), z_fn=lambda y: -0.04 * y,
              mat=C.rock_mat("deep", (0.02, 0.024, 0.03), (0.17, 0.18, 0.2), scale=1.2), disp=(0.22, 0.06))
    C.floor(size=(2.6, 26), center=(0, 9, -0.85), strength=0.1, name="silt")
    C.line([(0.4, -4, -0.6), (0.3, 5, -0.85), (0.5, 12, -1.1), (0.2, 21, -1.5)], thickness=0.006, emit=0.8,
           name="guideline")
    C.water(center=(0, 9, -0.3), size=(3.6, 26, 3.2), color=(0.25, 0.35, 0.5), density=0.05, absorption=(0.15, 0.1, 0.05),
            name="deepwater")
    s = C.cloud((0, 4.0, -0.3), (2.6, 7, 1.8), count=1600, radius=0.003, color=(0.75, 0.75, 0.7), emit=0.04, seed=12)
    C.drift(s, n, (0.03, 0.0, 0.01))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.1, -2.0, 0.25), (0.2, 8.0, -0.7)), (n, (0.1, -0.6, 0.2), (0.2, 9.0, -0.8))],
              shake=0.012, rot_shake=0.003)
    torch = L.spot((0, 0, 0), (0, 0, 0), energy=1600, size_deg=20, blend=0.35, color=C.TORCH, name="torch", radius=0.03)
    C.beam_cone(torch, length=5.0, strength=0.3, name="beam")
    torch.parent = cam
    torch.location = (0.25, -0.2, 0.05)
    aim = _track(torch, (0, 0, 0), "aim")
    C.key_loc(aim, [(1, (-1.2, 4.0, -0.4)), (int(n * 0.4), (1.2, 5.5, 0.2)), (int(n * 0.75), (-0.6, 7.0, 0.5)),
                    (n, (0.3, 9.0, -0.8))])
    C.cam_fill(cam, energy=15, color=(0.4, 0.55, 0.85))
    L.bake_static()


# ============================================================================ section diagrams (S06, S14)

def _ellipse(cx, cz, rx, rz, a0, a1, k=16):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / k)), cz + rz * math.sin(math.radians(a0 + (a1 - a0) * i / k)))
            for i in range(k + 1)]


BR = (0.0, -4.3, 3.0, 1.6)          # ballroom ellipse (cx, cz, rx, rz)
LOWER = [(2.85, -5.0), (3.5, -5.8), (4.1, -5.95), (4.6, -7.0), (5.2, -7.15), (5.6, -8.25), (6.3, -8.4)]
UPPER = [(2.98, -4.55), (3.75, -5.35), (4.35, -5.5), (4.95, -6.55), (5.55, -6.7), (6.0, -7.8), (6.3, -7.9)]
ROUTE = [(0.0, 0.0), (0.0, -0.6), (0.0, -2.7), (0.6, -4.0), (2.2, -4.8), (3.6, -5.6), (4.3, -5.75), (4.8, -6.8),
         (5.4, -6.95), (5.85, -8.05), (6.2, -8.15)]
FT_PER_UNIT = 36.0


def _eagle_section(L, name="xs"):
    C.world_black((0.0, 0.0, 0.0))
    cx, cz, rx, rz = BR
    poly = [(-1.9, 0.1), (-1.5, -0.25), (-0.8, -0.5), (-0.2, -0.65), (-0.16, -2.75)]
    poly += _ellipse(cx, cz, rx, rz, 95, 335, 24)
    poly += LOWER + list(reversed(UPPER))
    poly += _ellipse(cx, cz, rx, rz, 352, 445, 12)
    poly += [(0.16, -2.75), (0.2, -0.65), (0.8, -0.5), (1.5, -0.25), (1.9, 0.1)]
    xs = C.xsection([(x, -z) for x, z in poly], lambda d: -d, extent=(-6.0, 9.0, -10.5, 0.0),
                    water_top=(0.03, 0.24, 0.3), water_bot=(0.0, 0.04, 0.07), outline_color=C.CYAN, outline_strength=3.0,
                    name=name, rock_mat_=L.mat_noise_surface(name + "_rk", (0.07, 0.065, 0.06), (0.28, 0.26, 0.23),
                                                             scale=1.2, bump=0.2, rough=0.9))
    yb = 0.4 - 0.12 - 0.02
    mound = [(-2.2, -5.72), (-1.0, -5.05), (-0.2, -4.75), (0.6, -4.95), (1.8, -5.6), (2.4, -5.85)]
    C.flat_poly(mound, yb - 0.01, C.emis(name + "_mound", (0.4, 0.3, 0.18), 1.0), name=name + "_mound")
    C.curve([(-6.0, -0.42, 0.0), (-1.9, -0.42, 0.0)], thickness=0.02, mat=C.emis(name + "_gl", (0.4, 0.6, 0.3), 2.5),
            name=name + "_gl1")
    C.curve([(1.9, -0.42, 0.0), (9.0, -0.42, 0.0)], thickness=0.02, mat=C.emis(name + "_gl", (0.4, 0.6, 0.3), 2.5),
            name=name + "_gl2")
    rnd = random.Random(3)
    tm = C.emis(name + "_tree", (0.25, 0.45, 0.2), 1.3)
    for i in range(18):
        x = rnd.choice((-1, 1)) * rnd.uniform(2.4, 6.0) + (1.5 if rnd.random() < 0.4 else 0)
        o = L.prim("sphere", loc=(x, -0.42, 0.35), segments=10, ring_count=6, radius=rnd.uniform(0.22, 0.4),
                   name=name + "_tree")
        o.scale = (1.0, 0.3, 1.2)
        L.assign(o, tm)
    C.text("CHIMNEY", (1.2, -0.45, -1.7), size=0.36, color=(0.75, 0.95, 1.0), strength=3.0, align="LEFT",
           name=name + "_t1")
    C.text("BALLROOM", (-1.3, -0.45, -3.6), size=0.4, color=(0.75, 0.95, 1.0), strength=3.0, name=name + "_t2")
    L.area((-3, -6, 2), (math.radians(60), 0, math.radians(-25)), energy=2500, size=8, color=(0.7, 0.85, 1.0))
    L.area((5, -6, -6), (math.radians(70), 0, math.radians(30)), energy=1500, size=8, color=(0.8, 0.85, 0.9))
    return xs


def S06(L, n):
    _eagle_section(L, "s6")
    route = [(x, -0.46, z) for x, z in ROUTE]
    dot, _, _ = C.glow_dot(route[0], C.CYAN, r=0.08, halo=2.6, strength=6, name="dot")
    C.move_along(dot, route, [(6, 0.0), (n - 8, 1.0)], step=2)
    trail = C.curve(route, thickness=0.025, mat=C.emis("trail", C.CYAN, 2.5), name="trail")
    C.grow_curve(trail, [(6, 0.0), (n - 8, 1.0)])
    cam = C.camera(lens=30)
    C.aim_cam(cam, n, [(1, (1.6, -15.5, -2.6), (1.6, 0.0, -2.6)), (n, (1.6, -15.5, -5.6), (1.6, 0.0, -5.6))], fn=C.sm)
    L.bake_static()


def S14(L, n):
    _eagle_section(L, "s14")
    route = [(x, -0.46, z) for x, z in ROUTE]
    C.curve(route[:-1], thickness=0.025, mat=C.emis("trail", C.CYAN, 2.5), name="trail")
    mk = Vector((5.75, -0.47, -7.85))
    ring = L.prim("torus", loc=tuple(mk), rot=(math.pi / 2, 0, 0), major_radius=0.32, minor_radius=0.02, name="marker")
    L.assign(ring, C.emis("marker_m", (0.85, 0.85, 0.85), 2.0))
    for k, dx in enumerate((-0.09, 0.09)):
        g, _, hem = C.glow_dot((mk.x + dx, mk.y - 0.01, mk.z + 0.02 * k), (0.7, 0.72, 0.75), r=0.05, halo=2.5,
                               strength=3.0, name=f"grey{k}")
        em = g.active_material.node_tree.nodes["Emission"].inputs[1]
        C.key_input(em, [(1, 0.0), (20, 3.0), (int(n * 0.6), 3.0), (n, 1.0)])
        C.key_input(hem.inputs[1], [(1, 0.0), (20, 1.0), (int(n * 0.6), 1.0), (n, 0.3)])
    cam = C.camera(lens=30)
    C.aim_cam(cam, n, [(1, (2.2, -15.0, -4.6), (2.2, 0.0, -4.6)), (n, (4.4, -9.0, -6.4), (4.4, 0.0, -6.4))], fn=C.sm)
    L.bake_static()
