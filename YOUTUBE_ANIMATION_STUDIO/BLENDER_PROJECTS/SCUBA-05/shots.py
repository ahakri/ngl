"""SCUBA-05 — He Dived 332 m. Getting Back Took Nearly 15 Hours (Ahmed Gabr, Dahab, Red Sea, 2014).
One builder per shot: def Sxx(L, n). Scuba builders live in PIPELINE/blender/lib_scuba.py (tech_diver, descent_line,
depth_tag, stage_tank, lattice_tower, backdrop_z, mat_reveal_z, mat_xray, paper, magnifier, rubber_stamp ...).
Gabr is a faceless stylised tech diver (black suit + hood, sidemount twins, stage cylinders, yellow fins). No logos.
"""
import sys, os, math, random, importlib
import bpy
from mathutils import Vector, Matrix

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_scuba as S
importlib.reload(S)

PI = math.pi
SPEED = 2.6                       # apparent descent speed (m/s) in S01/S18
CAM01_A = Vector((3.3, 0.1, 2.15))   # S01 frame 1 == S18 last frame (loop)
CAM01_T = Vector((0.0, 0.25, 0.25))
CAM01_B = CAM01_A + Vector((0.1, 0.0, 0.25))
TEAL = (0.3, 1.0, 0.9)
YEL = (1.0, 0.82, 0.15)


# ----------------------------------------------------------------------------- helpers

def _finish(L):
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "AREA":
            o.data.volume_factor = 0.0
    L.bake_static()


def _upd():
    bpy.context.view_layer.update()


def _aim(o, frm, to, roll=0.0):
    o.location = frm
    q = (Vector(to) - Vector(frm)).to_track_quat("-Z", "Y")
    if roll:
        from mathutils import Quaternion
        q = q @ Quaternion((0, 0, 1), roll)
    o.rotation_euler = q.to_euler()
    return o


def look_keys(cam, keys, roll=0.0, interp=None):
    """keys: [(frame, pos, target)] -> location + rotation keys (no constraint)."""
    for f, p, t in keys:
        _aim(cam, p, t, roll)
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
    if interp:
        for fc in L_fc(cam):
            for kp in fc.keyframe_points:
                kp.interpolation = interp


def L_fc(o):
    import studio_lib
    return studio_lib._fcurves(o.animation_data.action)


def rim(L, loc, target, energy=600, size=4, color=(0.45, 0.85, 1.0), name="rim"):
    a = L.area(loc, (0, 0, 0), energy=energy, size=size, color=color, name=name)
    _aim(a, loc, target)
    return a


def bg_node():
    return [nd for nd in bpy.context.scene.world.node_tree.nodes if nd.type == "BACKGROUND"][0]


def key_input(sock, pairs):
    for f, v in pairs:
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=f)


def underwater_world(top=(0.25, 0.8, 0.85), horizon=(0.01, 0.12, 0.22), below=(0.0, 0.004, 0.01), strength=1.0,
                     sun_dir=None, sun_strength=8.0, sun_size=0.04):
    S.setup(vol_end=40)
    S.sky_gradient(top=top, horizon=horizon, below=below, strength=strength, sun_dir=sun_dir, sun_col=(0.85, 1.0, 1.0),
                   sun_size=sun_size, sun_strength=sun_strength)


def gabr(L, light=0.0, stages=4):
    P = S.tech_diver("gabr", light_energy=light, stages=stages)
    if light > 0:
        P["torch"].data.color = (0.85, 0.95, 1.0)
        S.no_shadow(P["torch"])
    return P


def snow(L, n, center, size, count=1500, emit=0.3, name="snow", radius=0.005):
    return L.particle_cloud(center, size, count=count, radius=radius, nframes=n, drift=(0.0, 0.0, 0.0), name=name,
                            mat=L.mat_principled(name + "m", (0.8, 0.9, 0.95), rough=1, emit=(0.6, 0.8, 0.9),
                                                 emit_strength=emit))


def matrix_rot(xcol, ycol, zcol):
    return Matrix((xcol, ycol, zcol)).transposed().to_euler()


# ----------------------------------------------------------------------------- S01 / S18 descent (loop pair)

def descent(L, n, s0, s1, cam_keys):
    underwater_world()
    S.world_volume(color=(0.05, 0.35, 0.55), density=0.03, anisotropy=0.6, absorption=(0.1, 0.4, 0.6),
                   center=(0, 0, -2), size=(16, 16, 18))
    sun = L.sun(rot=(0.2, 0.1, 0.0), energy=3.5, color=(0.7, 0.95, 1.0), angle=3)
    scr = L.link(bpy.data.objects.new("scroll", None))
    rope = S.descent_line(top=18, bottom=-40, radius=0.014)
    rope.parent = scr
    for k, z in enumerate([16 - 1.5 * i for i in range(38)]):
        t = S.depth_tag(f"{(k * 3) % 90 + 9}", loc=(0, 0, z), yaw=0.6 + (k % 2) * PI, scale=1.6, name=f"tg{k}",
                        rope_r=0.014, glow=0.15)
        t.parent = scr
    sn = snow(L, n, (0, 0, -6), (5, 5, 40), count=2600, emit=0.35)
    sn.parent = scr
    S.god_rays(center=(0.5, 1.0, 9), count=6, length=22, spread=3, tilt=(0.12, 0.06), color=(0.7, 0.95, 1.0),
               strength=1.0, alpha=0.16, nframes=n)
    scr.location = (0, 0, s0)
    scr.keyframe_insert("location", frame=1)
    scr.location = (0, 0, s1)
    scr.keyframe_insert("location", frame=n)
    L.linear_fcurves(scr)
    # diver head-first on the line (back +Y, belly toward the rope), hands forward on the rope
    P = gabr(L)
    r = P["root"]
    r.location = (0, 0.3, 0.0)
    r.rotation_euler = (-PI / 2, 0, 0)
    for tag, sx in (("L", -1), ("R", 1)):
        P[f"shoulder{tag}"].rotation_euler = (-0.45, 0, sx * 0.25)
    L.anim_swim(P, n, kick_rate=0.9, amp=0.12)
    starts = []
    for b in range(1, n + 1, 13):
        starts += [b + (i % 4) for i in range(8)]
    S.bubbles_at((0.0, 0.22, -0.72), starts, rise=SPEED + 1.0, spread=0.06, size=0.032, life=(16, 30), name="exh")
    rim(L, (-2.0, 2.2, -2.5), (0, 0.3, -0.3), energy=900, size=3, name="rimlow")
    rim(L, (2.5, 2.5, 2.0), (0, 0.3, 0.2), energy=500, size=3, color=(0.7, 0.95, 1.0), name="rimtop")
    cam, _ = L.camera(loc=cam_keys[0][1], target=CAM01_T, lens=24)
    L.cam_keys(cam, cam_keys)
    L.cam_light(cam, energy=50)
    L.handheld(cam, n, amp=0.012, rate=0.5, rot_amp=0.003)
    return cam


def S01(L, n):
    descent(L, n, 0.0, SPEED * n / 24, [(1, CAM01_A), (n, CAM01_B)])
    _finish(L)


def S18(L, n):
    c0 = CAM01_A + Vector((-0.25, 0.1, -0.3))
    descent(L, n, -SPEED * n / 24, 0.0, [(1, c0), (n, CAM01_A)])
    _finish(L)


# ----------------------------------------------------------------------------- S02 looking up the line

