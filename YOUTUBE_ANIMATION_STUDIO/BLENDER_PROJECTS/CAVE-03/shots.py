"""CAVE-03 — Plura, Norway (2014). Shot builders (def Sxx(L, n)). Shared builders: PIPELINE/blender/lib_cave.py"""
import sys, os, math, random
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "PIPELINE", "blender"))
import importlib
import lib_cave as C
importlib.reload(C)
import bpy
from mathutils import Vector

FIN_A = (0.15, 0.4, 1.0)     # team one, diver A (stuck) - blue
FIN_B = (0.92, 0.92, 0.9)    # team one, diver B - white
FIN_C = C.ORANGE             # team two, the diver who turned back
FIN_T2 = [(0.2, 0.85, 0.3), (0.85, 0.2, 0.6)]  # other team-two divers: green, magenta
TRI = [(0.0, 0.81), (-0.7, -0.4), (0.7, -0.4)]   # ice hole triangle (x, y)


# ============================================================================ under the ice (S01 / S16 / S18)

def _under_ice(L, n, sky=6.0, light=2200, density=0.05, plug=False):
    C.world_black((0.0, 0.006, 0.01))
    C.render_quality(vol_end=30)
    C.water(center=(0, 0, -6), size=(24, 24, 12), color=(0.35, 0.65, 0.7), density=density, absorption=(0.1, 0.3, 0.25))
    ice, icem, cut = C.ice_sheet(z=0.0, size=26, thickness=0.5, hole=TRI, name="ice")
    skyp = L.prim("plane", loc=(0, 0, 2.5), size=14, name="sky")
    L.assign(skyp, C.emis("skym", (0.85, 0.93, 1.0), sky))
    skyp.visible_shadow = False
    al = L.area((0, 0.1, 1.4), (0, 0, 0), energy=light, size=1.3, color=(0.85, 0.93, 1.0), name="holelight")
    # dim cold glow through the ice everywhere else
    L.area((0, 0, -0.6), (math.pi, 0, 0), energy=0, size=8, name="dummy")
    bottom = C.floor(size=(30, 30), center=(0, 0, -9), strength=0.6, name="pondfloor",
                     mat=C.rock_mat("pondrock", (0.02, 0.03, 0.035), (0.12, 0.16, 0.17), scale=1.2))
    return ice, al, skyp


