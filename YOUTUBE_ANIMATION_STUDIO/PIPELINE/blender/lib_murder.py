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
                    slab=False, slab_full=True, name="sec"):
    """Side-on slope cross-section (XZ plane, extruded along Y). Slope descends toward +X. Returns dict of parts.
    notch=(x_centre, width): tent platform cut into the snow layer."""
    tg = math.tan(math.radians(slope_deg))
    zg = lambda x: -x * tg
    zs = lambda x: zg(x) + T
    xn, wn = notch
    a, b = xn - wn / 2, xn + wn / 2
    zp = zs(b)
    x0, x1 = span
    bottom = zg(x1) - 4

    snow_m = L.mat_principled(name + "_snow", (0.86, 0.9, 0.97), rough=0.7, emit=(0.6, 0.66, 0.78), emit_strength=0.25)
    side_snow = L.mat_principled(name + "_snowside", (0.55, 0.62, 0.78), rough=0.8, emit=(0.3, 0.36, 0.5), emit_strength=0.25)
    ground_m = L.mat_noise_surface(name + "_ground", (0.05, 0.05, 0.055), (0.13, 0.13, 0.14), scale=3, bump=0.3)
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

    xs = [x0 + (x1 - x0) * i / 40 for i in range(41)]
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
        sx0 = a - 4.2
        thick = lambda x: 0.75 * smoothstep(sx0, a - 0.3, x)
        sxs = [sx0 + (a - sx0) * i / 12 for i in range(13)]
        spoly = [(x, zs(x) + thick(x)) for x in sxs] + [(a, zs(a) + thick(a) * 0.7), (a, zs(a))] + \
                [(x, zs(x) - 0.01) for x in reversed(sxs)]
        slab_m = L.mat_principled(name + "_slab", (0.78, 0.86, 1.0), rough=0.7, emit=(0.5, 0.65, 0.9), emit_strength=0.45)
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


def book(loc, size=(0.13, 0.19, 0.022), cover=(0.25, 0.12, 0.08), title=None, rot_z=0.0, name="book"):
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
        sm = L.mat_principled(name + "_str", (0.6, 0.55, 0.45), rough=0.9)
        s1 = L.prim("cyl", loc=(0.03, -0.01, h - 0.02), vertices=6, radius=0.0025, depth=0.12, rot=(0.25, 0.15, 0))
        L.assign(s1, sm)
        s1.parent = root
        s2 = L.prim("cyl", loc=(0.045, -0.02, h - 0.1), vertices=6, radius=0.0025, depth=0.06, rot=(0.6, -0.3, 0))
        L.assign(s2, sm)
        s2.parent = root
        # torn stub of a tag (tiny paper triangle) - the label itself is gone
        tb = mesh_obj(name + "_stub", [(0, 0, 0), (0.02, 0, -0.012), (0.004, 0, -0.03)], [(0, 1, 2)], mat=mat_paper(name + "_tp"))
        tb.location = (0.05, -0.03, h - 0.13)
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
    solidify(o, 0.0003)
    bd = o.modifiers.new("curl", "SIMPLE_DEFORM")
    bd.deform_method = "BEND"
    bd.deform_axis = "X"
    bd.angle = 2 * math.pi * turns
    return root, o, bd