def S02(L, n):
    underwater_world(top=(0.3, 0.8, 0.88), horizon=(0.01, 0.08, 0.15), below=(0, 0.003, 0.008))
    pin = L.prim("ico", loc=(0.0, 1.5, 40), subdivisions=2, radius=1.0, name="surfacepin")
    L.assign(pin, L.mat_emission("pinm", (0.9, 1.0, 1.0), 25.0))
    S.world_volume(color=(0.05, 0.3, 0.5), density=0.02, absorption=(0.1, 0.4, 0.6), center=(0, 0, 4), size=(20, 20, 26))
    L.sun(rot=(0.05, 0.0, 0.0), energy=2.5, color=(0.7, 0.95, 1.0))
    S.descent_line(top=60, bottom=-12, radius=0.014)
    for k in range(10):
        t = S.depth_tag("", loc=(0, 0, 1.5 + k * 2.2), yaw=0.4 * k, scale=1.6, name=f"tg{k}", rope_r=0.014, glow=0.4)
    P = gabr(L)
    r = P["root"]
    S.pose_upright(P, yaw=0.0, reach=("R", "L"))
    P["shoulderL"].rotation_euler = (-0.9, 0, 0.35)
    base = Vector((0, -0.32, 0.0))
    S.bob(r, n, amp=0.03, rate=0.25, tilt=0.0, base=base)
    for f in range(1, n + 1, 2):
        r.rotation_euler = (PI / 2, 0, 0.03 * math.sin(f * 0.1))
        r.keyframe_insert("rotation_euler", frame=f)
    S.bubbles_at((0.0, -0.4, 0.75), [6 + i % 4 for i in range(9)] + [44 + i % 4 for i in range(9)], rise=1.1,
                 spread=0.07, size=0.035, life=(30, 50), name="breath")
    snow(L, n, (0, 0, 1), (6, 6, 10), count=1500, emit=0.3)
    S.god_rays(center=(0, 0.5, 14), count=5, length=14, spread=2.5, tilt=(0.05, 0.03), color=(0.7, 0.95, 1.0),
               strength=1.2, alpha=0.15, nframes=n)
    rim(L, (2.5, 1.5, 3.5), (0, -0.3, 0.3), energy=250, size=3, name="rimtop")
    a, b = Vector((1.25, -2.35, -3.4)), Vector((1.1, -2.1, -3.0))
    cam, _ = L.camera(loc=a, target=(0.0, -0.25, 0.9), lens=20)
    L.cam_keys(cam, [(1, a), (n, b)])
    L.cam_light(cam, energy=15)
    _finish(L)


# ----------------------------------------------------------------------------- S03 Dahab coast, back-roll entry

def S03(L, n):
    S.setup(vol_end=80)
    S.sky_gradient(top=(0.1, 0.3, 0.75), horizon=(0.5, 0.66, 0.85), strength=1.0, sun_dir=(0.45, -0.55, 0.7),
                   sun_col=(1, 0.95, 0.85), sun_strength=8.0, below=(0.1, 0.25, 0.3))
    L.sun(rot=(math.radians(40), 0, math.radians(-140)), energy=5.0, color=(1.0, 0.93, 0.82), angle=1.5)
    S.ocean(size=240, nframes=n, wave_scale=0.22, choppiness=0.8, resolution=9, spatial=60, wind=7, foam=True,
            mat=S.mat_ocean("redsea", deep=(0.0, 0.04, 0.16), shallow=(0.0, 0.2, 0.42), rough=0.12,
                            under=(0.3, 0.7, 0.8), under_strength=1.0))
    # fringing reef shallows: turquoise band along the shore
    reef = L.prim("plane", loc=(-30, 0, 0.03), size=1, name="reef")
    reef.scale = (10, 240, 1)
    L.assign(reef, L.mat_noise_surface("reefm", (0.08, 0.55, 0.55), (0.35, 0.8, 0.7), scale=0.3, rough=0.2, bump=0.1,
                                       voronoi=False))
    # desert shore + low hills (Sinai)
    sand = L.mat_noise_surface("dsand", (0.55, 0.4, 0.26), (0.78, 0.62, 0.42), scale=0.08, bump=0.3, voronoi=False)
    shore = L.prim("plane", loc=(-160, 0, 0.25), size=1, name="shore")
    shore.scale = (250, 300, 1)
    L.assign(shore, sand)
    hm = L.mat_noise_surface("hillm", (0.4, 0.27, 0.17), (0.7, 0.52, 0.34), scale=0.05, bump=0.6, voronoi=False)
    rnd = random.Random(4)
    for i in range(9):
        x = rnd.uniform(-170, -80)
        y = -120 + i * 30 + rnd.uniform(-10, 10)
        h = L.prim("ico", loc=(x, y, -6), subdivisions=4, radius=1, name="hill")
        h.scale = (rnd.uniform(25, 40), rnd.uniform(25, 45), rnd.uniform(16, 30))
        L.add_displace(h, strength=0.25, scale=0.4, name=f"hd{i}")
        L.assign(h, hm)
    # dive boat moored off the reef
    broot, _ = S.dive_boat("db")
    S.bob(broot, n, amp=0.06, rate=0.3, tilt=0.015, base=(0, 0, 0.1))
    buoy = L.prim("sphere", loc=(-4, 14, 0.1), radius=0.35, name="buoy")
    L.assign(buoy, L.mat_principled("buoym", (0.95, 0.4, 0.05), rough=0.4))
    # diver on the starboard gunwale, back to the sea, rolls backward at ~f62
    P = gabr(L)
    r = P["root"]
    piv = L.link(bpy.data.objects.new("rollpiv", None))
    r.parent = piv
    r.location = (-0.05, 0, 0.42)
    r.rotation_euler = (PI / 2, 0, PI / 2)
    for tag, sx in (("L", -1), ("R", 1)):
        P[f"hip{tag}"].rotation_euler = (1.45, 0, 0)
        P[f"knee{tag}"].rotation_euler = (-1.4, 0, 0)
        P[f"shoulder{tag}"].rotation_euler = (-2.3, 0, sx * -0.2)
    P["shoulderR"].rotation_euler = (-0.6, 0, 0.1)   # hand on mask
    roll = 62
    for f, loc, ry in ((1, (2.85, -4.6, 1.42), 0.0), (roll - 6, (2.85, -4.6, 1.42), -0.08), (roll, (2.9, -4.6, 1.42), 0.0),
                       (roll + 8, (3.4, -4.6, 1.1), 1.2), (roll + 14, (3.9, -4.6, 0.25), 2.2),
                       (roll + 24, (4.3, -4.6, -1.2), 2.9)):
        piv.location = loc
        piv.rotation_euler = (0, ry, 0)
        piv.keyframe_insert("location", frame=f)
        piv.keyframe_insert("rotation_euler", frame=f)
    hit = roll + 13
    S.splash_drops((3.9, -4.6, 0.1), [hit, hit + 1, hit + 2], count=70, speed=4.0, size=0.05)
    S.foam_patch((3.9, -4.6), 0.3, 1.8, hit, n, name="efoam")
    S.foam_patch((3.9, -4.6), 0.2, 1.0, hit + 6, n, name="efoam2")
    # camera: aerial (under the map card) -> 35 mm wide over the water at the cut
    cut = 44
    cam, _ = L.camera(loc=(-25, -20, 130), lens=35)
    look_keys(cam, [(1, (-8, -30, 48), (-6, 0, 0)), (cut - 1, (-7, -27, 44), (-6, 0, 0)),
                    (cut, (6.0, -10.0, 3.4), (2.8, -4.5, 1.3)), (n, (5.6, -9.4, 3.2), (2.9, -4.5, 1.2))])
    for fc in L_fc(cam):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT" if kp.co[0] == cut - 1 else "BEZIER"
    L.handheld(cam, n, amp=0.03, rate=0.5, rot_amp=0.004)
    _finish(L)


# ----------------------------------------------------------------------------- S04 kit reveal, struck-out submarine

