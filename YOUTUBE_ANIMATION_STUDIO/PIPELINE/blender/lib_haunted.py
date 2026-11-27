"""Haunted-category builders (HAUNT-01 Enfield, HAUNT-02 Stanley Hotel).

Import from shots.py:
    import importlib, sys; sys.path.insert(0, <PIPELINE/blender>); import lib_haunted as H
All geometry procedural. Units metres, Z up. Uses studio_lib (L) helpers; never edits it.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion, Euler, Matrix, noise
import studio_lib as L

# ============================================================================ generic helpers

def eevee_quality(raytrace=False, shadows_hi=True):
    """Optional EEVEE tweaks (screen-space reflections for wet roads / glossy floors)."""
    e = bpy.context.scene.eevee
    for attr, val in (("use_raytracing", raytrace), ("use_shadows", True), ("volumetric_tile_size", "4"),
                      ("volumetric_samples", 48), ("volumetric_end", 80)):
        if hasattr(e, attr):
            try:
                setattr(e, attr, val)
            except Exception:
                pass


def empty(name, loc=(0, 0, 0), parent=None):
    o = L.link(bpy.data.objects.new(name, None))
    o.location = loc
    if parent:
        o.parent = parent
    return o


def box_mesh(name, boxes, mat=None, parent=None, bevel=0.0):
    """One mesh object made of many axis boxes. boxes: (cx,cy,cz,hx,hy,hz[,rz]) in metres (world/parent space)."""
    bm = bmesh.new()
    for b in boxes:
        cx, cy, cz, hx, hy, hz = b[:6]
        rz = b[6] if len(b) > 6 else 0.0
        c, s = math.cos(rz), math.sin(rz)
        vs = []
        for dx, dy, dz in ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)):
            x, y = dx * hx, dy * hy
            vs.append(bm.verts.new((cx + x * c - y * s, cy + x * s + y * c, cz + dz * hz)))
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            bm.faces.new([vs[i] for i in f])
    o = L.mesh_from_bm(name, bm)
    if mat:
        L.assign(o, mat)
    if parent:
        o.parent = parent
    if bevel:
        L.bevel(o, bevel, 1)
    return o


def aim(cam, loc, target, frame=None, roll=0.0):
    """Point camera from loc at target (no constraint, so handheld rotation noise works). Optionally keyframe."""
    cam.location = loc
    d = Vector(target) - Vector(loc)
    q = d.to_track_quat("-Z", "Y") @ Quaternion((0, 0, 1), roll)
    cam.rotation_euler = q.to_euler("XYZ", cam.rotation_euler)
    if frame is not None:
        cam.keyframe_insert("location", frame=frame)
        cam.keyframe_insert("rotation_euler", frame=frame)
    return cam


def cam(loc, target, lens=28, roll=0.0, name="cam"):
    c = bpy.data.cameras.new(name)
    c.lens = lens
    c.clip_start = 0.03
    c.clip_end = 600
    c.sensor_fit = "AUTO"
    o = L.link(bpy.data.objects.new(name, c))
    bpy.context.scene.camera = o
    aim(o, loc, target, roll=roll)
    return o


def cam_move(cam_o, keys, ease=True):
    """keys: [(frame, loc, target[, roll][, lens])] keyframed location+rotation (+lens)."""
    for k in keys:
        f, loc, tgt = k[0], k[1], k[2]
        roll = k[3] if len(k) > 3 and k[3] is not None else 0.0
        aim(cam_o, loc, tgt, frame=f, roll=roll)
        if len(k) > 4 and k[4]:
            cam_o.data.lens = k[4]
            cam_o.data.keyframe_insert("lens", frame=f)
    if not ease:
        L.linear_fcurves(cam_o)
    return cam_o


def handheld(cam_o, nframes, amp=0.02, rate=0.6, seed=3, rot_amp=0.008):
    """Like L.handheld but never overwrites existing frame-1 keys (L.handheld re-keys rotation at frame 1)."""
    ad = cam_o.animation_data
    have = set()
    if ad and ad.action:
        have = {fc.data_path for fc in L._fcurves(ad.action)}
    if "location" not in have:
        cam_o.keyframe_insert("location", frame=1)
    if "rotation_euler" not in have:
        cam_o.keyframe_insert("rotation_euler", frame=1)
    for fc in L._fcurves(cam_o.animation_data.action):
        if fc.data_path in ("location", "rotation_euler"):
            m = fc.modifiers.new("NOISE")
            m.scale = 24 / max(0.05, rate)
            m.strength = amp * 2 if fc.data_path == "location" else rot_amp * 2
            m.phase = seed * 13 + fc.array_index * 7
            m.blend_type = "ADD"


def key_energy(light_o, pairs, interp="CONSTANT"):
    """pairs: [(frame, energy)]"""
    for f, e in pairs:
        light_o.data.energy = e
        light_o.data.keyframe_insert("energy", frame=f)
    _interp_data(light_o.data, interp)


def _interp_data(idb, mode):
    ad = idb.animation_data
    if ad and ad.action:
        for fc in L._fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = mode


def key_emission(mat, pairs, interp="CONSTANT"):
    """Animate emission strength of an L.mat_emission material (node 'Emission') or principled."""
    nt = mat.node_tree
    node = next((n for n in nt.nodes if n.type == "EMISSION"), None)
    sock = node.inputs[1] if node else nt.nodes["Principled BSDF"].inputs["Emission Strength"]
    for f, v in pairs:
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=f)
    _interp_data(nt, interp)


def key_vis(objs, pairs):
    """pairs [(frame, visible_bool)] -> hide_render keyframes (constant)."""
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    for o in objs:
        for f, v in pairs:
            o.hide_render = not v
            o.keyframe_insert("hide_render", frame=f)
            o.hide_viewport = not v
            o.keyframe_insert("hide_viewport", frame=f)


def flicker_mat_with_light(light_o, mat, nframes, base_e, base_m, seed=1, depth=0.6, rate=0.35, blackouts=()):
    """Flicker a light and a matching emissive material together."""
    rnd = random.Random(seed)
    nt = mat.node_tree
    node = next((n for n in nt.nodes if n.type == "EMISSION"), None)
    sock = node.inputs[1] if node else nt.nodes["Principled BSDF"].inputs["Emission Strength"]
    for f in range(1, nframes + 1, 2):
        k = 1 - depth * max(0, noise.noise(Vector((f * rate, seed, 0)))) - depth * 0.3 * rnd.random()
        if any(a <= f <= b for a, b in blackouts):
            k = 0.0
        light_o.data.energy = max(0.0, base_e * k)
        light_o.data.keyframe_insert("energy", frame=f)
        sock.default_value = max(0.0, base_m * k)
        sock.keyframe_insert("default_value", frame=f)
    _interp_data(light_o.data, "CONSTANT")
    _interp_data(nt, "CONSTANT")


def spin(obj, nframes, revs_per_s, axis=2, start=1):
    fps = bpy.context.scene.render.fps
    r = list(obj.rotation_euler)
    obj.keyframe_insert("rotation_euler", index=axis, frame=start)
    r[axis] += 2 * math.pi * revs_per_s * (nframes - start + 1) / fps
    obj.rotation_euler = r
    obj.keyframe_insert("rotation_euler", index=axis, frame=nframes + 1)
    L.linear_fcurves(obj)


def dust(center, size, n, count=500, radius=0.004, drift=(0.0, 0.0, 0.01), emit=0.08, seed=7, name="dust"):
    m = L.mat_principled(name + "_m", (0.8, 0.78, 0.7), rough=1, emit=(0.6, 0.58, 0.5), emit_strength=emit)
    return L.particle_cloud(center, size, count=count, radius=radius, mat=m, drift=drift, seed=seed, nframes=n, name=name)


def room_fog(center, size, density=0.02, color=(0.6, 0.65, 0.75), anis=0.5, name="roomfog"):
    o = L.prim("cube", loc=center, name=name)
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    L.assign(o, L.mat_volume(name + "_m", color, density, anis))
    return o

# ============================================================================ materials

def _nodes(name):
    return L._mat(name)


def _ramp(n, stops, interp="LINEAR"):
    r = n.new("ShaderNodeValToRGB")
    r.color_ramp.interpolation = interp
    els = r.color_ramp.elements
    els[0].position = stops[0][0]
    els[0].color = (*stops[0][1], 1)
    els[1].position = stops[-1][0]
    els[1].color = (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        e = els.new(p)
        e.color = (*c, 1)
    return r


def _math(n, l, op, a, b=None, val=None):
    m = n.new("ShaderNodeMath")
    m.operation = op
    if isinstance(a, (int, float)):
        m.inputs[0].default_value = a
    else:
        l.new(a, m.inputs[0])
    if b is not None:
        if isinstance(b, (int, float)):
            m.inputs[1].default_value = b
        else:
            l.new(b, m.inputs[1])
    return m.outputs[0]


def _wall_uv(n, l):
    """World-space (along-wall, up) coordinate so patterns run correctly on X- or Y-aligned walls."""
    g = n.new("ShaderNodeNewGeometry")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(g.outputs["Position"], sep.inputs[0])
    u = _math(n, l, "ADD", sep.outputs[0], sep.outputs[1])
    comb = n.new("ShaderNodeCombineXYZ")
    l.new(u, comb.inputs[0])
    l.new(sep.outputs[2], comb.inputs[1])
    return comb.outputs[0], u, sep.outputs[2], g.outputs["Position"]


def mat_wallpaper(name="wallpaper", base=(0.34, 0.28, 0.15), stripe=(0.22, 0.16, 0.08), flower=(0.52, 0.3, 0.12),
                  leaf=(0.2, 0.24, 0.1), freq=4.0, fscale=5.0, rough=0.8):
    """1970s floral wallpaper: vertical stripes + scattered 'flower' dots + age blotches."""
    m, n, l = _nodes(name)
    p = n["Principled BSDF"]
    uv, u, z, pos = _wall_uv(n, l)
    s = _math(n, l, "SINE", _math(n, l, "MULTIPLY", u, freq * 2 * math.pi))
    stripe_v = _math(n, l, "MULTIPLY", _math(n, l, "ADD", s, 1.0), 0.22)  # 0..0.44
    vr = n.new("ShaderNodeTexVoronoi")
    vr.inputs["Scale"].default_value = fscale
    l.new(uv, vr.inputs["Vector"])
    fl = _math(n, l, "SUBTRACT", 1.0, _math(n, l, "MULTIPLY", vr.outputs["Distance"], 4.2))  # 1 at centre
    fl = _math(n, l, "MAXIMUM", fl, 0.0)
    val = _math(n, l, "MAXIMUM", stripe_v, fl)
    ramp = _ramp(n, [(0.0, base), (0.36, base), (0.43, stripe), (0.5, leaf), (0.62, flower), (1.0, flower)])
    l.new(val, ramp.inputs[0])
    # age blotch multiply via second noise -> value into bsdf through a mix
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.4
    l.new(pos, nz.inputs["Vector"])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 0.6
    l.new(ramp.outputs[0], mix.inputs[6])
    r2 = _ramp(n, [(0.35, (0.55, 0.5, 0.45)), (0.7, (1, 1, 1))])
    l.new(nz.outputs["Fac"], r2.inputs[0])
    l.new(r2.outputs[0], mix.inputs[7])
    l.new(mix.outputs[2], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    return m


def mat_brick(name="brick", c1=(0.25, 0.09, 0.05), c2=(0.36, 0.15, 0.08), mortar=(0.32, 0.3, 0.27), scale=4.4, rough=0.85, wet=False):
    m, n, l = _nodes(name)
    p = n["Principled BSDF"]
    uv, u, z, pos = _wall_uv(n, l)
    b = n.new("ShaderNodeTexBrick")
    b.inputs["Color1"].default_value = (*c1, 1)
    b.inputs["Color2"].default_value = (*c2, 1)
    b.inputs["Mortar"].default_value = (*mortar, 1)
    b.inputs["Scale"].default_value = scale
    b.inputs["Mortar Size"].default_value = 0.015
    b.inputs["Brick Width"].default_value = 0.5
    b.inputs["Row Height"].default_value = 0.25
    l.new(uv, b.inputs["Vector"])
    l.new(b.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.45 if wet else rough
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.4
    l.new(b.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_wet_road(name="wetroad"):
    m = L.mat_noise_surface(name, (0.012, 0.012, 0.014), (0.05, 0.05, 0.055), scale=18, bump=0.15, voronoi=False, rough=0.18)
    return m


def mat_carpet(name="carpet", c1=(0.08, 0.045, 0.022), c2=(0.17, 0.1, 0.05)):
    return L.mat_noise_surface(name, c1, c2, scale=60, bump=0.25, voronoi=False, rough=1.0)


def mat_hotel_carpet(name="hotelcarpet", red=(0.16, 0.018, 0.015), dark=(0.06, 0.008, 0.008), gold=(0.42, 0.24, 0.06),
                     orange=(0.45, 0.12, 0.03), k=2.2):
    """Dark red carpet with interlocking gold diamond lattice + centre lozenges (procedural, world XY)."""
    m, n, l = _nodes(name)
    p = n["Principled BSDF"]
    g = n.new("ShaderNodeNewGeometry")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(g.outputs["Position"], sep.inputs[0])
    def tri(v):
        fr = _math(n, l, "FRACT", _math(n, l, "MULTIPLY", v, k))
        return _math(n, l, "ABSOLUTE", _math(n, l, "SUBTRACT", fr, 0.5))
    d = _math(n, l, "ADD", tri(sep.outputs[0]), tri(sep.outputs[1]))  # 0..1 diamond distance
    ramp = _ramp(n, [(0.0, orange), (0.09, orange), (0.1, dark), (0.16, red), (0.44, red), (0.45, gold), (0.52, gold),
                     (0.53, dark), (0.6, red), (1.0, dark)], interp="CONSTANT")
    l.new(d, ramp.inputs[0])
    l.new(ramp.outputs[0], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.95
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 300
    l.new(g.outputs["Position"], nz.inputs["Vector"])
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.2
    l.new(nz.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_cork(name="cork"):
    return L.mat_noise_surface(name, (0.22, 0.13, 0.06), (0.42, 0.28, 0.14), scale=90, bump=0.5, voronoi=True, rough=0.9)


def mat_paper(name="paper", c=(0.78, 0.74, 0.62), emit=0.0):
    return L.mat_principled(name, c, rough=0.9, emit=c if emit else None, emit_strength=emit)


def mat_net_curtain(name="net", color=(0.85, 0.8, 0.7), alpha=0.5, emit=0.6):
    m = L.mat_principled(name, color, rough=1.0, emit=(1.0, 0.75, 0.45), emit_strength=emit, alpha=alpha)
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    return m


def mat_glass_dark(name="glass_dark", tint=(0.01, 0.012, 0.016)):
    return L.mat_principled(name, tint, rough=0.05, metal=0.3)


def mat_brass(name="brass"):
    return L.mat_principled(name, (0.62, 0.42, 0.14), rough=0.28, metal=1.0)

# ============================================================================ architecture

def wall_with_openings(name, axis, fixed, length, h, openings=(), t=0.1, mat=None, outward=1):
    """Wall plane along `axis` ('x' or 'y') at coordinate `fixed` on the other axis, centred on 0.
    openings: [(centre_along, width, bottom, top)]. Wall thickness extends outward*t beyond `fixed`."""
    boxes = []
    cur = -length / 2
    off = fixed + outward * t / 2
    def add(a0, a1, z0, z1):
        if a1 - a0 < 1e-4 or z1 - z0 < 1e-4:
            return
        ca, ha = (a0 + a1) / 2, (a1 - a0) / 2
        cz, hz = (z0 + z1) / 2, (z1 - z0) / 2
        if axis == "x":
            boxes.append((ca, off, cz, ha, t / 2, hz))
        else:
            boxes.append((off, ca, cz, t / 2, ha, hz))
    for c, w, b, tp in sorted(openings):
        a0, a1 = c - w / 2, c + w / 2
        add(cur, a0, 0, h)
        add(a0, a1, 0, b)
        add(a0, a1, tp, h)
        cur = a1
    add(cur, length / 2, 0, h)
    return box_mesh(name, boxes, mat)


def window_frame(name, axis, fixed, centre, width, bottom, top, mat=None, depth=0.08, bars=True, sash=True):
    """White-painted sash window frame filling an opening."""
    mat = mat or L.mat_principled(name + "_m", (0.75, 0.73, 0.68), rough=0.5)
    fw = 0.05
    boxes = []
    def B(ca, cz, ha, hz):
        if axis == "x":
            boxes.append((ca, fixed, cz, ha, depth / 2, hz))
        else:
            boxes.append((fixed, ca, cz, depth / 2, ha, hz))
    hw = width / 2
    B(centre - hw + fw / 2, (bottom + top) / 2, fw / 2, (top - bottom) / 2)
    B(centre + hw - fw / 2, (bottom + top) / 2, fw / 2, (top - bottom) / 2)
    B(centre, bottom + fw / 2, hw, fw / 2)
    B(centre, top - fw / 2, hw, fw / 2)
    if sash:
        B(centre, (bottom + top) / 2, hw, 0.03)
    if bars:
        B(centre, (bottom + top) / 2, 0.012, (top - bottom) / 2)
    # sill
    if axis == "x":
        boxes.append((centre, fixed, bottom - 0.03, hw + 0.08, depth / 2 + 0.06, 0.03))
    else:
        boxes.append((fixed, centre, bottom - 0.03, depth / 2 + 0.06, hw + 0.08, 0.03))
    return box_mesh(name, boxes, mat)


def curtain(name, centre, width, height, top_z, axis="x", fixed=0.0, folds=7, depth=0.05, mat=None, sway_frames=0, seed=1):
    """Pleated curtain (bmesh grid with sinusoidal folds), hanging from top_z."""
    bm = bmesh.new()
    nu, nv = folds * 6, 8
    rnd = random.Random(seed)
    grid = []
    for j in range(nv + 1):
        row = []
        z = top_z - height * j / nv
        for i in range(nu + 1):
            a = -width / 2 + width * i / nu
            d = depth * math.sin(i / nu * folds * 2 * math.pi) * (1 + 0.3 * j / nv)
            if axis == "x":
                co = (centre + a, fixed + d, z)
            else:
                co = (fixed + d, centre + a, z)
            row.append(bm.verts.new(co))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    o = L.mesh_from_bm(name, bm)
    L.smooth(o)
    L.assign(o, mat or L.mat_principled(name + "_m", (0.3, 0.22, 0.14), rough=1.0))
    return o


def door_slab(name, hinge, width=0.8, height=2.0, angle=0.0, axis="x", mat=None, thick=0.04, panels=True):
    """Door with hinge pivot empty. axis: wall direction. Door extends +along axis from hinge when angle=0."""
    piv = empty(name + "_hinge", hinge)
    mat = mat or L.mat_principled(name + "_m", (0.55, 0.5, 0.42), rough=0.6)
    boxes = [(width / 2, 0, height / 2, width / 2, thick / 2, height / 2)]
    if panels:
        for zc in (0.55, 1.45):
            boxes.append((width / 2, -thick / 2 - 0.006, zc, width * 0.36, 0.006, 0.36))
            boxes.append((width / 2, thick / 2 + 0.006, zc, width * 0.36, 0.006, 0.36))
    d = box_mesh(name, boxes, mat, parent=piv)
    knob = L.prim("sphere", loc=(width - 0.08, 0, 1.0), segments=10, ring_count=6, radius=0.03)
    L.assign(knob, mat_brass(name + "_knob"))
    knob.scale = (1, 2.2, 1)
    knob.parent = piv
    piv.rotation_euler = (0, 0, (0 if axis == "x" else math.pi / 2) + angle)
    return piv, d

# ============================================================================ props (shared)

def tape_recorder(loc=(0, 0, 0), rot_z=0.0, n=100, spin_from=1, spin_rate=0.55, rec_on=True, rec_on_frame=None,
                  reels_spin=True, name="rec", rec_strength=60.0):
    """Reel-to-reel recorder 40x25x12 cm: grey case, brushed deck, two 18 cm reels, tape path, VU meter, red REC lamp.
    rec_on_frame: lamp pops on at that frame (and reels start) — for the S14-style reveal."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    case = L.mat_principled(name + "_case", (0.05, 0.055, 0.06), rough=0.45)
    deck = L.mat_principled(name + "_deck", (0.55, 0.56, 0.58), rough=0.32, metal=0.85)
    dark = L.mat_principled(name + "_dark", (0.01, 0.01, 0.012), rough=0.4)
    silver = L.mat_principled(name + "_reel", (0.8, 0.8, 0.82), rough=0.2, metal=1.0)
    tape = L.mat_principled(name + "_tape", (0.12, 0.06, 0.03), rough=0.35)
    keys = L.mat_principled(name + "_keys", (0.7, 0.68, 0.62), rough=0.4)
    body = box_mesh(name + "_body", [(0, 0, 0.058, 0.2, 0.125, 0.058)], case, parent=root, bevel=0.01)
    box_mesh(name + "_plate", [(0, 0.005, 0.1175, 0.19, 0.115, 0.002)], deck, parent=root)
    box_mesh(name + "_keys", [(-0.07 + 0.035 * i, -0.105, 0.112, 0.014, 0.012, 0.006) for i in range(5)], keys, parent=root)
    box_mesh(name + "_head", [(0, -0.06, 0.13, 0.03, 0.012, 0.012)], dark, parent=root)
    # tape path along the front between reels
    box_mesh(name + "_tape", [(0, -0.075, 0.128, 0.105, 0.0015, 0.005)], tape, parent=root)
    reels = []
    for i, (x, pack) in enumerate(((-0.1, 0.072), (0.1, 0.048))):
        piv = empty(f"{name}_reel{i}", (x, 0.015, 0.124), parent=root)
        d = L.prim("cyl", loc=(0, 0, 0.012), vertices=32, radius=0.09, depth=0.004)
        L.assign(d, silver)
        d.parent = piv
        pk = L.prim("cyl", loc=(0, 0, 0.007), vertices=32, radius=pack, depth=0.008)
        L.assign(pk, tape)
        pk.parent = piv
        hub = L.prim("cyl", loc=(0, 0, 0.016), vertices=12, radius=0.018, depth=0.01)
        L.assign(hub, dark)
        hub.parent = piv
        for k in range(3):
            a = k * 2 * math.pi / 3
            w = L.prim("cyl", loc=(0.055 * math.cos(a), 0.055 * math.sin(a), 0.0145), vertices=16, radius=0.024, depth=0.002)
            L.assign(w, dark)
            w.parent = piv
        reels.append(piv)
    # VU meter (amber glow) + needle
    vu_m = L.mat_emission(name + "_vu", (1.0, 0.62, 0.22), 2.5)
    vu = box_mesh(name + "_vu", [(0.135, -0.1, 0.121, 0.035, 0.014, 0.002)], vu_m, parent=root)
    needle_piv = empty(name + "_needle", (0.135, -0.112, 0.124), parent=root)
    nd = box_mesh(name + "_nd", [(0, 0.012, 0, 0.0012, 0.012, 0.001)], dark, parent=needle_piv)
    # REC lamp
    rec_m = L.mat_emission(name + "_recm", (1.0, 0.04, 0.02), rec_strength)
    lamp = L.prim("sphere", loc=(-0.16, -0.1, 0.124), segments=12, ring_count=8, radius=0.012)
    L.assign(lamp, rec_m)
    lamp.parent = root
    rl = L.point((0, 0, 0), energy=2.5, color=(1, 0.05, 0.02), radius=0.01, name=name + "_recl")
    rl.parent = root
    rl.location = (-0.16, -0.12, 0.15)
    out = {"root": root, "reels": reels, "rec_mat": rec_m, "rec_light": rl, "vu_mat": vu_m, "needle": needle_piv, "body": body}
    start = spin_from
    if rec_on_frame:
        key_emission(rec_m, [(1, 0.0), (rec_on_frame, rec_strength)])
        key_energy(rl, [(1, 0.0), (rec_on_frame, 2.5)])
        key_emission(vu_m, [(1, 0.0), (rec_on_frame, 2.5)])
        start = rec_on_frame
    elif not rec_on:
        key_emission(rec_m, [(1, 0.0)])
        rl.data.energy = 0
        vu_m.node_tree.nodes["Emission"].inputs[1].default_value = 0.0
        reels_spin = False
    if reels_spin:
        for i, r in enumerate(reels):
            if start > 1:
                r.keyframe_insert("rotation_euler", index=2, frame=1)
            spin(r, n, spin_rate * (1.0 if i == 0 else 1.45), start=start)
        # needle jitter
        rnd = random.Random(3)
        for f in range(start, n + 1, 3):
            needle_piv.rotation_euler = (0, 0, 0.6 - 1.0 * abs(noise.noise(Vector((f * 0.3, 1, 0)))) - 0.2 * rnd.random())
            needle_piv.keyframe_insert("rotation_euler", index=2, frame=f)
    else:
        needle_piv.rotation_euler = (0, 0, 0.6)
    return out


