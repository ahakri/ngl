"""Murder / cold-case builders (Dyatlov Pass snow slope, Somerton beach, evidence desk & board, diagrams).

Used by BLENDER_PROJECTS/MURDER-*/shots.py. Depends on studio_lib (passed in or imported).
All geometry procedural. Units metres, Z up. Style: cold, desaturated night/dawn + warm practicals.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler, noise
import studio_lib as L

FPS = 24
F_ANTON = "/home/user/ngl/YOUTUBE_ANIMATION_STUDIO/PIPELINE/fonts/Anton-Regular.ttf"
F_OSWALD = "/home/user/ngl/YOUTUBE_ANIMATION_STUDIO/PIPELINE/fonts/Oswald.ttf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def _font(path):
    import os
    if not os.path.exists(path):
        return None
    for f in bpy.data.fonts:
        if f.filepath == path:
            return f
    return bpy.data.fonts.load(path)

# ============================================================================ generic helpers

def empty(name, loc=(0, 0, 0), parent=None):
    e = L.link(bpy.data.objects.new(name, None))
    e.location = loc
    if parent:
        e.parent = parent
    return e


def mesh_obj(name, verts, faces, mat=None, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    o = L.link(bpy.data.objects.new(name, me))
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    if mat:
        L.assign(o, mat)
    return o


def key(obj, path, frame, value, index=-1):
    setattr(obj, path, value) if not isinstance(value, (tuple, list)) else setattr(obj, path, value)
    obj.keyframe_insert(path, frame=frame, index=index)


def keys(obj, path, pairs, interp=None):
    for f, v in pairs:
        setattr(obj, path, v)
        obj.keyframe_insert(path, frame=f)
    if interp:
        set_interp(obj, interp)


def set_interp(obj, mode):
    ad = obj.animation_data
    if ad and ad.action:
        for fc in L._fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = mode


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def solidify(o, t=0.01):
    m = o.modifiers.new("solid", "SOLIDIFY")
    m.thickness = t
    return m


def aim(obj, target):
    c = obj.constraints.new("TRACK_TO")
    c.target = target
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    return c


def ortho(cam, scale):
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = scale
    return cam

# ============================================================================ materials

def mat_snow(name="snow", tint=(0.80, 0.85, 0.95), rough=0.55, sparkle=True):
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 6
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (tint[0] * 0.86, tint[1] * 0.88, tint[2] * 0.95, 1)
    ramp.color_ramp.elements[1].color = (*tint, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    # fine wind-ripple bump
    nz2 = n.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 28.0
    nz2.inputs["Detail"].default_value = 4
    l.new(tc.outputs["Object"], nz2.inputs["Vector"])
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.18
    l.new(nz2.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    if "Specular IOR Level" in p.inputs:
        p.inputs["Specular IOR Level"].default_value = 0.35
    return m


def mat_dusted(name, base=(0.012, 0.02, 0.016), snow=(0.7, 0.76, 0.86), thresh=0.55, rough=0.85, noise_scale=6.0):
    """Dark surface with snow settled on upward-facing parts (trees, rocks, tent roof)."""
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    geo = n.new("ShaderNodeNewGeometry")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(geo.outputs["Normal"], sep.inputs[0])
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = noise_scale
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    add = n.new("ShaderNodeMath")
    add.operation = "ADD"
    l.new(sep.outputs["Z"], add.inputs[0])
    mul = n.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 0.5
    l.new(nz.outputs["Fac"], mul.inputs[0])
    l.new(mul.outputs[0], add.inputs[1])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = thresh + 0.25
    ramp.color_ramp.elements[0].color = (*base, 1)
    ramp.color_ramp.elements[1].position = thresh + 0.4
    ramp.color_ramp.elements[1].color = (*snow, 1)
    l.new(add.outputs[0], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    return m


def mat_canvas(name="canvas", c1=(0.22, 0.075, 0.02), c2=(0.42, 0.16, 0.045), snow_amt=0.0, translucent=0.35):
    """Orange-brown tent canvas with weave bump, optional snow dusting, translucency so interior light glows through."""
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    out = n["Material Output"]
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 4.0
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    col = ramp.outputs["Color"]
    if snow_amt > 0:
        geo = n.new("ShaderNodeNewGeometry")
        sep = n.new("ShaderNodeSeparateXYZ")
        l.new(geo.outputs["Normal"], sep.inputs[0])
        nz2 = n.new("ShaderNodeTexNoise")
        nz2.inputs["Scale"].default_value = 2.5
        l.new(tc.outputs["Object"], nz2.inputs["Vector"])
        mm = n.new("ShaderNodeMath")
        mm.operation = "MULTIPLY"
        l.new(sep.outputs["Z"], mm.inputs[0])
        l.new(nz2.outputs["Fac"], mm.inputs[1])
        r2 = n.new("ShaderNodeValToRGB")
        r2.color_ramp.elements[0].position = 0.45 - 0.25 * snow_amt
        r2.color_ramp.elements[1].position = 0.5 - 0.25 * snow_amt
        l.new(mm.outputs[0], r2.inputs["Fac"])
        mix = n.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        l.new(r2.outputs["Color"], mix.inputs[0])
        l.new(col, mix.inputs[6])
        mix.inputs[7].default_value = (0.72, 0.77, 0.86, 1)
        col = mix.outputs[2]
    l.new(col, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.92
    wv = n.new("ShaderNodeTexWave")
    wv.inputs["Scale"].default_value = 90
    wv.inputs["Distortion"].default_value = 1.5
    l.new(tc.outputs["Object"], wv.inputs["Vector"])
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.08
    l.new(wv.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    if translucent > 0:
        tr = n.new("ShaderNodeBsdfTranslucent")
        l.new(col, tr.inputs["Color"])
        mx = n.new("ShaderNodeMixShader")
        mx.inputs[0].default_value = translucent
        l.new(p.outputs[0], mx.inputs[1])
        l.new(tr.outputs[0], mx.inputs[2])
        l.new(mx.outputs[0], out.inputs["Surface"])
    return m


def mat_grid(name, color=(0.1, 0.6, 1.0), bg=(0.004, 0.01, 0.025), scale=2.0, width=0.03, strength=3.0):
    """Emissive grid lines on dark background (computer-sim look)."""
    m, n, l = L._mat(name)
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sep.inputs[0])
    lines = []
    for ax in ("X", "Y"):
        mu = n.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = scale
        l.new(sep.outputs[ax], mu.inputs[0])
        fr = n.new("ShaderNodeMath"); fr.operation = "FRACT"
        l.new(mu.outputs[0], fr.inputs[0])
        lt = n.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = width
        l.new(fr.outputs[0], lt.inputs[0])
        lines.append(lt)
    mx = n.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    l.new(lines[0].outputs[0], mx.inputs[0]); l.new(lines[1].outputs[0], mx.inputs[1])
    em = n.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    em2 = n.new("ShaderNodeEmission")
    em2.inputs[0].default_value = (*bg, 1)
    em2.inputs[1].default_value = 1.0
    ms = n.new("ShaderNodeMixShader")
    l.new(mx.outputs[0], ms.inputs[0])
    l.new(em2.outputs[0], ms.inputs[1])
    l.new(em.outputs[0], ms.inputs[2])
    l.new(ms.outputs[0], n["Material Output"].inputs["Surface"])
    m["_em"] = 1
    return m, em


def mat_paper(name="paper", c=(0.62, 0.58, 0.48), rough=0.85):
    return L.mat_noise_surface(name, (c[0] * 0.82, c[1] * 0.8, c[2] * 0.74), c, scale=14, bump=0.05, voronoi=False, rough=rough)


def mat_wood_dark(name="desk_wood"):
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1, 12, 1)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    wv = n.new("ShaderNodeTexWave")
    wv.inputs["Scale"].default_value = 2.5
    wv.inputs["Distortion"].default_value = 6
    wv.inputs["Detail"].default_value = 4
    l.new(mp.outputs[0], wv.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.035, 0.016, 0.008, 1)
    ramp.color_ramp.elements[1].color = (0.11, 0.055, 0.025, 1)
    l.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.42
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.05
    l.new(wv.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_cork(name="cork"):
    return L.mat_noise_surface(name, (0.08, 0.045, 0.022), (0.24, 0.14, 0.07), scale=40, bump=0.35, voronoi=True, rough=0.95)

# ============================================================================ world / sky

def night_sky(zen=(0.002, 0.003, 0.008), hor=(0.018, 0.024, 0.045), stars=1.0, strength=1.0, star_density=0.035):
    """Gradient night sky + procedural stars. Also acts as faint ambient light."""
    w = bpy.context.scene.world
    nt = w.node_tree
    n, l = nt.nodes, nt.links
    for nd in list(n):
        if nd.type not in ("OUTPUT_WORLD",):
            n.remove(nd)
    out = [nd for nd in n if nd.type == "OUTPUT_WORLD"][0]
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*hor, 1)
    ramp.color_ramp.elements[1].position = 0.45
    ramp.color_ramp.elements[1].color = (*zen, 1)
    l.new(sep.outputs["Z"], ramp.inputs["Fac"])
    bg = n.new("ShaderNodeBackground")
    bg.inputs[1].default_value = strength
    col = ramp.outputs["Color"]
    if stars > 0:
        vr = n.new("ShaderNodeTexVoronoi")
        vr.inputs["Scale"].default_value = 260
        vr.inputs["Randomness"].default_value = 1.0
        l.new(tc.outputs["Generated"], vr.inputs["Vector"])
        lt = n.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = star_density
        l.new(vr.outputs["Distance"], lt.inputs[0])
        gt = n.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.6
        l.new(vr.outputs["Color"], gt.inputs[0])
        m1 = n.new("ShaderNodeMath"); m1.operation = "MULTIPLY"
        l.new(lt.outputs[0], m1.inputs[0]); l.new(gt.outputs[0], m1.inputs[1])
        hz = n.new("ShaderNodeMath"); hz.operation = "GREATER_THAN"; hz.inputs[1].default_value = 0.06
        l.new(sep.outputs["Z"], hz.inputs[0])
        m2 = n.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
        l.new(m1.outputs[0], m2.inputs[0]); l.new(hz.outputs[0], m2.inputs[1])
        m3 = n.new("ShaderNodeMath"); m3.operation = "MULTIPLY"; m3.inputs[1].default_value = stars * 0.6
        l.new(m2.outputs[0], m3.inputs[0])
        mix = n.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "ADD"
        mix.inputs[0].default_value = 1.0
        l.new(col, mix.inputs[6])
        cc = n.new("ShaderNodeCombineXYZ")
        for i in range(3):
            l.new(m3.outputs[0], cc.inputs[i])
        l.new(cc.outputs[0], mix.inputs[7])
        col = mix.outputs[2]
    l.new(col, bg.inputs[0])
    l.new(bg.outputs[0], out.inputs["Surface"])
    return bg


def dawn_sky(hor=(0.55, 0.36, 0.34), mid=(0.16, 0.17, 0.24), zen=(0.03, 0.04, 0.08), strength=1.0, sun_dir=None):
    """Pre-dawn gradient: pink-grey horizon, cold blue zenith."""
    w = bpy.context.scene.world
    nt = w.node_tree
    n, l = nt.nodes, nt.links
    for nd in list(n):
        if nd.type not in ("OUTPUT_WORLD",):
            n.remove(nd)
    out = [nd for nd in n if nd.type == "OUTPUT_WORLD"][0]
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = n.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (*hor, 1)
    cr.elements[1].position = 0.5
    cr.elements[1].color = (*zen, 1)
    e = cr.elements.new(0.12)
    e.color = (*mid, 1)
    l.new(sep.outputs["Z"], ramp.inputs["Fac"])
    col = ramp.outputs["Color"]
    if sun_dir is not None:
        # warm glow around a horizon direction
        dv = n.new("ShaderNodeVectorMath"); dv.operation = "DOT_PRODUCT"
        l.new(tc.outputs["Generated"], dv.inputs[0])
        dv.inputs[1].default_value = Vector(sun_dir).normalized()
        pw = n.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 6.0
        mx0 = n.new("ShaderNodeMath"); mx0.operation = "MAXIMUM"; mx0.inputs[1].default_value = 0.0
        l.new(dv.outputs["Value"], mx0.inputs[0])
        l.new(mx0.outputs[0], pw.inputs[0])
        mix = n.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "ADD"
        l.new(pw.outputs[0], mix.inputs[0])
        l.new(col, mix.inputs[6])
        mix.inputs[7].default_value = (1.0, 0.55, 0.3, 1)
        col = mix.outputs[2]
    bg = n.new("ShaderNodeBackground")
    bg.inputs[1].default_value = strength
    l.new(col, bg.inputs[0])
    l.new(bg.outputs[0], out.inputs["Surface"])
    return bg


def moon(rot=(1.1, 0.0, 0.6), energy=1.6, color=(0.55, 0.66, 1.0), angle=1.0):
    return L.sun(rot=rot, energy=energy, color=color, angle=angle, name="moon")


def moon_disc(loc, radius=3.0, strength=6.0):
    o = L.prim("ico", loc=loc, subdivisions=3, radius=radius, name="moon_disc")
    L.assign(o, L.mat_emission("moon_m", (0.85, 0.9, 1.0), strength))
    o.visible_shadow = False
    return o

# ============================================================================ snow FX

def snowfall(center, size, n, count=1500, radius=0.012, fall=0.8, wind=(0.8, 0.0, 0.0), seed=7, name="snowfall", emit=0.25,
             color=(0.9, 0.93, 1.0), cam=None, clear=1.0, size_var=(0.4, 1.4)):
    """Falling / blowing snow: one tetra cloud translated over the shot (cheap). Size is padded so the
    camera stays covered during the whole drift. cam=(start_xyz, end_xyz): flakes whose path passes within
    `clear` metres of the camera path are dropped (no giant flakes on the lens)."""
    T = n / FPS
    d = Vector((wind[0], wind[1], -fall)) * T
    c = Vector((center[0] - d.x / 2, center[1] - d.y / 2, center[2] - d.z / 2))
    sz = Vector((size[0] + abs(d.x), size[1] + abs(d.y), size[2] + abs(d.z)))
    rnd = random.Random(seed)
    bm = bmesh.new()
    c0 = Vector(cam[0]) if cam else None
    c1 = Vector(cam[1]) if cam else None
    k = 0
    tries = 0
    while k < count and tries < count * 4:
        tries += 1
        p = c + Vector((rnd.uniform(-0.5, 0.5) * sz.x, rnd.uniform(-0.5, 0.5) * sz.y, rnd.uniform(-0.5, 0.5) * sz.z))
        if cam:
            near = False
            for t in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
                if ((p + d * t) - (c0 + (c1 - c0) * t)).length < clear:
                    near = True
                    break
            if near:
                continue
        r = radius * rnd.uniform(*size_var)
        vs = [bm.verts.new(p + Vector(v) * r) for v in ((1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1))]
        for f in ((0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)):
            bm.faces.new([vs[i] for i in f])
        k += 1
    o = L.mesh_from_bm(name, bm)
    m = L.mat_principled(name + "_m", color, rough=0.6, emit=color, emit_strength=emit)
    L.assign(o, m)
    o.visible_shadow = False
    o.location = (0, 0, 0)
    o.keyframe_insert("location", frame=1)
    o.location = d
    o.keyframe_insert("location", frame=n)
    L.linear_fcurves(o)
    return o


def snow_burst(center, n, f0, count=900, radius=0.025, spread=3.0, rise=1.2, seed=21, name="burst", emit=0.15, dur=30):
    """Puff of snow at an impact: cloud scales up from a point, drifts up, then settles out (scale shrink)."""
    m = L.mat_principled(name + "_m", (0.88, 0.9, 0.96), rough=0.7, emit=(0.8, 0.85, 0.95), emit_strength=emit)
    o = L.particle_cloud((0, 0, 0), (1.0, 1.0, 0.6), count=count, radius=radius / spread, mat=m, drift=(0, 0, 0), seed=seed, nframes=n,
                         name=name)
    o.animation_data_clear()
    o.location = center
    o.scale = (0.001,) * 3
    o.keyframe_insert("scale", frame=max(1, f0 - 1))
    o.keyframe_insert("location", frame=max(1, f0 - 1))
    o.scale = (spread * 0.7,) * 3
    o.keyframe_insert("scale", frame=f0 + 6)
    o.scale = (spread, spread, spread * 0.8)
    o.location = (center[0], center[1], center[2] + rise)
    o.keyframe_insert("scale", frame=f0 + dur)
    o.keyframe_insert("location", frame=f0 + dur)
    return o


def fog(center, size, density=0.03, color=(0.62, 0.68, 0.82)):
    return L.fog_volume(center=center, size=size, density=density, color=color)

# ============================================================================ terrain

def make_slope_h(slope_deg=18.0, seed=0, platform=None, macro=1.0, ripple=0.03, base=0.0):
    """Height function for a snow slope rising toward +Y. platform=(cx, cy, half_x, half_y, z, soft) flattens
    a cut for the tent (creates the uphill cut wall)."""
    tg = math.tan(math.radians(slope_deg))
    s = Vector((seed * 13.1, seed * 7.7, 0))

    def h(x, y):
        z = base + y * tg
        z += macro * 1.6 * noise.noise(Vector((x * 0.025, y * 0.025, 0.3)) + s)
        z += macro * 0.35 * noise.noise(Vector((x * 0.12, y * 0.12, 1.1)) + s)
        # sastrugi / wind ripples elongated along X
        z += ripple * noise.noise(Vector((x * 0.6, y * 2.4, 2.0)) + s)
        if platform:
            cx, cy, hx, hy, pz, soft = platform
            w = (1 - smoothstep(hx, hx + soft, abs(x - cx))) * (1 - smoothstep(hy, hy + soft, abs(y - cy)))
            # only cut downwards on the uphill side; build up gently downhill
            z = z * (1 - w) + pz * w
        return z
    return h


def heightfield(name, x0, x1, y0, y1, nx, ny, hfun, mat=None, prints=None, rim=0.25):
    xs = [x0 + (x1 - x0) * i / (nx - 1) for i in range(nx)]
    ys = [y0 + (y1 - y0) * j / (ny - 1) for j in range(ny)]
    H = [[hfun(x, y) for x in xs] for y in ys]
    if prints:
        dx = (x1 - x0) / (nx - 1)
        dy = (y1 - y0) / (ny - 1)
        for (px, py, ang, rx, ry, depth) in prints:
            R = max(rx, ry) * 1.5
            i0, i1 = max(0, int((px - R - x0) / dx)), min(nx - 1, int((px + R - x0) / dx) + 1)
            j0, j1 = max(0, int((py - R - y0) / dy)), min(ny - 1, int((py + R - y0) / dy) + 1)
            ca, sa = math.cos(ang), math.sin(ang)
            for j in range(j0, j1 + 1):
                for i in range(i0, i1 + 1):
                    lx, ly = xs[i] - px, ys[j] - py
                    u = (lx * ca + ly * sa) / rx
                    v = (-lx * sa + ly * ca) / ry
                    d2 = u * u + v * v
                    if d2 < 1:
                        H[j][i] -= depth * (1 - d2) ** 0.7
                    elif d2 < 2.2:
                        H[j][i] += depth * rim * math.sin((d2 - 1) / 1.2 * math.pi)
    verts = [(xs[i], ys[j], H[j][i]) for j in range(ny) for i in range(nx)]
    faces = [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(ny - 1) for i in range(nx - 1)]
    return mesh_obj(name, verts, faces, mat=mat, smooth=True)


def trail(start, end, step=0.36, gap=0.11, seed=1, wobble=0.25, rx=0.055, ry=0.13, depth=0.05, skip=0.0):
    """Footprints from start to end (xy). Alternating left/right. Returns list for heightfield(prints=)."""
    rnd = random.Random(seed)
    a, b = Vector(start[:2]), Vector(end[:2])
    d = b - a
    ln = d.length
    dn = d.normalized()
    perp = Vector((-dn.y, dn.x))
    ang = math.atan2(dn.y, dn.x) - math.pi / 2
    out = []
    k = 0
    t = 0.0
    while t < ln:
        side = 1 if k % 2 == 0 else -1
        w = wobble * noise.noise(Vector((t * 0.15, seed * 3.3, 0)))
        p = a + dn * t + perp * (side * gap + w)
        if rnd.random() >= skip:
            out.append((p.x, p.y, ang + rnd.uniform(-0.15, 0.15), rx * rnd.uniform(0.85, 1.25), ry * rnd.uniform(0.85, 1.15),
                        depth * rnd.uniform(0.7, 1.2)))
        t += step * rnd.uniform(0.85, 1.15)
        k += 1
    return out


def print_decals(prints, hfun, name="prints", color=(0.16, 0.2, 0.3), lift=0.02, scale=1.0):
    """Far-view footprints: dark ovals laid on the terrain (single mesh)."""
    verts, faces = [], []
    seg = 8
    for (px, py, ang, rx, ry, depth) in prints:
        ca, sa = math.cos(ang), math.sin(ang)
        base = len(verts)
        verts.append((px, py, hfun(px, py) + lift))
        for s in range(seg):
            t = 2 * math.pi * s / seg
            u, v = math.cos(t) * rx * scale, math.sin(t) * ry * scale
            x, y = px + u * ca - v * sa, py + u * sa + v * ca
            verts.append((x, y, hfun(x, y) + lift))
        for s in range(seg):
            faces.append((base, base + 1 + s, base + 1 + (s + 1) % seg))
    m = L.mat_principled(name + "_m", color, rough=0.9)
    o = mesh_obj(name, verts, faces, mat=m)
    o.visible_shadow = False
    return o


def mountains(name, size=600, res=120, height=90, seed=3, center=(0, 0, 0), mat=None):
    """Big ridged mountain range terrain (for aerial / background)."""
    s = Vector((seed * 5.3, seed * 1.7, 0))

    def h(x, y):
        p = Vector((x / 180, y / 180, 0)) + s
        r = noise.ridged_multi_fractal(p, 1.0, 2.0, 6, 1.0, 2.0)
        return center[2] + height * 0.35 * r + 18 * noise.noise(p * 3)
    o = heightfield(name, center[0] - size / 2, center[0] + size / 2, center[1] - size / 2, center[1] + size / 2, res, res, h,
                    mat=mat or mat_snow(name + "_m"))
    return o, h

# ============================================================================ trees

def conifer_forest(name, spots, mat=None, seed=1, tiers=(4, 6), bare_frac=0.2):
    """spots: list of (x, y, z, height). One mesh for all trees (fast). Snow-dusted dark spruce/cedar silhouettes,
    with a fraction of bare birch-like trunks."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    for (x, y, z, h) in spots:
        rz = rnd.uniform(0, 6.28)
        lean = Matrix.Rotation(rnd.uniform(-0.05, 0.05), 4, "X") @ Matrix.Rotation(rnd.uniform(-0.05, 0.05), 4, "Y")
        base = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rz, 4, "Z") @ lean
        bmesh.ops.create_cone(bm, cap_ends=False, segments=5, radius1=h * 0.025, radius2=h * 0.01, depth=h,
                              matrix=base @ Matrix.Translation((0, 0, h / 2)))
        if rnd.random() < bare_frac:
            for k in range(rnd.randint(3, 5)):
                zz = h * rnd.uniform(0.35, 0.9)
                bl = h * rnd.uniform(0.12, 0.22)
                mm = base @ Matrix.Translation((0, 0, zz)) @ Matrix.Rotation(rnd.uniform(0, 6.28), 4, "Z") @ \
                    Matrix.Rotation(rnd.uniform(0.6, 1.1), 4, "X") @ Matrix.Translation((0, 0, bl / 2))
                bmesh.ops.create_cone(bm, cap_ends=False, segments=4, radius1=h * 0.008, radius2=h * 0.002, depth=bl, matrix=mm)
            continue
        nt = rnd.randint(*tiers)
        for k in range(nt):
            f = k / nt
            r = h * (0.24 * (1 - f) + 0.04) * rnd.uniform(0.85, 1.15)
            dz = h * 0.32 * (1 - 0.4 * f)
            zz = h * (0.12 + 0.82 * f)
            bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=r, radius2=0.0, depth=dz,
                                  matrix=base @ Matrix.Translation((rnd.uniform(-0.05, 0.05) * h, 0, zz + dz / 2)) @
                                  Matrix.Rotation(rnd.uniform(0, 6.28), 4, "Z"))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = L.link(bpy.data.objects.new(name, me))
    L.assign(o, mat or mat_dusted(name + "_m"))
    return o


def scatter_spots(area, count, hfun, seed=2, h=(7, 13), exclude=None):
    """area=(x0,x1,y0,y1). exclude(x,y)->True to skip."""
    rnd = random.Random(seed)
    out = []
    tries = 0
    while len(out) < count and tries < count * 10:
        tries += 1
        x, y = rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3])
        if exclude and exclude(x, y):
            continue
        out.append((x, y, hfun(x, y) - 0.2, rnd.uniform(*h)))
    return out

# ============================================================================ tent

def tent(loc=(0, 0, 0), rot_z=0.0, length=4.0, width=2.0, height=1.2, wall=0.32, slit=True, slit_x=0.35, gap=0.07,
         slit_len=(0.08, 0.92), mat=None, snow_amt=0.6, inner_light=0.0, crush=0.0, name="tent", flap_w=None, ends_buried=True):
    """Gabled canvas tent, ridge along local X. The -Y roof panel carries a vertical slit (cut from inside) with two
    hinged flaps (parts['flapL']/['flapR'] pivots: animate rotation_euler.y). crush 0..1 sags the ridge (slab impact).
    Returns dict(root, flapL, flapR, light, slit_world(list of points), panel_frame)."""
    m = mat or mat_canvas(name + "_canvas", snow_amt=snow_amt)
    inner = mat_canvas(name + "_inner", c1=(0.1, 0.035, 0.012), c2=(0.18, 0.07, 0.02), translucent=0.5)
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    hl, hw = length / 2, width / 2
    H = height * (1 - 0.45 * crush)
    parts = {"root": root}

    def ridge_z(x):
        # ridge sags a little between poles, more when crushed
        u = (x + hl) / length
        return H - (0.05 + 0.5 * crush) * math.sin(math.pi * u) ** 2

    def panel(pfun, nu, nv, nm, sag=0.035):
        verts, faces = [], []
        for j in range(nv + 1):
            for i in range(nu + 1):
                u, v = i / nu, j / nv
                p = pfun(u, v)
                s = sag * math.sin(math.pi * u) * math.sin(math.pi * v)
                verts.append((p[0], p[1], p[2] - s))
        for j in range(nv):
            for i in range(nu):
                a = j * (nu + 1) + i
                faces.append((a, a + 1, a + nu + 2, a + nu + 1))
        o = mesh_obj(nm, verts, faces, mat=m, smooth=True)
        o.data.materials.append(inner)
        o.parent = root
        solidify(o, 0.012)
        return o

    def roof_pt(side, x, v):
        # side -1 => -Y roof, +1 => +Y roof; v 0 eave .. 1 ridge
        y0, z0 = side * hw, wall
        y1, z1 = 0.0, ridge_z(x)
        return (x, y0 + (y1 - y0) * v, z0 + (z1 - z0) * v)

    # back (+Y) roof and walls
    panel(lambda u, v: roof_pt(1, -hl + length * u, v), 16, 6, name + "_roofB")
    panel(lambda u, v: (-hl + length * u, hw, wall * v), 16, 2, name + "_wallB", sag=0.0)
    panel(lambda u, v: (-hl + length * u, -hw, wall * v), 16, 2, name + "_wallF", sag=0.0)
    # front (-Y) roof, split by slit
    if slit:
        xa, xb = slit_x - gap, slit_x + gap
        va, vb = slit_len
        panel(lambda u, v: roof_pt(-1, -hl + (xa + hl) * u, v), 10, 6, name + "_roofF1")
        panel(lambda u, v: roof_pt(-1, xb + (hl - xb) * u, v), 8, 6, name + "_roofF2")
        # strips above/below the slit (slit doesn't reach eave/ridge)
        if va > 0:
            panel(lambda u, v: roof_pt(-1, xa + (xb - xa) * u, va * v), 2, 1, name + "_roofF3", sag=0)
        if vb < 1:
            panel(lambda u, v: roof_pt(-1, xa + (xb - xa) * u, vb + (1 - vb) * v), 2, 1, name + "_roofF4", sag=0)
        # flap pivots in panel frame
        E = Vector(roof_pt(-1, slit_x, va))
        R = Vector(roof_pt(-1, slit_x, vb))
        vdir = (R - E).normalized()
        udir = Vector((1, 0, 0))
        ndir = udir.cross(vdir)
        frame = Matrix((udir, vdir, ndir)).transposed().to_4x4()
        fw = flap_w or gap * 1.05
        flen = (R - E).length
        for tag, x0, sgn in (("L", xa, 1), ("R", xb, -1)):
            pv = empty(f"{name}_flap{tag}_pv", parent=root)
            pv.matrix_parent_inverse = Matrix.Identity(4)
            fr = Matrix.Translation(Vector((x0, E.y, E.z))) @ frame
            pv.matrix_basis = fr
            hinge = empty(f"{name}_flap{tag}", parent=pv)
            verts, faces = [], []
            nseg = 6
            for j in range(nseg + 1):
                yy = flen * j / nseg
                ragged = 0.012 * math.sin(j * 2.7 + (1 if tag == "L" else 3))
                verts += [(0, yy, 0), (sgn * (fw + ragged), yy, 0)]
            for j in range(nseg):
                a = 2 * j
                faces.append((a, a + 1, a + 3, a + 2))
            fo = mesh_obj(f"{name}_flap{tag}_m", verts, faces, mat=m)
            fo.data.materials.append(inner)
            fo.parent = hinge
            solidify(fo, 0.01)
            parts["flap" + tag] = hinge
        parts["slit_mid"] = (E + R) / 2
        parts["slit_E"] = E
        parts["slit_R"] = R
        parts["frame"] = frame
    else:
        panel(lambda u, v: roof_pt(-1, -hl + length * u, v), 16, 6, name + "_roofF")
    # gable ends
    for sx in (-1, 1):
        x = sx * hl
        pts = [(x, -hw, 0), (x, hw, 0), (x, hw, wall), (x, 0, ridge_z(x)), (x, -hw, wall)]
        o = mesh_obj(name + f"_end{sx}", pts, [(0, 1, 2, 3, 4)], mat=m)
        o.data.materials.append(inner)
        o.parent = root
        solidify(o, 0.012)
    # ridge pole + guy ropes
    rope_m = L.mat_principled(name + "_rope", (0.25, 0.22, 0.17), rough=0.9)
    for sx in (-1, 1):
        p = L.prim("cyl", loc=(sx * (hl + 0.05), 0, H / 2), vertices=6, radius=0.018, depth=H + 0.1)
        L.assign(p, rope_m)
        p.parent = root
    if inner_light > 0:
        lt = L.point((0, 0, 0.5), energy=inner_light, color=(1.0, 0.62, 0.3), radius=0.15, name=name + "_lamp")
        lt.parent = root
        parts["light"] = lt
    return parts