def S04(L, n):
    underwater_world(top=(0.3, 0.8, 0.9), horizon=(0.03, 0.28, 0.42), below=(0.0, 0.05, 0.1), strength=1.0)
    S.world_volume(color=(0.1, 0.45, 0.6), density=0.025, absorption=(0.15, 0.45, 0.6), center=(0, 0, 0), size=(24, 24, 20))
    L.sun(rot=(0.25, 0.1, 0.4), energy=3.5, color=(0.75, 0.95, 1.0), angle=4)
    S.god_rays(center=(0, 3, 8), count=6, length=14, spread=4, tilt=(0.15, 0.05), color=(0.7, 0.95, 1.0),
               strength=1.0, alpha=0.15, nframes=n)
    S.descent_line(top=12, bottom=-12, radius=0.014)
    for k in range(6):
        S.depth_tag("", loc=(0, 0, -3 + k * 1.6), yaw=0.5 * k, scale=1.6, name=f"tg{k}", rope_r=0.014, glow=0.2)
    P = gabr(L)
    r = P["root"]
    S.pose_upright(P, yaw=0.0, reach=("R",))
    r.location = (0, -0.33, 0)
    for f, yaw in ((1, 0.35), (n, -0.35)):
        r.rotation_euler = (PI / 2, 0, yaw)
        r.keyframe_insert("rotation_euler", frame=f)
    S.bubbles_at((0, -0.45, 0.75), [10 + i % 4 for i in range(9)] + [50 + i % 4 for i in range(8)], rise=1.0,
                 spread=0.07, size=0.035, life=(30, 50), name="breath")
    snow(L, n, (0, 0, 0), (8, 8, 8), count=1500, emit=0.25)
    rim(L, (-2.5, 2.5, 2.5), (0, -0.3, 0), energy=700, size=3, name="rimA")
    rim(L, (2.5, 2.0, -1.0), (0, -0.3, -0.5), energy=400, size=3, name="rimB")
    # orbit 90 deg
    cen = Vector((0, -0.3, -0.25))
    keys = []
    for k in range(7):
        f = 1 + (n - 1) * k / 6
        a = math.radians(-70 + 90 * k / 6)
        keys.append((f, cen + Vector((math.sin(a) * 4.2, -math.cos(a) * 4.2, 0.45))))
    cam, _ = L.camera(loc=keys[0][1], target=cen, lens=35)
    L.cam_keys(cam, keys)
    L.cam_light(cam, energy=45)
    # ghost submarine (line art, parented to the camera, behind the diver) -> red strike -> slides away
    sub, sm = S.submarine_outline(length=4.8, f0=3, f1=12, width=0.03)
    sub.parent = cam
    for f, x in ((1, 3.5), (10, 0.0), (28, 0.0), (38, -7.0)):
        sub.location = (x, 1.15, -9.0)
        sub.keyframe_insert("location", frame=f)
    strike = S.draw_on_curve([(-2.4, -0.2, 0), (2.4, 1.3, 0)], 13, 18, color=(1.0, 0.12, 0.08), width=0.07,
                             strength=6.0, name="strike")
    strike.parent = sub
    _finish(L)


# ----------------------------------------------------------------------------- S05 depth ladder

def S05(L, n):
    underwater_world(top=(0.15, 0.6, 0.75), horizon=(0.02, 0.15, 0.3), below=(0.0, 0.01, 0.03), strength=1.0)
    vol = S.world_volume(color=(0.05, 0.35, 0.55), density=0.03, absorption=(0.1, 0.4, 0.6), center=(0, 0, 0),
                         size=(20, 20, 20))
    sun = L.sun(rot=(0.15, 0.05, 0.0), energy=3.0, color=(0.7, 0.95, 1.0))
    scr = L.link(bpy.data.objects.new("scroll", None))
    rope = S.descent_line(top=8, bottom=-30, radius=0.016)
    rope.parent = scr
    tick = L.mat_emission("tickm", (0.9, 0.95, 1.0), 1.5)
    for k in range(-8, 31):
        t = L.prim("cube", loc=(0, 0, -k * 1.0), name="tick")
        t.scale = (0.12 if k % 6 else 0.0, 0.01, 0.012)
        L.assign(t, tick)
        t.parent = scr
    pm = L.mat_principled("platem", (0.02, 0.03, 0.05), rough=0.4, alpha=0.75)
    pm.surface_render_method = "BLENDED"
    for k, lab in ((1, "100 m"), (2, "200 m"), (3, "300 m")):
        z = -6.0 * k
        bar = L.prim("cube", loc=(-0.6, 0, z), name="mark")
        bar.scale = (0.7, 0.02, 0.025)
        L.assign(bar, L.mat_emission(f"markm{k}", YEL, 4.0))
        bar.parent = scr
        pl = L.prim("cube", loc=(-0.85, 0.05, z + 0.3), name="plate")
        pl.scale = (0.5, 0.02, 0.2)
        L.bevel(pl, 0.03)
        L.assign(pl, pm)
        pl.parent = scr
        tx = L.text3d(lab, loc=(-0.85, 0.0, z + 0.21), size=0.27, extrude=0.01, mat=L.mat_emission(f"txm{k}", (1, 1, 1), 3.0),
                      name=f"plate{k}")
        tx.parent = scr
    fish = L.fish_school((1.2, 1.5, -3.5), count=22, radius=1.4, nframes=n, size=0.09, color=(0.7, 0.8, 0.9))
    fish.parent = scr
    sn = snow(L, n, (0, 0, -9), (6, 6, 34), count=2600, emit=0.3)
    sn.parent = scr
    for f, z in ((1, 2.6), (8, 5.7), (28, 11.7), (45, 17.7), (n, 21.0)):
        scr.location = (0, 0, z)
        scr.keyframe_insert("location", frame=f)
    # diver head-first beside the rope, side-on to camera
    P = gabr(L, light=260)
    r = P["root"]
    r.location = (0.32, 0.0, -0.1)
    r.rotation_euler = (-PI / 2, 0, -PI / 2)   # head down, belly toward the rope (-X)
    for tag, sx in (("L", -1), ("R", 1)):
        P[f"shoulder{tag}"].rotation_euler = (-0.4, 0, sx * 0.25)
    L.anim_swim(P, n, kick_rate=0.9, amp=0.12)
    tb = S.beam_cone((0.32, 0.0, -0.85), (0, 0, -1), length=4, radius=0.7, color=(0.85, 0.95, 1.0), strength=1.2,
                     alpha=0.12, name="torchcone")
    starts = []
    for b in range(1, n + 1, 14):
        starts += [b + (i % 4) for i in range(7)]
    S.bubbles_at((0.32, 0.0, -0.72), starts, rise=3.4, spread=0.06, size=0.032, life=(14, 26), name="exh")
    # colour drains: blue -> indigo -> black
    key_input(bg_node().inputs[1], [(1, 1.0), (28, 0.35), (50, 0.05), (n, 0.03)])
    key_input(vol.inputs["Color"], [(1, (0.05, 0.35, 0.55, 1)), (28, (0.08, 0.08, 0.4, 1)), (50, (0.02, 0.02, 0.06, 1))])
    S.energy_keys(sun, [(1, 3.0), (28, 1.2), (50, 0.1)])
    fl = rim(L, (-2.0, 2.0, 1.5), (0.3, 0, -0.3), energy=600, size=3, name="rimA")
    S.energy_keys(fl, [(1, 600), (40, 250)])
    cam, _ = L.camera(loc=(0.0, -3.7, -0.35), target=(-0.05, 0.0, -0.3), lens=28)
    L.cam_keys(cam, [(1, (0.0, -3.7, -0.35)), (n, (-0.1, -3.45, -0.35))])
    cl = L.cam_light(cam, energy=40)
    L.handheld(cam, n, amp=0.02, rate=0.5)
    _finish(L)


# ----------------------------------------------------------------------------- S06 / S07 / S17 rope macro