def bedside_lamp(loc, on=True, energy=25.0, color=(1.0, 0.72, 0.4), name="blamp", shade_col=(0.7, 0.55, 0.35)):
    root = empty(name, loc)
    base_m = L.mat_principled(name + "_base", (0.35, 0.25, 0.12), rough=0.3, metal=0.6)
    b = L.prim("cyl", loc=(0, 0, 0.015), vertices=16, radius=0.07, depth=0.03)
    L.assign(b, base_m)
    b.parent = root
    s = L.prim("cyl", loc=(0, 0, 0.15), vertices=8, radius=0.012, depth=0.26)
    L.assign(s, base_m)
    s.parent = root
    shade_m = L.mat_principled(name + "_shade", shade_col, rough=1.0, emit=color, emit_strength=(1.6 if on else 0.0))
    sh = L.prim("cone", loc=(0, 0, 0.32), vertices=24, radius1=0.15, radius2=0.08, depth=0.18, end_fill_type="NOTHING")
    L.assign(sh, shade_m)
    sh.parent = root
    li = L.point((0, 0, 0), energy=energy if on else 0.0, color=color, radius=0.04, name=name + "_l")
    li.parent = root
    li.location = (0, 0, 0.3)
    return {"root": root, "light": li, "shade_mat": shade_m}


