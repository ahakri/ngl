"""HAUNT-06 — Bachelor's Grove (the 1991 photo). One builder per shot: def Sxx(L, n).
Our own framing and our own seated pose: the real photograph is never imitated or shown.
Sets live in PIPELINE/blender/lib_haunted.py ("BACHELOR'S GROVE sets")."""
import importlib, sys, os, math, random
_LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PIPELINE", "blender")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import lib_haunted as H
importlib.reload(H)
import bpy
from mathutils import Vector

# IR wide framing (S01 push start -> end; S12/S13 use the end, S14 the start)
IR_P0, IR_P1, IR_T = (0.4, -6.0, 1.3), (0.25, -4.0, 1.25), (0.0, 0.0, 0.3)


def _world(L, c, vol_end=60):
    H.eevee_quality()
    L.set_world(c, 1.0)
    try:
        bpy.context.scene.eevee.volumetric_end = vol_end
    except Exception:
        pass


def _sun_dir(L, d, energy=1.0, color=(1, 1, 1), name="sun", angle=1.5):
    s = L.sun(rot=(0, 0, 0), energy=energy, color=color, angle=angle, name=name)
    s.rotation_euler = Vector(d).normalized().to_track_quat("-Z", "Y").to_euler()
    return s


def _ir(L, fog=0.02):
    """Infrared-film look built from materials + light: black sky, white foliage/grass, one low key from camera left."""
    _world(L, (0.0, 0.0, 0.0))
    g = H.grove_clearing(ir=True)
    _sun_dir(L, (0.75, 0.55, -0.38), energy=2.2, color=(1, 1, 1), name="irkey")
    L.fog_volume(center=(0, 4, 1.2), size=(60, 50, 2.4), density=fog, color=(0.85, 0.85, 0.85))
    return g


def _night(L, fog=0.025):
    _world(L, (0.005, 0.007, 0.014))
    g = H.grove_clearing(ir=False)
    _sun_dir(L, (0.3, -0.85, -0.45), energy=1.4, color=(0.55, 0.65, 1.0), name="moon")
    L.fog_volume(center=(0, 4, 1.2), size=(60, 50, 2.4), density=fog, color=(0.7, 0.74, 0.85))
    return g


def _ir_push(L, n, start, end):
    _ir(L)
    c = H.cam(start, IR_T, lens=35)
    H.cam_move(c, [(1, start, IR_T), (n, end, IR_T)], ease=False)
    L.cam_light(c, energy=6, color=(1, 1, 1))
    return c


# --------------------------------------------------------------------------- IR wide (S01, S12, S13, S14)
def S01(L, n):
    _ir_push(L, n, IR_P0, IR_P1)
    L.bake_static()


def S14(L, n):
    # same speed as S01 so the loop cut back to S01 frame 1 is seamless
    k = n / 122.0
    end = tuple(IR_P0[i] + (IR_P1[i] - IR_P0[i]) * k for i in range(3))
    _ir_push(L, n, IR_P0, end)
    L.bake_static()


def S12(L, n):
    _ir(L)
    c = H.cam(IR_P1, IR_T, lens=35)
    # wind in the grass: the fog creeps; camera locked off
    L.cam_light(c, energy=6, color=(1, 1, 1))
    fogs = [o for o in bpy.data.objects if o.name.startswith("fog")]
    for o in fogs:
        o.keyframe_insert("location", frame=1)
        o.location.x += 0.6
        o.keyframe_insert("location", frame=n)
    H.dust((0, -1.5, 1.0), (4, 4, 1.6), n, count=120, radius=0.002, emit=0.3, drift=(0.03, 0, 0.0))
    L.bake_static()