def S01(L, n):
    ice, al, skyp = _under_ice(L, n)
    # ice plug still attached along the third side; saw bar finishes the cut, plug is lifted out
    sc = 0.94
    bm_pts = [(x * sc, y * sc) for x, y in TRI]
    import bmesh
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, 0.02)) for x, y in bm_pts]
    hi = [bm.verts.new((x, y, 0.48)) for x, y in bm_pts]
    bm.faces.new(lo)
    bm.faces.new(list(reversed(hi)))
    for i in range(3):
        bm.faces.new((lo[i], lo[(i + 1) % 3], hi[(i + 1) % 3], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    plug = L.mesh_from_bm("plug", bm)
    L.assign(plug, ice.active_material)
    lift = 44
    C.key_loc(plug, [(1, (0, 0, 0)), (lift, (0, 0, 0)), (lift + 14, (0.2, 0.3, 1.6)), (lift + 18, (2.0, 2.0, 3.0))])
    plug.rotation_euler = (0, 0, 0)
    plug.keyframe_insert("rotation_euler", frame=lift)
    plug.rotation_euler = (0.5, 0.2, 0)
    plug.keyframe_insert("rotation_euler", frame=lift + 14)
    # uncut bridge on side 2 (between TRI[1] and TRI[2]) shrinking as the bar travels
    a, b = Vector((*TRI[1], 0)), Vector((*TRI[2], 0))
    bridge = L.prim("cube", loc=(0, -0.42, 0.25), name="bridge")
    L.assign(bridge, ice.active_material)
    bar = L.prim("cube", loc=(0, 0, 0), name="sawbar")
    bar.scale = (0.03, 0.015, 0.32)
    L.assign(bar, L.mat_principled("bar_m", (0.45, 0.47, 0.5), metal=0.9, rough=0.3))
    L.bevel(bar, 0.01)
    cut_end = 40
    for f in range(1, cut_end + 1, 2):
        t = C.sm((f - 1) / (cut_end - 1))
        px = a.x + (b.x - a.x) * t
        bridge.scale = (max(0.001, (b.x - px) / 2), 0.05, 0.25)
        bridge.location = ((px + b.x) / 2, -0.42, 0.25)
        bridge.keyframe_insert("scale", frame=f)
        bridge.keyframe_insert("location", frame=f)
        bar.location = (px, -0.42, -0.12 + 0.03 * math.sin(f * 1.7))
        bar.keyframe_insert("location", frame=f)
    bar.location = (b.x + 0.1, -0.42, 0.6)
    bar.keyframe_insert("location", frame=cut_end + 6)
    # glowing kerfs: sides 0-1 and 2-0 already cut, side 1-2 follows the bar
    km = C.emis("kerf", (0.9, 0.97, 1.0), 12)
    for i0, i1 in ((0, 1), (2, 0)):
        C.curve([(*TRI[i0], -0.01), (*TRI[i1], -0.01)], thickness=0.012, mat=km, name="kerf")
    k2 = C.curve([(*TRI[1], -0.01), (*TRI[2], -0.01)], thickness=0.012, mat=km, name="kerf2")
    C.grow_curve(k2, [(1, 0.0), (cut_end, 1.0)])
    # bubbles + ice chips from the cut
    L.bubbles_stream((0.0, -0.45, -0.3), count=60, nframes=n, rise=0.5, spread=0.4, size=0.02, name="cutbub")
    chips = C.cloud((0.0, -0.45, -0.35), (1.6, 0.6, 0.5), count=150, radius=0.008, color=(0.9, 0.95, 1.0), emit=0.5,
                    seed=2, name="chips")
    C.key_loc(chips, [(1, (0, -0.45, -0.25)), (n, (0.1, -0.6, -1.4))])
    C.key_scale(chips, [(1, 0.4), (n, 1.6)])
    # gloved hand drops a white line through the triangle
    glove = L.prim("sphere", loc=(0.3, 0.1, 0.6), segments=12, ring_count=8, name="glove")
    glove.scale = (0.08, 0.12, 0.05)
    L.assign(glove, L.mat_principled("glove_m", (0.02, 0.02, 0.025), rough=0.6))
    C.key_loc(glove, [(1, (0.3, 0.1, 1.2)), (lift + 10, (0.3, 0.1, 1.2)), (lift + 20, (0.15, 0.1, 0.35)), (n, (0.15, 0.1, 0.3))])
    ln = C.line([(0.15, 0.1, 0.35), (0.12, 0.08, -4.0)], thickness=0.01, emit=1.5, name="dropline")
    C.grow_curve(ln, [(1, 0.0), (lift + 18, 0.0), (n, 1.0)])
    weight = L.prim("cyl", loc=(0, 0, 0), vertices=10, radius=0.03, depth=0.12, name="weight")
    L.assign(weight, L.mat_principled("wt", (0.3, 0.3, 0.32), metal=0.8))
    C.key_loc(weight, [(1, (0.15, 0.1, 0.6)), (lift + 18, (0.15, 0.1, 0.3)), (n, (0.12, 0.08, -4.0))])
    p = C.cloud((0, 0, -2), (6, 6, 3), count=1500, radius=0.005, emit=0.15, seed=4)
    C.drift(p, n, (0.02, 0.01, 0.03))
    cam = C.camera(lens=20)
    C.aim_cam(cam, n, [(1, (0.35, -1.6, -3.4), (0.0, 0.55, 0.0)), (n, (0.3, -1.25, -2.6), (0.0, 0.5, 0.0))],
              shake=0.02, rot_shake=0.004)
    C.cam_fill(cam, energy=25, color=(0.5, 0.8, 0.95))
    L.bake_static()


def S18(L, n):
    _under_ice(L, n, sky=7.0, light=2600)
    rnd = random.Random(6)
    sil = L.mat_principled("sil", (0.01, 0.012, 0.014), rough=0.8)
    for i in range(7):
        st = 4 + i * 13
        if st > n - 8:
            break
        root = L.link(bpy.data.objects.new(f"rec{i}", None))
        body = L.prim("sphere", loc=(0, 0, 0.3), segments=12, ring_count=8, name="recbody")
        body.scale = (0.16, 0.13, 0.55)
        L.assign(body, sil)
        body.parent = root
        sp = L.spot((0, 0, -0.3), (0, 0, 0), energy=1600, size_deg=18, blend=0.4, color=C.TORCH, name="rectorch")
        sp.rotation_euler = (rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), 0)
        sp.parent = root
        C.beam_cone(sp, length=5, strength=0.22, name="recbeam")
        lens = L.prim("sphere", loc=(0, 0, -0.3), segments=8, ring_count=6, radius=0.035)
        L.assign(lens, C.emis("recl", (1, 0.95, 0.85), 30))
        lens.parent = root
        x, y = rnd.uniform(-0.25, 0.25), rnd.uniform(-0.15, 0.3)
        ang = i * 2.4
        ex, ey = math.cos(ang) * 1.6, math.sin(ang) * 1.6 + 0.4
        C.key_loc(root, [(1, (x, y, 1.8)), (st, (x, y, 1.6)), (st + 30, (ex, ey, -1.4)), (n, (ex * 1.2, ey * 1.2, -1.9))])
        C.hide_from_frame([root, body, lens], f_show=st)
    p = C.cloud((0, 0, -2), (6, 6, 3), count=1500, radius=0.005, emit=0.15, seed=4)
    C.drift(p, n, (0.02, 0.01, 0.03))
    cam = C.camera(lens=20)
    end = n - 14
    C.aim_cam(cam, n, [(1, (0.3, -1.25, -2.6), (0.0, 0.5, 0.0)), (end, (0.35, -1.6, -3.4), (0.0, 0.55, 0.0)),
                       (n, (0.35, -1.6, -3.4), (0.0, 0.55, 0.0))], shake=0.015, rot_shake=0.003)
    C.cam_fill(cam, energy=25, color=(0.5, 0.8, 0.95))
    L.bake_static()


def S16(L, n):
    ice, al, skyp = _under_ice(L, n, sky=1.6, light=500, density=0.06)
    cut = n - 19
    d = C.diver("diverC", fins=FIN_C, rebreather=False, tanks="doubles", light_energy=500, beam_len=3, beam_strength=0.15)
    r = d["root"]
    r.rotation_euler = (math.pi / 2 - 0.15, 0, 0)  # hanging upright on the line
    r.location = (0.05, 0.25, -3.2)
    for f in range(1, cut, 4):
        r.location.z = -3.2 + 0.04 * math.sin(f * 0.12)
        r.keyframe_insert("location", frame=f)
    C.line([(0.05, 0.45, 0.4), (0.05, 0.45, -9)], thickness=0.01, emit=1.0, name="decoline")
    L.bubbles_stream((0.05, 0.85, -2.6), count=50, nframes=n, rise=1.0, spread=0.1, size=0.025, name="decobub")
    C.rim_light((0.05, 0.25, -3.0), (0.2, 2.5, 1.5), energy=400, color=(0.4, 0.7, 1.0), name="decorim")
    p = C.cloud((0, 0, -3), (5, 5, 3), count=1500, radius=0.005, emit=0.12, seed=5)
    C.drift(p, n, (0.03, 0.01, 0.02))
    # --- cut-away: blue emergency light flashing on snow (far set)
    OFF = Vector((500, 0, 0))
    snow = C.floor(size=(30, 30), center=tuple(OFF), strength=0.3, name="snowground",
                   mat=L.mat_principled("snowm", (0.8, 0.85, 0.9), rough=0.85))
    van = L.prim("cube", loc=tuple(OFF + Vector((1.2, 4.0, 1.0))), name="vehicle")
    van.scale = (2.2, 1.0, 1.0)
    L.assign(van, L.mat_principled("vanm", (0.03, 0.03, 0.035), rough=0.5))
    bl = L.point(tuple(OFF + Vector((0.6, 3.0, 2.2))), energy=0, color=(0.1, 0.3, 1.0), radius=0.1, name="bluelight")
    keys = [(1, 0)]
    for f in range(cut, n + 1):
        keys.append((f, 2500 if ((f - cut) // 3) % 2 == 0 else 50))
    C.key_energy(bl, keys)
    C.constant_keys(bl.data)
    flakes = C.cloud(tuple(OFF + Vector((0, 1, 1.5))), (8, 6, 3), count=1200, radius=0.006, color=(1, 1, 1), emit=0.2, seed=3)
    C.drift(flakes, n, (0.1, 0, -0.4))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (2.4, -1.2, -2.7), (0.05, 0.25, -2.9)), (cut - 1, (2.1, -2.0, -2.6), (0.05, 0.25, -2.9)),
                       (cut, tuple(OFF + Vector((-1.5, -5.0, 1.4))), tuple(OFF + Vector((0.8, 3.5, 0.5)))),
                       (n, tuple(OFF + Vector((-1.4, -4.7, 1.4))), tuple(OFF + Vector((0.8, 3.5, 0.5))))],
              shake=0.01, rot_shake=0.002)
    for o in (al,):
        C.key_energy(o, [(1, o.data.energy), (cut - 1, o.data.energy), (cut, 0)])
        C.constant_keys(o.data)
    L.bake_static()


# ============================================================================ U-shaped section through the mountain

ROUTE = [(-2.2, 0.62), (-2.18, 0.3), (-2.0, -0.15), (-1.6, -0.55), (-1.0, -0.8), (-0.35, -0.9), (0.25, -0.92),
         (0.8, -0.82), (1.35, -0.45), (1.8, 0.1), (2.1, 0.65), (2.15, 0.95)]
SQUEEZE = (0.25, -0.92)
MOUNTAIN = [(-3.4, 0.62), (-2.36, 0.62), (-2.04, 0.62), (-1.6, 0.95), (-1.0, 1.6), (-0.3, 2.25), (0.3, 2.55),
            (0.9, 2.2), (1.5, 1.7), (2.0, 1.25), (2.4, 1.1), (3.4, 0.95), (3.4, -6.5), (-3.4, -6.5)]


def _usection(L, n):
    C.world_black((0.0, 0.0, 0.0))
    widths = [0.12, 0.09, 0.09, 0.1, 0.1, 0.09, 0.045, 0.09, 0.1, 0.1, 0.11, 0.2]
    band = C.offset_band(ROUTE, widths)
    xs = C.xsection(band, lambda z: z, x_scale=1.0, extent=(-3.4, 3.4, -6.5, 2.6), outer_poly=MOUNTAIN,
                    outline_color=(0.3, 0.95, 1.0), outline_strength=2.5, name="plura",
                    rock_mat_=L.mat_noise_surface("mtn", (0.02, 0.022, 0.026), (0.08, 0.085, 0.095), scale=1.4, bump=0.2))
    snow = C.emis("snowline", (0.95, 0.97, 1.0), 3.0)
    C.curve([(x, -0.43, z + 0.01) for x, z in MOUNTAIN[:12]], thickness=0.03, mat=snow, name="snow")
    C.curve([(-2.36, -0.43, 0.62), (-2.04, -0.43, 0.62)], thickness=0.03, mat=C.emis("pondice", (0.6, 0.95, 1.0), 6),
            name="pond")
    C.text("PLURA", (-2.2, -0.45, 0.95), size=0.24, color=(1, 1, 1), strength=3, name="lab_plura")
    C.text("STEINUGLEFLÅGET", (1.75, -0.45, 1.55), size=0.17, color=(1, 1, 1), strength=3, name="lab_exit")
    # red squeeze marker
    ring = L.prim("torus", loc=(SQUEEZE[0], -0.46, SQUEEZE[1]), rot=(math.pi / 2, 0, 0), major_radius=0.17,
                  minor_radius=0.014, name="sq_ring")
    rm = C.emis("sqm", (1.0, 0.12, 0.08), 6)
    L.assign(ring, rm)
    C.text("SQUEEZE", (SQUEEZE[0], -0.45, SQUEEZE[1] - 0.32), size=0.14, color=(1, 0.3, 0.25), strength=4, name="lab_sq")
    L.area((-3, -4, 4), (math.radians(60), 0, math.radians(-35)), energy=500, size=4, color=(0.7, 0.85, 1.0))
    cam = C.camera(lens=50)
    route3 = [Vector((x, -0.47, z)) for x, z in ROUTE]
    return route3, ring, rm


def _cam_u(cam, n, keys):
    # keys: (frame, cx, cz, dist)
    C.aim_cam(cam, n, [(f, (cx + 0.6 * d / 13.9, -d, cz + 0.4 * d / 13.9), (cx, 0, cz)) for f, cx, cz, d in keys])


def _pulse(rm, n, period=12, hi=8.0, lo=1.5):
    em = rm.node_tree.nodes["Emission"].inputs[1]
    C.key_input(em, [(f, hi if (f // (period // 2)) % 2 == 0 else lo) for f in range(1, n + 1, period // 2)])


def S02(L, n):
    route, ring, rm = _usection(L, n)
    _cam_u(cam := bpy.context.scene.camera, n, [(1, -2.0, 0.4, 5.0), (20, -1.9, 0.35, 5.6), (n - 15, 0.0, 0.25, 13.9),
                                                (n, 0.0, 0.25, 13.9)])
    line = C.curve([tuple(p) for p in route], thickness=0.028, mat=C.emis("route", C.CYAN, 6), name="route")
    C.grow_curve(line, [(1, 0.0), (8, 0.02), (n - 15, 1.0)])
    head, _, _ = C.glow_dot(tuple(route[0]), C.CYAN, r=0.05, name="head")
    C.move_along(head, [tuple(p) for p in route], [(8, 0.0), (n - 15, 1.0)])
    _pulse(rm, n)
    L.bake_static()


def S06(L, n):
    route, ring, rm = _usection(L, n)
    _cam_u(bpy.context.scene.camera, n, [(1, -1.2, 0.25, 11.0), (n, 1.2, 0.25, 11.0)])
    rp = [tuple(p) for p in route]
    dots = []
    for i in range(5):
        d, _, _ = C.glow_dot(rp[0], C.CYAN, r=0.045, halo=3.0, name=f"d{i}")
        C.move_along(d, rp, [(6 + i * 3, 0.0), (n - 12 + i, 0.96 - i * 0.012)])
        dots.append(d)
    arrow = C.curve(rp, thickness=0.02, mat=C.emis("arrow", (0.85, 1, 1), 4), name="arrow")
    C.grow_curve(arrow, [(1, 0.0), (n - 12, 1.0)])
    # dry exit chamber + rope ladder icon
    lad = C.emis("ladder", (1.0, 0.85, 0.4), 4)
    lx, lz = 2.15, 0.95
    for sx in (-0.07, 0.07):
        C.curve([(lx + sx, -0.47, lz - 0.05), (lx + sx, -0.47, lz + 0.55)], thickness=0.012, mat=lad, name="ladrail")
    for k in range(5):
        C.curve([(lx - 0.07, -0.47, lz + 0.05 + k * 0.11), (lx + 0.07, -0.47, lz + 0.05 + k * 0.11)], thickness=0.01,
                mat=lad, name="ladrung")
    _pulse(rm, n, period=16, hi=4, lo=2)
    L.bake_static()


def S12(L, n):
    route, ring, rm = _usection(L, n)
    _cam_u(bpy.context.scene.camera, n, [(1, -0.2, 0.0, 12.5), (n, 0.0, -0.3, 10.5)])
    rp = [tuple(p) for p in route]
    sq_t = 0.555
    grey, _, gh = C.glow_dot(tuple(C.along(rp, sq_t - 0.012)), (0.55, 0.55, 0.58), r=0.045, halo=2.5, strength=3,
                             name="grey")
    cy, _, _ = C.glow_dot(tuple(C.along(rp, sq_t + 0.06)), C.CYAN, r=0.045, halo=3.0, name="b")
    for i in range(3):
        d, _, _ = C.glow_dot(rp[0], C.CYAN, r=0.045, halo=3.0, name=f"t2_{i}")
        C.move_along(d, rp, [(4 + i * 5, 0.0), (n, 0.33 - i * 0.03)])
    _pulse(rm, n, period=10, hi=10, lo=1.0)
    L.bake_static()


def S15(L, n):
    route, ring, rm = _usection(L, n)
    _cam_u(bpy.context.scene.camera, n, [(1, 0.4, 0.0, 11.0), (n, -1.4, 0.15, 11.0)])
    rp = [tuple(p) for p in route]
    st = 0.53
    od, _, _ = C.glow_dot(tuple(C.along(rp, st)), C.ORANGE, r=0.05, halo=3.2, light=0, name="orange")
    C.move_along(od, rp, [(1, st), (8, st - 0.01), (n - 6, 0.0)])
    back = rp[:]
    trail = C.dotted_path([tuple(C.along(rp, st * (1 - k / 60))) for k in range(61)], spacing=0.07, r=0.016,
                          color=(1.0, 0.6, 0.2), strength=4, name="trail")
    m = len(trail)
    C.pop_in(trail, [int(6 + (n - 14) * k / max(1, m - 1)) for k in range(m)], dur=3)
    C.glow_dot(tuple(C.along(rp, 0.545)), (0.55, 0.55, 0.58), r=0.04, halo=2.5, strength=3, name="grey")
    _pulse(rm, n, period=16, hi=5, lo=2)
    L.bake_static()


# ============================================================================ valley exterior (S03 / S04 / S17)

FIG_POS = [(math.cos(a) * 2.3, math.sin(a) * 2.3) for a in (math.radians(v) for v in (-150, -105, -60, -20, 200))]


def _valley(L, n, tod="day", figures=(0, 1, 2, 3, 4), snow_count=2600):
    C.render_quality(vol_end=80, vol_tile="8", vol_samples=32)
    if tod == "day":
        C.sky_world(top=(0.42, 0.48, 0.58), horizon=(0.72, 0.76, 0.82), ground=(0.4, 0.42, 0.45), strength=1.0)
        C.sun_from(C.sun_dir(8, 160), energy=0.8, color=(0.85, 0.9, 1.0), angle=10)
    else:
        C.sky_world(top=(0.04, 0.05, 0.1), horizon=(0.14, 0.18, 0.3), ground=(0.08, 0.09, 0.12), strength=1.0)
    snowm = L.mat_noise_surface("snow", (0.62, 0.66, 0.72), (0.85, 0.88, 0.92), scale=3, bump=0.15, voronoi=False,
                                rough=0.9)
    C.floor(size=(140, 140), center=(0, 0, 0), strength=0.5, name="snowfield", mat=snowm, ripples=False)
    mtn = L.mat_noise_surface("mtn_snow", (0.12, 0.13, 0.15), (0.8, 0.83, 0.88), scale=0.25, bump=1.0)
    rnd = random.Random(2)
    for i in range(6):
        x = -60 + i * 24 + rnd.uniform(-6, 6)
        m = L.prim("ico", loc=(x, 70 + rnd.uniform(-10, 10), -4), subdivisions=4, radius=1)
        m.scale = (rnd.uniform(16, 26), rnd.uniform(12, 18), rnd.uniform(18, 32))
        L.add_displace(m, strength=3, scale=6, name=f"mtd{i}")
        L.assign(m, mtn)
    # pond ice with the triangle hole
    pond = L.prim("cyl", loc=(0, 0, 0.04), vertices=64, radius=6, depth=0.06, name="pondice")
    L.assign(pond, L.mat_principled("pondice_m", (0.55, 0.62, 0.68), rough=0.25))
    tri = L.prim("cyl", loc=(0, 0, 0.08), vertices=3, radius=0.85, depth=0.02, name="hole")
    L.assign(tri, L.mat_principled("holewater", (0.003, 0.01, 0.015), rough=0.05))
    for i in range(8):
        a = i * 0.8 + 0.3
        L.tree((math.cos(a) * rnd.uniform(14, 24), math.sin(a) * rnd.uniform(14, 24) + 6, 0), height=rnd.uniform(4, 7),
               seed=10 + i)
    suit = (0.025, 0.03, 0.045)
    metal = L.mat_principled("tankm", (0.55, 0.57, 0.6), metal=0.8, rough=0.35)
    figs = []
    for i in figures:
        x, y = FIG_POS[i]
        f = L.char_figure(f"fig{i}", color=suit, height=1.78)
        f["root"].location = (x, y, 0.05)
        f["root"].rotation_euler = (0, 0, math.atan2(-x, y) + math.pi)  # face the hole
        for sx in (-0.09, 0.09):
            t = L.prim("cyl", loc=(sx, -0.2, 0.3), vertices=12, radius=0.085, depth=0.65, name="twin")
            L.assign(t, metal)
            t.parent = f["pelvis"]
        figs.append(f)
    # sled with tank stacks
    sled = L.prim("cube", loc=(3.6, -2.4, 0.2), name="sled")
    sled.scale = (0.5, 1.1, 0.08)
    L.assign(sled, L.mat_principled("sledm", (0.5, 0.12, 0.08), rough=0.6))
    for k in range(4):
        t = L.prim("cyl", loc=(3.6 + (k % 2) * 0.22 - 0.11, -2.4 + (k // 2) * 0.5 - 0.25, 0.55), vertices=12,
                   radius=0.09, depth=0.65, name="sledtank")
        L.assign(t, metal)
    snow = C.cloud((0, -6, 6), (36, 28, 14), count=snow_count, radius=0.008, color=(1, 1, 1), emit=0.4, seed=7,
                   name="snowfall")
    C.drift(snow, n, (0.15, 0.0, -0.9))
    return figs


def S03(L, n):
    figs = _valley(L, n, "day")
    for f in figs[::2]:
        L.anim_walk(f, 1, n, stride=0.12, rate=0.4)
    for i, f in enumerate(figs):  # breath vapour
        hp = f["root"].location + Vector((0, 0, 1.75))
        v = C.cloud(tuple(hp), (0.3, 0.3, 0.2), count=60, radius=0.008, color=(1, 1, 1), emit=0.3, seed=20 + i)
        C.drift(v, n, (0.02, 0, 0.1))
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (2, -34, 24), (0, 0, 0)), (n, (0.4, -9.5, 4.6), (0, 0, 0.4))], shake=0.03, rot_shake=0.002,
              rate=0.3)
    L.bake_static()


def S04(L, n):
    figs = _valley(L, n, "dusk", figures=(0, 2, 3))
    # where two others stood: footprints only
    fp = L.mat_principled("fp", (0.25, 0.28, 0.34), rough=0.9)
    for i in (1, 4):
        x, y = FIG_POS[i]
        for k, (dx, dy) in enumerate(((-0.12, 0), (0.12, 0.05))):
            o = L.prim("cyl", loc=(x + dx, y + dy, 0.075), vertices=10, radius=0.1, depth=0.01, name="footprint")
            o.scale = (0.7, 1.3, 1)
            L.assign(o, fp)
    # work lamp
    pole = L.prim("cyl", loc=(4.4, -1.6, 1.0), vertices=8, radius=0.03, depth=2.0, name="pole")
    L.assign(pole, L.mat_principled("polem", (0.05, 0.05, 0.05)))
    bulb = L.prim("sphere", loc=(4.4, -1.6, 2.05), segments=10, ring_count=6, radius=0.08)
    L.assign(bulb, C.emis("bulb", (1, 0.8, 0.5), 30))
    L.point((4.4, -1.6, 2.0), energy=900, color=(1, 0.75, 0.45), radius=0.1, name="worklamp")
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.4, -9.5, 4.6), (0, 0, 0.4)), (n, (0.4, -9.3, 4.55), (0, 0, 0.4))], shake=0.004,
              rot_shake=0.001)
    L.bake_static()


