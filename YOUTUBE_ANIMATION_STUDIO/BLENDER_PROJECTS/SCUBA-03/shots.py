"""SCUBA-03 — His Lifeline Snapped 100 m Under the North Sea (Chris Lemons, DSV Bibby Topaz, 2012).
One builder per shot: def Sxx(L, n). Scuba builders live in PIPELINE/blender/lib_scuba.py.
All people are faceless stylised divers / silhouettes. The umbilical is stylised as a glowing cyan tube.
"""
import sys, os, math, random, importlib
import bpy
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_scuba as S
importlib.reload(S)

PI = math.pi
MS = (6.0, 4.0, 3.0)              # manifold frame w, d, h
TOP = MS[2] + 0.12                # roof surface z (diver kneels here)
CYAN = (0.25, 1.0, 0.95)
WARM = (1.0, 0.78, 0.5)
COLD = (0.45, 0.75, 0.85)
LEM_LOC = Vector((0.3, 0.0, TOP + 1.02))   # kneeling diver root (torso centre)
LEM_YAW = PI + 0.35                         # faces ~ -Y (toward the S01 camera)
CAM01_A = Vector((-1.15, -3.9, 2.45))       # S01 first frame == S19 last frame (loop)
CAM01_T = Vector((0.15, 0.0, 3.55))
CAM01_B = CAM01_A + (CAM01_T - CAM01_A).normalized() * 0.5
CORNER = Vector((MS[0] / 2, -MS[1] / 2, TOP))   # snag corner (S07/S08)


# ----------------------------------------------------------------------------- helpers

def _finish(L):
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "AREA":
            o.data.volume_factor = 0.0
    L.bake_static()


def _upd():
    bpy.context.view_layer.update()


def _aim(o, frm, to):
    o.location = frm
    o.rotation_euler = (Vector(to) - Vector(frm)).to_track_quat("-Z", "Y").to_euler()
    return o


def sea_env(L, n, density=0.07, seabed=True, snow=1400, snow_emit=0.25, vol_center=(0, 0, 8), vol_size=(46, 46, 22),
            manifold=True):
    """Dark North Sea bottom at ~91 m: green-black water volume, silty seabed, manifold, marine snow."""
    S.setup(vol_end=45)
    L.set_world(color=(0.0012, 0.0035, 0.003), strength=1.0)
    S.world_volume(color=(0.16, 0.4, 0.33), density=density, anisotropy=0.55, absorption=(0.1, 0.3, 0.24),
                   center=vol_center, size=vol_size)
    out = {}
    if seabed:
        sb = L.seabed(size=70, strength=0.3, mat=L.mat_noise_surface("silt3", (0.035, 0.04, 0.035), (0.1, 0.11, 0.09),
                                                                       scale=5, bump=0.15, voronoi=False))
        sb.location.z = -0.2
    if manifold:
        out["man"] = S.manifold(size=MS)
    if snow:
        L.particle_cloud((0, 0, 5), (18, 18, 11), count=snow, radius=0.006, nframes=n, drift=(0.06, 0.03, -0.05),
                         name="snow", mat=L.mat_principled("snowm", (0.7, 0.75, 0.7), rough=1, emit=(0.55, 0.65, 0.6),
                                                           emit_strength=snow_emit))
    return out


def lemons(L, light=0.0, loc=LEM_LOC, yaw=LEM_YAW, pose="kneel", arms="work", lean=0.15, upright=True):
    """Chris Lemons: hard-hat saturation diver (yellow helmet), dark suit, single bailout cylinder. Faceless."""
    P = S.rescue_diver("lemons", helmet=(0.92, 0.7, 0.05), suit=(0.035, 0.035, 0.04), light_energy=max(light, 0.0),
                       umbilical=False)
    r = P["root"]
    r.location = loc
    r.rotation_euler = (0, 0, yaw)
    if upright:
        # faceplate + helmet lamp on the front (belly side) so an upright diver looks forward, not up
        vz = bpy.data.objects["lemons_visor"]
        vz.location = (0, 0.6, -0.15)
        vz.scale = (1.0, 0.8, 0.5)
        for k in ("lamp", "lens"):
            P[k].hide_render = True
        lens = L.prim("cyl", loc=(0.0, 0.72, -0.1), vertices=10, radius=0.035, depth=0.03, name="lemons_hlens")
        lm = L.mat_emission("lemons_hlensm", (1, 0.9, 0.75), 30 if light > 0 else 0.05)
        L.assign(lens, lm)
        lens.parent = r
        P["hlens_mat"] = lm
        P["torch"].location = (0.0, 0.72, -0.14)
        P["torch"].rotation_euler = (-0.45, 0, 0)
    if pose == "kneel":
        S.kneel(P, lean=lean, arms=arms)
    elif pose == "curl":
        S.curl_pose(P)
    elif pose == "stand":
        r.rotation_euler = (PI / 2 - 0.05, 0, yaw)
        for tag, s in (("L", -1), ("R", 1)):
            P[f"hip{tag}"].rotation_euler = (0.05, 0, 0)
            P[f"knee{tag}"].rotation_euler = (-0.15, 0, 0)
            P[f"fin{tag}"].scale = (0.07, 0.12, 0.05)
            P[f"shoulder{tag}"].rotation_euler = (-1.45, 0, s * 0.12)
    tk = P["tank0"]
    tk.scale = (0.085, 0.085, 0.3)
    tk.location = (0.0, -0.1, 0.26)
    L.assign(tk, L.mat_principled("bailm", (0.78, 0.8, 0.78), rough=0.35, metal=0.2))
    P["valve"] = S.bailout_valve(P)
    P["torch"].data.color = (1.0, 0.86, 0.68)
    S.no_shadow(P["torch"])
    _upd()
    return P


def world_of(o, local):
    _upd()
    return o.matrix_world @ Vector(local)


def attach_point(P):
    return world_of(P["root"], (0.0, 0.45, 0.22))


def dead_umb(P, name="deadumb"):
    """Slack, dark severed umbilical stub trailing from the diver's back (parented to the root)."""
    m = L_.mat_principled(name + "_m", (0.04, 0.08, 0.08), rough=0.5, emit=(0.1, 0.4, 0.38), emit_strength=0.05)
    t = S.tube([(0, 0.45, 0.22), (0.08, 0.3, 0.42), (0.25, -0.1, 0.5), (0.55, -0.7, 0.45), (0.85, -1.3, 0.3)], radius=0.028,
               mat=m, name=name, order=4)
    t.parent = P["root"]
    return t


L_ = None  # studio_lib handle (set by each builder)


def _L(L):
    global L_
    L_ = L


def rim(L, loc, target, energy=600, size=6, color=COLD, name="rim"):
    a = L.area(loc, (0, 0, 0), energy=energy, size=size, color=color, name=name)
    _aim(a, loc, target)
    return a


def gauge_glint(L, loc, energy=6, color=(0.8, 0.95, 1.0)):
    p = L.point(loc, energy=energy, color=color, radius=0.05, name="glint")
    S.no_shadow(p)
    return p


# ----------------------------------------------------------------------------- umbilical scene (S01 / S19 / S18)

def _umb_points(A):
    return [A, A + Vector((-0.25, 0.55, 0.55)), A + Vector((-1.2, 1.9, 3.4)), A + Vector((-2.4, 3.3, 6.8)),
            A + Vector((-3.4, 4.6, 9.8))]


def _umb_upper(B):
    return [B, B + Vector((-1.2, 1.4, 3.2)), B + Vector((-2.6, 3.0, 7.0)), B + Vector((-5, 6, 16))]


