"""SCUBA-07 — Sponge divers found a 2,000-year-old machine (Antikythera, 1900-01; CT scans 2005).
One builder per shot: def Sxx(L, n). New builders appended to PIPELINE/blender/lib_scuba.py: mat_bronze, mat_verdigris,
lump, split_halves, gear, mount, spin, amphora, helmet_diver, caique, air_pump. lib_cave is used for camera keys,
rain, clouds and text. Divers and crew are faceless; the 1901 casualties are shown only as an empty helmet.
Gears are a generic reconstruction look, not a copy of any one published model.
"""
import sys, os, math, random, importlib
import bpy
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_scuba as S
import lib_cave as C
importlib.reload(S)
importlib.reload(C)

PI = math.pi
BRONZE = (0.62, 0.4, 0.17)
XRAY = (0.55, 0.85, 1.0)
LUMP_Z = 0.045
# S01 frame-1 camera relative to the lump (S14 ends on the same relative pose: loop)
S01_D, S01_EL, S01_AZ0, S01_AZ1 = 1.2, 22.0, -24.0, -4.0


def _orbit(center, dist, el_deg, az_deg, tz=0.0):
    e, a = math.radians(el_deg), math.radians(az_deg)
    c = Vector(center)
    pos = c + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    return tuple(pos), tuple(c + Vector((0, 0, tz)))


def _finish(L):
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "AREA":
            o.data.volume_factor = 0.0
    L.bake_static()


def _aim_area(L, loc, target, energy, size, color, name):
    a = L.area(loc, (0, 0, 0), energy=energy, size=size, color=color, name=name)
    a.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return a


def _spot_at(L, loc, target, energy, deg, color, name, blend=0.5):
    sp = L.spot(loc, (0, 0, 0), energy=energy, size_deg=deg, blend=blend, color=color, name=name, radius=0.05)
    sp.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return sp


def _bg_node():
    return [nd for nd in bpy.context.scene.world.node_tree.nodes if nd.type == "BACKGROUND"][0]


def _the_lump(name="lump"):
    return S.lump(name, size=(0.2, 0.16, 0.09), seed=3,
                  mat=S.mat_verdigris(name + "_m", c1=(0.04, 0.07, 0.05), c2=(0.2, 0.3, 0.18), crust=(0.45, 0.42, 0.33)))


def _dust(n, center, size, count=600, color=(0.8, 0.85, 0.9), emit=0.3, vel=(0.004, 0.0, 0.006), radius=0.0012, seed=4):
    d = C.cloud(center, size, count=count, radius=radius, color=color, emit=emit, seed=seed)
    C.drift(d, n, vel)
    return d


# ============================================================================ S01 / S02 the lump on a plinth

def _plinth_set(L, n, xray=False):
    S.setup(vol_end=6)
    L.set_world(color=(0.0, 0.004, 0.008), strength=1.0)
    pl = L.prim("cube", loc=(0, 0, -0.5), name="plinth")
    pl.scale = (0.35, 0.35, 0.5)
    L.bevel(pl, 0.01)
    if xray:
        L.assign(pl, L.mat_principled("plinth_m", (0.01, 0.015, 0.02), rough=0.5))
    else:
        L.assign(pl, S.mat_caustic_ground("plinth_m", c1=(0.008, 0.01, 0.012), c2=(0.03, 0.035, 0.04),
                                          caustic=(0.45, 0.85, 1.0), strength=0.25, scale=1.4, nframes=n, base_scale=30))
    _spot_at(L, (0.15, -0.1, 1.3), (0, 0, LUMP_Z), 70, 30, (0.8, 0.92, 1.0), "keyspot", blend=0.6)
    _aim_area(L, (0.1, 0.9, 0.35), (0, 0, LUMP_Z), 25, 0.6, (0.3, 0.9, 0.85), "tealrim")
    _aim_area(L, (-0.8, 0.4, 0.3), (0, 0, LUMP_Z), 6, 0.6, (0.3, 0.6, 1.0), "siderim")
    return pl


def S01(L, n):
    _plinth_set(L, n)
    lp = _the_lump()
    lp.location = (0, 0, LUMP_Z)
    S.keys(lp, "rotation_euler", [(1, (0, 0, 0.15)), (n, (0, 0, 0.55))])
    _dust(n, (0, 0, 0.25), (0.8, 0.8, 0.5), count=500, emit=0.6)
    cam = C.camera(lens=85)
    keys = []
    for f in range(1, n + 1, 4):
        t = (f - 1) / (n - 1)
        az = S01_AZ0 + (S01_AZ1 - S01_AZ0) * t
        d = S01_D - 0.25 * C.sm(t)
        keys.append((f, *_orbit((0, 0, LUMP_Z), d, S01_EL, az, tz=0.035)))
    keys.append((n, *_orbit((0, 0, LUMP_Z), S01_D - 0.25, S01_EL, S01_AZ1, tz=0.035)))
    C.aim_cam(cam, n, keys, fn=lambda x: x)
    _finish(L)


def S02(L, n):
    _plinth_set(L, n, xray=True)
    lp = _the_lump("lump_x")
    lp.location = (0, 0, LUMP_Z)
    lp.rotation_euler = (0, 0, 0.55)
    # material: opaque verdigris on the right of the sweep, x-ray line-art on the left of it
    m = lp.active_material
    nt, lk = m.node_tree.nodes, m.node_tree.links
    out = nt["Material Output"]
    bsdf = nt["Principled BSDF"]
    lw = nt.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.45
    pw = nt.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 1.4
    lk.new(lw.outputs["Facing"], pw.inputs[0])
    ad = nt.new("ShaderNodeMath")
    ad.operation = "ADD"
    ad.use_clamp = True
    ad.inputs[1].default_value = 0.05
    lk.new(pw.outputs[0], ad.inputs[0])
    em = nt.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*XRAY, 1)
    em.inputs[1].default_value = 2.5
    tr = nt.new("ShaderNodeBsdfTransparent")
    xm = nt.new("ShaderNodeMixShader")
    lk.new(ad.outputs[0], xm.inputs[0])
    lk.new(tr.outputs[0], xm.inputs[1])
    lk.new(em.outputs[0], xm.inputs[2])
    geo = nt.new("ShaderNodeNewGeometry")
    sep = nt.new("ShaderNodeSeparateXYZ")
    lk.new(geo.outputs["Position"], sep.inputs[0])
    gt = nt.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    lk.new(sep.outputs["X"], gt.inputs[0])
    sweep = gt.inputs[1]
    mix = nt.new("ShaderNodeMixShader")
    lk.new(gt.outputs[0], mix.inputs[0])
    lk.new(xm.outputs[0], mix.inputs[1])
    lk.new(bsdf.outputs[0], mix.inputs[2])
    lk.new(mix.outputs[0], out.inputs["Surface"])
    x0, x1, f0, f1 = -0.16, 0.16, 4, 34
    C.key_input(sweep, [(1, x0), (f0, x0), (f1, x1), (n, x1)])
    # frozen gear train inside (x-ray line art)
    gm = S.mat_xray("gear_x", XRAY, strength=7.0, power=1.2, base=0.12)
    for k, (gx, gy, gz, r, t) in enumerate(((-0.035, 0.0, 0.0, 0.042, 48), (0.03, 0.012, 0.012, 0.026, 30),
                                            (0.058, -0.01, -0.012, 0.016, 18), (-0.072, 0.015, 0.016, 0.018, 20),
                                            (0.0, -0.02, -0.02, 0.014, 16), (0.02, 0.025, 0.02, 0.032, 36))):
        g = S.gear(f"xg{k}", teeth=t, r=r, thick=0.003, mat=gm, spokes=4 if r > 0.02 else 0)
        S.mount(g, (gx, gy, LUMP_Z + gz), normal=(0, -1, 0.35))
        g.rotation_euler = (0, 0, k * 0.4)
    # the scan bar (a thin emissive sheet facing the camera) + soft glow
    bar = L.prim("plane", loc=(0, -0.12, LUMP_Z + 0.02), rot=(PI / 2, 0, 0), size=1, name="scanbar")
    bar.scale = (0.003, 0.32, 1)
    L.assign(bar, L.mat_emission("scanbar_m", (0.8, 0.97, 1.0), 12.0))
    glow, gsock = C.glow_disc((0, -0.115, LUMP_Z + 0.02), radius=0.05, color=(0.5, 0.9, 1.0), strength=1.2,
                              rot=(PI / 2, 0, 0), name="scanglow")
    glow.scale = (0.35, 3.0, 1)
    for o in (bar, glow):
        C.key_loc(o, [(1, (x0, o.location.y, o.location.z)), (f0, (x0, o.location.y, o.location.z)),
                      (f1, (x1, o.location.y, o.location.z)), (n, (x1 + 0.4, o.location.y, o.location.z))])
    pl = L.point((0, -0.1, LUMP_Z + 0.05), energy=0.0, color=XRAY, radius=0.02, name="scanlight")
    pl.parent = bar
    C.key_energy(pl, [(1, 0), (f0, 6), (f1, 6), (f1 + 3, 0)])
    cam = C.camera(lens=85)
    p, t = _orbit((0, 0, LUMP_Z), S01_D - 0.3, 18.0, 0.0, tz=0.03)
    C.aim_cam(cam, n, [(1, p, t), (n, tuple(Vector(p) + Vector((0, 0.03, -0.005))), t)])
    S.scanlines(cam, lens=85, strength=0.25, tint=(0.0, 0.02, 0.05))
    _finish(L)