def S17(L, n):
    _valley(L, n, "day", figures=(), snow_count=2000)
    tape = L.mat_principled("tape", (0.9, 0.1, 0.08), rough=0.5, emit=(0.6, 0.05, 0.03), emit_strength=0.3)
    white = L.mat_principled("tapew", (0.9, 0.9, 0.88), rough=0.5)
    posts = [(-1.4, -1.2), (1.4, -1.2), (1.4, 1.3), (-1.4, 1.3)]
    for x, y in posts:
        p = L.prim("cyl", loc=(x, y, 0.5), vertices=8, radius=0.035, depth=1.0, name="post")
        L.assign(p, white)
    for (x0, y0), (x1, y1) in zip(posts, posts[1:] + posts[:1]):
        segs = 8
        for k in range(segs):
            t0, t1 = k / segs, (k + 1) / segs
            sag = 0.08 * math.sin(math.pi * (t0 + t1) / 2)
            o = C.curve([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0, 0.85 - sag),
                         (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1, 0.85 - sag)], thickness=0.025,
                        mat=tape if k % 2 == 0 else white, name="tape")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.6, -6.5, 1.6), (0, 0, 0.6)), (n, (0.5, -5.4, 1.5), (0, 0, 0.6))], shake=0.008)
    L.dof(cam, distance=1.2, fstop=1.0)
    L.bake_static()