def manifold_hero(L, n, snap=None, light_on=True, s19=False):
    """Lemons kneeling on the manifold roof, umbilical rising taut to the top-left; optional snap at frame `snap`."""
    _L(L)
    sea_env(L, n, density=0.075)
    P = lemons(L, light=380 if light_on else 0.0)
    A = attach_point(P)
    pts = _umb_points(A)
    B = pts[-1]
    up = _umb_upper(B)
    if snap:
        low_m, low_T, _ = S.mat_drain("umb_low_m", CYAN, 7.0, origin=B)
        hi_m, hi_T, _ = S.mat_drain("umb_hi_m", CYAN, 7.0, origin=B)
        low = S.tube(pts, radius=0.045, mat=low_m, name="umb_low", order=4)
        hi = S.tube(up, radius=0.045, mat=hi_m, name="umb_hi", order=4)
        # taut, then whipping sideways (the ship pulling) before it parts
        S.tube_keys(hi, 1, up)
        S.tube_keys(low, 1, pts)
        for f, dx in ((snap - 14, 0.0), (snap - 9, 0.35), (snap - 5, -0.45), (snap - 2, 0.55)):
            sw = [p + Vector((dx * k / 3, dx * 0.3 * k / 3, 0.05 * k)) for k, p in enumerate(up)]
            S.tube_keys(hi, f, sw)
            S.tube_keys(low, f, [p + Vector((dx * 0.25 * k / 4, 0, 0)) for k, p in enumerate(pts)])
        S.tube_keys(hi, snap, [p + Vector((0.55 * k / 3, 0.15 * k / 3, 0.1 * k)) for k, p in enumerate(up)])
        S.tube_keys(low, snap, [p + Vector((0.55 * 0.25 * k / 4, 0, 0)) for k, p in enumerate(pts)])
        # upper end recoils up and away into the dark
        S.tube_keys(hi, snap + 5, [B + Vector((-0.6, 1.2, 3.0)), up[1] + Vector((-0.8, 1.6, 3.6)),
                                   up[2] + Vector((-0.5, 1.5, 3.0)), up[3]])
        S.tube_keys(hi, n, [B + Vector((-2.0, 3.6, 8.0)), up[1] + Vector((-1.5, 3, 6)), up[2] + Vector((-1, 2, 4)), up[3]])
        # lower part goes slack and sinks
        slack = [A, A + Vector((-0.15, 0.5, 0.3)), A + Vector((-0.7, 1.4, 0.4)), A + Vector((-1.4, 2.4, -0.2)),
                 A + Vector((-2.0, 3.2, -0.9))]
        S.tube_keys(low, snap + 10, [p.lerp(q, 0.6) for p, q in zip(pts, slack)])
        S.tube_keys(low, n, slack)
        # glow drains outward from the break
        S.drain_keys(low_T, [(snap, -1.0), (snap + 3, 0.5), (snap + 26, 10.0)])
        S.drain_keys(hi_T, [(snap, -1.0), (snap + 2, 1.5), (snap + 14, 14.0)])
        # flash + burst at the break
        fl = L.point(B, energy=0, color=(0.8, 1.0, 1.0), radius=0.3, name="snapflash")
        S.no_shadow(fl)
        S.energy_keys(fl, [(snap - 1, 0), (snap, 9000), (snap + 2, 2500), (snap + 6, 0)])
        S.bubbles_at(B, [snap + random.Random(i).randint(0, 7) for i in range(30)], rise=2.2, spread=0.25, size=0.05,
                     life=(20, 40), name="burst")
        glow_pts = []
        for k, (p, e) in enumerate(((A + Vector((-0.4, 0.9, 1.0)), 60), (pts[2] + Vector((0.3, 0, 0)), 140))):
            gp = L.point(p, energy=e, color=CYAN, radius=0.3, name=f"umbglow{k}")
            S.no_shadow(gp)
            S.energy_keys(gp, [(1, e), (snap, e * 1.3), (snap + 4 + k * 6, e * 0.25), (snap + 18, 0)])
        if light_on:
            tl = P["torch"]
            S.energy_keys(tl, [(1, 380), (snap, 380), (snap + 1, 60), (snap + 2, 300), (snap + 3, 0), (n, 0)], "CONSTANT")
            S.emit_keys(P["hlens_mat"], [(1, 30), (snap, 30), (snap + 1, 4), (snap + 2, 24), (snap + 3, 0.05)], (), "CONSTANT")
    else:
        um, _ = S.umbilical(pts + up[1:], radius=0.045, color=CYAN, strength=7.0, name="umb")
        for k, (p, e) in enumerate(((A + Vector((-0.4, 0.9, 1.0)), 60), (pts[2] + Vector((0.3, 0, 0)), 140))):
            gp = L.point(p, energy=e, color=CYAN, radius=0.3, name=f"umbglow{k}")
            S.no_shadow(gp)
    rim(L, (1.5, 5.5, 9), LEM_LOC, energy=2600, size=4)
    rim(L, (-5, 1.5, 6), LEM_LOC + Vector((0, 0, -1.0)), energy=500, size=3, color=(0.3, 0.6, 0.55), name="side")
    rim(L, (3.5, -3.5, 2.5), Vector((0, -1.5, 2.0)), energy=350, size=4, color=(0.35, 0.55, 0.5), name="frontfill")
    return P


def S01(L, n):
    manifold_hero(L, n, snap=34)
    cam, _ = L.camera(loc=CAM01_A, target=CAM01_T, lens=26)
    L.cam_keys(cam, [(1, CAM01_A), (n, CAM01_B)], ease=False)
    L.handheld(cam, n, amp=0.02, rate=0.45, rot_amp=0.004)
    S.shake(cam, 34, length=5, amp=0.05, rot=0.012)
    _finish(L)


def S19(L, n):
    manifold_hero(L, n, snap=None, light_on=True)
    a0 = CAM01_A - (CAM01_T - CAM01_A).normalized() * 0.7 + Vector((-0.3, 0, 0.1))
    cam, _ = L.camera(loc=a0, target=CAM01_T, lens=26)
    L.cam_keys(cam, [(1, a0), (n, CAM01_A)])
    _finish(L)


def S18(L, n):
    _L(L)
    sea_env(L, n, density=0.075, snow_emit=0.35)
    # severed stub lying across the empty roof, its torn end drifting in the current
    base = Vector((0.4, -0.2, TOP + 0.05))
    m = L.mat_principled("stub_m", (0.04, 0.1, 0.1), rough=0.5, emit=CYAN, emit_strength=0.6)
    pts = [base, base + Vector((-0.8, 0.6, 0.0)), base + Vector((-1.5, 1.5, 0.2)), base + Vector((-1.9, 2.4, 0.9)),
           base + Vector((-2.1, 3.0, 1.8))]
    stub = S.tube(pts, radius=0.045, mat=m, name="stub", order=4)
    for f in range(1, n + 1, 6):
        s = math.sin(f * 0.12)
        S.tube_keys(stub, f, [pts[0], pts[1], pts[2] + Vector((0.1 * s, 0, 0)), pts[3] + Vector((0.3 * s, 0.1 * s, 0.05 * s)),
                              pts[4] + Vector((0.55 * s, 0.2 * s, 0.15 * s))])
    tip = L.prim("ico", loc=pts[4], subdivisions=1, radius=0.05, name="tip")
    L.assign(tip, L.mat_emission("tipm", CYAN, 1.5))
    for f in range(1, n + 1, 6):
        s = math.sin(f * 0.12)
        tip.location = pts[4] + Vector((0.55 * s, 0.2 * s, 0.15 * s))
        tip.keyframe_insert("location", frame=f)
    gp = L.point(pts[3] + Vector((0.3, -0.3, 0.3)), energy=40, color=CYAN, radius=0.2, name="stubglow")
    S.no_shadow(gp)
    rim(L, (1.5, 5.5, 9), LEM_LOC, energy=1800, size=4)
    rim(L, (-5, 1.5, 6), LEM_LOC + Vector((0, 0, -1.0)), energy=400, size=3, color=(0.3, 0.6, 0.55), name="side")
    rim(L, (3.5, -3.5, 2.5), Vector((0, -1.5, 2.0)), energy=300, size=4, color=(0.35, 0.55, 0.5), name="frontfill")
    a = Vector((-1.0, -3.4, TOP + 1.1))
    cam, _ = L.camera(loc=a, target=Vector((-0.7, 0.9, TOP + 0.4)), lens=26)
    L.cam_keys(cam, [(1, a), (n, a + Vector((0.6, 0.2, 0.15)))], ease=False)
    L.handheld(cam, n, amp=0.02, rate=0.4)
    _finish(L)


# ----------------------------------------------------------------------------- S02 bailout cylinder

