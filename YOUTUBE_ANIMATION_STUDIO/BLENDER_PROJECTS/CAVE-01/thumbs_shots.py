"""CAVE-01 thumbnail hero stills (NOT part of the video; shots.py is the video source and is not touched).
Purpose-built compositions for the custom Shorts thumbnail, rendered with a copy of render_shot.py pointed at this file.
THUMB_A: the lone torch at the bottom of the black water ("WENT BACK"). Shaw (black suit, yellow fins) hovers in trim over
  the silt, torch angled down onto the floor; a thin white shotline runs from his back straight up to a pin-prick of
  daylight at the very top of the frame. One warm light in a cold black void.
THUMB_B: the vertical cross-section of the sinkhole ("270 M"). Dusk desert on top, crater, pool, narrow throat, huge flooded
  chamber; one red descent arrow dives from the pool to a tiny warm dot (the diver's light) just above the floor.
Ethics: no body or remains. In A the lost diver is only the video's existing abstract marker (C.lost_shape: half-buried
  tank + two fin blades, exactly as in S01/S02); in B the lost diver is not shown at all. No faces, no real photos.
"""
import os, sys, math, random, importlib
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_cave as C
importlib.reload(C)
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

R = math.radians


def _place_cam(cam, pos, target):
    cam.location = pos
    cam.rotation_quaternion = C.look_quat(pos, target)
    bpy.context.view_layer.update()
    return cam


def _ray(cam, fx, fy):
    """World-space unit ray through the image point (fx from the left, fy from the TOP, both 0..1)."""
    tr, br, bl, tl = cam.data.view_frame(scene=bpy.context.scene)
    p = bl + (br - bl) * fx + (tl - bl) * (1 - fy)
    return (cam.matrix_world.to_3x3() @ p).normalized()


def _face(o, loc, toward):
    """Put o at loc with its local +Z pointing at `toward` (discs / glow cards that must face the lens)."""
    o.location = loc
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (Vector(toward) - Vector(loc)).to_track_quat("Z", "Y")
    return o