def flicker_lamp(lamp, n, base_e, base_m=1.6, seed=2, depth=0.6, rate=0.35, blackouts=()):
    rnd = random.Random(seed)
    sock = lamp["shade_mat"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    li = lamp["light"]
    for f in range(1, n + 1, 2):
        k = 1 - depth * max(0, noise.noise(Vector((f * rate, seed, 0)))) - depth * 0.3 * rnd.random()
        if any(a <= f <= b for a, b in blackouts):
            k = 0.0
        li.data.energy = max(0, base_e * k)
        li.data.keyframe_insert("energy", frame=f)
        sock.default_value = max(0, base_m * k)
        sock.keyframe_insert("default_value", frame=f)
    _interp_data(li.data, "CONSTANT")
    _interp_data(lamp["shade_mat"].node_tree, "CONSTANT")


def single_bed(loc, rot_z=0.0, length=1.9, width=0.9, blanket=(0.32, 0.18, 0.12), rumple=0.035, seed=1, name="bed",
               duvet_on=True, frame_col=(0.18, 0.11, 0.06)):
    """Child's single bed: wooden frame + headboard, mattress, pillow, rumpled blanket. Head at +Y local."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    wood = L.mat_principled(name + "_wood", frame_col, rough=0.55)
    sheet = L.mat_principled(name + "_sheet", (0.62, 0.6, 0.55), rough=0.9)
    hw, hl = width / 2, length / 2
    box_mesh(name + "_frame", [(0, 0, 0.2, hw, hl, 0.08),
                               (0, hl + 0.02, 0.5, hw + 0.02, 0.025, 0.5),
                               (0, -hl - 0.02, 0.3, hw + 0.02, 0.025, 0.3)] +
             [(sx * (hw - 0.03), sy * (hl - 0.03), 0.1, 0.03, 0.03, 0.1) for sx in (-1, 1) for sy in (-1, 1)], wood, parent=root)
    box_mesh(name + "_mat", [(0, 0, 0.34, hw - 0.02, hl - 0.02, 0.07)], sheet, parent=root, bevel=0.03)
    pil = L.prim("cube", loc=(0, hl - 0.22, 0.45))
    pil.scale = (hw - 0.12, 0.15, 0.05)
    L.apply_scale(pil)
    L.bevel(pil, 0.04, 3)
    L.assign(pil, sheet)
    pil.parent = root
    out = {"root": root}
    if duvet_on:
        out["duvet"] = duvet((0, -0.12, 0.43), (hw + 0.04, hl - 0.25, 0.03), blanket, rumple, seed, name + "_duvet", parent=root,
                             drape=True)
    return out


def duvet(loc, half, col, rumple=0.04, seed=1, name="duvet", parent=None, drape=False):
    """Rumpled blanket: subdivided slab with noise displacement. drape=True bends edges down over the mattress."""
    bm = bmesh.new()
    hx, hy, hz = half
    nx, ny = 14, 20
    rnd = random.Random(seed)
    off = Vector((rnd.random() * 50, rnd.random() * 50, 0))
    grid = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            x = -hx + 2 * hx * i / nx
            y = -hy + 2 * hy * j / ny
            z = rumple * noise.noise(Vector((x * 3.2, y * 3.2, 0)) + off) + rumple * 0.5 * noise.noise(Vector((x * 8, y * 8, 1)) + off)
            if drape:
                ex = max(0.0, abs(x) - (hx - 0.1)) / 0.1
                z -= 0.18 * ex * ex
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    o = L.mesh_from_bm(name, bm)
    sol = o.modifiers.new("sol", "SOLIDIFY")
    sol.thickness = hz * 2
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 1
    L.smooth(o)
    L.assign(o, L.mat_noise_surface(name + "_m", tuple(c * 0.75 for c in col), col, scale=6, bump=0.2, voronoi=False, rough=1.0))
    o.location = loc
    if parent:
        o.parent = parent
    return o


def chest_of_drawers(loc, rot=(0, 0, 0), w=0.6, d=0.4, h=0.75, name="chest"):
    root = empty(name, loc)
    root.rotation_euler = rot
    wood = L.mat_principled(name + "_w", (0.22, 0.13, 0.06), rough=0.5)
    front = L.mat_principled(name + "_f", (0.28, 0.17, 0.08), rough=0.45)
    box_mesh(name + "_b", [(0, 0, h / 2, w / 2, d / 2, h / 2)], wood, parent=root, bevel=0.01)
    dh = (h - 0.08) / 3
    box_mesh(name + "_d", [(0, -d / 2 - 0.006, 0.04 + dh * (k + 0.5), w / 2 - 0.03, 0.008, dh / 2 - 0.015) for k in range(3)], front, parent=root)
    box_mesh(name + "_k", [(sx * w * 0.22, -d / 2 - 0.02, 0.04 + dh * (k + 0.5), 0.025, 0.01, 0.008) for k in range(3) for sx in (-1, 1)],
             mat_brass(name + "_kb"), parent=root)
    return root


def wood_chair(loc, rot_z=0.0, name="chair", col=(0.2, 0.12, 0.06), jumper=False):
    """Kitchen-style wooden chair (spindle back). Front faces -Y local. Optional jumper hung on the back (shadow reads as head+shoulders)."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_principled(name + "_m", col, rough=0.5)
    boxes = [(0, 0, 0.45, 0.21, 0.2, 0.018)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            boxes.append((sx * 0.18, sy * 0.17, 0.22, 0.017, 0.017, 0.22))
        boxes.append((sx * 0.18, 0.18, 0.72, 0.017, 0.017, 0.27))
    boxes.append((0, 0.18, 0.95, 0.2, 0.02, 0.05))
    for k in (-1, 0, 1):
        boxes.append((k * 0.08, 0.18, 0.7, 0.01, 0.01, 0.22))
    boxes.append((0, 0.17, 0.12, 0.17, 0.01, 0.01))
    o = box_mesh(name + "_g", boxes, m, parent=root)
    out = {"root": root, "geo": o}
    if jumper:
        jm = L.mat_principled(name + "_jm", (0.12, 0.16, 0.22), rough=1.0)
        hd = L.prim("sphere", loc=(0, 0.2, 1.12), segments=16, ring_count=10, radius=0.11)
        hd.scale = (0.9, 0.7, 1.05)
        L.assign(hd, jm)
        L.smooth(hd)
        hd.parent = root
        sh = L.prim("sphere", loc=(0, 0.2, 0.92), segments=16, ring_count=10, radius=0.2)
        sh.scale = (1.25, 0.35, 0.55)
        L.assign(sh, jm)
        L.smooth(sh)
        sh.parent = root
        out["jumper"] = [hd, sh]
    return out

# ============================================================================ characters

def figure(name="fig", color=(0.012, 0.012, 0.014), height=1.75, coat=False, cap=False, dress=False, apron=False,
           rim=None):
    """char_figure + accessories: peaked police cap, long dress, apron. Faceless."""
    p = L.char_figure(name=name, color=color, height=height, coat=coat)
    s = height / 1.75
    m = p["torso"].data.materials[0]
    if cap:
        c = L.prim("cyl", loc=(0, 0, 0.24 * s), vertices=16, radius=0.11 * s, depth=0.08 * s)
        L.assign(c, m)
        c.parent = p["neck"]
        br = L.prim("cyl", loc=(0, 0.07 * s, 0.205 * s), vertices=16, radius=0.08 * s, depth=0.012 * s)
        br.scale = (1.1, 0.8, 1)
        L.assign(br, m)
        br.parent = p["neck"]
        p["cap"] = c
    if dress:
        d = L.prim("cone", loc=(0, 0, -0.42 * s), vertices=20, radius1=0.33 * s, radius2=0.17 * s, depth=0.95 * s)
        L.assign(d, m)
        L.smooth(d)
        d.parent = p["pelvis"]
        p["dress"] = d
    if apron:
        am = L.mat_principled(name + "_apron", (0.5, 0.48, 0.44), rough=1.0)
        a = box_mesh(name + "_apron", [(0, 0.15 * s, -0.25 * s, 0.17 * s, 0.01, 0.42 * s)], am)
        a.parent = p["pelvis"]
        p["apron"] = a
    return p


def walk(parts, start, nframes, stride=0.45, rate=0.95, travel=None, skip=(), bob=0.02):
    """Walk cycle like L.anim_walk but can skip limbs (e.g. arm carrying a prop) and adds a pelvis bob."""
    fps = bpy.context.scene.render.fps
    z0 = parts["pelvis"].location.z
    for f in range(start, start + nframes + 1, 2):
        t = (f - start) / fps
        ph = 2 * math.pi * rate * t
        for tag, sg in (("L", 1), ("R", -1)):
            parts[f"hip{tag}"].rotation_euler = (sg * stride * math.sin(ph), 0, 0)
            parts[f"knee{tag}"].rotation_euler = (-max(0, -sg * stride * 1.3 * math.sin(ph + 0.6)), 0, 0)
            for k in ("hip", "knee"):
                parts[f"{k}{tag}"].keyframe_insert("rotation_euler", frame=f)
            if f"arm{tag}" not in skip:
                parts[f"shoulder{tag}"].rotation_euler = (-sg * stride * 0.7 * math.sin(ph), 0, 0)
                parts[f"elbow{tag}"].rotation_euler = (0.25, 0, 0)
                parts[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
                parts[f"elbow{tag}"].keyframe_insert("rotation_euler", frame=f)
        parts["pelvis"].location.z = z0 + bob * abs(math.sin(ph))
        parts["pelvis"].keyframe_insert("location", index=2, frame=f)
    if travel:
        r = parts["root"]
        r.location = travel[0]
        r.keyframe_insert("location", frame=start)
        r.location = travel[1]
        r.keyframe_insert("location", frame=start + nframes)
        L.linear_fcurves(r)


def pose_hold(parts, which, shoulder=(0, 0, 0), elbow=(0, 0, 0), frame=1):
    parts[f"shoulder{which}"].rotation_euler = shoulder
    parts[f"elbow{which}"].rotation_euler = elbow
    parts[f"shoulder{which}"].keyframe_insert("rotation_euler", frame=frame)
    parts[f"elbow{which}"].keyframe_insert("rotation_euler", frame=frame)

# ============================================================================ ENFIELD sets

ROOM_W, ROOM_D, ROOM_H = 3.3, 3.6, 2.45
CHAIR_A = ((-0.2, 1.12, 0), math.radians(-58))   # 40 cm out, angled to left bed (the WRONG detail)
CHAIR_B = ((-0.45, 1.56, 0), 0.0)                # against the north wall
REC_POS = ((0.25, 1.52, 0.5), math.radians(-8))  # on the low cabinet between beds
BEDROOM_CAM = dict(start=(0.55, -2.05, 1.1), end=(0.42, -1.2, 1.08), target=(-0.05, 1.8, 0.82), lens=26)


def enfield_bedroom(n, chair="A", rec_on=True, rec_on_frame=None, reels_spin=True, lamp_on=False, lamp_energy=22,
                    toppled=False, moon=1.0, fog=True, dust_count=700, jumper=False, fill=25):
    """1970s council-house child's bedroom, 3.3x3.6 m. Door/camera on south wall, sash window north wall,
    beds along W and E walls, low cabinet between beds with recorder + lamp, chest of drawers by the door.
    chair: 'A' (askew, 40cm out), 'B' (against wall), 'toppled'."""
    W, D, Hh = ROOM_W, ROOM_D, ROOM_H
    wp = mat_wallpaper("wp_bed", base=(0.33, 0.29, 0.17), stripe=(0.24, 0.19, 0.1), flower=(0.45, 0.24, 0.1), leaf=(0.2, 0.22, 0.1))
    ceil = L.mat_principled("ceil", (0.42, 0.4, 0.36), rough=0.9)
    fl = L.prim("plane", loc=(0, 0, 0), size=1)
    fl.scale = (W + 0.4, D + 0.4, 1)
    L.assign(fl, mat_carpet("carpet_bed"))
    c = L.prim("plane", loc=(0, 0, Hh), size=1, rot=(math.pi, 0, 0))
    c.scale = (W + 0.4, D + 0.4, 1)
    L.assign(c, ceil)
    win = (0.0, 0.95, 1.0, 2.05)
    wall_with_openings("wallN", "x", D / 2, W + 0.2, Hh, [win], mat=wp, outward=1)
    wall_with_openings("wallS", "x", -D / 2, W + 0.2, Hh, [(0.55, 0.82, 0.0, 2.0)], mat=wp, outward=-1)
    wall_with_openings("wallE", "y", W / 2, D, Hh, [], mat=wp, outward=1)
    wall_with_openings("wallW", "y", -W / 2, D, Hh, [], mat=wp, outward=-1)
    skirting = L.mat_principled("skirt", (0.6, 0.58, 0.52), rough=0.5)
    box_mesh("skirting", [(0, D / 2 - 0.01, 0.05, W / 2, 0.01, 0.05), (0, -D / 2 + 0.01, 0.05, W / 2, 0.01, 0.05),
                          (W / 2 - 0.01, 0, 0.05, 0.01, D / 2, 0.05), (-W / 2 + 0.01, 0, 0.05, 0.01, D / 2, 0.05)], skirting)
    window_frame("winframe", "x", D / 2 + 0.05, win[0], win[1], win[2], win[3], mat=skirting)
    # night sky + rooftops beyond window
    sky = L.prim("plane", loc=(0, D / 2 + 3.0, 1.6), size=1, rot=(math.pi / 2, 0, 0))
    sky.scale = (8, 6, 1)
    skym, sn, sl = _nodes("nightsky")
    for nd in list(sn):
        if nd.type == "BSDF_PRINCIPLED":
            sn.remove(nd)
    tc = sn.new("ShaderNodeTexCoord")
    sep = sn.new("ShaderNodeSeparateXYZ")
    sl.new(tc.outputs["Generated"], sep.inputs[0])
    rr = _ramp(sn, [(0.0, (0.03, 0.05, 0.1)), (0.45, (0.08, 0.13, 0.24)), (1.0, (0.03, 0.05, 0.1))])
    sl.new(sep.outputs[1], rr.inputs[0])
    em = sn.new("ShaderNodeEmission")
    em.inputs[1].default_value = 1.0 * moon
    sl.new(rr.outputs[0], em.inputs[0])
    sl.new(em.outputs[0], sn["Material Output"].inputs["Surface"])
    L.assign(sky, skym)
    roofs = L.mat_principled("roofsil", (0.005, 0.006, 0.01), rough=1)
    box_mesh("rooftops", [(-1.6, D / 2 + 2.6, 0.4, 1.4, 0.2, 1.1), (1.3, D / 2 + 2.6, 0.2, 1.6, 0.2, 1.05),
                          (0.9, D / 2 + 2.55, 1.6, 0.08, 0.1, 0.25)], roofs)
    # curtains (half drawn)
    cm = L.mat_principled("curt_m", (0.28, 0.17, 0.09), rough=1.0)
    curtain("curtL", -0.62, 0.42, 1.45, 2.2, axis="x", fixed=D / 2 - 0.08, folds=4, mat=cm, seed=1)
    curtain("curtR", 0.62, 0.42, 1.45, 2.2, axis="x", fixed=D / 2 - 0.08, folds=4, mat=cm, seed=2)
    box_mesh("rail", [(0, D / 2 - 0.08, 2.22, 1.0, 0.015, 0.015)], skirting)
    # beds
    bl = single_bed((-W / 2 + 0.5, 0.65, 0), 0, blanket=(0.3, 0.2, 0.14), seed=3, name="bedL")
    br = single_bed((W / 2 - 0.5, 0.65, 0), 0, blanket=(0.22, 0.26, 0.3), seed=5, name="bedR", duvet_on=not toppled)
    if toppled:
        duvet((W / 2 - 0.75, -0.45, 0.06), (0.55, 0.7, 0.03), (0.22, 0.26, 0.3), 0.06, 9, "duvet_floor").rotation_euler = (0, 0, 0.5)
    # cabinet + lamp + recorder
    cab_m = L.mat_principled("cab_m", (0.2, 0.12, 0.06), rough=0.5)
    box_mesh("cabinet", [(0.28, 1.56, 0.24, 0.38, 0.2, 0.24), (0.28, 1.56, 0.49, 0.4, 0.21, 0.012)], cab_m, bevel=0.005)
    lamp = bedside_lamp((0.56, 1.6, 0.5), on=lamp_on, energy=lamp_energy, name="blamp")
    rec = tape_recorder(REC_POS[0], REC_POS[1], n=n, rec_on=rec_on, rec_on_frame=rec_on_frame, reels_spin=reels_spin)
    # chest of drawers by the door (or face-down)
    if toppled:
        chest_of_drawers((0.5, 0.55, 0.2), rot=(math.pi / 2, 0, 0.35), name="chest")
    else:
        chest_of_drawers((1.25, -1.45, 0), rot=(0, 0, -math.pi / 2), name="chest")
    # chair
    if chair == "A":
        ch = wood_chair(CHAIR_A[0], CHAIR_A[1], jumper=jumper)
    elif chair == "B":
        ch = wood_chair(CHAIR_B[0], CHAIR_B[1], jumper=jumper)
    else:
        ch = wood_chair((-0.1, 0.3, 0.21), 0.9, jumper=False)
        ch["root"].rotation_euler = (0, math.radians(90), 0.9)
    # a few child details: rug, poster rectangles
    box_mesh("rug", [(0.0, 0.3, 0.005, 0.5, 0.8, 0.005)], L.mat_noise_surface("rug_m", (0.18, 0.08, 0.05), (0.3, 0.16, 0.08), scale=20, bump=0.1, voronoi=False))
    box_mesh("poster", [(-W / 2 + 0.01, 0.8, 1.5, 0.005, 0.25, 0.32)], L.mat_principled("poster_m", (0.4, 0.3, 0.22), rough=0.8))
    # moonlight through window (+ faint bounce fill)
    ml = L.spot((0.1, D / 2 + 2.2, 3.0), (0, 0, 0), energy=1800 * moon, size_deg=32, blend=0.25, color=(0.55, 0.68, 1.0), name="moon", radius=0.05)
    aim(ml, (0.1, D / 2 + 2.2, 3.0), (-0.1, 0.2, 0.0))
    amb = L.area((0, 0.2, Hh - 0.05), (0, 0, 0), energy=22 * moon, size=2.5, color=(0.5, 0.6, 0.9), name="ambfill")
    out = {"lamp": lamp, "rec": rec, "chair": ch, "moon": ml, "bedL": bl, "bedR": br}
    if fog:
        out["fog"] = room_fog((0, 0, Hh / 2), (W, D, Hh), density=0.025, color=(0.6, 0.68, 0.85))
    if dust_count:
        out["dust"] = dust((0, 0.9, 1.3), (W * 0.7, 1.6, 1.6), n, count=int(dust_count * 0.45), radius=0.0022, drift=(0.005, 0.0, -0.01), emit=0.05)
    return out


def bedroom_camera(n, mode="push", lens=None, push=1.0):
    """S01-style doorway push-in. mode 'push' | 'static' | 'start' (hold S01 frame 1)."""
    c = BEDROOM_CAM
    lens = lens or c["lens"]
    cm = cam(c["start"], c["target"], lens=lens)
    if mode == "push":
        e = tuple(c["start"][i] + (c["end"][i] - c["start"][i]) * push for i in range(3))
        cam_move(cm, [(1, c["start"], c["target"]), (n, e, c["target"])], ease=False)
    L.cam_light(cm, energy=30, color=(0.65, 0.75, 1.0), size_deg=80)
    return cm


def semi_pair(name, origin=(0, 0, 0), w=10.0, d=7.0, fh=2.7, lit=(), open_win=None, brick=None, seed=1):
    """Pair of 1970s semi-detached brick houses (one block, two front doors), gable roof along X, front faces -Y.
    Windows: ids 'U0..U3' upstairs, 'D0','D1' downstairs (bay-less big windows), doors at the centre.
    lit: ids of windows glowing warm-dim. open_win: id left as a hole (caller builds interior)."""
    ox, oy, oz = origin
    brick = brick or mat_brick(name + "_brick", wet=True)
    H2 = fh * 2
    up = [(-w * 0.36, 1.3), (-w * 0.13, 0.7), (w * 0.13, 0.7), (w * 0.36, 1.3)]
    dn = [(-w * 0.3, 1.6), (w * 0.3, 1.6)]
    doors = [(-w * 0.08, 0.9), (w * 0.08, 0.9)]
    openings_front = []
    wins = {}
    for i, (x, ww) in enumerate(up):
        openings_front.append((x, ww, fh + 0.9, fh + 2.1))
        wins[f"U{i}"] = (x, ww, fh + 0.9, fh + 2.1)
    for i, (x, ww) in enumerate(dn):
        openings_front.append((x, ww, 0.8, 2.1))
        wins[f"D{i}"] = (x, ww, 0.8, 2.1)
    for x, ww in doors:
        openings_front.append((x, ww, 0.0, 2.05))
    root = empty(name, origin)
    fw = wall_with_openings(name + "_front", "x", 0, w, H2, openings_front, mat=brick, outward=1, t=0.25)
    fw.parent = root
    # body starts 2.8 m back so an 'open' window can show a built interior; side walls close the gap
    body = box_mesh(name + "_body", [(0, (d + 0.25 + 2.8) / 2, H2 / 2, w / 2, (d + 0.25 - 2.8) / 2, H2 / 2),
                                     (-w / 2 + 0.1, 1.5, H2 / 2, 0.1, 1.3, H2 / 2), (w / 2 - 0.1, 1.5, H2 / 2, 0.1, 1.3, H2 / 2)], brick, parent=root)
    # roof
    roofm = L.mat_noise_surface(name + "_tiles", (0.05, 0.045, 0.045), (0.13, 0.11, 0.1), scale=14, bump=0.4, voronoi=False, rough=0.6)
    bm = bmesh.new()
    rh = 2.6
    v = [bm.verts.new(p) for p in ((-w / 2 - 0.3, -0.35, H2), (w / 2 + 0.3, -0.35, H2), (w / 2 + 0.3, d / 2 + 0.25, H2 + rh),
                                   (-w / 2 - 0.3, d / 2 + 0.25, H2 + rh), (-w / 2 - 0.3, d + 0.85, H2), (w / 2 + 0.3, d + 0.85, H2))]
    for fc in ((0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2)):
        bm.faces.new([v[i] for i in fc])
    r = L.mesh_from_bm(name + "_roof", bm)
    L.assign(r, roofm)
    r.parent = root
    box_mesh(name + "_chim", [(0, d / 2 + 0.25, H2 + rh + 0.4, 0.45, 0.3, 0.7), (0, d / 2 + 0.25, H2 + rh + 1.12, 0.5, 0.35, 0.05)], brick, parent=root)
    # porch canopies + doors
    canm = L.mat_principled(name + "_can", (0.08, 0.08, 0.08), rough=0.6)
    box_mesh(name + "_canopy", [(0, -0.55, 2.35, w * 0.17, 0.55, 0.05)], canm, parent=root)
    doorm = L.mat_principled(name + "_door", (0.12, 0.2, 0.25) if seed % 2 else (0.3, 0.07, 0.05), rough=0.5)
    box_mesh(name + "_doors", [(x, 0.05, 1.02, ww / 2, 0.03, 1.02) for x, ww in doors], doorm, parent=root)
    frm = L.mat_principled(name + "_wf", (0.7, 0.68, 0.62), rough=0.5)
    lit_m = L.mat_emission(name + "_lit", (1.0, 0.62, 0.3), 2.2)
    dark_m = mat_glass_dark(name + "_glass")
    panes = []
    out = {"root": root, "wins": wins}
    for k, (x, ww, b, t) in wins.items():
        f = window_frame(f"{name}_wf{k}", "x", 0.02, x, ww, b, t, mat=frm, depth=0.06)
        f.parent = root
        if open_win == k:
            continue
        pane = box_mesh(f"{name}_pane{k}", [(x, 0.06, (b + t) / 2, ww / 2, 0.005, (t - b) / 2)], lit_m if k in lit else dark_m, parent=root)
        out[f"pane_{k}"] = pane
    # low garden wall + path
    lowb = brick
    gw = []
    for sx in (-1, 1):
        gw.append((sx * (w * 0.08 + 0.6 + (w / 2 - w * 0.08 - 0.6) / 2), -3.2, 0.3, (w / 2 - w * 0.08 - 0.6) / 2, 0.12, 0.3))
    gw.append((0, -1.6, 0.3, 0.12, 1.6, 0.3))
    box_mesh(name + "_gwall", gw, lowb, parent=root)
    garden = box_mesh(name + "_garden", [(0, -1.6, 0.01, w / 2, 1.6, 0.01)], L.GRASS_DARK(), parent=root)
    return out


def streetlamp(loc, height=6.0, energy=900, color=(1.0, 0.5, 0.14), name="slamp", arm=1.2, face=0.0):
    root = empty(name, loc)
    root.rotation_euler = (0, 0, face)
    pm = L.mat_principled(name + "_pole", (0.2, 0.21, 0.2), rough=0.6, metal=0.5)
    box_mesh(name + "_pole", [(0, 0, height / 2, 0.06, 0.06, height / 2), (0, arm / 2, height, 0.04, arm / 2, 0.04)], pm, parent=root)
    hm = L.mat_emission(name + "_head", (1.0, 0.55, 0.18), 30)
    hd = box_mesh(name + "_head", [(0, arm, height - 0.08, 0.12, 0.25, 0.06)], hm, parent=root)
    sp = L.spot((0, 0, 0), (0, 0, 0), energy=energy, size_deg=120, blend=0.6, color=color, name=name + "_l", radius=0.15)
    sp.parent = root
    sp.location = (0, arm, height - 0.2)
    pt = L.point((0, 0, 0), energy=energy * 0.12, color=color, radius=0.2, name=name + "_glow")
    pt.parent = root
    pt.location = (0, arm, height - 0.3)
    return {"root": root, "spot": sp, "glow": pt, "head_mat": hm}


def rain(center, size, n, count=1600, speed=7.0, length=0.09, seed=21, name="rain", emit=0.6):
    """Drizzle streaks: thin vertical slivers in one mesh, whole cloud falls (wraps by being tall)."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    fall = speed * n / 24.0
    hz = size[2] + fall
    for i in range(count):
        c = Vector((center[0] + rnd.uniform(-size[0], size[0]) / 2, center[1] + rnd.uniform(-size[1], size[1]) / 2,
                    center[2] - size[2] / 2 + rnd.uniform(0, hz)))
        w = 0.003
        vs = [bm.verts.new(c + Vector(v)) for v in ((-w, 0, 0), (w, 0, 0), (0, 0, length), (0, w, 0))]
        for f in ((0, 1, 2), (1, 3, 2), (3, 0, 2)):
            bm.faces.new([vs[k] for k in f])
    o = L.mesh_from_bm(name, bm)
    L.assign(o, L.mat_principled(name + "_m", (0.8, 0.8, 0.85), rough=0.1, emit=(0.7, 0.65, 0.6), emit_strength=emit))
    o.visible_shadow = False
    o.location = (0, 0, 0)
    o.keyframe_insert("location", frame=1)
    o.location = (0.4, 0, -fall)
    o.keyframe_insert("location", frame=n)
    L.linear_fcurves(o)
    return o


def telephone(loc, name="phone"):
    m = L.mat_principled(name + "_m", (0.02, 0.02, 0.02), rough=0.3)
    root = empty(name, loc)
    box_mesh(name + "_base", [(0, 0, 0.04, 0.1, 0.12, 0.04)], m, parent=root, bevel=0.02)
    return root


def evidence_board(name="board", w=2.4, h=3.6):
    """Dark corkboard plane in XZ at y=0 facing -Y, wooden frame."""
    cork = mat_cork(name + "_cork")
    b = box_mesh(name, [(0, 0.02, 0, w / 2, 0.02, h / 2)], cork)
    fr = L.mat_principled(name + "_fr", (0.08, 0.05, 0.03), rough=0.5)
    box_mesh(name + "_frame", [(0, 0, h / 2, w / 2 + 0.06, 0.04, 0.05), (0, 0, -h / 2, w / 2 + 0.06, 0.04, 0.05),
                               (w / 2, 0, 0, 0.05, 0.04, h / 2), (-w / 2, 0, 0, 0.05, 0.04, h / 2)], fr)
    return b


def pinned_card(name, loc, w, h, lines, size=0.12, rot=0.0, color=(0.82, 0.78, 0.66), ink=(0.05, 0.04, 0.03), pin_col=(0.75, 0.05, 0.04),
                header=None, header_col=(0.55, 0.05, 0.04), font_size_header=None):
    """Paper card on the board (front faces -Y) with 3D text lines and a pushpin. Returns root empty."""
    root = empty(name, loc)
    root.rotation_euler = (0, rot, 0)
    box_mesh(name + "_paper", [(0, 0, 0, w / 2, 0.003, h / 2)], mat_paper(name + "_pm", color), parent=root)
    ink_m = L.mat_principled(name + "_ink", ink, rough=0.7)
    z = h / 2 - 0.08 - size * 0.8
    if header:
        hs = font_size_header or size * 1.15
        t = L.text3d(header, loc=(0, -0.006, z), size=hs, extrude=0.001, mat=L.mat_principled(name + "_hm", header_col, rough=0.6), name=name + "_hdr")
        t.parent = root
        z -= hs * 1.5
    for i, ln in enumerate(lines):
        t = L.text3d(ln, loc=(0, -0.006, z - i * size * 1.35), size=size, extrude=0.001, mat=ink_m, name=f"{name}_t{i}")
        t.parent = root
    pin = L.prim("sphere", loc=(0, -0.03, h / 2 - 0.05), segments=12, ring_count=8, radius=0.025)
    L.assign(pin, L.mat_principled(name + "_pin", pin_col, rough=0.3))
    pin.parent = root
    return root


def waveform_curve(name, length=12.0, pts=600, amp=0.5, seed=4, z=0.0, y=0.0, thickness=0.012, color=(0.55, 1.0, 0.6), strength=6.0,
                   bursts=((0.25, 0.45), (0.6, 0.85))):
    """Oscilloscope-like jagged waveform as an emissive bevelled poly curve along X (x from 0..length)."""
    rnd = random.Random(seed)
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = thickness
    cu.bevel_resolution = 1
    sp = cu.splines.new("POLY")
    sp.points.add(pts - 1)
    for i in range(pts):
        u = i / (pts - 1)
        x = u * length
        env = 0.12
        for a, b in bursts:
            if a <= u <= b:
                env = max(env, math.sin((u - a) / (b - a) * math.pi) ** 0.6)
        v = (math.sin(x * 9.0) * 0.55 + math.sin(x * 23.0 + 1.3) * 0.25 + noise.noise(Vector((x * 6, 0, seed))) * 0.6
             + (rnd.random() - 0.5) * 0.5)
        sp.points[i].co = (x, y, z + amp * env * v, 1)
    o = L.link(bpy.data.objects.new(name, cu))
    o.data.materials.append(L.mat_emission(name + "_m", color, strength))
    return o


# ============================================================================ STANLEY HOTEL sets (HAUNT-02)

CORR_W, CORR_H, CORR_LEN = 2.4, 3.0, 24.0
DOOR_YS = (2.5, 6.0, 9.5, 13.0, 16.5, 20.0)
D217_Y = 9.5                    # door 217: right-hand wall (x=+CORR_W/2)
CORR_CAM = dict(start=(0.0, -0.6, 1.6), end=(0.05, 4.2, 1.6), target=(0.0, 14.0, 1.35), lens=24)


def mat_white_wall(name="hotelwall", c=(0.72, 0.69, 0.6)):
    return L.mat_noise_surface(name, tuple(v * 0.9 for v in c), c, scale=3, bump=0.08, voronoi=False, rough=0.7)


def sconce(loc, face_x, level=1.0, color=(1.0, 0.7, 0.38), name="sconce", energy=45):
    """Brass wall sconce (backplate, arm, two small fabric shades) + point light. face_x = +1 if on the -x wall facing +x."""
    root = empty(name, loc)
    b = mat_brass(name + "_b")
    box_mesh(name + "_plate", [(0, 0, 0, 0.012, 0.06, 0.12), (face_x * 0.08, 0, -0.02, 0.08, 0.012, 0.012),
                               (face_x * 0.15, 0, 0.0, 0.012, 0.16, 0.012)], b, parent=root)
    sm = L.mat_principled(name + "_shade", (0.8, 0.62, 0.4), rough=1.0, emit=color, emit_strength=3.5 * level)
    for sy in (-1, 1):
        s = L.prim("cone", loc=(face_x * 0.15, sy * 0.15, 0.09), vertices=16, radius1=0.075, radius2=0.04, depth=0.12,
                   end_fill_type="NOTHING")
        L.assign(s, sm)
        s.parent = root
    li = L.point((0, 0, 0), energy=energy * level, color=color, radius=0.08, name=name + "_l")
    li.parent = root
    li.location = (face_x * 0.2, 0, 0.1)
    return {"root": root, "light": li, "mat": sm}


def door_number(text, wall_x, y, z=1.62, side=1, name="num"):
    """Brass numerals on a door. side=+1 for right wall (x=+), faces -x."""
    rot = (math.pi / 2, 0, -math.pi / 2) if side > 0 else (math.pi / 2, 0, math.pi / 2)
    t = L.text3d(text, loc=(wall_x - side * 0.03, y, z), rot=rot, size=0.11, extrude=0.006, mat=mat_brass(name + "_m"), name=name)
    return t


def hotel_corridor(n, mode="night", sconce_level=0.3, d217="ajar", spill=1.0, far_window=1.0, fog=0.03, doors_lit=False,
                   dust_count=500, length=CORR_LEN):
    """Edwardian hotel corridor along +Y: white panelled walls (wainscot + chair rail), dark-red patterned carpet,
    brass sconces between doors, numbered doors in pairs, cold window at the far end. Door 217 on the right at y=9.5.
    mode: night | day | dream.  d217: 'ajar' | 'closed' | 'open'."""
    W, Hh, Ln = CORR_W, CORR_H, length
    wall = mat_white_wall()
    wains = L.mat_principled("wainscot", (0.78, 0.76, 0.7), rough=0.45)
    trim = L.mat_principled("ctrim", (0.85, 0.83, 0.78), rough=0.4)
    doorm = L.mat_principled("hdoor", (0.16, 0.07, 0.035), rough=0.4)
    fl = L.prim("plane", loc=(0, Ln / 2, 0), size=1)
    fl.scale = (W + 0.2, Ln + 2, 1)
    L.assign(fl, mat_hotel_carpet())
    cl = L.prim("plane", loc=(0, Ln / 2, Hh), size=1, rot=(math.pi, 0, 0))
    cl.scale = (W + 0.2, Ln + 2, 1)
    L.assign(cl, L.mat_principled("hceil", (0.7, 0.68, 0.62), rough=0.8))
    op = [(y, 0.95, 0.0, 2.2) for y in DOOR_YS]
    for side in (-1, 1):
        wo = wall_with_openings(f"cw{side}", "y", side * W / 2, Ln + 2, Hh, [(y - Ln / 2 - 0.0, w, b, t) for (y, w, b, t) in op],
                                mat=wall, outward=side)
        wo.location.y = Ln / 2
        # wainscot panels between doors, chair rail, skirting
        boxes = [(side * (W / 2 - 0.012), Ln / 2, 0.95, 0.012, Ln / 2 + 1, 0.025), (side * (W / 2 - 0.015), Ln / 2, 0.08, 0.015, Ln / 2 + 1, 0.08),
                 (side * (W / 2 - 0.01), Ln / 2, 2.55, 0.01, Ln / 2 + 1, 0.04)]
        edges = [-1.0] + [y for y in DOOR_YS] + [Ln + 1]
        for a, b in zip(edges[:-1], edges[1:]):
            a0, b0 = a + 0.6, b - 0.6
            if b0 - a0 < 0.6:
                continue
            k = max(1, int((b0 - a0) / 1.1))
            pw = (b0 - a0) / k
            for i in range(k):
                cy = a0 + pw * (i + 0.5)
                hw = pw / 2 - 0.08
                for (zz, hz, hy) in ((0.25, 0.012, hw), (0.75, 0.012, hw)):
                    boxes.append((side * (W / 2 - 0.012), cy, zz, 0.008, hy, hz))
                boxes.append((side * (W / 2 - 0.012), cy - hw, 0.5, 0.008, 0.012, 0.25))
                boxes.append((side * (W / 2 - 0.012), cy + hw, 0.5, 0.008, 0.012, 0.25))
        box_mesh(f"wains{side}", boxes, trim)
        # door casings + slabs + numbers
        cas = []
        for i, y in enumerate(DOOR_YS):
            cas += [(side * (W / 2 - 0.02), y - 0.53, 1.12, 0.03, 0.06, 1.12), (side * (W / 2 - 0.02), y + 0.53, 1.12, 0.03, 0.06, 1.12),
                    (side * (W / 2 - 0.02), y, 2.27, 0.03, 0.6, 0.07)]
        box_mesh(f"casing{side}", cas, trim)
    out = {"sconces": [], "doors": {}}
    for i, y in enumerate(DOOR_YS):
        for side in (-1, 1):
            num = 213 + 2 * i if side > 0 else 212 + 2 * i   # right side: 213, 215, 217 (y=9.5), ...
            hinge_y = y - 0.47 if side > 0 else y + 0.47
            ang = 0.0
            if num == 217:
                ang = {"ajar": 0.13, "closed": 0.0, "open": 1.2}[d217]
            # door rotates into the room (away from corridor)
            piv, slab = door_slab(f"door{num}", (side * (W / 2 + 0.05), hinge_y, 0), width=0.94, height=2.2, mat=doorm)
            piv.rotation_euler = (0, 0, (math.pi / 2 - ang) if side > 0 else (-math.pi / 2 - ang))
            out["doors"][num] = piv
            door_number(str(num), side * (W / 2 + 0.05), y, side=side, name=f"n{num}")
    # room behind 217 (warm light spilling through the gap)
    rx = W / 2 + 0.06
    box_mesh("r217", [(rx + 2.0, D217_Y, -0.01, 2.0, 1.6, 0.01), (rx + 4.0, D217_Y, 1.5, 0.05, 1.6, 1.5), (rx + 2.0, D217_Y + 1.6, 1.5, 2.0, 0.05, 1.5),
                      (rx + 2.0, D217_Y - 1.6, 1.5, 2.0, 0.05, 1.5), (rx + 2.0, D217_Y, 3.0, 2.0, 1.6, 0.05)],
             L.mat_principled("r217m", (0.6, 0.45, 0.3), rough=0.8))
    sp = L.point((rx + 0.9, D217_Y + 0.2, 1.3), energy=650 * spill, color=(1.0, 0.62, 0.3), radius=0.15, name="spill217")
    out["spill"] = sp
    # light slit in the ajar gap + a warm wedge of spill across the carpet (the WRONG detail must read on a phone)
    on = d217 in ("ajar", "open")
    slit_m = L.mat_emission("slit217", (1.0, 0.66, 0.32), 8.0 * spill if on else 0.0)
    out["slit"] = box_mesh("slit217", [(W / 2 + 0.06, D217_Y + 0.44, 1.08, 0.03, 0.035, 1.06)], slit_m)
    out["slit_mat"] = slit_m
    wm = L.mat_principled("wedge217", (0.0, 0.0, 0.0), rough=1, emit=(1.0, 0.6, 0.28), emit_strength=(0.9 * spill if on else 0.0), alpha=0.85)
    wm.surface_render_method = "BLENDED"
    bm_ = bmesh.new()
    Y = D217_Y
    vv = [bm_.verts.new(c) for c in ((W / 2, Y + 0.41, 0.004), (W / 2, Y + 0.49, 0.004), (W / 2 - 2.3, Y + 1.25, 0.004), (W / 2 - 2.3, Y + 0.85, 0.004))]
    bm_.faces.new(vv)
    out["wedge"] = L.mesh_from_bm("wedge217", bm_)
    L.assign(out["wedge"], wm)
    out["wedge_mat"] = wm
    # under-door glow strip (used when closed)
    strip_m = L.mat_emission("understrip", (1.0, 0.6, 0.28), 4.0 * spill if d217 == "closed" else 0.0)
    out["strip"] = box_mesh("strip217", [(W / 2 - 0.02, D217_Y, 0.004, 0.06, 0.45, 0.003)], strip_m)
    out["strip_mat"] = strip_m
    # sconces between door pairs (both walls)
    col = (1.0, 0.7, 0.38) if mode != "dream" else (0.85, 0.9, 1.0)
    ys = [y + 1.75 for y in DOOR_YS[:-1]] + [0.75]
    for j, y in enumerate(ys):
        for side in (-1, 1):
            sc = sconce((side * (W / 2 - 0.01), y, 1.95), -side, level=sconce_level, color=col, name=f"sc{j}{'R' if side > 0 else 'L'}")
            out["sconces"].append(sc)
    # far window (cold blue night / warm day)
    endm = wall
    wall_with_openings("cend", "x", Ln, W + 0.2, Hh, [(0, 1.1, 0.8, 2.6)], mat=endm, outward=1)
    window_frame("cendwin", "x", Ln + 0.05, 0, 1.1, 0.8, 2.6, mat=trim)
    if mode == "day":
        wc, we = (1.0, 0.82, 0.55), 6.0
    else:
        wc, we = (0.35, 0.5, 0.9), 2.5 * far_window
    box_mesh("cendsky", [(0, Ln + 1.0, 1.7, 1.2, 0.02, 1.2)], L.mat_emission("cendsky_m", wc, we))
    wl = L.area((0, Ln - 0.2, 1.8), (math.pi / 2, 0, 0), energy=(400 if mode == "day" else 120 * far_window), size=1.2, color=wc, name="farwin")
    wl.rotation_euler = (-math.pi / 2, 0, 0)
    out["farwin"] = wl
    box_mesh("cback", [(0, -1.0, Hh / 2, W / 2 + 0.2, 0.05, Hh / 2)], wall)
    if fog:
        out["fog"] = room_fog((0, Ln / 2, Hh / 2), (W, Ln + 2, Hh), density=fog, color=(0.75, 0.72, 0.68))
    if dust_count:
        out["dust"] = dust((0, 6.0, 1.6), (W * 0.8, 9.0, 2.2), n, count=dust_count, radius=0.003, emit=0.06)
    return out


def corridor_camera(n, mode="push", frac=1.0):
    c = CORR_CAM
    cm = cam(c["start"], c["target"], lens=c["lens"])
    if mode == "push":
        e = tuple(c["start"][i] + (c["end"][i] - c["start"][i]) * frac for i in range(3))
        cam_move(cm, [(1, c["start"], c["target"]), (n, e, c["target"])], ease=False)
    L.cam_light(cm, energy=12, color=(0.9, 0.85, 0.8), size_deg=70)
    return cm


def hotel_facade(n, lit=("W2_7", "W3_14"), snow=True):
    """Grand white 4-storey hotel (Georgian-revival): long central block with red hipped roof, projecting end pavilions,
    central portico + cupola, rows of windows; on a slope below fog-shrouded mountains."""
    white = L.mat_noise_surface("facade", (0.55, 0.55, 0.52), (0.72, 0.71, 0.67), scale=2, bump=0.05, voronoi=False, rough=0.7)
    red = L.mat_noise_surface("redroof", (0.22, 0.03, 0.02), (0.38, 0.07, 0.04), scale=10, bump=0.3, voronoi=False, rough=0.55)
    trim = L.mat_principled("ftrim", (0.8, 0.8, 0.76), rough=0.5)
    dark = mat_glass_dark("fglass", (0.008, 0.01, 0.016))
    litm = L.mat_emission("flit", (1.0, 0.66, 0.32), 5.0)
    root = empty("hotel")
    Wd, Dp, fh, fl = 44.0, 12.0, 3.4, 4
    Ht = fh * fl
    box_mesh("hbody", [(0, Dp / 2, Ht / 2, Wd / 2, Dp / 2, Ht / 2)], white)
    for sx in (-1, 1):  # end pavilions
        box_mesh(f"pav{sx}", [(sx * (Wd / 2 - 3.5), Dp / 2 - 1.2, (Ht + 1.2) / 2, 3.6, Dp / 2 + 1.2, (Ht + 1.2) / 2)], white)
        _hip_roof(f"pavroof{sx}", (sx * (Wd / 2 - 3.5), Dp / 2 - 1.2, Ht + 1.2), 7.6, Dp + 3.0, 3.2, red)
    _hip_roof("mainroof", (0, Dp / 2, Ht), Wd + 0.6, Dp + 0.6, 4.2, red)
    # cornice bands
    box_mesh("cornice", [(0, -0.15, Ht - 0.1, Wd / 2 + 0.1, 0.2, 0.15), (0, -0.1, fh + 0.0, Wd / 2, 0.12, 0.08)], trim)
    # windows
    panes, lits, frames = [], [], []
    cols = 18
    for fl_i in range(fl):
        for c_i in range(cols):
            x = -Wd / 2 + 2.6 + c_i * (Wd - 5.2) / (cols - 1)
            if abs(x) < 3.2 and fl_i == 0:
                continue
            z0 = fl_i * fh + 1.0
            key = f"W{fl_i}_{c_i}"
            ycut = -0.02 if abs(abs(x) - (Wd / 2 - 3.5)) > 3.6 else -2.42
            b = (x, ycut, z0 + 0.85, 0.5, 0.03, 0.85)
            (lits if key in lit else panes).append(b)
            frames.append((x, ycut - 0.02, z0 - 0.05, 0.62, 0.06, 0.06))
            frames.append((x, ycut - 0.02, z0 + 1.82, 0.62, 0.06, 0.1))
    box_mesh("fpanes", panes, dark)
    if lits:
        box_mesh("flits", lits, litm)
        for b in lits:
            L.point((b[0], 0.8, b[2]), energy=120, color=(1.0, 0.66, 0.32), radius=0.4, name="litwin")
    box_mesh("fframes", frames, trim)
    # portico + cupola
    box_mesh("portico", [(0, -2.2, 4.2, 3.6, 2.2, 0.3)] + [(sx * 3.2, -4.0, 2.0, 0.22, 0.22, 2.0) for sx in (-1, -0.35, 0.35, 1)], white)
    box_mesh("pdoor", [(0, -0.03, 1.6, 1.2, 0.05, 1.6)], L.mat_emission("pdoorlit", (1.0, 0.6, 0.3), 0.9))
    cz = Ht + 4.2
    cu = L.prim("cyl", loc=(0, Dp / 2, cz + 1.2), vertices=12, radius=1.6, depth=2.4)
    L.assign(cu, white)
    cr = L.prim("cone", loc=(0, Dp / 2, cz + 3.4), vertices=12, radius1=1.9, radius2=0.1, depth=2.2)
    L.assign(cr, red)
    sp = L.prim("cyl", loc=(0, Dp / 2, cz + 5.0), vertices=6, radius=0.06, depth=1.2)
    L.assign(sp, trim)
    # hillside + driveway
    g = L.prim("plane", loc=(0, 20, -0.05), size=260)
    sub = g.modifiers.new("sub", "SUBSURF")
    sub.subdivision_type = "SIMPLE"
    sub.levels = sub.render_levels = 5
    L.add_displace(g, strength=1.2, scale=8, name="hill_d")
    snowg = L.mat_noise_surface("snowground", (0.25, 0.27, 0.3), (0.5, 0.52, 0.56), scale=4, bump=0.2, voronoi=False, rough=0.8)
    L.assign(g, snowg)
    drive = L.prim("plane", loc=(0, -30, 0.05), size=1)
    drive.scale = (7, 52, 1)
    L.assign(drive, L.mat_noise_surface("drive", (0.04, 0.04, 0.045), (0.1, 0.1, 0.11), scale=15, bump=0.1, voronoi=False, rough=0.5))
    # mountains
    mm = L.mat_noise_surface("mount", (0.05, 0.06, 0.08), (0.2, 0.22, 0.28), scale=0.08, bump=0.6, voronoi=False, rough=0.9)
    for i, (x, y, h, r) in enumerate(((-70, 170, 75, 75), (10, 210, 105, 95), (95, 180, 80, 80), (-140, 230, 95, 90), (160, 240, 90, 85))):
        o = L.prim("cone", loc=(x, y, h / 2 - 5), vertices=24, radius1=r, radius2=2, depth=h)
        o.modifiers.new("sub", "SUBSURF").levels = 2
        L.add_displace(o, strength=8, scale=20, name=f"mt{i}")
        L.assign(o, mm)
    # pine silhouettes along the slope
    pm = L.mat_principled("pine", (0.01, 0.02, 0.015), rough=1)
    rnd = random.Random(4)
    pines = []
    for i in range(60):
        x = rnd.uniform(-80, 80)
        y = rnd.uniform(18, 70)
        if abs(x) < 30 and y < 25:
            continue
        h = rnd.uniform(6, 12)
        pines.append((x, y, h))
    for x, y, h in pines:
        o = L.prim("cone", loc=(x, y, h / 2), vertices=6, radius1=h * 0.22, radius2=0.0, depth=h)
        L.assign(o, pm)
    return root


def _hip_roof(name, c, w, d, h, mat):
    cx, cy, cz = c
    bm = bmesh.new()
    r = min(w, d) / 2 * 0.95
    v = [bm.verts.new(p) for p in ((cx - w / 2, cy - d / 2, cz), (cx + w / 2, cy - d / 2, cz), (cx + w / 2, cy + d / 2, cz), (cx - w / 2, cy + d / 2, cz),
                                   (cx - w / 2 + r, cy, cz + h), (cx + w / 2 - r, cy, cz + h))]
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (1, 2, 5), (3, 0, 4)):
        bm.faces.new([v[i] for i in f])
    o = L.mesh_from_bm(name, bm)
    L.assign(o, mat)
    return o


def snowfall(center, size, n, count=1500, speed=0.9, seed=31, name="snow"):
    m = L.mat_principled(name + "_m", (0.9, 0.92, 0.95), rough=1, emit=(0.6, 0.65, 0.75), emit_strength=0.25)
    return L.particle_cloud(center, size, count=count, radius=0.022, mat=m, drift=(0.3, 0.0, -speed), seed=seed, nframes=n, name=name)


def brass_bed(loc, name="bbed", w=1.5, l=2.0):
    root = empty(name, loc)
    br = mat_brass(name + "_brass")
    white = L.mat_principled(name + "_cover", (0.82, 0.8, 0.76), rough=0.85)
    for sy, hh in ((1, 1.35), (-1, 0.95)):
        y = sy * l / 2
        for sx in (-1, 1):
            p = L.prim("cyl", loc=(sx * w / 2, y, hh / 2), vertices=10, radius=0.025, depth=hh)
            L.assign(p, br)
            p.parent = root
            k = L.prim("sphere", loc=(sx * w / 2, y, hh + 0.03), segments=10, ring_count=6, radius=0.045)
            L.assign(k, br)
            k.parent = root
        for z in (hh - 0.05, hh - 0.35):
            r = L.prim("cyl", loc=(0, y, z), vertices=8, radius=0.016, depth=w, rot=(0, math.pi / 2, 0))
            L.assign(r, br)
            r.parent = root
        for k in range(5):
            x = -w / 2 + w * (k + 1) / 6
            r = L.prim("cyl", loc=(x, y, (hh - 0.35 + hh - 0.05) / 2), vertices=8, radius=0.01, depth=0.3)
            L.assign(r, br)
            r.parent = root
    box_mesh(name + "_mat", [(0, 0, 0.5, w / 2 - 0.02, l / 2 - 0.03, 0.12)], white, parent=root, bevel=0.05)
    box_mesh(name + "_cov", [(0, -0.12, 0.64, w / 2 + 0.03, l / 2 - 0.2, 0.025)], white, parent=root, bevel=0.03)
    for sx in (-1, 1):
        box_mesh(f"{name}_skirt{sx}", [(sx * (w / 2 + 0.05), -0.05, 0.42, 0.01, l / 2 - 0.08, 0.22)], white, parent=root)
    pil = box_mesh(name + "_pil", [(sx * 0.35, l / 2 - 0.3, 0.7, 0.3, 0.16, 0.06) for sx in (-1, 1)], white, parent=root, bevel=0.05)
    return root


def suitcase(loc, rot_z=0.0, state="closed", name="case"):
    """Brown leather suitcase 70x44x20 cm. state closed | open (lid hinged back, empty lining)."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    lea = L.mat_noise_surface(name + "_lea", (0.13, 0.06, 0.025), (0.24, 0.12, 0.05), scale=25, bump=0.15, voronoi=False, rough=0.55)
    lining = L.mat_principled(name + "_lin", (0.35, 0.08, 0.06), rough=0.9)
    br = mat_brass(name + "_br")
    W, D, Hb = 0.7, 0.44, 0.1
    if state == "closed":
        box_mesh(name + "_body", [(0, 0, 0.1, W / 2, D / 2, 0.1)], lea, parent=root, bevel=0.02)
        box_mesh(name + "_straps", [(sx * 0.2, 0, 0.1, 0.025, D / 2 + 0.005, 0.102) for sx in (-1, 1)],
                 L.mat_principled(name + "_st", (0.08, 0.04, 0.02), rough=0.5), parent=root)
        box_mesh(name + "_locks", [(sx * 0.2, -D / 2 - 0.008, 0.17, 0.02, 0.006, 0.015) for sx in (-1, 1)], br, parent=root)
        h = L.prim("torus", loc=(0, -D / 2 - 0.01, 0.2), major_radius=0.07, minor_radius=0.012, rot=(0, 0, 0))
        h.rotation_euler = (math.pi / 2, 0, 0)
        h.scale = (1, 0.6, 1)
        L.assign(h, lea)
        h.parent = root
    else:
        t = 0.015
        box_mesh(name + "_base", [(0, 0, 0.005, W / 2, D / 2, 0.005), (0, -D / 2 + t / 2, Hb / 2, W / 2, t / 2, Hb / 2),
                                  (0, D / 2 - t / 2, Hb / 2, W / 2, t / 2, Hb / 2), (-W / 2 + t / 2, 0, Hb / 2, t / 2, D / 2, Hb / 2),
                                  (W / 2 - t / 2, 0, Hb / 2, t / 2, D / 2, Hb / 2)], lea, parent=root)
        box_mesh(name + "_lining", [(0, 0, 0.012, W / 2 - t, D / 2 - t, 0.002)], lining, parent=root)
        hp = empty(name + "_hinge", (0, D / 2, Hb), parent=root)
        box_mesh(name + "_lid", [(0, -D / 2, 0.05, W / 2, D / 2, 0.005), (0, -D / 2, 0.025, W / 2 - t, D / 2 - t, 0.002)], lea, parent=hp)
        box_mesh(name + "_lidlin", [(0, -D / 2, 0.012, W / 2 - t, D / 2 - t, 0.002)], lining, parent=hp)
        hp.rotation_euler = (math.radians(-105), 0, 0)
    return root


def luggage_rack(loc, rot_z=0.0, name="rack"):
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_principled(name + "_m", (0.12, 0.06, 0.03), rough=0.45)
    box_mesh(name + "_g", [(sx * 0.33, sy * 0.2, 0.25, 0.02, 0.02, 0.25) for sx in (-1, 1) for sy in (-1, 1)] +
             [(0, sy * 0.2, 0.49, 0.36, 0.02, 0.015) for sy in (-1, 1)] +
             [(x, 0, 0.5, 0.03, 0.22, 0.004) for x in (-0.24, -0.08, 0.08, 0.24)], m, parent=root)
    return root


def folded_clothes(loc, rot_z=0.0, name="clothes"):
    """Four neat folded squares (shirt, sweater, trousers, cardigan) + returns root."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    cols = [(0.7, 0.68, 0.62), (0.12, 0.18, 0.3), (0.25, 0.22, 0.18), (0.42, 0.1, 0.08)]
    pos = [(-0.36, 0.0), (-0.12, 0.0), (0.12, 0.0), (0.36, 0.0)]
    for i, ((x, y), c) in enumerate(zip(pos, cols)):
        box_mesh(f"{name}{i}", [(x, y, 0.025, 0.105, 0.14, 0.025)], L.mat_principled(f"{name}{i}_m", c, rough=0.95), parent=root, bevel=0.012)
    return root


def shoes_pair(loc, rot_z=0.0, name="shoes"):
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_principled(name + "_m", (0.04, 0.025, 0.015), rough=0.25)
    for sx in (-1, 1):
        s = L.prim("sphere", loc=(sx * 0.07, 0, 0.045), segments=16, ring_count=8, radius=0.1)
        s.scale = (0.45, 1.3, 0.42)
        L.assign(s, m)
        s.parent = root
    return root


def typewriter(loc, rot_z=0.0, name="tw"):
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_principled(name + "_m", (0.02, 0.02, 0.022), rough=0.3, metal=0.3)
    keys = L.mat_principled(name + "_k", (0.7, 0.68, 0.6), rough=0.4)
    box_mesh(name + "_b", [(0, 0, 0.06, 0.2, 0.17, 0.06), (0, 0.08, 0.13, 0.2, 0.06, 0.04)], m, parent=root, bevel=0.01)
    r = L.prim("cyl", loc=(0, 0.1, 0.19), vertices=16, radius=0.03, depth=0.46, rot=(0, math.pi / 2, 0))
    L.assign(r, m)
    r.parent = root
    pp = box_mesh(name + "_paper", [(0, 0.12, 0.3, 0.1, 0.004, 0.13)], mat_paper(name + "_p", (0.85, 0.83, 0.76)), parent=root)
    pp.rotation_euler = (-0.25, 0, 0)
    box_mesh(name + "_keys", [(-0.15 + 0.03 * i, -0.08 - 0.03 * r_, 0.1 + 0.015 * r_, 0.011, 0.011, 0.006) for r_ in range(3) for i in range(11)],
             keys, parent=root)
    return root


def room217(n, era="modern", case_state="closed", lamp_on=True, lamp_energy=35, moon=1.0, gaslamp=False, fog=0.02,
            dust_count=400, door_angle=0.0):
    """Room 217: 4.2 x 5.0 x 3.3 m. Tall sash window on E wall (mountain view), white wainscoting, brass bed (head on N wall),
    wardrobe on W wall, writing desk + chair + typewriter under the window, luggage rack + suitcase at the bed foot.
    Door on S wall at x=-1.2. era '1911': sepia palette, gas lamp on W wall, no luggage."""
    W, D, Hh = 4.2, 5.0, 3.3
    sep = era == "1911"
    wallc = (0.62, 0.52, 0.38) if sep else (0.66, 0.64, 0.58)
    wall = L.mat_noise_surface("w217", tuple(v * 0.85 for v in wallc), wallc, scale=2.5, bump=0.06, voronoi=False, rough=0.75)
    trim = L.mat_principled("t217", (0.72, 0.64, 0.5) if sep else (0.84, 0.83, 0.78), rough=0.45)
    fl = L.prim("plane", loc=(0, 0, 0), size=1)
    fl.scale = (W + 0.4, D + 0.4, 1)
    L.assign(fl, mat_hotel_carpet("c217", red=(0.2, 0.08, 0.03) if sep else (0.16, 0.025, 0.02), k=1.6))
    cl = L.prim("plane", loc=(0, 0, Hh), size=1, rot=(math.pi, 0, 0))
    cl.scale = (W + 0.4, D + 0.4, 1)
    L.assign(cl, trim)
    win = (0.6, 1.2, 0.75, 2.85)
    door = (-1.2, 0.95, 0.0, 2.25)
    wall_with_openings("w217N", "x", D / 2, W + 0.2, Hh, [], mat=wall, outward=1)
    wall_with_openings("w217S", "x", -D / 2, W + 0.2, Hh, [door], mat=wall, outward=-1)
    wall_with_openings("w217E", "y", W / 2, D, Hh, [win], mat=wall, outward=1)
    wall_with_openings("w217W", "y", -W / 2, D, Hh, [], mat=wall, outward=-1)
    # wainscoting (rail + panel frames) on all walls
    bx = []
    for (ax, fixed, Lw) in (("x", D / 2 - 0.012, W), ("x", -D / 2 + 0.012, W), ("y", W / 2 - 0.012, D), ("y", -W / 2 + 0.012, D)):
        def B(a, z, ha, hz, th=0.012):
            bx.append((a, fixed, z, ha, th, hz) if ax == "x" else (fixed, a, z, th, ha, hz))
        B(0, 1.0, Lw / 2, 0.03, 0.02)
        B(0, 0.08, Lw / 2, 0.08, 0.016)
        k = int(Lw / 0.9)
        for i in range(k):
            a = -Lw / 2 + (i + 0.5) * Lw / k
            hw = Lw / k / 2 - 0.1
            B(a, 0.3, hw, 0.012)
            B(a, 0.82, hw, 0.012)
            B(a - hw, 0.56, 0.012, 0.26)
            B(a + hw, 0.56, 0.012, 0.26)
    box_mesh("wains217", bx, trim)
    window_frame("win217", "y", W / 2 + 0.05, win[0], win[1], win[2], win[3], mat=trim)
    # mountain view outside the window
    view = L.prim("plane", loc=(W / 2 + 4, win[0], 1.8), size=1, rot=(math.pi / 2, 0, math.pi / 2))
    view.scale = (9, 6, 1)
    vm, vn, vl = _nodes("view217")
    for nd in list(vn):
        if nd.type == "BSDF_PRINCIPLED":
            vn.remove(nd)
    tc = vn.new("ShaderNodeTexCoord")
    sx_ = vn.new("ShaderNodeSeparateXYZ")
    vl.new(tc.outputs["Generated"], sx_.inputs[0])
    nz = vn.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 6
    sep_x = vn.new("ShaderNodeCombineXYZ")
    vl.new(sx_.outputs[0], sep_x.inputs[0])
    vl.new(sep_x.outputs[0], nz.inputs["Vector"])
    ridge = _math(vn, vl, "ADD", _math(vn, vl, "MULTIPLY", nz.outputs["Fac"], 0.35), 0.25)
    mask = _math(vn, vl, "GREATER_THAN", sx_.outputs[1], ridge)
    if sep:
        sky_c, mt_c, st = (0.75, 0.6, 0.4), (0.3, 0.24, 0.16), 1.2
    else:
        sky_c, mt_c, st = (0.12, 0.18, 0.32), (0.02, 0.03, 0.05), 1.0 * moon
    rr = _ramp(vn, [(0.0, mt_c), (1.0, sky_c)], interp="CONSTANT")
    rr.color_ramp.elements[1].position = 0.5
    vl.new(mask, rr.inputs[0])
    em = vn.new("ShaderNodeEmission")
    em.inputs[1].default_value = st
    vl.new(rr.outputs[0], em.inputs[0])
    vl.new(em.outputs[0], vn["Material Output"].inputs["Surface"])
    L.assign(view, vm)
    # curtains
    cm = L.mat_principled("drape217", (0.35, 0.22, 0.1) if sep else (0.3, 0.05, 0.04), rough=1)
    curtain("dr1", win[0] - 0.85, 0.5, 2.6, 3.05, axis="y", fixed=W / 2 - 0.1, folds=5, mat=cm, seed=3)
    curtain("dr2", win[0] + 0.85, 0.5, 2.6, 3.05, axis="y", fixed=W / 2 - 0.1, folds=5, mat=cm, seed=4)
    # furniture
    bed = brass_bed((-0.2, 1.4, 0))
    wood = L.mat_principled("wood217", (0.15, 0.08, 0.035) if not sep else (0.2, 0.12, 0.05), rough=0.45)
    box_mesh("wardrobe", [(-W / 2 + 0.33, -1.0, 1.1, 0.3, 0.6, 1.1), (-W / 2 + 0.33, -1.0, 2.25, 0.34, 0.64, 0.05)], wood, bevel=0.01)
    box_mesh("wardoors", [(-W / 2 + 0.64, -1.0 + sy * 0.29, 1.1, 0.01, 0.27, 1.0) for sy in (-1, 1)], L.mat_principled("wd2", (0.2, 0.11, 0.05), rough=0.4))
    box_mesh("desk", [(W / 2 - 0.4, -0.9, 0.76, 0.32, 0.6, 0.025)] + [(W / 2 - 0.4 + sx * 0.28, -0.9 + sy * 0.55, 0.38, 0.02, 0.02, 0.38)
                                                                   for sx in (-1, 1) for sy in (-1, 1)], wood)
    wood_chair((W / 2 - 0.95, -0.95, 0), math.radians(90), name="dchair", col=(0.15, 0.08, 0.035))
    box_mesh("nightstand", [(0.85, 2.15, 0.3, 0.22, 0.2, 0.3)], wood)
    out = {}
    if not sep:
        out["tw"] = typewriter((W / 2 - 0.4, -0.85, 0.785), math.radians(-90))
        luggage_rack((-0.2, -0.05, 0), 0.0)
        out["case"] = suitcase((-0.2, -0.05, 0.505), 0.0, state=case_state)
        out["bedlamp"] = bedside_lamp((0.85, 2.15, 0.6), on=lamp_on, energy=lamp_energy, name="lamp217")
        out["desklamp"] = bedside_lamp((W / 2 - 0.25, -1.3, 0.785), on=lamp_on, energy=lamp_energy * 0.8, name="desklamp217",
                                       shade_col=(0.25, 0.45, 0.3))
    # door (S wall)
    piv, slab = door_slab("d217in", (door[0] - 0.47, -D / 2 - 0.05, 0), width=0.94, height=2.2,
                          mat=L.mat_principled("d217m", (0.16, 0.07, 0.035), rough=0.4))
    piv.rotation_euler = (0, 0, door_angle)
    out["door"] = piv
    # moonlight / daylight through the window
    if sep:
        ml = L.area((W / 2 + 0.8, win[0], 2.0), (0, -math.pi / 2, 0), energy=500, size=1.4, color=(1.0, 0.82, 0.58), name="daywin")
        L.area((0, 0, Hh - 0.05), (0, 0, 0), energy=70, size=3, color=(0.9, 0.75, 0.55), name="sepfill")
    else:
        ml = L.spot((W / 2 + 2.5, win[0] + 0.4, 3.6), (0, 0, 0), energy=1500 * moon, size_deg=35, blend=0.3, color=(0.55, 0.68, 1.0),
                    name="moon217", radius=0.05)
        aim(ml, (W / 2 + 2.5, win[0] + 0.4, 3.6), (-0.4, 0.4, 0.2))
        L.area((0, 0, Hh - 0.05), (0, 0, 0), energy=30 * moon, size=3, color=(0.55, 0.62, 0.9), name="ambf217")
    out["win_light"] = ml
    if gaslamp:
        out["gas"] = gas_lamp((-W / 2 + 0.02, 0.9, 1.9), sep)
    if fog:
        out["fog"] = room_fog((0, 0, Hh / 2), (W, D, Hh), density=fog, color=(0.8, 0.72, 0.6) if sep else (0.65, 0.68, 0.8))
    if dust_count:
        out["dust"] = dust((0, 0, 1.5), (W * 0.8, D * 0.8, 2.2), n, count=dust_count, radius=0.0025, emit=0.05)
    return out


def gas_lamp(loc, sepia=True, name="gas"):
    """Wall gas bracket on the W wall (faces +x): brass arm + frosted glass globe with small flame glow + a shimmer volume."""
    root = empty(name, loc)
    br = mat_brass(name + "_b")
    box_mesh(name + "_arm", [(0.0, 0, 0, 0.015, 0.06, 0.09), (0.12, 0, 0.0, 0.12, 0.012, 0.012), (0.24, 0, 0.06, 0.012, 0.012, 0.06)], br, parent=root)
    gm = L.mat_principled(name + "_glass", (0.9, 0.85, 0.72), rough=0.3, emit=(1.0, 0.75, 0.45), emit_strength=1.2, alpha=0.7)
    g = L.prim("sphere", loc=(0.24, 0, 0.2), segments=20, ring_count=12, radius=0.09)
    L.assign(g, gm)
    g.parent = root
    li = L.point((0, 0, 0), energy=25, color=(1.0, 0.72, 0.42), radius=0.05, name=name + "_l")
    li.parent = root
    li.location = (0.24, 0, 0.2)
    # heat shimmer: small volume with animated noise density
    m, n_, l = _nodes(name + "_shim")
    for nd in list(n_):
        if nd.type == "BSDF_PRINCIPLED":
            n_.remove(nd)
    tc = n_.new("ShaderNodeTexCoord")
    mp = n_.new("ShaderNodeMapping")
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = n_.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 6
    l.new(mp.outputs[0], nz.inputs["Vector"])
    v = n_.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (0.9, 0.8, 0.6, 1)
    dens = _math(n_, l, "MULTIPLY", _math(n_, l, "MAXIMUM", _math(n_, l, "SUBTRACT", nz.outputs["Fac"], 0.5), 0.0), 2.5)
    l.new(dens, v.inputs["Density"])
    l.new(v.outputs[0], n_["Material Output"].inputs["Volume"])
    sh = L.prim("cube", loc=(0.3, 0, 0.45), name=name + "_shimmer")
    sh.scale = (0.25, 0.3, 0.35)
    L.assign(sh, m)
    sh.parent = root
    mp.inputs["Location"].default_value = (0, 0, 0)
    mp.inputs["Location"].keyframe_insert("default_value", frame=1)
    mp.inputs["Location"].default_value = (0.2, 0.1, -1.5)
    mp.inputs["Location"].keyframe_insert("default_value", frame=200)
    return {"root": root, "light": li, "glass": gm}


def candle(parent=None, loc=(0, 0, 0), name="candle", energy=40):
    root = empty(name, loc, parent=parent)
    wax = L.mat_principled(name + "_wax", (0.85, 0.82, 0.7), rough=0.6)
    holder = mat_brass(name + "_h")
    d = L.prim("cyl", loc=(0, 0, 0), vertices=16, radius=0.06, depth=0.015)
    L.assign(d, holder)
    d.parent = root
    c = L.prim("cyl", loc=(0, 0, 0.07), vertices=12, radius=0.015, depth=0.13)
    L.assign(c, wax)
    c.parent = root
    fm = L.mat_emission(name + "_f", (1.0, 0.7, 0.3), 25)
    f = L.prim("sphere", loc=(0, 0, 0.155), segments=10, ring_count=6, radius=0.012)
    f.scale = (1, 1, 2.0)
    L.assign(f, fm)
    f.parent = root
    li = L.point((0, 0, 0), energy=energy, color=(1.0, 0.65, 0.3), radius=0.02, name=name + "_l")
    li.parent = root
    li.location = (0, 0, 0.2)
    return {"root": root, "light": li, "flame": fm}


def linen_trolley(loc, rot_z=0.0, name="trolley"):
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_principled(name + "_m", (0.3, 0.28, 0.25), rough=0.6, metal=0.4)
    lin = L.mat_principled(name + "_lin", (0.75, 0.74, 0.7), rough=0.9)
    box_mesh(name + "_f", [(0, 0, 0.18, 0.45, 0.25, 0.015), (0, 0, 0.62, 0.45, 0.25, 0.015)] +
             [(sx * 0.43, sy * 0.23, 0.45, 0.015, 0.015, 0.35) for sx in (-1, 1) for sy in (-1, 1)], m, parent=root)
    box_mesh(name + "_lin", [(sx * 0.2, 0, 0.7, 0.18, 0.2, 0.06) for sx in (-1, 1)] + [(0, 0, 0.27, 0.38, 0.2, 0.07)], lin, parent=root, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            w = L.prim("cyl", loc=(sx * 0.4, sy * 0.2, 0.05), vertices=10, radius=0.05, depth=0.03, rot=(0, math.pi / 2, 0))
            L.assign(w, m)
            w.parent = root
    return root


def fire_hose(points, n, start_frac=0.15, end_frame=None, name="hose", radius=0.045):
    """Canvas fire hose along a polyline that 'grows' toward camera (bevel factor) with a brass nozzle riding the head."""
    pts = [Vector(p) for p in points]
    # dense resample
    dense = []
    for i in range(len(pts) - 1):
        for k in range(12):
            dense.append(pts[i].lerp(pts[i + 1], k / 12))
    dense.append(pts[-1])
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    sp = cu.splines.new("POLY")
    sp.points.add(len(dense) - 1)
    for i, p in enumerate(dense):
        sp.points[i].co = (*p, 1)
    o = L.link(bpy.data.objects.new(name, cu))
    o.data.materials.append(L.mat_noise_surface(name + "_m", (0.45, 0.4, 0.3), (0.65, 0.6, 0.48), scale=40, bump=0.3, voronoi=False, rough=0.9))
    try:
        cu.bevel_factor_mapping_end = "SPLINE"
    except Exception:
        pass
    ef = end_frame or n
    cu.bevel_factor_end = start_frac
    cu.keyframe_insert("bevel_factor_end", frame=1)
    cu.bevel_factor_end = 1.0
    cu.keyframe_insert("bevel_factor_end", frame=ef)
    # nozzle follows head: precompute arc length
    seg = [0.0]
    for i in range(1, len(dense)):
        seg.append(seg[-1] + (dense[i] - dense[i - 1]).length)
    total = seg[-1]
    noz = L.prim("cone", loc=(0, 0, 0), vertices=16, radius1=radius * 1.3, radius2=radius * 0.5, depth=0.32)
    L.assign(noz, mat_brass(name + "_noz"))
    fc = None
    for f in range(1, ef + 1, 2):
        u = start_frac + (1 - start_frac) * (f - 1) / max(1, ef - 1)
        # bevel factor is linear in spline param (points evenly param'd), so index by u directly
        fi = u * (len(dense) - 1)
        i0 = min(int(fi), len(dense) - 2)
        p = dense[i0].lerp(dense[i0 + 1], fi - i0)
        d = (dense[i0 + 1] - dense[i0]).normalized()
        noz.location = p + d * 0.16
        noz.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        noz.keyframe_insert("location", frame=f)
        noz.keyframe_insert("rotation_euler", frame=f)
    L.linear_fcurves(noz)
    _interp_data(cu, "LINEAR")
    return o, noz


# ============================================================================ ARCHER AVENUE sets (HAUNT-03)
# World layout: Archer road runs along +Y at x=0 (width 7, right lane x=+1.75). Cemetery set: gates along X at y=0 facing -Y,
# cemetery road along X between y=-9 and y=-2. Dance hall: front facade at y=0 facing -Y, 22 m along X.

def _tube(bm, pts, r0, r1=None, sides=6):
    """Tapered tube through a polyline of points (Vector). Appends to bm."""
    r1 = r0 if r1 is None else r1
    rings = []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        d = (b - a).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
        u = d.cross(up).normalized()
        v = d.cross(u).normalized()
        r = r0 + (r1 - r0) * i / max(1, len(pts) - 1)
        rings.append([bm.verts.new(p + (u * math.cos(k * 2 * math.pi / sides) + v * math.sin(k * 2 * math.pi / sides)) * r)
                      for k in range(sides)])
    for j in range(len(rings) - 1):
        for k in range(sides):
            bm.faces.new((rings[j][k], rings[j][(k + 1) % sides], rings[j + 1][(k + 1) % sides], rings[j + 1][k]))
    return rings


def bare_forest(name, regions, count=80, seed=3, height=(6.0, 12.0), mat=None, depth=3):
    """Many bare deciduous trees in ONE mesh (cheap). regions: [(xmin, xmax, ymin, ymax)]."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    tot = sum((r[1] - r[0]) * (r[3] - r[2]) for r in regions)

    def branch(base, d, length, rad, lvl):
        end = base + d * length
        mid = (base + end) / 2 + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * length * 0.06
        _tube(bm, [base, mid, end], rad, rad * 0.6, sides=5 if lvl > 1 else 4)
        if lvl > 0:
            for _ in range(rnd.randint(2, 3)):
                nd = (d + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.05, 0.6)))).normalized()
                if nd.z < 0.1:
                    nd.z = 0.1
                    nd.normalize()
                branch(end - d * length * rnd.uniform(0, 0.25), nd, length * rnd.uniform(0.5, 0.72), rad * 0.55, lvl - 1)

    for reg in regions:
        k = max(1, int(round(count * (reg[1] - reg[0]) * (reg[3] - reg[2]) / tot)))
        for i in range(k):
            x, y = rnd.uniform(reg[0], reg[1]), rnd.uniform(reg[2], reg[3])
            h = rnd.uniform(*height)
            lean = Vector((rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08), 1)).normalized()
            branch(Vector((x, y, -0.3)), lean, h * 0.42, h * 0.026, depth)
    o = L.mesh_from_bm(name, bm)
    L.assign(o, mat or L.mat_noise_surface(name + "_bark", (0.012, 0.012, 0.012), (0.05, 0.045, 0.04), scale=6, bump=0.3, voronoi=False))
    return o


