"""CAVE-02 — Tham Luang rescue (2018). Shot builders (def Sxx(L, n)). Shared builders: PIPELINE/blender/lib_cave.py"""
import sys, os, math, random
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "PIPELINE", "blender"))
import importlib
import lib_cave as C
importlib.reload(C)
import bpy
from mathutils import Vector, noise

VOL_FINS = C.YELLOW
STANTON_FINS = C.ORANGE
CYAN_RIM = (0.35, 0.85, 1.0)
MUD = None


def _mud(L):
    return L.mat_noise_surface("mud", (0.045, 0.03, 0.018), (0.2, 0.14, 0.08), scale=1.4, bump=0.45, rough=0.42,
                               voronoi=False)


def _lime(L, name="lime"):
    return C.rock_mat(name, (0.025, 0.026, 0.028), (0.2, 0.19, 0.17), scale=1.3)


# ============================================================================ flooded air-gap passage (S01 / S20)

def _airgap_set(L, n):
    C.world_black((0.0, 0.002, 0.003))
    C.render_quality(vol_end=40, vol_tile="8", vol_samples=32)

    def hh(y):
        return 1.42 + 1.3 * C.sm((y - 18) / 6)

    pas, info = C.passage(length=34, half_w=1.75, zc=0.62, y0=-6, h_fn=hh, seed=4, rough=0.1,
                          floor_flat=0.3, mat=_lime(L), disp=(0.22, 0.07))
    wz = 1.22
    C.water_surface(size=(4.2, 34), center=(0, 11, wz), n=n, flow=(0.0, 0.12), wave_scale=1.3, bump=0.25)
    # mud slope far ahead where the gap opens (empty)
    slope = C.heightfield(size=(5, 9), center=(0, 26.5, 0), res=0.25,
                          fn=lambda x, y: wz - 0.4 + max(0.0, (y - 22.5)) * 0.55 + 0.15 * abs(x),
                          mat=_mud(L), name="farslope", disp=(0.2, 0.05))
    L.point((0.3, 25.0, 3.0), energy=55, color=(1.0, 0.75, 0.5), radius=0.5, name="slopeglow")
    # stalactites near the ceiling, clear of the camera path
    rnd = random.Random(7)
    sm_ = _lime(L, "stal")
    for i in range(34):
        y = rnd.uniform(-2, 18)
        x = rnd.choice((-1, 1)) * rnd.uniform(0.45, 1.35)
        top = 0.62 + hh(y) * math.sqrt(max(0.0, 1 - (x / 1.75) ** 2)) * 0.92
        ln = rnd.uniform(0.12, min(0.5, top - wz - 0.12))
        o = L.prim("cone", loc=(x, y, top - ln / 2), vertices=7, radius1=rnd.uniform(0.03, 0.08), radius2=0.004,
                   depth=ln, rot=(math.pi, 0, 0), name="stal")
        L.assign(o, sm_)
    C.drip_rings([(0.35, 6.0, wz + 0.002), (-0.5, 9.5, wz + 0.002), (0.2, 13.0, wz + 0.002), (-0.25, 3.2, wz + 0.002)],
                 n, period=30, seed=3, strength=0.35, rmax=0.5)
    C.water(center=(0, 11, 2.4), size=(4.5, 34, 2.6), color=(0.55, 0.7, 0.75), density=0.012, anisotropy=0.6,
            absorption=(0.02, 0.05, 0.05), name="airhaze")
    return info, wz


def _airgap_cam(L, n, y_from, y_to, ramp_in=True):
    cam = C.camera(lens=24)
    z = 1.44
    C.aim_cam(cam, n, [(1, (0.0, y_from, z), (0.0, y_from + 12, 1.32)), (n, (0.0, y_to, z), (0.0, y_to + 12, 1.32))],
              shake=0.015, rot_shake=0.003, rate=0.5, fn=lambda x: x,
              shake_keys=([(1, 0.0), (24, 1.0)] if ramp_in else [(1, 1.0), (n - 24, 1.0), (n, 0.0)]))
    # cool bounce from an off-screen torch behind the camera
    sp = L.spot((0, -0.6, 0.15), (0, 0, 0), energy=1400, size_deg=80, blend=0.9, color=(0.45, 0.85, 0.95),
                name="bounce", radius=0.3)
    sp.parent = cam
    # a tight warm streak skimming the water from behind (specular highlights on the surface)
    for yy in (6.0, 12.0):
        pf = L.point((0.6, y_from + yy, 1.85), energy=25, color=(0.4, 0.8, 0.9), radius=0.3, name="passfill")
        pf.data.specular_factor = 0.0
    sk = L.spot((0.5, y_from - 1.0, 1.75), (0, 0, 0), energy=1600, size_deg=18, blend=0.6, color=(1.0, 0.92, 0.8),
                name="skim", radius=0.05)
    sk.rotation_mode = "QUATERNION"
    sk.rotation_quaternion = (Vector((0.0, y_from + 14, 1.25)) - Vector(sk.location)).to_track_quat("-Z", "Y")
    return cam


def S01(L, n):
    _airgap_set(L, n)
    _airgap_cam(L, n, 0.0, 4.4, ramp_in=True)
    L.bake_static()


def S20(L, n):
    _airgap_set(L, n)
    _airgap_cam(L, n, -4.4, 0.0, ramp_in=False)
    L.bake_static()


# ============================================================================ mud-ledge chamber (S02 / S03 / S04 / S10)

def _slope_z(x, y):
    if y < 0:
        b = max(-1.6, -0.3 + y * 0.35)
    elif y < 6:
        b = -0.3 + 3.2 * (y / 6.0)
    elif y < 9.5:
        b = 2.9 + 0.05 * (y - 6)
    else:
        b = 3.08 + (y - 9.5) * 2.6
    return b + 1.2 * max(0.0, abs(x) - 4.0) ** 1.6


def _ceil_z(x, y):
    return 6.6 - max(0.0, -y - 2.0) * 0.8 - 0.25 * max(0.0, abs(x) - 3) ** 1.3


def _chamber(L, n, fog=0.018, water_glow=None):
    C.world_black((0.0, 0.002, 0.003))
    C.render_quality(vol_end=30, vol_tile="8", vol_samples=32)
    C.heightfield(size=(16, 24), center=(0, 2, 0), res=0.25, fn=_slope_z, mat=_mud(L), name="slope",
                  disp=(0.25, 0.06))
    C.heightfield(size=(16, 24), center=(0, 2, 0), res=0.4, fn=_ceil_z, mat=_lime(L, "ceil"), name="ceiling",
                  disp=(0.6, 0.15))
    ws, sock = C.water_surface(size=(16, 10.6), center=(0, -4.7, 0.0), n=n, flow=(0.0, -0.05), wave_scale=1.0,
                               bump=0.18, glow_at=water_glow, glow_radius=1.6)
    C.water(center=(0, 2, 3.2), size=(15, 22, 6.6), color=(0.6, 0.65, 0.6), density=fog, anisotropy=0.55,
            absorption=(0.03, 0.04, 0.05), name="chamberhaze")
    return sock


def _place_on_slope(rigs, dz=0.0):
    for p in rigs:
        r = p["root"]
        r.location.z = _slope_z(r.location.x, r.location.y) + dz


