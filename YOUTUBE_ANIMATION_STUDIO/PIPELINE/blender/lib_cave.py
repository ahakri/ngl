"""Cave-diving builders shared by CAVE-* shorts (Boesmansgat shaft, Plura ice/restriction, diagrams, desert/snow exteriors).

Import from shots.py:
    import sys, os; sys.path.insert(0, <PIPELINE/blender>); import lib_cave as C
All functions take/return plain bpy objects and build on top of studio_lib (passed as L or imported here).
Conventions: Z up, metres. Camera helpers use quaternion aim keys (no TRACK_TO) so roll/dutch and shake are explicit.
"""
import bpy, bmesh, math, random, os
from mathutils import Vector, Quaternion, Matrix, noise
import studio_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_ANTON = os.path.join(os.path.dirname(HERE), "fonts", "Anton-Regular.ttf")
FONT_OSWALD = os.path.join(os.path.dirname(HERE), "fonts", "Oswald.ttf")
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

CYAN = (0.25, 0.9, 0.85)
ORANGE = (1.0, 0.45, 0.08)
YELLOW = (1.0, 0.78, 0.05)
TORCH = (1.0, 0.93, 0.8)


# ----------------------------------------------------------------------------- utils

def sm(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def lerp(a, b, t):
    return a + (b - a) * t


def vlerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def piecewise(keys, f, fn=sm):
    """keys: [(frame, value)], value float or tuple. Smooth interpolation between consecutive keys."""
    if f <= keys[0][0]:
        return keys[0][1]
    for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
        if f0 <= f <= f1:
            t = fn((f - f0) / max(1e-6, f1 - f0))
            if isinstance(v0, (tuple, list, Vector)):
                return tuple(lerp(a, b, t) for a, b in zip(v0, v1))
            return lerp(v0, v1, t)
    return keys[-1][1]


def render_quality(vol_tile="4", vol_samples=64, vol_end=60.0, vol_start=0.1, shadows=True):
    e = bpy.context.scene.eevee
    for k, v in (("volumetric_tile_size", vol_tile), ("volumetric_samples", vol_samples),
                 ("use_volumetric_shadows", shadows), ("volumetric_sample_distribution", 0.85),
                 ("use_volume_custom_range", True), ("volumetric_start", vol_start), ("volumetric_end", vol_end),
                 ("volumetric_light_clamp", 0.0), ("use_shadows", True)):
        try:
            setattr(e, k, v)
        except Exception:
            pass


def hide_from_frame(objs, f_hide=None, f_show=None):
    """Keyframe hide_render (constant). f_show: frame it appears; f_hide: frame it disappears."""
    for o in objs:
        if f_show is not None:
            o.hide_render = True
            o.keyframe_insert("hide_render", frame=1)
            o.hide_render = False
            o.keyframe_insert("hide_render", frame=f_show)
        if f_hide is not None:
            o.hide_render = False
            o.keyframe_insert("hide_render", frame=max(1, f_hide - 1))
            o.hide_render = True
            o.keyframe_insert("hide_render", frame=f_hide)
        _constant(o)


def _constant(o):
    ad = o.animation_data
    if ad and ad.action:
        for fc in L._fcurves(ad.action):
            if fc.data_path == "hide_render":
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"


def constant_keys(idblock):
    ad = getattr(idblock, "animation_data", None)
    if ad and ad.action:
        for fc in L._fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def key_scale(o, keys):
    for f, s in keys:
        o.scale = (s, s, s) if not isinstance(s, (tuple, list)) else s
        o.keyframe_insert("scale", frame=f)


def key_loc(o, keys):
    for f, p in keys:
        o.location = p
        o.keyframe_insert("location", frame=f)


def key_energy(light_obj, keys):
    for f, e in keys:
        light_obj.data.energy = e
        light_obj.data.keyframe_insert("energy", frame=f)


def key_input(node_input, keys):
    for f, v in keys:
        node_input.default_value = v
        node_input.keyframe_insert("default_value", frame=f)


# ----------------------------------------------------------------------------- camera

def camera(lens=28, name="cam", clip_end=400):
    c = bpy.data.cameras.new(name)
    c.lens = lens
    c.clip_start = 0.03
    c.clip_end = clip_end
    c.sensor_fit = "AUTO"
    o = L.link(bpy.data.objects.new(name, c))
    o.rotation_mode = "QUATERNION"
    bpy.context.scene.camera = o
    return o


def look_quat(pos, target, roll_deg=0.0):
    d = Vector(target) - Vector(pos)
    q = d.to_track_quat("-Z", "Y")
    if roll_deg:
        q = q @ Quaternion((0, 0, 1), math.radians(roll_deg))
    return q


def aim_cam(cam, n, keys, shake=0.0, rot_shake=0.0, rate=0.5, seed=1, shake_keys=None, fn=sm, step=1, lens_keys=None):
    """Keyframe camera along smooth piecewise keys: [(frame, pos, target, roll_deg)].
    shake = metres of positional noise, rot_shake = radians; shake_keys=[(frame, mult)] ramps the shake."""
    prev = None
    off = seed * 17.3
    for f in list(range(1, n + 1, step)) + ([n] if (n - 1) % step else []):
        pos = Vector(piecewise([(k[0], tuple(k[1])) for k in keys], f, fn))
        tgt = Vector(piecewise([(k[0], tuple(k[2])) for k in keys], f, fn))
        roll = piecewise([(k[0], k[3] if len(k) > 3 else 0.0) for k in keys], f, fn)
        mult = piecewise(shake_keys, f, sm) if shake_keys else 1.0
        t = f * rate / 24.0
        if shake:
            pos += Vector((noise.noise(Vector((t, off, 0))), noise.noise(Vector((t, off + 5, 3))),
                           noise.noise(Vector((t, off + 9, 7))))) * shake * mult
        q = look_quat(pos, tgt, roll)
        if rot_shake:
            rx = noise.noise(Vector((t * 1.3, off + 21, 1))) * rot_shake * mult
            ry = noise.noise(Vector((t * 1.3, off + 33, 2))) * rot_shake * mult
            q = q @ Quaternion((1, 0, 0), rx) @ Quaternion((0, 1, 0), ry)
        if prev is not None and q.dot(prev) < 0:
            q.negate()
        prev = q.copy()
        cam.location = pos
        cam.rotation_quaternion = q
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_quaternion", frame=f)
    if lens_keys:
        for f, v in lens_keys:
            cam.data.lens = v
            cam.data.keyframe_insert("lens", frame=f)
    return cam


def rim_light(target, from_offset, energy=800, color=(0.4, 0.85, 1.0), size_deg=40, name="rim"):
    """Spot placed at target+from_offset aimed at target (back/rim light so silhouettes pop)."""
    pos = Vector(target) + Vector(from_offset)
    sp = L.spot(tuple(pos), (0, 0, 0), energy=energy, size_deg=size_deg, blend=0.7, color=color, name=name, radius=0.2)
    sp.rotation_mode = "QUATERNION"
    sp.rotation_quaternion = (Vector(target) - pos).to_track_quat("-Z", "Y")
    return sp


def cam_fill(cam, energy=40, color=(0.6, 0.85, 0.9), size_deg=80):
    return L.cam_light(cam, energy=energy, color=color, size_deg=size_deg)


# ----------------------------------------------------------------------------- world / water

def world_black(color=(0.0, 0.004, 0.006), strength=1.0):
    L.set_world(color=color, strength=strength)


def water(center=(0, 0, 0), size=(40, 40, 30), color=(0.35, 0.65, 0.62), density=0.045, anisotropy=0.65,
          absorption=(0.05, 0.25, 0.25), name="water"):
    o = L.water_volume(center=center, size=size, color=color, density=density, anisotropy=anisotropy,
                       absorption=absorption, name=name)
    return o


def noisy_volume(center, size, color=(0.55, 0.5, 0.42), density=1.0, scale=1.2, name="plume", anisotropy=0.5,
                 contrast=(0.45, 0.75)):
    """Clumpy volume (silt cloud / fog bank): density = ramp(noise) * density, spherical falloff."""
    o = L.prim("cube", loc=center, name=name)
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    m, n, l = L._mat(name + "_m")
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    v = n.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (*color, 1)
    v.inputs["Anisotropy"].default_value = anisotropy
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 4
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = contrast[0]
    ramp.color_ramp.elements[1].position = contrast[1]
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    # spherical falloff from object centre (object coords -1..1)
    ln = n.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    l.new(tc.outputs["Object"], ln.inputs[0])
    fall = n.new("ShaderNodeMapRange")
    fall.inputs["From Min"].default_value = 0.35
    fall.inputs["From Max"].default_value = 1.0
    fall.inputs["To Min"].default_value = 1.0
    fall.inputs["To Max"].default_value = 0.0
    l.new(ln.outputs["Value"], fall.inputs["Value"])
    mul = n.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    l.new(ramp.outputs["Color"], mul.inputs[0])
    l.new(fall.outputs["Result"], mul.inputs[1])
    mul2 = n.new("ShaderNodeMath")
    mul2.operation = "MULTIPLY"
    mul2.inputs[1].default_value = density
    l.new(mul.outputs[0], mul2.inputs[0])
    l.new(mul2.outputs[0], v.inputs["Density"])
    l.new(v.outputs[0], n["Material Output"].inputs["Volume"])
    L.assign(o, m)
    o["density_socket"] = 1
    o.visible_shadow = False
    return o, mul2.inputs[1], nz


# ----------------------------------------------------------------------------- materials

def rock_mat(name="rock", dark=(0.025, 0.028, 0.03), light=(0.2, 0.19, 0.17), scale=1.6, bump=1.0):
    return L.mat_noise_surface(name, dark, light, scale=scale, bump=bump)


def silt_mat(name="silt", c1=(0.09, 0.075, 0.05), c2=(0.24, 0.2, 0.15)):
    return L.mat_noise_surface(name, c1, c2, scale=5, bump=0.25, voronoi=False, rough=0.95)


def emis(name, color, strength=4.0):
    return L.mat_emission(name, color, strength)


def glow_mat(name, color, strength=6.0, falloff=2.0):
    """Soft halo: emission scaled by facing (bright centre, transparent edge). Use on a sphere."""
    m, n, l = L._mat(name)
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
    pw.inputs[1].default_value = falloff
    l.new(inv.outputs[0], pw.inputs[0])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    tr = n.new("ShaderNodeBsdfTransparent")
    mix = n.new("ShaderNodeMixShader")
    l.new(pw.outputs[0], mix.inputs[0])
    l.new(tr.outputs[0], mix.inputs[1])
    l.new(em.outputs[0], mix.inputs[2])
    l.new(mix.outputs[0], n["Material Output"].inputs["Surface"])
    _blended(m)
    return m, em


def _blended(m):
    for k, v in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(m, k, v)
        except Exception:
            pass
    try:
        m.use_transparency_overlap = True
    except Exception:
        pass
    m.use_backface_culling = False


def beam_mat(name, color=TORCH, strength=1.2, along_pow=2.2):
    """Fake volumetric cone: emission * (closeness to apex)^p * (1-facing), additive over transparent."""
    m, n, l = L._mat(name)
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sep.inputs[0])
    pw = n.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = along_pow
    l.new(sep.outputs["Z"], pw.inputs[0])
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.45
    inv = n.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    l.new(lw.outputs["Facing"], inv.inputs[1])
    sq = n.new("ShaderNodeMath")
    sq.operation = "POWER"
    sq.inputs[1].default_value = 3.0
    l.new(inv.outputs[0], sq.inputs[0])
    mul = n.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    l.new(pw.outputs[0], mul.inputs[0])
    l.new(sq.outputs[0], mul.inputs[1])
    mul2 = n.new("ShaderNodeMath")
    mul2.operation = "MULTIPLY"
    mul2.inputs[1].default_value = strength
    l.new(mul.outputs[0], mul2.inputs[0])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    l.new(mul2.outputs[0], em.inputs[1])
    tr = n.new("ShaderNodeBsdfTransparent")
    add = n.new("ShaderNodeAddShader")
    l.new(tr.outputs[0], add.inputs[0])
    l.new(em.outputs[0], add.inputs[1])
    l.new(add.outputs[0], n["Material Output"].inputs["Surface"])
    _blended(m)
    m.use_backface_culling = True
    return m, mul2.inputs[1]