# ============================================================================ sea and boat

def _sea(L, n, mood="storm", sun_e=1.2, wave=1.3, chop=1.1, wind=18, size=200):
    S.setup(vol_end=120)
    if mood == "storm":
        top, hor, below = (0.08, 0.09, 0.11), (0.3, 0.32, 0.34), (0.02, 0.03, 0.035)
        sd, sc = Vector((0.3, 0.6, 0.35)).normalized(), (0.6, 0.65, 0.7)
        deep, shallow = (0.01, 0.03, 0.035), (0.06, 0.12, 0.12)
    elif mood == "overcast":
        top, hor, below = (0.3, 0.36, 0.42), (0.62, 0.64, 0.64), (0.03, 0.05, 0.06)
        sd, sc = Vector((-0.3, 0.5, 0.6)).normalized(), (0.9, 0.9, 0.88)
        deep, shallow = (0.0, 0.05, 0.07), (0.05, 0.2, 0.22)
    else:  # golden calm
        top, hor, below = (0.2, 0.38, 0.65), (1.0, 0.72, 0.42), (0.0, 0.03, 0.05)
        sd, sc = Vector((0.2, 0.9, 0.22)).normalized(), (1.0, 0.75, 0.45)
        deep, shallow = (0.0, 0.08, 0.12), (0.0, 0.3, 0.34)
    S.sky_gradient(top=top, horizon=hor, below=below, strength=1.0, sun_dir=tuple(sd), sun_col=sc, sun_size=0.03,
                   sun_strength=4.0 if mood == "golden" else 0.5)
    m = S.mat_ocean("sea_" + mood, deep=deep, shallow=shallow, rough=0.08, under=(0.15, 0.45, 0.5), under_strength=1.0)
    sea = S.ocean(size=size, nframes=n, wave_scale=wave, choppiness=chop, resolution=10, spatial=60, wind=wind, mat=m,
                  foam=(mood == "storm"))
    fp = L.prim("plane", loc=(0, 0, -0.6), size=6000, name="farsea")
    L.assign(fp, m)
    sun = L.sun(rot=(0, 0, 0), energy=sun_e, color=sc, angle=2.0 if mood != "golden" else 0.8)
    sun.rotation_euler = (-sd).to_track_quat("-Z", "Y").to_euler()
    return sea, sun


def _island(L, loc, scale, seed=2, name="island", green=0.3):
    o = L.prim("ico", loc=loc, subdivisions=5, radius=1.0, name=name)
    o.scale = scale
    L.apply_scale(o)
    L.add_displace(o, strength=scale[2] * 0.35, scale=scale[2] * 0.6, name=name + "_d1")
    L.add_displace(o, strength=scale[2] * 0.08, scale=scale[2] * 0.12, name=name + "_d2")
    L.assign(o, L.mat_noise_surface(name + "_m", (0.08, 0.075, 0.065), (0.32 - green * 0.1, 0.3, 0.24 - green * 0.05),
                                    scale=0.15, bump=0.8, voronoi=False))
    return o


def _crew(L, name, loc, rot_z=0.0, h=1.7, color=(0.06, 0.05, 0.045), rim=(1.0, 0.85, 0.65), rim_s=0.6):
    p = C.figure(name, height=h, base=color, rim=rim, rim_strength=rim_s)
    p["root"].location = loc
    p["root"].rotation_euler = (0, 0, rot_z)
    return p


def S03(L, n):
    sea, sun = _sea(L, n, "storm", sun_e=1.0, wave=1.6, chop=1.2, wind=22)
    _island(L, (-25, 150, -4), (70, 35, 26), seed=2, name="antik")
    _island(L, (60, 200, -6), (40, 25, 14), seed=5, name="rock2")
    boat = S.caique("caique")
    b = boat["root"]
    by0, by1 = 18.0, 26.0
    S.bob(b, n + 2, amp=0.35, rate=0.3, tilt=0.09, base=(0, by0, 0.0))
    # forward motion layered on the bob via a parent
    car = L.link(bpy.data.objects.new("boatcar", None))
    b.parent = car
    C.key_loc(car, [(1, (0, 0, 0)), (n, (0, by1 - by0, 0))])
    L.linear_fcurves(car)
    for k, (x, y) in enumerate(((0.4, -2.5), (-0.5, -1.0), (0.3, 2.2))):
        cr = _crew(L, f"crew{k}", (x, y, 0.72), rot_z=PI if k == 2 else 0.0, h=1.65, rim_s=0.3)
        cr["root"].parent = b
    sail = [o for o in bpy.data.objects if o.name.startswith("caique_sail")]
    C.rain((6, 22, 6), (40, 40, 16), count=2600, n=n, speed=11.0, length=0.6, width=0.012, color=(0.75, 0.8, 0.85),
           strength=0.5, seed=3)
    S.splash_drops((0, by0 + 4.4, 0.6), [12, 13, 14, 15, 50, 51, 52, 88, 89, 90, 120], count=60, speed=3.0, seed=4,
                   name="bowspray", size=0.05)
    # one lightning flash (frames 9-13) lighting the sky and the sea
    bg = _bg_node()
    C.key_input(bg.inputs[1], [(1, 1.0), (8, 1.0), (9, 6.0), (10, 2.0), (11, 5.0), (13, 1.0), (n, 1.0)])
    C.key_energy(sun, [(1, 1.0), (8, 1.0), (9, 9.0), (10, 2.5), (11, 7.0), (13, 1.0), (n, 1.0)])
    cam = C.camera(lens=28, clip_end=6000)
    C.aim_cam(cam, n, [(1, (9.5, 8.0, 2.6), (0.0, 19.5, 2.4)), (n, (8.5, 14.5, 2.3), (0.0, 27.5, 2.4))],
              shake=0.12, rot_shake=0.01, rate=0.5)
    _finish(L)


# ============================================================================ seabed at ~50 m (S04, S14 end)

def _seabed(L, n, depth_z=0.0, vol_center=(0, 2, 5), vol_size=(40, 40, 16), density=0.07, rays=True):
    S.setup(vol_end=35)
    L.set_world(color=(0.01, 0.035, 0.05), strength=1.0)
    S.world_volume(color=(0.2, 0.42, 0.5), density=density, anisotropy=0.6, absorption=(0.35, 0.2, 0.15),
                   center=vol_center, size=vol_size)
    sb = L.seabed(size=40, strength=0.45, z=depth_z,
                  mat=S.mat_caustic_ground("bed", c1=(0.2, 0.2, 0.17), c2=(0.42, 0.4, 0.33), caustic=(0.6, 0.85, 0.9),
                                           strength=0.25, scale=0.4, nframes=n))
    sb.rotation_euler = (0.1, 0, 0)
    sun = L.sun(rot=(0.15, 0.1, 0.2), energy=2.6, color=(0.6, 0.85, 1.0), angle=5)
    if rays:
        S.god_rays(center=(0, 4, depth_z + 13), count=7, length=15, spread=5, tilt=(0.15, 0.05), color=(0.6, 0.9, 1.0),
                   strength=0.8, alpha=0.18, nframes=n)
    return sb


def _wreck_props(L, seed=7, center=(0.8, 3.0), z=0.0):
    rnd = random.Random(seed)
    cx, cy = center
    out = []
    for k in range(13):
        x = cx + rnd.uniform(-2.6, 2.6)
        y = cy + rnd.uniform(-1.6, 2.4)
        zz = z + 0.1 * (y - 0.0) * 0.1 - rnd.uniform(0.05, 0.2)
        a = S.amphora((x, y, zz), rot=(rnd.uniform(1.0, 1.55), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 6.28)),
                      h=rnd.uniform(0.6, 0.8), name=f"amph{k}", crust=0.5)
        out.append(a)
    # bronze arm and shoulder of a statue, half out of the silt
    bz = S.mat_bronze("statue_bz", (0.35, 0.24, 0.12), rough=0.4, patina=0.55)
    ua = L.prim("cyl", loc=(cx - 0.6, cy - 0.6, z + 0.25), rot=(0.35, 1.0, 0.4), vertices=16, radius=0.1, depth=0.6,
                name="statue_upper")
    fa = L.prim("cyl", loc=(cx - 0.12, cy - 0.85, z + 0.42), rot=(0.1, 1.45, -0.2), vertices=16, radius=0.08, depth=0.55,
                name="statue_fore")
    sh = L.prim("sphere", loc=(cx - 0.95, cy - 0.45, z + 0.12), segments=16, ring_count=8, radius=0.24,
                name="statue_shoulder")
    sh.scale = (1.0, 0.8, 0.6)
    for o in (ua, fa, sh):
        L.assign(o, bz)
        L.smooth(o)
    hp = S.hand("statue_hand", color=(0.3, 0.2, 0.1), scale=2.2)
    hp["root"].location = (cx + 0.18, cy - 0.92, z + 0.45)
    hp["root"].rotation_euler = (0.1, 0, -1.6)
    for o in bpy.data.objects:
        if o.name.startswith("statue_hand") and o.type == "MESH":
            o.data.materials.clear()
            o.data.materials.append(bz)
    S.curl(hp, 1, 0.5)
    # pale marble figures lying half buried (faceless)
    mm = L.mat_noise_surface("marble", (0.62, 0.6, 0.55), (0.85, 0.83, 0.78), scale=4, bump=0.2, rough=0.55,
                             voronoi=False)
    for k, (x, y, rz) in enumerate(((cx + 1.6, cy + 0.7, 0.8), (cx - 2.1, cy + 1.6, -0.5))):
        p = L.char_figure(f"marble{k}", color=(0.8, 0.78, 0.72), height=1.7)
        for kk, o in list(p.items()):
            if o.type == "MESH":
                o.data.materials.clear()
                o.data.materials.append(mm)
        p["root"].location = (x, y, z - 0.02)
        p["root"].rotation_euler = (PI / 2 - 0.1, 0.0, rz)
        p["shoulderL"].rotation_euler = (0.4, 0, 0.3)
        p["hipR"].rotation_euler = (0.3, 0, 0)
    return out