def S02(L, n):
    brk = int(n * 0.5)
    sock = _chamber(L, n, fog=0.02, water_glow=(0.0, -2.4))
    C.key_input(sock, [(1, 0.0), (8, 0.0), (brk - 6, 6.0), (brk + 4, 3.0), (n, 1.2)])
    d = C.diver("vol", fins=VOL_FINS, light_energy=2600, beam_len=7, beam_strength=0.35, beam_deg=26)
    r = d["root"]
    r.rotation_euler = (math.pi / 2 - 0.15, 0, 0)
    C.key_loc(r, [(1, (0, -2.4, -2.2)), (brk - 8, (0, -2.4, -1.4)), (brk + 8, (0, -2.4, -0.28)), (n, (0, -2.3, -0.22))])
    L.ease_all(r)
    # helmet torch tracks up across the ceiling over the slope
    t = d["torch"]
    tgt = L.link(bpy.data.objects.new("beam_tgt", None))
    C.key_loc(tgt, [(1, (0.0, -1.0, 6.0)), (brk + 4, (0.4, 1.5, 6.4)), (n, (-0.6, 3.0, 6.2))])
    con = t.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    C.key_energy(t, [(1, 0), (brk - 7, 0), (brk - 2, 2600)])
    if d.get("beam_sock") is not None:
        C.key_input(d["beam_sock"], [(1, 0.0), (brk - 7, 0.0), (brk - 1, 0.35)])
    # underwater glow under the surface before the break
    g = L.point((0, -2.4, -0.6), energy=0, color=(0.6, 1.0, 0.85), radius=0.4, name="uwglow")
    C.key_energy(g, [(1, 0), (8, 0), (brk - 4, 90), (n, 25)])
    C.rim_light((0, -2.4, 0.3), (0.3, -4.5, 1.6), energy=600, color=CYAN_RIM, size_deg=30, name="headrim")
    C.drip_rings([(0.15, -2.2, 0.003), (-0.3, -2.6, 0.003), (0.35, -2.7, 0.003)], n, period=16, seed=5, strength=0.6,
                 rmax=0.4)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.35, 2.4, 1.25), (0.0, -2.4, 0.15)), (brk, (0.35, 2.3, 1.22), (0.0, -2.4, 0.2)),
                       (n, (0.3, 1.9, 1.15), (0.0, -2.4, 0.3))], shake=0.008, rot_shake=0.002)
    C.cam_fill(cam, energy=25)
    dust = C.cloud((0, -1.0, 1.4), (4, 5, 2.4), count=1200, radius=0.004, emit=0.05, seed=4)
    C.drift(dust, n, (0.02, 0.0, 0.03))
    L.bake_static()


def _ledge_group(L, seed=4, shared=False, rim_strength=1.0):
    g = C.group13(center=(0.0, 7.0, 0.0), face=math.pi, spacing=0.62, seed=seed, rows=(5, 5, 3), shared=shared,
                  rim=CYAN_RIM, rim_strength=rim_strength)
    _place_on_slope(g, dz=-0.02)
    _sharpen_rims(g)
    return g


def _sharpen_rims(g, pw=5.0):
    seen = set()
    for p in g:
        m = p["mat"]
        if m.name in seen:
            continue
        seen.add(m.name)
        for nd in m.node_tree.nodes:
            if nd.type == "MATH" and nd.operation == "POWER":
                nd.inputs[1].default_value = pw


def S03(L, n):
    _chamber(L, n, fog=0.022)
    g = _ledge_group(L, rim_strength=0.9)
    d = C.diver("vol", fins=VOL_FINS, light_energy=4200, beam_len=9, beam_strength=0.3, beam_deg=18)
    r = d["root"]
    r.location = (0.35, -0.9, -0.42)
    r.rotation_euler = (math.pi / 2 - 0.05, 0, 0)
    t = d["torch"]
    tgt = L.link(bpy.data.objects.new("beam_tgt", None))
    C.key_loc(tgt, [(1, (-1.2, 3.0, 1.4)), (int(n * 0.45), (-0.6, 6.4, 3.0)), (n, (0.6, 7.6, 3.4))])
    con = t.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    # front-row figures raise hands against the glare
    for i, p in enumerate(g[:6]):
        f0 = int(n * 0.45) + i * 2
        for tag in ("L", "R"):
            sh = p[f"shoulder{tag}"]
            sh.keyframe_insert("rotation_euler", frame=f0)
            sh.rotation_euler = (2.5, 0, sh.rotation_euler.z)
            sh.keyframe_insert("rotation_euler", frame=f0 + 8)
    # back-light from behind the group (silhouettes against the wall glow)
    C.rim_light((0, 7.4, 3.6), (0.5, 3.0, 2.4), energy=1600, color=CYAN_RIM, size_deg=50, name="backrim")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.75, -2.15, 0.62), (0.0, 4.0, 1.3)), (n, (0.7, -2.0, 0.66), (0.1, 7.6, 3.1))],
              shake=0.012, rot_shake=0.003)
    C.cam_fill(cam, energy=8)
    dust = C.cloud((0, 4.0, 2.0), (4, 7, 3), count=1500, radius=0.004, emit=0.05, seed=6)
    C.drift(dust, n, (0.03, 0.0, 0.02))
    L.bake_static()


def S04(L, n):
    _chamber(L, n, fog=0.022)
    g = _ledge_group(L, rim_strength=0.0)
    tp = C.dive_torch((0.2, -0.9, 0.3), (0.0, 7.3, 3.2), energy=3500, size_deg=34, beam_len=7.5, beam_strength=0.3)
    C.glow_dot((0.2, -0.92, 0.3), C.TORCH, r=0.03, halo=5, strength=8, name="torchglare")
    # count order: as the beam crosses left -> right
    order = sorted(range(13), key=lambda i: g[i]["root"].location.x + 0.05 * i)
    f_first, f_last = 6, int(n * 0.78)
    for k, i in enumerate(order):
        f = f_first + int((f_last - f_first) * k / 12)
        C.key_input(g[i]["rim_sock"], [(1, 0.0), (f - 1, 0.0), (f + 2, 1.6), (f + 10, 0.7)])
    tgt = L.link(bpy.data.objects.new("sweep_tgt", None))
    C.key_loc(tgt, [(1, (-2.0, 7.0, 3.1)), (f_last, (2.0, 7.0, 3.1)), (n, (1.0, 7.2, 3.1))])
    sw = L.spot((0.2, -0.9, 0.3), (0, 0, 0), energy=1800, size_deg=16, blend=0.5, color=C.TORCH, name="sweep")
    con = sw.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    L.point((0.0, 6.0, 5.2), energy=40, color=CYAN_RIM, radius=1.0, name="topfill")
    cam = C.camera(lens=35)
    cam.data.lens = 24
    C.aim_cam(cam, n, [(1, (0.45, 9.45, 4.7), (0.0, 0.5, 1.0)), (n, (0.42, 9.4, 4.65), (0.0, 0.5, 1.0))],
              shake=0.004, rot_shake=0.001)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 2.0
    cam.data.dof.focus_distance = 4.4
    cam.data.dof.keyframe_insert("focus_distance", frame=int(n * 0.55))
    cam.data.dof.focus_distance = 12.5
    cam.data.dof.keyframe_insert("focus_distance", frame=n)
    dust = C.cloud((0, 3.5, 1.6), (4, 7, 2.5), count=1400, radius=0.004, emit=0.05, seed=8)
    C.drift(dust, n, (0.02, 0.0, 0.03))
    L.bake_static()