def beam_cone(spot_obj, length=6.0, angle_deg=None, color=TORCH, strength=1.0, name="beam"):
    """Visible torch cone parented to a spot light (points along spot local -Z). Returns (cone, strength_socket)."""
    ang = math.radians(angle_deg) if angle_deg else spot_obj.data.spot_size
    r = math.tan(ang / 2) * length * 0.85
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=48, radius1=r, radius2=0.015, depth=length)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = L.link(bpy.data.objects.new(name, me))
    o.parent = spot_obj
    o.location = (0, 0, -length / 2)
    m, sock = beam_mat(name + "_m", color, strength)
    L.assign(o, m)
    L.smooth(o)
    o.visible_shadow = False
    try:
        o.visible_volume_scatter = False
    except Exception:
        pass
    return o, sock


# ----------------------------------------------------------------------------- geometry builders

def shaft(z_top, z_bot, radius_fn, step=0.5, ring=40, seed=1, rough=0.35, mat=None, name="shaft", cap_bottom=False,
          center_fn=None, disp=(0.5, 0.15)):
    """Vertical, inward-facing rock shaft. radius_fn(z, angle) -> radius. center_fn(z) -> (x,y)."""
    rnd = random.Random(seed)
    off = Vector((rnd.random() * 100, rnd.random() * 100, rnd.random() * 100))
    nseg = max(2, int(abs(z_top - z_bot) / step))
    bm = bmesh.new()
    rings = []
    for i in range(nseg + 1):
        z = z_top + (z_bot - z_top) * i / nseg
        cx, cy = center_fn(z) if center_fn else (0.0, 0.0)
        rv = []
        for j in range(ring):
            a = 2 * math.pi * j / ring
            d = Vector((math.cos(a), math.sin(a), 0))
            r = radius_fn(z, a)
            r *= 1 + rough * noise.noise(Vector((d.x * 1.4, d.y * 1.4, z * 0.25)) + off)
            rv.append(bm.verts.new((cx + d.x * r, cy + d.y * r, z)))
        rings.append(rv)
    for i in range(nseg):
        for j in range(ring):
            a, b = rings[i][j], rings[i][(j + 1) % ring]
            c, d = rings[i + 1][(j + 1) % ring], rings[i + 1][j]
            bm.faces.new((a, b, c, d))
    if cap_bottom:
        bm.faces.new(list(reversed(rings[-1])))
    bm.normal_update()
    # make normals face the axis
    bm.faces.ensure_lookup_table()
    f0 = bm.faces[0]
    cen = f0.calc_center_median()
    cx, cy = center_fn(cen.z) if center_fn else (0.0, 0.0)
    if f0.normal.dot(Vector((cx, cy, cen.z)) - cen) < 0:
        for f in bm.faces:
            f.normal_flip()
    o = L.mesh_from_bm(name, bm)
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 1
    if disp[0]:
        L.add_displace(o, strength=disp[0], scale=1.0, name=name + "_d1")
    if disp[1]:
        L.add_displace(o, strength=disp[1], scale=0.2, name=name + "_d2")
    L.smooth(o)
    L.assign(o, mat or rock_mat(name + "_m"))
    return o


def floor(size=(30, 30), center=(0, 0, 0), mat=None, strength=0.35, levels=6, name="floor", ripples=True):
    o = L.prim("plane", loc=center, size=1, name=name)
    o.scale = (size[0], size[1], 1)
    L.apply_scale(o)
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.subdivision_type = "SIMPLE"
    sub.levels = sub.render_levels = levels
    L.add_displace(o, strength=strength, scale=2.5, name=name + "_d1")
    if ripples:
        L.add_displace(o, strength=0.04, scale=0.25, name=name + "_d2")
    L.smooth(o)
    L.assign(o, mat or silt_mat(name + "_m"))
    return o


def rim_glass_mat(name, color=(0.5, 0.9, 1.0), strength=3.0, power=3.0, base=0.03):
    """Transparent tube/glass with bright fresnel rim (studio macro look)."""
    m, n, l = L._mat(name)
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
    ad.inputs[1].default_value = base
    l.new(pw.outputs[0], ad.inputs[0])
    mu = n.new("ShaderNodeMath")
    mu.operation = "MULTIPLY"
    mu.inputs[1].default_value = strength
    l.new(ad.outputs[0], mu.inputs[0])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    l.new(mu.outputs[0], em.inputs[1])
    tr = n.new("ShaderNodeBsdfTransparent")
    add = n.new("ShaderNodeAddShader")
    l.new(tr.outputs[0], add.inputs[0])
    l.new(em.outputs[0], add.inputs[1])
    l.new(add.outputs[0], n["Material Output"].inputs["Surface"])
    _blended(m)
    return m


def rocks(points, count=12, size=(0.3, 1.2), seed=5, mat=None, sink=0.3, flat=(0.5, 0.9)):
    rnd = random.Random(seed)
    m = mat or rock_mat("boulder_m", (0.03, 0.03, 0.03), (0.22, 0.2, 0.18), scale=2.5)
    out = []
    for i in range(count):
        c = Vector(points[i % len(points)]) if len(points) >= count else Vector(rnd.choice(points))
        s = rnd.uniform(*size)
        o = L.prim("ico", loc=(c.x, c.y, c.z + s * (1 - sink) * 0.5), subdivisions=3, radius=s)
        o.scale = (rnd.uniform(0.8, 1.3), rnd.uniform(0.7, 1.2), rnd.uniform(*flat))
        o.rotation_euler = (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 6.28))
        L.add_displace(o, strength=s * 0.35, scale=s * 0.8, name=f"rk{i}_{seed}")
        L.smooth(o)
        L.assign(o, m)
        out.append(o)
    return out


def cloud(center, size, count=800, radius=0.01, color=(0.85, 0.8, 0.68), emit=0.05, shape="box", seed=7,
          name="silt", mat=None):
    """Particle mesh (tetrahedra) with object origin at center (so scale keys expand from the centre)."""
    rnd = random.Random(seed)
    radius = min(radius, 0.008)
    bm = bmesh.new()
    for i in range(count):
        if shape == "torus":  # size = (major_radius, minor_radius, _)
            a = rnd.uniform(0, 2 * math.pi)
            b = rnd.uniform(0, 2 * math.pi)
            rr = size[1] * math.sqrt(rnd.random())
            R = size[0] + rr * math.cos(b)
            c = Vector((math.cos(a) * R, math.sin(a) * R, rr * math.sin(b)))
        elif shape == "sphere":
            while True:
                v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
                if v.length <= 1:
                    break
            c = Vector((v.x * size[0] / 2, v.y * size[1] / 2, v.z * size[2] / 2))
        elif shape == "cylx":  # cylinder along X
            a = rnd.uniform(0, 2 * math.pi)
            r = math.sqrt(rnd.random())
            c = Vector((rnd.uniform(-0.5, 0.5) * size[0], math.cos(a) * r * size[1] / 2, math.sin(a) * r * size[2] / 2))
        else:
            c = Vector((rnd.uniform(-0.5, 0.5) * size[0], rnd.uniform(-0.5, 0.5) * size[1], rnd.uniform(-0.5, 0.5) * size[2]))
        r = radius * rnd.uniform(0.5, 1.6)
        vs = [bm.verts.new(c + Vector(v) * r) for v in ((1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1))]
        for f in ((0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)):
            bm.faces.new([vs[k] for k in f])
    o = L.mesh_from_bm(name, bm)
    o.location = center
    L.assign(o, mat or L.mat_principled(name + "_m", color, rough=1, emit=color, emit_strength=emit))
    o.visible_shadow = False
    return o


def drift(o, n, vel=(0, 0, 0.02), rot=0.0):
    base = Vector(o.location)
    o.keyframe_insert("location", frame=1)
    o.location = base + Vector(vel) * n / 24
    o.keyframe_insert("location", frame=n)
    if rot:
        o.rotation_euler = (0, 0, 0)
        o.keyframe_insert("rotation_euler", frame=1)
        o.rotation_euler = (0, 0, rot * n / 24)
        o.keyframe_insert("rotation_euler", frame=n)
    L.linear_fcurves(o)
    return o


def line(points, thickness=0.008, color=(0.92, 0.9, 0.82), emit=0.6, name="line", mat=None, kind="POLY"):
    return L.guideline(points, thickness=thickness, name=name,
                       mat=mat or L.mat_principled(name + "_m", color, rough=0.4, emit=color, emit_strength=emit))


def curve(points, thickness=0.02, mat=None, name="crv", smooth_pts=False, resolution=12):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = thickness
    cu.bevel_resolution = 3
    cu.resolution_u = resolution
    if smooth_pts:
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(points) - 1)
        for i, p in enumerate(points):
            bp = sp.bezier_points[i]
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = "AUTO"
    else:
        sp = cu.splines.new("POLY")
        sp.points.add(len(points) - 1)
        for i, p in enumerate(points):
            sp.points[i].co = (*p, 1)
    o = L.link(bpy.data.objects.new(name, cu))
    if mat:
        o.data.materials.append(mat)
    return o


def grow_curve(o, keys):
    """Animate bevel_factor_end: keys [(frame, 0..1)]."""
    cu = o.data
    cu.bevel_factor_mapping_end = "SPLINE"
    for f, v in keys:
        cu.bevel_factor_end = v
        cu.keyframe_insert("bevel_factor_end", frame=f)


def helix(center, axis, radius, turns, length, pts_per_turn=16, phase=0.0, wobble=0.0, seed=1):
    axis = Vector(axis).normalized()
    side = axis.orthogonal().normalized()
    up = axis.cross(side)
    rnd = random.Random(seed)
    out = []
    N = int(turns * pts_per_turn)
    for i in range(N + 1):
        t = i / N
        a = phase + 2 * math.pi * turns * t
        r = radius * (1 + wobble * (rnd.random() - 0.5))
        p = Vector(center) + axis * (t - 0.5) * length + (side * math.cos(a) + up * math.sin(a)) * r
        out.append(tuple(p))
    return out


def text(body, loc, size=0.3, color=(1, 1, 1), strength=3.0, font=FONT_ANTON, rot=(math.pi / 2, 0, 0), align="CENTER",
         name="txt", extrude=0.0, mat=None):
    o = L.text3d(body, loc=loc, rot=rot, size=size, extrude=extrude, mat=mat or emis(name + "_m", color, strength),
                 font=font if font and os.path.exists(font) else None, align=align, name=name)
    o.data.align_y = "CENTER"
    return o


def glow_dot(loc, color=CYAN, r=0.07, halo=3.5, strength=10, light=0.0, name="dot"):
    core = L.prim("sphere", loc=loc, segments=16, ring_count=8, radius=r, name=name)
    L.assign(core, emis(name + "_core", tuple(min(1, c * 0.6 + 0.45) for c in color), strength))
    L.smooth(core)
    h = L.prim("sphere", loc=(0, 0, 0), segments=24, ring_count=12, radius=r * halo, name=name + "_halo")
    hm, hem = glow_mat(name + "_halo_m", color, strength * 0.35, falloff=2.5)
    L.assign(h, hm)
    L.smooth(h)
    h.parent = core
    core["halo_emit"] = 1
    if light:
        pl = L.point((0, 0, 0), energy=light, color=color, radius=r, name=name + "_pl")
        pl.parent = core
    return core, h, hem


# ----------------------------------------------------------------------------- characters / props