# ============================================================================ S05 map

NORDIC = [(7.0, 58.0), (5.5, 58.7), (5.0, 60.0), (4.9, 61.0), (5.0, 62.0), (6.5, 62.6), (8.0, 63.3), (9.8, 63.9),
          (11.0, 64.8), (12.5, 65.9), (13.5, 67.0), (14.5, 67.9), (15.5, 68.5), (16.5, 69.2), (18.5, 69.8),
          (20.5, 70.2), (23.0, 70.8), (25.8, 71.1), (28.0, 70.9), (31.0, 70.3), (29.0, 69.6), (29.5, 69.0),
          (28.5, 68.0), (29.5, 67.0), (30.0, 65.5), (29.8, 64.0), (31.0, 63.0), (29.0, 61.5), (27.8, 60.5),
          (25.0, 60.2), (23.0, 59.9), (21.5, 60.6), (21.3, 61.8), (21.5, 63.0), (23.0, 63.9), (24.5, 64.9),
          (25.5, 65.4), (24.6, 65.8), (22.0, 65.6), (21.0, 64.5), (19.5, 63.5), (17.8, 62.5), (17.3, 61.0),
          (18.5, 60.2), (18.8, 59.3), (17.0, 58.6), (16.5, 57.5), (16.2, 56.4), (14.5, 56.0), (12.8, 55.5),
          (12.5, 56.3), (12.0, 57.5), (11.5, 58.5), (10.8, 59.2), (10.0, 59.0), (9.0, 58.6), (8.0, 58.1)]