def S13(L, n):
    _ir(L)
    p1 = tuple(IR_P1[i] + (IR_T[i] - IR_P1[i]) * 0.02 for i in range(3))
    c = H.cam(IR_P1, IR_T, lens=35)
    H.cam_move(c, [(1, IR_P1, IR_T), (n, p1, IR_T)], ease=False)
    L.cam_light(c, energy=6, color=(1, 1, 1))
    w = H.seated_woman("sitter", alpha=0.5, emit=0.2, seat_z=0.75)
    w["root"].location.x, w["root"].location.y = 0.08, 0.02
    w["root"].rotation_euler = (0, 0, math.pi + math.radians(14))     # facing the camera side, turned a little
    w["neck"].rotation_euler = (math.radians(-6), 0, math.radians(-24))   # head turned away
    H.set_alpha(w["mat"], [(1, 0.0), (min(n - 4, 24), 0.5)])
    H.key_principled(w["mat"], "Emission Strength", [(1, 0.0), (min(n - 4, 24), 0.2)])
    L.bake_static()


def S09(L, n):
    _ir(L)
    p0, p1, tg = (0.22, -3.7, 1.15), (0.17, -3.25, 1.12), (0.0, 0.0, 0.42)
    c = H.cam(p0, tg, lens=50)
    H.cam_move(c, [(1, p0, tg), (n, p1, tg)], ease=False)
    L.cam_light(c, energy=4, color=(1, 1, 1))
    L.bake_static()


def S07(L, n):
    _ir(L)
    p0, tg = (0.12, -4.6, 1.42), (0.0, 0.0, 0.42)
    c = H.cam(p0, tg, lens=50)
    still = int(n * 0.45)
    H.cam_move(c, [(1, (0.2, -4.62, 1.47), (0.06, 0.0, 0.47)), (still, p0, tg), (n, p0, tg)])
    L.cam_light(c, energy=4, color=(1, 1, 1))
    # viewfinder mask (3D, on the lens): black surround, portrait gate, focusing circle + split line
    D = 0.1
    vh, vw = 0.1 * 36 / 50, 0.1 * 36 / 50 * 9 / 16
    gh, gw = vh * 0.66, vw * 0.86
    blk = L.mat_emission("vf_black", (0.0, 0.0, 0.0), 0.0)
    gx, gz = vw * 0.42, vh * 0.3          # gate half-sizes (vw, vh = full visible width/height at D)
    bx = [(0, gz + vh, 0, vw, vh, 0.0005), (0, -gz - vh, 0, vw, vh, 0.0005),
          (gx + vw, 0, 0, vw, gz + 0.001, 0.0005), (-gx - vw, 0, 0, vw, gz + 0.001, 0.0005)]
    gw = gx * 2
    mask = H.box_mesh("vf_mask", bx, blk)
    mask.parent = c
    mask.location = (0, 0, -D)
    ring = L.prim("torus", loc=(0, 0, -D + 0.0005), major_radius=gw * 0.16, minor_radius=0.00018)
    L.assign(ring, L.mat_emission("vf_ring", (0.85, 0.85, 0.85), 0.6))
    ring.parent = c
    split = H.box_mesh("vf_split", [(0, 0, 0, gw * 0.16, 0.00012, 0.0002)], L.mat_emission("vf_split_m", (0.85, 0.85, 0.85), 0.5))
    split.parent = c
    split.location = (0, 0, -D + 0.0005)
    shot = int(n * 0.72)
    H.flash_pop(c, shot, peak=60000, decay=3, size=0.3, offset=(0.0, 0.08, 0.0))
    L.bake_static()


# --------------------------------------------------------------------------- night clearing (S03, S05) and S06 macro
def S03(L, n):
    _night(L)
    p0, p1 = (1.6, -5.3, 0.5), (6.2, -5.3, 0.5)
    c = H.cam(p0, (0.6, 3.0, 0.45), lens=28)
    H.cam_move(c, [(1, p0, (0.6, 3.0, 0.45)), (n, p1, (4.2, 3.0, 0.45))], ease=False)
    H.handheld(c, n, amp=0.004, rate=0.4)
    L.cam_light(c, energy=10, color=(0.6, 0.68, 0.9))
    H.dust((4, -3, 0.6), (6, 4, 1.0), n, count=200, radius=0.0025, emit=0.15)
    L.bake_static()


