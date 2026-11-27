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


def silt_mat(name="silt", c1=(0.16, 0.13, 0.09), c2=(0.36, 0.31, 0.23)):
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


def beam_mat(name, color=TORCH, strength=1.2, along_pow=1.6):
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
    sq.inputs[1].default_value = 2.0
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
    bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=24, radius1=r, radius2=0.015, depth=length)
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
    bm = bmesh.new()
    for i in range(count):
        if shape == "sphere":
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
    mound_m = silt_mat(name + "_mound", (0.2, 0.17, 0.12), (0.38, 0.33, 0.25))
    tank = L.prim("cyl", loc=(0.05, 0.1, 0.09 - sink * 0.18), rot=(math.pi / 2, 0.15, 0), vertices=20, radius=0.1,
                  depth=0.75, name=name + "_tank")
    L.assign(tank, metal)
    L.smooth(tank)
    tank.parent = root
    valve = L.prim("cyl", loc=(0.05, 0.5, 0.09 - sink * 0.18), rot=(math.pi / 2, 0, 0), vertices=10, radius=0.03,
                   depth=0.1, name=name + "_valve")
    L.assign(valve, metal)
    valve.parent = root
    mound = L.prim("sphere", loc=(-0.12, -0.05, -0.05), segments=24, ring_count=12, name=name + "_mound")
    mound.scale = (0.32, 0.85, 0.16)
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
                  rock=None):
    """Bottom of a vast dark chamber: silt floor, scattered boulders, optional far curved back wall."""
    cx, cy, cz = center
    fl = floor(size=(size, size), center=center, strength=0.45, name="chamber_floor")
    rnd = random.Random(seed)
    pts = []
    for i in range(boulder_count):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(2.2, size * 0.35)
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
    l.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = n.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.42
    cr.elements[0].color = (*ground, 1)
    cr.elements[1].position = 0.75
    cr.elements[1].color = (*top, 1)
    e = cr.elements.new(0.5)
    e.color = (*horizon, 1)
    e2 = cr.elements.new(0.56)
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
            ("rim", 1.03, 0.25), ("rim", 1.0, 0.0), ("rim", 0.98, -0.8), ("rim", 0.95, -2.5), ("rim", 0.9, -5.0),
            ("rim", 0.86, -8.0), ("rim", 0.8, -11.0), ("rim", 0.74, -depth + 0.6), ("rim", 0.62, -depth - 0.5)]
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
    pool = L.prim("circle" if False else "cyl", loc=(0, 0, pool_z - 0.05), vertices=64, radius=R * 0.9, depth=0.1,
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
             snow=None, name="xs"):
    """Rock slab (XZ plane, facing -Y) with a cave void cut from a polygon [(x, depth_m), ...] (clockwise or ccw).
    Returns dict(rock, water, outline, P) where P(x, depth) -> world Vector on the front face."""
    def P(x, d, y=None):
        return Vector((x * x_scale, slab[0] - 0.01 if y is None else y, depth_to_z(d)))
    pts2 = [(x * x_scale, depth_to_z(d)) for x, d in poly]
    # rock block
    x0, x1, z0, z1 = extent
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
    vs = [bm.verts.new((x, yb - 0.005, z)) for x, z in pts2]
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
    zs = [z for _, z in pts2]
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
    ramp.color_ramp.elements[0].color = (0.25, 0.25, 0.25, 1)
    ramp.color_ramp.elements[1].color = (0.05, 0.05, 0.05, 1)
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
