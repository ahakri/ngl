"""CAVE-05 — Xisco Gràcia, Sa Piqueta air pocket (Mallorca, 2017). Shot builders (def Sxx(L, n)).
Shared builders: PIPELINE/blender/lib_cave.py (air_bell, ledge, glow_disc, gauge, drill_rig, beacon, pose_edge_sit added)."""
import sys, os, math, random
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "PIPELINE", "blender"))
import importlib
import lib_cave as C
importlib.reload(C)
import bpy
from mathutils import Vector, Matrix, Euler

GRACIA = C.YELLOW
MASCARO = C.ORANGE
RESCUE = (0.92, 0.92, 0.9)
CYAN_RIM = (0.35, 0.85, 1.0)
MURK = (0.45, 0.38, 0.22)
TEAL = (0.3, 0.62, 0.6)


# ============================================================================ helpers

def _track(obj, pos, name="tgt"):
    """TRACK_TO obj (a light) at a new empty at pos. Returns the empty (keyframe its location)."""
    t = bpy.data.objects.new(name, None)
    C.L.link(t)
    t.location = pos
    con = obj.constraints.new("TRACK_TO")
    con.target = t
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    return t


def _diver(name, fins, energy=1800, beam_len=3.5, beam=0.4, deg=22, tanks="doubles"):
    return C.diver(name, fins=fins, tanks=tanks, rebreather=False, light_energy=energy, beam_len=beam_len,
                   beam_strength=beam, beam_deg=deg)


def _upright(d, loc, face_deg, tilt=0.3, helmet=(0.85, 0.68, 0.08)):
    """Hover upright: head up, belly toward heading face_deg (0 = +Y, 90 = -X, -90 = +X). Arms forward-down.
    Adds a helmet + belly-facing mask (lib upright_head_kit)."""
    C.upright_head_kit(d, helmet=helmet)
    r = d["root"]
    r.location = loc
    r.rotation_euler = (math.pi / 2 - tilt, 0, math.radians(face_deg))
    for tag, sg in (("L", -1), ("R", 1)):
        d[f"shoulder{tag}"].rotation_euler = (-1.25, 0, sg * 0.3)
        d[f"knee{tag}"].rotation_euler = (0.35, 0, 0)
    return r


def _passage(L, n, density=0.08, color=MURK, absorption=(0.15, 0.22, 0.45), seed=5, vol=True, half_w=2.0):
    C.world_black((0.0, 0.002, 0.003))
    C.render_quality(vol_end=18, vol_tile="8", vol_samples=24)
    pas, info = C.passage(length=30, y0=-8, half_w=half_w, half_h=1.5, zc=0.0, seed=seed, rough=0.12, floor_flat=0.3,
                          x_fn=lambda y: 0.4 * math.sin(y * 0.15),
                          mat=C.rock_mat("pas", (0.03, 0.028, 0.022), (0.27, 0.24, 0.19), scale=1.2),
                          disp=(0.25, 0.07))
    C.floor(size=(2 * half_w - 0.4, 30), center=(0, 7, -0.98), strength=0.12, name="siltfloor")
    w = None
    if vol:
        w = C.water(center=(0, 7, 0), size=(2 * half_w + 0.4, 30, 3.2), color=color, density=density, absorption=absorption,
                    name="uw")
    return w


def _vol_node(w):
    return [nd for nd in w.active_material.node_tree.nodes if nd.type == "PRINCIPLED_VOLUME"][0]


def _silt(n, center, size, count=1600, seed=4, vel=(0.02, 0.0, 0.02), color=(0.8, 0.72, 0.55)):
    s = C.cloud(center, size, count=int(count * 0.7), radius=0.0025, color=color, emit=0.035, seed=seed)
    C.drift(s, n, vel)
    return s


# ============================================================================ S01 cold open: two divers, one cut line

def S01(L, n):
    _passage(L, n, density=0.06)
    a = _diver("gracia", GRACIA, energy=750, beam_len=3.0, beam=0.2)
    b = _diver("mascaro", MASCARO, energy=750, beam_len=3.0, beam=0.2)
    _upright(a, (-0.82, 2.0, -0.05), -90, tilt=0.35, helmet=(0.85, 0.68, 0.08))
    _upright(b, (0.82, 2.15, -0.1), 90, tilt=0.4, helmet=(0.9, 0.45, 0.1))
    ta = _track(a["torch"], (0.6, 2.5, -0.7), "ta")
    tb = _track(b["torch"], (-0.6, 1.6, -0.6), "tb")
    C.key_loc(ta, [(1, (0.6, 2.5, -0.15)), (n, (0.45, 2.3, -0.05))])
    C.key_loc(tb, [(1, (-0.5, 1.6, -0.2)), (n, (-0.65, 1.8, -0.1))])
    for d, ph in ((a, 0.0), (b, 1.3)):
        r = d["root"]
        base = Vector(r.location)
        C.key_loc(r, [(1, tuple(base)), (n // 2, tuple(base + Vector((0, 0, 0.05 * math.sin(ph + 1))))),
                      (n, tuple(base + Vector((0, 0, -0.04))))])
        L.anim_swim(d, n, kick_rate=0.45, amp=0.12)
    # gauge held in front of Gràcia's chest, tapped by his right hand
    g = C.gauge("g1", radius=0.055)
    g["root"].location = (-0.42, 1.78, 0.12)
    g["root"].rotation_euler = (0.15, 0, -0.35)
    g["pivot"].rotation_euler = (0, -1.75, 0)
    glove = L.prim("sphere", loc=(-0.36, 1.72, 0.25), segments=10, ring_count=6, radius=1.0, name="tapglove")
    glove.scale = (0.045, 0.06, 0.035)
    L.assign(glove, L.mat_principled("glove", (0.03, 0.03, 0.035), rough=0.6))
    keys = []
    for k, f in enumerate(range(1, n + 1, 6)):
        keys.append((f, (-0.36, 1.72, 0.2 + (0.05 if k % 2 == 0 else 0.0))))
    C.key_loc(glove, keys)
    # two cut ends of the guideline drift slack between them
    lm = L.mat_principled("gl_m", (0.95, 0.93, 0.85), rough=0.4, emit=(0.95, 0.93, 0.85), emit_strength=0.9)
    for name, tie, pts, sg in (("lineR", (1.7, 4.8, -0.95), [(0, 0, 0), (-0.5, -1.2, 0.25), (-1.1, -1.9, 0.45),
                                                              (-1.55, -2.0, 0.55), (-1.62, -1.75, 0.5)], 1),
                               ("lineL", (-1.6, -2.5, -0.95), [(0, 0, 0), (0.6, 2.2, 0.15), (1.2, 3.6, 0.25),
                                                               (1.45, 4.3, 0.3), (1.5, 4.6, 0.22)], -1)):
        o = C.curve(pts, thickness=0.006, mat=lm, name=name, smooth_pts=True)
        o.location = tie
        for f, rz, rx in ((1, 0.0, 0.0), (n // 2, sg * 0.07, 0.05), (n, sg * 0.12, -0.03)):
            o.rotation_euler = (rx, 0, rz)
            o.keyframe_insert("rotation_euler", frame=f)
    C.rim_light((0, 2.1, 0.2), (0.3, 3.5, 1.4), energy=1800, color=CYAN_RIM, size_deg=60, name="backrim")
    C.rim_light((0, 2.0, 0.0), (0.0, 0.2, 2.2), energy=500, color=(0.9, 0.8, 0.6), size_deg=70, name="topfill")
    _silt(n, (0, 2.6, 0.0), (3.2, 3.6, 2.2), count=1800, seed=3)
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.05, -1.55, 0.28), (0.0, 2.0, -0.05)), (n, (0.0, -0.95, 0.22), (-0.05, 2.0, -0.05))],
              shake=0.02, rot_shake=0.004, rate=0.6, fn=lambda x: x)
    C.cam_fill(cam, energy=220, color=(0.85, 0.75, 0.55))
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 4.0
    cam.data.dof.focus_distance = 3.3
    cam.data.dof.keyframe_insert("focus_distance", frame=1)
    cam.data.dof.keyframe_insert("focus_distance", frame=int(n * 0.45))
    cam.data.dof.focus_distance = 4.4
    cam.data.dof.keyframe_insert("focus_distance", frame=n)
    L.bake_static()


# ============================================================================ S03 map backdrop (defocused passage)

def S03(L, n):
    _passage(L, n, density=0.06, color=(0.4, 0.42, 0.3))
    tp = C.dive_torch((0.3, 6.0, 0.1), (-0.8, 12.0, -0.5), energy=1500, size_deg=26, beam_len=4, beam_strength=0.4)
    C.line([(-1.2, -6, -0.85), (-0.4, 4, -0.7), (0.6, 14, -0.9)], thickness=0.006, emit=0.8, name="guideline")
    _silt(n, (0, 2.5, 0), (3.5, 6, 2.4), count=2200, seed=8, vel=(0.05, 0.0, 0.03))
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.2, -1.5, 0.2), (0.0, 6.0, -0.1)), (n, (0.1, -0.6, 0.15), (0.0, 6.0, -0.15))],
              shake=0.01, rot_shake=0.002)
    C.cam_fill(cam, energy=40, color=(0.7, 0.8, 0.7))
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 1.2
    cam.data.dof.focus_distance = 1.2
    L.bake_static()


