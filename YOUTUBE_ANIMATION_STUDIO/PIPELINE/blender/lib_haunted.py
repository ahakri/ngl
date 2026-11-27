"""Haunted-category builders (HAUNT-01 Enfield, HAUNT-02 Stanley Hotel).

Import from shots.py:
    import importlib, sys; sys.path.insert(0, <PIPELINE/blender>); import lib_haunted as H
All geometry procedural. Units metres, Z up. Uses studio_lib (L) helpers; never edits it.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion, Euler, noise
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
    sock = node.inputs[1]
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
    lamp = L.prim("sphere", loc=(-0.16, -0.1, 0.124), segments=12, ring_count=8, radius=0.009)
    L.assign(lamp, rec_m)
    lamp.parent = root
    rl = L.point((0, 0, 0), energy=0.8, color=(1, 0.05, 0.02), radius=0.01, name=name + "_recl")
    rl.parent = root
    rl.location = (-0.16, -0.12, 0.15)
    out = {"root": root, "reels": reels, "rec_mat": rec_m, "rec_light": rl, "vu_mat": vu_m, "needle": needle_piv, "body": body}
    start = spin_from
    if rec_on_frame:
        key_emission(rec_m, [(1, 0.0), (rec_on_frame, rec_strength)])
        key_energy(rl, [(1, 0.0), (rec_on_frame, 0.8)])
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
        chest_of_drawers((1.0, -1.1, 0.2), rot=(math.pi / 2, 0, 0.35), name="chest")
    else:
        chest_of_drawers((1.25, -1.45, 0), rot=(0, 0, math.pi / 2), name="chest")
    # chair
    if chair == "A":
        ch = wood_chair(CHAIR_A[0], CHAIR_A[1], jumper=jumper)
    elif chair == "B":
        ch = wood_chair(CHAIR_B[0], CHAIR_B[1], jumper=jumper)
    else:
        ch = wood_chair((-0.15, 0.6, 0.21), 0.9, jumper=False)
        ch["root"].rotation_euler = (0, math.radians(90), 0.9)
    # a few child details: rug, poster rectangles
    box_mesh("rug", [(0.0, 0.3, 0.005, 0.5, 0.8, 0.005)], L.mat_noise_surface("rug_m", (0.18, 0.08, 0.05), (0.3, 0.16, 0.08), scale=20, bump=0.1, voronoi=False))
    box_mesh("poster", [(-W / 2 + 0.01, 0.8, 1.5, 0.005, 0.25, 0.32)], L.mat_principled("poster_m", (0.4, 0.3, 0.22), rough=0.8))
    # moonlight through window (+ faint bounce fill)
    ml = L.spot((0.1, D / 2 + 2.2, 3.0), (0, 0, 0), energy=1800 * moon, size_deg=32, blend=0.25, color=(0.55, 0.68, 1.0), name="moon", radius=0.15)
    aim(ml, (0.1, D / 2 + 2.2, 3.0), (-0.1, 0.2, 0.0))
    amb = L.area((0, 0.2, Hh - 0.05), (0, 0, 0), energy=12 * moon, size=2.5, color=(0.5, 0.6, 0.9), name="ambfill")
    out = {"lamp": lamp, "rec": rec, "chair": ch, "moon": ml, "bedL": bl, "bedR": br}
    if fog:
        out["fog"] = room_fog((0, 0, Hh / 2), (W, D, Hh), density=0.025, color=(0.6, 0.68, 0.85))
    if dust_count:
        out["dust"] = dust((0, 0.4, 1.2), (W * 0.8, D * 0.8, 1.8), n, count=dust_count, radius=0.004, drift=(0.005, 0.0, -0.01), emit=0.12)
    return out


def bedroom_camera(n, mode="push", lens=None, push=1.0):
    """S01-style doorway push-in. mode 'push' | 'static' | 'start' (hold S01 frame 1)."""
    c = BEDROOM_CAM
    lens = lens or c["lens"]
    cm = cam(c["start"], c["target"], lens=lens)
    if mode == "push":
        e = tuple(c["start"][i] + (c["end"][i] - c["start"][i]) * push for i in range(3))
        cam_move(cm, [(1, c["start"], c["target"]), (n, e, c["target"])], ease=False)
    L.cam_light(cm, energy=18, color=(0.65, 0.75, 1.0), size_deg=80)
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
    body = box_mesh(name + "_body", [(0, d / 2 + 0.25, H2 / 2, w / 2, d / 2, H2 / 2)], brick, parent=root)
    # interior darkness box behind openings
    box_mesh(name + "_inner", [(0, 0.6, H2 / 2, w / 2 - 0.05, 0.02, H2 / 2)], L.mat_principled(name + "_dk", (0.01, 0.01, 0.01)), parent=root)
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
