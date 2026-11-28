"""Scuba-category builders (SCUBA-01 Okene / SCUBA-02 Lonergans and future scuba shorts).

Import from shots.py:
    import sys, importlib; sys.path.insert(0, <PIPELINE/blender>); import lib_scuba as S; importlib.reload(S)
All builders are procedural, original, EEVEE-friendly. Units metres, Z up.
"""
import bpy, bmesh, math, random
from mathutils import Vector
import studio_lib as L

# ----------------------------------------------------------------------------- scene helpers


def setup(raytrace=False, vol_end=60, vol_tile="8", vol_samples=24):
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
        # crisp disc (~2-3 deg) + soft halo
        r2 = nt.nodes.new("ShaderNodeMapRange")
        r2.inputs["From Min"].default_value = 1 - sun_size * 0.08
        r2.inputs["From Max"].default_value = 1 - sun_size * 0.05
        nt.links.new(dot.outputs["Value"], r2.inputs["Value"])
        disc = nt.nodes.new("ShaderNodeMath")
        disc.operation = "MULTIPLY"
        disc.inputs[1].default_value = sun_strength
        nt.links.new(r2.outputs[0], disc.inputs[0])
        r3 = nt.nodes.new("ShaderNodeMapRange")
        r3.inputs["From Min"].default_value = 0.82
        r3.inputs["From Max"].default_value = 1.0
        nt.links.new(dot.outputs["Value"], r3.inputs["Value"])
        pw = nt.nodes.new("ShaderNodeMath")
        pw.operation = "POWER"
        pw.inputs[1].default_value = 5.0
        nt.links.new(r3.outputs[0], pw.inputs[0])
        halo = nt.nodes.new("ShaderNodeMath")
        halo.operation = "MULTIPLY"
        halo.inputs[1].default_value = 0.6
        nt.links.new(pw.outputs[0], halo.inputs[0])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "ADD"
        nt.links.new(disc.outputs[0], mul.inputs[0])
        nt.links.new(halo.outputs[0], mul.inputs[1])
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


def world_volume(color=(0.2, 0.5, 0.6), density=0.03, anisotropy=0.6, absorption=None, center=(0, 0, 0), size=(120, 120, 60)):
    """Scene-wide water/haze as a big volume *cube* (an EEVEE world volume would absorb the sun completely, since
    sun light travels an infinite distance through it). Returns the Principled Volume node (animatable)."""
    o = L.water_volume(center=center, size=size, color=color, density=density, anisotropy=anisotropy,
                       absorption=absorption, name="sceneVolume")
    o.visible_shadow = False
    return [nd for nd in o.data.materials[0].node_tree.nodes if nd.type == "PRINCIPLED_VOLUME"][0]


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
        mr.inputs["From Min"].default_value = 0.65
        mr.inputs["From Max"].default_value = 1.0
        l.new(at.outputs["Fac"], mr.inputs["Value"])
        fm = n.new("ShaderNodeMix")
        fm.data_type = "RGBA"
        l.new(mr.outputs[0], fm.inputs["Factor"])
        l.new(col, fm.inputs[6])
        fm.inputs[7].default_value = (0.85, 0.92, 0.95, 1)
        col = fm.outputs[2]
    l.new(col, p.inputs["Base Color"])
    # fine capillary ripples (glitter + texture the Ocean modifier is too coarse to give)
    tcx = n.new("ShaderNodeTexCoord")
    rn = n.new("ShaderNodeTexNoise")
    rn.inputs["Scale"].default_value = 1.6
    rn.inputs["Detail"].default_value = 6
    l.new(tcx.outputs["Object"], rn.inputs["Vector"])
    rb = n.new("ShaderNodeBump")
    rb.inputs["Strength"].default_value = 0.25
    l.new(rn.outputs["Fac"], rb.inputs["Height"])
    l.new(rb.outputs["Normal"], p.inputs["Normal"])
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
    mr.inputs["From Max"].default_value = 0.045
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
          mat=None, z=0.0, speed=1.0, loc=(0, 0, 0), repeat=1, name="ocean", alignment=0.0, t0=1.0, seed=3):
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
    oc.random_seed = seed
    if foam:
        oc.use_foam = True
        oc.foam_layer_name = "foam"
        oc.foam_coverage = 0.25
    oc.time = t0
    o.keyframe_insert('modifiers["ocean"].time', frame=1)
    oc.time = t0 + speed * (nframes - 1) / 24
    o.keyframe_insert('modifiers["ocean"].time', frame=nframes)
    L.linear_fcurves(o)
    L.smooth(o)
    L.assign(o, mat or mat_ocean())
    o.visible_shadow = False
    return o