def anim_flaps(parts, n, base=0.7, amp=0.35, rate=1.6, seed=1, open_from=None, open_to=None, start_closed=False):
    """Flaps flutter outward in the wind. open_from/open_to frames: animate from closed to open."""
    for tag, sg in (("L", -1), ("R", 1)):
        hn = parts.get("flap" + tag)
        if not hn:
            continue
        for f in range(1, n + 1, 2):
            t = f / FPS
            a = base + amp * noise.noise(Vector((t * rate, seed + (0 if tag == "L" else 5.5), 0.5)))
            a += 0.12 * math.sin(t * 9 + (0 if tag == "L" else 1.3))
            if open_from is not None:
                a *= ease((f - open_from) / max(1, (open_to - open_from)))
            hn.rotation_euler = (0, sg * a, 0)
            hn.keyframe_insert("rotation_euler", frame=f)


def snow_bank(loc, scale, seed=1, mat=None, rot_z=0.0, name="bank"):
    o = L.prim("ico", loc=loc, subdivisions=4, radius=1.0, name=name)
    o.scale = scale
    o.rotation_euler = (0, 0, rot_z)
    L.add_displace(o, strength=0.18, scale=0.6, name=name + "_d")
    L.smooth(o)
    L.assign(o, mat or mat_snow(name + "_m"))
    return o


def torch(loc, target_loc, energy=900, size_deg=22, color=(1.0, 0.78, 0.5), name="torch"):
    """Warm handheld torch beam: spot aimed at a (movable) target empty."""
    sp = L.spot(loc, (0, 0, 0), energy=energy, size_deg=size_deg, blend=0.35, color=color, name=name, radius=0.03)
    tg = empty(name + "_tgt", target_loc)
    aim(sp, tg)
    return sp, tg

# ============================================================================ characters

def hiker(name="hiker", color=(0.018, 0.02, 0.026), height=1.75, emit=None):
    return L.char_figure(name=name, color=color, height=height, coat=True, emit=emit)


def seated_pose(parts, slump=0.35, lean=0.22):
    """Seated against a wall, legs out, head bowed (respectful, distant silhouette). Figure faces +Y locally."""
    pel = parts["pelvis"]
    pel.location.z = 0.13
    pel.rotation_euler = (lean, 0, 0)  # torso leans back
    for t in ("L", "R"):
        parts["hip" + t].rotation_euler = (math.radians(92) - lean, 0, (0.1 if t == "L" else -0.1))
        parts["knee" + t].rotation_euler = (math.radians(-6), 0, 0)
        parts["shoulder" + t].rotation_euler = (0.3, 0, (0.15 if t == "L" else -0.15))
        parts["elbow" + t].rotation_euler = (0.55, 0, 0)
    parts["neck"].rotation_euler = (-0.45 - slump * 0.4, 0, 0.15)


# ============================================================================ cross-section diagram

def section_diagram(slope_deg=24.0, T=1.35, notch=(0.0, 2.2), depth_y=1.6, span=(-9, 9), with_notch=True, tent_block=True,
                    slab=False, slab_full=True, name="sec", ridge_x=-3.4):
    """Side-on slope cross-section (XZ plane, extruded along Y). Slope descends toward +X. Returns dict of parts.
    notch=(x_centre, width): tent platform cut into the snow layer."""
    tg = math.tan(math.radians(slope_deg))

    def zg(x):
        if ridge_x is None or x >= ridge_x:
            return -x * tg
        # rounded crest, gentle windward side beyond the ridge
        d = ridge_x - x
        return -ridge_x * tg - d * tg * 0.25
    zs = lambda x: zg(x) + T
    xn, wn = notch
    a, b = xn - wn / 2, xn + wn / 2
    zp = zs(b)
    x0, x1 = span
    bottom = zg(x1) - 4

    snow_m = L.mat_principled(name + "_snow", (0.86, 0.9, 0.97), rough=0.7, emit=(0.6, 0.66, 0.78), emit_strength=0.25)
    side_snow = L.mat_principled(name + "_snowside", (0.55, 0.62, 0.78), rough=0.8, emit=(0.3, 0.36, 0.5), emit_strength=0.25)
    ground_m = L.mat_noise_surface(name + "_ground", (0.035, 0.035, 0.04), (0.07, 0.07, 0.08), scale=1.2, bump=0.1, voronoi=False)
    parts = {"a": a, "b": b, "zp": zp, "zs": zs, "zg": zg, "tg": tg}

    def extrude(poly, nm, mats, y0=-depth_y / 2, y1=depth_y / 2):
        bm = bmesh.new()
        vf = [bm.verts.new((x, y0, z)) for x, z in poly]
        vb = [bm.verts.new((x, y1, z)) for x, z in poly]
        f = bm.faces.new(vf)
        f.material_index = 0
        fb = bm.faces.new(list(reversed(vb)))
        fb.material_index = 0
        k = len(poly)
        for i in range(k):
            q = bm.faces.new((vf[i], vf[(i + 1) % k], vb[(i + 1) % k], vb[i]))
            q.material_index = 1
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        me = bpy.data.meshes.new(nm)
        bm.to_mesh(me)
        bm.free()
        o = L.link(bpy.data.objects.new(nm, me))
        for mm in mats:
            o.data.materials.append(mm)
        return o

    xs = sorted(set([x0 + (x1 - x0) * i / 60 for i in range(61)] + ([ridge_x] if ridge_x is not None else [])))
    gpoly = [(x, zg(x)) for x in xs] + [(x1, bottom), (x0, bottom)]
    parts["ground"] = extrude(gpoly, name + "_g", [ground_m, ground_m])
    # snow layer polygon (top with optional notch), then ground line back
    if with_notch:
        top = [(x, zs(x)) for x in xs if x < a - 1e-6] + [(a, zs(a)), (a, zp), (b, zp)] + [(x, zs(x)) for x in xs if x > b + 1e-6]
    else:
        top = [(x, zs(x)) for x in xs]
    poly = top + [(x, zg(x)) for x in reversed(xs)]
    parts["snow"] = extrude(poly, name + "_s", [snow_m, side_snow], y0=-depth_y / 2 - 0.01, y1=depth_y / 2 + 0.01)
    if with_notch:
        # the dug-out wedge (animated away in S13)
        fill = extrude([(a, zs(a)), (a, zp), (b, zp)], name + "_fill", [snow_m, side_snow], y0=-depth_y / 2 - 0.02,
                       y1=depth_y / 2 + 0.02)
        parts["fill"] = fill
    if tent_block:
        tw, th, tw2 = wn * 0.8, 1.05, 0.22
        cx = (a + b) / 2 + 0.05
        tpoly = [(cx - tw / 2, zp), (cx + tw / 2, zp), (cx + tw / 2, zp + 0.25), (cx, zp + th), (cx - tw / 2, zp + 0.25)]
        tm = L.mat_principled(name + "_tent", (0.55, 0.2, 0.05), rough=0.8, emit=(0.6, 0.22, 0.05), emit_strength=0.6)
        parts["tent"] = extrude(tpoly, name + "_tent", [tm, tm], y0=-depth_y * 0.35, y1=depth_y * 0.35)
        parts["tent_c"] = (cx, zp)
    if slab:
        # wind slab: wedge on the snow surface uphill of the notch
        sx0 = max(a - 4.2, (ridge_x + 0.3) if ridge_x is not None else -99)
        thick = lambda x: 0.75 * smoothstep(sx0, a - 0.3, x)
        sxs = [sx0 + (a - sx0) * i / 12 for i in range(13)]
        spoly = [(x, zs(x) + thick(x)) for x in sxs] + [(a, zs(a) + thick(a) * 0.7), (a, zs(a))] + \
                [(x, zs(x) - 0.01) for x in reversed(sxs)]
        slab_m = L.mat_principled(name + "_slab", (0.45, 0.7, 1.0), rough=0.7, emit=(0.3, 0.6, 1.0), emit_strength=0.9)
        sl = extrude(spoly, name + "_slab", [slab_m, side_snow], y0=-depth_y / 2 - 0.03, y1=depth_y / 2 + 0.03)
        parts["slab"] = sl
        parts["slab_x0"] = sx0
        if not slab_full:
            sk0 = sl.shape_key_add(name="Basis")
            sk1 = sl.shape_key_add(name="full")
            for v, bv in zip(sl.data.vertices, sk0.data):
                x, z = v.co.x, v.co.z
                bv.co.z = max(zs(x) - 0.005, min(z, zs(x) + 0.03))
            parts["slab_key"] = sk1
    return parts


def arrow(start, end, color=(0.9, 0.95, 1.0), strength=2.0, width=0.06, head=0.25, name="arrow", y=-1.0):
    """Flat emissive arrow in the XZ plane at depth y (for diagrams)."""
    s, e = Vector((start[0], y, start[1])), Vector((end[0], y, end[1]))
    d = (e - s)
    ln = d.length
    dn = d.normalized()
    pr = Vector((-dn.z, 0, dn.x))
    hb = e - dn * head
    vs = [s + pr * width / 2, hb + pr * width / 2, hb + pr * head * 0.55, e, hb - pr * head * 0.55, hb - pr * width / 2, s - pr * width / 2]
    o = mesh_obj(name, vs, [(0, 1, 5, 6), (2, 3, 4)], mat=L.mat_emission(name + "_m", color, strength))
    return o

# ============================================================================ evidence board

def evidence_board(w=3.2, h=5.0, lamp=True, lamp_energy=220, name="board"):
    """Dark cork wall in the XZ plane at y=0 facing -Y, single hanging lamp. Returns dict."""
    b = L.prim("plane", loc=(0, 0, 0), size=1, rot=(math.pi / 2, 0, 0), name=name)
    b.scale = (w, h, 1)
    L.assign(b, mat_cork(name + "_cork"))
    wall = L.prim("plane", loc=(0, 0.02, 0), size=1, rot=(math.pi / 2, 0, 0), name=name + "_wall")
    wall.scale = (14, 14, 1)
    L.assign(wall, L.mat_noise_surface(name + "_wallm", (0.02, 0.02, 0.022), (0.05, 0.05, 0.055), scale=5, bump=0.2, voronoi=False))
    frame_m = L.mat_principled(name + "_frame", (0.04, 0.025, 0.015), rough=0.6)
    for (x, z, sx, sz) in ((0, h / 2, w / 2 + 0.06, 0.05), (0, -h / 2, w / 2 + 0.06, 0.05), (w / 2, 0, 0.05, h / 2), (-w / 2, 0, 0.05, h / 2)):
        f = L.prim("cube", loc=(x, -0.03, z))
        f.scale = (sx, 0.04, sz)
        L.assign(f, frame_m)
    out = {"board": b}
    if lamp:
        shade_m = L.mat_principled(name + "_shade", (0.03, 0.035, 0.03), rough=0.4, metal=0.7)
        lz = h / 2 + 0.35
        sh = L.prim("cone", loc=(0, -0.9, lz), vertices=24, radius1=0.32, radius2=0.08, depth=0.3, name=name + "_shade")
        L.assign(sh, shade_m)
        cord = L.prim("cyl", loc=(0, -0.9, lz + 1.5), vertices=6, radius=0.008, depth=3.0)
        L.assign(cord, shade_m)
        bulb = L.prim("sphere", loc=(0, -0.9, lz - 0.12), radius=0.07, segments=12, ring_count=8)
        L.assign(bulb, L.mat_emission(name + "_bulb", (1.0, 0.75, 0.45), 30))
        bulb.visible_shadow = False
        sp = L.spot((0, -0.9, lz - 0.14), (math.radians(-28), 0, 0), energy=lamp_energy * 4, size_deg=75, blend=0.8,
                    color=(1.0, 0.72, 0.42), name=name + "_lamp", radius=0.1)
        pt = L.point((0, -1.3, lz - 0.3), energy=lamp_energy * 0.25, color=(1.0, 0.7, 0.4), radius=0.3, name=name + "_fill")
        out.update(lamp=sp, fill=pt, bulb=bulb)
    return out


def paper_card(text, loc, size=(0.95, 0.62), rot_y=0.0, badge="THEORY", font=None, name="card", text_size=0.2,
               paper=(0.66, 0.62, 0.52)):
    """Pinned paper card with dark text and a yellow badge; root empty at loc (card lies in XZ plane, facing -Y)."""
    root = empty(name, loc)
    root.rotation_euler = (0, rot_y, 0)
    p = L.prim("plane", loc=(0, 0, 0), size=1, rot=(math.pi / 2, 0, 0), name=name + "_paper")
    p.scale = (size[0], size[1], 1)
    L.assign(p, mat_paper(name + "_pm", paper))
    p.parent = root
    ink = L.mat_principled(name + "_ink", (0.03, 0.025, 0.02), rough=0.7)
    t = L.text3d(text, loc=(0, -0.006, -0.08), size=text_size, extrude=0.0, mat=ink, font=None, name=name + "_t")
    t.data.font = _font(font or F_ANTON) or t.data.font
    t.data.align_y = "CENTER"
    t.parent = root
    if badge:
        bm_ = L.mat_principled(name + "_badge", (0.95, 0.68, 0.08), rough=0.5, emit=(0.9, 0.6, 0.05), emit_strength=0.3)
        bd = L.prim("plane", loc=(-size[0] / 2 + 0.2, -0.008, size[1] / 2 - 0.1), size=1, rot=(math.pi / 2, 0, 0))
        bd.scale = (0.32, 0.1, 1)
        L.assign(bd, bm_)
        bd.parent = root
        bt = L.text3d(badge, loc=(-size[0] / 2 + 0.2, -0.012, size[1] / 2 - 0.1), size=0.065, extrude=0, mat=ink, name=name + "_bt")
        bt.data.font = _font(F_OSWALD) or bt.data.font
        bt.data.align_y = "CENTER"
        bt.parent = root
    pin = L.prim("sphere", loc=(0, -0.03, size[1] / 2 - 0.06), radius=0.03, segments=10, ring_count=6)
    L.assign(pin, L.mat_principled(name + "_pin", (0.6, 0.04, 0.03), rough=0.3))
    pin.parent = root
    return root


def slam_in(root, f_hit, frm=(0.0, -1.4, 0.3), rot0=0.25, scale0=1.6, lead=6):
    """Card flies in from the camera side and lands with a little overshoot at f_hit."""
    end_loc = root.location.copy()
    end_rot = root.rotation_euler.copy()
    root.location = end_loc + Vector(frm)
    root.rotation_euler = (end_rot.x, end_rot.y + rot0, end_rot.z)
    root.scale = (scale0,) * 3
    for f in (1, f_hit - lead):
        root.keyframe_insert("location", frame=max(1, f))
        root.keyframe_insert("rotation_euler", frame=max(1, f))
        root.keyframe_insert("scale", frame=max(1, f))
    root.location = end_loc
    root.rotation_euler = end_rot
    root.scale = (0.97, 0.97, 0.97)
    root.keyframe_insert("location", frame=f_hit)
    root.keyframe_insert("rotation_euler", frame=f_hit)
    root.keyframe_insert("scale", frame=f_hit)
    root.scale = (1, 1, 1)
    root.keyframe_insert("scale", frame=f_hit + 3)
    if f_hit - lead <= 1:
        pass


def hide_until(obj, f):
    """Visibility switch (render) at frame f."""
    if f <= 1:
        return
    obj.hide_render = True
    obj.keyframe_insert("hide_render", frame=1)
    obj.hide_render = True
    obj.keyframe_insert("hide_render", frame=max(1, f - 1))
    obj.hide_render = False
    obj.keyframe_insert("hide_render", frame=f)
    for c in obj.children_recursive:
        c.hide_render = True
        c.keyframe_insert("hide_render", frame=1)
        c.keyframe_insert("hide_render", frame=max(1, f - 1))
        c.hide_render = False
        c.keyframe_insert("hide_render", frame=f)


def shake(cam, hits, amp=0.04, decay=8):
    """Add decaying camera shake impulses at hit frames (on top of existing location keys)."""
    base = {}
    ad = cam.animation_data
    # sample existing path
    sc = bpy.context.scene
    for hf in hits:
        for k in range(0, decay + 1):
            f = hf + k
            sc.frame_set(f)
            p = cam.location.copy()
            a = amp * (1 - k / decay) * (1 if k % 2 == 0 else -1)
            cam.location = (p.x + a * 0.6, p.y, p.z + a)
            cam.keyframe_insert("location", frame=f)
    sc.frame_set(1)

# ============================================================================ helix / headstones / beach (Somerton)

def dna_helix(n_pairs=26, radius=0.6, pitch=3.2, height=5.0, sphere_r=0.08, color_a=(0.2, 0.85, 1.0), color_b=(0.9, 0.95, 1.0),
              strength=4.0, name="dna"):
    """Double helix built from emissive spheres along two spirals + rungs. Root empty (rotate about Z)."""
    root = empty(name)
    ma = L.mat_emission(name + "_a", color_a, strength)
    mb = L.mat_emission(name + "_b", color_b, strength * 0.8)
    mr = L.mat_emission(name + "_r", (0.3, 0.6, 0.9), strength * 0.4)
    bm_a, bm_b, bm_r = bmesh.new(), bmesh.new(), bmesh.new()
    for i in range(n_pairs * 3):
        t = i / (n_pairs * 3 - 1)
        z = -height / 2 + height * t
        ang = 2 * math.pi * z / pitch
        for k, bmx in ((0, bm_a), (1, bm_b)):
            a = ang + math.pi * k
            bmesh.ops.create_icosphere(bmx, subdivisions=2, radius=sphere_r * (1.0 if i % 3 == 0 else 0.6),
                                       matrix=Matrix.Translation((radius * math.cos(a), radius * math.sin(a), z)))
        if i % 3 == 0:
            p0 = Vector((radius * math.cos(ang), radius * math.sin(ang), z))
            p1 = Vector((radius * math.cos(ang + math.pi), radius * math.sin(ang + math.pi), z))
            mid = (p0 + p1) / 2
            d = p1 - p0
            mm = Matrix.Translation(mid) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
            bmesh.ops.create_cone(bm_r, cap_ends=True, segments=6, radius1=sphere_r * 0.3, radius2=sphere_r * 0.3, depth=d.length * 0.9, matrix=mm)
    objs = []
    for bmx, mm, nm in ((bm_a, ma, "_sa"), (bm_b, mb, "_sb"), (bm_r, mr, "_rg")):
        me = bpy.data.meshes.new(name + nm)
        bmx.to_mesh(me)
        bmx.free()
        o = L.link(bpy.data.objects.new(name + nm, me))
        L.assign(o, mm)
        o.parent = root
        objs.append(o)
    return root, objs


