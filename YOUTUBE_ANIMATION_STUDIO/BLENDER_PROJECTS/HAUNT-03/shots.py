"""HAUNT-03 — Don't Stop for Her on Archer Avenue (Resurrection Mary). One builder per shot: def Sxx(L, n)."""
import importlib, sys, os, math
_LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PIPELINE", "blender")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import lib_haunted as H
importlib.reload(H)
import bpy
from mathutils import Vector

ROAD_SPEED = 7.5          # m/s (storyboard: 12) so the roadside figure stays in frame for the whole shot
WOMAN_Y = 50.0            # distance of the roadside figure at frame 1
CAM_X, CAM_Z = 1.3, 1.2   # driver's eye in the right lane
GATE_P0, GATE_P1, GATE_T = (0.0, -10.5, 1.6), (0.0, -8.6, 1.6), (0.0, 0.0, 1.05)   # S04 / S14 framing
CAR_STOP_X, CAR_Y = -3.2, -7.3


def _night(L, c=(0.006, 0.008, 0.016), vol_end=90):
    H.eevee_quality()
    L.set_world(c, 1.0)
    try:
        bpy.context.scene.eevee.volumetric_end = vol_end
    except Exception:
        pass


def _sun_dir(L, d, energy=0.3, color=(0.55, 0.65, 1.0), name="moon"):
    s = L.sun(rot=(0, 0, 0), energy=energy, color=color, angle=3, name=name)
    s.rotation_euler = Vector(d).normalized().to_track_quat("-Z", "Y").to_euler()
    return s


def _face(parts, d):
    """Rotate a figure root (faces +Y) to face direction d (x, y)."""
    parts["root"].rotation_euler = (0, 0, math.atan2(-d[0], d[1]))


# --------------------------------------------------------------------------- S01 / S15 driver's POV down Archer Avenue
def _road_pov(L, n, y_start=0.0, woman=True, blur=False):
    _night(L)
    H.archer_road(y0=-30, y1=200, fog=0.022, fog_h=2.6, count=150)
    _sun_dir(L, (0.25, -1.0, -0.55), energy=0.35)
    if woman:
        w = H.pale_woman("mary_road", emit=0.55)
        w["root"].location = (4.9, y_start + WOMAN_Y, 0)
        _face(w, (-1, -0.25))
    y1 = y_start + ROAD_SPEED * n / 24.0
    p0, p1 = (CAM_X, y_start, CAM_Z), (CAM_X, y1, CAM_Z)
    dz = -40 * math.tan(math.radians(6))
    c = H.cam(p0, (CAM_X, y_start + 40, CAM_Z + dz), lens=28)
    H.cam_move(c, [(1, p0, (CAM_X, y_start + 40, CAM_Z + dz)), (n, p1, (CAM_X, y1 + 40, CAM_Z + dz))], ease=False)
    H.handheld(c, n, amp=0.01, rate=1.6, rot_amp=0.002)
    for sx, nm in ((-0.75, "hlL"), (0.65, "hlR")):
        s = L.spot((sx, -0.55, -1.9), (-0.025, 0, 0), energy=2600, size_deg=30, blend=0.45, color=(1.0, 0.88, 0.66), name=nm, radius=0.08)
        s.data.volume_factor = 0.15
        s.parent = c
    rig = H.empty("rainrig", (CAM_X, y_start, 0))
    rig.keyframe_insert("location", frame=1)
    rig.location = (CAM_X, y1, 0)
    rig.keyframe_insert("location", frame=n)
    L.linear_fcurves(rig)
    r = H.rain((0, 8, 2.0), (7, 12, 4), n, count=700, speed=7, emit=0.25)
    r.parent = rig
    if blur:
        L.dof(c, distance=0.6, fstop=0.6)
    return c


def S01(L, n):
    _road_pov(L, n)
    L.bake_static()


def S15(L, n):
    _road_pov(L, n)
    L.bake_static()


# --------------------------------------------------------------------------- S02 map card over the blurred road
def S02(L, n):
    _road_pov(L, n, y_start=20.0, woman=False, blur=True)
    L.bake_static()