# ============================================================================ S04 survey dive (clear teal)

def S04(L, n):
    _passage(L, n, density=0.03, color=TEAL, absorption=(0.08, 0.2, 0.25), seed=7, half_w=3.2)
    y0, y1 = -0.4, 1.9
    a = _diver("gracia", GRACIA, energy=1500, beam_len=3.5, beam=0.35, tanks="doubles")
    b = _diver("mascaro", MASCARO, energy=1500, beam_len=3.5, beam=0.35, tanks="doubles")
    ra, rb = a["root"], b["root"]
    C.key_loc(ra, [(1, (0.1, y0, 0.45)), (n, (0.1, y1, 0.5))])
    C.key_loc(rb, [(1, (0.8, y0 - 0.5, -0.32)), (n, (0.8, y1 - 0.5, -0.3))])
    for r in (ra, rb):
        L.linear_fcurves(r)
        r.rotation_euler = (0.08, 0, 0)
    L.anim_swim(a, n, kick_rate=0.7, amp=0.22)
    L.anim_swim(b, n, kick_rate=0.75, amp=0.22, start=3)
    for d, nm in ((a, "ta"), (b, "tb")):  # torch targets ride with each diver (root space: ahead and below)
        t = _track(d["torch"], (0, 0, 0), nm)
        t.parent = d["root"]
        t.location = (0.0, 3.0, -0.9)
    # slate in Gràcia's right hand, reel in Mascaró's left hand
    a["shoulderR"].rotation_euler = (0.45, 0, 0.55)
    slate = L.prim("cube", loc=(0, 0.44, 0.0), name="slate")
    slate.scale = (0.11, 0.08, 0.008)
    slate.rotation_euler = (0.6, 0, 0)
    L.assign(slate, L.mat_principled("slate_m", (0.9, 0.9, 0.86), rough=0.5, emit=(0.9, 0.9, 0.86),
                                     emit_strength=0.4))
    slate.parent = a["shoulderR"]
    pencil = L.prim("cyl", loc=(0.04, 0.42, 0.03), vertices=6, radius=0.006, depth=0.12, rot=(0, 0.9, 0),
                    name="pencil")
    L.assign(pencil, L.mat_principled("pencil_m", (0.1, 0.1, 0.1), rough=0.5))
    pencil.parent = a["shoulderL"]
    for f in range(1, n + 1, 4):
        a["shoulderL"].rotation_euler = (0.3, 0, -0.55 - 0.08 * math.sin(f * 0.9))
        a["shoulderL"].keyframe_insert("rotation_euler", frame=f)
    reel = L.prim("cyl", loc=(0, 0.46, 0.0), vertices=16, radius=0.06, depth=0.04, rot=(0, math.pi / 2, 0),
                  name="reel")
    L.assign(reel, L.mat_principled("reel_m", (0.95, 0.6, 0.08), rough=0.4))
    reel.parent = b["shoulderL"]
    b["shoulderL"].rotation_euler = (-0.25, 0, -0.2)
    # survey line laid from the reel back along the floor (grows with the reel)
    lm = L.mat_principled("sl_m", (0.95, 0.95, 0.9), rough=0.4, emit=(0.95, 0.95, 0.9), emit_strength=1.0)
    yE = y1 - 0.5 + 0.95
    pts = [(0.85, -8.0, -0.9), (0.8, -3.0, -0.75), (0.77, y0 - 0.5 + 0.95, -0.42), (0.77, yE, -0.4)]
    ln = C.curve(pts, thickness=0.006, mat=lm, name="surveyline")
    total = sum((Vector(q) - Vector(p)).length for p, q in zip(pts, pts[1:]))
    t0 = sum((Vector(q) - Vector(p)).length for p, q in zip(pts[:3], pts[1:3])) / total
    C.grow_curve(ln, [(1, t0), (n, 1.0)])
    for fc in L._fcurves(ln.data.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    _silt(n, (0, 1.0, 0), (3.2, 6, 2.2), count=1500, seed=5, color=(0.75, 0.85, 0.8))
    L.point((0.0, 1.0, 1.0), energy=30, color=(0.4, 0.85, 0.85), radius=1.0, name="cyanamb")
    C.rim_light((0.1, 0.8, 0.0), (2.2, 1.0, 1.0), energy=500, color=CYAN_RIM, size_deg=55, name="rim")
    cam = C.camera(lens=20)
    C.aim_cam(cam, n, [(1, (-2.3, y0 - 0.25, 0.25), (0.45, y0 - 0.35, -0.35)),
                       (n, (-2.3, y1 - 0.15, 0.27), (0.45, y1 - 0.35, -0.35))],
              shake=0.012, rot_shake=0.003, fn=lambda x: x)
    C.cam_fill(cam, energy=160, color=(0.6, 0.85, 0.85))
    L.bake_static()


# ============================================================================ S05 the line snaps / gauge insert

def S05(L, n):
    cut = 40
    w = _passage(L, n, density=0.035, color=TEAL, absorption=(0.08, 0.2, 0.25), seed=9)
    vn = _vol_node(w)
    snap = 11
    C.key_input(vn.inputs["Density"], [(1, 0.035), (snap, 0.04), (cut, 0.11), (n, 0.13)])
    C.key_input(vn.inputs["Color"], [(1, (*TEAL, 1)), (snap, (*TEAL, 1)), (cut - 6, (*MURK, 1)), (n, (*MURK, 1))])
    # sharp rock edge with the taut line over it
    rk = L.prim("ico", loc=(0.0, 2.0, -0.78), subdivisions=2, radius=0.5, name="edge")
    rk.scale = (1.4, 0.55, 0.65)
    rk.rotation_euler = (0, 0.12, 0.3)
    L.add_displace(rk, strength=0.12, scale=0.25, name="edge_d")
    L.assign(rk, C.rock_mat("edge_m", (0.02, 0.018, 0.015), (0.16, 0.14, 0.11), scale=4.0))
    apex = Vector((0.03, 2.0, -0.47))
    lm = L.mat_principled("gl_m", (0.95, 0.93, 0.85), rough=0.4, emit=(0.95, 0.93, 0.85), emit_strength=1.1)
    left_tie, right_tie = Vector((-2.0, 3.0, -0.2)), Vector((1.8, 1.4, -0.95))
    lh = C.curve([(0, 0, 0), tuple(apex - left_tie)], thickness=0.006, mat=lm, name="lineL")
    lh.location = left_tie
    rh = C.curve([(0, 0, 0), tuple((apex - right_tie) * 0.55 + Vector((0, 0, 0.02))), tuple(apex - right_tie)],
                 thickness=0.006, mat=lm, name="lineR", smooth_pts=True)
    rh.location = right_tie
    # whip: the right half springs away and down, the left half sags
    for f, rot in ((1, (0, 0, 0)), (snap, (0, 0, 0)), (snap + 4, (0.25, 0.7, -0.5)), (snap + 9, (0.1, 1.05, -0.35)),
                   (n, (0.15, 1.2, -0.45))):
        rh.rotation_euler = rot
        rh.keyframe_insert("rotation_euler", frame=f)
    for f, rot in ((1, (0, 0, 0)), (snap, (0, 0, 0)), (snap + 6, (-0.25, 0.0, 0.08)), (n, (-0.32, 0.0, 0.12))):
        lh.rotation_euler = rot
        lh.keyframe_insert("rotation_euler", frame=f)
    flash, _, fem = C.glow_dot(tuple(apex), (1.0, 0.95, 0.85), r=0.02, halo=5, strength=0.0, name="snapflash")
    C.key_input(flash.active_material.node_tree.nodes["Emission"].inputs[1], [(1, 0), (snap - 1, 0), (snap, 14),
                                                                              (snap + 5, 0)])
    C.key_input(fem.inputs[1], [(1, 0), (snap - 1, 0), (snap, 5), (snap + 5, 0)])
    plume, dsock, _ = C.noisy_volume((0.2, 2.2, -0.6), (2.6, 2.4, 1.4), color=(0.6, 0.48, 0.3), density=0.0,
                                     scale=1.8, name="siltcloud")
    C.key_input(dsock, [(1, 0.0), (snap, 0.0), (snap + 10, 2.5), (cut, 6.0)])
    C.key_scale(plume, [(1, 0.6), (snap, 0.6), (cut, 1.5)])
    C.key_loc(plume, [(1, (0.2, 2.2, -0.75)), (cut, (0.0, 1.6, -0.3))])
    _silt(n, (0, 1.8, -0.2), (3.0, 3.0, 1.8), count=1400, seed=11, vel=(0.05, -0.08, 0.08))
    # Gràcia's torch on the edge (the diver himself is just off frame)
    tp = C.dive_torch((-0.9, 0.3, 0.6), tuple(apex), energy=700, size_deg=26, beam_len=2.2, beam_strength=0.35)
    # gauge insert set, a few metres back down the passage (same water)
    gz = Vector((0.6, -3.0, 0.15))
    g = C.gauge("g2", radius=0.06)
    g["root"].location = gz
    g["root"].rotation_euler = (0.1, 0, 0.12)
    for f, a in ((1, 1.0), (cut + 1, 1.0), (cut + 8, 1.25), (n - 6, 1.85), (n, 1.9)):
        g["pivot"].rotation_euler = (0, -a, 0)
        g["pivot"].keyframe_insert("rotation_euler", frame=f)
    gt = L.spot((gz.x - 0.5, gz.y - 0.5, gz.z + 0.5), (0, 0, 0), energy=60, size_deg=40, blend=0.8, color=C.TORCH,
                name="gaugekey")
    gt.rotation_mode = "QUATERNION"
    gt.rotation_quaternion = (gz - Vector(gt.location)).to_track_quat("-Z", "Y")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (0.35, -0.9, 0.05), tuple(apex + Vector((0, 0, -0.08)))),
                       (cut, (0.12, 0.85, -0.25), tuple(apex + Vector((0.1, 0, -0.08)))),
                       (cut + 1, tuple(gz + Vector((0.03, -0.62, 0.06))), tuple(gz + Vector((0, 0, -0.1)))),
                       (n, tuple(gz + Vector((0.02, -0.52, 0.05))), tuple(gz + Vector((0, 0, -0.085))))],
              shake=0.012, rot_shake=0.004, fn=lambda x: x, shake_keys=[(1, 1.0), (snap, 2.5), (cut, 1.0), (n, 0.5)])
    cam.data.lens = 35
    cam.data.keyframe_insert("lens", frame=cut)
    cam.data.lens = 50
    cam.data.keyframe_insert("lens", frame=cut + 1)
    C.constant_keys(cam.data)
    C.cam_fill(cam, energy=140, color=(0.8, 0.8, 0.7))
    L.bake_static()