def diver(name="diver", fins=YELLOW, suit=(0.03, 0.03, 0.035), rebreather=True, light_energy=1500, beam_deg=22,
          tanks="single", beam=True, beam_len=7.0, beam_strength=0.6, scale=1.0, light_color=TORCH):
    """char_diver + rebreather box/counterlungs + visible beam cone. Root faces +Y (head), back = +Z."""
    p = L.char_diver(name=name, suit=suit, accent=fins, tanks=tanks, light_energy=light_energy, scale=1.0)
    root = p["root"]
    dark = L.mat_principled(name + "_rb", (0.07, 0.075, 0.08), rough=0.45)
    if rebreather:
        box = L.prim("cube", loc=(0, -0.05, 0.24), name=name + "_rebreather")
        box.scale = (0.17, 0.32, 0.09)
        L.assign(box, dark)
        L.bevel(box, 0.03)
        box.parent = root
        for sx in (-1, 1):
            cl = L.prim("sphere", loc=(sx * 0.16, 0.28, 0.12), segments=12, ring_count=8, name=f"{name}_lung{sx}")
            cl.scale = (0.07, 0.12, 0.05)
            L.assign(cl, dark)
            L.smooth(cl)
            cl.parent = root
        hose = L.prim("torus", loc=(0, 0.5, 0.05), rot=(0, math.pi / 2, 0), major_radius=0.14, minor_radius=0.018,
                      name=name + "_hose")
        L.assign(hose, dark)
        hose.parent = root
    # bigger, wider fins so they read in silhouette
    for tag in ("L", "R"):
        fin = p.get(f"fin{tag}")
        if fin:
            fin.scale = (0.13, 0.26, 0.012)
    t = p.get("torch")
    if t:
        t.data.spot_size = math.radians(beam_deg)
        t.data.spot_blend = 0.45
        t.data.color = light_color
        t.data.shadow_soft_size = 0.02
        if beam:
            cone, sock = beam_cone(t, length=beam_len, color=light_color, strength=beam_strength, name=name + "_beam")
            p["beam"] = cone
            p["beam_sock"] = sock
    root.scale = (scale,) * 3
    return p


def pose_upright_kneel(p, lean=0.35):
    """Pose a char_diver rig kneeling upright: torso up, thighs down, shins back along the floor."""
    root = p["root"]
    root.rotation_euler = (math.pi / 2 - lean, 0, root.rotation_euler.z)
    for tag in ("L", "R"):
        p[f"hip{tag}"].rotation_euler = (-lean * 0.9, 0, 0)
        p[f"knee{tag}"].rotation_euler = (-math.pi / 2 + 0.2, 0, 0)
        p[f"shoulder{tag}"].rotation_euler = (-1.0, 0, (-0.25 if tag == "L" else 0.25))