# --------------------------------------------------------------------------- S03 / S05 dance hall
def _hall_world(L, n, doors_open=None, fog=0.018):
    _night(L, (0.008, 0.011, 0.022), vol_end=110)
    hall = H.dance_hall(n, doors_open=doors_open)
    H.box_mesh("hallroad", [(0, -29.5, 0.0, 60, 3.5, 0.01)], H.mat_wet_road("hallwet"))
    _sun_dir(L, (0.5, -0.6, -0.6), energy=0.5)
    L.fog_volume(center=(0, -14, 3.0), size=(70, 46, 6), density=fog, color=(0.72, 0.75, 0.85))
    return hall


def S03(L, n):
    _hall_world(L, n)
    p0, p1 = (7.0, -27.0, 0.55), (-1.0, -27.0, 0.55)
    c = H.cam(p0, (5.0, 0, 3.6), lens=35)
    H.cam_move(c, [(1, p0, (5.0, 0, 3.6)), (n, p1, (-3.0, 0, 3.6))], ease=False)
    H.handheld(c, n, amp=0.006, rate=0.4)
    L.bake_static()


def S05(L, n):
    hall = _hall_world(L, n, doors_open=(1, 16))
    man = H.figure("palus", height=1.78, cap=True, coat=False, color=(0.012, 0.012, 0.014))
    w = H.pale_woman("mary_hall")
    car = (-6.0, -8.0)
    for parts, st, x0, dx in ((man, 12, -0.45, 0.0), (w, 16, 0.4, 0.75)):
        start = (x0, 0.9, 0)
        end = (car[0] + 1.2 + dx, car[1] + 2.4 - dx * 0.4, 0)
        d = (end[0] - start[0], end[1] - start[1])
        _face(parts, d)
        parts["root"].location = start
        parts["root"].keyframe_insert("location", frame=1)
        H.walk(parts, st, n - st, stride=0.4, rate=0.9, travel=(start, end), bob=0.015)
    # rim from the doorway + soft fill so the dark suit reads against the gravel
    L.point((0, 0.2, 2.0), energy=200, color=(1.0, 0.62, 0.3), radius=0.4, name="rimdoor")
    p0 = (-3.6, -15.0, 1.55)
    t0 = (-1.2, 0.0, 2.1)
    c = H.cam(p0, t0, lens=40)
    p1 = tuple(p0[i] + (t0[i] - p0[i]) * 0.05 for i in range(3))
    H.cam_move(c, [(1, p0, t0), (int(n * 0.4), p0, t0), (n, p1, (-1.6, 0.0, 2.0))])
    H.handheld(c, n, amp=0.004, rate=0.3)
    L.bake_static()


