"""HAUNT-04 — The Brown Lady of Raynham Hall (1936 photograph). One builder per shot: def Sxx(L, n).
All imagery is our own: the real photograph is never shown, traced or imitated (figure pose/framing deliberately different)."""
import importlib, sys, os, math
_LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PIPELINE", "blender")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import lib_haunted as H
importlib.reload(H)
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
NEG_IMG = os.path.join(HERE, "plate_negative.png")   # our own S01 render, inverted (made once from a preview still)
POS_IMG = os.path.join(HERE, "plate_positive.png")

# staircase framing: S01 push from P0 to P1; S13 / S14 locked on P1; S14 eases back to P0 (loop)
S01_P0, S01_T0 = (-0.62, -6.2, 1.3), (0.55, 5.0, 2.75)
S01_P1, S01_T1 = (-0.5, -2.2, 1.42), (0.5, 5.0, 3.05)
LADY_LANDING = (-0.5, 5.2, H.LANDING_Z)
FLASH_F = 8


def _calm():
    """Clamp indirect light: the emissive leaded window throws firefly speckle at 2 TAA samples."""
    e = bpy.context.scene.eevee
    e.clamp_surface_indirect = 0.3
    try:
        e.fast_gi_method = "AMBIENT_OCCLUSION_ONLY"
    except Exception:
        pass


def _stairs(L, day=False, window=1.0, world=None, vol=None):
    H.eevee_quality()
    _calm()
    L.set_world(world or ((0.05, 0.055, 0.065) if day else (0.004, 0.0045, 0.006)), 1.0)
    st = H.manor_staircase(day=day, window=window)
    if vol:
        H.room_fog((0.9, 0.0, 3.5), (3.6, 16, 7), density=vol, color=(0.75, 0.78, 0.85), anis=0.5, name="hallhaze")
    if day:
        L.area((0.9, -6.0, 6.5), (math.radians(40), 0, 0), energy=500, size=5, color=(0.8, 0.85, 0.95), name="dayfill")
    return st


def _lady(name, loc, alpha=0.25, emit=0.4, face=(0, -1)):
    p = H.brown_lady(name, alpha=alpha, emit=emit)
    p["root"].location = loc
    p["root"].rotation_euler = (0, 0, math.atan2(-face[0], face[1]))
    # hands loosely together in front (our own pose)
    for tag, sx in (("L", -1), ("R", 1)):
        p[f"shoulder{tag}"].rotation_euler = (math.radians(18), 0, sx * math.radians(-12))
        p[f"elbow{tag}"].rotation_euler = (math.radians(55), 0, 0)
    return p