def S04(L, n):
    _seabed(L, n)
    _wreck_props(L)
    # helmet diver lowering down the weighted line onto the slope
    P = S.helmet_diver("diver")
    r = P["root"]
    z0, z1, land = 6.0, 0.15, int(n * 0.7)
    C.key_loc(r, [(1, (-0.6, 0.4, z0)), (land, (-0.6, 0.45, z1)), (n, (-0.55, 0.5, z1))])
    r.rotation_euler = (0, 0, -0.5)
    P["shoulderR"].rotation_euler = (2.6, 0, -0.2)  # right hand up on the line
    P["shoulderL"].rotation_euler = (0.5, 0, 0.3)
    for f in range(1, land, 4):
        sw = 0.15 * math.sin(f * 0.15)
        P["hipL"].rotation_euler = (sw, 0, 0)
        P["hipR"].rotation_euler = (-sw, 0, 0)
        P["hipL"].keyframe_insert("rotation_euler", frame=f)
        P["hipR"].keyframe_insert("rotation_euler", frame=f)
    line_x, line_y = -0.42, 0.62
    C.line([(line_x, line_y, 20), (line_x, line_y, -0.1)], thickness=0.012, color=(0.7, 0.65, 0.5), emit=0.2,
           name="downline")
    wt = L.prim("cube", loc=(line_x, line_y, 0.05), name="sinker")
    wt.scale = (0.12, 0.12, 0.1)
    L.assign(wt, L.mat_principled("sinker_m", (0.1, 0.1, 0.1), rough=0.6))
    hose = S.tube([(0, -0.18, 1.62), (0.1, -0.5, 2.6), (0.4, -0.9, 5.0), (0.6, -1.2, 12.0)], radius=0.022,
                  mat=L.mat_principled("hose_m", (0.12, 0.11, 0.1), rough=0.7), name="hose")
    hose.parent = r
    bpy.context.view_layer.update()

    def ex(f):
        zz = C.piecewise([(1, z0), (land, z1), (n, z1)], f)
        return Vector((-0.6, 0.3, zz + 1.85))
    C.bubble_trail(ex, n, count=45, every=2.0, rise=1.8, size=0.03, seed=5, spread=0.05, life=(24, 40), name="exh")
    silt, dsock, _ = C.noisy_volume((0.6, 2.5, 0.5), (7.0, 5.0, 1.6), color=(0.55, 0.55, 0.48), density=0.0, scale=1.5,
                                    name="silt")
    C.key_input(dsock, [(1, 1.6), (n, 0.25)])
    _dust(n, (0, 2.0, 2.0), (8, 8, 5), count=1500, color=(0.7, 0.8, 0.8), emit=0.15, vel=(0.03, 0.0, -0.02),
          radius=0.004)
    _aim_area(L, (3.5, -2.5, 6.0), (0, 1.0, 1.0), 300, 6, (0.5, 0.8, 1.0), "fill")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (2.6, -3.4, 5.4), (-0.6, 0.4, 5.4)), (land, (2.6, -3.3, 2.6), (0.2, 1.6, 0.6)),
                       (n, (2.5, -3.0, 2.3), (0.5, 2.2, 0.3))], shake=0.03, rot_shake=0.004, rate=0.4)
    C.cam_fill(cam, energy=60, color=(0.55, 0.8, 1.0))
    _finish(L)


# ============================================================================ deck (S05 / S07 / S08)

def _deck(L, n, mood="overcast", bob=True):
    sea, sun = _sea(L, n, mood, sun_e=2.5, wave=0.7, chop=0.8, wind=10, size=160)
    _island(L, (-60, 110, -6), (60, 30, 22), seed=2, name="antik")
    boat = S.caique("caique")
    b = boat["root"]
    if bob:
        S.bob(b, n + 2, amp=0.08, rate=0.25, tilt=0.025, base=(0, 0, 0))
    return boat, sun


def _helmet_prop(L, loc, rot_z=0.0, name="helmprop", brass=(0.62, 0.42, 0.16)):
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    bm_ = S.mat_bronze(name + "_br", brass, rough=0.25)
    hel = L.prim("sphere", loc=(0, 0, 0.19), segments=24, ring_count=12, radius=0.19, name=name + "_dome")
    L.assign(hel, bm_)
    L.smooth(hel)
    hel.parent = root
    glass = L.mat_principled(name + "_gl", (0.01, 0.012, 0.015), rough=0.05, metal=0.3)
    fp = L.prim("cyl", loc=(0, -0.175, 0.19), rot=(PI / 2, 0, 0), vertices=24, radius=0.09, depth=0.03, name=name + "_face")
    L.assign(fp, glass)
    fp.parent = root
    fr = L.prim("torus", loc=(0, -0.19, 0.19), rot=(PI / 2, 0, 0), major_radius=0.095, minor_radius=0.014,
                major_segments=24, minor_segments=6, name=name + "_fr")
    L.assign(fr, bm_)
    fr.parent = root
    for sx in (-1, 1):
        sp = L.prim("cyl", loc=(sx * 0.17, -0.05, 0.21), rot=(0, PI / 2, 0), vertices=16, radius=0.05, depth=0.03,
                    name=name + "_port")
        L.assign(sp, glass)
        sp.parent = root
    collar = L.prim("cyl", loc=(0, 0, 0.03), vertices=24, radius=0.2, depth=0.06, name=name + "_collar")
    collar.scale = (1.0, 0.85, 1.0)
    L.assign(collar, bm_)
    collar.parent = root
    return root