# ============================================================================ S06 the handover

def S06(L, n):
    _passage(L, n, density=0.075, color=MURK, seed=13)
    a = _diver("gracia", GRACIA, energy=700, beam_len=2.5, beam=0.3)
    b = _diver("mascaro", MASCARO, energy=1200, beam_len=4.0, beam=0.35)
    _upright(a, (-0.35, 0.0, -0.1), 0, tilt=0.35)
    L.spot((0.0, 0.7, 2.0), (0, 0, 0), energy=500, size_deg=60, blend=0.8, color=(0.9, 0.85, 0.75), name="handtop")
    bloc, brot = Vector((0.12, 1.3, 0.0)), (math.pi / 2 - 0.35, 0, math.pi)
    rb = _upright(b, tuple(bloc), 180, tilt=0.35, helmet=(0.9, 0.45, 0.1))
    ta = _track(a["torch"], (0.1, 1.0, -0.3), "ta")
    tb = _track(b["torch"], (0.0, 0.3, -0.5), "tb")
    turn0, turn1, gone = 36, 52, 92
    C.key_loc(tb, [(1, (0.0, 0.3, -0.5)), (turn0, (0.0, 0.4, -0.5)), (turn1, (0.0, 20.0, 0.0)), (n, (0.0, 30.0, 0.0))])
    C.key_loc(ta, [(1, (0.1, 1.0, -0.3)), (turn1, (0.1, 1.4, -0.3)), (n, (0.0, 8.0, -0.2))])
    # Mascaró turns away and swims off down the passage
    for f, rot in ((1, brot), (turn0, brot), (turn1, (0.15, 0, 0.0)), (n, (0.1, 0, 0.0))):
        rb.rotation_euler = rot
        rb.keyframe_insert("rotation_euler", frame=f)
    C.key_loc(rb, [(1, tuple(bloc)), (turn0, tuple(bloc)), (turn1, (0.1, 2.2, 0.05)), (gone, (0.0, 11.0, 0.1)),
                   (n, (0.0, 12.5, 0.1))])
    L.anim_swim(b, n, kick_rate=0.9, amp=0.28, start=turn0)
    L.anim_swim(a, n, kick_rate=0.4, amp=0.1)
    # his torch shrinks to a dot, then is gone
    C.key_energy(b["torch"], [(1, 1200), (gone - 14, 1200), (gone, 0)])
    if b.get("beam_sock") is not None:
        C.key_input(b["beam_sock"], [(1, 0.45), (gone - 14, 0.45), (gone, 0.0)])
    dot, _, dem = C.glow_dot((0, 0, 0), C.TORCH, r=0.03, halo=6, strength=10, name="bdot")
    dot.parent = rb
    dot.location = (0.0, 0.62, 0.32)
    core_em = dot.active_material.node_tree.nodes["Emission"].inputs[1]
    C.key_input(core_em, [(1, 0.0), (turn0, 0.0), (turn1, 6.0), (gone - 10, 6.0), (gone, 0.0)])
    C.key_input(dem.inputs[1], [(1, 0.0), (turn0, 0.0), (turn1, 1.8), (gone - 10, 1.8), (gone, 0.0)])
    # the stage cylinder: from Gràcia's side into Mascaró's hands, then it leaves with him (child-of switch)
    tk = C.tank((-0.32, 0.12, -0.15), rot=(0.2, 0, 0.1), length=0.62, r=0.075, band=(1.0, 0.78, 0.1), name="stage")
    hand_f = 30
    hold = Vector((0.1, 0.92, 0.0))
    C.key_loc(tk, [(1, (-0.32, 0.12, -0.15)), (8, (-0.3, 0.2, -0.1)), (hand_f, tuple(hold))])
    for f, rot in ((1, (0.2, 0, 0.1)), (hand_f, (0.05, 0, 1.4))):
        tk.rotation_euler = rot
        tk.keyframe_insert("rotation_euler", frame=f)
    co = tk.constraints.new("CHILD_OF")
    co.target = rb
    co.inverse_matrix = Matrix.LocRotScale(bloc, Euler(brot).to_quaternion(), Vector((1, 1, 1))).inverted()
    co.influence = 0.0
    co.keyframe_insert("influence", frame=turn0 - 1)
    co.influence = 1.0
    co.keyframe_insert("influence", frame=turn0)
    for fc in L._fcurves(tk.animation_data.action):
        if fc.data_path.startswith("constraints"):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    # Mascaró's hands come forward to take it
    for f, ang in ((1, -1.25), (hand_f - 8, -1.25), (hand_f, -1.55), (turn0, -1.55)):
        for tag, sg in (("L", -1), ("R", 1)):
            b[f"shoulder{tag}"].rotation_euler = (ang, 0, sg * 0.15)
            b[f"shoulder{tag}"].keyframe_insert("rotation_euler", frame=f)
    C.rim_light((0.1, 1.2, 0.2), (-0.6, 2.2, 1.6), energy=1500, color=CYAN_RIM, size_deg=55, name="rim")
    _silt(n, (0, 1.5, 0), (3.0, 5.0, 2.2), count=1600, seed=6)
    C.bubble_trail(lambda f: Vector(rb.location) + Vector((0, 0, 0.6)), n, count=12, rise=0.6, size=0.014,
                   life=(14, 26), seed=8)
    cam = C.camera(lens=40)
    C.aim_cam(cam, n, [(1, (0.5, -1.95, 0.6), (0.0, 1.3, -0.05)), (turn1, (0.48, -1.9, 0.58), (0.0, 2.5, -0.05)),
                       (n, (0.45, -1.85, 0.55), (0.0, 6.0, 0.0))], shake=0.012, rot_shake=0.003)
    C.cam_fill(cam, energy=200, color=(0.85, 0.75, 0.55))
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 4.0
    for f, d in ((1, 3.3), (turn1, 4.2), (gone, 10.0)):
        cam.data.dof.focus_distance = d
        cam.data.dof.keyframe_insert("focus_distance", frame=f)
    L.bake_static()


# ============================================================================ S11 rescuers in zero visibility