def lost_shape(loc=(0, 0, 0), rot_z=0.0, name="lost", sink=0.55, fins_visible=True, color=(0.12, 0.12, 0.13)):
    """Abstract, respectful 'lost diver' marker: a half-buried single tank, two fin blades and a low silt mound.
    No body form, no face."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    metal = L.mat_principled(name + "_tank", (0.22, 0.23, 0.24), rough=0.55, metal=0.6)
    dark = L.mat_principled(name + "_dark", color, rough=0.8)
    mound_m = silt_mat(name + "_mound", (0.1, 0.085, 0.06), (0.22, 0.19, 0.14))
    tank = L.prim("cyl", loc=(0.05, 0.1, 0.1 - sink * 0.1), rot=(math.pi / 2, 0.15, 0), vertices=20, radius=0.1,
                  depth=0.75, name=name + "_tank")
    L.assign(tank, metal)
    L.smooth(tank)
    tank.parent = root
    valve = L.prim("cyl", loc=(0.05, 0.5, 0.1 - sink * 0.1), rot=(math.pi / 2, 0, 0), vertices=10, radius=0.03,
                   depth=0.1, name=name + "_valve")
    L.assign(valve, metal)
    valve.parent = root
    mound = L.prim("sphere", loc=(-0.12, -0.05, -0.05), segments=24, ring_count=12, name=name + "_mound")
    mound.scale = (0.26, 0.7, 0.09)
    L.add_displace(mound, strength=0.05, scale=0.2, name=name + "_md")
    L.assign(mound, mound_m)
    L.smooth(mound)
    mound.parent = root
    fins = []
    if fins_visible:
        for k, (x, rz, ry) in enumerate(((-0.22, 0.25, 0.5), (-0.02, -0.15, 0.9))):
            f = L.prim("cube", loc=(x, -0.95, 0.08), rot=(0.35, ry, rz), name=f"{name}_fin{k}")
            f.scale = (0.11, 0.26, 0.01)
            L.assign(f, dark)
            L.bevel(f, 0.008)
            f.parent = root
            fins.append(f)
    return root, {"tank": tank, "mound": mound, "fins": fins}


# ----------------------------------------------------------------------------- environment kits

def chamber_floor(center=(0, 0, 0), size=40, seed=3, boulder_count=14, back_wall=True, wall_dist=9.0,
                  rock=None, rmin=5.0):
    """Bottom of a vast dark chamber: silt floor, scattered boulders, optional far curved back wall."""
    cx, cy, cz = center
    fl = floor(size=(size, size), center=center, strength=0.45, name="chamber_floor")
    rnd = random.Random(seed)
    pts = []
    for i in range(boulder_count):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(rmin, max(rmin + 1, size * 0.35))
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r, cz))
    bl = rocks(pts, count=boulder_count, size=(0.4, 1.6), seed=seed)
    wall = None
    if back_wall:
        wall = shaft(cz + 14, cz - 1.5, lambda z, a: wall_dist + 2.5 * math.sin(a * 3 + 1) + 0.15 * (z - cz),
                     step=1.0, ring=48, seed=seed, rough=0.3, mat=rock if rock else None, name="chamber_wall",
                     center_fn=lambda z: (cx, cy), disp=(0.8, 0.25))
    return {"floor": fl, "boulders": bl, "wall": wall}


def sky_world(top=(0.25, 0.4, 0.6), horizon=(0.9, 0.7, 0.5), ground=(0.08, 0.06, 0.05), sun_dir=None,
              sun_color=(1.0, 0.7, 0.4), sun_glow=2.0, strength=1.0, glow_pow=40.0):
    """Gradient sky with soft sun glow. sun_dir points FROM scene TOWARD sun."""
    w = bpy.context.scene.world
    nt = w.node_tree
    n, l = nt.nodes, nt.links
    for nd in list(n):
        if nd.type != "OUTPUT_WORLD":
            n.remove(nd)
    out = [nd for nd in n if nd.type == "OUTPUT_WORLD"][0]
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    dirn = n.new("ShaderNodeVectorMath")
    dirn.operation = "NORMALIZE"
    l.new(tc.outputs["Generated"], dirn.inputs[0])
    l.new(dirn.outputs[0], sep.inputs[0])
    ramp = n.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.46
    cr.elements[0].color = (*ground, 1)
    cr.elements[1].position = 0.7
    cr.elements[1].color = (*top, 1)
    e = cr.elements.new(0.505)
    e.color = (*horizon, 1)
    e2 = cr.elements.new(0.54)
    e2.color = tuple(lerp(h, t, 0.35) for h, t in zip(horizon, top)) + (1,)
    # Generated z in world is direction z mapped? use (z+1)/2 to be safe
    mp = n.new("ShaderNodeMapRange")
    mp.inputs["From Min"].default_value = -1
    mp.inputs["From Max"].default_value = 1
    l.new(sep.outputs["Z"], mp.inputs["Value"])
    l.new(mp.outputs["Result"], ramp.inputs["Fac"])
    bg = n.new("ShaderNodeBackground")
    bg.inputs[1].default_value = strength
    if sun_dir:
        nrm = n.new("ShaderNodeVectorMath")
        nrm.operation = "NORMALIZE"
        l.new(tc.outputs["Generated"], nrm.inputs[0])
        dot = n.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        dot.inputs[1].default_value = tuple(Vector(sun_dir).normalized())
        l.new(nrm.outputs[0], dot.inputs[0])
        cl = n.new("ShaderNodeMath")
        cl.operation = "MAXIMUM"
        cl.inputs[1].default_value = 0
        l.new(dot.outputs["Value"], cl.inputs[0])
        pw = n.new("ShaderNodeMath")
        pw.operation = "POWER"
        pw.inputs[1].default_value = glow_pow
        l.new(cl.outputs[0], pw.inputs[0])
        pw2 = n.new("ShaderNodeMath")
        pw2.operation = "POWER"
        pw2.inputs[1].default_value = 4.0
        l.new(cl.outputs[0], pw2.inputs[0])
        ad = n.new("ShaderNodeMath")
        ad.operation = "MULTIPLY_ADD"
        ad.inputs[1].default_value = 0.25
        l.new(pw2.outputs[0], ad.inputs[0])
        l.new(pw.outputs[0], ad.inputs[2])
        sc = n.new("ShaderNodeMath")
        sc.operation = "MULTIPLY"
        sc.inputs[1].default_value = sun_glow
        l.new(ad.outputs[0], sc.inputs[0])
        mixc = n.new("ShaderNodeMix")
        mixc.data_type = "RGBA"
        mixc.blend_type = "ADD"
        mixc.inputs["B"].default_value = (*sun_color, 1)
        l.new(sc.outputs[0], mixc.inputs["Factor"])
        l.new(ramp.outputs["Color"], mixc.inputs["A"])
        l.new(mixc.outputs["Result"], bg.inputs[0])
    else:
        l.new(ramp.outputs["Color"], bg.inputs[0])
    l.new(bg.outputs[0], out.inputs["Surface"])
    return bg


def sun_from(direction_to_sun, energy=3.0, color=(1, 0.8, 0.6), angle=1.5, name="sun"):
    s = L.sun(energy=energy, color=color, angle=angle, name=name)
    s.rotation_mode = "QUATERNION"
    s.rotation_quaternion = (-Vector(direction_to_sun)).to_track_quat("-Z", "Y")
    return s


def sun_dir(elev_deg, az_deg):
    e, a = math.radians(elev_deg), math.radians(az_deg)
    return Vector((math.cos(e) * math.sin(a), math.cos(e) * math.cos(a), math.sin(e)))


def crater(R=9.0, depth=14.0, outer=70.0, seed=2, ground_mat=None, wall_mat=None, pool_mat=None, ang_seg=72,
           name="crater"):
    """Desert sinkhole: annular ground falling into a steep rocky pit with a still pool at the bottom.
    Returns dict(ground, pool, rim_r(a), pool_z)."""
    rnd = random.Random(seed)
    off = rnd.random() * 50

    def rim(a):
        return R * (1 + 0.16 * noise.noise(Vector((math.cos(a) * 1.3 + off, math.sin(a) * 1.3, 0.5))) +
                    0.06 * math.sin(3 * a + 1))
    # profile: (radius factor relative to rim (None=absolute), z)
    prof = [(outer, 0.15), (outer * 0.6, 0.1), (outer * 0.35, 0.0), (R * 2.2, 0.05), (R * 1.5, 0.0), ("rim", 1.12, 0.35),
            ("rim", 1.03, 0.25), ("rim", 1.0, 0.0), ("rim", 0.98, -0.8 * depth / 14), ("rim", 0.95, -2.5 * depth / 14),
            ("rim", 0.9, -5.0 * depth / 14), ("rim", 0.86, -8.0 * depth / 14), ("rim", 0.8, -11.0 * depth / 14),
            ("rim", 0.74, -depth + 0.6), ("rim", 0.62, -depth - 0.5)]
    bm = bmesh.new()
    rings = []
    for k, pr in enumerate(prof):
        rv = []
        for j in range(ang_seg):
            a = 2 * math.pi * j / ang_seg
            if pr[0] == "rim":
                r = rim(a) * pr[1]
                z = pr[2]
            else:
                r, z = pr
            rv.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, z)))
        rings.append(rv)
    wall_start = 7
    for i in range(len(rings) - 1):
        for j in range(ang_seg):
            f = bm.faces.new((rings[i][j], rings[i][(j + 1) % ang_seg], rings[i + 1][(j + 1) % ang_seg], rings[i + 1][j]))
            f.material_index = 0 if i < wall_start - 1 else 1
    bm.normal_update()
    bm.faces.ensure_lookup_table()
    f0 = bm.faces[0]
    if f0.normal.z < 0:
        for f in bm.faces:
            f.normal_flip()
    o = L.mesh_from_bm(name, bm)
    o.data.materials.append(ground_mat or L.mat_noise_surface("desert_sand", (0.32, 0.2, 0.12), (0.62, 0.45, 0.3),
                                                                scale=0.8, bump=0.3, voronoi=False))
    o.data.materials.append(wall_mat or L.mat_noise_surface("sink_rock", (0.12, 0.1, 0.085), (0.45, 0.38, 0.3),
                                                              scale=0.6, bump=1.0))
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 2
    L.add_displace(o, strength=0.9, scale=2.2, name=name + "_d1")
    L.add_displace(o, strength=0.25, scale=0.35, name=name + "_d2")
    L.smooth(o)
    pool_z = -depth + 0.9
    pool = L.prim("cyl", loc=(0, 0, pool_z - 0.05), vertices=64, radius=R * 0.78, depth=0.1,
                  name="pool")
    L.assign(pool, pool_mat or L.mat_principled("pool_m", (0.01, 0.07, 0.065), rough=0.04))
    return {"ground": o, "pool": pool, "rim": rim, "pool_z": pool_z}


def bushes(count=60, rmin=12, rmax=55, seed=4, z=0.0, color=(0.12, 0.11, 0.06), size=(0.3, 0.9)):
    rnd = random.Random(seed)
    m = L.mat_noise_surface("bush_m", tuple(c * 0.5 for c in color), color, scale=8, bump=0.6, voronoi=False)
    out = []
    for i in range(count):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(rmin, rmax)
        s = rnd.uniform(*size)
        o = L.prim("ico", loc=(math.cos(a) * r, math.sin(a) * r, z + s * 0.25), subdivisions=2, radius=s)
        o.scale = (1, rnd.uniform(0.7, 1.2), 0.6)
        L.add_displace(o, strength=s * 0.5, scale=0.25, name=f"bush{i}")
        L.assign(o, m)
        out.append(o)
    return out


# ----------------------------------------------------------------------------- 2.5D cross-section diagram

def xsection(poly, depth_to_z, x_scale=1.0, slab=(-0.4, 0.4), extent=(-4, 4, -6, 4), outline_color=CYAN,
             water_top=(0.02, 0.16, 0.18), water_bot=(0.0, 0.01, 0.015), rock_mat_=None, outline_strength=4.0,
             snow=None, name="xs", water_poly=None, outer_poly=None):
    """Rock slab (XZ plane, facing -Y) with a cave void cut from a polygon [(x, depth_m), ...] (clockwise or ccw).
    Returns dict(rock, water, outline, P) where P(x, depth) -> world Vector on the front face."""
    def P(x, d, y=None):
        return Vector((x * x_scale, slab[0] - 0.01 if y is None else y, depth_to_z(d)))
    pts2 = [(x * x_scale, depth_to_z(d)) for x, d in poly]
    # rock block
    x0, x1, z0, z1 = extent
    if outer_poly:  # prism from an (x, z) outline, e.g. a mountain silhouette
        bm = bmesh.new()
        fr = [bm.verts.new((x, slab[0], z)) for x, z in outer_poly]
        bk = [bm.verts.new((x, slab[1], z)) for x, z in outer_poly]
        bm.faces.new(fr)
        bm.faces.new(list(reversed(bk)))
        N0 = len(outer_poly)
        for i in range(N0):
            bm.faces.new((fr[i], fr[(i + 1) % N0], bk[(i + 1) % N0], bk[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        rock = L.mesh_from_bm(name + "_rock", bm)
    else:
        rock = L.prim("cube", loc=((x0 + x1) / 2, (slab[0] + slab[1]) / 2, (z0 + z1) / 2), name=name + "_rock")
        rock.scale = ((x1 - x0) / 2, (slab[1] - slab[0]) / 2, (z1 - z0) / 2)
        L.apply_scale(rock)
    L.assign(rock, rock_mat_ or L.mat_noise_surface(name + "_rockm", (0.03, 0.035, 0.04), (0.11, 0.12, 0.13), scale=1.2,
                                                     bump=0.25, rough=0.9))
    # void prism
    bm = bmesh.new()
    yb, yf = slab[1] - 0.12, slab[0] - 0.5
    back = [bm.verts.new((x, yb, z)) for x, z in pts2]
    front = [bm.verts.new((x, yf, z)) for x, z in pts2]
    bm.faces.new(back)
    bm.faces.new(list(reversed(front)))
    N = len(pts2)
    for i in range(N):
        bm.faces.new((back[i], back[(i + 1) % N], front[(i + 1) % N], front[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    cutter = L.mesh_from_bm(name + "_cut", bm)
    bo = rock.modifiers.new("void", "BOOLEAN")
    bo.object = cutter
    bo.operation = "DIFFERENCE"
    try:
        bo.solver = "EXACT"
    except Exception:
        pass
    cutter.hide_render = True
    cutter.hide_viewport = True
    # water back plate
    bm = bmesh.new()
    wpts = [(x * x_scale, depth_to_z(d)) for x, d in water_poly] if water_poly else pts2
    vs = [bm.verts.new((x, yb - 0.005, z)) for x, z in wpts]
    bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    wat = L.mesh_from_bm(name + "_water", bm)
    m, n, l = L._mat(name + "_waterm")
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sep.inputs[0])
    zs = [z for _, z in wpts]
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = min(zs)
    mr.inputs["From Max"].default_value = max(zs)
    l.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*water_bot, 1)
    ramp.color_ramp.elements[1].color = (*water_top, 1)
    ramp.color_ramp.elements[1].position = 0.92
    l.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.5
    l.new(ramp.outputs["Color"], mix.inputs["A"])
    l.new(nz.outputs["Color"], mix.inputs["B"])
    em = n.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.6
    l.new(mix.outputs["Result"], em.inputs[0])
    l.new(em.outputs[0], n["Material Output"].inputs["Surface"])
    L.assign(wat, m)
    # outline
    om = emis(name + "_outm", outline_color, outline_strength)
    outline = curve([(x, slab[0] - 0.02, z) for x, z in pts2] + [(pts2[0][0], slab[0] - 0.02, pts2[0][1])],
                    thickness=0.018, mat=om, name=name + "_outline")
    return {"rock": rock, "water": wat, "outline": outline, "P": P, "outline_mat": om}


def fin_blade(loc, rot, length=0.55, w0=0.09, w1=0.2, mat=None, name="fin"):
    """Tapered fin blade (foot pocket narrow, blade wide) as a thin solid."""
    bm = bmesh.new()
    pts = [(-w0, 0), (w0, 0), (w1, length), (0.02, length * 0.92), (-0.02, length * 0.92), (-w1, length)]
    vs = [bm.verts.new((x, y, 0)) for x, y in pts]
    bm.faces.new(vs)
    o = L.mesh_from_bm(name, bm)
    so = o.modifiers.new("solid", "SOLIDIFY")
    so.thickness = 0.012
    o.location = loc
    o.rotation_euler = rot
    if mat:
        L.assign(o, mat)
    return o


def dotted_path(points, spacing=0.12, r=0.025, color=(1, 1, 1), strength=3.0, name="dots"):
    """Return list of small emissive spheres evenly spaced along a polyline (no animation)."""
    m = emis(name + "_m", color, strength)
    pts = [Vector(p) for p in points]
    out = []
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        seg = (b - a).length
        t = acc
        while t < seg:
            p = a.lerp(b, t / seg)
            o = L.prim("sphere", loc=p, segments=8, ring_count=6, radius=r, name=name)
            L.assign(o, m)
            out.append(o)
            t += spacing
        acc = t - seg
    return out


def pop_in(objs, frames, dur=4, overshoot=1.35):
    """Scale-pop each object at its frame."""
    for o, f in zip(objs, frames):
        s = tuple(o.scale)
        o.scale = (0, 0, 0)
        o.keyframe_insert("scale", frame=max(1, f - 1))
        o.scale = tuple(v * overshoot for v in s)
        o.keyframe_insert("scale", frame=f + dur // 2)
        o.scale = s
        o.keyframe_insert("scale", frame=f + dur)


def along(points, t):
    """Point at fraction t (0..1, by arc length) of a polyline."""
    pts = [Vector(p) for p in points]
    lens = [(b - a).length for a, b in zip(pts, pts[1:])]
    tot = sum(lens)
    d = max(0.0, min(1.0, t)) * tot
    for (a, b), ln in zip(zip(pts, pts[1:]), lens):
        if d <= ln:
            return a.lerp(b, d / max(1e-9, ln))
        d -= ln
    return pts[-1]


def move_along(o, points, keys, step=2, n=None):
    """keys [(frame, t)] -> keyframe location of o along polyline."""
    f0, f1 = keys[0][0], keys[-1][0]
    for f in list(range(f0, f1 + 1, step)) + [f1]:
        t = piecewise(keys, f)
        o.location = along(points, t)
        o.keyframe_insert("location", frame=f)


# ----------------------------------------------------------------------------- ice (Plura)

def ice_sheet(z=0.0, size=40, thickness=0.5, hole=None, seed=3, name="ice"):
    """Ice slab with optional polygon hole [(x,y),...] cut by boolean. Underside reads milky-white/blue from below."""
    o = L.prim("cube", loc=(0, 0, z + thickness / 2), name=name)
    o.scale = (size / 2, size / 2, thickness / 2)
    L.apply_scale(o)
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.subdivision_type = "SIMPLE"
    sub.levels = sub.render_levels = 4
    L.add_displace(o, strength=0.08, scale=0.8, name=name + "_d")
    m, n, l = L._mat(name + "_m")
    p = n["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.6, 0.75, 0.8, 1)
    p.inputs["Roughness"].default_value = 0.35
    p.inputs["Emission Color"].default_value = (0.35, 0.6, 0.75, 1)
    tc = n.new("ShaderNodeTexCoord")
    vr = n.new("ShaderNodeTexVoronoi")
    vr.inputs["Scale"].default_value = 1.6
    l.new(tc.outputs["Object"], vr.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.14, 0.14, 0.14, 1)
    ramp.color_ramp.elements[1].color = (0.06, 0.06, 0.06, 1)
    ramp.color_ramp.elements[1].position = 0.6
    l.new(vr.outputs["Distance"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Emission Strength"])
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.4
    l.new(vr.outputs["Distance"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    L.assign(o, m)
    cutter = None
    if hole:
        bm = bmesh.new()
        bot = [bm.verts.new((x, y, z - 1)) for x, y in hole]
        top = [bm.verts.new((x, y, z + thickness + 1)) for x, y in hole]
        bm.faces.new(bot)
        bm.faces.new(list(reversed(top)))
        N = len(hole)
        for i in range(N):
            bm.faces.new((bot[i], bot[(i + 1) % N], top[(i + 1) % N], top[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        cutter = L.mesh_from_bm(name + "_holecut", bm)
        bo = o.modifiers.new("hole", "BOOLEAN")
        bo.object = cutter
        bo.operation = "DIFFERENCE"
        cutter.hide_render = True
        cutter.hide_viewport = True
    return o, m, cutter


def tunnel(path_pts, radius=2.0, seed=1, rough=0.5, mat=None, name="tunnel", flatten=0.0, ring=24, seg=24):
    """Horizontal-ish cave tunnel (wraps studio_lib.cave_tunnel) with optional vertical squash (flatten 0..0.7)."""
    o, samples = L.cave_tunnel(path_pts, radius=radius, seg=seg, ring=ring, seed=seed, rough=rough,
                               mat=mat or rock_mat(name + "_m"), name=name)
    if flatten:
        # squash around each sample's z: approximate via object-level scale is wrong for long paths, so edit verts
        me = o.data
        import mathutils
        kd = mathutils.kdtree.KDTree(len(samples))
        for i, s in enumerate(samples):
            kd.insert(s, i)
        kd.balance()
        for v in me.vertices:
            co, idx, dist = kd.find(v.co)
            v.co.z = co.z + (v.co.z - co.z) * (1 - flatten)
    return o, samples


def offset_band(center_pts, half_w):
    """Polygon (x, z) around a 2D polyline [(x, z)] with half width (for tunnels in a section diagram)."""
    P = [Vector((x, z)) for x, z in center_pts]
    left, right = [], []
    for i, p in enumerate(P):
        a = P[max(0, i - 1)]
        b = P[min(len(P) - 1, i + 1)]
        t = (b - a).normalized()
        nrm = Vector((-t.y, t.x))
        w = half_w[i] if isinstance(half_w, (list, tuple)) else half_w
        left.append(tuple(p + nrm * w))
        right.append(tuple(p - nrm * w))
    return left + list(reversed(right))


# ============================================================================= CAVE-02 (Tham Luang) / CAVE-04 (Nutty Putty)
# Added by the CAVE-02/04 director. New functions only; nothing above was changed.

def passage(length=30.0, half_w=1.6, half_h=1.4, zc=0.0, y0=0.0, step=0.5, ring=32, seed=1, rough=0.12,
            w_fn=None, h_fn=None, x_fn=None, z_fn=None, mat=None, name="passage", disp=(0.25, 0.08), floor_flat=0.3):
    """Straight-ish horizontal tunnel along +Y with an elliptical, inward-facing section (no Catmull/up-vector issues).
    w_fn(y)/h_fn(y) override half width/height, x_fn(y)/z_fn(y) shift the centre; floor_flat squashes the lower half.
    Returns (obj, info) with info = dict(cx(y), cz(y), hw(y), hh(y), floor(y), ceil(y))."""
    rnd = random.Random(seed)
    off = Vector((rnd.random() * 100, rnd.random() * 100, rnd.random() * 100))
    W = w_fn or (lambda y: half_w)
    H = h_fn or (lambda y: half_h)
    X = x_fn or (lambda y: 0.0)
    Z = z_fn or (lambda y: zc)
    nseg = max(2, int(length / step))
    bm = bmesh.new()
    rings = []
    for i in range(nseg + 1):
        y = y0 + length * i / nseg
        rv = []
        for j in range(ring):
            a = 2 * math.pi * j / ring
            ca, sa = math.cos(a), math.sin(a)
            k = 1 + rough * noise.noise(Vector((ca * 1.3, sa * 1.3, y * 0.35)) + off)
            hz = H(y) * (1 - floor_flat if sa < 0 else 1.0)
            rv.append(bm.verts.new((X(y) + W(y) * ca * k, y, Z(y) + hz * sa * k)))
        rings.append(rv)
    for i in range(nseg):
        for j in range(ring):
            bm.faces.new((rings[i][j], rings[i][(j + 1) % ring], rings[i + 1][(j + 1) % ring], rings[i + 1][j]))
    bm.normal_update()
    bm.faces.ensure_lookup_table()
    f0 = bm.faces[0]
    cen = f0.calc_center_median()
    if f0.normal.dot(Vector((X(cen.y), cen.y, Z(cen.y))) - cen) < 0:
        for f in bm.faces:
            f.normal_flip()
    o = L.mesh_from_bm(name, bm)
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 1
    if disp[0]:
        L.add_displace(o, strength=disp[0], scale=0.9, name=name + "_d1")
    if disp[1]:
        L.add_displace(o, strength=disp[1], scale=0.2, name=name + "_d2")
    L.smooth(o)
    L.assign(o, mat or rock_mat(name + "_m"))
    info = {"cx": X, "cz": Z, "hw": W, "hh": H,
            "floor": lambda y: Z(y) - H(y) * (1 - floor_flat), "ceil": lambda y: Z(y) + H(y)}
    return o, info


def water_surface(size=(6, 40), center=(0, 0, 0), color=(0.004, 0.012, 0.014), rough=0.05, wave_scale=1.6, bump=0.22,
                  n=100, flow=(0.0, 0.25), glow_at=None, glow_color=(0.55, 1.0, 0.85), glow_radius=1.2,
                  name="watersurf", subdiv=0):
    """Glassy water plane: dark glossy base, animated noise bump (ripples drift with `flow` m/s).
    glow_at=(x, y) adds a radial emission patch (torch under the surface); returns (obj, glow_strength_socket)."""
    o = L.prim("plane", loc=center, size=1, name=name)
    o.scale = (size[0], size[1], 1)
    L.apply_scale(o)
    if subdiv:
        s = o.modifiers.new("sub", "SUBSURF")
        s.subdivision_type = "SIMPLE"
        s.levels = s.render_levels = subdiv
    m, nd, l = L._mat(name + "_m")
    p = nd["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    try:
        p.inputs["Specular IOR Level"].default_value = 0.8
    except Exception:
        pass
    tc = nd.new("ShaderNodeTexCoord")
    mp = nd.new("ShaderNodeMapping")
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = nd.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = wave_scale
    nz.inputs["Detail"].default_value = 3
    l.new(mp.outputs["Vector"], nz.inputs["Vector"])
    bp = nd.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    l.new(nz.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    loc_in = mp.inputs["Location"]
    loc_in.default_value = (0, 0, 0)
    loc_in.keyframe_insert("default_value", frame=1)
    loc_in.default_value = (-flow[0] * n / 24, -flow[1] * n / 24, 0.15 * n / 24)
    loc_in.keyframe_insert("default_value", frame=n)
    for fc in L._fcurves(m.node_tree.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    sock = None
    if glow_at is not None:
        gx, gy = glow_at[0] - center[0], glow_at[1] - center[1]
        vm = nd.new("ShaderNodeVectorMath")
        vm.operation = "DISTANCE"
        vm.inputs[1].default_value = (gx, gy, 0)
        l.new(tc.outputs["Object"], vm.inputs[0])
        mr = nd.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.0
        mr.inputs["From Max"].default_value = glow_radius
        mr.inputs["To Min"].default_value = 1.0
        mr.inputs["To Max"].default_value = 0.0
        l.new(vm.outputs["Value"], mr.inputs["Value"])
        pw = nd.new("ShaderNodeMath")
        pw.operation = "POWER"
        pw.inputs[1].default_value = 2.0
        l.new(mr.outputs["Result"], pw.inputs[0])
        mul = nd.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = 0.0
        l.new(pw.outputs[0], mul.inputs[0])
        p.inputs["Emission Color"].default_value = (*glow_color, 1)
        l.new(mul.outputs[0], p.inputs["Emission Strength"])
        sock = mul.inputs[1]
    L.assign(o, m)
    return o, sock


def drip_rings(points, n, period=34, seed=1, color=(0.55, 0.85, 0.9), strength=0.5, rmax=0.45, name="ring"):
    """Expanding thin rings on a water surface (drips). points = [(x, y, z)]."""
    rnd = random.Random(seed)
    m = emis(name + "_m", color, strength)
    out = []
    for i, p in enumerate(points):
        o = L.prim("torus", loc=p, major_radius=1.0, minor_radius=0.006, major_segments=40, minor_segments=4,
                   name=f"{name}{i}")
        L.assign(o, m)
        ph = rnd.randint(0, period)
        f = 1 - ph
        while f < n + period:
            for ff, s in ((f, 0.02), (f + period - 1, rmax), (f + period, 0.0)):
                if ff >= -period:
                    o.scale = (s, s, 1.0 if s else 0.0)
                    o.keyframe_insert("scale", frame=ff)
            f += period + rnd.randint(4, 14)
        L.linear_fcurves(o)
        o.visible_shadow = False
        out.append(o)
    return out


def rim_figure_mat(name, base=(0.012, 0.012, 0.015), rim=(0.35, 0.85, 1.0), strength=1.5, power=2.5):
    """Silhouette material with a view-facing fresnel rim in emission (reads against beams and black).
    Returns (mat, strength_socket)."""
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*base, 1)
    p.inputs["Roughness"].default_value = 0.75
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    pw = n.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = power
    l.new(lw.outputs["Facing"], pw.inputs[0])
    mul = n.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = strength
    l.new(pw.outputs[0], mul.inputs[0])
    p.inputs["Emission Color"].default_value = (*rim, 1)
    l.new(mul.outputs[0], p.inputs["Emission Strength"])
    return m, mul.inputs[1]


def pose_sit(p, height=1.75, lean=-0.25):
    """Seated, knees hugged (char_figure rig). Pelvis sits on the ground at the root's z."""
    s = height / 1.75
    p["pelvis"].location.z = 0.06 * s
    p["pelvis"].rotation_euler = (lean, 0, 0)
    for tag in ("L", "R"):
        p[f"hip{tag}"].rotation_euler = (2.3 - lean, 0, 0)
        p[f"knee{tag}"].rotation_euler = (-1.61, 0, 0)
        p[f"shoulder{tag}"].rotation_euler = (0.95 - lean, 0, (0.18 if tag == "L" else -0.18))
        p[f"elbow{tag}"].rotation_euler = (0.9, 0, 0)
    p["neck"].rotation_euler = (-0.2, 0, 0)