def S05(L, n):
    cut = 60
    boat, sun = _deck(L, n)
    b = boat["root"]
    dz = boat["deck_z"]
    pump = S.air_pump((0.0, -1.2, dz), rot_z=0.0, name="pump")
    pump["root"].parent = b
    for w in pump["wheels"]:
        S.spin(w, n, 0.55)
    for k, sx in enumerate((-1, 1)):
        p = _crew(L, f"pumper{k}", (sx * 1.0, -1.2, dz), rot_z=(-PI / 2 if sx < 0 else PI / 2), h=1.7, rim_s=0.5)
        p["root"].parent = b
        p["pelvis"].rotation_euler = (0.25, 0, 0)
        for f in range(1, cut + 1, 2):
            ph = 2 * PI * 0.55 * f / 24 + k * PI
            for tag, sg in (("L", 1), ("R", -1)):
                p[f"shoulder{tag}"].rotation_euler = (1.2 + 0.45 * math.sin(ph), 0, 0)
                p[f"elbow{tag}"].rotation_euler = (0.6 + 0.4 * math.cos(ph), 0, 0)
                p[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
                p[f"elbow{tag}"].keyframe_insert("rotation_euler", frame=f)
    hose = S.tube([(0.2, -1.2, dz + 0.3), (0.8, -1.0, dz + 0.05), (1.3, -0.5, dz + 0.1), (1.45, 0.0, dz + 0.25),
                   (1.75, 0.3, -0.6), (1.9, 0.5, -2.5)], radius=0.03,
                  mat=L.mat_principled("hose_m", (0.12, 0.11, 0.1), rough=0.7), name="hose")
    hose.parent = b
    # underwater insert, far below the boat: helmet close-up in blue gloom
    U = Vector((0, 0, -80))
    S.world_volume(color=(0.15, 0.4, 0.55), density=0.12, anisotropy=0.6, absorption=(0.3, 0.15, 0.1),
                   center=tuple(U + Vector((0, 0, 1))), size=(10, 10, 8))
    S.backdrop_z("udrop", stops=((U.z - 4, (0.0, 0.01, 0.02)), (U.z + 1, (0.02, 0.12, 0.18)), (U.z + 4, (0.08, 0.3, 0.38))),
                 loc=tuple(U + Vector((0, 4, 0))), size=(20, 20), strength=1.0)
    P = S.helmet_diver("diver")
    P["root"].location = tuple(U + Vector((0, 0, -1.0)))
    P["root"].rotation_euler = (0, 0, PI + 0.5)
    S.bob(P["root"], n + 2, amp=0.03, rate=0.3, tilt=0.02, base=tuple(U + Vector((0, 0, -1.0))))
    bpy.context.view_layer.update()
    exw = P["neck"].matrix_world @ Vector(P["exhaust"])
    S.bubbles_at(tuple(exw), [cut + 1 + k * 2 + (k // 4) * 6 for k in range(22)], rise=1.6, spread=0.04, size=0.022,
                 life=(20, 34), name="exb")
    _aim_area(L, tuple(U + Vector((0.6, -0.4, 3.0))), tuple(U + Vector((0, 0, 0.7))), 150, 2.0, (0.6, 0.85, 1.0), "utop")
    _aim_area(L, tuple(U + Vector((-1.0, 1.4, 1.0))), tuple(U + Vector((0, 0, 0.7))), 80, 1.0, (0.3, 0.8, 0.9), "urim")
    hz = U + Vector((0, 0, 0.62))
    cam = C.camera(lens=35, clip_end=6000)
    keys = [(1, (2.6, -3.6, dz + 1.7), (0.0, -1.0, dz + 0.9)), (cut - 1, (2.2, -3.0, dz + 1.6), (0.0, -1.0, dz + 0.8)),
            (cut, tuple(hz + Vector((-0.45, -0.75, 0.12))), tuple(hz)),
            (n, tuple(hz + Vector((-0.38, -0.62, 0.1))), tuple(hz))]
    C.aim_cam(cam, n, keys, shake=0.02, rot_shake=0.004, rate=0.6)
    cam.data.lens = 35
    cam.data.keyframe_insert("lens", frame=cut - 1)
    cam.data.lens = 50
    cam.data.keyframe_insert("lens", frame=cut)
    C.constant_keys(cam.data)
    _finish(L)


def S07(L, n):
    cut = 52
    boat, sun = _deck(L, n, bob=False)
    b = boat["root"]
    dz = boat["deck_z"]
    mast = Vector(boat["mast_top"])
    my = mast.y
    # the diver sits slumped against the mast, helmet off beside him; a crewman's hand on his shoulder
    P = S.helmet_diver("diver")
    for o in bpy.data.objects:
        if o.name.startswith("diver_") and any(k in o.name for k in ("helmet", "face", "frame", "port", "valve")):
            o.hide_render = True
    P["head"].hide_render = False
    P["head"].data.materials.clear()
    P["head"].data.materials.append(L.mat_principled("head_m", (0.05, 0.045, 0.04), rough=0.8))
    C.pose_sit(P, 1.75, lean=-0.35)
    P["root"].location = (0.0, my - 0.32, dz)
    P["root"].rotation_euler = (0, 0, PI)
    P["neck"].rotation_euler = (0.55, 0.15, 0)
    for tag in ("L", "R"):
        P[f"shoulder{tag}"].rotation_euler = (0.25, 0, 0.15 if tag == "L" else -0.15)
        P[f"elbow{tag}"].rotation_euler = (0.3, 0, 0)
    for f, a in ((1, 0.5), (n // 2, 0.6), (n, 0.55)):
        P["neck"].rotation_euler = (a, 0.15, 0)
        P["neck"].keyframe_insert("rotation_euler", frame=f)
    _helmet_prop(L, (0.55, my - 0.55, dz), rot_z=2.4, name="helmside")
    cw = _crew(L, "crewman", (-0.55, my - 0.75, dz), rot_z=-PI / 2 - 0.5, h=1.72, rim_s=0.5)
    cw["pelvis"].rotation_euler = (0.55, 0, 0)
    cw["hipL"].rotation_euler = (-0.9, 0, 0)
    cw["kneeL"].rotation_euler = (1.6, 0, 0)
    cw["hipR"].rotation_euler = (-0.3, 0, 0)
    cw["shoulderR"].rotation_euler = (1.15, 0, -0.2)
    cw["elbowR"].rotation_euler = (0.4, 0, 0)
    # the insert: one empty helmet on the wet deck (towards the stern)
    hy = -2.6
    _helmet_prop(L, (0.1, hy, dz), rot_z=0.25, name="emptyhelm")
    wet = L.prim("plane", loc=(0.1, hy, dz + 0.025), size=1.6, name="wetdeck")
    L.assign(wet, L.mat_principled("wet_m", (0.06, 0.045, 0.03), rough=0.08))
    hz = Vector((0.1, hy, dz + 0.2))
    cam = C.camera(lens=35, clip_end=6000)
    keys = [(1, (1.9, my - 3.0, dz + 1.5), (0.0, my - 0.4, dz + 0.55)),
            (cut - 1, (1.55, my - 2.45, dz + 1.4), (0.0, my - 0.4, dz + 0.55)),
            (cut, tuple(hz + Vector((0.55, -0.95, 0.28))), tuple(hz + Vector((0, 0, -0.1)))),
            (n, tuple(hz + Vector((0.53, -0.93, 0.27))), tuple(hz + Vector((0, 0, -0.1))))]
    C.aim_cam(cam, n, keys, shake=0.01, rot_shake=0.002)
    cam.data.lens = 35
    cam.data.keyframe_insert("lens", frame=cut - 1)
    cam.data.lens = 50
    cam.data.keyframe_insert("lens", frame=cut)
    C.constant_keys(cam.data)
    _aim_area(L, (2.5, my - 2.5, dz + 3.0), (0, my - 0.5, dz + 0.5), 250, 3, (0.85, 0.88, 0.9), "greyfill")
    _aim_area(L, (0.8, hy - 1.0, dz + 1.5), tuple(hz), 60, 1.0, (0.85, 0.88, 0.95), "helmfill")
    _finish(L)


def S08(L, n):
    boat, sun = _deck(L, n, bob=False)
    b = boat["root"]
    dz = boat["deck_z"]
    gx = 1.2  # gunwale x (starboard)
    basket = L.link(bpy.data.objects.new("basket", None))
    cyl = L.prim("cyl", loc=(0, 0, 0.17), vertices=16, radius=0.32, depth=0.34, name="basket_mesh")
    wf = cyl.modifiers.new("wf", "WIREFRAME")
    wf.thickness = 0.012
    L.assign(cyl, L.mat_principled("wicker", (0.45, 0.34, 0.2), rough=0.8))
    cyl.parent = basket
    base = L.prim("cyl", loc=(0, 0, 0.01), vertices=16, radius=0.31, depth=0.02, name="basket_base")
    L.assign(base, L.mat_principled("wicker2", (0.35, 0.26, 0.15), rough=0.8))
    base.parent = basket
    # contents
    lp = _the_lump("lump_b")
    lp.parent = basket
    lp.location = (0.09, -0.12, 0.13)
    lp.rotation_euler = (0.3, 0.1, 0.6)
    bz = S.mat_bronze("arm_bz", (0.35, 0.24, 0.12), rough=0.4, patina=0.55)
    arm = L.prim("cyl", loc=(-0.05, 0.05, 0.3), rot=(0.3, 1.2, 0.2), vertices=14, radius=0.07, depth=0.55, name="arm")
    L.assign(arm, bz)
    L.smooth(arm)
    arm.parent = basket
    mm = L.mat_noise_surface("marble", (0.62, 0.6, 0.55), (0.85, 0.83, 0.78), scale=4, bump=0.2, rough=0.55,
                             voronoi=False)
    head = L.prim("sphere", loc=(-0.12, -0.08, 0.3), segments=20, ring_count=12, radius=0.12, name="marblehead")
    head.scale = (0.9, 1.0, 1.15)
    L.add_displace(head, strength=0.015, scale=0.05, name="mh_d")
    L.assign(head, mm)
    head.parent = basket
    shard = L.prim("cyl", loc=(0.15, 0.12, 0.22), rot=(0.9, 0.3, 0), vertices=12, radius=0.12, depth=0.15, name="shard")
    shard.scale = (1, 0.5, 1)
    L.assign(shard, L.mat_noise_surface("terracotta", (0.3, 0.15, 0.08), (0.55, 0.3, 0.17), scale=6, bump=0.4,
                                        voronoi=False))
    shard.parent = basket
    up, over, land = 34, 52, 62
    path = [(1, (gx + 0.55, -0.4, -0.55)), (up, (gx + 0.45, -0.4, dz + 0.55)), (over, (gx - 0.4, -0.45, dz + 0.65)),
            (land, (gx - 0.75, -0.45, dz + 0.04)), (n, (gx - 0.75, -0.45, dz + 0.04))]
    C.key_loc(basket, path)
    for f, rx in ((1, 0.12), (up, -0.08), (over, 0.1), (land, 0.0), (n, 0.0)):
        basket.rotation_euler = (rx, 0, 0.3)
        basket.keyframe_insert("rotation_euler", frame=f)
    # drips falling from the basket while it is over the water
    dm = L.mat_principled("drip_m", (0.8, 0.95, 1.0), rough=0.02, emit=(0.6, 0.8, 0.85), emit_strength=0.6)
    rnd = random.Random(3)
    for k in range(18):
        d = L.prim("sphere", loc=(0, 0, 0), segments=8, ring_count=6, radius=0.012, name=f"drip{k}")
        d.scale = (1, 1, 1.8)
        L.assign(d, dm)
        f0 = rnd.randint(2, over - 6)
        p0 = Vector(C.piecewise([(f, v) for f, v in path], f0)) + Vector((rnd.uniform(-0.25, 0.25),
                                                                            rnd.uniform(-0.25, 0.25), 0.0))
        d.scale = (0.001,) * 3
        d.keyframe_insert("scale", frame=max(1, f0 - 1))
        d.location = p0
        d.keyframe_insert("location", frame=f0)
        d.scale = (1, 1, 1.8)
        d.keyframe_insert("scale", frame=f0)
        d.location = p0 - Vector((0, 0, 1.4))
        d.keyframe_insert("location", frame=f0 + 9)
        d.scale = (0.001,) * 3
        d.keyframe_insert("scale", frame=f0 + 9)
    # rope up to the crew's hands at the gunwale
    rope = S.tube([(0, 0, 0.36), (0.0, 0.0, 1.2), (-0.3, 0.1, 2.0)], radius=0.012,
                  mat=L.mat_principled("rope_m", (0.7, 0.62, 0.45), rough=0.8), name="rope")
    rope.parent = basket
    for k, (x, y) in enumerate(((gx - 0.6, 0.3), (gx - 0.55, -1.3))):
        cr = _crew(L, f"hauler{k}", (x, y, dz), rot_z=-PI / 2, h=1.72, rim_s=0.5)
        cr["pelvis"].rotation_euler = (-0.25, 0, 0)
        cr["shoulderL"].rotation_euler = (1.4, 0, 0.3)
        cr["shoulderR"].rotation_euler = (1.1, 0, -0.3)
    cam = C.camera(lens=50, clip_end=6000)
    keys = [(1, (gx + 2.9, -2.6, 0.5), (gx + 0.55, -0.4, -0.2)), (up, (gx + 2.6, -2.4, dz + 0.9), (gx + 0.45, -0.4, dz + 0.5)),
            (land, (gx + 1.4, -1.8, dz + 1.0), (gx - 0.7, -0.5, dz + 0.15)),
            (n, (gx + 0.15, -1.2, dz + 0.55), tuple(Vector((gx - 0.75, -0.45, dz + 0.04)) + Vector((0.09, -0.12, 0.13))))]
    C.aim_cam(cam, n, keys, shake=0.015, rot_shake=0.003, rate=0.6)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 2.0
    for f, dd in ((1, 3.6), (land, 2.4), (n, 1.0)):
        cam.data.dof.focus_distance = dd
        cam.data.dof.keyframe_insert("focus_distance", frame=f)
    _aim_area(L, (gx + 2.0, -1.5, dz + 3.0), (gx - 0.6, -0.45, dz), 300, 3, (0.9, 0.9, 0.88), "dayfill")
    _finish(L)


# ============================================================================ S06 timeline over a grey sea plate

def S06(L, n):
    sea, sun = _sea(L, n, "overcast", sun_e=1.5, wave=0.8, chop=0.8, wind=12, size=200)
    for o in bpy.data.materials:
        if o.name.startswith("sea_"):
            p = o.node_tree.nodes.get("Principled BSDF")
            if p:
                p.inputs["Roughness"].default_value = 0.25
    cam = C.camera(lens=50, clip_end=6000)
    C.aim_cam(cam, n, [(1, (-4.0, -10.0, 12.0), (-2.0, 8.0, 0.0)), (n, (4.0, -10.0, 12.0), (6.0, 8.0, 0.0))])
    # small helmet-diver icons in screen space (parented to the camera) dropping in along the 1901 side
    im = L.mat_emission("icon_m", (0.92, 0.95, 1.0), 2.5)
    d = 1.0
    hh = 2 * d * 18 / 50
    ww = hh * 9 / 16

    def scr(px, py):
        return ((px - 540) / 1080 * ww, -(py - 960) / 1920 * hh, -d)
    for k in range(8):
        px, py = 545 + k * 52, 1088
        ic = L.link(bpy.data.objects.new(f"icon{k}", None))
        ic.parent = cam
        ic.location = scr(px, py)
        hd = L.prim("cyl", loc=(0, 0.007, 0), vertices=16, radius=0.0055, depth=0.0005, name=f"ic_h{k}")
        bd = L.prim("cube", loc=(0, -0.004, 0), name=f"ic_b{k}")
        bd.scale = (0.005, 0.006, 0.0003)
        for o in (hd, bd):
            L.assign(o, im)
            o.parent = ic
        f0 = 22 + k * 6
        C.key_loc(ic, [(1, tuple(Vector(ic.location) + Vector((0, 0.03, 0)))), (f0, tuple(Vector(ic.location) + Vector((0, 0.03, 0)))),
                       (f0 + 5, tuple(ic.location))])
        C.hide_from_frame([hd, bd], f_show=f0)
    _finish(L)


# ============================================================================ S09 museum storeroom, 1902

def S09(L, n):
    snap = 15
    S.setup(vol_end=8)
    L.set_world(color=(0.004, 0.003, 0.002), strength=1.0)
    S.world_volume(color=(0.8, 0.7, 0.55), density=0.025, anisotropy=0.5, center=(0, 0.5, 1.2), size=(5, 5, 3))
    wood = L.mat_noise_surface("shelfwood", (0.08, 0.05, 0.03), (0.22, 0.14, 0.08), scale=3, rough=0.6, bump=0.3,
                               voronoi=False)
    tb = L.prim("cube", loc=(0, 0.2, 0.75), name="table")
    tb.scale = (0.9, 0.5, 0.03)
    L.assign(tb, wood)
    for k in range(3):  # shelves behind with numbered trays
        sh = L.prim("cube", loc=(0, 1.3, 0.6 + k * 0.5), name="shelf")
        sh.scale = (1.6, 0.25, 0.02)
        L.assign(sh, wood)
        for j in range(5):
            tr = L.prim("cube", loc=(-1.2 + j * 0.6, 1.25, 0.66 + k * 0.5), name="tray")
            tr.scale = (0.22, 0.16, 0.04)
            L.assign(tr, L.mat_principled("tray_m", (0.3, 0.24, 0.16), rough=0.7))
            lab = C.text(f"{(k * 5 + j) * 7 + 1012}", (-1.2 + j * 0.6, 1.08, 0.66 + k * 0.5), size=0.04,
                         color=(0.75, 0.7, 0.6), strength=0.4, font=C.FONT_SERIF, name="trlab")
    for x in (-1.6, 1.6):
        up = L.prim("cube", loc=(x, 1.3, 1.1), name="upright")
        up.scale = (0.03, 0.25, 1.1)
        L.assign(up, wood)
    tray = L.prim("cube", loc=(0, 0.2, 0.8), name="maintray")
    tray.scale = (0.2, 0.16, 0.02)
    L.assign(tray, L.mat_principled("maintray_m", (0.35, 0.28, 0.18), rough=0.7))
    lp = _the_lump("lump_s")
    lp.location = (0, 0.2, 0.82 + LUMP_Z)
    bpy.context.view_layer.update()
    nrm = Vector((0.25, -1.0, 0.2)).normalized()
    a, b = S.split_halves(lp, plane_no=tuple(nrm), plane_co=(0, 0.2 - 0.005, 0.82 + LUMP_Z),
                          inner_mat=L.mat_principled("lump_in", (0.07, 0.1, 0.06), rough=0.9))
    # a: front piece falls away toward camera; b: back piece shows its cut face with a gear in it
    for o, dv, rot in ((a, nrm * 0.07 + Vector((0, 0, -0.025)), (0.5, 0.0, 0.15)), (b, -nrm * 0.006, (0, 0, 0))):
        o0 = Vector(o.location)
        r0 = o.rotation_euler.copy()
        C.key_loc(o, [(1, tuple(o0)), (snap, tuple(o0)), (snap + 5, tuple(o0 + dv))])
        for f, rr in ((1, r0), (snap, r0), (snap + 6, (r0.x + rot[0], r0.y + rot[1], r0.z + rot[2]))):
            o.rotation_euler = rr
            o.keyframe_insert("rotation_euler", frame=f)
    gb = S.mat_bronze("gear_bz", (0.55, 0.38, 0.17), rough=0.35, patina=0.35)
    g = S.gear("relic_gear", teeth=26, r=0.032, thick=0.006, mat=gb, spokes=4)
    gm = S.mount(g, (0.01, 0.2 - 0.004, 0.82 + LUMP_Z + 0.004), normal=tuple(nrm))
    gm.parent = b
    gm.matrix_parent_inverse = b.matrix_world.inverted()
    # desk lamp swings onto the tray
    lamp = L.link(bpy.data.objects.new("lamp", None))
    lamp.location = (-0.55, 0.0, 1.35)
    shade = L.prim("cone", loc=(0, 0, 0.06), vertices=20, radius1=0.12, radius2=0.04, depth=0.14, name="shade")
    shade.data.flip_normals() if hasattr(shade.data, "flip_normals") else None
    L.assign(shade, L.mat_principled("shade_m", (0.15, 0.25, 0.12), rough=0.4, metal=0.5))
    shade.parent = lamp
    bulb = L.prim("sphere", loc=(0, 0, 0.0), segments=12, ring_count=8, radius=0.03, name="bulb")
    L.assign(bulb, L.mat_emission("bulb_m", (1.0, 0.8, 0.5), 8.0))
    bulb.parent = lamp
    sp = L.spot((0, 0, -0.01), (0, 0, 0), energy=70, size_deg=42, blend=0.5, color=(1.0, 0.75, 0.45), name="lampspot",
                radius=0.03)
    sp.parent = lamp
    tgt = L.link(bpy.data.objects.new("lamp_t", None))
    con = lamp.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    C.key_loc(tgt, [(1, (-0.9, 0.7, 0.6)), (snap + 2, (-0.6, 0.6, 0.7)), (snap + 14, (0.0, 0.2, 0.86)), (n, (0.02, 0.2, 0.86))])
    L.ease_all(tgt)
    arm = S.tube([(-0.75, 0.45, 0.78), (-0.75, 0.4, 1.2), (-0.55, 0.0, 1.35)], radius=0.012,
                 mat=L.mat_principled("lamparm", (0.1, 0.1, 0.1), rough=0.4, metal=0.6), name="lamparm")
    # curator's sleeve and hand resting near the tray
    hp = S.hand("curator", color=(0.5, 0.38, 0.3), scale=1.0)
    hp["root"].location = (0.33, 0.0, 0.8)
    hp["root"].rotation_euler = (0, 0, 2.3)
    S.curl(hp, 1, 0.35)
    sl = L.prim("cyl", loc=(0.55, -0.22, 0.82), rot=(PI / 2, 0, 2.3), vertices=16, radius=0.05, depth=0.35, name="sleeve")
    L.assign(sl, L.mat_principled("sleeve_m", (0.05, 0.05, 0.06), rough=0.85))
    _dust(n, (-0.2, 0.2, 1.05), (0.8, 0.6, 0.6), count=500, color=(1.0, 0.85, 0.6), emit=0.5, vel=(0.005, 0, 0.004))
    L.point((0.5, -1.0, 1.6), energy=6, color=(0.7, 0.75, 0.85), radius=0.5, name="cool_amb")
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.25, -0.95, 1.22), (0.0, 0.2, 0.86)), (n, (0.15, -0.62, 1.08), (0.0, 0.2, 0.86))],
              shake=0.003, rot_shake=0.001, rate=0.5)
    S.shake(cam, snap, length=6, amp=0.01, rot=0.01, seed=2)
    _finish(L)


# ============================================================================ S10 CT lab, 2005

def S10(L, n):
    cut = 80
    S.setup(vol_end=10)
    L.set_world(color=(0.08, 0.09, 0.1), strength=1.0)
    fl = L.prim("plane", loc=(0, 0, 0), size=14, name="labfloor")
    L.assign(fl, L.mat_principled("labfloor_m", (0.35, 0.37, 0.4), rough=0.35))
    wall = L.prim("plane", loc=(0, 3.0, 2.5), rot=(PI / 2, 0, 0), size=14, name="labwall")
    L.assign(wall, L.mat_principled("labwall_m", (0.55, 0.58, 0.6), rough=0.8))
    grey = L.mat_principled("cab_m", (0.62, 0.64, 0.66), rough=0.4, metal=0.2)
    cab = L.prim("cube", loc=(0, 1.0, 1.0), name="cabinet")
    cab.scale = (0.9, 0.8, 1.0)
    L.bevel(cab, 0.08, 3)
    L.assign(cab, grey)
    hole = L.prim("cube", loc=(0, 0.22, 1.05), name="cab_open")
    hole.scale = (0.5, 0.05, 0.42)
    L.bevel(hole, 0.03)
    L.assign(hole, L.mat_principled("cab_in", (0.03, 0.035, 0.04), rough=0.6))
    stripe = L.prim("cube", loc=(0, 0.195, 1.55), name="cab_stripe")
    stripe.scale = (0.6, 0.01, 0.015)
    L.assign(stripe, L.mat_emission("cab_led", (0.3, 0.8, 1.0), 4.0))
    tt = L.prim("cyl", loc=(0, 0.2, 0.7), vertices=32, radius=0.16, depth=0.04, name="turntable")
    L.assign(tt, L.mat_principled("tt_m", (0.2, 0.2, 0.22), rough=0.3, metal=0.6))
    spinr = L.link(bpy.data.objects.new("spin", None))
    spinr.location = (0, 0.2, 0.72)
    tt.parent = spinr
    tt.location = (0, 0, -0.02)
    lp = _the_lump("lump_ct")
    lp.parent = spinr
    lp.location = (0, 0, LUMP_Z)
    S.spin(spinr, n, 0.12)
    xr = L.spot((0, 0.2, 1.45), (0, 0, 0), energy=25, size_deg=40, blend=0.8, color=(0.7, 0.9, 1.0), name="inner")
    # desk + monitor with flickering CT slices
    desk = L.prim("cube", loc=(1.55, 0.6, 0.72), name="desk")
    desk.scale = (0.55, 0.35, 0.03)
    L.assign(desk, L.mat_principled("desk_m", (0.85, 0.85, 0.85), rough=0.5))
    mon = L.prim("cube", loc=(1.55, 0.75, 1.1), name="monitor")
    mon.scale = (0.32, 0.02, 0.22)
    L.assign(mon, L.mat_principled("mon_m", (0.03, 0.03, 0.035), rough=0.4))
    scr = L.prim("plane", loc=(1.55, 0.728, 1.1), rot=(PI / 2, 0, 0), size=1, name="screen")
    scr.scale = (0.3, 0.2, 1)
    L.assign(scr, L.mat_emission("screen_m", (0.02, 0.03, 0.035), 1.0))
    sm_ = L.mat_emission("slice_m", (0.85, 0.92, 0.95), 3.0)
    dimm = L.mat_emission("slice_dim", (0.35, 0.42, 0.45), 2.0)
    rnd = random.Random(5)
    sets = []
    for si in range(4):
        objs = []
        blob = L.prim("cyl", loc=(1.55, 0.726, 1.1), rot=(PI / 2, 0, 0), vertices=24, radius=0.15, depth=0.0005,
                      name=f"slice{si}")
        blob.scale = (1.0, 0.72 + 0.05 * si, 1.0)
        L.add_displace(blob, strength=0.015, scale=0.04, name=f"sd{si}")
        L.assign(blob, dimm)
        objs.append(blob)
        for k in range(3):
            r = rnd.uniform(0.025, 0.06)
            g = S.gear(f"sg{si}_{k}", teeth=int(120 * r * 3) // 2 * 2, r=r, thick=0.0006, mat=sm_, spokes=4 if r > 0.035 else 0)
            S.mount(g, (1.55 + rnd.uniform(-0.08, 0.08), 0.7245, 1.1 + rnd.uniform(-0.06, 0.06)), normal=(0, -1, 0))
            g.rotation_euler = (0, 0, rnd.uniform(0, 6))
            objs.append(g)
        for k in range(4):  # rows of tiny lettering (dashes)
            ln = L.prim("cube", loc=(1.55 + rnd.uniform(-0.06, 0.04), 0.7244, 1.02 + 0.012 * k + 0.04 * si % 0.08),
                        name=f"txt{si}_{k}")
            ln.scale = (rnd.uniform(0.02, 0.05), 0.0002, 0.002)
            L.assign(ln, sm_)
            objs.append(ln)
        sets.append(objs)
    per = 10
    for si, objs in enumerate(sets):
        for f0 in range(1 + si * per, n + 1, per * len(sets)):
            for o in objs:
                o.hide_render = True
                o.keyframe_insert("hide_render", frame=max(1, f0 - 1))
                o.hide_render = False
                o.keyframe_insert("hide_render", frame=f0)
                o.hide_render = True
                o.keyframe_insert("hide_render", frame=f0 + per)
            for o in objs:
                C._constant(o)
        if si > 0:
            for o in objs:
                o.hide_render = True
                o.keyframe_insert("hide_render", frame=1)
                C._constant(o)
    _aim_area(L, (-2.5, -2.5, 3.5), (0, 1.0, 1.0), 900, 4, (0.85, 0.92, 1.0), "labkey")
    _aim_area(L, (2.5, -1.0, 3.0), (0.5, 1.0, 1.0), 400, 3, (0.8, 0.9, 1.0), "labfill")
    cam = C.camera(lens=28)
    sc = Vector((1.55, 0.7245, 1.1))
    keys = [(1, (-1.6, -2.2, 1.35), (0.1, 0.6, 1.0)), (cut - 1, (0.6, -2.5, 1.3), (0.35, 0.6, 1.0)),
            (cut, tuple(sc + Vector((-0.05, -0.7, 0.04))), tuple(sc)), (n, tuple(sc + Vector((-0.03, -0.58, 0.03))), tuple(sc))]
    C.aim_cam(cam, n, keys, shake=0.004, rot_shake=0.001)
    cam.data.lens = 28
    cam.data.keyframe_insert("lens", frame=cut - 1)
    cam.data.lens = 50
    cam.data.keyframe_insert("lens", frame=cut)
    C.constant_keys(cam.data)
    scan = S.scanlines(cam, lens=50, strength=0.3, tint=(0.0, 0.03, 0.05))
    C.hide_from_frame([scan], f_show=cut)
    _finish(L)


# ============================================================================ the reconstruction (S11 / S12)

MOD = 1.0 / 60.0  # gear module: teeth = 120 * r


def _teeth(r):
    return max(8, int(round(2 * r / MOD)))


def _blue_void(L, n):
    S.setup(vol_end=12)
    L.set_world(color=(0.004, 0.015, 0.04), strength=1.0)
    bd = L.prim("plane", loc=(0, 2.5, 0), rot=(PI / 2, 0, 0), size=1, name="void_bg")
    bd.scale = (12, 12, 1)
    L.assign(bd, S.mat_caustic_ground("void_m", c1=(0.003, 0.012, 0.03), c2=(0.008, 0.03, 0.06), caustic=(0.25, 0.5, 0.8),
                                      strength=0.18, scale=0.35, nframes=n, base_scale=4))
    _dust(n, (0, 0.5, 0), (5, 3, 6), count=700, color=(0.6, 0.8, 1.0), emit=0.3, vel=(0.01, 0, 0.02), radius=0.004)


def _train(L, n, rate=0.08, bronze=BRONZE):
    """Generic bronze gear train facing -Y. Returns (list of (gear, center, r), crank)."""
    bz = S.mat_bronze("train_bz", bronze, rough=0.3)
    bz2 = S.mat_bronze("train_bz2", tuple(c * 0.8 for c in bronze), rough=0.38)
    A = (Vector((0, 0, 0)), 0.55)
    specs = [("A", A[0], A[1], 0.0, None, 1)]
    # meshing chain: (name, parent, r, angle_deg, y_offset, compound_with)
    chain = [("B", "A", 0.2, 35, 0.0), ("B2", "B", 0.32, None, -0.06), ("C", "B2", 0.14, -20, -0.06),
             ("D", "A", 0.17, 150, 0.0), ("D2", "D", 0.28, None, 0.06), ("E", "D2", 0.12, 200, 0.06),
             ("F", "A", 0.12, 260, 0.0)]
    G = {"A": (A[0], A[1], 1.0, 0.0)}
    for nm, par, r, ang, yo in chain:
        pc, pr, pw, py = G[par]
        if ang is None:  # compound: same axle, same speed
            G[nm] = (pc.copy(), r, pw, yo)
        else:
            a = math.radians(ang)
            d = pr + r + MOD * 0.2
            c = pc + Vector((math.cos(a) * d, 0, math.sin(a) * d))
            G[nm] = (c, r, -pw * pr / r, yo)
    out = []
    for nm, (c, r, w, yo) in G.items():
        g = S.gear(f"g{nm}", teeth=_teeth(r), r=r, thick=0.035 if r > 0.3 else 0.03, mat=bz if len(nm) == 1 else bz2,
                   spokes=4 if r > 0.15 else 0)
        S.mount(g, (c.x, yo, c.z), normal=(0, -1, 0))
        S.spin(g, n, rate * w, phase=(PI / _teeth(r) if w < 0 else 0.0))
        out.append((g, c, r))
        ax = L.prim("cyl", loc=(c.x, 0.0, c.z), rot=(PI / 2, 0, 0), vertices=12, radius=0.018, depth=0.3, name=f"axle{nm}")
        L.assign(ax, bz2)
    # crank on A's axle, sticking out toward the camera
    crank = L.link(bpy.data.objects.new("crank", None))
    S.mount(crank, (0, -0.12, 0), normal=(0, -1, 0))
    arm = L.prim("cube", loc=(0.17, 0, 0), name="crank_arm")
    arm.scale = (0.18, 0.025, 0.012)
    knob = L.prim("cyl", loc=(0.33, 0, 0.07), vertices=12, radius=0.025, depth=0.14, name="crank_knob")
    for o in (arm, knob):
        L.assign(o, bz2)
        o.parent = crank
    S.spin(crank, n, rate)
    frame = L.prim("torus", loc=(0, 0.12, 0), rot=(PI / 2, 0, 0), major_radius=1.05, minor_radius=0.02,
                   major_segments=48, minor_segments=6, name="frame_ring")
    L.assign(frame, bz2)
    return out, crank


def S11(L, n):
    _blue_void(L, n)
    gears, crank = _train(L, n, rate=0.09)
    # the fragment dissolves into the train: lump shrinks away as the gears pop in
    lp = _the_lump("lump_d")
    lp.location = (0, -0.3, 0)
    lp.scale = (3.5, 3.5, 3.5)
    C.key_scale(lp, [(1, 3.5), (10, 0.001)])
    objs = [g.parent for g, c, r in gears]
    C.pop_in(objs, [4 + 2 * k for k in range(len(objs))], dur=6, overshoot=1.08)
    _aim_area(L, (-2.5, -3.0, 2.5), (0, 0, 0), 900, 3, (1.0, 0.85, 0.65), "warmkey")
    _aim_area(L, (1.5, 2.0, 1.5), (0, 0, 0), 600, 3, (0.35, 0.6, 1.0), "bluerim")
    _aim_area(L, (2.5, -1.5, -1.5), (0, 0, 0), 200, 3, (0.5, 0.7, 1.0), "fill")
    cam = C.camera(lens=35)
    keys = []
    for f in range(1, n + 1, 4):
        t = (f - 1) / (n - 1)
        az = -28 + 40 * t
        p, tg = _orbit((0.05, 0, 0.0), 3.4 - 0.3 * t, 12, az, tz=0.45)
        keys.append((f, p, tg))
    p, tg = _orbit((0.05, 0, 0.0), 3.1, 12, 12, tz=0.45)
    keys.append((n, p, tg))
    C.aim_cam(cam, n, keys, fn=lambda x: x)
    _finish(L)


def S12(L, n):
    _blue_void(L, n)
    ecl0, ecl1, sp0 = 36, 50, 56
    bz = S.mat_bronze("dial_bz", BRONZE, rough=0.35)
    bz2 = S.mat_bronze("dial_bz2", tuple(c * 0.75 for c in BRONZE), rough=0.45)
    dial = L.prim("cyl", loc=(0, 0.02, 0), rot=(PI / 2, 0, 0), vertices=64, radius=0.62, depth=0.04, name="dial")
    L.assign(dial, bz2)
    plate = L.prim("cube", loc=(0, 0.06, -0.05), name="plate")
    plate.scale = (0.75, 0.02, 0.85)
    L.assign(plate, S.mat_bronze("plate_bz", (0.3, 0.2, 0.1), rough=0.5, patina=0.3))
    for rr in (0.6, 0.5, 0.42):
        ring = L.prim("torus", loc=(0, -0.002, 0), rot=(PI / 2, 0, 0), major_radius=rr, minor_radius=0.007,
                      major_segments=64, minor_segments=6, name="ring")
        L.assign(ring, bz)
    for k in range(72):
        a = 2 * PI * k / 72
        tk = L.prim("cube", loc=(math.sin(a) * 0.55, -0.004, math.cos(a) * 0.55), rot=(0, a, 0), name="tick")
        tk.scale = (0.003, 0.003, 0.03 if k % 6 == 0 else 0.015)
        L.assign(tk, bz)
    # sun pointer with a golden ball, moon pointer with a half-silver ball (phase)
    sun_p = L.link(bpy.data.objects.new("sun_ptr", None))
    S.mount(sun_p, (0, -0.03, 0), normal=(0, -1, 0))
    bar = L.prim("cube", loc=(0, 0.25, 0), name="sun_bar")
    bar.scale = (0.008, 0.25, 0.004)
    L.assign(bar, bz)
    bar.parent = sun_p
    sun_m = L.mat_emission("sun_m", (1.0, 0.8, 0.3), 5.0)
    sball = L.prim("sphere", loc=(0, 0.47, 0), segments=20, ring_count=10, radius=0.05, name="sun_ball")
    L.assign(sball, sun_m)
    sball.parent = sun_p
    moon_p = L.link(bpy.data.objects.new("moon_ptr", None))
    S.mount(moon_p, (0, -0.05, 0), normal=(0, -1, 0))
    mbar = L.prim("cube", loc=(0, 0.2, 0), name="moon_bar")
    mbar.scale = (0.006, 0.2, 0.004)
    L.assign(mbar, bz)
    mbar.parent = moon_p
    mspin = L.link(bpy.data.objects.new("moon_spin", None))
    mspin.parent = moon_p
    mspin.location = (0, 0.36, 0)
    for k, (col, met) in enumerate((((0.85, 0.85, 0.88), 1.0), ((0.02, 0.02, 0.025), 0.0))):
        hs = L.prim("sphere", loc=(0, 0, 0), segments=20, ring_count=10, radius=0.04, name=f"moon_half{k}")
        bm_ = hs.data
        import bmesh as _bm
        bmx = _bm.new()
        bmx.from_mesh(bm_)
        _bm.ops.bisect_plane(bmx, geom=bmx.verts[:] + bmx.edges[:] + bmx.faces[:], plane_co=(0, 0, 0), plane_no=(1, 0, 0),
                             clear_inner=(k == 0), clear_outer=(k == 1))
        bmx.to_mesh(bm_)
        bmx.free()
        L.assign(hs, L.mat_principled(f"moon_m{k}", col, rough=0.3, metal=met))
        hs.parent = mspin
    S.spin(mspin, n, 0.5)
    # angles: sun slow, moon fast; they line up at frame ecl0..ecl1
    fa = (ecl0 + ecl1) / 2
    for f in range(1, n + 1, 2):
        sun_p.rotation_euler = (0, 0, 0.6 - 0.004 * (f - fa))
        moon_p.rotation_euler = (0, 0, 0.6 - 0.045 * (f - fa))
        sun_p.keyframe_insert("rotation_euler", frame=f)
        moon_p.keyframe_insert("rotation_euler", frame=f)
    # eclipse disc slides over the sun ball
    ed = L.prim("cyl", loc=(0, 0, 0), vertices=24, radius=0.055, depth=0.004, name="eclipse")
    L.assign(ed, L.mat_principled("ecl_m", (0.005, 0.005, 0.006), rough=0.6))
    ed.parent = sun_p
    C.key_loc(ed, [(1, (0.14, 0.47, 0.06)), (ecl0, (0.14, 0.47, 0.06)), (fa, (0.0, 0.47, 0.06)), (ecl1, (0.0, 0.47, 0.06)),
                   (ecl1 + 10, (-0.14, 0.47, 0.06))])
    C.hide_from_frame([ed], f_show=ecl0 - 2, f_hide=ecl1 + 11)
    S.emit_keys(sun_m, [(1, 5.0), (ecl0, 5.0), (fa, 0.4), (ecl1, 0.4), (ecl1 + 10, 5.0)])
    key = _aim_area(L, (-1.8, -2.6, 2.2), (0, 0, 0), 700, 3, (1.0, 0.85, 0.65), "warmkey")
    C.key_energy(key, [(1, 700), (ecl0, 700), (fa, 180), (ecl1, 180), (ecl1 + 10, 700)])
    _aim_area(L, (1.5, 1.5, 1.2), (0, 0, 0), 400, 3, (0.35, 0.6, 1.0), "bluerim")
    # then a spiral (the back dial) glows on, drawn over the face
    pts = []
    for i in range(240):
        t = i / 239
        a = 2 * PI * 4.5 * t
        r = 0.08 + 0.3 * t
        pts.append((math.sin(a) * r, -0.075, math.cos(a) * r))
    S.draw_on_curve(pts, sp0, n - 4, color=(1.0, 0.82, 0.35), width=0.006, strength=5.0, name="spiral")
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.0, -5.9, -0.95), (0.0, 0.0, -0.95)), (n, (0.0, -5.2, -0.82), (0.0, 0.0, -0.82))])
    _finish(L)