# --------------------------------------------------------------------------- S06 car interior
def S06(L, n):
    _night(L, (0.006, 0.008, 0.016), vol_end=60)
    paint = L.mat_principled("int_paint", (0.03, 0.028, 0.026), rough=0.35, metal=0.2)
    trim = L.mat_principled("int_trim", (0.09, 0.06, 0.035), rough=0.5)
    seat = L.mat_noise_surface("int_seat", (0.05, 0.035, 0.025), (0.11, 0.08, 0.05), scale=40, bump=0.2, voronoi=False, rough=0.9)
    glass = L.mat_principled("int_glass", (0.6, 0.65, 0.7), rough=0.35, alpha=0.12, emit=(0.4, 0.45, 0.55), emit_strength=0.03)
    try:
        glass.surface_render_method = "BLENDED"
    except Exception:
        pass
    # shell: floor, roof, dash, door panels, pillars
    H.box_mesh("shell", [(0, -0.4, 0.3, 0.82, 1.3, 0.04), (0, -0.4, 1.62, 0.82, 1.3, 0.03),
                         (0, 0.62, 0.86, 0.8, 0.16, 0.18),                     # dash
                         (0.8, -0.3, 0.68, 0.03, 0.95, 0.3), (-0.8, -0.3, 0.68, 0.03, 0.95, 0.3),   # door panels
                         (0.79, 0.52, 1.28, 0.04, 0.05, 0.36), (-0.79, 0.52, 1.28, 0.04, 0.05, 0.36),  # A pillars
                         (0.79, -0.55, 1.28, 0.04, 0.07, 0.36), (-0.79, -0.55, 1.28, 0.04, 0.07, 0.36),  # B pillars
                         (0, 0.56, 1.62, 0.8, 0.05, 0.04), (0, 0.56, 0.98, 0.8, 0.03, 0.02),
                         (0.79, -0.02, 0.99, 0.05, 0.55, 0.02), (-0.79, -0.02, 0.99, 0.05, 0.55, 0.02)], paint)
    H.box_mesh("dashface", [(0, 0.47, 0.92, 0.75, 0.02, 0.1)], trim, bevel=0.01)
    H.box_mesh("bench", [(0, -0.35, 0.55, 0.78, 0.3, 0.1), (0, -0.9, 0.95, 0.78, 0.07, 0.38)], seat, bevel=0.05)
    dial = L.mat_emission("dialglow", (1.0, 0.6, 0.22), 2.2)
    for x in (0.02, 0.26):
        d = L.prim("cyl", loc=(x, 0.455, 0.93), vertices=24, radius=0.06, depth=0.01, rot=(math.pi / 2, 0, 0))
        L.assign(d, dial)
        rim = L.prim("torus", loc=(x, 0.452, 0.93), major_radius=0.064, minor_radius=0.008, rot=(math.pi / 2, 0, 0))
        L.assign(rim, H.mat_brass("dialrim"))
    wheel = L.prim("torus", loc=(-0.4, 0.18, 1.02), major_radius=0.21, minor_radius=0.014, rot=(math.radians(60), 0, 0))
    L.assign(wheel, L.mat_principled("wheelm", (0.02, 0.018, 0.015), rough=0.4))
    col = L.prim("cyl", loc=(-0.4, 0.35, 0.92), vertices=10, radius=0.025, depth=0.4, rot=(math.radians(60), 0, 0))
    L.assign(col, paint)
    glove = L.mat_principled("glove", (0.035, 0.025, 0.02), rough=0.7)
    for hx in (-0.6, -0.21):
        g = L.prim("sphere", loc=(hx, 0.16, 1.07), segments=12, ring_count=8, radius=0.045)
        g.scale = (0.9, 1.3, 0.8)
        L.assign(g, glove)
    # passenger
    w = H.pale_woman("mary_car")
    w["root"].location = (0.4, -0.38, -0.2)
    for tag in ("L", "R"):
        w[f"hip{tag}"].rotation_euler = (math.radians(85), 0, 0)
        w[f"knee{tag}"].rotation_euler = (-math.radians(85), 0, 0)
        w[f"shoulder{tag}"].rotation_euler = (math.radians(25), 0, 0)
        w[f"elbow{tag}"].rotation_euler = (math.radians(40), 0, 0)
    w["dress"].scale = (1.0, 0.85, 0.45)
    w["dress"].location.z += 0.2
    # outside world sliding past (moves -Y): road, verge, trees
    world = H.empty("outside", (0, 0, 0))
    span = 10.0 * n / 24.0 + 60
    r = H.box_mesh("o_road", [(0, span / 2 - 20, -0.0, 3.5, span / 2 + 20, 0.01)], H.mat_wet_road("o_wet"))
    v = H.ground_box("o_verge", -40, 40, -40, span + 20, -0.02, H.mat_verge("o_verge_m"))
    cl = H.box_mesh("o_line", [(-1.6, y, 0.012, 0.06, 1.5, 0.002) for y in range(-20, int(span), 7)],
                    L.mat_principled("o_cl", (0.45, 0.38, 0.16), rough=0.5))
    t = H.bare_forest("o_trees", [(4.0, 25, -20, span), (-25, -5.0, -20, span)], count=40, seed=9)
    for o in (r, v, cl, t):
        o.parent = world
    world.location = (1.6, 0, 0)
    world.keyframe_insert("location", frame=1)
    world.location = (1.6, -10.0 * n / 24.0, 0)
    world.keyframe_insert("location", frame=n)
    L.linear_fcurves(world)
    # headlight beams ahead + bounce, dash glow, moon
    for sx in (-0.6, 0.6):
        L.spot((sx, 2.4, 0.95), (math.pi / 2 - 0.08, 0, 0), energy=2500, size_deg=30, blend=0.5, color=(1.0, 0.88, 0.66), name="hl")
    L.point((0.0, 0.3, 0.75), energy=6, color=(1.0, 0.6, 0.25), radius=0.2, name="dashglow")
    L.point((0.0, 0.1, 0.9), energy=5, color=(0.8, 0.82, 0.9), radius=0.5, name="bounce")
    _sun_dir(L, (-0.6, -0.2, -0.5), energy=0.6)
    L.fog_volume(center=(0, 20, 1.5), size=(60, 60, 3), density=0.05, color=(0.72, 0.75, 0.82))
    p = (-0.38, -0.74, 1.3)
    tg = (0.6, 0.15, 1.08)
    c = H.cam(p, tg, lens=15)
    H.cam_move(c, [(1, p, tg), (n, (-0.38, -0.72, 1.3), (0.6, 0.17, 1.08))], ease=False)
    L.cam_light(c, energy=6, color=(0.75, 0.8, 0.95))
    H.handheld(c, n, amp=0.004, rate=2.2, rot_amp=0.003)
    L.bake_static()