def figure(name="fig", height=1.75, pose="stand", base=(0.012, 0.012, 0.015), rim=(0.35, 0.85, 1.0), rim_strength=1.5,
           mat=None):
    """Faceless char_figure with a rim-light material (shared mat optional). pose: stand | sit."""
    p = L.char_figure(name, color=base, height=height)
    if mat is None:
        mat, sock = rim_figure_mat(name + "_rim", base, rim, rim_strength)
    else:
        sock = None
    for k, o in list(p.items()):
        if o.type == "MESH":
            o.data.materials.clear()
            o.data.materials.append(mat)
    if pose == "sit":
        pose_sit(p, height)
    p["mat"] = mat
    p["rim_sock"] = sock
    return p


def group13(center=(0, 0, 0), face=0.0, spacing=0.62, seed=4, pose="sit", rows=(5, 5, 3), shared=False,
            rim=(0.35, 0.85, 1.0), rim_strength=1.5, coach_index=11, name="kid"):
    """13 faceless figures (12 smaller, 1 taller coach) in loose rows facing `face` (radians, 0 = +Y).
    Returns list of rigs, front row first."""
    rnd = random.Random(seed)
    out = []
    shared_mat = rim_figure_mat(name + "_shared", rim=rim, strength=rim_strength)[0] if shared else None
    rot = Matrix.Rotation(face, 3, "Z")
    k = 0
    for r, cnt in enumerate(rows):
        for c in range(cnt):
            x = (c - (cnt - 1) / 2) * spacing + rnd.uniform(-0.1, 0.1) + (0.2 if r % 2 else 0)
            y = -r * spacing * 0.95 + rnd.uniform(-0.08, 0.08)
            h = 1.72 if k == coach_index else rnd.uniform(1.28, 1.5)
            p = figure(f"{name}{k}", height=h, pose=pose, mat=shared_mat, rim=rim, rim_strength=rim_strength)
            v = rot @ Vector((x, y, 0))
            p["root"].location = Vector(center) + v
            p["root"].rotation_euler = (0, 0, face + rnd.uniform(-0.35, 0.35))
            out.append(p)
            k += 1
    return out