BORDER_NS = [(11.5, 59.0), (12.5, 61.0), (12.2, 62.5), (12.3, 63.5), (14.0, 64.5), (14.5, 65.5), (15.5, 66.5),
             (17.0, 68.0), (19.0, 68.5), (20.5, 69.0)]
BORDER_SF = [(20.5, 69.0), (23.5, 68.5), (24.0, 67.0), (24.6, 65.8)]
BORDER_NF = [(20.5, 69.0), (25.0, 68.6), (28.5, 69.5), (29.0, 69.6)]
PLURA_LL = (14.6, 66.3)


def mp(lon, lat, z=0.0):
    k = 1.0
    return ((lon - 17.0) * math.cos(math.radians(65)) * k, (lat - 64.5) * k, z)


def S05(L, n):
    import bmesh
    C.world_black((0.005, 0.01, 0.02))
    sea = L.prim("plane", loc=(0, 0, -0.02), size=60, name="sea")
    sm = L.mat_noise_surface("sea", (0.01, 0.02, 0.04), (0.02, 0.04, 0.07), scale=0.5, bump=0.05, voronoi=False)
    L.assign(sea, sm)
    bm = bmesh.new()
    vs = [bm.verts.new(mp(lo, la)) for lo, la in NORDIC]
    bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    land = L.mesh_from_bm("land", bm)
    so = land.modifiers.new("solid", "SOLIDIFY")
    so.thickness = 0.12
    L.assign(land, L.mat_noise_surface("landm", (0.05, 0.07, 0.1), (0.09, 0.12, 0.16), scale=2, bump=0.2, voronoi=False))
    coast = C.curve([mp(lo, la, 0.01) for lo, la in NORDIC + NORDIC[:1]], thickness=0.025,
                    mat=C.emis("coast", C.CYAN, 3), name="coast")
    bmat = C.emis("border", (0.5, 0.6, 0.7), 1.5)
    for b in (BORDER_NS, BORDER_SF, BORDER_NF):
        C.curve([mp(lo, la, 0.02) for lo, la in b], thickness=0.012, mat=bmat, name="border")
    # Arctic Circle (66.56 N) dashed
    ac = C.emis("arctic", (0.85, 0.9, 1.0), 2.5)
    lon = 3.0
    while lon < 33:
        C.curve([mp(lon, 66.56, 0.03), mp(lon + 0.6, 66.56, 0.03)], thickness=0.012, mat=ac, name="ac")
        lon += 1.1
    C.text("ARCTIC CIRCLE", mp(24.5, 66.8, 0.04), size=0.32, color=(0.85, 0.9, 1.0), strength=2.5, rot=(0, 0, 0),
           name="aclab")
    for name_, ll, sz in (("NORWAY", (8.4, 61.4), 0.8), ("SWEDEN", (15.6, 62.6), 0.7), ("FINLAND", (26.4, 63.2), 0.65)):
        C.text(name_, mp(*ll, 0.14), size=sz, color=(0.7, 0.8, 0.9), strength=3.0, rot=(0, 0, 0), name="ctry")
    # pin
    px, py, _ = mp(*PLURA_LL)
    pin = L.link(bpy.data.objects.new("pin", None))
    head, _, _ = C.glow_dot((0, 0, 0.6), C.CYAN, r=0.12, halo=2.5, name="pinhead")
    head.parent = pin
    stem = L.prim("cone", loc=(0, 0, 0.3), vertices=12, radius1=0.0, radius2=0.08, depth=0.6, name="pinstem")
    L.assign(stem, C.emis("pinstem_m", C.CYAN, 3))
    stem.parent = pin
    land_ring = L.prim("torus", loc=(px, py, 0.05), major_radius=0.3, minor_radius=0.02, name="pinring")
    L.assign(land_ring, C.emis("pinring_m", C.CYAN, 5))
    drop = int(n * 0.6)
    C.key_loc(pin, [(1, (px, py, 2.5)), (drop - 6, (px, py, 2.5)), (drop, (px, py, 0.05)), (drop + 3, (px, py, 0.15)),
                    (drop + 6, (px, py, 0.05))])
    C.key_scale(land_ring, [(1, 0.0), (drop, 0.0), (drop + 4, 1.4), (n, 1.0)])
    C.text("PLURA", (px + 0.3, py + 0.1, 0.16), size=0.55, color=(1, 1, 1), strength=4, rot=(0, 0, 0), align="LEFT",
           name="plab")
    L.sun(rot=(0.3, 0.2, 0.4), energy=2.0, color=(0.8, 0.9, 1.0))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.6, -1.6, 21), (0.6, -0.6, 0)), (int(n * 0.55), (px + 0.5, py - 1.8, 13.0), (px + 0.5, py - 0.2, 0)),
                       (n, (px + 0.5, py - 1.6, 12.0), (px + 0.5, py - 0.1, 0))])
    L.bake_static()


# ============================================================================ Plura tunnels