def ground_box(name, x0, x1, y0, y1, z=0.0, mat=None):
    """Flat ground quad in world coords (object coords = metres, so noise materials keep real scale)."""
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in ((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z))]
    bm.faces.new(vs)
    o = L.mesh_from_bm(name, bm)
    if mat:
        L.assign(o, mat)
    return o


def mat_gravel(name="gravel"):
    return L.mat_noise_surface(name, (0.05, 0.05, 0.05), (0.17, 0.16, 0.15), scale=9, bump=0.5, voronoi=True, rough=0.9)


def mat_verge(name="verge"):
    return L.mat_noise_surface(name, (0.012, 0.016, 0.01), (0.05, 0.055, 0.035), scale=3, bump=0.4, voronoi=False, rough=1.0)


def mat_limestone(name="limestone"):
    return L.mat_noise_surface(name, (0.3, 0.29, 0.26), (0.55, 0.53, 0.48), scale=3.5, bump=0.35, voronoi=True, rough=0.85)


def archer_road(y0=-30.0, y1=230.0, forest=True, fog=0.05, fog_h=2.4, count=130, seed=3, dashes=True):
    """Two-lane wet country road along +Y through bare woods, low fog over the verges."""
    box_mesh("road", [(0, (y0 + y1) / 2, 0.0, 3.5, (y1 - y0) / 2, 0.01)], mat_wet_road("archer_wet"))
    ground_box("verge", -60, 60, y0, y1 + 40, -0.02, mat_verge())
    if dashes:
        lm = L.mat_principled("cline", (0.45, 0.38, 0.16), rough=0.5, emit=(0.3, 0.25, 0.1), emit_strength=0.05)
        box_mesh("centreline", [(0.0, y, 0.012, 0.06, 1.5, 0.002) for y in range(int(y0), int(y1), 7)], lm)
    tr = None
    if forest:
        tr = bare_forest("woods", [(-40, -5.2, y0, y1), (5.2, 40, y0, y1)], count=count, seed=seed)
    fg = None
    if fog:
        fg = L.fog_volume(center=(0, (y0 + y1) / 2, fog_h / 2), size=(70, y1 - y0, fog_h), density=fog, color=(0.72, 0.75, 0.82))
    return {"trees": tr, "fog": fg}