def rain(center, size, count=2200, n=100, speed=8.0, length=0.32, width=0.005, color=(0.7, 0.78, 0.85), strength=0.5,
         seed=3, name="rain"):
    """Falling rain streaks: crossed thin quads in one mesh, object drifts down (additive emission)."""
    rnd = random.Random(seed)
    fall = speed * n / 24.0
    bm = bmesh.new()
    for i in range(count):
        c = Vector((rnd.uniform(-0.5, 0.5) * size[0], rnd.uniform(-0.5, 0.5) * size[1],
                    rnd.uniform(-0.5 * size[2], 0.5 * size[2] + fall)))
        ln = length * rnd.uniform(0.6, 1.4)
        for ax in (Vector((width, 0, 0)), Vector((0, width, 0))):
            vs = [bm.verts.new(c + v) for v in (-ax, ax, ax + Vector((0, 0, ln)), -ax + Vector((0, 0, ln)))]
            bm.faces.new(vs)
    o = L.mesh_from_bm(name, bm)
    o.location = center
    m, n_, l = L._mat(name + "_m")
    for nd in list(n_):
        if nd.type == "BSDF_PRINCIPLED":
            n_.remove(nd)
    em = n_.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    tr = n_.new("ShaderNodeBsdfTransparent")
    ad = n_.new("ShaderNodeAddShader")
    l.new(tr.outputs[0], ad.inputs[0])
    l.new(em.outputs[0], ad.inputs[1])
    l.new(ad.outputs[0], n_["Material Output"].inputs["Surface"])
    _blended(m)
    L.assign(o, m)
    o.visible_shadow = False
    o.keyframe_insert("location", frame=1)
    o.location = Vector(center) - Vector((0, 0, fall))
    o.keyframe_insert("location", frame=n)
    L.linear_fcurves(o)
    return o


def heightfield(size=(60, 60), center=(0, 0, 0), res=0.8, fn=None, mat=None, name="terrain", disp=(0.6, 0.15)):
    """Grid mesh with z = fn(x, y) (world coordinates relative to center)."""
    nx, ny = max(2, int(size[0] / res)), max(2, int(size[1] / res))
    bm = bmesh.new()
    grid = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            x = -size[0] / 2 + size[0] * i / nx
            y = -size[1] / 2 + size[1] * j / ny
            row.append(bm.verts.new((x, y, fn(x + center[0], y + center[1]) if fn else 0.0)))
        grid.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    o = L.mesh_from_bm(name, bm)
    o.location = center
    if disp[0]:
        L.add_displace(o, strength=disp[0], scale=2.0, name=name + "_d1")
    if disp[1]:
        L.add_displace(o, strength=disp[1], scale=0.4, name=name + "_d2")
    L.smooth(o)
    L.assign(o, mat or rock_mat(name + "_m"))
    return o


def jungle(points, size=(0.9, 2.2), seed=1, c1=(0.015, 0.035, 0.012), c2=(0.05, 0.11, 0.035), name="jungle"):
    """Canopy blobs (displaced icos) at points [(x, y, z)]."""
    rnd = random.Random(seed)
    m = L.mat_noise_surface(name + "_m", c1, c2, scale=3, bump=0.8, voronoi=True, rough=0.8)
    out = []
    for i, p in enumerate(points):
        s = rnd.uniform(*size)
        o = L.prim("ico", loc=(p[0], p[1], p[2] + s * 0.35), subdivisions=2, radius=s, name=f"{name}{i}")
        o.scale = (rnd.uniform(0.9, 1.3), rnd.uniform(0.9, 1.3), rnd.uniform(0.6, 0.9))
        L.add_displace(o, strength=s * 0.45, scale=s * 0.35, name=f"{name}{i}_d")
        L.assign(o, m)
        out.append(o)
    return out


def cliff_with_mouth(width=4.5, height=3.6, wall=(36, 18), res=0.3, depth=26, seed=2, rock=None, inner_rock=None,
                     name="mouth", spring=0.45, passage_kw=None):
    """Cliff face in the XZ plane at y=0 (outside = -Y) with an arched cave mouth at x=0 (floor z=0) and a
    passage running into +Y. No booleans: faces inside the arch are skipped. Returns dict(wall, passage, info)."""
    rnd = random.Random(seed)
    off = rnd.random() * 50
    hw = width / 2
    zs = height * spring

    def inside(x, z):
        if z < -0.6:
            return False
        if z <= zs:
            return abs(x) < hw
        return (x / hw) ** 2 + ((z - zs) / (height - zs)) ** 2 < 1.0

    W, H = wall
    nx, nz = int(W / res), int((H + 1.0) / res)
    bm = bmesh.new()
    grid = []
    for j in range(nz + 1):
        row = []
        for i in range(nx + 1):
            x = -W / 2 + W * i / nx
            z = -1.0 + (H + 1.0) * j / nz
            r = math.hypot(x / max(hw, 0.1), max(0.0, z) / height)
            # wall bulges outward away from the mouth, recedes into an alcove near it
            y = -0.9 * min(1.0, max(0.2, r - 1.0)) * noise.noise(Vector((x * 0.25 + off, z * 0.25, 0.0))) \
                - 0.6 * min(1.0, max(0.0, r - 1.0)) \
                + 0.5 * max(0.0, 1.4 - r)
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    for j in range(nz):
        for i in range(nx):
            cx = -W / 2 + W * (i + 0.5) / nx
            cz = -1.0 + (H + 1.0) * (j + 0.5) / nz
            if inside(cx, cz):
                continue
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context="VERTS")
    # snap the stair-stepped hole rim onto the arch curve
    for v in bm.verts:
        x, z = v.co.x, v.co.z
        if z < -0.3 or abs(x) > hw * 1.8 or z > height * 1.8:
            continue
        if not any(e.is_boundary for e in v.link_edges):
            continue
        if z <= zs:
            v.co.x = math.copysign(hw, x if x else 1.0)
        else:
            dx, dz = x / hw, (z - zs) / (height - zs)
            r = math.hypot(dx, dz) or 1.0
            v.co.x, v.co.z = dx / r * hw, zs + dz / r * (height - zs)
    bm.normal_update()
    bm.faces.ensure_lookup_table()
    if len(bm.faces) and bm.faces[0].normal.y > 0:
        for f in bm.faces:
            f.normal_flip()
    o = L.mesh_from_bm(name + "_wall", bm)
    L.add_displace(o, strength=0.7, scale=1.6, name=name + "_wd1")
    L.add_displace(o, strength=0.18, scale=0.3, name=name + "_wd2")
    L.smooth(o)
    L.assign(o, rock or L.mat_noise_surface(name + "_rock", (0.06, 0.06, 0.05), (0.34, 0.32, 0.27), scale=0.9, bump=0.9))
    kw = dict(length=depth, half_w=hw * 1.25, half_h=height * 0.62, zc=height * 0.44, y0=0.8, seed=seed + 3,
              rough=0.15, floor_flat=0.32, mat=inner_rock or rock_mat(name + "_in", (0.02, 0.02, 0.02),
                                                                     (0.16, 0.14, 0.12)))
    kw.update(passage_kw or {})
    pas, info = passage(name=name + "_pass", **kw)
    cap = L.prim("plane", loc=(0, kw["y0"] + kw["length"] - 0.6, kw["zc"]), rot=(math.pi / 2, 0, 0), size=14,
                 name=name + "_endcap")
    L.assign(cap, L.mat_principled(name + "_capm", (0.01, 0.01, 0.01), rough=0.9))
    return {"wall": o, "passage": pas, "info": info, "cap": cap}


def dive_torch(loc, aim, energy=900, size_deg=24, beam_len=4.0, beam_strength=0.4, color=TORCH, body_len=0.22,
               name="torchprop"):
    """Hand-held canister torch prop with lens glow, spot and visible beam, pointing from loc toward aim."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_mode = "QUATERNION"
    root.rotation_quaternion = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y")
    body = L.prim("cyl", loc=(0, 0, body_len / 2), vertices=16, radius=0.028, depth=body_len, name=name + "_body")
    L.assign(body, L.mat_principled(name + "_bm", (0.03, 0.03, 0.035), rough=0.35, metal=0.4))
    body.parent = root
    head = L.prim("cyl", loc=(0, 0, 0.0), vertices=16, radius=0.038, depth=0.05, name=name + "_head")
    L.assign(head, L.mat_principled(name + "_hm", (0.15, 0.15, 0.16), rough=0.3, metal=0.8))
    head.parent = root
    lens = L.prim("cyl", loc=(0, 0, -0.027), vertices=16, radius=0.032, depth=0.004, name=name + "_lens")
    lm = emis(name + "_lm", color, 25)
    L.assign(lens, lm)
    lens.parent = root
    sp = L.spot((0, 0, -0.03), (0, 0, 0), energy=energy, size_deg=size_deg, blend=0.45, color=color, name=name + "_sp",
                radius=0.02)
    sp.parent = root
    beam, sock = (None, None)
    if beam_len:
        beam, sock = beam_cone(sp, length=beam_len, color=color, strength=beam_strength, name=name + "_beam")
    return {"root": root, "spot": sp, "beam": beam, "beam_sock": sock, "lens_mat": lm}


def tank(loc, rot=(0, 0, 0), length=0.7, r=0.085, color=(0.62, 0.64, 0.66), band=(1.0, 0.78, 0.1), name="tank"):
    """Scuba cylinder with valve and a coloured band; local axis = Z."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = rot
    b = L.prim("cyl", loc=(0, 0, 0), vertices=18, radius=r, depth=length, name=name + "_b")
    L.assign(b, L.mat_principled(name + "_m", color, rough=0.3, metal=0.7))
    L.smooth(b)
    b.parent = root
    cap = L.prim("sphere", loc=(0, 0, length / 2), segments=16, ring_count=8, radius=r, name=name + "_cap")
    cap.scale = (1, 1, 0.6)
    L.assign(cap, b.active_material)
    cap.parent = root
    v = L.prim("cyl", loc=(0, 0, length / 2 + r * 0.7), vertices=10, radius=r * 0.3, depth=r * 0.9, name=name + "_v")
    L.assign(v, L.mat_principled(name + "_vm", (0.1, 0.1, 0.1), rough=0.4, metal=0.6))
    v.parent = root
    bd = L.prim("cyl", loc=(0, 0, length * 0.18), vertices=18, radius=r * 1.02, depth=length * 0.12, name=name + "_band")
    L.assign(bd, L.mat_principled(name + "_bdm", band, rough=0.5, emit=band, emit_strength=0.15))
    bd.parent = root
    return root


def full_face_mask(name="ffm", scale=1.0):
    """Full-face diving mask: clear visor dome with fresnel rim, black rubber frame, regulator. Faces local -Y."""
    root = L.link(bpy.data.objects.new(name, None))
    rub = L.mat_principled(name + "_rub", (0.02, 0.02, 0.022), rough=0.5)
    vis = L.prim("sphere", loc=(0, -0.02, 0), segments=24, ring_count=12, radius=1.0, name=name + "_visor")
    vis.scale = (0.11, 0.06, 0.14)
    L.assign(vis, rim_glass_mat(name + "_glass", (0.55, 0.9, 1.0), strength=2.2, power=2.5, base=0.04))
    L.smooth(vis)
    vis.parent = root
    fr = L.prim("torus", loc=(0, 0.0, 0), rot=(math.pi / 2, 0, 0), major_radius=1.0, minor_radius=0.12, name=name + "_frame")
    fr.scale = (0.12, 0.15, 0.12)
    L.assign(fr, rub)
    fr.parent = root
    reg = L.prim("cyl", loc=(0, -0.06, -0.1), rot=(math.pi / 2, 0, 0), vertices=16, radius=0.026, depth=0.035,
                 name=name + "_reg")
    L.assign(reg, rub)
    reg.parent = root
    root.scale = (scale,) * 3
    return root