def S11(L, n):
    w = _passage(L, n, density=0.55, color=(0.72, 0.5, 0.26), absorption=(0.04, 0.08, 0.16), seed=17)
    r1 = _diver("res1", (0.55, 0.56, 0.56), energy=2600, beam_len=1.0, beam=0.8, deg=26)
    r2 = _diver("res2", (0.55, 0.56, 0.56), energy=2600, beam_len=1.0, beam=0.8, deg=26)
    _upright(r1, (0.28, 0.85, -0.12), 0, tilt=0.6, helmet=(0.85, 0.85, 0.82))
    rr2 = r2["root"]
    rr2.rotation_euler = (0.1, 0, 0.05)
    C.key_loc(rr2, [(1, (-0.45, 1.9, -0.25)), (n, (-0.45, 2.6, -0.22))])
    L.anim_swim(r2, n, kick_rate=0.7, amp=0.25)
    L.anim_swim(r1, n, kick_rate=0.4, amp=0.12)
    _track(r1["torch"], (0.3, 4.0, -0.3), "t1")
    _track(r2["torch"], (-0.4, 6.0, -0.3), "t2")
    # hand up to the mask, then reaching forward into the murk
    sh = r1["shoulderR"]
    for f, rot in ((1, (-1.25, 0, 0.3)), (14, (-0.4, 0, 0.55)), (int(n * 0.45), (-0.3, 0, 0.5)),
                   (int(n * 0.75), (-1.5, 0, 0.15)), (n, (-1.55, 0, 0.12))):
        sh.rotation_euler = rot
        sh.keyframe_insert("rotation_euler", frame=f)
    C.rim_light((0.28, 0.9, 0.3), (0.6, 1.8, 1.2), energy=900, color=(1.0, 0.8, 0.5), size_deg=40, name="rim")
    for y in (1.6, 2.6):
        L.point((0.1, y, 0.0), energy=60, color=(1.0, 0.8, 0.55), radius=0.3, name="murkglow")
    _silt(n, (0, 1.5, 0), (3.0, 4.0, 2.2), count=1500, seed=12, color=(0.85, 0.7, 0.5))
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (0.15, -0.75, 0.95), (0.1, 2.6, -0.35)), (n, (0.15, -0.5, 0.9), (0.1, 2.6, -0.35))],
              shake=0.015, rot_shake=0.004)
    C.cam_fill(cam, energy=160, color=(0.9, 0.75, 0.55))
    L.bake_static()


# ============================================================================ air bell (S02, S08, S09, S12-S15, S17)

LEDGE = (-1.7, 1.2, 0.32)
SEAT = (-1.12, 0.78, 0.32)
SEAT_RZ = math.radians(-128)
HEAD0 = (0.0, 0.4)


def _bell(L, n, haze=0.012, bump=0.12, glow_at=None, drips=True, dome_rough=0.18, amb=6.0):
    C.world_black((0.0, 0.001, 0.002))
    C.render_quality(vol_end=12, vol_tile="8", vol_samples=24)
    dome = C.air_bell(R=(3.0, 2.6), H=2.1, below=1.2, seed=5, rough=dome_rough)
    C.ledge(LEDGE, size=(1.7, 1.4, 0.9))
    rnd = random.Random(3)
    pts = []
    for i in range(16):
        a = rnd.uniform(0, 2 * math.pi)
        pts.append((math.cos(a) * 2.45, math.sin(a) * 2.1, -0.15))
    C.rocks(pts, count=16, size=(0.2, 0.5), seed=4, sink=0.5)
    ws, sock = C.water_surface(size=(7, 6), center=(0, 0, 0), n=n, flow=(0.0, 0.03), wave_scale=1.3, bump=bump,
                               glow_at=glow_at, glow_radius=0.7, rough=0.22)
    bsdf = ws.active_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Specular IOR Level"].default_value = 0.12
    if amb:
        pl = L.point((0.3, -0.2, 1.3), energy=amb, color=(0.55, 0.75, 0.8), radius=1.2, name="domeamb")
        pl.data.specular_factor = 0.2
    ws.visible_shadow = False
    sm = C.rock_mat("stal", (0.03, 0.028, 0.025), (0.28, 0.25, 0.2), scale=2.0)
    for i in range(22):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.6, 2.0)
        x, y = math.cos(a) * r, math.sin(a) * r
        top = 2.1 * math.sqrt(max(0.05, 1 - (x / 3.0) ** 2 - (y / 2.6) ** 2)) * 0.9
        ln = rnd.uniform(0.08, 0.3)
        o = L.prim("cone", loc=(x, y, top - ln / 2), vertices=7, radius1=rnd.uniform(0.02, 0.06), radius2=0.003,
                   depth=ln, rot=(math.pi, 0, 0), name="stal")
        L.assign(o, sm)
    if drips:
        C.drip_rings([(0.7, -0.3, 0.003), (-0.4, -0.8, 0.003), (0.9, 0.9, 0.003), (-0.5, 0.2, 0.003)], n, period=30,
                     seed=3, strength=0.15, rmax=0.4)
    hz = None
    if haze:
        hz = C.water(center=(0, 0, 1.0), size=(6.2, 5.4, 2.1), color=(0.72, 0.74, 0.7), density=haze, anisotropy=0.5,
                     absorption=(0.03, 0.03, 0.03), name="airhaze")
    return {"dome": dome, "ws": ws, "glow": sock, "haze": hz}


def _gracia_seated(L, lamp=500, rim=0.9, mask=True):
    p = C.figure("gracia", height=1.72, base=(0.05, 0.05, 0.055), rim=CYAN_RIM, rim_strength=rim * 0.4)
    C.pose_edge_sit(p)
    p["root"].location = SEAT
    p["root"].rotation_euler = (0, 0, SEAT_RZ)
    p["neck"].rotation_euler = (-0.35, 0, 0)
    s = 1.72 / 1.75
    hm = C.helmet(p["neck"], s, color=(0.85, 0.68, 0.08), lamp_energy=lamp, lamp_deg=38, name="g_hel")
    if mask:
        mk = L.prim("torus", loc=(0, 0.1 * s, 0.26 * s), rot=(math.pi / 2 - 0.5, 0, 0), major_radius=0.075,
                    minor_radius=0.014, name="g_mask")
        mk.scale = (1.0, 0.7, 1.0)
        L.assign(mk, L.mat_principled("g_mask_m", (0.85, 0.68, 0.08), rough=0.4))
        mk.parent = p["neck"]
    # kit on the ledge: a cylinder lying down and his yellow fins
    C.tank((SEAT[0] - 0.5, SEAT[1] + 0.35, SEAT[2] + 0.09), rot=(math.pi / 2, 0, -0.6), length=0.7, r=0.08,
           name="g_tank")
    fm = L.mat_principled("g_fin_m", GRACIA, rough=0.4)
    for k, (dx, dy, rz) in enumerate(((-0.25, -0.35, 0.3), (-0.05, -0.45, 0.55))):
        C.fin_blade((SEAT[0] + dx - 0.3, SEAT[1] + dy + 0.55, SEAT[2] + 0.02 + 0.015 * k), (0, 0, rz), mat=fm,
                    name=f"g_fin{k}")
    return p, hm


def S02(L, n):
    emerge = 30
    b = _bell(L, n, haze=0.018, glow_at=HEAD0)
    C.key_input(b["glow"], [(1, 2.6), (emerge - 8, 3.5), (emerge + 4, 0.4), (n, 0.0)])
    d = _diver("gracia", GRACIA, energy=1800, beam_len=3.5, beam=0.3, deg=30)
    r = _upright(d, (HEAD0[0], HEAD0[1], -1.0), 180, tilt=0.05)
    C.key_loc(r, [(1, (HEAD0[0], HEAD0[1], -1.05)), (emerge - 6, (HEAD0[0], HEAD0[1], -0.62)),
                  (emerge + 6, (HEAD0[0], HEAD0[1], -0.3)), (n, (HEAD0[0], HEAD0[1] + 0.03, -0.33))])
    L.ease_all(r)
    t = _track(d["torch"], (0.0, -0.6, 1.9), "ta")
    C.key_loc(t, [(1, (0.0, -0.4, 2.0)), (emerge + 4, (0.2, -0.9, 1.8)), (n, (0.7, -1.5, 1.4))])
    C.drip_rings([(HEAD0[0] + 0.05, HEAD0[1] - 0.05, 0.004), (HEAD0[0] - 0.1, HEAD0[1] + 0.05, 0.004),
                  (HEAD0[0] + 0.12, HEAD0[1] + 0.1, 0.004)], n, period=18, seed=7, strength=0.7, rmax=0.6,
                 name="boil")
    vap = C.cloud((0.0, 0.2, 0.35), (0.25, 0.25, 0.2), count=110, radius=0.0025, color=(0.9, 0.9, 0.88), emit=0.2,
                  seed=9, name="vapour")
    C.hide_from_frame([vap], f_show=emerge + 4)
    C.drift(vap, n, (0.0, -0.08, 0.12))
    L.point((0.0, 0.1, 0.35), energy=12, color=(1.0, 0.8, 0.55), radius=0.4, name="bounce")
    C.rim_light((0.0, 0.4, 0.2), (0.4, 1.6, 0.9), energy=260, color=CYAN_RIM, size_deg=45, name="headrim")
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.06, -0.62, 0.06), (0.0, 0.4, -0.02)), (emerge, (0.06, -0.8, 0.08), (0.0, 0.4, 0.0)),
                       (n, (0.12, -1.7, 0.3), (0.0, 0.4, 0.05))], shake=0.006, rot_shake=0.002, fn=C.sm)
    C.cam_fill(cam, energy=8, color=(0.8, 0.85, 0.9))
    L.bake_static()