def rope_macro_env(L, n, bg=(0.0, 0.006, 0.014), vol=0.06):
    S.setup(vol_end=8)
    L.set_world(color=bg, strength=1.0)
    S.world_volume(color=(0.2, 0.45, 0.6), density=vol, absorption=(0.1, 0.35, 0.5), center=(0, -0.5, 0), size=(4, 4, 4))


def glove(L, name="glove"):
    return S.hand(name, color=(0.035, 0.035, 0.04), scale=1.15, glove=True)


def S06(L, n):
    rope_macro_env(L, n)
    scr = L.link(bpy.data.objects.new("scroll", None))
    rope = S.descent_line(top=3, bottom=-3, radius=0.012)
    rope.parent = scr
    for k, lab in enumerate(("290 m", "300 m", "310 m", "320 m")):
        t = S.depth_tag(lab, loc=(0, 0, 0.42 - k * 0.36), yaw=0.15, scale=1.0, name=f"tg{k}", glow=0.05)
        t.parent = scr
    for f, z in ((1, 0.0), (n, 0.32)):
        scr.location = (0, 0, z)
        scr.keyframe_insert("location", frame=f)
    L.linear_fcurves(scr)
    # glove loosely around the rope, sliding down past the tags
    H = glove(L)
    hr = H["root"]
    hr.rotation_euler = matrix_rot((0, 0, -1), (1, 0, 0), (0, -1, 0))
    for f, z in ((1, 0.32), (n, -0.12)):
        hr.location = (-0.075, -0.03, z)
        hr.keyframe_insert("location", frame=f)
    S.curl(H, 1, 0.9)
    sp = L.spot((-0.55, -0.7, 0.55), (0, 0, 0), energy=90, size_deg=30, blend=0.3, color=(0.85, 0.93, 1.0),
                name="torch", radius=0.01)
    _aim(sp, (-0.55, -0.7, 0.55), (0, 0, 0.05))
    rim(L, (0.6, 0.6, 0.6), (0, 0, 0.1), energy=20, size=1, name="rimbk")
    L.particle_cloud((0, -0.3, 0.1), (0.9, 0.6, 1.0), count=350, radius=0.0008, nframes=n, drift=(0.01, 0, 0.03),
                     name="backscatter", mat=L.mat_principled("bsm", (0.9, 0.95, 1.0), emit=(0.8, 0.9, 1.0), emit_strength=0.6))
    cam = L.camera(loc=(0.05, -0.52, 0.08), lens=50)[0]
    look_keys(cam, [(1, (0.05, -0.78, 0.1), (0, 0, 0.06)), (n, (0.05, -0.74, 0.04), (0, 0, 0.0))], roll=-0.55)
    L.handheld(cam, n, amp=0.004, rate=0.5, rot_amp=0.003)
    L.cam_light(cam, energy=4)
    _finish(L)


def S07(L, n):
    rope_macro_env(L, n, bg=(0.0, 0.002, 0.005), vol=0.05)
    S.descent_line(top=3, bottom=-0.25, radius=0.012)
    wt = L.prim("cyl", loc=(0, 0, -0.32), vertices=16, radius=0.05, depth=0.14, name="weight")
    L.assign(wt, L.mat_principled("leadm", (0.18, 0.18, 0.2), rough=0.4, metal=0.6))
    tag = S.depth_tag("332 m", loc=(0, 0, 0.06), yaw=0.15, scale=1.15, name="tag332", glow=0.08)
    H = glove(L)
    hr = H["root"]
    grab, off = 22, 26
    # hand comes in from the left, pinches the tag, pulls it off toward camera
    hr.rotation_euler = matrix_rot((0, 0, -1), (1, 0, 0), (0, -1, 0))
    hk = [(1, (-0.4, -0.05, 0.15)), (grab, (-0.115, 0.0, 0.005)), (off, (-0.115, -0.005, 0.005)),
          (off + 12, (-0.2, -0.12, 0.06)), (n, (-0.21, -0.14, 0.07))]
    for f, p in hk:
        hr.location = p
        hr.keyframe_insert("location", frame=f)
    S.curl(H, 1, 0.3)
    S.curl(H, grab, 0.3)
    S.curl(H, grab + 3, 1.1)
    for f, p in ((1, (0, 0, 0.06)), (off, (0, 0, 0.06)), (off + 12, (-0.085, -0.125, 0.115)), (n, (-0.095, -0.14, 0.125))):
        tag.location = p
        tag.keyframe_insert("location", frame=f)
    tie = bpy.data.objects["tag332_tie"]
    for f, s in ((off - 1, 1.0), (off, 0.001)):
        tie.scale = (s,) * 3
        tie.keyframe_insert("scale", frame=f)
    S.bubbles_at((-0.3, 0.25, -0.35), [1 + i % 6 for i in range(16)], rise=0.7, spread=0.06, size=0.018, life=(30, 50),
                 name="burst")
    sp = L.spot((-0.5, -0.55, 0.5), (0, 0, 0), energy=80, size_deg=26, blend=0.35, color=(0.85, 0.93, 1.0),
                name="torch", radius=0.01)
    _aim(sp, (-0.5, -0.55, 0.5), (0, 0, 0.02))
    gl = L.point((0.03, -0.12, 0.1), energy=0, color=(1, 1, 1), radius=0.02, name="glint")
    S.no_shadow(gl)
    S.energy_keys(gl, [(30, 0), (34, 4), (40, 0.5)])
    L.particle_cloud((0, -0.25, 0.05), (0.8, 0.5, 0.8), count=300, radius=0.0008, nframes=n, drift=(0.01, 0, 0.02),
                     name="backscatter", mat=L.mat_principled("bsm", (0.9, 0.95, 1.0), emit=(0.8, 0.9, 1.0), emit_strength=0.5))
    cam = L.camera(loc=(0.03, -0.6, 0.1), lens=45)[0]
    look_keys(cam, [(1, (0.03, -0.62, 0.12), (-0.03, 0, 0.0)), (grab, (0.02, -0.6, 0.1), (-0.04, 0, 0.0)),
                    (n, (0.0, -0.58, 0.12), (-0.07, -0.08, 0.06))])
    for f, l_ in ((1, 40), (grab, 42), (grab + 5, 55), (n, 57)):
        cam.data.lens = l_
        cam.data.keyframe_insert("lens", frame=f)
    S.shake(cam, 34, length=6, amp=0.006, rot=0.01)
    L.cam_light(cam, energy=3)
    _finish(L)


def S17(L, n):
    rope_macro_env(L, n, bg=(0.0, 0.002, 0.006), vol=0.05)
    S.descent_line(top=3, bottom=-0.6, radius=0.012)
    tag = S.depth_tag("330 m", loc=(0, 0, 0.12), yaw=0.15, scale=1.15, name="tagl", glow=0.0)
    pm = bpy.data.materials["tagl_w"]
    p = pm.node_tree.nodes["Principled BSDF"]
    key_input(p.inputs["Emission Strength"], [(1, 0.05), (20, 0.25), (24, 0.25), (25, 0.04), (n, 0.03)])
    off = 24
    sp = L.spot((-0.5, -0.55, 0.45), (0, 0, 0), energy=80, size_deg=24, blend=0.35, color=(0.85, 0.93, 1.0),
                name="torch", radius=0.01)
    _aim(sp, (-0.5, -0.55, 0.45), (0, 0, 0.05))
    S.energy_keys(sp, [(1, 80), (off, 80), (off + 1, 0)], "CONSTANT")
    gl = L.point((0.035, -0.1, 0.12), energy=0, color=(1, 1, 1), radius=0.02, name="glint")
    S.no_shadow(gl)
    S.energy_keys(gl, [(6, 0), (12, 6), (18, 1), (off, 1), (off + 1, 0)])
    amb = rim(L, (0.3, 0.6, 1.2), (0, 0, 0.0), energy=6, size=1.5, color=(0.3, 0.55, 0.8), name="ghost")
    L.particle_cloud((0, -0.25, 0.1), (0.8, 0.5, 0.8), count=300, radius=0.0008, nframes=n, drift=(0.01, 0, 0.02),
                     name="backscatter", mat=L.mat_principled("bsm", (0.9, 0.95, 1.0), emit=(0.8, 0.9, 1.0), emit_strength=0.4))
    cam = L.camera(loc=(0.03, -0.55, 0.12), lens=50)[0]
    look_keys(cam, [(1, (0.04, -0.56, 0.14), (0, 0, 0.08)), (n, (0.0, -0.5, 0.1), (0, 0, 0.07))], roll=-0.2)
    L.handheld(cam, n, amp=0.003, rate=0.4, rot_amp=0.002)
    _finish(L)


