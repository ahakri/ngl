"""CAVE-01 thumbnail hero stills (NOT part of the video; shots.py is the video source and is not touched).
Purpose-built compositions for the custom Shorts thumbnail, rendered with a copy of render_shot.py pointed at this file.
THUMB_A: the lone torch at the bottom of the black shaft ("270 M"). Shaw (black suit, yellow fins) hovers in trim over the
  silt, torch angled down onto the floor; a thin white shotline runs from him up to a pin-prick of daylight far above.
  The opening is a forced-perspective miniature (a small lit rock funnel facing the camera), so it reads as very far away.
THUMB_B: the vertical cross-section of the sinkhole ("WENT BACK"). Crater, pool, narrow throat, huge flooded chamber; one red
  descent line dives from the pool to a tiny warm dot (the diver's light) just above the floor.
Ethics: no body or remains. In A the lost diver is only the video's existing abstract marker (C.lost_shape: half-buried
  tank + two fin blades, as in S01/S02); in B the lost diver is not shown at all. No faces, no real photos.
"""
import os, sys, math, importlib
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_cave as C
importlib.reload(C)
import bpy
from mathutils import Vector

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


# ============================================================================ THUMB_A  "270 M"

def THUMB_A(L, n):
    C.world_black((0.0, 0.003, 0.005))
    C.render_quality(vol_end=34)
    C.water(center=(-1.5, 2.0, 4.0), size=(30, 30, 12), color=(0.3, 0.62, 0.6), density=0.045,
            absorption=(0.06, 0.3, 0.3))
    # same silt floor (same height field) and same abstract marker placement as the video's S01/S02
    C.floor(size=(34, 34), center=(0, 0, 0), strength=0.45, name="chamber_floor")
    C.lost_shape(loc=(0, 0, 0), rot_z=0.55)
    C.rocks([(-5.4, 2.8, 0), (2.7, 3.6, 0), (0.9, 5.4, 0), (-3.1, 5.6, 0)], count=4, size=(0.45, 1.0), seed=4)

    # --- Shaw, in trim just above the silt, torch angled down onto the floor beside the marker
    RX, RY, RZ = -2.12, 0.25, 1.4
    d = C.diver("shaw", fins=C.YELLOW, light_energy=3200, beam_len=2.6, beam_strength=0.3, beam_deg=26)
    r = d["root"]
    r.location = (RX, RY, RZ)
    r.rotation_euler = (-0.1, 0.25, -math.pi / 2 + 0.1)  # faces +X, slightly head-down, back rolled toward the lens
    d["torch"].rotation_euler = (math.pi / 2 - 0.634, 0, 0)  # beam ~42 deg below horizontal
    for tag, roll, knee in (("L", 0.55, -0.8), ("R", -0.55, -0.5)):  # frog-kick trim: knees bent, fin blades turned out
        d[f"hip{tag}"].rotation_euler = (0.08, roll, 0)
        d[f"knee{tag}"].rotation_euler = (knee, 0, 0)
    d["shoulderL"].rotation_euler = (-0.45, 0, -0.3)
    d["shoulderR"].rotation_euler = (-0.3, 0, 0.3)
    T0 = (RX, RY, RZ)
    # cyan back light: the haze behind him is what the silhouette reads against
    C.rim_light(T0, (0.9, 3.3, 0.8), energy=1500, color=(0.3, 0.8, 1.0), size_deg=50, name="rim_back")
    C.rim_light(T0, (-1.8, 2.6, -0.5), energy=700, color=(0.3, 0.7, 0.95), size_deg=45, name="rim_legs")

    # --- camera
    CAM = Vector((-1.25, -7.0, 2.0))
    cam = C.camera(lens=21)
    _place_cam(cam, CAM, (-1.55, 0.25, 2.27))
    C.cam_fill(cam, energy=10)

    # --- the way out: a pin-prick of daylight "far" above (forced-perspective lit rock funnel facing the lens)
    D = CAM + _ray(cam, 0.47, 0.31) * 12.5
    fun = C.shaft(0.0, -1.7, lambda z, a: 0.22 + (-z) * 1.0, step=0.07, ring=64, seed=7, rough=0.1, name="throat",
                  disp=(0.08, 0.025), mat=C.rock_mat("throatrock", (0.03, 0.06, 0.065), (0.3, 0.42, 0.42), scale=9.0))
    fun.location = D
    fun.rotation_mode = "QUATERNION"
    fun.rotation_quaternion = (CAM - D).to_track_quat("-Z", "Y")
    sky = L.prim("cyl", loc=(0, 0, 0.02), vertices=32, radius=0.32, depth=0.01, name="daylight")
    L.assign(sky, C.emis("daylight_m", (0.8, 0.97, 1.0), 14.0))
    sky.parent = fun
    glow, _ = C.glow_disc((0, 0, -1.0), radius=0.7, color=(0.5, 0.95, 1.0), strength=1.6, power=3.0, name="skyglow")
    glow.parent = fun
    pl = L.point((0, 0, -0.45), energy=60, color=(0.5, 0.9, 1.0), radius=0.1, name="throat_light")
    pl.parent = fun

    # --- the shotline from the opening down to him (its lower end is hidden behind his back), thinning with distance
    F = Vector((RX + 0.15, RY + 0.3, RZ + 0.1))
    _tapered_line(F, D, 0.02, 0.011, C.emis("shotline_m", (0.95, 0.97, 1.0), 2.6))
    for deg, ln, st in ((7, 4.5, 0.45), (18, 3.0, 0.18)):  # faint light shaft following the line, dying in the dark
        sp = L.spot(tuple(D), (0, 0, 0), energy=0, size_deg=deg, name="skyray")
        sp.rotation_mode = "QUATERNION"
        sp.rotation_quaternion = (F - D).to_track_quat("-Z", "Y")
        C.beam_cone(sp, length=ln, color=(0.6, 0.93, 1.0), strength=st, name="skyray_c")

    # --- fine silt: motes in the beam + a sparse field; all >= 6 m from the lens, radius <= 0.004
    C.cloud((RX + 1.75, RY + 0.05, 0.85), (2.6, 1.6, 1.6), count=700, radius=0.003, emit=0.04, seed=11, name="motes")
    C.cloud((-1.5, 1.6, 2.2), (9.0, 5.0, 4.0), count=450, radius=0.004, emit=0.05, seed=9, name="field")
    L.bake_static()