# --------------------------------------------------------------------------- S01 cold open: flash on the staircase
def S01(L, n):
    _stairs(L, window=1.0, vol=None)
    lady = _lady("lady_land", LADY_LANDING, alpha=0.3, emit=0.35)
    H.key_principled(lady["mat"], "Emission Strength", [(1, 0.35), (FLASH_F - 1, 0.35), (FLASH_F, 2.0), (FLASH_F + 10, 0.6), (n, 0.45)])
    H.key_principled(lady["mat"], "Alpha", [(1, 0.28), (FLASH_F - 1, 0.28), (FLASH_F, 0.55), (FLASH_F + 10, 0.35), (n, 0.3)])
    c = H.cam(S01_P0, S01_T0, lens=35)
    H.cam_move(c, [(1, S01_P0, S01_T0), (n, S01_P1, S01_T1)])
    H.handheld(c, n, amp=0.006, rate=0.3)
    L.cam_light(c, energy=30, color=(0.75, 0.8, 0.95))
    H.flash_pop(c, FLASH_F, peak=900, decay=10)
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S02 the house in daylight fog
def S02(L, n):
    H.eevee_quality()
    bpy.context.scene.eevee.volumetric_end = 160
    L.set_world((0.32, 0.34, 0.37), 1.0)
    H.manor_exterior()
    L.sun(rot=(0.9, 0.1, 2.7), energy=0.8, color=(0.85, 0.88, 0.95), angle=20)
    L.fog_volume(center=(0, -20, 8), size=(200, 160, 18), density=0.012, color=(0.8, 0.82, 0.86))
    p0, t0 = (0.0, -88.0, 16.0), (0.0, 0.0, 6.0)
    p1, t1 = (0.0, -64.0, 2.6), (0.0, 0.0, 8.5)
    c = H.cam(p0, t0, lens=40)
    H.cam_move(c, [(1, p0, t0), (n, p1, t1)])
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S03 empty portrait frame on the landing
def S03(L, n):
    _stairs(L, window=0.8)
    LZ = H.LANDING_Z
    gilt = L.mat_principled("gilt", (0.55, 0.38, 0.12), rough=0.3, metal=1.0)
    py, pz = 4.95, LZ + 1.55
    fw, fh = 0.38, 0.5
    H.box_mesh("pframe", [(-0.955, py, pz + fh, 0.03, fw + 0.06, 0.06), (-0.955, py, pz - fh, 0.03, fw + 0.06, 0.06),
                          (-0.955, py - fw, pz, 0.03, 0.06, fh), (-0.955, py + fw, pz, 0.03, 0.06, fh)], gilt, bevel=0.015)
    H.box_mesh("canvas", [(-0.965, py, pz, 0.01, fw, fh)], L.mat_noise_surface("canv", (0.004, 0.0035, 0.003), (0.012, 0.01, 0.008),
                                                                          scale=40, bump=0.05, voronoi=False, rough=0.7))
    H.box_mesh("sconceplate", [(-0.96, 5.62, LZ + 1.3, 0.02, 0.07, 0.12), (-0.88, 5.62, LZ + 1.25, 0.1, 0.02, 0.015)], H.mat_brass("sbr"))
    cnd = H.candle(loc=(-0.8, 5.62, LZ + 1.27), name="sc_candle", energy=35)
    H.flicker_mat_with_light(cnd["light"], cnd["flame"], n, 35, 25, seed=4, depth=0.35, rate=0.5)
    p0, p1 = (1.3, 4.45, LZ + 1.25), (1.3, 5.15, LZ + 1.25)
    c = H.cam(p0, (-1.0, 4.45 + 0.35, LZ + 1.05), lens=50)
    H.cam_move(c, [(1, p0, (-1.0, 4.8, LZ + 1.05)), (n, p1, (-1.0, 5.5, LZ + 1.05))], ease=False)
    L.cam_light(c, energy=6, color=(0.7, 0.75, 0.9))
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S04 corridor: the pistol shot
def S04(L, n):
    H.eevee_quality()
    L.set_world((0.003, 0.003, 0.004), 1.0)
    H.oak_corridor(length=14.0)
    man = H.figure("marryat", height=1.8, coat=True, color=(0.015, 0.013, 0.012))
    man["root"].location = (0.3, 1.4, 0)
    H.pose_hold(man, "R", shoulder=(math.radians(85), 0, math.radians(8)), elbow=(math.radians(5), 0, 0))
    H.pose_hold(man, "L", shoulder=(math.radians(45), 0, math.radians(-25)), elbow=(math.radians(60), 0, 0))
    gm = L.mat_principled("pistol", (0.03, 0.03, 0.03), rough=0.35, metal=0.6)
    H.box_mesh("pistol", [(0, 0, -0.44, 0.015, 0.02, 0.13), (0, -0.05, -0.33, 0.015, 0.06, 0.02)], gm, parent=man["elbowR"])
    lamp = H.empty("lampholder", (0, 0.0, -0.33), parent=man["elbowL"])
    lm = L.mat_emission("lampglass", (1.0, 0.7, 0.35), 8)
    lg = L.prim("cyl", loc=(0, 0, 0), vertices=12, radius=0.04, depth=0.1)
    L.assign(lg, lm)
    lg.parent = lamp
    lamp_l = L.point((0, 0, 0), energy=40, color=(1.0, 0.65, 0.3), radius=0.05, name="lamp_l")
    lamp_l.parent = lamp
    lamp_l.location = (0, 0.05, 0)
    H.flicker_mat_with_light(lamp_l, lm, n, 40, 8, seed=2, depth=0.3, rate=0.5)
    lady = _lady("lady_corr", (0.0, 10.5, 0), alpha=0.3, emit=0.45)
    shot = 48
    H.key_vis(lady["root"].children_recursive + [lady["root"]], [(1, True), (shot + 6, False)])
    mz = L.point((0, 0, 0), energy=0, color=(1.0, 0.75, 0.4), radius=0.05, name="muzzle")
    mz.parent = man["elbowR"]
    mz.location = (0, 0, -0.6)
    H.key_energy(mz, [(1, 0), (shot, 3000), (shot + 1, 0)])
    smoke = H.room_fog((0.3, 3.0, 1.45), (1.6, 2.6, 1.2), density=0.0, color=(0.7, 0.7, 0.72), anis=0.3, name="smoke")
    vn = next(nd for nd in smoke.active_material.node_tree.nodes if nd.type == "PRINCIPLED_VOLUME")
    for f, d in ((1, 0.0), (shot, 0.0), (shot + 2, 0.9), (shot + 14, 0.5), (n, 0.0)):
        vn.inputs["Density"].default_value = d
        vn.inputs["Density"].keyframe_insert("default_value", frame=f)
    smoke.location.x += 0
    L.point((0.0, 13.5, 2.2), energy=25, color=(0.55, 0.65, 0.9), radius=0.6, name="farcold")
    p0, t0 = (0.72, 0.15, 1.78), (0.0, 10.5, 1.2)
    c = H.cam(p0, t0, lens=35)
    H.cam_move(c, [(1, p0, t0), (n, (0.7, 0.35, 1.76), (0.0, 10.5, 1.2))], ease=False)
    H.handheld(c, n, amp=0.008, rate=0.6)
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S05 the photographers (daylight)
def _photographers(L, n):
    pc = H.plate_camera((0.25, -1.9, 0), 0.0, name="pcam")
    a = H.figure("provand", height=1.78, coat=False, color=(0.03, 0.028, 0.026))
    a["root"].location = (0.25, -2.55, 0)
    H.pose_hold(a, "R", shoulder=(math.radians(55), 0, 0), elbow=(math.radians(40), 0, 0))
    H.pose_hold(a, "L", shoulder=(math.radians(50), 0, 0), elbow=(math.radians(45), 0, 0))
    b = H.figure("shira", height=1.72, cap=True, color=(0.035, 0.03, 0.028))
    b["root"].location = (1.35, -1.3, 0)
    b["root"].rotation_euler = (0, 0, math.radians(20))
    H.pose_hold(b, "R", shoulder=(math.radians(150), 0, math.radians(10)), elbow=(math.radians(10), 0, 0))
    fg = H.flash_gun(parent=b["elbowR"], loc=(0, 0.0, -0.36), rot=(math.radians(-60), 0, 0), name="fgun")
    return pc, a, b, fg