def wavy_plane(size=10, nframes=120, loc=(0, 0, 0), amp=0.03, mat=None, sub=6, name="wavy"):
    """Small rippled water plane (inside a compartment): two Wave modifiers, kept live."""
    o = L.prim("plane", loc=loc, size=1, name=name)
    o.scale = (size[0], size[1], 1) if isinstance(size, (tuple, list)) else (size, size, 1)
    L.apply_scale(o)
    s = o.modifiers.new("sub", "SUBSURF")
    s.subdivision_type = "SIMPLE"
    s.levels = s.render_levels = sub
    # NOTE: Wave modifiers made glossy domes that mirrored the air pocket as white discs; the animated bump in the
    # surface material carries the ripples instead. A faint static swell keeps the reflection alive.
    L.add_displace(o, strength=amp, scale=0.3, name=name + "_swell")
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
            lp[uv].uv = (1.0 if lp.vert == vs[idx][0] else 0.0, idx / segs)
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
    sm = mat_water_surface(name + "_surfm", color=(0.01, 0.04, 0.045), rough=0.22, alpha=surface_alpha,
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


# ============================================================================= SCUBA-03 / SCUBA-04 additions
# (new builders only — functions above are used by SCUBA-01/02 and are left untouched)


def emit_node(mat):
    """First Emission node of a material (L.mat_emission / flat_mat) for keyframing."""
    return [nd for nd in mat.node_tree.nodes if nd.type == "EMISSION"][0]


def emit_keys(mat, pairs=(), color_pairs=(), interp=None):
    """Keyframe an emission material: pairs [(frame, strength)], color_pairs [(frame, rgb)]."""
    e = emit_node(mat)
    for f, v in pairs:
        e.inputs[1].default_value = v
        e.inputs[1].keyframe_insert("default_value", frame=f)
    for f, c in color_pairs:
        e.inputs[0].default_value = (*c, 1)
        e.inputs[0].keyframe_insert("default_value", frame=f)
    if interp:
        ad = mat.node_tree.animation_data
        if ad and ad.action:
            for fc in L._fcurves(ad.action):
                for kp in fc.keyframe_points:
                    kp.interpolation = interp
    return e


def energy_keys(light, pairs, interp=None):
    """Keyframe a light's energy: pairs [(frame, watts)]."""
    for f, v in pairs:
        light.data.energy = v
        light.data.keyframe_insert("energy", frame=f)
    if interp and light.data.animation_data and light.data.animation_data.action:
        for fc in L._fcurves(light.data.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = interp
    return light


def exposure_keys(pairs):
    """Film exposure keyframes (fades to/from black without a compositor): pairs [(frame, stops)]."""
    vs = bpy.context.scene.view_settings
    for f, v in pairs:
        vs.exposure = v
        vs.keyframe_insert("exposure", frame=f)


def shake(cam, start, length=6, amp=0.08, rot=0.03, seed=1):
    """Hard camera shake for `length` frames starting at `start` (adds to existing location keys via delta)."""
    rnd = random.Random(seed)
    cam.keyframe_insert("delta_location", frame=start - 1)
    cam.keyframe_insert("delta_rotation_euler", frame=start - 1)
    for k in range(length):
        d = 1 - k / length
        cam.delta_location = (rnd.uniform(-amp, amp) * d, rnd.uniform(-amp, amp) * d, rnd.uniform(-amp, amp) * d)
        cam.delta_rotation_euler = (rnd.uniform(-rot, rot) * d, rnd.uniform(-rot, rot) * d, rnd.uniform(-rot, rot) * d)
        cam.keyframe_insert("delta_location", frame=start + k)
        cam.keyframe_insert("delta_rotation_euler", frame=start + k)
    cam.delta_location = (0, 0, 0)
    cam.delta_rotation_euler = (0, 0, 0)
    cam.keyframe_insert("delta_location", frame=start + length)
    cam.keyframe_insert("delta_rotation_euler", frame=start + length)


def tube(points, radius=0.04, mat=None, name="tube", order=3, res=10):
    """Smooth NURBS tube through/near the control points (endpoints exact). Control points can be keyframed with
    tube_keys() (robust: no auto-handle recompute issues). Returns the curve object."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    cu.resolution_u = res
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS")
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (*p, 1)
    sp.order_u = min(order, len(points))
    sp.use_endpoint_u = True
    o = L.link(bpy.data.objects.new(name, cu))
    if mat:
        o.data.materials.append(mat)
    return o


def tube_keys(o, frame, points, interp=None):
    """Keyframe all control points of a tube() at `frame`."""
    sp = o.data.splines[0]
    for pt, p in zip(sp.points, points):
        pt.co = (*p, 1)
        pt.keyframe_insert("co", frame=frame)
    if interp and o.data.animation_data and o.data.animation_data.action:
        for fc in L._fcurves(o.data.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = interp


def umbilical(points, radius=0.045, color=(0.25, 1.0, 0.95), strength=6.0, name="umb"):
    """Glowing diver umbilical (stylised: emissive cyan tube). Returns (curve object, emission material)."""
    m = L.mat_emission(name + "_m", color, strength)
    return tube(points, radius=radius, mat=m, name=name, order=4), m


# ----------------------------------------------------------------------------- subsea manifold


def manifold(loc=(0, 0, 0), size=(6.0, 4.0, 3.0), paint=(0.72, 0.5, 0.06), grime=0.55, name="manifold", spools=True):
    """Subsea manifold / template structure: tubular steel frame (4 legs, ring beams at 3 levels, X-bracing),
    mudmats, a grated roof panel on top (where a diver kneels), internal header pipe with vertical branches, valve
    bodies with handwheels on the long side, pipe spools leaving along the seabed. Origin = seabed centre.
    Returns parts: root, top_z, corners (top corner xyz), valve (front handwheel world xyz), mats."""
    w, d, h = size
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    P = {"root": root, "top_z": loc[2] + h}
    steel = mat_paint(name + "_paint", paint, rough=0.5, metal=0.2, grime=grime, rust=0.35, scale=2.0)
    dark = mat_paint(name + "_dark", (0.12, 0.13, 0.13), rough=0.5, metal=0.5, grime=0.5, rust=0.3)
    pipe = mat_paint(name + "_pipe", (0.3, 0.32, 0.33), rough=0.35, metal=0.7, grime=0.4, rust=0.2)
    grate = L.mat_principled(name + "_grate", (0.06, 0.06, 0.06), rough=0.7, metal=0.4)
    P["mats"] = (steel, dark, pipe)

    def add(o, m):
        L.assign(o, m)
        o.parent = root
        return o

    def beam(a, b, r=0.11, m=steel, nm="beam"):
        a, b = Vector(a), Vector(b)
        c = (a + b) / 2
        o = L.prim("cyl", loc=c, vertices=10, radius=r, depth=(b - a).length, name=f"{name}_{nm}")
        o.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
        return add(o, m)

    cx = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
    for (x, y) in cx:
        beam((x, y, 0.0), (x, y, h + 0.05), r=0.16, nm="leg")
        mm = L.prim("cube", loc=(x, y, 0.04), name=f"{name}_mudmat")
        mm.scale = (0.65, 0.65, 0.05)
        add(mm, dark)
    for z in (0.35, h * 0.55, h):
        for i in range(4):
            a, b = cx[i], cx[(i + 1) % 4]
            beam((a[0], a[1], z), (b[0], b[1], z), r=0.12 if z == h else 0.1)
    # X bracing on the four sides between the lower and middle ring
    for i in range(4):
        a, b = cx[i], cx[(i + 1) % 4]
        beam((a[0], a[1], 0.35), (b[0], b[1], h * 0.55), r=0.07, nm="brace")
        beam((b[0], b[1], 0.35), (a[0], a[1], h * 0.55), r=0.07, nm="brace")
    # roof: grating panel + stringers (diver kneels here)
    rf = L.prim("cube", loc=(0, 0, h + 0.06), name=f"{name}_roof")
    rf.scale = (w / 2 - 0.05, d / 2 - 0.05, 0.04)
    add(rf, grate)
    for k in range(-3, 4):
        s = L.prim("cube", loc=(k * w / 7.5, 0, h + 0.11), name=f"{name}_stringer")
        s.scale = (0.05, d / 2 - 0.05, 0.03)
        add(s, steel)
    # internal header pipe + branches + valve bodies with handwheels (front side, -Y)
    hd = beam((-w / 2 - 0.8, 0.2, 1.0), (w / 2 + 0.8, 0.2, 1.0), r=0.32, m=pipe, nm="header")
    for k, x in enumerate((-1.8, -0.6, 0.6, 1.8)):
        beam((x * w / 6, 0.2, 1.0), (x * w / 6, 0.2, h * 0.85), r=0.14, m=pipe, nm="branch")
        vb = L.prim("cube", loc=(x * w / 6, -0.25, h * 0.62), name=f"{name}_valve")
        vb.scale = (0.28, 0.3, 0.28)
        L.bevel(vb, 0.05)
        add(vb, dark)
        st = beam((x * w / 6, -0.5, h * 0.62), (x * w / 6, -d / 2 + 0.05, h * 0.62), r=0.04, m=pipe, nm="stem")
        hw = L.prim("torus", loc=(x * w / 6, -d / 2 - 0.02, h * 0.62), rot=(math.pi / 2, 0, 0), major_radius=0.26,
                    minor_radius=0.03, name=f"{name}_wheel")
        add(hw, L.mat_principled(name + "_wheelm", (0.7, 0.1, 0.05), rough=0.4))
        for a in range(3):
            sp_ = L.prim("cube", loc=(x * w / 6, -d / 2 - 0.02, h * 0.62), rot=(0, a * math.pi / 3, 0), name=f"{name}_spoke")
            sp_.scale = (0.25, 0.015, 0.015)
            add(sp_, hw.data.materials[0])
        if k == 1:
            P["valve"] = Vector(loc) + Vector((x * w / 6, -d / 2 - 0.05, h * 0.62))
    # flanges on the header ends
    for sx in (-1, 1):
        fl = L.prim("cyl", loc=(sx * (w / 2 + 0.3), 0.2, 1.0), vertices=16, radius=0.45, depth=0.12,
                    rot=(0, math.pi / 2, 0), name=f"{name}_flange")
        add(fl, dark)
    if spools:
        for sx in (-1, 1):
            beam((sx * (w / 2 + 0.8), 0.2, 1.0), (sx * (w / 2 + 2.2), 0.2, 0.4), r=0.3, m=pipe, nm="spool")
            beam((sx * (w / 2 + 2.2), 0.2, 0.4), (sx * (w / 2 + 14), 1.5 * sx, 0.35), r=0.3, m=pipe, nm="spool")
    P["corners"] = [Vector(loc) + Vector((x, y, h + 0.12)) for (x, y) in cx]
    return P


def kneel(P, lean=0.15, arms="work"):
    """Pose an L.char_diver / rescue_diver rig upright and kneeling. Root origin = torso centre; place the root
    about 1.05 m above the surface it kneels on. Diver faces +Y of the root's yaw. arms: work | hang | reach."""
    r = P["root"]
    r.rotation_euler = (math.pi / 2 - lean, 0, r.rotation_euler.z)
    for tag in ("L", "R"):
        P[f"hip{tag}"].rotation_euler = (0.25 + lean, 0, 0)
        P[f"knee{tag}"].rotation_euler = (-1.65, 0, 0)
        if f"fin{tag}" in P:
            P[f"fin{tag}"].scale = (0.07, 0.12, 0.05)
    sx = {"L": -1, "R": 1}
    for tag in ("L", "R"):
        if arms == "work":
            P[f"shoulder{tag}"].rotation_euler = (-2.1, 0, sx[tag] * -0.25)
        elif arms == "hang":
            P[f"shoulder{tag}"].rotation_euler = (-2.9, 0, sx[tag] * -0.2)
        else:
            P[f"shoulder{tag}"].rotation_euler = (-1.5, 0, sx[tag] * -0.15)


def curl_pose(P):
    """Diver lying on his side, curled (knees up, arms in) — motionless."""
    r = P["root"]
    r.rotation_euler = (0.0, math.pi / 2, r.rotation_euler.z)
    for tag in ("L", "R"):
        P[f"hip{tag}"].rotation_euler = (1.2, 0, 0)
        P[f"knee{tag}"].rotation_euler = (-1.5, 0, 0)
        P[f"shoulder{tag}"].rotation_euler = (-1.6, 0, 0)


def bailout_valve(P, name="bail"):
    """Add a chunky pillar valve + handwheel + first stage on top of a char_diver single tank (bailout cylinder).
    Returns the handwheel object (glint target)."""
    tk = [o for k, o in P.items() if k.startswith("tank")][0]
    met = L.mat_principled(name + "_chrome", (0.85, 0.86, 0.88), rough=0.12, metal=1.0)
    blk = L.mat_principled(name + "_blk", (0.03, 0.03, 0.03), rough=0.4)
    root = P["root"]
    base = Vector(tk.location) + Vector((0, tk.scale.z + 0.02, 0))
    v = L.prim("cyl", loc=base, vertices=12, radius=0.035, depth=0.09, rot=(math.pi / 2, 0, 0), name=name + "_valve")
    L.assign(v, met)
    v.parent = root
    hw = L.prim("torus", loc=base + Vector((0.06, 0.02, 0)), rot=(0, math.pi / 2, 0), major_radius=0.035,
                minor_radius=0.01, name=name + "_wheel")
    L.assign(hw, blk)
    hw.parent = root
    fs = L.prim("cyl", loc=base + Vector((-0.05, 0.03, 0)), vertices=10, radius=0.03, depth=0.06,
                rot=(0, math.pi / 2, 0), name=name + "_first")
    L.assign(fs, met)
    fs.parent = root
    return v


# ----------------------------------------------------------------------------- vessels / bell


def dsv(name="dsv", length=90.0, beam=20.0, depth=10.0, draft=6.0, hull=(0.12, 0.14, 0.18), house=(0.85, 0.85, 0.82),
        floods=True, flood_energy=6000):
    """Dive support vessel (stylised, generic): lofted hull (bow +Y, waterline z=0), tall forward accommodation block
    with bridge window band (emission, animatable via parts['bridge_mat']), helideck disc over the bow, moon-pool
    dive tower midships (lattice), aft deck crane, lit cabin windows, sodium deck floods (point lights).
    Returns parts dict."""
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root, "floods": []}
    half = length / 2
    sts = []
    for i in range(25):
        t = i / 24
        y = -half + length * t
        b = beam / 2 * (0.92 + 0.08 * min(1, t / 0.06)) if t < 0.62 else beam / 2 * max(0.04, 1 - ((t - 0.62) / 0.38) ** 1.7) ** 0.55
        keel = -draft + (depth * 0.7 * ((t - 0.8) / 0.2) ** 2.2 if t > 0.8 else 0) + (1.2 * ((0.05 - t) / 0.05) if t < 0.05 else 0)
        deck = -draft + depth + 2.0 * max(0, t - 0.75) ** 1.5 * 4
        ring = [(xn * b, y, keel + (deck - keel) * zn) for (xn, zn) in SECTION[:-1]] + [(0, y, keel)]
        ring += [(-xn * b, y, keel + (deck - keel) * zn) for (xn, zn) in reversed(SECTION[:-1])]
        sts.append(ring)
    h = _loft(name + "_hull", sts)
    L.smooth(h)
    L.assign(h, mat_z_bands(name + "_hullm", [(-draft - 1, (0.3, 0.06, 0.04)), (-0.3, hull), (depth - draft - 0.8, house)],
                            rough=0.5, metal=0.2, space="Object"))
    h.parent = root
    P["hull"] = h
    dz = depth - draft  # main deck height above waterline
    P["deck_z"] = dz
    whitem = mat_paint(name + "_house", house, rough=0.45, grime=0.35)
    darkm = L.mat_principled(name + "_dk", (0.03, 0.03, 0.035), rough=0.6)
    yel = mat_paint(name + "_yel", (0.8, 0.55, 0.05), rough=0.5, grime=0.4)
    winm = L.mat_emission(name + "_cabin", (1.0, 0.78, 0.45), 4.0)
    bridgem = L.mat_emission(name + "_bridge", (0.2, 1.0, 0.45), 6.0)
    P["bridge_mat"] = bridgem

    def box(loc, scl, m, nm):
        o = L.prim("cube", loc=loc, name=f"{name}_{nm}")
        o.scale = scl
        L.assign(o, m)
        o.parent = root
        return o

    dk = box((0, -half * 0.25, dz + 0.1), (beam / 2 * 0.9, half * 0.7, 0.12), darkm, "deck")
    # accommodation block forward (y ~ +0.15L .. +0.38L), 4 tiers + bridge
    hy = half * 0.42
    box((0, hy, dz + 6), (beam / 2 * 0.86, length * 0.1, 6), whitem, "house")
    box((0, hy + 1, dz + 13.5), (beam / 2 * 0.8, length * 0.07, 1.6), whitem, "bridgedeck")
    for k in range(3):  # cabin window rows
        for sx in (-1, 1):
            box((sx * beam / 2 * 0.87, hy, dz + 2.2 + k * 3.2), (0.05, length * 0.085, 0.35), winm, "cabwin")
        box((0, hy + length * 0.1 + 0.05, dz + 2.2 + k * 3.2), (beam / 2 * 0.75, 0.05, 0.35), winm, "cabwinf")
    # bridge window band (front + sides)
    box((0, hy + 1 + length * 0.07 + 0.06, dz + 13.7), (beam / 2 * 0.75, 0.06, 0.6), bridgem, "bridgewin")
    for sx in (-1, 1):
        box((sx * (beam / 2 * 0.8 + 0.05), hy + 1, dz + 13.7), (0.06, length * 0.06, 0.6), bridgem, "bridgewins")
    # helideck over the bow
    hdk = L.prim("cyl", loc=(0, hy + length * 0.14, dz + 16.0), vertices=32, radius=beam * 0.55, depth=0.4,
                 name=name + "_helideck")
    L.assign(hdk, L.mat_principled(name + "_heli", (0.12, 0.3, 0.15), rough=0.6))
    hdk.parent = root
    ring_ = L.prim("torus", loc=(0, hy + length * 0.14, dz + 16.25), major_radius=beam * 0.36, minor_radius=0.25,
                   name=name + "_hring")
    L.assign(ring_, L.mat_principled(name + "_hringm", (0.9, 0.8, 0.2), rough=0.5))
    ring_.parent = root
    for sx in (-1, 1):  # helideck legs
        lg = L.prim("cyl", loc=(sx * beam * 0.25, hy + length * 0.17, dz + 13), vertices=8, radius=0.4, depth=6,
                    name=name + "_hleg")
        L.assign(lg, whitem)
        lg.parent = root
    # mast on the bridge roof
    ms = L.prim("cyl", loc=(0, hy, dz + 19), vertices=8, radius=0.25, depth=8, name=name + "_mast")
    L.assign(ms, whitem)
    ms.parent = root
    # moon-pool dive tower midships (lattice)
    ty = -half * 0.05
    th = 22.0
    tw = 3.2
    for sx in (-1, 1):
        for sy in (-1, 1):
            lg = L.prim("cyl", loc=(sx * tw, ty + sy * tw, dz + th / 2), vertices=8, radius=0.3, depth=th,
                        name=name + "_tleg")
            L.assign(lg, yel)
            lg.parent = root
    for z in range(3, int(th), 4):
        for (a, b) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
            pa = Vector((a[0] * tw, ty + a[1] * tw, dz + z))
            pb = Vector((b[0] * tw, ty + b[1] * tw, dz + z + 3.5))
            o = L.prim("cyl", loc=(pa + pb) / 2, vertices=6, radius=0.15, depth=(pb - pa).length, name=name + "_tbr")
            o.rotation_euler = (pb - pa).to_track_quat("Z", "Y").to_euler()
            L.assign(o, yel)
            o.parent = root
    box((0, ty, dz + th), (tw + 0.6, tw + 0.6, 0.4), yel, "ttop")
    P["tower_xy"] = (0, ty)
    # aft crane (pedestal + jib)
    pd = L.prim("cyl", loc=(beam * 0.3, -half * 0.6, dz + 3), vertices=12, radius=1.0, depth=6, name=name + "_crane")
    L.assign(pd, yel)
    pd.parent = root
    jb = box((beam * 0.3, -half * 0.45, dz + 9), (0.6, 0.6, 9), yel, "jib")
    jb.rotation_euler = (0.9, 0, 0)
    # deck floods (sodium)
    if floods:
        for k, (x, y, z) in enumerate(((beam * 0.4, ty, dz + 8), (-beam * 0.4, ty, dz + 8), (0, hy - length * 0.1, dz + 10),
                                       (0, -half * 0.7, dz + 6))):
            pl = L.point((x, y, z), energy=flood_energy, color=(1.0, 0.62, 0.28), radius=0.6, name=f"{name}_flood{k}")
            pl.parent = root
            P["floods"].append(pl)
            g = L.prim("sphere", loc=(x, y, z), segments=8, ring_count=6, radius=0.45, name=f"{name}_lamp{k}")
            L.assign(g, L.mat_emission(name + "_lampm", (1.0, 0.7, 0.35), 25))
            g.parent = root
    return P


def diving_bell(name="bell", radius=1.5, height=2.4, paint=(0.85, 0.42, 0.05), lamp_energy=300, hatch_strength=4.0):
    """Closed diving bell: squat vertical cylinder with domed top and dished bottom, external guard frame (ring +
    four legs), strapped gas bottles, two side lamps (emissive + spot lights, parts['lamps']), lift-wire eye on top,
    a bottom trunk with a warm glowing hatch disc (parts['hatch_mat'], emission). Origin at bell centre.
    Returns parts."""
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root, "lamps": []}
    pm = mat_paint(name + "_paint", paint, rough=0.45, grime=0.35, rust=0.15)
    dm = L.mat_principled(name + "_frame", (0.08, 0.08, 0.09), rough=0.5, metal=0.6)
    met = L.mat_principled(name + "_met", (0.7, 0.72, 0.75), rough=0.25, metal=1.0)

    def add(o, m):
        L.assign(o, m)
        L.smooth(o)
        o.parent = root
        return o

    add(L.prim("cyl", loc=(0, 0, 0), vertices=32, radius=radius, depth=height, name=name + "_body"), pm)
    top = add(L.prim("sphere", loc=(0, 0, height / 2), segments=32, ring_count=12, radius=radius, name=name + "_dome"), pm)
    top.scale = (1, 1, 0.45)
    bot = add(L.prim("sphere", loc=(0, 0, -height / 2), segments=32, ring_count=12, radius=radius, name=name + "_dish"), pm)
    bot.scale = (1, 1, 0.25)
    for z in (-height / 2 - 0.1, height / 2 - 0.1):
        add(L.prim("torus", loc=(0, 0, z), major_radius=radius + 0.25, minor_radius=0.08, name=name + "_ring"), dm)
    for a in range(4):
        ang = a * math.pi / 2 + math.pi / 4
        x, y = math.cos(ang) * (radius + 0.25), math.sin(ang) * (radius + 0.25)
        add(L.prim("cyl", loc=(x, y, -0.4), vertices=8, radius=0.08, depth=height + 1.4, name=name + "_leg"), dm)
    for a in range(5):  # gas bottles
        ang = math.pi * 0.85 + a * 0.22
        add(L.prim("cyl", loc=(math.cos(ang) * (radius + 0.12), math.sin(ang) * (radius + 0.12), 0), vertices=12,
                   radius=0.12, depth=height * 0.8, name=name + "_bottle"),
            L.mat_principled(name + "_bot", (0.15, 0.4, 0.25), rough=0.4))
    add(L.prim("torus", loc=(0, 0, height / 2 + radius * 0.45 + 0.15), rot=(math.pi / 2, 0, 0), major_radius=0.22,
               minor_radius=0.05, name=name + "_eye"), met)
    # viewport (porthole) glows warm
    pv = add(L.prim("cyl", loc=(0, -radius - 0.01, 0.3), vertices=16, radius=0.17, depth=0.06, rot=(math.pi / 2, 0, 0),
                    name=name + "_port"), L.mat_emission(name + "_portm", (1.0, 0.75, 0.4), 6))
    # bottom trunk + hatch glow
    add(L.prim("cyl", loc=(0, 0, -height / 2 - 0.35), vertices=24, radius=0.5, depth=0.35, name=name + "_trunk"), dm)
    hm = L.mat_emission(name + "_hatch", (1.0, 0.72, 0.35), hatch_strength)
    hz = add(L.prim("cyl", loc=(0, 0, -height / 2 - 0.53), vertices=24, radius=0.42, depth=0.02, name=name + "_hatchdisc"), hm)
    P["hatch_mat"] = hm
    P["hatch"] = hz
    P["bottom_z"] = -height / 2 - 0.55
    for sx in (-1, 1):
        lp = add(L.prim("cyl", loc=(sx * (radius + 0.3), -0.3, -0.6), vertices=10, radius=0.1, depth=0.25,
                        name=name + "_lamp"), L.mat_emission(name + "_lampm", (1.0, 0.85, 0.6), 20))
        if lamp_energy:
            sp = L.spot((sx * (radius + 0.3), -0.3, -0.75), (0, 0, 0), energy=lamp_energy, size_deg=50, blend=0.6,
                        color=(1.0, 0.82, 0.55), name=name + "_lampspot")
            sp.parent = root
            P["lamps"].append(sp)
    return P


def lift_wire(top, bottom, radius=0.03, name="wire", color=(0.25, 0.25, 0.27)):
    """Straight steel wire / cable between two points."""
    a, b = Vector(top), Vector(bottom)
    o = L.prim("cyl", loc=(a + b) / 2, vertices=6, radius=radius, depth=(b - a).length, name=name)
    o.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    L.assign(o, L.mat_principled(name + "_m", color, rough=0.4, metal=0.8))
    return o


def lobster_boat(name="lobsterboat", length=12.0, beam=4.2, hull=(0.93, 0.93, 0.9), bottom=(0.55, 0.08, 0.05),
                 trim=(0.1, 0.25, 0.5)):
    """New-England lobster boat: lofted hull with high flared bow (bow +Y, waterline z=0), forward wheelhouse with
    windows and roof, open aft deck with a hauler davit, trap stack, gunwale rail. Returns parts
    (root, deck_z, gunwale_z, stern_y)."""
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root}
    half = length / 2
    sts = []
    for i in range(21):
        t = i / 20
        y = -half + length * t
        b = beam / 2 * (0.94 if t < 0.5 else max(0.03, 1 - ((t - 0.5) / 0.5) ** 1.8) ** 0.6)
        keel = -0.9 + (1.1 * ((t - 0.75) / 0.25) ** 2 if t > 0.75 else 0)
        deck = 1.1 + 0.6 * t ** 2.2
        ring = [(xn * b, y, keel + (deck - keel) * zn) for (xn, zn) in SECTION[:-1]] + [(0, y, keel)]
        ring += [(-xn * b, y, keel + (deck - keel) * zn) for (xn, zn) in reversed(SECTION[:-1])]
        sts.append(ring)
    h = _loft(name + "_hull", sts)
    sub = h.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 1
    L.smooth(h)
    L.assign(h, mat_z_bands(name + "_hullm", [(-2, bottom), (0.05, (0.05, 0.05, 0.05)), (0.12, hull), (0.78, trim),
                                              (0.9, hull)], rough=0.35, metal=0.0))
    h.parent = root
    P["hull"] = h
    whm = L.mat_principled(name + "_white", hull, rough=0.35)
    deckm = L.mat_principled(name + "_deckm", (0.55, 0.55, 0.5), rough=0.7)
    glass = L.mat_principled(name + "_glass", (0.03, 0.05, 0.07), rough=0.05, metal=0.5)

    def box(loc, scl, m, nm, rot=(0, 0, 0)):
        o = L.prim("cube", loc=loc, rot=rot, name=f"{name}_{nm}")
        o.scale = scl
        L.assign(o, m)
        o.parent = root
        return o

    box((0, -0.8, 1.16), (beam / 2 * 0.88, half * 0.78, 0.04), deckm, "deck")
    for sx in (-1, 1):  # low bulwark / gunwale rail along the open aft deck
        box((sx * beam / 2 * 0.9, -1.6, 1.42), (0.05, half * 0.66, 0.24), whm, "bulwark")
    P["deck_z"] = 1.2
    P["gunwale_z"] = 1.66
    P["stern_y"] = -half
    # wheelhouse forward
    wy = half * 0.25
    box((0, wy, 2.1), (beam * 0.36, 1.4, 1.0), whm, "house")
    box((0, wy - 0.3, 3.18), (beam * 0.4, 1.9, 0.07), whm, "roof")
    box((0, wy + 1.42, 2.45), (beam * 0.3, 0.02, 0.4), glass, "winf")
    for sx in (-1, 1):
        box((sx * (beam * 0.36 + 0.02), wy + 0.3, 2.45), (0.02, 0.9, 0.38), glass, "wins")
    mast = L.prim("cyl", loc=(0, wy - 0.6, 4.0), vertices=8, radius=0.05, depth=1.6, name=name + "_mast")
    L.assign(mast, whm)
    mast.parent = root
    # hauler davit (starboard, just aft of house) + trap stack aft
    dv = L.prim("cyl", loc=(beam * 0.42, wy - 1.8, 2.1), vertices=8, radius=0.05, depth=1.4, name=name + "_davit")
    L.assign(dv, L.mat_principled(name + "_steel", (0.6, 0.6, 0.62), rough=0.3, metal=1))
    dv.parent = root
    for k in range(3):
        box((-beam * 0.18, -half * 0.55 + k * 0.05, 1.45 + k * 0.5), (0.6, 0.4, 0.24),
            L.mat_principled(name + "_trap", (0.15, 0.35, 0.2), rough=0.8), "trap")
    # rope coil + crate
    rc = L.prim("torus", loc=(beam * 0.2, -half * 0.7, 1.26), major_radius=0.3, minor_radius=0.06, name=name + "_coil")
    L.assign(rc, L.mat_principled(name + "_rope", (0.75, 0.6, 0.2), rough=0.9))
    rc.parent = root
    P["coil"] = rc
    return P