# --------------------------------------------------------------------------- cemetery gates scenes (S04, S07-S10, S14)
def _gates(L, n, bent=False, prints=False, fog=0.03, vol_end=80):
    _night(L, (0.006, 0.008, 0.017), vol_end=vol_end)
    g = H.cemetery_gates(bent=bent, prints=prints)
    _sun_dir(L, (0.45, -0.75, -0.5), energy=0.55)   # moon from back-left -> rim on bars and piers
    L.fog_volume(center=(0, 2, 1.6), size=(60, 50, 3.2), density=fog, color=(0.72, 0.75, 0.85))
    fgl = L.point((-3.0, 9.0, 3.0), energy=1100, color=(0.55, 0.65, 1.0), radius=2.0, name="fogglow")   # back-glow: bars silhouette
    fgl.data.specular_factor = 0.0
    return g


def S04(L, n):
    _gates(L, n)
    c = H.cam(GATE_P0, GATE_T, lens=35)
    H.cam_move(c, [(1, GATE_P0, GATE_T), (n, GATE_P1, GATE_T)], ease=False)
    hl = L.spot((-14.0, -7.5, 1.0), (0, 0, 0), energy=0, size_deg=35, blend=0.5, color=(1.0, 0.88, 0.66), name="spill")
    H.aim(hl, (-14.0, -7.5, 1.0), (0.0, -1.0, 1.0))
    H.key_energy(hl, [(1, 0), (int(n * 0.6), 0), (n, 6000)], "LINEAR")
    L.bake_static()


def _road_car(n, tail=1.0):
    car = H.car_1930s("palus_car", (CAR_STOP_X, CAR_Y, 0), -math.pi / 2, lamp_energy=2200, tail=tail)
    return car


def S07(L, n):
    _gates(L, n)
    car = _road_car(n)
    r = car["root"]
    for f, x in ((1, -24.0), (int(n * 0.45), -10.5), (int(n * 0.82), CAR_STOP_X), (n, CAR_STOP_X)):
        r.location = (x, CAR_Y, 0)
        r.keyframe_insert("location", frame=f)
    H.key_energy(car["tail_light"], [(1, 10), (int(n * 0.42), 10), (int(n * 0.47), 90)], "LINEAR")
    H.key_emission(car["tail_mat"], [(1, 2.0), (int(n * 0.42), 2.0), (int(n * 0.47), 14.0)], "LINEAR")
    p0, t0 = (-7.0, -16.0, 0.45), (-20.0, -7.3, 1.2)
    p1, t1 = (-6.0, -16.0, 0.45), (-1.0, -3.0, 1.5)
    c = H.cam(p0, t0, lens=28)
    H.cam_move(c, [(1, p0, t0), (int(n * 0.85), p1, t1), (n, p1, t1)])
    H.handheld(c, n, amp=0.004, rate=0.5)
    L.bake_static()