def _plura_water(L, density=0.03, center=(0, 0, 0), size=(40, 40, 12)):
    C.world_black((0.0, 0.006, 0.01))
    C.render_quality(vol_end=35)
    return C.water(center=center, size=size, color=(0.5, 0.72, 0.82), density=density, absorption=(0.1, 0.22, 0.25))


def _amb(L, pts, energy=250, color=(0.45, 0.7, 0.95)):
    for p in pts:
        L.point(p, energy=energy, color=color, radius=1.0, name="amb")


MARBLE = lambda: C.rock_mat("marble", (0.08, 0.1, 0.12), (0.42, 0.47, 0.52), scale=1.1, bump=0.7)


def _scooter_diver(name, fins, light=2200, beam_len=6, tanks="doubles"):
    d = C.diver(name, fins=fins, rebreather=False, tanks=tanks, light_energy=light, beam_len=beam_len, beam_strength=0.25)
    sc = L_prim_scooter(name)
    sc.parent = d["root"]
    return d


def L_prim_scooter(name):
    import studio_lib as L
    s = L.prim("cyl", loc=(0, 0.95, -0.15), rot=(math.pi / 2, 0, 0), vertices=16, radius=0.11, depth=0.55,
               name=name + "_scooter")
    L.assign(s, L.mat_principled(name + "_scm", (0.85, 0.65, 0.05), rough=0.4))
    L.smooth(s)
    return s


def S07(L, n):
    _plura_water(L, density=0.025, size=(60, 20, 12))
    path = [(-24, 0, 0), (-10, 0.3, 0.3), (2, 0, -0.2), (14, -0.3, 0.2), (28, 0, 0)]
    C.tunnel(path, radius=3.2, seed=3, rough=0.5, mat=MARBLE(), name="plura_t")
    _amb(L, [(x, 0.5, 1.2) for x in (-10, -4, 2, 8, 14)], energy=400)
    C.line([(-24, 0.9, -1.6), (-6, 1.0, -1.7), (6, 0.8, -1.6), (28, 0.9, -1.6)], thickness=0.01, emit=0.8, name="gl")
    divers = []
    for i, (fins, y, z, st) in enumerate(((FIN_A, 0.7, 0.2, 1), (FIN_B, 1.4, -0.3, 8))):
        d = _scooter_diver(f"t1d{i}", fins)
        d["root"].rotation_euler = (0, 0, -math.pi / 2)
        C.key_loc(d["root"], [(1, (-5 - st * 0.3, y, z)), (34, (7 - st * 0.3, y, z + 0.1))])
        L.linear_fcurves(d["root"])
        L.anim_swim(d, n, kick_rate=0.3, amp=0.08)
        divers.append(d)
    # flash / time jump
    cam = C.camera(lens=20)
    C.aim_cam(cam, n, [(1, (0.0, -2.3, -0.3), (0.6, 3.0, 0.0)), (n, (0.2, -2.3, -0.3), (0.8, 3.0, 0.0))], shake=0.01)
    fl = L.prim("plane", loc=(0, 0, -0.2), size=0.6, name="flash")
    fl.parent = cam
    fm = C.emis("flashm", (1, 1, 1), 0.0)
    L.assign(fl, fm)
    fe = fm.node_tree.nodes["Emission"].inputs[1]
    C.key_input(fe, [(1, 0), (34, 0), (37, 30), (39, 30), (44, 0)])
    C.hide_from_frame([fl], f_show=34, f_hide=45)
    # team two: three lights entering later
    for i, fins in enumerate((FIN_C, FIN_T2[0], FIN_T2[1])):
        d = _scooter_diver(f"t2d{i}", fins, light=1800)
        d["root"].rotation_euler = (0, 0, -math.pi / 2)
        y = 1.0 + i * 0.7
        C.key_loc(d["root"], [(1, (-30, y, 0)), (40, (-9 - i * 2, y, 0.1 * i)), (n, (0.5 - i * 2.2, y, 0.1 * i))])
        L.linear_fcurves(d["root"])
        C.hide_from_frame([o for o in bpy.data.objects if o.name.startswith(f"t2d{i}")], f_show=40)
    p = C.cloud((0, 1, 0), (16, 5, 4), count=2000, radius=0.005, emit=0.06, seed=2)
    C.drift(p, n, (0.05, 0, 0.02))
    C.cam_fill(cam, energy=60, color=(0.6, 0.8, 0.95))
    L.bake_static()


def _squeeze(L, n, density=0.04, wide_far=True):
    """Big tunnel (−Y side) ends at a rock face with a low flattened slot at y≈0; tight restriction (r≈0.8) beyond."""
    import studio_lib as Ls
    _plura_water(L, density=density, center=(0, 0, 0), size=(14, 30, 8))
    marble = MARBLE()
    C.tunnel([(0, -16, 0.3), (0.3, -8, 0.4), (0, -1.0, 0)], radius=2.3, seed=5, rough=0.45, mat=marble, name="tA")
    C.tunnel([(0, -0.5, -0.5), (0.1, 1.5, -0.55), (0.2, 3.0, -0.5)], radius=0.8, seed=8, rough=0.3, mat=marble,
             name="tB", flatten=0.35)
    if wide_far:
        C.tunnel([(0.2, 2.6, -0.4), (0.4, 6, -0.3), (0.0, 12, 0)], radius=1.5, seed=9, rough=0.4, mat=marble, name="tC")
    face = L.prim("cyl", loc=(0, -0.2, 0), rot=(math.pi / 2, 0, 0), vertices=48, radius=4.0, depth=1.0, name="face")
    sub = face.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 2
    L.add_displace(face, strength=0.3, scale=0.7, name="face_d")
    hole = L.prim("cyl", loc=(0, -0.2, -0.5), rot=(math.pi / 2, 0, 0), vertices=32, radius=0.7, depth=3, name="slotcut")
    hole.scale = (1.0, 0.5, 1.0)
    bo = face.modifiers.new("slot", "BOOLEAN")
    bo.object = hole
    bo.operation = "DIFFERENCE"
    hole.hide_render = True
    hole.hide_viewport = True
    L.assign(face, marble)
    C.rocks([(-1.2, -1.0, -1.3), (1.3, -1.2, -1.3), (0.7, -0.9, -1.0), (-0.8, -1.6, -1.4)], count=4, size=(0.35, 0.6),
            seed=4, mat=marble)
    C.floor(size=(6, 18), center=(0, -6, -1.55), strength=0.15, name="siltbed")
    _amb(L, [(0.5, -3.0, 1.2), (-0.6, -7.0, 1.0)], energy=220)
    if wide_far:
        _amb(L, [(0.3, 5.5, 0.6)], energy=120)
    return Vector((0, -0.2, -0.5))