def lobster(loc=(0, 0, 0), rot_z=0.0, scale=1.0, name="lobster"):
    """Small red-brown lobster prop (body segments, tail fan, two claws, antennae)."""
    m = L.mat_principled(name + "_m", (0.25, 0.08, 0.04), rough=0.45)
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)

    def p(kind, l, s, r=(0, 0, 0), **kw):
        o = L.prim(kind, loc=l, rot=r, **kw)
        o.scale = s
        L.assign(o, m)
        L.smooth(o)
        o.parent = root
        return o

    p("sphere", (0, 0.05, 0.05), (0.05, 0.1, 0.045), segments=12, ring_count=8)
    for k in range(4):
        p("sphere", (0, -0.07 - k * 0.045, 0.04), (0.045 - k * 0.006, 0.03, 0.03), segments=10, ring_count=6)
    p("cube", (0, -0.27, 0.035), (0.06, 0.03, 0.006))
    for sx in (-1, 1):
        p("cyl", (sx * 0.06, 0.15, 0.05), (0.015, 0.015, 0.06), r=(math.pi / 2 - 0.3, 0, sx * 0.4), vertices=8)
        p("sphere", (sx * 0.1, 0.23, 0.05), (0.035, 0.07, 0.025), r=(0, 0, sx * 0.3), segments=10, ring_count=6)
        p("cyl", (sx * 0.03, 0.25, 0.08), (0.003, 0.003, 0.15), r=(math.pi / 2 - 0.2, 0, sx * 0.3), vertices=4)
    root.scale = (scale,) * 3
    return root


# ----------------------------------------------------------------------------- humpback whale


def _whale_body_mat(name, top=(0.05, 0.055, 0.065), belly=(0.62, 0.62, 0.6)):
    """Countershaded skin: dark back, paler underside (by normal Z), mottle + barnacle-ish speckle."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    geo = n.new("ShaderNodeNewGeometry")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(geo.outputs["Normal"], sep.inputs[0])
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.55
    mr.inputs["From Max"].default_value = -0.85
    l.new(sep.outputs["Z"], mr.inputs["Value"])
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 6
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = n.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    l.new(mr.outputs[0], mx.inputs["Factor"])
    mx.inputs[6].default_value = (*top, 1)
    mx.inputs[7].default_value = (*belly, 1)
    ov = n.new("ShaderNodeMix")
    ov.data_type = "RGBA"
    ov.blend_type = "OVERLAY"
    ov.inputs["Factor"].default_value = 0.35
    l.new(mx.outputs[2], ov.inputs[6])
    l.new(nz.outputs["Color"], ov.inputs[7])
    l.new(ov.outputs[2], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.35
    p.inputs["Specular IOR Level"].default_value = 0.6
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.15
    l.new(nz.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def _pleat_mat(name, base=(0.6, 0.6, 0.58), groove=(0.06, 0.06, 0.07), count=9.0):
    """Ventral throat pleats: pale with dark lengthwise grooves (bands across object X => stripes run along Y)."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    wv = n.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "X"
    wv.wave_profile = "SIN"
    wv.inputs["Scale"].default_value = count / 2
    wv.inputs["Distortion"].default_value = 0.6
    l.new(tc.outputs["Generated"], wv.inputs["Vector"])
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.12
    mr.inputs["From Max"].default_value = 0.3
    l.new(wv.outputs["Fac"], mr.inputs["Value"])
    mx = n.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    l.new(mr.outputs[0], mx.inputs["Factor"])
    mx.inputs[6].default_value = (*groove, 1)
    mx.inputs[7].default_value = (*base, 1)
    l.new(mx.outputs[2], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.4
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.5
    l.new(mr.outputs[0], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


_WHALE_PROF = [  # t (0 tail stock .. 1 snout): half-width, half-height, centre z  (fractions of length)
    (0.0, 0.018, 0.045, 0.0), (0.1, 0.035, 0.06, 0.005), (0.25, 0.07, 0.085, 0.01), (0.42, 0.105, 0.1, 0.01),
    (0.58, 0.11, 0.098, 0.0), (0.7, 0.1, 0.085, -0.008), (0.82, 0.078, 0.065, -0.012), (0.92, 0.05, 0.045, -0.012),
    (1.0, 0.012, 0.014, -0.01)]


def _wprof(t):
    for i in range(len(_WHALE_PROF) - 1):
        a, b = _WHALE_PROF[i], _WHALE_PROF[i + 1]
        if a[0] <= t <= b[0]:
            u = (t - a[0]) / (b[0] - a[0])
            u = u * u * (3 - 2 * u)
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return _WHALE_PROF[-1][1:]


def humpback(name="humpback", length=12.0, top=(0.05, 0.055, 0.065), belly=(0.62, 0.62, 0.6), t_hinge=0.6, seg=28,
             ring=20):
    """Stylised humpback built from primitives / lofts. Body along +Y (snout +Y), origin at body centre.
    - body loft: dark back / pale belly; the head part above the mouth line is a 'lid' whose underside is dark
      baleen (stripes), so opening the jaw reveals a dark mouth.
    - lower jaw + throat pouch: separate loft (pale, dark pleat grooves) parented to parts['jaw'] (hinge empty at the
      mouth corner; rotate X positive to open; scale Z to distend the throat).
    - long white pectoral fins on pivots (parts['pecL'/'pecR']), fluke on parts['fluke'] pivot, small dorsal hump,
      knobbly tubercles on the head and jaw tip. Returns parts."""
    Lw = length
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root, "length": Lw}
    body_m = _whale_body_mat(name + "_skin", top, belly)
    baleen = L.mat_noise_surface(name + "_baleen", (0.03, 0.025, 0.02), (0.16, 0.13, 0.1), scale=30, bump=0.3, voronoi=False)
    mouth_in = L.mat_principled(name + "_mouth", (0.12, 0.05, 0.05), rough=0.6)
    pleat = _pleat_mat(name + "_pleat", base=tuple(c * 0.95 for c in belly))
    white = L.mat_principled(name + "_fin", (0.78, 0.78, 0.76), rough=0.45)

    def zmouth(t):
        a, b, c = _wprof(t)
        u = (t - t_hinge) / (1 - t_hinge)
        return Lw * (c - b * (0.32 - 0.25 * u))

    def build(nm, t0, t1, n_st, clamp, mats):
        bm = bmesh.new()
        rings = []
        flagged = set()
        for i in range(n_st + 1):
            t = t0 + (t1 - t0) * i / n_st
            a, b, c = _wprof(t)
            zm = zmouth(t) if t >= t_hinge - 1e-6 else None
            rr = []
            for j in range(ring):
                th = 2 * math.pi * j / ring
                x, z = a * Lw * math.cos(th), c * Lw + b * Lw * math.sin(th)
                fl = False
                if clamp == "lid" and zm is not None and z < zm:
                    z, fl = zm, True
                if clamp == "jaw":
                    zz = zmouth(max(t, t_hinge))
                    if z > zz:
                        z, fl = zz, True
                    else:
                        x *= 1.02
                v = bm.verts.new((x, -Lw / 2 + Lw * t, z))
                if fl:
                    flagged.add(v)
                rr.append(v)
            rings.append(rr)
        for i in range(len(rings) - 1):
            for j in range(ring):
                f = bm.faces.new((rings[i][j], rings[i][(j + 1) % ring], rings[i + 1][(j + 1) % ring], rings[i + 1][j]))
                if all(v in flagged for v in f.verts):
                    f.material_index = 1
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        o = L.mesh_from_bm(nm, bm)
        for m in mats:
            o.data.materials.append(m)
        sub = o.modifiers.new("sub", "SUBSURF")
        sub.levels = sub.render_levels = 1
        L.smooth(o)
        return o

    body = build(name + "_body", 0.0, 1.0, seg, "lid", (body_m, baleen))
    body.parent = root
    P["body"] = body
    # lower jaw / throat pouch, hinged at the mouth corner
    a, b, c = _wprof(t_hinge)
    hinge = L.link(bpy.data.objects.new(name + "_jawpivot", None))
    hinge.parent = root
    hz = zmouth(t_hinge)
    hinge.location = (0, -Lw / 2 + Lw * (t_hinge - 0.08), hz)
    P["jaw"] = hinge
    jaw = build(name + "_jaw", t_hinge - 0.2, 1.0, int(seg * 0.5), "jaw", (pleat, mouth_in))
    jaw.parent = hinge
    jaw.location = (0, -hinge.location.y, -hz)
    P["jawmesh"] = jaw
    # pectoral fins (very long, white, knobbly leading edge)
    for sx, tag in ((-1, "L"), (1, "R")):
        pv = L.link(bpy.data.objects.new(f"{name}_pec{tag}", None))
        pv.parent = root
        a, b, c = _wprof(0.6)
        pv.location = (sx * a * Lw * 0.85, -Lw / 2 + Lw * 0.6, (c - b * 0.45) * Lw)
        pv.rotation_euler = (0.25, sx * 0.5, sx * 0.55)
        fl = L.prim("cone", loc=(sx * Lw * 0.15, 0, 0), vertices=12, radius1=Lw * 0.035, radius2=Lw * 0.008,
                    depth=Lw * 0.3, rot=(0, sx * math.pi / 2, 0), name=f"{name}_fin{tag}")
        L.assign(fl, white)
        L.smooth(fl)
        fl.parent = pv
        # flatten: squash the cone in its local X (which maps to world Z after the Y rotation)
        fl.scale = (0.3, 1.0, 1.0)
        for k in range(5):
            kb = L.prim("sphere", loc=(sx * Lw * (0.04 + 0.05 * k), Lw * 0.028 * (1 - k * 0.15), 0), segments=8, ring_count=6,
                        radius=Lw * 0.008, name=f"{name}_knob{tag}")
            L.assign(kb, white)
            kb.parent = pv
        P["pec" + tag] = pv
    # fluke
    fk = L.link(bpy.data.objects.new(name + "_flukepivot", None))
    fk.parent = root
    fk.location = (0, -Lw / 2 + 0.01 * Lw, 0.0)
    P["fluke"] = fk
    for sx in (-1, 1):
        f = L.prim("cone", loc=(sx * Lw * 0.09, -Lw * 0.05, 0), vertices=3, radius1=Lw * 0.09, radius2=0.0,
                   depth=Lw * 0.02, name=name + "_flukeblade")
        f.rotation_euler = (0, 0, sx * 0.9 + math.pi)
        f.scale = (1.0, 0.55, 1.0)
        L.assign(f, body_m)
        f.parent = fk
    # dorsal hump + tubercles
    a, b, c = _wprof(0.3)
    d_ = L.prim("cone", loc=(0, -Lw / 2 + Lw * 0.3, (c + b * 0.92) * Lw), vertices=8, radius1=Lw * 0.03, radius2=Lw * 0.004,
                depth=Lw * 0.035, rot=(-0.6, 0, 0), name=name + "_dorsal")
    L.assign(d_, body_m)
    d_.parent = root
    rnd = random.Random(5)
    for k in range(16):
        t = rnd.uniform(0.78, 0.98)
        a, b, c = _wprof(t)
        x = rnd.uniform(-0.6, 0.6) * a * Lw
        zt = (c + b * math.sqrt(max(0.0, 1 - (x / (a * Lw)) ** 2)) * 0.97) * Lw
        tb = L.prim("sphere", loc=(x, -Lw / 2 + Lw * t, zt), segments=8, ring_count=6, radius=Lw * 0.006,
                    name=name + "_tub")
        L.assign(tb, body_m)
        tb.parent = root
    for sx in (-1, 1):  # eye (small dark dome just above the mouth corner)
        a, b, c = _wprof(t_hinge + 0.03)
        ey = L.prim("sphere", loc=(sx * a * Lw * 0.98, -Lw / 2 + Lw * (t_hinge + 0.03), zmouth(t_hinge) + 0.03 * Lw),
                    segments=10, ring_count=6, radius=Lw * 0.008, name=name + "_eye")
        L.assign(ey, L.mat_principled(name + "_eyem", (0.01, 0.01, 0.01), rough=0.1))
        ey.parent = root
    return P


def whale_swim(P, nframes, rate=0.35, amp=0.18, start=1, step=2):
    """Slow fluke beat + gentle pectoral sway."""
    for f in range(start, start + nframes + 1, step):
        t = (f - start) / 24
        ph = 2 * math.pi * rate * t
        P["fluke"].rotation_euler = (amp * math.sin(ph), 0, 0)
        P["fluke"].keyframe_insert("rotation_euler", frame=f)
        for tag, sx in (("L", -1), ("R", 1)):
            pv = P["pec" + tag]
            pv.rotation_euler = (0.25 + 0.08 * math.sin(ph + 1), sx * 0.5, sx * (0.55 + 0.06 * math.sin(ph)))
            pv.keyframe_insert("rotation_euler", frame=f)


def jaw_keys(P, pairs):
    """pairs: [(frame, open_radians, throat_scale)]."""
    j = P["jaw"]
    for f, a, s in pairs:
        j.rotation_euler = (-a, 0, 0)
        j.scale = (1.0 + 0.15 * (s - 1), 1.0, s)
        j.keyframe_insert("rotation_euler", frame=f)
        j.keyframe_insert("scale", frame=f)


def bubbles_at(origin, starts, rise=1.6, spread=0.12, size=0.025, life=(28, 50), seed=3, name="bub", mat=None,
               drift=(0.0, 0.0)):
    """Bubbles released at explicit frames (bursts, rhythmic exhalations, a supply running out).
    starts: list of frames (one bubble each; repeat a frame for a burst)."""
    rnd = random.Random(seed)
    m = mat or L.mat_principled(name + "_m", (0.8, 0.95, 1.0), rough=0.05, emit=(0.55, 0.75, 0.85), emit_strength=0.5)
    out = []
    o0 = Vector(origin)
    for i, st in enumerate(starts):
        r = size * rnd.uniform(0.45, 1.4)
        o = L.prim("sphere", loc=o0, segments=8, ring_count=6, radius=r, name=f"{name}{i}")
        L.assign(o, m)
        o.visible_shadow = False
        lf = rnd.randint(*life)
        ox, oy = rnd.uniform(-spread, spread), rnd.uniform(-spread, spread)
        o.scale = (0.001,) * 3
        o.location = o0
        o.keyframe_insert("scale", frame=max(0, st - 1))
        o.keyframe_insert("location", frame=max(0, st - 1))
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=st)
        for k in range(1, 5):
            f = st + lf * k / 4
            o.location = (o0.x + ox * k + drift[0] * k + 0.03 * math.sin(k * 2.1 + i), o0.y + oy * k + drift[1] * k,
                          o0.z + rise * k / 4 * lf / 24)
            o.keyframe_insert("location", frame=f)
        o.scale = (0.001,) * 3
        o.keyframe_insert("scale", frame=st + lf)
        out.append(o)
    return out


def mat_drain(name, color=(0.25, 1.0, 0.95), strength=6.0, origin=(0, 0, 0)):
    """Emission whose glow can 'drain' outward from a point: strength * clamp((dist(P, origin) - T) / 0.4) where
    T is keyframable (returned socket). T < 0 => fully lit; T beyond the tube length => dark.
    Object must have an identity transform (object space == world space)."""
    m, n, l = _m(name)
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    tc = n.new("ShaderNodeTexCoord")
    dv = n.new("ShaderNodeVectorMath")
    dv.operation = "DISTANCE"
    dv.inputs[1].default_value = origin
    l.new(tc.outputs["Object"], dv.inputs[0])
    sub = n.new("ShaderNodeMath")
    sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = -1.0
    l.new(dv.outputs["Value"], sub.inputs[0])
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.4
    l.new(sub.outputs[0], mr.inputs["Value"])
    mul = n.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = strength
    l.new(mr.outputs[0], mul.inputs[0])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    l.new(mul.outputs[0], em.inputs[1])
    dark = n.new("ShaderNodeBsdfPrincipled")
    dark.inputs["Base Color"].default_value = (0.03, 0.05, 0.05, 1)
    dark.inputs["Roughness"].default_value = 0.5
    add = n.new("ShaderNodeAddShader")
    l.new(dark.outputs[0], add.inputs[0])
    l.new(em.outputs[0], add.inputs[1])
    l.new(add.outputs[0], n["Material Output"].inputs["Surface"])
    return m, sub.inputs[1], mul.inputs[1]


def drain_keys(sock, pairs):
    for f, v in pairs:
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=f)


def no_shadow(*lights):
    for o in lights:
        try:
            o.data.use_shadow = False
        except Exception:
            pass


# ============================================================================= SCUBA-05 / SCUBA-06 additions
# (Gabr 332 m descent line / Fox great white) — new builders only, everything above is untouched.