def pale_woman(name="mary", height=1.62, alpha=1.0, emit=0.15, color=(0.75, 0.75, 0.72)):
    """Faceless pale woman in a long 1930s dress (figure(dress=True)), soft emission so she reads in fog."""
    p = figure(name, color=color, height=height, dress=True)
    m = p["torso"].data.materials[0]
    pr = m.node_tree.nodes["Principled BSDF"]
    pr.inputs["Emission Color"].default_value = (0.85, 0.88, 0.92, 1)
    pr.inputs["Emission Strength"].default_value = emit
    pr.inputs["Roughness"].default_value = 0.9
    s = height / 1.75
    hair = L.prim("sphere", loc=(0, -0.03 * s, 0.1 * s), segments=14, ring_count=8, radius=0.1 * s)
    hair.scale = (1.12, 1.05, 1.15)
    L.assign(hair, m)
    hair.parent = p["neck"]
    # slightly flared hem + narrow waist so the silhouette reads as a dress, not a cone
    p["dress"].scale = (1.0, 0.85, 1.0)
    if alpha < 1.0:
        pr.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    p["mat"] = m
    return p


def set_alpha(mat, pairs):
    """Animate principled alpha [(frame, a)] (material must be BLENDED/dithered)."""
    pr = mat.node_tree.nodes["Principled BSDF"]
    try:
        mat.surface_render_method = "BLENDED"
    except Exception:
        pass
    for f, a in pairs:
        pr.inputs["Alpha"].default_value = a
        pr.inputs["Alpha"].keyframe_insert("default_value", frame=f)