def S10(L, n):
    _chamber(L, n, fog=0.015)
    g = C.group13(center=(0.0, 1.05, 0.0), face=math.pi, spacing=0.6, seed=9, rows=(5, 5, 3), shared=True,
                  rim=CYAN_RIM, rim_strength=1.0)
    _place_on_slope(g, dz=-0.03)
    _sharpen_rims(g, 4.0)
    # heads tilted down at the water
    for p in g:
        p["neck"].rotation_euler = (-0.5, 0, 0)
    tz = _slope_z(1.4, 0.45) + 0.05
    tp = C.dive_torch((1.4, 0.45, tz), (-2.0, -5.0, 0.05), energy=2600, size_deg=28, beam_len=6.0, beam_strength=0.25)
    cold = L.area((0, -4.0, 4.5), (0, 0, 0), energy=120, size=6, color=(0.35, 0.6, 0.9), name="coldwater")
    C.rim_light((0, 1.2, 0.6), (0.0, -5.0, 1.2), energy=700, color=CYAN_RIM, size_deg=45, name="waterrim")
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.6, 5.8, 5.4), (0.0, -2.2, -0.1)), (n, (0.5, 5.0, 4.4), (0.0, -2.2, 0.0))],
              shake=0.006, rot_shake=0.0015)
    C.cam_fill(cam, energy=10)
    dust = C.cloud((0, 1.5, 1.5), (5, 5, 2.5), count=1000, radius=0.004, emit=0.05, seed=10)
    C.drift(dust, n, (0.02, 0.0, 0.02))
    L.bake_static()


# ============================================================================ hillside & cave mouth (S05 / S06 / S17 / S18 / S19)

def _mountain_z(x, y):
    v = Vector((x * 0.05, y * 0.05, 0.3))
    return 19.0 + max(0.0, y) * 0.55 + 6.0 * noise.noise(v) + 3.0 * noise.noise(v * 3.0) - 0.004 * x * x


def _mouth_set(L, n, tod="day", jungle=True, mist=0.0):
    rock = L.mat_noise_surface("limecliff", (0.07, 0.075, 0.065), (0.36, 0.36, 0.32), scale=0.6, bump=0.9)
    if tod == "night":
        rock = L.mat_noise_surface("limecliff_n", (0.03, 0.03, 0.03), (0.2, 0.2, 0.19), scale=0.6, bump=0.9)
    cm = C.cliff_with_mouth(width=4.6, height=3.8, wall=(70, 21), res=0.35, depth=30, seed=2, rock=rock,
                            passage_kw={"rough": 0.14})
    C.heightfield(size=(110, 70), center=(0, 34.0, 0), res=1.2, fn=_mountain_z, mat=rock, name="mountain",
                  disp=(1.6, 0.4))
    gmat = L.mat_noise_surface("mudground", (0.04, 0.03, 0.018), (0.16, 0.12, 0.07), scale=0.7, bump=0.4, rough=0.5,
                               voronoi=False)
    C.heightfield(size=(110, 70), center=(0, -34.6, 0), res=0.9,
                  fn=lambda x, y: -0.05 + 0.02 * abs(x) * (1 - min(1, abs(y) / 30)) + 0.012 * max(0, -y - 10) ** 1.2,
                  mat=gmat, name="ground", disp=(0.35, 0.08))
    blobs = []
    if jungle:
        rnd = random.Random(11)
        pts = []
        for i in range(140):
            x, y = rnd.uniform(-50, 50), rnd.uniform(1.5, 45)
            pts.append((x, y, _mountain_z(x, y) - 0.6))
        for i in range(60):
            x = rnd.uniform(-34, 34)
            pts.append((x, rnd.uniform(-0.5, 2.0), 19.5 + rnd.uniform(-0.6, 0.6)))
        for i in range(70):
            x = rnd.choice((-1, 1)) * rnd.uniform(6.5, 45)
            pts.append((x, rnd.uniform(-22, -1.5), 0.0))
        blobs = C.jungle(pts[:140], size=(2.2, 4.2), seed=3, name="canopy")
        blobs += C.jungle(pts[140:200], size=(1.4, 2.8), seed=4, name="cliffbush")
        blobs += C.jungle(pts[200:], size=(1.0, 2.6), seed=5, name="groundbush")
        # vines/bushes on the cliff face
        vp = [(rnd.uniform(-30, 30), -0.6, rnd.uniform(4.5, 18)) for _ in range(45)]
        vp = [p for p in vp if abs(p[0]) > 3.5 or p[2] > 6.5]
        C.jungle(vp, size=(0.6, 1.3), seed=6, name="cliffveg")
    # stream out of the mouth
    C.water_surface(size=(1.6, 26), center=(0.3, -13.0, 0.06), color=(0.05, 0.035, 0.02), rough=0.08, n=n,
                    flow=(0, -0.6), wave_scale=3, bump=0.3, name="stream")
    return cm


def _sky(L, tod):
    if tod == "day":
        C.sky_world(top=(0.42, 0.46, 0.47), horizon=(0.62, 0.66, 0.64), ground=(0.12, 0.13, 0.11), strength=1.1)
        C.sun_from(C.sun_dir(55, 200), energy=1.2, color=(0.85, 0.9, 0.9), angle=20)
    elif tod == "bright":
        C.sky_world(top=(0.7, 0.78, 0.85), horizon=(1.0, 1.0, 0.95), ground=(0.35, 0.35, 0.3), strength=2.6)
        C.sun_from(C.sun_dir(40, 200), energy=4.0, color=(1.0, 0.95, 0.85), angle=5)
    elif tod == "night":
        C.sky_world(top=(0.004, 0.006, 0.012), horizon=(0.012, 0.016, 0.025), ground=(0.004, 0.004, 0.005),
                    strength=1.0)
    elif tod == "dawn":
        C.sky_world(top=(0.14, 0.22, 0.38), horizon=(0.45, 0.52, 0.65), ground=(0.06, 0.07, 0.08), strength=0.9)
        C.sun_from(C.sun_dir(8, 150), energy=0.8, color=(0.6, 0.72, 0.95), angle=15)


def S05(L, n):
    C.render_quality(vol_end=80, vol_tile="8", vol_samples=24)
    _sky(L, "day")
    _mouth_set(L, n, "day")
    C.water(center=(0, -12, 3), size=(70, 40, 8), color=(0.75, 0.8, 0.78), density=0.025, anisotropy=0.2,
            absorption=(0.02, 0.02, 0.02), name="mist")
    rn = C.rain((0, -12, 12), (28, 22, 26), count=2600, n=n, speed=9, length=0.45, width=0.003, strength=0.5, seed=3)
    rn2 = C.rain((0, -7, 3), (8, 6, 7), count=900, n=n, speed=8, length=0.25, width=0.002, strength=0.45, seed=4,
                 name="rain_near")
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (4.0, -30.0, 36.0), (0.0, 8.0, 18.0)), (n, (1.2, -9.5, 2.5), (0.0, 2.0, 1.9))],
              shake=0.04, rot_shake=0.002, rate=0.4)
    L.bake_static()