def _tapered_line(p0, p1, r0, r1, mat, name="shotline", n=14):
    """Straight emissive line from p0 to p1 whose radius goes r0 -> r1 (forced perspective: it thins toward the far end)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r0
    cu.bevel_resolution = 2
    sp = cu.splines.new("POLY")
    sp.points.add(n - 1)
    a, b = Vector(p0), Vector(p1)
    for i in range(n):
        t = i / (n - 1)
        sp.points[i].co = (*a.lerp(b, t), 1)
        sp.points[i].radius = 1 + (r1 / r0 - 1) * t
    o = C.L.link(bpy.data.objects.new(name, cu))
    o.data.materials.append(mat)
    return o


# ============================================================================ THUMB_A  "WENT BACK"

def THUMB_A(L, n):
    C.world_black((0.0, 0.003, 0.005))
    C.render_quality(vol_end=34)
    C.water(center=(-1.5, 2.0, 4.75), size=(30, 30, 13.5), color=(0.3, 0.62, 0.6), density=0.045,
            absorption=(0.06, 0.3, 0.3))
    # same silt floor (same height field) and same abstract marker placement as the video's S01/S02
    C.floor(size=(34, 34), center=(0, 0, 0), strength=0.45, name="chamber_floor")
    C.lost_shape(loc=(0, 0, 0), rot_z=0.55)

    # --- Shaw, in trim just above the silt (slightly head-down), torch on the floor beside the marker
    RX, RY, RZ = -1.62, 0.25, 1.5
    d = C.diver("shaw", fins=C.YELLOW, light_energy=4000, beam_len=2.3, beam_strength=0.5, beam_deg=26)
    r = d["root"]
    r.location = (RX, RY, RZ)
    r.rotation_euler = (-R(10), 0.25, -math.pi / 2 + 0.1)  # faces +X, 10 deg head-down, back rolled toward the lens
    d["torch"].rotation_euler = (math.pi / 2 - R(42), 0, 0)  # beam ~50 deg below horizontal
    for tag, roll, knee in (("L", 0.55, -0.8), ("R", -0.55, -0.5)):  # frog-kick trim: knees bent, fin blades turned out
        d[f"hip{tag}"].rotation_euler = (0.08, roll, 0)
        d[f"knee{tag}"].rotation_euler = (knee, 0, 0)
    d["shoulderL"].rotation_euler = (-0.45, 0, -0.3)
    d["shoulderR"].rotation_euler = (-0.3, 0, 0.3)

    # --- camera
    CAM = Vector((-0.95, -7.0, 2.0))
    cam = C.camera(lens=25.5)
    _place_cam(cam, CAM, (-1.25, 0.25, 1.39))
    C.cam_fill(cam, energy=10)

    # --- cyan back lights, hidden exactly behind his body: the haze they light is what the silhouette reads against
    p_torso = d["torso"].matrix_world.translation + Vector((0, 0, 0.08))
    p_knees = (d["kneeL"].matrix_world.translation + d["kneeR"].matrix_world.translation) / 2
    for name, p, dist, e, deg in (("back_torso", p_torso, 2.6, 1500, 55), ("back_legs", p_knees, 2.2, 500, 50)):
        C.rim_light(tuple(p), tuple((p - CAM).normalized() * dist), energy=e, color=(0.3, 0.8, 1.0), size_deg=deg,
                    name=name)
    # warm bounce off the lit silt (motivated by the torch pool): lifts the marker's near side and his chest
    L.point((0.3, 0.2, 0.28), energy=110, color=C.TORCH, radius=0.5, name="pool_bounce")

    # --- the way out: a pin-prick of daylight at the very top, and the shotline from it straight down to his back
    rb = bpy.data.objects["shaw_rebreather"].matrix_world.translation
    F = rb + (rb - CAM).normalized() * 0.3  # lower end, hidden behind the rebreather
    fx = world_to_camera_view(bpy.context.scene, cam, F).x
    D = CAM + _ray(cam, fx, 0.045) * 13.0
    sky = L.prim("cyl", vertices=24, radius=0.1, depth=0.01, name="daylight")
    L.assign(sky, C.emis("daylight_m", (0.8, 0.97, 1.0), 20.0))
    _face(sky, D, CAM)
    glow, _ = C.glow_disc((0, 0, 0), radius=0.5, color=(0.5, 0.95, 1.0), strength=2.2, power=2.5, name="skyglow")
    _face(glow, D + (CAM - D).normalized() * 0.05, CAM)
    _tapered_line(F, D, 0.02, 0.012, C.emis("shotline_m", (0.95, 0.97, 1.0), 2.6))
    sp = L.spot(tuple(D), (0, 0, 0), energy=0, size_deg=5, name="skyray")  # faint light shaft dying in the dark
    sp.rotation_mode = "QUATERNION"
    sp.rotation_quaternion = (F - D).to_track_quat("-Z", "Y")
    C.beam_cone(sp, length=5.0, color=(0.6, 0.93, 1.0), strength=0.3, name="skyray_c")

    # --- fine silt: motes in the beam + a sparse field; all >= 6 m from the lens, radius <= 0.004
    C.cloud((RX + 1.3, RY + 0.05, 0.75), (1.9, 1.3, 1.5), count=500, radius=0.003, emit=0.04, seed=11, name="motes")
    C.cloud((-1.5, 1.6, 2.2), (9.0, 5.0, 4.0), count=400, radius=0.004, emit=0.05, seed=9, name="field")
    L.bake_static()


# ============================================================================ THUMB_B  "270 M"

def _strata_mat(name="strata"):
    """Dark rock with faint wavy horizontal strata, so the slab reads as ground in section (not as a glass flask)."""
    m, nd, ln = C.L._mat(name)
    p = nd["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.9
    tc = nd.new("ShaderNodeTexCoord")
    wave = nd.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 0.55
    wave.inputs["Distortion"].default_value = 5.0
    wave.inputs["Detail"].default_value = 3.0
    wave.inputs["Detail Scale"].default_value = 1.4
    ln.new(tc.outputs["Object"], wave.inputs["Vector"])
    ramp = nd.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.014, 0.018, 0.024, 1)
    ramp.color_ramp.elements[1].color = (0.046, 0.054, 0.063, 1)
    ln.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nz = nd.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.3
    nz.inputs["Detail"].default_value = 6.0
    ln.new(tc.outputs["Object"], nz.inputs["Vector"])
    mix = nd.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.6
    ln.new(ramp.outputs["Color"], mix.inputs["A"])
    ln.new(nz.outputs["Color"], mix.inputs["B"])
    ln.new(mix.outputs["Result"], p.inputs["Base Color"])
    return m


def _sky_card(z0, height=1.7, y=0.9, horizon=(1.0, 0.36, 0.08), top=(0.004, 0.006, 0.02), strength=1.5):
    """Emissive dusk gradient behind the slab: warm at the horizon (z0), falling to near-black `height` above it."""
    o = C.L.prim("plane", loc=(0, y, z0 + 2.2), rot=(math.pi / 2, 0, 0), size=1, name="sky")
    o.scale = (18, 5.0, 1)  # from 0.3 below the horizon to well above the top of the frame (no seam)
    m, nd, ln = C.L._mat("sky_m")
    for x in list(nd):
        if x.type == "BSDF_PRINCIPLED":
            nd.remove(x)
    geo = nd.new("ShaderNodeNewGeometry")
    sep = nd.new("ShaderNodeSeparateXYZ")
    ln.new(geo.outputs["Position"], sep.inputs[0])
    mr = nd.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = z0
    mr.inputs["From Max"].default_value = z0 + height
    ln.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nd.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*horizon, 1)
    ramp.color_ramp.elements[1].color = (*top, 1)
    ramp.color_ramp.elements[1].position = 0.55
    mid = ramp.color_ramp.elements.new(0.18)
    mid.color = (horizon[0] * 0.32, horizon[1] * 0.22, horizon[2] * 0.6 + 0.02, 1)
    ln.new(mr.outputs["Result"], ramp.inputs["Fac"])
    em = nd.new("ShaderNodeEmission")
    em.inputs[1].default_value = strength
    ln.new(ramp.outputs["Color"], em.inputs[0])
    ln.new(em.outputs[0], nd["Material Output"].inputs["Surface"])
    C.L.assign(o, m)
    return o


def THUMB_B(L, n):
    C.world_black((0.0, 0.0, 0.0))
    K, Z0, XS = 0.0125, 2.0, 0.75  # metres -> scene units (vertical), z of the pool surface, horizontal scale
    GROUND = -22  # ground level: 22 m above the pool

    def dz(dep):
        return Z0 - dep * K

    poly = [(-1.75, GROUND - 6), (-1.6, GROUND), (-1.1, -12), (-0.65, -3), (-0.42, 0), (-0.22, 8), (-0.18, 22),
            (-0.2, 40), (-0.35, 55), (-0.8, 68), (-1.35, 90), (-1.75, 125), (-1.95, 165), (-2.0, 205), (-1.9, 240),
            (-1.6, 262), (-1.0, 272), (-0.3, 280), (0.4, 283), (1.1, 276), (1.55, 262), (1.85, 235), (1.95, 195),
            (1.85, 150), (1.6, 110), (1.15, 80), (0.55, 60), (0.25, 45), (0.2, 25), (0.25, 8), (0.42, 0), (0.65, -3),
            (1.1, -12), (1.6, GROUND), (1.75, GROUND - 6)]
    xs = C.xsection(poly, dz, x_scale=XS, extent=(-6, 6, -9, dz(GROUND)), water_poly=[p for p in poly if p[1] >= 0],
                    name="boes", water_top=(0.03, 0.25, 0.28), water_bot=(0.0, 0.006, 0.01), rock_mat_=_strata_mat())
    P = xs["P"]
    # open outline (no closing stroke across the crater mouth), thick enough to survive channel-grid size
    xs["outline"].hide_render = True
    C.curve([tuple(P(x, dep, -0.42)) for x, dep in poly[1:-1]], thickness=0.03, mat=C.emis("rim_m", C.CYAN, 2.4),
            name="outline_open")
    sand = C.emis("sand_line", (1.0, 0.5, 0.16), 1.8)
    for side in (-1, 1):
        C.curve([(side * 6.0, -0.42, dz(GROUND)), (side * 1.6 * XS, -0.42, dz(GROUND))], thickness=0.024, mat=sand,
                name="ground")
    C.curve([tuple(P(-0.42, 0)), tuple(P(0.42, 0))], thickness=0.02, mat=C.emis("poolline", (0.7, 1, 1), 6),
            name="pool")

    # the surface: dusk sky behind the slab + a few scrub silhouettes on the rim, so "up" is unmistakably the desert
    _sky_card(dz(GROUND))
    rnd = random.Random(6)
    scrub = L.mat_principled("scrub_m", (0.006, 0.006, 0.007), rough=1.0)
    for i in range(13):
        x = rnd.choice((-1, 1)) * rnd.uniform(1.6 * XS + 0.12, 2.9)
        s = rnd.uniform(0.05, 0.11)
        b = L.prim("ico", loc=(x, 0.0, dz(GROUND) + s * 0.45), subdivisions=2, radius=s, name="scrub")
        b.scale = (rnd.uniform(1.0, 1.7), 1.0, rnd.uniform(0.55, 0.9))
        L.assign(b, scrub)

    # the descent: one red arrow from the pool down the throat to just above the diver's light
    red = C.emis("descent_m", (1.0, 0.02, 0.01), 0.75)
    path = [P(0.02, 1, -0.46), P(0.02, 50, -0.46), P(0.1, 110, -0.46), P(0.2, 180, -0.46), P(0.25, 232, -0.46)]
    tip = P(0.25, 252, -0.46)
    C.curve([tuple(p) for p in path], thickness=0.026, mat=red, name="descent", smooth_pts=True)
    dirv = (tip - path[-1]).normalized()
    head = L.prim("cone", loc=tuple(tip - dirv * 0.12), vertices=20, radius1=0.1, radius2=0, depth=0.24,
                  name="descent_head")
    head.rotation_mode = "QUATERNION"
    head.rotation_quaternion = dirv.to_track_quat("Z", "Y")
    L.assign(head, red)
    # the diver: a tiny warm light far below the surface (small hot core + soft additive glow, not a ball)
    dot = P(0.25, 268, -0.47)
    core, halo, hem = C.glow_dot(tuple(dot), (1.0, 0.72, 0.25), r=0.04, strength=14, light=20, name="shaw")
    halo.hide_render = True
    for rad, st, pw, col in ((0.36, 1.3, 2.0, (1.0, 0.6, 0.2)), (0.13, 5.0, 1.5, (1.0, 0.85, 0.5))):
        C.glow_disc((dot.x, dot.y - 0.05, dot.z), radius=rad, color=col, strength=st, power=pw, name="shaw_glow",
                    rot=(math.pi / 2, 0, 0))

    a = L.area((-3, -4, 4), (R(60), 0, R(-35)), energy=380, size=4, color=(0.7, 0.85, 1.0))
    cam = C.camera(lens=60)
    _place_cam(cam, (0.6, -13.73, 0.75), (0.0, 0.0, 0.4))
    L.bake_static()