def car_1930s(name="car", loc=(0, 0, 0), rot_z=0.0, body=(0.02, 0.022, 0.025), lamps=True, lamp_energy=900, tail=1.0,
              door_open=0.0, police=False):
    """1930s sedan silhouette facing +Y local: long hood, upright cabin, separate fenders, running boards, spare wheel.
    Returns dict root, spots, tail_light, tail_mat, head_mat, door (hinge empty, passenger/right side)."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    bm_ = L.mat_principled(name + "_paint", body, rough=0.28, metal=0.3)
    chrome = L.mat_principled(name + "_chrome", (0.6, 0.6, 0.62), rough=0.2, metal=1.0)
    glass = L.mat_principled(name + "_glass", (0.01, 0.012, 0.016), rough=0.05, metal=0.2)
    tyre = L.mat_principled(name + "_tyre", (0.01, 0.01, 0.01), rough=0.8)
    box_mesh(name + "_body", [(0, -0.2, 0.74, 0.66, 1.75, 0.24),           # main tub
                             (0, 1.55, 0.86, 0.46, 0.65, 0.2),             # long hood
                             (0, -1.9, 0.8, 0.62, 0.3, 0.28)], bm_, parent=root, bevel=0.07)
    box_mesh(name + "_cabin", [(0, -0.55, 1.26, 0.74, 1.0, 0.35)], bm_, parent=root, bevel=0.2)
    box_mesh(name + "_fender", [(sx * 0.8, sy * 1.45 - 0.1, 0.66, 0.15, 0.55, 0.13) for sx in (-1, 1) for sy in (-1, 1)], bm_,
             parent=root, bevel=0.1)
    box_mesh(name + "_win", [(0, -0.55, 1.3, 0.75, 0.92, 0.2), (0, 0.46, 1.3, 0.68, 0.01, 0.2)], glass, parent=root)
    box_mesh(name + "_grille", [(0, 2.21, 0.82, 0.32, 0.04, 0.24)], chrome, parent=root, bevel=0.02)
    box_mesh(name + "_board", [(sx * 0.8, -0.05, 0.42, 0.12, 0.85, 0.02) for sx in (-1, 1)], tyre, parent=root)
    box_mesh(name + "_bump", [(0, 2.42, 0.48, 0.85, 0.04, 0.05), (0, -2.32, 0.48, 0.85, 0.04, 0.05)], chrome, parent=root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            w = L.prim("cyl", loc=(sx * 0.8, sy * 1.45 - 0.1, 0.36), vertices=16, radius=0.36, depth=0.2, rot=(0, math.pi / 2, 0))
            L.assign(w, tyre)
            w.parent = root
            hub = L.prim("cyl", loc=(sx * 0.91, sy * 1.45 - 0.1, 0.36), vertices=12, radius=0.12, depth=0.02, rot=(0, math.pi / 2, 0))
            L.assign(hub, chrome)
            hub.parent = root
    sp_ = L.prim("torus", loc=(0, -2.25, 0.95), major_radius=0.3, minor_radius=0.08, rot=(math.pi / 2, 0, 0))
    L.assign(sp_, tyre)
    sp_.parent = root
    head_mat = L.mat_emission(name + "_lamp", (1.0, 0.86, 0.6), 25.0 if lamps else 0.0)
    tail_mat = L.mat_emission(name + "_tail", (1.0, 0.05, 0.02), 6.0 * tail)
    spots = []
    for sx in (-1, 1):
        h = L.prim("sphere", loc=(sx * 0.6, 2.2, 1.02), segments=14, ring_count=8, radius=0.13)
        h.scale = (1, 0.7, 1)
        L.assign(h, head_mat if lamps else chrome)
        h.parent = root
        t = L.prim("sphere", loc=(sx * 0.72, -2.2, 0.85), segments=10, ring_count=6, radius=0.05)
        L.assign(t, tail_mat)
        t.parent = root
        if lamps:
            s = L.spot((0, 0, 0), (math.pi / 2 - 0.07, 0, 0), energy=lamp_energy, size_deg=30, blend=0.5, color=(1.0, 0.88, 0.66),
                       name=f"{name}_hl{sx}", radius=0.08)
            s.parent = root
            s.location = (sx * 0.6, 2.35, 1.02)
            spots.append(s)
    tl = L.point((0, -2.7, 0.6), energy=40 * tail, color=(1.0, 0.05, 0.02), radius=0.3, name=name + "_brake")
    tl.parent = root
    out = {"root": root, "spots": spots, "tail_light": tl, "tail_mat": tail_mat, "head_mat": head_mat}
    # passenger (right, +X) front door as separate hinged slab
    # rear-hinged ("suicide") front door, typical of the period: opens forward, door_open in radians
    hinge = empty(name + "_dhinge", (0.76, -0.5, 0.48), parent=root)
    box_mesh(name + "_door", [(0, 0.45, 0.5, 0.03, 0.45, 0.5)], bm_, parent=hinge)
    box_mesh(name + "_dwin", [(0.006, 0.45, 0.8, 0.03, 0.38, 0.17)], glass, parent=hinge)
    hinge.rotation_euler = (0, 0, -door_open)
    out["door"] = hinge
    if police:
        bar = box_mesh(name + "_bar", [(0, -0.5, 1.68, 0.55, 0.12, 0.06)], L.mat_principled(name + "_barm", (0.1, 0.1, 0.1)), parent=root)
        rm = L.mat_emission(name + "_red", (1.0, 0.02, 0.02), 30)
        bmm = L.mat_emission(name + "_blue", (0.05, 0.2, 1.0), 30)
        r = box_mesh(name + "_rl", [(-0.32, -0.5, 1.68, 0.2, 0.13, 0.065)], rm, parent=root)
        b = box_mesh(name + "_bl", [(0.32, -0.5, 1.68, 0.2, 0.13, 0.065)], bmm, parent=root)
        rl = L.point((-0.4, -0.5, 1.9), energy=900, color=(1.0, 0.03, 0.02), radius=0.15, name=name + "_redl")
        bl = L.point((0.4, -0.5, 1.9), energy=900, color=(0.1, 0.25, 1.0), radius=0.15, name=name + "_bluel")
        rl.parent = root
        bl.parent = root
        out.update({"red": rl, "blue": bl, "red_mat": rm, "blue_mat": bmm})
    return out


def police_flash(car, n, hz=2.0, energy=900, fade=None):
    """Alternating red/blue at hz (each colour half a cycle). fade=(f0,f1) ramps to 0."""
    fps = bpy.context.scene.render.fps
    half = max(1, int(round(fps / hz / 2)))
    for f in range(1, n + 2):
        on_red = ((f - 1) // half) % 2 == 0
        k = 1.0
        if fade:
            k = max(0.0, min(1.0, (fade[1] - f) / max(1, fade[1] - fade[0])))
        car["red"].data.energy = energy * k if on_red else 0.0
        car["blue"].data.energy = 0.0 if on_red else energy * k
        car["red"].data.keyframe_insert("energy", frame=f)
        car["blue"].data.keyframe_insert("energy", frame=f)
    for o in (car["red"], car["blue"]):
        _interp_data(o.data, "CONSTANT")
    for mat, red in ((car["red_mat"], True), (car["blue_mat"], False)):
        node = next(nd for nd in mat.node_tree.nodes if nd.type == "EMISSION")
        for f in range(1, n + 2, half):
            on_red = ((f - 1) // half) % 2 == 0
            node.inputs[1].default_value = 30.0 if (on_red == red) else 0.5
            node.inputs[1].keyframe_insert("default_value", frame=f)
        _interp_data(mat.node_tree, "CONSTANT")


def cemetery_gates(loc=(0, 0, 0), bent=False, prints=False, wall_len=26.0, stones=True, trees=True, road=True, seed=5):
    """Iron gates between two limestone piers along X (facing -Y), low stone walls, lawn + headstones behind,
    wet road in front (y -9..-2). bent: two left-of-centre bars bowed out toward the road; prints: scorched palm marks."""
    root = empty("gates", loc)
    lime = mat_limestone()
    iron = L.mat_principled("iron", (0.03, 0.032, 0.034), rough=0.32, metal=0.75)
    ow = 3.2
    nb = 22
    pier_x = ow / 2 + 0.45
    for sx in (-1, 1):
        box_mesh(f"pier{sx}", [(sx * pier_x, 0, 1.6, 0.45, 0.45, 1.6), (sx * pier_x, 0, 3.27, 0.52, 0.52, 0.07),
                               (sx * pier_x, 0, 0.12, 0.52, 0.52, 0.12)], lime, parent=root, bevel=0.02)
        f = L.prim("sphere", loc=(sx * pier_x, 0, 3.62), segments=18, ring_count=10, radius=0.27)
        L.assign(f, lime)
        L.smooth(f)
        f.parent = root
        nk = L.prim("cyl", loc=(sx * pier_x, 0, 3.38), vertices=12, radius=0.14, depth=0.12)
        L.assign(nk, lime)
        nk.parent = root
    # bars
    bm = bmesh.new()
    bent_idx = (8, 9)
    tips = []
    bar_r, hgt = 0.013, 2.6
    xs = [-ow / 2 + ow * (i + 0.5) / nb for i in range(nb)]
    for i, x in enumerate(xs):
        if bent and i in bent_idx:
            pts = []
            side = -1 if i == bent_idx[0] else 1
            for k in range(13):
                t = k / 12
                z = 0.1 + t * hgt
                w = math.sin(math.pi * min(1, max(0, (z - 0.4) / 1.6))) if z < 2.0 else 0.0
                pts.append(Vector((x + side * 0.055 * w, -0.16 * w, z)))
            _tube(bm, pts, bar_r, bar_r, sides=8)
        else:
            _tube(bm, [Vector((x, 0, 0.1)), Vector((x, 0, 0.1 + hgt))], bar_r, bar_r, sides=8)
        tips.append((x, 0.1 + hgt))
    bars = L.mesh_from_bm("bars", bm)
    L.assign(bars, iron)
    bars.parent = root
    L.smooth(bars)
    bmt = bmesh.new()
    for x, z in tips:
        bmesh.ops.create_cone(bmt, cap_ends=True, segments=6, radius1=0.028, radius2=0.0, depth=0.16,
                              matrix=Matrix.Translation((x, 0, z + 0.08)))
    tp = L.mesh_from_bm("bartips", bmt)
    L.assign(tp, iron)
    tp.parent = root
    rails = [(0, 0, 0.42, ow / 2, 0.022, 0.03), (0, 0, 2.25, ow / 2, 0.022, 0.03), (0, 0, 2.5, ow / 2, 0.018, 0.02),
             (0, 0, 1.35, 0.03, 0.03, 1.3)]
    for sx in (-1, 1):
        rails.append((sx * (ow / 2 - 0.03), 0, 1.35, 0.03, 0.03, 1.3))
    box_mesh("rails", rails, iron, parent=root)
    if prints:
        pm = L.mat_noise_surface("scorch", (0.015, 0.008, 0.004), (0.07, 0.035, 0.015), scale=60, bump=0.6, voronoi=False, rough=1.0)
        for j, i in enumerate(bent_idx):
            side = -1 if j == 0 else 1
            x = xs[i] + side * 0.052
            z = 1.12 + 0.04 * j
            w = math.sin(math.pi * (z - 0.4) / 1.6)
            y = -0.16 * w
            palm = L.prim("sphere", loc=(x, y - 0.002, z), segments=12, ring_count=8, radius=1)
            palm.scale = (0.017, 0.017, 0.036)
            L.assign(palm, pm)
            palm.parent = root
            for k in range(4):
                fg = L.prim("sphere", loc=(x + (k - 1.5) * 0.004, y - 0.002, z + 0.065 + 0.012 * (1 - abs(k - 1.5) / 1.5)),
                            segments=8, ring_count=6, radius=1)
                fg.scale = (0.0142, 0.0142, 0.02)
                L.assign(fg, pm)
                fg.parent = root
    # walls
    wl = (wall_len - pier_x - 0.45) / 2
    wx = pier_x + 0.45 + wl
    box_mesh("cwall", [(sx * wx, 0, 0.55, wl, 0.25, 0.55) for sx in (-1, 1)] +
             [(sx * wx, 0, 1.13, wl + 0.02, 0.3, 0.05) for sx in (-1, 1)], lime, parent=root)
    grass = mat_verge("lawn")
    ground_box("lawn", -60, 60, 0.3, 80, 0.0, grass)
    ground_box("cverge", -60, 60, -2.0, 0.3, 0.005, grass)
    if road:
        box_mesh("croad", [(0, -5.5, 0.0, 60, 3.5, 0.01)], mat_wet_road("cwet"))
        ground_box("sverge", -60, 60, -40, -9, 0.005, grass)
        lm = L.mat_principled("ccline", (0.45, 0.38, 0.16), rough=0.5)
        box_mesh("ccentre", [(x, -5.5, 0.012, 1.5, 0.06, 0.002) for x in range(-58, 60, 7)], lm)
    st = []
    if stones:
        rnd = random.Random(seed)
        stm = L.mat_noise_surface("stone", (0.2, 0.2, 0.19), (0.42, 0.41, 0.38), scale=4, bump=0.4, voronoi=True)
        boxes = []
        for i in range(40):
            x, y = rnd.uniform(-22, 22), rnd.uniform(4, 40)
            if abs(x) < 2.5 and y < 9:
                continue
            boxes.append((x, y, 0.4, rnd.uniform(0.25, 0.4), 0.08, rnd.uniform(0.3, 0.55), rnd.uniform(-0.15, 0.15)))
        st.append(box_mesh("headstones", boxes, stm, bevel=0.03))
    if trees:
        bare_forest("ctrees", [(-30, 30, 12, 45)], count=22, seed=seed + 2, height=(7, 13))
        bare_forest("ctrees_s", [(-40, 40, -40, -14)], count=14, seed=seed + 4, height=(7, 12))
    return {"root": root, "bars": bars, "xs": xs, "bent_idx": bent_idx}


def headstone_row(xs, y=0.0, h=0.85, w=0.6, t=0.14, name="hs"):
    """Plain blank upright headstones (round-topped), no names, no dates."""
    stm = L.mat_noise_surface(name + "_m", (0.28, 0.28, 0.27), (0.5, 0.49, 0.46), scale=5, bump=0.35, voronoi=True, rough=0.8)
    out = []
    for i, x in enumerate(xs):
        b = box_mesh(f"{name}{i}", [(x, y, h / 2 - 0.1, w / 2, t / 2, h / 2)], stm, bevel=0.025)
        c = L.prim("cyl", loc=(x, y, h - 0.1), vertices=24, radius=w / 2, depth=t, rot=(math.pi / 2, 0, 0))
        c.scale = (1, 0.45, 1)
        L.assign(c, stm)
        base = box_mesh(f"{name}{i}_base", [(x, y, 0.06, w / 2 + 0.08, t / 2 + 0.1, 0.08)], stm, bevel=0.02)
        out += [b, c, base]
    return out


def dance_hall(n, doors_open=None, cars=True, sign=True, gravel=True):
    """1930s single-storey suburban dance hall, front facade at y=0 facing -Y, 22 x 12 m, hipped roof,
    six tall arched amber windows, canopy over double doors, unlit rooftop 'BALLROOM' sign, gravel car park.
    doors_open: (f0, f1) animate the double doors opening between those frames (else closed)."""
    Wd, Dp, Ht = 22.0, 12.0, 5.2
    stucco = L.mat_noise_surface("stucco", (0.26, 0.24, 0.21), (0.42, 0.39, 0.34), scale=2.0, bump=0.12, voronoi=False, rough=0.85)
    roofm = L.mat_noise_surface("hallroof", (0.03, 0.03, 0.035), (0.09, 0.085, 0.08), scale=6, bump=0.3, voronoi=False, rough=0.7)
    trim = L.mat_principled("halltrim", (0.55, 0.5, 0.42), rough=0.6)
    glow = L.mat_emission("hallglow", (1.0, 0.62, 0.28), 4.0)
    door = (0.0, 2.2, 0.0, 2.7)
    wall_with_openings("hallfront", "x", 0.0, Wd, Ht, [door], mat=stucco, outward=-1)
    box_mesh("hallbody", [(0, (Dp + 2.4) / 2, Ht / 2, Wd / 2, (Dp - 2.4) / 2, Ht / 2), (-Wd / 2 + 0.1, 1.2, Ht / 2, 0.1, 1.2, Ht / 2),
                          (Wd / 2 - 0.1, 1.2, Ht / 2, 0.1, 1.2, Ht / 2), (0, 1.2, Ht - 0.1, Wd / 2, 1.2, 0.1),
                          (-1.7, 1.2, Ht / 2, 0.05, 1.2, Ht / 2), (1.7, 1.2, Ht / 2, 0.05, 1.2, Ht / 2)], stucco)
    box_mesh("hallcornice", [(0, -0.12, Ht - 0.1, Wd / 2 + 0.15, 0.12, 0.12), (0, -0.12, 0.2, Wd / 2 + 0.05, 0.08, 0.2)], trim)
    _hip_roof("hallroof", (0, Dp / 2, Ht), Wd + 0.8, Dp + 0.8, 2.0, roofm)
    # six tall arched windows: emissive panes + dark mullions/glazing bars
    wxs = (-9.0, -6.2, -3.4, 3.4, 6.2, 9.0)
    panes, mull = [], []
    for x in wxs:
        panes.append((x, -0.12, 2.15, 0.6, 0.02, 1.25))
        for k in (-1, 0, 1):
            mull.append((x + k * 0.3, -0.15, 2.4, 0.025, 0.02, 1.5))
        for z in (1.4, 2.2, 3.0):
            mull.append((x, -0.15, z, 0.6, 0.02, 0.022))
        mull.append((x, -0.16, 0.86, 0.72, 0.06, 0.04))
    box_mesh("hallpanes", panes, glow)
    box_mesh("hallmull", mull, L.mat_principled("mullm", (0.04, 0.035, 0.03), rough=0.7))
    for x in wxs:
        a = L.prim("cyl", loc=(x, -0.12, 3.4), vertices=24, radius=0.6, depth=0.04, rot=(math.pi / 2, 0, 0))
        L.assign(a, glow)
        ar = L.prim("torus", loc=(x, -0.14, 3.4), major_radius=0.64, minor_radius=0.05, rot=(math.pi / 2, 0, 0))
        L.assign(ar, trim)
    for x in (-7.6, -3.4, 3.4, 7.6):
        L.area((x, -1.2, 2.6), (math.radians(80), 0, 0), energy=260, size=2.2, color=(1.0, 0.62, 0.3), name="winspill")
    # interior behind the doors
    box_mesh("foyer", [(0, 1.6, 1.6, 1.6, 0.05, 1.6), (0, 0.8, 0.0, 1.6, 0.8, 0.02)], L.mat_principled("foyerm", (0.6, 0.42, 0.24), rough=0.6,
                                                                                                         emit=(1.0, 0.6, 0.3), emit_strength=1.2))
    fl = L.point((0, 1.0, 2.2), energy=300, color=(1.0, 0.62, 0.3), radius=0.4, name="foyerlight")
    dm = L.mat_principled("halldoor", (0.12, 0.06, 0.03), rough=0.5)
    dl, _ = door_slab("hdoorL", (-1.1, -0.06, 0), width=1.1, height=2.7, mat=dm)
    dr, _ = door_slab("hdoorR", (1.1, -0.06, 0), width=1.1, height=2.7, mat=dm)
    dr.rotation_euler = (0, 0, math.pi)
    spill = L.spot((0, 1.0, 2.3), (-math.radians(62), 0, 0), energy=0, size_deg=95, blend=0.5, color=(1.0, 0.62, 0.3), name="doorspill",
                   radius=0.3)
    if doors_open:
        f0, f1 = doors_open
        for piv, a0, a1 in ((dl, 0.0, -1.8), (dr, math.pi, math.pi + 1.8)):
            piv.rotation_euler = (0, 0, a0)
            piv.keyframe_insert("rotation_euler", index=2, frame=f0)
            piv.rotation_euler = (0, 0, a1)
            piv.keyframe_insert("rotation_euler", index=2, frame=f1)
        key_energy(spill, [(f0, 0.0), (f1, 1500.0)], "LINEAR")
    # canopy on two posts + bulbs under it
    box_mesh("canopy", [(0, -1.25, 3.05, 2.1, 1.25, 0.08)], trim)
    box_mesh("canposts", [(sx * 1.95, -2.35, 1.5, 0.07, 0.07, 1.5) for sx in (-1, 1)], trim)
    cb = L.mat_emission("canbulb", (1.0, 0.75, 0.45), 15)
    for x in (-1.3, 0, 1.3):
        b = L.prim("sphere", loc=(x, -2.2, 2.9), segments=10, ring_count=6, radius=0.06)
        L.assign(b, cb)
    L.point((0, -1.6, 2.7), energy=120, color=(1.0, 0.72, 0.42), radius=0.3, name="canlight")
    if sign:
        sm = L.mat_principled("signm", (0.62, 0.58, 0.5), rough=0.6, emit=(0.9, 0.85, 0.75), emit_strength=0.25)
        box_mesh("signframe", [(0, 1.2, Ht + 1.9, 4.3, 0.05, 0.75)] + [(sx * 3.6, 1.25, Ht + 0.9, 0.05, 0.05, 1.0) for sx in (-1, 1)],
                 L.mat_principled("signbk", (0.05, 0.045, 0.04), rough=0.6))
        L.text3d("BALLROOM", loc=(0, 1.13, Ht + 1.55), size=1.05, extrude=0.04, mat=sm, name="signtxt")
    if gravel:
        ground_box("carpark", -30, 30, -26, -0.1, 0.0, mat_gravel())
        ground_box("hallgrass", -60, 60, -60, 60, -0.03, mat_verge("hverge"))
    if cars:
        car_1930s("park1", (-7.0, -8.5, 0), math.radians(8), lamps=False, tail=0.0)
        car_1930s("park2", (7.5, -9.5, 0), math.radians(-5), body=(0.04, 0.03, 0.025), lamps=False, tail=0.0)
    bare_forest("halltrees", [(-34, 34, 16, 40), (-40, -14, -10, 16), (14, 40, -10, 16)], count=26, seed=11, height=(8, 14))
    return {"doors": (dl, dr), "spill": spill, "foyer_light": fl}


def wire_globe(loc, radius=1.0, color=(0.35, 0.75, 0.7), strength=2.0, n=100, deg=20.0, name="globe"):
    """Dark wireframe UV globe slowly rotating (deg over n frames)."""
    g = L.prim("sphere", loc=loc, segments=36, ring_count=18, radius=radius)
    w = g.modifiers.new("wire", "WIREFRAME")
    w.thickness = radius * 0.006
    L.assign(g, L.mat_emission(name + "_m", color, strength))
    g.rotation_euler = (math.radians(23), 0, 0)
    g.keyframe_insert("rotation_euler", frame=1)
    g.rotation_euler = (math.radians(23), 0, math.radians(deg))
    g.keyframe_insert("rotation_euler", frame=n)
    L.linear_fcurves(g)
    core = L.prim("sphere", loc=loc, segments=36, ring_count=18, radius=radius * 0.985)
    L.assign(core, L.mat_principled(name + "_core", (0.005, 0.01, 0.012), rough=0.5))
    return g


# ============================================================================ RAYNHAM / MANOR sets (HAUNT-04)
# Staircase layout: hall floor z=0. First flight rises +Y from y=0 (x -0.8..0.8), 14 steps (rise 0.18, going 0.3) to a
# half-landing (y 4.2..5.8, x -0.8..2.6, z 2.52). Return flight (10 steps) rises -Y at x 1.0..2.6 from the landing.
# Panelled walls: west x=-1.0, landing wall y=5.9 (leaded window above the landing at x=0), east x=2.75.

STAIR_RISE, STAIR_GO, STAIR_N = 0.18, 0.3, 14
LANDING_Z = STAIR_RISE * STAIR_N
LANDING_Y0 = STAIR_GO * STAIR_N


def _beam(bm, a, b, hw, hh):
    """Rectangular prism from a to b (Vectors), width 2*hw horizontal, height 2*hh roughly vertical."""
    d = (b - a).normalized()
    u = d.cross(Vector((0, 0, 1)))
    if u.length < 1e-4:
        u = Vector((1, 0, 0))
    u.normalize()
    v = u.cross(d).normalized()
    if v.z < 0:
        v = -v
    vs = []
    for p in (a, b):
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new(p + u * su * hw + v * sv * hh))
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f])


def _lathe(bm, base, prof, sides=8):
    """Turned shape: prof [(dz, r)] from base (Vector)."""
    rings = []
    for dz, r in prof:
        rings.append([bm.verts.new(base + Vector((r * math.cos(k * 2 * math.pi / sides), r * math.sin(k * 2 * math.pi / sides), dz)))
                      for k in range(sides)])
    for j in range(len(rings) - 1):
        for k in range(sides):
            bm.faces.new((rings[j][k], rings[j][(k + 1) % sides], rings[j + 1][(k + 1) % sides], rings[j + 1][k]))


BALUSTER = [(0, 0.03), (0.06, 0.03), (0.08, 0.022), (0.2, 0.018), (0.3, 0.032), (0.38, 0.034), (0.46, 0.02), (0.56, 0.016),
            (0.62, 0.026), (0.66, 0.026), (0.7, 0.018), (0.78, 0.018)]


def mat_oak(name="oak", dark=1.0):
    return L.mat_noise_surface(name, (0.05 * dark, 0.028 * dark, 0.013 * dark), (0.17 * dark, 0.095 * dark, 0.045 * dark),
                               scale=7, bump=0.15, voronoi=False, rough=0.45)


def panelled_wall(name, axis, fixed, a0, a1, z0, z1, side=1, pw=0.62, ph=0.85, mat=None, frame_mat=None, plaster_to=None):
    """Oak panelling on a wall plane. axis 'x' (wall runs along X at y=fixed) or 'y'. side: room-side normal sign.
    Back board + raised panel grid 2 cm proud. plaster_to: plain plaster from z1 up to this height."""
    mat = mat or mat_oak(name + "_oak")
    frame_mat = frame_mat or mat_oak(name + "_fr", 0.7)
    def B(ca, cz, ha, hz, off, t):
        c = fixed + side * off
        return (ca, c, cz, ha, t, hz) if axis == "x" else (c, ca, cz, t, ha, hz)
    boxes = [B((a0 + a1) / 2, (z0 + z1) / 2, (a1 - a0) / 2, (z1 - z0) / 2, -0.03, 0.03)]
    na = max(1, int((a1 - a0) / pw))
    nz = max(1, int((z1 - z0 - 0.3) / ph))
    sa = (a1 - a0) / na
    sz = (z1 - z0 - 0.3) / nz
    panels = []
    for i in range(na):
        for j in range(nz):
            panels.append(B(a0 + sa * (i + 0.5), z0 + 0.2 + sz * (j + 0.5), sa / 2 - 0.07, sz / 2 - 0.07, 0.012, 0.012))
    rails = [B((a0 + a1) / 2, z0 + 0.1, (a1 - a0) / 2, 0.1, 0.02, 0.02), B((a0 + a1) / 2, z1 - 0.04, (a1 - a0) / 2, 0.06, 0.035, 0.035)]
    box_mesh(name, boxes, frame_mat)
    box_mesh(name + "_pan", panels, mat, bevel=0.012)
    box_mesh(name + "_rail", rails, frame_mat)
    if plaster_to:
        pl = L.mat_noise_surface(name + "_pl", (0.36, 0.34, 0.3), (0.5, 0.47, 0.42), scale=2.5, bump=0.05, voronoi=False, rough=0.9)
        box_mesh(name + "_plaster", [B((a0 + a1) / 2, (z1 + plaster_to) / 2, (a1 - a0) / 2, (plaster_to - z1) / 2, -0.03, 0.03)], pl)


def leaded_window(name, centre, width, z0, z1, y, glow=1.0, color=(0.7, 0.78, 0.9)):
    """Tall leaded window on an X-running wall at y (room on -Y side): emissive glass + diamond lead lattice + stone mullion."""
    gm = L.mat_emission(name + "_glass", color, 2.5 * glow)
    g = box_mesh(name + "_g", [(centre, y + 0.01, (z0 + z1) / 2, width / 2, 0.005, (z1 - z0) / 2)], gm)
    g.visible_shadow = False
    bm = bmesh.new()
    s = 0.2
    h = z1 - z0
    k = -int(h / s) - 2
    while k * s < width + h:
        for sgn in (1, -1):
            # line x = x0 + sgn*(z - z0) + offset, clipped to the window rect
            pts = []
            for t in (0.0, 1.0):
                pass
            x_start = centre - width / 2 + k * s
            a = Vector((x_start, y - 0.005, z0))
            b = Vector((x_start + sgn * h, y - 0.005, z1))
            # clip to rect by sampling
            def clip(p, q):
                lo, hi = 0.0, 1.0
                for i, (mn, mx) in ((0, (centre - width / 2, centre + width / 2)), (2, (z0, z1))):
                    dp = q[i] - p[i]
                    for bound, sg in ((mn, 1), (mx, -1)):
                        if abs(dp) < 1e-9:
                            if (p[i] - bound) * sg < 0:
                                return None
                            continue
                        t = (bound - p[i]) / dp
                        if sg * dp > 0:
                            lo = max(lo, t)
                        else:
                            hi = min(hi, t)
                if hi <= lo:
                    return None
                return p.lerp(q, lo), p.lerp(q, hi)
            seg = clip(a, b)
            if seg:
                _beam(bm, seg[0], seg[1], 0.006, 0.004)
        k += 1
    lead = L.mesh_from_bm(name + "_lead", bm)
    lead.visible_shadow = False
    L.assign(lead, L.mat_principled(name + "_leadm", (0.02, 0.02, 0.02), rough=0.6))
    stone = L.mat_noise_surface(name + "_st", (0.3, 0.29, 0.26), (0.48, 0.46, 0.42), scale=4, bump=0.2, voronoi=False)
    box_mesh(name + "_mull", [(centre, y - 0.04, (z0 + z1) / 2, 0.05, 0.06, (z1 - z0) / 2),
                              (centre, y - 0.04, z0 + (z1 - z0) * 0.62, width / 2, 0.06, 0.05),
                              (centre - width / 2 - 0.06, y - 0.04, (z0 + z1) / 2, 0.07, 0.08, (z1 - z0) / 2 + 0.06),
                              (centre + width / 2 + 0.06, y - 0.04, (z0 + z1) / 2, 0.07, 0.08, (z1 - z0) / 2 + 0.06),
                              (centre, y - 0.04, z1 + 0.06, width / 2 + 0.12, 0.08, 0.06),
                              (centre, y - 0.06, z0 - 0.06, width / 2 + 0.14, 0.12, 0.06)], stone)
    return gm


def manor_staircase(day=False, window=1.0, return_flight=True, hall=True, floor_y0=-10.0):
    """Jacobean-style oak staircase in a panelled manor hall (see layout above). Returns dict with landing/key points."""
    oak = mat_oak("stair_oak")
    dark = mat_oak("stair_dark", 0.6)
    steps = []
    for i in range(STAIR_N):
        steps.append((0, STAIR_GO * i + STAIR_GO / 2, STAIR_RISE * i + STAIR_RISE / 2, 0.8, STAIR_GO / 2 + 0.02, STAIR_RISE / 2))
    # landing
    steps.append((0.9, LANDING_Y0 + 0.8, LANDING_Z / 2, 1.7, 0.8, LANDING_Z / 2))
    if return_flight:
        for i in range(10):
            y = LANDING_Y0 - STAIR_GO * i - STAIR_GO / 2
            z = LANDING_Z + STAIR_RISE * (i + 1)
            steps.append((1.8, y, z - STAIR_RISE / 2, 0.8, STAIR_GO / 2 + 0.02, STAIR_RISE / 2))
        # soffit under the return flight
        bm = bmesh.new()
        _beam(bm, Vector((1.8, LANDING_Y0, LANDING_Z - 0.15)), Vector((1.8, LANDING_Y0 - 3.0, LANDING_Z + 1.8 - 0.15)), 0.8, 0.08)
        so = L.mesh_from_bm("soffit", bm)
        L.assign(so, dark)
    box_mesh("steps", steps, oak, bevel=0.012)
    # nosings
    box_mesh("nosing", [(0, STAIR_GO * i + 0.01, STAIR_RISE * (i + 1) - 0.012, 0.81, 0.03, 0.014) for i in range(STAIR_N)], dark)
    # stringer (open side, x=+0.8)
    bm = bmesh.new()
    _beam(bm, Vector((0.84, -0.05, 0.05)), Vector((0.84, LANDING_Y0, LANDING_Z + 0.05)), 0.04, 0.2)
    # handrail + balusters along first flight
    rail_h = 0.9
    _beam(bm, Vector((0.84, 0.15, STAIR_RISE + rail_h)), Vector((0.84, LANDING_Y0, LANDING_Z + rail_h)), 0.05, 0.045)
    # landing balustrade along y = LANDING_Y0 from x 0.84 to 1.0 (gap) and return flight rail
    if return_flight:
        _beam(bm, Vector((0.96, LANDING_Y0 - 0.02, LANDING_Z + 0.18 + rail_h)), Vector((0.96, LANDING_Y0 - 3.0, LANDING_Z + 1.8 + rail_h)), 0.05, 0.045)
    rail = L.mesh_from_bm("handrail", bm)
    L.assign(rail, dark)
    bm = bmesh.new()
    y = 0.25
    while y < LANDING_Y0 - 0.05:
        zb = STAIR_RISE * (int(y / STAIR_GO) + 1)
        zt = STAIR_RISE + rail_h + (y - 0.15) * (STAIR_RISE / STAIR_GO)
        sc = (zt - zb) / 0.78
        _lathe(bm, Vector((0.84, y, zb)), [(dz * sc, r) for dz, r in BALUSTER])
        y += 0.25
    if return_flight:
        y = LANDING_Y0 - 0.2
        while y > LANDING_Y0 - 2.9:
            i = int((LANDING_Y0 - y) / STAIR_GO)
            zb = LANDING_Z + STAIR_RISE * (i + 1)
            zt = LANDING_Z + 0.18 + rail_h + (LANDING_Y0 - y) * (STAIR_RISE / STAIR_GO)
            sc = (zt - zb) / 0.78
            _lathe(bm, Vector((0.96, y, zb)), [(dz * sc, r) for dz, r in BALUSTER])
            y -= 0.25
    bal = L.mesh_from_bm("balusters", bm)
    bal.visible_shadow = False
    L.assign(bal, oak)
    L.smooth(bal)
    # newel posts with ball finials
    newels = [(0.84, 0.05, 0.0, 1.25), (0.9, LANDING_Y0, LANDING_Z - 0.4, 1.4)]
    for i, (x, y_, z0, hgt) in enumerate(newels):
        box_mesh(f"newel{i}", [(x, y_, z0 + hgt / 2, 0.1, 0.1, hgt / 2), (x, y_, z0 + hgt + 0.03, 0.13, 0.13, 0.03),
                               (x, y_, z0 + 0.15, 0.12, 0.12, 0.15)], dark, bevel=0.01)
        b = L.prim("sphere", loc=(x, y_, z0 + hgt + 0.17), segments=16, ring_count=10, radius=0.11)
        L.assign(b, oak)
        L.smooth(b)
    # walls
    panelled_wall("pw_west", "y", -1.0, floor_y0, 6.0, 0.0, 4.9, side=1, plaster_to=7.0)
    panelled_wall("pw_land", "x", 5.9, -1.0, -0.25, LANDING_Z, LANDING_Z + 2.3, side=-1)
    panelled_wall("pw_land2", "x", 5.9, 1.25, 2.75, LANDING_Z, LANDING_Z + 2.3, side=-1)
    panelled_wall("pw_east", "y", 2.75, -3.0, 6.0, 0.0, 4.9, side=-1, plaster_to=7.0)
    pl = L.mat_noise_surface("hall_pl", (0.34, 0.32, 0.28), (0.48, 0.45, 0.4), scale=2.5, bump=0.05, voronoi=False, rough=0.9)
    win_c, win_w, wz0, wz1 = 0.5, 1.4, LANDING_Z + 0.7, LANDING_Z + 4.1
    wall_with_openings("landwall", "x", 5.9, 3.8, 7.2, [(win_c - 0.05, win_w + 0.1, wz0, wz1)], mat=pl, outward=1)
    gm = leaded_window("lwin", win_c, win_w, wz0, wz1, 5.92, glow=window * (1.6 if day else 0.5))
    box_mesh("ceiling", [(0.9, (floor_y0 + 6) / 2, 7.2, 4.5, (6 - floor_y0) / 2, 0.05)], pl)
    if hall:
        flag = L.mat_noise_surface("flags", (0.12, 0.11, 0.1), (0.26, 0.24, 0.21), scale=1.4, bump=0.3, voronoi=True, rough=0.6)
        box_mesh("hallfloor", [(0.0, (floor_y0 + 6) / 2, -0.02, 6, (6 - floor_y0) / 2, 0.02)], flag)
        panelled_wall("pw_east2", "y", 2.75, floor_y0, -3.0, 0.0, 2.6, side=-1, plaster_to=7.0)
        rug = L.mat_noise_surface("rug", (0.12, 0.03, 0.02), (0.25, 0.08, 0.04), scale=30, bump=0.1, voronoi=False, rough=1.0)
        box_mesh("rug", [(0.0, -2.6, 0.005, 1.1, 1.6, 0.005)], rug)
    # window light into the stair well
    col = (0.7, 0.78, 0.92)
    a = L.area((win_c, 6.6, LANDING_Z + 2.4), (math.radians(90), 0, 0), energy=(900 if day else 520) * window, size=0.7, color=col, name="winlight")
    a.rotation_euler = (math.radians(-80), 0, 0)
    return {"landing": (0.0, LANDING_Y0 + 0.8, LANDING_Z), "win_mat": gm, "win_light": a}


def step_pos(i, x=0.0):
    """Top-centre of first-flight step i (0 = bottom step)."""
    return (x, STAIR_GO * i + STAIR_GO / 2, STAIR_RISE * (i + 1))


def brown_lady(name="lady", alpha=0.25, emit=0.4, height=1.7, color=(0.72, 0.7, 0.66)):
    """Translucent veiled figure (our own design): long gown (coat), conical veil + cap, no face. Returns parts with 'mat'."""
    p = figure(name, color=color, height=height, coat=True, dress=True)
    m = p["torso"].data.materials[0]
    pr = m.node_tree.nodes["Principled BSDF"]
    pr.inputs["Emission Color"].default_value = (0.85, 0.82, 0.76, 1)
    pr.inputs["Emission Strength"].default_value = emit
    pr.inputs["Alpha"].default_value = alpha
    try:
        m.surface_render_method = "BLENDED"
        m.use_transparency_overlap = False
    except Exception:
        pass
    s = height / 1.75
    veil = L.prim("cone", loc=(0, -0.02 * s, -0.05 * s), vertices=20, radius1=0.26 * s, radius2=0.07 * s, depth=0.55 * s)
    L.assign(veil, m)
    L.smooth(veil)
    veil.parent = p["neck"]
    cap = L.prim("sphere", loc=(0, -0.01 * s, 0.2 * s), segments=16, ring_count=8, radius=0.11 * s)
    L.assign(cap, m)
    cap.parent = p["neck"]
    p["coat"].scale = (p["coat"].scale[0] * 1.1, p["coat"].scale[1] * 1.1, p["coat"].scale[2] * 1.05)
    p["mat"] = m
    return p


def key_principled(mat, inp, pairs, interp="LINEAR"):
    pr = mat.node_tree.nodes["Principled BSDF"]
    for f, v in pairs:
        pr.inputs[inp].default_value = v
        pr.inputs[inp].keyframe_insert("default_value", frame=f)
    _interp_data(mat.node_tree, interp)


def flash_pop(cam_o, f, peak=4000, decay=10, size=2.0, offset=(0.4, 0.3, 0.2), color=(0.95, 0.97, 1.0), name="flash"):
    """Magnesium flash: area light near the camera, spike at frame f then decays over `decay` frames."""
    a = L.area((0, 0, 0), (0, 0, 0), energy=0, size=size, color=color, name=name)
    a.parent = cam_o
    a.location = offset
    key_energy(a, [(1, 0), (max(1, f - 1), 0), (f, peak), (f + 2, peak * 0.6), (f + decay, 0)], "LINEAR")
    a.data.volume_factor = 0.15
    return a


def plate_camera(loc, rot_z=0.0, name="pcam", cap_on=True):
    """Large-format plate camera on a wooden tripod (faces +Y local). Returns dict root, cap, lens_tip (world-ish local pos)."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    wood = L.mat_noise_surface(name + "_wood", (0.12, 0.06, 0.025), (0.3, 0.16, 0.07), scale=12, bump=0.15, voronoi=False, rough=0.4)
    blk = L.mat_principled(name + "_bell", (0.015, 0.012, 0.01), rough=0.7)
    brass = mat_brass(name + "_brass")
    bm = bmesh.new()
    top = Vector((0, 0, 1.25))
    for a in (90, 210, 330):
        r = math.radians(a)
        _beam(bm, top, Vector((0.55 * math.cos(r), 0.55 * math.sin(r), 0.0)), 0.02, 0.02)
    tp = L.mesh_from_bm(name + "_tripod", bm)
    L.assign(tp, wood)
    tp.parent = root
    box_mesh(name + "_head", [(0, 0, 1.27, 0.14, 0.14, 0.02), (0, -0.05, 1.42, 0.14, 0.04, 0.14), (0, 0.32, 1.42, 0.12, 0.03, 0.12),
                              (0, 0.12, 1.3, 0.1, 0.25, 0.015)], wood, parent=root, bevel=0.005)
    box_mesh(name + "_gg", [(0, -0.095, 1.42, 0.11, 0.003, 0.11)], L.mat_principled(name + "_ggm", (0.3, 0.32, 0.3), rough=0.3), parent=root)
    # bellows: pleated taper
    bel = []
    for k in range(8):
        t = k / 7
        y = -0.01 + 0.31 * t
        hs = 0.13 - 0.03 * t + (0.008 if k % 2 else 0)
        bel.append((0, y, 1.42, hs, 0.02, hs))
    box_mesh(name + "_bel", bel, blk, parent=root)
    lens = L.prim("cyl", loc=(0, 0.42, 1.42), vertices=24, radius=0.045, depth=0.16, rot=(math.pi / 2, 0, 0))
    L.assign(lens, brass)
    lens.parent = root
    ring = L.prim("torus", loc=(0, 0.36, 1.42), major_radius=0.05, minor_radius=0.008, rot=(math.pi / 2, 0, 0))
    L.assign(ring, brass)
    ring.parent = root
    glass = L.prim("cyl", loc=(0, 0.497, 1.42), vertices=24, radius=0.038, depth=0.004, rot=(math.pi / 2, 0, 0))
    L.assign(glass, L.mat_principled(name + "_lensg", (0.02, 0.03, 0.04), rough=0.02, metal=0.5))
    glass.parent = root
    cap = L.prim("cyl", loc=(0, 0.51, 1.42), vertices=24, radius=0.05, depth=0.03, rot=(math.pi / 2, 0, 0))
    L.assign(cap, L.mat_principled(name + "_capm", (0.02, 0.018, 0.016), rough=0.5))
    cap.parent = root
    cl = L.prim("cyl", loc=(0, 0, 0), vertices=12, radius=0.012, depth=0.012)
    L.assign(cl, brass)
    cl.parent = cap
    cl.location = (0, 0, 0.018)
    if not cap_on:
        cap.hide_render = True
    return {"root": root, "cap": cap, "lens": lens}