def _walker(L, name, h, color_lamp=(1.0, 0.75, 0.4), lamp=True, rim=0.5):
    p = C.figure(name, height=h, rim=(1.0, 0.92, 0.8), rim_strength=rim)
    if lamp:
        s = h / 1.75
        lm = L.prim("sphere", loc=(0, 0.11 * s, 0.17 * s), segments=8, ring_count=6, radius=0.03, name=name + "_lamp")
        L.assign(lm, C.emis(name + "_lampm", color_lamp, 12))
        lm.parent = p["neck"]
        p["lamp"] = lm
    return p


def S06(L, n):
    C.render_quality(vol_end=40, vol_tile="8", vol_samples=24)
    _sky(L, "bright")
    _mouth_set(L, n, "day")
    # puddles on the dry floor
    pm = L.mat_principled("puddle", (0.01, 0.012, 0.012), rough=0.03)
    for (x, y, sx, sy) in ((-0.8, 3.5, 0.6, 0.35), (1.1, 6.2, 0.45, 0.3), (0.2, 8.8, 0.7, 0.4)):
        o = L.prim("cyl", loc=(x, y, 0.09), vertices=24, radius=1.0, depth=0.01, name="puddle")
        o.scale = (sx, sy, 1)
        L.assign(o, pm)
    # 13 walkers single file entering: path from outside, through the mouth, past the camera's right
    path = [Vector((1.4, -9.0, 0.06)), Vector((0.9, 0.0, 0.06)), Vector((-0.9, 5.5, 0.06)), Vector((-2.3, 10.5, 0.06))]
    rnd = random.Random(2)
    spd = 1.5 / 24.0
    total = 4.8
    lit = 0
    for k in range(13):
        h = 1.72 if k == 6 else rnd.uniform(1.3, 1.5)
        p = _walker(L, f"walk{k}", h, rim=0.6)
        s0 = 9.6 - k * 1.05
        pts_t = []
        for f in range(1, n + 1, 4):
            s = s0 + spd * (f - 1)
            pts_t.append((f, s))
        pts_t.append((n, s0 + spd * (n - 1)))
        r = p["root"]
        L_tot = sum((b - a).length for a, b in zip(path, path[1:]))
        for f, s in pts_t:
            t = max(0.0, min(1.0, s / L_tot))
            pos = C.along([tuple(v) for v in path], t)
            pos2 = C.along([tuple(v) for v in path], min(1.0, t + 0.01))
            d = pos2 - pos
            r.location = pos
            r.rotation_euler = (0, 0, math.atan2(-d.x, d.y) if d.length > 1e-6 else 0)
            r.keyframe_insert("location", frame=f)
            r.keyframe_insert("rotation_euler", frame=f)
        L.linear_fcurves(r)
        L.anim_walk(p, 1, n, stride=0.45, rate=1.1 + 0.05 * (k % 3))
        if k in (3, 7, 10):
            pl = L.point((0, 0, 0), energy=6, color=(1.0, 0.75, 0.4), radius=0.05, name=f"wl{k}")
            pl.parent = p["lamp"]
    C.rim_light((0.5, 5.0, 1.0), (0.0, -6.5, 1.8), energy=900, color=(1.0, 0.95, 0.85), size_deg=50, name="mouthrim")
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.9, 10.2, 0.42), (0.2, 0.0, 1.5)), (n, (0.8, 10.2, 0.42), (-0.9, 1.5, 1.4))],
              shake=0.01, rot_shake=0.002)
    C.cam_fill(cam, energy=20, color=(1.0, 0.85, 0.7))
    dust = C.cloud((0, 5, 1.2), (4, 8, 2), count=1500, radius=0.004, color=(1, 0.9, 0.75), emit=0.15, seed=6)
    C.drift(dust, n, (0.03, -0.02, 0.02))
    C.water(center=(0, 4, 1.6), size=(6, 12, 3.4), color=(0.9, 0.88, 0.82), density=0.02, anisotropy=0.5,
            name="mouthhaze")
    L.bake_static()


# ============================================================================ S07 flood surge

def S07(L, n):
    C.render_quality(vol_end=30, vol_tile="8", vol_samples=24)
    _sky(L, "day")
    pas, info = C.passage(length=40, half_w=1.9, half_h=1.6, zc=1.0, y0=-2, seed=8, rough=0.12, floor_flat=0.35,
                          mat=_lime(L), disp=(0.22, 0.06), x_fn=lambda y: 0.6 * math.sin(y * 0.12))
    # daylight end (entrance) far ahead at y = -2: bright card
    sky = L.prim("plane", loc=(0.0, -3.5, 1.2), rot=(math.pi / 2, 0, 0), size=8, name="daylight")
    L.assign(sky, C.emis("daylight_m", (0.85, 0.9, 0.85), 3.0))
    dl = L.area((0.0, -1.5, 1.3), (-math.pi / 2, 0, 0), energy=600, size=3.5, color=(0.9, 0.95, 0.9), name="dayspill")
    dl.rotation_euler = (math.radians(-90), 0, 0)
    dl.rotation_mode = "QUATERNION"
    dl.rotation_quaternion = Vector((0, 1, 0)).to_track_quat("-Z", "Y")
    em = sky.active_material.node_tree.nodes["Emission"].inputs[1]
    C.key_input(em, [(1, 3.0), (int(n * 0.55), 2.0), (n - 6, 0.0)])
    C.key_energy(dl, [(1, 600), (int(n * 0.55), 380), (n - 6, 0)])
    # rising brown water (surface + murk volume parented to it)
    ws, _ = C.water_surface(size=(5, 44), center=(0, 18, 0), color=(0.07, 0.045, 0.02), rough=0.12, n=n,
                            flow=(0, 1.2), wave_scale=2.2, bump=0.45, name="flood")
    for f, z in ((1, -0.5), (int(n * 0.5), 0.1), (int(n * 0.85), 0.55), (n, 1.3)):
        ws.location.z = z
        ws.keyframe_insert("location", frame=f)
    murk = L.water_volume(center=(0, 18, -2.0), size=(5, 44, 4), color=(0.4, 0.28, 0.12), density=0.9, anisotropy=0.3,
                          absorption=(0.2, 0.35, 0.6), name="murk")
    murk.parent = ws
    murk.location = (0, 0, -2.0)
    foam = C.cloud((0, 0, 0.02), (3.0, 8, 0.03), count=1500, radius=0.003, color=(0.85, 0.8, 0.7), emit=0.25, seed=5,
                   name="foam")
    foam.parent = ws
    foam.location = (0, -12.0, 0.02)
    foam.keyframe_insert("location", frame=1)
    foam.location = (0, -12.0 + 1.2 * n / 24, 0.02)
    foam.keyframe_insert("location", frame=n)
    L.linear_fcurves(foam)
    cam = C.camera(lens=20)
    C.aim_cam(cam, n, [(1, (0.6, 14.0, 0.62), (0.0, -2.0, 1.3)), (n, (0.6, 14.0, 0.62), (0.0, -2.0, 1.25))],
              shake=0.02, rot_shake=0.004, shake_keys=[(1, 0.3), (n, 1.6)])
    C.cam_fill(cam, energy=40, color=(0.8, 0.85, 0.8))
    L.bake_static()


# ============================================================================ S08 map backdrop