def tech_diver(name="tech", suit=(0.03, 0.03, 0.035), fins=(1.0, 0.78, 0.05), stages=4, light_energy=0.0,
               stage_cols=((0.9, 0.9, 0.86), (0.95, 0.75, 0.1), (0.15, 0.6, 0.3), (0.85, 0.25, 0.15))):
    """Deep tech diver: L.char_diver (dark suit + hood, sidemount twins) + yellow fins and `stages` slim stage
    cylinders clipped along each side (coloured neck bands). Root faces +Y, back +Z (trim). parts['stages'] = list."""
    P = L.char_diver(name=name, suit=suit, accent=(0.08, 0.08, 0.09), tanks="sidemount", light_on=light_energy > 0,
                     light_energy=max(light_energy, 1.0))
    fm = L.mat_principled(name + "_finm", fins, rough=0.4)
    for tag in ("L", "R"):
        L.assign(P[f"fin{tag}"], fm)
    alu = L.mat_principled(name + "_alu", (0.72, 0.74, 0.76), rough=0.3, metal=0.8)
    offs = [(0.33, 0.05), (0.37, -0.06), (0.34, -0.17), (0.27, -0.24)][:stages]
    P["stages"] = []
    for sx in (-1, 1):
        for k, (x, z) in enumerate(offs):
            t = L.prim("cyl", loc=(sx * x, -0.14 + 0.05 * k, z), rot=(math.pi / 2, 0, 0), vertices=12, radius=1, depth=2,
                       name=f"{name}_stage")
            t.scale = (0.055, 0.055, 0.27)
            L.assign(t, alu)
            L.smooth(t)
            t.parent = P["root"]
            b = L.prim("cyl", loc=(sx * x, -0.14 + 0.05 * k + 0.25, z), rot=(math.pi / 2, 0, 0), vertices=12, radius=1,
                       depth=2, name=f"{name}_stageband")
            b.scale = (0.058, 0.058, 0.04)
            L.assign(b, L.mat_principled(f"{name}_band{k}", stage_cols[k % len(stage_cols)], rough=0.4))
            b.parent = P["root"]
            P["stages"].append((t, b))
    return P


def pose_upright(P, yaw=0.0, reach=("R",), lean=0.0, legs=0.25):
    """Stand a char_diver rig upright (head +Z, faces +Y rotated by yaw). Arms in `reach` go forward/up (rope grip),
    the others hang. Knees softly bent."""
    r = P["root"]
    r.rotation_euler = (math.pi / 2 - lean, 0, yaw)
    for tag, sx in (("L", -1), ("R", 1)):
        P[f"hip{tag}"].rotation_euler = (legs, 0, 0)
        P[f"knee{tag}"].rotation_euler = (-legs * 1.6, 0, 0)
        if tag in reach:
            P[f"shoulder{tag}"].rotation_euler = (-0.55, 0, sx * -0.3)
        else:
            P[f"shoulder{tag}"].rotation_euler = (-2.7, 0, sx * -0.25)


def mat_rope(name="rope", color=(0.92, 0.92, 0.88), stripe=(0.35, 0.33, 0.3), period=0.08, emit=0.15):
    """White braided-rope look: fine diagonal bands along object Z (scrolls with the object), slight self-glow."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    wv = n.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "DIAGONAL"
    wv.inputs["Scale"].default_value = 2 * math.pi / (20 * period)
    l.new(tc.outputs["Object"], wv.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*stripe, 1)
    ramp.color_ramp.elements[1].color = (*color, 1)
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[1].position = 0.6
    l.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.8
    p.inputs["Emission Color"].default_value = (*color, 1)
    p.inputs["Emission Strength"].default_value = emit
    return m


def descent_line(top=5.0, bottom=-20.0, x=0.0, y=0.0, radius=0.012, mat=None, name="line"):
    """Vertical descent rope between z=top and z=bottom (object origin at its centre)."""
    h = top - bottom
    o = L.prim("cyl", loc=(x, y, (top + bottom) / 2), vertices=10, radius=radius, depth=h, name=name)
    L.assign(o, mat or mat_rope(name + "_m"))
    return o


def depth_tag(text, loc=(0, 0, 0), yaw=0.0, scale=1.0, name="tag", rope_r=0.012, glow=0.0):
    """Small white plastic depth tag zip-tied to a vertical rope at loc: tie ring + tag plate + printed number
    (faces -Y before yaw). Returns root empty (parent it to the rope)."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = (0, 0, yaw)
    wm = L.mat_principled(name + "_w", (0.92, 0.92, 0.9), rough=0.45, emit=(0.9, 0.95, 1.0), emit_strength=glow)
    tie = L.prim("torus", loc=(0, 0, 0), major_radius=rope_r + 0.004, minor_radius=0.003, name=name + "_tie")
    L.assign(tie, L.mat_principled(name + "_tiem", (0.1, 0.1, 0.1), rough=0.5))
    tie.parent = root
    pl = L.prim("cube", loc=(0, -rope_r - 0.004, -0.055), name=name + "_plate")
    pl.scale = (0.035, 0.003, 0.05)
    L.bevel(pl, 0.006, 2)
    L.assign(pl, wm)
    pl.parent = root
    tx = L.text3d(text, loc=(0, -rope_r - 0.0075, -0.062), size=0.026, extrude=0.0005,
                  mat=L.mat_principled(name + "_ink", (0.02, 0.02, 0.025), rough=0.6), name=name + "_txt")
    tx.data.align_y = "CENTER"
    tx.parent = root
    root.scale = (scale,) * 3
    return root


def stage_tank(loc=(0, 0, 0), rot=(0, 0, 0), band=(0.95, 0.75, 0.1), length=0.6, radius=0.06, name="stg"):
    """Loose aluminium stage cylinder with coloured neck band, valve and clip (axis = local Z, valve at +Z)."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = rot
    alu = L.mat_principled(name + "_alu", (0.75, 0.77, 0.79), rough=0.3, metal=0.8)
    body = L.prim("cyl", loc=(0, 0, 0), vertices=14, radius=radius, depth=length, name=name + "_body")
    L.assign(body, alu)
    L.smooth(body)
    body.parent = root
    b = L.prim("cyl", loc=(0, 0, length * 0.42), vertices=14, radius=radius * 1.04, depth=length * 0.12, name=name + "_band")
    L.assign(b, L.mat_principled(name + "_bandm", band, rough=0.4))
    b.parent = root
    v = L.prim("cyl", loc=(0, 0, length / 2 + 0.04), vertices=8, radius=radius * 0.35, depth=0.08, name=name + "_valve")
    L.assign(v, L.mat_principled(name + "_chrome", (0.85, 0.85, 0.88), rough=0.15, metal=1.0))
    v.parent = root
    return root


def mat_reveal_z(name, color=(0.3, 1.0, 0.9), strength=4.0, soft=0.4, alpha=1.0):
    """Emission visible only below a keyframable world-Z threshold (draw-on from the bottom up). Returns (mat, socket):
    key socket.default_value = threshold z."""
    m, n, l = _m(name)
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    geo = n.new("ShaderNodeNewGeometry")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(geo.outputs["Position"], sep.inputs[0])
    sub = n.new("ShaderNodeMath")
    sub.operation = "SUBTRACT"
    l.new(sep.outputs["Z"], sub.inputs[1])  # T - z
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = soft
    mr.inputs["To Max"].default_value = alpha
    l.new(sub.outputs[0], mr.inputs["Value"])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    tr = n.new("ShaderNodeBsdfTransparent")
    mx = n.new("ShaderNodeMixShader")
    l.new(mr.outputs[0], mx.inputs[0])
    l.new(tr.outputs[0], mx.inputs[1])
    l.new(em.outputs[0], mx.inputs[2])
    l.new(mx.outputs[0], n["Material Output"].inputs["Surface"])
    m.surface_render_method = "BLENDED"
    return m, sub.inputs[0]


def lattice_tower(base_z=0.0, height=33.0, half_base=6.25, center=(0, 0), mat=None, bevel=0.08, name="tower"):
    """Eiffel-style lattice tower as one emissive wire curve object (1 unit = 10 m by default: 330 m tall).
    Four curved legs (double rails), three platforms, cross-bracing, arches, spire. Built in world space."""
    cx, cy = center
    H = height

    def hw(t):  # half-width profile (concave legs)
        return max(0.035 * half_base, half_base * (1 - t) ** 2.6 + 0.02 * half_base)

    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = bevel
    cu.bevel_resolution = 1

    def seg(pts):
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            sp.points[i].co = (p[0] + cx, p[1] + cy, p[2] + base_z, 1)

    ts = [k / 24 for k in range(25)]
    corners = ((1, 1), (-1, 1), (-1, -1), (1, -1))
    tmax = 0.9
    for sx, sy in corners:
        for inset in (1.0, 0.82):
            seg([(sx * hw(t * tmax) * inset, sy * hw(t * tmax) * inset, t * tmax * H) for t in ts])
    # rings / platforms
    for t, w in ((0.17, 1.15), (0.35, 1.1), (0.84, 1.6)):
        r = hw(t) * w
        seg([(r, r, t * H), (-r, r, t * H), (-r, -r, t * H), (r, -r, t * H), (r, r, t * H)])
    for k in range(1, 18):
        t = k / 18 * tmax
        r = hw(t)
        seg([(r, r, t * H), (-r, r, t * H), (-r, -r, t * H), (r, -r, t * H), (r, r, t * H)])
        # X-bracing on the 4 faces between this ring and the previous
        t0 = (k - 1) / 18 * tmax
        r0 = hw(t0)
        for (ax, ay), (bx, by) in zip(corners, corners[1:] + corners[:1]):
            seg([(ax * r0, ay * r0, t0 * H), (bx * r, by * r, t * H)])
            seg([(bx * r0, by * r0, t0 * H), (ax * r, ay * r, t * H)])
    # base arches on each face
    for (ax, ay), (bx, by) in zip(corners, corners[1:] + corners[:1]):
        pts = []
        for k in range(13):
            u = k / 12
            t = 0.17 * math.sin(u * math.pi) * 0.85
            r = hw(t)
            x = (ax + (bx - ax) * u) * r
            y = (ay + (by - ay) * u) * r
            pts.append((x, y, t * H))
        seg(pts)
    # spire
    seg([(0, 0, tmax * H), (0, 0, H)])
    o = L.link(bpy.data.objects.new(name, cu))
    o.data.materials.append(mat or L.mat_emission(name + "_m", (0.3, 1.0, 0.9), 4.0))
    return o


def backdrop_z(name="backdrop", stops=((-40, (0.0, 0.004, 0.01)), (-5, (0.02, 0.25, 0.35)), (0, (0.25, 0.75, 0.8)),
                                       (0.2, (0.55, 0.7, 0.85)), (30, (0.15, 0.35, 0.65))),
               loc=(0, 30, 0), size=(200, 200), strength=1.0):
    """Big vertical emissive backdrop plane (faces -Y) coloured by world Z through colour stops [(z, rgb)]."""
    o = L.prim("plane", loc=loc, rot=(math.pi / 2, 0, 0), size=1, name=name)
    o.scale = (size[0], size[1], 1)
    m, n, l = _m(name + "_m")
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    geo = n.new("ShaderNodeNewGeometry")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(geo.outputs["Position"], sep.inputs[0])
    z0, z1 = stops[0][0], stops[-1][0]
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = z0
    mr.inputs["From Max"].default_value = z1
    l.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = n.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.0, (*stops[0][1], 1)
    els[1].position, els[1].color = 1.0, (*stops[-1][1], 1)
    for z, c in stops[1:-1]:
        e = els.new((z - z0) / (z1 - z0))
        e.color = (*c, 1)
    l.new(mr.outputs[0], ramp.inputs["Fac"])
    em = n.new("ShaderNodeEmission")
    em.inputs[1].default_value = strength
    l.new(ramp.outputs["Color"], em.inputs[0])
    l.new(em.outputs[0], n["Material Output"].inputs["Surface"])
    L.assign(o, m)
    o.visible_shadow = False
    return o


def mat_xray(name, color, strength=2.0, power=1.6, base=0.04):
    """Line-art x-ray look: silhouette edges glow (Layer Weight Facing), faces see-through."""
    m, n, l = _m(name)
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


def restyle(prefix, mat):
    """Replace the material on every mesh/curve whose name starts with prefix."""
    for o in bpy.data.objects:
        if o.name.startswith(prefix) and o.type in ("MESH", "CURVE", "FONT"):
            o.data.materials.clear()
            o.data.materials.append(mat)


def diagram_grid(y=5.5, color=(0.02, 0.1, 0.1), bg=(0.004, 0.035, 0.04), step=0.8, extent=20, name="grid"):
    """Dark teal diagram backdrop (plane facing -Y at y) with a faint square grid."""
    b = L.prim("plane", loc=(0, y + 0.5, 0), rot=(math.pi / 2, 0, 0), size=1, name=name + "_bg")
    b.scale = (extent * 3, extent * 3, 1)
    L.assign(b, flat_mat(name + "_bgm", bg, 1))
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.012 * step / 0.8
    k = int(extent / step)
    for i in range(-k, k + 1):
        for horiz in (0, 1):
            sp = cu.splines.new("POLY")
            sp.points.add(1)
            if horiz:
                sp.points[0].co, sp.points[1].co = (-extent, y, i * step, 1), (extent, y, i * step, 1)
            else:
                sp.points[0].co, sp.points[1].co = (i * step, y, -extent, 1), (i * step, y, extent, 1)
    o = L.link(bpy.data.objects.new(name, cu))
    o.data.materials.append(flat_mat(name + "_m", color, 1))
    return o


def splash_drops(center, starts, count=60, speed=4.0, seed=3, name="spl", size=0.05):
    """White droplets thrown up and falling back (small ico spheres on ballistic keys)."""
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
        o.keyframe_insert("scale", frame=max(0, st - 1))
        o.scale = (1, 1, 1)
        o.keyframe_insert("scale", frame=st)
        p0 = c + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * 0.5
        for k in range(0, 21, 4):
            t = k / 24
            o.location = p0 + v * t + Vector((0, 0, -4.9 * t * t))
            o.keyframe_insert("location", frame=st + k)
        o.scale = (0.001,) * 3
        o.keyframe_insert("scale", frame=st + 22)


def foam_patch(loc, r0=0.3, r1=2.0, f0=1, f1=40, name="foam", z=0.04):
    """Expanding white foam ring on the water surface."""
    m = L.mat_principled(name + "_m", (0.95, 0.97, 0.97), rough=0.6, emit=(0.6, 0.65, 0.65), emit_strength=0.4)
    o = L.prim("torus", loc=(loc[0], loc[1], z), major_radius=1.0, minor_radius=0.25, name=name)
    L.add_displace(o, strength=0.2, scale=0.3, name=name + "_d")
    L.assign(o, m)
    o.scale = (0.001, 0.001, 0.001)
    o.keyframe_insert("scale", frame=max(0, f0 - 1))
    o.scale = (r0, r0, 0.4)
    o.keyframe_insert("scale", frame=f0)
    o.scale = (r1, r1, 0.15)
    o.keyframe_insert("scale", frame=f1)
    return o


def paper(loc=(0, 0, 0), size=(0.21, 0.297), rot_z=0.0, color=(0.88, 0.86, 0.8), lines=10, redact=(), seed=1,
          name="paper", ink=(0.12, 0.12, 0.14)):
    """Sheet of paper lying flat (z up) with grey 'text' lines (illegible strokes); redact = list of line indexes
    that get a black redaction bar (parts['bars'] for scale-x draw-on: origin at the bar's left end)."""
    rnd = random.Random(seed)
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    P = {"root": root, "bars": []}
    pl = L.prim("cube", loc=(0, 0, 0.0008), name=name + "_sheet")
    pl.scale = (size[0] / 2, size[1] / 2, 0.0008)
    L.assign(pl, L.mat_principled(name + "_pm", color, rough=0.85))
    pl.parent = root
    lm = L.mat_principled(name + "_lm", tuple(c * 0.6 + 0.3 for c in ink), rough=0.9)
    bm = L.mat_principled(name + "_bm", (0.01, 0.01, 0.012), rough=0.6)
    x0 = -size[0] / 2 + size[0] * 0.12
    wmax = size[0] * 0.76
    for i in range(lines):
        y = size[1] / 2 - size[1] * 0.14 - i * size[1] * 0.07
        w = wmax * (rnd.uniform(0.55, 1.0) if i else 0.45)
        ln = L.prim("cube", loc=(x0 + w / 2, y, 0.0018), name=name + "_ln")
        ln.scale = (w / 2, size[1] * 0.009, 0.0002)
        L.assign(ln, lm)
        ln.parent = root
        if i in redact:
            piv = L.link(bpy.data.objects.new(name + "_barpiv", None))
            piv.parent = root
            piv.location = (x0 - 0.004, y, 0.0024)
            b = L.prim("cube", loc=(w / 2 + 0.004, 0, 0), name=name + "_bar")
            b.scale = (w / 2 + 0.006, size[1] * 0.02, 0.0004)
            L.assign(b, bm)
            b.parent = piv
            P["bars"].append(piv)
    return P


def magnifier(loc=(0, 0, 0), radius=0.07, name="loupe"):
    """Hand magnifier lying above a desk: chrome ring, faintly tinted glass disc, black handle (+X)."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    ring = L.prim("torus", loc=(0, 0, 0), major_radius=radius, minor_radius=radius * 0.09, name=name + "_ring")
    L.assign(ring, L.mat_principled(name + "_chrome", (0.85, 0.85, 0.88), rough=0.15, metal=1.0))
    ring.parent = root
    gl = L.prim("cyl", loc=(0, 0, 0), vertices=32, radius=radius, depth=radius * 0.04, name=name + "_glass")
    gm = L.mat_principled(name + "_gm", (0.75, 0.9, 1.0), rough=0.05, alpha=0.18)
    gm.surface_render_method = "BLENDED"
    L.assign(gl, gm)
    gl.parent = root
    h = L.prim("cyl", loc=(radius * 2.2, 0, 0), rot=(0, math.pi / 2, 0), vertices=12, radius=radius * 0.16,
               depth=radius * 2.2, name=name + "_handle")
    L.assign(h, L.mat_principled(name + "_hm", (0.03, 0.03, 0.03), rough=0.5))
    h.parent = root
    return root


def rubber_stamp(loc=(0, 0, 0), size=0.12, name="stamp", wood=(0.35, 0.2, 0.1)):
    """Office rubber stamp: red rubber pad, wooden block and round knob handle. Origin at the pad face."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    pad = L.prim("cube", loc=(0, 0, 0.006), name=name + "_pad")
    pad.scale = (size / 2, size * 0.3, 0.006)
    L.assign(pad, L.mat_principled(name + "_rub", (0.5, 0.05, 0.04), rough=0.7))
    pad.parent = root
    blk = L.prim("cube", loc=(0, 0, 0.03), name=name + "_block")
    blk.scale = (size / 2 * 1.05, size * 0.32, 0.018)
    L.bevel(blk, 0.004, 2)
    wm = L.mat_principled(name + "_wood", wood, rough=0.5)
    L.assign(blk, wm)
    blk.parent = root
    st = L.prim("cyl", loc=(0, 0, 0.09), vertices=16, radius=size * 0.09, depth=0.09, name=name + "_stem")
    L.assign(st, wm)
    st.parent = root
    kn = L.prim("sphere", loc=(0, 0, 0.15), segments=16, ring_count=10, radius=size * 0.2, name=name + "_knob")
    kn.scale = (1, 1, 0.8)
    L.assign(kn, L.mat_principled(name + "_knobm", (0.05, 0.05, 0.06), rough=0.3))
    kn.parent = root
    return root


def submarine_outline(length=4.0, name="subline", color=(0.75, 0.95, 1.0), width=0.02, f0=1, f1=12):
    """2.5D line-art submarine silhouette in the local XY plane (draws on f0..f1). Returns root empty + material."""
    root = L.link(bpy.data.objects.new(name, None))
    h = length * 0.11
    hull = []
    for k in range(41):
        a = k / 40 * 2 * math.pi
        x = math.cos(a) * length / 2
        y = math.sin(a) * h * (1.0 if math.cos(a) > -0.3 else 0.75)
        hull.append((x * (1.0 if x > 0 else 1.05), y, 0))
    tower = [(-0.02 * length, h * 0.95, 0), (0.0, h * 2.0, 0), (0.17 * length, h * 2.0, 0), (0.2 * length, h * 0.95, 0)]
    fin = [(-0.47 * length, 0, 0), (-0.58 * length, h * 1.3, 0), (-0.56 * length, 0, 0), (-0.58 * length, -h * 1.3, 0),
           (-0.47 * length, 0, 0)]
    objs = []
    m = None
    for i, pts in enumerate((hull, tower, fin)):
        o = draw_on_curve(pts, f0, f1, color=color, width=width, strength=3.0, name=f"{name}{i}")
        if m is None:
            m = o.data.materials[0]
        else:
            o.data.materials.clear()
            o.data.materials.append(m)
        o.parent = root
        objs.append(o)
    for k in range(4):
        c = L.prim("torus", loc=(-0.25 * length + k * 0.14 * length, 0, 0), major_radius=h * 0.25, minor_radius=width,
                   name=f"{name}_port")
        L.assign(c, m)
        c.parent = root
        for f, s in ((f1 - 2, 0.001), (f1, 1.0)):
            c.scale = (s,) * 3
            c.keyframe_insert("scale", frame=f)
    return root, m


# ----------------------------------------------------------------------------- SCUBA-06 (Fox) additions


def _gw_r(t):
    """Great-white half-width profile, t = 0 tail .. 1 snout (fraction of length)."""
    pts = ((0.0, 0.018), (0.1, 0.03), (0.2, 0.055), (0.35, 0.095), (0.5, 0.122), (0.62, 0.13), (0.75, 0.124),
           (0.85, 0.106), (0.93, 0.078), (0.98, 0.042), (1.0, 0.01))
    for (a, ra), (b, rb) in zip(pts, pts[1:]):
        if a <= t <= b:
            u = (t - a) / (b - a)
            u = u * u * (3 - 2 * u)
            return ra + (rb - ra) * u
    return pts[-1][1]


def _fin_mesh(name, pts, thick, mat, parent):
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    bm.faces.new(vs)
    o = L.mesh_from_bm(name, bm)
    so = o.modifiers.new("sol", "SOLIDIFY")
    so.thickness = thick
    so.offset = 0
    L.assign(o, mat)
    o.parent = parent
    return o


def great_white(name="gw", length=4.5, top=(0.24, 0.27, 0.3), belly=(0.86, 0.86, 0.84), seg=22, ring=16):
    """Stylised great white shark: lofted fusiform body (conical snout, deep girth, narrow peduncle), countershaded
    (grey back / white belly by normal), dorsal + pectoral fins, lunate caudal on a tail pivot, black eyes, gill
    slits and closed mouth line. Body along +Y (snout +Y), origin mid-body. Returns parts (root, tail, eyes, body)."""
    Lh = length
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root}
    skin = _whale_body_mat(name + "_skin", top=top, belly=belly)
    skin.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.45
    tail = L.link(bpy.data.objects.new(name + "_tail", None))
    tail.parent = root
    tcut = 0.3
    tail.location = (0, (tcut - 0.5) * Lh, 0)
    P["tail"] = tail

    def ring_at(t, yoff=0.0):
        r = _gw_r(t) * Lh
        rz = r * 1.18
        out = []
        for j in range(ring):
            a = 2 * math.pi * j / ring
            z = math.sin(a) * rz * (0.85 if math.sin(a) < 0 else 1.0)
            out.append((math.cos(a) * r, (t - 0.5) * Lh - yoff, z + 0.02 * Lh * (t - 0.5)))
        return out
    front = _loft(name + "_body", [ring_at(tcut - 0.02 + (1 - tcut + 0.02) * k / seg) for k in range(seg + 1)])
    L.smooth(front)
    L.assign(front, skin)
    front.parent = root
    P["body"] = front
    rear = _loft(name + "_rear", [ring_at(tcut * k / 8, (tcut - 0.5) * Lh) for k in range(9)])
    L.smooth(rear)
    L.assign(rear, skin)
    rear.parent = tail
    finm = L.mat_principled(name + "_finm", tuple(c * 0.85 for c in top), rough=0.45)
    y = lambda t: (t - 0.5) * Lh
    zt = lambda t: _gw_r(t) * Lh * 1.18
    _fin_mesh(name + "_dorsal", [(0, y(0.47), zt(0.47) * 0.8), (0, y(0.63), zt(0.63) * 0.8), (0, y(0.45), zt(0.5) + 0.2 * Lh)],
              0.025 * Lh, finm, root)
    for sx in (-1, 1):
        P[f"pec{sx}"] = _fin_mesh(name + f"_pec{sx}", [(sx * _gw_r(0.7) * Lh * 0.8, y(0.72), -0.04 * Lh),
                                                         (sx * _gw_r(0.62) * Lh * 0.8, y(0.62), -0.06 * Lh),
                                                         (sx * 0.36 * Lh, y(0.5), -0.17 * Lh)], 0.02 * Lh, finm, root)
    # caudal (in tail space: tail pivot at t=tcut)
    ty = lambda t: (t - tcut) * Lh
    _fin_mesh(name + "_caudal", [(0, ty(0.04), 0.01 * Lh), (0, ty(-0.1), 0.27 * Lh), (0, ty(-0.06), 0.0),
                                 (0, ty(-0.09), -0.21 * Lh)], 0.02 * Lh, finm, tail)
    _fin_mesh(name + "_anal", [(0, ty(0.18), -0.02 * Lh), (0, ty(0.26), -0.035 * Lh), (0, ty(0.16), -0.07 * Lh)],
              0.012 * Lh, finm, tail)
    _fin_mesh(name + "_dorsal2", [(0, ty(0.17), 0.03 * Lh), (0, ty(0.23), 0.045 * Lh), (0, ty(0.16), 0.08 * Lh)],
              0.012 * Lh, finm, tail)
    # eyes, gills, mouth
    eyem = L.mat_principled(name + "_eyem", (0.005, 0.005, 0.006), rough=0.05, metal=0.0)
    P["eyes"] = []
    te = 0.86
    for sx in (-1, 1):
        r = _gw_r(te) * Lh
        e = L.prim("sphere", loc=(sx * r * 0.95, y(te), r * 0.35), segments=16, ring_count=10, radius=0.011 * Lh,
                   name=name + f"_eye{sx}")
        L.assign(e, eyem)
        L.smooth(e)
        e.parent = root
        P["eyes"].append(e)
        for k in range(5):
            tg = 0.7 + k * 0.025
            rg = _gw_r(tg) * Lh
            g = L.prim("cube", loc=(sx * rg * 0.98, y(tg), 0.0), rot=(0.25, 0, 0), name=name + "_gill")
            g.scale = (0.004 * Lh, 0.003 * Lh, 0.05 * Lh)
            L.assign(g, L.mat_principled(name + "_gillm", (0.12, 0.13, 0.15), rough=0.5))
            g.parent = root
    mp = []
    for k in range(9):
        u = -1 + 2 * k / 8
        tm = 0.88 - 0.06 * abs(u) ** 1.5
        rm = _gw_r(tm) * Lh
        mp.append((u * rm * 0.9, y(tm), -rm * 0.55))
    mo = tube(mp, radius=0.006 * Lh, mat=L.mat_principled(name + "_mouthm", (0.08, 0.05, 0.05), rough=0.5), name=name + "_mouth")
    mo.parent = root
    return P