def flash_gun(parent=None, loc=(0, 0, 0), rot=(0, 0, 0), name="fgun"):
    """Hand flash gun: chrome dish reflector (cone, opens +Y local) + bulb + handle. Returns dict root, dish_mat, bulb_mat."""
    root = empty(name, loc, parent=parent)
    root.rotation_euler = rot
    chrome = L.mat_principled(name + "_chrome", (0.75, 0.75, 0.78), rough=0.12, metal=1.0)
    d = L.prim("cone", loc=(0, 0.05, 0), vertices=28, radius1=0.02, radius2=0.11, depth=0.1, rot=(-math.pi / 2, 0, 0),
               end_fill_type="NOTHING")
    L.assign(d, chrome)
    d.parent = root
    bulb_m = L.mat_emission(name + "_bulb", (1.0, 0.98, 0.95), 0.3)
    b = L.prim("sphere", loc=(0, 0.04, 0), segments=12, ring_count=8, radius=0.025)
    L.assign(b, bulb_m)
    b.parent = root
    h = L.prim("cyl", loc=(0, -0.03, -0.12), vertices=12, radius=0.02, depth=0.22)
    L.assign(h, L.mat_principled(name + "_h", (0.03, 0.03, 0.03), rough=0.4))
    h.parent = root
    return {"root": root, "bulb_mat": bulb_m, "dish": d}


def oak_corridor(length=16.0, w=2.4, h=3.0, door_every=4.0):
    """Upstairs panelled corridor along +Y from y=0: oak floorboards, panelling both sides, doors, beamed plaster ceiling."""
    fl = L.mat_noise_surface("boards", (0.04, 0.022, 0.01), (0.13, 0.075, 0.035), scale=5, bump=0.2, voronoi=False, rough=0.35)
    box_mesh("cfloor", [(0, length / 2, -0.02, w / 2 + 0.2, length / 2 + 1, 0.02)], fl)
    pl = L.mat_noise_surface("c_pl", (0.25, 0.23, 0.2), (0.38, 0.35, 0.3), scale=2.5, bump=0.05, voronoi=False, rough=0.9)
    box_mesh("cceil", [(0, length / 2, h + 0.02, w / 2 + 0.2, length / 2 + 1, 0.02)], pl)
    dark = mat_oak("c_beam", 0.6)
    box_mesh("cbeams", [(0, y, h - 0.1, w / 2, 0.1, 0.1) for y in range(1, int(length), 2)], dark)
    for sx in (-1, 1):
        panelled_wall(f"cw{sx}", "y", sx * w / 2, -1.0, length + 1, 0.0, 2.2, side=-sx, plaster_to=h)
    doors = []
    y = 2.5
    dm = mat_oak("c_door", 0.8)
    while y < length - 1:
        for sx in (-1, 1):
            box_mesh(f"door{sx}_{y}", [(sx * (w / 2 - 0.02), y, 1.05, 0.04, 0.45, 1.05)], dm, bevel=0.01)
            box_mesh(f"dfr{sx}_{y}", [(sx * (w / 2 - 0.03), y, 2.15, 0.05, 0.55, 0.06), (sx * (w / 2 - 0.03), y - 0.5, 1.05, 0.05, 0.05, 1.05),
                                      (sx * (w / 2 - 0.03), y + 0.5, 1.05, 0.05, 0.05, 1.05)], dark)
        y += door_every
    box_mesh("cend", [(0, length + 1, h / 2, w / 2 + 0.2, 0.05, h / 2)], pl)
    return {"length": length}


