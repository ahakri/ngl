"""Scuba-category builders (SCUBA-01 Okene / SCUBA-02 Lonergans and future scuba shorts).

Import from shots.py:
    import sys, importlib; sys.path.insert(0, <PIPELINE/blender>); import lib_scuba as S; importlib.reload(S)
All builders are procedural, original, EEVEE-friendly. Units metres, Z up.
"""
import bpy, bmesh, math, random
from mathutils import Vector
import studio_lib as L

# ----------------------------------------------------------------------------- scene helpers


def setup(raytrace=True, vol_end=60, vol_tile="4", vol_samples=48):
    """EEVEE tweaks for water scenes: screen-space reflections/refraction for water surfaces."""
    e = bpy.context.scene.eevee
    for attr, val in (("use_raytracing", raytrace), ("volumetric_end", vol_end), ("volumetric_tile_size", vol_tile),
                      ("volumetric_samples", vol_samples), ("use_volumetric_shadows", True)):
        try:
            setattr(e, attr, val)
        except Exception:
            pass
    try:
        e.ray_tracing_options.resolution_scale = "2"
    except Exception:
        pass


def keep_live(o):
    """Give an object a (static) keyframe so L.bake_static() leaves its time-driven modifiers alive."""
    o.keyframe_insert("location", frame=1)
    return o


def keys(o, path, pairs, interp=None):
    """pairs: [(frame, value)] for any animatable attribute (tuple for vectors)."""
    for f, v in pairs:
        setattr(o, path, v)
        o.keyframe_insert(path, frame=f)
    if interp:
        ad = o.animation_data
        if ad and ad.action:
            for fc in L._fcurves(ad.action):
                if fc.data_path == path:
                    for kp in fc.keyframe_points:
                        kp.interpolation = interp