def S08(L, n):
    C.world_black((0.0, 0.0, 0.0))
    topo, sock = C.topo_relief(size=(20, 26), center=(0, 0, 0), height=4.0, seed=5, line_strength=1.2, spacing=0.32)
    # route glow across the relief (entrance lower-left to ledge upper-right)
    pts = []
    for i in range(16):
        t = i / 15
        x, y = -5.5 + 11 * t, -8 + 15 * t + 1.2 * math.sin(t * 6)
        pts.append((x, y, 0))
    C.curve([(x, y, 5.2) for x, y, _ in pts], thickness=0.05, mat=C.emis("routeglow", (1.0, 0.85, 0.3), 3.0),
            name="route")
    L.sun(rot=(0.9, 0.2, 0.8), energy=1.2, color=(0.7, 0.85, 1.0))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (1.0, -15.0, 15.0), (0.0, 0.0, 1.0)), (n, (0.8, -13.8, 13.6), (0.0, 0.5, 1.0))],
              shake=0.01, rot_shake=0.001)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 1.4
    cam.data.dof.focus_distance = 12.0
    L.bake_static()


# ============================================================================ underwater passages (S09 / S11 / S12 / S13 / S16)

def _uw(L, color=(0.3, 0.45, 0.4), density=0.05, center=(0, 12, 0), size=(5, 40, 4), absorption=(0.12, 0.25, 0.35)):
    C.world_black((0.0, 0.002, 0.003))
    C.render_quality(vol_end=25, vol_tile="8", vol_samples=32)
    return C.water(center=center, size=size, color=color, density=density, absorption=absorption, name="uwater")


def S09(L, n):
    _uw(L, color=(0.45, 0.42, 0.3), density=0.06, center=(0, 3, 0), size=(4, 16, 3))

    def wf(y):
        return 1.35 - 0.8 * C.sm(1 - abs(y - 6.0) / 2.2)

    def hf(y):
        return 1.05 - 0.55 * C.sm(1 - abs(y - 6.0) / 2.2)
    C.passage(length=18, y0=-4, w_fn=wf, h_fn=hf, zc=0.0, seed=12, rough=0.1, floor_flat=0.2,
              mat=C.rock_mat("restr", (0.03, 0.027, 0.022), (0.22, 0.18, 0.13)), disp=(0.18, 0.06))
    C.line([(0.25, -4.0, -0.62), (0.2, 3.0, -0.55), (0.05, 6.0, -0.32), (-0.1, 13.0, -0.5)], thickness=0.006,
           emit=0.8, name="guideline")
    d = C.diver("stanton", fins=STANTON_FINS, tanks="sidemount", light_energy=2400, beam_len=5, beam_strength=0.35,
                beam_deg=24)
    r = d["root"]
    C.key_loc(r, [(1, (0.0, 1.0, -0.05)), (n, (0.0, 3.3, -0.12))])
    r.rotation_euler = (0, 0, 0)
    r.keyframe_insert("rotation_euler", frame=8)
    r.rotation_euler = (0, math.radians(80), 0)
    r.keyframe_insert("rotation_euler", frame=30)
    L.anim_swim(d, n, kick_rate=0.9, amp=0.25)
    # silt billows from the floor and swallows the frame
    plume, dsock, _ = C.noisy_volume((0, 4.0, -0.4), (3.0, 4.5, 1.6), color=(0.55, 0.45, 0.3), density=0.0, scale=1.6,
                                     name="silt")
    C.key_input(dsock, [(1, 0.4), (18, 2.0), (n, 9.0)])
    C.key_loc(plume, [(1, (0, 4.0, -0.4)), (n, (0, 1.2, 0.0))])
    C.key_scale(plume, [(1, 1.0), (n, 1.8)])
    s = C.cloud((0, 5.0, -0.2), (2.0, 3, 1.0), count=1500, radius=0.003, color=(0.8, 0.7, 0.5), emit=0.08, seed=9)
    C.drift(s, n, (0.0, -0.3, 0.12))
    C.bubble_trail(lambda f: Vector((0.0, 1.0 + 2.3 * f / n + 0.55, 0.2)), n, count=14, rise=0.7, size=0.018,
                   life=(12, 26), seed=3)
    C.rim_light((0, 2.0, 0), (0.2, 3.5, 1.0), energy=300, color=CYAN_RIM, size_deg=40, name="rim")
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.3, -2.1, 0.7), (0.0, 5.5, -0.25)), (n, (0.25, 0.3, 0.62), (0.0, 7.0, -0.2))],
              shake=0.03, rot_shake=0.008, rate=0.8)
    C.cam_fill(cam, energy=90)
    L.bake_static()


def _tank_row(L, n):
    _uw(L, color=(0.38, 0.42, 0.24), density=0.07, center=(0, 14, 0), size=(4.5, 40, 3.4),
        absorption=(0.15, 0.2, 0.45))
    C.passage(length=42, y0=-4, half_w=1.7, half_h=1.3, zc=0.0, seed=21, rough=0.12, floor_flat=0.3,
              mat=C.rock_mat("tunnel", (0.05, 0.055, 0.04), (0.3, 0.3, 0.22)), disp=(0.22, 0.06))
    fz = -0.91
    line_pts = []
    for i in range(15):
        y = -3 + i * 3.0
        line_pts.append((-0.55 + 0.1 * math.sin(i), y, fz + 0.35 + 0.06 * math.cos(i * 1.7)))
    C.line(line_pts, thickness=0.006, emit=0.7, name="guideline")
    clip = L.mat_principled("clip", (0.1, 0.1, 0.1), rough=0.4, metal=0.6)
    tanks = []
    for k in range(9):
        y = 1.0 + k * 3.4
        p = C.along(line_pts, (y + 3) / 42.0)
        tk = C.tank((p.x - 0.12, y, p.z - 0.04), rot=(math.pi / 2, 0, 0.05 * ((k % 3) - 1)), length=0.7, r=0.08,
                    band=(1.0, 0.8, 0.1) if k % 2 == 0 else (0.95, 0.95, 0.95), name=f"tank{k}")
        tanks.append(tk)
        c = L.prim("torus", loc=(p.x - 0.05, y + 0.3, p.z), major_radius=0.03, minor_radius=0.008, name="clip")
        L.assign(c, clip)
    cam = C.camera(lens=45)
    C.aim_cam(cam, n, [(1, (0.55, -1.6, -0.5), (-0.2, 20.0, -0.35)), (n, (0.55, -1.45, -0.5), (-0.2, 20.0, -0.33))],
              shake=0.006, rot_shake=0.0015)
    C.cam_fill(cam, energy=70)
    for yy in (6, 12, 18):
        L.point((0.6, yy, 0.9), energy=18, color=(0.5, 0.7, 0.45), radius=0.4, name="murkfill")
    fill = L.spot((0.9, -1.0, 0.1), (0, 0, 0), energy=600, size_deg=40, blend=0.9, color=(0.5, 0.75, 0.8),
                  name="nearfill")
    fill.rotation_mode = "QUATERNION"
    fill.rotation_quaternion = (Vector((-0.6, 1.3, -0.8)) - Vector(fill.location)).to_track_quat("-Z", "Y")
    s = C.cloud((0, 12, 0), (3, 16, 2), count=2000, radius=0.003, color=(0.75, 0.7, 0.5), emit=0.06, seed=12)
    C.drift(s, n, (0.02, 0.0, 0.02))
    return cam, tanks