def S02(L, n):
    _L(L)
    sea_env(L, n, density=0.06, snow=900)
    P = lemons(L, light=0.0)
    dead_umb(P)
    V = world_of(P["valve"], (0, 0, 0))
    back = (world_of(P["root"], (0, 0, 1)) - world_of(P["root"], (0, 0, 0))).normalized()
    side = back.cross(Vector((0, 0, 1))).normalized()
    c0 = V + back * 0.85 + Vector((0, 0, 0.55)) + side * 0.6
    c1 = V + back * 0.9 + Vector((0, 0, 0.5)) + side * 0.3
    tgt = L.link(bpy.data.objects.new("valve_tgt", None))
    tgt.location = V
    cam, _ = L.camera(loc=c0, target=tgt, lens=35)
    L.cam_keys(cam, [(1, c0), (n, c1)], ease=False)
    L.handheld(cam, n, amp=0.01, rate=0.5)
    L.dof(cam, target=tgt, fstop=2.2)
    # exhalations: bursts from the helmet exhaust rising past camera
    ex = world_of(P["root"], (0.12, 0.7, 0.12))
    starts = []
    for b in (4, 30, 56):
        starts += [b + k % 4 for k in range(7)]
    S.bubbles_at(ex, starts, rise=1.6, spread=0.06, size=0.03, life=(26, 40), name="exh", drift=(0.0, 0.03))
    top = L.area(V + Vector((0, 0, 4)), (0, 0, 0), energy=120, size=3, color=COLD, name="toplight")
    gauge_glint(L, V + back * 0.5 + side * 0.4 + Vector((0, 0, 0.35)), energy=5)
    rim(L, V - back * 3 + Vector((0, 0, 3)), V, energy=600, size=3)
    rim(L, V + side * 3 + Vector((0, 0, 1)), V, energy=150, size=2, color=(0.35, 0.6, 0.55), name="sidefill")
    _finish(L)


# ----------------------------------------------------------------------------- S03 map background

def S03(L, n):
    S.setup()
    L.set_world(color=(0.002, 0.004, 0.008), strength=1)
    m = S.mat_water_surface("nightsea", color=(0.006, 0.02, 0.035), rough=0.08, alpha=1.0, ripple=0.6, nframes=n)
    w = L.prim("plane", loc=(0, 0, 0), size=400, name="nightsea")
    L.assign(w, m)
    L.sun(rot=(0.25, 0.1, 2.6), energy=3.0, color=(0.5, 0.65, 1.0))
    rnd = random.Random(4)
    lm = L.mat_emission("rigs", (1.0, 0.7, 0.35), 25)
    for i in range(9):  # distant rigs / vessels as warm points
        o = L.prim("ico", loc=(rnd.uniform(-60, 60), rnd.uniform(-90, 90), 0.4), subdivisions=1, radius=0.5, name="rig")
        L.assign(o, lm)
    cam, _ = L.camera(loc=(0, 0, 160), lens=35)
    cam.rotation_euler = (0, 0, 0.2)
    L.cam_keys(cam, [(1, (0, 0, 160)), (n, (4, 6, 150))], ease=False)
    _finish(L)


# ----------------------------------------------------------------------------- S04 working (flashback to normal)