def S08(L, n):
    g = _gates(L, n, fog=0.025)
    car = H.car_1930s("palus_car", (CAR_STOP_X, CAR_Y, 0), -math.pi / 2, lamp_energy=2200, tail=0.6, door_open=1.15)
    w = H.pale_woman("mary_cross", emit=0.3)
    vanish = n - 30
    pts = [(-0.55, -6.6), (-0.3, -4.6), (0.0, -2.6)]
    fr = [1, int(vanish * 0.5), vanish]
    for (x, y), f in zip(pts, fr):
        w["root"].location = (x, y, 0)
        w["root"].keyframe_insert("location", frame=f)
    L.linear_fcurves(w["root"])
    _face(w, (0.15, 1))
    H.walk(w, 1, vanish, stride=0.5, rate=1.15, bob=0.015)
    H.key_vis(w["root"].children_recursive + [w["root"]], [(1, True), (vanish, False)])
    # fog bank over the verge in front of the bars thickens as she reaches it, then thins
    bank = H.room_fog((0.0, -1.8, 1.4), (7.0, 2.0, 2.8), density=0.02, color=(0.8, 0.82, 0.88), anis=0.4, name="fogbank")
    vnode = next(nd for nd in bank.active_material.node_tree.nodes if nd.type == "PRINCIPLED_VOLUME")
    for f, d in ((1, 0.03), (vanish - 10, 0.03), (vanish - 2, 0.6), (vanish + 8, 0.6), (n, 0.08)):
        vnode.inputs["Density"].default_value = d
        vnode.inputs["Density"].keyframe_insert("default_value", frame=f)
    L.point((0.4, -3.6, 2.2), energy=120, color=(1.0, 0.85, 0.6), radius=1.0, name="beamscatter")
    p0, t0 = (CAR_STOP_X - 0.9, -10.3, 2.35), (0.0, -1.8, 0.9)
    c = H.cam(p0, t0, lens=35)
    p1 = (p0[0] + 0.2, p0[1] + 0.3, p0[2])
    H.cam_move(c, [(1, p0, t0), (vanish, p0, t0), (n, p1, t0)])
    L.cam_light(c, energy=12, color=(0.8, 0.85, 1.0))
    L.bake_static()


def S09(L, n):
    _gates(L, n, fog=0.03)
    w = H.pale_woman("mary_bars")
    w["root"].location = (-0.25, 0.42, 0)
    _face(w, (0, -1))
    for tag, sx in (("L", -1), ("R", 1)):
        w[f"shoulder{tag}"].rotation_euler = (math.radians(62), 0, sx * math.radians(-6))
        w[f"elbow{tag}"].rotation_euler = (math.radians(20), 0, 0)
    pc = H.car_1930s("police", (5.5, -6.0, 0), math.radians(110), body=(0.01, 0.01, 0.012), lamp_energy=1500, tail=0.3, police=True)
    r = pc["root"]
    r.location = (9.0, -5.0, 0)
    r.keyframe_insert("location", frame=1)
    r.location = (5.5, -6.0, 0)
    r.keyframe_insert("location", frame=int(n * 0.45))
    H.police_flash(pc, n, hz=2.0, energy=2500)
    ctr = Vector((-0.25, 0.3, 0))
    def arc(deg, r_=6.0, h=1.45):
        a = math.radians(deg)
        return (ctr.x + r_ * math.cos(a), ctr.y + r_ * math.sin(a), h)
    p0, p1 = arc(-128), arc(-113)
    tg = (-0.25, 0.3, 1.25)
    c = H.cam(p0, tg, lens=50)
    H.cam_move(c, [(1, p0, tg), (n, p1, tg)], ease=False)
    H.handheld(c, n, amp=0.004, rate=0.4)
    L.bake_static()


