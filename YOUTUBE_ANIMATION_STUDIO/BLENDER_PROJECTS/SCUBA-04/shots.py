"""SCUBA-04 — A Humpback Closed Its Mouth Around Him (Michael Packard, Provincetown, 2021).
One builder per shot: def Sxx(L, n). Scuba builders (incl. humpback, lobster boat) live in PIPELINE/blender/lib_scuba.py.
People are faceless stylised divers / silhouettes. No gore: the mouth interior is darkness, soft tissue and light leaks.
"""
import sys, os, math, random, importlib
import bpy
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_scuba as S
importlib.reload(S)

PI = math.pi
DEPTH = 13.7                     # 45 ft
GREEN_VOL = (0.3, 0.6, 0.42)
SUN_COL = (0.85, 1.0, 0.88)
SLIT = (0.75, 1.0, 0.85)
# S01 opening framing (S17 ends exactly here for the loop)
DIV01 = Vector((0.0, 0.0, 0.5))
CAM01_A = Vector((-1.55, -0.85, 1.55))
CAM01_T = Vector((0.3, 0.85, 0.2))
CAM01_B = CAM01_A + (CAM01_T - CAM01_A).normalized() * 0.3


# ----------------------------------------------------------------------------- helpers

def _finish(L):
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "AREA":
            o.data.volume_factor = 0.0
    L.bake_static()


def _upd():
    bpy.context.view_layer.update()


def _aim(o, frm, to):
    o.location = frm
    o.rotation_euler = (Vector(to) - Vector(frm)).to_track_quat("-Z", "Y").to_euler()
    return o


def world_of(o, local):
    _upd()
    return o.matrix_world @ Vector(local)


def glow_mat(L, name, color, strength=4.0, power=2.0):
    """Soft glowing blob: emission whose alpha falls off toward the silhouette (facing ratio)."""
    m, n, l = S._m(name)
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    inv = n.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    l.new(lw.outputs["Facing"], inv.inputs[1])
    pw = n.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = power
    l.new(inv.outputs[0], pw.inputs[0])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    tr = n.new("ShaderNodeBsdfTransparent")
    mx = n.new("ShaderNodeMixShader")
    l.new(pw.outputs[0], mx.inputs[0])
    l.new(tr.outputs[0], mx.inputs[1])
    l.new(em.outputs[0], mx.inputs[2])
    l.new(mx.outputs[0], n["Material Output"].inputs["Surface"])
    m.surface_render_method = "BLENDED"
    return m


def xray_mat(L, name, color, strength=2.0, power=1.6, base=0.04):
    """Line-art x-ray look: silhouette edges glow (Layer Weight 'Facing' is 1 at grazing angles), faces see-through."""
    m, n, l = S._m(name)
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    pw = n.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = power
    l.new(lw.outputs["Facing"], pw.inputs[0])
    ad = n.new("ShaderNodeMath")
    ad.operation = "ADD"
    ad.use_clamp = True
    ad.inputs[1].default_value = base
    l.new(pw.outputs[0], ad.inputs[0])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    tr = n.new("ShaderNodeBsdfTransparent")
    mx = n.new("ShaderNodeMixShader")
    l.new(ad.outputs[0], mx.inputs[0])
    l.new(tr.outputs[0], mx.inputs[1])
    l.new(em.outputs[0], mx.inputs[2])
    l.new(mx.outputs[0], n["Material Output"].inputs["Surface"])
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = True
    return m


def _xr(L, prefix, m):
    for o in bpy.data.objects:
        if o.name.startswith(prefix) and o.type in ("MESH", "CURVE"):
            o.data.materials.clear()
            o.data.materials.append(m)
            if o.type == "MESH":
                for poly in o.data.polygons:
                    poly.material_index = 0


def packard(L, loc=(0, 0, 0), rot=(0, 0, 0), name="packard"):
    """Michael Packard: black wetsuit, single tank, orange fins, mask + regulator. Faceless."""
    P = L.char_diver(name=name, suit=(0.03, 0.03, 0.035), accent=(0.95, 0.42, 0.05), tanks="single", light_on=False)
    r = P["root"]
    r.location = loc
    r.rotation_euler = rot
    met = L.mat_principled(name + "_reg", (0.08, 0.08, 0.09), rough=0.3, metal=0.3)
    chrome = L.mat_principled(name + "_chrome", (0.85, 0.86, 0.88), rough=0.12, metal=1.0)
    rg = L.prim("cyl", loc=(0.0, 0.66, -0.1), vertices=10, radius=0.035, depth=0.06, rot=(PI / 2, 0, 0), name=name + "_regulator")
    L.assign(rg, met)
    rg.parent = r
    P["reg"] = rg
    hose = S.tube([(0.0, 0.64, -0.1), (0.12, 0.55, -0.05), (0.14, 0.4, 0.15), (0.05, 0.36, 0.25)], radius=0.012, mat=met,
                  name=name + "_hose", order=3)
    hose.parent = r
    vv = L.prim("cyl", loc=(0.0, 0.38, 0.2), vertices=10, radius=0.03, depth=0.07, rot=(PI / 2, 0, 0), name=name + "_valve")
    L.assign(vv, chrome)
    vv.parent = r
    P["valve"] = vv
    return P


def pose_reach(P):
    """Horizontal near the bottom, right arm reaching forward-down (to the lobster), left arm back along the body."""
    P["shoulderR"].rotation_euler = (-0.45, 0, -0.1)
    P["shoulderL"].rotation_euler = (0, 0, 2.6)
    for tag in ("L", "R"):
        P[f"hip{tag}"].rotation_euler = (0.15, 0, 0)
        P[f"knee{tag}"].rotation_euler = (0.35, 0, 0)


def curl(P):
    P["root"].rotation_euler = (0.25, PI / 2 - 0.3, 0.2)
    for tag in ("L", "R"):
        P[f"hip{tag}"].rotation_euler = (1.25, 0, 0)
        P[f"knee{tag}"].rotation_euler = (-1.6, 0, 0)
        P[f"shoulder{tag}"].rotation_euler = (-1.7, 0, 0)


def cape_env(L, n, depth=DEPTH, vol=0.07, rays=True, caustic=0.3, surface=True, snow=900, center=(0, 0), size=70,
             rocks=True):
    """Green Cape Cod water: sandy bottom with caustics, sun shafts, glowing surface overhead."""
    S.setup(vol_end=60)
    L.set_world(color=(0.04, 0.12, 0.09), strength=1.0)
    S.world_volume(color=GREEN_VOL, density=vol, anisotropy=0.6, absorption=(0.35, 0.65, 0.45),
                   center=(center[0], center[1], depth / 2 - 0.2), size=(size, size, depth + 0.6))
    sand = S.mat_caustic_ground("capesand", c1=(0.3, 0.3, 0.22), c2=(0.52, 0.5, 0.38), caustic=(0.8, 1.0, 0.85),
                                strength=caustic, scale=1.4, nframes=n)
    sb = L.seabed(size=size, strength=0.25, mat=sand)
    sb.location = (center[0], center[1], -0.05)
    out = {"sand": sand}
    if rocks:
        rm = L.mat_noise_surface("rockm", (0.08, 0.09, 0.07), (0.25, 0.26, 0.2), scale=3, bump=0.6)
        rnd = random.Random(3)
        for i, (x, y, r) in enumerate(((0.75, 1.35, 0.45), (-1.6, 2.8, 0.7), (2.4, 4.5, 0.9), (-3.5, -1.0, 0.6),
                                       (1.2, 2.2, 0.25))):
            o = L.prim("ico", loc=(x + center[0], y + center[1], r * 0.25), subdivisions=3, radius=r, name="rock")
            o.scale = (1.2, 1.0, 0.6)
            L.add_displace(o, strength=r * 0.25, scale=r * 0.6, name=f"rk{i}")
            L.assign(o, rm)
    if surface:
        surf = L.prim("plane", loc=(center[0], center[1], depth), size=size * 1.6, name="undersurface")
        L.assign(surf, S.mat_water_surface("usurf", color=(0.3, 0.55, 0.45), rough=0.1, alpha=1.0,
                                           under_color=(0.55, 0.85, 0.7), under_strength=1.3, ripple=0.4, nframes=n))
        surf.visible_shadow = False
    sun = L.sun(rot=(0.3, 0.12, 0.4), energy=4.5, color=SUN_COL, angle=4)
    out["sun"] = sun
    if rays:
        out["rays"] = S.god_rays(center=(center[0], center[1] + 3, depth - 0.1), count=8, length=depth, spread=6,
                                 tilt=(0.25, 0.12), color=(0.8, 1.0, 0.85), strength=0.9, alpha=0.2, nframes=n)
    if snow:
        L.particle_cloud((center[0], center[1], depth / 2), (24, 24, depth), count=snow, radius=0.006, nframes=n,
                         drift=(0.05, 0.03, 0.02), name="plankton",
                         mat=L.mat_principled("plk", (0.8, 0.9, 0.8), rough=1, emit=(0.5, 0.6, 0.5), emit_strength=0.15))
    return out