# ============================================================================ S13 timeline: a 1,000-year gap

def S13(L, n):
    S.setup(vol_end=10)
    L.set_world(color=(0.0, 0.0, 0.0), strength=1.0)
    S.backdrop_z("tl_bg", stops=((-6, (0.0, 0.005, 0.02)), (0, (0.01, 0.04, 0.1)), (6, (0.02, 0.08, 0.16))),
                 loc=(0, 3, 0), size=(30, 20), strength=1.0)
    _dust(n, (0, 1.0, 0), (12, 2, 8), count=900, color=(0.6, 0.8, 1.0), emit=0.4, vel=(0.05, 0, 0.02), radius=0.006)
    bz = S.mat_bronze("icon_bz", BRONZE, rough=0.3)
    g = S.gear("icon_gear", teeth=30, r=0.42, thick=0.05, mat=bz, spokes=4)
    gm = S.mount(g, (-1.15, 0.0, 1.5), normal=(0, -1, 0))
    S.spin(g, n, 0.12)
    g2 = S.gear("icon_gear2", teeth=14, r=0.2, thick=0.05, mat=bz, spokes=0)
    S.mount(g2, (-0.5, 0.0, 1.85), normal=(0, -1, 0))
    S.spin(g2, n, -0.12 * 0.42 / 0.2, phase=PI / 14)
    # medieval clock face
    cx = 4.3
    face = L.prim("cyl", loc=(cx, 0.0, 1.55), rot=(PI / 2, 0, 0), vertices=48, radius=0.55, depth=0.04, name="clockface")
    L.assign(face, L.mat_principled("clock_m", (0.75, 0.68, 0.5), rough=0.5))
    rim = L.prim("torus", loc=(cx, -0.03, 1.55), rot=(PI / 2, 0, 0), major_radius=0.57, minor_radius=0.04,
                 major_segments=48, minor_segments=8, name="clockrim")
    L.assign(rim, bz)
    for k in range(12):
        a = 2 * PI * k / 12
        tk = L.prim("cube", loc=(cx + math.sin(a) * 0.46, -0.03, 1.55 + math.cos(a) * 0.46), rot=(0, a, 0), name="ctick")
        tk.scale = (0.015, 0.005, 0.05)
        L.assign(tk, L.mat_principled("ctick_m", (0.08, 0.06, 0.05), rough=0.5))
    hand = L.link(bpy.data.objects.new("clockhand", None))
    S.mount(hand, (cx, -0.05, 1.55), normal=(0, -1, 0))
    hb = L.prim("cube", loc=(0, 0.18, 0), name="chand")
    hb.scale = (0.015, 0.2, 0.005)
    L.assign(hb, L.mat_principled("chand_m", (0.08, 0.06, 0.05), rough=0.5))
    hb.parent = hand
    S.spin(hand, n, 0.05)
    _aim_area(L, (0, -4, 4), (1.5, 0, 1.5), 900, 8, (1.0, 0.92, 0.8), "key")
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.2, -7.5, 0.4), (0.2, 0, 0.4)), (n, (2.2, -7.5, 0.4), (2.2, 0, 0.4))])
    _finish(L)