def S05(L, n):
    _night(L, fog=0.03)
    rnd = random.Random(4)
    people = [("inv_a", (-1.7, -3.0), 30, (0.05, 0.05, 0.065)), ("inv_b", (1.6, -3.4), -60, (0.07, 0.045, 0.03)),
              ("inv_m", (0.75, -5.2), 70, (0.04, 0.05, 0.045))]
    turn = int(n * 0.55)
    for i, (nm, (x, y), a0, col) in enumerate(people):
        p = H.figure(nm, color=col, height=1.76 - 0.05 * i, coat=False)
        r = p["root"]
        r.location = (x, y, 0)
        face = math.atan2(-(0 - x), (0 - y))            # rotation that faces the hero stone
        r.rotation_euler = (0, 0, face + math.radians(a0))
        r.keyframe_insert("rotation_euler", frame=1)
        r.keyframe_insert("rotation_euler", frame=turn - 14 + 4 * i)
        r.rotation_euler = (0, 0, face)
        r.keyframe_insert("rotation_euler", frame=turn + 4 * i)
        H.pose_hold(p, "R", shoulder=(math.radians(70), 0, 0), elbow=(math.radians(10), 0, 0))
        fl = L.spot((0, 0, 0), (math.radians(78), 0, 0), energy=260, size_deg=22, blend=0.4, color=(1.0, 0.9, 0.75), name=nm + "_fl", radius=0.02)
        fl.parent = r
        fl.location = (0.22, 0.45, 1.25)
        fl.data.volume_factor = 1.5
        if nm == "inv_m":
            H.pose_hold(p, "L", shoulder=(math.radians(55), 0, math.radians(-15)), elbow=(math.radians(25), 0, 0))
            meter = H.box_mesh("meter", [(0, 0, 0, 0.035, 0.06, 0.012)], L.mat_principled("meter_m", (0.12, 0.12, 0.1), rough=0.5))
            meter.parent = p["elbowL"]
            meter.location = (0, 0.04, -0.3)
            led = L.prim("sphere", loc=(0, 0.04, 0.014), segments=8, ring_count=6, radius=0.006)
            lm = L.mat_emission("led_m", (1.0, 0.1, 0.05), 8.0)
            L.assign(led, lm)
            led.parent = meter
            pairs = [(f, 30.0 if rnd.random() < 0.55 else 0.5) for f in range(1, n + 1)]
            H.key_emission(lm, pairs, "CONSTANT")
            ll = L.point((0, 0.04, 0.03), energy=0.5, color=(1.0, 0.1, 0.05), radius=0.01, name="led_lt")
            ll.parent = meter
            H.key_energy(ll, [(f, 1.5 if v > 1 else 0.0) for f, v in pairs])
    rim = L.area((0.0, 4.0, 3.0), (0, 0, 0), energy=120, size=0.3, color=(0.55, 0.65, 1.0), name="rim")
    H.aim(rim, (0.0, 4.0, 3.0), (0.5, -4.0, 1.2))
    p0, tg = (2.1, -8.4, 1.95), (-0.1, -1.0, 0.8)
    c = H.cam(p0, tg, lens=35)
    H.cam_move(c, [(1, p0, tg), (n, (2.0, -8.0, 1.92), tg)], ease=False)
    H.handheld(c, n, amp=0.008, rate=0.7, rot_amp=0.003)
    L.cam_light(c, energy=6, color=(0.6, 0.68, 0.9))
    H.crisp_shadows()
    L.bake_static()