def S08(L, n):
    slot = _squeeze(L, n, density=0.04)
    for i, (pos, col) in enumerate((((-0.8, -7.6, 0.3), C.TORCH), ((0.9, -7.9, 0.1), (0.95, 0.97, 1.0)))):
        sp = L.spot(pos, (0, 0, 0), energy=2600, size_deg=16, blend=0.4, color=col, name=f"beam{i}")
        sp.rotation_mode = "QUATERNION"
        tgt = slot + Vector((0.15 * (1 if i else -1), 0, 0))
        q0 = (tgt + Vector((1.5 * (-1 if i else 1), 0, 0.8)) - Vector(pos)).to_track_quat("-Z", "Y")
        q1 = (tgt - Vector(pos)).to_track_quat("-Z", "Y")
        sp.rotation_quaternion = q0
        sp.keyframe_insert("rotation_quaternion", frame=1)
        sp.rotation_quaternion = q1
        sp.keyframe_insert("rotation_quaternion", frame=int(n * 0.7))
        pass
    p = C.cloud((0, -3, -0.6), (4, 5, 2), count=2000, radius=0.005, emit=0.06, seed=3)
    C.drift(p, n, (0.02, 0.03, 0.01))
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.25, -6.8, 0.1), (0, -0.2, -0.55)), (n, (0.15, -4.4, -0.2), (0, -0.2, -0.55))],
              shake=0.012, rot_shake=0.003)
    C.cam_fill(cam, energy=20)
    L.bake_static()


def S09(L, n):
    slot = _squeeze(L, n, density=0.045)
    d = C.diver("diverB", fins=FIN_B, rebreather=False, tanks="doubles", light_energy=1800, beam_len=4, beam_strength=0.25)
    r = d["root"]
    turn0, turn1 = 46, 66
    C.key_loc(r, [(1, (0.05, -0.7, -0.5)), (turn0, (0.15, 2.0, -0.45)), (n, (0.18, 2.1, -0.45))])
    r.rotation_euler = (0, 0, 0)
    r.keyframe_insert("rotation_euler", frame=turn0)
    r.rotation_euler = (0.2, 0.3, math.pi * 0.92)
    r.keyframe_insert("rotation_euler", frame=turn1)
    L.anim_swim(d, n, kick_rate=0.9, amp=0.25)
    puffs = C.cloud((0, 0.2, -0.75), (1.4, 1.5, 0.5), count=1200, radius=0.005, emit=0.08, seed=5)
    C.key_scale(puffs, [(1, 0.5), (n, 1.4)])
    C.drift(puffs, n, (0, 0.1, 0.1))
    behind, dens, _ = C.noisy_volume((0, -1.6, -0.4), (2.5, 2.5, 1.6), color=(0.6, 0.55, 0.45), density=2.0, name="behind")
    L.point((0.0, -1.8, -0.35), energy=180, color=C.TORCH, radius=0.1, name="buddyglow")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.8, 5.6, 0.0), (0.05, 0.5, -0.5)), (n, (0.75, 5.4, -0.02), (0.05, -0.1, -0.5))],
              shake=0.01, rot_shake=0.003)
    c = cam.data
    c.dof.use_dof = True
    c.dof.aperture_fstop = 1.2
    for f, dist in ((1, 5.0), (turn0, 3.0), (turn1, 3.0), (n, 5.7)):
        c.dof.focus_distance = dist
        c.dof.keyframe_insert("focus_distance", frame=f)
    C.cam_fill(cam, energy=25)
    C.rim_light((0.15, 2.6, -0.45), (0.5, 2.5, 1.5), energy=400, name="brim")
    L.bake_static()


def _blink_keys(n, pattern=(3, 2, 3, 2, 3, 6), on=1600, off=40, start=1):
    keys = []
    f = start
    i = 0
    state = True
    while f <= n:
        keys.append((f, on if state else off))
        f += pattern[i % len(pattern)]
        i += 1
        state = not state
    return keys


def _stuck_buddy(L, n, slot):
    sil = L.mat_principled("buddysil", (0.015, 0.015, 0.02), rough=0.7)
    root = L.link(bpy.data.objects.new("buddyA", None))
    root.location = slot + Vector((0.05, -0.9, 0.1))
    for sx in (-0.09, 0.09):
        t = L.prim("cyl", loc=(sx, 0.0, 0.18), rot=(math.pi / 2, 0, 0), vertices=12, radius=0.085, depth=0.7, name="btank")
        L.assign(t, sil)
        t.parent = root
    h = L.prim("sphere", loc=(0, 0.45, 0.02), segments=12, ring_count=8, radius=0.13, name="bhead")
    L.assign(h, sil)
    h.parent = root
    b = L.prim("sphere", loc=(0, 0, 0), segments=12, ring_count=8, name="bbody")
    b.scale = (0.22, 0.42, 0.16)
    L.assign(b, sil)
    b.parent = root
    torch = L.spot((0.15, 0.55, -0.05), (math.radians(80), 0, math.radians(-10)), energy=1600, size_deg=24,
                   color=C.TORCH, name="buddytorch")
    torch.parent = root
    lens = L.prim("sphere", loc=(0.15, 0.58, -0.05), segments=8, ring_count=6, radius=0.03, name="blens")
    lm = C.emis("blensm", C.TORCH, 25)
    L.assign(lens, lm)
    lens.parent = root
    # snagged cord loop from the slot edge around the tank valve
    cord = C.curve([tuple(slot + Vector((0.55, 0.0, 0.2))), tuple(slot + Vector((0.4, -0.4, 0.4))),
                    tuple(root.location + Vector((0.12, -0.25, 0.35))), tuple(root.location + Vector((-0.1, -0.3, 0.3))),
                    tuple(root.location + Vector((-0.05, 0.1, 0.32))), tuple(slot + Vector((-0.5, 0.05, 0.1)))],
                   thickness=0.006, mat=L.mat_principled("cord", (0.95, 0.95, 0.9), emit=(0.9, 0.9, 0.85), emit_strength=1.2),
                   name="cord", smooth_pts=True)
    return root, torch, lm


def S10(L, n):
    slot = _squeeze(L, n, density=0.05, wide_far=True)
    root, torch, lm = _stuck_buddy(L, n, slot)
    C.key_energy(torch, _blink_keys(n))
    C.constant_keys(torch.data)
    em = lm.node_tree.nodes["Emission"].inputs[1]
    C.key_input(em, [(f, 25 if e > 100 else 0.5) for f, e in _blink_keys(n)])
    C.constant_keys(lm.node_tree)
    cloud, dens, _ = C.noisy_volume(tuple(slot + Vector((0, -1.0, 0))), (2.6, 2.6, 1.8), color=(0.6, 0.55, 0.45),
                                    density=2.5, scale=2.0, name="siltcloud")
    C.key_scale(cloud, [(1, 0.9), (n, 1.15)])
    p = C.cloud(tuple(slot + Vector((0, -0.8, 0))), (2, 1.6, 1.2), count=1200, radius=0.0025, emit=0.08, seed=9)
    C.drift(p, n, (0.03, 0.05, 0.03))
    cam = C.camera(lens=50)
    C.aim_cam(cam, n, [(1, (0.05, 2.4, -0.4), (0.0, -1.2, -0.45)), (n, (0.05, 2.1, -0.42), (0.0, -1.2, -0.45))],
              shake=0.006, rot_shake=0.004, rate=1.2, shake_keys=[(1, 0.4), (n, 2.5)])
    sp = L.spot((0.1, 0.05, 0), (0, 0, 0), energy=900, size_deg=30, blend=0.5, color=(0.95, 0.97, 1.0), name="myhelmet")
    sp.parent = cam
    L.bake_static()


