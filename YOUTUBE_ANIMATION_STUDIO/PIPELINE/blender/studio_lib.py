"""Studio Blender library: scene setup, materials, environments, characters, FX, cameras.

Run with /opt/bpyenv/bin/python (bpy 5.0). All geometry is procedural and original.
Units: metres. Vertical 9:16 framing. Z up.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Euler, noise

# ----------------------------------------------------------------------------- scene

def reset(res=(720, 1280), fps=24, engine="BLENDER_EEVEE", samples=24):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.resolution_x, s.render.resolution_y = res
    s.render.resolution_percentage = 100
    s.render.fps = fps
    s.render.engine = engine
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGB"
    s.view_settings.view_transform = "AgX"
    s.view_settings.look = "AgX - Medium High Contrast"
    if engine == "CYCLES":
        s.cycles.samples = samples
        s.cycles.use_denoising = True
        s.cycles.device = "CPU"
        s.cycles.max_bounces = 4
        s.cycles.volume_bounces = 0
    else:
        e = s.eevee
        e.taa_render_samples = samples
        for attr, val in (("use_volumetric_shadows", True), ("volumetric_tile_size", "4"),
                          ("volumetric_samples", 48), ("use_bloom", True), ("use_gtao", True)):
            if hasattr(e, attr):
                try:
                    setattr(e, attr, val)
                except Exception:
                    pass
        if hasattr(e, "volumetric_end"):
            e.volumetric_end = 60
    w = bpy.data.worlds.new("World")
    s.world = w
    w.use_nodes = True
    set_world(color=(0, 0, 0), strength=0)
    return s


def set_world(color=(0.0, 0.0, 0.0), strength=1.0, volume=None):
    w = bpy.context.scene.world
    nt = w.node_tree
    bg = nt.nodes.get("Background") or nt.nodes.new("ShaderNodeBackground")
    bg.inputs[0].default_value = (*color, 1)
    bg.inputs[1].default_value = strength
    out = nt.nodes.get("World Output")
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    if volume:
        vol = nt.nodes.new("ShaderNodeVolumePrincipled")
        vol.inputs["Color"].default_value = (*volume.get("color", (0.3, 0.5, 0.6)), 1)
        vol.inputs["Density"].default_value = volume.get("density", 0.05)
        vol.inputs["Anisotropy"].default_value = volume.get("anisotropy", 0.6)
        if "absorption" in volume:
            vol.inputs["Absorption Color"].default_value = (*volume["absorption"], 1)
        nt.links.new(vol.outputs[0], out.inputs["Volume"])


def frames(seconds):
    return max(1, int(round(seconds * bpy.context.scene.render.fps)))


def set_range(n):
    s = bpy.context.scene
    s.frame_start, s.frame_end = 1, n


def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj

# ----------------------------------------------------------------------------- materials

def _mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links


def mat_principled(name, color, rough=0.6, metal=0.0, emit=None, emit_strength=0.0, alpha=1.0):
    m, n, l = _mat(name)
    p = n["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = emit_strength
    if alpha < 1:
        p.inputs["Alpha"].default_value = alpha
    return m


def mat_noise_surface(name, c1, c2, scale=3.0, rough=0.85, bump=0.6, detail=8, voronoi=True, metal=0.0):
    """Generic rocky / rusty / plaster surface: two-colour noise ramp + bump."""
    m, n, l = _mat(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = 0.6
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.7
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    if voronoi:
        vr = n.new("ShaderNodeTexVoronoi")
        vr.inputs["Scale"].default_value = scale * 1.7
        l.new(tc.outputs["Object"], vr.inputs["Vector"])
        mx = n.new("ShaderNodeMath")
        mx.operation = "ADD"
        l.new(nz.outputs["Fac"], mx.inputs[0])
        l.new(vr.outputs["Distance"], mx.inputs[1])
        l.new(mx.outputs[0], bp.inputs["Height"])
    else:
        l.new(nz.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_emission(name, color, strength=5.0):
    m, n, l = _mat(name)
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    e = n.new("ShaderNodeEmission")
    e.inputs[0].default_value = (*color, 1)
    e.inputs[1].default_value = strength
    l.new(e.outputs[0], n["Material Output"].inputs["Surface"])
    return m


def mat_volume(name, color=(0.2, 0.45, 0.5), density=0.08, anisotropy=0.5, absorption=None):
    m, n, l = _mat(name)
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    v = n.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (*color, 1)
    v.inputs["Density"].default_value = density
    v.inputs["Anisotropy"].default_value = anisotropy
    if absorption:
        v.inputs["Absorption Color"].default_value = (*absorption, 1)
    l.new(v.outputs[0], n["Material Output"].inputs["Volume"])
    return m


def mat_image(name, path, emit=0.0, rough=0.8):
    m, n, l = _mat(name)
    p = n["Principled BSDF"]
    t = n.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path)
    l.new(t.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    if emit:
        l.new(t.outputs["Color"], p.inputs["Emission Color"])
        p.inputs["Emission Strength"].default_value = emit
    return m


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

# presets
ROCK_CAVE = lambda: mat_noise_surface("rock_cave", (0.05, 0.045, 0.04), (0.28, 0.25, 0.2), scale=2.2, bump=0.9)
ROCK_LIME = lambda: mat_noise_surface("rock_lime", (0.25, 0.23, 0.19), (0.62, 0.58, 0.5), scale=1.8, bump=0.8)
SAND = lambda: mat_noise_surface("sand", (0.45, 0.4, 0.3), (0.7, 0.64, 0.5), scale=12, bump=0.2, voronoi=False)
SILT = lambda: mat_noise_surface("silt", (0.18, 0.15, 0.1), (0.35, 0.3, 0.22), scale=6, bump=0.15, voronoi=False)
RUST = lambda: mat_noise_surface("rust", (0.12, 0.05, 0.02), (0.42, 0.2, 0.08), scale=5, bump=0.7, metal=0.4)
PLASTER = lambda: mat_noise_surface("plaster", (0.32, 0.3, 0.26), (0.55, 0.52, 0.45), scale=4, bump=0.25, voronoi=False)
WOOD_OLD = lambda: mat_noise_surface("wood", (0.08, 0.05, 0.03), (0.25, 0.16, 0.09), scale=8, bump=0.3, voronoi=False)
CONCRETE = lambda: mat_noise_surface("concrete", (0.2, 0.2, 0.19), (0.45, 0.44, 0.42), scale=6, bump=0.35)
ASPHALT = lambda: mat_noise_surface("asphalt", (0.03, 0.03, 0.03), (0.12, 0.12, 0.12), scale=30, bump=0.2, voronoi=False)
GRASS_DARK = lambda: mat_noise_surface("grass", (0.02, 0.05, 0.02), (0.08, 0.13, 0.05), scale=15, bump=0.3, voronoi=False)

# ----------------------------------------------------------------------------- mesh helpers

def mesh_from_bm(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def add_displace(obj, strength=0.6, scale=1.2, tex_type="CLOUDS", name=None, depth=3):
    t = bpy.data.textures.new(name or f"tx_{obj.name}", tex_type)
    if tex_type in ("CLOUDS",):
        t.noise_scale = scale
        t.noise_depth = depth
    elif tex_type == "VORONOI":
        t.noise_scale = scale
    d = obj.modifiers.new("disp", "DISPLACE")
    d.texture = t
    d.strength = strength
    d.texture_coords = "GLOBAL"
    return d


def prim(kind, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), name=None, **kw):
    fn = {"cube": bpy.ops.mesh.primitive_cube_add, "sphere": bpy.ops.mesh.primitive_uv_sphere_add,
          "ico": bpy.ops.mesh.primitive_ico_sphere_add, "cyl": bpy.ops.mesh.primitive_cylinder_add,
          "cone": bpy.ops.mesh.primitive_cone_add, "plane": bpy.ops.mesh.primitive_plane_add,
          "torus": bpy.ops.mesh.primitive_torus_add}[kind]
    fn(location=loc, rotation=rot, **kw)
    o = bpy.context.active_object
    o.scale = scale
    if name:
        o.name = name
    return o


def apply_scale(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# ----------------------------------------------------------------------------- environments: cave

def cave_tunnel(path_pts, radius=2.5, seg=28, ring=22, seed=1, rough=0.55, mat=None, floor_silt=True, name="cave"):
    """Organic flooded tunnel following a polyline (list of xyz). Inside-facing tube with noise displacement."""
    rnd = random.Random(seed)
    pts = [Vector(p) for p in path_pts]
    # Catmull-Rom resample
    def cr(p0, p1, p2, p3, t):
        return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    samples = []
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    for i in range(1, len(ext) - 2):
        for k in range(seg):
            samples.append(cr(ext[i - 1], ext[i], ext[i + 1], ext[i + 2], k / seg))
    samples.append(pts[-1])
    bm = bmesh.new()
    rings = []
    up = Vector((0, 0, 1))
    off = rnd.random() * 100
    for i, c in enumerate(samples):
        tan = (samples[min(i + 1, len(samples) - 1)] - samples[max(i - 1, 0)]).normalized()
        side = tan.cross(up).normalized()
        nup = side.cross(tan).normalized()
        r_i = radius * (0.75 + 0.5 * (noise.noise(Vector((i * 0.07 + off, 0, 0))) + 0.5))
        ring_v = []
        for j in range(ring):
            a = 2 * math.pi * j / ring
            dirv = side * math.cos(a) + nup * math.sin(a)
            # flatten floor, widen sides (phreatic tube shape)
            sq = 1.0 + 0.35 * abs(math.cos(a))
            rr = r_i * sq
            if math.sin(a) < -0.45:
                rr *= 0.72
            n3 = noise.noise(c * 0.35 + dirv * 1.3 + Vector((off, off, off)))
            rr *= 1 + rough * 0.45 * n3
            ring_v.append(bm.verts.new(c + dirv * rr))
        rings.append(ring_v)
    for i in range(len(rings) - 1):
        for j in range(ring):
            a, b = rings[i][j], rings[i][(j + 1) % ring]
            c2, d = rings[i + 1][(j + 1) % ring], rings[i + 1][j]
            bm.faces.new((a, d, c2, b))  # inward normals
    o = mesh_from_bm(name, bm)
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 2
    add_displace(o, strength=0.35, scale=0.6, name=f"{name}_d1")
    add_displace(o, strength=0.12, scale=0.15, name=f"{name}_d2")
    smooth(o)
    assign(o, mat or ROCK_CAVE())
    o["samples"] = [tuple(v) for v in samples]
    return o, samples


def stalactites(center_pts, count=40, seed=3, length=(0.3, 1.4), radius=2.2, mat=None, up=True):
    rnd = random.Random(seed)
    m = mat or ROCK_LIME()
    objs = []
    for i in range(count):
        c = Vector(rnd.choice(center_pts))
        off = Vector((rnd.uniform(-1, 1) * radius * 0.6, rnd.uniform(-1, 1) * radius * 0.6, 0))
        L = rnd.uniform(*length)
        z = c.z + (radius * 0.85 if up else -radius * 0.6)
        o = prim("cone", loc=(c.x + off.x, c.y + off.y, z - (L / 2 if up else -L / 2)), vertices=8,
                 radius1=rnd.uniform(0.06, 0.2), radius2=0.005, depth=L, rot=((math.pi if up else 0), 0, 0))
        assign(o, m)
        objs.append(o)
    return objs


def boulders(points, count=25, seed=5, size=(0.2, 0.9), mat=None):
    rnd = random.Random(seed)
    m = mat or ROCK_CAVE()
    out = []
    for i in range(count):
        c = Vector(rnd.choice(points))
        s = rnd.uniform(*size)
        o = prim("ico", loc=(c.x + rnd.uniform(-1.5, 1.5), c.y + rnd.uniform(-1.5, 1.5), c.z - rnd.uniform(1.2, 1.8)),
                 subdivisions=2, radius=s)
        o.scale = (1, rnd.uniform(0.6, 1.3), rnd.uniform(0.4, 0.8))
        add_displace(o, strength=s * 0.4, scale=0.4, name=f"b{i}")
        smooth(o)
        assign(o, m)
        out.append(o)
    return out


def guideline(points, mat=None, thickness=0.012, name="guideline"):
    """Cave diver's guideline: thin white bevelled curve."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = thickness
    cu.bevel_resolution = 2
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (*p, 1)
    o = link(bpy.data.objects.new(name, cu))
    o.data.materials.append(mat or mat_principled("line_white", (0.9, 0.88, 0.8), rough=0.4, emit=(0.6, 0.6, 0.55), emit_strength=0.4))
    return o