# ----------------------------------------------------------------------------- S08 Eiffel comparison

def S08(L, n):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0)
    S.backdrop_z(stops=((-36, (0.0, 0.003, 0.008)), (-20, (0.005, 0.04, 0.08)), (-4, (0.03, 0.3, 0.4)),
                        (0.0, (0.3, 0.8, 0.85)), (0.05, (0.75, 0.85, 0.95)), (40, (0.25, 0.45, 0.8))),
                 loc=(0, 40, 0), size=(300, 300), strength=1.0)
    surf = L.prim("cube", loc=(0, 0, 0), name="surfline")
    surf.scale = (80, 0.05, 0.06)
    L.assign(surf, L.mat_emission("surfm", (0.85, 1.0, 1.0), 6.0))
    rm = L.mat_emission("ropem", (0.95, 0.95, 0.9), 2.5)
    rope = L.prim("cyl", loc=(0, 0, -16.6), vertices=8, radius=0.006, depth=33.2, name="rope")
    L.assign(rope, rm)
    for f, s_ in ((1, 1.0), (12, 2.0), (32, 6.0), (n, 9.0)):
        rope.scale = (s_, s_, 1)
        rope.keyframe_insert("scale", frame=f)
    broot, _ = S.dive_boat("db")
    broot.scale = (0.12, 0.12, 0.12)
    broot.location = (-0.6, 0.0, 0.0)
    L.sun(rot=(0.6, 0.2, 0.5), energy=3)
    tm, thr = S.mat_reveal_z("towerm", TEAL, 5.0, soft=1.0, alpha=0.9)
    S.lattice_tower(base_z=-33.2, height=33.0, half_base=6.25, center=(8.2, 0.0), mat=tm, bevel=0.09)
    key_input(thr, [(1, -33.5), (6, -31.0), (40, 1.5)])
    # tiny diver at the bottom of the rope (to scale: 1 unit = 10 m)
    P = gabr(L, light=0.0)
    r = P["root"]
    S.pose_upright(P, yaw=-0.4, reach=("R",))
    r.scale = (0.1, 0.1, 0.1)
    r.location = (-0.035, -0.03, -33.05)
    pl = L.point((0.3, -0.6, -32.7), energy=6, color=(0.8, 0.95, 1.0), radius=0.1, name="fill")
    glow = L.prim("ico", loc=(0.0, -0.06, -32.98), subdivisions=1, radius=0.007, name="lamp")
    L.assign(glow, L.mat_emission("lampm", (1, 0.95, 0.85), 20))
    cam, _ = L.camera(loc=(0.4, -0.55, -32.95), lens=35)
    T0 = Vector((-0.02, 0, -33.0))
    T1 = Vector((4.6, 0, -13.2))
    keys = [(1, 0.0, 0.62), (8, 0.06, 3.0), (18, 0.25, 12.0), (32, 0.7, 36.0), (46, 0.95, 52.0), (n, 1.0, 56.0)]
    out = []
    for f, u, d in keys:
        t = T0.lerp(T1, u)
        p = t + Vector((0.55, -1.0, 0.08)).normalized() * d * (1 - u) + Vector((0, -d, 0)) * u
        out.append((f, p, t))
    look_keys(cam, out)
    _finish(L)


# ----------------------------------------------------------------------------- S09 record bars

def S09(L, n):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0)
    S.backdrop_z(stops=((-12, (0.0, 0.004, 0.01)), (-4, (0.005, 0.03, 0.06)), (2, (0.02, 0.12, 0.18)),
                        (8, (0.03, 0.2, 0.28))), loc=(0, 10, 0), size=(80, 80))
    U = 1 / 6.0  # 1 unit = 6 m, axis starts at 300 m
    axis = L.prim("cube", loc=(0, 0, 0.0), name="axis")
    axis.scale = (3.4, 0.03, 0.03)
    L.assign(axis, L.mat_emission("axism", (0.85, 0.9, 0.95), 2.5))
    L.text3d("300 m", loc=(-3.45, 0, 0.25), size=0.38, align="LEFT", mat=L.mat_emission("axt", (0.75, 0.85, 0.9), 2.0))

    def bar(x, metres, col, f0, f1, name):
        h = (metres - 300) * U
        piv = L.link(bpy.data.objects.new(name + "piv", None))
        piv.location = (x, 0, 0)
        b = L.prim("cube", loc=(0, 0, -0.5), name=name)
        b.scale = (1.0, 0.25, 0.5)
        b.parent = piv
        L.assign(b, L.mat_principled(name + "m", col, rough=0.4, emit=col, emit_strength=0.6))
        for f, s in ((f0, 0.001), (f1, h)):
            piv.scale = (1, 1, s)
            piv.keyframe_insert("scale", frame=f)
        return piv, h
    g, hg = bar(-1.3, 318.25, (0.45, 0.47, 0.5), 3, 22, "bar05")
    y, hy = bar(1.3, 332.35, YEL, 18, 40, "bar14")
    L.text3d("2005", loc=(-1.3, 0, 0.45), size=0.7, mat=L.mat_emission("t05", (0.8, 0.82, 0.85), 2.0))
    L.text3d("2014", loc=(1.3, 0, 0.45), size=0.7, mat=L.mat_emission("t14", YEL, 3.0))
    v1 = L.text3d("318.25", loc=(-1.3, -0.3, -hg + 0.35), size=0.42, mat=L.mat_emission("v05", (1, 1, 1), 2.5))
    v2 = L.text3d("332.35", loc=(1.3, -0.3, -hy + 0.35), size=0.42, mat=L.mat_emission("v14", (0.05, 0.04, 0.0), 1.0))
    for o, f in ((v1, 22), (v2, 40)):
        o.scale = (0.001,) * 3
        o.keyframe_insert("scale", frame=f - 1)
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=f + 3)
    # dashed line at the old mark: the new bar passes it
    dm = L.mat_emission("dashm", (0.9, 0.9, 0.9), 2.0)
    for k in range(9):
        d = L.prim("cube", loc=(-0.2 + k * 0.32, -0.3, -hg), name="dash")
        d.scale = (0.1, 0.01, 0.025)
        L.assign(d, dm)
    snow(L, n, (0, -1, -3), (12, 4, 14), count=900, emit=0.25)
    L.sun(rot=(0.5, 0.2, 0.3), energy=2.5)
    cam, _ = L.camera(loc=(0, -16, -1.2), target=(0, 0, -1.6), lens=35)
    L.cam_keys(cam, [(1, (0, -16.5, -1.2)), (n, (0, -15.0, -1.3))])
    _finish(L)


# ----------------------------------------------------------------------------- S10 looking up the endless rope