def darkroom_tray(loc=(0, 0, 0.9), img=None, n=100, reveal=(1, 80)):
    """Shallow developing tray with liquid surface (animated ripple) over a glass plate whose image fades in (reveal frames)."""
    root = empty("tray", loc)
    enamel = L.mat_principled("tray_m", (0.75, 0.73, 0.68), rough=0.35)
    W, D = 0.36, 0.28
    box_mesh("tray_b", [(0, 0, 0.003, W, D, 0.003), (W, 0, 0.03, 0.006, D, 0.03), (-W, 0, 0.03, 0.006, D, 0.03),
                        (0, D, 0.03, W, 0.006, 0.03), (0, -D, 0.03, W, 0.006, 0.03)], enamel, parent=root)
    # plate with image (fades from black to image)
    m, nn, l = _nodes("plate_m")
    p = nn["Principled BSDF"]
    mix = nn.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs[6].default_value = (0.02, 0.02, 0.02, 1)
    if img:
        t = nn.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(img)
        l.new(t.outputs["Color"], mix.inputs[7])
    else:
        mix.inputs[7].default_value = (0.4, 0.4, 0.4, 1)
    l.new(mix.outputs[2], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.3
    mix.inputs[0].default_value = 0.0
    mix.inputs[0].keyframe_insert("default_value", frame=reveal[0])
    mix.inputs[0].default_value = 1.0
    mix.inputs[0].keyframe_insert("default_value", frame=reveal[1])
    bm = bmesh.new()
    pw, ph = 0.2, 0.25
    vs = [bm.verts.new(v) for v in ((-pw, -ph, 0.01), (pw, -ph, 0.01), (pw, ph, 0.01), (-pw, ph, 0.01))]
    f = bm.faces.new(vs)
    uv = bm.loops.layers.uv.new()
    for lp, c in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        lp[uv].uv = c
    plate = L.mesh_from_bm("plate", bm)
    L.assign(plate, m)
    plate.parent = root
    plate.rotation_euler = (0, 0, math.radians(-4))
    # liquid: glossy, transparent-ish, animated bump
    lm, ln, ll = _nodes("liquid_m")
    lp_ = ln["Principled BSDF"]
    lp_.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
    lp_.inputs["Roughness"].default_value = 0.04
    lp_.inputs["Alpha"].default_value = 0.25
    try:
        lm.surface_render_method = "BLENDED"
    except Exception:
        pass
    tc = ln.new("ShaderNodeTexCoord")
    mp = ln.new("ShaderNodeMapping")
    ll.new(tc.outputs["Object"], mp.inputs["Vector"])
    wv = ln.new("ShaderNodeTexWave")
    wv.inputs["Scale"].default_value = 6
    wv.inputs["Distortion"].default_value = 3
    ll.new(mp.outputs[0], wv.inputs["Vector"])
    bp = ln.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.08
    ll.new(wv.outputs["Fac"], bp.inputs["Height"])
    ll.new(bp.outputs["Normal"], lp_.inputs["Normal"])
    mp.inputs["Location"].default_value = (0, 0, 0)
    mp.inputs["Location"].keyframe_insert("default_value", frame=1)
    mp.inputs["Location"].default_value = (0.15, 0.08, 0)
    mp.inputs["Location"].keyframe_insert("default_value", frame=n)
    liq = box_mesh("liquid", [(0, 0, 0.025, W - 0.006, D - 0.006, 0.0005)], lm, parent=root)
    return {"root": root, "plate": plate, "plate_mat": m}


def manor_exterior():
    """Large symmetrical 17th-century-style country house (generic): 34 m, 3 floors, central pediment, shaped end gables,
    tall sash windows, pale stone. Front at y=0 facing -Y."""
    stone = L.mat_noise_surface("mstone", (0.42, 0.4, 0.35), (0.62, 0.59, 0.52), scale=1.5, bump=0.08, voronoi=False, rough=0.85)
    roof = L.mat_noise_surface("mroof", (0.08, 0.08, 0.085), (0.18, 0.17, 0.17), scale=6, bump=0.2, voronoi=False, rough=0.7)
    trim = L.mat_principled("mtrim", (0.7, 0.68, 0.62), rough=0.6)
    dark = mat_glass_dark("mglass", (0.015, 0.018, 0.022))
    Wd, Dp, fh = 34.0, 14.0, 3.6
    Ht = fh * 3
    box_mesh("mbody", [(0, Dp / 2, Ht / 2, Wd / 2, Dp / 2, Ht / 2)], stone)
    for sx in (-1, 1):
        box_mesh(f"mwing{sx}", [(sx * (Wd / 2 - 3.5), -0.6, Ht / 2, 3.5, 0.6, Ht / 2)], stone)
    _hip_roof("mroof", (0, Dp / 2, Ht), Wd + 0.6, Dp + 0.6, 4.5, roof)
    bm = bmesh.new()
    for cx, w, hgt in ((0.0, 9.0, 4.0),):
        v = [bm.verts.new(p) for p in ((cx - w / 2, -0.25, Ht), (cx + w / 2, -0.25, Ht), (cx, -0.25, Ht + hgt),
                                        (cx - w / 2, 1.5, Ht), (cx + w / 2, 1.5, Ht), (cx, 1.5, Ht + hgt))]
        for f in ((0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)):
            bm.faces.new([v[i] for i in f])
    ped = L.mesh_from_bm("pediment", bm)
    L.assign(ped, stone)
    # shaped (Dutch) end gables: stepped blocks + semicircular cap on each wing
    for sx in (-1, 1):
        cx = sx * (Wd / 2 - 3.5)
        box_mesh(f"gable{sx}", [(cx, -1.0, Ht + 0.8, 3.2, 0.25, 0.8), (cx, -1.0, Ht + 2.2, 2.2, 0.25, 0.6), (cx, -1.0, Ht + 3.3, 1.2, 0.25, 0.5)],
                 stone)
        c = L.prim("cyl", loc=(cx, -1.0, Ht + 3.8), vertices=24, radius=1.2, depth=0.5, rot=(math.pi / 2, 0, 0))
        L.assign(c, stone)
        _hip_roof(f"wroof{sx}", (cx, 0.5, Ht), 7.2, 3.0, 2.5, roof)
    box_mesh("mcornice", [(0, -0.25, Ht - 0.1, Wd / 2 - 7, 0.25, 0.14), (0, -0.2, fh, Wd / 2 - 7, 0.15, 0.08)], trim)
    panes, frames = [], []
    for fl_i in range(3):
        for c_i in range(13):
            x = -Wd / 2 + 1.6 + c_i * (Wd - 3.2) / 12
            yf = -1.22 if abs(x) > Wd / 2 - 7 else -0.02
            if fl_i == 0 and abs(x) < 1.5:
                continue
            z0 = fl_i * fh + 0.9
            panes.append((x, yf, z0 + 1.0, 0.55, 0.03, 1.0))
            frames += [(x, yf - 0.03, z0 + 1.0, 0.025, 0.02, 1.0), (x, yf - 0.03, z0 + 1.0, 0.55, 0.02, 0.025),
                       (x, yf - 0.04, z0 - 0.05, 0.68, 0.06, 0.06), (x, yf - 0.04, z0 + 2.05, 0.68, 0.06, 0.08)]
    box_mesh("mpanes", panes, dark)
    box_mesh("mframes", frames, trim)
    box_mesh("mdoor", [(0, -0.03, 1.5, 1.0, 0.05, 1.5), (0, -0.3, 3.2, 1.6, 0.3, 0.2)], mat_oak("mdoorm", 0.7))
    box_mesh("mporch", [(sx * 1.4, -0.4, 1.6, 0.18, 0.18, 1.6) for sx in (-1, 1)], trim)
    ground_box("mlawn", -120, 120, -120, 120, -0.02, L.mat_noise_surface("mgrass", (0.06, 0.08, 0.04), (0.13, 0.16, 0.08), scale=2,
                                                                          bump=0.2, voronoi=False, rough=1))
    ground_box("mgravel", -22, 22, -14, -0.5, 0.0, mat_gravel("mgrav"))
    bare_forest("mtrees", [(-70, -26, -30, 40), (26, 70, -30, 40), (-60, 60, 30, 70)], count=45, seed=13, height=(10, 18))


def crisp_shadows(area_max=0.3, radius_max=0.05):
    """Shrink soft-shadow sizes on all lights: EEVEE soft shadows speckle badly at the pipeline's 2 TAA samples."""
    for o in bpy.data.objects:
        if o.type != "LIGHT":
            continue
        d = o.data
        if d.type == "AREA":
            d.size = min(d.size, area_max)
        elif d.type != "SUN":
            d.shadow_soft_size = min(d.shadow_soft_size, radius_max)
        if o.parent is not None and o.parent.type == "CAMERA":
            d.use_shadow = False      # camera-mounted fills/flashes: no shadow acne on grazing walls

# ============================================================================ WAVERLY HILLS sets (HAUNT-05)
# Body chute: built in a local frame (tunnel runs along +Y local, floor z=0) under a root empty tilted about X so +Y
# goes DOWNHILL. Parent anything (camera, gurney, figures, lights) to the root and work in local coords.
# Sanatorium: front facade faces -Y at y=0, hill falls away toward -Y. Sun-porch corridor: along Y centred on y=0,
# porch openings in the +X wall, doors in the -X wall, end doorway at +Y.

def mat_streaked(name, c1, c2, stain=0.45, scale=3.0, zstretch=0.3, rough=0.85, bump=0.25, stain_scale=2.0):
    """Two-tone noise surface darkened by vertical drip streaks (noise stretched along Z, object coords)."""
    m, n, l = _nodes(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 6
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    base = _ramp(n, [(0.32, c1), (0.68, c2)])
    l.new(nz.outputs["Fac"], base.inputs[0])
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 1.0, zstretch)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz2 = n.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = stain_scale
    nz2.inputs["Detail"].default_value = 4
    l.new(mp.outputs[0], nz2.inputs["Vector"])
    sr = _ramp(n, [(0.42, (1, 1, 1)), (0.62, (stain, stain * 0.95, stain * 0.85))])
    l.new(nz2.outputs["Fac"], sr.inputs[0])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 1.0
    l.new(base.outputs[0], mix.inputs[6])
    l.new(sr.outputs[0], mix.inputs[7])
    l.new(mix.outputs[2], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    l.new(nz.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def chute_tunnel(length=60.0, w=2.4, h=2.6, slope_deg=12.0, lamp_every=6.0, lamp_y0=2.0, lamp_energy=40.0, dead=(),
                 door_glow=0.6, fog=0.02, name="chute", steps_from=-2.5):
    """Sloped concrete body-chute tunnel (Waverly-style, stylised). Returns dict root, lamps [(light, mat)], s, c, wall_h.
    Local frame: x across (-w/2 steps side .. +w/2 rails side), y downhill from the top landing (y=0), z up from floor."""
    root = empty(name)
    a = math.radians(slope_deg)
    root.rotation_euler = (-a, 0, 0)
    s, c = math.sin(a), math.cos(a)
    conc = mat_streaked(name + "_conc", (0.13, 0.125, 0.11), (0.33, 0.32, 0.29), stain=0.38, scale=2.5, zstretch=0.25)
    fl = mat_streaked(name + "_floor", (0.09, 0.085, 0.075), (0.24, 0.23, 0.2), stain=0.55, scale=4.0, zstretch=1.0, rough=0.7)
    hw = w / 2
    rise = 0.35
    wall_h = h - rise
    y0, y1 = -3.0, length
    ly = y1 - y0
    cy = (y0 + y1) / 2
    box_mesh(name + "_floor", [(0, cy, -0.1, hw + 0.2, ly / 2, 0.1)], fl, parent=root)
    box_mesh(name + "_walls", [(-hw - 0.1, cy, wall_h / 2, 0.1, ly / 2, wall_h / 2 + 0.05),
                                (hw + 0.1, cy, wall_h / 2, 0.1, ly / 2, wall_h / 2 + 0.05)], conc, parent=root)
    # shallow arched ceiling (single surface + outer lid so nothing leaks)
    bm = bmesh.new()
    K = 10
    rows = []
    for yy in (y0, y1):
        rows.append([bm.verts.new((-hw - 0.01 + (w + 0.02) * i / K, yy, wall_h + rise * (1 - ((-1 + 2 * i / K) ** 2)))) for i in range(K + 1)])
    for i in range(K):
        bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    arch = L.mesh_from_bm(name + "_arch", bm)
    L.assign(arch, conc)
    arch.parent = root
    box_mesh(name + "_lid", [(0, cy, h + 0.2, hw + 0.2, ly / 2, 0.1)], conc, parent=root)
    # end walls: bottom closed; top has a doorway onto the landing
    box_mesh(name + "_bottom", [(0, y1 + 0.1, h / 2, hw + 0.2, 0.1, h / 2 + 0.2)], conc, parent=root)
    dw, dh = 1.1, 2.1
    box_mesh(name + "_top", [(-(hw + dw / 2) / 2 - 0.05, y0 - 0.1, h / 2, (hw - dw / 2) / 2 + 0.15, 0.1, h / 2 + 0.2),
                             ((hw + dw / 2) / 2 + 0.05, y0 - 0.1, h / 2, (hw - dw / 2) / 2 + 0.15, 0.1, h / 2 + 0.2),
                             (0, y0 - 0.1, (dh + h) / 2 + 0.1, dw / 2, 0.1, (h - dh) / 2 + 0.1)], conc, parent=root)
    dm = L.mat_emission(name + "_doorglow", (0.45, 0.6, 1.0), door_glow)
    box_mesh(name + "_doorlight", [(0, y0 - 0.6, dh / 2, dw / 2 + 0.05, 0.02, dh / 2 + 0.05)], dm, parent=root)
    # steps (left half): horizontal treads, sawtooth on the sloped floor
    tr = 0.42
    hgt = tr * s / c
    bm = bmesh.new()
    yy = steps_from
    while yy < y1 - 0.5:
        p0 = Vector((0, yy, 0.0))
        p1 = p0 + Vector((0, c, s)) * tr
        p2 = p1 + Vector((0, s, -c)) * hgt
        prof = [p0, p1, p2]
        va = [bm.verts.new((-hw, q.y, q.z)) for q in prof]
        vb = [bm.verts.new((-0.04, q.y, q.z)) for q in prof]
        bm.faces.new((va[0], va[1], va[2]))
        bm.faces.new((vb[2], vb[1], vb[0]))
        for i in range(3):
            j = (i + 1) % 3
            bm.faces.new((va[i], vb[i], vb[j], va[j]))
        yy = p2.y
    st = L.mesh_from_bm(name + "_steps", bm)
    L.assign(st, mat_streaked(name + "_stepm", (0.16, 0.155, 0.14), (0.36, 0.35, 0.32), stain=0.6, scale=5.0, zstretch=1.0))
    st.parent = root
    steel = L.mat_principled(name + "_rail", (0.32, 0.3, 0.28), rough=0.35, metal=0.9)
    box_mesh(name + "_rails", [(0.38, cy + 1.5, 0.025, 0.018, ly / 2 - 1.5, 0.025), (0.92, cy + 1.5, 0.025, 0.018, ly / 2 - 1.5, 0.025),
                               (0.65, cy + 1.5, 0.012, 0.008, ly / 2 - 1.5, 0.008)], steel, parent=root)
    box_mesh(name + "_kerb", [(-0.02, cy, 0.05, 0.03, ly / 2, 0.05)], conc, parent=root)
    wet = L.mat_principled(name + "_wet", (0.012, 0.012, 0.012), rough=0.12)
    box_mesh(name + "_gutter", [(hw - 0.07, cy, 0.003, 0.06, ly / 2, 0.003)], wet, parent=root)
    # cage lamps
    lamps = []
    glassoff = L.mat_principled(name + "_bulboff", (0.05, 0.05, 0.045), rough=0.2)
    wire = L.mat_principled(name + "_wire", (0.04, 0.04, 0.04), rough=0.5, metal=0.6)
    i = 0
    yy = lamp_y0
    while yy < y1 - 0.5:
        z = h - 0.32
        on = i not in dead
        bm_ = L.mat_emission(f"{name}_bulb{i}", (1.0, 0.72, 0.4), 22.0) if on else glassoff
        b = L.prim("sphere", loc=(0, yy, z), segments=12, ring_count=8, radius=0.05)
        L.assign(b, bm_)
        b.parent = root
        cg = L.prim("cyl", loc=(0, yy, z), vertices=8, radius=0.075, depth=0.14)
        cg.modifiers.new("w", "WIREFRAME").thickness = 0.006
        L.assign(cg, wire)
        cg.parent = root
        cd = L.prim("cyl", loc=(0, yy, z + 0.15), vertices=6, radius=0.008, depth=0.2)
        L.assign(cd, wire)
        cd.parent = root
        lt = None
        if on:
            lt = L.point((0, yy, z - 0.08), energy=lamp_energy, color=(1.0, 0.7, 0.38), radius=0.03, name=f"{name}_lamp{i}")
            lt.parent = root
        lamps.append((lt, bm_ if on else None, yy))
        yy += lamp_every
        i += 1
    fg = None
    if fog:
        fg = room_fog((0, cy, h / 2), (w, ly, h), density=fog, color=(0.75, 0.72, 0.66), anis=0.45, name=name + "_fog")
        fg.parent = root
    return {"root": root, "lamps": lamps, "s": s, "c": c, "wall_h": wall_h, "h": h, "w": w, "y0": y0, "y1": y1}


def chute_world(t, p):
    """Local tunnel point -> world (for aim targets of unparented objects)."""
    return tuple(t["root"].matrix_world @ Vector(p))


def gurney(name="gurney", parent=None, sheet=True):
    """Empty steel hospital gurney (faces +Y local), top at 0.8 m, folded sheet slab, NO body. Returns root."""
    root = empty(name)
    if parent:
        root.parent = parent
    steel = L.mat_principled(name + "_steel", (0.55, 0.55, 0.56), rough=0.3, metal=0.9)
    pad = L.mat_principled(name + "_pad", (0.06, 0.075, 0.075), rough=0.45)
    bx = [(sx * 0.29, 0, 0.78, 0.016, 0.95, 0.016) for sx in (-1, 1)] + [(0, sy * 0.94, 0.78, 0.3, 0.016, 0.016) for sy in (-1, 1)]
    bx += [(sx * 0.27, 0, 0.3, 0.012, 0.85, 0.012) for sx in (-1, 1)] + [(0, sy * 0.84, 0.3, 0.27, 0.012, 0.012) for sy in (-1, 1)]
    bx += [(sx * 0.27, sy * 0.84, 0.44, 0.015, 0.015, 0.34) for sx in (-1, 1) for sy in (-1, 1)]
    bx += [(sx * 0.27, -0.99, 0.88, 0.012, 0.012, 0.1) for sx in (-1, 1)] + [(0, -0.99, 0.98, 0.27, 0.012, 0.012)]
    box_mesh(name + "_frame", bx, steel, parent=root)
    box_mesh(name + "_pad", [(0, 0, 0.82, 0.28, 0.92, 0.025)], pad, parent=root, bevel=0.012)
    if sheet:
        sm = L.mat_principled(name + "_sheet", (0.78, 0.77, 0.72), rough=0.9, emit=(0.8, 0.8, 0.75), emit_strength=0.02)
        box_mesh(name + "_sheet", [(0, 0.5, 0.865, 0.27, 0.21, 0.022), (0, 0.5, 0.893, 0.26, 0.2, 0.008)], sm, parent=root, bevel=0.008)
    dark = L.mat_principled(name + "_wheel", (0.02, 0.02, 0.02), rough=0.6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            wh = L.prim("cyl", loc=(sx * 0.27, sy * 0.84, 0.05), vertices=12, radius=0.05, depth=0.03, rot=(0, math.pi / 2, 0))
            L.assign(wh, dark)
            wh.parent = root
    return root


def roll_along(obj, keys, axis_rot=None, radius=None):
    """keys [(frame, (x,y,z))] linear-ish location keys; optional rolling rotation about X by distance/radius."""
    dist = 0.0
    prev = None
    for f, p in keys:
        obj.location = p
        obj.keyframe_insert("location", frame=f)
        if radius:
            if prev is not None:
                dist += (Vector(p) - Vector(prev)).length * (1 if p[1] >= prev[1] else -1)
            obj.rotation_euler = (dist / radius, 0, 0) if axis_rot is None else axis_rot(dist / radius)
            obj.keyframe_insert("rotation_euler", frame=f)
        prev = p


def bare_forest_z(name, regions, zfunc, count=40, seed=3, height=(6.0, 12.0), mat=None, depth=3, avoid=None):
    """bare_forest on uneven ground: each trunk base sits at zfunc(x, y). avoid(x, y) -> True skips the spot."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    tot = sum((r[1] - r[0]) * (r[3] - r[2]) for r in regions)

    def branch(base, d, length, rad, lvl):
        end = base + d * length
        mid = (base + end) / 2 + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * length * 0.06
        _tube(bm, [base, mid, end], rad, rad * 0.6, sides=5 if lvl > 1 else 4)
        if lvl > 0:
            for _ in range(rnd.randint(2, 3)):
                nd = (d + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.05, 0.6)))).normalized()
                if nd.z < 0.1:
                    nd.z = 0.1
                    nd.normalize()
                branch(end - d * length * rnd.uniform(0, 0.25), nd, length * rnd.uniform(0.5, 0.72), rad * 0.55, lvl - 1)

    for reg in regions:
        k = max(1, int(round(count * (reg[1] - reg[0]) * (reg[3] - reg[2]) / tot)))
        for i in range(k):
            x, y = rnd.uniform(reg[0], reg[1]), rnd.uniform(reg[2], reg[3])
            if avoid and avoid(x, y):
                continue
            h = rnd.uniform(*height)
            lean = Vector((rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08), 1)).normalized()
            branch(Vector((x, y, zfunc(x, y) - 0.3)), lean, h * 0.42, h * 0.026, depth)
    o = L.mesh_from_bm(name, bm)
    L.assign(o, mat or L.mat_noise_surface(name + "_bark", (0.012, 0.012, 0.012), (0.05, 0.045, 0.04), scale=6, bump=0.3, voronoi=False))
    return o


def hill_z(x, y, top=-8.0, slope_deg=15.0, floor_y=-110.0):
    """Ground height: flat plateau for y > top, falling at slope_deg toward -Y (flattening below floor_y), gentle noise."""
    t = math.tan(math.radians(slope_deg))
    d = min(max(0.0, top - y), top - floor_y)
    return -d * t + 0.6 * noise.noise(Vector((x * 0.04, y * 0.04, 0.5)))


def hill_ground(name="hill", x0=-180, x1=180, y0=-160, y1=140, step=4.0, mat=None, **kw):
    bm = bmesh.new()
    nx, ny = int((x1 - x0) / step) + 1, int((y1 - y0) / step) + 1
    vs = [[bm.verts.new((x0 + i * step, y0 + j * step, hill_z(x0 + i * step, y0 + j * step, **kw))) for i in range(nx)] for j in range(ny)]
    for j in range(ny - 1):
        for i in range(nx - 1):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    o = L.mesh_from_bm(name, bm)
    L.smooth(o)
    L.assign(o, mat or L.mat_noise_surface(name + "_m", (0.025, 0.025, 0.02), (0.09, 0.08, 0.06), scale=0.4, bump=0.3, voronoi=False, rough=1.0))
    return o


def _porch_block(name, x0, x1, floors, fh, depth, bays, parent, stucco, dark, lit=None, y_front=0.0, porch=1.9):
    """Flat-roofed block whose every storey is a continuous band of open sun-porch bays (front at y_front, facing -Y).
    lit: {(floor, bay): material} emissive back panels. Local coords of `parent`."""
    W = x1 - x0
    cx = (x0 + x1) / 2
    yf = y_front
    bx = []
    Ht = floors * fh
    for f in range(floors):
        z0 = f * fh
        bx.append((cx, yf + 0.15, z0 + 0.5, W / 2, 0.15, 0.5))                 # balustrade / spandrel
        bx.append((cx, yf + 0.15, z0 + fh - 0.22, W / 2, 0.15, 0.22))          # lintel band
        bx.append((cx, yf + porch / 2, z0 + 0.06, W / 2, porch / 2, 0.08))      # porch floor slab
        bx.append((cx, yf - 0.05, z0 + 1.02, W / 2 + 0.05, 0.08, 0.04))         # sill line (shadow line)
    for i in range(bays + 1):
        x = x0 + W * i / bays
        bx.append((x, yf + 0.15, Ht / 2, 0.24 if 0 < i < bays else 0.45, 0.17, Ht / 2))
    bx.append((cx, yf + depth / 2, Ht + 0.45, W / 2 + 0.15, depth / 2 + 0.15, 0.45))   # roof + parapet
    bx.append((cx, yf + porch + (depth - porch) / 2 + 0.02, Ht / 2, W / 2, (depth - porch) / 2, Ht / 2))  # body
    box_mesh(name, bx, stucco, parent=parent)
    back = []
    lit = lit or {}
    for f in range(floors):
        for i in range(bays):
            if (f, i) in lit:
                continue
            bw = W / bays
            back.append((x0 + bw * (i + 0.5), yf + porch - 0.02, f * fh + fh / 2 + 0.3, bw / 2 - 0.2, 0.01, fh / 2 - 0.25))
    box_mesh(name + "_recess", back, dark, parent=parent)
    lights = {}
    for (f, i), m in lit.items():
        bw = W / bays
        x = x0 + bw * (i + 0.5)
        box_mesh(f"{name}_lit{f}_{i}", [(x, yf + porch - 0.02, f * fh + fh / 2 + 0.3, bw / 2 - 0.2, 0.01, fh / 2 - 0.25)], m, parent=parent)
        lights[(f, i)] = (x, yf + porch - 0.5, f * fh + fh / 2 + 0.3)
    return lights


def sanatorium(lit=None, floors=5, fh=3.6, wings=True, hill=True, trees=True, seed=4, tree_count=70, near_trees=None):
    """Stylised five-storey sun-porch sanatorium on a hilltop (NOT a likeness): 80 m central range of 30 bays per floor,
    central entrance block one storey taller, two short wings angled back 30 degrees. lit: {(block, floor, bay): (mat, energy)}
    with block in ('C', 'E', 'L', 'R'). Returns dict with light objects keyed like lit."""
    root = empty("sanatorium")
    stucco = mat_streaked("stucco", (0.34, 0.33, 0.3), (0.56, 0.55, 0.51), stain=0.42, scale=0.6, zstretch=0.12, rough=0.9,
                          bump=0.08, stain_scale=1.5)
    dark = L.mat_principled("porchdark", (0.004, 0.0045, 0.006), rough=0.95)
    lit = lit or {}
    out = {}

    def sub(block):
        return {(f, b): v[0] for (bk, f, b), v in lit.items() if bk == block}

    def add_lights(block, pos, par):
        for (f, b), p in pos.items():
            e = lit[(block, f, b)][1]
            if e > 0:
                lt = L.point(p, energy=e, color=(1.0, 0.72, 0.42), radius=0.3, name=f"bay_{block}{f}_{b}")
                lt.parent = par
                out[(block, f, b)] = lt
    add_lights("C", _porch_block("range", -40, 40, floors, fh, 14, 30, root, stucco, dark, sub("C")), root)
    add_lights("E", _porch_block("entrance", -7.5, 7.5, floors + 1, fh, 16, 5, root, stucco, dark, sub("E"), y_front=-2.6), root)
    if wings:
        for sx, nm in ((-1, "L"), (1, "R")):
            pv = empty("wing" + nm, (sx * 40.0, 0, 0), parent=root)
            pv.rotation_euler = (0, 0, sx * math.radians(30))
            x0, x1 = (-22.0, 0.0) if sx < 0 else (0.0, 22.0)
            add_lights(nm, _porch_block("wing" + nm, x0, x1, floors, fh, 12, 8, pv, stucco, dark, sub(nm)), pv)
    # entrance steps + door
    box_mesh("entry_steps", [(0, -3.4 - k * 0.35, 0.15 - k * 0.15, 3.0, 0.2, 0.15 + 0.0) for k in range(4)], stucco)
    if hill:
        hill_ground("hill", mat=L.mat_noise_surface("deadgrass", (0.03, 0.028, 0.022), (0.1, 0.09, 0.065), scale=0.35, bump=0.25,
                                                     voronoi=False, rough=1.0))
        box_mesh("drive", [(0, -9.0, 0.02, 3.0, 2.0, 0.03)], L.mat_principled("drive_m", (0.05, 0.05, 0.05), rough=0.8))
    if trees:
        bldg = lambda x, y: (-62 < x < 62 and -10 < y < 30) or (abs(x) < 8 and y < -6)
        bare_forest_z("hilltrees", [(-140, -45, -120, 60), (45, 140, -120, 60), (-45, 45, -100, -20), (-90, 90, 30, 90)],
                      hill_z, count=tree_count, seed=seed, height=(9, 16), avoid=bldg)
        if near_trees:
            bare_forest_z("neartrees", near_trees[0], hill_z, count=near_trees[1], seed=seed + 7, height=(8, 13))
    return {"root": root, "lights": out, "stucco": stucco}


def mat_peeling(name="peel", c1=(0.07, 0.075, 0.065), c2=(0.42, 0.45, 0.4), scale=3.0):
    """Institutional green-grey paint flaking off to dark plaster: voronoi-cell flakes over a noise base."""
    m, n, l = _nodes(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 8
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    vr = n.new("ShaderNodeTexVoronoi")
    vr.inputs["Scale"].default_value = scale * 6
    l.new(tc.outputs["Object"], vr.inputs["Vector"])
    v = _math(n, l, "ADD", _math(n, l, "MULTIPLY", nz.outputs["Fac"], 1.0), _math(n, l, "MULTIPLY", vr.outputs["Distance"], 0.35))
    r = _ramp(n, [(0.55, c2), (0.6, (c2[0] * 0.6, c2[1] * 0.6, c2[2] * 0.6)), (0.64, c1), (1.0, c1)], interp="LINEAR")
    l.new(v, r.inputs[0])
    l.new(r.outputs[0], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.9
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.35
    l.new(v, bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def porch_corridor(length=30.0, w=3.0, h=3.0, bay=2.0, door_every=4.0, ajar=(1, 4), seed=2, end_room=True,
                   moon_dir=(-0.75, 0.35, -0.55), moon=4.0, end_glow=1.0, debris=True, fog=0.015, open_w=None):
    """4th-floor sun-porch corridor along Y (y from -length/2 to +length/2): +X wall is an unglazed band of porch
    openings (sill 0.9, head 2.6) letting moonlight stripes across the floor; -X wall doors every door_every, some ajar;
    peeling paint; end doorway at +Y onto a moonlit room. Returns dict with moon (sun), openings [y centres], hy."""
    hy = length / 2
    paint = mat_peeling("cpaint")
    flm = L.mat_noise_surface("cfloor", (0.05, 0.048, 0.042), (0.17, 0.16, 0.14), scale=3, bump=0.15, voronoi=True, rough=0.6)
    ceil = mat_peeling("cceil", (0.05, 0.05, 0.045), (0.33, 0.34, 0.31), scale=2.0)
    box_mesh("cor_floor", [(0, 0, -0.05, w / 2 + 0.3, hy + 6, 0.05)], flm)
    box_mesh("cor_ceil", [(0, 0, h + 0.05, w / 2 + 0.3, hy + 6, 0.05)], ceil)
    doors_y = []
    y = -hy + 2.0
    while y < hy - 1.0:
        doors_y.append(y)
        y += door_every
    wall_with_openings("cor_left", "y", -w / 2, length, h, [(dy, 0.95, 0, 2.1) for dy in doors_y], t=0.15, mat=paint, outward=-1)
    dm = L.mat_noise_surface("cdoor", (0.06, 0.055, 0.045), (0.2, 0.18, 0.14), scale=6, bump=0.2, voronoi=False, rough=0.8)
    rnd = random.Random(seed)
    for i, dy in enumerate(doors_y):
        ang = -math.radians(rnd.uniform(25, 70)) if i in ajar else 0.0
        door_slab(f"cdoor{i}", (-w / 2 - 0.07, dy - 0.47, 0), width=0.94, height=2.08, angle=ang, axis="y", mat=dm, panels=True)
    # behind the doors: black rooms (a box so nothing leaks)
    box_mesh("cor_rooms", [(-w / 2 - 2.2, 0, h / 2, 2.0, hy, h / 2 + 0.1)], L.mat_principled("roomblack", (0.01, 0.01, 0.01), rough=1.0))
    openings = []
    y = -hy + bay / 2
    while y < hy:
        openings.append(y)
        y += bay
    wall_with_openings("cor_right", "y", w / 2, length, h, [(oy, open_w or bay - 0.5, 0.9, 2.6) for oy in openings], t=0.25, mat=paint, outward=1)
    # far end wall + doorway, start wall
    wall_with_openings("cor_end", "x", hy, w + 0.6, h, [(0, 1.1, 0, 2.2)], t=0.15, mat=paint, outward=1)
    box_mesh("cor_start", [(0, -hy - 0.1, h / 2, w / 2 + 0.3, 0.1, h / 2)], paint)
    res = {"hy": hy, "openings": openings, "doors": doors_y, "w": w, "h": h}
    if end_room:
        rm = mat_peeling("rpaint", (0.06, 0.065, 0.06), (0.4, 0.42, 0.38), scale=2.5)
        box_mesh("endroom", [(0, hy + 4.15, h / 2, 3.0, 0.1, h / 2), (-3.0, hy + 2.1, h / 2, 0.1, 2.0, h / 2),
                             (3.0, hy + 2.1, h / 2, 0.1, 2.0, h / 2)], rm)
        a = L.area((1.8, hy + 1.2, 2.4), (0, 0, 0), energy=60 * end_glow, size=1.0, color=(0.55, 0.65, 1.0), name="endglow")
        aim(a, (1.8, hy + 1.2, 2.4), (-0.5, hy + 4.0, 1.0))
        res["endglow"] = a
    # outside: a few far tree silhouettes against a faint sky so openings are not flat black
    sky = L.mat_emission("porchsky", (0.05, 0.065, 0.1), 1.0)
    box_mesh("porch_sky", [(w / 2 + 40, 0, 10, 0.1, hy + 40, 25)], sky)
    bare_forest("porch_trees", [(w / 2 + 12, w / 2 + 30, -hy - 10, hy + 10)], count=14, seed=seed + 3, height=(10, 18))
    mv = Vector(moon_dir).normalized()
    sn = L.sun(rot=(0, 0, 0), energy=moon, color=(0.62, 0.72, 1.0), angle=0.5, name="moon")
    sn.rotation_euler = mv.to_track_quat("-Z", "Y").to_euler()
    res["moon"] = sn
    res["moon_dir"] = mv
    if debris:
        bx = []
        for i in range(26):
            x = rnd.uniform(-w / 2 + 0.15, w / 2 - 0.2)
            yy = rnd.uniform(-hy + 1, hy - 1)
            if abs(x) < 0.45:
                continue
            s_ = rnd.uniform(0.03, 0.14)
            bx.append((x, yy, s_ * 0.4, s_ * rnd.uniform(0.8, 2.5), s_, s_ * 0.4, rnd.uniform(0, 3)))
        for i in range(6):
            x = rnd.choice((-1, 1)) * rnd.uniform(0.7, w / 2 - 0.2)
            bx.append((x, rnd.uniform(-hy + 1, hy - 1), 0.02, 0.05, rnd.uniform(0.5, 1.1), 0.015, rnd.uniform(-0.4, 0.4)))
        box_mesh("debris", bx, L.mat_noise_surface("debris_m", (0.05, 0.045, 0.04), (0.25, 0.23, 0.2), scale=8, bump=0.3, voronoi=False))
    if fog:
        res["fog"] = room_fog((0, 0, h / 2), (w, length, h), density=fog, color=(0.7, 0.75, 0.85), anis=0.55, name="corfog")
    return res


def moon_floor_point(cor, oy, x=0.0, z_open=None):
    """Floor point at lateral x lit through the porch opening centred at oy (approx centre of the stripe)."""
    d = cor["moon_dir"]
    wx = cor["w"] / 2
    t = (x - wx) / d.x                     # param along the ray from the wall plane to x
    zw = -d.z * t                          # height at which that ray crossed the wall plane
    yw = oy
    return (x, yw + d.y * t, 0.0), zw


def rubber_ball(name="ball", r=0.035, loc=(0, 0, 0.035)):
    m = L.mat_noise_surface(name + "_m", (0.3, 0.02, 0.015), (0.55, 0.06, 0.04), scale=40, bump=0.1, voronoi=False, rough=0.6)
    b = L.prim("sphere", loc=loc, segments=24, ring_count=12, radius=r, name=name)
    L.assign(b, m)
    L.smooth(b)
    # a pale scuff stripe so the roll reads
    s = L.prim("torus", loc=(0, 0, 0), major_radius=r * 0.98, minor_radius=r * 0.12, rot=(0, math.pi / 2, 0))
    L.assign(s, L.mat_principled(name + "_scuff", (0.45, 0.35, 0.3), rough=0.8))
    s.parent = b
    return b


def ticket_icon(name, loc, w=0.9, h=0.42, parent=None, col=(0.55, 0.06, 0.05)):
    """Flat admission-ticket icon (notched ends, perforation) facing -Y, in the board's XZ plane."""
    root = empty(name, loc, parent=parent)
    m = L.mat_principled(name + "_m", col, rough=0.6)
    box_mesh(name + "_b", [(0, 0, 0, w / 2, 0.002, h / 2)], m, parent=root)
    paper = L.mat_principled(name + "_p", (0.86, 0.83, 0.72), rough=0.9)
    for sx in (-1, 1):
        c = L.prim("cyl", loc=(sx * w / 2, -0.003, 0), vertices=16, radius=h * 0.18, depth=0.003, rot=(math.pi / 2, 0, 0))
        L.assign(c, paper)
        c.parent = root
    box_mesh(name + "_perf", [(w * 0.25, -0.003, -h / 2 + (k + 0.5) * h / 7, 0.008, 0.002, h / 28) for k in range(7)], paper, parent=root)
    return root