# ============================================================================ THUMB_B  "WENT BACK"

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
                    name="boes", water_top=(0.03, 0.25, 0.28), water_bot=(0.0, 0.006, 0.01))
    P = xs["P"]
    # open outline (no closing stroke across the crater mouth), thick enough to survive channel-grid size
    xs["outline"].hide_render = True
    C.curve([tuple(P(x, dep, -0.42)) for x, dep in poly[1:-1]], thickness=0.03, mat=C.emis("rim_m", C.CYAN, 4.0),
            name="outline_open")
    sand = C.emis("sand_line", (0.9, 0.66, 0.36), 2.6)
    for side in (-1, 1):
        C.curve([(side * 6.0, -0.42, dz(GROUND)), (side * 1.6 * XS, -0.42, dz(GROUND))], thickness=0.026, mat=sand,
                name="ground")
    C.curve([tuple(P(-0.42, 0)), tuple(P(0.42, 0))], thickness=0.02, mat=C.emis("poolline", (0.7, 1, 1), 6),
            name="pool")

    # the descent: one red line from the pool down the throat to just above the diver's light, with an arrowhead
    red = C.emis("descent_m", (1.0, 0.05, 0.03), 1.6)
    path = [P(0.02, 1, -0.46), P(0.02, 50, -0.46), P(0.1, 110, -0.46), P(0.2, 180, -0.46), P(0.25, 236, -0.46)]
    tip = P(0.25, 256, -0.46)
    C.curve([tuple(p) for p in path], thickness=0.02, mat=red, name="descent", smooth_pts=True)
    dirv = (tip - path[-1]).normalized()
    head = L.prim("cone", loc=tuple(tip - dirv * 0.11), vertices=20, radius1=0.085, radius2=0, depth=0.22,
                  name="descent_head")
    head.rotation_mode = "QUATERNION"
    head.rotation_quaternion = dirv.to_track_quat("Z", "Y")
    L.assign(head, red)
    # the diver: a tiny warm light far below the surface
    C.glow_dot(tuple(P(0.25, 268, -0.47)), (1.0, 0.8, 0.4), r=0.08, halo=3.6, strength=12, light=25, name="shaw")

    L.area((-3, -4, 4), (R(60), 0, R(-35)), energy=600, size=4, color=(0.7, 0.85, 1.0))
    cam = C.camera(lens=60)
    _place_cam(cam, (0.6, -13.73, 0.75), (0.0, 0.0, 0.4))
    L.bake_static()