def S11(L, n):
    cam, tanks = _tank_row(L, n)
    d = C.diver("kunan", fins=(0.12, 0.12, 0.13), tanks="sidemount", light_energy=2200, beam_len=6, beam_strength=0.3,
                beam_deg=24)
    r = d["root"]
    C.key_loc(r, [(1, (0.1, 1.6, 0.0)), (n, (0.0, 17.0, -0.1))])
    L.linear_fcurves(r)
    L.anim_swim(d, n, kick_rate=0.8, amp=0.25)
    sp = L.spot((0.6, -1.5, 0.3), (0, 0, 0), energy=380, size_deg=16, blend=0.6, color=(0.55, 0.85, 0.95),
                name="backrim")
    tgt = L.link(bpy.data.objects.new("rim_tgt", None))
    tgt.parent = r
    con = sp.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    C.bubble_trail(lambda f: Vector((0.1 - 0.1 * f / n, 1.6 + 15.4 * f / n + 0.55, 0.2)), n, count=24, rise=0.6,
                   size=0.016, life=(14, 30), seed=4)
    L.bake_static()


def S12(L, n):
    cam, tanks = _tank_row(L, n)
    g, h, hem = C.glow_dot((0.0, 19.0, 0.0), C.TORCH, r=0.05, halo=5, strength=12, light=0, name="farglow")
    pl = L.point((0.0, 18.5, 0.0), energy=220, color=C.TORCH, radius=0.3, name="farlight")
    sp = L.spot((0.0, 18.8, 0.0), (math.pi / 2, 0, 0), energy=2000, size_deg=30, blend=0.5, color=C.TORCH, name="fartorch")
    em = g.active_material.node_tree.nodes["Emission"].inputs[1]
    fade = [(1, 1.0), (int(n * 0.25), 1.0), (int(n * 0.75), 0.0), (n, 0.0)]
    C.key_input(em, [(f, 12 * v) for f, v in fade])
    C.key_input(hem.inputs[1], [(f, 4.2 * v) for f, v in fade])
    C.key_energy(pl, [(f, 220 * v) for f, v in fade])
    C.key_energy(sp, [(f, 2000 * v) for f, v in fade])
    L.bake_static()


def S13(L, n):
    _uw(L, color=(0.3, 0.42, 0.42), density=0.04, center=(0, 1, 0), size=(8, 8, 5))
    wall = C.heightfield(size=(10, 6), center=(0, 2.6, 0.0), res=0.12, fn=lambda x, y: 0.0, name="backwall",
                         mat=C.rock_mat("bw", (0.02, 0.024, 0.024), (0.14, 0.15, 0.14)), disp=(0.5, 0.12))
    wall.rotation_euler = (math.pi / 2, 0, 0)
    fl = C.floor(size=(10, 6), center=(0, 0.5, -1.0), strength=0.25, name="uwfloor")
    pts = [(-3.0, 0.35, 0.28), (-1.5, 0.15, 0.05), (0.0, 0.0, -0.05), (1.5, -0.1, 0.0), (3.0, -0.2, 0.22)]
    C.line(pts, thickness=0.007, emit=0.9, name="guideline")
    # line arrow marker pointing to the exit (left)
    ar = L.prim("cone", loc=(-0.6, 0.06, 0.0), rot=(0, -math.pi / 2, 0), vertices=3, radius1=0.05, radius2=0.0,
                depth=0.11, name="arrow")
    ar.scale = (1, 0.35, 1)
    L.assign(ar, L.mat_principled("arrow_m", (0.02, 0.02, 0.02), rough=0.5))
    fill = L.spot((0.6, -2.5, 1.6), (0, 0, 0), energy=90, size_deg=35, blend=1.0, color=(0.5, 0.75, 0.85), name="fill")
    fill.rotation_mode = "QUATERNION"
    fill.rotation_quaternion = (Vector((0, 0, 0)) - Vector(fill.location)).to_track_quat("-Z", "Y")
    C.rim_light((0, 0, 0), (0.3, 2.0, 1.2), energy=160, color=CYAN_RIM, size_deg=60, name="rim")
    s = C.cloud((0, 0.3, 0.6), (4, 2, 2.2), count=2200, radius=0.004, color=(0.8, 0.8, 0.7), emit=0.06, seed=13)
    C.drift(s, n, (0.0, 0.0, -0.12))
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.0, -3.0, 0.35), (0.0, 0.0, -0.05)), (n, (0.0, -2.9, 0.35), (0.0, 0.0, -0.05))],
              shake=0.004, rot_shake=0.001)
    L.bake_static()


def S16(L, n):
    _uw(L, color=(0.4, 0.7, 0.72), density=0.04, center=(0, 3, 0), size=(6, 16, 4), absorption=(0.06, 0.25, 0.3))
    C.passage(length=18, y0=-6, half_w=3.2, half_h=1.6, zc=0.0, seed=31, rough=0.12, floor_flat=0.3,
              mat=C.rock_mat("tun16", (0.025, 0.03, 0.032), (0.2, 0.22, 0.22)), disp=(0.25, 0.06))
    C.line([(-0.9, -6, -0.8), (-0.8, 4, -0.7), (-0.9, 12, -0.85)], thickness=0.006, emit=0.8, name="guideline")
    y0, y1 = -0.6, 2.4
    a = C.diver("vol", fins=VOL_FINS, tanks="sidemount", light_energy=1800, beam_len=4, beam_strength=0.25)
    ra = a["root"]
    C.key_loc(ra, [(1, (-0.3, y0, 0.25)), (n, (-0.3, y1, 0.25))])
    L.linear_fcurves(ra)
    L.anim_swim(a, n, kick_rate=0.7, amp=0.22)
    a["shoulderL"].rotation_euler = (0, 0, -0.9)
    a["shoulderR"].rotation_euler = (0, 0, 0.9)
    ch = C.wrapped_child("child", length=1.0, rim_strength=1.4)
    ch["root"].parent = ra
    ch["root"].location = (0.0, 0.55, -0.32)
    ch["root"].rotation_euler = (0, 0, 0)
    b = C.diver("diverD", fins=(0.92, 0.92, 0.9), tanks="sidemount", light_energy=2600, beam_len=5, beam_strength=0.3)
    rb = b["root"]
    C.key_loc(rb, [(1, (0.25, y0 - 2.4, 0.6)), (n, (0.25, y1 - 2.3, 0.55))])
    L.linear_fcurves(rb)
    rb.rotation_euler = (-0.12, 0, -0.08)
    L.anim_swim(b, n, kick_rate=0.75, amp=0.22, start=1)
    C.bubble_trail(lambda f: Vector((-0.3, y0 + (y1 - y0) * f / n + 0.55, 0.45)), n, count=18, rise=0.7, size=0.016,
                   life=(14, 28), seed=6)
    C.bubble_trail(lambda f: Vector((0.25, y0 - 2.4 + (y1 - y0) * f / n + 0.55, 0.8)), n, count=14, rise=0.7,
                   size=0.016, life=(14, 28), seed=7)
    C.rim_light((-0.3, 1.0, 0.2), (-2.4, 0.5, 1.4), energy=2500, color=CYAN_RIM, size_deg=60, name="rimback")
    L.spot((0.0, 0.8, 1.5), (0, 0, 0), energy=900, size_deg=90, blend=1.0, color=(0.5, 0.85, 0.95), name="topwash")
    cam = C.camera(lens=28)
    cam.data.lens = 24
    C.aim_cam(cam, n, [(1, (1.35, y0 + 1.3, 0.6), (-0.2, y0 - 1.0, 0.3)), (n, (1.35, y1 + 1.0, 0.6),
                                                                          (-0.2, y1 - 1.2, 0.35))],
              shake=0.02, rot_shake=0.004, fn=lambda x: x)
    C.cam_fill(cam, energy=150)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 2.8
    cam.data.dof.focus_distance = 1.7
    cam.data.dof.keyframe_insert("focus_distance", frame=int(n * 0.45))
    cam.data.dof.focus_distance = 3.0
    cam.data.dof.keyframe_insert("focus_distance", frame=n)
    s = C.cloud((-0.8, 1, 0), (2.5, 8, 2.5), count=1500, radius=0.003, emit=0.05, seed=16)
    C.drift(s, n, (0.0, -0.05, 0.03))
    L.bake_static()