def S10(L, n):
    underwater_world(top=(0.004, 0.02, 0.035), horizon=(0.0, 0.004, 0.01), below=(0.0, 0.0, 0.003))
    pin = L.prim("ico", loc=(0.0, 1.0, 45), subdivisions=2, radius=0.2, name="surfacepin")
    L.assign(pin, L.mat_emission("pinm", (0.8, 0.95, 1.0), 6.0))
    S.world_volume(color=(0.2, 0.45, 0.6), density=0.05, absorption=(0.1, 0.35, 0.5), center=(0, 0, 4), size=(12, 12, 20))
    S.descent_line(top=40, bottom=-3, radius=0.014)
    for k in range(8):
        S.depth_tag("", loc=(0, 0, 1.4 + k * 1.7), yaw=0.4 * k, scale=1.6, name=f"tg{k}", rope_r=0.014, glow=0.05)
    P = gabr(L, light=500)
    r = P["root"]
    S.pose_upright(P, yaw=0.0, reach=("R", "L"))
    r.location = (0, -0.33, 0)
    for f, lean in ((1, 0.0), (n, -0.35)):
        r.rotation_euler = (PI / 2 + lean, 0, 0.1)
        r.keyframe_insert("rotation_euler", frame=f)
    S.energy_keys(P["torch"], [(1, 500), (28, 500), (n, 160)])
    tb = S.beam_cone((0, -0.3, 0.8), (0, 0.12, 1), length=7, radius=0.9, color=(0.85, 0.95, 1.0), strength=1.4,
                     alpha=0.16, name="torchcone")
    snow(L, n, (0, 0, 3), (5, 5, 12), count=1800, emit=0.25)
    rim(L, (1.8, 1.5, -1.0), (0, -0.3, 0.2), energy=180, size=2, name="rimA")
    S.bubbles_at((0, -0.45, 0.75), [4 + i % 4 for i in range(8)], rise=1.0, spread=0.07, size=0.035, life=(30, 44),
                 name="breath")
    tgt = L.link(bpy.data.objects.new("tgt", None))
    for f, p in ((1, (0, -0.25, -0.2)), (10, (0, -0.2, 0.3)), (n, (0, 0.05, 7.5))):
        tgt.location = p
        tgt.keyframe_insert("location", frame=f)
    cam, _ = L.camera(loc=(1.7, -2.7, -0.3), target=tgt, lens=24)
    L.cam_keys(cam, [(1, (1.7, -2.7, -0.3)), (n, (1.3, -2.1, -0.6))])
    L.cam_light(cam, energy=20)
    _finish(L)


# ----------------------------------------------------------------------------- S11 x-ray bends diagram

def S11(L, n):
    L.set_world(color=(0, 0, 0), strength=0)
    S.diagram_grid(y=1.5, step=0.25, extent=6)
    F = L.char_figure("xfig", height=1.75)
    S.restyle("xfig", S.mat_xray("xfm", TEAL, 2.5, power=1.6, base=0.03))
    for tag, sx in (("L", -1), ("R", 1)):
        F[f"shoulder{tag}"].rotation_euler = (0, sx * 0.25, 0)
    rnd = random.Random(5)
    dm = L.mat_emission("dotm", (0.6, 1.0, 0.95), 4.0)
    # dissolved gas dots inside torso / thighs / arms
    regions = [((0, 0, 1.27), (0.15, 0.08, 0.28), 40), ((-0.1, 0, 0.72), (0.05, 0.04, 0.2), 10), ((0.1, 0, 0.72), (0.05, 0.04, 0.2), 10),
               ((-0.1, 0, 0.3), (0.04, 0.03, 0.18), 7), ((0.1, 0, 0.3), (0.04, 0.03, 0.18), 7),
               ((-0.24, 0, 1.25), (0.03, 0.03, 0.15), 5), ((0.24, 0, 1.25), (0.03, 0.03, 0.15), 5)]
    swell0 = 40
    for (c, s, cnt) in regions:
        for i in range(cnt):
            p = Vector(c) + Vector((rnd.uniform(-1, 1) * s[0], rnd.uniform(-1, 1) * s[1] - 0.05, rnd.uniform(-1, 1) * s[2]))
            d = L.prim("ico", loc=p, subdivisions=1, radius=0.011, name="dot")
            L.assign(d, dm)
            st = swell0 + rnd.randint(0, 22)
            for f, sc in ((1, 0.001), (3 + rnd.randint(0, 10), 1.0), (st, 1.0), (st + 8, rnd.uniform(2.6, 4.0))):
                d.scale = (sc,) * 3
                d.keyframe_insert("scale", frame=f)
    S.emit_keys(dm, [(1, 4.0), (swell0, 4.0), (swell0 + 20, 6.0)], [(swell0, (0.6, 1.0, 0.95)), (swell0 + 20, (1.0, 0.95, 0.9))])
    # fast upward arrow
    ax = 0.62
    S.draw_on_curve([(ax, -0.05, 0.1), (ax, -0.05, 1.75)], 16, 30, color=YEL, width=0.03, strength=4.0, name="arrow")
    S.draw_on_curve([(ax - 0.14, -0.05, 1.58), (ax, -0.05, 1.76), (ax + 0.14, -0.05, 1.58)], 28, 33, color=YEL,
                    width=0.03, strength=4.0, name="arrowhead")
    # red X on "the bends"
    xf = 74
    xr = L.link(bpy.data.objects.new("xroot", None))
    xr.location = (ax, -0.12, 0.95)
    xm = L.mat_emission("xm", (1.0, 0.12, 0.08), 6.0)
    for a in (0.75, -0.75):
        b = L.prim("cube", loc=(0, 0, 0), rot=(0, a, 0), name="xbar")
        b.scale = (0.4, 0.02, 0.05)
        L.assign(b, xm)
        b.parent = xr
    for f, s in ((xf - 1, 0.001), (xf, 1.5), (xf + 3, 1.0)):
        xr.scale = (s,) * 3
        xr.keyframe_insert("scale", frame=f)
    cam, _ = L.camera(loc=(0.1, -10, 0.8), lens=50)
    cam.rotation_euler = (PI / 2, 0, 0)
    cam.data.type = "ORTHO"
    for f, s in ((1, 4.4), (n, 4.1)):
        cam.data.ortho_scale = s
        cam.data.keyframe_insert("ortho_scale", frame=f)
    cam.keyframe_insert("location", frame=1)
    S.shake(cam, xf, length=6, amp=0.05, rot=0.01)
    _finish(L)


# ----------------------------------------------------------------------------- S12 decompression stops