def S06(L, n):
    _night(L, fog=0.015)
    tpos = (0.9, -3.2, 0)
    tri, head = H.tripod("tripod", tpos, h=1.22)
    tilt = H.empty("tilt", (0, 0, 0.05), parent=head)
    tilt.rotation_euler = (math.radians(-28), 0, 0)
    tilt.keyframe_insert("rotation_euler", frame=1)
    tilt.rotation_euler = (0, 0, 0)
    tilt.keyframe_insert("rotation_euler", frame=int(n * 0.75))
    head.rotation_euler = (0, 0, math.radians(-12))
    slr = H.slr_camera("slr", (0, 0, 0.045), parent=tilt)
    H.gloved_hand("glove", parent=slr, loc=(0.1, -0.005, 0.0), rot=(0, 0, 0))
    # stone ledge beside it with the plain 'IR' film canister
    st = H.box_mesh("ledge", [(tpos[0] - 0.2, tpos[1] + 0.05, 0.55, 0.16, 0.1, 0.6)], H.grove_mats(False)["stone"], bevel=0.02)
    can = L.prim("cyl", loc=(tpos[0] - 0.17, tpos[1] + 0.02, 1.175), vertices=20, radius=0.016, depth=0.05)
    L.assign(can, L.mat_principled("can_m", (0.08, 0.08, 0.085), rough=0.3, metal=0.6))
    band = L.prim("cyl", loc=(tpos[0] - 0.17, tpos[1] + 0.02, 1.172), vertices=20, radius=0.0163, depth=0.028)
    L.assign(band, L.mat_principled("can_lbl", (0.75, 0.73, 0.65), rough=0.8))
    ir = L.text3d("IR", loc=(tpos[0] - 0.17, tpos[1] + 0.02 - 0.0166, 1.166), size=0.016, extrude=0.0,
                  mat=L.mat_principled("can_ink", (0.02, 0.02, 0.02), rough=0.6), name="ir_txt")
    # lights: flashlight bounce (warm, low front) + moon rim from behind
    L.point((tpos[0] + 0.5, tpos[1] - 0.6, 0.8), energy=40, color=(1.0, 0.85, 0.65), radius=0.05, name="bounce")
    rim = L.spot((tpos[0] - 0.4, tpos[1] + 1.2, 1.9), (0, 0, 0), energy=400, size_deg=30, blend=0.5, color=(0.6, 0.7, 1.0), name="rimspot")
    H.aim(rim, (tpos[0] - 0.4, tpos[1] + 1.2, 1.9), (tpos[0], tpos[1], 1.25))
    ctr = Vector((tpos[0] - 0.07, tpos[1], 1.22))

    def orbit(deg, r=1.05, h=1.32):
        a = math.radians(deg)
        return (ctr.x + r * math.sin(a), ctr.y - r * math.cos(a), h)
    c = H.cam(orbit(-20), tuple(ctr), lens=85)
    H.cam_move(c, [(1, orbit(-20), tuple(ctr)), (n, orbit(-5), tuple(ctr))], ease=False)
    L.dof(c, target=slr, fstop=2.8)
    H.dust(tuple(ctr), (0.6, 0.6, 0.5), n, count=120, radius=0.0008, emit=0.3)
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S02 lane + fence, S04 folklore fog
def S02(L, n):
    _world(L, (0.006, 0.008, 0.016), vol_end=60)
    mats = H.grove_mats(False)
    H.ground_box("lane_ground", -60, 60, -40, 60, 0.0, mats["grass"])
    H.box_mesh("lane", [(0, -12, 0.01, 1.8, 20, 0.012)], L.mat_noise_surface("broken_asph", (0.02, 0.02, 0.02), (0.13, 0.12, 0.11),
                                                                          scale=3, bump=0.6, voronoi=True, rough=0.7))
    H.chainlink("fence", -12, 12, 8.0, h=1.9, gate=(-1.7, 3.4), gate_angle=1.25,
                mat=L.mat_principled("fence_m", (0.7, 0.72, 0.75), rough=0.35, metal=0.6, emit=(0.4, 0.45, 0.55), emit_strength=0.08))
    gl = L.point((0.0, 10.5, 2.2), energy=60, color=(0.6, 0.7, 1.0), radius=0.5, name="fencebackglow")
    H.headstone_row((-3.5, 2.5, 5.0), y=13.0, h=0.8)
    H.leafy_trees("lane_trees", [(-16, -3.2, -30, 25), (3.2, 16, -30, 25), (-14, 14, 22, 34)], mats, count=34, seed=8)
    _sun_dir(L, (0.35, 0.8, -0.45), energy=2.6, color=(0.55, 0.65, 1.0), name="moon")
    _sun_dir(L, (-0.3, -0.8, -0.3), energy=0.8, color=(0.55, 0.65, 1.0), name="backmoon")
    L.fog_volume(center=(0, 0, 1.4), size=(40, 60, 2.8), density=0.025, color=(0.7, 0.74, 0.85))
    p0, p1, tg = (0.35, -7.0, 1.6), (0.2, -1.5, 1.6), (0.0, 8.0, 1.1)
    c = H.cam(p0, tg, lens=28)
    H.cam_move(c, [(1, p0, tg), (n, p1, tg)], ease=False)
    H.handheld(c, n, amp=0.012, rate=0.9, rot_amp=0.004)
    L.cam_light(c, energy=25, color=(0.6, 0.68, 0.9))
    lm = L.mat_principled("leaves", (0.05, 0.06, 0.03), rough=1.0, emit=(0.3, 0.35, 0.25), emit_strength=0.05)
    L.particle_cloud((0, -2, 2.5), (6, 12, 4), count=25, radius=0.008, mat=lm, drift=(0.2, 0, -0.35), seed=3, nframes=n, name="leaves")
    L.bake_static()