# ============================================================================ S14 loop: calm cove, sponge, sink to the lump

def S14(L, n):
    up_end, dip0, dip1 = 56, 58, 72
    sea, sun = _sea(L, n, "golden", sun_e=3.5, wave=0.35, chop=0.6, wind=6, size=160)
    _island(L, (-35, 70, -5), (45, 22, 18), seed=2, name="antik")
    _island(L, (30, 85, -5), (30, 18, 12), seed=4, name="cove2")
    boat = S.caique("caique")
    boat["root"].location = (3.0, 16.0, 0.0)
    boat["root"].rotation_euler = (0, 0, 2.2)
    S.bob(boat["root"], n + 2, amp=0.05, rate=0.2, tilt=0.015, base=(3.0, 16.0, 0.0))
    # helmet breaks the surface; a hand lifts a brown sponge
    hp_ = _helmet_prop(L, (0.0, 4.0, -0.6), rot_z=PI + 0.3, name="surfhelm")
    C.key_loc(hp_, [(1, (0.0, 4.0, -0.55)), (14, (0.0, 4.0, -0.5)), (30, (0.0, 4.0, -0.05)), (up_end, (0.0, 4.0, 0.0))])
    hd = S.hand("diverhand", color=(0.4, 0.38, 0.33), scale=1.6, glove=True)
    hr = hd["root"]
    hr.rotation_euler = (-PI / 2 + 0.3, 0, 0.3)
    C.key_loc(hr, [(1, (0.45, 3.7, -0.6)), (24, (0.45, 3.7, -0.5)), (40, (0.45, 3.65, 0.45)), (up_end, (0.45, 3.65, 0.55))])
    S.curl(hd, 1, 0.6)
    sp = L.prim("ico", loc=(0, 0.13, 0.0), subdivisions=3, radius=0.09, name="sponge")
    sp.scale = (1.0, 1.0, 0.8)
    L.add_displace(sp, strength=0.03, scale=0.025, tex_type="VORONOI", name="sponge_d")
    L.assign(sp, L.mat_noise_surface("sponge_m", (0.2, 0.12, 0.05), (0.45, 0.3, 0.14), scale=40, bump=1.0, rough=0.9,
                                     voronoi=True))
    sp.parent = hr
    S.splash_drops((0.2, 4.0, 0.05), [28, 29, 30, 31, 38, 39, 40], count=40, speed=2.0, seed=6, name="sspl", size=0.03)
    # underwater: volume below the surface, seabed with the lump where the camera ends (S01 framing)
    BED = -7.5
    S.world_volume(color=(0.15, 0.42, 0.5), density=0.07, anisotropy=0.6, absorption=(0.3, 0.15, 0.1),
                   center=(0, 5, (BED - 0.5) / 2 - 0.15), size=(30, 30, -BED + 0.2))
    sb = L.seabed(size=30, strength=0.25, z=BED,
                  mat=S.mat_caustic_ground("bed14", c1=(0.15, 0.14, 0.11), c2=(0.3, 0.28, 0.22), caustic=(0.6, 0.85, 0.9),
                                           strength=0.2, scale=0.5, nframes=n))
    sb.location = (0, 6, BED)
    LZ = BED + 0.06
    lump_c = Vector((0.0, 6.0, LZ))
    lp = _the_lump("lump_end")
    lp.location = tuple(lump_c)
    lp.rotation_euler = (0, 0, 0.15)
    mound = L.prim("sphere", loc=tuple(lump_c + Vector((0, 0, -0.06))), segments=24, ring_count=12, radius=1.0, name="mound")
    mound.scale = (0.25, 0.22, 0.05)
    L.assign(mound, L.mat_noise_surface("mound_m", (0.08, 0.075, 0.06), (0.2, 0.19, 0.15), scale=20, bump=0.6,
                                        voronoi=False))
    _spot_at(L, tuple(lump_c + Vector((0.15, -0.1, 1.3))), tuple(lump_c), 0, 30, (0.8, 0.92, 1.0), "endspot", blend=0.6)
    endspot = bpy.data.objects["endspot"]
    C.key_energy(endspot, [(1, 0), (dip1, 0), (n, 70)])
    _dust(n, tuple(lump_c + Vector((0, 0, 0.3))), (1.2, 1.2, 0.8), count=500, emit=0.5)
    cam = C.camera(lens=28, clip_end=6000)
    p_end, t_end = _orbit(tuple(lump_c), S01_D, S01_EL, S01_AZ0, tz=0.035)
    keys = [(1, (0.6, 0.0, 0.55), (0.0, 4.0, 0.35)), (up_end, (0.55, 0.6, 0.5), (0.1, 4.0, 0.4)),
            (dip0, (0.5, 0.8, 0.3), (0.2, 4.5, -0.6)), (dip1, (0.4, 1.6, -1.6), (0.2, 5.5, -5.0)),
            (n - 10, tuple(Vector(p_end) + Vector((0, -0.6, 0.6))), t_end), (n, p_end, t_end)]
    C.aim_cam(cam, n, keys, shake=0.02, rot_shake=0.004, rate=0.5, shake_keys=[(1, 1.0), (dip1, 0.6), (n - 8, 0.0)])
    for f, ln in ((1, 28), (dip1, 28), (n - 10, 85), (n, 85)):
        cam.data.lens = ln
        cam.data.keyframe_insert("lens", frame=f)
    _finish(L)