def S12(L, n):
    underwater_world(top=(0.35, 0.85, 0.9), horizon=(0.05, 0.35, 0.5), below=(0.0, 0.08, 0.14), strength=0.9)
    vol = S.world_volume(color=(0.12, 0.5, 0.65), density=0.025, absorption=(0.2, 0.5, 0.65), center=(0, 0, 2),
                         size=(24, 24, 22))
    sun = L.sun(rot=(0.25, 0.1, 0.4), energy=2.5, color=(0.75, 0.95, 1.0), angle=4)
    S.energy_keys(sun, [(1, 2.5), (n, 4.5)])
    key_input(bg_node().inputs[1], [(1, 0.85), (n, 1.35)])
    key_input(vol.inputs["Color"], [(1, (0.1, 0.45, 0.65, 1)), (n, (0.25, 0.6, 0.6, 1))])
    S.god_rays(center=(0, 3, 12), count=7, length=16, spread=4, tilt=(0.15, 0.05), color=(0.8, 1.0, 0.95),
               strength=1.1, alpha=0.16, nframes=n)
    S.descent_line(top=14, bottom=-8, radius=0.014)
    stops = ("30 m", "27 m", "24 m", "21 m")
    for k, lab in enumerate(stops):
        z = -0.55 + k * 1.3
        pl = L.prim("cube", loc=(-0.42, 0.0, z), name="stopplate")
        pl.scale = (0.26, 0.01, 0.1)
        L.bevel(pl, 0.02)
        L.assign(pl, L.mat_principled(f"spm{k}", (0.95, 0.8, 0.1), rough=0.4, emit=YEL, emit_strength=0.3))
        tx = L.text3d(lab, loc=(-0.42, -0.02, z - 0.05), size=0.13, extrude=0.003,
                      mat=L.mat_principled(f"stx{k}", (0.02, 0.02, 0.02), rough=0.5))
    # second line with fresh stage tanks coming down
    S.descent_line(top=14, bottom=-6, x=1.35, y=0.7, radius=0.01, name="supply")
    for k, (f0, f1, z0, z1) in enumerate(((1, 50, 4.5, 0.6), (38, n, 6.5, 2.2))):
        t = S.stage_tank(loc=(1.43, 0.7, z0), band=((0.15, 0.6, 0.3), (0.95, 0.75, 0.1))[k], name=f"fresh{k}")
        for f, z in ((f0, z0), (f1, z1)):
            t.location = (1.43, 0.7, z)
            t.keyframe_insert("location", frame=f)
    # Gabr hangs on the main line; steps up stop by stop
    P = gabr(L, stages=3)
    r = P["root"]
    S.pose_upright(P, yaw=0.0, reach=("R",))
    for f, z in ((1, 0.0), (24, 0.0), (34, 1.3), (60, 1.3), (70, 2.6), (n, 2.6)):
        r.location = (0, -0.33, z)
        r.keyframe_insert("location", frame=f)
    # spent stage cylinders sent up
    for k, (f0, dx) in enumerate(((16, -0.5), (58, 0.5))):
        t = S.stage_tank(loc=(dx, -0.35, -0.3), rot=(0.3, 0, 0), band=(0.9, 0.9, 0.86), name=f"spent{k}")
        z0 = -0.3 + (1.3 if f0 > 40 else 0)
        for f, z, rx in ((1, z0, 0.3), (f0, z0, 0.3), (f0 + 14, z0 + 1.2, 0.6), (f0 + 40, z0 + 6.5, 1.0)):
            t.location = (dx, -0.4, z)
            t.rotation_euler = (rx, 0.2, 0)
            t.keyframe_insert("location", frame=f)
            t.keyframe_insert("rotation_euler", frame=f)
        S.bubbles_at((dx, -0.4, z0 + 0.4), [f0 + i % 3 for i in range(6)], rise=1.0, spread=0.05, size=0.03,
                     life=(20, 30), name=f"sb{k}")
    for k in range(4):
        S.bubbles_at((0, -0.45, 0.75 + (0 if k < 2 else 1.3 * (k - 1))), [8 + k * 24 + i % 4 for i in range(7)], rise=1.0,
                     spread=0.07, size=0.035, life=(28, 44), name=f"br{k}")
    # two support divers in the background
    for k, (loc, yaw) in enumerate((((-3.2, 4.5, 2.0), 0.9), ((3.0, 5.5, 3.3), -2.2))):
        D = L.char_diver(name=f"sup{k}", suit=(0.05, 0.06, 0.08), accent=(0.85, 0.1, 0.08), tanks="single", light_on=False)
        D["root"].location = loc
        D["root"].rotation_euler = (0, 0, yaw)
        L.anim_swim(D, n, kick_rate=0.6, amp=0.25)
    snow(L, n, (0, 0, 2), (8, 8, 10), count=1300, emit=0.2)
    rim(L, (-2.2, 2.2, 3.0), (0, -0.3, 1.2), energy=600, size=3, name="rimA")
    cam, _ = L.camera(loc=(1.8, -4.4, -0.2), target=(0.2, 0, 0.0), lens=28)
    tgt = cam.constraints[0].target
    for f, cz, tz in ((1, -0.4, -0.05), (n, 2.2, 2.4)):
        cam.location = (1.4, -3.5, cz)
        cam.keyframe_insert("location", frame=f)
        tgt.location = (0.25, 0, tz)
        tgt.keyframe_insert("location", frame=f)
    L.cam_light(cam, energy=35)
    _finish(L)


# ----------------------------------------------------------------------------- S13 night surface off Dahab

def S13(L, n):
    S.setup(vol_end=60)
    S.sky_gradient(top=(0.003, 0.006, 0.02), horizon=(0.02, 0.035, 0.07), strength=1.0, below=(0.005, 0.01, 0.02))
    moon = L.prim("ico", loc=(-60, 160, 75), subdivisions=3, radius=3.0, name="moon")
    L.assign(moon, L.mat_emission("moonm", (0.85, 0.9, 1.0), 6.0))
    L.sun(rot=(math.radians(60), 0, math.radians(200)), energy=0.35, color=(0.65, 0.78, 1.0), angle=1)
    S.ocean(size=120, nframes=n, wave_scale=0.45, choppiness=0.8, resolution=10, spatial=40, wind=8, foam=False,
            mat=S.mat_ocean("nightsea", deep=(0.0, 0.015, 0.035), shallow=(0.01, 0.05, 0.09), rough=0.18, foam=False,
                            under=(0.05, 0.1, 0.12), under_strength=0.3))
    broot, _ = S.dive_boat("db")
    broot.rotation_euler = (0, 0, PI / 2 + 0.25)
    S.bob(broot, n, amp=0.04, rate=0.25, tilt=0.01, base=(-4.0, 19.0, 0.1))
    warm = L.mat_emission("winm", (1.0, 0.75, 0.45), 1.2)
    for o in bpy.data.objects:
        if o.name.startswith("db_win"):
            L.assign(o, warm)
    for k, loc in enumerate(((0, -4.5, 3.0), (0, 2.0, 3.2), (2.5, -2.0, 2.2), (-2.5, -2.0, 2.2))):
        pt = L.point(loc, energy=70, color=(1.0, 0.72, 0.4), radius=0.3, name=f"deck{k}")
        pt.parent = broot
    for k, loc in enumerate(((2.2, -2.5, 1.3), (1.7, -5.0, 1.3))):
        F = L.char_figure(name=f"crew{k}", color=(0.02, 0.02, 0.025), height=1.75)
        F["root"].parent = broot
        F["root"].location = loc
        F["root"].rotation_euler = (0, 0, PI / 2 + 0.3)
    # Gabr's head and torch break the surface
    W = S.swimmer("gabrs", suit=(0.025, 0.025, 0.03), bcd=(0.06, 0.06, 0.07), tank=True)
    wr = W["root"]
    brk = 50
    for f, z in ((1, -0.9), (brk - 6, -0.55), (brk, -0.02), (brk + 6, 0.06), (n, 0.02)):
        wr.location = (0.2, 1.4, z)
        wr.rotation_euler = (0, 0, PI - 0.5)
        wr.keyframe_insert("location", frame=f)
    lamp = L.prim("cyl", loc=(0.45, 1.05, 0.15), rot=(1.2, 0, 0.6), vertices=10, radius=0.035, depth=0.2, name="torchbody")
    L.assign(lamp, L.mat_principled("torchm", (0.1, 0.1, 0.11), rough=0.3, metal=0.6))
    lens = L.prim("ico", loc=(0.0, 0, 0.11), subdivisions=2, radius=0.04, name="torchlens")
    lm = L.mat_emission("tlens", (0.9, 0.97, 1.0), 25.0)
    L.assign(lens, lm)
    lens.parent = lamp
    tl = L.spot((0, 0, 0.13), (0, 0, 0), energy=250, size_deg=35, blend=0.5, color=(0.9, 0.97, 1.0), name="torch")
    tl.parent = lamp
    tl.rotation_euler = (PI, 0, 0)
    for f, z in ((1, -0.95), (brk - 4, -0.55), (brk + 2, 0.12), (brk + 8, 0.2), (n, 0.18)):
        lamp.location = (0.5, 1.05, z)
        lamp.keyframe_insert("location", frame=f)
    S.bubbles_at((0.2, 1.4, -0.05), [4 + i * 2 for i in range(20)], rise=0.15, spread=0.15, size=0.04, life=(6, 12),
                 name="boil")
    S.splash_drops((0.2, 1.4, 0.0), [brk, brk + 1], count=40, speed=2.5, size=0.03)
    rim(L, (-1.5, 4.5, 1.5), (0.2, 1.4, 0.2), energy=60, size=2, color=(1.0, 0.75, 0.45), name="boatrim")
    cam, _ = L.camera(loc=(1.35, -1.05, 0.33), target=(0.0, 2.2, 0.45), lens=35)
    L.cam_keys(cam, [(1, (1.35, -1.05, 0.33)), (n, (1.15, -0.65, 0.3))])
    L.handheld(cam, n, amp=0.03, rate=0.5, rot_amp=0.006)
    L.cam_light(cam, energy=8, color=(0.6, 0.75, 1.0))
    _finish(L)