def water_volume(center=(0, 0, 0), size=(60, 60, 60), color=(0.25, 0.5, 0.55), density=0.06, anisotropy=0.55, absorption=None, name="water"):
    o = prim("cube", loc=center, name=name)
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    assign(o, mat_volume(name + "_m", color, density, anisotropy, absorption))
    o.visible_shadow = False if hasattr(o, "visible_shadow") else None
    return o

# ----------------------------------------------------------------------------- particles

def particle_cloud(center, size, count=600, radius=0.012, mat=None, drift=(0, 0, 0.02), seed=7, nframes=240, name="silt",
                   jitter=0.004):
    """Suspended particles (silt, dust, plankton) as a single mesh of tiny tetrahedra, animated by shape-free
    object drift + per-vertex noise via a Wave-like displace. Cheap and render-engine agnostic."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    for i in range(count):
        c = Vector((center[0] + rnd.uniform(-size[0], size[0]) / 2, center[1] + rnd.uniform(-size[1], size[1]) / 2,
                    center[2] + rnd.uniform(-size[2], size[2]) / 2))
        r = radius * rnd.uniform(0.5, 1.6)
        vs = [bm.verts.new(c + Vector(v) * r) for v in ((1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1))]
        for f in ((0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)):
            bm.faces.new([vs[k] for k in f])
    o = mesh_from_bm(name, bm)
    assign(o, mat or mat_principled(name + "_m", (0.8, 0.75, 0.6), rough=1, emit=(0.5, 0.45, 0.35), emit_strength=0.25))
    o.visible_shadow = False
    d = add_displace(o, strength=0.25, scale=1.5, name=name + "_turb")
    # animate drift
    o.location = (0, 0, 0)
    o.keyframe_insert("location", frame=1)
    o.location = (drift[0] * nframes / 24, drift[1] * nframes / 24, drift[2] * nframes / 24)
    o.keyframe_insert("location", frame=nframes)
    linear_fcurves(o)
    return o


def bubbles_stream(origin, count=40, nframes=120, rise=1.2, spread=0.15, seed=11, name="bubbles", size=0.03):
    """Rising exhalation bubbles: individual spheres keyframed upward with wobble."""
    rnd = random.Random(seed)
    m = mat_principled(name + "_m", (0.8, 0.95, 1.0), rough=0.05, emit=(0.6, 0.8, 0.9), emit_strength=0.6)
    out = []
    for i in range(count):
        r = size * rnd.uniform(0.4, 1.4)
        o = prim("sphere", loc=origin, segments=8, ring_count=6, radius=r)
        assign(o, m)
        start = rnd.randint(1, max(1, nframes - 10))
        ox, oy = rnd.uniform(-spread, spread), rnd.uniform(-spread, spread)
        o.location = (origin[0] + ox * 0.2, origin[1] + oy * 0.2, origin[2])
        o.scale = (0.001,) * 3
        o.keyframe_insert("location", frame=start - 1)
        o.keyframe_insert("scale", frame=start - 1)
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=start)
        steps = 4
        life = rnd.randint(30, 60)
        for k in range(steps + 1):
            f = start + life * k / steps
            o.location = (origin[0] + ox * (1 + k) + 0.05 * math.sin(k * 2 + i), origin[1] + oy * (1 + k),
                          origin[2] + rise * k / steps * life / 24)
            o.keyframe_insert("location", frame=f)
        o.scale = (0.001,) * 3
        o.keyframe_insert("scale", frame=start + life)
        out.append(o)
    return out


def linear_fcurves(obj):
    ad = obj.animation_data
    if not ad or not ad.action:
        return
    for fc in _fcurves(ad.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def _fcurves(action):
    if hasattr(action, "fcurves") and len(getattr(action, "fcurves", [])):
        return list(action.fcurves)
    out = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for cb in strip.channelbags:
                out.extend(cb.fcurves)
    return out


def ease_all(obj, mode="BEZIER"):
    ad = obj.animation_data
    if not ad or not ad.action:
        return
    for fc in _fcurves(ad.action):
        for kp in fc.keyframe_points:
            kp.interpolation = mode

# ----------------------------------------------------------------------------- lights

def spot(loc, rot, energy=400, size_deg=28, blend=0.4, color=(1, 0.95, 0.85), parent=None, name="spot", radius=0.05):
    L = bpy.data.lights.new(name, "SPOT")
    L.energy = energy
    L.spot_size = math.radians(size_deg)
    L.spot_blend = blend
    L.color = color
    L.shadow_soft_size = radius
    o = link(bpy.data.objects.new(name, L))
    o.location = loc
    o.rotation_euler = rot
    if parent:
        o.parent = parent
    return o


def point(loc, energy=100, color=(1, 1, 1), radius=0.2, name="pt"):
    L = bpy.data.lights.new(name, "POINT")
    L.energy = energy
    L.color = color
    L.shadow_soft_size = radius
    o = link(bpy.data.objects.new(name, L))
    o.location = loc
    return o


def area(loc, rot, energy=200, size=2, color=(1, 1, 1), name="area"):
    L = bpy.data.lights.new(name, "AREA")
    L.energy = energy
    L.size = size
    L.color = color
    o = link(bpy.data.objects.new(name, L))
    o.location = loc
    o.rotation_euler = rot
    return o


def sun(rot=(0.6, 0.2, 0.5), energy=3, color=(1, 1, 1), angle=2.0, name="sun"):
    L = bpy.data.lights.new(name, "SUN")
    L.energy = energy
    L.color = color
    L.angle = math.radians(angle)
    o = link(bpy.data.objects.new(name, L))
    o.rotation_euler = rot
    return o


def flicker(light_obj, nframes, base=None, seed=1, depth=0.6, rate=0.35, blackouts=()):
    """Keyframe irregular flicker; blackouts = [(start,end)] frames forced near zero."""
    rnd = random.Random(seed)
    L = light_obj.data
    base = base if base is not None else L.energy
    for f in range(1, nframes + 1, 2):
        v = base * (1 - depth * max(0, noise.noise(Vector((f * rate, seed, 0)))) - depth * 0.3 * rnd.random())
        if any(a <= f <= b for a, b in blackouts):
            v = base * 0.02
        L.energy = max(0.0, v)
        L.keyframe_insert("energy", frame=f)

# ----------------------------------------------------------------------------- characters

def char_diver(name="diver", suit=(0.05, 0.05, 0.06), accent=(0.9, 0.35, 0.05), tanks="sidemount", light_on=True,
               light_energy=900, scale=1.0):
    """Stylised scuba/cave diver built from primitives with an object-hierarchy rig.
    Returns dict of parts. Root faces +Y (swims along +Y), body horizontal (trim position)."""
    suit_m = mat_principled(name + "_suit", suit, rough=0.55)
    acc_m = mat_principled(name + "_acc", accent, rough=0.4)
    metal_m = mat_principled(name + "_metal", (0.55, 0.57, 0.6), rough=0.25, metal=1.0)
    glass_m = mat_principled(name + "_glass", (0.05, 0.08, 0.1), rough=0.05, metal=0.2)
    root = link(bpy.data.objects.new(name, None))
    root.empty_display_size = 0.3
    parts = {"root": root}

    def part(kind, loc, scl, rot=(0, 0, 0), mat=suit_m, parent=root, pname="p", **kw):
        o = prim(kind, loc=loc, rot=rot, **kw)
        o.scale = scl
        o.name = f"{name}_{pname}"
        assign(o, mat)
        smooth(o)
        o.parent = parent
        parts[pname] = o
        return o

    torso = part("sphere", (0, 0, 0), (0.22, 0.42, 0.16), pname="torso", segments=16, ring_count=10)
    part("sphere", (0, -0.42, -0.02), (0.18, 0.22, 0.14), pname="hips", segments=12, ring_count=8)
    head = part("sphere", (0, 0.58, 0.04), (0.12, 0.13, 0.13), pname="head", segments=16, ring_count=10)
    part("cube", (0, 0.66, 0.0), (0.09, 0.03, 0.06), mat=glass_m, pname="mask", parent=root)
    part("torus", (0, 0.67, 0.0), (0.1, 0.1, 0.07), rot=(math.pi / 2, 0, 0), mat=acc_m, pname="maskframe",
         major_radius=1.0, minor_radius=0.15)
    # tanks
    if tanks == "sidemount":
        for sx in (-1, 1):
            part("cyl", (sx * 0.27, -0.1, -0.06), (0.075, 0.075, 0.42), rot=(math.pi / 2, 0, 0), mat=metal_m,
                 pname=f"tank{sx}", vertices=16)
    else:
        for sx in ((-0.09, 0.09) if tanks == "doubles" else (0,)):
            part("cyl", (sx, -0.05, 0.2), (0.09, 0.09, 0.4), rot=(math.pi / 2, 0, 0), mat=metal_m, pname=f"tank{sx}",
                 vertices=16)
    # arms (shoulder pivots)
    for sx, tag in ((-1, "L"), (1, "R")):
        sh = link(bpy.data.objects.new(f"{name}_shoulder{tag}", None))
        sh.parent = root
        sh.location = (sx * 0.2, 0.32, 0.02)
        parts[f"shoulder{tag}"] = sh
        part("cyl", (0, 0.2, 0), (0.05, 0.05, 0.2), rot=(math.pi / 2, 0, 0), parent=sh, pname=f"arm{tag}", vertices=10)
        part("sphere", (0, 0.42, 0), (0.05, 0.06, 0.04), parent=sh, pname=f"hand{tag}", segments=8, ring_count=6)
        sh.rotation_euler = (0, 0, sx * 0.35)
        # hip/leg pivots
        hp = link(bpy.data.objects.new(f"{name}_hip{tag}", None))
        hp.parent = root
        hp.location = (sx * 0.1, -0.55, -0.02)
        parts[f"hip{tag}"] = hp
        part("cyl", (0, -0.25, 0), (0.07, 0.07, 0.25), rot=(math.pi / 2, 0, 0), parent=hp, pname=f"thigh{tag}", vertices=10)
        kn = link(bpy.data.objects.new(f"{name}_knee{tag}", None))
        kn.parent = hp
        kn.location = (0, -0.5, 0)
        parts[f"knee{tag}"] = kn
        part("cyl", (0, -0.22, 0), (0.055, 0.055, 0.22), rot=(math.pi / 2, 0, 0), parent=kn, pname=f"shin{tag}", vertices=10)
        part("cube", (0, -0.62, 0), (0.1, 0.22, 0.012), parent=kn, mat=acc_m, pname=f"fin{tag}")
    # helmet / handheld light
    if light_on:
        lamp = part("cyl", (0.0, 0.62, 0.15), (0.03, 0.03, 0.06), rot=(math.pi / 2, 0, 0), mat=metal_m, pname="lamp",
                    vertices=10)
        lens = part("cyl", (0.0, 0.69, 0.15), (0.032, 0.032, 0.006), rot=(math.pi / 2, 0, 0),
                    mat=mat_emission(name + "_lens", (1, 0.95, 0.85), 30), pname="lens", vertices=10)
        sp = spot((0, 0.72, 0.15), (-math.pi / 2, 0, 0), energy=light_energy, size_deg=24, blend=0.35, parent=root,
                  name=name + "_torch")
        parts["torch"] = sp
    root.scale = (scale,) * 3
    return parts


def anim_swim(parts, nframes, kick_rate=1.1, amp=0.35, start=1, arm_sweep=False):
    """Flutter kick: alternate hip/knee rotation; subtle body roll."""
    fps = bpy.context.scene.render.fps
    for f in range(start, start + nframes + 1, 2):
        t = (f - start) / fps
        ph = 2 * math.pi * kick_rate * t
        for tag, sgn in (("L", 1), ("R", -1)):
            parts[f"hip{tag}"].rotation_euler = (sgn * amp * math.sin(ph), 0, 0)
            parts[f"hip{tag}"].keyframe_insert("rotation_euler", frame=f)
            parts[f"knee{tag}"].rotation_euler = (max(0, sgn * amp * 1.2 * math.sin(ph - 0.8)), 0, 0)
            parts[f"knee{tag}"].keyframe_insert("rotation_euler", frame=f)
            if arm_sweep:
                parts[f"shoulder{tag}"].rotation_euler = (0.2 * math.sin(ph * 0.5), 0, (-1 if tag == "L" else 1) * (0.35 + 0.25 * math.sin(ph * 0.5)))
                parts[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)


def path_follow(obj, pts, start, end, bank=False, ease=True, look=True):
    """Keyframe obj along list of points between frames, oriented along +Y travel direction."""
    n = len(pts)
    for i, p in enumerate(pts):
        f = start + (end - start) * i / max(1, n - 1)
        obj.location = p
        if look and n > 1:
            a, b = Vector(pts[max(0, i - 1)]), Vector(pts[min(n - 1, i + 1)])
            d = (b - a).normalized()
            obj.rotation_euler = d.to_track_quat("Y", "Z").to_euler()
            obj.keyframe_insert("rotation_euler", frame=f)
        obj.keyframe_insert("location", frame=f)
    if not ease:
        linear_fcurves(obj)


def char_figure(name="figure", color=(0.02, 0.02, 0.025), height=1.75, coat=False, emit=None):
    """Faceless silhouette human (used for victims/witnesses/investigators: respectful, non-identifying).
    Pivot empties: hipL/R, kneeL/R, shoulderL/R, neck. Faces -Y? No: faces +Y."""
    m = mat_principled(name + "_m", color, rough=0.8, emit=emit, emit_strength=(2.0 if emit else 0))
    root = link(bpy.data.objects.new(name, None))
    parts = {"root": root}
    s = height / 1.75

    def piv(pn, loc, parent):
        e = link(bpy.data.objects.new(f"{name}_{pn}", None))
        e.parent = parent
        e.location = loc
        parts[pn] = e
        return e

    def body(kind, loc, scl, parent, pn, rot=(0, 0, 0), **kw):
        o = prim(kind, loc=loc, rot=rot, **kw)
        o.scale = scl
        o.name = f"{name}_{pn}"
        assign(o, m)
        smooth(o)
        o.parent = parent
        parts[pn] = o
        return o

    pelvis = piv("pelvis", (0, 0, 0.95 * s), root)
    body("sphere", (0, 0, 0.32 * s), (0.19 * s, 0.12 * s, 0.33 * s), pelvis, "torso", segments=16, ring_count=10)
    if coat:
        body("cone", (0, 0, -0.05 * s), (0.26 * s, 0.18 * s, 0.45 * s), pelvis, "coat", vertices=16)
    neck = piv("neck", (0, 0, 0.66 * s), pelvis)
    body("sphere", (0, 0, 0.12 * s), (0.1 * s, 0.115 * s, 0.13 * s), neck, "head", segments=16, ring_count=10)
    for sx, tag in ((-1, "L"), (1, "R")):
        sh = piv(f"shoulder{tag}", (sx * 0.2 * s, 0, 0.56 * s), pelvis)
        body("cyl", (0, 0, -0.17 * s), (0.045 * s, 0.045 * s, 0.17 * s), sh, f"uarm{tag}", vertices=10)
        el = piv(f"elbow{tag}", (0, 0, -0.34 * s), sh)
        body("cyl", (0, 0, -0.15 * s), (0.04 * s, 0.04 * s, 0.15 * s), el, f"farm{tag}", vertices=10)
        hp = piv(f"hip{tag}", (sx * 0.1 * s, 0, 0.0), pelvis)
        body("cyl", (0, 0, -0.23 * s), (0.065 * s, 0.065 * s, 0.23 * s), hp, f"thigh{tag}", vertices=10)
        kn = piv(f"knee{tag}", (0, 0, -0.46 * s), hp)
        body("cyl", (0, 0, -0.22 * s), (0.05 * s, 0.05 * s, 0.22 * s), kn, f"shin{tag}", vertices=10)
        body("cube", (0, 0.05 * s, -0.46 * s), (0.05 * s, 0.11 * s, 0.03 * s), kn, f"foot{tag}")
    return parts


def anim_walk(parts, start, nframes, stride=0.5, rate=0.9, travel=None):
    """Simple walk cycle on figure rig; travel=(from_xyz,to_xyz) moves root linearly."""
    fps = bpy.context.scene.render.fps
    for f in range(start, start + nframes + 1, 2):
        t = (f - start) / fps
        ph = 2 * math.pi * rate * t
        for tag, sg in (("L", 1), ("R", -1)):
            parts[f"hip{tag}"].rotation_euler = (sg * stride * math.sin(ph), 0, 0)
            parts[f"knee{tag}"].rotation_euler = (-max(0, -sg * stride * 1.3 * math.sin(ph + 0.6)), 0, 0)
            parts[f"shoulder{tag}"].rotation_euler = (-sg * stride * 0.7 * math.sin(ph), 0, 0)
            parts[f"elbow{tag}"].rotation_euler = (0.25, 0, 0)
            for k in ("hip", "knee", "shoulder", "elbow"):
                parts[f"{k}{tag}"].keyframe_insert("rotation_euler", frame=f)
        parts["pelvis"].location.z = parts["pelvis"].location.z if f > start else parts["pelvis"].location.z
    if travel:
        r = parts["root"]
        r.location = travel[0]
        r.keyframe_insert("location", frame=start)
        r.location = travel[1]
        r.keyframe_insert("location", frame=start + nframes)
        linear_fcurves(r)


def shark(name="shark", length=3.5, color=(0.32, 0.36, 0.4)):
    """Low-poly stylised shark body (fusiform) with dorsal/pectoral/tail fins; tail pivot for swim."""
    m = mat_noise_surface(name + "_m", tuple(c * 0.6 for c in color), color, scale=4, bump=0.1, voronoi=False, rough=0.5)
    belly = mat_principled(name + "_b", (0.8, 0.8, 0.78), rough=0.5)
    root = link(bpy.data.objects.new(name, None))
    parts = {"root": root}
    body = prim("sphere", loc=(0, 0, 0), segments=24, ring_count=12)
    body.scale = (0.18 * length, 0.5 * length, 0.17 * length)
    assign(body, m)
    smooth(body)
    body.parent = root
    bel = prim("sphere", loc=(0, 0.02 * length, -0.05 * length), segments=16, ring_count=8)
    bel.scale = (0.15 * length, 0.42 * length, 0.11 * length)
    assign(bel, belly)
    smooth(bel)
    bel.parent = root
    for pn, loc, scl, rot in (("dorsal", (0, 0.02 * length, 0.2 * length), (0.02, 0.12, 0.16), (-0.5, 0, 0)),
                               ("pecL", (-0.2 * length, 0.12 * length, -0.06 * length), (0.18, 0.08, 0.015), (0, 0.4, 0.3)),
                               ("pecR", (0.2 * length, 0.12 * length, -0.06 * length), (0.18, 0.08, 0.015), (0, -0.4, -0.3))):
        o = prim("cube", loc=loc, rot=rot)
        o.scale = tuple(v * length for v in scl)
        assign(o, m)
        o.parent = root
        parts[pn] = o
    tail = link(bpy.data.objects.new(name + "_tailpivot", None))
    tail.parent = root
    tail.location = (0, -0.45 * length, 0)
    parts["tail"] = tail
    for z, r in ((0.14, -0.6), (-0.1, 0.6)):
        o = prim("cube", loc=(0, -0.12 * length, z * length), rot=(r, 0, 0))
        o.scale = (0.015 * length, 0.12 * length, 0.05 * length)
        assign(o, m)
        o.parent = tail
    parts["body"] = body
    return parts


def anim_shark_swim(parts, nframes, rate=0.8, amp=0.35, start=1):
    fps = bpy.context.scene.render.fps
    for f in range(start, start + nframes + 1, 2):
        t = (f - start) / fps
        parts["tail"].rotation_euler = (0, 0, amp * math.sin(2 * math.pi * rate * t))
        parts["tail"].keyframe_insert("rotation_euler", frame=f)

# ----------------------------------------------------------------------------- open water / reef / wreck

def seabed(size=80, mat=None, seed=2, z=0, strength=1.2):
    o = prim("plane", loc=(0, 0, z), size=size)
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.subdivision_type = "SIMPLE"
    sub.levels = sub.render_levels = 6
    add_displace(o, strength=strength, scale=4.0, name="sea_d")
    add_displace(o, strength=0.15, scale=0.4, name="sea_d2")
    smooth(o)
    assign(o, mat or SAND())
    return o


def caustics_light(loc=(0, 0, 30), energy=6, scale=0.6, color=(0.75, 0.95, 1.0), animate_frames=0):
    """Sun with Voronoi gobo emulated by a textured emission plane? Simpler: animated sun + light-texture via area.
    Here: sun light plus a large emissive 'surface' plane with voronoi pattern visible from below."""
    s = sun(rot=(0.15, 0.1, 0.3), energy=energy, color=color, angle=4)
    m, n, l = _mat("surface_m")
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    tc = n.new("ShaderNodeTexCoord")
    vr = n.new("ShaderNodeTexVoronoi")
    vr.feature = "SMOOTH_F1" if hasattr(vr, "feature") else vr.feature
    vr.inputs["Scale"].default_value = 0.25
    mp = n.new("ShaderNodeMapping")
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    l.new(mp.outputs[0], vr.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.9, 1, 1, 1)
    ramp.color_ramp.elements[1].position = 0.25
    ramp.color_ramp.elements[1].color = (0.05, 0.25, 0.35, 1)
    l.new(vr.outputs["Distance"], ramp.inputs["Fac"])
    em = n.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.5
    l.new(ramp.outputs[0], em.inputs[0])
    l.new(em.outputs[0], n["Material Output"].inputs["Surface"])
    p = prim("plane", loc=loc, size=200)
    assign(p, m)
    if animate_frames:
        mp.inputs["Location"].default_value = (0, 0, 0)
        mp.inputs["Location"].keyframe_insert("default_value", frame=1)
        mp.inputs["Location"].default_value = (3, 2, 0)
        mp.inputs["Location"].keyframe_insert("default_value", frame=animate_frames)
    return s, p


def coral_field(area=20, count=60, seed=4, z=0.0, palette=None):
    rnd = random.Random(seed)
    pal = palette or [(0.9, 0.35, 0.3), (0.95, 0.6, 0.2), (0.6, 0.3, 0.7), (0.2, 0.7, 0.6), (0.85, 0.8, 0.4)]
    mats = [mat_noise_surface(f"coral{i}", tuple(c * 0.5 for c in col), col, scale=10, bump=0.5, rough=0.7)
            for i, col in enumerate(pal)]
    out = []
    for i in range(count):
        x, y = rnd.uniform(-area, area), rnd.uniform(-area, area)
        kind = rnd.random()
        if kind < 0.4:  # brain/boulder coral
            o = prim("ico", loc=(x, y, z + 0.1), subdivisions=3, radius=rnd.uniform(0.3, 1.0))
            o.scale.z = 0.6
            add_displace(o, strength=0.08, scale=0.08, tex_type="VORONOI", name=f"cd{i}")
        elif kind < 0.75:  # branching: cluster of cones
            o = prim("cone", loc=(x, y, z + 0.4), vertices=6, radius1=0.08, radius2=0.01, depth=0.8)
            for k in range(rnd.randint(3, 6)):
                c = prim("cone", loc=(x + rnd.uniform(-0.3, 0.3), y + rnd.uniform(-0.3, 0.3), z + 0.35), vertices=6,
                         radius1=0.06, radius2=0.01, depth=rnd.uniform(0.4, 0.9), rot=(rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), 0))
                assign(c, rnd.choice(mats))
                out.append(c)
        else:  # fan
            o = prim("cube", loc=(x, y, z + 0.6), rot=(0, 0, rnd.uniform(0, 3.14)))
            o.scale = (0.6, 0.02, 0.6)
            add_displace(o, strength=0.1, scale=0.2, name=f"fd{i}")
        assign(o, rnd.choice(mats))
        smooth(o)
        out.append(o)
    return out


def fish_school(center, count=60, radius=3.0, nframes=240, seed=9, color=(0.75, 0.8, 0.85), orbit_speed=0.3, size=0.12):
    """School of small fish orbiting a centre (each a stretched ico + tail)."""
    rnd = random.Random(seed)
    m = mat_principled("fish_m", color, rough=0.3, metal=0.6)
    piv = link(bpy.data.objects.new("school", None))
    piv.location = center
    for i in range(count):
        a = rnd.uniform(0, 2 * math.pi)
        r = radius * rnd.uniform(0.6, 1.0)
        o = prim("ico", loc=(math.cos(a) * r, math.sin(a) * r, rnd.uniform(-1, 1)), subdivisions=1, radius=size)
        o.scale = (0.35, 1.0, 0.5)
        o.rotation_euler = (0, 0, a)
        assign(o, m)
        o.parent = piv
    piv.rotation_euler = (0, 0, 0)
    piv.keyframe_insert("rotation_euler", frame=1)
    piv.rotation_euler = (0, 0, orbit_speed * nframes / 24)
    piv.keyframe_insert("rotation_euler", frame=nframes)
    linear_fcurves(piv)
    return piv


def shipwreck(loc=(0, 0, 0), length=40, list_deg=12, broken=True, seed=6):
    """Large steel hull resting on the seabed, rusted, with superstructure, masts, portholes."""
    rnd = random.Random(seed)
    rust = RUST()
    dark = mat_principled("hull_dark", (0.04, 0.035, 0.03), rough=0.9)
    root = link(bpy.data.objects.new("wreck", None))
    root.location = loc
    root.rotation_euler = (0, math.radians(list_deg), 0)
    bm = bmesh.new()
    nseg, half = 24, length / 2
    prof = []
    for i in range(nseg + 1):
        y = -half + length * i / nseg
        t = i / nseg
        w = 4.0 * (math.sin(math.pi * min(1, t * 1.2)) ** 0.5 if t < 0.85 else (1 - (t - 0.85) / 0.15) * 0.95)
        w = max(0.3, w)
        ring = []
        for j in range(9):
            a = math.pi * j / 8
            x = -w * math.cos(a)
            z = -3.2 * math.sin(a) * (0.6 + 0.4 * min(1, w / 4)) + 3.0
            ring.append(bm.verts.new((x, y, z)))
        prof.append(ring)
    for i in range(nseg):
        for j in range(8):
            bm.faces.new((prof[i][j], prof[i][j + 1], prof[i + 1][j + 1], prof[i + 1][j]))
    hull = mesh_from_bm("hull", bm)
    sol = hull.modifiers.new("solid", "SOLIDIFY")
    sol.thickness = 0.15
    add_displace(hull, strength=0.15, scale=0.5, name="hull_d")
    assign(hull, rust)
    hull.parent = root
    deck = prim("cube", loc=(0, 0, 3.0))
    deck.scale = (3.6, half * 0.82, 0.08)
    assign(deck, rust)
    deck.parent = root
    # superstructure
    ss = prim("cube", loc=(0, -half * 0.35, 4.4))
    ss.scale = (2.4, 3.5, 1.4)
    assign(ss, rust)
    ss.parent = root
    br = prim("cube", loc=(0, -half * 0.3, 6.2))
    br.scale = (1.8, 1.6, 0.6)
    assign(br, rust)
    br.parent = root
    for k in range(8):  # portholes
        p = prim("cyl", loc=(2.42, -half * 0.35 - 3 + k * 0.85, 4.6), rot=(0, math.pi / 2, 0), vertices=12, radius=0.18, depth=0.1)
        assign(p, dark)
        p.parent = root
    for yy in (half * 0.35, -half * 0.05):  # masts, one broken
        mh = rnd.uniform(4, 8)
        m = prim("cyl", loc=(0, yy, 3 + mh / 2), vertices=10, radius=0.18, depth=mh, rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.2, 0.2), 0))
        assign(m, rust)
        m.parent = root
    fun = prim("cyl", loc=(0, -half * 0.18, 6.0), vertices=16, radius=0.8, depth=3.0, rot=(0.15, 0, 0))
    assign(fun, rust)
    fun.parent = root
    if broken:
        b = prim("cube", loc=(0, half * 0.15, 3.0))
        b.scale = (5, 1.2, 4)
        bo = hull.modifiers.new("break", "BOOLEAN")
        bo.object = b
        bo.operation = "DIFFERENCE"
        b.hide_render = True
        b.parent = root
    return root, hull

# ----------------------------------------------------------------------------- interiors / exteriors

def room(w=5, d=6, h=2.8, wall=None, floor=None, ceiling=None, door_wall="N", window_wall="E", name="room"):
    """Box room (open front -Y side for camera) with door and window cut-outs."""
    wall = wall or PLASTER()
    floor = floor or WOOD_OLD()
    objs = {}
    f = prim("plane", loc=(0, 0, 0), size=1)
    f.scale = (w, d, 1)
    assign(f, floor)
    objs["floor"] = f
    c = prim("plane", loc=(0, 0, h), size=1, rot=(math.pi, 0, 0))
    c.scale = (w, d, 1)
    assign(c, ceiling or wall)
    objs["ceiling"] = c
    specs = {"N": ((0, d / 2, h / 2), (math.pi / 2, 0, 0), (w, h)), "S": ((0, -d / 2, h / 2), (math.pi / 2, 0, 0), (w, h)),
             "E": ((w / 2, 0, h / 2), (math.pi / 2, 0, math.pi / 2), (d, h)), "W": ((-w / 2, 0, h / 2), (math.pi / 2, 0, math.pi / 2), (d, h))}
    for k, (loc, rot, (a, b)) in specs.items():
        o = prim("cube", loc=loc, rot=rot)
        o.scale = (a / 2, b / 2, 0.06)
        assign(o, wall)
        objs[k] = o
        cut = None
        if k == door_wall:
            cut = prim("cube", loc=(loc[0], loc[1], 1.05))
            cut.scale = (0.48, 0.48, 1.05) if k in "NS" else (0.48, 0.48, 1.05)
        if k == window_wall:
            cut = prim("cube", loc=(loc[0], loc[1], 1.5))
            cut.scale = (0.3, 0.6, 0.55) if k in "EW" else (0.6, 0.3, 0.55)
        if cut:
            bo = o.modifiers.new("cut", "BOOLEAN")
            bo.object = cut
            bo.operation = "DIFFERENCE"
            cut.hide_render = True
            cut.hide_viewport = True
    return objs


def corridor(length=30, w=2.6, h=3.0, door_every=4.0, wall=None, floor=None, name="corridor", lamp_every=6.0,
             lamp_energy=60, lamp_color=(1.0, 0.85, 0.6)):
    """Long institutional corridor along +Y (hospital / hotel / asylum) with side doors and ceiling lamps."""
    wall = wall or PLASTER()
    floor = floor or mat_noise_surface("tile", (0.2, 0.2, 0.18), (0.4, 0.38, 0.33), scale=2, bump=0.1, voronoi=True, rough=0.35)
    doorm = WOOD_OLD()
    out = {"lamps": []}
    f = prim("plane", loc=(0, length / 2, 0), size=1)
    f.scale = (w, length, 1)
    assign(f, floor)
    c = prim("plane", loc=(0, length / 2, h), size=1, rot=(math.pi, 0, 0))
    c.scale = (w, length, 1)
    assign(c, wall)
    for sx in (-1, 1):
        o = prim("cube", loc=(sx * w / 2, length / 2, h / 2))
        o.scale = (0.05, length / 2, h / 2)
        assign(o, wall)
    y = 2.0
    while y < length - 1:
        for sx in (-1, 1):
            dr = prim("cube", loc=(sx * (w / 2 - 0.03), y, 1.05))
            dr.scale = (0.04, 0.45, 1.05)
            assign(dr, doorm)
            fr = prim("cube", loc=(sx * (w / 2 - 0.02), y, 1.05))
            fr.scale = (0.03, 0.52, 1.12)
            assign(fr, mat_principled("frame", (0.1, 0.09, 0.08)))
        y += door_every
    y = 1.5
    while y < length:
        lo = prim("cube", loc=(0, y, h - 0.03))
        lo.scale = (0.25, 0.08, 0.02)
        assign(lo, mat_emission("lampm", lamp_color, 6))
        out["lamps"].append(point((0, y, h - 0.25), energy=lamp_energy, color=lamp_color, radius=0.3))
        y += lamp_every
    end = prim("cube", loc=(0, length, h / 2))
    end.scale = (w / 2, 0.05, h / 2)
    assign(end, wall)
    return out


def house_exterior(loc=(0, 0, 0), w=8, d=7, floors=2, roof_h=3.2, siding=None, roof=None, window_glow=(1, 0.7, 0.35),
                   lit_windows=(1,), seed=1):
    """Victorian-ish two-storey house with gable roof, porch, windows (some lit)."""
    rnd = random.Random(seed)
    siding = siding or mat_noise_surface("siding", (0.12, 0.11, 0.1), (0.28, 0.26, 0.23), scale=3, bump=0.2, voronoi=False)
    roofm = roof or mat_noise_surface("roof", (0.03, 0.03, 0.035), (0.09, 0.09, 0.1), scale=8, bump=0.4, voronoi=False)
    root = link(bpy.data.objects.new("house", None))
    root.location = loc
    fh = 3.0
    body = prim("cube", loc=(0, 0, fh * floors / 2))
    body.scale = (w / 2, d / 2, fh * floors / 2)
    assign(body, siding)
    body.parent = root
    bm = bmesh.new()
    z0 = fh * floors
    v = [bm.verts.new(p) for p in ((-w / 2 - 0.4, -d / 2 - 0.4, z0), (w / 2 + 0.4, -d / 2 - 0.4, z0), (0, -d / 2 - 0.4, z0 + roof_h),
                                   (-w / 2 - 0.4, d / 2 + 0.4, z0), (w / 2 + 0.4, d / 2 + 0.4, z0), (0, d / 2 + 0.4, z0 + roof_h))]
    for fc in ((0, 1, 2), (3, 5, 4), (0, 2, 5, 3), (1, 4, 5, 2), (0, 3, 4, 1)):
        bm.faces.new([v[i] for i in fc])
    r = mesh_from_bm("roof", bm)
    assign(r, roofm)
    r.parent = root
    lit = mat_emission("win_lit", window_glow, 4)
    dark = mat_principled("win_dark", (0.01, 0.012, 0.015), rough=0.1)
    idx = 0
    for fl in range(floors):
        for xx in (-w / 3, 0, w / 3):
            wn = prim("cube", loc=(xx, -d / 2 - 0.02, fl * fh + 1.6))
            wn.scale = (0.45, 0.04, 0.7)
            assign(wn, lit if idx in lit_windows else dark)
            wn.parent = root
            idx += 1
    door = prim("cube", loc=(0, -d / 2 - 0.03, 1.1))
    door.scale = (0.5, 0.04, 1.1)
    assign(door, WOOD_OLD())
    door.parent = root
    porch = prim("cube", loc=(0, -d / 2 - 1.2, 2.9))
    porch.scale = (w / 2, 1.2, 0.08)
    assign(porch, roofm)
    porch.parent = root
    for xx in (-w / 2 + 0.3, w / 2 - 0.3, -1.2, 1.2):
        pc = prim("cyl", loc=(xx, -d / 2 - 2.2, 1.45), vertices=8, radius=0.08, depth=2.9)
        assign(pc, siding)
        pc.parent = root
    return root


def tree(loc, height=8, seed=1, bare=True, mat=None):
    """Bare spooky tree: trunk + recursive branches as cones."""
    rnd = random.Random(seed)
    m = mat or mat_noise_surface("bark", (0.02, 0.02, 0.02), (0.08, 0.07, 0.06), scale=6, bump=0.5, voronoi=False)
    objs = []

    def branch(base, direction, length, radius, depth):
        end = base + direction * length
        mid = (base + end) / 2
        o = prim("cone", loc=mid, vertices=6, radius1=radius, radius2=radius * 0.55, depth=length)
        o.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
        assign(o, m)
        objs.append(o)
        if depth > 0:
            for _ in range(rnd.randint(2, 3)):
                d = (direction + Vector((rnd.uniform(-0.9, 0.9), rnd.uniform(-0.9, 0.9), rnd.uniform(-0.1, 0.5)))).normalized()
                branch(end, d, length * rnd.uniform(0.55, 0.75), radius * 0.55, depth - 1)

    branch(Vector(loc), Vector((0, 0, 1)), height * 0.45, height * 0.035, 3 if bare else 2)
    return objs


def forest(area=40, count=60, seed=3, clear_radius=4, z=0, road_halfwidth=None):
    rnd = random.Random(seed)
    out = []
    for i in range(count):
        x, y = rnd.uniform(-area, area), rnd.uniform(-area, area)
        if math.hypot(x, y) < clear_radius:
            continue
        if road_halfwidth and abs(x) < road_halfwidth + 1:
            continue
        out += tree((x, y, z), height=rnd.uniform(6, 12), seed=rnd.randint(0, 9999))
    return out


def road(length=200, width=7, mat=None, lines=True):
    r = prim("plane", loc=(0, length / 2 - 20, 0.01), size=1)
    r.scale = (width, length, 1)
    assign(r, mat or ASPHALT())
    if lines:
        lm = mat_principled("roadline", (0.8, 0.7, 0.3), rough=0.6, emit=(0.4, 0.35, 0.15), emit_strength=0.2)
        y = -20
        while y < length - 20:
            d = prim("plane", loc=(0, y, 0.02), size=1)
            d.scale = (0.12, 2.0, 1)
            assign(d, lm)
            y += 6
    return r


def ground(size=300, mat=None, z=0, strength=0.4):
    g = prim("plane", loc=(0, 0, z), size=size)
    sub = g.modifiers.new("sub", "SUBSURF")
    sub.subdivision_type = "SIMPLE"
    sub.levels = sub.render_levels = 5
    add_displace(g, strength=strength, scale=6, name="gr_d")
    assign(g, mat or GRASS_DARK())
    return g


def fog_volume(center=(0, 0, 2), size=(80, 80, 6), density=0.04, color=(0.7, 0.72, 0.8)):
    return water_volume(center=center, size=size, color=color, density=density, anisotropy=0.3, name="fog")

# ----------------------------------------------------------------------------- props

def table(loc, w=1.6, d=0.9, h=0.78, mat=None):
    m = mat or WOOD_OLD()
    top = prim("cube", loc=(loc[0], loc[1], loc[2] + h))
    top.scale = (w / 2, d / 2, 0.03)
    assign(top, m)
    for sx in (-1, 1):
        for sy in (-1, 1):
            leg = prim("cube", loc=(loc[0] + sx * (w / 2 - 0.05), loc[1] + sy * (d / 2 - 0.05), loc[2] + h / 2))
            leg.scale = (0.03, 0.03, h / 2)
            assign(leg, m)
    return top


def bed(loc, mat=None):
    m = mat or mat_principled("sheet", (0.55, 0.53, 0.5), rough=0.9)
    fr = prim("cube", loc=(loc[0], loc[1], loc[2] + 0.3))
    fr.scale = (0.5, 1.0, 0.1)
    assign(fr, mat_principled("bedframe", (0.15, 0.15, 0.16), metal=0.6, rough=0.4))
    mt = prim("cube", loc=(loc[0], loc[1], loc[2] + 0.45))
    mt.scale = (0.48, 0.97, 0.08)
    assign(mt, m)
    bevel(mt, 0.05)
    return mt


def chair(loc, rot_z=0, mat=None):
    m = mat or WOOD_OLD()
    root = link(bpy.data.objects.new("chair", None))
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    s = prim("cube", loc=(0, 0, 0.45))
    s.scale = (0.22, 0.22, 0.02)
    b = prim("cube", loc=(0, 0.21, 0.75))
    b.scale = (0.22, 0.02, 0.3)
    parts = [s, b]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(prim("cube", loc=(sx * 0.19, sy * 0.19, 0.22)))
            parts[-1].scale = (0.02, 0.02, 0.22)
    for p in parts:
        assign(p, m)
        p.parent = root
    return root


def bevel(o, w=0.02, segs=2):
    b = o.modifiers.new("bev", "BEVEL")
    b.width = w
    b.segments = segs
    return b


def text3d(body, loc=(0, 0, 0), rot=(math.pi / 2, 0, 0), size=0.5, extrude=0.02, mat=None, font=None, align="CENTER", name="txt"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    if font:
        cu.font = bpy.data.fonts.load(font)
    o = link(bpy.data.objects.new(name, cu))
    o.location = loc
    o.rotation_euler = rot
    o.data.materials.append(mat or mat_emission(name + "_m", (1, 1, 1), 3))
    return o

# ----------------------------------------------------------------------------- camera

def camera(loc=(0, -6, 1.6), target=None, lens=28, name="cam", dof=None):
    c = bpy.data.cameras.new(name)
    c.lens = lens
    c.clip_start = 0.05
    c.clip_end = 400
    o = link(bpy.data.objects.new(name, c))
    o.location = loc
    bpy.context.scene.camera = o
    if target is not None:
        if not isinstance(target, bpy.types.Object):
            t = link(bpy.data.objects.new(name + "_tgt", None))
            t.location = target
            target = t
        con = o.constraints.new("TRACK_TO")
        con.target = target
        con.track_axis = "TRACK_NEGATIVE_Z"
        con.up_axis = "UP_Y"
    if dof:
        c.dof.use_dof = True
        c.dof.aperture_fstop = dof.get("fstop", 2.8)
        if "target" in dof:
            c.dof.focus_object = dof["target"]
        else:
            c.dof.focus_distance = dof.get("distance", 3)
    return o, target


def cam_keys(cam, keys, ease=True):
    """keys: list of (frame, (x,y,z)) camera positions."""
    for f, p in keys:
        cam.location = p
        cam.keyframe_insert("location", frame=f)
    if not ease:
        linear_fcurves(cam)


def handheld(cam, nframes, amp=0.03, rate=0.6, seed=3, rot_amp=0.008):
    """Add subtle handheld / underwater sway via noise modifiers on location & rotation fcurves."""
    if not cam.animation_data or not cam.animation_data.action:
        cam.keyframe_insert("location", frame=1)
    cam.keyframe_insert("rotation_euler", frame=1)
    for fc in _fcurves(cam.animation_data.action):
        if fc.data_path in ("location", "rotation_euler"):
            m = fc.modifiers.new("NOISE")
            m.scale = 24 / max(0.05, rate)
            m.strength = amp * 2 if fc.data_path == "location" else rot_amp * 2
            m.phase = seed * 13 + fc.array_index * 7
            m.blend_type = "ADD"


def render_frames(out_dir, start=None, end=None, step=1):
    s = bpy.context.scene
    import os
    os.makedirs(out_dir, exist_ok=True)
    a = start or s.frame_start
    b = end or s.frame_end
    for f in range(a, b + 1, step):
        s.frame_set(f)
        s.render.filepath = os.path.join(out_dir, f"{f:04d}.png")
        if os.path.exists(s.render.filepath):
            continue
        bpy.ops.render.render(write_still=True)


def save_blend(path):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