def S11(L, n):
    slot = _squeeze(L, n, density=0.04, wide_far=True)
    root, torch, lm = _stuck_buddy(L, n, slot)
    torch.data.energy = 500
    cloud, dens, _ = C.noisy_volume(tuple(slot + Vector((0, -0.8, -0.1))), (2.6, 2.6, 1.8), color=(0.6, 0.55, 0.45),
                                    density=2.0, scale=2.0, name="settle")
    C.key_input(dens, [(1, 2.2), (n, 0.6)])
    C.key_loc(cloud, [(1, tuple(cloud.location)), (n, tuple(cloud.location + Vector((0, 0, -0.3))))])
    d = C.diver("diverB", fins=FIN_B, rebreather=False, tanks="doubles", light_energy=1500, beam_len=3.5, beam_strength=0.22)
    r = d["root"]
    r.location = (0.15, 1.7, -0.42)
    r.rotation_euler = (0.1, 0.25, math.pi * 0.95)
    L.anim_swim(d, n, kick_rate=0.12, amp=0.05)
    p = C.cloud((0, 1.0, -0.2), (2.2, 3, 1.4), count=1600, radius=0.004, emit=0.06, seed=5)
    C.drift(p, n, (0.0, 0.0, -0.08))
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (0.9, 6.2, 0.25), (0.0, 0.8, -0.5)), (n, (0.95, 6.6, 0.3), (0.0, 0.8, -0.5))], shake=0.004)
    C.cam_fill(cam, energy=30)
    C.rim_light((0.15, 1.7, -0.4), (-0.4, 2.0, 1.3), energy=350, name="b2rim")
    L.bake_static()


def S14(L, n):
    slot = _squeeze(L, n, density=0.045, wide_far=False)
    sil = L.mat_principled("block", (0.012, 0.012, 0.015), rough=0.7)
    blk = L.prim("sphere", loc=tuple(slot + Vector((0, 0.35, 0.0))), segments=16, ring_count=10, name="blockage")
    blk.scale = (0.5, 0.5, 0.28)
    L.assign(blk, sil)
    t = L.prim("cyl", loc=tuple(slot + Vector((0.25, 0.1, 0.08))), rot=(math.pi / 2, 0.3, 0), vertices=12, radius=0.085,
               depth=0.6, name="blocktank")
    L.assign(t, L.mat_principled("bt", (0.2, 0.21, 0.22), metal=0.6, rough=0.4))
    hose = L.prim("torus", loc=tuple(slot + Vector((-0.25, 0.05, 0.05))), rot=(0.4, 0.8, 0), major_radius=0.12,
                  minor_radius=0.015, name="blockhose")
    L.assign(hose, sil)
    d = C.diver("diverC", fins=FIN_C, rebreather=False, tanks="doubles", light_energy=1100, beam_len=3.2,
                beam_strength=0.25, beam_deg=20)
    r = d["root"]
    C.key_loc(r, [(1, (0.25, -2.6, -0.4)), (int(n * 0.6), (0.2, -1.6, -0.45)), (n, (0.2, -1.55, -0.45))])
    r.rotation_euler = (-0.05, 0, 0.05)
    L.anim_swim(d, n, kick_rate=0.5, amp=0.15)
    d["torch"].rotation_euler = (math.pi / 2 - 0.1, 0, 0.0)
    p = C.cloud((0, -1.2, -0.5), (2.5, 2.5, 1.2), count=1600, radius=0.004, emit=0.08, seed=8)
    C.drift(p, n, (0.02, 0.0, 0.03))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.9, -4.4, 0.7), (0.0, -0.2, -0.6)), (int(n * 0.7), (0.8, -3.4, 0.55), (0.0, -0.2, -0.6)),
                       (n, (0.8, -3.35, 0.55), (0.0, -0.2, -0.6))], shake=0.008, rot_shake=0.002)
    C.cam_fill(cam, energy=15)
    C.rim_light((0.2, -2.0, -0.35), (-1.0, -1.0, 1.5), energy=300, color=(0.4, 0.7, 1.0), name="crim")
    L.bake_static()


def S13(L, n):
    _plura_water(L, density=0.06, size=(40, 16, 12))
    C.tunnel([(-10, 0, 0), (0, 0.5, -0.5), (12, -0.3, -1.2), (24, 0, -1.0)], radius=3.6, seed=12, rough=0.55,
             mat=C.rock_mat("deep", (0.03, 0.035, 0.045), (0.2, 0.22, 0.26)), name="deep")
    C.line([(-10, -0.4, -2.0), (4, -0.2, -2.2), (14, 0.0, -2.6), (24, 0.0, -2.6)], thickness=0.01, emit=0.7, name="gl")
    sil = L.mat_principled("t2sil", (0.012, 0.012, 0.015), rough=0.7)
    starts = [(-1.0, 0.0, -0.9), (0.5, 0.6, -0.6), (2.0, -0.4, -1.1)]
    for i, st in enumerate(starts):
        root = L.link(bpy.data.objects.new(f"t2_{i}", None))
        body = L.prim("sphere", loc=(0, 0, 0), segments=12, ring_count=8, name="t2body")
        body.scale = (0.5, 0.17, 0.15)
        L.assign(body, sil)
        body.parent = root
        sp = L.spot((0.5, 0, 0.05), (0, math.radians(90), 0), energy=2000, size_deg=18, blend=0.4, color=C.TORCH,
                    name="t2torch")
        sp.parent = root
        C.beam_cone(sp, length=6, strength=0.45, name="t2beam")
        lens = L.prim("sphere", loc=(0.52, 0, 0.05), segments=8, ring_count=6, radius=0.03)
        L.assign(lens, C.emis("t2l", C.TORCH, 25))
        lens.parent = root
        if i == 1:  # drifts away from the line and stops
            C.key_loc(root, [(1, st), (30, (st[0] + 1.2, st[1] - 0.4, st[2] - 0.2)), (70, (st[0] + 1.6, st[1] - 1.3, st[2] - 0.7)),
                             (n, (st[0] + 1.62, st[1] - 1.32, st[2] - 0.72))])
            root.rotation_euler = (0, 0, 0)
            root.keyframe_insert("rotation_euler", frame=30)
            root.rotation_euler = (0.3, 0.5, -1.1)
            root.keyframe_insert("rotation_euler", frame=70)
        else:
            C.key_loc(root, [(1, st), (n, (st[0] + 5.5, st[1], st[2] - 0.3))])
            L.linear_fcurves(root)
    p = C.cloud((2, 0, -0.8), (10, 5, 3), count=3000, radius=0.005, emit=0.06, seed=3)
    C.drift(p, n, (0.04, 0.0, 0.02))
    cam = C.camera(lens=24)
    _amb(L, [(x, 0.0, 2.6) for x in (-6, 0, 6, 12)], energy=60, color=(0.3, 0.5, 0.85))
    C.aim_cam(cam, n, [(1, (-3.4, -1.1, -1.25), (1.8, 0.0, -0.9)), (n, (-2.7, -0.9, -1.25), (1.8, 0.0, -0.95))],
              shake=0.01, rot_shake=0.002)
    C.cam_fill(cam, energy=15, color=(0.4, 0.6, 0.9))
    L.bake_static()