def S05(L, n):
    _stairs(L, day=True, window=1.0)
    _photographers(L, n)
    p0, t0 = (2.15, -5.4, 0.55), (-0.1, 1.6, 1.85)
    c = H.cam(p0, t0, lens=24)
    H.cam_move(c, [(1, p0, t0), (n, (1.95, -4.6, 0.6), (-0.1, 1.6, 1.9))], ease=False)
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S06 Shira's POV: the vapour gathers
def S06(L, n):
    _stairs(L, day=True, window=1.0)
    s11, s10 = H.step_pos(11), H.step_pos(10)
    lady = _lady("lady_form", (0.0, s11[1], s11[2]), alpha=0.0, emit=0.5)
    r = lady["root"]
    r.keyframe_insert("location", frame=int(n * 0.45))
    r.location = (0.0, s10[1], s10[2])
    r.keyframe_insert("location", frame=n)
    H.key_principled(lady["mat"], "Alpha", [(1, 0.0), (int(n * 0.35), 0.0), (n, 0.22)])
    col = H.room_fog((0.0, s11[1], s11[2] + 1.0), (0.9, 0.9, 2.2), density=0.0, color=(0.85, 0.86, 0.9), anis=0.6, name="vapour")
    vn = next(nd for nd in col.active_material.node_tree.nodes if nd.type == "PRINCIPLED_VOLUME")
    for f, d in ((1, 0.02), (int(n * 0.5), 0.2), (n, 0.08)):
        vn.inputs["Density"].default_value = d
        vn.inputs["Density"].keyframe_insert("default_value", frame=f)
    col.keyframe_insert("rotation_euler", frame=1)
    col.rotation_euler = (0, 0, 1.2)
    col.keyframe_insert("rotation_euler", frame=n)
    col.scale = (0.45, 0.45, 1.1)
    col.keyframe_insert("scale", frame=1)
    col.scale = (0.3, 0.3, 0.95)
    col.keyframe_insert("scale", frame=n)
    L.spot((0.0, 6.2, 4.8), (0, 0, 0), energy=300, size_deg=35, blend=0.6, color=(0.75, 0.8, 0.95), name="rimvapour")
    H.aim(bpy.data.objects["rimvapour"], (0.0, 6.2, 4.8), (0.0, 3.3, 2.6))
    p0, t0 = (-0.35, -1.1, 1.95), (0.0, 3.4, 2.75)
    c = H.cam(p0, t0, lens=50)
    H.cam_move(c, [(1, p0, t0), (n, (-0.3, -0.3, 2.0), (0.0, 3.4, 2.8))], ease=False)
    H.handheld(c, n, amp=0.004, rate=0.4)
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S07 macro: lens cap off, flash fires
def S07(L, n):
    _stairs(L, day=True, window=1.0)
    pc, a, b, fg = _photographers(L, n)
    cap = pc["cap"]
    cut, fire = 46, 58
    glove = L.mat_principled("glove7", (0.03, 0.025, 0.02), rough=0.7)
    hand = H.empty("hand7", (0.45, -1.2, 1.2))
    hb = L.prim("sphere", loc=(0, 0, 0), segments=14, ring_count=8, radius=0.05)
    hb.scale = (0.9, 1.2, 0.7)
    L.assign(hb, glove)
    hb.parent = hand
    arm = L.prim("cyl", loc=(0.12, 0.08, -0.1), vertices=12, radius=0.035, depth=0.3, rot=(0.6, 0.9, 0))
    L.assign(arm, glove)
    arm.parent = hand
    lens_w = Vector((0.25, -1.9 + 0.51, 1.42))
    for f, loc in ((1, (0.45, -1.2, 1.2)), (16, tuple(lens_w + Vector((0.04, 0.05, 0.0)))), (22, tuple(lens_w + Vector((0.04, 0.05, 0.0)))),
                   (40, (0.55, -1.0, 1.6))):
        hand.location = loc
        hand.keyframe_insert("location", frame=f)
    cl0 = tuple(cap.location)
    cap.keyframe_insert("location", frame=22)
    cap.location = (cl0[0] + 0.28, cl0[1] + 0.38, cl0[2] + 0.17)
    cap.keyframe_insert("location", frame=40)
    # flash fires: bulb blowout + huge area light
    H.key_emission(fg["bulb_mat"], [(1, 0.3), (fire, 4000), (fire + 4, 0.3)])
    fl = L.point((0, 0, 0), energy=0, color=(1, 1, 1), radius=0.3, name="flashburst")
    fl.parent = fg["root"]
    fl.location = (0, 0.12, 0)
    H.key_energy(fl, [(1, 0), (fire, 60000), (fire + 3, 60000), (fire + 4, 0)])
    # camera: 85 mm macro on the lens cap, cut at `cut` to the flash dish
    pcam = Vector((0.25, -1.9, 0))
    c = H.cam((0.62, -1.0, 1.52), tuple(lens_w), lens=85)
    bpy.context.view_layer.update()
    dish = fg["dish"].matrix_world.translation.copy()
    dish_n = (fg["root"].matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
    cpos = dish + dish_n * 0.75 + Vector((0.25, 0, 0))
    H.cam_move(c, [(1, (0.62, -1.0, 1.52), tuple(lens_w)), (cut - 1, (0.6, -1.02, 1.5), tuple(lens_w)),
                   (cut, tuple(cpos), tuple(dish)), (n, tuple(cpos + (dish - cpos) * 0.05), tuple(dish))])
    for fc in L._fcurves(c.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR" if kp.co[0] >= cut else "BEZIER"
    for fc in L._fcurves(c.animation_data.action):
        for kp in fc.keyframe_points:
            if abs(kp.co[0] - (cut - 1)) < 0.5:
                kp.interpolation = "CONSTANT"
    c.data.dof.use_dof = True
    c.data.dof.aperture_fstop = 2.8
    c.data.dof.focus_distance = (Vector((0.62, -1.0, 1.52)) - lens_w).length
    c.data.dof.keyframe_insert("focus_distance", frame=1)
    c.data.dof.keyframe_insert("focus_distance", frame=cut - 1)
    c.data.dof.focus_distance = 0.75
    c.data.dof.keyframe_insert("focus_distance", frame=cut + 3)
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S08 darkroom: the plate develops
def S08(L, n):
    H.eevee_quality()
    L.set_world((0.002, 0.0, 0.0), 1.0)
    bench = L.mat_noise_surface("bench8", (0.03, 0.025, 0.02), (0.08, 0.06, 0.045), scale=6, bump=0.1, voronoi=False, rough=0.6)
    H.box_mesh("bench", [(0, 0, 0.85, 1.2, 0.6, 0.05)], bench)
    img = NEG_IMG if os.path.exists(NEG_IMG) else None
    tr = H.darkroom_tray((0.0, 0.0, 0.9), img=img, n=n, reveal=(6, int(n * 0.85)))
    # second empty tray + bottles + tongs
    H.box_mesh("tray2", [(0.85, 0.05, 0.93, 0.3, 0.24, 0.03)], L.mat_principled("t2", (0.6, 0.58, 0.55), rough=0.4))
    gl = L.mat_principled("bottle", (0.12, 0.05, 0.02), rough=0.1, metal=0.1)
    for i, (x, y) in enumerate(((-0.75, 0.35), (-0.62, 0.42), (-0.9, 0.3))):
        bt = L.prim("cyl", loc=(x, y, 1.02), vertices=16, radius=0.05, depth=0.25)
        L.assign(bt, gl)
    H.box_mesh("tongs", [(0.3, -0.25, 0.94, 0.12, 0.008, 0.005, 0.5)], L.mat_principled("tg", (0.5, 0.5, 0.48), rough=0.3, metal=1))
    red = L.area((0.2, 0.3, 2.0), (math.radians(-15), 0, 0), energy=60, size=0.5, color=(1.0, 0.02, 0.0), name="safelight")
    lampbox = H.box_mesh("safebox", [(0.2, 0.32, 2.05, 0.18, 0.08, 0.1)], L.mat_emission("safem", (1.0, 0.03, 0.0), 6))
    L.point((0.0, -0.2, 1.4), energy=8, color=(1.0, 0.05, 0.0), radius=0.4, name="redfill")
    c = H.cam((0.02, -0.12, 1.95), (0.0, 0.0, 0.9), lens=50, roll=0.0)
    H.cam_move(c, [(1, (0.02, -0.12, 1.95), (0.0, 0.0, 0.9)), (n, (0.0, -0.06, 1.62), (0.0, 0.0, 0.9))], ease=False)
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S09 magazine page over a blurred staircase
def S09(L, n):
    _stairs(L, window=1.4, world=(0.01, 0.01, 0.012))
    c = H.cam((-0.4, -4.0, 1.2), (0.4, 4.0, 2.4), lens=35)
    H.cam_move(c, [(1, (-0.4, -4.0, 1.2), (0.4, 4.0, 2.4)), (n, (-0.4, -4.0, 1.6), (0.4, 4.0, 2.9))], ease=False)
    L.cam_light(c, energy=20, color=(0.9, 0.8, 0.65))
    L.dof(c, distance=0.5, fstop=0.8)
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S10 lightbox + magnifier
def S10(L, n):
    H.eevee_quality()
    L.set_world((0.004, 0.004, 0.005), 1.0)
    H.box_mesh("lbtable", [(0, 0, 0.85, 1.0, 0.7, 0.05)], L.WOOD_OLD())
    H.box_mesh("lbbox", [(0, 0, 0.95, 0.38, 0.3, 0.05)], L.mat_principled("lbcase", (0.05, 0.05, 0.05), rough=0.5))
    H.box_mesh("lbtop", [(0, 0, 1.002, 0.35, 0.27, 0.002)], L.mat_emission("lbglow", (0.95, 0.95, 0.9), 2.2))
    m, nn, l = H._nodes("plate10")
    p = nn["Principled BSDF"]
    img = POS_IMG if os.path.exists(POS_IMG) else None
    if img:
        t = nn.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(img)
        l.new(t.outputs["Color"], p.inputs["Emission Color"])
        l.new(t.outputs["Color"], p.inputs["Base Color"])
        p.inputs["Emission Strength"].default_value = 2.0
    import bmesh
    bm = bmesh.new()
    pw, ph = 0.17, 0.21
    vs = [bm.verts.new(v) for v in ((-pw, -ph, 1.006), (pw, -ph, 1.006), (pw, ph, 1.006), (-pw, ph, 1.006))]
    f = bm.faces.new(vs)
    uv = bm.loops.layers.uv.new()
    for lp, cc in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        lp[uv].uv = cc
    pl = L.mesh_from_bm("plate10", bm)
    L.assign(pl, m)
    mg = H.empty("magnifier", (-0.25, -0.15, 1.12))
    brass = H.mat_brass("mgb")
    rim = L.prim("torus", loc=(0, 0, 0), major_radius=0.07, minor_radius=0.008)
    L.assign(rim, brass)
    rim.parent = mg
    lens = L.prim("cyl", loc=(0, 0, 0), vertices=32, radius=0.07, depth=0.006)
    lm = L.mat_principled("mglens", (0.9, 0.95, 1.0), rough=0.02, alpha=0.15)
    lm.surface_render_method = "BLENDED"
    L.assign(lens, lm)
    lens.parent = mg
    hd = L.prim("cyl", loc=(0.15, -0.06, 0), vertices=12, radius=0.012, depth=0.16, rot=(0, math.pi / 2, math.radians(-20)))
    L.assign(hd, L.mat_principled("mgh", (0.04, 0.03, 0.02), rough=0.4))
    hd.parent = mg
    pts = [(1, (-0.2, -0.15, 1.12)), (int(n * 0.5), (0.02, 0.02, 1.1)), (n, (0.08, 0.13, 1.1))]
    for f_, loc in pts:
        mg.location = loc
        mg.keyframe_insert("location", frame=f_)
    c = H.cam((-0.15, -0.2, 1.75), (-0.15, -0.12, 1.0), lens=50)
    H.cam_move(c, [(1, (-0.12, -0.22, 1.72), (-0.12, -0.13, 1.0)), (int(n * 0.5), (0.02, -0.05, 1.68), (0.02, 0.02, 1.0)),
                   (n, (0.06, 0.04, 1.65), (0.06, 0.1, 1.0))])
    L.area((0, -1.0, 2.2), (math.radians(30), 0, 0), energy=15, size=1.0, color=(0.8, 0.85, 1.0), name="lbfill")
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S11 sceptics board: double exposure diagram
def S11(L, n):
    H.eevee_quality()
    L.set_world((0.01, 0.01, 0.012), 1.0)
    H.box_mesh("bwall", [(0, 0.2, 0, 4, 0.05, 4)], L.mat_principled("bw", (0.05, 0.05, 0.055), rough=0.9))
    H.evidence_board("board", 2.4, 4.0)
    H.pinned_card("c_hdr", (0.0, -0.01, 1.35), 1.5, 0.36, [], header="WHAT SCEPTICS SAY", size=0.1, font_size_header=0.125,
                  color=(0.86, 0.83, 0.72), rot=math.radians(-1.5))
    ink = L.mat_principled("ink11", (0.05, 0.04, 0.03), rough=0.6)
    out = []
    for nm, x0, col in (("STAIRS", -0.62, (0.25, 0.45, 0.75)), ("FIGURE", 0.62, (0.85, 0.82, 0.7))):
        mat = L.mat_principled("sheet_" + nm, col, rough=0.6, alpha=0.55, emit=col, emit_strength=0.15)
        mat.surface_render_method = "BLENDED"
        root = H.empty("sh_" + nm, (x0, -0.03 if nm == "STAIRS" else -0.04, 0.35))
        H.box_mesh("shb_" + nm, [(0, 0, 0, 0.42, 0.002, 0.55)], mat, parent=root)
        t = L.text3d(nm, loc=(0, -0.006, 0.4 if nm == "STAIRS" else -0.48), size=0.1, extrude=0.001, mat=ink, name="sht_" + nm)
        t.parent = root
        if nm == "STAIRS":
            bm = []
            for i in range(6):
                bm.append((-0.25 + i * 0.09, -0.005, -0.35 + i * 0.09, 0.05, 0.002, 0.045))
            H.box_mesh("stairicon", bm, ink, parent=root)
        else:
            fi = L.prim("sphere", loc=(0, -0.006, 0.18), segments=12, ring_count=8, radius=0.07)
            fi.scale = (1, 0.05, 1.1)
            L.assign(fi, ink)
            fi.parent = root
            bd = L.prim("cone", loc=(0, -0.006, -0.12), vertices=16, radius1=0.16, radius2=0.06, depth=0.5)
            bd.scale = (1, 0.03, 1)
            L.assign(bd, ink)
            bd.parent = root
        root.keyframe_insert("location", frame=1)
        root.keyframe_insert("location", frame=10)
        root.location = (0.0, root.location.y, 0.35)
        root.keyframe_insert("location", frame=48)
        out.append(root)
    red = L.mat_principled("redframe", (0.7, 0.04, 0.03), rough=0.5)
    fr = H.box_mesh("oneframe", [(0, -0.05, 0.35 + 0.6, 0.48, 0.003, 0.02), (0, -0.05, 0.35 - 0.6, 0.48, 0.003, 0.02),
                                 (-0.48, -0.05, 0.35, 0.02, 0.003, 0.6), (0.48, -0.05, 0.35, 0.02, 0.003, 0.6)], red)
    tx = L.text3d("ONE PLATE", loc=(0, -0.05, -0.42), size=0.13, extrude=0.002, mat=red, name="oneplate")
    H.key_vis([fr, tx], [(1, False), (52, True)])
    # v2 (QC fix): the desk lamp cast a crisp black copy of the raised red text/frame onto the board, which read as a
    # second, misregistered "ONE PLATE". The red frame + its label cast no shadow now, so the label renders once.
    for o in (fr, tx):
        o.visible_shadow = False
    lamp = L.spot((-1.6, -2.2, 2.6), (0, 0, 0), energy=900, size_deg=60, blend=0.8, color=(1.0, 0.78, 0.5), name="desklamp")
    H.aim(lamp, (-1.6, -2.2, 2.6), (0.0, 0, 0.5))
    c = H.cam((0.0, -4.4, 0.85), (0.0, 0, 0.78), lens=50)
    H.cam_move(c, [(1, (0.0, -4.4, 0.85), (0.0, 0, 0.78)), (n, (0.0, -3.9, 0.82), (0.0, 0, 0.76))], ease=False)
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S12 grease on the lens / someone on the stairs
def S12(L, n):
    _stairs(L, day=True, window=1.0)
    man = H.figure("walker", height=1.75, cap=True, color=(0.03, 0.028, 0.026))
    mm = man["torso"].data.materials[0]
    mm.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.6
    mm.surface_render_method = "BLENDED"
    man["root"].rotation_euler = (0, 0, math.pi)
    a, b = H.step_pos(12), H.step_pos(5)
    H.walk(man, 1, n - 1, stride=0.35, rate=1.0, travel=((0.1, a[1], a[2]), (0.1, b[1], b[2])), bob=0.02)
    cp = Vector((-0.1, -4.2, 1.6))
    tgt = Vector((0.05, 2.3, 1.95))
    d = (tgt - cp).normalized()
    # lens glass in front of the camera with a pale grease smear
    lens_c = cp + d * 0.3
    gm, gn, gl = H._nodes("grease")
    gp = gn["Principled BSDF"]
    gp.inputs["Base Color"].default_value = (0.9, 0.88, 0.8, 1)
    gp.inputs["Roughness"].default_value = 0.6
    nz = gn.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 8
    tc = gn.new("ShaderNodeTexCoord")
    mp = gn.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1, 1, 6)
    gl.new(tc.outputs["Object"], mp.inputs["Vector"])
    gl.new(mp.outputs[0], nz.inputs["Vector"])
    rp = H._ramp(gn, [(0.45, (0, 0, 0)), (0.75, (0.5, 0.5, 0.5))])
    gl.new(nz.outputs["Fac"], rp.inputs[0])
    gl.new(rp.outputs[0], gp.inputs["Alpha"])
    gm.surface_render_method = "BLENDED"
    disc = L.prim("cyl", loc=tuple(lens_c), vertices=40, radius=0.06, depth=0.003)
    disc.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    L.assign(disc, gm)
    ring = L.prim("torus", loc=tuple(lens_c), major_radius=0.066, minor_radius=0.01)
    ring.rotation_euler = disc.rotation_euler
    L.assign(ring, H.mat_brass("ringb"))
    c = H.cam(tuple(cp), tuple(tgt), lens=85)
    c.data.dof.use_dof = True
    c.data.dof.aperture_fstop = 2.0
    c.data.dof.focus_distance = 0.3
    c.data.dof.keyframe_insert("focus_distance", frame=1)
    c.data.dof.keyframe_insert("focus_distance", frame=int(n * 0.35))
    c.data.dof.focus_distance = 6.5
    c.data.dof.keyframe_insert("focus_distance", frame=int(n * 0.55))
    H.cam_move(c, [(1, tuple(cp), tuple(tgt)), (n, tuple(cp + d * 0.04), tuple(tgt))], ease=False)
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S13 empty staircase (dead air)
def S13(L, n):
    _stairs(L, window=1.0, vol=0.02)
    c = H.cam(S01_P1, S01_T1, lens=35)
    H.cam_move(c, [(1, S01_P1, S01_T1), (n, S01_P1, S01_T1)])
    L.cam_light(c, energy=12, color=(0.75, 0.8, 0.95))
    H.crisp_shadows()
    L.bake_static()


# --------------------------------------------------------------------------- S14 reveal flash + loop back to S01 start
def S14(L, n):
    _stairs(L, window=1.0, vol=0.02)
    fl = 6
    s3 = H.step_pos(3)
    near = _lady("lady_near", (0.0, s3[1], s3[2]), alpha=0.45, emit=1.6)
    H.key_vis(near["root"].children_recursive + [near["root"]], [(1, False), (fl, True), (fl + 9, False)])
    H.key_principled(near["mat"], "Emission Strength", [(fl, 1.8), (fl + 8, 0.4)])
    far = _lady("lady_land14", LADY_LANDING, alpha=0.28, emit=0.35)
    H.key_vis(far["root"].children_recursive + [far["root"]], [(1, False), (fl + 9, True)])
    c = H.cam(S01_P1, S01_T1, lens=35)
    H.cam_move(c, [(1, S01_P1, S01_T1), (fl + 10, S01_P1, S01_T1), (n, S01_P0, S01_T0)])
    L.cam_light(c, energy=12, color=(0.75, 0.8, 0.95))
    H.flash_pop(c, fl, peak=900, decay=10)
    H.crisp_shadows()
    L.bake_static()