def sky_gradient(top=(0.25, 0.45, 0.8), horizon=(0.9, 0.75, 0.55), strength=1.0, sun_dir=None, sun_col=(1, 0.8, 0.5),
                 sun_size=0.04, sun_strength=8.0, below=None):
    """World: vertical gradient sky with an optional soft sun disc (for horizons / surface shots)."""
    w = bpy.context.scene.world
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nrm = nt.nodes.new("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    nt.links.new(tc.outputs["Generated"], nrm.inputs[0])
    sep2 = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(nrm.outputs[0], sep2.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position = 0.0
    els[0].color = (*(below or tuple(c * 0.5 for c in horizon)), 1)
    els[1].position = 0.5
    els[1].color = (*horizon, 1)
    e3 = els.new(0.62)
    e3.color = (*tuple(0.5 * a + 0.5 * b for a, b in zip(top, horizon)), 1)
    e4 = els.new(0.85)
    e4.color = (*top, 1)
    mp = nt.nodes.new("ShaderNodeMapRange")
    mp.inputs["From Min"].default_value = -1
    mp.inputs["From Max"].default_value = 1
    nt.links.new(sep2.outputs["Z"], mp.inputs["Value"])
    nt.links.new(mp.outputs[0], ramp.inputs["Fac"])
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs[1].default_value = strength
    col = ramp.outputs["Color"]
    if sun_dir is not None:
        d = Vector(sun_dir).normalized()
        dot = nt.nodes.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        dot.inputs[1].default_value = d
        nt.links.new(nrm.outputs[0], dot.inputs[0])
        r2 = nt.nodes.new("ShaderNodeMapRange")
        r2.inputs["From Min"].default_value = 1 - sun_size * 6
        r2.inputs["From Max"].default_value = 1.0
        nt.links.new(dot.outputs["Value"], r2.inputs["Value"])
        pw = nt.nodes.new("ShaderNodeMath")
        pw.operation = "POWER"
        pw.inputs[1].default_value = 3.0
        nt.links.new(r2.outputs[0], pw.inputs[0])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = sun_strength
        nt.links.new(pw.outputs[0], mul.inputs[0])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "ADD"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(col, mix.inputs[6])
        sc = nt.nodes.new("ShaderNodeMix")
        sc.data_type = "RGBA"
        sc.blend_type = "MULTIPLY"
        sc.inputs["Factor"].default_value = 1.0
        sc.inputs[6].default_value = (*sun_col, 1)
        nt.links.new(mul.outputs[0], sc.inputs[7])
        nt.links.new(sc.outputs[2], mix.inputs[7])
        col = mix.outputs[2]
    nt.links.new(col, bg.inputs[0])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    return w


def world_volume(color=(0.2, 0.5, 0.6), density=0.03, anisotropy=0.6, absorption=None):
    w = bpy.context.scene.world
    nt = w.node_tree
    out = [n for n in nt.nodes if n.type == "OUTPUT_WORLD"][0]
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (*color, 1)
    vol.inputs["Density"].default_value = density
    vol.inputs["Anisotropy"].default_value = anisotropy
    if absorption:
        vol.inputs["Absorption Color"].default_value = (*absorption, 1)
    nt.links.new(vol.outputs[0], out.inputs["Volume"])
    return vol

# ----------------------------------------------------------------------------- materials


def _m(name):
    return L._mat(name)


def mat_z_bands(name, bands, rough=0.5, metal=0.2, noise_amt=0.0, rust=None, space="Object"):
    """Paint split by object-space Z: bands = [(z_from, colour)] ascending (e.g. red antifouling / black topsides).
    rust=(strength) mixes rust/algae noise for wrecks."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs[space], sep.inputs[0])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    zs = [b[0] for b in bands]
    z0, z1 = min(zs) - 0.01, max(zs) + 1.0
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = z0
    mr.inputs["From Max"].default_value = z1
    l.new(sep.outputs["Z"], mr.inputs["Value"])
    els = ramp.color_ramp.elements
    for i, (z, c) in enumerate(bands):
        pos = (z - z0) / (z1 - z0)
        e = els[i] if i < 2 else els.new(pos)
        e.position = pos if i > 0 else 0.0
        e.color = (*c, 1)
    l.new(mr.outputs[0], ramp.inputs["Fac"])
    col = ramp.outputs["Color"]
    if rust:
        nz = n.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 1.6
        nz.inputs["Detail"].default_value = 10
        l.new(tc.outputs["Object"], nz.inputs["Vector"])
        rr = n.new("ShaderNodeValToRGB")
        rr.color_ramp.elements[0].position = 0.45
        rr.color_ramp.elements[0].color = (0, 0, 0, 1)
        rr.color_ramp.elements[1].position = 0.65
        rr.color_ramp.elements[1].color = (1, 1, 1, 1)
        l.new(nz.outputs["Fac"], rr.inputs["Fac"])
        mx = n.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        l.new(rr.outputs["Color"], mx.inputs["Factor"])
        l.new(col, mx.inputs[6])
        mx.inputs[7].default_value = (0.16, 0.11, 0.06, 1)
        mf = n.new("ShaderNodeMath")
        mf.operation = "MULTIPLY"
        mf.inputs[1].default_value = rust
        l.new(rr.outputs["Color"], mf.inputs[0])
        l.new(mf.outputs[0], mx.inputs["Factor"])
        col = mx.outputs[2]
        bp = n.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = 0.35 * rust
        l.new(nz.outputs["Fac"], bp.inputs["Height"])
        l.new(bp.outputs["Normal"], p.inputs["Normal"])
    l.new(col, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    return m


def mat_paint(name, color, rough=0.45, metal=0.15, grime=0.0, rust=0.0, scale=3.0):
    """Painted steel with optional grime/rust streaks (vertical-stretched noise)."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if grime <= 0 and rust <= 0:
        p.inputs["Base Color"].default_value = (*color, 1)
        return m
    tc = n.new("ShaderNodeTexCoord")
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale * 0.25)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Detail"].default_value = 8
    l.new(mp.outputs[0], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position = 0.4
    els[0].color = (*color, 1)
    els[1].position = 0.75
    els[1].color = (*tuple(c * (1 - grime) + r * rust for c, r in zip(color, (0.25, 0.12, 0.05))), 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.15 + 0.3 * rust
    l.new(nz.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_water_surface(name="watersurf", color=(0.02, 0.06, 0.07), rough=0.03, alpha=0.85, under_color=None,
                      under_strength=0.0, ripple=0.0, nframes=0):
    """Flat reflective water surface (EEVEE raytraced reflections). Backface can glow (seen from below).
    ripple>0 adds an animated bump."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = 0.8
    p.inputs["IOR"].default_value = 1.33
    out = n["Material Output"]
    shader = p.outputs[0]
    if ripple > 0:
        tc = n.new("ShaderNodeTexCoord")
        nz = n.new("ShaderNodeTexNoise")
        nz.noise_dimensions = "4D"
        nz.inputs["Scale"].default_value = 6.0
        nz.inputs["Detail"].default_value = 3
        l.new(tc.outputs["Object"], nz.inputs["Vector"])
        if nframes:
            nz.inputs["W"].default_value = 0
            nz.inputs["W"].keyframe_insert("default_value", frame=1)
            nz.inputs["W"].default_value = nframes / 24 * 0.8
            nz.inputs["W"].keyframe_insert("default_value", frame=nframes)
            _linear_node_anim(m)
        bp = n.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = ripple
        l.new(nz.outputs["Fac"], bp.inputs["Height"])
        l.new(bp.outputs["Normal"], p.inputs["Normal"])
    if alpha < 1:
        tr = n.new("ShaderNodeBsdfTransparent")
        mx = n.new("ShaderNodeMixShader")
        mx.inputs[0].default_value = alpha
        l.new(tr.outputs[0], mx.inputs[1])
        l.new(shader, mx.inputs[2])
        shader = mx.outputs[0]
        m.surface_render_method = "BLENDED"
    if under_color is not None:
        geo = n.new("ShaderNodeNewGeometry")
        em = n.new("ShaderNodeEmission")
        em.inputs[0].default_value = (*under_color, 1)
        em.inputs[1].default_value = under_strength
        mx2 = n.new("ShaderNodeMixShader")
        l.new(geo.outputs["Backfacing"], mx2.inputs[0])
        l.new(shader, mx2.inputs[1])
        l.new(em.outputs[0], mx2.inputs[2])
        shader = mx2.outputs[0]
    l.new(shader, out.inputs["Surface"])
    return m


def _linear_node_anim(mat):
    nt = mat.node_tree
    ad = nt.animation_data
    if ad and ad.action:
        for fc in L._fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


def mat_ocean(name="ocean", deep=(0.0, 0.09, 0.14), shallow=(0.0, 0.32, 0.38), rough=0.06, foam=True,
              under=(0.25, 0.65, 0.75), under_strength=1.5):
    """Open-ocean surface: facing-ratio colour (deep straight down / lighter at grazing), Ocean-modifier foam,
    glowing underside (Snell's window feel when seen from below)."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.4
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    l.new(lw.outputs["Facing"], mix.inputs["Factor"])
    mix.inputs[6].default_value = (*deep, 1)
    mix.inputs[7].default_value = (*shallow, 1)
    col = mix.outputs[2]
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = 0.7
    p.inputs["IOR"].default_value = 1.33
    if foam:
        at = n.new("ShaderNodeAttribute")
        at.attribute_name = "foam"
        mr = n.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.35
        mr.inputs["From Max"].default_value = 1.0
        l.new(at.outputs["Fac"], mr.inputs["Value"])
        fm = n.new("ShaderNodeMix")
        fm.data_type = "RGBA"
        l.new(mr.outputs[0], fm.inputs["Factor"])
        l.new(col, fm.inputs[6])
        fm.inputs[7].default_value = (0.85, 0.92, 0.95, 1)
        col = fm.outputs[2]
    l.new(col, p.inputs["Base Color"])
    out = n["Material Output"]
    geo = n.new("ShaderNodeNewGeometry")
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*under, 1)
    em.inputs[1].default_value = under_strength
    mx2 = n.new("ShaderNodeMixShader")
    l.new(geo.outputs["Backfacing"], mx2.inputs[0])
    l.new(p.outputs[0], mx2.inputs[1])
    l.new(em.outputs[0], mx2.inputs[2])
    l.new(mx2.outputs[0], out.inputs["Surface"])
    return m


def mat_caustic_ground(name="caustic_sand", c1=(0.45, 0.42, 0.33), c2=(0.75, 0.7, 0.55), caustic=(0.75, 1.0, 1.0),
                       strength=1.2, scale=0.9, nframes=0, speed=0.35, base_scale=10):
    """Sand / reef ground with animated caustic network (4D voronoi edge lines) added as emission."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = base_scale
    nz.inputs["Detail"].default_value = 6
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.7
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.9
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.25
    l.new(nz.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    caustic_into(m, tc.outputs["Object"], p, caustic, strength, scale, nframes, speed)
    return m


def caustic_into(m, vec_socket, p, caustic=(0.75, 1.0, 1.0), strength=1.2, scale=0.9, nframes=0, speed=0.35):
    """Add an animated caustic emission network to an existing principled material."""
    n, l = m.node_tree.nodes, m.node_tree.links
    dn = n.new("ShaderNodeTexNoise")
    dn.inputs["Scale"].default_value = 1.2
    dmix = n.new("ShaderNodeMix")
    dmix.data_type = "VECTOR"
    dmix.inputs["Factor"].default_value = 0.18
    l.new(vec_socket, dmix.inputs[4])
    l.new(dn.outputs["Color"], dmix.inputs[5])
    l.new(vec_socket, dn.inputs["Vector"])
    vr = n.new("ShaderNodeTexVoronoi")
    vr.voronoi_dimensions = "4D"
    vr.feature = "DISTANCE_TO_EDGE"
    vr.inputs["Scale"].default_value = scale
    l.new(dmix.outputs[1], vr.inputs["Vector"])
    if nframes:
        vr.inputs["W"].default_value = 0
        vr.inputs["W"].keyframe_insert("default_value", frame=1)
        vr.inputs["W"].default_value = speed * nframes / 24
        vr.inputs["W"].keyframe_insert("default_value", frame=nframes)
        _linear_node_anim(m)
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.09
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    l.new(vr.outputs["Distance"], mr.inputs["Value"])
    pw = n.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 2.0
    l.new(mr.outputs[0], pw.inputs[0])
    p.inputs["Emission Color"].default_value = (*caustic, 1)
    ms = n.new("ShaderNodeMath")
    ms.operation = "MULTIPLY"
    ms.inputs[1].default_value = strength
    l.new(pw.outputs[0], ms.inputs[0])
    l.new(ms.outputs[0], p.inputs["Emission Strength"])
    return m


def mat_beam(name="beam", color=(1, 0.95, 0.8), strength=2.0, falloff_axis="Z", length=1.0, alpha=0.6):
    """Additive-looking emissive transparent cone material fading along local axis (god rays / fake torch cones)."""
    m, n, l = _m(name)
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sep.inputs[0])
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    inv = n.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    l.new(lw.outputs["Facing"], inv.inputs[1])
    mul = n.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    l.new(sep.outputs[falloff_axis], mul.inputs[0])
    l.new(inv.outputs[0], mul.inputs[1])
    mul2 = n.new("ShaderNodeMath")
    mul2.operation = "MULTIPLY"
    mul2.inputs[1].default_value = alpha
    l.new(mul.outputs[0], mul2.inputs[0])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    tr = n.new("ShaderNodeBsdfTransparent")
    add = n.new("ShaderNodeAddShader")
    mx = n.new("ShaderNodeMixShader")
    l.new(mul2.outputs[0], mx.inputs[0])
    l.new(tr.outputs[0], mx.inputs[1])
    l.new(em.outputs[0], mx.inputs[2])
    l.new(tr.outputs[0], add.inputs[0])
    l.new(mx.outputs[0], add.inputs[1])
    l.new(mx.outputs[0], n["Material Output"].inputs["Surface"])
    m.surface_render_method = "BLENDED"
    m.use_transparency_overlap = True
    try:
        m.use_backface_culling = False
    except Exception:
        pass
    return m


def beam_cone(origin, direction, length=6, radius=0.8, color=(1, 0.95, 0.8), strength=2.0, alpha=0.5, name="beamcone",
              parent=None):
    """Fake volumetric beam (cheap, very readable on phones): open cone from origin along direction, fading out."""
    d = Vector(direction).normalized()
    o = L.prim("cone", loc=(0, 0, 0), vertices=24, radius1=radius, radius2=0.02, depth=length, name=name)
    # cone apex is +Z; put apex at origin
    me = o.data
    for v in me.vertices:
        v.co.z = -v.co.z + 0  # flip so apex at -Z? (keep tidy below)
    for v in me.vertices:
        v.co.z += length / 2
    # now apex (r=0.02) at z=0? after flip radius2 end (+depth/2) went to -depth/2 -> +0 ; base at +length
    o.location = origin
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    L.assign(o, mat_beam(name + "_m", color, strength, "Z", alpha=alpha))
    # Generated Z runs 0 at apex .. 1 at base: invert so it fades out
    nt = o.data.materials[0].node_tree
    sep = [nd for nd in nt.nodes if nd.type == "SEPXYZ"][0]
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    mul = [nd for nd in nt.nodes if nd.type == "MATH" and nd.operation == "MULTIPLY"][0]
    nt.links.new(sep.outputs["Z"], inv.inputs[1])
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 1.6
    nt.links.new(inv.outputs[0], pw.inputs[0])
    nt.links.new(pw.outputs[0], mul.inputs[0])
    o.visible_shadow = False
    if parent:
        o.parent = parent
    return o

# ----------------------------------------------------------------------------- ocean surface


def ocean(size=60, nframes=120, wave_scale=0.6, choppiness=0.9, resolution=10, spatial=40, wind=12, foam=True,
          mat=None, z=0.0, speed=1.0, loc=(0, 0, 0), repeat=1, name="ocean", alignment=0.0):
    """Animated Ocean-modifier surface (keyframed time => stays live through bake_static)."""
    bpy.ops.mesh.primitive_plane_add(size=2, location=(loc[0], loc[1], z))
    o = bpy.context.active_object
    o.name = name
    oc = o.modifiers.new("ocean", "OCEAN")
    oc.geometry_mode = "GENERATE"
    oc.size = size / spatial
    oc.spatial_size = int(spatial)
    oc.repeat_x = oc.repeat_y = repeat
    oc.resolution = resolution
    oc.wave_scale = wave_scale
    oc.choppiness = choppiness
    oc.wind_velocity = wind
    oc.wave_alignment = alignment
    oc.random_seed = 3
    if foam:
        oc.use_foam = True
        oc.foam_layer_name = "foam"
        oc.foam_coverage = 0.25
    oc.time = 1.0
    o.keyframe_insert('modifiers["ocean"].time', frame=1)
    oc.time = 1.0 + speed * nframes / 24
    o.keyframe_insert('modifiers["ocean"].time', frame=nframes)
    L.linear_fcurves(o)
    L.smooth(o)
    L.assign(o, mat or mat_ocean())
    return o


def wavy_plane(size=10, nframes=120, loc=(0, 0, 0), amp=0.03, mat=None, sub=6, name="wavy"):
    """Small rippled water plane (inside a compartment): two Wave modifiers, kept live."""
    o = L.prim("plane", loc=loc, size=1, name=name)
    o.scale = (size[0], size[1], 1) if isinstance(size, (tuple, list)) else (size, size, 1)
    L.apply_scale(o)
    s = o.modifiers.new("sub", "SUBSURF")
    s.subdivision_type = "SIMPLE"
    s.levels = s.render_levels = sub
    for i, (sx, sy, w, sp) in enumerate(((0.3, -0.2, 0.35, 0.05), (-0.5, 0.4, 0.22, 0.07))):
        wv = o.modifiers.new(f"wave{i}", "WAVE")
        wv.height = amp * (1 - 0.4 * i)
        wv.width = w
        wv.speed = sp
        wv.start_position_x = sx
        wv.start_position_y = sy
        wv.narrowness = 1.5
    L.smooth(o)
    if mat:
        L.assign(o, mat)
    keep_live(o)
    return o

# ----------------------------------------------------------------------------- vessels


def _loft(name, stations, close_ends=True):
    """stations: list of rings (list of xyz), same vert count; returns mesh object with quads + end caps."""
    bm = bmesh.new()
    rings = [[bm.verts.new(p) for p in r] for r in stations]
    k = len(rings[0])
    for i in range(len(rings) - 1):
        for j in range(k):
            a, b = rings[i][j], rings[i][(j + 1) % k]
            c, d = rings[i + 1][(j + 1) % k], rings[i + 1][j]
            bm.faces.new((a, b, c, d))
    if close_ends:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return L.mesh_from_bm(name, bm)


SECTION = [(1.0, 1.0), (1.0, 0.72), (0.97, 0.45), (0.86, 0.22), (0.62, 0.07), (0.3, 0.01), (0.0, 0.0)]


def tug(name="tug", length=14.0, beam=5.4, depth=2.4, rusted=0.0, lit_windows=False, hull_cols=None, house_col=None,
        algae=False, seed=3):
    """Compact harbour/offshore tug: lofted hull (bow +Y), red antifouling / black topsides / white band, rubber
    fender belt, two-tier deckhouse + wheelhouse with window band, twin funnels, mast, towing winch + H-bitt aft,
    Kort nozzle + rudder under the stern. Keel at z=0, deck ~depth. Returns (root, parts).
    Capsize: rotate root about Y by pi (roll) -- builders below use that."""
    rnd = random.Random(seed)
    root = L.link(bpy.data.objects.new(name, None))
    parts = {"root": root}
    nst = 22
    stations = []
    half = length / 2
    for i in range(nst + 1):
        t = i / nst  # 0 stern .. 1 bow
        y = -half + length * t
        if t < 0.08:
            b = beam / 2 * (0.86 + 0.14 * t / 0.08)
        elif t < 0.55:
            b = beam / 2
        else:
            u = (t - 0.55) / 0.45
            b = beam / 2 * max(0.03, (1 - u ** 1.8)) ** 0.6
        keel = 0.0
        if t < 0.18:
            keel = 0.9 * ((0.18 - t) / 0.18) ** 1.5  # stern cutaway / tunnel
        if t > 0.72:
            keel = depth * 0.95 * ((t - 0.72) / 0.28) ** 2.2
        deck = depth + 0.55 * t ** 2.4
        ring = []
        sec = SECTION
        for sx in (1, -1):
            pts = sec if sx == 1 else list(reversed(sec))
            for (xn, zn) in pts:
                if sx == -1 and xn == 0.0:
                    continue
                if sx == 1 and xn == 0.0:
                    ring.append((0, y, keel))
                    continue
                ring.append((sx * xn * b, y, keel + (deck - keel) * zn))
        # ring goes starboard deck->keel->port deck; drop duplicate keel handled above
        stations.append(ring)
    hull = _loft(name + "_hull", stations)
    sub = hull.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 1
    L.smooth(hull)
    wl = depth * 0.5
    cols = hull_cols or [(-1, (0.32, 0.05, 0.03)), (wl, (0.03, 0.03, 0.035)), (depth - 0.25, (0.85, 0.85, 0.82))]
    L.assign(hull, mat_z_bands(name + "_paint", cols, rough=0.5, metal=0.25, rust=rusted if rusted else None))
    hull.parent = root
    parts["hull"] = hull
    # deck plate
    deckm = mat_paint(name + "_deck", (0.22, 0.24, 0.22), rough=0.7, grime=0.4, rust=rusted)
    whitem = mat_paint(name + "_white", house_col or (0.82, 0.82, 0.78), rough=0.4, grime=0.25 + 0.5 * rusted,
                       rust=rusted * 0.8)
    darkm = L.mat_principled(name + "_dark", (0.02, 0.02, 0.025), rough=0.6)
    glassm = (L.mat_emission(name + "_win", (1.0, 0.75, 0.4), 6) if lit_windows else
              L.mat_principled(name + "_glass", (0.02, 0.03, 0.04), rough=0.05, metal=0.4))
    rubber = L.mat_principled(name + "_rubber", (0.015, 0.015, 0.015), rough=0.85)
    # deck slab follows the sheer roughly
    dk = L.prim("cube", loc=(0, -0.6, depth + 0.05), name=name + "_deck")
    dk.scale = (beam / 2 * 0.93, half * 0.8, 0.06)
    L.assign(dk, deckm)
    dk.parent = root
    # bulwark posts / rail
    # fender belt along the gunwale (curve following outline)
    cu = bpy.data.curves.new(name + "_fender", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.22
    cu.bevel_resolution = 3
    sp = cu.splines.new("POLY")
    outline = []
    for i in range(nst + 1):
        r = stations[i]
        outline.append(Vector(r[0]) + Vector((0.08, 0, -0.35)))
    for i in range(nst, -1, -1):
        r = stations[i]
        outline.append(Vector(r[-1]) + Vector((-0.08, 0, -0.35)))
    sp.points.add(len(outline) - 1)
    for i, p in enumerate(outline):
        sp.points[i].co = (*p, 1)
    sp.use_cyclic_u = True
    fo = L.link(bpy.data.objects.new(name + "_fender", cu))
    fo.data.materials.append(rubber)
    fo.parent = root
    parts["fender"] = fo
    # bow tyre fenders
    for k in range(4):
        tz = depth * 0.55 + k * 0.0
        tt = L.prim("torus", loc=(0.0 + (k - 1.5) * 0.55, half - 0.05, depth * (0.75 - 0.0)), major_radius=0.32,
                    minor_radius=0.13, rot=(math.pi / 2, 0, 0), name=f"{name}_tyre{k}")
        tt.rotation_euler = (0, math.pi / 2, 0)
        tt.location = ((k - 1.5) * 0.45, half * 0.97, depth * 0.55 + 0.2)
        L.assign(tt, rubber)
        tt.parent = root
    # deckhouse (lower) + wheelhouse
    dh = L.prim("cube", loc=(0, 1.2, depth + 1.0), name=name + "_house")
    dh.scale = (beam * 0.36, length * 0.2, 0.95)
    L.bevel(dh, 0.08)
    L.assign(dh, whitem)
    dh.parent = root
    wh = L.prim("cube", loc=(0, 1.9, depth + 2.65), name=name + "_wheelhouse")
    wh.scale = (beam * 0.33, length * 0.1, 0.7)
    L.bevel(wh, 0.06)
    L.assign(wh, whitem)
    wh.parent = root
    roof = L.prim("cube", loc=(0, 1.9, depth + 3.42), name=name + "_roof")
    roof.scale = (beam * 0.37, length * 0.12, 0.07)
    L.assign(roof, whitem)
    roof.parent = root
    # window band around wheelhouse
    for (lx, ly, sx, sy) in ((0, 1.9 + length * 0.1 + 0.01, beam * 0.3, 0.02),
                             (beam * 0.33 + 0.01, 1.9, 0.02, length * 0.085),
                             (-beam * 0.33 - 0.01, 1.9, 0.02, length * 0.085),
                             (0, 1.9 - length * 0.1 - 0.01, beam * 0.28, 0.02)):
        w = L.prim("cube", loc=(lx, ly, depth + 2.85), name=name + "_window")
        w.scale = (sx, sy, 0.3)
        L.assign(w, glassm)
        w.parent = root
    # portholes on lower house sides
    for sx in (-1, 1):
        for k in range(3):
            ph = L.prim("cyl", loc=(sx * (beam * 0.36 + 0.01), 0.2 + k * 0.9, depth + 1.15), vertices=14, radius=0.17,
                        depth=0.05, rot=(0, math.pi / 2, 0), name=f"{name}_port")
            L.assign(ph, glassm)
            ph.parent = root
    # funnels
    for sx in (-1, 1):
        f = L.prim("cube", loc=(sx * beam * 0.22, -0.9, depth + 2.6), name=f"{name}_funnel")
        f.scale = (0.28, 0.55, 0.85)
        f.rotation_euler = (-0.12, 0, 0)
        L.bevel(f, 0.1)
        L.assign(f, mat_z_bands(f"{name}_fun{sx}", [(-1, house_col or (0.82, 0.82, 0.78)), (0.55, (0.02, 0.02, 0.02))],
                                rough=0.5, rust=rusted if rusted else None))
        f.parent = root
    # mast
    m = L.prim("cyl", loc=(0, 1.9, depth + 4.6), vertices=8, radius=0.07, depth=2.4, name=name + "_mast")
    L.assign(m, whitem)
    m.parent = root
    yard = L.prim("cube", loc=(0, 1.9, depth + 5.2), name=name + "_yard")
    yard.scale = (0.9, 0.04, 0.04)
    L.assign(yard, whitem)
    yard.parent = root
    # aft: towing winch drum + H-bitt + towing hook
    wd = L.prim("cyl", loc=(0, -half * 0.45, depth + 0.55), vertices=16, radius=0.45, depth=1.8, rot=(0, math.pi / 2, 0),
                name=name + "_winch")
    L.assign(wd, mat_paint(name + "_winchm", (0.5, 0.12, 0.05), rough=0.5, grime=0.4, rust=rusted))
    wd.parent = root
    for sx in (-1, 1):
        b = L.prim("cyl", loc=(sx * 0.5, -half * 0.78, depth + 0.5), vertices=10, radius=0.14, depth=0.9,
                   name=f"{name}_bitt")
        L.assign(b, darkm)
        b.parent = root
    hb = L.prim("cube", loc=(0, -half * 0.78, depth + 0.75), name=name + "_hbar")
    hb.scale = (0.55, 0.08, 0.08)
    L.assign(hb, darkm)
    hb.parent = root
    # Kort nozzle + rudder + skeg (very readable when the hull is upside down)
    for sx in (-1, 1):
        nz = L.prim("cyl", loc=(sx * beam * 0.22, -half + 1.0, 0.55), vertices=24, radius=0.75, depth=0.9,
                    rot=(math.pi / 2, 0, 0), name=f"{name}_nozzle")
        sol = nz.modifiers.new("sol", "SOLIDIFY")
        sol.thickness = 0.12
        # hollow tube: delete caps by boolean-free trick -> scale a slightly smaller inner cylinder dark
        L.assign(nz, mat_paint(f"{name}_nozm{sx}", (0.32, 0.05, 0.03), rough=0.6, grime=0.4, rust=rusted))
        nz.parent = root
        inner = L.prim("cyl", loc=(sx * beam * 0.22, -half + 1.0, 0.55), vertices=16, radius=0.58, depth=0.95,
                       rot=(math.pi / 2, 0, 0), name=f"{name}_nozin")
        L.assign(inner, darkm)
        inner.parent = root
        for k in range(4):
            bl = L.prim("cube", loc=(sx * beam * 0.22, -half + 1.0, 0.55), name=f"{name}_blade")
            bl.scale = (0.5, 0.04, 0.12)
            bl.rotation_euler = (0, k * math.pi / 4 + 0.3, 0.3)
            L.assign(bl, L.mat_principled(f"{name}_bronze", (0.55, 0.38, 0.15), rough=0.35, metal=1.0))
            bl.parent = root
        rd = L.prim("cube", loc=(sx * beam * 0.22, -half + 0.2, 0.75), name=f"{name}_rudder")
        rd.scale = (0.05, 0.45, 0.7)
        L.assign(rd, mat_paint(f"{name}_rudm{sx}", (0.32, 0.05, 0.03), rough=0.6, grime=0.4, rust=rusted))
        rd.parent = root
    sk = L.prim("cube", loc=(0, -half * 0.35, 0.15), name=name + "_skeg")
    sk.scale = (0.08, half * 0.5, 0.2)
    L.assign(sk, mat_paint(name + "_skegm", (0.32, 0.05, 0.03), rough=0.6, rust=rusted))
    sk.parent = root
    if algae:
        # growth patches: bumpy dark-green flecks over the bottom
        pass
    parts["depth"] = depth
    return root, parts


def dive_boat(name="diveboat", length=16, beam=6.0, hull=(0.92, 0.93, 0.92), stripe=(0.05, 0.25, 0.6), seed=2):
    """Day dive catamaran: twin lofted hulls, bridging deck, enclosed cabin with dark windows, flybridge with
    bimini, dive-tank racks aft, swim ladder. Bow +Y, waterline z~0 (hull keel at -0.7)."""
    root = L.link(bpy.data.objects.new(name, None))
    parts = {"root": root}
    white = mat_z_bands(name + "_hullm", [(-2, (0.1, 0.12, 0.14)), (-0.05, hull), (0.55, stripe), (0.75, hull)],
                        rough=0.35, metal=0.0)
    whm = L.mat_principled(name + "_white", hull, rough=0.35)
    glass = L.mat_principled(name + "_glass", (0.02, 0.03, 0.05), rough=0.05, metal=0.5)
    blue = L.mat_principled(name + "_blue", stripe, rough=0.5)
    half = length / 2
    hw = beam * 0.16
    for sx in (-1, 1):
        sts = []
        for i in range(17):
            t = i / 16
            y = -half + length * t
            b = hw * (1 if t < 0.6 else max(0.05, 1 - ((t - 0.6) / 0.4) ** 1.6) ** 0.6)
            keel = -0.7 + (0.9 * ((t - 0.7) / 0.3) ** 2 if t > 0.7 else 0)
            deck = 1.0 + 0.3 * t ** 2
            ring = []
            for (xn, zn) in SECTION[:-1]:
                ring.append((sx * beam * 0.32 + xn * b, y, keel + (deck - keel) * zn))
            ring.append((sx * beam * 0.32, y, keel))
            for (xn, zn) in reversed(SECTION[:-1]):
                ring.append((sx * beam * 0.32 - xn * b, y, keel + (deck - keel) * zn))
            sts.append(ring)
        h = _loft(f"{name}_hull{sx}", sts)
        L.smooth(h)
        L.assign(h, white)
        h.parent = root
    dk = L.prim("cube", loc=(0, -0.5, 1.15), name=name + "_deck")
    dk.scale = (beam / 2 * 0.95, half * 0.85, 0.15)
    L.assign(dk, whm)
    dk.parent = root
    cab = L.prim("cube", loc=(0, 1.5, 2.25), name=name + "_cabin")
    cab.scale = (beam * 0.4, length * 0.2, 0.95)
    L.bevel(cab, 0.12)
    L.assign(cab, whm)
    cab.parent = root
    for (lx, ly, sx_, sy_) in ((0, 1.5 + length * 0.2 + 0.01, beam * 0.36, 0.02), (beam * 0.4 + 0.01, 1.5, 0.02, length * 0.17),
                               (-beam * 0.4 - 0.01, 1.5, 0.02, length * 0.17)):
        w = L.prim("cube", loc=(lx, ly, 2.45), name=name + "_win")
        w.scale = (sx_, sy_, 0.4)
        L.assign(w, glass)
        w.parent = root
    fb = L.prim("cube", loc=(0, 0.8, 3.3), name=name + "_flybridge")
    fb.scale = (beam * 0.36, length * 0.14, 0.1)
    L.assign(fb, whm)
    fb.parent = root
    bim = L.prim("cube", loc=(0, 0.8, 4.4), name=name + "_bimini")
    bim.scale = (beam * 0.38, length * 0.15, 0.05)
    L.assign(bim, blue)
    bim.parent = root
    for sx in (-1, 1):
        for sy in (-1, 1):
            pst = L.prim("cyl", loc=(sx * beam * 0.34, 0.8 + sy * length * 0.13, 3.85), vertices=6, radius=0.04, depth=1.1,
                         name=name + "_post")
            L.assign(pst, whm)
            pst.parent = root
    # tank racks aft
    tankm = L.mat_principled(name + "_tank", (0.75, 0.78, 0.8), rough=0.3, metal=0.9)
    for k in range(8):
        for sx in (-1, 1):
            tk = L.prim("cyl", loc=(sx * (beam * 0.42), -half * 0.6 + k * 0.45, 1.65), vertices=10, radius=0.1, depth=0.7,
                        name=name + "_tank")
            L.assign(tk, tankm)
            tk.parent = root
    # ladder
    for k in range(5):
        r = L.prim("cube", loc=(0, -half - 0.15, 0.9 - k * 0.3), name=name + "_rung")
        r.scale = (0.3, 0.03, 0.02)
        L.assign(r, tankm)
        r.parent = root
    return root, parts


def wake(start=(0, 0, 0.02), length=60, width0=2.0, width1=12, angle=0.0, name="wake", strength=1.0, curve=0.0, segs=30):
    """Foam wake: a flat ribbon widening behind a boat, white emissive-ish with noisy alpha, fading out."""
    bm = bmesh.new()
    prev = None
    d = Vector((math.sin(angle), -math.cos(angle), 0))
    side = Vector((-d.y, d.x, 0))
    vs = []
    for i in range(segs + 1):
        t = i / segs
        c = Vector(start) + d * length * t + side * curve * length * t * t
        w = width0 + (width1 - width0) * t
        a = bm.verts.new(c + side * w / 2)
        b = bm.verts.new(c - side * w / 2)
        vs.append((a, b))
    for i in range(segs):
        bm.faces.new((vs[i][0], vs[i][1], vs[i + 1][1], vs[i + 1][0]))
    uv = bm.loops.layers.uv.new()
    for f in bm.faces:
        for lp in f.loops:
            idx = [k for k, p in enumerate(vs) if lp.vert in p][0]
            lp[uv] = (1.0 if lp.vert == vs[idx][0] else 0.0, idx / segs)
    o = L.mesh_from_bm(name, bm)
    m, n, l = _m(name + "_m")
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    uvn = n.new("ShaderNodeUVMap")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(uvn.outputs[0], sep.inputs[0])
    # edge mask (two foam lines at the edges + centre churn near the stern)
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 8
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    edge = n.new("ShaderNodeMath")
    edge.operation = "PINGPONG"
    edge.inputs[1].default_value = 0.5
    l.new(sep.outputs["X"], edge.inputs[0])
    e2 = n.new("ShaderNodeMapRange")
    e2.inputs["From Min"].default_value = 0.5
    e2.inputs["From Max"].default_value = 0.2
    l.new(edge.outputs[0], e2.inputs["Value"])
    fade = n.new("ShaderNodeMapRange")
    fade.inputs["From Min"].default_value = 0.0
    fade.inputs["From Max"].default_value = 1.0
    fade.inputs["To Min"].default_value = 1.0
    fade.inputs["To Max"].default_value = 0.0
    l.new(sep.outputs["Y"], fade.inputs["Value"])
    mulA = n.new("ShaderNodeMath")
    mulA.operation = "MULTIPLY"
    l.new(nz.outputs["Fac"], mulA.inputs[0])
    l.new(fade.outputs[0], mulA.inputs[1])
    churn = n.new("ShaderNodeMath")
    churn.operation = "MAXIMUM"
    l.new(e2.outputs[0], churn.inputs[0])
    l.new(fade.outputs[0], churn.inputs[1])
    tot = n.new("ShaderNodeMath")
    tot.operation = "MULTIPLY"
    l.new(churn.outputs[0], tot.inputs[0])
    l.new(mulA.outputs[0], tot.inputs[1])
    rr = n.new("ShaderNodeMapRange")
    rr.inputs["From Min"].default_value = 0.2
    rr.inputs["From Max"].default_value = 0.55
    rr.inputs["To Max"].default_value = strength
    l.new(tot.outputs[0], rr.inputs["Value"])
    df = n.new("ShaderNodeBsdfDiffuse")
    df.inputs[0].default_value = (0.92, 0.96, 0.97, 1)
    tr = n.new("ShaderNodeBsdfTransparent")
    mx = n.new("ShaderNodeMixShader")
    l.new(rr.outputs[0], mx.inputs[0])
    l.new(tr.outputs[0], mx.inputs[1])
    l.new(df.outputs[0], mx.inputs[2])
    l.new(mx.outputs[0], n["Material Output"].inputs["Surface"])
    m.surface_render_method = "BLENDED"
    L.assign(o, m)
    o.visible_shadow = False
    return o

# ----------------------------------------------------------------------------- inverted compartment (Okene)


def inverted_compartment(w=2.4, d=2.2, h=2.4, water=1.2, nframes=120, wall_col=(0.36, 0.42, 0.38), rust=0.5,
                         water_col=(0.05, 0.28, 0.26), water_density=0.55, open_front=True, door=True, name="cmp",
                         surface_alpha=0.75, light_fitting=True, ripple_amp=0.015):
    """Small steel compartment of a capsized ship, built *upside down* in world space so an upright camera reads it
    as inverted: original deck (with toilet + floor grating) is now the overhead, original ceiling (dead lamp) is the
    bottom. Front (-Y) is open for a cutaway. Water fills z<water (volume + reflective rippled surface);
    the air pocket sits under the 'floor'. Returns dict of parts (incl. 'surface', 'volume', 'basin', 'door')."""
    P = {}
    steel = mat_paint(name + "_wall", wall_col, rough=0.55, metal=0.2, grime=0.45, rust=rust, scale=2.5)
    deckm = L.mat_noise_surface(name + "_deck", (0.08, 0.08, 0.075), (0.22, 0.21, 0.19), scale=14, bump=0.5, metal=0.5)
    whitem = mat_paint(name + "_porc", (0.78, 0.8, 0.78), rough=0.25, grime=0.3)
    pipem = mat_paint(name + "_pipe", (0.35, 0.25, 0.15), rough=0.4, metal=0.6, grime=0.3, rust=0.6)
    dark = L.mat_principled(name + "_dark", (0.015, 0.015, 0.015), rough=0.7)
    t = 0.08
    # walls
    for (loc, scl) in (((0, d / 2 + t / 2, h / 2), (w / 2 + t, t / 2, h / 2 + t)),
                       ((-w / 2 - t / 2, 0, h / 2), (t / 2, d / 2, h / 2 + t)),
                       ((w / 2 + t / 2, 0, h / 2), (t / 2, d / 2, h / 2 + t))):
        o = L.prim("cube", loc=loc, name=name + "_wall")
        o.scale = scl
        L.assign(o, steel)
    if not open_front:
        o = L.prim("cube", loc=(0, -d / 2 - t / 2, h / 2), name=name + "_front")
        o.scale = (w / 2 + t, t / 2, h / 2 + t)
        L.assign(o, steel)
    top = L.prim("cube", loc=(0, 0, h + t / 2), name=name + "_overhead_deck")
    top.scale = (w / 2 + t, d / 2 + t, t / 2)
    L.assign(top, deckm)
    bot = L.prim("cube", loc=(0, 0, -t / 2), name=name + "_old_ceiling")
    bot.scale = (w / 2 + t, d / 2 + t, t / 2)
    L.assign(bot, steel)
    # stiffener ribs on the walls (horizontal frames read as ship steel)
    for z in (h * 0.33, h * 0.66):
        for sx in (-1, 1):
            r = L.prim("cube", loc=(sx * (w / 2 - 0.03), 0, z), name=name + "_rib")
            r.scale = (0.03, d / 2, 0.04)
            L.assign(r, steel)
        r = L.prim("cube", loc=(0, d / 2 - 0.03, z), name=name + "_rib")
        r.scale = (w / 2, 0.03, 0.04)
        L.assign(r, steel)
    # floor grating strips (now overhead)
    for k in range(9):
        g = L.prim("cube", loc=(-w / 2 + (k + 0.5) * w / 9, 0, h - 0.02), name=name + "_grate")
        g.scale = (0.02, d / 2 * 0.95, 0.025)
        L.assign(g, deckm)
    # toilet bowl hanging from the overhead, right-back corner
    tb = L.prim("cyl", loc=(w / 2 - 0.4, d / 2 - 0.45, h - 0.22), vertices=20, radius=0.22, depth=0.42, name=name + "_toilet")
    tb.scale = (1.0, 1.25, 1.0)
    L.bevel(tb, 0.05)
    L.assign(tb, whitem)
    cis = L.prim("cube", loc=(w / 2 - 0.4, d / 2 - 0.1, h - 0.55), name=name + "_cistern")
    cis.scale = (0.22, 0.1, 0.22)
    L.bevel(cis, 0.03)
    L.assign(cis, whitem)
    P["toilet"] = tb
    # wash basin upside down on back wall (bowl opens downward), near the top: hand-hold for the figure
    bz = h - 0.75
    basin = L.prim("sphere", loc=(-0.55, d / 2 - 0.25, bz), segments=20, ring_count=10, radius=0.28, name=name + "_basin")
    basin.scale = (1.2, 0.85, 0.5)
    L.smooth(basin)
    L.assign(basin, whitem)
    P["basin"] = basin
    tap = L.prim("cyl", loc=(-0.55, d / 2 - 0.05, bz - 0.2), vertices=10, radius=0.025, depth=0.25,
                 rot=(math.pi / 2, 0, 0), name=name + "_tap")
    L.assign(tap, L.mat_principled(name + "_chrome", (0.7, 0.7, 0.72), rough=0.15, metal=1.0))
    mirror = L.prim("cube", loc=(-0.55, d / 2 - 0.01, bz - 0.75), name=name + "_mirror")
    mirror.scale = (0.32, 0.01, 0.25)
    L.assign(mirror, L.mat_principled(name + "_mirm", (0.6, 0.65, 0.65), rough=0.05, metal=1.0))
    # pipes along the back wall under the overhead
    for k, (z, r) in enumerate(((h - 0.15, 0.045), (h - 0.28, 0.03))):
        pp = L.prim("cyl", loc=(0, d / 2 - 0.08 - k * 0.07, z), vertices=12, radius=r, depth=w, rot=(0, math.pi / 2, 0),
                    name=name + "_pipe")
        L.assign(pp, pipem)
    vp = L.prim("cyl", loc=(w / 2 - 0.12, d / 2 - 0.12, h / 2), vertices=12, radius=0.04, depth=h, name=name + "_vpipe")
    L.assign(vp, pipem)
    # door on left wall: opening runs up to the overhead (frame inverted), door shut
    if door:
        dz0 = h - 2.0 if h > 2.0 else 0.2
        fr = L.prim("cube", loc=(-w / 2 + 0.01, -0.05, (dz0 + h) / 2), name=name + "_doorframe")
        fr.scale = (0.03, 0.5, (h - dz0) / 2)
        L.assign(fr, mat_paint(name + "_frm", (0.2, 0.22, 0.2), rough=0.5, grime=0.5, rust=0.6))
        dr = L.prim("cube", loc=(-w / 2 + 0.04, -0.05, (dz0 + h) / 2 + 0.03), name=name + "_door")
        dr.scale = (0.025, 0.42, (h - dz0) / 2 - 0.06)
        L.assign(dr, mat_paint(name + "_doorm", (0.5, 0.5, 0.45), rough=0.5, grime=0.4, rust=0.5))
        hd = L.prim("cube", loc=(-w / 2 + 0.08, 0.25, dz0 + 0.95), name=name + "_handle")
        hd.scale = (0.03, 0.1, 0.02)
        L.assign(hd, dark)
        P["door"] = dr
    if light_fitting:
        lf = L.prim("cube", loc=(0, 0, 0.05), name=name + "_deadlamp")
        lf.scale = (0.35, 0.12, 0.04)
        L.assign(lf, L.mat_principled(name + "_lampglass", (0.5, 0.55, 0.5), rough=0.2))
    # water volume + surface
    vol = L.water_volume(center=(0, 0, water / 2 - 0.05), size=(w + 0.02, d + 0.02, water + 0.1), color=water_col,
                         density=water_density, anisotropy=0.6, absorption=(0.02, 0.12, 0.12), name=name + "_water")
    P["volume"] = vol
    sm = mat_water_surface(name + "_surfm", color=(0.01, 0.04, 0.045), rough=0.03, alpha=surface_alpha,
                           under_color=(0.25, 0.55, 0.5), under_strength=0.25, ripple=0.04, nframes=nframes)
    surf = wavy_plane(size=(w, d), nframes=nframes, loc=(0, 0, water), amp=ripple_amp, mat=sm, name=name + "_surface")
    P["surface"] = surf
    P["dims"] = (w, d, h, water)
    return P


def drips(points, nframes, fall=0.6, mat=None, seed=5, every=(18, 40), name="drip"):
    """Condensation drips: tiny elongated spheres falling from given xyz points to fall distance below, repeating."""
    rnd = random.Random(seed)
    m = mat or L.mat_principled(name + "_m", (0.8, 0.95, 1.0), rough=0.02, emit=(0.6, 0.8, 0.8), emit_strength=0.4)
    out = []
    for i, p in enumerate(points):
        o = L.prim("sphere", loc=p, segments=8, ring_count=6, radius=0.012, name=f"{name}{i}")
        o.scale = (1, 1, 1.8)
        L.assign(o, m)
        f = rnd.randint(1, every[0])
        while f < nframes:
            o.location = p
            o.keyframe_insert("location", frame=f)
            o.location = (p[0], p[1], p[2] - fall)
            o.keyframe_insert("location", frame=f + 8)
            o.location = p
            o.keyframe_insert("location", frame=f + 9)
            f += rnd.randint(*every)
        L.linear_fcurves(o)
        out.append(o)
    return out


def ripple_rings(center, nframes, count=3, every=20, max_r=0.5, mat=None, name="ring", start=1):
    """Expanding thin torus rings on a water surface (drip impacts / breathing)."""
    m = mat or L.mat_principled(name + "_m", (0.7, 0.85, 0.85), rough=0.05, emit=(0.5, 0.7, 0.7), emit_strength=0.5)
    out = []
    for k in range(count):
        o = L.prim("torus", loc=center, major_radius=1.0, minor_radius=0.01, name=f"{name}{k}")
        L.assign(o, m)
        f0 = start + k * every
        while f0 < nframes:
            o.scale = (0.01, 0.01, 1)
            o.keyframe_insert("scale", frame=f0)
            o.scale = (max_r, max_r, 1)
            o.keyframe_insert("scale", frame=f0 + 30)
            o.scale = (0.01, 0.01, 1)
            o.keyframe_insert("scale", frame=f0 + 31)
            f0 += every * count
        out.append(o)
    return out

# ----------------------------------------------------------------------------- characters


def hand(name="hand", color=(0.05, 0.05, 0.055), scale=1.0, glove=False, emit=None):
    """Stylised low-poly hand (palm + 4 two-joint fingers + thumb). Points along +Y, palm faces -Z.
    parts['curl'] list of finger joint empties: set rotation_euler.x positive to close the grip."""
    m = (L.mat_principled(name + "_m", color, rough=0.75 if not glove else 0.5, emit=emit, emit_strength=1.0 if emit else 0))
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root, "curl": [], "thumb": None}

    def blk(loc, scl, parent, rot=(0, 0, 0)):
        o = L.prim("cube", loc=loc, rot=rot, name=name + "_seg")
        o.scale = scl
        L.bevel(o, 0.012, 2)
        L.assign(o, m)
        o.parent = parent
        return o

    blk((0, 0.0, 0), (0.045, 0.05, 0.015), root)
    # wrist / forearm
    fa = L.prim("cyl", loc=(0, -0.2, 0), vertices=12, radius=0.035 if not glove else 0.05, depth=0.32, rot=(math.pi / 2, 0, 0),
                name=name + "_forearm")
    L.assign(fa, m)
    L.smooth(fa)
    fa.parent = root
    P["forearm"] = fa
    for i, (x, ln) in enumerate(((-0.032, 0.035), (-0.011, 0.042), (0.011, 0.04), (0.032, 0.032))):
        j1 = L.link(bpy.data.objects.new(f"{name}_k{i}", None))
        j1.parent = root
        j1.location = (x, 0.05, 0)
        blk((0, ln / 2, 0), (0.0095, ln / 2, 0.011), j1)
        j2 = L.link(bpy.data.objects.new(f"{name}_m{i}", None))
        j2.parent = j1
        j2.location = (0, ln, 0)
        blk((0, ln * 0.4, 0), (0.0088, ln * 0.4, 0.010), j2)
        P["curl"] += [j1, j2]
    th = L.link(bpy.data.objects.new(f"{name}_thumb", None))
    th.parent = root
    th.location = (-0.045, -0.01, -0.005)
    th.rotation_euler = (0, 0, 0.7)
    blk((0, 0.025, 0), (0.011, 0.028, 0.011), th)
    P["thumb"] = th
    root.scale = (scale,) * 3
    return P


def curl(P, frame, amount):
    for k, j in enumerate(P["curl"]):
        j.rotation_euler = (-amount * (1.1 if k % 2 else 0.9), 0, 0)
        j.keyframe_insert("rotation_euler", frame=frame)
    th = P["thumb"]
    th.rotation_euler = (-amount * 0.4, amount * 0.6, 0.7 - amount * 0.5)
    th.keyframe_insert("rotation_euler", frame=frame)


def rescue_diver(name="rdiver", helmet=(0.95, 0.75, 0.05), suit=(0.04, 0.04, 0.05), light_energy=1200, umbilical=True,
                 scale=1.0):
    """Commercial/saturation diver: L.char_diver (single tank) + rounded hard-hat helmet with dark faceplate, side
    lamps, and a trailing umbilical. Faceless. Returns parts (root faces +Y, torch spot in parts['torch'])."""
    P = L.char_diver(name=name, suit=suit, accent=helmet, tanks="single", light_energy=light_energy, scale=1.0)
    root = P["root"]
    hm = L.mat_principled(name + "_helm", helmet, rough=0.3, metal=0.1)
    glass = L.mat_principled(name + "_visor", (0.02, 0.025, 0.03), rough=0.02, metal=0.5)
    for k in ("head", "mask", "maskframe"):
        if k in P:
            P[k].hide_render = True
    hel = L.prim("sphere", loc=(0, 0.6, 0.08), segments=20, ring_count=12, radius=0.19, name=name + "_helmet")
    hel.scale = (1.0, 1.1, 1.0)
    L.smooth(hel)
    L.assign(hel, hm)
    hel.parent = root
    vz = L.prim("sphere", loc=(0, 0.74, 0.07), segments=16, ring_count=8, radius=0.1, name=name + "_visor")
    vz.scale = (1.1, 0.6, 0.8)
    L.smooth(vz)
    L.assign(vz, glass)
    vz.parent = root
    P["helmet"] = hel
    if umbilical:
        cu = bpy.data.curves.new(name + "_umb", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = 0.025
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(2)
        for i, (p) in enumerate(((0, 0.45, 0.25), (0.3, -0.6, 0.9), (0.5, -2.5, 3.5))):
            bp = sp.bezier_points[i]
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = "AUTO"
        uo = L.link(bpy.data.objects.new(name + "_umbilical", cu))
        uo.data.materials.append(L.mat_principled(name + "_umbm", (0.75, 0.6, 0.1), rough=0.6))
        uo.parent = root
        P["umbilical"] = uo
    root.scale = (scale,) * 3
    return P


def swimmer(name="swimmer", suit=(0.03, 0.03, 0.035), bcd=(0.05, 0.15, 0.35), mask_col=(0.1, 0.1, 0.12), seed=1,
            tank=True):
    """Diver floating upright at the surface, seen from behind/side: hooded head, shoulders, inflated BCD collar,
    mask pushed up on the forehead, tank valve + regulator hose. Faceless. Origin at the waterline (z=0).
    Returns parts; root faces +Y."""
    m = L.mat_principled(name + "_suit", suit, rough=0.55)
    bm_ = L.mat_principled(name + "_bcd", bcd, rough=0.45)
    mk = L.mat_principled(name + "_mask", mask_col, rough=0.3)
    gl = L.mat_principled(name + "_lens", (0.3, 0.4, 0.45), rough=0.02, metal=0.6)
    met = L.mat_principled(name + "_metal", (0.7, 0.72, 0.75), rough=0.25, metal=1.0)
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root}

    def part(kind, loc, scl, mat, rot=(0, 0, 0), pn="p", **kw):
        o = L.prim(kind, loc=loc, rot=rot, name=f"{name}_{pn}", **kw)
        o.scale = scl
        L.assign(o, mat)
        L.smooth(o)
        o.parent = root
        P[pn] = o
        return o

    part("sphere", (0, 0, 0.28), (0.11, 0.12, 0.135), m, pn="head", segments=20, ring_count=12)
    part("cyl", (0, -0.01, 0.13), (0.065, 0.065, 0.08), m, pn="neck", vertices=12)
    part("sphere", (0, -0.02, -0.08), (0.24, 0.14, 0.16), m, pn="shoulders", segments=20, ring_count=10)
    part("torus", (0, -0.01, 0.06), (0.17, 0.15, 0.1), bm_, pn="bcdcollar", major_radius=1.0, minor_radius=0.45)
    for sx in (-1, 1):
        part("sphere", (sx * 0.17, 0.05, -0.12), (0.09, 0.1, 0.17), bm_, pn=f"bcd{sx}", segments=12, ring_count=8)
    # mask pushed up on forehead, strap around head
    part("cube", (0, 0.095, 0.37), (0.085, 0.03, 0.04), mk, rot=(-0.5, 0, 0), pn="mask")
    part("cube", (0, 0.115, 0.37), (0.07, 0.01, 0.03), gl, rot=(-0.5, 0, 0), pn="masklens")
    part("torus", (0, 0, 0.35), (0.12, 0.13, 0.12), mk, rot=(0.25, 0, 0), pn="strap", major_radius=1.0, minor_radius=0.06)
    if tank:
        part("cyl", (0, -0.2, -0.15), (0.09, 0.09, 0.3), met, pn="tank", vertices=16)
        part("cyl", (0, -0.2, 0.2), (0.03, 0.03, 0.06), met, pn="valve", vertices=8)
    # arms sculling just below the surface
    for sx, tag in ((-1, "L"), (1, "R")):
        sh = L.link(bpy.data.objects.new(f"{name}_sh{tag}", None))
        sh.parent = root
        sh.location = (sx * 0.22, 0, -0.08)
        P[f"sh{tag}"] = sh
        a = L.prim("cyl", loc=(sx * 0.12, 0.05, -0.12), vertices=10, name=f"{name}_arm{tag}")
        a.scale = (0.045, 0.045, 0.18)
        a.rotation_euler = (0.6, sx * -0.9, 0)
        L.assign(a, m)
        a.parent = sh
    return P


def bob(obj, nframes, amp=0.12, rate=0.35, phase=0.0, tilt=0.06, base=None, step=2):
    """Surface bob: z oscillation + small roll/pitch."""
    base = Vector(base if base is not None else obj.location)
    fps = 24
    for f in range(1, nframes + 1, step):
        t = f / fps
        ph = 2 * math.pi * rate * t + phase
        obj.location = (base.x, base.y, base.z + amp * math.sin(ph))
        obj.rotation_euler = (tilt * math.sin(ph * 0.7 + 1), tilt * math.sin(ph * 1.1), obj.rotation_euler.z)
        obj.keyframe_insert("location", frame=f)
        obj.keyframe_insert("rotation_euler", frame=f)

# ----------------------------------------------------------------------------- props


def decompression_chamber(loc=(0, 0, 0), length=3.2, radius=0.85, name="chamber"):
    """White cylindrical decompression chamber on saddles: domed ends, porthole (warm glow), hatch with wheel."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    white = mat_paint(name + "_w", (0.85, 0.86, 0.84), rough=0.35, grime=0.25, scale=2)
    dark = L.mat_principled(name + "_d", (0.05, 0.05, 0.06), rough=0.5, metal=0.6)
    glow = L.mat_emission(name + "_glow", (1.0, 0.65, 0.3), 12)
    body = L.prim("cyl", loc=(0, 0, radius + 0.35), vertices=40, radius=radius, depth=length, rot=(0, math.pi / 2, 0),
                  name=name + "_body")
    L.assign(body, white)
    L.smooth(body)
    body.parent = root
    for sx in (-1, 1):
        dm = L.prim("sphere", loc=(sx * length / 2, 0, radius + 0.35), segments=32, ring_count=16, radius=radius,
                    name=name + "_dome")
        dm.scale = (0.45, 1, 1)
        L.assign(dm, white)
        L.smooth(dm)
        dm.parent = root
        sd = L.prim("cube", loc=(sx * length * 0.3, 0, 0.25), name=name + "_saddle")
        sd.scale = (0.12, radius * 0.8, 0.25)
        L.assign(sd, dark)
        sd.parent = root
        for k in range(2):
            rib = L.prim("torus", loc=(sx * length * (0.15 + 0.2 * k), 0, radius + 0.35), major_radius=radius + 0.02,
                         minor_radius=0.03, rot=(0, math.pi / 2, 0), name=name + "_rib")
            L.assign(rib, white)
            rib.parent = root
    # porthole on the camera side (-Y)
    pr = L.prim("torus", loc=(0.2, -radius - 0.02, radius + 0.55), major_radius=0.17, minor_radius=0.04,
                rot=(math.pi / 2, 0, 0), name=name + "_portring")
    L.assign(pr, dark)
    pr.parent = root
    pg = L.prim("cyl", loc=(0.2, -radius + 0.02, radius + 0.55), vertices=24, radius=0.16, depth=0.08,
                rot=(math.pi / 2, 0, 0), name=name + "_portglass")
    L.assign(pg, glow)
    pg.parent = root
    # end hatch with wheel (+X end)
    hx = length / 2 + radius * 0.45
    ht = L.prim("cyl", loc=(hx - 0.02, 0, radius + 0.35), vertices=24, radius=0.5, depth=0.1, rot=(0, math.pi / 2, 0),
                name=name + "_hatch")
    L.assign(ht, white)
    ht.parent = root
    wh = L.prim("torus", loc=(hx + 0.1, 0, radius + 0.35), major_radius=0.22, minor_radius=0.025,
                rot=(0, math.pi / 2, 0), name=name + "_wheel")
    L.assign(wh, dark)
    wh.parent = root
    for k in range(3):
        sp = L.prim("cube", loc=(hx + 0.1, 0, radius + 0.35), name=name + "_spoke")
        sp.scale = (0.015, 0.22, 0.015)
        sp.rotation_euler = (k * math.pi / 3, 0, 0)
        L.assign(sp, dark)
        sp.parent = root
    pl = L.point((0.2, -radius - 0.4, radius + 0.55), energy=25, color=(1.0, 0.6, 0.3), radius=0.2, name=name + "_portlight")
    pl.parent = root
    return root


def bcd_vest(loc=(0, 0, 0), rot=(0, 0, 0), color=(0.05, 0.12, 0.3), name="bcd"):
    """Buoyancy vest prop lying flat-ish: two inflated bladders, back plate, tank strap + buckle, hose."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = rot
    m = L.mat_principled(name + "_m", color, rough=0.5)
    blk = L.mat_principled(name + "_k", (0.02, 0.02, 0.02), rough=0.7)
    met = L.mat_principled(name + "_met", (0.7, 0.7, 0.72), rough=0.25, metal=1.0)
    for sx in (-1, 1):
        o = L.prim("sphere", loc=(sx * 0.2, 0, 0.08), segments=16, ring_count=10, radius=0.3, name=name + "_bl")
        o.scale = (0.7, 1.1, 0.3)
        L.add_displace(o, strength=0.03, scale=0.1, name=name + f"_bd{sx}")
        L.smooth(o)
        L.assign(o, m)
        o.parent = root
    bp = L.prim("cube", loc=(0, 0, 0.03), name=name + "_back")
    bp.scale = (0.2, 0.3, 0.03)
    L.assign(bp, blk)
    bp.parent = root
    st = L.prim("cube", loc=(0, -0.05, 0.1), name=name + "_strap")
    st.scale = (0.45, 0.04, 0.01)
    L.assign(st, blk)
    st.parent = root
    bk = L.prim("cube", loc=(0.3, -0.05, 0.11), name=name + "_buckle")
    bk.scale = (0.05, 0.05, 0.015)
    L.assign(bk, met)
    bk.parent = root
    cu = bpy.data.curves.new(name + "_hose", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.015
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(2)
    for i, p in enumerate(((-0.25, 0.3, 0.12), (-0.45, 0.6, 0.05), (-0.3, 0.85, 0.03))):
        sp.bezier_points[i].co = p
        sp.bezier_points[i].handle_left_type = sp.bezier_points[i].handle_right_type = "AUTO"
    h = L.link(bpy.data.objects.new(name + "_hose", cu))
    h.data.materials.append(blk)
    h.parent = root
    return root


def wetsuit(loc=(0, 0, 0), rot=(0, 0, 0), name="wetsuit"):
    """Empty crumpled wetsuit lying on sand (flattened tubes, no body)."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = rot
    m = L.mat_principled(name + "_m", (0.025, 0.025, 0.03), rough=0.6)
    segs = [((0, 0, 0.04), (0.2, 0.32, 0.04), (0, 0, 0.1)), ((0.08, -0.55, 0.035), (0.07, 0.35, 0.035), (0, 0, 0.15)),
            ((-0.1, -0.52, 0.035), (0.07, 0.33, 0.035), (0, 0, -0.3)), ((0.3, 0.2, 0.03), (0.05, 0.25, 0.03), (0, 0, -1.0)),
            ((-0.3, 0.25, 0.03), (0.05, 0.25, 0.03), (0, 0, 1.3))]
    for loc_, scl, r in segs:
        o = L.prim("sphere", loc=loc_, rot=r, segments=12, ring_count=8, name=name + "_seg")
        o.scale = scl
        L.add_displace(o, strength=0.02, scale=0.05, name=name + "_d")
        L.smooth(o)
        L.assign(o, m)
        o.parent = root
    return root


def seaweed_clump(loc, count=12, seed=1, color=(0.12, 0.14, 0.04), name="weed"):
    rnd = random.Random(seed)
    m = L.mat_principled(name + "_m", color, rough=0.6)
    out = []
    for i in range(count):
        o = L.prim("cube", loc=(loc[0] + rnd.uniform(-0.4, 0.4), loc[1] + rnd.uniform(-0.4, 0.4), loc[2] + 0.01),
                   rot=(0, 0, rnd.uniform(0, 3.14)), name=name)
        o.scale = (0.02, rnd.uniform(0.15, 0.4), 0.005)
        L.assign(o, m)
        out.append(o)
    return out


def dive_slate(loc=(0, 0, 0), rot=(0, 0, 0), name="slate"):
    """White plastic dive slate with pencil on a cord; 'writing' is illegible scribble strokes."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = rot
    wm = L.mat_principled(name + "_w", (0.85, 0.86, 0.83), rough=0.4)
    o = L.prim("cube", loc=(0, 0, 0.006), name=name + "_board")
    o.scale = (0.11, 0.15, 0.006)
    L.bevel(o, 0.01)
    L.assign(o, wm)
    o.parent = root
    ink = L.mat_principled(name + "_ink", (0.15, 0.15, 0.17), rough=0.8)
    rnd = random.Random(4)
    for k in range(6):
        cu = bpy.data.curves.new(name + f"_s{k}", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = 0.0018
        sp = cu.splines.new("POLY")
        npt = 14
        sp.points.add(npt - 1)
        y = 0.1 - k * 0.035
        for i in range(npt):
            sp.points[i].co = (-0.085 + i * 0.012 + rnd.uniform(-0.002, 0.002), y + rnd.uniform(-0.008, 0.008), 0.0135, 1)
        so = L.link(bpy.data.objects.new(name + f"_s{k}", cu))
        so.data.materials.append(ink)
        so.parent = root
    pen = L.prim("cyl", loc=(0.15, -0.05, 0.01), vertices=6, radius=0.006, depth=0.12, rot=(math.pi / 2, 0, 0.3),
                 name=name + "_pencil")
    L.assign(pen, L.mat_principled(name + "_pm", (0.8, 0.6, 0.1), rough=0.5))
    pen.parent = root
    cu = bpy.data.curves.new(name + "_cord", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.002
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(1)
    sp.bezier_points[0].co = (0.08, 0.13, 0.013)
    sp.bezier_points[1].co = (0.15, 0.01, 0.01)
    for bp in sp.bezier_points:
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    co = L.link(bpy.data.objects.new(name + "_cord", cu))
    co.data.materials.append(ink)
    co.parent = root
    return root


def god_rays(center=(0, 0, 10), count=7, length=18, spread=6, tilt=(0.25, 0.1), color=(0.7, 0.95, 1.0), strength=1.2,
             alpha=0.25, seed=3, nframes=0, name="ray"):
    """Fake underwater light shafts: thin fading emissive cones pointing down from the surface, slowly swaying."""
    rnd = random.Random(seed)
    out = []
    for i in range(count):
        o = beam_cone((center[0] + rnd.uniform(-spread, spread), center[1] + rnd.uniform(-spread, spread), center[2]),
                      (tilt[0] + rnd.uniform(-0.05, 0.05), tilt[1] + rnd.uniform(-0.05, 0.05), -1),
                      length=length * rnd.uniform(0.7, 1.1), radius=rnd.uniform(0.3, 1.0), color=color,
                      strength=strength, alpha=alpha * rnd.uniform(0.5, 1.0), name=f"{name}{i}")
        # inverted cone: wide at the surface -> we want wide at bottom fading; beam_cone apex at origin is fine
        if nframes:
            r0 = o.rotation_euler.copy()
            o.keyframe_insert("rotation_euler", frame=1)
            o.rotation_euler = (r0.x + rnd.uniform(-0.04, 0.04), r0.y + rnd.uniform(-0.04, 0.04), r0.z)
            o.keyframe_insert("rotation_euler", frame=nframes)
        out.append(o)
    return out


def scanlines(cam, lens=18, dist=0.12, strength=0.35, tint=(0.0, 0.0, 0.0), name="scan"):
    """Monitor look in-scene: camera-parented transparent plane with dark scanlines + vignette."""
    hh = dist * 18 / lens * 1.08
    o = L.prim("plane", loc=(0, 0, -dist), size=2, name=name)
    o.scale = (hh * 9 / 16, hh, 1)
    o.parent = cam
    m, n, l = _m(name + "_m")
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["UV"], sep.inputs[0])
    wv = n.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "Y"
    wv.inputs["Scale"].default_value = 90
    l.new(tc.outputs["UV"], wv.inputs["Vector"])
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.3
    mr.inputs["From Max"].default_value = 0.9
    l.new(wv.outputs["Fac"], mr.inputs["Value"])
    # vignette: distance from centre
    vm = n.new("ShaderNodeVectorMath")
    vm.operation = "DISTANCE"
    vm.inputs[1].default_value = (0.5, 0.5, 0)
    l.new(tc.outputs["UV"], vm.inputs[0])
    vg = n.new("ShaderNodeMapRange")
    vg.inputs["From Min"].default_value = 0.35
    vg.inputs["From Max"].default_value = 0.75
    l.new(vm.outputs["Value"], vg.inputs["Value"])
    mx = n.new("ShaderNodeMath")
    mx.operation = "MULTIPLY"
    mx.inputs[1].default_value = strength
    l.new(mr.outputs[0], mx.inputs[0])
    tot = n.new("ShaderNodeMath")
    tot.operation = "MAXIMUM"
    l.new(mx.outputs[0], tot.inputs[0])
    l.new(vg.outputs[0], tot.inputs[1])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*tint, 1)
    tr = n.new("ShaderNodeBsdfTransparent")
    ms = n.new("ShaderNodeMixShader")
    l.new(tot.outputs[0], ms.inputs[0])
    l.new(tr.outputs[0], ms.inputs[1])
    l.new(em.outputs[0], ms.inputs[2])
    l.new(ms.outputs[0], n["Material Output"].inputs["Surface"])
    m.surface_render_method = "BLENDED"
    L.assign(o, m)
    o.visible_shadow = False
    return o


def flat_mat(name, color, strength=1.0):
    """Diagram fill (emission, unaffected by lights)."""
    return L.mat_emission(name, color, strength)


def draw_on_curve(points, nframes_start, nframes_end, color=(1, 0.86, 0.24), width=0.02, strength=3.0, name="drawline"):
    """Poly curve that draws on via bevel_factor_end animation (diagram measurement / arrows)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = width
    cu.bevel_resolution = 2
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (*p, 1)
    o = L.link(bpy.data.objects.new(name, cu))
    o.data.materials.append(L.mat_emission(name + "_m", color, strength))
    cu.bevel_factor_end = 0.0
    cu.keyframe_insert("bevel_factor_end", frame=nframes_start)
    cu.bevel_factor_end = 1.0
    cu.keyframe_insert("bevel_factor_end", frame=nframes_end)
    return o