def S10(L, n):
    g = _gates(L, n, bent=True, prints=True, fog=0.03)
    p0 = (-1.45, -1.25, 1.7)
    c = H.cam(p0, (0.3, 2.0, 2.9), lens=50)
    H.cam_move(c, [(1, p0, (0.3, 2.0, 2.9)), (int(n * 0.65), (-1.4, -1.1, 1.45), (-0.26, -0.08, 1.12)),
                   (n, (-1.32, -1.02, 1.42), (-0.26, -0.08, 1.12))])
    H.handheld(c, n, amp=0.012, rate=0.9, rot_amp=0.006)
    t = L.spot((0.12, -0.1, 0.05), (0, 0, 0), energy=260, size_deg=20, blend=0.35, color=(0.95, 0.97, 1.0), name="torch", radius=0.03)
    t.parent = c
    red = L.point((-3.5, -3.5, 1.5), energy=800, color=(1.0, 0.03, 0.02), radius=0.3, name="redspill")
    blue = L.point((3.0, -3.8, 1.5), energy=800, color=(0.1, 0.25, 1.0), radius=0.3, name="bluespill")
    fps = 24
    for f in range(1, n + 2):
        k = max(0.0, 1 - f / (n * 0.85))
        on = ((f - 1) // 6) % 2 == 0
        red.data.energy = 900 * k if on else 0
        blue.data.energy = 0 if on else 900 * k
        red.data.keyframe_insert("energy", frame=f)
        blue.data.keyframe_insert("energy", frame=f)
    H.dust((-0.3, -0.6, 1.6), (1.5, 1.5, 1.8), n, count=250, radius=0.0012, emit=0.15)
    L.bake_static()


def S14(L, n):
    _gates(L, n, bent=True, prints=False, fog=0.022)
    w = H.pale_woman("mary_faint", alpha=0.3, emit=0.12)
    w["root"].location = (-0.25, 0.55, 0)
    _face(w, (0, -1))
    H.key_vis(w["root"].children_recursive + [w["root"]], [(1, False), (n - 24, True)])
    H.set_alpha(w["mat"], [(n - 24, 0.0), (n - 16, 0.3)])
    c = H.cam(GATE_P0, GATE_T, lens=35)
    p1 = tuple(GATE_P0[i] + (GATE_T[i] - GATE_P0[i]) * 0.02 for i in range(3))
    H.cam_move(c, [(1, GATE_P0, GATE_T), (n, p1, GATE_T)], ease=False)
    sw = L.spot((-14.0, -7.0, 1.0), (0, 0, 0), energy=0, size_deg=28, blend=0.5, color=(1.0, 0.88, 0.66), name="sweep")
    H.aim(sw, (-14.0, -7.0, 1.0), (-6.0, 2.0, 1.2))
    H.key_energy(sw, [(1, 0), (20, 0), (24, 7000), (36, 7000), (42, 0)], "LINEAR")
    H.cam_move(sw, [(20, (-14.0, -7.0, 1.0), (-6.0, 2.0, 1.2)), (42, (-8.0, -7.0, 1.0), (6.0, 2.0, 1.2))], ease=False)
    L.bake_static()


# --------------------------------------------------------------------------- S11 evidence board: the truck
def S11(L, n):
    _night(L, (0.01, 0.01, 0.012))
    H.box_mesh("bwall", [(0, 0.2, 0, 4, 0.05, 4)], L.mat_principled("bw", (0.05, 0.05, 0.055), rough=0.9))
    H.evidence_board("board", 2.4, 4.0)
    ink = L.mat_principled("ink", (0.04, 0.035, 0.03), rough=0.6)
    H.pinned_card("c_hdr", (0.0, -0.01, 1.32), 1.5, 0.36, [], header="WHAT SCEPTICS SAY", size=0.1, font_size_header=0.125,
                  color=(0.86, 0.83, 0.72), rot=math.radians(-1.5))
    tc = H.pinned_card("c_truck", (0.0, -0.012, 0.25), 1.6, 1.25, ["REVERSED INTO", "THE FENCE"], size=0.09, rot=math.radians(2))
    # drawn icon: box truck backing (arrow) into a fence line of bars
    boxes = [(0.12, -0.008, -0.05, 0.32, 0.002, 0.17), (-0.32, -0.008, -0.1, 0.12, 0.002, 0.12), (-0.4, -0.008, 0.0, 0.04, 0.002, 0.03)]
    box = H.box_mesh("truck", boxes, ink, parent=tc)
    for x in (-0.3, 0.0, 0.3):
        wh = L.prim("cyl", loc=(x, -0.009, -0.26), vertices=16, radius=0.06, depth=0.003, rot=(math.pi / 2, 0, 0))
        L.assign(wh, ink)
        wh.parent = tc
    red = L.mat_principled("arrow", (0.6, 0.05, 0.04), rough=0.6)
    H.box_mesh("arrow", [(0.2, -0.009, 0.24, 0.16, 0.002, 0.018)], red, parent=tc)
    ah = L.prim("cone", loc=(0.4, -0.009, 0.24), vertices=3, radius1=0.05, radius2=0, depth=0.003, rot=(math.pi / 2, 0, 0))
    ah.rotation_euler = (math.pi / 2, math.radians(-90), 0)
    L.assign(ah, red)
    ah.parent = tc
    H.box_mesh("fence", [(0.55 + k * 0.05, -0.009, -0.05 + (0.04 if k == 1 else 0), 0.008, 0.002, 0.23) for k in range(4)] +
               [(0.62, -0.009, 0.08, 0.1, 0.002, 0.008)], ink, parent=tc)
    redst = L.mat_principled("string", (0.6, 0.02, 0.02), rough=0.5)
    L.guideline([(0.0, -0.05, 1.45), (0.0, -0.05, 0.9)], mat=redst, thickness=0.005, name="str1")
    H.box_mesh("scraps", [(0.95, -0.006, 0.55, 0.2, 0.002, 0.26, 0.1), (-0.95, -0.006, -0.6, 0.22, 0.002, 0.16, -0.08),
                          (-0.9, -0.006, 1.0, 0.2, 0.002, 0.15, 0.05)], H.mat_paper("scrap", (0.6, 0.57, 0.48)))
    tgt = tuple(tc.location)
    tc.location = (tgt[0] + 2.6, tgt[1], tgt[2] + 0.1)
    tc.keyframe_insert("location", frame=1)
    tc.location = tgt
    tc.keyframe_insert("location", frame=12)
    lamp = L.spot((-1.6, -2.2, 2.6), (0, 0, 0), energy=900, size_deg=60, blend=0.8, color=(1.0, 0.78, 0.5), name="desklamp")
    H.aim(lamp, (-1.6, -2.2, 2.6), (0.0, 0, 0.5))
    c = H.cam((0.0, -4.6, 0.75), (0.0, 0, 0.7), lens=50)
    H.cam_move(c, [(1, (0.0, -4.6, 0.75), (0.0, 0, 0.7)), (n, (0.0, -4.0, 0.72), (0.0, 0, 0.68))], ease=False)
    L.bake_static()


# --------------------------------------------------------------------------- S12 wireframe globe behind the document
def S12(L, n):
    _night(L, (0.004, 0.006, 0.01))
    H.wire_globe((0, 0, 0), radius=1.6, n=n, deg=20)
    m = L.mat_emission("stars", (0.7, 0.8, 0.9), 1.5)
    import random
    rnd = random.Random(3)
    bm = []
    for i in range(160):
        x, z = rnd.uniform(-6, 6), rnd.uniform(-9, 9)
        if x * x + z * z < 4.0:
            continue
        s = rnd.uniform(0.006, 0.014)
        bm.append((x, 6, z, s, s, s))
    H.box_mesh("stars", bm, m)
    L.point((-3, -3, 3), energy=200, color=(0.6, 0.8, 1.0), radius=1, name="globekey")
    c = H.cam((0, -6.2, 1.2), (0, 0, 0.9), lens=40)
    H.cam_move(c, [(1, (0, -6.2, 1.2), (0, 0, 0.9)), (n, (0, -5.8, 1.15), (0, 0, 0.88))], ease=False)
    L.bake_static()


# --------------------------------------------------------------------------- S13 blank headstones in fog
def S13(L, n):
    _night(L, (0.005, 0.007, 0.014), vol_end=60)
    H.ground_box("lawn13", -40, 40, -20, 60, 0.0, H.mat_verge("lawn13m"))
    H.headstone_row((-1.7, 0.0, 1.7), y=0.0, h=0.95)
    H.bare_forest("trees13", [(-25, 25, 8, 35)], count=18, seed=21, height=(8, 13))
    _sun_dir(L, (0.2, -1.0, -0.45), energy=0.7, color=(0.6, 0.7, 1.0))
    L.fog_volume(center=(0, 10, 1.2), size=(50, 40, 2.4), density=0.045, color=(0.72, 0.75, 0.85))
    L.area((0.0, -5.0, 2.5), (math.radians(60), 0, 0), energy=25, size=5, color=(0.55, 0.62, 0.85), name="moonfill")
    rim = L.area((0.0, 3.0, 2.2), (math.radians(-110), 0, 0), energy=60, size=6, color=(0.6, 0.7, 1.0), name="rimfill")
    p0, p1 = (-3.2, -3.4, 0.85), (1.7, -3.4, 0.85)
    hold = max(2, n - 22)    # last ~0.9 s is a still hold (dead air)
    c = H.cam(p0, (-2.2, 0, 0.7), lens=50)
    H.cam_move(c, [(1, p0, (-2.2, 0, 0.7)), (hold, p1, (1.7, 0, 0.7)), (n, p1, (1.7, 0, 0.7))])
    L.dof(c, distance=3.4, fstop=2.2)
    L.bake_static()