def gw_swim(P, nframes, rate=0.5, amp=0.3, start=1, step=2):
    """Tail sweep (tail pivot yaw) with a small counter-yaw on the pectorals."""
    for f in range(start, start + nframes + 1, step):
        t = (f - start) / 24
        P["tail"].rotation_euler = (0, 0, amp * math.sin(2 * math.pi * rate * t))
        P["tail"].keyframe_insert("rotation_euler", frame=f)


def spearfisher(name="fox", suit=(0.025, 0.03, 0.045), scuba=False, gun=True):
    """1960s breath-hold spearfisher (faceless): char_diver without tank (unless scuba), black wetsuit + hood,
    oval mask, snorkel, weight belt with buckle, long fins, wooden speargun in the right hand.
    parts['belt_pt'] = local belt attachment point for a float line. Root faces +Y, back +Z."""
    P = L.char_diver(name=name, suit=suit, accent=(0.05, 0.05, 0.05), tanks="single", light_on=False)
    if not scuba:
        for k in list(P):
            if k.startswith("tank"):
                bpy.data.objects.remove(P.pop(k), do_unlink=True)
    r = P["root"]
    sn = tube([(0.07, 0.66, -0.06), (0.12, 0.6, 0.02), (0.13, 0.5, 0.18), (0.13, 0.48, 0.32)], radius=0.012,
              mat=L.mat_principled(name + "_snork", (0.9, 0.55, 0.1), rough=0.4), name=name + "_snorkel")
    sn.parent = r
    belt = L.prim("torus", loc=(0, -0.38, -0.01), rot=(math.pi / 2, 0, 0), major_radius=1.0, minor_radius=0.12,
                  name=name + "_belt")
    belt.scale = (0.2, 0.17, 0.14)
    L.assign(belt, L.mat_principled(name + "_beltm", (0.02, 0.02, 0.02), rough=0.5))
    belt.parent = r
    bk = L.prim("cube", loc=(0, -0.38, -0.17), name=name + "_buckle")
    bk.scale = (0.04, 0.02, 0.012)
    L.assign(bk, L.mat_principled(name + "_bkm", (0.7, 0.7, 0.72), rough=0.2, metal=1.0))
    bk.parent = r
    for sx in (-1, 1):
        w = L.prim("cube", loc=(sx * 0.15, -0.38, -0.12), name=name + "_lead")
        w.scale = (0.04, 0.03, 0.025)
        L.assign(w, L.mat_principled(name + "_leadm", (0.25, 0.25, 0.27), rough=0.5, metal=0.5))
        w.parent = r
    for tag in ("L", "R"):
        f = P[f"fin{tag}"]
        f.scale = (0.1, 0.36, 0.012)
        f.location = (0, -0.75, 0)
    if gun:
        g = L.prim("cyl", loc=(0, 0.95, 0), rot=(math.pi / 2, 0, 0), vertices=8, radius=0.022, depth=1.1, name=name + "_gun")
        L.assign(g, L.mat_principled(name + "_wood", (0.35, 0.2, 0.08), rough=0.5))
        g.parent = P["shoulderR"]
        sp = L.prim("cyl", loc=(0, 1.75, 0.0), rot=(math.pi / 2, 0, 0), vertices=6, radius=0.006, depth=0.6, name=name + "_spear")
        L.assign(sp, L.mat_principled(name + "_steel", (0.75, 0.75, 0.78), rough=0.2, metal=1.0))
        sp.parent = P["shoulderR"]
        P["gun"] = g
    P["belt_pt"] = (0, -0.38, 0.16)
    return P