# ----------------------------------------------------------------------------- S14 / S15 / S16 desk

def desk(L, n, light=(0.7, 0.85, 1.0), energy=60):
    L.set_world(color=(0.002, 0.003, 0.005), strength=1.0)
    d = L.prim("plane", loc=(0, 0, 0), size=3, name="desk")
    L.assign(d, L.mat_noise_surface("deskm", (0.02, 0.018, 0.016), (0.07, 0.06, 0.05), scale=3, rough=0.6, bump=0.1,
                                    voronoi=False))
    sp = L.spot((0.1, 0.1, 1.5), (0, 0, 0), energy=energy, size_deg=55, blend=0.6, color=light, name="top", radius=0.04)
    _aim(sp, (0.1, 0.1, 1.5), (0, 0.05, 0))
    return sp


def S14(L, n):
    desk(L, n, energy=70)
    sheets = []
    for k, (x, y, rz, red) in enumerate(((0.02, 0.06, -0.08, (1, 2, 4, 6, 7)), (-0.07, 0.15, 0.1, (0, 3, 5, 8)),
                                         (0.08, 0.2, -0.18, (2, 4, 6, 9)))):
        P = S.paper(loc=(x + 0.8, y, 0.002 * k), rot_z=rz, lines=11, redact=red, seed=k + 3, name=f"mail{k}",
                    color=(0.86, 0.86, 0.84))
        r = P["root"]
        f0 = 2 + k * 6
        for f, xx in (((1, x),) if k == 0 else ((1, x + 0.8), (f0, x + 0.8), (f0 + 10, x))):
            r.location = (xx, y, 0.002 * k)
            r.keyframe_insert("location", frame=f)
        for i, b in enumerate(P["bars"]):
            fb = 24 + k * 6 + i * 7
            for f, s in ((fb, 0.001), (fb + 6, 1.0)):
                b.scale = (s, 1, 1)
                b.keyframe_insert("scale", frame=f)
    cam, _ = L.camera(loc=(0.0, -0.18, 0.95), target=(0.0, 0.1, 0.0), lens=35)
    L.cam_keys(cam, [(1, (0.0, -0.18, 0.95)), (n, (0.0, -0.12, 0.82))])
    _finish(L)


def S15(L, n):
    desk(L, n, energy=70)
    # tag (lying flat), dive-profile log, rope diagram
    tag = S.depth_tag("332 m", loc=(-0.1, 0.3, 0.012), yaw=0.0, scale=2.2, name="evtag", glow=0.05)
    tag.rotation_euler = (-PI / 2, 0, 0.25)
    log = S.paper(loc=(0.09, 0.14, 0.0), rot_z=0.06, lines=3, seed=7, name="log")
    ink = L.mat_principled("inkred", (0.6, 0.05, 0.04), rough=0.6)
    prof = [(-0.08, 0.1), (-0.06, -0.12)]
    x, z = -0.06, -0.12
    for k in range(7):
        x += 0.018
        prof.append((x, z))
        z += 0.03
        prof.append((x, z))
    cu = S.draw_on_curve([(px, py, 0.003) for px, py in prof], 0, 1, color=(0.6, 0.05, 0.04), width=0.0025, strength=0.0,
                         name="profile")
    cu.data.materials.clear()
    cu.data.materials.append(ink)
    cu.parent = log["root"]
    diag = S.paper(loc=(-0.11, -0.02, 0.0), rot_z=-0.1, lines=2, seed=9, name="diag")
    rl = L.prim("cube", loc=(0, -0.02, 0.003), name="dline")
    rl.scale = (0.002, 0.11, 0.0005)
    L.assign(rl, L.mat_principled("dlm", (0.05, 0.1, 0.3), rough=0.6))
    rl.parent = diag["root"]
    for k in range(6):
        tk = L.prim("cube", loc=(0.012, 0.08 - k * 0.036, 0.003), name="dtick")
        tk.scale = (0.01, 0.003, 0.0005)
        L.assign(tk, rl.data.materials[0])
        tk.parent = diag["root"]
    mg = S.magnifier(loc=(-0.1, 0.3, 0.07), radius=0.075)
    for f, p in ((1, (-0.35, 0.34, 0.07)), (6, (-0.1, 0.3, 0.07)), (14, (-0.09, 0.29, 0.07)), (20, (0.08, 0.14, 0.07)),
                 (30, (0.09, 0.13, 0.07)), (36, (-0.11, -0.01, 0.07)), (n, (-0.11, -0.02, 0.07))):
        mg.location = p
        mg.keyframe_insert("location", frame=f)
    cam, _ = L.camera(loc=(0.0, 0.04, 0.85), target=(0.0, 0.13, 0.0), lens=35)
    L.cam_keys(cam, [(1, (0.0, 0.04, 0.85)), (n, (0.0, 0.06, 0.8))])
    _finish(L)


def S16(L, n):
    desk(L, n, energy=70)
    pp = S.paper(loc=(0.0, 0.12, 0.0), rot_z=0.04, lines=8, seed=11, name="report", size=(0.24, 0.32))
    L.text3d("332.35 m", loc=(0, 0.2, 0.003), rot=(0, 0, 0.04), size=0.035, extrude=0.0,
             mat=L.mat_principled("rtx", (0.05, 0.05, 0.06), rough=0.6))
    hit = 12
    gm = L.mat_principled("stampink", (0.05, 0.5, 0.2), rough=0.7)
    mark = L.link(bpy.data.objects.new("mark", None))
    mark.location = (0.0, 0.08, 0.0035)
    mark.rotation_euler = (0, 0, -0.12)
    tx = L.text3d("CONFIRMED", loc=(0, -0.012, 0), rot=(0, 0, 0), size=0.032, extrude=0.0, mat=gm, name="marktx")
    tx.parent = mark
    for (x, y, sx, sy) in ((0, 0.03, 0.105, 0.003), (0, -0.03, 0.105, 0.003), (0.105, 0, 0.003, 0.03), (-0.105, 0, 0.003, 0.03)):
        b = L.prim("cube", loc=(x, y, 0), name="markbox")
        b.scale = (sx, sy, 0.0003)
        L.assign(b, gm)
        b.parent = mark
    for f, s in ((hit - 1, 0.001), (hit, 1.35)):
        mark.scale = (s,) * 3
        mark.keyframe_insert("scale", frame=f)
    st = S.rubber_stamp(loc=(0, 0.08, 0.3), size=0.15)
    st.rotation_euler = (0, 0, -0.12)
    for f, x, z in ((1, 0.0, 0.3), (hit - 3, 0.0, 0.1), (hit, 0.0, 0.002), (hit + 6, 0.0, 0.002), (hit + 12, 0.15, 0.15),
                    (hit + 22, 0.6, 0.3)):
        st.location = (x, 0.08, z)
        st.keyframe_insert("location", frame=f)
    cam, _ = L.camera(loc=(0.0, -0.05, 0.85), target=(0.0, 0.1, 0.0), lens=35)
    L.cam_keys(cam, [(1, (0.0, -0.05, 0.85)), (n, (0.0, -0.02, 0.76))])
    S.shake(cam, hit, length=5, amp=0.008, rot=0.006)
    _finish(L)