def wrapped_child(name="child", length=1.25, suit=(0.02, 0.03, 0.04), mask=True, rim=(0.35, 0.85, 1.0), rim_strength=1.2):
    """Small wrapped figure lying along +Y (head at +Y), wetsuit/hood, optional full-face mask. Faceless.
    Returns dict(root, chest, head, mask)."""
    root = L.link(bpy.data.objects.new(name, None))
    m, sock = rim_figure_mat(name + "_suit", suit, rim, rim_strength)
    s = length / 1.25
    body = L.prim("sphere", loc=(0, 0, 0), segments=20, ring_count=12, radius=1.0, name=name + "_body")
    body.scale = (0.17 * s, 0.5 * s, 0.12 * s)
    L.assign(body, m)
    L.smooth(body)
    body.parent = root
    chest = L.prim("sphere", loc=(0, 0.2 * s, 0.03 * s), segments=16, ring_count=10, radius=1.0, name=name + "_chest")
    chest.scale = (0.16 * s, 0.22 * s, 0.11 * s)
    L.assign(chest, m)
    L.smooth(chest)
    chest.parent = root
    head = L.prim("sphere", loc=(0, 0.6 * s, 0.02 * s), segments=16, ring_count=10, radius=1.0, name=name + "_head")
    head.scale = (0.1 * s, 0.11 * s, 0.1 * s)
    L.assign(head, m)
    L.smooth(head)
    head.parent = root
    for k, yy in enumerate((-0.25, 0.05, 0.35)):  # wrap straps
        st = L.prim("torus", loc=(0, yy * s, 0), rot=(math.pi / 2, 0, 0), major_radius=1.0, minor_radius=0.035,
                    name=f"{name}_strap{k}")
        st.scale = (0.175 * s, 0.13 * s, 0.13 * s)
        L.assign(st, L.mat_principled(name + "_strapm", (0.12, 0.12, 0.11), rough=0.6))
        st.parent = root
    mk = None
    if mask:
        mk = full_face_mask(name + "_mask", scale=0.85 * s)
        mk.parent = root
        mk.location = (0, 0.62 * s, 0.1 * s)
        mk.rotation_euler = (-math.pi / 2, 0, 0)  # visor faces up (+Z) when lying on the back
    return {"root": root, "chest": chest, "head": head, "mask": mk, "rim_sock": sock, "mat": m}


def stretcher(name="sked", length=1.5, color=(0.85, 0.32, 0.06), child=True):
    """Small rescue stretcher (shell + wrapped shape). Long axis = local Y."""
    root = L.link(bpy.data.objects.new(name, None))
    sh = L.prim("cube", loc=(0, 0, 0.06), name=name + "_shell")
    sh.scale = (0.28, length / 2, 0.06)
    L.assign(sh, L.mat_principled(name + "_m", color, rough=0.55))
    L.bevel(sh, 0.04)
    sh.parent = root
    if child:
        c = wrapped_child(name + "_c", length=length * 0.8, mask=False, rim_strength=0.6)
        c["root"].parent = root
        c["root"].location = (0, -0.05, 0.16)
    return root


def work_light(loc, aim, energy=2500, color=(0.95, 0.97, 1.0), size_deg=70, name="wl"):
    """Tripod work light: pole, glowing panel, spot aimed at `aim`."""
    x, y, z = loc
    pole = L.prim("cyl", loc=(x, y, z / 2), vertices=8, radius=0.025, depth=z, name=name + "_pole")
    L.assign(pole, L.mat_principled(name + "_pm", (0.08, 0.08, 0.08), rough=0.5, metal=0.5))
    for k in range(3):
        a = k * 2 * math.pi / 3
        leg = L.prim("cyl", loc=(x + 0.25 * math.cos(a), y + 0.25 * math.sin(a), 0.3), vertices=6, radius=0.015,
                     depth=0.75, rot=(0.5 * math.sin(a), -0.5 * math.cos(a), 0), name=name + "_leg")
        L.assign(leg, pole.active_material)
    panel = L.prim("cube", loc=loc, name=name + "_panel")
    panel.scale = (0.22, 0.04, 0.16)
    panel.rotation_mode = "QUATERNION"
    panel.rotation_quaternion = (Vector(aim) - Vector(loc)).to_track_quat("-Y", "Z")
    L.assign(panel, emis(name + "_em", color, 30))
    sp = L.spot(loc, (0, 0, 0), energy=energy, size_deg=size_deg, blend=0.6, color=color, name=name + "_sp", radius=0.15)
    sp.rotation_mode = "QUATERNION"
    sp.rotation_quaternion = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y")
    return sp


def topo_relief(size=(16, 16), center=(0, 0, 0), height=3.5, seed=3, base=(0.015, 0.025, 0.025),
                line_color=CYAN, line_strength=1.6, spacing=0.3, res=0.12, name="topo"):
    """Dark terrain relief with glowing contour lines (map-room / briefing table look)."""
    rnd = random.Random(seed)
    off = Vector((rnd.random() * 40, rnd.random() * 40, 0))

    def fn(x, y):
        v = Vector((x * 0.12, y * 0.12, 0)) + off
        return height * (0.5 + 0.5 * noise.noise(v)) * (0.6 + 0.4 * noise.noise(v * 2.3))
    o = heightfield(size=size, center=center, res=res, fn=lambda x, y: fn(x - center[0], y - center[1]), name=name,
                    disp=(0, 0))
    m, n, l = L._mat(name + "_m")
    p = n["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*base, 1)
    p.inputs["Roughness"].default_value = 0.7
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sep.inputs[0])
    md = n.new("ShaderNodeMath")
    md.operation = "PINGPONG"
    md.inputs[1].default_value = spacing / 2
    l.new(sep.outputs["Z"], md.inputs[0])
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = spacing * 0.07
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    l.new(md.outputs[0], mr.inputs["Value"])
    mul = n.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = line_strength
    l.new(mr.outputs["Result"], mul.inputs[0])
    p.inputs["Emission Color"].default_value = (*line_color, 1)
    l.new(mul.outputs[0], p.inputs["Emission Strength"])
    L.assign(o, m)
    return o, mul.inputs[1]


def clip_poly(poly, axis, value, keep_less=True):
    """Sutherland-Hodgman clip of a 2D polygon [(a, b)] by axis (0/1) <= value (keep_less) or >= value."""
    def ins(p):
        return p[axis] <= value if keep_less else p[axis] >= value
    out = []
    N = len(poly)
    for i in range(N):
        cur, prv = poly[i], poly[i - 1]
        ci, pi_ = ins(cur), ins(prv)
        if ci != pi_:
            t = (value - prv[axis]) / ((cur[axis] - prv[axis]) or 1e-9)
            out.append((prv[0] + (cur[0] - prv[0]) * t, prv[1] + (cur[1] - prv[1]) * t))
        if ci:
            out.append(cur)
    return out