def S04(L, n):
    _L(L)
    o = sea_env(L, n, density=0.065)
    V = o["man"]["valve"]
    P = lemons(L, light=420, loc=Vector((V.x, V.y - 0.62, 1.5)), yaw=0.0, pose="stand")
    A = attach_point(P)
    bell = S.diving_bell("bell", radius=1.5, lamp_energy=0, hatch_strength=6)
    bell["root"].location = (-5.0, 5.0, 19.0)
    hb = Vector((-5.0, 5.0, 19.0 + bell["bottom_z"]))
    pts = [A, A + Vector((0, -0.6, 0.9)), A + Vector((-0.6, -0.9, 4.0)), A + Vector((-2.2, 0.5, 9.0)),
           hb + Vector((0.6, -1.5, -4)), hb]
    S.umbilical(pts, radius=0.045, color=CYAN, strength=7, name="umb")
    S.lift_wire(hb + Vector((0, 0, 3.5)), hb + Vector((0, 0, 30)), name="bellwire")
    for k, (p, e) in enumerate(((A + Vector((0.3, -0.5, 1.2)), 50), (pts[3], 200))):
        gp = L.point(p, energy=e, color=CYAN, radius=0.3, name=f"umbglow{k}")
        S.no_shadow(gp)
    S.bubbles_at(world_of(P["root"], (0.12, 0.72, 0.15)), [3 + k * 2 + (k // 5) * 18 for k in range(25)], rise=1.6,
                 spread=0.05, size=0.03, name="exh")
    # wheel turning
    whl = [o_ for o_ in bpy.data.objects if o_.name.startswith("manifold_wheel")]
    rim(L, (4, 6, 12), (0, -1, 2), energy=900, size=6)
    tgt = L.link(bpy.data.objects.new("tilt_tgt", None))
    tgt.location = (-2.2, 2.0, 12.5)
    tgt.keyframe_insert("location", frame=1)
    tgt.location = (V.x + 0.1, V.y - 0.4, 2.0)
    tgt.keyframe_insert("location", frame=int(n * 0.7))
    tgt.keyframe_insert("location", frame=n)
    cam, _ = L.camera(loc=(2.6, -8.6, 2.6), target=tgt, lens=28)
    L.cam_keys(cam, [(1, (2.6, -8.6, 2.6)), (n, (2.3, -7.6, 2.4))])
    L.handheld(cam, n, amp=0.015, rate=0.4)
    L.cam_light(cam, energy=40, color=COLD, size_deg=60)
    _finish(L)


# ----------------------------------------------------------------------------- surface: DSV

def storm_sea(L, n, size=320, spatial=80, wave=2.2, chop=1.3, res=11, foam=True):
    S.setup(vol_end=250)
    S.sky_gradient(top=(0.002, 0.004, 0.01), horizon=(0.03, 0.05, 0.09), strength=1.0, below=(0.005, 0.01, 0.015))
    sea = S.ocean(size=size, nframes=n, wave_scale=wave, choppiness=chop, resolution=res, spatial=spatial, wind=24,
                  mat=S.mat_ocean("sea_n", deep=(0.002, 0.006, 0.009), shallow=(0.02, 0.05, 0.07), rough=0.12,
                                  under=(0.02, 0.05, 0.06), under_strength=0.1), foam=foam)
    return sea


def rain(L, n, center=(0, 0, 10), size=(120, 120, 30), count=1400, fall=-14.0):
    r = L.particle_cloud(center, size, count=count, radius=0.008, nframes=n, drift=(2.0, 0.5, fall), name="rain",
                         mat=L.mat_principled("rainm", (0.7, 0.8, 0.9), rough=0.3, emit=(0.5, 0.6, 0.7), emit_strength=0.8))
    r.scale = (6, 6, 40)
    return r


def S05(L, n):
    storm_sea(L, n)
    P = S.dsv("dsv", flood_energy=9000)
    root = P["root"]
    root.location = (0, 0, -0.3)
    root.rotation_euler = (0, 0, 0.55)
    S.bob(root, n, amp=0.5, rate=0.18, tilt=0.025, base=(0, 0, -0.3))
    root.rotation_euler.z = 0.55
    for fc in S.L._fcurves(root.animation_data.action):
        if fc.data_path == "rotation_euler" and fc.array_index == 2:
            for kp in fc.keyframe_points:
                kp.co[1] = 0.55
    # bridge screens: green -> flashing red from ~1/3 of the shot
    sw = int(n * 0.3)
    cols = [(1, (0.2, 1.0, 0.45)), (sw, (0.2, 1.0, 0.45))]
    for k, f in enumerate(range(sw + 1, n + 1, 4)):
        cols.append((f, (1.0, 0.06, 0.03) if k % 2 == 0 else (0.35, 0.02, 0.01)))
    S.emit_keys(P["bridge_mat"], [(1, 7.0)], cols, "CONSTANT")
    hy = 45 * 0.42
    alarm = L.point((0, hy + 8, P["deck_z"] + 14), energy=0, color=(1, 0.08, 0.04), radius=2, name="alarm")
    alarm.parent = root
    S.no_shadow(alarm)
    S.energy_keys(alarm, [(1, 0), (sw, 0)] + [(f, 40000 if k % 2 == 0 else 6000) for k, f in enumerate(range(sw + 1, n + 1, 4))],
                  "CONSTANT")
    S.no_shadow(*P["floods"])
    L.sun(rot=(math.radians(80), 0, math.radians(200)), energy=0.8, color=(0.5, 0.65, 1.0), angle=3)
    rain(L, n, center=(-20, -60, 12), size=(90, 90, 26))
    L.particle_cloud((-10, -30, 2), (60, 40, 4), count=300, radius=0.008, nframes=n, drift=(1.5, 0.5, 0.6), name="spray",
                     mat=L.mat_principled("spraym", (0.8, 0.9, 1.0), emit=(0.4, 0.5, 0.6), emit_strength=0.5))
    cam, _ = L.camera(loc=(-62, -118, 6.5), target=(2, 12, 11), lens=35)
    L.cam_keys(cam, [(1, (-62, -118, 6.5)), (n, (-54, -103, 6.0))])
    pf = int(n * 0.6)
    cam.data.keyframe_insert("lens", frame=pf - 1)
    cam.data.lens = 41
    cam.data.keyframe_insert("lens", frame=pf + 1)
    L.handheld(cam, n, amp=0.25, rate=0.5, rot_amp=0.008)
    _finish(L)


def _dots(L, pts, dash=1.6, gap=1.6, radius=0.35, color=(1.0, 0.85, 0.2), strength=6, name="dash", closed=True):
    """Dashed emissive marker line through 2D/3D points."""
    m = L.mat_emission(name + "_m", color, strength)
    seq = pts + ([pts[0]] if closed else [])
    out = []
    for a, b in zip(seq[:-1], seq[1:]):
        a, b = Vector(a), Vector(b)
        ln = (b - a).length
        k = 0.0
        while k < ln:
            s0 = a + (b - a) * (k / ln)
            s1 = a + (b - a) * (min(ln, k + dash) / ln)
            o = L.prim("cyl", loc=(s0 + s1) / 2, vertices=6, radius=radius, depth=max(0.05, (s1 - s0).length), name=name)
            o.rotation_euler = (s1 - s0).to_track_quat("Z", "Y").to_euler()
            L.assign(o, m)
            o.visible_shadow = False
            out.append(o)
            k += dash + gap
    return out


def S06(L, n):
    storm_sea(L, n, size=520, spatial=120, wave=3.0, chop=1.4, res=11)
    P = S.dsv("dsv", flood_energy=30000)
    S.no_shadow(*P["floods"])
    root = P["root"]
    hw, hl = 12.0, 49.0
    _dots(L, [(-hw, -hl, 1.5), (hw, -hl, 1.5), (hw, hl, 1.5), (-hw, hl, 1.5)], dash=3, gap=3, radius=0.6, name="target")
    for f, x in ((1, -14.0), (n, 30.0)):
        root.location = (x, 0, -0.3)
        root.rotation_euler = (0, 0, 0.06 if f == 1 else 0.14)
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_euler", frame=f)
    L.linear_fcurves(root)
    L.sun(rot=(math.radians(35), 0, math.radians(200)), energy=1.0, color=(0.5, 0.65, 1.0), angle=3)
    rain(L, n, center=(0, 0, 80), size=(160, 260, 60), count=1200, fall=-30)
    cam, _ = L.camera(loc=(8, -6, 230), target=(8, 0, 0), lens=50)
    L.cam_keys(cam, [(1, (8, -6, 230)), (n, (12, -6, 226))], ease=False)
    L.handheld(cam, n, amp=0.6, rate=0.5)
    _finish(L)


# ----------------------------------------------------------------------------- S07 snag / S08 parts

def _snag_points(A, k):
    """k=0: umbilical rising freely; k=1: swept onto the corner; k=2: bent hard around it (taut)."""
    C = CORNER
    if k == 0:
        return [A, A + Vector((0.3, -0.25, 0.9)), A + Vector((0.7, -0.6, 2.2)), A + Vector((1.1, -1.0, 3.6)),
                A + Vector((1.6, -1.5, 5.4)), A + Vector((2.4, -2.2, 8.0)), A + Vector((4, -3.5, 13))]
    if k == 1:
        return [A, A + Vector((0.5, -0.45, 0.2)), C + Vector((-0.9, 0.6, 0.45)), C + Vector((-0.15, 0.1, 0.3)),
                C + Vector((0.6, -0.5, 0.6)), C + Vector((4.0, -3.0, 3.0)), C + Vector((14, -8, 9))]
    return [A, A + Vector((0.6, -0.5, -0.3)), C + Vector((-0.8, 0.55, 0.06)), C + Vector((-0.05, 0.04, 0.07)),
            C + Vector((0.12, -0.1, -0.12)), C + Vector((3.5, -2.5, -0.3)), C + Vector((16, -10, 4))]


def snag_scene(L, n, light=380):
    _L(L)
    sea_env(L, n, density=0.07, snow_emit=0.3)
    P = lemons(L, light=light, loc=Vector((0.1, 0.4, TOP + 1.02)), yaw=PI * 0.75, arms="work")
    A = attach_point(P)
    rim(L, (-3, 7, 12), CORNER, energy=700, size=6)
    return P, A


def S07(L, n):
    P, A = snag_scene(L, n)
    m = L.mat_emission("umb_m", CYAN, 6.0)
    t = S.tube(_snag_points(A, 0), radius=0.045, mat=m, name="umb", order=3)
    S.tube_keys(t, 1, _snag_points(A, 0))
    S.tube_keys(t, int(n * 0.45), _snag_points(A, 1))
    S.tube_keys(t, n, _snag_points(A, 2))
    # strain: glow brightens and stutters as it's pulled taut
    pr = [(1, 6.0), (int(n * 0.45), 7.0)]
    rnd = random.Random(3)
    for f in range(int(n * 0.5), n + 1, 3):
        pr.append((f, 8 + 6 * (f - n * 0.5) / (n * 0.5) + rnd.uniform(-2, 2)))
    S.emit_keys(m, pr)
    cg = L.point(CORNER + Vector((0.4, -0.6, 0.6)), energy=60, color=CYAN, radius=0.2, name="cornerglow")
    S.no_shadow(cg)
    S.energy_keys(cg, [(1, 20), (int(n * 0.45), 60), (n, 160)])
    # silt puff where it catches / the frame shifts
    pc = L.particle_cloud(CORNER + Vector((0, 0, -0.6)), (1.6, 1.6, 1.2), count=500, radius=0.0025, nframes=n,
                          drift=(0.05, 0, 0.1), name="puff",
                          mat=L.mat_principled("puffm", (0.4, 0.42, 0.35), rough=1, emit=(0.3, 0.35, 0.3), emit_strength=0.3))
    f0 = int(n * 0.5)
    pc.scale = (0.02,) * 3
    pc.keyframe_insert("scale", frame=f0)
    pc.scale = (0.7,) * 3
    pc.keyframe_insert("scale", frame=f0 + 6)
    pc.scale = (1.3,) * 3
    pc.keyframe_insert("scale", frame=n)
    c0 = CORNER + Vector((2.1, -2.9, 1.25))
    cam, _ = L.camera(loc=c0, target=CORNER + Vector((-0.6, 0.6, 0.5)), lens=40)
    L.cam_keys(cam, [(1, c0), (n, CORNER + Vector((1.6, -2.3, 1.05)))])
    L.handheld(cam, n, amp=0.012, rate=0.5)
    L.cam_light(cam, energy=25, color=COLD, size_deg=50)
    _finish(L)


def S08(L, n):
    P, A = snag_scene(L, n)
    pts = _snag_points(A, 2)
    C = pts[3]
    low_pts = pts[:4] + [pts[4]]
    hi_pts = [pts[4], pts[4] + Vector((1.2, -0.9, -0.2)), pts[5], pts[6]]
    low_m, low_T, _ = S.mat_drain("low_m", CYAN, 12.0, origin=C)
    hi_m, hi_T, _ = S.mat_drain("hi_m", CYAN, 12.0, origin=C)
    low = S.tube(low_pts, radius=0.045, mat=low_m, name="umb_low", order=3)
    hi = S.tube(hi_pts, radius=0.045, mat=hi_m, name="umb_hi", order=3)
    sn = 4
    S.tube_keys(low, sn, low_pts)
    S.tube_keys(hi, sn, hi_pts)
    S.tube_keys(hi, sn + 4, [hi_pts[0] + Vector((1.2, -0.6, 2.5)), hi_pts[1] + Vector((1.6, -1.0, 2.0)), hi_pts[2] + Vector((1, -1, 1)),
                             hi_pts[3]])
    S.tube_keys(hi, n, [hi_pts[0] + Vector((3.5, -2.5, 6.0)), hi_pts[1] + Vector((3.5, -2.5, 4.5)), hi_pts[2] + Vector((2, -1, 2)),
                        hi_pts[3]])
    S.tube_keys(low, sn + 8, [low_pts[0], low_pts[1], low_pts[2], low_pts[3] + Vector((0.1, 0.05, 0.25)),
                              low_pts[4] + Vector((0.2, -0.3, 0.7))])
    S.tube_keys(low, n, [low_pts[0], low_pts[1] + Vector((0, 0, 0.05)), low_pts[2] + Vector((-0.1, 0.1, 0.0)),
                         low_pts[3] + Vector((-0.3, 0.1, 0.05)), low_pts[3] + Vector((-0.2, -0.3, 0.1))])
    S.drain_keys(low_T, [(sn, -1.0), (sn + 2, 0.3), (sn + 22, 5.0)])
    S.drain_keys(hi_T, [(sn, -1.0), (sn + 1, 0.8), (sn + 12, 12.0)])
    fl = L.point(C + Vector((0, -0.2, 0.2)), energy=0, color=(0.85, 1.0, 1.0), radius=0.4, name="flash")
    S.no_shadow(fl)
    S.energy_keys(fl, [(1, 0), (sn - 1, 0), (sn, 20000), (sn + 1, 9000), (sn + 4, 0)])
    fb = L.prim("ico", loc=C, subdivisions=2, radius=0.35, name="flashball")
    fbm = L.mat_emission("flashballm", (0.9, 1.0, 1.0), 40)
    L.assign(fb, fbm)
    for f, s in ((1, 0.001), (sn - 1, 0.001), (sn, 1.0), (sn + 2, 0.6), (sn + 4, 0.001)):
        fb.scale = (s,) * 3
        fb.keyframe_insert("scale", frame=f)
    S.bubbles_at(C, [sn + random.Random(i).randint(0, 8) for i in range(35)], rise=2.2, spread=0.25, size=0.05,
                 life=(18, 30), name="burst")
    S.energy_keys(P["torch"], [(1, 380), (sn, 380), (sn + 1, 0), (sn + 2, 160), (sn + 3, 0)], "CONSTANT")
    S.emit_keys(P["hlens_mat"], [(1, 30), (sn, 30), (sn + 1, 0.05), (sn + 2, 12), (sn + 3, 0.05)], (), "CONSTANT")
    c0 = CORNER + Vector((3.0, -4.2, 1.6))
    cam, _ = L.camera(loc=c0, target=CORNER + Vector((-0.8, 0.8, 0.6)), lens=35)
    cam.keyframe_insert("location", frame=1)
    S.shake(cam, sn, length=6, amp=0.12, rot=0.03)
    _finish(L)


# ----------------------------------------------------------------------------- S09 darkness

def S09(L, n):
    _L(L)
    sea_env(L, n, density=0.06, snow=1600, snow_emit=0.7)
    rail_a, rail_b = Vector((-6.5, -2.6, 0.35)), Vector((-3.05, -1.4, TOP - 0.02))
    railm = L.mat_principled("railm", (0.15, 0.15, 0.14), rough=0.5, metal=0.6)
    S.tube([rail_a, (rail_a + rail_b) / 2 + Vector((0, 0, 0.1)), rail_b], radius=0.09, mat=railm, name="rail")
    P = lemons(L, light=0.0, loc=rail_a, yaw=0.0, pose="none", upright=False)
    dead_umb(P)
    r = P["root"]
    d = (rail_b - rail_a).normalized()
    path = [rail_a + d * (k * (rail_b - rail_a).length / 6) + Vector((0, 0, 0.27)) for k in range(7)]
    path[0] = path[0] + d * 1.2
    L.path_follow(r, path, 1, int(n * 0.68), ease=False)
    # hand over hand
    for f in range(1, int(n * 0.7), 4):
        ph = f * 0.42
        P["shoulderL"].rotation_euler = (0.0, 0, -0.35 - 0.45 * math.sin(ph))
        P["shoulderR"].rotation_euler = (0.0, 0, 0.35 - 0.45 * math.sin(ph + PI))
        P["shoulderL"].keyframe_insert("rotation_euler", frame=f)
        P["shoulderR"].keyframe_insert("rotation_euler", frame=f)
    # onto the roof, then curls up and stops
    f1, f2 = int(n * 0.7), int(n * 0.92)
    end = Vector((-1.9, -0.7, TOP + 0.3))
    r.location = end
    r.keyframe_insert("location", frame=f2)
    r.rotation_euler = (0, PI / 2, 0.3)
    r.keyframe_insert("rotation_euler", frame=f2)
    for tag in ("L", "R"):
        for k, (f, hip, knee, sh) in enumerate(((f1, 0.0, 0.0, (0, 0, 0)), (f2, 1.2, -1.5, (-1.6, 0, 0)))):
            P[f"hip{tag}"].rotation_euler = (hip, 0, 0)
            P[f"knee{tag}"].rotation_euler = (knee, 0, 0)
            P[f"hip{tag}"].keyframe_insert("rotation_euler", frame=f)
            P[f"knee{tag}"].keyframe_insert("rotation_euler", frame=f)
        P[f"shoulder{tag}"].rotation_euler = (-1.6, 0, 0)
        P[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f2)
    rim(L, (-3, 5, 7), (-4, -1.5, 2), energy=2200, size=4)
    rim(L, (-9, 3, 5), (-4, -1.5, 2), energy=450, size=4, color=(0.25, 0.5, 0.5), name="side")
    tg = L.link(bpy.data.objects.new("s09tgt", None))
    for f, p in ((1, (-5.0, -2.2, 1.6)), (int(n * 0.7), (-3.0, -1.3, 2.9)), (n, (-2.3, -0.9, 3.2))):
        tg.location = p
        tg.keyframe_insert("location", frame=f)
    piv = L.link(bpy.data.objects.new("orbit", None))
    piv.location = (-3.6, -1.6, 2.4)
    cam, _ = L.camera(loc=(0, 0, 0), target=tg, lens=26)
    cam.parent = piv
    cam.location = (-1.6, -4.6, 0.9)
    L.cam_light(cam, energy=35, color=(0.45, 0.7, 0.75), size_deg=50)
    piv.rotation_euler = (0, 0, -0.17)
    piv.keyframe_insert("rotation_euler", frame=1)
    piv.rotation_euler = (0, 0, 0.18)
    piv.keyframe_insert("rotation_euler", frame=n)
    _finish(L)


# ----------------------------------------------------------------------------- S10 gas runs out

def S10(L, n):
    _L(L)
    sea_env(L, n, density=0.05, snow=700, snow_emit=0.3)
    P = lemons(L, light=0.0, loc=Vector((0.0, 0.0, TOP + 0.3)), yaw=0.0, pose="curl")
    dead_umb(P)
    V = world_of(P["valve"], (0, 0, 0))
    tgt = L.link(bpy.data.objects.new("vt", None))
    tgt.location = V
    c0 = V + Vector((1.25, -0.9, 0.75))
    cam, _ = L.camera(loc=c0, target=tgt, lens=50)
    L.cam_keys(cam, [(1, c0), (n, V + Vector((1.05, -0.75, 0.62)))], ease=False)
    L.dof(cam, target=tgt, fstop=2.0)
    reg = world_of(P["root"], (0.1, 0.72, -0.1))
    S.bubbles_at(V + Vector((0.0, 0.05, 0.05)), [2, 3, 5, 9, 10, 15, 22, 30, 41], rise=1.2, spread=0.03, size=0.02,
                 life=(26, 40), name="last")
    gl = L.point(V + Vector((0.4, -0.5, 0.6)), energy=6, color=(0.75, 0.9, 1.0), radius=0.05, name="key")
    S.no_shadow(gl)
    rim(L, V + Vector((-2, 2, 3)), V, energy=160, size=3)
    S.exposure_keys([(1, 0.0), (int(n * 0.45), 0.0), (n, -3.2)])
    _finish(L)


# ----------------------------------------------------------------------------- S11 split-level: ship + bell

def S11(L, n):
    S.setup(vol_end=90)
    S.sky_gradient(top=(0.002, 0.004, 0.01), horizon=(0.03, 0.05, 0.1), strength=1.0, below=(0.01, 0.02, 0.03))
    # water as a 'tank' cross-section: volume box below z=0, ocean surface on top of it only
    S.world_volume(color=(0.1, 0.3, 0.45), density=0.035, anisotropy=0.5, absorption=(0.05, 0.2, 0.3),
                   center=(0, 30, -20), size=(120, 70, 40))
    sea = S.ocean(size=140, nframes=n, wave_scale=1.0, choppiness=1.0, resolution=9, spatial=60, wind=16, foam=False,
                  mat=S.mat_ocean("sea_s", deep=(0.003, 0.01, 0.015), shallow=(0.03, 0.08, 0.1), rough=0.1,
                                  under=(0.05, 0.15, 0.2), under_strength=0.3))
    sea.location = (0, 65, 0)  # surface starts at y = -5 (front edge of the tank)
    edge = L.prim("cube", loc=(0, -5.0, -0.1), name="cutline")
    edge.scale = (60, 0.04, 0.12)
    L.assign(edge, L.mat_emission("cutm", (0.5, 0.8, 0.9), 1.5))
    P = S.dsv("dsv", length=70, beam=16, depth=8, draft=5, flood_energy=6000)
    S.no_shadow(*P["floods"])
    root = P["root"]
    root.rotation_euler = (0, 0, PI / 2 + 0.25)
    for f, x, yaw in ((1, -9.0, PI / 2 + 0.35), (n, -1.0, PI / 2 + 0.12)):
        root.location = (x, 40, 0.0)
        root.rotation_euler = (0, 0, yaw)
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_euler", frame=f)
    # bell on its wire below the moon pool (bell kept nearer the camera so it reads)
    bell = S.diving_bell("bell", radius=1.7, lamp_energy=900, hatch_strength=5)
    br = bell["root"]
    for f, z in ((1, -13.0), (n, -17.0)):
        br.location = (-1.0, 22, z)
        br.keyframe_insert("location", frame=f)
    wire = S.tube([(-1.0, 40, 8), (-1.0, 31, -4), (-1.0, 22, z + 1.8)], radius=0.06,
                  mat=L.mat_principled("wirem", (0.5, 0.5, 0.5), rough=0.4, metal=0.8), name="wire", order=3)
    for f, z in ((1, -13.0), (n, -17.0)):
        S.tube_keys(wire, f, [(-1.0, 40, 8), (-1.0, 31, (z + 1.8) / 2), (-1.0, 22, z + 2.4)])
    S.bubbles_at((-1.0, 22, -16), [k * 3 for k in range(1, 20)], rise=4.0, spread=0.3, size=0.08, name="bellbub")
    # dotted marker: where the vessel should be (vertical line down to the worksite)
    _dots(L, [(-1.0, 40, -0.6), (-1.0, 40, -40)], dash=1.2, gap=1.2, radius=0.12, closed=False, name="mark", strength=4)
    L.sun(rot=(math.radians(70), 0, math.radians(160)), energy=0.8, color=(0.5, 0.65, 1.0), angle=3)
    fill = L.area((6, 8, -6), (0, 0, 0), energy=4000, size=10, color=(0.3, 0.55, 0.8), name="underfill")
    _aim(fill, (8, 6, -6), (-1, 22, -15))
    cam, _ = L.camera(loc=(2.5, -30, 1.8), target=(-1, 25, -5.5), lens=28)
    L.cam_keys(cam, [(1, (2.5, -30, 1.8)), (n, (1.5, -28, 1.6))])
    L.handheld(cam, n, amp=0.05, rate=0.4)
    _finish(L)


# ----------------------------------------------------------------------------- S12 the rescuer finds him

def S12(L, n):
    _L(L)
    sea_env(L, n, density=0.08, snow=1600, snow_emit=0.2)
    P = lemons(L, light=0.0, loc=Vector((0.4, 0.2, TOP + 0.3)), yaw=0.4, pose="curl")
    dead_umb(P)
    Y = S.rescue_diver("yuasa", helmet=(0.85, 0.12, 0.06), suit=(0.04, 0.04, 0.05), light_energy=2600, umbilical=True)
    yr = Y["root"]
    tgt = Vector((0.4, 0.2, TOP + 0.3))
    p0, p1 = Vector((-2.9, -2.6, 5.6)), Vector((-2.0, -1.9, 5.0))
    for f, p in ((1, p0), (n, p1)):
        yr.location = p
        yr.rotation_euler = (tgt - p).to_track_quat("Y", "Z").to_euler()
        yr.keyframe_insert("location", frame=f)
        yr.keyframe_insert("rotation_euler", frame=f)
    L.anim_swim(Y, n, kick_rate=0.8, amp=0.25)
    Y["torch"].data.color = (1.0, 0.88, 0.72)
    Y["torch"].data.spot_size = math.radians(24)
    Y["torch"].location = (0.18, 0.95, 0.05)   # held out in front of the helmet (never inside it)
    S.no_shadow(Y["torch"])
    S.beam_cone((0, 0, 0), (0, 0, -1), length=5.5, radius=1.0, color=(1.0, 0.9, 0.75), strength=4.0, alpha=0.5,
                name="ybeam", parent=Y["torch"])
    S.bubbles_at(world_of(yr, (0, 0.75, 0.3)), [4 + k * 3 + (k // 6) * 14 for k in range(18)], rise=1.6, spread=0.06,
                 size=0.035, name="ybub")
    rim(L, (3, 6, 10), tgt, energy=250, size=5)
    off = Vector((-1.6, 0.15, 0.65))
    rim(L, (1.5, 1.5, 6.5), p1, energy=300, size=2, color=(0.45, 0.7, 0.75), name="yrim")
    cam, _ = L.camera(loc=p0 + off, target=tgt + Vector((0, 0, -0.7)), lens=28)
    L.cam_keys(cam, [(1, p0 + off), (n, p1 + off + Vector((0.2, 0.2, -0.1)))])
    L.handheld(cam, n, amp=0.015, rate=0.5)
    _finish(L)


# ----------------------------------------------------------------------------- S13 into the bell

def S13(L, n):
    _L(L)
    sea_env(L, n, density=0.06, seabed=False, manifold=False, snow=1000, vol_center=(0, 0, 6), vol_size=(40, 40, 24))
    bell = S.diving_bell("bell", radius=1.6, lamp_energy=0, hatch_strength=14)
    bell["root"].location = (0, 0, 12.5)
    hz = 12.5 + bell["bottom_z"]
    S.lift_wire((0, 0, 14.5), (0, 0, 40), name="bellwire")
    sp = L.spot((0, 0, hz - 0.1), (0, 0, 0), energy=3500, size_deg=55, blend=0.7, color=(1.0, 0.72, 0.4), name="hatchlight")
    S.no_shadow(sp)
    Y = S.rescue_diver("yuasa", helmet=(0.85, 0.12, 0.06), light_energy=0, umbilical=True)
    yr = Y["root"]
    P = lemons(L, light=0.0, loc=Vector((0, 0, 5)), yaw=0.0, pose="none", upright=False)
    lr = P["root"]
    for f, z in ((1, 5.6), (n, 8.4)):
        yr.location = (0.25, 0.1, z)
        yr.rotation_euler = (-PI / 2 + 0.25, 0, 0.3)
        yr.keyframe_insert("location", frame=f)
        yr.keyframe_insert("rotation_euler", frame=f)
        lr.location = (-0.35, -0.25, z - 1.4)
        lr.rotation_euler = (-PI / 2 + 0.6, 0.35, -0.4)
        lr.keyframe_insert("location", frame=f)
        lr.keyframe_insert("rotation_euler", frame=f)
    yr.rotation_euler = (PI / 2 - 0.25, 0, 0.3)
    yr.keyframe_insert("rotation_euler", frame=1)
    yr.keyframe_insert("rotation_euler", frame=n)
    lr.rotation_euler = (PI / 2 - 0.6, 0.35, -0.4)
    lr.keyframe_insert("rotation_euler", frame=1)
    lr.keyframe_insert("rotation_euler", frame=n)
    L.anim_swim(Y, n, kick_rate=1.0, amp=0.35)
    Y["shoulderL"].rotation_euler = (-2.6, 0, 0.3)  # one arm down holding the limp diver's harness
    for tag in ("L", "R"):
        P[f"shoulder{tag}"].rotation_euler = (-2.9, 0, 0.3 if tag == "L" else -0.3)
        P[f"hip{tag}"].rotation_euler = (0.3, 0, 0)
        P[f"knee{tag}"].rotation_euler = (-0.5, 0, 0)
    dead_umb(P)
    S.bubbles_at((0.35, 0.1, 7.6), [3 + k * 3 for k in range(16)], rise=2.0, spread=0.08, size=0.04, name="ybub")
    fill = L.area((4, -4, 2), (0, 0, 0), energy=500, size=6, color=(0.25, 0.5, 0.5), name="teal")
    _aim(fill, (4, -4, 2), (0, 0, 7))
    cam, _ = L.camera(loc=(1.6, -4.2, 0.8), target=(0, 0, 9.0), lens=20)
    L.cam_keys(cam, [(1, (1.6, -4.2, 0.8)), (n, (1.2, -3.4, 2.6))])
    L.handheld(cam, n, amp=0.02, rate=0.5)
    _finish(L)


# ----------------------------------------------------------------------------- S14 / S15 inside the bell

def bell_interior(L, n, lamp=55.0):
    """2.5D cutaway of a diving bell: back half shell, floor, bench, gas panel, lamp, trunk hatch, two figures."""
    L.set_world(color=(0.004, 0.008, 0.012), strength=1)
    R, H = 1.3, 2.3
    steel = S.mat_paint("bellin", (0.55, 0.58, 0.55), rough=0.5, grime=0.35)
    outer = S.mat_paint("bellout", (0.85, 0.42, 0.05), rough=0.45, grime=0.3)
    bm = S.bmesh.new()
    seg = 24
    rings = []
    for k in range(seg + 1):
        a = PI * k / seg
        x, y = R * math.cos(a), R * math.sin(a)
        rings.append([bm.verts.new((x, y, 0)), bm.verts.new((x, y, H))])
    for k in range(seg):
        bm.faces.new((rings[k][0], rings[k + 1][0], rings[k + 1][1], rings[k][1]))
    wall = L.mesh_from_bm("bellwall", bm)
    sol = wall.modifiers.new("sol", "SOLIDIFY")
    sol.thickness = 0.12
    sol.offset = 1.0
    sol.material_offset_rim = 1
    wall.data.materials.append(steel)
    wall.data.materials.append(outer)
    # dome (back half)
    dome = L.prim("sphere", loc=(0, 0, H), segments=24, ring_count=12, radius=R, name="belldome")
    dome.scale = (1, 1, 0.45)
    bm2 = S.bmesh.new()
    bm2.from_mesh(dome.data)
    S.bmesh.ops.delete(bm2, geom=[v for v in bm2.verts if v.co.y < -0.01 or v.co.z < -0.01], context="VERTS")
    bm2.to_mesh(dome.data)
    bm2.free()
    L.assign(dome, steel)
    fl = L.prim("cyl", loc=(0, 0, -0.08), vertices=32, radius=R + 0.12, depth=0.16, name="bellfloor")
    L.assign(fl, L.mat_noise_surface("bellfl", (0.3, 0.3, 0.28), (0.5, 0.5, 0.46), scale=10, bump=0.3, voronoi=False))
    # cut-section outline (orange) along the front edge
    for x in (-R - 0.06, R + 0.06):
        s = L.prim("cube", loc=(x, 0, H / 2), name="cutedge")
        s.scale = (0.07, 0.03, H / 2 + 0.05)
        L.assign(s, outer)
    hatch = L.prim("cyl", loc=(-0.75, -0.35, 0.005), vertices=24, radius=0.38, depth=0.02, name="trunkwater")
    L.assign(hatch, S.mat_water_surface("trunkw", color=(0.02, 0.12, 0.14), rough=0.05, alpha=1.0, ripple=0.3, nframes=n))
    bench = L.prim("cube", loc=(0.3, 0.95, 0.45), name="bench")
    bench.scale = (0.7, 0.2, 0.05)
    L.assign(bench, steel)
    panel = L.prim("cube", loc=(-0.55, 1.1, 1.45), rot=(0, 0, -0.4), name="gaspanel")
    panel.scale = (0.38, 0.03, 0.32)
    L.assign(panel, L.mat_principled("panelm", (0.1, 0.12, 0.12), rough=0.5, metal=0.3))
    gm = L.mat_emission("gaugem", (0.85, 0.9, 0.8), 1.2)
    for k in range(4):
        g = L.prim("cyl", loc=(-0.78 + (k % 2) * 0.3 * math.cos(0.4), 1.17 - (k % 2) * 0.12, 1.6 - (k // 2) * 0.28),
                   vertices=16, radius=0.07, depth=0.02, rot=(PI / 2, 0, -0.4), name="gauge")
        L.assign(g, gm)
    lampm = L.mat_emission("lampm", (1.0, 0.75, 0.45), 18)
    lb = L.prim("cyl", loc=(0.0, 0.85, H + 0.25), vertices=16, radius=0.15, depth=0.06, rot=(0.6, 0, 0), name="lamp")
    L.assign(lb, lampm)
    lp = L.point((0.0, 0.5, H + 0.05), energy=lamp, color=(1.0, 0.72, 0.45), radius=0.15, name="lamp_l")
    rimL = L.area((0.6, -1.8, H + 1.2), (0, 0, 0), energy=60, size=2, color=(0.4, 0.6, 0.9), name="coldrim")
    _aim(rimL, (0.6, 1.8, H + 0.8), (0.4, 0.3, 0.7))
    S.drips([(0.6, 0.6, H + 0.35), (-0.4, 0.7, H + 0.4), (0.1, 1.0, H + 0.2)], n, fall=H, seed=4)
    # Lemons: helmet off, lying on his back across the bell floor (head toward +X), in front
    lem = L.char_figure(name="lemfig", color=(0.1, 0.1, 0.11), height=1.75)
    lem["root"].location = (-1.22, -0.3, 0.13)
    lem["root"].rotation_euler = (PI / 2, 0, PI / 2)
    lem["neck"].rotation_euler = (-0.25, 0, 0)
    for tag, s in (("L", -1), ("R", 1)):
        lem[f"hip{tag}"].rotation_euler = (0.55, 0, s * 0.05)
        lem[f"knee{tag}"].rotation_euler = (-1.0, 0, 0)
        lem[f"shoulder{tag}"].rotation_euler = (0.1, 0, s * 0.25)
        lem[f"elbow{tag}"].rotation_euler = (0.2, 0, 0)
    # Allcock: kneeling at his head, facing -X, leaning over him (profile to camera)
    al = L.char_figure(name="allfig", color=(0.02, 0.02, 0.025), height=1.78)
    al["root"].location = (1.12, -0.15, -0.44)
    al["root"].rotation_euler = (0, 0, PI / 2)
    for tag, s in (("L", -1), ("R", 1)):
        al[f"knee{tag}"].rotation_euler = (-1.6, 0, 0)
        al[f"shoulder{tag}"].rotation_euler = (0.7, 0, s * 0.15)
        al[f"elbow{tag}"].rotation_euler = (0.9, 0, 0)
    key = L.area((-0.4, -2.2, 2.4), (0, 0, 0), energy=45, size=1.5, color=(0.55, 0.7, 0.9), name="frontrim")
    _aim(key, (-0.4, -2.2, 2.4), (0.0, -0.3, 0.2))
    return lem, al, lp


def _lean(al, f, a):
    al["pelvis"].rotation_euler = (-a, 0, 0)
    al["pelvis"].keyframe_insert("rotation_euler", frame=f)
    for tag in ("L", "R"):
        al[f"hip{tag}"].rotation_euler = (a, 0, 0)
        al[f"hip{tag}"].keyframe_insert("rotation_euler", frame=f)
    al["neck"].rotation_euler = (-0.25 * a, 0, 0)
    al["neck"].keyframe_insert("rotation_euler", frame=f)


def S14(L, n):
    lem, al, lp = bell_interior(L, n)
    for f, a in ((1, 0.8), (14, 1.25), (26, 1.25), (36, 0.85), (48, 1.25), (60, 1.25), (n, 0.9)):
        _lean(al, f, a)
    cam, _ = L.camera(loc=(0.05, -5.8, 1.1), target=(0.05, 0.3, 0.45), lens=42)
    L.cam_keys(cam, [(1, (0.05, -5.8, 1.1)), (n, (0.07, -5.5, 1.08))])
    _finish(L)


def S15(L, n):
    lem, al, lp = bell_interior(L, n, lamp=50)
    for f, a in ((1, 0.9), (int(n * 0.5), 0.7), (n, 0.45)):
        _lean(al, f, a)
    t = lem["torso"]
    base = tuple(t.scale)
    for f, k in ((1, 1.0), (10, 1.0), (20, 1.09), (32, 1.0), (44, 1.1), (56, 1.0)):
        t.scale = (base[0] * (1 + (k - 1) * 0.4), base[1] * (1 + (k - 1) * 1.6), base[2])
        t.keyframe_insert("scale", frame=f)
    S.energy_keys(lp, [(1, 50), (int(n * 0.6), 65), (n, 68)])
    S.emit_keys(bpy.data.materials["lampm"], [(1, 18), (int(n * 0.6), 24)])
    cam, _ = L.camera(loc=(0.2, -5.6, 1.0), target=(0.3, 0.3, 0.4), lens=44)
    cam.data.keyframe_insert("lens", frame=1)
    cam.data.lens = 58
    cam.data.keyframe_insert("lens", frame=n)
    _finish(L)


# ----------------------------------------------------------------------------- S16 / S17 cold diagram

def _diagram(L, n):
    L.set_world(color=(0, 0, 0), strength=0)
    bg = L.prim("plane", loc=(0, 0.8, 1.0), rot=(PI / 2, 0, 0), size=1, name="bg")
    bg.scale = (14, 14, 1)
    L.assign(bg, S.flat_mat("bgm", (0.005, 0.035, 0.08), 1))
    # water-field wave lines
    for k in range(-9, 12):
        pts = [(x * 0.25, 0.7, 1 + k * 0.32 + 0.04 * math.sin(x * 0.9 + k)) for x in range(-16, 17)]
        cu = bpy.data.curves.new("w", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = 0.005
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            sp.points[i].co = (*p, 1)
        o = L.link(bpy.data.objects.new("wave", cu))
        o.data.materials.append(S.flat_mat("wavem", (0.03, 0.13, 0.22), 1))
    fig = L.char_figure(name="xfig", height=1.75)
    xm = S.mat_beam("xraym", (0.75, 0.92, 1.0), 1.4, alpha=0.95)
    for o in bpy.data.objects:
        if o.name.startswith("xfig") and o.type == "MESH":
            L.assign(o, xm)
    fig["root"].rotation_euler = (0, 0, PI)
    fig["root"].location = (-0.35, 0, 0)
    for tag, s in (("L", 1), ("R", -1)):
        fig[f"shoulder{tag}"].rotation_euler = (0, 0, s * -0.2)
        fig[f"hip{tag}"].rotation_euler = (0, 0, s * -0.05)
    L.particle_cloud((-0.3, -0.2, 1.1), (2.4, 0.4, 2.6), count=220, radius=0.008, nframes=n, drift=(0.02, 0, -0.05),
                     name="frost", mat=L.mat_emission("frostm", (0.8, 0.95, 1.0), 2.0))
    return fig


def _softglow(name, color, strength):
    """Emission blob, opaque in the centre and fading to transparent at the silhouette."""
    m, nn, l = S._m(name)
    for nd in list(nn):
        if nd.type == "BSDF_PRINCIPLED":
            nn.remove(nd)
    lw = nn.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    inv = nn.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    l.new(lw.outputs["Facing"], inv.inputs[1])
    pw = nn.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 2.0
    l.new(inv.outputs[0], pw.inputs[0])
    em = nn.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    tr = nn.new("ShaderNodeBsdfTransparent")
    mx = nn.new("ShaderNodeMixShader")
    l.new(pw.outputs[0], mx.inputs[0])
    l.new(tr.outputs[0], mx.inputs[1])
    l.new(em.outputs[0], mx.inputs[2])
    l.new(mx.outputs[0], nn["Material Output"].inputs["Surface"])
    m.surface_render_method = "BLENDED"
    return m


def _thermo(L, n, x=0.85, z0=0.35, h=1.5, drain=(1, 1)):
    glass = L.mat_emission("thglass", (0.85, 0.95, 1.0), 1.6)
    tube_o = S.tube([(x, -0.05, z0), (x, -0.05, z0 + h)], radius=0.075, mat=glass, name="thtube", order=2)
    tube_o.data.bevel_depth = 0.075
    tube_o.data.fill_mode = "FULL"
    inner = S.tube([(x, -0.08, z0), (x, -0.08, z0 + h)], radius=0.055, mat=S.flat_mat("thin", (0.01, 0.03, 0.06), 1),
                   name="thin", order=2)
    blb = L.prim("sphere", loc=(x, -0.1, z0 - 0.08), segments=16, ring_count=8, radius=0.14, name="bulb")
    bm = L.mat_emission("bulbm", (1.0, 0.25, 0.15), 3)
    L.assign(blb, bm)
    bar = L.prim("cube", loc=(x, -0.12, z0), name="bar")
    bar.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 1)))
    bar.scale = (0.05, 0.01, h * 0.45)
    barm = L.mat_emission("barm", (1.0, 0.25, 0.15), 5)
    L.assign(bar, barm)
    f0, f1 = drain
    bar.keyframe_insert("scale", frame=f0)
    bar.scale = (0.05, 0.01, h * 0.08)
    bar.keyframe_insert("scale", frame=f1)
    S.emit_keys(barm, [], [(f0, (1.0, 0.25, 0.15)), (f1, (0.3, 0.7, 1.0))])
    S.emit_keys(bm, [], [(f0, (1.0, 0.25, 0.15)), (f1, (0.3, 0.7, 1.0))])
    for k in range(6):
        t = L.prim("cube", loc=(x + 0.13, -0.05, z0 + 0.15 + k * h / 6), name="tick")
        t.scale = (0.04, 0.005, 0.006)
        L.assign(t, glass)
    return bar


def S16(L, n):
    fig = _diagram(L, n)
    _thermo(L, n, drain=(4, n - 4))
    cam, _ = L.camera(loc=(0.15, -9, 0.95), target=(0.15, 0, 0.95), lens=50)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 3.9
    cam.data.keyframe_insert("ortho_scale", frame=1)
    cam.data.ortho_scale = 3.65
    cam.data.keyframe_insert("ortho_scale", frame=n)
    _finish(L)


def S17(L, n):
    fig = _diagram(L, n)
    # head glow (oxygen demand) dims as the body cools
    hz = 1.62
    hg = L.prim("sphere", loc=(-0.35, -0.3, hz), segments=16, ring_count=10, radius=0.17, name="headglow")
    hm = _softglow("headglowm", (1.0, 0.65, 0.25), 6)
    L.assign(hg, hm)
    S.emit_keys(hm, [(1, 6), (int(n * 0.8), 0.6)], [(1, (1.0, 0.65, 0.25)), (int(n * 0.8), (0.35, 0.6, 1.0))])
    for f, s in ((1, 1.25), (int(n * 0.8), 0.85)):
        hg.scale = (s,) * 3
        hg.keyframe_insert("scale", frame=f)
    # O2-demand gauge: arc, ticks, falling needle
    gc = Vector((0.55, -0.2, 1.25))
    arc = [gc + Vector((0.36 * math.cos(a), 0, 0.36 * math.sin(a))) for a in [PI * k / 16 for k in range(17)]]
    S.tube(arc, radius=0.018, mat=L.mat_emission("arcm", (0.85, 0.95, 1.0), 1.8), name="arc", order=3)
    for k in range(7):
        a = PI * k / 6
        t = L.prim("cube", loc=gc + Vector((0.3 * math.cos(a), 0, 0.3 * math.sin(a))), rot=(0, -a, 0), name="gtick")
        t.scale = (0.05, 0.005, 0.008)
        L.assign(t, L.mat_emission("gtickm", (1.0, 0.3, 0.2) if k >= 5 else (0.85, 0.95, 1.0), 2))
    piv = L.link(bpy.data.objects.new("needle", None))
    piv.location = gc
    nd = L.prim("cube", loc=(0.14, -0.02, 0), name="needle_m")
    nd.scale = (0.14, 0.005, 0.014)
    L.assign(nd, L.mat_emission("needlem", (1.0, 0.85, 0.2), 4))
    nd.parent = piv
    for f, a in ((1, -0.35), (int(n * 0.25), -0.35), (int(n * 0.85), -2.7), (n, -2.75)):
        piv.rotation_euler = (0, a, 0)
        piv.keyframe_insert("rotation_euler", frame=f)
    lab = L.text3d("O2 DEMAND", loc=(gc.x, -0.2, gc.z - 0.16), size=0.09, mat=L.mat_emission("labm", (0.85, 0.95, 1.0), 2))
    cam, _ = L.camera(loc=(0.15, -9, 0.6), target=None, lens=50)
    cam.rotation_euler = (PI / 2, 0, 0)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 3.4
    L.cam_keys(cam, [(1, (0.1, -9, 0.75)), (n, (0.25, -9, 1.35))])
    cam.data.keyframe_insert("ortho_scale", frame=1)
    cam.data.ortho_scale = 2.9
    cam.data.keyframe_insert("ortho_scale", frame=n)
    _finish(L)