def float_buoy(loc=(0, 0, 0), name="float", color=(1.0, 0.38, 0.03)):
    """Orange surface float with a short flag pole."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    b = L.prim("sphere", loc=(0, 0, 0), segments=16, ring_count=10, radius=0.22, name=name + "_ball")
    b.scale = (1, 1, 0.8)
    L.assign(b, L.mat_principled(name + "_m", color, rough=0.4))
    b.parent = root
    p = L.prim("cyl", loc=(0, 0, 0.45), vertices=6, radius=0.012, depth=0.6, name=name + "_pole")
    L.assign(p, L.mat_principled(name + "_pm", (0.15, 0.15, 0.15), rough=0.5))
    p.parent = root
    fl = L.prim("cube", loc=(0.1, 0, 0.66), name=name + "_flag")
    fl.scale = (0.1, 0.005, 0.07)
    L.assign(fl, L.mat_principled(name + "_fm", (0.9, 0.1, 0.08), rough=0.5))
    fl.parent = root
    return root


def dinghy(name="dinghy", length=4.0, beam=1.5, wood=(0.42, 0.24, 0.11), inside=(0.6, 0.45, 0.3)):
    """Small wooden open dinghy (bow +Y, waterline z=0): lofted planked hull, gunwale rail, two thwarts, oars."""
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root}
    hm = L.mat_noise_surface(name + "_hull", tuple(c * 0.7 for c in wood), wood, scale=6, rough=0.6, bump=0.2, voronoi=False)
    sts = []
    for i in range(13):
        t = i / 12
        y = (t - 0.5) * length
        b = beam / 2 * (math.sin(math.pi * min(1.0, 0.15 + t * 0.95)) ** 0.7 if t > 0.1 else 0.85)
        b = max(0.04, b)
        keel = -0.3 + 0.25 * max(0, t - 0.75) / 0.25
        gun = 0.42 + 0.15 * max(0, t - 0.7) / 0.3
        ring = [(xn * b, y, keel + (gun - keel) * zn) for xn, zn in SECTION[:-1]]
        ring.append((0, y, keel))
        ring += [(-xn * b, y, keel + (gun - keel) * zn) for xn, zn in reversed(SECTION[:-1])]
        sts.append(ring)
    h = _loft(name + "_hull", sts, close_ends=True)
    L.smooth(h)
    L.assign(h, hm)
    h.parent = root
    fl = L.prim("cube", loc=(0, -0.1, 0.36), name=name + "_floor")
    fl.scale = (beam * 0.42, length * 0.38, 0.03)
    L.assign(fl, L.mat_principled(name + "_in", inside, rough=0.7))
    fl.parent = root
    for ty in (-0.6, 0.5):
        th = L.prim("cube", loc=(0, ty, 0.48), name=name + "_thwart")
        th.scale = (beam * 0.45, 0.1, 0.02)
        L.assign(th, hm)
        th.parent = root
    for sx in (-1, 1):
        oar = L.prim("cyl", loc=(sx * 0.9, -0.1, 0.45), rot=(0, math.pi / 2 - sx * 0.2, 0.25 * sx), vertices=6,
                     radius=0.025, depth=2.2, name=name + "_oar")
        L.assign(oar, hm)
        oar.parent = root
    return P


def shark_cage(name="cage", w=2.0, d=1.2, h=1.8, bar=0.25, steel=(0.55, 0.57, 0.6), drums=(0.95, 0.85, 0.2)):
    """Two-person shark cage: steel box frame (origin at bottom centre), vertical bars every `bar` m, mid rail, top
    hatch frame, two float drums on top, lifting bridle ring. Returns root."""
    root = L.link(bpy.data.objects.new(name, None))
    sm = L.mat_principled(name + "_steel", steel, rough=0.35, metal=0.8)

    def rod(a, b, r=0.018):
        a, b = Vector(a), Vector(b)
        o = L.prim("cyl", loc=(a + b) / 2, vertices=8, radius=r, depth=(b - a).length, name=name + "_rod")
        o.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
        L.assign(o, sm)
        o.parent = root
        return o
    cs = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
    for z, r in ((0, 0.035), (h, 0.035), (h * 0.55, 0.025)):
        for (ax, ay), (bx, by) in zip(cs, cs[1:] + cs[:1]):
            rod((ax, ay, z), (bx, by, z), r)
    for (ax, ay), (bx, by) in zip(cs, cs[1:] + cs[:1]):
        ln = math.hypot(bx - ax, by - ay)
        k = int(ln / bar)
        for i in range(k + 1):
            u = i / k
            rod((ax + (bx - ax) * u, ay + (by - ay) * u, 0), (ax + (bx - ax) * u, ay + (by - ay) * u, h), 0.016 if 0 < i < k else 0.035)
    for x in (-w / 4, w / 4):
        rod((x, -d / 2, 0), (x, d / 2, 0), 0.02)
    # top hatch frame
    for (ax, ay), (bx, by) in (((-0.35, -0.35), (0.35, -0.35)), ((0.35, -0.35), (0.35, 0.35)), ((0.35, 0.35), (-0.35, 0.35)),
                               ((-0.35, 0.35), (-0.35, -0.35))):
        rod((ax, ay, h + 0.03), (bx, by, h + 0.03), 0.02)
    dm = L.mat_principled(name + "_drum", drums, rough=0.4)
    for y in (-d / 2 + 0.15, d / 2 - 0.15):
        dr = L.prim("cyl", loc=(0, y, h + 0.17), rot=(0, math.pi / 2, 0), vertices=16, radius=0.15, depth=w * 0.9, name=name + "_drum")
        L.assign(dr, dm)
        dr.parent = root
    ring = L.prim("torus", loc=(0, 0, h + 0.6), rot=(math.pi / 2, 0, 0), major_radius=0.08, minor_radius=0.015, name=name + "_ring")
    L.assign(ring, sm)
    ring.parent = root
    for (cx, cy) in cs:
        rod((cx, cy, h), (0, 0, h + 0.55), 0.008)
    return root


def film_housing(name="camhousing", body=(0.12, 0.13, 0.15)):
    """1960s boxy underwater cine-camera housing: box, front lens port (+Y), side handles, top viewfinder."""
    root = L.link(bpy.data.objects.new(name, None))
    bm_ = L.mat_principled(name + "_m", body, rough=0.35, metal=0.6)
    b = L.prim("cube", loc=(0, 0, 0), name=name + "_box")
    b.scale = (0.14, 0.2, 0.13)
    L.bevel(b, 0.02, 2)
    L.assign(b, bm_)
    b.parent = root
    port = L.prim("cyl", loc=(0, 0.24, 0), rot=(math.pi / 2, 0, 0), vertices=24, radius=0.07, depth=0.08, name=name + "_port")
    L.assign(port, bm_)
    port.parent = root
    gl = L.prim("cyl", loc=(0, 0.285, 0), rot=(math.pi / 2, 0, 0), vertices=24, radius=0.058, depth=0.005, name=name + "_glass")
    L.assign(gl, L.mat_principled(name + "_gl", (0.05, 0.1, 0.15), rough=0.02, metal=0.5))
    gl.parent = root
    for sx in (-1, 1):
        hd = L.prim("cube", loc=(sx * 0.2, -0.02, -0.02), name=name + "_handle")
        hd.scale = (0.02, 0.03, 0.12)
        L.assign(hd, bm_)
        hd.parent = root
    vf = L.prim("cube", loc=(0, -0.05, 0.16), name=name + "_vf")
    vf.scale = (0.04, 0.08, 0.03)
    L.assign(vf, bm_)
    vf.parent = root
    return root


def polyline(points, mat, width=0.01, name="pl", closed=False):
    """Static emissive poly curve (diagram line art)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = width
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (*p, 1)
    sp.use_cyclic_u = closed
    o = L.link(bpy.data.objects.new(name, cu))
    o.data.materials.append(mat)
    return o


def torso_diagram(name="torso", color=(0.9, 0.95, 1.0), width=0.008):
    """Front-view schematic torso in the XZ plane (y=0): outline, neck, both upper arms, clavicles, sternum,
    6 rib arcs per side (each its own material: parts['ribs'][side] = [(obj, mat)]), lung loops (parts['lungL'] is
    an empty at the patient's LEFT lung centre (+X = viewer's right) — scale it to deflate). Height ~1.0 unit."""
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root, "ribs": {"L": [], "R": []}}
    m = L.mat_emission(name + "_m", color, 3.0)

    def add(pts, nm, mat=None, closed=False, parent=root):
        o = polyline([(x, 0, z) for x, z in pts], mat or m, width, name + nm, closed)
        o.parent = parent
        return o
    half = [(0.06, 0.62), (0.07, 0.52), (0.2, 0.47), (0.27, 0.43), (0.29, 0.3), (0.27, 0.1), (0.23, -0.1), (0.21, -0.25),
            (0.24, -0.38)]
    add(half, "_outR")
    add([(-x, z) for x, z in half], "_outL")
    add([(-0.24, -0.38), (0, -0.42), (0.24, -0.38)], "_hip")
    for sx in (-1, 1):
        add([(sx * 0.29, 0.42), (sx * 0.37, 0.35), (sx * 0.39, 0.1), (sx * 0.38, -0.12)], f"_armo{sx}")
        add([(sx * 0.28, 0.2), (sx * 0.31, 0.05), (sx * 0.31, -0.12)], f"_armi{sx}")
        add([(sx * 0.03, 0.42), (sx * 0.22, 0.44)], f"_clav{sx}")
    add([(0, 0.4), (0, 0.12)], "_sternum")
    for side, sx in (("R", -1), ("L", 1)):
        for k in range(6):
            z = 0.36 - k * 0.06
            rm = L.mat_emission(f"{name}_rib{side}{k}", color, 2.2)
            pts = [(sx * 0.02, z), (sx * 0.12, z + 0.01), (sx * 0.22, z - 0.03), (sx * (0.25 - k * 0.003), z - 0.1)]
            P["ribs"][side].append((add(pts, f"_rib{side}{k}", rm), rm))
    for side, sx in (("R", -1), ("L", 1)):
        c = L.link(bpy.data.objects.new(f"{name}_lung{side}", None))
        c.parent = root
        c.location = (sx * 0.13, 0, 0.2)
        lm = L.mat_emission(f"{name}_lungm{side}", (0.4, 0.8, 1.0), 2.5)
        pts = []
        for j in range(20):
            a = 2 * math.pi * j / 20
            pts.append((sx * (0.075 * math.cos(a)), 0.15 * math.sin(a) - 0.0))
        o = add(pts, f"_lung{side}c", lm, closed=True, parent=c)
        P[f"lung{side}"] = c
        P[f"lungm{side}"] = lm
    return P


def film_grain(cam, lens=18, dist=0.12, strength=0.25, nframes=60, tint=(0.25, 0.2, 0.12), name="grain"):
    """Camera-parented film look: flickering noise grain + soft vignette + faint vertical scratch (transparent)."""
    hh = dist * 18 / lens * 1.08
    o = L.prim("plane", loc=(0, 0, -dist), size=2, name=name)
    o.scale = (hh * 9 / 16, hh, 1)
    o.parent = cam
    m, n, l = _m(name + "_m")
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    tc = n.new("ShaderNodeTexCoord")
    mp = n.new("ShaderNodeMapping")
    l.new(tc.outputs["UV"], mp.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 260
    nz.inputs["Detail"].default_value = 2
    l.new(mp.outputs[0], nz.inputs["Vector"])
    for f in range(1, nframes + 1):
        mp.inputs["Location"].default_value = ((f * 0.37) % 1, (f * 0.61) % 1, 0)
        mp.inputs["Location"].keyframe_insert("default_value", frame=f)
    ad = mp.inputs["Location"].id_data.animation_data
    if ad and ad.action:
        for fc in L._fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    gr = n.new("ShaderNodeMapRange")
    gr.inputs["From Min"].default_value = 0.45
    gr.inputs["From Max"].default_value = 0.75
    gr.inputs["To Max"].default_value = strength
    l.new(nz.outputs["Fac"], gr.inputs["Value"])
    vm = n.new("ShaderNodeVectorMath")
    vm.operation = "DISTANCE"
    vm.inputs[1].default_value = (0.5, 0.5, 0)
    l.new(tc.outputs["UV"], vm.inputs[0])
    vg = n.new("ShaderNodeMapRange")
    vg.inputs["From Min"].default_value = 0.3
    vg.inputs["From Max"].default_value = 0.72
    vg.inputs["To Max"].default_value = 0.85
    l.new(vm.outputs["Value"], vg.inputs["Value"])
    tot = n.new("ShaderNodeMath")
    tot.operation = "MAXIMUM"
    l.new(gr.outputs[0], tot.inputs[0])
    l.new(vg.outputs[0], tot.inputs[1])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*tint, 1)
    em.inputs[1].default_value = 0.3
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


# ============================================================================= SCUBA-07 additions (Antikythera)
# gears, corroded lump, 1900 hard-hat diver, sponge caïque, amphora. New builders only.

def mat_bronze(name="bronze", color=(0.55, 0.36, 0.16), rough=0.32, patina=0.0):
    """Polished (patina=0) to weathered (patina~0.6) bronze."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    p.inputs["Metallic"].default_value = 1.0 - 0.6 * patina
    p.inputs["Roughness"].default_value = rough + 0.4 * patina
    if patina <= 0:
        p.inputs["Base Color"].default_value = (*color, 1)
        return m
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 12.0
    nz.inputs["Detail"].default_value = 6
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.45 - 0.2 * patina
    ramp.color_ramp.elements[0].color = (*color, 1)
    ramp.color_ramp.elements[1].position = 0.62
    ramp.color_ramp.elements[1].color = (0.12, 0.3, 0.22, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    return m


def mat_verdigris(name="verdigris", c1=(0.05, 0.09, 0.06), c2=(0.22, 0.32, 0.2), crust=(0.42, 0.38, 0.3), scale=18.0):
    """Corroded bronze lump: dark green-brown with pale calcareous crust patches and strong bump."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.85
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 10
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    vr = n.new("ShaderNodeTexVoronoi")
    vr.inputs["Scale"].default_value = scale * 0.6
    l.new(tc.outputs["Object"], vr.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    cr = n.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].position = 0.55
    cr.color_ramp.elements[1].position = 0.75
    l.new(vr.outputs["Distance"], cr.inputs["Fac"])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    l.new(cr.outputs["Color"], mix.inputs["Factor"])
    l.new(ramp.outputs["Color"], mix.inputs["A"])
    mix.inputs["B"].default_value = (*crust, 1)
    l.new(mix.outputs["Result"], p.inputs["Base Color"])
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.8
    ad = n.new("ShaderNodeMath")
    ad.operation = "ADD"
    l.new(nz.outputs["Fac"], ad.inputs[0])
    l.new(cr.outputs["Color"], ad.inputs[1])
    l.new(ad.outputs[0], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def lump(name="lump", size=(0.2, 0.17, 0.09), seed=3, mat=None, apply=True):
    """Fist-sized corroded bronze lump (flattened, lumpy slab). Origin at its centre."""
    o = L.prim("ico", loc=(0, 0, 0), subdivisions=4, radius=1.0, name=name)
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    L.apply_scale(o)
    t = bpy.data.textures.new(name + "_t", "CLOUDS")
    t.noise_scale = 0.06
    t.noise_depth = 3
    rnd = random.Random(seed)
    d = o.modifiers.new("d1", "DISPLACE")
    d.texture = t
    d.strength = 0.035
    d.texture_coords = "OBJECT"
    t2 = bpy.data.textures.new(name + "_t2", "VORONOI")
    t2.noise_scale = 0.025
    d2 = o.modifiers.new("d2", "DISPLACE")
    d2.texture = t2
    d2.strength = -0.008
    o.rotation_euler = (0, 0, rnd.uniform(0, 0.5))
    L.smooth(o)
    L.assign(o, mat or mat_verdigris(name + "_m"))
    if apply:
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        o.modifiers.clear()
        o.data = me
    return o


def split_halves(o, plane_no=(1.0, 0.25, 0.0), plane_co=(0, 0, 0), inner_mat=None):
    """Duplicate a mesh into two halves cut by a plane (holes filled; the cut face gets inner_mat). Hides o.
    Returns (half_a, half_b)."""
    out = []
    for keep in (True, False):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=plane_co,
                                     plane_no=plane_no, clear_inner=keep, clear_outer=not keep)
        cut_edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
        nf = bmesh.ops.holes_fill(bm, edges=cut_edges, sides=0)
        me = bpy.data.meshes.new(o.name + ("_a" if keep else "_b"))
        for f in nf["faces"]:
            f.material_index = 1
        bm.to_mesh(me)
        bm.free()
        h = L.link(bpy.data.objects.new(me.name, me))
        h.matrix_world = o.matrix_world.copy()
        for ms in o.data.materials:
            me.materials.append(ms)
        me.materials.append(inner_mat or L.mat_principled(o.name + "_in", (0.06, 0.08, 0.05), rough=0.9))
        out.append(h)
    o.hide_render = True
    o.hide_viewport = True
    return out