def S17(L, n):
    """Empty air bell; ends on S02's first-frame composition (camera + underwater glow)."""
    b = _bell(L, n, haze=0.018, glow_at=HEAD0)
    C.key_input(b["glow"], [(1, 1.5), (n // 2, 2.2), (n, 2.6)])
    sp = L.spot((HEAD0[0], HEAD0[1], -0.6), (math.pi, 0, 0), energy=0, size_deg=40, blend=0.5, color=C.TORCH, name="uwtorch")
    C.key_energy(sp, [(1, 900), (n, 1400)])
    C.tank((SEAT[0] - 0.5, SEAT[1] + 0.35, SEAT[2] + 0.09), rot=(math.pi / 2, 0, -0.6), length=0.7, r=0.08,
           name="g_tank")
    C.rim_light((-1.2, 1.0, 0.4), (1.6, -1.0, 1.0), energy=180, color=CYAN_RIM, size_deg=50, name="ledgerim")
    L.point((-0.5, 0.2, 1.2), energy=6, color=(0.5, 0.8, 0.9), radius=1.0, name="amb")
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.9, -1.2, 0.55), (-1.0, 0.9, 0.25)), (int(n * 0.55), (0.45, -0.9, 0.2), (-0.4, 0.6, 0.05)),
                       (n - 12, (0.06, -0.62, 0.06), (0.0, 0.4, -0.02)), (n, (0.06, -0.62, 0.06), (0.0, 0.4, -0.02))],
              shake=0.006, rot_shake=0.002, shake_keys=[(1, 1.0), (n - 12, 0.0), (n, 0.0)])
    C.cam_fill(cam, energy=8, color=(0.8, 0.85, 0.9))
    L.bake_static()


def S08(L, n):
    off = 58
    _bell(L, n, haze=0.03, bump=0.06)
    p, hm = _gracia_seated(L, lamp=600)
    lamp = hm["lamp"]
    C.key_energy(lamp, [(1, 600), (40, 260), (off - 1, 200), (off, 0)])
    cone, csock = C.beam_cone(lamp, length=2.0, strength=0.25, name="g_beam")
    C.key_input(csock, [(1, 0.25), (off - 1, 0.12), (off, 0.0)])
    C.key_input(hm["lens_mat"].node_tree.nodes["Emission"].inputs[1], [(1, 6), (off - 1, 4), (off, 0.4)])
    # cup water to the mouth with the right hand
    sh, el = p["shoulderR"], p["elbowR"]
    for f, s_, e_ in ((1, 0.5, 0.6), (14, 0.95, 0.1), (24, 0.95, 0.1), (40, 1.25, 2.3), (52, 1.25, 2.3), (64, 0.6, 0.7),
                      (n, 0.55, 0.6)):
        sh.rotation_euler = (s_, 0, -0.15)
        el.rotation_euler = (e_, 0, 0)
        sh.keyframe_insert("rotation_euler", frame=f)
        el.keyframe_insert("rotation_euler", frame=f)
    for f, a in ((1, -0.45), (24, -0.6), (40, -0.1), (52, -0.15), (64, -0.35), (n, -0.3)):
        p["neck"].rotation_euler = (a, 0, 0)
        p["neck"].keyframe_insert("rotation_euler", frame=f)
    C.drip_rings([(SEAT[0] + 0.45, SEAT[1] - 0.5, 0.004)], n, period=22, seed=11, strength=0.5, rmax=0.3, name="cup")
    # faint cyan on wet rock keeps the frame from going fully black after the click
    C.rim_light((SEAT[0], SEAT[1], 0.8), (-0.9, 1.4, 1.2), energy=220, color=CYAN_RIM, size_deg=60, name="backrim")
    L.area((0.5, -0.5, 1.9), (0, 0, 0), energy=25, size=3, color=(0.35, 0.7, 0.85), name="cyanwash")
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, (1.25, -1.45, 0.5), (SEAT[0], SEAT[1], 0.72)), (n, (0.95, -1.1, 0.48), (SEAT[0], SEAT[1], 0.72))],
              shake=0.006, rot_shake=0.0015)
    C.cam_fill(cam, energy=6, color=(0.7, 0.85, 0.95))
    L.bake_static()


def S09(L, n):
    _bell(L, n, haze=0.035, bump=0.0, drips=True)
    eye = Vector((SEAT[0] + 0.1, SEAT[1] - 0.12, 1.18))
    sp = L.spot(tuple(eye + Vector((0.12, 0.0, -0.08))), (0, 0, 0), energy=0, size_deg=26, blend=0.4, color=C.TORCH,
                name="flash", radius=0.02)
    cone, csock = C.beam_cone(sp, length=3.2, strength=0.3, name="flashbeam")
    tgt = _track(sp, (1.2, -1.0, 0.0), "ft")
    windows = [(10, 19), (34, 43), (58, 67), (82, 91)]
    aims = [(1.4, -0.9, 0.0), (0.6, -1.6, 0.0), (1.8, -0.2, 0.0), (0.9, -0.6, 0.0)]
    ekeys, bkeys = [(1, 0)], [(1, 0.0)]
    for (a, z), aim in zip(windows, aims):
        ekeys += [(a - 1, 0), (a, 1500), (z, 1500), (z + 1, 0)]
        bkeys += [(a - 1, 0.0), (a, 0.3), (z, 0.3), (z + 1, 0.0)]
        tgt.location = aim
        tgt.keyframe_insert("location", frame=a - 1)
        tgt.location = (aim[0] - 0.5, aim[1] + 0.3, 0.0)
        tgt.keyframe_insert("location", frame=z)
    C.key_energy(sp, ekeys)
    C.constant_keys(sp.data)
    C.key_input(csock, bkeys)
    for fc in L._fcurves(bpy.data.materials["flashbeam_m"].node_tree.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"
    # the dark between flashes: a faint cyan wash on the water and rock
    L.area((0.8, -0.6, 1.9), (0, 0, 0), energy=10, size=3.5, color=(0.35, 0.7, 0.85), name="cyanwash")
    C.rim_light((0.8, -0.6, 0.0), (1.2, -1.5, 1.4), energy=40, color=CYAN_RIM, size_deg=70, name="watersheen")
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, tuple(eye), (1.2, -0.9, -0.15)), (n, tuple(eye + Vector((0.02, -0.03, -0.02))),
                                                           (1.1, -0.95, -0.15))], shake=0.004, rot_shake=0.0015)
    L.bake_static()