def caustic_socket(mat):
    """The MULTIPLY node that scales the caustic emission in mat_caustic_ground (for a blackout)."""
    for nd in mat.node_tree.nodes:
        if nd.type == "MATH" and nd.operation == "MULTIPLY":
            for lk in nd.outputs[0].links:
                if lk.to_socket.name == "Emission Strength":
                    return nd.inputs[1]
    return None


def seabed_shot(L, n, cam_a, cam_b, whale_from=None, blackout=None, shadow=None):
    """S01 / S17: Packard reaching for a lobster by a rock. whale_from: animate the lunge in from above;
    blackout: frame of the hard black; shadow: (f0, f1) a dark shape sliding across the top of frame."""
    env = cape_env(L, n)
    P = packard(L, loc=DIV01, rot=(-0.22, 0, 0.12))
    pose_reach(P)
    S.lobster(loc=(0.42, 1.18, 0.02), rot_z=-2.6, scale=1.4)
    for f in range(1, n + 1, 6):
        P["shoulderR"].rotation_euler = (-0.45 - 0.08 * math.sin(f * 0.15), 0, -0.1)
        P["shoulderR"].keyframe_insert("rotation_euler", frame=f)
    L.anim_swim(P, n, kick_rate=0.5, amp=0.12)
    reg = world_of(P["root"], (0, 0.66, -0.1))
    starts = []
    for b in range(4, n, 34):
        starts += [b + k for k in range(6)]
    S.bubbles_at(reg, starts, rise=1.8, spread=0.05, size=0.025, name="reg")
    cam, _ = L.camera(loc=cam_a, target=CAM01_T, lens=28)
    L.cam_keys(cam, [(1, cam_a), (n, cam_b)], ease=False)
    L.handheld(cam, n, amp=0.012, rate=0.45)
    fill = L.area((1.5, -2.0, 3.0), (0, 0, 0), energy=60, size=3, color=(0.7, 0.95, 0.85), name="fill")
    _aim(fill, (1.5, -2.0, 3.0), (0.2, 0.6, 0.3))
    if whale_from:
        W = S.humpback("hb", length=12.0)
        r = W["root"]
        f0, f1 = whale_from
        for f, loc, rot in ((1, (1.5, 11.0, 13.0), (-1.0, 0, PI)), (f0, (1.2, 8.0, 9.5), (-0.95, 0, PI)),
                            (f1, (0.6, 4.6, 6.3), (-0.85, 0, PI))):
            r.location = loc
            r.rotation_euler = rot
            r.keyframe_insert("location", frame=f)
            r.keyframe_insert("rotation_euler", frame=f)
        S.jaw_keys(W, [(1, 0.3, 1.0), (f0, 0.55, 1.2), (f1, 0.9, 1.6)])
        S.whale_swim(W, n, rate=0.5, amp=0.2)
    if shadow:
        W = S.humpback("hb", length=12.0)
        r = W["root"]
        f0, f1 = shadow
        for f, x in ((1, -18.0), (f0, -14.0), (f1, 1.0), (n, 3.5)):
            r.location = (x, 2.5, 7.5)
            r.rotation_euler = (-0.15, 0.0, -PI / 2 + 0.2)
            r.keyframe_insert("location", frame=f)
            r.keyframe_insert("rotation_euler", frame=f)
        L.linear_fcurves(r)
        S.whale_swim(W, n, rate=0.4, amp=0.2)
    if blackout:
        b = blackout
        occ = L.prim("sphere", loc=CAM01_A + Vector((0.4, 0.8, -0.3)), segments=24, ring_count=12, radius=3.2, name="mouthdark")
        L.assign(occ, L.mat_principled("occm", (0.0, 0.0, 0.0), rough=1.0))
        occ.scale = (0.001,) * 3
        occ.keyframe_insert("scale", frame=b - 1)
        occ.scale = (1, 1, 1)
        occ.keyframe_insert("scale", frame=b)
        for fc in L._fcurves(occ.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
        S.energy_keys(env["sun"], [(1, 4.5), (b - 1, 4.5), (b, 0.0)], "CONSTANT")
        S.energy_keys(fill, [(1, 60), (b - 1, 60), (b, 0.0)], "CONSTANT")
        cs = caustic_socket(env["sand"])
        if cs is not None:
            for f, v in ((1, 0.3), (b - 1, 0.3), (b, 0.0)):
                cs.default_value = v
                cs.keyframe_insert("default_value", frame=f)
            S._linear_node_anim(env["sand"])
            for fc in L._fcurves(env["sand"].node_tree.animation_data.action):
                if "inputs[1]" in fc.data_path:
                    for kp in fc.keyframe_points:
                        kp.interpolation = "CONSTANT"
        leak = L.point(reg + Vector((0.3, -0.2, 0.6)), energy=0, color=SLIT, radius=0.1, name="leak")
        S.energy_keys(leak, [(1, 0), (b - 1, 0), (b, 2.5)], "CONSTANT")
        S.no_shadow(leak)
        S.shake(cam, b, length=4, amp=0.06, rot=0.02)
    _finish(L)
    return P, cam


# ----------------------------------------------------------------------------- S01 / S17 (loop pair)

def S01(L, n):
    seabed_shot(L, n, CAM01_A, CAM01_B, whale_from=(30, 64), blackout=65)


def S17(L, n):
    a0 = CAM01_A - (CAM01_T - CAM01_A).normalized() * 0.6 + Vector((-0.2, 0, 0.1))
    seabed_shot(L, n, a0, CAM01_A, shadow=(80, n))


# ----------------------------------------------------------------------------- S02 map background

def S02(L, n):
    S.setup()
    S.sky_gradient(top=(0.3, 0.5, 0.8), horizon=(0.8, 0.85, 0.9))
    sb = L.prim("plane", loc=(0, 0, -6), size=300, name="bed")
    L.assign(sb, S.mat_caustic_ground("bedm", c1=(0.12, 0.3, 0.25), c2=(0.5, 0.52, 0.4), strength=0.15, scale=0.5,
                                      nframes=n, base_scale=0.04))
    w = L.prim("plane", loc=(0, 0, 0), size=300, name="water")
    L.assign(w, S.mat_water_surface("aerialw", color=(0.0, 0.22, 0.2), rough=0.05, alpha=0.6, ripple=0.3, nframes=n))
    B = S.lobster_boat("lb")
    B["root"].location = (6, 10, 0)
    B["root"].rotation_euler = (0, 0, 0.6)
    B["root"].scale = (1.6, 1.6, 1.6)
    L.sun(rot=(0.5, 0.2, 0.4), energy=4, color=(1, 0.95, 0.85))
    cam, _ = L.camera(loc=(0, 0, 70), lens=35)
    cam.rotation_euler = (0, 0, 0.25)
    L.cam_keys(cam, [(1, (0, 0, 70)), (n, (3, 5, 60))], ease=False)
    _finish(L)


# ----------------------------------------------------------------------------- S03 split-level descent

def S03(L, n):
    S.setup(vol_end=80)
    S.sky_gradient(top=(0.2, 0.42, 0.8), horizon=(0.75, 0.85, 0.92), strength=1.0, sun_dir=(0.4, 0.6, 0.7),
                   sun_col=(1, 0.95, 0.85), sun_strength=6.0, below=(0.2, 0.35, 0.35))
    D = DEPTH
    S.world_volume(color=(0.12, 0.42, 0.3), density=0.07, anisotropy=0.6, absorption=(0.2, 0.55, 0.35), center=(0, 25, -D / 2),
                   size=(80, 60, D + 0.2))
    sea = S.ocean(size=120, nframes=n, wave_scale=0.35, choppiness=0.8, resolution=9, spatial=40, wind=8, foam=False,
                  mat=S.mat_ocean("sea_d", deep=(0.0, 0.12, 0.12), shallow=(0.05, 0.35, 0.32), rough=0.05,
                                  under=(0.45, 0.8, 0.65), under_strength=1.2))
    sea.location = (0, 55, 0)  # front edge of the water 'tank' at y = -5
    edge = L.prim("cube", loc=(0, -5.0, -0.06), name="cutline")
    edge.scale = (60, 0.03, 0.08)
    L.assign(edge, L.mat_emission("cutm", (0.8, 1.0, 0.95), 1.5))
    sand = S.mat_caustic_ground("capesand", c1=(0.3, 0.3, 0.22), c2=(0.52, 0.5, 0.38), caustic=(0.8, 1.0, 0.85),
                                strength=0.3, scale=1.4, nframes=n)
    sb = L.seabed(size=80, strength=0.25, mat=sand)
    sb.location = (0, 25, -D)
    B = S.lobster_boat("lb")
    br = B["root"]
    br.rotation_euler = (0, 0, 0.35)
    S.bob(br, n, amp=0.12, rate=0.3, tilt=0.04, base=(1.0, 14.0, -0.1))
    P = packard(L)
    r = P["root"]
    for f, z in ((1, -1.4), (int(n * 0.55), -7.5), (n, -11.8)):
        r.location = (-0.5, 12.0, z)
        r.rotation_euler = (PI / 2 - 0.15, 0, 0.5)
        r.keyframe_insert("location", frame=f)
        r.keyframe_insert("rotation_euler", frame=f)
    L.anim_swim(P, n, kick_rate=0.6, amp=0.2)
    for tag, s in (("L", -1), ("R", 1)):
        P[f"shoulder{tag}"].rotation_euler = (-2.7, 0, s * 0.3)
    zk = [(1, -1.4), (int(n * 0.55), -7.5), (n, -11.8)]

    def zat(f):
        for (fa, za), (fb, zb) in zip(zk[:-1], zk[1:]):
            if fa <= f <= fb:
                return za + (zb - za) * (f - fa) / (fb - fa)
        return zk[-1][1]
    for k, f in enumerate(range(2, n - 4, 7)):
        S.bubbles_at((-0.45, 12.25, zat(f) + 0.75), [f, f + 1, f + 2, f + 3], rise=3.5, spread=0.08, size=0.06,
                     life=(30, 48), seed=k, name=f"db{k}")
    sun = L.sun(rot=(0.45, 0.2, 0.6), energy=4.0, color=(1, 0.97, 0.9), angle=3)
    S.god_rays(center=(0, 14, -0.15), count=7, length=D, spread=7, tilt=(0.25, 0.12), color=(0.8, 1.0, 0.85),
               strength=0.8, alpha=0.18, nframes=n)
    tgt = L.link(bpy.data.objects.new("ctgt", None))
    for f, p in ((1, (0.5, 14, 0.8)), (int(n * 0.35), (0.0, 13, -3.0)), (n, (-0.3, 12.5, -9.0))):
        tgt.location = p
        tgt.keyframe_insert("location", frame=f)
    cam, _ = L.camera(loc=(2.0, -8.0, 0.8), target=tgt, lens=24)
    L.cam_keys(cam, [(1, (2.0, -8.0, 0.8)), (n, (1.6, -7.0, 0.5))])
    L.handheld(cam, n, amp=0.04, rate=0.4)
    _finish(L)


# ----------------------------------------------------------------------------- S04 imagined shark

def S04(L, n):
    S.setup(vol_end=40)
    L.set_world(color=(0.0, 0.004, 0.006), strength=1)
    S.world_volume(color=(0.12, 0.3, 0.3), density=0.05, anisotropy=0.5, center=(0, 0, 0), size=(40, 40, 20))
    sh = L.shark("shark", length=3.5, color=(0.3, 0.33, 0.36))
    r = sh["root"]
    for f, x in ((1, -9.0), (n, 9.0)):
        r.location = (x, 6.0, 0.2)
        r.rotation_euler = (0, 0, -PI / 2)
        r.keyframe_insert("location", frame=f)
        r.keyframe_insert("rotation_euler", frame=f)
    L.linear_fcurves(r)
    L.anim_shark_swim(sh, n, rate=1.6, amp=0.4)
    under = L.area((0, 6, -4), (0, 0, 0), energy=900, size=12, color=(0.5, 0.75, 0.8), name="under")
    under.rotation_euler = (PI, 0, 0)
    rimt = L.area((0, 9, 4), (0, 0, 0), energy=300, size=8, color=(0.4, 0.7, 0.8), name="rimtop")
    _aim(rimt, (0, 10, 4), (0, 6, 0))
    L.particle_cloud((0, 4, 0), (20, 10, 8), count=900, radius=0.006, nframes=n, drift=(-0.6, 0, 0), name="silt",
                     mat=L.mat_principled("siltm", (0.6, 0.7, 0.7), rough=1, emit=(0.4, 0.5, 0.5), emit_strength=0.3))
    tgt = L.link(bpy.data.objects.new("tg", None))
    for f, x in ((1, -3.0), (n, 4.0)):
        tgt.location = (x, 6.0, 0.6)
        tgt.keyframe_insert("location", frame=f)
    cam, _ = L.camera(loc=(0, -2.5, 0.3), target=tgt, lens=35)
    L.handheld(cam, n, amp=0.03, rate=0.8)
    sc = bpy.context.scene
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.6
    _finish(L)


# ----------------------------------------------------------------------------- mouth interior (S05 / S08 / S09 / S12)

def mouth_set(L, n, slit_energy=60, vol=0.14):
    """Inside the closed mouth: soft dark cavity, tongue floor, pale baleen curtains along the roof edge, a thin slit
    of daylight where the lips meet (+Y). Returns dict (pivot for room tilt, slit light, slit material)."""
    S.setup(vol_end=20)
    L.set_world(color=(0, 0, 0), strength=0)
    piv = L.link(bpy.data.objects.new("mouthroom", None))
    out = {"piv": piv}
    tissue = L.mat_principled("tissue", (0.11, 0.06, 0.06), rough=0.3)
    tissue.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.8
    cav = L.prim("sphere", loc=(0, 0, 0), segments=32, ring_count=16, radius=1.0, name="cavity")
    cav.scale = (2.3, 3.4, 1.35)
    L.smooth(cav)
    L.add_displace(cav, strength=0.12, scale=0.8, name="cavd")
    L.assign(cav, tissue)
    cav.parent = piv
    tg = L.prim("sphere", loc=(0, 0.3, -1.15), segments=24, ring_count=12, radius=1.0, name="tongue")
    tg.scale = (1.7, 2.6, 0.5)
    L.smooth(tg)
    L.assign(tg, L.mat_principled("tonguem", (0.16, 0.08, 0.08), rough=0.35))
    tg.parent = piv
    bal = L.mat_principled("baleenm", (0.42, 0.38, 0.3), rough=0.6)
    for sx in (-1, 1):
        for k in range(36):
            y = -2.6 + k * 0.15
            u = y / 3.4
            x = sx * 2.0 * math.sqrt(max(0.05, 1 - u * u)) * 0.92
            pl = L.prim("cube", loc=(x, y, 0.55), name="baleen")
            pl.scale = (0.012, 0.06, 0.45)
            pl.rotation_euler = (0, sx * 0.25, 0)
            L.assign(pl, bal)
            pl.parent = piv
    sm = L.mat_emission("slitm", SLIT, 12)
    sl = L.prim("cube", loc=(0, 3.25, 0.15), name="slit")
    sl.scale = (1.2, 0.02, 0.012)
    L.assign(sl, sm)
    sl.parent = piv
    sp = L.spot((0, 3.15, 0.15), (0, 0, 0), energy=slit_energy, size_deg=70, blend=0.8, color=SLIT, name="slitlight")
    _aim(sp, (0, 3.15, 0.15), (0, -1, -0.3))
    sp.parent = piv
    S.no_shadow(sp)
    out["slit"], out["slit_mat"] = sp, sm
    vb = L.water_volume(center=(0, 0, 0), size=(5, 7.4, 3.2), color=(0.3, 0.6, 0.45), density=vol, anisotropy=0.6,
                        name="mouthwater")
    vb.parent = piv
    rimL = L.area((0, 2.0, 1.0), (0, 0, 0), energy=30, size=1.5, color=SLIT, name="rimarea")
    _aim(rimL, (0.3, 2.2, 0.9), (0, 0, -0.1))
    rimL.parent = piv
    out["rim"] = rimL
    # bubbles pooled against the roof (silver puddles that grow)
    pm = L.mat_principled("poolm", (0.7, 0.85, 0.85), rough=0.05, metal=0.5, emit=(0.3, 0.45, 0.45), emit_strength=0.4)
    pools = []
    for k, (x, y) in enumerate(((0.1, 0.4), (-0.3, -0.1), (0.4, -0.3))):
        po = L.prim("sphere", loc=(x, y, 1.22), segments=16, ring_count=8, radius=0.25 - k * 0.05, name="pool")
        po.scale = (1, 0.8, 0.18)
        L.assign(po, pm)
        po.parent = piv
        pools.append(po)
    out["pools"] = pools
    L.particle_cloud((0, 0, 0), (3.5, 5, 2), count=300, radius=0.005, nframes=n, drift=(0, 0.02, 0.01), name="mote",
                     mat=L.mat_principled("motem", (0.6, 0.7, 0.6), rough=1, emit=(0.4, 0.5, 0.45), emit_strength=0.3)).parent = piv
    return out


def _mouth_diver(L, n, M, loc=(0.0, 0.2, -0.15), upright=True):
    P = packard(L)
    r = P["root"]
    r.location = loc
    r.parent = M["piv"]
    if upright:
        r.rotation_euler = (PI / 2 - 0.35, 0, PI + 0.4)
        for tag in ("L", "R"):
            P[f"hip{tag}"].rotation_euler = (0.5, 0, 0)
            P[f"knee{tag}"].rotation_euler = (-0.9, 0, 0)
    reg = world_of(r, (0, 0.66, -0.1))
    return P, reg


def _pool_grow(M, n):
    for k, po in enumerate(M["pools"]):
        s0 = tuple(po.scale)
        po.scale = (s0[0] * 0.6, s0[1] * 0.6, s0[2])
        po.keyframe_insert("scale", frame=1)
        po.scale = s0
        po.keyframe_insert("scale", frame=n)


def S05(L, n):
    M = mouth_set(L, n)
    P, reg = _mouth_diver(L, n, M)
    # pats his arms / legs, then reaches out to the soft wall (+X)
    sh = P["shoulderR"]
    for f, rot in ((1, (-2.4, 0, 0.6)), (12, (-2.9, 0, 0.2)), (22, (-2.4, 0, 0.7)), (32, (-2.9, 0, 0.1)),
                   (44, (-1.6, 0, -0.6)), (n, (-1.5, 0, -0.75))):
        sh.rotation_euler = rot
        sh.keyframe_insert("rotation_euler", frame=f)
    for f, rot in ((1, (-2.6, 0, -0.4)), (16, (-2.9, 0, -0.1)), (28, (-2.5, 0, -0.5)), (n, (-2.7, 0, -0.3))):
        P["shoulderL"].rotation_euler = rot
        P["shoulderL"].keyframe_insert("rotation_euler", frame=f)
    S.bubbles_at(reg, [3, 4, 5, 6, 30, 31, 32, 33], rise=0.9, spread=0.05, size=0.03, life=(30, 40), name="rb")
    _pool_grow(M, n)
    cam, _ = L.camera(loc=(-0.4, -2.0, 0.2), target=(0.1, 0.3, -0.05), lens=35)
    L.cam_keys(cam, [(1, (-0.4, -2.0, 0.2)), (n, (-0.3, -1.6, 0.15))])
    L.handheld(cam, n, amp=0.008, rate=0.4)
    kl = L.point((-0.6, -0.9, 0.6), energy=2.0, color=(0.6, 0.8, 0.75), radius=0.3, name="faint")
    S.no_shadow(kl)
    _finish(L)


def S08(L, n):
    M = mouth_set(L, n, slit_energy=50)
    P, reg = _mouth_diver(L, n, M)
    for tag, rot in (("L", (-2.7, 0, -0.3)), ("R", (-2.6, 0, 0.4))):
        P[f"shoulder{tag}"].rotation_euler = rot
    starts = []
    for b in range(2, n, 22):
        starts += [b + k for k in range(7)]
    S.bubbles_at(reg, starts, rise=0.9, spread=0.04, size=0.025, life=(28, 36), name="rb")
    _pool_grow(M, n)
    V = world_of(P["valve"], (0, 0, 0))
    gl = L.point(V + Vector((0.3, -0.3, 0.3)), energy=1.5, color=(0.8, 1.0, 0.9), radius=0.05, name="glint")
    S.no_shadow(gl)
    head = world_of(P["root"], (0, 0.6, -0.05))
    piv = L.link(bpy.data.objects.new("orb", None))
    piv.location = head
    cam, _ = L.camera(loc=(0, 0, 0), target=head, lens=50)
    cam.parent = piv
    cam.location = (0.35, -1.15, 0.12)
    piv.rotation_euler = (0, 0, -0.13)
    piv.keyframe_insert("rotation_euler", frame=1)
    piv.rotation_euler = (0, 0, 0.13)
    piv.keyframe_insert("rotation_euler", frame=n)
    L.dof(cam, target=P["reg"], fstop=2.4)
    _finish(L)


def S09(L, n):
    M = mouth_set(L, n, slit_energy=55)
    P = packard(L)
    r = P["root"]
    r.parent = M["piv"]
    r.location = (0.1, 0.1, -0.45)
    curl(P)
    L.flicker(M["slit"], n, base=55, seed=6, depth=0.7, rate=0.4, blackouts=((30, 33), (58, 60)))
    rnd = random.Random(2)
    S.emit_keys(M["slit_mat"], [(f, 12 * (0.3 + 0.7 * rnd.random())) for f in range(1, n + 1, 3)])
    reg = world_of(r, (0, 0.66, -0.1))
    S.bubbles_at(reg, [5, 6, 7, 40, 41, 42], rise=0.9, spread=0.04, size=0.025, life=(30, 40), name="rb")
    piv = M["piv"]
    for f in range(1, n + 1, 8):
        piv.rotation_euler = (0.03 * math.sin(f * 0.07), 0.04 * math.sin(f * 0.05 + 1), 0)
        piv.keyframe_insert("rotation_euler", frame=f)
    kl = L.point((-0.9, -1.0, 0.7), energy=4.0, color=(0.6, 0.8, 0.75), radius=0.3, name="faint")
    S.no_shadow(kl)
    cam, _ = L.camera(loc=(-1.1, -2.1, 0.25), target=(0.1, 0.1, -0.45), lens=35)
    L.cam_keys(cam, [(1, (-1.1, -2.1, 0.25)), (n, (-0.95, -1.85, 0.2))])
    _finish(L)


def S12(L, n):
    M = mouth_set(L, n, slit_energy=30)
    P = packard(L)
    r = P["root"]
    r.parent = M["piv"]
    r.location = (0.1, 0.1, -0.45)
    curl(P)
    S.energy_keys(M["slit"], [(1, 25), (n, 140)])
    S.emit_keys(M["slit_mat"], [(1, 8), (n, 30)])
    S.energy_keys(M["rim"], [(1, 8), (n, 30)])
    reg = world_of(r, (0, 0.66, -0.1))
    S.bubbles_at(reg, [4, 5, 6, 38, 39, 40], rise=0.9, spread=0.04, size=0.025, life=(30, 40), name="rb")
    cam, _ = L.camera(loc=(0, 0, 0), lens=28)
    cam.parent = M["piv"]
    cam.location = (-1.0, -2.3, 0.35)
    cam.rotation_euler = (PI / 2 - 0.25, 0, -0.4)
    piv = M["piv"]
    piv.rotation_euler = (0, 0, 0)
    piv.keyframe_insert("rotation_euler", frame=1)
    piv.rotation_euler = (math.radians(25), 0, 0)
    piv.keyframe_insert("rotation_euler", frame=n)
    _finish(L)


# ----------------------------------------------------------------------------- S06 pull-back reveal

def S06(L, n):
    env = cape_env(L, n, rocks=False, snow=600, size=80, center=(0, 0))
    W = S.humpback("hb", length=12.0)
    r = W["root"]
    r.location = (0.0, 0.0, 6.0)
    r.rotation_euler = (0.18, 0.12, -0.6)
    S.jaw_keys(W, [(1, 0.0, 1.55), (n, 0.0, 1.6)])
    S.whale_swim(W, n, rate=0.3, amp=0.12)
    # x-ray hint: soft glow where the diver is, on the throat side facing the camera
    _upd()
    gp = world_of(r, (0.55, 3.0, -0.9))
    gl = L.prim("sphere", loc=gp, segments=16, ring_count=8, radius=0.75, name="diverglow")
    gl.parent = r
    gl.matrix_parent_inverse = r.matrix_world.inverted()
    gm = glow_mat(L, "diverglowm", (1.0, 0.9, 0.55), 5.0, power=1.5)
    L.assign(gl, gm)
    S.emit_keys(gm, [(1, 0.0), (int(n * 0.35), 0.0), (int(n * 0.6), 6.0), (n, 5.0)])
    pl = L.point(gp + Vector((0.4, -0.6, 0)), energy=0, color=(1, 0.85, 0.5), radius=0.3, name="glowpt")
    S.energy_keys(pl, [(1, 0), (int(n * 0.35), 0), (int(n * 0.6), 60)])
    school = L.fish_school((-4.5, 4.0, 7.5), count=50, radius=2.0, nframes=n, orbit_speed=0.8, size=0.1)
    snout = world_of(r, (0, 6.0, -0.15))
    fwd = (world_of(r, (0, 7.0, 0)) - world_of(r, (0, 6.0, 0))).normalized()
    side = (world_of(r, (1.0, 6.0, 0)) - world_of(r, (0, 6.0, 0))).normalized()
    away = (fwd * 0.75 + side * 0.6).normalized()
    away.z = 0.0
    away.normalize()
    c0 = snout + away * 0.6
    c1 = snout + away * 15.0 + Vector((0, 0, 0.5))
    cam, _ = L.camera(loc=c0, target=snout + Vector((0, 0, 0)), lens=24)
    tg = cam.constraints[0].target
    tg.keyframe_insert("location", frame=1)
    tg.location = world_of(r, (0, 0.5, 0))
    tg.keyframe_insert("location", frame=n)
    cam.location = c0
    cam.keyframe_insert("location", frame=1)
    cam.location = c0.lerp(c1, 0.75)
    cam.keyframe_insert("location", frame=int(n * 0.45))
    cam.location = c1
    cam.keyframe_insert("location", frame=n)
    L.handheld(cam, n, amp=0.03, rate=0.4)
    key = L.area((8, -10, 14), (0, 0, 0), energy=4000, size=10, color=SUN_COL, name="key")
    _aim(key, (8, -10, 14), (0, 0, 6))
    _finish(L)


# ----------------------------------------------------------------------------- S07 the lunge (wide)

def S07(L, n):
    env = cape_env(L, n, snow=600, size=80)
    school = L.fish_school((2.5, 0.0, 4.2), count=90, radius=1.8, nframes=n, orbit_speed=1.6, size=0.09)
    P = packard(L, loc=(3.2, 0.6, 3.0), rot=(0.1, 0, PI * 0.8))
    L.anim_swim(P, n, kick_rate=0.7, amp=0.25)
    W = S.humpback("hb", length=12.0)
    r = W["root"]
    eat = int(n * 0.72)
    for f, loc, rot in ((1, (-17.0, 2.0, 2.9), (0.42, 0, -PI / 2 + 0.1)), (int(n * 0.45), (-8.5, 1.2, 3.3), (0.38, 0, -PI / 2 + 0.05)),
                        (eat, (-1.6, 0.4, 4.1), (0.3, 0, -PI / 2)), (n, (1.6, 0.0, 4.9), (0.22, 0, -PI / 2))):
        r.location = loc
        r.rotation_euler = rot
        r.keyframe_insert("location", frame=f)
        r.keyframe_insert("rotation_euler", frame=f)
    S.jaw_keys(W, [(1, 0.0, 1.0), (int(n * 0.35), 0.35, 1.1), (int(n * 0.6), 0.95, 1.5), (eat + 4, 0.8, 1.7),
                   (n, 0.08, 1.75)])
    S.whale_swim(W, n, rate=0.45, amp=0.22)
    # school + diver vanish into the mouth as it sweeps through
    school.keyframe_insert("scale", frame=eat - 6)
    school.keyframe_insert("location", frame=eat - 6)
    school.scale = (0.2, 0.2, 0.2)
    school.location = (3.0, 0.2, 4.6)
    school.keyframe_insert("scale", frame=eat + 4)
    school.keyframe_insert("location", frame=eat + 4)
    school.scale = (0.001,) * 3
    school.keyframe_insert("scale", frame=eat + 8)
    pr = P["root"]
    pr.keyframe_insert("location", frame=eat - 2)
    pr.location = (3.4, 0.4, 3.9)
    pr.keyframe_insert("location", frame=eat + 3)
    for f, h in ((1, False), (eat + 3, False), (eat + 4, True)):
        for o in [o_ for o_ in bpy.data.objects if o_.name.startswith("packard")]:
            if o.type in ("MESH", "CURVE"):
                o.hide_render = h
                o.keyframe_insert("hide_render", frame=f)
    pc = L.particle_cloud((-1.0, 0.5, 0.3), (8, 4, 1.0), count=900, radius=0.007, nframes=n, drift=(0.2, 0, 0.25),
                          name="sandpuff", mat=L.mat_principled("puffm", (0.6, 0.58, 0.45), rough=1, emit=(0.4, 0.4, 0.3),
                                                                emit_strength=0.25))
    pc.scale = (0.05,) * 3
    pc.keyframe_insert("scale", frame=int(n * 0.35))
    pc.scale = (1.2, 1.2, 1.6)
    pc.keyframe_insert("scale", frame=n)
    cam, _ = L.camera(loc=(-1.0, -14.5, 3.6), target=(-0.5, 0, 4.2), lens=20)
    L.cam_keys(cam, [(1, (-1.0, -14.5, 3.6)), (n, (0.5, -13.5, 3.8))])
    L.handheld(cam, n, amp=0.03, rate=0.35)
    key = L.area((6, -12, 13), (0, 0, 0), energy=5000, size=12, color=SUN_COL, name="key")
    _aim(key, (6, -12, 13), (0, 0, 3))
    _finish(L)


# ----------------------------------------------------------------------------- S10 / S11 x-ray diagram

def _xray_bg(L):
    L.set_world(color=(0, 0, 0), strength=0)
    bg = L.prim("plane", loc=(0, 6, 0), rot=(PI / 2, 0, 0), size=1, name="bg")
    bg.scale = (60, 60, 1)
    L.assign(bg, S.flat_mat("bgm", (0.004, 0.035, 0.04), 1))
    gm = S.flat_mat("gridm", (0.02, 0.1, 0.1), 1)
    for k in range(-24, 25):
        for horiz in (0, 1):
            cu = bpy.data.curves.new("g", "CURVE")
            cu.dimensions = "3D"
            cu.bevel_depth = 0.012
            sp = cu.splines.new("POLY")
            sp.points.add(1)
            if horiz:
                sp.points[0].co, sp.points[1].co = (-20, 5.5, k * 0.8, 1), (20, 5.5, k * 0.8, 1)
            else:
                sp.points[0].co, sp.points[1].co = (k * 0.8, 5.5, -20, 1), (k * 0.8, 5.5, 20, 1)
            o = L.link(bpy.data.objects.new("grid", cu))
            o.data.materials.append(gm)


def _xray_whale(L, n):
    """Whale standing snout-up (fits the 9:16 frame), side profile, slight lean; cavity/diver/throat in whale space."""
    W = S.humpback("xw", length=12.0)
    _xr(L, "xw", xray_mat(L, "xwm", (0.8, 0.95, 1.0), 2.5))
    r = W["root"]
    tilt = L.link(bpy.data.objects.new("tilt", None))
    tilt.rotation_euler = (0, -0.3, 0)
    r.parent = tilt
    r.rotation_euler = (PI / 2, 0, PI / 2)
    S.jaw_keys(W, [(1, 0.0, 1.5)])

    def local(o, loc, scl=None, rot=(0, 0, 0)):
        o.parent = r
        o.location = loc
        o.rotation_euler = rot
        if scl:
            o.scale = scl
        return o
    cav = local(L.prim("sphere", segments=24, ring_count=12, radius=1.0, name="cav"), (0, 3.3, -0.75), (0.9, 2.3, 0.65))
    L.assign(cav, xray_mat(L, "cavm", (0.2, 0.75, 0.7), 1.5, power=1.0, base=0.15))
    D = L.char_diver(name="xd", light_on=False, tanks="single")
    _xr(L, "xd", xray_mat(L, "xdm", (1.0, 0.85, 0.3), 3.0, power=1.2, base=0.12))
    local(D["root"], (0.3, 3.4, -0.8), (0.85, 0.85, 0.85), rot=(0, PI / 2, 0.3))
    for tag in ("L", "R"):
        D[f"hip{tag}"].rotation_euler = (1.1, 0, 0)
        D[f"knee{tag}"].rotation_euler = (-1.4, 0, 0)
    tm = L.mat_emission("throatm", (1.0, 0.15, 0.1), 5)
    th = S.tube([(0, 1.3, -0.45), (0, 0.4, -0.35), (0, -0.8, -0.2)], radius=0.08, mat=tm, name="throat", order=3)
    th.parent = r
    _upd()
    return W, D, tm, world_of(r, (0, 1.0, -0.4))


def S10(L, n):
    _xray_bg(L)
    W, D, tm, thr = _xray_whale(L, n)
    S.emit_keys(tm, [(f, 7 if (f // 12) % 2 else 2.5) for f in range(1, n + 1, 6)])
    cam, _ = L.camera(loc=(0.0, -30, 0.6), lens=50)
    cam.rotation_euler = (PI / 2, 0, 0)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 15.0
    cam.data.keyframe_insert("ortho_scale", frame=1)
    cam.data.ortho_scale = 9.0
    cam.data.keyframe_insert("ortho_scale", frame=n)
    L.cam_keys(cam, [(1, (0.0, -30, 0.6)), (n, (thr.x, -30, thr.z + 1.2))])
    _finish(L)


def S11(L, n):
    _xray_bg(L)
    # throat opening (red ring, fist-sized) vs a human fist and the diver's shoulders
    ring = L.prim("torus", loc=(0.0, 0, 0.3), rot=(PI / 2, 0, 0), major_radius=0.06, minor_radius=0.012, name="throatring")
    rm = L.mat_emission("ringm", (1.0, 0.15, 0.1), 6)
    L.assign(ring, rm)
    S.emit_keys(rm, [(f, 8 if (f // 10) % 2 else 3) for f in range(1, n + 1, 5)])
    inner = L.prim("cyl", loc=(0, 0.01, 0.3), rot=(PI / 2, 0, 0), vertices=24, radius=0.055, depth=0.005, name="throathole")
    L.assign(inner, S.flat_mat("holem", (0.0, 0.0, 0.0), 1))
    fist = S.hand("fist", color=(0.9, 0.9, 0.9), scale=0.9, emit=(0.85, 0.95, 1.0))
    S.curl(fist, 1, 1.4)
    fr = fist["root"]
    fr.location = (0.24, -0.05, 0.3)
    fr.rotation_euler = (PI / 2, 0, 0.3)
    for f, s in ((1, 0.001), (5, 0.001), (10, 1.15), (14, 0.9)):
        fr.scale = (s,) * 3
        fr.keyframe_insert("scale", frame=f)
    _xr(L, "fist", xray_mat(L, "fistm", (0.9, 0.97, 1.0), 3.0, power=1.2, base=0.15))
    D = L.char_diver(name="xd", light_on=False, tanks="single")
    _xr(L, "xd", xray_mat(L, "xdm", (1.0, 0.85, 0.3), 3.0, power=1.2, base=0.12))
    dr = D["root"]
    dr.location = (0.0, 0.4, -0.52)
    dr.rotation_euler = (PI / 2, 0, 0)  # head toward the opening, shoulders far wider than the ring
    lbl = L.text3d("FIST", loc=(0.24, -0.05, 0.16), size=0.05, mat=L.mat_emission("lblm", (0.85, 0.95, 1.0), 2))
    lbl2 = L.text3d("THROAT", loc=(-0.02, -0.05, 0.4), size=0.045, mat=L.mat_emission("lblm2", (1.0, 0.4, 0.3), 3))
    cam, _ = L.camera(loc=(0.05, -10, 0.05), lens=50)
    cam.rotation_euler = (PI / 2, 0, 0)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 1.6
    cam.data.keyframe_insert("ortho_scale", frame=1)
    cam.data.ortho_scale = 1.5
    cam.data.keyframe_insert("ortho_scale", frame=n)
    _finish(L)


# ----------------------------------------------------------------------------- surface shots (S13 / S14 / S15 / S16)

def day_sea(L, n, size=160, wave=0.4, res=10):
    S.setup(vol_end=80)
    S.sky_gradient(top=(0.18, 0.4, 0.8), horizon=(0.78, 0.86, 0.92), strength=1.0, sun_dir=(0.5, -0.6, 0.6),
                   sun_col=(1, 0.95, 0.85), sun_strength=8.0, below=(0.1, 0.25, 0.28))
    sea = S.ocean(size=size, nframes=n, wave_scale=wave, choppiness=0.9, resolution=res, spatial=50, wind=9, foam=True,
                  mat=S.mat_ocean("sea_day", deep=(0.0, 0.1, 0.12), shallow=(0.05, 0.35, 0.33), rough=0.05,
                                  under=(0.4, 0.75, 0.65), under_strength=1.0))
    sun = L.sun(rot=(math.radians(50), 0, math.radians(-150)), energy=4.5, color=(1, 0.96, 0.88), angle=2)
    return sea, sun


def foam_ring(L, loc, r0=0.5, r1=4.0, f0=1, f1=40, name="foam", z=0.05):
    m = L.mat_principled(name + "_m", (0.95, 0.97, 0.97), rough=0.6, emit=(0.6, 0.65, 0.65), emit_strength=0.4)
    o = L.prim("torus", loc=(loc[0], loc[1], z), major_radius=1.0, minor_radius=0.25, name=name)
    L.add_displace(o, strength=0.25, scale=0.3, name=name + "_d")
    L.assign(o, m)
    o.scale = (0.001, 0.001, 0.001)
    o.keyframe_insert("scale", frame=max(1, f0 - 1))
    o.scale = (r0, r0, 0.4)
    o.keyframe_insert("scale", frame=f0)
    o.scale = (r1, r1, 0.15)
    o.keyframe_insert("scale", frame=f1)
    return o


def splash(L, center, starts, count=60, speed=4.0, seed=3, name="spl", size=0.06):
    """White droplets thrown up and falling back (individual small spheres, ballistic keys)."""
    rnd = random.Random(seed)
    m = L.mat_principled(name + "_m", (0.95, 0.98, 1.0), rough=0.2, emit=(0.5, 0.55, 0.6), emit_strength=0.5)
    c = Vector(center)
    for i in range(count):
        st = rnd.choice(starts)
        o = L.prim("ico", loc=c, subdivisions=1, radius=size * rnd.uniform(0.5, 1.3), name=name)
        L.assign(o, m)
        o.visible_shadow = False
        v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(1.2, 2.5))).normalized() * speed * rnd.uniform(0.5, 1.2)
        o.scale = (0.001,) * 3
        o.keyframe_insert("scale", frame=st - 1)
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=st)
        p0 = c + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * 0.8
        for k in range(0, 21, 4):
            t = k / 24
            o.location = p0 + v * t + Vector((0, 0, -4.9 * t * t))
            o.keyframe_insert("location", frame=st + k)
        o.scale = (0.001,) * 3
        o.keyframe_insert("scale", frame=st + 22)


def S13(L, n):
    sea, sun = day_sea(L, n)
    W = S.humpback("hb", length=12.0)
    r = W["root"]
    for f, loc, pitch in ((1, (0, 9.0, -6.0), 0.75), (int(n * 0.3), (0, 8.0, -2.8), 0.95), (n, (0, 7.6, -2.6), 0.9)):
        r.location = loc
        r.rotation_euler = (pitch, 0, PI + 0.15)
        r.keyframe_insert("location", frame=f)
        r.keyframe_insert("rotation_euler", frame=f)
    # head swings side to side after breaching
    for k, f in enumerate(range(int(n * 0.35), n + 1, 12)):
        r.rotation_euler = (0.92, 0.25 * (1 if k % 2 else -1), PI + 0.15 + 0.3 * (1 if k % 2 else -1))
        r.keyframe_insert("rotation_euler", frame=f)
    S.jaw_keys(W, [(1, 0.0, 1.5), (int(n * 0.5), 0.0, 1.4), (n, 0.25, 1.2)])
    S.whale_swim(W, n, rate=0.5, amp=0.2)
    # light pouring into the parting lips
    lip = L.point((0, 3.2, 3.0), energy=0, color=(1, 0.95, 0.8), radius=0.5, name="lipgleam")
    S.energy_keys(lip, [(1, 0), (int(n * 0.6), 0), (n, 300)])
    foam_ring(L, (0, 4.5), 0.3, 2.6, int(n * 0.12), int(n * 0.6))
    splash(L, (0, 4.0, 0.3), [int(n * 0.15), int(n * 0.2), int(n * 0.25)], count=90, speed=6.0)
    L.particle_cloud((0, 4.0, 2.0), (6, 3, 4), count=700, radius=0.008, nframes=n, drift=(0.3, 0, -0.6), name="mist",
                     mat=L.mat_principled("mistm", (0.95, 0.97, 1.0), emit=(0.6, 0.65, 0.7), emit_strength=0.6))
    cam, _ = L.camera(loc=(1.1, -3.6, 0.8), target=(0, 4.2, 3.0), lens=24)
    L.cam_keys(cam, [(1, (1.1, -3.6, 0.8)), (n, (0.9, -3.0, 0.75))])
    L.handheld(cam, n, amp=0.06, rate=0.7, rot_amp=0.01)
    _finish(L)


def S14(L, n):
    sea, sun = day_sea(L, n)
    W = S.humpback("hb", length=12.0)
    r = W["root"]
    ej = 7
    for f, loc, rot in ((1, (0, 7.6, -2.6), (0.9, 0.25, PI + 0.45)), (ej, (0, 7.6, -2.7), (0.85, 0.3, PI + 0.4)),
                        (int(n * 0.6), (1.5, 8.5, -4.5), (0.5, 0.8, PI + 0.6)), (n, (2.5, 9.5, -7.5), (0.2, 1.4, PI + 0.7))):
        r.location = loc
        r.rotation_euler = rot
        r.keyframe_insert("location", frame=f)
        r.keyframe_insert("rotation_euler", frame=f)
    S.jaw_keys(W, [(1, 0.25, 1.2), (ej, 0.75, 1.1), (ej + 10, 0.6, 1.0), (n, 0.1, 1.0)])
    P = packard(L)
    pr = P["root"]
    for o in [o_ for o_ in bpy.data.objects if o_.name.startswith("packard") and o_.type in ("MESH", "CURVE")]:
        for f, h in ((1, True), (ej - 1, True), (ej, False)):
            o.hide_render = h
            o.keyframe_insert("hide_render", frame=f)
    for f, loc, rot in ((1, (0.1, 3.2, 1.0), (0.5, 0.2, PI)), (ej, (0.1, 3.0, 1.0), (0.6, 0.4, PI)),
                        (ej + 8, (-0.6, 2.2, 0.4), (1.8, 1.5, PI + 0.6)), (n, (-0.9, 1.9, -0.1), (2.2, 2.4, PI + 0.9))):
        pr.location = loc
        pr.rotation_euler = rot
        pr.keyframe_insert("location", frame=f)
        pr.keyframe_insert("rotation_euler", frame=f)
    for tag, s in (("L", -1), ("R", 1)):
        P[f"shoulder{tag}"].rotation_euler = (-1.0, 0, s * 1.2)
        P[f"hip{tag}"].rotation_euler = (0.4 * s, 0, 0)
    foam_ring(L, (-0.8, 0.8), 0.3, 2.5, ej + 6, n, name="efoam")
    splash(L, (-0.6, 1.0, 0.2), [ej + 7, ej + 9], count=60, speed=4.0, name="esp")
    S.bubbles_at((-0.8, 0.8, -0.3), [ej + 6 + k % 5 for k in range(30)], rise=0.6, spread=0.3, size=0.07, life=(10, 20),
                 name="foamb")
    foam_ring(L, (1.0, 6.0), 2.0, 3.0, 2, n, name="wfoam")
    cam, _ = L.camera(loc=(0.9, -3.0, 0.75), target=(-0.2, 3.5, 2.2), lens=24)
    L.cam_keys(cam, [(1, (0.9, -3.0, 0.75)), (n, (0.7, -2.4, 0.7))])
    L.handheld(cam, n, amp=0.05, rate=0.7, rot_amp=0.01)
    S.exposure_keys([(1, 0.0), (ej, 0.0), (ej + 1, 1.6), (ej + 2, 1.6), (ej + 3, 0.0)])
    _finish(L)


def S15(L, n):
    sea, sun = day_sea(L, n, wave=0.3)
    B = S.lobster_boat("lb")
    br = B["root"]
    arrive = int(n * 0.35)
    for f, y in ((1, -9.0), (arrive, -0.6), (n, 0.0)):
        br.location = (0.0, y, 0.0)
        br.rotation_euler = (0, 0, 0)
        br.keyframe_insert("location", frame=f)
    br.rotation_euler = (0, 0, 0)
    # Mayo (cap) at the starboard gunwale, leaning over the side
    M = L.char_figure(name="mayo", color=(0.035, 0.035, 0.04), height=1.8)
    mr = M["root"]
    mr.parent = br
    mr.location = (1.25, -1.6, 0.6)
    mr.rotation_euler = (0, 0, -PI / 2)
    cap = L.prim("cyl", loc=(0, 0.0, 0.23), vertices=16, radius=0.11, depth=0.06, name="mayo_cap")
    L.assign(cap, L.mat_principled("capm", (0.08, 0.15, 0.3), rough=0.6))
    cap.parent = M["head"]
    bill = L.prim("cube", loc=(0, 0.11, 0.21), name="mayo_bill")
    bill.scale = (0.08, 0.06, 0.01)
    L.assign(bill, cap.data.materials[0])
    bill.parent = M["head"]
    for f, lean, arm in ((1, 0.2, 0.6), (arrive, 0.3, 1.2), (int(n * 0.55), 0.85, 2.6), (int(n * 0.8), 0.6, 2.2), (n, 0.35, 1.6)):
        M["pelvis"].rotation_euler = (-lean, 0, 0)
        M["pelvis"].keyframe_insert("rotation_euler", frame=f)
        for tag in ("L", "R"):
            M[f"hip{tag}"].rotation_euler = (lean, 0, 0)
            M[f"hip{tag}"].keyframe_insert("rotation_euler", frame=f)
            M[f"shoulder{tag}"].rotation_euler = (arm, 0, 0)
            M[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
    # Packard in the water by the hull, hauled up to the gunwale
    P = packard(L)
    pr = P["root"]
    for f, loc, rot in ((1, (2.6, 1.0, -0.35), (PI / 2 - 0.2, 0, PI / 2)), (int(n * 0.55), (2.25, -1.4, -0.3), (PI / 2 - 0.1, 0, PI / 2)),
                        (int(n * 0.85), (2.0, -1.5, 0.75), (PI / 2 + 0.3, 0, PI / 2)), (n, (1.85, -1.5, 1.05), (PI / 2 + 0.6, 0, PI / 2))):
        pr.location = loc
        pr.rotation_euler = rot
        pr.keyframe_insert("location", frame=f)
        pr.keyframe_insert("rotation_euler", frame=f)
    for tag, s in (("L", -1), ("R", 1)):
        P[f"shoulder{tag}"].rotation_euler = (-0.3, 0, s * -0.3)
    foam_ring(L, (2.4, -1.2), 0.3, 1.6, int(n * 0.55), n, name="hfoam")
    L.particle_cloud((2.2, -1.4, 0.4), (0.8, 0.6, 0.8), count=150, radius=0.008, nframes=n, drift=(0, 0, -0.8), name="drips",
                     mat=L.mat_principled("dripm", (0.9, 0.95, 1.0), emit=(0.5, 0.6, 0.6), emit_strength=0.4))
    cam, _ = L.camera(loc=(7.5, -4.2, 0.6), target=(1.6, -1.2, 1.1), lens=35)
    L.cam_keys(cam, [(1, (7.5, -4.2, 0.6)), (n, (7.0, -3.9, 0.55))])
    L.handheld(cam, n, amp=0.04, rate=0.6)
    _finish(L)


def S16(L, n):
    sea, sun = day_sea(L, n, wave=0.25)
    sun.data.color = (1.0, 0.85, 0.65)
    sun.rotation_euler = (math.radians(65), 0, math.radians(-120))
    B = S.lobster_boat("lb")
    br = B["root"]
    S.bob(br, n, amp=0.05, rate=0.3, tilt=0.025, base=(0, 0, 0))
    # Packard seated on the deck against the gunwale, mask off; tank + fins beside him
    F = L.char_figure(name="packfig", color=(0.03, 0.03, 0.035), height=1.78)
    fr = F["root"]
    fr.parent = br
    fr.location = (1.35, -2.4, 0.6 - 0.83)
    fr.rotation_euler = (0, 0, PI / 2)
    F["pelvis"].rotation_euler = (0.3, 0, 0)
    F["neck"].rotation_euler = (0.35, 0, 0)
    F["hipL"].rotation_euler = (1.3, 0, 0.1)
    F["kneeL"].rotation_euler = (-0.1, 0, 0)
    F["hipR"].rotation_euler = (1.8, 0, -0.1)
    F["kneeR"].rotation_euler = (-1.6, 0, 0)
    F["shoulderL"].rotation_euler = (0.25, 0, -0.15)
    F["shoulderR"].rotation_euler = (0.55, 0, 0.1)
    F["elbowR"].rotation_euler = (0.7, 0, 0)
    met = L.mat_principled("tankm", (0.75, 0.77, 0.8), rough=0.25, metal=1)
    tk = L.prim("cyl", loc=(0.6, -1.4, 0.75), vertices=16, radius=0.09, depth=0.7, rot=(PI / 2, 0, 0.4), name="tank")
    L.assign(tk, met)
    tk.parent = br
    fm = L.mat_principled("finm", (0.95, 0.42, 0.05), rough=0.45)
    for k in range(2):
        fn = L.prim("cube", loc=(0.2 + k * 0.15, -3.1, 0.62), rot=(0, 0, 0.3 + k * 0.4), name="fin")
        fn.scale = (0.11, 0.3, 0.012)
        L.assign(fn, fm)
        fn.parent = br
    mask = L.prim("torus", loc=(0.9, -2.9, 0.64), major_radius=0.08, minor_radius=0.025, name="mask")
    L.assign(mask, fm)
    mask.parent = br
    cam, _ = L.camera(loc=(0.2, -5.8, 1.9), target=(1.2, -2.4, 0.9), lens=35)
    cam.parent = br
    L.cam_keys(cam, [(1, (0.2, -5.8, 1.9)), (n, (0.35, -5.2, 1.75))])
    fill = L.area((-2, -1, 3.5), (0, 0, 0), energy=150, size=3, color=(1.0, 0.85, 0.7), name="bounce")
    _aim(fill, (-2, -1, 3.5), (1.2, -2.4, 0.7))
    _finish(L)