def gear(name="gear", teeth=32, r=0.1, thick=0.01, mat=None, spokes=4, hub=None, rim=None):
    """Flat spur gear in the local XY plane (axis = local Z), origin at the centre. Teeth are trapezoids;
    module = 2r/teeth. spokes=0 gives a solid disc. Returns the object (rotate it about local Z to turn)."""
    mod = 2 * r / teeth
    r_tip, r_root = r + mod, r - 1.25 * mod
    r_in = rim if rim is not None else (r_root - max(0.12 * r, 2.2 * mod) if spokes else 0.0)
    p = 2 * math.pi / teeth
    prof = []
    for k in range(teeth):
        a0 = k * p
        prof += [(r_root, a0), (r_tip, a0 + 0.2 * p), (r_tip, a0 + 0.45 * p), (r_root, a0 + 0.65 * p)]
    bm = bmesh.new()
    h = thick / 2
    N = len(prof)
    if r_in > 0:
        ot = [bm.verts.new((rr * math.cos(a), rr * math.sin(a), h)) for rr, a in prof]
        ob = [bm.verts.new((rr * math.cos(a), rr * math.sin(a), -h)) for rr, a in prof]
        it = [bm.verts.new((r_in * math.cos(a), r_in * math.sin(a), h)) for _, a in prof]
        ib = [bm.verts.new((r_in * math.cos(a), r_in * math.sin(a), -h)) for _, a in prof]
        for i in range(N):
            j = (i + 1) % N
            bm.faces.new((ot[i], ot[j], it[j], it[i]))
            bm.faces.new((ob[j], ob[i], ib[i], ib[j]))
            bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
            bm.faces.new((it[i], it[j], ib[j], ib[i]))
    else:
        ct, cb = bm.verts.new((0, 0, h)), bm.verts.new((0, 0, -h))
        ot = [bm.verts.new((rr * math.cos(a), rr * math.sin(a), h)) for rr, a in prof]
        ob = [bm.verts.new((rr * math.cos(a), rr * math.sin(a), -h)) for rr, a in prof]
        for i in range(N):
            j = (i + 1) % N
            bm.faces.new((ct, ot[i], ot[j]))
            bm.faces.new((cb, ob[j], ob[i]))
            bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
    if r_in > 0:
        hub_r = hub or max(0.12 * r, 0.006)
        w = max(0.08 * r, 0.004)
        for s in range(spokes):
            a = 2 * math.pi * s / spokes
            dx, dy = math.cos(a), math.sin(a)
            px, py = -dy * w, dx * w
            ins = hub_r * 0.8
            outs = r_in * 1.02
            vs = []
            for z in (h * 0.8, -h * 0.8):
                vs.append([bm.verts.new((dx * ins + px, dy * ins + py, z)), bm.verts.new((dx * outs + px, dy * outs + py, z)),
                           bm.verts.new((dx * outs - px, dy * outs - py, z)), bm.verts.new((dx * ins - px, dy * ins - py, z))])
            t, b = vs
            bm.faces.new(t)
            bm.faces.new(list(reversed(b)))
            for i in range(4):
                j = (i + 1) % 4
                bm.faces.new((b[i], b[j], t[j], t[i]))
        seg = 16
        ht = [bm.verts.new((hub_r * math.cos(2 * math.pi * i / seg), hub_r * math.sin(2 * math.pi * i / seg), h * 1.4))
              for i in range(seg)]
        hb = [bm.verts.new((hub_r * math.cos(2 * math.pi * i / seg), hub_r * math.sin(2 * math.pi * i / seg), -h * 1.4))
              for i in range(seg)]
        bm.faces.new(ht)
        bm.faces.new(list(reversed(hb)))
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((hb[i], hb[j], ht[j], ht[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = L.mesh_from_bm(name, bm)
    if mat:
        L.assign(o, mat)
    o["r"] = r
    o["teeth"] = teeth
    return o


def mount(obj, loc, normal=(0, -1, 0)):
    """Parent obj (a gear spinning about its local Z) to a new empty at loc whose Z axis = normal."""
    e = L.link(bpy.data.objects.new(obj.name + "_mount", None))
    e.location = loc
    e.rotation_mode = "QUATERNION"
    e.rotation_quaternion = Vector(normal).to_track_quat("Z", "Y")
    obj.parent = e
    obj.location = (0, 0, 0)
    return e


def spin(obj, nframes, turns_per_sec, phase=0.0, start=1, step=2):
    """Linear spin about local Z (radians keyed per `step` frames, linear)."""
    for f in list(range(start, nframes + 1, step)) + [nframes]:
        obj.rotation_euler = (0, 0, phase + 2 * math.pi * turns_per_sec * (f - start) / 24.0)
        obj.keyframe_insert("rotation_euler", frame=f)
    ad = obj.animation_data
    if ad and ad.action:
        for fc in L._fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


def amphora(loc=(0, 0, 0), rot=(0, 0, 0), h=0.7, name="amph", color=(0.55, 0.3, 0.17), crust=0.4, seg=20):
    """Roman transport amphora: lathe body (pointed toe), neck, rim and two loop handles. Base of toe at origin."""
    prof = [(0.0, 0.0), (0.03, 0.03), (0.07, 0.12), (0.15, 0.32), (0.17, 0.48), (0.16, 0.6), (0.1, 0.68), (0.055, 0.72),
            (0.05, 0.9), (0.065, 0.93), (0.05, 0.95)]
    sc = h / 0.95
    rings = []
    for r, z in prof:
        rings.append([(max(r, 0.002) * sc * math.cos(2 * math.pi * k / seg), max(r, 0.002) * sc * math.sin(2 * math.pi * k / seg),
                       z * sc) for k in range(seg)])
    o = _loft(name, rings, close_ends=True)
    m = L.mat_noise_surface(name + "_m", tuple(c * 0.6 for c in color), color, scale=6, bump=0.5, voronoi=False) \
        if crust <= 0 else mat_verdigris(name + "_m", c1=tuple(c * 0.5 for c in color), c2=color,
                                         crust=(0.55, 0.52, 0.45), scale=6.0)
    L.smooth(o)
    L.assign(o, m)
    for sx in (-1, 1):
        hd = L.prim("torus", loc=(sx * 0.085 * sc, 0, 0.8 * sc), rot=(math.pi / 2, 0, 0), major_radius=0.06 * sc,
                    minor_radius=0.012 * sc, major_segments=16, minor_segments=6, name=name + "_h")
        L.assign(hd, m)
        hd.parent = o
    o.location = loc
    o.rotation_euler = rot
    return o


def helmet_diver(name="hardhat", canvas=(0.42, 0.4, 0.35), brass=(0.62, 0.42, 0.16), height=1.75):
    """1900 hard-hat diver: faceless char_figure in grey canvas, copper/brass sphere helmet with a round dark-glass
    faceplate (no face), breastplate, lead boots. Faces +Y. parts: root, pelvis, neck, helmet, exhaust (local loc)."""
    P = L.char_figure(name, color=canvas, height=height)
    cm = L.mat_noise_surface(name + "_canvas", tuple(c * 0.75 for c in canvas), canvas, scale=30, bump=0.25, rough=0.95,
                             voronoi=False)
    for k, o in list(P.items()):
        if hasattr(o, "type") and o.type == "MESH":
            o.data.materials.clear()
            o.data.materials.append(cm)
    s = height / 1.75
    P["head"].hide_render = True
    P["head"].hide_viewport = True
    bm_ = mat_bronze(name + "_brass", brass, rough=0.28)
    hel = L.prim("sphere", loc=(0, 0, 0.15 * s), segments=24, ring_count=12, radius=0.19 * s, name=name + "_helmet")
    L.assign(hel, bm_)
    L.smooth(hel)
    hel.parent = P["neck"]
    glass = L.mat_principled(name + "_glass", (0.01, 0.012, 0.015), rough=0.05, metal=0.3)
    fp = L.prim("cyl", loc=(0, 0.175 * s, 0.15 * s), rot=(math.pi / 2, 0, 0), vertices=24, radius=0.09 * s, depth=0.03 * s,
                name=name + "_face")
    L.assign(fp, glass)
    fp.parent = P["neck"]
    fr = L.prim("torus", loc=(0, 0.19 * s, 0.15 * s), rot=(math.pi / 2, 0, 0), major_radius=0.095 * s,
                minor_radius=0.014 * s, major_segments=24, minor_segments=6, name=name + "_frame")
    L.assign(fr, bm_)
    fr.parent = P["neck"]
    for sx in (-1, 1):
        sp = L.prim("cyl", loc=(sx * 0.17 * s, 0.05 * s, 0.17 * s), rot=(0, math.pi / 2, 0), vertices=16, radius=0.05 * s,
                    depth=0.03 * s, name=name + "_port")
        L.assign(sp, glass)
        sp.parent = P["neck"]
    vb = L.prim("cyl", loc=(0.0, -0.15 * s, 0.24 * s), rot=(-0.6, 0, 0), vertices=10, radius=0.025 * s, depth=0.08 * s,
                name=name + "_valve")
    L.assign(vb, bm_)
    vb.parent = P["neck"]
    bp = L.prim("cyl", loc=(0, 0, 0.6 * s), vertices=24, radius=0.25 * s, depth=0.06 * s, name=name + "_breast")
    bp.scale = (1.0, 0.85, 1.0)
    L.assign(bp, bm_)
    bp.parent = P["pelvis"]
    lead = L.mat_principled(name + "_lead", (0.08, 0.08, 0.085), rough=0.6, metal=0.4)
    for tag in ("L", "R"):
        bt = L.prim("cube", loc=(0, 0.04 * s, -0.47 * s), name=name + "_boot" + tag)
        bt.scale = (0.07 * s, 0.15 * s, 0.06 * s)
        L.assign(bt, lead)
        bt.parent = P[f"knee{tag}"]
    for k, z in enumerate((0.4, 0.15)):
        wt = L.prim("cube", loc=(0, 0.13 * s, z * s), name=name + f"_weight{k}")
        wt.scale = (0.12 * s, 0.03 * s, 0.07 * s)
        L.assign(wt, lead)
        wt.parent = P["pelvis"]
    P["helmet"] = hel
    P["canvas_mat"] = cm
    P["brass_mat"] = bm_
    P["exhaust"] = (0.0, -0.17 * s, 0.25 * s)  # neck-local
    return P


def caique(name="caique", length=9.0, beam=2.8, wood=(0.5, 0.33, 0.18), stripe=(0.1, 0.25, 0.55), sail=(0.82, 0.76, 0.62)):
    """Greek sponge boat (bow +Y, waterline z=0): lofted wooden hull with raised bow and stern, deck, painted
    sheer stripe, single mast with a furled sail on a slanted yard. Returns parts dict(root, deck_z, mast_top)."""
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root}
    hm = L.mat_noise_surface(name + "_hull", tuple(c * 0.7 for c in wood), wood, scale=4, rough=0.65, bump=0.25,
                             voronoi=False)
    sts = []
    for i in range(17):
        t = i / 16
        y = (t - 0.5) * length
        b = beam / 2 * max(0.05, math.sin(math.pi * t) ** 0.6)
        keel = -0.75 + 0.45 * (abs(t - 0.5) * 2) ** 3
        gun = 0.75 + 0.55 * (abs(t - 0.5) * 2) ** 2.5
        ring = [(xn * b, y, keel + (gun - keel) * zn) for xn, zn in SECTION[:-1]]
        ring.append((0, y, keel))
        ring += [(-xn * b, y, keel + (gun - keel) * zn) for xn, zn in reversed(SECTION[:-1])]
        sts.append(ring)
    h = _loft(name + "_hull", sts, close_ends=True)
    L.smooth(h)
    L.assign(h, hm)
    h.parent = root
    st = L.prim("cyl", loc=(0, 0, 0.68), vertices=32, radius=1.0, depth=0.08, name=name + "_stripe")
    st.scale = (beam / 2 * 1.005, length / 2 * 0.86, 1)
    L.assign(st, L.mat_principled(name + "_st", stripe, rough=0.5))
    st.parent = root
    dk = L.prim("cyl", loc=(0, 0, 0.7), vertices=32, radius=1.0, depth=0.04, name=name + "_deck")
    dk.scale = (beam / 2 * 0.93, length / 2 * 0.84, 1)
    dm = L.mat_noise_surface(name + "_deckm", (0.3, 0.22, 0.14), (0.55, 0.42, 0.28), scale=3, rough=0.7, bump=0.2,
                             voronoi=False)
    L.assign(dk, dm)
    dk.parent = root
    wm = L.mat_principled(name + "_spar", (0.32, 0.22, 0.12), rough=0.6)
    mast_h = length * 0.75
    ms = L.prim("cyl", loc=(0, length * 0.12, 0.7 + mast_h / 2), vertices=10, radius=0.07, depth=mast_h, name=name + "_mast")
    L.assign(ms, wm)
    ms.parent = root
    yard_c = Vector((0, length * 0.12 + 0.15, 0.7 + mast_h * 0.7))
    yd = L.prim("cyl", loc=tuple(yard_c), rot=(-0.9, 0, 0), vertices=8, radius=0.045, depth=length * 0.85, name=name + "_yard")
    L.assign(yd, wm)
    yd.parent = root
    sl = L.prim("cyl", loc=tuple(yard_c + Vector((0, 0, -0.08))), rot=(-0.9, 0, 0), vertices=10, radius=0.13,
                depth=length * 0.7, name=name + "_sail")
    sl.scale = (1.0, 0.8, 1.0)
    L.add_displace(sl, strength=0.04, scale=0.15, name=name + "_sd")
    L.assign(sl, L.mat_noise_surface(name + "_sailm", tuple(c * 0.8 for c in sail), sail, scale=10, rough=0.9, bump=0.3,
                                     voronoi=False))
    sl.parent = root
    for k, (y, w) in enumerate(((-length * 0.32, 1.0), (length * 0.3, 0.8))):
        bx = L.prim("cube", loc=(0, y, 0.95), name=name + f"_house{k}")
        bx.scale = (beam * 0.18 * w, 0.4, 0.22)
        L.assign(bx, hm)
        bx.parent = root
    P["deck_z"] = 0.72
    P["mast_top"] = (0, length * 0.12, 0.7 + mast_h)
    P["hull_mat"] = hm
    return P


def air_pump(loc=(0, 0, 0), rot_z=0.0, name="pump", wood=(0.35, 0.22, 0.12), brass=(0.62, 0.42, 0.16)):
    """Hand-cranked diving air pump: wooden box with two big iron flywheels (cranks). parts: root, wheels [spin objs]."""
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    bx = L.prim("cube", loc=(0, 0, 0.35), name=name + "_box")
    bx.scale = (0.32, 0.25, 0.35)
    L.bevel(bx, 0.02)
    L.assign(bx, L.mat_noise_surface(name + "_wood", tuple(c * 0.7 for c in wood), wood, scale=5, rough=0.6, bump=0.2,
                                     voronoi=False))
    bx.parent = root
    gm = mat_bronze(name + "_brassm", brass, rough=0.3)
    for k, sx in enumerate((-1, 1)):
        g = L.prim("cyl", loc=(sx * 0.36, 0, 0.62), rot=(0, math.pi / 2, 0), vertices=12, radius=0.07, depth=0.06,
                   name=name + "_gauge")
        L.assign(g, gm)
        g.parent = root
    iron = L.mat_principled(name + "_iron", (0.06, 0.06, 0.065), rough=0.5, metal=0.6)
    wheels = []
    for k, sx in enumerate((-1, 1)):
        hub = L.link(bpy.data.objects.new(f"{name}_wheel{k}", None))
        hub.parent = root
        hub.location = (sx * 0.42, 0, 0.45)
        hub.rotation_euler = (0, math.pi / 2, 0)
        sp = L.link(bpy.data.objects.new(f"{name}_spin{k}", None))
        sp.parent = hub
        rim = L.prim("torus", loc=(0, 0, 0), major_radius=0.38, minor_radius=0.025, major_segments=32, minor_segments=8,
                     name=f"{name}_rim{k}")
        L.assign(rim, iron)
        rim.parent = sp
        for s in range(4):
            a = math.pi * s / 4
            spk = L.prim("cube", loc=(0, 0, 0), rot=(0, 0, a), name=f"{name}_spk{k}")
            spk.scale = (0.37, 0.012, 0.012)
            L.assign(spk, iron)
            spk.parent = sp
        hd = L.prim("cyl", loc=(0.36, 0, sx * 0.12), vertices=8, radius=0.02, depth=0.22, name=f"{name}_handle{k}")
        L.assign(hd, L.mat_principled(name + "_hw", (0.3, 0.2, 0.1), rough=0.6))
        hd.parent = sp
        wheels.append(sp)
    return {"root": root, "wheels": wheels}


# ============================================================================= SCUBA-08 additions (Endurance)
# Added by the SCUBA-08 director. New functions only; nothing above was changed.

BQ_HL = 22.0          # barquentine half length (bow +X)
BQ_HB = 3.8           # half beam


def bq_hw(t):
    f = 0.6 + 0.4 * min(1.0, t / 0.12) if t < 0.12 else (1.0 if t < 0.55 else max(0.02, 1 - ((t - 0.55) / 0.45) ** 2.2) ** 0.7)
    return BQ_HB * f


def bq_top(t):
    return 2.6 + 1.2 * (2 * t - 1) ** 2 * (1.0 if t > 0.5 else 0.7)


def mat_ship_wood(name="shipwood", c1=(0.035, 0.025, 0.015), c2=(0.2, 0.14, 0.08), seam=0.24, silt=0.0):
    """Planked hull wood: streaky noise + dark horizontal seams by object Z; silt > 0 dusts upward faces grey."""
    m, n, l = _m(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.25, 0.25, 4.0)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 6
    l.new(mp.outputs[0], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (*c2, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sep.inputs[0])
    dv = n.new("ShaderNodeMath"); dv.operation = "DIVIDE"; dv.inputs[1].default_value = seam
    l.new(sep.outputs["Z"], dv.inputs[0])
    fr = n.new("ShaderNodeMath"); fr.operation = "FRACT"
    l.new(dv.outputs[0], fr.inputs[0])
    lt = n.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.1
    l.new(fr.outputs[0], lt.inputs[0])
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"
    mx.inputs["B"].default_value = (0.004, 0.003, 0.002, 1)
    sc = n.new("ShaderNodeMath"); sc.operation = "MULTIPLY"; sc.inputs[1].default_value = 0.75
    l.new(lt.outputs[0], sc.inputs[0])
    l.new(sc.outputs[0], mx.inputs["Factor"])
    l.new(ramp.outputs["Color"], mx.inputs["A"])
    out = mx.outputs["Result"]
    if silt:
        geo = n.new("ShaderNodeNewGeometry")
        s2 = n.new("ShaderNodeSeparateXYZ")
        l.new(geo.outputs["Normal"], s2.inputs[0])
        mr = n.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.5
        mr.inputs["From Max"].default_value = 0.95
        mr.inputs["To Max"].default_value = silt
        l.new(s2.outputs["Z"], mr.inputs["Value"])
        m2 = n.new("ShaderNodeMix"); m2.data_type = "RGBA"
        m2.inputs["B"].default_value = (0.3, 0.3, 0.27, 1)
        l.new(mr.outputs["Result"], m2.inputs["Factor"])
        l.new(out, m2.inputs["A"])
        out = m2.outputs["Result"]
    l.new(out, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.7
    bp = n.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.4
    l.new(nz.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def _cyl_between(a, b, r, mat, name, parent=None, r2=None, verts=10):
    a, b = Vector(a), Vector(b)
    d = b - a
    o = L.prim("cone", loc=(a + b) / 2, vertices=verts, radius1=r, radius2=r if r2 is None else r2, depth=d.length, name=name)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    L.assign(o, mat)
    if parent:
        o.parent = parent
    return o


def anemone(loc, scale=1.0, color=(0.95, 0.8, 0.75), parent=None, name="anem", seed=1):
    """Small pale sea anemone: stalk + crown of short tentacles (generic)."""
    rnd = random.Random(seed)
    m = L.mat_principled(name + "_m", color, rough=0.6, emit=color, emit_strength=0.12)
    root = L.link(bpy.data.objects.new(name, None))
    root.location = loc
    root.scale = (scale,) * 3
    st = L.prim("cyl", loc=(0, 0, 0.06), vertices=8, radius=0.035, depth=0.12, name=name + "_s")
    L.assign(st, m); st.parent = root
    for k in range(14):
        a = 2 * math.pi * k / 14
        tl = 0.95 if k % 2 else 0.6
        t = L.prim("cone", loc=(0.05 * tl * math.cos(a), 0.05 * tl * math.sin(a), 0.13 + 0.03 * (1 - tl)), vertices=5, radius1=0.009,
                   radius2=0.002, depth=0.1, name=name + "_t")
        t.rotation_euler = (-tl * math.sin(a) + rnd.uniform(-0.1, 0.1), tl * math.cos(a), 0)
        L.assign(t, m); t.parent = root
    if parent:
        root.parent = parent
    return root


def stern_name(text="ENDURANCE", size=0.5, radius=4.5, star=0.46, gold=(0.85, 0.62, 0.2), name="sternname"):
    """Arc of raised capital letters with a five-pointed star beneath, in the local XY plane of the returned empty
    (letters face local +Z). Returns (root, material)."""
    m = L.mat_principled(name + "_gold", gold, rough=0.35, metal=0.8, emit=gold, emit_strength=0.25)
    root = L.link(bpy.data.objects.new(name, None))
    fp = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    step = size * 0.86 / radius
    k0 = (len(text) - 1) / 2
    import os
    for i, ch in enumerate(text):
        th = (i - k0) * step
        t = L.text3d(ch, loc=(radius * math.sin(th), radius * math.cos(th) - radius, 0), rot=(0, 0, -th), size=size,
                     extrude=0.025, mat=m, font=fp if os.path.exists(fp) else None, name=f"{name}_{i}")
        t.data.align_y = "CENTER"
        t.parent = root
    bm = bmesh.new()
    vs = []
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        r = star if k % 2 == 0 else star * 0.4
        vs.append(bm.verts.new((r * math.cos(a), r * math.sin(a) - size * 2.3, 0)))
    bm.faces.new(vs)
    st = L.mesh_from_bm(name + "_star", bm)
    so = st.modifiers.new("solid", "SOLIDIFY"); so.thickness = 0.05; so.offset = 1.0
    L.assign(st, m)
    st.parent = root
    return root, m


def barquentine(name="bq", wreck=False, silt=0.0, anemones=0, seed=3):
    """Simple three-masted wooden barquentine, ~44 m, bow +X, root at the waterline centre (keel z = -3.4, deck ~+1.9).
    wreck=False: standing masts, yards on the foremast, gaffs, bowsprit, rigging. wreck=True: mast stumps, spars
    fallen across the deck, draped lines. The flat stern carries ENDURANCE in an arc with a star beneath.
    Returns dict(root, hull, yard (a foremast yard to key), masts, name_root, stern_x, deck_z)."""
    rnd = random.Random(seed)
    root = L.link(bpy.data.objects.new(name, None))
    P = {"root": root, "masts": []}
    wood = mat_ship_wood(name + "_wood", silt=silt)
    sec = [(1.0, 1.0), (1.0, 0.5), (0.98, 0.0), (0.92, -0.35), (0.76, -0.65), (0.48, -0.88), (0.16, -1.0), (0.0, -1.0)]
    N = 36
    sts = []
    for i in range(N + 1):
        t = i / N
        x = -BQ_HL + 2 * BQ_HL * t
        hw, top = bq_hw(t), bq_top(t)
        kz = 3.4 * (1 - 0.6 * max(0.0, (t - 0.85) / 0.15) ** 1.5) * (1 - 0.5 * max(0.0, (0.1 - t) / 0.1))
        ring = [(fy, top * fz if fz > 0 else kz * fz) for fy, fz in sec]
        full = [(x, hw * fy, z) for fy, z in ring] + [(x, -hw * fy, z) for fy, z in reversed(ring[:-1])]
        sts.append(full)
    hull = _loft(name + "_hull", sts)
    L.smooth(hull)
    L.assign(hull, wood)
    hull.parent = root
    P["hull"] = hull
    bm = bmesh.new()
    prev = None
    for i in range(N + 1):
        t = i / N
        x = -BQ_HL + 2 * BQ_HL * t
        hw = bq_hw(t) * 0.97
        a, b = bm.verts.new((x, -hw, bq_top(t) - 0.9)), bm.verts.new((x, hw, bq_top(t) - 0.9))
        if prev:
            bm.faces.new((prev[0], a, b, prev[1]))
        prev = (a, b)
    deck = L.mesh_from_bm(name + "_deck", bm)
    L.assign(deck, L.mat_noise_surface(name + "_deckm", (0.1, 0.08, 0.055), (0.3 if not silt else 0.26, 0.25, 0.2), scale=5, bump=0.3,
                                       voronoi=False))
    deck.parent = root
    dz = bq_top(0.5) - 0.9
    P["deck_z"] = dz
    dark = L.mat_principled(name + "_dark", (0.05, 0.04, 0.03), rough=0.7)
    for (x, sx, sy, sz) in ((-9.0, 3.2, 1.9, 0.9), (2.5, 1.6, 1.2, 0.35), (10.5, 1.2, 1.0, 0.3)):
        b = L.prim("cube", loc=(x, 0, dz + sz), name=name + "_house")
        b.scale = (sx, sy, sz)
        L.assign(b, wood if sz > 0.5 else dark)
        b.parent = root
    spar = L.mat_noise_surface(name + "_spar", (0.1, 0.07, 0.04), (0.3, 0.22, 0.13), scale=8, bump=0.2, voronoi=False)
    rope = L.mat_principled(name + "_rope", (0.12, 0.1, 0.07), rough=0.9)
    mast_x = ((9.0, 24.0), (-2.0, 25.0), (-12.5, 20.0))
    bow = Vector((BQ_HL - 0.5, 0, bq_top(1.0) - 0.2))
    tip = bow + Vector((8.0, 0, 2.2))
    if not wreck:
        _cyl_between(bow - Vector((3, 0, 0.4)), tip, 0.2, spar, name + "_bowsprit", root, r2=0.08)
        lines = []
        for k, (mx, ht) in enumerate(mast_x):
            top = Vector((mx, 0, dz + ht))
            P["masts"].append(_cyl_between((mx, 0, dz - 0.5), top, 0.24, spar, f"{name}_mast{k}", root, r2=0.08))
            for sy in (-1, 1):
                for dx in (-1.6, -0.6, 0.5):
                    t = (mx + dx + BQ_HL) / (2 * BQ_HL)
                    lines.append([(mx, sy * 0.1, dz + ht * 0.78), (mx + dx, sy * bq_hw(t), bq_top(t))])
            if k == 0:
                for j, (z, ln) in enumerate(((7.5, 13.0), (12.5, 10.5), (17.0, 8.0))):
                    y = _cyl_between((mx + 0.3, -ln / 2, dz + z), (mx + 0.3, ln / 2, dz + z), 0.1, spar, f"{name}_yard{j}", root)
                    f = _cyl_between((mx + 0.45, -ln * 0.42, dz + z - 0.2), (mx + 0.45, ln * 0.42, dz + z - 0.2), 0.2,
                                     L.mat_principled(name + "_furl", (0.5, 0.48, 0.42), rough=0.9), f"{name}_furl{j}", root)
                    if j == 1:
                        piv = L.link(bpy.data.objects.new(name + "_yardpiv", None))
                        piv.parent = root
                        piv.location = (mx + 0.3, 0, dz + z)
                        for o in (y, f):
                            o.parent = piv
                            o.location = Vector(o.location) - Vector(piv.location)
                        P["yard"] = piv
                lines.append([tuple(top), tuple(tip)])
                lines.append([(mx, 0, dz + ht * 0.6), tuple(tip - Vector((2, 0, 0.5)))])
            else:
                _cyl_between((mx - 0.3, 0, dz + 3.0), (mx - 8.0, 0, dz + 3.5), 0.1, spar, f"{name}_boom{k}", root)
                _cyl_between((mx - 0.3, 0, dz + ht * 0.55), (mx - 6.0, 0, dz + ht * 0.72), 0.09, spar, f"{name}_gaff{k}", root)
                lines.append([tuple(top), (mast_x[k - 1][0], 0, dz + mast_x[k - 1][1] * 0.8)])
        for i, ln in enumerate(lines):
            polyline(ln, rope, width=0.025, name=f"{name}_rig{i}").parent = root
    else:
        for k, (mx, ht) in enumerate(mast_x):
            sh = rnd.uniform(1.8, 4.0)
            P["masts"].append(_cyl_between((mx, 0, dz - 0.5), (mx + rnd.uniform(-0.3, 0.3), rnd.uniform(-0.2, 0.2), dz + sh), 0.24,
                                           spar, f"{name}_stump{k}", root, r2=0.2))
            ang = rnd.uniform(-0.5, 0.5)
            ln = ht * 0.55
            a = Vector((mx + 1.0, -math.copysign(1.5, ang or 1), dz + 0.5))
            b = a + Vector((math.cos(ang) * ln * -0.9, math.sin(ang) * ln + (3.5 if k % 2 else -3.5), 1.4))
            _cyl_between(a, b, 0.2, spar, f"{name}_fallen{k}", root, r2=0.1)
            c = Vector((mx - 2.5, 0, dz + 0.6))
            _cyl_between(c + Vector((0, -4.5, 0.2)), c + Vector((1.0, 4.8, 0.9)), 0.1, spar, f"{name}_spar{k}", root)
            t = (mx + BQ_HL) / (2 * BQ_HL)
            for sy in (-1, 1):
                polyline([(mx, 0, dz + sh), (mx + 1.0, sy * bq_hw(t) * 0.6, dz + 0.9), (mx + 2.5, sy * bq_hw(t), bq_top(t) + 0.05),
                          (mx + 3.0, sy * (bq_hw(t) + 0.15), bq_top(t) - 1.6)], rope, width=0.03, name=f"{name}_drape{k}").parent = root
        _cyl_between(bow - Vector((3, 0, 0.4)), bow + Vector((2.5, 0.3, 0.5)), 0.2, spar, name + "_bowstump", root, r2=0.16)
    nr, nm = stern_name(name=name + "_name")
    nr.parent = root
    nr.location = (-BQ_HL - 0.03, 0, 2.55)
    nr.rotation_euler = (math.pi / 2, 0, -math.pi / 2)
    P["name_root"], P["name_mat"] = nr, nm
    P["stern_x"] = -BQ_HL
    for k in range(anemones):
        t = rnd.uniform(0.0, 0.95)
        sy = rnd.choice((-1, 1))
        x = -BQ_HL + 2 * BQ_HL * t
        if rnd.random() < 0.3:
            loc = (-BQ_HL + rnd.uniform(0.2, 1.5), rnd.uniform(-2.0, 2.0), bq_top(0.02) + 0.0)
        else:
            loc = (x, sy * bq_hw(t) * 0.99, bq_top(t) + 0.02)
        anemone(loc, scale=rnd.uniform(1.0, 1.8), color=rnd.choice(((0.8, 0.62, 0.56), (0.85, 0.5, 0.42), (0.75, 0.7, 0.62))),
                parent=root, name=f"{name}_an{k}", seed=k)
    return P


def auv_torpedo(name="auv", length=3.5, color=(0.95, 0.7, 0.05), lamp=900):
    """Generic torpedo-shaped survey robot (nose +Y): cylinder body, rounded nose, cross tail fins, prop, nose lamp."""
    root = L.link(bpy.data.objects.new(name, None))
    yel = mat_paint(name + "_yel", color, rough=0.4)
    dark = L.mat_principled(name + "_dk", (0.03, 0.03, 0.035), rough=0.5)
    r = length * 0.075
    b = L.prim("cyl", loc=(0, 0, 0), rot=(math.pi / 2, 0, 0), vertices=20, radius=r, depth=length * 0.8, name=name + "_body")
    n = L.prim("sphere", loc=(0, length * 0.4, 0), segments=20, ring_count=10, radius=r, name=name + "_nose")
    n.scale = (1, 1.8, 1)
    t = L.prim("cone", loc=(0, -length * 0.47, 0), rot=(math.pi / 2, 0, 0), vertices=20, radius1=r * 0.35, radius2=r, depth=length * 0.14,
               name=name + "_tail")
    for o in (b, n, t):
        L.assign(o, yel); L.smooth(o); o.parent = root
    for k in range(4):
        f = L.prim("cube", loc=(0, -length * 0.45, 0), name=name + "_fin")
        f.scale = (0.012, length * 0.06, r * 1.9)
        f.rotation_euler = (0, k * math.pi / 4 * 2, 0) if k < 2 else (0, math.pi / 4 + k * math.pi / 2, 0)
        L.assign(f, dark); f.parent = root
    bd = L.prim("cyl", loc=(0, length * 0.1, 0), rot=(math.pi / 2, 0, 0), vertices=20, radius=r * 1.02, depth=length * 0.06, name=name + "_band")
    L.assign(bd, dark); bd.parent = root
    P = {"root": root}
    lens = L.prim("sphere", loc=(0, length * 0.4 + r * 1.7, 0), segments=10, ring_count=6, radius=r * 0.3, name=name + "_lens")
    lm = L.mat_emission(name + "_lensm", (0.85, 0.95, 1.0), 20)
    L.assign(lens, lm); lens.parent = root
    sp = L.spot((0, length * 0.4 + r * 2, 0), (math.pi / 2, 0, 0), energy=lamp, size_deg=40, blend=0.5, color=(0.85, 0.95, 1.0),
                parent=root, name=name + "_lamp")
    P.update({"lamp": sp, "lens_mat": lm})
    return P


def rov_drone(name="rov", color=(0.95, 0.68, 0.05), lamp=1500):
    """Generic hybrid underwater drone (nose +Y): flat rounded yellow body 3.5 x 1.1 x 0.6 m, four thruster pods,
    sensor dome, two forward/down lamps with fake beam cones. Returns dict(root, lamps, cones, lens_mat)."""
    root = L.link(bpy.data.objects.new(name, None))
    yel = mat_paint(name + "_yel", color, rough=0.4)
    dark = L.mat_principled(name + "_dk", (0.03, 0.03, 0.035), rough=0.5)
    b = L.prim("cube", loc=(0, 0, 0), name=name + "_body")
    b.scale = (0.55, 1.75, 0.3)
    L.bevel(b, 0.18, 3)
    L.assign(b, yel); b.parent = root
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = L.prim("cyl", loc=(sx * 0.68, sy * 1.0, 0), rot=(math.pi / 2, 0, 0), vertices=14, radius=0.17, depth=0.5, name=name + "_pod")
            L.assign(p, dark); p.parent = root
            a = L.prim("cube", loc=(sx * 0.58, sy * 1.0, 0), name=name + "_arm")
            a.scale = (0.08, 0.08, 0.05)
            L.assign(a, dark); a.parent = root
    dm = L.prim("sphere", loc=(0, 0.6, 0.3), segments=14, ring_count=8, radius=0.2, name=name + "_dome")
    L.assign(dm, dark); dm.parent = root
    sk = L.prim("cube", loc=(0, 0, -0.36), name=name + "_skid")
    sk.scale = (0.5, 1.2, 0.04)
    L.assign(sk, dark); sk.parent = root
    P = {"root": root, "lamps": [], "cones": []}
    lm = L.mat_emission(name + "_lensm", (0.85, 0.95, 1.0), 25)
    P["lens_mat"] = lm
    for sx in (-1, 1):
        ln = L.prim("sphere", loc=(sx * 0.3, 1.72, -0.12), segments=10, ring_count=6, radius=0.09, name=name + "_lens")
        L.assign(ln, lm); ln.parent = root
        d = Vector((sx * 0.08, 0.55, -0.83)).normalized()
        sp = L.spot((sx * 0.3, 1.8, -0.15), (0, 0, 0), energy=lamp, size_deg=38, blend=0.5, color=(0.85, 0.95, 1.0), parent=root,
                    name=name + "_lamp")
        sp.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        P["lamps"].append(sp)
        P["cones"].append(beam_cone((sx * 0.3, 1.8, -0.15), tuple(d), length=7, radius=2.2, color=(0.8, 0.93, 1.0), strength=1.4,
                                    alpha=0.3, name=name + "_cone", parent=root))
    return P


def ice_floes(size=(400, 600), cell=14.0, seed=2, gap=0.8, z=0.0, thick=0.6, keep=None, name="floes", jitter=0.35):
    """Broken sea ice as ONE mesh: an irregular polygon per jittered grid cell with dark leads between (lay it over a
    dark water plane). keep(x, y) -> bool drops floes (e.g. a ship's lane). Returns the object."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    nx, ny = int(size[0] / cell), int(size[1] / cell)
    for i in range(nx):
        for j in range(ny):
            cx = -size[0] / 2 + (i + 0.5 + rnd.uniform(-jitter, jitter) * 0.5) * cell
            cy = -size[1] / 2 + (j + 0.5 + rnd.uniform(-jitter, jitter) * 0.5) * cell
            if keep and not keep(cx, cy):
                continue
            k = rnd.randint(6, 9)
            a0 = rnd.uniform(0, 6.28)
            rr = (cell - gap) * 0.56
            top = [bm.verts.new((cx + math.cos(a0 + 2 * math.pi * q / k) * rr * rnd.uniform(0.72, 1.0),
                                 cy + math.sin(a0 + 2 * math.pi * q / k) * rr * rnd.uniform(0.72, 1.0), z + thick * 0.4)) for q in range(k)]
            bot = [bm.verts.new((v.co.x, v.co.y, z - thick * 0.6)) for v in top]
            bm.faces.new(top)
            for q in range(k):
                bm.faces.new((top[q], bot[q], bot[(q + 1) % k], top[(q + 1) % k]))
    o = L.mesh_from_bm(name, bm)
    L.assign(o, L.mat_noise_surface(name + "_m", (0.62, 0.68, 0.74), (0.92, 0.94, 0.96), scale=0.12, bump=0.25, voronoi=False, rough=0.6))
    return o