def S04(L, n):
    _world(L, (0.006, 0.008, 0.015), vol_end=70)
    mats = H.grove_mats(False)
    H.ground_box("f_ground", -60, 60, -40, 80, 0.0, mats["grass"])
    H.leafy_trees("f_trees", [(-18, -2.6, -6, 30), (2.6, 18, -6, 30)], mats, count=30, seed=11)
    _sun_dir(L, (0.2, -0.9, -0.4), energy=0.4, color=(0.55, 0.65, 1.0), name="moon")
    L.fog_volume(center=(0, 20, 2.5), size=(50, 60, 5), density=0.03, color=(0.72, 0.76, 0.88))
    fh = H.farmhouse("farm", (1.0, 34.0, 0), rot_z=math.radians(-8), porch_energy=180)
    fade = int(n * 0.85)
    r = fh["root"]
    r.scale = (1, 1, 1)
    r.keyframe_insert("scale", frame=1)
    r.scale = (0.6, 0.6, 0.6)
    r.keyframe_insert("scale", frame=fade)
    for m in fh["mats"]:
        H.set_alpha(m, [(1, 1.0), (int(n * 0.35), 1.0), (fade, 0.0)])
    H.key_energy(fh["light"], [(1, 180), (int(n * 0.35), 180), (fade, 0)], "LINEAR")
    H.key_emission(fh["win"], [(1, 1.2), (int(n * 0.35), 1.2), (fade, 0.0)], "LINEAR")
    H.key_emission(fh["bulb"].active_material, [(1, 15), (int(n * 0.35), 15), (fade, 0.0)], "LINEAR")
    for i, p in enumerate(((-1.2, 9.0, 1.7), (0.6, 11.5, 1.5), (1.8, 8.0, 1.9))):
        H.orb(f"orb{i}", p, n, seed=i + 2, amp=0.5, energy=6)
    p0, p1, tg = (0.0, -2.0, 1.6), (0.0, 5.0, 1.6), (0.6, 34.0, 1.8)
    c = H.cam(p0, tg, lens=35)
    H.cam_move(c, [(1, p0, tg), (n, p1, tg)], ease=False)
    L.cam_light(c, energy=6, color=(0.6, 0.68, 0.9))
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S08 darkroom
def S08(L, n):
    _world(L, (0.0, 0.0, 0.0), vol_end=10)
    wall = L.mat_principled("dr_wall", (0.08, 0.075, 0.07), rough=0.9)
    H.box_mesh("dr_room", [(0, 0, -0.02, 1.1, 1.35, 0.02), (0, 1.3, 1.25, 1.1, 0.05, 1.25), (-1.05, 0, 1.25, 0.05, 1.35, 1.25),
                           (1.05, 0, 1.25, 0.05, 1.35, 1.25), (0, 0, 2.52, 1.1, 1.35, 0.02)], wall)
    H.box_mesh("dr_bench", [(0, 0.85, 0.85, 1.0, 0.4, 0.04)], L.mat_principled("dr_bench_m", (0.05, 0.05, 0.05), rough=0.6))
    trays = []
    for i, x in enumerate((-0.72, 0.0, 0.72)):
        t = H.darkroom_tray(loc=(x, 0.82, 0.89), img=None, n=n, reveal=(1, n) if i == 1 else (1, 2))
        trays.append(t)
    sl = L.point((0.6, 1.1, 2.0), energy=70, color=(1.0, 0.04, 0.02), radius=0.05, name="safelight")
    lamp = L.prim("cube", loc=(0.6, 1.22, 2.05), scale=(0.12, 0.04, 0.08))
    L.assign(lamp, L.mat_emission("safelamp", (1.0, 0.05, 0.02), 6.0))
    p0, p1 = (-0.7, -0.15, 1.55), (-0.15, -0.1, 1.52)
    c = H.cam(p0, (-0.35, 0.82, 0.88), lens=50)
    H.cam_move(c, [(1, p0, (-0.35, 0.82, 0.88)), (n, p1, (0.1, 0.82, 0.88))], ease=False)
    L.dof(c, distance=1.05, fstop=2.0)
    L.cam_light(c, energy=1.5, color=(1.0, 0.1, 0.05))
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S10 generic list spread
def S10(L, n):
    _world(L, (0.01, 0.01, 0.012))
    paper = L.mat_noise_surface("spread", (0.62, 0.58, 0.5), (0.74, 0.7, 0.62), scale=40, bump=0.05, voronoi=False, rough=0.9)
    H.box_mesh("spread", [(0, 0.01, 0, 1.1, 0.005, 1.6)], paper)
    H.box_mesh("fold", [(0, 0.004, 0, 0.004, 0.002, 1.6)], L.mat_principled("fold_m", (0.3, 0.28, 0.24), rough=0.9))
    ink = L.mat_principled("sp_ink", (0.05, 0.045, 0.04), rough=0.7)
    H.box_mesh("headbars", [(0, -0.002, 1.38, 0.8, 0.002, 0.05), (-0.2, -0.002, 1.25, 0.6, 0.002, 0.02)], ink)
    grey = L.mat_principled("frame_grey", (0.25, 0.25, 0.25), rough=0.8)
    hi = L.mat_principled("frame_hi", (0.25, 0.25, 0.25), rough=0.8, emit=(0.9, 0.85, 0.7), emit_strength=0.0)
    cells = {}
    k = 1
    for row in range(3):
        for col in range(2):
            x, z = -0.5 + col * 1.0, 0.75 - row * 0.85
            cells[k] = (x, z)
            H.box_mesh(f"ph{k}", [(x, -0.003, z, 0.4, 0.002, 0.28)], hi if k == 5 else grey)
            t = L.text3d(f"#{k}", loc=(x - 0.36, -0.006, z - 0.38), size=0.07, extrude=0.0, mat=ink, align="LEFT", name=f"num{k}")
            if k != 5:
                H.box_mesh(f"cap{k}", [(x + 0.05, -0.004, z - 0.36, 0.25, 0.002, 0.012)], ink)
            k += 1
    x5, z5 = cells[5]
    H.key_principled(hi, "Emission Strength", [(1, 0.0), (int(n * 0.25), 0.0), (int(n * 0.35), 1.2)])
    cap = L.text3d("Bachelor's Grove, 1991", loc=(x5 - 0.24, -0.006, z5 - 0.38), size=0.05, extrude=0.0, mat=ink, align="LEFT", name="cap5")
    occ = H.box_mesh("occluder", [(0.0, 0, 0, 0.36, 0.002, 0.035)], paper)
    occ.location = (x5 + 0.16, -0.012, z5 - 0.365)
    occ.keyframe_insert("location", frame=int(n * 0.35))
    occ.location = (x5 + 0.16 + 0.75, -0.012, z5 - 0.365)
    occ.keyframe_insert("location", frame=int(n * 0.8))
    L.linear_fcurves(occ)
    lamp = L.spot((-1.4, -2.4, 2.4), (0, 0, 0), energy=500, size_deg=60, blend=0.8, color=(1.0, 0.82, 0.6), name="warm")
    H.aim(lamp, (-1.4, -2.4, 2.4), (0, 0, 0))
    p0, t0 = (0.0, -3.6, 0.15), (0.0, 0.0, 0.1)
    p1, t1 = (x5 * 0.7, -2.0, z5 + 0.05), (x5, 0.0, z5)
    c = H.cam(p0, t0, lens=50)
    H.cam_move(c, [(1, p0, t0), (int(n * 0.25), p0, t0), (n, p1, t1)])
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S11 evidence board: double exposure
def S11(L, n):
    _world(L, (0.01, 0.01, 0.012))
    H.box_mesh("bwall", [(0, 0.2, 0, 4, 0.05, 4)], L.mat_principled("bw", (0.05, 0.05, 0.055), rough=0.9))
    H.evidence_board("board", 2.4, 4.0)
    H.pinned_card("c_hdr", (0.0, -0.01, 1.32), 1.5, 0.36, [], header="WHAT SCEPTICS SAY", size=0.1, font_size_header=0.125,
                  color=(0.86, 0.83, 0.72), rot=math.radians(-1.5))

    def sheet(name, col, alpha):
        m = L.mat_principled(name + "_m", col, rough=0.8, emit=col, emit_strength=0.25, alpha=alpha)
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
        return m
    ink = L.mat_principled("s_ink", (0.1, 0.1, 0.12), rough=0.7)
    # A: empty stone outline
    a = H.empty("sheetA", (0, 0, 0.25))
    H.box_mesh("sheetA_p", [(0, 0, 0, 0.42, 0.002, 0.55)], sheet("sheetA", (0.75, 0.78, 0.85), 0.55), parent=a)
    H.box_mesh("sheetA_stone", [(0, -0.004, -0.2, 0.25, 0.002, 0.008), (0, -0.004, 0.05, 0.25, 0.002, 0.008),
                                (-0.25, -0.004, -0.075, 0.008, 0.002, 0.13), (0.25, -0.004, -0.075, 0.008, 0.002, 0.13),
                                (0, -0.004, -0.33, 0.4, 0.002, 0.006)], ink, parent=a)
    # B: a vague pale seated shape (generic, not the photographed figure)
    b = H.empty("sheetB", (0, -0.006, 0.25))
    H.box_mesh("sheetB_p", [(0, 0, 0, 0.42, 0.002, 0.55)], sheet("sheetB", (0.85, 0.82, 0.78), 0.4), parent=b)
    pale = sheet("pale", (0.95, 0.95, 0.92), 0.6)
    hd = L.prim("sphere", loc=(0.02, -0.006, 0.3), segments=12, ring_count=8, radius=0.06)
    bd = L.prim("sphere", loc=(0.0, -0.006, 0.12), segments=12, ring_count=8, radius=1)
    bd.scale = (0.13, 0.01, 0.16)
    lp = L.prim("sphere", loc=(0.04, -0.006, -0.06), segments=12, ring_count=8, radius=1)
    lp.scale = (0.2, 0.01, 0.07)
    for o in (hd, bd, lp):
        L.assign(o, pale)
        o.parent = b
    meet = int(n * 0.55)
    for o, x0 in ((a, -0.62), (b, 0.62)):
        o.location.x = x0
        o.keyframe_insert("location", frame=1)
        o.keyframe_insert("location", frame=int(n * 0.12))
        o.location.x = 0.0
        o.keyframe_insert("location", frame=meet)
    lamp = L.spot((-1.6, -2.2, 2.6), (0, 0, 0), energy=900, size_deg=60, blend=0.8, color=(1.0, 0.78, 0.5), name="desklamp")
    H.aim(lamp, (-1.6, -2.2, 2.6), (0.0, 0, 0.5))
    c = H.cam((0.0, -4.6, 0.75), (0.0, 0, 0.7), lens=50)
    H.cam_move(c, [(1, (0.0, -4.6, 0.75), (0.0, 0, 0.7)), (n, (0.0, -4.0, 0.72), (0.0, 0, 0.66))], ease=False)
    H.crisp_shadows()
    L.bake_static()