def flat_poly(pts_xz, y, mat, name="fill"):
    """Flat polygon in the XZ plane at depth y (front-facing -Y) for diagram fills."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z)) for x, z in pts_xz]
    if len(vs) < 3:
        bm.free()
        return None
    bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    o = L.mesh_from_bm(name, bm)
    L.assign(o, mat)
    return o


def bubble_trail(pos_fn, n, count=40, every=None, rise=0.9, size=0.02, seed=5, spread=0.06, life=(22, 40),
                 name="btrail", strength=1.6):
    """Exhalation bubbles spawned at a moving source: pos_fn(frame) -> Vector. Bubbles rise in world space."""
    rnd = random.Random(seed)
    m = rim_glass_mat(name + "_m", (0.7, 0.95, 1.0), strength=strength, power=1.5, base=0.15)
    out = []
    for i in range(count):
        f0 = (1 + int(i * (every or max(1, n / count)))) if every else rnd.randint(-20, n)
        lf = rnd.randint(*life)
        r = size * rnd.uniform(0.5, 1.4)
        o = L.prim("sphere", loc=(0, 0, 0), segments=8, ring_count=6, radius=r, name=f"{name}{i}")
        L.assign(o, m)
        L.smooth(o)
        base = Vector(pos_fn(max(1, f0))) + Vector((rnd.uniform(-spread, spread), rnd.uniform(-spread, spread), 0))
        ph = rnd.uniform(0, 6.28)
        keys = []
        for k in range(5):
            f = f0 + lf * k / 4
            p = base + Vector((0.04 * math.sin(ph + k * 1.7), 0.04 * math.cos(ph + k * 1.3), rise * (k / 4) * lf / 24))
            keys.append((f, p))
        o.scale = (0.001,) * 3
        o.keyframe_insert("scale", frame=keys[0][0] - 1)
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=keys[0][0])
        o.keyframe_insert("scale", frame=keys[-1][0] - 1)
        o.scale = (0.001,) * 3
        o.keyframe_insert("scale", frame=keys[-1][0])
        for f, p in keys:
            o.location = p
            o.keyframe_insert("location", frame=f)
        o.visible_shadow = False
        out.append(o)
    return out


# ----------------------------------------------------------------------------- CAVE-04 (Nutty Putty: dry cave, rope rig, desert hill)

def clay_mat(name="clay", c1=(0.2, 0.16, 0.12), c2=(0.5, 0.43, 0.34), scale=2.2, bump=0.5):
    return L.mat_noise_surface(name, c1, c2, scale=scale, bump=bump, rough=0.8, voronoi=False)


def crack_floor_z(x, y, crack_y=(-0.2, 1.3), hw=0.42, depth=5.0, wall_x=0.9, back_y=1.7, seed_off=3.0):
    """Crawlway floor with a steep V-crack across y-range crack_y (deepening toward +y), side walls, back wall."""
    z = 0.05 * noise.noise(Vector((x * 1.3 + seed_off, y * 1.3, 0.2)))
    z += 3.0 * max(0.0, abs(x) - wall_x) ** 1.5 + 3.0 * max(0.0, y - back_y) ** 1.5
    y0, y1 = crack_y
    if y0 < y < y1:
        t = (y - y0) / (y1 - y0)
        w = hw * math.sin(math.pi * min(1.0, t * 1.15)) ** 0.5
        if abs(x) < w:
            z -= min(depth * (0.5 + t), 9.0 * (w - abs(x)))
    return z


def crawl_ceiling_z(x, y, base=1.15, wall_x=1.1):
    return base + 0.1 * noise.noise(Vector((x * 0.9, y * 0.9, 4.0))) - 1.6 * max(0.0, abs(x) - wall_x) \
        - 1.2 * max(0.0, y - 2.1)


def crawl_set(y_far=-14.0, ceiling=1.15, mat=None, cmat=None, crack=True):
    """Low dry crawlway along -Y ending at a downward crack near y=0..1.3. Returns (floor objs, ceiling)."""
    mat = mat or clay_mat("crawlclay")
    cmat = cmat or clay_mat("crawlceil", (0.14, 0.12, 0.1), (0.42, 0.37, 0.3), scale=1.5)
    fz = crack_floor_z if crack else (lambda x, y: crack_floor_z(x, y, crack_y=(9, 9)))
    near = heightfield(size=(3.2, 3.6), center=(0, 0.6, 0), res=0.04, fn=fz, mat=mat, name="crackfloor", disp=(0, 0))
    far = heightfield(size=(3.2, abs(y_far) - 1.15), center=(0, (y_far - 1.2) / 2, 0), res=0.1, fn=fz, mat=mat,
                      name="crawlfloor", disp=(0, 0))
    ce = heightfield(size=(3.2, abs(y_far) + 3.0), center=(0, (y_far + 3.0) / 2, 0), res=0.12,
                     fn=lambda x, y: crawl_ceiling_z(x, y, ceiling), mat=cmat, name="crawlceil", disp=(0, 0))
    return [near, far], ce


def helmet(parent, s=1.0, color=(0.75, 0.08, 0.05), lamp_energy=300, lamp_deg=40, name="helmet", beam=False):
    """Caving helmet with headlamp on a char_figure neck (lamp points along neck local +Y, i.e. the face)."""
    h = L.prim("sphere", loc=(0, 0.0, 0.16 * s), segments=16, ring_count=8, radius=0.13 * s, name=name)
    h.scale = (1, 1.08, 0.8)
    L.assign(h, L.mat_principled(name + "_m", color, rough=0.35))
    h.parent = parent
    lens = L.prim("cyl", loc=(0, 0.13 * s, 0.17 * s), rot=(math.pi / 2, 0, 0), vertices=10, radius=0.028 * s,
                  depth=0.03 * s, name=name + "_lens")
    lm = emis(name + "_lm", (1.0, 0.85, 0.6), 18)
    L.assign(lens, lm)
    lens.parent = parent
    sp = None
    if lamp_energy:
        sp = L.spot((0, 0.16 * s, 0.17 * s), (math.pi / 2, 0, 0), energy=lamp_energy, size_deg=lamp_deg, blend=0.6,
                    color=(1.0, 0.85, 0.62), name=name + "_lamp", radius=0.02)
        sp.parent = parent
    return {"shell": h, "lens_mat": lm, "lamp": sp}


def crawler(name="crawler", height=1.7, suit=(0.16, 0.11, 0.07), helmet_color=(0.75, 0.08, 0.05), lamp_energy=300,
            rim=(1.0, 0.8, 0.55), rim_strength=0.6):
    """Faceless figure lying prone along its root +Y (head first), for crawlways. Root z = floor."""
    p = figure(name, height=height, base=suit, rim=rim, rim_strength=rim_strength)
    s = height / 1.75
    p["pelvis"].location = (0, -0.25 * s, 0.17 * s)
    p["pelvis"].rotation_euler = (-math.pi / 2, 0, 0)
    for tag, sg in (("L", 1), ("R", -1)):
        p[f"hip{tag}"].rotation_euler = (0.1, 0, sg * 0.15)
        p[f"knee{tag}"].rotation_euler = (-0.5, 0, 0)
        p[f"shoulder{tag}"].rotation_euler = (2.4, 0, 0)
        p[f"elbow{tag}"].rotation_euler = (0.9, 0, 0)
    p["neck"].rotation_euler = (0.9, 0, 0)
    hm = helmet(p["neck"], s, helmet_color, lamp_energy, name=name + "_hel")
    p.update({"helmet": hm["shell"], "lamp": hm["lamp"], "lamp_mat": hm["lens_mat"]})
    return p


def anim_crawl(p, n, rate=0.8, start=1, amp=0.45):
    """Alternating arm reach / knee drive on a crawler rig."""
    for f in range(start, n + 1, 2):
        ph = 2 * math.pi * rate * (f - start) / 24.0
        for tag, sg in (("L", 1), ("R", -1)):
            p[f"shoulder{tag}"].rotation_euler = (2.4 + sg * amp * math.sin(ph), 0, 0)
            p[f"elbow{tag}"].rotation_euler = (0.9 - sg * 0.4 * math.sin(ph), 0, 0)
            p[f"hip{tag}"].rotation_euler = (0.1 - sg * 0.35 * math.sin(ph), 0, sg * 0.15)
            p[f"knee{tag}"].rotation_euler = (-0.5 - 0.4 * max(0.0, sg * math.sin(ph)), 0, 0)
            for k in ("shoulder", "elbow", "hip", "knee"):
                p[f"{k}{tag}"].keyframe_insert("rotation_euler", frame=f)


def outline_figure(name="ofig", length=0.6, color=(0.78, 0.78, 0.76), strength=2.5, lamp=True, thick=0.018):
    """Flat diagram figure in the XZ plane (faces -Y): head at the root origin, body along local +Z (feet at +Z).
    Returns dict(root, mat, lamp_core, lamp_halo_emit, lamp_core_emit)."""
    root = L.link(bpy.data.objects.new(name, None))
    m = emis(name + "_m", color, strength)
    s = length / 0.6
    head = L.prim("torus", loc=(0, 0, 0), rot=(math.pi / 2, 0, 0), major_radius=0.055 * s, minor_radius=thick * 0.8,
                  name=name + "_head")
    L.assign(head, m)
    head.parent = root
    segs = [[(0, 0, 0.06), (0, 0, 0.3)], [(0, 0, 0.1), (-0.09, 0, 0.22)], [(0, 0, 0.1), (0.09, 0, 0.22)],
            [(0, 0, 0.3), (-0.05, 0, 0.58)], [(0, 0, 0.3), (0.05, 0, 0.58)]]
    for i, sg in enumerate(segs):
        c = curve([tuple(v * s for v in p) for p in sg], thickness=thick, mat=m, name=f"{name}_l{i}")
        c.parent = root
    out = {"root": root, "mat": m}
    if lamp:
        core, halo, hem = glow_dot((0, -0.01, -0.06 * s), (1.0, 0.85, 0.45), r=0.022 * s, halo=4, strength=10,
                                   name=name + "_lamp")
        core.parent = root
        out.update({"lamp_core": core, "lamp_halo_emit": hem,
                    "lamp_core_emit": core.active_material.node_tree.nodes["Emission"].inputs[1]})
    return out


def arrow2d(p0, p1, color=(1, 1, 1), strength=3.0, thick=0.02, head=0.12, y=-0.45, name="arrow"):
    """Line + cone head in the XZ plane from p0 to p1 ((x, z) tuples)."""
    m = emis(name + "_m", color, strength)
    a, b = Vector((p0[0], y, p0[1])), Vector((p1[0], y, p1[1]))
    d = (b - a).normalized()
    ln = curve([tuple(a), tuple(b - d * head * 0.8)], thickness=thick, mat=m, name=name + "_ln")
    cn = L.prim("cone", loc=tuple(b - d * head * 0.5), vertices=12, radius1=head * 0.45, radius2=0, depth=head,
                name=name + "_hd")
    cn.rotation_mode = "QUATERNION"
    cn.rotation_quaternion = d.to_track_quat("Z", "Y")
    L.assign(cn, m)
    return [ln, cn], m


def x_mark(center, size=0.16, color=(1.0, 0.15, 0.1), strength=5.0, y=-0.47, name="xmark"):
    m = emis(name + "_m", color, strength)
    cx, cz = center
    out = []
    for sg in (1, -1):
        out.append(curve([(cx - size, y, cz - sg * size), (cx + size, y, cz + sg * size)], thickness=0.025, mat=m,
                         name=name))
    return out, m


def bolt_anchor(loc, name="anchor", down=(0, 0, -1)):
    """Expansion bolt + hanger plate + carabiner-style ring, hanging from a ceiling point. Returns dict."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    steel = L.mat_principled(name + "_st", (0.7, 0.7, 0.72), rough=0.25, metal=1.0)
    bolt = L.prim("cyl", loc=(0, 0, 0.02), vertices=12, radius=0.012, depth=0.12, name=name + "_bolt")
    L.assign(bolt, steel)
    bolt.parent = root
    nut = L.prim("cyl", loc=(0, 0, -0.035), vertices=6, radius=0.02, depth=0.015, name=name + "_nut")
    L.assign(nut, steel)
    nut.parent = root
    hang = L.prim("cube", loc=(0, 0.0, -0.06), name=name + "_hanger")
    hang.scale = (0.025, 0.004, 0.045)
    L.assign(hang, steel)
    hang.parent = root
    ring = L.prim("torus", loc=(0, 0, -0.13), rot=(0, math.pi / 2, 0), major_radius=0.04, minor_radius=0.007,
                  name=name + "_krab")
    ring.scale = (1, 0.7, 1.4)
    L.assign(ring, L.mat_principled(name + "_kr", (0.9, 0.55, 0.1), rough=0.3, metal=0.8))
    ring.parent = root
    return {"root": root, "bolt": bolt, "hanger": hang, "krab": ring, "nut": nut}


def pulley(loc, name="pulley", rot=(0, 0, 0)):
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = rot
    wheel = L.prim("cyl", loc=(0, 0, 0), rot=(0, math.pi / 2, 0), vertices=20, radius=0.035, depth=0.02,
                   name=name + "_wheel")
    L.assign(wheel, L.mat_principled(name + "_wm", (0.6, 0.6, 0.62), rough=0.3, metal=1.0))
    wheel.parent = root
    for sx in (-1, 1):
        pl = L.prim("cube", loc=(sx * 0.016, 0, 0.01), name=name + "_side")
        pl.scale = (0.002, 0.026, 0.036)
        L.assign(pl, L.mat_principled(name + "_pm", (0.15, 0.35, 0.8), rough=0.4, metal=0.6))
        pl.parent = root
    return root


def star_dome(count=1500, radius=180.0, size=0.18, seed=7, strength=6.0, name="stars", min_elev=4.0):
    rnd = random.Random(seed)
    bm = bmesh.new()
    for i in range(count):
        a = rnd.uniform(0, 2 * math.pi)
        e = math.radians(rnd.uniform(min_elev, 88))
        c = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))) * radius
        r = size * rnd.uniform(0.5, 1.5)
        vs = [bm.verts.new(c + Vector(v) * r) for v in ((1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1))]
        for f in ((0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)):
            bm.faces.new([vs[k] for k in f])
    o = L.mesh_from_bm(name, bm)
    L.assign(o, emis(name + "_m", (0.85, 0.9, 1.0), strength))
    o.visible_shadow = False
    return o


def sagebrush(points, seed=3, color=(0.32, 0.34, 0.27), size=(0.35, 0.7), name="sage"):
    """Low grey-green shrubs: small bare twig cluster + 2-3 fuzzy blobs each. Returns list of roots."""
    rnd = random.Random(seed)
    m = L.mat_noise_surface(name + "_m", tuple(c * 0.45 for c in color), color, scale=9, bump=0.7, voronoi=False)
    tw = L.mat_principled(name + "_tw", (0.12, 0.1, 0.08), rough=0.8)
    out = []
    for i, p in enumerate(points):
        s = rnd.uniform(*size)
        root = L.link(bpy.data.objects.new(f"{name}{i}", None))
        root.location = p
        for k in range(rnd.randint(2, 3)):
            b = L.prim("ico", loc=(rnd.uniform(-0.3, 0.3) * s, rnd.uniform(-0.3, 0.3) * s, s * rnd.uniform(0.35, 0.6)),
                       subdivisions=2, radius=s * rnd.uniform(0.35, 0.55), name=f"{name}{i}_b{k}")
            b.scale = (1, 1, 0.7)
            L.add_displace(b, strength=s * 0.25, scale=s * 0.2, name=f"{name}{i}_d{k}")
            L.assign(b, m)
            b.parent = root
        for k in range(3):
            t = L.prim("cone", loc=(0, 0, s * 0.25), vertices=4, radius1=0.015, radius2=0.003, depth=s * 0.5,
                       rot=(rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), 0), name=f"{name}{i}_t{k}")
            L.assign(t, tw)
            t.parent = root
        out.append(root)
    return out


def hill_z(x, y, pit=(0.0, 0.0), pit_r=(0.75, 0.55), pit_depth=2.6):
    """Bare desert hill rising toward +Y, with a small steep-walled cave opening (pit) at `pit`."""
    v = Vector((x * 0.06, y * 0.06, 1.7))
    z = 0.16 * (y + 40) * (1 - 0.35 * C_sm((y - 10) / 30)) + 2.2 * noise.noise(v) + 0.6 * noise.noise(v * 4) \
        - 0.0015 * x * x
    dx, dy = (x - pit[0]) / pit_r[0], (y - pit[1]) / pit_r[1]
    r = math.hypot(dx, dy)
    if r < 1.0:
        z -= pit_depth * min(1.0, ((1.0 - r) / 0.3)) ** 0.7
    return z


def C_sm(x):
    return sm(x)


def hill_set(mat=None, fine_res=0.07, coarse_res=0.7, pit=(0.0, 0.0)):
    """Coarse hill (120 m) + fine patch (12 m) around the cave opening. Returns (coarse, fine, ground_z(x, y))."""
    mat = mat or L.mat_noise_surface("hillsoil", (0.2, 0.16, 0.12), (0.46, 0.39, 0.3), scale=0.5, bump=0.5,
                                     voronoi=False)
    fn = lambda x, y: hill_z(x, y, pit)
    coarse = heightfield(size=(140, 140), center=(0, 20, 0), res=coarse_res, fn=lambda x, y: fn(x, y) - 0.08, mat=mat,
                         name="hill", disp=(0, 0))
    fine = heightfield(size=(12, 12), center=(pit[0], pit[1], 0), res=fine_res, fn=fn, mat=mat, name="hillpatch",
                       disp=(0, 0))
    return coarse, fine, fn