def headstone(loc, rot_z=0.0, w=0.6, h=0.9, d=0.14, mat=None, kind=0, name="stone"):
    if kind == 0:  # rounded top
        bm = bmesh.new()
        pts = [(-w / 2, 0), (w / 2, 0), (w / 2, h - w / 2)] + \
              [(w / 2 * math.cos(a), h - w / 2 + w / 2 * math.sin(a)) for a in [math.pi * k / 10 for k in range(1, 10)]] + [(-w / 2, h - w / 2)]
        vf = [bm.verts.new((x, -d / 2, z)) for x, z in pts]
        vb = [bm.verts.new((x, d / 2, z)) for x, z in pts]
        bm.faces.new(vf)
        bm.faces.new(list(reversed(vb)))
        k = len(pts)
        for i in range(k):
            bm.faces.new((vf[i], vf[(i + 1) % k], vb[(i + 1) % k], vb[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        o = L.link(bpy.data.objects.new(name, me))
    elif kind == 1:  # slab
        o = L.prim("cube", loc=(0, 0, h / 2), name=name)
        o.scale = (w / 2, d / 2, h / 2)
        L.apply_scale(o)
        o.location = (0, 0, 0)
        for v in o.data.vertices:
            v.co.z += h / 2
    else:  # cross
        o = L.prim("cube", loc=(0, 0, 0), name=name)
        o.scale = (0.07, d / 2, h / 2)
        L.apply_scale(o)
        for v in o.data.vertices:
            v.co.z += h / 2
        c2 = L.prim("cube", loc=(0, 0, h * 0.72))
        c2.scale = (w * 0.38, d / 2, 0.07)
        c2.parent = o
        L.assign(c2, mat)
    o.location = loc
    o.rotation_euler = (0.04 * math.sin(loc[0] * 3), 0.05 * math.cos(loc[1] * 2), rot_z)
    L.assign(o, mat)
    L.bevel(o, 0.015)
    return o


def sea(size=(400, 300), loc=(0, 60, 0), color=(0.035, 0.05, 0.06), n=100, speed=(0.6, 0.25), name="sea"):
    """Flat sea plane with animated wave normals (moving texture) - cheap."""
    m, nd, l = L._mat(name + "_m")
    p = nd["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = 0.12
    tc = nd.new("ShaderNodeTexCoord")
    mp = nd.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.6, 1.6, 1)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = nd.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.2
    nz.inputs["Detail"].default_value = 8
    l.new(mp.outputs[0], nz.inputs["Vector"])
    bp = nd.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.35
    bp.inputs["Distance"].default_value = 0.3
    l.new(nz.outputs["Fac"], bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    mp.inputs["Location"].default_value = (0, 0, 0)
    mp.inputs["Location"].keyframe_insert("default_value", frame=1)
    mp.inputs["Location"].default_value = (speed[0] * n / FPS, speed[1] * n / FPS, 0.2 * n / FPS)
    mp.inputs["Location"].keyframe_insert("default_value", frame=n)
    o = L.prim("plane", loc=loc, size=1, name=name)
    o.scale = (size[0], size[1], 1)
    L.assign(o, m)
    return o


def surf_line(x_range=(-60, 60), y=8.0, z=0.02, n=100, amp=1.2, period=4.0, name="surf"):
    """Foam strip at the waterline, washing up and back."""
    m = L.mat_principled(name + "_m", (0.75, 0.78, 0.8), rough=0.6, emit=(0.4, 0.42, 0.45), emit_strength=0.1)
    verts, faces = [], []
    nx = 120
    for i in range(nx + 1):
        x = x_range[0] + (x_range[1] - x_range[0]) * i / nx
        w = 0.25 + 0.2 * noise.noise(Vector((x * 0.2, 0, 0)))
        off = 0.6 * noise.noise(Vector((x * 0.08, 3, 0)))
        verts += [(x, y + off - w, z), (x, y + off + w, z)]
    for i in range(nx):
        faces.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    o = mesh_obj(name, verts, faces, mat=m)
    for f in range(1, n + 1, 4):
        o.location = (0, -amp * (0.5 + 0.5 * math.sin(2 * math.pi * f / (period * FPS))), 0)
        o.keyframe_insert("location", frame=f)
    return o


def seawall(length=80, h=1.6, top_w=0.8, y=0.0, mat=None, steps_at=(), name="seawall"):
    """Low concrete seawall running along X at y, beach side -Y. Slightly sloped face."""
    m = mat or L.mat_noise_surface(name + "_m", (0.17, 0.16, 0.15), (0.34, 0.33, 0.31), scale=2.5, bump=0.4)
    bm = bmesh.new()
    prof = [(y - 0.35, -0.3), (y, h), (y + top_w, h), (y + top_w + 0.2, h + 0.1), (y + top_w + 0.2, -0.3)]
    nx = 2
    vf = [bm.verts.new((-length / 2, py, pz)) for py, pz in prof]
    vb = [bm.verts.new((length / 2, py, pz)) for py, pz in prof]
    bm.faces.new(vf)
    bm.faces.new(list(reversed(vb)))
    k = len(prof)
    for i in range(k):
        bm.faces.new((vf[i], vf[(i + 1) % k], vb[(i + 1) % k], vb[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = L.link(bpy.data.objects.new(name, me))
    L.assign(o, m)
    # expansion joints
    jm = L.mat_principled(name + "_j", (0.06, 0.06, 0.06), rough=0.9)
    x = -length / 2 + 3
    while x < length / 2:
        j = L.prim("cube", loc=(x, y - 0.17, h / 2))
        j.scale = (0.03, 0.2, h / 2 + 0.05)
        j.rotation_euler = (math.atan2(0.35, h + 0.3), 0, 0)
        L.assign(j, jm)
        x += 4.5
    for sx in steps_at:
        for k2 in range(5):
            st = L.prim("cube", loc=(sx, y - 0.4 - k2 * 0.32, h * (1 - (k2 + 1) / 6) / 2))
            st.scale = (0.9, 0.18, h * (1 - (k2 + 1) / 6) / 2 + 0.01)
            L.assign(st, m)
    return o


def desk_lamp(loc, target, energy=60, rot_z=0.0, name="desklamp"):
    """Simple banker/arm desk lamp: base, arm, conical shade + warm spot aimed at target."""
    mt = L.mat_principled(name + "_m", (0.05, 0.06, 0.05), rough=0.35, metal=0.8)
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    base = L.prim("cyl", loc=(0, 0, 0.02), vertices=24, radius=0.12, depth=0.04)
    arm = L.prim("cyl", loc=(0, 0.0, 0.25), vertices=8, radius=0.012, depth=0.5)
    arm2 = L.prim("cyl", loc=(0, -0.14, 0.52), vertices=8, radius=0.012, depth=0.32, rot=(math.radians(60), 0, 0))
    sh = L.prim("cone", loc=(0, -0.3, 0.6), vertices=24, radius1=0.12, radius2=0.04, depth=0.16, rot=(math.radians(-35), 0, 0))
    for o in (base, arm, arm2, sh):
        L.assign(o, mt)
        o.parent = root
    sh.visible_shadow = False
    arm2.visible_shadow = False
    bulb = L.prim("sphere", loc=(0, -0.33, 0.55), radius=0.035, segments=10, ring_count=6)
    L.assign(bulb, L.mat_emission(name + "_b", (1.0, 0.8, 0.5), 20))
    bulb.parent = root
    bulb.visible_shadow = False
    bpy.context.view_layer.update()
    sp = L.spot(bulb.matrix_world.translation, (0, 0, 0), energy=energy, size_deg=80, blend=0.6, color=(1.0, 0.72, 0.42),
                name=name + "_spot", radius=0.04)
    tg = empty(name + "_tgt", target)
    aim(sp, tg)
    return root, sp


def book(loc, size=(0.13, 0.19, 0.022), cover=(0.1, 0.05, 0.035), title=None, rot_z=0.0, name="book"):
    """Small hardback: cover box + paper block; optional title text on top."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    cm = L.mat_noise_surface(name + "_c", tuple(c * 0.7 for c in cover), cover, scale=30, bump=0.1, voronoi=False, rough=0.75)
    pm = mat_paper(name + "_p", (0.7, 0.66, 0.55))
    w, h, t = size
    for z in (0.0015, t - 0.0015):
        c = L.prim("cube", loc=(0, 0, z))
        c.scale = (w / 2, h / 2, 0.0015)
        L.assign(c, cm)
        c.parent = root
    sp = L.prim("cube", loc=(-w / 2, 0, t / 2))
    sp.scale = (0.002, h / 2, t / 2)
    L.assign(sp, cm)
    sp.parent = root
    pb = L.prim("cube", loc=(0.002, 0, t / 2))
    pb.scale = (w / 2 - 0.004, h / 2 - 0.003, t / 2 - 0.002)
    L.assign(pb, pm)
    pb.parent = root
    if title:
        gm = L.mat_principled(name + "_gold", (0.6, 0.45, 0.2), rough=0.35, metal=0.8)
        tt = L.text3d(title, loc=(0, 0.02, t + 0.0003), rot=(0, 0, 0), size=0.016, extrude=0, mat=gm, name=name + "_t")
        tt.data.font = _font(F_SERIF_B) or tt.data.font
        tt.data.align_y = "CENTER"
        tt.data.space_line = 1.1
        tt.parent = root
        # decorative border
        for yy in (h / 2 - 0.012, -h / 2 + 0.012):
            bl = L.prim("cube", loc=(0, yy, t + 0.0002))
            bl.scale = (w / 2 - 0.012, 0.0012, 0.0002)
            L.assign(bl, gm)
            bl.parent = root
    return root


def suitcase(loc, size=(0.62, 0.2, 0.42), color=(0.2, 0.1, 0.05), rot_z=0.0, name="case", tag_string=False):
    """Old leather suitcase standing on its side (long axis X). Returns root."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    lm = L.mat_noise_surface(name + "_m", tuple(c * 0.6 for c in color), color, scale=18, bump=0.25, voronoi=False, rough=0.6)
    w, d, h = size
    b = L.prim("cube", loc=(0, 0, h / 2))
    b.scale = (w / 2, d / 2, h / 2)
    L.assign(b, lm)
    L.bevel(b, 0.025, 3)
    b.parent = root
    mt = L.mat_principled(name + "_metal", (0.45, 0.38, 0.25), rough=0.35, metal=0.9)
    for sx in (-1, 1):
        c = L.prim("cube", loc=(sx * w * 0.3, -d / 2 - 0.004, h * 0.85))
        c.scale = (0.025, 0.006, 0.02)
        L.assign(c, mt)
        c.parent = root
        st = L.prim("cube", loc=(sx * w * 0.3, 0, h / 2))
        st.scale = (0.022, d / 2 + 0.004, h / 2 + 0.004)
        L.assign(st, L.mat_principled(name + "_strap", tuple(c2 * 0.5 for c2 in color), rough=0.7))
        st.parent = root
    hd = L.prim("torus", loc=(0, 0, h + 0.03), major_radius=0.07, minor_radius=0.012, rot=(math.pi / 2, 0, 0))
    hd.scale = (1, 0.6, 1)
    L.assign(hd, lm)
    hd.parent = root
    if tag_string:
        # empty luggage-tag string: loop through the handle, hanging down the front; only a torn stub of the tag left
        sm = L.mat_principled(name + "_str", (0.75, 0.7, 0.58), rough=0.9, emit=(0.4, 0.37, 0.3), emit_strength=0.15)
        cu = bpy.data.curves.new(name + "_strc", "CURVE")
        cu.dimensions = "3D"
        sp = cu.splines.new("BEZIER")
        pts = [(0.02, 0.0, h + 0.06), (0.035, -d / 2 - 0.012, h - 0.02), (0.03, -d / 2 - 0.016, h - 0.12), (0.05, -d / 2 - 0.014, h - 0.2)]
        sp.bezier_points.add(len(pts) - 1)
        for bp, p in zip(sp.bezier_points, pts):
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = "AUTO"
        cu.bevel_depth = 0.0028
        so = L.link(bpy.data.objects.new(name + "_string", cu))
        so.data.materials.append(sm)
        so.parent = root
        tb = mesh_obj(name + "_stub", [(0, 0, 0), (0.022, 0, -0.01), (0.012, 0, -0.03), (-0.004, 0, -0.026)], [(0, 1, 2, 3)],
                      mat=mat_paper(name + "_tp", (0.75, 0.7, 0.55)))
        tb.location = (0.045, -d / 2 - 0.016, h - 0.2)
        tb.parent = root
    return root


def plaster_bust(loc, scale=1.0, name="bust"):
    """Featureless plaster head-and-shoulders form (no facial features)."""
    m = L.mat_noise_surface(name + "_m", (0.55, 0.53, 0.5), (0.78, 0.76, 0.72), scale=9, bump=0.08, voronoi=False, rough=0.8)
    root = empty(name, loc)
    root.scale = (scale,) * 3
    sh = L.prim("sphere", loc=(0, 0, 0.12), radius=1, segments=32, ring_count=16)
    sh.scale = (0.24, 0.13, 0.12)
    nk = L.prim("cyl", loc=(0, 0, 0.27), vertices=24, radius=0.055, depth=0.16)
    hd = L.prim("sphere", loc=(0, 0.005, 0.43), radius=1, segments=32, ring_count=16)
    hd.scale = (0.085, 0.1, 0.12)
    base = L.prim("cyl", loc=(0, 0, 0.02), vertices=32, radius=0.16, depth=0.04)
    for o in (sh, nk, hd, base):
        L.assign(o, m)
        L.smooth(o)
        o.parent = root
    return root


def tweezers(loc, rot=(0, 0, 0), name="tweezers", open_=0.01):
    root = empty(name, loc)
    root.rotation_euler = rot
    mt = L.mat_principled(name + "_m", (0.7, 0.72, 0.75), rough=0.2, metal=1.0)
    for s in (-1, 1):
        a = L.prim("cube", loc=(s * open_, 0, 0.06), rot=(0, s * 0.06, 0))
        a.scale = (0.0015, 0.004, 0.065)
        L.assign(a, mt)
        a.parent = root
    return root


def rolled_scrap(loc, length=0.06, height=0.014, rot_z=0.0, turns=2.1, name="scrap", text="Tam\u00e1m Shud"):
    """Tiny printed paper strip (text along +Y) rolled around local X by a SimpleDeform BEND modifier.
    Animate unroll with bd.angle (keyframe on the object: modifiers["curl"].angle). Returns (root, paper_obj, bend_mod)."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    pm = mat_paper(name + "_m", (0.8, 0.76, 0.64))
    ink = L.mat_principled(name + "_ink", (0.04, 0.035, 0.03), rough=0.6)
    ny = 40
    verts, faces = [], []
    for j in range(ny + 1):
        y = length * j / ny
        verts += [(-height / 2, y, 0), (height / 2, y, 0)]
    for j in range(ny):
        faces.append((2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2))
    o = mesh_obj(name + "_p", verts, faces, mat=pm)
    o.data.materials.append(ink)
    if text:
        t = L.text3d(text, loc=(0, length / 2, 0.0004), rot=(0, 0, math.pi / 2), size=height * 0.62, extrude=0, mat=ink, name=name + "_t")
        t.data.font = _font(F_SERIF) or t.data.font
        t.data.align_y = "CENTER"
        t.data.resolution_u = 4
        dg = bpy.context.evaluated_depsgraph_get()
        tm = bpy.data.meshes.new_from_object(t.evaluated_get(dg))
        tm.transform(t.matrix_world)
        bm = bmesh.new()
        bm.from_mesh(o.data)
        off = len(bm.verts)
        bm2 = bmesh.new()
        bm2.from_mesh(tm)
        # subdivide text faces along Y so they follow the bend
        vmap = {}
        for v in bm2.verts:
            vmap[v.index] = bm.verts.new(v.co)
        bm.verts.ensure_lookup_table()
        for f in bm2.faces:
            try:
                nf = bm.faces.new([vmap[v.index] for v in f.verts])
                nf.material_index = 1
            except ValueError:
                pass
        bm2.free()
        bm.to_mesh(o.data)
        bm.free()
        bpy.data.objects.remove(t)
    o.parent = root
    # rolled state as a shape key: strip wound around an axis parallel to X, starting at y=0
    r0 = length / (2 * math.pi * turns)
    o.shape_key_add(name="Basis")
    key = o.shape_key_add(name="rolled")
    for v, kv in zip(o.data.vertices, key.data):
        x, y, z = v.co
        th = y / r0
        r = r0 + 0.0005 * th / (2 * math.pi) - z
        kv.co = (x, r * math.sin(th), r0 - r * math.cos(th))
    key.value = 1.0
    bd = key
    return root, o, bd


# ============================================================================ Somerton extras

def desk(size=(3.0, 2.0), z=0.0, name="desk"):
    """Dark wood desktop (top at z)."""
    t = L.prim("cube", loc=(0, 0, z - 0.03), name=name)
    t.scale = (size[0] / 2, size[1] / 2, 0.03)
    L.apply_scale(t)
    L.assign(t, mat_wood_dark(name + "_m"))
    return t


def folded_jacket(loc, rot_z=0.0, color=(0.07, 0.07, 0.075), name="jacket", label_outline=True):
    """Folded suit jacket seen from above: body slab with lapels, collar, tie, and an empty stitched rectangle
    where the maker's label was cut out."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    cm = L.mat_noise_surface(name + "_m", tuple(c * 0.6 for c in color), color, scale=60, bump=0.15, voronoi=False, rough=0.9)
    body = L.prim("cube", loc=(0, 0, 0.025))
    body.scale = (0.24, 0.32, 0.025)
    L.assign(body, cm)
    L.bevel(body, 0.02, 3)
    body.parent = root
    lm = L.mat_noise_surface(name + "_lin", (0.16, 0.14, 0.12), (0.26, 0.23, 0.2), scale=40, bump=0.05, voronoi=False, rough=0.6)
    lin = L.prim("plane", loc=(0, 0.17, 0.0515), size=1)
    lin.scale = (0.16, 0.13, 1)
    L.assign(lin, lm)
    lin.parent = root
    for s in (-1, 1):
        lp = mesh_obj(name + f"_lap{s}", [(s * 0.005, 0.04, 0.053), (s * 0.17, 0.3, 0.053), (s * 0.06, 0.3, 0.053)], [(0, 1, 2)], mat=cm)
        lp.parent = root
    col = L.prim("cube", loc=(0, 0.31, 0.058))
    col.scale = (0.14, 0.02, 0.008)
    L.assign(col, cm)
    col.parent = root
    tm = L.mat_noise_surface(name + "_tie", (0.08, 0.03, 0.03), (0.2, 0.07, 0.06), scale=80, bump=0.1, voronoi=False, rough=0.6)
    tie = mesh_obj(name + "_tie", [(-0.018, 0.29, 0.056), (0.018, 0.29, 0.056), (0.03, -0.1, 0.056), (0.0, -0.14, 0.056), (-0.03, -0.1, 0.056)],
                   [(0, 1, 2, 3, 4)], mat=tm)
    tie.parent = root
    if label_outline:
        stm = L.mat_principled(name + "_stitch", (0.6, 0.55, 0.45), rough=0.7)
        lx, ly, w, h = 0.0, 0.2, 0.08, 0.035
        dashes = []
        for (x0, y0, x1, y1) in ((lx - w, ly - h, lx + w, ly - h), (lx + w, ly - h, lx + w, ly + h), (lx + w, ly + h, lx - w, ly + h),
                                 (lx - w, ly + h, lx - w, ly - h)):
            seg = 9
            for i in range(0, seg, 2):
                ax, ay = x0 + (x1 - x0) * i / seg, y0 + (y1 - y0) * i / seg
                bx, by = x0 + (x1 - x0) * (i + 1) / seg, y0 + (y1 - y0) * (i + 1) / seg
                dashes.append(((ax, ay), (bx, by)))
        verts, faces = [], []
        for (a, b) in dashes:
            d = Vector((b[0] - a[0], b[1] - a[1], 0))
            p = Vector((-d.y, d.x, 0)).normalized() * 0.0018
            base = len(verts)
            verts += [(a[0] + p.x, a[1] + p.y, 0.0525), (b[0] + p.x, b[1] + p.y, 0.0525), (b[0] - p.x, b[1] - p.y, 0.0525),
                      (a[0] - p.x, a[1] - p.y, 0.0525)]
            faces.append((base, base + 1, base + 2, base + 3))
        so = mesh_obj(name + "_stitches", verts, faces, mat=stm)
        so.parent = root
        pr = L.prim("plane", loc=(lx, ly, 0.0518), size=1)
        pr.scale = (w * 1.9, h * 1.8, 1)
        L.assign(pr, L.mat_principled(name + "_pale", (0.33, 0.3, 0.26), rough=0.7))
        pr.parent = root
    return root


def scissors(loc, rot_z=0.0, name="scissors"):
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    mt = L.mat_principled(name + "_m", (0.55, 0.56, 0.58), rough=0.25, metal=1.0)
    hm = L.mat_principled(name + "_h", (0.05, 0.05, 0.05), rough=0.5)
    for s in (-1, 1):
        bl = mesh_obj(name + f"_b{s}", [(0, 0, 0.004), (s * 0.01, 0.12, 0.004), (s * 0.004, 0.12, 0.004), (-s * 0.006, 0.0, 0.004)],
                      [(0, 1, 2, 3)], mat=mt)
        bl.rotation_euler = (0, 0, s * 0.12)
        bl.parent = root
        rg = L.prim("torus", loc=(s * 0.022, -0.04, 0.005), major_radius=0.018, minor_radius=0.004)
        L.assign(rg, hm)
        rg.parent = root
    return root


def luggage_shelf(x_range=(-4, 4), y=1.0, levels=(0.0, 0.9, 1.8), depth=0.7, seed=4, name="shelf", skip_slot=None):
    """Long wooden cloakroom shelving with assorted suitcases. skip_slot=(level, x) leaves a gap."""
    rnd = random.Random(seed)
    wm = L.WOOD_OLD()
    out = []
    for z in levels:
        b = L.prim("cube", loc=((x_range[0] + x_range[1]) / 2, y, z + 0.4))
        b.scale = ((x_range[1] - x_range[0]) / 2, depth / 2, 0.02)
        L.assign(b, wm)
    x = x_range[0]
    while x <= x_range[1]:
        p = L.prim("cube", loc=(x, y - depth / 2 + 0.03, (levels[-1] + 0.4) / 2 + 0.2))
        p.scale = (0.03, 0.03, (levels[-1] + 0.4) / 2 + 0.2)
        L.assign(p, wm)
        x += 2.0
    cols = [(0.17, 0.09, 0.05), (0.1, 0.07, 0.05), (0.22, 0.17, 0.11), (0.06, 0.06, 0.07), (0.25, 0.12, 0.06), (0.14, 0.12, 0.1)]
    for li, z in enumerate(levels):
        x = x_range[0] + 0.1
        while x < x_range[1] - 0.5:
            w = rnd.uniform(0.45, 0.8)
            if skip_slot and skip_slot[0] == li and abs(x + w / 2 - skip_slot[1]) < 0.6:
                x += 1.2
                continue
            hgt = rnd.uniform(0.3, 0.45)
            c = suitcase((x + w / 2, y + rnd.uniform(-0.05, 0.05), z + 0.42), size=(w, rnd.uniform(0.18, 0.26), hgt),
                         color=rnd.choice(cols), rot_z=rnd.uniform(-0.05, 0.05), name=f"{name}_c{li}_{int(x * 10)}")
            out.append(c)
            x += w + rnd.uniform(0.03, 0.15)
    return out


def test_tube(loc, glow=(0.3, 0.9, 1.0), strength=3.0, name="tube"):
    root = empty(name, loc)
    gm = L.mat_principled(name + "_glass", (0.8, 0.9, 0.95), rough=0.05)
    p = gm.node_tree.nodes["Principled BSDF"]
    if "Coat Weight" in p.inputs:
        p.inputs["Coat Weight"].default_value = 0.5
    t = L.prim("cyl", loc=(0, 0, 0.06), vertices=20, radius=0.012, depth=0.12)
    L.assign(t, gm)
    t.parent = root
    liq = L.prim("cyl", loc=(0, 0, 0.03), vertices=16, radius=0.01, depth=0.05)
    L.assign(liq, L.mat_emission(name + "_liq", glow, strength))
    liq.parent = root
    cap = L.prim("cyl", loc=(0, 0, 0.125), vertices=16, radius=0.014, depth=0.015)
    L.assign(cap, L.mat_principled(name + "_cap", (0.1, 0.4, 0.8), rough=0.4))
    cap.parent = root
    return root, liq


def work_light(loc, target, energy=2500, name="worklight"):
    """Tripod work light with a harsh white flood aimed at target."""
    root = empty(name, loc)
    mt = L.mat_principled(name + "_m", (0.12, 0.12, 0.12), rough=0.4, metal=0.6)
    for k in range(3):
        a = 2 * math.pi * k / 3
        leg = L.prim("cyl", loc=(0.25 * math.cos(a), 0.25 * math.sin(a), 0.8), vertices=6, radius=0.015, depth=1.7,
                     rot=(0.17 * math.sin(a), -0.17 * math.cos(a), 0))
        L.assign(leg, mt)
        leg.parent = root
    head = L.prim("cube", loc=(0, 0, 1.75))
    head.scale = (0.18, 0.08, 0.13)
    L.assign(head, L.mat_principled(name + "_y", (0.7, 0.5, 0.05), rough=0.5))
    head.parent = root
    head.visible_shadow = False
    lens = L.prim("plane", loc=(0, -0.085, 1.75), size=1, rot=(math.pi / 2, 0, 0))
    lens.scale = (0.15, 0.1, 1)
    L.assign(lens, L.mat_emission(name + "_lens", (1, 0.98, 0.95), 40))
    lens.parent = root
    lens.visible_shadow = False
    bpy.context.view_layer.update()
    sp = L.spot(lens.matrix_world.translation, (0, 0, 0), energy=energy, size_deg=70, blend=0.3, color=(0.95, 0.97, 1.0),
                name=name + "_spot", radius=0.1)
    tg = empty(name + "_tgt", target)
    aim(sp, tg)
    return root, sp


def tree_lines(root_pts, end_pt, mat, z=0.0, name="tree"):
    """Family-tree style orthogonal connectors (curves) in the XZ plane; animate with curve_draw."""
    out = []
    for i, p in enumerate(root_pts):
        mid_z = (p[1] + end_pt[1]) / 2
        pts = [(p[0], z, p[1]), (p[0], z, mid_z), (end_pt[0], z, mid_z), (end_pt[0], z, end_pt[1])]
        cu = bpy.data.curves.new(f"{name}{i}", "CURVE")
        cu.dimensions = "3D"
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for k, q in enumerate(pts):
            sp.points[k].co = (*q, 1)
        cu.bevel_depth = 0.012
        o = L.link(bpy.data.objects.new(f"{name}{i}", cu))
        o.data.materials.append(mat)
        out.append(o)
    return out


def curve_draw(o, f0, f1):
    cu = o.data
    cu.bevel_factor_end = 0.0
    cu.keyframe_insert("bevel_factor_end", frame=max(1, f0))
    cu.bevel_factor_end = 1.0
    cu.keyframe_insert("bevel_factor_end", frame=max(f0 + 1, f1))


def cloud_points(pts, radius=0.01, name="pts", mat=None, seed=3):
    """Tetra particles at the given world points (one mesh)."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    for p in pts:
        r = radius * rnd.uniform(0.6, 1.4)
        c = Vector(p)
        vs = [bm.verts.new(c + Vector(v) * r) for v in ((1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1))]
        for f in ((0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)):
            bm.faces.new([vs[i] for i in f])
    o = L.mesh_from_bm(name, bm)
    if mat:
        L.assign(o, mat)
    o.visible_shadow = False
    return o


def volume_puff(center, f0, n, size=2.5, density=0.25, color=(0.8, 0.84, 0.95), dur=30, name="puff"):
    """Expanding, thinning snow-dust cloud (volume sphere) for an impact."""
    o = L.prim("ico", loc=center, subdivisions=2, radius=1.0, name=name)
    m = mat_volume_anim(name + "_m", color, density)
    L.assign(o, m[0])
    dens = m[1]
    o.scale = (0.01,) * 3
    o.keyframe_insert("scale", frame=max(1, f0 - 1))
    o.scale = (size * 0.6,) * 3
    o.keyframe_insert("scale", frame=f0 + 5)
    o.scale = (size, size, size * 0.7)
    o.keyframe_insert("scale", frame=f0 + dur)
    dens.default_value = density
    dens.keyframe_insert("default_value", frame=f0 + 3)
    dens.default_value = density * 0.15
    dens.keyframe_insert("default_value", frame=min(n, f0 + dur))
    return o


def mat_volume_anim(name, color, density):
    m, n, l = L._mat(name)
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    v = n.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (*color, 1)
    v.inputs["Density"].default_value = density
    # soft spherical falloff
    tc = n.new("ShaderNodeTexCoord")
    vl = n.new("ShaderNodeVectorMath"); vl.operation = "LENGTH"
    l.new(tc.outputs["Object"], vl.inputs[0])
    mr = n.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.3
    mr.inputs["From Max"].default_value = 1.0
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    l.new(vl.outputs["Value"], mr.inputs["Value"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.0
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    m1 = n.new("ShaderNodeMath"); m1.operation = "MULTIPLY"
    l.new(mr.outputs[0], m1.inputs[0]); l.new(nz.outputs["Fac"], m1.inputs[1])
    val = n.new("ShaderNodeValue")
    val.outputs[0].default_value = density
    m2 = n.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
    l.new(m1.outputs[0], m2.inputs[0])
    l.new(val.outputs[0], m2.inputs[1])
    l.new(m2.outputs[0], v.inputs["Density"])
    l.new(v.outputs[0], n["Material Output"].inputs["Volume"])
    return m, val.outputs[0]


def smooth_obj(o):
    o.data.polygons.foreach_set("use_smooth", [True] * len(o.data.polygons))
    return o


# ============================================================================ MURDER-03 (D.B. Cooper) builders
# Stylised Boeing 727 (no livery), rain, storm cloud, lightning, parachute, money, cabin, apron, riverbank, hangar.

def _nn(n, l, kind, **inp):
    nd = n.new(kind)
    for k, v in inp.items():
        if k == "op":
            nd.operation = v
        else:
            nd.inputs[k].default_value = v
    return nd


def _mathn(n, l, op, a, b=None, val=None, clamp=False):
    m = n.new("ShaderNodeMath")
    m.operation = op
    m.use_clamp = clamp
    if isinstance(a, (int, float)):
        m.inputs[0].default_value = a
    else:
        l.new(a, m.inputs[0])
    if b is not None:
        if isinstance(b, (int, float)):
            m.inputs[1].default_value = b
        else:
            l.new(b, m.inputs[1])
    if val is not None:
        m.inputs[1].default_value = val
    return m.outputs[0]


def _band(n, l, sock, lo, hi):
    a = _mathn(n, l, "GREATER_THAN", sock, lo)
    b = _mathn(n, l, "LESS_THAN", sock, hi)
    return _mathn(n, l, "MULTIPLY", a, b)


def mat_jet_skin(name="jetskin", base=(0.045, 0.055, 0.075), stripe=(0.45, 0.03, 0.025), window=(1.0, 0.72, 0.4),
                 win_strength=6.0, stripe_z=(0.05, 0.32), win_z=(0.42, 0.72), win_x=(-10.0, 13.0), win_pitch=0.52):
    """Dark navy-grey metal fuselage with a red cheat-line (object Z band) and warm cabin window dots."""
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    p.inputs["Metallic"].default_value = 0.55
    p.inputs["Roughness"].default_value = 0.32
    tc = n.new("ShaderNodeTexCoord")
    sp = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sp.inputs[0])
    band = _band(n, l, sp.outputs["Z"], *stripe_z)
    mix = n.new("ShaderNodeMix"); mix.data_type = "RGBA"
    l.new(band, mix.inputs[0])
    mix.inputs[6].default_value = (*base, 1)
    mix.inputs[7].default_value = (*stripe, 1)
    l.new(mix.outputs[2], p.inputs["Base Color"])
    # windows
    fx = _mathn(n, l, "MULTIPLY", sp.outputs["X"], 1.0 / win_pitch)
    fr = _mathn(n, l, "FRACT", fx)
    wx = _band(n, l, fr, 0.2, 0.62)
    wz = _band(n, l, sp.outputs["Z"], *win_z)
    wr = _band(n, l, sp.outputs["X"], *win_x)
    w = _mathn(n, l, "MULTIPLY", _mathn(n, l, "MULTIPLY", wx, wz), wr)
    p.inputs["Emission Color"].default_value = (*window, 1)
    ws = _mathn(n, l, "MULTIPLY", w, win_strength)
    l.new(ws, p.inputs["Emission Strength"])
    # panel-line grime
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    rr = n.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.22
    rr.inputs["To Max"].default_value = 0.5
    l.new(nz.outputs["Fac"], rr.inputs["Value"])
    l.new(rr.outputs[0], p.inputs["Roughness"])
    return m


def _loft_x(name, stations, seg=28, mat=None):
    """Closed tube along X. stations = [(x, radius, zc, yscale)]; capped ends. Returns object."""
    bm = bmesh.new()
    rings = []
    for (x, r, zc, ys) in stations:
        ring = []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            ring.append(bm.verts.new((x, ys * r * math.cos(a), zc + r * math.sin(a))))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for k in range(seg):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % seg], rings[i + 1][(k + 1) % seg], rings[i + 1][k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = L.mesh_from_bm(name, bm)
    smooth_obj(o)
    if mat:
        L.assign(o, mat)
    return o


def _slab(name, outline_top, thick_root, thick_tip, mat=None, mirror_y=False):
    """Wing/fin slab from a planar 4-point outline (root_le, tip_le, tip_te, root_te) in 3D, thickened along `normal`.
    outline points are (x, y, z); thickness applied along +-normal of the outline plane."""
    a, b, c, d = [Vector(p) for p in outline_top]
    nrm = (b - a).cross(d - a).normalized()
    th = [thick_root, thick_tip, thick_tip, thick_root]
    verts = []
    for p, t in zip((a, b, c, d), th):
        verts.append(p + nrm * t / 2)
    for p, t in zip((a, b, c, d), th):
        verts.append(p - nrm * t / 2)
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    o = mesh_obj(name, verts, faces, mat=mat)
    bv = o.modifiers.new("bv", "BEVEL")
    bv.width = min(thick_tip, thick_root) * 0.45
    bv.segments = 2
    if mirror_y:
        mm = o.modifiers.new("mir", "MIRROR")
        mm.use_axis = (False, True, False)
        mm.use_bisect_axis = (False, False, False)
    return o


def jet727(name="jet", loc=(0, 0, 0), rot_z=0.0, stair_open=0.0, skin=None, windows=True, door_open=False, vane=False,
           stair_light=True, nav_lights=True):
    """Stylised Boeing 727 (no livery). Nose at +X, tail at -X, belly -Z. Fuselage r 1.9, ~41 m long.
    Ventral aft airstair hinged at x=-14.3 under the belly: parts['stair_hinge'].rotation_euler.y = 0 (closed)
    .. -35 deg (open, aft end down). Returns dict of parts."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    P = {"root": root}
    skin = skin or mat_jet_skin(name + "_skin", win_strength=6.0 if windows else 0.0)
    trim = L.mat_principled(name + "_trim", (0.05, 0.055, 0.065), rough=0.35, metal=0.6)
    dark = L.mat_principled(name + "_dark", (0.008, 0.008, 0.01), rough=0.5)
    light_metal = L.mat_principled(name + "_lm", (0.3, 0.31, 0.33), rough=0.3, metal=0.9)
    st = [(20.6, 0.02, -0.45, 1), (20.3, 0.45, -0.4, 1), (19.6, 0.95, -0.3, 1), (18.5, 1.4, -0.18, 1), (17.0, 1.75, -0.06, 1),
          (15.0, 1.9, 0, 1), (-11.5, 1.9, 0, 1), (-13.5, 1.84, 0.08, 1), (-15.5, 1.62, 0.3, 1), (-17.5, 1.3, 0.62, 1),
          (-19.3, 0.9, 0.95, 1), (-20.6, 0.55, 1.15, 1), (-21.2, 0.3, 1.2, 1)]
    fus = _loft_x(name + "_fus", st, seg=32, mat=skin)
    fus.parent = root
    P["fuselage"] = fus
    # cockpit windows (dark band)
    cw = L.prim("cube", loc=(19.0, 0, 0.45))
    cw.scale = (0.55, 0.95, 0.16)
    cw.rotation_euler = (0, math.radians(-28), 0)
    L.assign(cw, L.mat_principled(name + "_cw", (0.01, 0.012, 0.016), rough=0.05, metal=0.3, emit=(0.25, 0.35, 0.5), emit_strength=0.4))
    cw.parent = root
    # wings (low, swept) + mirror
    wing = _slab(name + "_wing", [(3.5, 1.4, -1.25), (-6.4, 16.5, -0.55), (-8.6, 16.5, -0.55), (-4.5, 1.4, -1.25)], 0.55, 0.14,
                 mat=trim, mirror_y=True)
    wing.parent = root
    P["wing"] = wing
    # wing tip nav lights
    if nav_lights:
        for yy, col in ((16.5, (0.1, 1.0, 0.2)), (-16.5, (1.0, 0.05, 0.03))):
            b = L.prim("sphere", loc=(-7.4, yy, -0.55), radius=0.12, segments=8, ring_count=6)
            L.assign(b, L.mat_emission(name + f"_nav{yy}", col, 40))
            b.parent = root
            b.visible_shadow = False
    # fin (swept) + T-tail stabiliser
    fin = _slab(name + "_fin", [(-12.0, 0, 1.6), (-17.3, 0, 8.6), (-20.4, 0, 8.6), (-20.2, 0, 1.4)], 0.42, 0.22, mat=skin)
    # fix fin orientation: built in XZ plane, thickness along Y automatically
    fin.parent = root
    P["fin"] = fin
    stab = _slab(name + "_stab", [(-16.6, 0.0, 8.75), (-20.4, 5.8, 9.1), (-21.9, 5.8, 9.1), (-20.6, 0.0, 8.75)], 0.32, 0.12,
                 mat=trim, mirror_y=True)
    stab.parent = root
    # engines: two side pods + centre engine (S-duct intake on top, exhaust in the tail cone)
    for sy in (-1, 1):
        pod = _loft_x(name + f"_pod{sy}", [(-12.4, 0.62, 0, 1), (-12.6, 0.78, 0, 1), (-14.5, 0.82, 0, 1), (-16.8, 0.7, 0, 1),
                                           (-17.6, 0.55, 0, 1)], seg=20, mat=trim)
        pod.location = (0, sy * 2.75, 1.05)
        pod.parent = root
        pyl = L.prim("cube", loc=(-15.0, sy * 1.95, 1.0))
        pyl.scale = (1.3, 0.5, 0.12)
        L.assign(pyl, trim)
        pyl.parent = root
        ink = L.prim("cyl", loc=(-12.42, sy * 2.75, 1.05), vertices=20, radius=0.6, depth=0.06, rot=(0, math.pi / 2, 0))
        L.assign(ink, dark)
        ink.parent = root
        ex = L.prim("cyl", loc=(-17.62, sy * 2.75, 1.05), vertices=20, radius=0.46, depth=0.06, rot=(0, math.pi / 2, 0))
        L.assign(ex, dark)
        ex.parent = root
    duct = _loft_x(name + "_duct", [(-10.6, 0.5, 0, 1.15), (-10.8, 0.7, 0, 1.15), (-12.5, 0.75, 0, 1.1), (-13.5, 0.6, -0.2, 1.0)],
                   seg=20, mat=skin)
    duct.location = (0, 0, 2.05)
    duct.parent = root
    di = L.prim("cyl", loc=(-10.62, 0, 2.05), vertices=20, radius=0.55, depth=0.05, rot=(0, math.pi / 2, 0))
    di.scale = (1, 1.12, 1)
    L.assign(di, dark)
    di.parent = root
    cex = L.prim("cyl", loc=(-21.25, 0, 1.2), vertices=20, radius=0.32, depth=0.12, rot=(0, math.pi / 2, 0))
    L.assign(cex, dark)
    cex.parent = root
    # --- ventral aft airstair -------------------------------------------------------------
    hx, hz = -14.0, -1.78
    hinge = empty(name + "_stair_hinge", (hx, 0, hz), parent=root)
    base_ang = math.radians(16)   # closed: follows the rising belly line of the tail cone
    hinge["base"] = base_ang
    hinge.rotation_euler = (0, base_ang - math.radians(stair_open), 0)
    sm_ = L.mat_principled(name + "_stairm", (0.16, 0.165, 0.17), rough=0.4, metal=0.8)
    ramp = L.prim("cube", loc=(-2.85, 0, -0.07))
    ramp.scale = (2.85, 0.48, 0.06)
    L.assign(ramp, skin)
    ramp.parent = hinge
    for k in range(11):
        s = L.prim("cube", loc=(-0.35 - k * 0.5, 0, 0.03))
        s.scale = (0.13, 0.42, 0.05)
        L.assign(s, sm_)
        s.parent = hinge
    for sy in (-0.47, 0.47):
        rail = L.prim("cyl", loc=(-2.85, sy, 0.45), vertices=6, radius=0.025, depth=5.6, rot=(0, math.pi / 2, 0))
        L.assign(rail, light_metal)
        rail.parent = hinge
        for k in range(5):
            post = L.prim("cyl", loc=(-0.3 - k * 1.3, sy, 0.22), vertices=6, radius=0.02, depth=0.46)
            L.assign(post, light_metal)
            post.parent = hinge
    P["stair_hinge"] = hinge
    P["stair_mat"] = sm_
    # glowing opening in the belly (covered by the closed stair)
    gl = L.mat_emission(name + "_open", (1.0, 0.66, 0.32), 9.0)
    op = L.prim("plane", loc=(0, 0, 0), size=1)
    op.scale = (2.8, 0.45, 1)
    op.parent = hinge
    op.location = (-2.85, 0, 0.004)
    L.assign(op, gl)
    op.visible_shadow = False
    P["opening"] = op
    # the opening plane must stay with the fuselage, not rotate with the stair: re-parent to root at closed pose
    bpy.context.view_layer.update()
    hinge_rot = hinge.rotation_euler.copy()
    hinge.rotation_euler = (0, base_ang, 0)
    bpy.context.view_layer.update()
    mw = op.matrix_world.copy()
    op.parent = root
    op.matrix_world = mw
    hinge.rotation_euler = hinge_rot
    if stair_light:
        sp = L.spot((-15.5, 0, -1.4), (0, math.radians(200), 0), energy=900, size_deg=95, blend=0.9, color=(1.0, 0.62, 0.3),
                    name=name + "_spill", radius=0.3)
        sp.parent = root
        pt = L.point((-16.0, 0, -1.6), energy=180, color=(1.0, 0.6, 0.3), radius=0.6, name=name + "_spillpt")
        pt.parent = root
        P["spill"] = sp
        P["spill_pt"] = pt
    if door_open:
        d = L.prim("plane", loc=(15.2, -1.93, 0.25), size=1, rot=(math.pi / 2, 0, 0))
        d.scale = (0.48, 0.95, 1)
        L.assign(d, L.mat_emission(name + "_door", (1.0, 0.75, 0.45), 6))
        d.parent = root
        P["door"] = d
    if vane:
        vh = empty(name + "_vane_hinge", (hx + 0.55, -0.75, hz + 0.02), parent=root)
        pad = L.prim("cube", loc=(0, 0, -0.26))
        pad.scale = (0.05, 0.16, 0.26)
        vm = L.mat_principled(name + "_vanem", (0.55, 0.56, 0.58), rough=0.3, metal=0.9)
        L.assign(pad, vm)
        pad.parent = vh
        bk = L.prim("cube", loc=(hx + 0.55, -0.75, hz + 0.06))
        bk.scale = (0.12, 0.2, 0.05)
        L.assign(bk, trim)
        bk.parent = root
        P["vane_hinge"] = vh
        P["vane"] = pad
        P["vane_mat"] = vm
    if nav_lights:
        bc = L.prim("sphere", loc=(-1.0, 0, 1.95), radius=0.14, segments=8, ring_count=6)
        bm_ = L.mat_emission(name + "_beacon", (1.0, 0.05, 0.03), 0.0)
        L.assign(bc, bm_)
        bc.parent = root
        P["beacon_mat"] = bm_
    return P


def stair_anim(P, keys):
    """keys = [(frame, open_deg)] (0 closed .. 35 fully open)."""
    h = P["stair_hinge"]
    for f, deg in keys:
        h.rotation_euler = (0, h["base"] - math.radians(deg), 0)
        h.keyframe_insert("rotation_euler", frame=f)


def beacon_blink(P, n, every=24, on=3, strength=60):
    """Red anti-collision beacon blinking."""
    m = P.get("beacon_mat")
    if not m:
        return
    s = [nd for nd in m.node_tree.nodes if nd.type == "EMISSION"][0].inputs[1]
    for f0 in range(1, n + 1, every):
        for f, v in ((f0, strength), (f0 + on, 0.0)):
            s.default_value = v
            s.keyframe_insert("default_value", frame=f)
    for fc in L._fcurves(m.node_tree.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"


def rain(center, size, vel, n, count=1500, length=0.5, width=0.006, period=10, seed=5, name="rain", color=(0.62, 0.68, 0.8),
         emit=0.5, cam=None, clear=1.2):
    """Seamless looping rain streaks. Streaks are thin prisms aligned with `vel` (m/s, relative to the camera).
    The cloud is periodic along the velocity axis and loops every `period` frames (CYCLES modifier), so streaks can
    move fast without padding the volume. `size` = (along-velocity, side, side) extents of the covered region."""
    rnd = random.Random(seed)
    u = Vector(vel).normalized()
    tmp = Vector((0, 0, 1)) if abs(u.z) < 0.9 else Vector((1, 0, 0))
    v = u.cross(tmp).normalized()
    w = u.cross(v).normalized()
    D = Vector(vel).length * period / FPS
    K = int(math.ceil(size[0] / D)) + 1
    per = max(1, int(count / K))
    c = Vector(center)
    camp = Vector(cam) if cam else None
    bm = bmesh.new()
    base = []
    for i in range(per):
        uu = -size[0] / 2 + rnd.uniform(0, D)
        vv = rnd.uniform(-0.5, 0.5) * size[1]
        ww = rnd.uniform(-0.5, 0.5) * size[2]
        base.append((uu, vv, ww, length * rnd.uniform(0.6, 1.3)))
    for j in range(K):
        for (uu, vv, ww, ln) in base:
            p = c + u * (uu + j * D - D) + v * vv + w * ww
            if camp is not None and (p - camp).length < clear:
                continue
            q = p + u * ln
            r = width
            a0 = [p + (v * math.cos(t) + w * math.sin(t)) * r for t in (0, 2.094, 4.189)]
            a1 = [q + (v * math.cos(t) + w * math.sin(t)) * r * 0.3 for t in (0, 2.094, 4.189)]
            vs0 = [bm.verts.new(x) for x in a0]
            vs1 = [bm.verts.new(x) for x in a1]
            for k in range(3):
                bm.faces.new((vs0[k], vs0[(k + 1) % 3], vs1[(k + 1) % 3], vs1[k]))
    o = L.mesh_from_bm(name, bm)
    L.assign(o, L.mat_principled(name + "_m", color, rough=0.2, emit=color, emit_strength=emit))
    o.visible_shadow = False
    o.location = (0, 0, 0)
    o.keyframe_insert("location", frame=1)
    o.location = u * D
    o.keyframe_insert("location", frame=1 + period)
    L.linear_fcurves(o)
    for fc in L._fcurves(o.animation_data.action):
        fc.modifiers.new("CYCLES")
    return o


def cloud_volume(center, size, density=0.6, scale=0.8, color=(0.32, 0.36, 0.46), contrast=(0.42, 0.7), drift=(0, 0, 0), n=100,
                 anisotropy=0.3, falloff=True, name="cloud", emit=None, emit_strength=0.0):
    """Clumpy storm-cloud volume (noise density). drift = texture drift (m/s) so clouds stream past."""
    o = L.prim("cube", loc=center, name=name)
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    m, nn, l = L._mat(name + "_m")
    for nd in list(nn):
        if nd.type == "BSDF_PRINCIPLED":
            nn.remove(nd)
    v = nn.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (*color, 1)
    v.inputs["Anisotropy"].default_value = anisotropy
    if emit:
        v.inputs["Emission Color"].default_value = (*emit, 1)
        v.inputs["Emission Strength"].default_value = emit_strength
    tc = nn.new("ShaderNodeTexCoord")
    mp = nn.new("ShaderNodeMapping")
    l.new(tc.outputs["Generated"], mp.inputs["Vector"])
    mp.inputs["Scale"].default_value = (size[0] * scale / 10, size[1] * scale / 10, size[2] * scale / 10)
    nz = nn.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = 5
    nz.inputs["Roughness"].default_value = 0.6
    l.new(mp.outputs[0], nz.inputs["Vector"])
    if any(drift):
        mp.inputs["Location"].default_value = (0, 0, 0)
        mp.inputs["Location"].keyframe_insert("default_value", frame=1)
        mp.inputs["Location"].default_value = tuple(-drift[i] * n / FPS * scale / 10 * size[i] / size[i] for i in range(3))
        mp.inputs["Location"].keyframe_insert("default_value", frame=n)
        for fc in L._fcurves(m.node_tree.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    ramp = nn.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = contrast[0]
    ramp.inputs["From Max"].default_value = contrast[1]
    l.new(nz.outputs["Fac"], ramp.inputs["Value"])
    dens = ramp.outputs[0]
    if falloff:
        sp = nn.new("ShaderNodeSeparateXYZ")
        l.new(tc.outputs["Generated"], sp.inputs[0])
        fz = _mathn(nn, l, "MULTIPLY", _mathn(nn, l, "SINE", _mathn(nn, l, "MULTIPLY", sp.outputs["Z"], math.pi)), 1.0)
        fx = _mathn(nn, l, "SINE", _mathn(nn, l, "MULTIPLY", sp.outputs["X"], math.pi))
        fy = _mathn(nn, l, "SINE", _mathn(nn, l, "MULTIPLY", sp.outputs["Y"], math.pi))
        f = _mathn(nn, l, "MULTIPLY", _mathn(nn, l, "MULTIPLY", fz, fx), fy)
        f = _mathn(nn, l, "POWER", f, 0.35)
        dens = _mathn(nn, l, "MULTIPLY", dens, f)
    d2 = _mathn(nn, l, "MULTIPLY", dens, density)
    l.new(d2, v.inputs["Density"])
    l.new(v.outputs[0], nn["Material Output"].inputs["Volume"])
    L.assign(o, m)
    o.visible_shadow = False
    return o


def lightning(n, flashes, rot=(math.radians(35), 0, math.radians(30)), energy=12.0, color=(0.7, 0.78, 1.0), name="lightning",
              world_bg=None, world_base=1.0, world_peak=3.0):
    """Sun light that is dark except for double-flash strobes at the given frames."""
    s = L.sun(rot=rot, energy=0.0, color=color, angle=8.0, name=name)
    d = s.data
    def kk(f, v):
        d.energy = v
        d.keyframe_insert("energy", frame=max(1, f))
        if world_bg is not None:
            world_bg.inputs[1].default_value = world_base + (world_peak - world_base) * (v / energy)
            world_bg.inputs[1].keyframe_insert("default_value", frame=max(1, f))
    kk(1, 0.0)
    for f in flashes:
        kk(f - 1, 0.0)
        kk(f, energy)
        kk(f + 1, energy * 0.25)
        kk(f + 2, energy * 0.9)
        kk(f + 5, 0.0)
    for fc in L._fcurves(d.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    return s


def storm_sky(zen=(0.004, 0.006, 0.012), hor=(0.03, 0.038, 0.06), strength=1.0):
    """Starless dark storm gradient (night_sky without stars). Returns the Background node (for lightning)."""
    return night_sky(zen=zen, hor=hor, stars=0.0, strength=strength)


def parachute(loc=(0, 0, 0), radius=3.2, line_len=5.0, color=(0.78, 0.75, 0.66), stripe=(0.55, 0.12, 0.06), name="chute"):
    """Round canopy (half-sphere with gore stripes) + suspension lines converging below. Root at the canopy centre;
    the jumper hangs at (0,0,-line_len). Returns (root, canopy)."""
    root = empty(name, loc)
    can = L.prim("sphere", loc=(0, 0, 0), radius=radius, segments=24, ring_count=12, name=name + "_canopy")
    bpy.context.view_layer.objects.active = can
    me = can.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < radius * 0.18], context="VERTS")
    for v in bm.verts:
        v.co.z -= radius * 0.18
        v.co.z *= 0.8
    bm.to_mesh(me)
    bm.free()
    smooth_obj(can)
    solidify(can, 0.03)
    m, nn, l = L._mat(name + "_m")
    p = nn["Principled BSDF"]
    tc = nn.new("ShaderNodeTexCoord")
    sp = nn.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sp.inputs[0])
    at = nn.new("ShaderNodeMath"); at.operation = "ARCTAN2"
    l.new(sp.outputs["Y"], at.inputs[0]); l.new(sp.outputs["X"], at.inputs[1])
    g = _mathn(nn, l, "FRACT", _mathn(nn, l, "MULTIPLY", at.outputs[0], 6 / (2 * math.pi)))
    gt = _mathn(nn, l, "GREATER_THAN", g, 0.5)
    mix = nn.new("ShaderNodeMix"); mix.data_type = "RGBA"
    l.new(gt, mix.inputs[0])
    mix.inputs[6].default_value = (*color, 1)
    mix.inputs[7].default_value = (*stripe, 1)
    l.new(mix.outputs[2], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.8
    p.inputs["Subsurface Weight"].default_value = 0.0
    L.assign(can, m)
    can.parent = root
    lm = L.mat_principled(name + "_lines", (0.5, 0.5, 0.48), rough=0.8)
    rim_z = 0.0
    for k in range(10):
        a = 2 * math.pi * k / 10
        p0 = Vector((radius * 0.98 * math.cos(a), radius * 0.98 * math.sin(a), rim_z))
        p1 = Vector((0, 0, -line_len))
        mid = (p0 + p1) / 2
        dv = p1 - p0
        cy = L.prim("cyl", loc=mid, vertices=4, radius=0.012, depth=dv.length)
        cy.rotation_euler = dv.to_track_quat("Z", "Y").to_euler()
        L.assign(cy, lm)
        cy.parent = root
        cy.visible_shadow = False
    return root, can


def mat_bill(name="bill", c=(0.2, 0.3, 0.2), rot=0.0):
    """Generic green paper money (no currency artwork): pale border + darker centre field via box coords."""
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    sp = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sp.inputs[0])
    bx = _band(n, l, sp.outputs["X"], 0.08, 0.92)
    by = _band(n, l, sp.outputs["Y"], 0.12, 0.88)
    f = _mathn(n, l, "MULTIPLY", bx, by)
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 40
    l.new(tc.outputs["Generated"], nz.inputs["Vector"])
    mix = n.new("ShaderNodeMix"); mix.data_type = "RGBA"
    l.new(f, mix.inputs[0])
    mix.inputs[6].default_value = (c[0] * 2.2, c[1] * 2.0, c[2] * 1.9, 1)
    mix.inputs[7].default_value = (*c, 1)
    l.new(mix.outputs[2], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.85
    return m


def bill_brick(loc, rot_z=0.0, size=(0.156, 0.066, 0.05), band=True, name="brick", mat=None, rot_x=0.0):
    """Banded stack of generic bills: box + paper band."""
    o = L.prim("cube", loc=loc, name=name)
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.rotation_euler = (rot_x, 0, rot_z)
    L.assign(o, mat or mat_bill(name + "_m"))
    bv = o.modifiers.new("bv", "BEVEL"); bv.width = 0.004; bv.segments = 2
    if band:
        b = L.prim("cube", loc=(0, 0, 0))
        b.scale = (0.12, 1.04, 1.06)
        L.assign(b, L.mat_principled(name + "_band", (0.75, 0.68, 0.5), rough=0.8))
        b.parent = o
    return o


def loose_bills(center, count, n, area=(2.0, 2.0, 2.0), size=(0.156, 0.066), vel=(0, 0, 3.0), spin=6.0, seed=4, name="bills",
                mat=None):
    """Individual bills fluttering (each a plane with tumbling keys). vel = drift relative to camera (m/s)."""
    rnd = random.Random(seed)
    m = mat or mat_bill(name + "_m")
    out = []
    for i in range(count):
        p = Vector((center[0] + rnd.uniform(-0.5, 0.5) * area[0], center[1] + rnd.uniform(-0.5, 0.5) * area[1],
                    center[2] + rnd.uniform(-0.5, 0.5) * area[2]))
        b = L.prim("plane", loc=p, size=1, name=f"{name}{i}")
        b.scale = (size[0], size[1], 1)
        L.assign(b, m)
        b.visible_shadow = False
        r0 = Vector((rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0, 6)))
        w = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * spin
        vv = Vector(vel) + Vector((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6)))
        for f in (1, n):
            t = (f - 1) / FPS
            b.location = p + vv * t
            b.rotation_euler = tuple(r0[k] + w[k] * t for k in range(3))
            b.keyframe_insert("location", frame=f)
            b.keyframe_insert("rotation_euler", frame=f)
        set_interp(b, "LINEAR")
        out.append(b)
    return out


def rounded_box(loc, size, color, rough=0.8, bevel=0.3, name="rbox", mat=None, rot=(0, 0, 0)):
    o = L.prim("cube", loc=loc, name=name)
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.rotation_euler = rot
    L.apply_scale(o)
    bv = o.modifiers.new("bv", "BEVEL")
    bv.width = min(size) * bevel
    bv.segments = 4
    L.assign(o, mat or L.mat_noise_surface(name + "_m", tuple(c * 0.75 for c in color), color, scale=25, bump=0.25,
                                            voronoi=False, rough=rough))
    smooth_obj(o)
    return o


def parachute_pack(loc, color=(0.18, 0.2, 0.1), rot_z=0.0, name="pack"):
    """Rounded canvas parachute pack with two harness straps and a buckle. Returns root."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    b = rounded_box((0, 0, 0.11), (0.46, 0.34, 0.2), color, bevel=0.25, name=name + "_b")
    b.parent = root
    sm_ = L.mat_principled(name + "_s", (0.05, 0.05, 0.045), rough=0.7)
    for x in (-0.12, 0.12):
        s = L.prim("cube", loc=(x, 0, 0.11))
        s.scale = (0.025, 0.18, 0.105)
        L.assign(s, sm_)
        s.parent = root
    bk = L.prim("cube", loc=(0, -0.171, 0.12))
    bk.scale = (0.05, 0.01, 0.035)
    L.assign(bk, L.mat_principled(name + "_bk", (0.6, 0.6, 0.6), rough=0.3, metal=1.0))
    bk.parent = root
    return root


def money_bag(loc, color=(0.42, 0.36, 0.22), name="bag"):
    """Khaki canvas bag with drawstring neck. Returns root."""
    root = empty(name, loc)
    b = L.prim("sphere", loc=(0, 0, 0), radius=0.2, segments=16, ring_count=10, name=name + "_b")
    b.scale = (1.0, 0.7, 1.15)
    L.add_displace(b, strength=0.03, scale=0.25, name=name + "_d")
    L.assign(b, L.mat_noise_surface(name + "_m", tuple(c * 0.7 for c in color), color, scale=40, bump=0.4, voronoi=False))
    smooth_obj(b)
    b.parent = root
    nk = L.prim("cone", loc=(0, 0, 0.26), vertices=12, radius1=0.08, radius2=0.03, depth=0.14)
    L.assign(nk, b.data.materials[0])
    nk.parent = root
    t = L.prim("torus", loc=(0, 0, 0.24), major_radius=0.06, minor_radius=0.008)
    L.assign(t, L.mat_principled(name + "_cord", (0.15, 0.12, 0.08), rough=0.8))
    t.parent = root
    return root


def cabin_727(length=16.0, rows=12, pitch=0.86, seat_cols=((0.95, 0.7, 0.45), (-0.45, -0.7, -0.95)), name="cabin",
              seat_a=(0.36, 0.14, 0.04), seat_b=(0.2, 0.08, 0.03), window_col=(0.25, 0.35, 0.55), light=1.0):
    """1970s narrow-body cabin interior along X (front +X, rear -X). Floor z=0, aisle at y in (-0.25,0.25).
    Seats: rows at x = -k*pitch. Returns dict (incl. 'row_x')."""
    out = {}
    wall = L.mat_principled(name + "_wall", (0.42, 0.38, 0.3), rough=0.7)
    tube = _loft_x(name + "_tube", [(length / 2, 1.85, 1.05, 1), (-length / 2, 1.85, 1.05, 1)], seg=40, mat=wall)
    for p in tube.data.polygons:
        p.flip()
    tube.data.update()
    fl = L.prim("cube", loc=(0, 0, -0.05))
    fl.scale = (length / 2, 1.8, 0.05)
    L.assign(fl, L.mat_noise_surface(name + "_carpet", (0.06, 0.035, 0.02), (0.13, 0.07, 0.035), scale=60, bump=0.2, voronoi=False))
    ais = L.prim("plane", loc=(0, 0, 0.002), size=1)
    ais.scale = (length, 0.5, 1)
    L.assign(ais, L.mat_noise_surface(name + "_aisle", (0.12, 0.05, 0.02), (0.22, 0.09, 0.03), scale=50, bump=0.1, voronoi=False))
    # overhead bins
    binm = L.mat_principled(name + "_bin", (0.55, 0.5, 0.4), rough=0.5)
    for sy in (-1, 1):
        b = L.prim("cube", loc=(0, sy * 1.25, 2.02))
        b.scale = (length / 2, 0.38, 0.17)
        b.rotation_euler = (sy * 0.35, 0, 0)
        L.assign(b, binm)
    strip = L.prim("plane", loc=(0, 0, 2.38), size=1)
    strip.scale = (length * 0.95, 0.18, 1)
    strip.rotation_euler = (math.pi, 0, 0)
    L.assign(strip, L.mat_emission(name + "_strip", (1.0, 0.82, 0.58), 3.0 * light))
    strip.visible_shadow = False
    sa = L.mat_noise_surface(name + "_sa", tuple(c * 0.7 for c in seat_a), seat_a, scale=30, bump=0.3, voronoi=False)
    sb = L.mat_noise_surface(name + "_sb", tuple(c * 0.7 for c in seat_b), seat_b, scale=30, bump=0.3, voronoi=False)
    wm = L.mat_emission(name + "_win", window_col, 1.2)
    row_x = []
    for k in range(rows):
        x = length / 2 - 1.6 - k * pitch
        row_x.append(x)
        for side in seat_cols:
            for j, y in enumerate(side):
                m = sa if (k + j) % 2 == 0 else sb
                cu = rounded_box((x, y, 0.46), (0.46, 0.44, 0.13), seat_a, bevel=0.3, name=f"{name}_c{k}_{j}_{y}", mat=m)
                bk = rounded_box((x - 0.22, y, 0.82), (0.11, 0.44, 0.66), seat_a, bevel=0.3, name=f"{name}_b{k}_{j}_{y}", mat=m,
                                 rot=(0, math.radians(-8), 0))
                hr = rounded_box((x - 0.25, y, 1.2), (0.12, 0.3, 0.14), seat_a, bevel=0.3, name=f"{name}_h{k}_{j}_{y}",
                                 mat=binm)
        for sy in (-1, 1):
            w = L.prim("cyl", loc=(x + 0.1, sy * 1.74, 1.22), vertices=16, radius=0.15, depth=0.06, rot=(math.pi / 2, 0, 0))
            w.scale = (0.82, 1.15, 1)
            L.assign(w, wm)
            w.visible_shadow = False
    # warm overhead pools
    for k in range(0, rows, 3):
        L.point((length / 2 - 1.6 - k * pitch, 0, 2.1), energy=60 * light, color=(1.0, 0.78, 0.52), radius=0.3, name=f"{name}_pl{k}")
    out.update(row_x=row_x, tube=tube, wall=wall)
    return out


def mat_wet_apron(name="apron"):
    """Wet tarmac: very dark, low roughness with rougher dry patches (puddle reflections)."""
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.12; nz.inputs["Detail"].default_value = 6
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    rr = n.new("ShaderNodeMapRange")
    rr.inputs["From Min"].default_value = 0.45; rr.inputs["From Max"].default_value = 0.6
    rr.inputs["To Min"].default_value = 0.03; rr.inputs["To Max"].default_value = 0.45
    l.new(nz.outputs["Fac"], rr.inputs["Value"])
    l.new(rr.outputs[0], p.inputs["Roughness"])
    n2 = n.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 4.0
    l.new(tc.outputs["Object"], n2.inputs["Vector"])
    cr = n.new("ShaderNodeMapRange")
    cr.inputs["To Min"].default_value = 0.012; cr.inputs["To Max"].default_value = 0.04
    l.new(n2.outputs["Fac"], cr.inputs["Value"])
    cc = n.new("ShaderNodeCombineXYZ")
    for i in range(3):
        l.new(cr.outputs[0], cc.inputs[i])
    l.new(cc.outputs[0], p.inputs["Base Color"])
    return m


def flood_mast(loc, target, height=14.0, energy=60000, color=(1.0, 0.62, 0.28), size_deg=60, name="mast"):
    """Apron floodlight mast: pole + glowing head + sodium spot aimed at target."""
    root = empty(name, loc)
    pm = L.mat_principled(name + "_m", (0.12, 0.12, 0.13), rough=0.5, metal=0.6)
    pole = L.prim("cyl", loc=(0, 0, height / 2), vertices=8, radius=0.15, depth=height)
    L.assign(pole, pm)
    pole.parent = root
    head = L.prim("cube", loc=(0, 0, height + 0.2))
    head.scale = (0.9, 0.3, 0.3)
    L.assign(head, L.mat_emission(name + "_h", color, 25))
    head.parent = root
    head.visible_shadow = False
    sp = L.spot((loc[0], loc[1], loc[2] + height), (0, 0, 0), energy=energy, size_deg=size_deg, blend=0.6, color=color,
                name=name + "_spot", radius=0.4)
    tg = empty(name + "_tgt", target)
    aim(sp, tg)
    return root, sp


def boarding_stairs(loc, rot_z=0.0, height=3.0, length=4.5, width=1.2, name="bstairs"):
    """Mobile boarding stair truck: stepped incline from ground (local -X end) up to +X end at `height`."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_principled(name + "_m", (0.5, 0.5, 0.48), rough=0.5, metal=0.6)
    steps = int(height / 0.2)
    for k in range(steps):
        s = L.prim("cube", loc=(-length / 2 + (k + 0.5) * length / steps, 0, (k + 0.5) * height / steps))
        s.scale = (length / steps / 2, width / 2, 0.03)
        L.assign(s, m)
        s.parent = root
    ang = math.atan2(height, length)
    for sy in (-1, 1):
        r = L.prim("cube", loc=(0, sy * width / 2, height / 2 + 0.5))
        r.scale = (math.hypot(length, height) / 2, 0.03, 0.03)
        r.rotation_euler = (0, -ang, 0)
        L.assign(r, m)
        r.parent = root
        side = L.prim("cube", loc=(0, sy * width / 2, height / 2 - 0.2))
        side.scale = (math.hypot(length, height) / 2, 0.02, 0.25)
        side.rotation_euler = (0, -ang, 0)
        L.assign(side, m)
        side.parent = root
    plat = L.prim("cube", loc=(length / 2 + 0.4, 0, height))
    plat.scale = (0.45, width / 2, 0.05)
    L.assign(plat, m)
    plat.parent = root
    return root


def mat_sand(name="sand", c1=(0.26, 0.22, 0.16), c2=(0.48, 0.42, 0.32), wet=False, ripple=True):
    m = L.mat_noise_surface(name, c1, c2, scale=18, bump=0.25, voronoi=False, rough=0.55 if wet else 0.9)
    return m


def riverbank(x=(-40, 40), y=(-30, 6), res=0.25, water_y=4.0, seed=3, ripple=0.03, name="bank", sand=None):
    """Sandy bar sloping gently into a flat river at +Y (water surface z=0). Returns (hfun, ground, water)."""
    def h(px, py):
        base = (water_y - py) * 0.035 - 0.05
        mac = 0.25 * noise.noise(Vector((px * 0.05, py * 0.05, seed)))
        rip = ripple * math.sin(px * 3.2 + 1.3 * noise.noise(Vector((px * 0.3, py * 0.3, seed + 4))) * 4 + py * 0.6)
        return base + mac + rip
    nx = int((x[1] - x[0]) / res) + 1
    ny = int((y[1] - y[0]) / res) + 1
    g = heightfield(name, x[0], x[1], y[0], y[1], nx, ny, h, mat=sand or mat_sand(name + "_m"))
    w = sea(size=(300, 200), loc=(0, water_y + 100, 0.0), color=(0.05, 0.06, 0.065), n=150, speed=(0.15, 0.5), name=name + "_river")
    return h, g, w


def driftwood(loc, length=2.5, r=0.12, rot=(0, 0, 0), name="log", seed=1):
    o = L.prim("cyl", loc=loc, vertices=10, radius=r, depth=length, rot=rot, name=name)
    L.add_displace(o, strength=0.03, scale=0.3, name=name + "_d")
    L.assign(o, L.mat_noise_surface(name + "_m", (0.18, 0.16, 0.13), (0.36, 0.33, 0.28), scale=12, bump=0.5, voronoi=False))
    return o


def rotten_bundle(loc, rot_z=0.0, size=(0.156, 0.066, 0.035), seed=1, name="bundle"):
    """Weathered, swollen packet of generic bills (dark mouldy edges) with a perished rubber band."""
    o = L.prim("cube", loc=loc, name=name)
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.rotation_euler = (0, 0, rot_z)
    L.apply_scale(o)
    sub = o.modifiers.new("sub", "SUBSURF"); sub.levels = sub.render_levels = 2; sub.subdivision_type = "SIMPLE"
    L.add_displace(o, strength=0.006, scale=0.03, name=name + "_d")
    m, n, l = L._mat(name + "_m")
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; nz.inputs["Detail"].default_value = 6
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    vl = n.new("ShaderNodeVectorMath"); vl.operation = "LENGTH"
    sc = n.new("ShaderNodeVectorMath"); sc.operation = "MULTIPLY"
    sc.inputs[1].default_value = (2 / size[0], 2 / size[1], 0.5 / size[2])
    l.new(tc.outputs["Object"], sc.inputs[0])
    l.new(sc.outputs[0], vl.inputs[0])
    edge = _mathn(n, l, "ADD", vl.outputs["Value"], _mathn(n, l, "MULTIPLY", nz.outputs["Fac"], 0.6))
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.7
    ramp.color_ramp.elements[0].color = (0.11, 0.16, 0.1, 1)
    ramp.color_ramp.elements[1].position = 1.35
    ramp.color_ramp.elements[1].color = (0.02, 0.02, 0.015, 1)
    l.new(edge, ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.8
    L.assign(o, m)
    smooth_obj(o)
    b = L.prim("cube", loc=(loc[0], loc[1], loc[2]))
    b.scale = (0.006, size[1] / 2 + 0.003, size[2] / 2 + 0.003)
    b.rotation_euler = (0, 0, rot_z)
    L.assign(b, L.mat_principled(name + "_band", (0.15, 0.08, 0.05), rough=0.6))
    return o


def glow_poly(points, color=(0.3, 0.7, 1.0), strength=4.0, bevel=0.01, name="glow", closed=False):
    """Emissive polyline curve (blueprint / outline graphics). Animate with curve_draw."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    pts = list(points) + ([points[0]] if closed else [])
    sp.points.add(len(pts) - 1)
    for k, q in enumerate(pts):
        sp.points[k].co = (*q, 1)
    cu.bevel_depth = bevel
    cu.bevel_resolution = 2
    o = L.link(bpy.data.objects.new(name, cu))
    o.data.materials.append(L.mat_emission(name + "_m", color, strength))
    o.visible_shadow = False
    return o


def rect_pts(cx, cz, w, h, y=0.0):
    return [(cx - w / 2, y, cz - h / 2), (cx + w / 2, y, cz - h / 2), (cx + w / 2, y, cz + h / 2), (cx - w / 2, y, cz + h / 2)]


def hangar(size=(60, 40, 16), name="hangar", light=1.0):
    """Dim hangar box: concrete floor, ribbed back wall, row of cool top lights. Centre at origin, floor z=0."""
    sx, sy, sz = size
    fl = L.prim("plane", loc=(0, 0, 0), size=1)
    fl.scale = (sx, sy, 1)
    L.assign(fl, L.mat_noise_surface(name + "_floor", (0.05, 0.05, 0.05), (0.14, 0.14, 0.14), scale=1.5, bump=0.1, rough=0.35,
                                     voronoi=False))
    wm = L.mat_noise_surface(name + "_wall", (0.025, 0.028, 0.032), (0.07, 0.075, 0.08), scale=2, bump=0.2, voronoi=False)
    bw = L.prim("plane", loc=(0, sy / 2, sz / 2), size=1, rot=(math.pi / 2, 0, 0))
    bw.scale = (sx, sz, 1)
    L.assign(bw, wm)
    rib_m = L.mat_principled(name + "_rib", (0.05, 0.055, 0.06), rough=0.5, metal=0.6)
    for x in range(int(-sx / 2), int(sx / 2) + 1, 5):
        r = L.prim("cube", loc=(x, sy / 2 - 0.3, sz / 2))
        r.scale = (0.25, 0.3, sz / 2)
        L.assign(r, rib_m)
    lm = L.mat_emission(name + "_lamp", (0.75, 0.85, 1.0), 12)
    for x in range(int(-sx / 2) + 5, int(sx / 2), 10):
        for y in (-6, 6):
            lp = L.prim("cube", loc=(x, y, sz - 0.3))
            lp.scale = (0.8, 0.8, 0.08)
            L.assign(lp, lm)
            lp.visible_shadow = False
            L.spot((x, y, sz - 0.5), (0, 0, 0), energy=4000 * light, size_deg=85, blend=0.8, color=(0.75, 0.85, 1.0),
                   name=f"{name}_sp{x}_{y}", radius=0.5)
    return fl


def suspect_wall(cols=12, rows=8, w=0.42, h=0.56, gap=0.12, origin=(0, 0, 0), seed=3, name="suspects", jitter=0.06):
    """Big wall of pinned faceless suspect cards (paper + dark silhouette bust + red pin), each as one joined mesh.
    Cards lie in the XZ plane facing -Y, grid centred on origin. Returns list of 3 objects."""
    rnd = random.Random(seed)
    bp, bs, bn = bmesh.new(), bmesh.new(), bmesh.new()
    W = cols * (w + gap)
    H = rows * (h + gap)
    for i in range(cols):
        for j in range(rows):
            cx = origin[0] - W / 2 + (i + 0.5) * (w + gap) + rnd.uniform(-jitter, jitter)
            cz = origin[2] - H / 2 + (j + 0.5) * (h + gap) + rnd.uniform(-jitter, jitter)
            a = rnd.uniform(-0.08, 0.08)
            M = Matrix.Translation((cx, origin[1], cz)) @ Matrix.Rotation(a, 4, "Y")
            bmesh.ops.create_grid(bp, x_segments=1, y_segments=1, size=0.5,
                                  matrix=M @ Matrix.Rotation(math.pi / 2, 4, "X") @ Matrix.Diagonal((w, h, 1, 1)))
            # silhouette: head disc + shoulders half-disc
            bmesh.ops.create_circle(bs, cap_ends=True, segments=16, radius=w * 0.17,
                                    matrix=M @ Matrix.Translation((0, -0.004, h * 0.1)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
            bmesh.ops.create_circle(bs, cap_ends=True, segments=20, radius=w * 0.34,
                                    matrix=M @ Matrix.Translation((0, -0.003, -h * 0.36)) @ Matrix.Rotation(math.pi / 2, 4, "X")
                                    @ Matrix.Diagonal((1, 0.75, 1, 1)))
            bmesh.ops.create_uvsphere(bn, u_segments=6, v_segments=4, radius=0.018,
                                      matrix=M @ Matrix.Translation((0, -0.02, h * 0.42)))
    paper = L.mesh_from_bm(name + "_paper", bp)
    L.assign(paper, mat_paper(name + "_pm", (0.6, 0.57, 0.48)))
    # trim silhouettes to card bottom: shoulders disc extends below card -> squash handled by Diagonal; fine stylised
    sil = L.mesh_from_bm(name + "_sil", bs)
    L.assign(sil, L.mat_principled(name + "_sm", (0.03, 0.03, 0.035), rough=0.9))
    pins = L.mesh_from_bm(name + "_pins", bn)
    L.assign(pins, L.mat_principled(name + "_pn", (0.6, 0.04, 0.03), rough=0.3))
    return [paper, sil, pins]


def red_string(points, name="string", strength=0.6):
    """Taut red string between pins (thin curve)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for k, q in enumerate(points):
        sp.points[k].co = (*q, 1)
    cu.bevel_depth = 0.006
    o = L.link(bpy.data.objects.new(name, cu))
    o.data.materials.append(L.mat_principled(name + "_m", (0.6, 0.02, 0.02), rough=0.5, emit=(0.6, 0.02, 0.02),
                                             emit_strength=strength))
    return o


def glass_drops(center, size=(3.0, 4.0), count=260, seed=3, name="drops", rmin=0.008, rmax=0.035):
    """Raindrops on a vertical pane (XZ plane at center.y, facing -Y): one mesh of flattened hemispheres."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    for i in range(count):
        r = rnd.uniform(rmin, rmax) * (1.0 if rnd.random() > 0.15 else 1.8)
        x = center[0] + rnd.uniform(-0.5, 0.5) * size[0]
        z = center[2] + rnd.uniform(-0.5, 0.5) * size[1]
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=r,
                                  matrix=Matrix.Translation((x, center[1], z)) @ Matrix.Diagonal((1, 0.35, 1.25, 1)))
    o = L.mesh_from_bm(name, bm)
    smooth_obj(o)
    L.assign(o, L.mat_principled(name + "_m", (0.5, 0.55, 0.62), rough=0.02, metal=0.0, emit=(0.35, 0.4, 0.5), emit_strength=0.25))
    return o


def bokeh_lights(center, size, count=30, seed=4, colors=((1.0, 0.55, 0.2), (1.0, 0.8, 0.5), (0.6, 0.75, 1.0), (1.0, 0.2, 0.1)),
                 strength=12, name="bokeh"):
    """Distant city/airport lights (emissive spheres) for a defocused background."""
    rnd = random.Random(seed)
    out = []
    mats = [L.mat_emission(f"{name}_m{i}", c, strength) for i, c in enumerate(colors)]
    for i in range(count):
        p = (center[0] + rnd.uniform(-0.5, 0.5) * size[0], center[1] + rnd.uniform(-0.5, 0.5) * size[1],
             center[2] + rnd.uniform(-0.5, 0.5) * size[2])
        s = L.prim("ico", loc=p, subdivisions=1, radius=rnd.uniform(0.06, 0.18))
        L.assign(s, mats[rnd.randrange(len(mats))])
        s.visible_shadow = False
        out.append(s)
    return out


# ============================================================================ MURDER-04 (Zodiac 340) builders
# Cipher grid of individually keyframable stand-in glyphs (illustrative only, not the real sheet), screens, CRT TV.

F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CIPHER_LET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CIPHER_GREEK = "ΘΦΣΔΩΓΛΠΨ"
CIPHER_SHAPES = ["tri", "trio", "dot", "slash", "bslash", "sq", "plus", "circ"]


def cipher_specs(n=340, seed=340):
    """Same generator as BLENDER_PROJECTS/MURDER-04/make_textures.py (kind, glyph, rot90s, mirror)."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        r = rnd.random()
        if r < 0.62:
            out.append(("ch", rnd.choice(CIPHER_LET), rnd.choice([0, 0, 0, 1, 2, 3]), rnd.random() < 0.25))
        elif r < 0.78:
            out.append(("ch", rnd.choice(CIPHER_GREEK), 0, False))
        else:
            out.append(("sh", rnd.choice(CIPHER_SHAPES), 0, False))
    return out


_GLYPH_CACHE = {}


def _glyph_mesh(spec, size):
    """Mesh datablock for a glyph lying in the local XY plane (facing +Z), centred, height ~size. Cached."""
    key = (spec, round(size, 4))
    if key in _GLYPH_CACHE:
        return _GLYPH_CACHE[key]
    kind, g, rot, mirror = spec
    s = size * 0.42
    if kind == "ch":
        cu = bpy.data.curves.new("gtmp", "FONT")
        cu.body = g
        cu.size = size * 0.95
        cu.extrude = size * 0.04
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        f = _font(F_SANS_B)
        if f:
            cu.font = f
        o = L.link(bpy.data.objects.new("gtmp", cu))
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        bpy.data.objects.remove(o)
        bpy.data.curves.remove(cu)
    else:
        bm = bmesh.new()
        w = max(size * 0.07, 0.004)
        if g in ("tri", "trio"):
            pts = [(0, s), (s, -s), (-s, -s)]
            if g == "tri":
                vs = [bm.verts.new((x, y, 0)) for x, y in pts]
                bm.faces.new(vs)
            else:
                for i in range(3):
                    a, b = Vector((*pts[i], 0)), Vector((*pts[(i + 1) % 3], 0))
                    _bar(bm, a, b, w)
        elif g == "dot":
            bmesh.ops.create_circle(bm, cap_ends=True, segments=16, radius=s * 0.35)
        elif g == "slash":
            _bar(bm, Vector((-s, -s, 0)), Vector((s, s, 0)), w * 1.3)
        elif g == "bslash":
            _bar(bm, Vector((-s, s, 0)), Vector((s, -s, 0)), w * 1.3)
        elif g == "sq":
            c = [(-s, -s), (s, -s), (s, s), (-s, s)]
            for i in range(4):
                _bar(bm, Vector((*c[i], 0)), Vector((*c[(i + 1) % 4], 0)), w)
        elif g == "plus":
            _bar(bm, Vector((-s, 0, 0)), Vector((s, 0, 0)), w * 1.3)
            _bar(bm, Vector((0, -s, 0)), Vector((0, s, 0)), w * 1.3)
        elif g == "circ":
            k = 20
            for i in range(k):
                a0, a1 = 2 * math.pi * i / k, 2 * math.pi * (i + 1) / k
                _bar(bm, Vector((s * math.cos(a0), s * math.sin(a0), 0)), Vector((s * math.cos(a1), s * math.sin(a1), 0)), w)
            _bar(bm, Vector((-s, 0, 0)), Vector((s, 0, 0)), w)
        ext = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
        for v in [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]:
            v.co.z += size * 0.04
        me = bpy.data.meshes.new("gsh")
        bm.to_mesh(me)
        bm.free()
    M_ = Matrix.Identity(4)
    if mirror:
        M_ = Matrix.Diagonal((-1, 1, 1, 1)) @ M_
    if rot:
        M_ = Matrix.Rotation(math.pi / 2 * rot, 4, "Z") @ M_
    me.transform(M_)
    if mirror:
        me.flip_normals()
    _GLYPH_CACHE[key] = me
    return me


def _bar(bm, a, b, w):
    d = (b - a)
    n = Vector((-d.y, d.x, 0)).normalized() * w / 2
    vs = [bm.verts.new(a + n), bm.verts.new(b + n), bm.verts.new(b - n), bm.verts.new(a - n)]
    bm.faces.new(vs)


def mat_glyph(name="glyph", ink=(0.03, 0.025, 0.035), glow=6.0):
    """Shared glyph material: base ink; emission colour = object colour RGB, strength = object colour alpha * glow.
    Keyframe obj.color per glyph (set_glyph) to light it up without per-object materials."""
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    oi = n.new("ShaderNodeObjectInfo")
    mix = n.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs[0].default_value = 0.0
    p.inputs["Base Color"].default_value = (*ink, 1)
    p.inputs["Roughness"].default_value = 0.6
    l.new(oi.outputs["Color"], p.inputs["Emission Color"])
    s = _mathn(n, l, "MULTIPLY", oi.outputs["Alpha"], glow)
    l.new(s, p.inputs["Emission Strength"])
    # base colour tint: lerp ink -> object colour by alpha (so lit glyphs are not dark-cored)
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"
    l.new(_mathn(n, l, "MINIMUM", oi.outputs["Alpha"], 1.0), mx.inputs[0])
    mx.inputs[6].default_value = (*ink, 1)
    l.new(oi.outputs["Color"], mx.inputs[7])
    l.new(mx.outputs[2], p.inputs["Base Color"])
    return m


def set_glyph(o, frame, rgb=(1, 0.1, 0.05), amount=0.0):
    o.color = (*rgb, amount)
    o.keyframe_insert("color", frame=max(1, frame))


def cipher_grid(rows=20, cols=17, cw=0.1, ch=0.12, origin=(0, 0, 0), seed=340, paper=True, mat=None, name="cg",
                paper_col=(0.62, 0.58, 0.48), margin=(0.12, 0.16), glyph_scale=0.78):
    """Grid of rows x cols stand-in glyph objects in the XZ plane (facing -Y), centred on origin, row 0 at the top.
    Returns dict: g[r][c] objects, pos(r,c) -> Vector, paper, specs, cw, ch."""
    specs = cipher_specs(rows * cols, seed)
    mat = mat or mat_glyph(name + "_gm")
    W, H = cols * cw, rows * ch
    ox, oy, oz = origin
    out = {"g": [], "specs": specs, "cw": cw, "ch": ch, "rows": rows, "cols": cols, "mat": mat}

    def pos(r, c, y=-0.004):
        return Vector((ox - W / 2 + (c + 0.5) * cw, oy + y, oz + H / 2 - (r + 0.5) * ch))
    out["pos"] = pos
    for r in range(rows):
        row = []
        for c in range(cols):
            me = _glyph_mesh(specs[r * cols + c], ch * glyph_scale)
            o = L.link(bpy.data.objects.new(f"{name}_{r}_{c}", me))
            o.data.materials.clear()
            o.data.materials.append(mat)
            o.location = pos(r, c)
            o.rotation_euler = (math.pi / 2, 0, 0)
            o.color = (1, 1, 1, 0)
            row.append(o)
        out["g"].append(row)
    if paper:
        pp = L.prim("plane", loc=(ox, oy + 0.002, oz), size=1, rot=(math.pi / 2, 0, 0), name=name + "_paper")
        pp.scale = (W + 2 * margin[0], H + 2 * margin[1], 1)
        L.assign(pp, mat_paper(name + "_pm", paper_col))
        out["paper"] = pp
    return out


def letter_obj(ch_, size, mat, loc, name="let"):
    me = _glyph_mesh(("ch", ch_, 0, False), size)
    o = L.link(bpy.data.objects.new(name, me))
    o.data.materials.clear()
    o.data.materials.append(mat)
    o.location = loc
    o.rotation_euler = (math.pi / 2, 0, 0)
    o.color = (1, 1, 1, 0)
    return o


def hop_path(rows, cols, start=(0, 0), dr=1, dc=2, count=None):
    """Diagonal reading order (down dr rows, right dc columns, wrapping at the edges)."""
    r, c = start
    out = []
    for k in range(count or rows * cols):
        out.append((r, c))
        r = (r + dr) % rows
        c = (c + dc) % cols
    return out


def mat_screen(name, path, strength=3.0, scroll=(0.0, 0.0), n=100, scale=(1, 1), tint=(1, 1, 1), flicker=0.0, seed=1,
               steps=None):
    """Emissive screen with an image; scroll = UV units per second (wrapping); steps = (period_frames, offsets list) for
    a stepped atlas flicker; flicker = strength jitter depth."""
    m, nn, l = L._mat(name)
    for nd in list(nn):
        if nd.type == "BSDF_PRINCIPLED":
            nn.remove(nd)
    tc = nn.new("ShaderNodeTexCoord")
    mp = nn.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (*scale, 1)
    l.new(tc.outputs["UV"], mp.inputs["Vector"])
    tx = nn.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(path, check_existing=True)
    tx.extension = "REPEAT"
    l.new(mp.outputs[0], tx.inputs["Vector"])
    em = nn.new("ShaderNodeEmission")
    tn = nn.new("ShaderNodeMix"); tn.data_type = "RGBA"; tn.blend_type = "MULTIPLY"
    tn.inputs[0].default_value = 1.0
    l.new(tx.outputs["Color"], tn.inputs[6])
    tn.inputs[7].default_value = (*tint, 1)
    l.new(tn.outputs[2], em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    l.new(em.outputs[0], nn["Material Output"].inputs["Surface"])
    loc = mp.inputs["Location"]
    if any(scroll):
        loc.default_value = (0, 0, 0)
        loc.keyframe_insert("default_value", frame=1)
        loc.default_value = (scroll[0] * n / FPS, scroll[1] * n / FPS, 0)
        loc.keyframe_insert("default_value", frame=n)
    if steps:
        per, offs = steps
        k = 0
        for f in range(1, n + 1, per):
            loc.default_value = (*offs[k % len(offs)], 0)
            loc.keyframe_insert("default_value", frame=f)
            k += 1
    if m.node_tree.animation_data and m.node_tree.animation_data.action:
        for fc in L._fcurves(m.node_tree.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT" if steps else "LINEAR"
    if flicker:
        rnd = random.Random(seed)
        st = em.inputs["Strength"]
        for f in range(1, n + 1, 2):
            st.default_value = strength * (1 - flicker * rnd.random())
            st.keyframe_insert("default_value", frame=f)
    return m, em


def monitor(loc=(0, 0, 0), rot_z=0.0, w=0.62, h=0.36, screen_mat=None, name="mon", keyboard=True):
    """Modern flat monitor on a stand (screen faces -Y locally), optional keyboard. Root at desk level."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    bm_ = L.mat_principled(name + "_b", (0.015, 0.015, 0.017), rough=0.35, metal=0.3)
    bz = 0.12 + h / 2
    bez = L.prim("cube", loc=(0, 0.0, bz))
    bez.scale = (w / 2 + 0.015, 0.018, h / 2 + 0.015)
    L.assign(bez, bm_)
    bez.parent = root
    sc = L.prim("plane", loc=(0, -0.0195, bz), size=1, rot=(math.pi / 2, 0, 0), name=name + "_screen")
    sc.scale = (w, h, 1)
    if screen_mat:
        L.assign(sc, screen_mat)
    sc.parent = root
    sc.visible_shadow = False
    nk = L.prim("cube", loc=(0, 0.05, 0.08))
    nk.scale = (0.03, 0.015, 0.08)
    L.assign(nk, bm_)
    nk.parent = root
    bs = L.prim("cube", loc=(0, 0.02, 0.006))
    bs.scale = (0.12, 0.09, 0.006)
    L.assign(bs, bm_)
    bs.parent = root
    if keyboard:
        kb = L.prim("cube", loc=(0, -0.3, 0.012))
        kb.scale = (0.22, 0.07, 0.012)
        L.assign(kb, L.mat_principled(name + "_kb", (0.03, 0.03, 0.035), rough=0.6))
        kb.parent = root
    return {"root": root, "screen": sc, "center_z": bz}


def crt_tv(loc=(0, 0, 0), rot_z=0.0, screen_mat=None, name="tv", legs=True):
    """1960s wood-veneer box TV with a slightly convex screen, knobs and splayed legs. Screen faces -Y locally."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    wood = L.mat_noise_surface(name + "_wood", (0.08, 0.04, 0.018), (0.22, 0.11, 0.05), scale=6, bump=0.15, voronoi=False, rough=0.45)
    z0 = 0.45 if legs else 0.0
    box = rounded_box((0, 0, z0 + 0.3), (0.82, 0.55, 0.6), (0.2, 0.1, 0.05), bevel=0.08, name=name + "_box", mat=wood)
    box.parent = root
    fr = L.prim("cube", loc=(-0.08, -0.276, z0 + 0.3))
    fr.scale = (0.3, 0.005, 0.24)
    L.assign(fr, L.mat_principled(name + "_fr", (0.03, 0.03, 0.03), rough=0.4))
    fr.parent = root
    # slightly bulged flat screen (subdivided grid, default 0..1 UVs keep the whole picture)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=16, y_subdivisions=16, size=1.0, location=(-0.08, -0.28, z0 + 0.3),
                                    rotation=(math.pi / 2, 0, 0))
    sc = bpy.context.active_object
    sc.name = name + "_screen"
    sc.scale = (0.58, 0.46, 1)
    for v in sc.data.vertices:
        r2 = (v.co.x * 2) ** 2 + (v.co.y * 2) ** 2
        v.co.z = 0.03 * max(0.0, 1 - 0.5 * r2) / 1.0
    smooth_obj(sc)
    if screen_mat:
        L.assign(sc, screen_mat)
    sc.parent = root
    sc.visible_shadow = False
    km = L.mat_principled(name + "_k", (0.5, 0.45, 0.35), rough=0.3, metal=0.8)
    for kz in (0.42, 0.3, 0.18):
        k = L.prim("cyl", loc=(0.3, -0.29, z0 + kz), vertices=16, radius=0.03, depth=0.03, rot=(math.pi / 2, 0, 0))
        L.assign(k, km)
        k.parent = root
    gr = L.prim("cube", loc=(0.3, -0.278, z0 + 0.52))
    gr.scale = (0.07, 0.004, 0.05)
    L.assign(gr, L.mat_principled(name + "_gr", (0.05, 0.04, 0.03), rough=0.8))
    gr.parent = root
    if legs:
        for sx in (-1, 1):
            for sy in (-1, 1):
                lg = L.prim("cyl", loc=(sx * 0.32, sy * 0.18, 0.22), vertices=8, radius=0.018, depth=0.48,
                            rot=(sy * 0.12, -sx * 0.12, 0))
                L.assign(lg, wood)
                lg.parent = root
    return {"root": root, "screen": sc, "screen_center": (loc[0] - 0.08, loc[1] - 0.29, loc[2] + z0 + 0.3)}


def mat_tv_screen(name, path, n, strength=2.5, static=0.35, roll=0.6, tint=(0.82, 0.9, 1.0)):
    """CRT picture: greyscale image + animated static noise + a rolling brighter band; slight vignette."""
    m, nn, l = L._mat(name)
    for nd in list(nn):
        if nd.type == "BSDF_PRINCIPLED":
            nn.remove(nd)
    tc = nn.new("ShaderNodeTexCoord")
    tx = nn.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(path, check_existing=True)
    tx.extension = "EXTEND"
    l.new(tc.outputs["UV"], tx.inputs["Vector"])
    nz = nn.new("ShaderNodeTexNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["Scale"].default_value = 180.0
    nz.inputs["Detail"].default_value = 1.0
    l.new(tc.outputs["UV"], nz.inputs["Vector"])
    w = nz.inputs["W"]
    for f in range(1, n + 1):
        w.default_value = f * 7.3
        w.keyframe_insert("default_value", frame=f)
    sep = nn.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["UV"], sep.inputs[0])
    # rolling band
    band = _mathn(nn, l, "SUBTRACT", sep.outputs["Y"], 0.0)
    bnode = band.node
    for f in (1, n):
        bnode.inputs[1].default_value = 1.2 - roll * (f / FPS) * 1.0
        bnode.inputs[1].keyframe_insert("default_value", frame=f)
    fr = _mathn(nn, l, "FRACT", band)
    bd = _mathn(nn, l, "MULTIPLY", _mathn(nn, l, "POWER", fr, 12.0), 0.5)
    img = nn.new("ShaderNodeRGBToBW")
    l.new(tx.outputs["Color"], img.inputs[0])
    mixs = _mathn(nn, l, "ADD", _mathn(nn, l, "MULTIPLY", img.outputs[0], 1 - static),
                  _mathn(nn, l, "MULTIPLY", nz.outputs["Fac"], static))
    tot = _mathn(nn, l, "ADD", mixs, bd)
    em = nn.new("ShaderNodeEmission")
    cc = nn.new("ShaderNodeCombineXYZ")
    for i, t in enumerate(tint):
        l.new(_mathn(nn, l, "MULTIPLY", tot, t), cc.inputs[i])
    l.new(cc.outputs[0], em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    l.new(em.outputs[0], nn["Material Output"].inputs["Surface"])
    if m.node_tree.animation_data and m.node_tree.animation_data.action:
        for fc in L._fcurves(m.node_tree.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    return m, em


def box_typewriter(loc, rot_z=0.0, color=(0.05, 0.06, 0.055), name="tw"):
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_principled(name + "_m", color, rough=0.35, metal=0.4)
    b = rounded_box((0, 0, 0.07), (0.42, 0.34, 0.14), color, bevel=0.15, name=name + "_b", mat=m)
    b.parent = root
    pl = L.prim("cyl", loc=(0, 0.12, 0.17), vertices=16, radius=0.04, depth=0.46, rot=(0, math.pi / 2, 0))
    L.assign(pl, L.mat_principled(name + "_pl", (0.02, 0.02, 0.02), rough=0.5))
    pl.parent = root
    km = L.mat_principled(name + "_k", (0.7, 0.68, 0.6), rough=0.4)
    for r in range(4):
        for c in range(10):
            k = L.prim("cyl", loc=(-0.16 + c * 0.035, -0.12 + r * 0.035, 0.145 + r * 0.008), vertices=8, radius=0.012, depth=0.01)
            L.assign(k, km)
            k.parent = root
    sh = L.prim("plane", loc=(0, 0.16, 0.26), size=1, rot=(math.radians(75), 0, 0))
    sh.scale = (0.2, 0.22, 1)
    L.assign(sh, mat_paper(name + "_sheet", (0.75, 0.72, 0.62)))
    sh.parent = root
    return root


def hanging_lamp(loc, energy=300, color=(1.0, 0.72, 0.42), name="hlamp", cord=2.0):
    shade_m = L.mat_principled(name + "_shade", (0.06, 0.07, 0.06), rough=0.4, metal=0.7)
    sh = L.prim("cone", loc=loc, vertices=24, radius1=0.25, radius2=0.06, depth=0.22, name=name)
    L.assign(sh, shade_m)
    cd = L.prim("cyl", loc=(loc[0], loc[1], loc[2] + cord / 2), vertices=6, radius=0.006, depth=cord)
    L.assign(cd, shade_m)
    bulb = L.prim("sphere", loc=(loc[0], loc[1], loc[2] - 0.08), radius=0.05, segments=10, ring_count=6)
    L.assign(bulb, L.mat_emission(name + "_bulb", (1.0, 0.8, 0.5), 25))
    bulb.visible_shadow = False
    sp = L.spot((loc[0], loc[1], loc[2] - 0.1), (0, 0, 0), energy=energy, size_deg=80, blend=0.7, color=color, name=name + "_sp",
                radius=0.08)
    return sp


def coffee_cup(loc, color=(0.75, 0.72, 0.65), name="cup"):
    m = L.mat_principled(name + "_m", color, rough=0.25)
    c = L.prim("cyl", loc=(loc[0], loc[1], loc[2] + 0.045), vertices=20, radius=0.04, depth=0.09, name=name)
    L.assign(c, m)
    t = L.prim("torus", loc=(loc[0] + 0.045, loc[1], loc[2] + 0.05), major_radius=0.022, minor_radius=0.006, rot=(math.pi / 2, 0, 0))
    L.assign(t, m)
    cf = L.prim("cyl", loc=(loc[0], loc[1], loc[2] + 0.085), vertices=20, radius=0.036, depth=0.002)
    L.assign(cf, L.mat_principled(name + "_cf", (0.03, 0.015, 0.008), rough=0.1))
    return c


def image_plane(path, loc, size, rot=(math.pi / 2, 0, 0), emit=0.0, name="img", rough=0.8):
    o = L.prim("plane", loc=loc, size=1, rot=rot, name=name)
    o.scale = (size[0], size[1], 1)
    L.assign(o, L.mat_image(name + "_m", path, emit=emit, rough=rough))
    return o


def fast_conifers(name, spots, mat=None, tiers=(3, 4), seg=6, seed=1, **kw):
    """Fast stacked-cone conifers (plain vertex lists, no bmesh ops) for big distant forests.
    spots: (x, y, z, height). One mesh."""
    rnd = random.Random(seed)
    verts, faces = [], []
    for (x, y, z, h) in spots:
        nt = rnd.randint(*tiers)
        rot = rnd.uniform(0, 6.28)
        # trunk (3-sided)
        b = len(verts)
        tr = h * 0.03
        for k in range(3):
            a = rot + 2 * math.pi * k / 3
            verts.append((x + tr * math.cos(a), y + tr * math.sin(a), z))
        verts.append((x, y, z + h * 0.4))
        faces += [(b, b + 1, b + 3), (b + 1, b + 2, b + 3), (b + 2, b, b + 3)]
        for k in range(nt):
            f = k / nt
            r = h * (0.26 * (1 - f) + 0.05) * rnd.uniform(0.85, 1.15)
            zb = z + h * (0.15 + 0.78 * f)
            zt = zb + h * 0.34 * (1 - 0.4 * f)
            b = len(verts)
            for s in range(seg):
                a = rot + 2 * math.pi * s / seg + k * 0.5
                rr = r * rnd.uniform(0.85, 1.1)
                verts.append((x + rr * math.cos(a), y + rr * math.sin(a), zb + rnd.uniform(-0.04, 0.04) * h))
            verts.append((x, y, zt))
            for s in range(seg):
                faces.append((b + s, b + (s + 1) % seg, b + seg))
            faces.append(tuple(b + s for s in reversed(range(seg))))
    o = mesh_obj(name, verts, faces, mat=mat or mat_dusted(name + "_m"))
    o.visible_shadow = kw.get("shadow", False)  # thousands of shadow casters are very slow in EEVEE (virtual shadow maps)
    return o


# ============================================================================ MURDER-05 (Hinterkaifeck farm, 1922) builders
# Farmstead (studio_lib.house_exterior + attached gabled barn wing), plank material, keyable lit window, fence, lantern,
# primitive cattle, iron key, question-mark suspect cards, newspaper, oil lamp, laptop, case folder.
# Farm layout: house centred at loc, front (gable end with windows) faces -Y; barn wing attached on +X, ridge along X.

def mat_planks(name, c1=(0.05, 0.032, 0.02), c2=(0.13, 0.085, 0.05), width=0.22, axis="X", rough=0.85):
    """Weathered vertical planks: dark seams every `width` m along `axis` (object coords) + grain noise."""
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sep.inputs[0])
    coord = sep.outputs[axis]
    fr = _mathn(n, l, "FRACT", _mathn(n, l, "DIVIDE", coord, width))
    seam = _mathn(n, l, "LESS_THAN", fr, 0.06)
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 9.0
    nz.inputs["Detail"].default_value = 6
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (6, 6, 0.6) if axis == "X" else (0.6, 6, 6)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    l.new(mp.outputs[0], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    l.new(seam, mix.inputs[0])
    l.new(ramp.outputs["Color"], mix.inputs[6])
    mix.inputs[7].default_value = (c1[0] * 0.25, c1[1] * 0.25, c1[2] * 0.25, 1)
    l.new(mix.outputs[2], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.25
    l.new(_mathn(n, l, "SUBTRACT", 1.0, seam), bp.inputs["Height"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def gable_box(name, x0, x1, y0, y1, wall_h, roof_h, wall_mat, roof_mat, overhang=0.4, ridge="X", z0=0.0):
    """Walls box + gabled roof prism. ridge='X': ridge runs along X (gables at the X ends). Returns (walls, roof)."""
    w = L.prim("cube", loc=((x0 + x1) / 2, (y0 + y1) / 2, z0 + wall_h / 2), name=name + "_walls")
    w.scale = ((x1 - x0) / 2, (y1 - y0) / 2, wall_h / 2)
    L.apply_scale(w)
    L.assign(w, wall_mat)
    o = overhang
    zt = z0 + wall_h
    if ridge == "X":
        ym = (y0 + y1) / 2
        v = [(x0 - o, y0 - o, zt - 0.15), (x1 + o, y0 - o, zt - 0.15), (x1 + o, ym, zt + roof_h), (x0 - o, ym, zt + roof_h),
             (x0 - o, y1 + o, zt - 0.15), (x1 + o, y1 + o, zt - 0.15)]
        f = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2), (0, 4, 5, 1)]
        gv = [(x0, y0, zt), (x0, y1, zt), (x0, ym, zt + roof_h), (x1, y0, zt), (x1, y1, zt), (x1, ym, zt + roof_h)]
    else:
        xm = (x0 + x1) / 2
        v = [(x0 - o, y0 - o, zt - 0.15), (xm, y0 - o, zt + roof_h), (xm, y1 + o, zt + roof_h), (x0 - o, y1 + o, zt - 0.15),
             (x1 + o, y0 - o, zt - 0.15), (x1 + o, y1 + o, zt - 0.15)]
        f = [(0, 1, 2, 3), (1, 4, 5, 2), (0, 4, 1), (3, 2, 5), (0, 3, 5, 4)]
        gv = [(x0, y0, zt), (x1, y0, zt), (xm, y0, zt + roof_h), (x0, y1, zt), (x1, y1, zt), (xm, y1, zt + roof_h)]
    r = mesh_obj(name + "_roof", v, f, mat=roof_mat)
    solidify(r, 0.18)
    g = mesh_obj(name + "_gables", gv, [(0, 1, 2), (3, 5, 4)], mat=wall_mat)
    solidify(g, 0.1)
    return w, r


def farmstead(loc=(0, 0, 0), lit=True, seed=1, window_energy=3.0, spill=35.0, smoke=False, lit_xz=(3.0, 1.6)):
    """Hinterkaifeck-style farmstead: two-storey gabled house (studio_lib.house_exterior, porch removed, snow-dusted
    roof, chimney) + attached barn wing (14 x 7 x 5 m, planks, double door). One lit window with a keyable emission
    strength (out['win_strength'] socket) and a warm spill point light (out['win_light'])."""
    lx, ly, lz = loc
    roofm = mat_dusted("farm_roof", base=(0.03, 0.022, 0.02), snow=(0.66, 0.71, 0.8), thresh=0.5, noise_scale=3.0)
    plaster = L.mat_noise_surface("farm_plaster", (0.2, 0.19, 0.17), (0.36, 0.34, 0.3), scale=3, bump=0.25, voronoi=False)
    house = L.house_exterior(loc=(lx, ly, lz - 0.1), w=9, d=7, floors=2, roof_h=3.4, siding=plaster, roof=roofm, lit_windows=())
    for c in list(house.children):
        if c.location.y < -3.5 - 0.5:  # porch roof + columns (not on a Bavarian farmhouse)
            bpy.data.objects.remove(c, do_unlink=True)
        elif abs(c.location.x) < 0.01 and abs(c.location.z - 1.6) < 0.01:  # window overlapping the door
            bpy.data.objects.remove(c, do_unlink=True)
    # window frames (pale) around every front window
    fm = L.mat_principled("farm_winframe", (0.32, 0.3, 0.26), rough=0.7)
    for fl in range(2):
        for xx in (-3.0, 0.0, 3.0):
            if fl == 0 and xx == 0.0:
                continue
            for (dx, dz, sx, sz) in ((0, 0.74, 0.52, 0.05), (0, -0.74, 0.52, 0.05), (0.49, 0, 0.04, 0.74), (-0.49, 0, 0.04, 0.74),
                                     (0, 0, 0.45, 0.025)):
                b = L.prim("cube", loc=(lx + xx + dx, ly - 3.58, lz - 0.1 + fl * 3.0 + 1.6 + dz))
                b.scale = (sx, 0.04, sz)
                L.assign(b, fm)
    out = {"house": house}
    # chimney
    ch = L.prim("cube", loc=(lx + 1.3, ly + 1.0, lz + 8.9), name="chimney")
    ch.scale = (0.32, 0.32, 1.5)
    L.assign(ch, L.mat_noise_surface("chimney_m", (0.12, 0.08, 0.07), (0.25, 0.16, 0.12), scale=12, bump=0.3, voronoi=False))
    out["chimney_top"] = Vector((lx + 1.3, ly + 1.0, lz + 10.4))
    # barn wing
    planks = mat_planks("barn_planks", axis="X")
    w, r = gable_box("barn", lx + 4.5, lx + 18.5, ly - 3.5, ly + 3.5, 5.0, 3.0, planks, roofm, ridge="X", z0=lz - 0.1)
    out["barn"] = w
    dm = mat_planks("barn_door", c1=(0.035, 0.022, 0.014), c2=(0.08, 0.05, 0.03), width=0.16, axis="X")
    bm_ = L.mat_principled("door_brace", (0.03, 0.02, 0.012), rough=0.8)
    for sx in (-1, 1):
        d = L.prim("cube", loc=(lx + 12 + sx * 0.92, ly - 3.56, lz + 1.6))
        d.scale = (0.9, 0.05, 1.7)
        L.assign(d, dm)
        br = L.prim("cube", loc=(lx + 12 + sx * 0.92, ly - 3.62, lz + 1.6), rot=(0, sx * 0.95, 0))
        br.scale = (0.06, 0.02, 1.85)
        L.assign(br, bm_)
    lintel = L.prim("cube", loc=(lx + 12, ly - 3.58, lz + 3.4))
    lintel.scale = (2.0, 0.08, 0.1)
    L.assign(lintel, bm_)
    # small dark barn windows
    dark = L.mat_principled("barn_win", (0.008, 0.008, 0.01), rough=0.3)
    for xx in (7.0, 16.5):
        bw = L.prim("cube", loc=(lx + xx, ly - 3.55, lz + 2.6))
        bw.scale = (0.35, 0.04, 0.3)
        L.assign(bw, dark)
    # the lit window (own material so it can be switched off)
    m, n, l = L._mat("win_glow")
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    e = n.new("ShaderNodeEmission")
    e.inputs[0].default_value = (1.0, 0.7, 0.4, 1)
    e.inputs[1].default_value = window_energy if lit else 0.0
    l.new(e.outputs[0], n["Material Output"].inputs["Surface"])
    wx, wz = lit_xz
    win = L.prim("cube", loc=(lx + wx, ly - 3.555, lz - 0.1 + wz), name="lit_window")
    win.scale = (0.44, 0.02, 0.69)
    L.assign(win, m)
    pt = L.point((lx + wx, ly - 4.3, lz + wz), energy=spill if lit else 0.0, color=(1.0, 0.62, 0.3), radius=0.4, name="win_spill")
    out.update(win_strength=e.inputs[1], win_light=pt, win_energy=window_energy, win_spill=spill, window=win)
    return out


def window_keys(F, keys):
    """keys = [(frame, 0..1)] -> animates window glow + spill together (constant interpolation for flicker)."""
    s = F["win_strength"]
    pt = F["win_light"].data
    for f, v in keys:
        s.default_value = F["win_energy"] * v
        s.keyframe_insert("default_value", frame=f)
        pt.energy = F["win_spill"] * v
        pt.keyframe_insert("energy", frame=f)


def fence(x0, x1, y, z_of=None, gate=None, step=2.2, h=1.1, name="fence", mat=None, seed=3):
    """Simple post-and-two-rail farm fence along X at y. gate=(gx, half_width) leaves a gap. One mesh."""
    rnd = random.Random(seed)
    m = mat or mat_dusted(name + "_m", base=(0.05, 0.035, 0.022), thresh=0.6)
    bm = bmesh.new()
    zf = z_of or (lambda x, yy: 0.0)
    xs = []
    x = x0
    while x <= x1:
        if not (gate and abs(x - gate[0]) < gate[1]):
            xs.append(x)
        x += step
    if gate:
        xs += [gate[0] - gate[1], gate[0] + gate[1]]
    xs.sort()
    for x in xs:
        z = zf(x, y)
        bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((x, y, z + h / 2 - 0.1)) @ Matrix.Rotation(rnd.uniform(-0.05, 0.05), 4, "Y")
                              @ Matrix.Diagonal((0.1, 0.1, h + 0.2, 1)))
    for a, b in zip(xs[:-1], xs[1:]):
        if gate and a < gate[0] < b:
            continue
        for zz in (0.45, 0.9):
            za, zb = zf(a, y) + zz, zf(b, y) + zz
            mid = Vector(((a + b) / 2, y - 0.06, (za + zb) / 2))
            ln = math.hypot(b - a, zb - za)
            ang = math.atan2(zb - za, b - a)
            bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation(mid) @ Matrix.Rotation(-ang, 4, "Y") @ Matrix.Diagonal((ln, 0.05, 0.08, 1)))
    o = L.mesh_from_bm(name, bm)
    L.assign(o, m)
    return o


def lantern(loc, energy=40.0, color=(1.0, 0.62, 0.28), name="lantern", parent=None, flicker_n=0):
    """Small storm lantern (iron frame, glowing glass) + warm point light. Returns (root, light)."""
    root = empty(name, loc, parent)
    im = L.mat_principled(name + "_iron", (0.03, 0.03, 0.03), rough=0.5, metal=0.6)
    gm = L.mat_emission(name + "_glass", (1.0, 0.7, 0.35), 6.0)
    g = L.prim("cyl", loc=(0, 0, 0.12), vertices=12, radius=0.055, depth=0.14)
    L.assign(g, gm)
    g.visible_shadow = False
    for z, r, dpt in ((0.03, 0.07, 0.04), (0.21, 0.065, 0.03)):
        c = L.prim("cyl", loc=(0, 0, z), vertices=12, radius=r, depth=dpt)
        L.assign(c, im)
        c.parent = root
        c.location = (0, 0, z)
    top = L.prim("cone", loc=(0, 0, 0.26), vertices=12, radius1=0.06, radius2=0.015, depth=0.07)
    L.assign(top, im)
    hd = L.prim("torus", loc=(0, 0, 0.33), major_radius=0.05, minor_radius=0.006, rot=(math.pi / 2, 0, 0))
    L.assign(hd, im)
    for o in (g, top, hd):
        o.parent = root
    pt = L.point((0, 0, 0.12), energy=energy, color=color, radius=0.05, name=name + "_pt")
    pt.parent = root
    pt.location = (0, 0, 0.12)
    if flicker_n:
        L.flicker(pt, flicker_n, depth=0.15, rate=0.5, seed=7)
    return root, pt


def cow(loc, rot_z=0.0, color=(0.09, 0.05, 0.03), name="cow", head_down=0.6, seed=1):
    """Primitive dairy cow silhouette (rounded body, head box, four legs, horns). Faces +X locally. Returns dict."""
    rnd = random.Random(seed)
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_noise_surface(name + "_m", tuple(c * 0.6 for c in color), color, scale=6, bump=0.15, voronoi=False, rough=0.8)
    pale = L.mat_principled(name + "_pale", (0.42, 0.38, 0.32), rough=0.8)
    body = rounded_box((0, 0, 1.0), (1.9, 0.72, 0.75), color, bevel=0.4, name=name + "_body", mat=m)
    body.parent = root
    for sx in (-0.72, 0.72):
        for sy in (-0.24, 0.24):
            lg = L.prim("cyl", loc=(sx, sy, 0.38), vertices=8, radius=0.07, depth=0.78)
            L.assign(lg, m)
            lg.parent = root
    neck = empty(name + "_neck", (0.9, 0, 1.15), root)
    nk = L.prim("cyl", loc=(0, 0, 0), vertices=10, radius=0.2, depth=0.5, rot=(0, math.radians(70), 0))
    L.assign(nk, m)
    nk.parent = neck
    nk.location = (0.18, 0, -0.05)
    hd = rounded_box((0, 0, 0), (0.5, 0.3, 0.32), color, bevel=0.3, name=name + "_head", mat=m)
    hd.parent = neck
    hd.location = (0.45, 0, -0.15)
    hd.rotation_euler = (0, math.radians(35), 0)
    mz = rounded_box((0, 0, 0), (0.2, 0.26, 0.2), color, bevel=0.3, name=name + "_muzzle", mat=pale)
    mz.parent = neck
    mz.location = (0.68, 0, -0.3)
    for sy in (-1, 1):
        hn = L.prim("cone", loc=(0, 0, 0), vertices=6, radius1=0.035, radius2=0.005, depth=0.18)
        L.assign(hn, pale)
        hn.parent = neck
        hn.location = (0.32, sy * 0.15, 0.05)
        hn.rotation_euler = (sy * -0.9, -0.3, 0)
        ear = L.prim("cube", loc=(0, 0, 0))
        ear.scale = (0.04, 0.09, 0.03)
        L.assign(ear, m)
        ear.parent = neck
        ear.location = (0.3, sy * 0.2, -0.04)
    tail = L.prim("cyl", loc=(-0.98, 0, 0.85), vertices=6, radius=0.025, depth=0.7, rot=(0, 0.12, 0))
    L.assign(tail, m)
    tail.parent = root
    neck.rotation_euler = (0, head_down, 0)
    return {"root": root, "neck": neck, "body": body, "tail": tail}


def iron_key(loc, rot=(0, 0, 0), scale=1.0, name="key", mat=None):
    """Old iron key (bow ring + shaft + bit) lying in the local XZ plane, bow at top. Returns root."""
    root = empty(name, loc)
    root.rotation_euler = rot
    root.scale = (scale,) * 3
    m = mat or L.mat_principled(name + "_m", (0.06, 0.055, 0.05), rough=0.45, metal=0.85)
    bow = L.prim("torus", loc=(0, 0, 0), major_radius=0.028, minor_radius=0.006, rot=(math.pi / 2, 0, 0))
    sh = L.prim("cyl", loc=(0, 0, -0.085), vertices=10, radius=0.0055, depth=0.12)
    bit = L.prim("cube", loc=(0.012, 0, -0.13))
    bit.scale = (0.012, 0.004, 0.014)
    col = L.prim("cyl", loc=(0, 0, -0.03), vertices=10, radius=0.009, depth=0.01)
    for o in (bow, sh, bit, col):
        L.assign(o, m)
        o.parent = root
    return root


def qmark_cards(positions, size=(0.36, 0.48), name="qcards", paper=(0.42, 0.42, 0.41), mark=(0.12, 0.12, 0.13), seed=5):
    """Blank grey suspect cards with a single '?' (no names/faces). positions: list of (x, z) in the board plane (y=-0.01).
    Linked-duplicate meshes (cheap). Returns list of root empties (each with paper + mark + pin children)."""
    rnd = random.Random(seed)
    pm = mat_paper(name + "_pm", paper)
    mm = L.mat_principled(name + "_mm", mark, rough=0.8)
    pinm = L.mat_principled(name + "_pin", (0.6, 0.04, 0.03), rough=0.3)
    pl = L.prim("plane", loc=(0, 0, 0), size=1, rot=(math.pi / 2, 0, 0), name=name + "_proto")
    pl.scale = (size[0], size[1], 1)
    L.apply_scale(pl)
    t = L.text3d("?", loc=(0, 0, 0), size=size[1] * 0.62, extrude=0.0, mat=mm, name=name + "_q")
    t.data.font = _font(F_ANTON) or t.data.font
    t.data.align_y = "CENTER"
    bpy.context.view_layer.update()
    qme = bpy.data.meshes.new_from_object(t.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    qme.materials.clear()
    qme.materials.append(mm)
    bpy.data.objects.remove(t, do_unlink=True)
    pin = L.prim("sphere", loc=(0, 0, 0), radius=0.018, segments=8, ring_count=5)
    L.assign(pin, pinm)
    out = []
    for i, (x, z) in enumerate(positions):
        r = empty(f"{name}{i}", (x, -0.012, z))
        r.rotation_euler = (0, rnd.uniform(-0.07, 0.07), 0)
        a = L.link(bpy.data.objects.new(f"{name}{i}_p", pl.data))
        a.parent = r
        a.rotation_euler = (math.pi / 2, 0, 0)
        b = L.link(bpy.data.objects.new(f"{name}{i}_q", qme))
        b.parent = r
        b.location = (0, -0.003, 0)
        b.rotation_euler = (math.pi / 2, 0, 0)
        c = L.link(bpy.data.objects.new(f"{name}{i}_n", pin.data))
        c.parent = r
        c.location = (0, -0.02, size[1] / 2 - 0.05)
        out.append(r)
    pl.data.materials.clear()
    pl.data.materials.append(pm)
    bpy.data.objects.remove(pl, do_unlink=True)
    bpy.data.objects.remove(pin, do_unlink=True)
    return out


def pop_in(root, f, dur=4, s0=0.01):
    """Scale pop (0 -> 1.08 -> 1) starting at frame f."""
    root.scale = (s0,) * 3
    root.keyframe_insert("scale", frame=max(1, f - 1))
    root.scale = (1.08,) * 3
    root.keyframe_insert("scale", frame=f + dur)
    root.scale = (1.0,) * 3
    root.keyframe_insert("scale", frame=f + dur + 3)


def newspaper(loc, rot_z=0.0, size=(0.46, 0.32), name="paper", masthead="ZEITUNG"):
    """Folded generic broadsheet lying flat (XY): paper slab, masthead text, column rules and grey text bars (no real
    title or article text). Returns root."""
    rnd = random.Random(4)
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    w, h = size
    sl = L.prim("cube", loc=(0, 0, 0.004))
    sl.scale = (w / 2, h / 2, 0.004)
    L.assign(sl, mat_paper(name + "_pm", (0.66, 0.62, 0.52)))
    sl.parent = root
    ink = L.mat_principled(name + "_ink", (0.05, 0.045, 0.04), rough=0.8)
    grey = L.mat_principled(name + "_grey", (0.3, 0.28, 0.24), rough=0.9)
    t = L.text3d(masthead, loc=(0, h / 2 - 0.045, 0.0085), rot=(0, 0, 0), size=0.05, extrude=0, mat=ink, name=name + "_mast")
    t.data.font = _font(F_SERIF_B) or t.data.font
    t.data.align_y = "CENTER"
    t.parent = root
    bm = bmesh.new()
    for yy in (h / 2 - 0.078, h / 2 - 0.084):
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5, matrix=Matrix.Translation((0, yy, 0.0084)) @ Matrix.Diagonal((w - 0.04, 0.0018, 1, 1)))
    cols = 4
    cw = (w - 0.05) / cols
    for c in range(cols):
        cx = -w / 2 + 0.025 + cw * (c + 0.5)
        y = h / 2 - 0.1
        while y > -h / 2 + 0.03:
            if rnd.random() < 0.12:
                y -= 0.014
                continue
            ln = cw * 0.86 * (rnd.uniform(0.5, 0.9) if rnd.random() < 0.15 else 1.0)
            bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5,
                                  matrix=Matrix.Translation((cx - (cw * 0.86 - ln) / 2, y, 0.0084)) @ Matrix.Diagonal((ln, 0.0045, 1, 1)))
            y -= 0.0095
    o = L.mesh_from_bm(name + "_lines", bm)
    L.assign(o, grey)
    o.parent = root
    return root


def oil_lamp(loc, energy=60.0, name="oillamp", flicker_n=0):
    """Paraffin table lamp: brass base, glass chimney with flame, warm point light. Returns (root, light)."""
    root = empty(name, loc)
    br = L.mat_principled(name + "_brass", (0.35, 0.24, 0.1), rough=0.35, metal=0.9)
    gl = L.mat_principled(name + "_glass", (0.9, 0.85, 0.75), rough=0.05, emit=(1.0, 0.7, 0.4), emit_strength=0.6, alpha=0.35)
    gl.surface_render_method = "BLENDED"
    for (z, r1, r2, d) in ((0.02, 0.07, 0.07, 0.04), (0.08, 0.055, 0.07, 0.09), (0.15, 0.03, 0.04, 0.05)):
        c = L.prim("cone", loc=(0, 0, z), vertices=20, radius1=r2, radius2=r1, depth=d)
        L.assign(c, br)
        c.parent = root
        c.location = (0, 0, z)
    ch = L.prim("cyl", loc=(0, 0, 0.26), vertices=20, radius=0.032, depth=0.18)
    L.assign(ch, gl)
    ch.parent = root
    ch.location = (0, 0, 0.26)
    ch.visible_shadow = False
    fl = L.prim("sphere", loc=(0, 0, 0.21), radius=0.012, segments=10, ring_count=6)
    fl.scale = (1, 1, 2.0)
    L.assign(fl, L.mat_emission(name + "_flame", (1.0, 0.65, 0.25), 25))
    fl.parent = root
    fl.location = (0, 0, 0.21)
    fl.visible_shadow = False
    pt = L.point((0, 0, 0.23), energy=energy, color=(1.0, 0.62, 0.3), radius=0.03, name=name + "_pt")
    pt.parent = root
    pt.location = (0, 0, 0.23)
    if flicker_n:
        L.flicker(pt, flicker_n, depth=0.12, rate=0.5, seed=4)
    return root, pt


def laptop(loc, rot_z=0.0, open_deg=105, screen_color=(0.45, 0.62, 0.9), strength=2.5, name="laptop"):
    """Generic modern laptop: dark base + lid with a glowing (abstract, text-free) screen. Screen faces -Y locally."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_principled(name + "_m", (0.06, 0.065, 0.07), rough=0.35, metal=0.6)
    b = L.prim("cube", loc=(0, 0, 0.009))
    b.scale = (0.17, 0.12, 0.009)
    L.assign(b, m)
    b.parent = root
    kb = L.prim("plane", loc=(0, 0.015, 0.0185), size=1)
    kb.scale = (0.3, 0.1, 1)
    L.assign(kb, L.mat_principled(name + "_kb", (0.015, 0.015, 0.018), rough=0.6))
    kb.parent = root
    hinge = empty(name + "_hinge", (0, 0.12, 0.018), root)
    hinge.rotation_euler = (math.radians(open_deg - 90) * -1 + 0, 0, 0)
    lid = L.prim("cube", loc=(0, 0, 0.115))
    lid.scale = (0.17, 0.006, 0.115)
    L.assign(lid, m)
    lid.parent = hinge
    lid.location = (0, 0.0, 0.115)
    sm, n, l = L._mat(name + "_scr")
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    tc = n.new("ShaderNodeTexCoord")
    wv = n.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "Y"
    wv.inputs["Scale"].default_value = 3.0
    l.new(tc.outputs["UV"], wv.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (screen_color[0] * 0.5, screen_color[1] * 0.5, screen_color[2] * 0.5, 1)
    ramp.color_ramp.elements[1].color = (*screen_color, 1)
    l.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    e = n.new("ShaderNodeEmission")
    e.inputs[1].default_value = strength
    l.new(ramp.outputs["Color"], e.inputs[0])
    l.new(e.outputs[0], n["Material Output"].inputs["Surface"])
    sc = L.prim("plane", loc=(0, 0, 0), size=1, rot=(math.pi / 2, 0, 0))
    sc.scale = (0.31, 0.2, 1)
    L.assign(sc, sm)
    sc.parent = hinge
    sc.location = (0, -0.0065, 0.118)
    return root, hinge


def case_folder(loc, rot_z=0.0, size=(0.34, 0.25), name="folder", color=(0.5, 0.4, 0.22), label="AKTE"):
    """Thick manila case file with a stack of yellowed pages; cover hinged on the local -X edge (animate
    out['cover'].rotation_euler.y from 0 to -pi). Returns dict."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    w, h = size
    fm = L.mat_noise_surface(name + "_m", tuple(c * 0.75 for c in color), color, scale=20, bump=0.08, voronoi=False, rough=0.8)
    back = L.prim("cube", loc=(0, 0, 0.002))
    back.scale = (w / 2, h / 2, 0.002)
    L.assign(back, fm)
    back.parent = root
    st = L.prim("cube", loc=(0.004, 0, 0.022))
    st.scale = (w / 2 - 0.01, h / 2 - 0.008, 0.018)
    L.assign(st, mat_paper(name + "_pages", (0.62, 0.56, 0.4)))
    st.parent = root
    hinge = empty(name + "_hinge", (-w / 2, 0, 0.042), root)
    cv = L.prim("cube", loc=(0, 0, 0))
    cv.scale = (w / 2, h / 2, 0.002)
    L.assign(cv, fm)
    cv.parent = hinge
    cv.location = (w / 2, 0, 0)
    ink = L.mat_principled(name + "_ink", (0.08, 0.05, 0.03), rough=0.8)
    lb = L.prim("plane", loc=(0, 0, 0), size=1)
    lb.scale = (0.16, 0.06, 1)
    L.assign(lb, mat_paper(name + "_lab", (0.75, 0.72, 0.62)))
    lb.parent = hinge
    lb.location = (w / 2, 0.04, 0.0025)
    t = L.text3d(label, loc=(0, 0, 0), rot=(0, 0, 0), size=0.03, extrude=0, mat=ink, name=name + "_t")
    t.data.font = _font(F_SERIF_B) or t.data.font
    t.data.align_y = "CENTER"
    t.parent = hinge
    t.location = (w / 2, 0.04, 0.003)
    # top page with typed-text bars (generic)
    bm = bmesh.new()
    rnd = random.Random(2)
    y = h / 2 - 0.035
    while y > -h / 2 + 0.03:
        ln = (w - 0.07) * (rnd.uniform(0.4, 0.95) if rnd.random() < 0.3 else 0.95)
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5,
                              matrix=Matrix.Translation((-w / 2 + 0.035 + ln / 2, y, 0.0405)) @ Matrix.Diagonal((ln, 0.004, 1, 1)))
        y -= 0.011 if rnd.random() > 0.1 else 0.022
    o = L.mesh_from_bm(name + "_lines", bm)
    L.assign(o, L.mat_principled(name + "_lm", (0.22, 0.2, 0.17), rough=0.9))
    o.parent = root
    return {"root": root, "cover": hinge}


# ============================================================================ MURDER-06 (Mary Celeste, 1872) builders
# Brigantine (lofted tapered hull, plank deck, deckhouse, foremast with square yards/sails, mainmast with gaff sail, jib,
# bowsprit, rigging, stern davits with empty falls, wheel, transom name), swell sea, barrels, sounding rod, deck pump,
# lifeboat, legend cabin props, deerstalker, compositor sepia/grain grade (legend scenes).
# Ship layout: bow +X, stern -X, waterline z=0, deck z=DECK_Z, length 31 m (x -15.5..15.5), beam 7.5 m.

SHIP_L = 31.0
SHIP_B = 7.5
DECK_Z = 1.5


def _hull_hw(x):
    """Half-beam at the sheer for station x (bow +X narrows to 0.15 of max, stern transom ~0.72)."""
    t = (x + SHIP_L / 2) / SHIP_L  # 0 stern .. 1 bow
    if t < 0.35:
        k = 0.72 + 0.28 * math.sin(t / 0.35 * math.pi / 2)
    elif t < 0.6:
        k = 1.0
    else:
        u = (t - 0.6) / 0.4
        k = 1.0 - 0.85 * u ** 1.6
    return SHIP_B / 2 * k


def _hull_top(x):
    t = (x + SHIP_L / 2) / SHIP_L
    return 2.15 + 0.6 * max(0.0, (t - 0.55) / 0.45) ** 2 + 0.25 * max(0.0, (0.2 - t) / 0.2) ** 2


def mat_hull(name="hull", base=(0.028, 0.025, 0.022), stripe=(0.72, 0.7, 0.64), bottom=(0.06, 0.035, 0.025), stripe_z=(0.35, 0.6)):
    """Tarred planking (horizontal seams by object Z) with a white band above the waterline and dark bottom paint."""
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    sp = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sp.inputs[0])
    z = sp.outputs["Z"]
    seam = _mathn(n, l, "LESS_THAN", _mathn(n, l, "FRACT", _mathn(n, l, "DIVIDE", z, 0.22)), 0.07)
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.3, 3, 3)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    l.new(mp.outputs[0], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*base, 1)
    ramp.color_ramp.elements[1].color = (base[0] * 2.6, base[1] * 2.4, base[2] * 2.2, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    col = ramp.outputs["Color"]
    mx = n.new("ShaderNodeMix"); mx.data_type = "RGBA"
    l.new(_band(n, l, z, stripe_z[0], stripe_z[1]), mx.inputs[0])
    l.new(col, mx.inputs[6]); mx.inputs[7].default_value = (*stripe, 1)
    mx2 = n.new("ShaderNodeMix"); mx2.data_type = "RGBA"
    l.new(_mathn(n, l, "LESS_THAN", z, 0.05), mx2.inputs[0])
    l.new(mx.outputs[2], mx2.inputs[6]); mx2.inputs[7].default_value = (*bottom, 1)
    mx3 = n.new("ShaderNodeMix"); mx3.data_type = "RGBA"
    l.new(_mathn(n, l, "MULTIPLY", seam, 0.6), mx3.inputs[0])
    l.new(mx2.outputs[2], mx3.inputs[6]); mx3.inputs[7].default_value = (0.0, 0.0, 0.0, 1)
    l.new(mx3.outputs[2], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.6
    return m


def mat_canvas_sail(name="sail", c=(0.62, 0.6, 0.52), emit=0.0):
    m = L.mat_noise_surface(name, (c[0] * 0.78, c[1] * 0.76, c[2] * 0.7), c, scale=4, bump=0.08, voronoi=False, rough=0.9)
    p = m.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in p.inputs:
        p.inputs["Transmission Weight"].default_value = 0.0
    if "Subsurface Weight" in p.inputs:
        p.inputs["Subsurface Weight"].default_value = 0.0
    if emit:
        p.inputs["Emission Color"].default_value = (*c, 1)
        p.inputs["Emission Strength"].default_value = emit
    return m


def _sail_mesh(name, corners, bulge=0.6, nu=10, nv=10, normal=(0, 1, 0), mat=None, sag=0.0):
    """Bilinear patch between 4 corners (top-left, top-right, bottom-right, bottom-left) pushed along `normal` by a
    sin*sin bulge. sag lowers the bottom edge centre (slack sail)."""
    a, b, c, d = [Vector(q) for q in corners]
    nv_ = Vector(normal)
    verts, faces = [], []
    for j in range(nv + 1):
        v = j / nv
        for i in range(nu + 1):
            u = i / nu
            top = a.lerp(b, u)
            bot = d.lerp(c, u)
            p = top.lerp(bot, v)
            p += nv_ * bulge * math.sin(math.pi * u) * math.sin(math.pi * min(1.0, v * 0.85 + 0.15))
            p.z += sag * math.sin(math.pi * u) * v ** 2
            verts.append(p)
    for j in range(nv):
        for i in range(nu):
            k = j * (nu + 1) + i
            faces.append((k, k + 1, k + nu + 2, k + nu + 1))
    return mesh_obj(name, verts, faces, mat=mat, smooth=True)


def _rope(name, pts, r=0.02, mat=None):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    for seg in pts:
        sp = cu.splines.new("POLY")
        sp.points.add(len(seg) - 1)
        for k, q in enumerate(seg):
            sp.points[k].co = (*q, 1)
    cu.bevel_depth = r
    cu.bevel_resolution = 1
    o = L.link(bpy.data.objects.new(name, cu))
    o.data.materials.append(mat or L.mat_principled(name + "_m", (0.06, 0.05, 0.04), rough=0.8))
    return o


def brigantine(name="ship", sails="half", fill=0.0, davit_falls=True, lifeboat=False, deck_props=True, wheel=True):
    """Two-masted brigantine (~31 m). sails: 'half' (lower topsail + jib set slack, course & topgallant furled,
    gaff sail set) | 'full' (filled) | 'none'. fill 0..1 adds bulge. Returns dict of parts; root at waterline centre."""
    root = empty(name)
    P = {"root": root}
    wood = mat_hull(name + "_hull")
    # ---- lofted hull: stations along X, section points from sheer (y=hw, z=top) round the bilge to the keel
    nx = 40
    sec = [(1.0, 1.0), (1.0, 0.55), (0.985, 0.0), (0.93, -0.35), (0.78, -0.65), (0.5, -0.88), (0.18, -1.0), (0.0, -1.0)]
    keel = -2.3
    verts, faces = [], []
    xs = [-SHIP_L / 2 + SHIP_L * i / nx for i in range(nx + 1)]
    ns = len(sec) * 2 - 1
    for x in xs:
        hw = _hull_hw(x)
        top = _hull_top(x)
        t = (x + SHIP_L / 2) / SHIP_L
        kz = keel * (1 - 0.55 * max(0, (t - 0.8) / 0.2) ** 1.5) * (1 - 0.25 * max(0, (0.1 - t) / 0.1))
        ring = []
        for (fy, fz) in sec:
            z = top * fz if fz > 0 else kz * -fz
            ring.append((fy, z))
        full = [(hw * fy, z) for fy, z in ring] + [(-hw * fy, z) for fy, z in reversed(ring[:-1])]
        for (y, z) in full:
            verts.append((x, y, z))
    for i in range(nx):
        for j in range(ns - 1):
            a = i * ns + j
            faces.append((a, a + 1, a + ns + 1, a + ns))
    # transom cap at stern + stem cap
    faces.append(tuple(range(ns - 1, -1, -1)))
    faces.append(tuple(nx * ns + k for k in range(ns)))
    hull = mesh_obj(name + "_hullmesh", verts, faces, mat=wood)
    solidify(hull, 0.08)
    hull.parent = root
    P["hull"] = hull
    # ---- deck
    deckm = mat_planks(name + "_deckm", c1=(0.16, 0.13, 0.095), c2=(0.3, 0.25, 0.19), width=0.16, axis="Y", rough=0.8)
    dv, df = [], []
    for x in xs:
        hw = _hull_hw(x) * 0.97
        dv += [(x, -hw, DECK_Z), (x, hw, DECK_Z)]
    for i in range(nx):
        df.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    deck = mesh_obj(name + "_deck", dv, df, mat=deckm)
    deck.parent = root
    P["deck"] = deck
    # rail cap
    rv = [[(x, _hull_hw(x), _hull_top(x) + 0.04) for x in xs], [(x, -_hull_hw(x), _hull_top(x) + 0.04) for x in xs]]
    _rope(name + "_rail", rv, r=0.07, mat=L.mat_principled(name + "_railm", (0.09, 0.06, 0.04), rough=0.6)).parent = root
    dark = L.mat_principled(name + "_dark", (0.05, 0.04, 0.03), rough=0.7)
    paint = L.mat_noise_surface(name + "_paint", (0.4, 0.38, 0.33), (0.6, 0.57, 0.5), scale=6, bump=0.15, voronoi=False)
    # deckhouse aft of the mainmast
    dh = L.prim("cube", loc=(-9.0, 0, DECK_Z + 0.8))
    dh.scale = (3.0, 2.0, 0.8)
    L.assign(dh, paint)
    dh.parent = root
    dhr = L.prim("cube", loc=(-9.0, 0, DECK_Z + 1.65))
    dhr.scale = (3.15, 2.15, 0.06)
    L.assign(dhr, dark)
    dhr.parent = root
    for xx in (-10.8, -9.0, -7.2):
        w = L.prim("cube", loc=(xx, -2.02, DECK_Z + 1.0))
        w.scale = (0.25, 0.03, 0.2)
        L.assign(w, L.mat_principled(name + "_win", (0.01, 0.012, 0.012), rough=0.1))
        w.parent = root
    # hatches
    for (hx, hl) in ((2.0, 2.4), (8.5, 1.6)):
        h = L.prim("cube", loc=(hx, 0, DECK_Z + 0.25))
        h.scale = (hl / 2, 1.1, 0.25)
        L.assign(h, dark)
        h.parent = root
    P["main_hatch"] = Vector((2.0, 0, DECK_Z + 0.5))
    # masts, yards, bowsprit
    spar = L.mat_principled(name + "_spar", (0.14, 0.1, 0.06), rough=0.6)
    FX, MXm = 6.0, -3.0
    for (mx_, ht, nm) in ((FX, 26.0, "fore"), (MXm, 27.0, "main")):
        m = L.prim("cone", loc=(mx_, 0, DECK_Z + ht / 2), vertices=10, radius1=0.2, radius2=0.09, depth=ht)
        L.assign(m, spar)
        m.parent = root
    bs = L.prim("cone", loc=(0, 0, 0), vertices=8, radius1=0.17, radius2=0.07, depth=8.0)
    bs.location = (15.5 + 3.0, 0, 3.4)
    bs.rotation_euler = (0, math.radians(90 - 14), 0)
    L.assign(bs, spar)
    bs.parent = root
    bow_tip = Vector((15.5 + 3.0 + 3.9 * math.cos(math.radians(14)), 0, 3.4 + 3.9 * math.sin(math.radians(14))))
    sailm = mat_canvas_sail(name + "_sail")
    furl = L.mat_principled(name + "_furl", (0.5, 0.48, 0.42), rough=0.9)
    yards = ((8.0, 13.0, "course"), (12.5, 11.0, "topsail"), (16.8, 8.5, "tgallant"), (20.0, 6.0, "royal"))
    for (z, ln, nm) in yards:
        y = L.prim("cyl", loc=(FX, 0, DECK_Z + z), vertices=8, radius=0.09, depth=ln, rot=(math.pi / 2, 0, 0))
        L.assign(y, spar)
        y.parent = root
    setsails = {"half": ("topsail",), "full": ("course", "topsail", "tgallant"), "none": ()}[sails]
    b = 0.5 + 1.8 * fill
    for k, (z, ln, nm) in enumerate(yards[:3]):
        if nm in setsails:
            zb = yards[k - 1][0] + 0.4 if k > 0 else 2.8
            lnb = yards[k - 1][1] if k > 0 else ln * 1.1
            s = _sail_mesh(f"{name}_{nm}", [(FX + 0.15, -ln / 2 + 0.2, DECK_Z + z), (FX + 0.15, ln / 2 - 0.2, DECK_Z + z),
                                            (FX + 0.15 + 0.4, lnb / 2 - 0.3, DECK_Z + zb), (FX + 0.15 + 0.4, -lnb / 2 + 0.3, DECK_Z + zb)],
                           bulge=b, normal=(1, 0, 0), mat=sailm, sag=(0.0 if fill > 0.5 else 0.6))
            s.parent = root
            P[nm] = s
        else:
            f = L.prim("cyl", loc=(FX + 0.15, 0, DECK_Z + z - 0.2), vertices=8, radius=0.22, depth=ln * 0.85, rot=(math.pi / 2, 0, 0))
            L.assign(f, furl)
            f.parent = root
    # main: boom + gaff + gaff sail
    boom0, boom1 = Vector((MXm - 0.3, 0, DECK_Z + 3.0)), Vector((-15.0, 0, DECK_Z + 3.4))
    gaff0, gaff1 = Vector((MXm - 0.3, 0, DECK_Z + 14.5)), Vector((-11.5, 0, DECK_Z + 18.5))
    for nm_, a, c in (("boom", boom0, boom1), ("gaff", gaff0, gaff1)):
        d = c - a
        o = L.prim("cyl", loc=(a + c) / 2, vertices=8, radius=0.1, depth=d.length)
        o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        L.assign(o, spar)
        o.parent = root
    if sails != "none":
        g = _sail_mesh(name + "_gaffsail", [(gaff0.x - 0.2, 0, gaff0.z), (gaff1.x + 0.3, 0, gaff1.z - 0.2), (boom1.x + 0.4, 0, boom1.z + 0.2),
                                            (boom0.x - 0.2, 0, boom0.z + 0.2)], bulge=0.4 + 1.6 * fill, normal=(0, 1, 0), mat=sailm,
                       sag=0.0)
        g.parent = root
        P["gaffsail"] = g
        j = _sail_mesh(name + "_jib", [(FX + 0.4, 0, DECK_Z + 15.5), (FX + 0.5, 0, DECK_Z + 15.3), (bow_tip.x - 0.4, 0, bow_tip.z + 0.2),
                                       (FX + 1.2, 0, DECK_Z + 2.2)], bulge=0.3 + 1.2 * fill, normal=(0, 1, 0), mat=sailm, nu=8, nv=8)
        j.parent = root
    # rigging
    rp = []
    ft, mt = Vector((FX, 0, DECK_Z + 25.6)), Vector((MXm, 0, DECK_Z + 26.6))
    rp.append([tuple(ft), tuple(bow_tip)])
    rp.append([(FX, 0, DECK_Z + 16.0), tuple(bow_tip + Vector((-1.5, 0, -0.4)))])
    rp.append([tuple(mt), (FX, 0, DECK_Z + 21.0)])
    for s_ in (-1, 1):
        for (mx_, top, xs_) in ((FX, 20.0, (FX - 1.5, FX - 0.5, FX + 0.5)), (MXm, 21.0, (MXm - 1.6, MXm - 0.6, MXm + 0.4))):
            for xx in xs_:
                rp.append([(mx_, s_ * 0.15, DECK_Z + top), (xx, s_ * (_hull_hw(xx) + 0.05), _hull_top(xx))])
        rp.append([tuple(mt + Vector((0, s_ * 0.1, -2))), (-14.0, s_ * (_hull_hw(-14.0) + 0.05), _hull_top(-14.0))])
    _rope(name + "_rig", rp, r=0.025).parent = root
    # stern davits with empty falls
    davm = L.mat_principled(name + "_davit", (0.08, 0.075, 0.07), rough=0.5, metal=0.6)
    P["falls"] = []
    for s_ in (-1, 1):
        yy = s_ * 1.6
        pts = [(-14.6, yy, _hull_top(-14.6)), (-15.0, yy, 3.6), (-15.6, yy, 4.2), (-16.6, yy, 4.25)]
        d = _rope(f"{name}_davit{s_}", [pts], r=0.07, mat=davm)
        d.parent = root
        if davit_falls:
            piv = empty(f"{name}_fallpiv{s_}", (-16.5, yy, 4.2), root)
            fr = _rope(f"{name}_fall{s_}", [[(0, 0, 0), (0.02, 0.0, -0.8), (-0.03, 0, -1.6)], [(0.12, 0, 0), (0.13, 0, -1.2)]], r=0.018,
                       mat=L.mat_principled(name + "_rope", (0.32, 0.27, 0.18), rough=0.9))
            fr.parent = piv
            blk = L.prim("cube", loc=(0, 0, -0.12))
            blk.scale = (0.08, 0.06, 0.12)
            L.assign(blk, spar)
            blk.parent = piv
            P["falls"].append(piv)
    # wheel
    if wheel:
        ped = L.prim("cube", loc=(-13.6, 0, DECK_Z + 0.5))
        ped.scale = (0.2, 0.25, 0.5)
        L.assign(ped, dark)
        ped.parent = root
        wh = empty(name + "_wheel", (-13.35, 0, DECK_Z + 1.25), root)
        rim = L.prim("torus", loc=(0, 0, 0), major_radius=0.55, minor_radius=0.035, rot=(0, math.pi / 2, 0))
        L.assign(rim, spar)
        rim.parent = wh
        hub = L.prim("cyl", loc=(0, 0, 0), vertices=10, radius=0.08, depth=0.12, rot=(0, math.pi / 2, 0))
        L.assign(hub, spar)
        hub.parent = wh
        for k in range(8):
            a = math.pi * 2 * k / 8
            sp_ = L.prim("cyl", loc=(0, 0.4 * math.cos(a), 0.4 * math.sin(a)), vertices=6, radius=0.022, depth=0.95)
            sp_.rotation_euler = (a + math.pi / 2, 0, 0)
            sp_.location = (0, 0.37 * math.cos(a), 0.37 * math.sin(a))
            L.assign(sp_, spar)
            sp_.parent = wh
            sp_.scale = (1, 1, 1)
        P["wheel"] = wh
    # transom name board
    nm_m = L.mat_principled(name + "_name", (0.85, 0.82, 0.72), rough=0.5, emit=(0.5, 0.48, 0.42), emit_strength=0.15)
    t = L.text3d("MARY CELESTE", loc=(-15.5 - 0.1, 0, 1.25), rot=(math.pi / 2, 0, -math.pi / 2), size=0.42, extrude=0.01, mat=nm_m,
                 name=name + "_nametxt")
    t.data.font = _font(F_SERIF_B) or t.data.font
    t.data.align_y = "CENTER"
    t.parent = root
    if deck_props:
        pump = deck_pump((-1.0, 1.2, DECK_Z), name=name + "_pump")
        pump.parent = root
    return P


def ship_bob(root, n, amp=(0.25, 0.02, 0.035), period=(5.5, 7.0, 6.2), base_loc=None, base_rot=(0, 0, 0), travel=None, seed=1):
    """Swell motion: heave z, roll x, pitch y (sine), optional linear travel (from, to)."""
    bl = Vector(base_loc or root.location)
    for f in range(1, n + 1, 3):
        t = f / FPS
        k = (f - 1) / max(1, n - 1)
        p = bl + (Vector(travel[1]) - Vector(travel[0])) * k if travel else bl.copy()
        p.z += amp[0] * math.sin(2 * math.pi * t / period[0] + seed)
        root.location = p
        root.rotation_euler = (base_rot[0] + amp[1] * math.sin(2 * math.pi * t / period[1] + seed * 2),
                               base_rot[1] + amp[2] * math.sin(2 * math.pi * t / period[2] + seed * 3), base_rot[2])
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_euler", frame=f)


def swell_sea(size=600, res=160, center=(0, 0, 0), color=(0.03, 0.045, 0.045), n=100, height=0.55, width=14.0, speed=0.12,
              name="sea"):
    """Grid sea with a Wave modifier (long, near-straight swell from a far-away origin) + moving normal noise material.
    Keeps a location key so bake_static does not freeze the wave."""
    s = sea(size=(1, 1), loc=(0, 0, -50), color=color, n=n, name=name + "_tmp")
    m = s.data.materials[0]
    bpy.data.objects.remove(s, do_unlink=True)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=res, y_segments=res, size=size / 2)
    o = L.mesh_from_bm(name, bm)
    o.location = center
    L.assign(o, m)
    smooth_obj(o)
    w = o.modifiers.new("swell", "WAVE")
    w.height = height
    w.width = width
    w.narrowness = 1.2
    w.speed = speed
    w.start_position_x = -2000
    w.start_position_y = -600
    w.use_normal = False
    w.falloff_radius = 0
    o.keyframe_insert("location", frame=1)
    return o


def barrel_mesh(name="barrel", r=0.32, h=0.95, bulge=0.06, open_top=False):
    """Bulged stave barrel with three dark iron hoops (one mesh, two materials). Mesh datablock for linked copies."""
    seg, rings = 16, 10
    verts, faces, mats = [], [], []
    for j in range(rings + 1):
        v = j / rings
        rr = r + bulge * math.sin(math.pi * v)
        for i in range(seg):
            a = 2 * math.pi * i / seg
            verts.append((rr * math.cos(a), rr * math.sin(a), h * v))
    for j in range(rings):
        for i in range(seg):
            a, b = j * seg + i, j * seg + (i + 1) % seg
            faces.append((a, b, b + seg, a + seg))
            mats.append(1 if j in (1, rings // 2, rings - 2) else 0)
    faces.append(tuple(reversed(range(seg))))
    mats.append(0)
    if not open_top:
        faces.append(tuple(rings * seg + i for i in range(seg)))
        mats.append(2)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.polygons.foreach_set("material_index", mats)
    me.polygons.foreach_set("use_smooth", [True] * len(faces))
    me.update()
    oak = L.mat_noise_surface(name + "_oak", (0.1, 0.06, 0.03), (0.24, 0.15, 0.08), scale=12, bump=0.3, voronoi=False)
    iron = L.mat_principled(name + "_iron", (0.05, 0.045, 0.04), rough=0.5, metal=0.7)
    lid = L.mat_noise_surface(name + "_lid", (0.12, 0.08, 0.045), (0.26, 0.18, 0.1), scale=20, bump=0.2, voronoi=False)
    for mm in (oak, iron, lid):
        me.materials.append(mm)
    return me


def barrel_stacks(rows, me, name="barrels", stencil=(), stencil_mat=None):
    """rows: list of (x0, x1, y, tiers, lying) -> linked barrel copies. Barrels lie along Y when lying=True.
    stencil: list of indices that get an 'ALCOHOL' stencil. Returns list of objects."""
    out = []
    k = 0
    for (x0, x1, y, tiers, lying) in rows:
        dx = 0.78
        cnt = int((x1 - x0) / dx)
        for t in range(tiers):
            for i in range(cnt - (t % 2)):
                x = x0 + dx * (i + 0.5 + 0.5 * (t % 2))
                o = L.link(bpy.data.objects.new(f"{name}{k}", me))
                if lying:
                    o.location = (x, y - 0.48, 0.38 + t * 0.66)
                    o.rotation_euler = (-math.pi / 2, 0, 0)
                else:
                    o.location = (x, y, t * 1.0)
                out.append(o)
                if k in stencil and stencil_mat:
                    tx = L.text3d("ALCOHOL", loc=(0, 0, 0), size=0.09, extrude=0, mat=stencil_mat, name=f"{name}{k}_st")
                    tx.data.font = _font(F_MONO) or tx.data.font
                    tx.data.align_y = "CENTER"
                    tx.parent = o
                    if lying:
                        tx.location = (0, 0, -0.005)
                        tx.rotation_euler = (math.pi, 0, 0)
                        tx.location = (0, 0, -0.002)
                    else:
                        tx.location = (0, -0.385, 0.5)
                        tx.rotation_euler = (math.pi / 2, 0, 0)
                k += 1
    return out


def sounding_rod(loc, rot_z=0.0, name="rod"):
    """Iron sounding rod (1.2 m, notch marks) with a coiled line beside it, lying on deck."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    iron = L.mat_principled(name + "_m", (0.09, 0.085, 0.08), rough=0.4, metal=0.85)
    r = L.prim("cyl", loc=(0, 0, 0.018), vertices=10, radius=0.016, depth=1.2, rot=(0, math.pi / 2, 0))
    L.assign(r, iron)
    r.parent = root
    for k in range(9):
        nt = L.prim("torus", loc=(-0.5 + k * 0.12, 0, 0.018), major_radius=0.018, minor_radius=0.004, rot=(0, math.pi / 2, 0))
        L.assign(nt, iron)
        nt.parent = root
    ey = L.prim("torus", loc=(0.63, 0, 0.018), major_radius=0.03, minor_radius=0.006, rot=(math.pi / 2, 0, 0))
    L.assign(ey, iron)
    ey.parent = root
    rope = L.mat_principled(name + "_rope", (0.36, 0.3, 0.2), rough=0.95)
    coil = []
    for k in range(5):
        rr = 0.18 - k * 0.02
        coil += [(0.95 + rr * math.cos(a), 0.1 + rr * math.sin(a), 0.012 + k * 0.012) for a in [2 * math.pi * q / 24 for q in range(25)]]
    _rope(name + "_coil", [coil, [(0.66, 0, 0.018), (0.8, 0.06, 0.012), (0.95 + 0.18, 0.1, 0.012)]], r=0.011, mat=rope).parent = root
    return root


def deck_pump(loc, dismantled=False, name="pump"):
    """Ship's deck pump: two barrels/cylinders on a base + rocking lever; dismantled=True removes one plunger cap and
    lays parts on deck. Returns root (parts in root['parts'] is not used; children named)."""
    root = empty(name, loc)
    iron = L.mat_principled(name + "_m", (0.12, 0.11, 0.1), rough=0.45, metal=0.7)
    wood = L.mat_noise_surface(name + "_w", (0.1, 0.07, 0.04), (0.22, 0.16, 0.1), scale=10, bump=0.2, voronoi=False)
    base = L.prim("cube", loc=(0, 0, 0.08))
    base.scale = (0.5, 0.3, 0.08)
    L.assign(base, wood)
    base.parent = root
    for k, x in enumerate((-0.22, 0.22)):
        c = L.prim("cyl", loc=(x, 0, 0.55), vertices=14, radius=0.09, depth=0.8)
        L.assign(c, iron)
        c.parent = root
        if not (dismantled and k == 1):
            cap = L.prim("cyl", loc=(x, 0, 0.98), vertices=14, radius=0.11, depth=0.06)
            L.assign(cap, iron)
            cap.parent = root
    post = L.prim("cube", loc=(0, 0, 0.75))
    post.scale = (0.03, 0.06, 0.75)
    L.assign(post, wood)
    post.parent = root
    lev = L.prim("cyl", loc=(0, 0, 1.45), vertices=8, radius=0.025, depth=1.4, rot=(0, math.pi / 2 + (0.0 if not dismantled else 0.25), 0))
    L.assign(lev, wood)
    lev.parent = root
    if dismantled:
        for i, (p, r) in enumerate((((0.8, 0.5, 0.03), (0, math.pi / 2, 0.4)), ((0.6, -0.55, 0.06), (0, 0, 0)), ((-0.7, 0.45, 0.02), (0, math.pi / 2, -0.3)))):
            if i == 1:
                o = L.prim("cyl", loc=p, vertices=14, radius=0.11, depth=0.06)
            else:
                o = L.prim("cyl", loc=p, vertices=10, radius=0.03, depth=0.7, rot=r)
            L.assign(o, iron)
            o.parent = root
    return root


def lifeboat(loc=(0, 0, 0), length=6.0, beam=1.9, name="lifeboat", people=4, color=(0.33, 0.3, 0.26)):
    """Open clinker-ish boat: half-ellipsoid hull (open top), thwarts, faceless seated silhouettes. Bow +X."""
    root = empty(name, loc)
    seg, rings = 24, 8
    verts, faces = [], []
    for j in range(rings + 1):
        v = j / rings  # 0 gunwale .. 1 keel
        for i in range(seg + 1):
            u = i / seg
            x = (u - 0.5) * length
            w = math.sqrt(max(0.0, 1 - (2 * x / length) ** 2)) ** 0.8
            ang = v * math.pi / 2
            y = beam / 2 * w * math.cos(ang)
            z = -0.75 * math.sin(ang) * (0.6 + 0.4 * w) + 0.12 * (2 * x / length) ** 2
            verts.append((x, y, z))
    for j in range(rings):
        for i in range(seg):
            a = j * (seg + 1) + i
            faces.append((a, a + 1, a + seg + 2, a + seg + 1))
    half = len(verts)
    verts += [(x, -y, z) for (x, y, z) in verts]
    faces += [tuple(reversed([q + half for q in f])) for f in faces]
    m = L.mat_noise_surface(name + "_m", tuple(c * 0.7 for c in color), color, scale=8, bump=0.2, voronoi=False)
    h = mesh_obj(name + "_hull", verts, faces, mat=m, smooth=True)
    solidify(h, 0.05)
    h.parent = root
    for x in (-1.2, 0.0, 1.2):
        t = L.prim("cube", loc=(x, 0, -0.2))
        t.scale = (0.12, beam / 2 * 0.85, 0.03)
        L.assign(t, m)
        t.parent = root
    figs = []
    for k in range(people):
        p = L.char_figure(f"{name}_p{k}", color=(0.025, 0.025, 0.028), coat=True, height=1.7)
        p["root"].parent = root
        x = -1.6 + k * 1.05
        p["root"].location = (x, 0.25 * (-1) ** k, -0.95)
        p["root"].rotation_euler = (0, 0, -math.pi / 2 + 0.3 * (-1) ** k)
        for t in ("L", "R"):
            p["hip" + t].rotation_euler = (1.5, 0, 0)
            p["knee" + t].rotation_euler = (-1.5, 0, 0)
            p["shoulder" + t].rotation_euler = (0.5, 0, 0)
            p["elbow" + t].rotation_euler = (0.9, 0, 0)
        p["neck"].rotation_euler = (0.25, 0, 0)
        figs.append(p)
    return root, figs


def deerstalker(loc, rot_z=0.0, name="deerstalker", c1=(0.22, 0.17, 0.1), c2=(0.36, 0.28, 0.16)):
    """Check-wool deerstalker: crown half-sphere, front/back peaks, tied-up ear flaps, top button."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m, n, l = L._mat(name + "_m")
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    ck = n.new("ShaderNodeTexChecker")
    ck.inputs["Scale"].default_value = 18.0
    ck.inputs["Color1"].default_value = (*c1, 1)
    ck.inputs["Color2"].default_value = (*c2, 1)
    l.new(tc.outputs["Object"], ck.inputs["Vector"])
    l.new(ck.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.95
    cr = L.prim("sphere", loc=(0, 0, 0), segments=20, ring_count=10)
    cr.scale = (0.11, 0.1, 0.085)
    bm_ = bmesh.new()
    L.assign(cr, m)
    cr.parent = root
    cut = cr.modifiers.new("cut", "BOOLEAN")
    cutter = L.prim("cube", loc=(0, 0, -0.5))
    cutter.scale = (1, 1, 0.5)
    cutter.hide_render = True
    cutter.hide_viewport = True
    cut.object = cutter
    cut.operation = "DIFFERENCE"
    bm_.free()
    for s in (-1, 1):
        pk = L.prim("cyl", loc=(s * 0.11, 0, 0.005), vertices=16, radius=0.07, depth=0.008)
        pk.scale = (1.0, 1.15, 1)
        pk.rotation_euler = (0, s * -0.2, 0)
        L.assign(pk, m)
        pk.parent = root
        fl = L.prim("cube", loc=(0, s * 0.095, 0.055))
        fl.scale = (0.05, 0.008, 0.04)
        fl.rotation_euler = (s * 0.5, 0, 0)
        L.assign(fl, m)
        fl.parent = root
    bt = L.prim("sphere", loc=(0, 0, 0.087), radius=0.012, segments=8, ring_count=5)
    L.assign(bt, m)
    bt.parent = root
    return root


def legend_grade(sepia=1.0, cold=0.0, grain=0.05, tint=(1.0, 0.72, 0.42), cold_tint=(0.62, 0.7, 0.68), vignette=True):
    """Compositor grade for LEGEND scenes (Blender 5 compositing_node_group): desaturate + sepia multiply, optional
    blend to a cold grey-green (cold 0..1), animated film grain, vignette. Returns dict of keyable sockets
    {'sepia', 'cold', 'grain'}."""
    sc = bpy.context.scene
    ng = bpy.data.node_groups.new("legend_grade", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    n, l = ng.nodes, ng.links
    rl = n.new("CompositorNodeRLayers")
    out = n.new("NodeGroupOutput")
    bw = n.new("CompositorNodeRGBToBW")
    l.new(rl.outputs["Image"], bw.inputs[0])
    sep = n.new("ShaderNodeMix"); sep.data_type = "RGBA"; sep.blend_type = "MULTIPLY"
    sep.inputs[0].default_value = 1.0
    l.new(bw.outputs[0], sep.inputs[6]); sep.inputs[7].default_value = (*tint, 1)
    cld = n.new("ShaderNodeMix"); cld.data_type = "RGBA"; cld.blend_type = "MULTIPLY"
    cld.inputs[0].default_value = 1.0
    l.new(bw.outputs[0], cld.inputs[6]); cld.inputs[7].default_value = (*cold_tint, 1)
    m1 = n.new("ShaderNodeMix"); m1.data_type = "RGBA"
    m1.inputs[0].default_value = sepia
    l.new(rl.outputs["Image"], m1.inputs[6]); l.new(sep.outputs[2], m1.inputs[7])
    m2 = n.new("ShaderNodeMix"); m2.data_type = "RGBA"
    m2.inputs[0].default_value = cold
    l.new(m1.outputs[2], m2.inputs[6]); l.new(cld.outputs[2], m2.inputs[7])
    img = m2.outputs[2]
    tm = n.new("CompositorNodeSceneTime")
    nz = n.new("ShaderNodeTexNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["Scale"].default_value = 600.0
    nz.inputs["Detail"].default_value = 0.0
    l.new(_mathn(n, l, "MULTIPLY", tm.outputs["Frame"], 7.31), nz.inputs["W"])
    gr = n.new("ShaderNodeMix"); gr.data_type = "RGBA"; gr.blend_type = "LINEAR_LIGHT"
    gr.inputs[0].default_value = grain
    l.new(img, gr.inputs[6]); l.new(nz.outputs["Color"], gr.inputs[7])
    img = gr.outputs[2]
    if vignette:
        em = n.new("CompositorNodeEllipseMask")
        try:
            em.inputs["Size"].default_value = (0.95, 0.75)
        except Exception:
            pass
        bl = n.new("CompositorNodeBlur")
        try:
            bl.inputs["Size"].default_value = (60, 60)
        except Exception:
            bl.size_x = bl.size_y = 60
        l.new(em.outputs[0], bl.inputs[0])
        vg = n.new("ShaderNodeMix"); vg.data_type = "RGBA"; vg.blend_type = "MULTIPLY"
        l.new(_mathn(n, l, "SUBTRACT", 1.0, bl.outputs[0]), vg.inputs[0])
        l.new(img, vg.inputs[6]); vg.inputs[7].default_value = (0.35, 0.33, 0.3, 1)
        img = vg.outputs[2]
    l.new(img, out.inputs[0])
    sc.compositing_node_group = ng
    return {"sepia": m1.inputs[0], "cold": m2.inputs[0], "grain": gr.inputs[0], "tree": ng}


# ============================================================================ MURDER-07 (Oetzi): glacier ice, X-ray line art,
# CT diagram, lightbox, CT gantry, Copper Age kit, last-meal props, traveller silhouette. Appended; nothing above changed.

def mat_glacier_ice(name="ice", deep=(0.06, 0.26, 0.46), surf=(0.62, 0.8, 0.92), alpha=0.62, glow=0.35, crack=0.35, scale=2.5):
    """Cloudy blue glacier ice: noise-mixed colour, partial alpha (shows what lies beneath, blurred by cloudiness),
    voronoi crack bump, faint blue self-glow (subsurface feel). Works on horizontal slabs and vertical panes."""
    m, n, l = L._mat(name)
    p = n["Principled BSDF"]
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 8
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*deep, 1)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (*surf, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.12
    ra = n.new("ShaderNodeMapRange")
    ra.inputs["From Min"].default_value = 0.3
    ra.inputs["From Max"].default_value = 0.7
    ra.inputs["To Min"].default_value = max(0.0, alpha - 0.25)
    ra.inputs["To Max"].default_value = min(1.0, alpha + 0.25)
    l.new(nz.outputs["Fac"], ra.inputs["Value"])
    l.new(ra.outputs["Result"], p.inputs["Alpha"])
    p.inputs["Emission Color"].default_value = (*deep, 1)
    p.inputs["Emission Strength"].default_value = glow
    vo = n.new("ShaderNodeTexVoronoi")
    vo.feature = "DISTANCE_TO_EDGE"
    vo.inputs["Scale"].default_value = scale * 1.6
    l.new(tc.outputs["Object"], vo.inputs["Vector"])
    bp = n.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = crack
    l.new(vo.outputs["Distance"], bp.inputs["Height"])
    nz2 = n.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = scale * 12
    l.new(tc.outputs["Object"], nz2.inputs["Vector"])
    bp2 = n.new("ShaderNodeBump")
    bp2.inputs["Strength"].default_value = 0.12
    l.new(nz2.outputs["Fac"], bp2.inputs["Height"])
    l.new(bp2.outputs["Normal"], bp.inputs["Normal"])
    l.new(bp.outputs["Normal"], p.inputs["Normal"])
    try:
        m.surface_render_method = "DITHERED"
    except Exception:
        pass
    return m


def abstract_form(loc, length=1.1, rot_z=0.3, color=(0.07, 0.04, 0.022), name="form"):
    """Unreadable dark-brown lump (a 'shoulder line' under ice): two smooth stretched ellipsoids, no limbs/face."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_principled(name + "_m", color, rough=0.9)
    for k, (x, sx, sy, sz) in enumerate(((0.0, length * 0.5, 0.17, 0.09), (length * 0.42, length * 0.22, 0.13, 0.07))):
        o = L.prim("sphere", loc=(x, 0, 0), segments=20, ring_count=10, name=f"{name}_{k}")
        o.scale = (sx, sy, sz)
        L.assign(o, m)
        L.smooth(o)
        o.parent = root
    return root


def ice_sheet(loc=(0, 0, 0), size=(6.0, 6.0), thick=0.35, mat=None, glow=(0.05, 0.3, 0.6), glow_strength=0.8, form=True,
              form_loc=(0.15, 0.25), form_rot=0.35, name="icesheet"):
    """Horizontal ice slab (top at loc.z) over a blue glowing 'deep ice' floor; optional abstract dark form inside."""
    x, y, z = loc
    top = L.prim("plane", loc=(x, y, z), size=1, name=name)
    top.scale = (size[0], size[1], 1)
    L.apply_scale(top)
    sd = top.modifiers.new("sub", "SUBSURF")
    sd.levels = sd.render_levels = 2
    sd.subdivision_type = "SIMPLE"
    L.add_displace(top, strength=0.03, scale=0.6, name=name + "_d")
    L.assign(top, mat or mat_glacier_ice(name + "_m"))
    fl = L.prim("plane", loc=(x, y, z - thick), size=1, name=name + "_deep")
    fl.scale = (size[0] * 1.2, size[1] * 1.2, 1)
    m2, n2, l2 = L._mat(name + "_deepm")
    p2 = n2["Principled BSDF"]
    tc = n2.new("ShaderNodeTexCoord")
    nz = n2.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.6
    l2.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = n2.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (glow[0] * 0.4, glow[1] * 0.4, glow[2] * 0.4, 1)
    ramp.color_ramp.elements[1].color = (*glow, 1)
    l2.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    l2.new(ramp.outputs["Color"], p2.inputs["Emission Color"])
    p2.inputs["Emission Strength"].default_value = glow_strength
    p2.inputs["Base Color"].default_value = (*glow, 1)
    L.assign(fl, m2)
    out = {"top": top, "deep": fl}
    if form:
        out["form"] = abstract_form((x + form_loc[0], y + form_loc[1], z - thick * 0.55), rot_z=form_rot, name=name + "_form")
    return out


def melt_beads(center, size=(1.0, 1.0), count=120, seed=3, name="beads", rmin=0.004, rmax=0.02, z_of=None):
    """Meltwater beads lying on a horizontal surface (flattened hemispheres, glossy). center.z = surface height."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    for i in range(count):
        r = rnd.uniform(rmin, rmax) * (1.0 if rnd.random() > 0.15 else 1.8)
        x = center[0] + rnd.uniform(-0.5, 0.5) * size[0]
        y = center[1] + rnd.uniform(-0.5, 0.5) * size[1]
        z = z_of(x, y) if z_of else center[2]
        res = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=r)
        for v in res["verts"]:
            v.co.z = max(0.0, v.co.z) * 0.45
            v.co.y *= rnd.uniform(1.0, 1.6)
            v.co += Vector((x, y, z))
    o = L.mesh_from_bm(name, bm)
    m = L.mat_principled(name + "_m", (0.5, 0.65, 0.75), rough=0.03)
    p = m.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in p.inputs:
        p.inputs["Transmission Weight"].default_value = 0.6
    p.inputs["Coat Weight"].default_value = 1.0 if "Coat Weight" in p.inputs else 0
    L.assign(o, m)
    L.smooth(o)
    o.visible_shadow = False
    return o


def ice_axe(loc, rot=(0, 0, 0), name="iceaxe", length=0.7, shaft=(0.55, 0.12, 0.06)):
    """Mountaineering ice axe: shaft + steel head (pick + adze). Root at the spike (bottom)."""
    root = empty(name, loc)
    root.rotation_euler = rot
    sm = L.mat_principled(name + "_s", shaft, rough=0.45)
    hm = L.mat_principled(name + "_h", (0.5, 0.52, 0.55), rough=0.3, metal=1.0)
    s = L.prim("cyl", loc=(0, 0, length / 2), vertices=10, radius=0.016, depth=length)
    L.assign(s, sm)
    s.parent = root
    h = L.prim("cube", loc=(0.04, 0, length + 0.01))
    h.scale = (0.14, 0.012, 0.02)
    L.assign(h, hm)
    h.parent = root
    pk = L.prim("cone", loc=(0.21, 0, length - 0.005), vertices=4, radius1=0.02, radius2=0.002, depth=0.09, rot=(0, math.radians(100), 0))
    L.assign(pk, hm)
    pk.parent = root
    sp = L.prim("cone", loc=(0, 0, -0.03), vertices=6, radius1=0.016, radius2=0.002, depth=0.06, rot=(math.pi, 0, 0))
    L.assign(sp, hm)
    sp.parent = root
    return root


def helicopter(loc=(0, 0, 0), rot_z=0.0, body=(0.42, 0.05, 0.04), stripe=(0.85, 0.85, 0.82), name="heli"):
    """Simple light helicopter: rounded cabin, dark window band, tail boom + fin, skids, two-blade rotor (key 'rotor')."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    bm_ = L.mat_principled(name + "_b", body, rough=0.35)
    wm = L.mat_principled(name + "_w", (0.02, 0.025, 0.03), rough=0.08)
    km = L.mat_principled(name + "_k", (0.05, 0.05, 0.055), rough=0.5, metal=0.6)
    sm = L.mat_principled(name + "_st", stripe, rough=0.4)
    cab = L.prim("sphere", loc=(0, 0, 1.25), segments=24, ring_count=12)
    cab.scale = (1.55, 0.85, 0.85)
    L.assign(cab, bm_)
    L.smooth(cab)
    win = L.prim("sphere", loc=(0.55, 0, 1.38), segments=24, ring_count=12)
    win.scale = (1.05, 0.8, 0.62)
    L.assign(win, wm)
    L.smooth(win)
    band = L.prim("cube", loc=(-0.3, 0, 1.0))
    band.scale = (1.0, 0.86, 0.06)
    L.assign(band, sm)
    boom = L.prim("cone", loc=(-2.6, 0, 1.45), vertices=12, radius1=0.24, radius2=0.09, depth=3.2, rot=(0, math.radians(-90), 0))
    L.assign(boom, bm_)
    fin = L.prim("cube", loc=(-4.15, 0, 1.85))
    fin.scale = (0.28, 0.03, 0.5)
    fin.rotation_euler = (0, math.radians(-18), 0)
    L.assign(fin, bm_)
    mast = L.prim("cyl", loc=(0, 0, 2.15), vertices=8, radius=0.07, depth=0.3)
    L.assign(mast, km)
    for o in (cab, win, band, boom, fin, mast):
        o.parent = root
    for sy in (-0.7, 0.7):
        sk = L.prim("cyl", loc=(0.0, sy, 0.06), vertices=8, radius=0.04, depth=2.6, rot=(0, math.radians(90), 0))
        L.assign(sk, km)
        sk.parent = root
        for sx in (-0.5, 0.6):
            st = L.prim("cyl", loc=(sx, sy * 0.85, 0.35), vertices=6, radius=0.03, depth=0.6, rot=(math.radians(-12 if sy > 0 else 12), 0, 0))
            L.assign(st, km)
            st.parent = root
    rotor = empty(name + "_rotor", (0, 0, 2.32), parent=root)
    bl = L.prim("cube", loc=(0, 0, 0))
    bl.scale = (4.2, 0.1, 0.015)
    L.assign(bl, km)
    bl.parent = rotor
    tr = L.prim("cube", loc=(-4.2, 0.08, 1.95))
    tr.scale = (0.03, 0.02, 0.5)
    L.assign(tr, km)
    tr.parent = root
    return {"root": root, "rotor": rotor}


def kneel_pose(parts, lean=0.35, reach=0.0, frame=None):
    """Kneeling on both knees, torso leaning forward over the ground (figure faces +Y). reach: arms forward/down."""
    s = parts["torso"].scale.z / 0.33 if "torso" in parts else 1.0
    pel = parts["pelvis"]
    pel.location.z = 0.56 * s
    pel.rotation_euler = (-lean, 0, 0)
    for t in ("L", "R"):
        parts["hip" + t].rotation_euler = (lean + 0.15, 0, 0)
        parts["knee" + t].rotation_euler = (-1.62, 0, 0)
        parts["shoulder" + t].rotation_euler = (0.5 + reach, 0, (0.12 if t == "L" else -0.12))
        parts["elbow" + t].rotation_euler = (0.6, 0, 0)
    parts["neck"].rotation_euler = (-0.35, 0, 0)
    if frame is not None:
        for k in ("pelvis",):
            parts[k].keyframe_insert("location", frame=frame)
        for k in ("pelvis", "hipL", "hipR", "kneeL", "kneeR", "shoulderL", "shoulderR", "elbowL", "elbowR", "neck"):
            parts[k].keyframe_insert("rotation_euler", frame=frame)


def glow_lines(name, polylines, color=(0.7, 0.85, 1.0), strength=3.0, bevel=0.004, mat=None):
    """Many emissive polylines in ONE curve object (fast line art). Returns (obj, emission_node)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    for pts in polylines:
        if len(pts) < 2:
            continue
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for k, q in enumerate(pts):
            sp.points[k].co = (*q, 1)
    cu.bevel_depth = bevel
    cu.bevel_resolution = 1
    o = L.link(bpy.data.objects.new(name, cu))
    m = mat or L.mat_emission(name + "_m", color, strength)
    o.data.materials.append(m)
    o.visible_shadow = False
    em = [nd for nd in m.node_tree.nodes if nd.type == "EMISSION"]
    return o, (em[0] if em else None)


def key_strength(node, pairs, interp="LINEAR"):
    """Keyframe an emission node's Strength: pairs [(frame, value), ...]."""
    for f, v in pairs:
        node.inputs[1].default_value = v
        node.inputs[1].keyframe_insert("default_value", frame=f)
    nt = node.id_data
    if nt.animation_data and nt.animation_data.action:
        for fc in L._fcurves(nt.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = interp


def circle_pts(c, r, n=40, y=0.0, a0=0.0, a1=2 * math.pi):
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * i / n), y, c[1] + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def xray_back_lines(s=1.0, cx=0.0, cz=0.0, y=0.0):
    """Stylised chest/shoulder line art seen FROM BEHIND (patient's left = viewer's left), in the XZ plane at depth y.
    Not traced from any radiograph. Film units ~0.9 x 1.1 m at s=1. Returns dict of polyline lists + arrowhead point."""
    def P(x, z):
        return (cx + x * s, y, cz + z * s)
    spine, ribs, clav, scap, hum = [], [], [], [], []
    spine.append([P(-0.018, z / 100) for z in range(50, -52, -6)])
    spine.append([P(0.018, z / 100) for z in range(50, -52, -6)])
    for k in range(15):
        z = 0.47 - k * 0.068
        spine.append([P(-0.035, z), P(0.035, z)])
    for i in range(10):
        z0 = 0.36 - 0.082 * i
        W = 0.15 + 0.15 * math.sin(math.pi * (i + 2.5) / 13.0)
        for sg in (-1, 1):
            pts = []
            for k in range(17):
                t = k / 16
                x = sg * (0.03 + W * math.sin(t * math.pi / 2))
                z = z0 + 0.035 * math.sin(t * math.pi) - 0.12 * t * t
                pts.append(P(x, z))
            ribs.append(pts)
    for sg in (-1, 1):
        clav.append([P(sg * (0.04 + 0.25 * t), 0.43 + 0.035 * t + 0.012 * math.sin(2 * math.pi * t)) for t in [k / 14 for k in range(15)]])
        scap.append([P(sg * 0.1, 0.37), P(sg * 0.2, 0.395), P(sg * 0.27, 0.36), P(sg * 0.25, 0.27), P(sg * 0.17, 0.05),
                     P(sg * 0.11, 0.2), P(sg * 0.1, 0.37)])
        scap.append([P(sg * 0.11, 0.31), P(sg * 0.2, 0.345), P(sg * 0.285, 0.395)])
        hum.append([P(sg * 0.31 + 0.045 * math.cos(a) * sg, 0.37 + 0.045 * math.sin(a)) for a in [math.radians(v) for v in range(-120, 181, 15)]])
        hum.append([P(sg * 0.29, 0.33), P(sg * 0.31, 0.1), P(sg * 0.32, -0.12)])
        hum.append([P(sg * 0.35, 0.335), P(sg * 0.36, 0.1), P(sg * 0.37, -0.12)])
    tip = (-0.205, 0.34)
    return {"spine": spine, "ribs": ribs, "clav": clav, "scap": scap, "hum": hum, "arrow": P(*tip), "s": s}


def arrowhead(loc, size=0.04, rot_y=0.0, color=(1.0, 0.95, 0.85), strength=6.0, name="arrowhead", y_axis=True):
    """Small flint arrowhead as an emissive leaf-triangle in the XZ plane (tip up at loc). Returns (obj, emission node)."""
    vs = [(0, 0, 0), (-size * 0.32, 0, -size * 0.75), (-size * 0.18, 0, -size), (size * 0.18, 0, -size), (size * 0.32, 0, -size * 0.75)]
    o = mesh_obj(name, vs, [(0, 1, 2, 3, 4)])
    m = L.mat_emission(name + "_m", color, strength)
    o.data.materials.append(m)
    o.location = loc
    o.rotation_euler = (0, rot_y, 0)
    o.visible_shadow = False
    return o, [nd for nd in m.node_tree.nodes if nd.type == "EMISSION"][0]


def lightbox(loc=(0, 0, 0), w=1.0, h=1.25, energy=4.0, color=(0.82, 0.9, 1.0), name="lightbox"):
    """Wall lightbox (front faces -Y): metal frame + emissive diffuser + area light. Returns dict(panel_node, light)."""
    root = empty(name, loc)
    fm = L.mat_principled(name + "_f", (0.18, 0.19, 0.2), rough=0.35, metal=0.8)
    box = L.prim("cube", loc=(0, 0.06, 0))
    box.scale = (w / 2 + 0.05, 0.05, h / 2 + 0.05)
    L.assign(box, fm)
    box.parent = root
    pan = L.prim("plane", loc=(0, -0.002, 0), size=1, rot=(math.pi / 2, 0, 0), name=name + "_panel")
    pan.scale = (w, h, 1)
    pm = L.mat_emission(name + "_pm", color, energy)
    L.assign(pan, pm)
    pan.parent = root
    clip_m = L.mat_principled(name + "_c", (0.6, 0.62, 0.64), rough=0.3, metal=1.0)
    for x in (-w * 0.3, w * 0.3):
        c = L.prim("cube", loc=(x, -0.012, h / 2 - 0.02))
        c.scale = (0.04, 0.008, 0.03)
        L.assign(c, clip_m)
        c.parent = root
    a = L.area((0, -0.25, 0), (math.radians(90), 0, 0), energy=energy * 12, size=max(w, h), color=color, name=name + "_a")
    a.parent = root
    node = [nd for nd in pm.node_tree.nodes if nd.type == "EMISSION"][0]
    return {"root": root, "node": node, "light": a, "panel": pan}


def film_sheet(loc, w=0.9, h=1.1, tint=(0.015, 0.03, 0.05), glow=1.0, name="film", parent=None):
    """X-ray film: dark translucent-looking sheet (emissive dark blue) in XZ facing -Y."""
    p = L.prim("plane", loc=loc, size=1, rot=(math.pi / 2, 0, 0), name=name)
    p.scale = (w, h, 1)
    m, n, l = L._mat(name + "_m")
    for nd in list(n):
        if nd.type == "BSDF_PRINCIPLED":
            n.remove(nd)
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (tint[0] * 0.6, tint[1] * 0.6, tint[2] * 0.6, 1)
    ramp.color_ramp.elements[1].color = (tint[0] * 1.8, tint[1] * 1.8, tint[2] * 1.8, 1)
    l.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    e = n.new("ShaderNodeEmission")
    e.inputs[1].default_value = glow
    l.new(ramp.outputs["Color"], e.inputs[0])
    l.new(e.outputs[0], n["Material Output"].inputs["Surface"])
    L.assign(p, m)
    p.visible_shadow = False
    if parent:
        p.parent = parent
    return p, e


def ct_gantry(loc=(0, 0, 0), rot_z=0.0, name="ct", ring_r=0.42, outer=1.05, depth=0.7, color=(0.82, 0.84, 0.86)):
    """CT scanner: square-ish gantry with circular bore (+X axis through bore), glowing bore ring, table, and an inner
    rotating ring with emissive markers (key 'spin' empty rotation_euler.x)."""
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    bm = bmesh.new()
    seg = 48
    zc = 1.05
    rings = []
    for xv in (-depth / 2, depth / 2):
        outer_r = []
        inner_r = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            c, s_ = math.cos(a), math.sin(a)
            k = max(abs(c), abs(s_))
            ro = outer / (k ** 0.35)
            outer_r.append(bm.verts.new((xv, ro * c, zc + ro * s_)))
            inner_r.append(bm.verts.new((xv, ring_r * c, zc + ring_r * s_)))
        rings.append((outer_r, inner_r))
    for i in range(seg):
        j = (i + 1) % seg
        for (o_, in_) in rings:
            bm.faces.new((o_[i], o_[j], in_[j], in_[i]))
        bm.faces.new((rings[0][0][i], rings[0][0][j], rings[1][0][j], rings[1][0][i]))
        bm.faces.new((rings[0][1][i], rings[1][1][i], rings[1][1][j], rings[0][1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    g = L.mesh_from_bm(name + "_gantry", bm)
    L.assign(g, L.mat_principled(name + "_m", color, rough=0.35))
    L.smooth(g)
    g.parent = root
    base = L.prim("cube", loc=(0, 0, 0.2))
    base.scale = (depth / 2 + 0.05, outer * 0.8, 0.2)
    L.assign(base, L.mat_principled(name + "_bm", (0.55, 0.57, 0.6), rough=0.4))
    base.parent = root
    for xv in (-depth / 2 - 0.004, depth / 2 + 0.004):
        rg = L.prim("torus", loc=(xv, 0, zc), major_radius=ring_r + 0.015, minor_radius=0.012, rot=(0, math.radians(90), 0),
                    major_segments=48, minor_segments=6)
        L.assign(rg, L.mat_emission(name + "_glow", (0.35, 0.75, 1.0), 6.0))
        rg.parent = root
    spin = empty(name + "_spin", (0, 0, zc), parent=root)
    mk = L.mat_emission(name + "_mk", (0.4, 0.85, 1.0), 10.0)
    for i in range(6):
        a = 2 * math.pi * i / 6
        d = L.prim("cube", loc=(-depth / 2 - 0.01, (ring_r + 0.04) * math.cos(a), (ring_r + 0.04) * math.sin(a)))
        d.scale = (0.006, 0.03, 0.03)
        L.assign(d, mk)
        d.parent = spin
    tm = L.mat_principled(name + "_tm", (0.12, 0.13, 0.15), rough=0.5)
    top = L.prim("cube", loc=(-1.6, 0, 0.78))
    top.scale = (1.5, 0.28, 0.04)
    L.assign(top, L.mat_principled(name + "_pad", (0.75, 0.78, 0.8), rough=0.5))
    ped = L.prim("cube", loc=(-1.9, 0, 0.38))
    ped.scale = (0.5, 0.2, 0.38)
    L.assign(ped, tm)
    for o in (top, ped):
        o.parent = root
    return {"root": root, "spin": spin, "zc": zc, "table_z": 0.82}


def copper_axe(loc, rot=(0, 0, 0), name="axe", haft_len=0.6):
    """Copper Age axe: yew haft with a bent-forward head, trapezoid copper blade bound with leather. Root = haft bottom."""
    root = empty(name, loc)
    root.rotation_euler = rot
    wood = L.mat_noise_surface(name + "_w", (0.2, 0.09, 0.03), (0.34, 0.17, 0.06), scale=30, bump=0.15, voronoi=False, rough=0.6)
    cop = L.mat_principled(name + "_c", (0.9, 0.42, 0.2), rough=0.3, metal=1.0)
    lea = L.mat_principled(name + "_l", (0.12, 0.06, 0.03), rough=0.85)
    h = L.prim("cyl", loc=(0, 0, haft_len / 2), vertices=12, radius=0.016, depth=haft_len)
    L.assign(h, wood)
    hd = L.prim("cyl", loc=(0.05, 0, haft_len + 0.01), vertices=12, radius=0.022, depth=0.13, rot=(0, math.radians(90), 0))
    L.assign(hd, wood)
    bl = mesh_obj(name + "_blade", [(0.08, -0.006, -0.025), (0.08, 0.006, -0.025), (0.08, 0.006, 0.025), (0.08, -0.006, 0.025),
                                    (0.18, -0.002, -0.045), (0.18, 0.002, -0.045), (0.18, 0.002, 0.045), (0.18, -0.002, 0.045)],
                  [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], mat=cop)
    bl.location = (0, 0, haft_len + 0.01)
    wr = L.prim("cyl", loc=(0.07, 0, haft_len + 0.01), vertices=10, radius=0.027, depth=0.04, rot=(0, math.radians(90), 0))
    L.assign(wr, lea)
    for o in (h, hd, bl, wr):
        o.parent = root
    return root


def flint_dagger(loc, rot=(0, 0, 0), name="dagger", scale=1.0):
    """Small flint dagger (leaf blade, chipped) with an ash-wood handle. Root at the handle end; points +Z."""
    root = empty(name, loc)
    root.rotation_euler = rot
    root.scale = (scale, scale, scale)
    fm = L.mat_noise_surface(name + "_f", (0.36, 0.33, 0.28), (0.62, 0.58, 0.5), scale=60, bump=0.8, voronoi=True, rough=0.45)
    wm = L.mat_noise_surface(name + "_w", (0.32, 0.22, 0.12), (0.5, 0.36, 0.2), scale=40, bump=0.1, voronoi=False, rough=0.7)
    hd = L.prim("cyl", loc=(0, 0, 0.045), vertices=12, radius=0.011, depth=0.09)
    hd.scale = (1.0, 0.75, 1.0)
    L.assign(hd, wm)
    bl = L.prim("ico", loc=(0, 0, 0.13), subdivisions=3, radius=1.0, name=name + "_blade")
    bl.scale = (0.017, 0.0045, 0.05)
    L.apply_scale(bl)
    for v in bl.data.vertices:  # leaf shape: pointed tip, broad base
        t = (v.co.z / 0.05 + 1) / 2
        v.co.x *= 1.15 - 0.85 * t ** 1.4
    L.assign(bl, fm)
    for o in (hd, bl):
        o.parent = root
    return root


def bow_stave(loc, length=1.82, rot=(0, 0, 0), name="bow"):
    """Unfinished yew longbow stave: tapered both ends, no nocks, no string. Root at centre."""
    root = empty(name, loc)
    root.rotation_euler = rot
    m = L.mat_noise_surface(name + "_m", (0.32, 0.13, 0.04), (0.52, 0.25, 0.08), scale=18, bump=0.12, voronoi=False, rough=0.55)
    bm = bmesh.new()
    seg, ring = 24, 8
    rows = []
    for i in range(seg + 1):
        t = i / seg
        z = (t - 0.5) * length
        r = 0.016 * (0.45 + 0.55 * math.sin(t * math.pi) ** 0.5)
        rows.append([bm.verts.new((r * math.cos(2 * math.pi * k / ring), r * 0.8 * math.sin(2 * math.pi * k / ring), z)) for k in range(ring)])
    for i in range(seg):
        for k in range(ring):
            j = (k + 1) % ring
            bm.faces.new((rows[i][k], rows[i][j], rows[i + 1][j], rows[i + 1][k]))
    bm.faces.new(rows[0][::-1])
    bm.faces.new(rows[-1])
    o = L.mesh_from_bm(name + "_stave", bm)
    L.assign(o, m)
    L.smooth(o)
    o.parent = root
    return root


def quiver(loc, rot=(0, 0, 0), name="quiver", length=0.9, color=(0.2, 0.12, 0.06)):
    """Deerskin quiver: slightly flattened tube with a stiffening rod and a few arrow shafts at the top."""
    root = empty(name, loc)
    root.rotation_euler = rot
    m = L.mat_noise_surface(name + "_m", (color[0] * 0.7, color[1] * 0.7, color[2] * 0.7), color, scale=25, bump=0.3, voronoi=False)
    t = L.prim("cyl", loc=(0, 0, length / 2), vertices=16, radius=0.06, depth=length)
    t.scale = (1.0, 0.6, 1.0)
    L.assign(t, m)
    L.smooth(t)
    rod = L.prim("cyl", loc=(0.06, 0, length / 2 + 0.03), vertices=8, radius=0.009, depth=length + 0.06)
    wm = L.mat_principled(name + "_w", (0.3, 0.2, 0.1), rough=0.6)
    L.assign(rod, wm)
    for o in (t, rod):
        o.parent = root
    for k, dx in enumerate((-0.025, 0.0, 0.022)):
        s = L.prim("cyl", loc=(dx, 0, length + 0.05 + 0.02 * k), vertices=6, radius=0.004, depth=0.14)
        L.assign(s, wm)
        s.parent = root
    return root


def einkorn_ear(loc, rot=(0, 0, 0), name="ear", length=0.09, seed=1, stalk=0.14):
    """Einkorn wheat ear: stalk + two rows of flattened grains + short awns. Root at the stalk base."""
    rnd = random.Random(seed)
    root = empty(name, loc)
    root.rotation_euler = rot
    gm = L.mat_principled(name + "_g", (0.62, 0.47, 0.24), rough=0.6)
    st = L.prim("cyl", loc=(0, 0, stalk / 2), vertices=6, radius=0.0025, depth=stalk)
    L.assign(st, gm)
    st.parent = root
    bm = bmesh.new()
    k = int(length / 0.009)
    for i in range(k):
        z = stalk + i * 0.009
        for sg in (-1, 1):
            res = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.0055)
            for v in res["verts"]:
                v.co = Vector((v.co.x * 0.7, v.co.y * 0.45, v.co.z * 1.25))
                v.co.rotate(Euler((0, sg * 0.45, 0)))
                v.co += Vector((sg * 0.004, 0, z))
            aw = [bm.verts.new((sg * 0.006, 0, z + 0.004)), bm.verts.new((sg * 0.009 + rnd.uniform(-0.002, 0.002), 0, z + 0.035)),
                  bm.verts.new((sg * 0.0065, 0.0008, z + 0.004))]
            bm.faces.new(aw)
    o = L.mesh_from_bm(name + "_grains", bm)
    L.assign(o, gm)
    o.parent = root
    return root


def meat_strip(loc, rot_z=0.0, size=(0.22, 0.06, 0.012), name="meat"):
    o = rounded_box(loc, size, (0.22, 0.06, 0.035), rough=0.55, bevel=0.4, name=name)
    o.rotation_euler = (0, 0, rot_z)
    L.add_displace(o, strength=0.006, scale=0.05, name=name + "_d")
    return o


def herb_sprig(loc, rot_z=0.0, name="herb", seed=2):
    rnd = random.Random(seed)
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    m = L.mat_principled(name + "_m", (0.08, 0.16, 0.05), rough=0.6)
    st = L.prim("cyl", loc=(0.06, 0, 0.004), vertices=5, radius=0.0018, depth=0.12, rot=(0, math.radians(90), 0))
    L.assign(st, m)
    st.parent = root
    for i in range(9):
        x = 0.01 + i * 0.012
        for sg in (-1, 1):
            lf = L.prim("sphere", loc=(x, sg * 0.008, 0.005), segments=8, ring_count=4)
            lf.scale = (0.009, 0.004, 0.0012)
            lf.rotation_euler = (0, 0, sg * rnd.uniform(0.4, 0.8))
            L.assign(lf, m)
            lf.parent = root
    return root


def ibex_outline():
    """Generic ibex side profile (facing +X), units ~1 m long, base at z=0. Returns list of polylines (x, z)."""
    body = [(-0.45, 0.56), (-0.1, 0.6), (0.2, 0.62), (0.3, 0.72), (0.38, 0.84), (0.45, 0.86), (0.56, 0.74), (0.55, 0.71),
            (0.5, 0.68), (0.4, 0.64), (0.33, 0.5), (0.3, 0.38), (0.29, 0.04), (0.29, 0.0), (0.24, 0.0), (0.24, 0.04),
            (0.22, 0.3), (0.0, 0.29), (-0.28, 0.31), (-0.3, 0.2), (-0.27, 0.04), (-0.27, 0.0), (-0.32, 0.0), (-0.34, 0.15),
            (-0.4, 0.3), (-0.47, 0.44), (-0.5, 0.52), (-0.45, 0.56)]
    legs2 = [[(0.17, 0.3), (0.16, 0.04), (0.16, 0.0), (0.12, 0.0)], [(-0.2, 0.31), (-0.22, 0.12), (-0.2, 0.0), (-0.24, 0.0)]]
    horn = [(0.43, 0.87), (0.38, 0.98), (0.28, 1.08), (0.14, 1.12), (0.02, 1.08), (-0.06, 0.98), (-0.08, 0.9)]
    horn2 = [(0.4, 0.86), (0.35, 0.95), (0.26, 1.03), (0.14, 1.06), (0.04, 1.02), (-0.02, 0.95)]
    ridges = []
    for t in (0.2, 0.35, 0.5, 0.65, 0.8):
        i = int(t * (len(horn) - 1))
        f = t * (len(horn) - 1) - i
        a = Vector(horn[i]).lerp(Vector(horn[i + 1]), f)
        b = Vector(horn2[min(i, len(horn2) - 2)]).lerp(Vector(horn2[min(i + 1, len(horn2) - 1)]), f)
        ridges.append([tuple(a), tuple(b)])
    beard = [(0.5, 0.68), (0.49, 0.6)]
    ear = [(0.4, 0.82), (0.34, 0.86), (0.37, 0.8)]
    return [body, horn, horn2, beard, ear] + legs2 + ridges


def side_figure_outline(h=1.75):
    """Generic faceless human side profile (facing +X), base z=0. Returns polylines (x, z) and the upper-back point."""
    s = h / 1.75
    body = [(0.05, 1.5), (0.08, 1.45), (0.14, 1.3), (0.12, 1.05), (0.09, 0.9), (0.07, 0.52), (0.05, 0.48), (0.06, 0.06), (0.17, 0.0),
            (-0.07, 0.0), (-0.08, 0.06), (-0.09, 0.3), (-0.08, 0.5), (-0.13, 0.88), (-0.1, 0.98), (-0.13, 1.15), (-0.12, 1.38),
            (-0.04, 1.5)]
    head = [(0.02 + 0.11 * math.cos(2 * math.pi * k / 32), 1.62 + 0.115 * math.sin(2 * math.pi * k / 32)) for k in range(33)]
    arm = [(-0.02, 1.4), (-0.03, 1.12), (0.0, 0.86), (0.03, 0.82)]
    sc = lambda pl: [(x * s, z * s) for (x, z) in pl]
    return [sc(body), sc(head), sc(arm)], (-0.115 * s, 1.36 * s)


def traveller(name="traveller", height=1.65, color=(0.03, 0.024, 0.02), bow=True, axe=True):
    """Prehistoric traveller silhouette (faceless): fur cape, round cap, bow stave over the shoulder, axe at the belt."""
    p = L.char_figure(name, color=color, height=height, coat=True)
    s = height / 1.75
    cm = L.mat_principled(name + "_cap", (0.05, 0.035, 0.02), rough=0.9)
    cap = L.prim("sphere", loc=(0, 0, 0.16 * s), segments=14, ring_count=8)
    cap.scale = (0.115 * s, 0.125 * s, 0.09 * s)
    L.assign(cap, cm)
    cap.parent = p["neck"]
    cape = L.prim("cone", loc=(0, 0, 0.5 * s), vertices=16, radius1=0.3 * s, radius2=0.12 * s, depth=0.42 * s)
    cape.scale = (1.0, 0.8, 1.0)
    L.assign(cape, cm)
    cape.parent = p["pelvis"]
    if bow:
        b = bow_stave((0.08 * s, -0.16 * s, 0.5 * s), length=1.8 * s, rot=(0, math.radians(-28), 0), name=name + "_bow")
        b.parent = p["pelvis"]
        p["bow"] = b
    if axe:
        a = copper_axe((0.2 * s, 0.02, -0.02), rot=(0, math.radians(180), 0), name=name + "_axe", haft_len=0.5 * s)
        a.parent = p["pelvis"]
        a.location = (0.21 * s, 0.0, 0.18 * s)
        p["axe"] = a
    return p


def pose_keys(parts, frame, names=("pelvis", "hipL", "hipR", "kneeL", "kneeR", "shoulderL", "shoulderR", "elbowL", "elbowR", "neck")):
    for k in names:
        parts[k].keyframe_insert("rotation_euler", frame=frame)
    parts["pelvis"].keyframe_insert("location", frame=frame)