# ============================================================================ S14 cross-section: the way out

CL = [(-7.2, 0.08), (-6.2, 0.02), (-5.4, -0.15), (-4.6, -0.55), (-3.8, -0.62), (-3.0, -0.15), (-2.2, 0.05),
      (-1.4, -0.5), (-0.4, -0.68), (0.4, -0.25), (1.2, 0.08), (2.0, -0.4), (2.8, -0.6), (3.6, -0.15), (4.4, 0.1),
      (5.1, -0.35), (5.8, -0.3), (6.5, 0.2), (7.0, 0.32)]
SUMPS = [(-5.2, -2.85, -0.2), (-2.0, 0.8, -0.18), (1.6, 3.4, -0.2), (4.8, 6.2, -0.1)]


def S14(L, n):
    C.world_black((0.0, 0.0, 0.0))
    band = C.offset_band(CL, [0.2 if i not in (len(CL) - 1, len(CL) - 2) else 0.32 for i in range(len(CL))])
    mountain = [(-9, -2.6), (9, -2.6), (9, 0.6), (7.8, 1.2), (6.0, 2.6), (4.2, 3.6), (2.6, 4.3), (1.2, 4.0),
                (-0.4, 3.4), (-2.2, 2.6), (-4.2, 1.5), (-6.0, 0.6), (-6.9, 0.28), (-9, 0.28)]
    xs = C.xsection([(x, -z) for x, z in band], lambda d: -d, extent=(-9, 9, -2.6, 4.3), outer_poly=mountain,
                    water_top=(0.09, 0.09, 0.1), water_bot=(0.05, 0.05, 0.055), outline_color=C.CYAN,
                    outline_strength=3.0, name="tl")
    yb = 0.4 - 0.12 - 0.02
    wm = C.emis("sumpwater", (0.08, 0.35, 0.95), 1.6)
    for x0, x1, wl in SUMPS:
        p = C.clip_poly(band, 1, wl, keep_less=True)
        p = C.clip_poly(p, 0, x0, keep_less=False)
        p = C.clip_poly(p, 0, x1, keep_less=True)
        C.flat_poly(p, yb, wm, name="sump")
        C.curve([(x0 + 0.05, -0.43, wl), (x1 - 0.05, -0.43, wl)], thickness=0.01, mat=C.emis("wl", (0.5, 0.8, 1.0), 3),
                name="wline")
    sock = wm.node_tree.nodes["Emission"].inputs[1]
    C.key_input(sock, [(f, 1.0 + 1.3 * (0.5 + 0.5 * math.sin(f * 0.32))) for f in range(1, n + 1, 3)])
    # ground line + jungle dots
    C.curve([(-9, -0.42, 0.29), (-6.9, -0.42, 0.29)], thickness=0.02, mat=C.emis("gl", (0.45, 0.7, 0.4), 2.5),
            name="groundline")
    # route dotted line from ledge (right) back to entrance (left)
    route = [(x, -0.43, z) for x, z in reversed(CL)]
    dots = C.dotted_path(route, spacing=0.16, r=0.03, color=(1.0, 1.0, 1.0), strength=4.0, name="route")
    for k, o in enumerate(dots):
        C.hide_from_frame([o], f_show=4 + int((n - 14) * k / max(1, len(dots) - 1)))
    led, _, _ = C.glow_dot((7.0, -0.45, 0.32), (1.0, 0.85, 0.3), r=0.07, halo=4, strength=10, name="ledge")
    C.glow_dot((-7.1, -0.45, 0.1), (0.5, 1.0, 0.6), r=0.06, halo=4, strength=8, name="entr")
    C.text("LEDGE", (6.6, -0.45, 0.85), size=0.32, color=(1.0, 0.85, 0.35), strength=3.0, name="t_ledge")
    C.text("ENTRANCE", (-6.2, -0.45, 0.75), size=0.32, color=(0.6, 1.0, 0.7), strength=3.0, name="t_entr")
    C.text("FLOODED", (-0.4, -0.45, -1.15), size=0.24, color=(0.45, 0.75, 1.0), strength=3.0, name="t_fl")
    L.area((-3, -6, 5), (math.radians(55), 0, math.radians(-25)), energy=500, size=5, color=(0.7, 0.85, 1.0))
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (4.9, -11.5, 0.5), (4.9, 0.0, 0.1)), (n, (-4.9, -11.5, 0.5), (-4.9, 0.0, 0.1))],
              fn=C.sm)
    L.bake_static()


# ============================================================================ S15 full-face mask close-up