def S12(L, n):
    b = _bell(L, n, haze=0.0, bump=0.08)
    dome = b["dome"]
    for f in range(1, n + 1, 6):
        s = 1.0 + 0.022 * math.sin(f * 2 * math.pi / 36)
        dome.scale = (s, 2.0 - s, 1.0 + 0.018 * math.sin(f * 2 * math.pi / 36 + 1.3))
        dome.keyframe_insert("scale", frame=f)
    cols = [(0.3, 0.95, 0.9), (0.45, 0.6, 1.0), (0.7, 1.0, 0.75)]
    spots = [(1.0, -0.8), (-0.6, -1.0), (0.4, 1.1)]
    for k, ((x, y), col) in enumerate(zip(spots, cols)):
        g, sock = C.glow_disc((x, y, 0.006), radius=0.7, color=col, strength=0.0, power=2.5, name=f"hglow{k}")
        pl = L.point((x, y, 0.25), energy=0, color=col, radius=0.4, name=f"hpl{k}")
        ph = k * 11
        keys, ek = [], []
        for f in range(1, n + 1, 3):
            v = max(0.0, math.sin((f + ph) * 2 * math.pi / 30)) ** 2 * (1 - 0.6 * f / n)
            keys.append((f, 3.5 * v))
            ek.append((f, 60 * v))
        C.key_input(sock, keys)
        C.key_energy(pl, ek)
    fog, fsock, _ = C.noisy_volume((0, 0, 0.9), (5.6, 5.0, 1.8), color=(0.6, 0.75, 0.75), density=0.0, scale=1.1,
                                   name="hfog")
    C.key_input(fsock, [(1, 0.05), (n, 0.5)])
    L.area((0, 0, 1.9), (0, 0, 0), energy=8, size=3, color=(0.4, 0.7, 0.8), name="topwash")
    cam = C.camera(lens=20)
    keys = []
    for k in range(5):
        a = math.radians(-60 + 120 * k / 4)
        keys.append((1 + int((n - 1) * k / 4), (0.1, -0.2, 0.85), (0.1 + math.sin(a) * 2.0, -0.2 - math.cos(a) * 2.0,
                                                                  -0.1), 3.0 * math.sin(k)))
    C.aim_cam(cam, n, keys, shake=0.01, rot_shake=0.004, fn=lambda x: x,
              lens_keys=[(1, 20), (n // 3, 22), (2 * n // 3, 19), (n, 21)])
    L.bake_static()


def S13(L, n):
    spot_xy = (0.7, -0.75)
    b = _bell(L, n, haze=0.02, bump=0.1, glow_at=spot_xy, amb=10)
    C.key_input(b["glow"], [(1, 0.25), (int(n * 0.35), 0.6), (int(n * 0.75), 2.5), (n, 3.5)])
    g, gsock = C.glow_disc((spot_xy[0], spot_xy[1], 0.006), radius=0.6, color=(0.85, 1.0, 0.95), strength=0.0,
                           power=3.0, name="riseglow")
    C.key_input(gsock, [(1, 0.12), (int(n * 0.3), 0.3), (int(n * 0.7), 1.2), (n, 2.2)])
    C.key_scale(g, [(1, 1.4), (n, 0.55)])
    sp = L.spot((spot_xy[0], spot_xy[1], -1.6), (math.pi, 0, 0), energy=0, size_deg=24, blend=0.5, color=C.TORCH,
                name="risetorch", radius=0.05)
    C.key_loc(sp, [(1, (spot_xy[0], spot_xy[1], -1.6)), (n, (spot_xy[0], spot_xy[1], -0.35))])
    C.key_energy(sp, [(1, 60), (int(n * 0.3), 300), (n, 3500)])
    C.drip_rings([(spot_xy[0] + 0.1, spot_xy[1], 0.004), (spot_xy[0] - 0.1, spot_xy[1] + 0.08, 0.004),
                  (spot_xy[0], spot_xy[1] - 0.12, 0.004)], n, period=20, seed=13, strength=0.9, rmax=0.5,
                 name="lit_ring")
    p, hm = _gracia_seated(L, lamp=0, rim=0.6)
    L.area((0.0, 0.0, 1.9), (0, 0, 0), energy=6, size=3, color=(0.35, 0.7, 0.85), name="cyanwash")
    eye = Vector((SEAT[0] + 0.35, SEAT[1] - 0.35, 0.42))
    cam = C.camera(lens=35)
    C.aim_cam(cam, n, [(1, tuple(eye), (spot_xy[0], spot_xy[1], 0.25)),
                       (n, tuple(eye + Vector((0.35, -0.35, -0.08))), (spot_xy[0], spot_xy[1], 0.35))],
              shake=0.005, rot_shake=0.0015)
    L.bake_static()


def _rescuer_in_water(L, name, loc, face_deg, aim, energy=900, beam=0.12):
    d = _diver(name, RESCUE, energy=energy, beam_len=3.0, beam=beam, deg=28)
    _upright(d, loc, face_deg, tilt=0.08, helmet=(0.88, 0.88, 0.85))
    _track(d["torch"], aim, name + "_t")
    return d


def _face_deg(frm, to):
    v = Vector(to) - Vector(frm)
    return math.degrees(math.atan2(-v.x, v.y))


def S14(L, n):
    _bell(L, n, haze=0.02, bump=0.14)
    p, hm = _gracia_seated(L, lamp=0, rim=0.8)
    # he lifts an arm against the light
    sh = p["shoulderL"]
    for f, a in ((1, 0.5), (14, 0.5), (26, 1.9), (n, 2.0)):
        sh.rotation_euler = (a, 0, 0.3)
        sh.keyframe_insert("rotation_euler", frame=f)
    rloc = Vector((0.55, -0.45, -0.9))
    chest = (SEAT[0] + 0.05, SEAT[1] - 0.05, 0.75)
    d = _rescuer_in_water(L, "res1", tuple(rloc), _face_deg(rloc, chest), chest, energy=1400, beam=0.18)
    r = d["root"]
    C.key_loc(r, [(1, tuple(rloc)), (12, (rloc.x, rloc.y, -0.3)), (n, (rloc.x, rloc.y, -0.33))])
    L.ease_all(r)
    C.drip_rings([(rloc.x + 0.05, rloc.y, 0.004), (rloc.x - 0.08, rloc.y + 0.06, 0.004)], n, period=14, seed=5,
                 strength=0.8, rmax=0.55, name="boil")
    C.bubble_trail(lambda f: Vector((rloc.x, rloc.y, -0.1)), n, count=14, rise=0.5, size=0.02, life=(8, 16), seed=4)
    L.point((SEAT[0] + 0.5, SEAT[1] - 0.6, 0.5), energy=25, color=(1.0, 0.8, 0.55), radius=0.6, name="bounce")
    C.rim_light((rloc.x, rloc.y, 0.2), (-0.8, 1.0, 1.0), energy=300, color=CYAN_RIM, size_deg=45, name="rrim")
    fwd = (Vector(chest) - rloc)
    fwd.z = 0
    fwd.normalize()
    cpos = rloc - fwd * 0.95
    cam = C.camera(lens=28)
    side = Vector((fwd.y, -fwd.x, 0))
    cpos = rloc - fwd * 1.5 + side * 0.45
    C.aim_cam(cam, n, [(1, (cpos.x, cpos.y, 0.1), (SEAT[0] + 0.2, SEAT[1] - 0.2, 0.35)),
                       (n, (cpos.x + fwd.x * 0.35, cpos.y + fwd.y * 0.35, 0.14), (SEAT[0] + 0.2, SEAT[1] - 0.2, 0.4))],
              shake=0.01, rot_shake=0.003)
    C.cam_fill(cam, energy=8)
    L.bake_static()


def S15(L, n):
    _bell(L, n, haze=0.018, bump=0.12)
    p, hm = _gracia_seated(L, lamp=200, rim=0.6)
    C.beam_cone(hm["lamp"], length=1.6, strength=0.08, name="g_beam")
    hm["lens_mat"].node_tree.nodes["Emission"].inputs[1].default_value = 5
    # Gràcia's hand reaches down for the regulator
    for f, a in ((1, 0.6), (int(n * 0.4), 1.0), (n, 1.05)):
        p["shoulderR"].rotation_euler = (a, 0, -0.1)
        p["shoulderR"].keyframe_insert("rotation_euler", frame=f)
    l1 = Vector((-0.45, 0.05, -0.35))
    l2 = Vector((0.2, 0.75, -0.38))
    chest = (SEAT[0], SEAT[1], 0.8)
    d1 = _rescuer_in_water(L, "res1", tuple(l1), _face_deg(l1, chest), (SEAT[0], SEAT[1], 0.9), energy=500)
    d2 = _rescuer_in_water(L, "res2", tuple(l2), _face_deg(l2, chest) + 25, (-1.6, 1.9, 1.0), energy=500)
    for d, ph in ((d1, 0), (d2, 1.7)):
        base = Vector(d["root"].location)
        C.key_loc(d["root"], [(1, tuple(base)), (n // 2, tuple(base + Vector((0, 0, 0.03 * math.sin(ph + 1))))),
                              (n, tuple(base))])
    d1["shoulderR"].rotation_euler = (-0.6, 0, 0.5)
    # regulator hose passed up from rescuer 1 to Gràcia
    reg_end = Vector((SEAT[0] + 0.28, SEAT[1] - 0.22, 0.42))
    hose = C.curve([(l1.x + 0.15, l1.y + 0.05, 0.1), (l1.x + 0.0, l1.y + 0.35, 0.32), tuple(reg_end)],
                   thickness=0.012, mat=L.mat_principled("hose_m", (0.04, 0.04, 0.045), rough=0.5), name="hose",
                   smooth_pts=True)
    reg = L.prim("cyl", loc=tuple(reg_end), vertices=12, radius=0.035, depth=0.05, name="reg")
    L.assign(reg, L.mat_principled("reg_m", (0.85, 0.65, 0.1), rough=0.4))
    for x, y in ((l1.x, l1.y), (l2.x, l2.y)):
        C.drip_rings([(x + 0.1, y, 0.004), (x - 0.1, y + 0.05, 0.004)], n, period=24, seed=int(10 + 3 * x), strength=0.6,
                     rmax=0.45, name="wr")
    vap = C.cloud((SEAT[0] + 0.1, SEAT[1] - 0.1, 1.3), (0.6, 0.6, 0.5), count=80, radius=0.0025,
                  color=(0.9, 0.9, 0.88), emit=0.12, seed=21, name="vapour")
    C.drift(vap, n, (0.02, -0.02, 0.05))
    L.point((-0.6, 0.2, 0.6), energy=40, color=(1.0, 0.82, 0.6), radius=0.8, name="bounce")
    C.rim_light((-0.6, 0.5, 0.4), (-1.0, 1.5, 1.2), energy=300, color=CYAN_RIM, size_deg=60, name="rim")
    cam = C.camera(lens=24)
    C.aim_cam(cam, n, [(1, (1.35, -1.05, 0.25), (-0.8, 0.6, 0.35)), (n, (1.25, -1.0, 0.95), (-0.8, 0.6, 0.3))],
              shake=0.008, rot_shake=0.002)
    C.cam_fill(cam, energy=12)
    L.bake_static()


# ============================================================================ cross-section diagrams (S07, S10)

def _section(L, cl, hw, dome, wl_dome, extent, ground_z, name, zoff=0.0, entrance_wl=None):
    """Passage band along centreline cl [(x, z)] ending in an elliptical dome (cx, cz, rx, rz).
    Returns dict(xs, poly, air)."""
    band = C.offset_band(cl, hw)
    nL = len(cl)
    left, right = band[:nL], band[nL:]
    cx, cz, rx, rz = dome
    arc = []
    for k in range(25):
        a = math.radians(165 - 330 * k / 24)
        arc.append((cx + rx * math.cos(a), cz + rz * math.sin(a)))
    poly = left + arc + right
    pz = [(x, z + zoff) for x, z in poly]
    extent = (extent[0], extent[1], extent[2] + zoff, extent[3] + zoff)
    xs = C.xsection([(x, -z) for x, z in pz], lambda d: -d, extent=extent, water_top=(0.03, 0.22, 0.28),
                    water_bot=(0.0, 0.05, 0.08), outline_color=C.CYAN, outline_strength=3.0, name=name,
                    rock_mat_=L.mat_noise_surface(name + "_rk", (0.08, 0.075, 0.07), (0.32, 0.3, 0.27), scale=1.2,
                                                  bump=0.2, rough=0.9))
    yb = 0.4 - 0.12 - 0.02
    air = C.clip_poly(pz, 1, wl_dome + zoff, keep_less=False)
    air = C.clip_poly(air, 0, cx - rx - 0.1, keep_less=False)
    air_o = C.flat_poly(air, yb - 0.01, C.emis(name + "_air", (0.62, 0.66, 0.68), 1.3), name=name + "_air")
    C.curve([(cx - rx * 0.97, -0.43, wl_dome + zoff), (cx + rx * 0.97, -0.43, wl_dome + zoff)], thickness=0.01,
            mat=C.emis(name + "_wl", (0.6, 0.9, 1.0), 3), name=name + "_wline")
    if entrance_wl is not None:
        top = C.clip_poly(pz, 1, entrance_wl + zoff, keep_less=False)
        C.flat_poly(top, yb - 0.01, C.emis(name + "_sky", (0.02, 0.03, 0.04), 1.0), name=name + "_open")
    C.curve([(extent[0], -0.42, ground_z + zoff), (extent[1], -0.42, ground_z + zoff)], thickness=0.02,
            mat=C.emis(name + "_gl", (0.55, 0.5, 0.35), 2.5), name=name + "_ground")
    return {"xs": xs, "poly": pz, "air": air_o}


CL7 = [(-6.2, 2.7), (-6.2, 1.5), (-6.0, 0.5), (-5.5, -0.35), (-4.6, -0.8), (-3.4, -0.62), (-2.2, -1.0), (-1.0, -0.75),
       (0.2, -1.1), (1.4, -0.85), (2.6, -1.05), (3.8, -0.8), (4.6, -0.72)]


def S07(L, n):
    C.world_black((0.0, 0.0, 0.0))
    dome = (5.45, -0.55, 0.95, 0.85)
    sec = _section(L, CL7, 0.22, dome, -0.3, (-8.5, 8.5, -4.0, 2.0), 2.0, "s7", entrance_wl=1.85)
    # scrub dots on the ground line
    rnd = random.Random(4)
    for i in range(26):
        x = rnd.uniform(-8.2, 8.2)
        if abs(x + 6.2) < 0.5:
            continue
        o = L.prim("sphere", loc=(x, -0.42, 2.06), segments=8, ring_count=6, radius=rnd.uniform(0.06, 0.14),
                   name="scrub")
        o.scale = (1.4, 0.3, 0.8)
        L.assign(o, C.emis("scrub_m", (0.35, 0.5, 0.3), 1.2))
    route = [(x, -0.45, z) for x, z in reversed(CL7[2:])] + [(-6.2, -0.45, 1.5), (-6.2, -0.45, 2.3)]
    t_go, t_end = 12, 80
    o_dot, _, _ = C.glow_dot(route[0], (1.0, 0.55, 0.15), r=0.06, halo=2.6, strength=6, name="mascaro_dot")
    C.move_along(o_dot, route, [(t_go, 0.0), (t_end, 1.0)], step=2)
    c_dot, _, chem = C.glow_dot((4.6, -0.46, -0.72), C.CYAN, r=0.06, halo=2.6, strength=6, name="gracia_dot")
    C.key_loc(c_dot, [(1, (4.55, -0.46, -0.72)), (8, (4.65, -0.46, -0.7)), (26, (5.35, -0.46, -0.12)),
                      (n, (5.35, -0.46, -0.12))])
    C.key_input(chem.inputs[1], [(f, 2.0 + 1.0 * math.sin(f * 0.25)) for f in range(1, n + 1, 3)])
    ruler = C.dotted_path(route[:-2], spacing=0.3, r=0.028, color=(0.95, 0.95, 0.95), strength=3.0, name="ruler")
    total = len(ruler)
    for k, o in enumerate(ruler):
        C.hide_from_frame([o], f_show=t_go + 1 + int((t_end - 10 - t_go) * k / max(1, total - 1)))
    C.text("ENTRANCE", (-4.7, -0.45, 1.3), size=0.45, color=(1.0, 0.75, 0.4), strength=3.0, name="t_ent")
    C.text("AIR POCKET", (5.3, -0.45, 0.75), size=0.45, color=(0.7, 0.95, 1.0), strength=3.0, name="t_air")
    L.area((-3, -6, 5), (math.radians(55), 0, math.radians(-25)), energy=2500, size=8, color=(0.7, 0.85, 1.0))
    L.area((4, -6, 3), (math.radians(65), 0, math.radians(30)), energy=1200, size=8, color=(0.8, 0.85, 0.9))
    cam = C.camera(lens=50)
    zc = -0.7
    keys = [(1, (4.0, -11.5, zc), (4.0, 0.0, zc - 0.6))]
    for f in range(t_go, t_end + 1, 4):
        p = C.along(route, C.piecewise([(t_go, 0.0), (t_end, 1.0)], f))
        x = max(-5.2, min(4.0, p.x))
        keys.append((f, (x, -11.5, zc), (x, 0.0, zc - 0.6)))
    keys.append((88, keys[-1][1], keys[-1][2]))
    keys.append((96, (4.0, -11.5, zc), (4.0, 0.0, zc - 0.6)))
    keys.append((n, (4.05, -11.0, zc), (4.05, 0.0, zc - 0.6)))
    C.aim_cam(cam, n, keys, fn=C.sm)
    L.bake_static()


def _night_sky(L):
    C.sky_world(top=(0.008, 0.014, 0.035), horizon=(0.03, 0.045, 0.08), ground=(0.005, 0.005, 0.006), strength=1.0)
    C.star_dome(count=1200, radius=150, size=0.15, strength=4.0)


def _scrub_ground(L, fn, size=(60, 60), center=(0, 0, 0), res=0.35):
    gm = L.mat_noise_surface("garrigue", (0.05, 0.035, 0.025), (0.24, 0.18, 0.13), scale=0.9, bump=0.6, voronoi=False)
    return C.heightfield(size=size, center=center, res=res, fn=fn, mat=gm, name="ground", disp=(0.25, 0.06))


def S10(L, n):
    cut = 44
    ZD = -60.0
    _night_sky(L)
    C.render_quality(vol_end=30, vol_tile="8", vol_samples=16)
    _scrub_ground(L, lambda x, y: 0.12 * math.sin(x * 0.3) * math.cos(y * 0.25), size=(50, 50), res=0.5)
    C.bushes(count=55, rmin=3.5, rmax=22, seed=6, color=(0.06, 0.07, 0.035), size=(0.25, 0.7))
    rig = C.drill_rig((0, 0, 0), height=6.0)
    for x in (-3.2, 3.4):
        C.work_light((x, -3.0, 2.6), (0.0, 0.0, 1.5), energy=2200, color=(1.0, 0.58, 0.2), name=f"wl{x}")
    for k, (x, y, rz) in enumerate(((-1.9, -1.6, 0.6), (1.6, -2.1, -0.4))):
        p = C.figure(f"crew{k}", height=1.75, base=(0.03, 0.03, 0.035), rim=(1.0, 0.7, 0.35), rim_strength=0.4)
        p["root"].location = (x, y, 0.05)
        p["root"].rotation_euler = (0, 0, rz + math.pi)
        C.helmet(p["neck"], 1.0, color=(0.95, 0.85, 0.15), lamp_energy=0, name=f"hat{k}")
    dust = C.cloud((0, -1.5, 1.5), (6, 4, 3), count=600, radius=0.004, color=(1.0, 0.75, 0.5), emit=0.15, seed=10)
    up = L.spot((0.0, -2.5, 0.3), (0, 0, 0), energy=1500, size_deg=40, blend=0.6, color=(1.0, 0.6, 0.25), name="uplight")
    up.rotation_mode = "QUATERNION"
    up.rotation_quaternion = (Vector((0, 0, 4.0)) - Vector(up.location)).to_track_quat("-Z", "Y")
    C.drift(dust, n, (0.1, 0.02, 0.05))
    C.water(center=(0, -1, 2), size=(14, 10, 4), color=(0.9, 0.75, 0.6), density=0.01, anisotropy=0.4,
            absorption=(0.02, 0.02, 0.02), name="nighthaze")
    # --- section below (cut at `cut`, match on the bore line at x = 0)
    cl = [(-6.5, -4.3), (-5.0, -4.05), (-3.6, -4.35), (-2.2, -4.05), (-0.9, -4.3), (0.1, -4.1)]
    sec = _section(L, cl, 0.2, (1.0, -3.95, 0.85, 0.7), -3.75, (-6.5, 6.5, -7.5, 3.0), 3.0, "s10", zoff=ZD)
    for z, k in ((1.6, 0), (0.2, 1), (-1.4, 2), (-2.6, 3)):  # strata lines
        C.curve([(-6.4, -0.42, ZD + z + 0.1 * math.sin(k)), (6.4, -0.42, ZD + z - 0.1 * math.cos(k))], thickness=0.008,
                mat=C.emis("strata", (0.3, 0.28, 0.25), 1.2), name="strata")
    for i, (a, b) in enumerate((((-0.6, 3.0), (0.0, 4.6)), ((0.6, 3.0), (0.0, 4.6)))):  # rig icon
        C.curve([(a[0], -0.43, ZD + a[1]), (b[0], -0.43, ZD + b[1])], thickness=0.03,
                mat=C.emis("rigicon", (1.0, 0.6, 0.2), 3.0), name="rigicon")
    stop = -2.15
    bore = C.curve([(0, -0.44, ZD + 3.0), (0, -0.44, ZD + stop)], thickness=0.05, mat=C.emis("bore", (1.0, 0.6, 0.2), 3.5),
                   name="bore")
    f_stop = 62
    C.grow_curve(bore, [(cut + 1, 0.02), (f_stop, 1.0)])
    tip, _, _ = C.glow_dot((0, -0.46, ZD + 3.0), (1.0, 0.7, 0.3), r=0.09, halo=3, strength=10, name="bit")
    C.key_loc(tip, [(cut + 1, (0, -0.46, ZD + 2.9)), (f_stop, (0, -0.46, ZD + stop))])
    xm, xmm = C.x_mark((0.0, ZD + stop - 0.35), size=0.25, y=-0.47, name="xstop")
    C.hide_from_frame(xm, f_show=f_stop + 1)
    g_dot, _, gem = C.glow_dot((1.0, -0.46, ZD - 3.55), C.CYAN, r=0.07, halo=4, strength=10, name="gracia_dot")
    C.key_input(gem.inputs[1], [(f, 3.5 + 2.0 * math.sin(f * 0.25)) for f in range(1, n + 1, 3)])
    gap = C.curve([(0.35, -0.45, ZD + stop - 0.1), (0.35, -0.45, ZD - 3.2)], thickness=0.012,
                  mat=C.emis("gap", (1.0, 0.3, 0.25), 2.0), name="gap")
    C.hide_from_frame([gap], f_show=f_stop + 4)
    secl = L.area((-3, -6, ZD + 3), (math.radians(60), 0, math.radians(-25)), energy=600, size=6, color=(0.7, 0.85, 1.0),
                  name="seclight")
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (2.0, -8.0, 4.2), (0.0, 0.0, 2.6)), (cut - 10, (1.2, -5.0, 1.6), (0.0, 0.0, 0.5)),
                       (cut, (0.6, -3.2, 0.35), (0.0, 0.0, -0.6)),
                       (cut + 1, (0.0, -11.0, ZD + 2.6), (0.0, 0.0, ZD + 2.0)),
                       (f_stop, (0.0, -11.0, ZD + 0.6), (0.0, 0.0, ZD - 0.4)),
                       (n, (0.05, -10.4, ZD + 0.2), (0.0, 0.0, ZD - 0.9))],
              shake=0.01, rot_shake=0.002, shake_keys=[(1, 1.0), (cut, 1.0), (cut + 1, 0.2), (n, 0.2)])
    cam.data.lens = 28
    cam.data.keyframe_insert("lens", frame=cut)
    cam.data.lens = 45
    cam.data.keyframe_insert("lens", frame=cut + 1)
    C.constant_keys(cam.data)
    L.bake_static()


# ============================================================================ S16 surface entrance at night

def _pit_z(x, y, c=(0.0, 1.2), r=2.0, depth=1.9):
    d = math.hypot(x - c[0], (y - c[1]) * 1.15)
    z = 0.12 * math.sin(x * 0.35) * math.cos(y * 0.3) + 0.012 * max(0, y - 4) ** 1.5 - 0.02 * max(0, -y - 2)
    if d < r * 1.2:
        t = C.sm((r * 1.2 - d) / (r * 0.45))
        z -= depth * t
    return z


def S16(L, n):
    _night_sky(L)
    C.render_quality(vol_end=30, vol_tile="8", vol_samples=16)
    _scrub_ground(L, _pit_z, size=(40, 40), center=(0, 6, 0), res=0.22)
    pool, _ = C.water_surface(size=(4.2, 3.8), center=(0.0, 1.2, -1.45), n=n, flow=(0, 0.02), wave_scale=1.5,
                              bump=0.12, name="pool")
    rnd = random.Random(8)
    pts = []
    for i in range(14):
        a = rnd.uniform(0, 2 * math.pi)
        x, y = math.cos(a) * 2.6, 1.2 + math.sin(a) * 2.3
        pts.append((x, y, _pit_z(x, y)))
    C.rocks(pts, count=14, size=(0.25, 0.6), seed=9, sink=0.4,
            mat=C.rock_mat("lime", (0.06, 0.055, 0.05), (0.4, 0.37, 0.32), scale=2.0))
    bp = []
    for i in range(50):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(4.0, 16)
        x, y = math.cos(a) * r, 1.2 + math.sin(a) * r
        if y < -3.0 and abs(x) < 2.5:
            continue
        bp.append((x, y, _pit_z(x, y)))
    C.jungle(bp, size=(0.35, 0.8), seed=5, c1=(0.02, 0.03, 0.015), c2=(0.08, 0.1, 0.05), name="scrub")
    # beacons on unseen vehicles (generic blue / amber, unmarked), <= 1 Hz rotation
    for k, (loc, col, ph) in enumerate((((-6.5, -2.0, 1.9), (0.1, 0.3, 1.0), 0.0), ((5.5, -1.0, 1.9), (0.1, 0.3, 1.0), 2.0),
                                        ((7.0, 4.5, 1.8), (1.0, 0.55, 0.05), 1.0))):
        C.beacon(loc, col, n=n, hz=0.8, energy=2200, phase=ph, name=f"bcn{k}")
    # Mascaró: lone figure at the edge, orange fin in hand
    m = C.figure("mascaro", height=1.75, base=(0.03, 0.03, 0.035), rim=(0.6, 0.75, 1.0), rim_strength=0.5)
    mz = _pit_z(0.2, -1.3)
    m["root"].location = (0.2, -1.3, mz)
    m["root"].rotation_euler = (0, 0, 0.1)
    m["neck"].rotation_euler = (-0.35, 0, 0)
    m["shoulderR"].rotation_euler = (0.1, 0, -0.15)
    fin = C.fin_blade((0, 0.03, -0.32), (-math.pi / 2, 0, 0), length=0.5, mat=L.mat_principled("ofin", MASCARO, rough=0.4,
                                                                                    emit=MASCARO, emit_strength=0.3),
                      name="ofin")
    fin.parent = m["elbowR"]
    # rescue team on the far side, headlamps toward the water
    for k, (x, y) in enumerate(((-1.6, 3.6), (-0.6, 4.0), (1.4, 3.7))):
        p = C.figure(f"team{k}", height=1.72 + 0.04 * k, base=(0.03, 0.03, 0.035), rim=(1.0, 0.75, 0.4), rim_strength=0.4)
        p["root"].location = (x, y, _pit_z(x, y))
        p["root"].rotation_euler = (0, 0, math.pi + 0.3 * (k - 1))
        p["neck"].rotation_euler = (-0.5, 0, 0)
        C.helmet(p["neck"], 1.0, color=(0.9, 0.9, 0.85), lamp_energy=220, lamp_deg=35, name=f"thel{k}")
    wl = C.work_light((0.8, 5.5, 2.4), (0.0, 1.0, -1.2), energy=1500, color=(0.95, 0.95, 1.0), name="wlfar")
    C.rim_light((0.2, -1.3, 1.2), (0.0, 3.5, 1.2), energy=900, color=(0.7, 0.8, 1.0), size_deg=35, name="figrim")
    L.area((0.0, 1.2, 3.0), (0, 0, 0), energy=150, size=4, color=(0.45, 0.6, 1.0), name="pitwash")
    dust = C.cloud((0, 0, 1.2), (8, 8, 2.5), count=1200, radius=0.006, color=(0.8, 0.85, 1.0), emit=0.2, seed=12)
    C.drift(dust, n, (0.12, 0.05, 0.02))
    cam = C.camera(lens=28)
    C.aim_cam(cam, n, [(1, (0.9, -4.9, 2.6), (0.0, 1.3, -0.6)), (n, (0.75, -4.1, 2.45), (0.0, 1.3, -0.7))],
              shake=0.01, rot_shake=0.002)
    C.cam_fill(cam, energy=30, color=(0.6, 0.7, 1.0))
    L.bake_static()