def S15(L, n):
    C.world_black((0.0, 0.002, 0.003))
    C.render_quality(vol_end=10, vol_tile="8", vol_samples=24)
    slab = L.prim("cube", loc=(0, 0.3, -0.12), name="ledge")
    slab.scale = (1.4, 1.6, 0.12)
    L.apply_scale(slab)
    sub = slab.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 3
    L.add_displace(slab, strength=0.05, scale=0.3, name="ledge_d")
    L.assign(slab, _mud(L))
    ch = C.wrapped_child("boy", length=1.25, suit=(0.012, 0.014, 0.018), rim_strength=0.5)
    r = ch["root"]
    r.location = (0, 0, 0.12)
    mk = ch["mask"]
    s = 1.0
    final = tuple(mk.location)
    C.key_loc(mk, [(1, (final[0], final[1] + 0.05, final[2] + 0.5)), (10, (final[0], final[1] + 0.05, final[2] + 0.42)),
                   (34, final), (n, final)])
    L.ease_all(mk)
    # gloved hands placing the mask, then withdrawing
    glove = L.mat_principled("glove", (0.02, 0.02, 0.025), rough=0.6)
    hands = []
    for sx in (-1, 1):
        h = L.prim("sphere", loc=(0, 0, 0), segments=12, ring_count=8, radius=1.0, name=f"glove{sx}")
        h.scale = (0.05, 0.09, 0.035)
        L.assign(h, glove)
        L.smooth(h)
        fx, fy, fz = final
        C.key_loc(h, [(1, (sx * 0.15, fy + 0.6 + 0.05, fz + 0.52)), (34, (sx * 0.15, fy + 0.62, fz + 0.04)),
                      (44, (sx * 0.15, fy + 0.62, fz + 0.04)), (64, (sx * 0.35, fy + 0.62, fz + 0.75))])
        h.parent = r
        L.ease_all(h)
        hands.append(h)
    # breathing (alive, sedated)
    C.key_scale(ch["chest"], [(f, (0.16, 0.22, 0.11 * (1 + 0.06 * math.sin(f * 2 * math.pi / 72))))
                              for f in range(1, n + 1, 6)])
    # air hose to a small tank
    tk = C.tank((0.55, 0.85, 0.09), rot=(math.pi / 2, 0, 0.4), length=0.55, r=0.07, name="ponytank")
    hose = C.curve([(0.03, 0.62, 0.15), (0.2, 0.78, 0.05), (0.42, 0.92, 0.12), (0.52, 1.18, 0.12)], thickness=0.012,
                   mat=L.mat_principled("hose", (0.03, 0.03, 0.035), rough=0.5), name="hose", smooth_pts=True)
    key = L.area((-0.8, 0.2, 1.4), (0, 0, 0), energy=25, size=1.0, color=(0.45, 0.85, 1.0), name="key")
    key.rotation_mode = "QUATERNION"
    key.rotation_quaternion = (Vector((0, 0.5, 0.1)) - Vector(key.location)).to_track_quat("-Z", "Y")
    fill = L.area((1.0, 0.0, 0.6), (0, 0, 0), energy=18, size=1.0, color=(1.0, 0.75, 0.5), name="warmfill")
    fill.rotation_mode = "QUATERNION"
    fill.rotation_quaternion = (Vector((0, 0.5, 0.1)) - Vector(fill.location)).to_track_quat("-Z", "Y")
    C.rim_light((0, 0.6, 0.15), (0.0, 1.6, 0.7), energy=120, color=CYAN_RIM, size_deg=40, name="rim")
    cam = C.camera(lens=50)
    tgt = (0.0, 0.55, 0.12)
    keys = []
    for k, f in enumerate((1, n // 2, n)):
        a = math.radians(35 + 15 * k / 2)
        keys.append((f, (math.cos(a) * 1.0, 0.6 + math.sin(a) * 1.0, 0.75), tgt))
    C.aim_cam(cam, n, keys, fn=lambda x: x, shake=0.003, rot_shake=0.001)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 2.8
    cam.data.dof.focus_distance = 1.25
    L.bake_static()


# ============================================================================ S17 / S18 / S19 cave mouth plates

def S17(L, n):
    C.render_quality(vol_end=50, vol_tile="8", vol_samples=16)
    _sky(L, "night")
    _mouth_set(L, n, "night")
    for x in (-4.0, 3.5):
        C.work_light((x, -5.5, 2.6), (0.0, 1.0, 1.5), energy=2500, name=f"wl{x}")
    rn = C.rain((0, -5, 3), (14, 8, 8), count=1500, n=n, speed=8, length=0.35, width=0.003, strength=0.5, seed=5)
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.6, -14, 1.6), (0.0, 1.0, 1.8)), (n, (0.55, -13.2, 1.6), (0.0, 1.0, 1.8))],
              shake=0.01, rot_shake=0.001)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 0.6
    cam.data.dof.focus_distance = 1.5
    L.bake_static()


def _carry_group(L, n, idx, x, y_from, y_to, delay=0):
    """Stretcher with 2 carriers (front/back) + 1 escort, walking toward -Y."""
    rig = L.link(bpy.data.objects.new(f"carry{idx}", None))
    C.key_loc(rig, [(1, (x, y_from, 0.0)), (n, (x, y_to, 0.0))])
    L.linear_fcurves(rig)
    st = C.stretcher(f"sked{idx}", length=1.3)
    st.parent = rig
    st.location = (0, 0, 0.72)
    st.rotation_euler = (0, 0, 0)
    for k, (dx, dy) in enumerate(((0.0, -1.0), (0.0, 1.0), (0.62, -0.3))):
        p = C.figure(f"res{idx}_{k}", height=1.72 + 0.04 * k, rim=(0.9, 0.95, 1.0), rim_strength=1.6)
        p["root"].parent = rig
        p["root"].location = (dx, dy, 0.02)
        p["root"].rotation_euler = (0, 0, math.pi)
        L.anim_walk(p, 1 + delay + k * 3, n, stride=0.35, rate=1.0)
        if k < 2:
            for f in range(1, n + 1, 2):
                for tag in ("L", "R"):
                    p[f"shoulder{tag}"].rotation_euler = (0.45, 0, 0)
                    p[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
                    p[f"elbow{tag}"].rotation_euler = (0.6, 0, 0)
                    p[f"elbow{tag}"].keyframe_insert("rotation_euler", frame=f)
    return rig


def S18(L, n):
    C.render_quality(vol_end=40, vol_tile="8", vol_samples=24)
    _sky(L, "night")
    _mouth_set(L, n, "night")
    for x, y, z in ((-4.2, -6.5, 2.8), (3.8, -6.5, 3.0), (-3.0, -3.8, 3.6)):
        C.work_light((x, y, z), (0.0, 0.5, 1.0), energy=2200, name=f"wl{x}")
    L.area((0, -3, 6), (0, 0, 0), energy=200, size=6, color=(0.7, 0.8, 1.0), name="topfill")
    _carry_group(L, n, 0, -0.75, 0.8, -5.0)
    _carry_group(L, n, 1, 0.85, 3.6, -2.2, delay=5)
    C.rain((0, -7, 4), (14, 12, 10), count=2600, n=n, speed=8.5, length=0.4, width=0.003, strength=0.55, seed=6)
    C.water(center=(0, -5, 2.5), size=(16, 14, 5), color=(0.75, 0.8, 0.85), density=0.022, anisotropy=0.4,
            absorption=(0.02, 0.02, 0.02), name="rainhaze")
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (0.7, -8.6, 0.95), (0.0, 1.5, 1.6)), (n, (0.7, -10.2, 0.95), (0.0, 1.5, 1.6))],
              shake=0.015, rot_shake=0.002)
    L.bake_static()


def S19(L, n):
    C.render_quality(vol_end=40, vol_tile="8", vol_samples=24)
    _sky(L, "dawn")
    _mouth_set(L, n, "dawn")
    rk = C.rocks([(0.5, 1.6, 0.0)], count=1, size=(0.42, 0.42), seed=8, sink=0.2, flat=(0.65, 0.7))
    tp = C.dive_torch((0.45, 1.55, 0.55), (0.9, 14.0, 1.3), energy=2400, size_deg=22, beam_len=8, beam_strength=0.45)
    C.water(center=(0, 6, 1.8), size=(7, 14, 4.0), color=(0.75, 0.8, 0.85), density=0.035, anisotropy=0.6,
            absorption=(0.02, 0.02, 0.02), name="innerhaze")
    mist = C.cloud((0, -4, 0.8), (16, 10, 1.6), count=1400, radius=0.008, color=(0.75, 0.82, 0.95), emit=0.25, seed=19,
                   name="mist")
    C.drift(mist, n, (0.25, 0.05, 0.0))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.9, -10.0, 1.6), (0.3, 2.0, 1.0)), (n, (0.6, -3.2, 1.0), (0.45, 1.8, 0.6))],
              shake=0.008, rot_shake=0.0015)
    C.cam_fill(cam, energy=40, color=(0.6, 0.7, 0.95))
    L.bake_static()
