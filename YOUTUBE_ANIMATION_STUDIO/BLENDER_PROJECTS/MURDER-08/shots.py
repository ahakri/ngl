"""MURDER-08 - "Who put Bella in the Wych Elm?" (Hagley Wood, Worcestershire, 1943).
Shot builders: def SXX(L, n). Reusable builders live in PIPELINE/blender/lib_murder.py (MURDER-08 block: sooty brick, setts,
single-stroke chalk lettering, blackout lamp, sandbags, boarded street front, wych elm, hollow interior, season ground, obelisk,
archive racking, flat height-chart figure, stamp mark, ladder, canvas screen, evidence props, wind grass, falling leaves) and in
lib_haunted.py (faceless figures, helmets, hand torch, bare forest).

Rules for this film: the woman is never shown. The hollow of the elm is darkness only (black, unlit) - no remains, nothing inside
the tree, in any shot. The four boys are small faceless figures seen from behind and are never identified. Evidence props (S10) are
generic. Chalk / paint wording = the documented variants only (S01/S20 Birmingham 1944 wording, S12 "Hagley Wood Bella", S19 obelisk).

World layouts.  STREET: brick front in the XZ plane at y=0 facing -Y, pavement y -2.2..0, setts beyond; chalk question at x=0.
WOOD: the elm at the origin, cameras approach from -Y, low sun behind the tree.  BOARD: cork board in the XZ plane at y=0,
theory card A at x=-0.75, card B at x=0.55.
"""
import os, sys, math, random, importlib
_HERE = os.path.dirname(os.path.abspath(__file__))
_LIB = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import lib_murder as M
import lib_haunted as H
import lib_scuba as SC
import studio_lib as L
importlib.reload(M)
importlib.reload(H)
import bpy
from mathutils import Vector, noise

R = math.radians
MARKS = {}  # debug: named world points, projected by the dry-run tool (not used by the renderer)


def mark(**pts):
    MARKS.update(pts)


def cam_shot(n, p0, t0, p1, t1, lens=35, ease=False, lens1=None, f0=1):
    c = H.cam(p0, t0, lens=lens)
    H.cam_move(c, [(f0, p0, t0, None, lens if lens1 else None), (n, p1, t1, None, lens1)], ease=ease)
    return c


def no_shadow(light):
    light.data.use_shadow = False
    return light


def aimed_area(loc, target, energy, size, color, name, shadow=False):
    a = L.area(loc, (0, 0, 0), energy=energy, size=size, color=color, name=name)
    H.aim(a, loc, target)
    a.data.use_shadow = shadow
    return a


def aimed_spot(loc, target, energy, size_deg, color, name, blend=0.6, radius=0.05):
    s = L.spot(loc, (0, 0, 0), energy=energy, size_deg=size_deg, blend=blend, color=color, name=name, radius=radius)
    H.aim(s, loc, target)
    return s


def lamp_buzz(lamp, n, base, dips=(), depth=0.07, seed=2, glow=0.03):
    """Blackout lamp buzz: small per-frame ripple, dips = [(f0, f1, level)]. Frames 1 and n sit at exactly `base` (loop match)."""
    rnd = random.Random(seed)
    em = next(nd for nd in lamp["bulb_mat"].node_tree.nodes if nd.type == "EMISSION")
    for f in range(1, n + 1):
        k = 1.0 if f in (1, n) else 1.0 - depth * rnd.random()
        for a, b, lv in dips:
            if a <= f <= b:
                k = lv * (0.8 + 0.4 * rnd.random())
        lamp["spot"].data.energy = base * k
        lamp["spot"].data.keyframe_insert("energy", frame=f)
        lamp["glow"].data.energy = base * glow * k
        lamp["glow"].data.keyframe_insert("energy", frame=f)
        em.inputs[1].default_value = 14.0 * k
        em.inputs[1].keyframe_insert("default_value", frame=f)
    for idb in (lamp["spot"].data, lamp["glow"].data, lamp["bulb_mat"].node_tree):
        for fc in L._fcurves(idb.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def motes(n, center, size, count=200, radius=0.0022, drift=(0.012, 0.0, -0.015), color=(1.0, 0.85, 0.65), emit=0.5, seed=5, name="motes"):
    m = L.mat_principled(name + "_m", color, rough=1, emit=color, emit_strength=emit)
    return L.particle_cloud(center, size, count=count, radius=radius, drift=drift, seed=seed, nframes=n, name=name, mat=m)


# ============================================================================= STREET (S01, S02, S13, S20)

TEXT_LINES = ["WHO PUT", ("BELLA", 1.45), "DOWN THE", "WYCH ELM", ("- HAGLEY WOOD", 0.55)]
TEXT_TOP = (0.0, 0.0, 2.42)
LAMP_AT = (1.55, 0.0, 3.55)


def street(L, n, lamp_e=800.0, fog=0.028, opposite=False, moon_e=0.1, fill=70.0, stars=0.5):
    M.night_sky(stars=stars, hor=(0.02, 0.026, 0.05), zen=(0.003, 0.004, 0.011))
    M.moon(rot=(R(58), 0, R(-140)), energy=moon_e, color=(0.5, 0.6, 1.0), angle=2.0)
    F = M.blackout_facade("frontA", brick=M.mat_sooty_brick("brickA"))
    M.blackout_facade("frontL", x0=-19.5, x1=-7.12, h=9.3, up=((-16.4, 1.2), (-13.3, 1.2), (-10.2, 1.2)), down=((-16.4, 1.4), (-10.2, 1.4)),
                      door=(-13.3, 1.1), floor_h=4.3, seed=5, brick=M.mat_sooty_brick("brickL", c1=(0.06, 0.03, 0.025), c2=(0.1, 0.05, 0.036), soot=0.7))
    M.blackout_facade("frontR", x0=7.12, x1=21.0, h=6.5, up=((9.6, 1.2), (13.4, 1.2), (17.2, 1.2)), down=((9.6, 1.6), (17.2, 1.6)),
                      door=(13.4, 1.1), floor_h=3.4, seed=9, brick=M.mat_sooty_brick("brickR", c1=(0.075, 0.04, 0.026), c2=(0.12, 0.066, 0.04), soot=0.65))
    flag = L.mat_noise_surface("flags", (0.02, 0.02, 0.022), (0.075, 0.075, 0.075), scale=5, bump=0.25, voronoi=True, rough=0.35)
    H.box_mesh("pavement", [(0.75, -1.1, 0.06, 21.0, 1.1, 0.06), (0.75, -2.26, 0.055, 21.0, 0.07, 0.065)], flag)
    H.ground_box("road", -45, 45, -14.0, -2.2, z=0.0, mat=M.mat_cobbles("setts"))
    if opposite:
        O = M.blackout_facade("frontO", x0=-24.0, x1=24.0, h=8.4, up=((-18, 1.2), (-12, 1.2), (-6, 1.2), (0, 1.2), (6, 1.2), (12, 1.2), (18, 1.2)),
                              down=((-15, 1.5), (-3, 1.5), (9, 1.5), (20, 1.5)), door=(3.0, 1.1), floor_h=4.0, seed=13,
                              brick=M.mat_sooty_brick("brickO", c1=(0.06, 0.035, 0.03), c2=(0.1, 0.055, 0.04), soot=0.7))
        O["obj"].rotation_euler = (0, 0, math.pi)
        O["obj"].location = (0, -9.4, 0)
        H.box_mesh("pavement2", [(0.0, -8.6, 0.06, 24.0, 0.8, 0.06)], flag)
    T = M.chalk_text(TEXT_LINES, loc=TEXT_TOP, height=0.2, seed=4, name="question")
    M.sandbags((-3.2, -0.17, 0.12), cols=4, rows=7, depth=2, taper=False, seed=4, name="sandbags")
    M.sandbags((3.7, -0.2, 0.12), cols=3, rows=3, depth=1, taper=True, seed=6, name="sandbags2")
    lamp = M.hooded_lamp(LAMP_AT, energy=lamp_e)
    if fill:
        aimed_area((-3.5, -5.5, 3.2), (0, 0, 1.6), fill, 4.0, (0.45, 0.55, 0.95), "coldfill")
    M.fog((0, -5, 4.5), (70, 24, 10), density=fog)
    return {"F": F, "lamp": lamp, "text": T}


S01_P0, S01_T0 = (0.15, -4.15, 0.95), (0.02, 0.0, 1.2)
S01_P1, S01_T1 = (-0.03, -3.8, 0.97), (-0.04, 0.0, 1.25)
S01_N = 51


def wall_shot(L, n, p0, t0, p1, t1, dips):
    S = street(L, n)
    lamp_buzz(S["lamp"], n, 800.0, dips=dips)
    c = cam_shot(n, p0, t0, p1, t1, lens=50)
    motes(n, (0.4, -1.3, 2.0), (2.6, 1.4, 2.2), count=220)
    b = S["text"]["bounds"]
    mark(text_top=(0, 0, TEXT_TOP[2] + b[3]), text_bot=(0, 0, TEXT_TOP[2] + b[2]), text_l=(b[0], 0, 1.7), text_r=(b[1], 0, 1.7),
         wall_base=(0, 0, 0.12), lamp=(LAMP_AT[0], -0.9, LAMP_AT[2] - 0.2))
    L.bake_static()
    return c


def S01(L, n):
    # COLD OPEN: the chalked question under one buzzing blackout lamp; linear push (the loop continues it)
    wall_shot(L, n, S01_P0, S01_T0, S01_P1, S01_T1, dips=((19, 22, 0.42), (29, 30, 0.6)))


def S20(L, n):
    # LOOP FRAME: same wall; linear push that ends exactly on S01's frame-1 pose (same per-frame speed as S01)
    k = (n - 1) / (S01_N - 1)
    back = tuple(S01_P0[i] + (S01_P0[i] - S01_P1[i]) * k for i in range(3))
    backt = tuple(S01_T0[i] + (S01_T0[i] - S01_T1[i]) * k for i in range(3))
    wall_shot(L, n, back, backt, S01_P0, S01_T0, dips=((34, 37, 0.45),))


def S02(L, n):
    # wider: the empty boarded building, taped windows, sandbags, deserted wet street
    S = street(L, n, fog=0.03, moon_e=0.5, fill=320.0)
    lamp_buzz(S["lamp"], n, 800.0, dips=((40, 43, 0.45),))
    c = cam_shot(n, (-2.4, -5.6, 1.5), (0.2, 0.0, 1.7), (-3.9, -8.8, 1.7), (0.3, 0.0, 2.1), lens=28)
    aimed_area((-9.0, -7.0, 9.0), (-2.0, 0.0, 5.5), 3200.0, 8.0, (0.4, 0.5, 0.95), "moonwash")
    b = S["text"]["bounds"]
    mark(text_top=(0, 0, TEXT_TOP[2] + b[3]), text_bot=(0, 0, TEXT_TOP[2] + b[2]), lamp=(LAMP_AT[0], -0.9, LAMP_AT[2] - 0.2),
         win_up=(0, 0, 5.45), parapet=(0, 0, 7.7), bags=(-4.3, -0.4, 0.6), door=(3.7, 0, 1.2))
    L.bake_static()


def S13(L, n):
    # the constable's torch sweeps the empty street and finds only the chalk; nobody in sight
    S = street(L, n, lamp_e=160.0, fog=0.026, opposite=True, moon_e=0.3, fill=130.0)
    lamp_buzz(S["lamp"], n, 160.0)
    aimed_area((-2.0, -8.0, 9.0), (2.0, 0.0, 3.0), 900.0, 8.0, (0.4, 0.5, 0.95), "moonwash13")
    far = M.hooded_lamp((19.0, 0.0, 3.6), energy=600.0, name="farlamp")
    M.chalk_text(["HAGLEY WOOD", ("BELLA", 1.3)], loc=(-6.3, 0.0, 2.25), height=0.2, seed=9, name="second")
    pc = H.figure("pc", height=1.83, coat=True, color=(0.012, 0.013, 0.018))
    H.custodian_helmet(pc)
    pc["root"].rotation_euler = (0, 0, R(-90))
    H.walk(pc, 1, n, stride=0.26, rate=0.75, travel=((-10.7, -3.75, 0.0), (-9.8, -3.75, 0.0)), skip=("armR",))
    sp = H.hand_torch(pc, "R", energy=3800, size_deg=24)
    tg = M.empty("beam_t", (-6.6, 0.0, 1.5))
    for f, p in ((1, (-6.6, 0.0, 1.7)), (int(n * 0.42), (-0.6, 0.0, 1.8)), (int(n * 0.62), (0.4, 0.0, 1.6)), (n, (4.4, 0.0, 1.3))):
        tg.location = p
        tg.keyframe_insert("location", frame=f)
    M.aim(sp, tg)
    for f, az in ((1, 38), (int(n * 0.5), 26), (n, 14)):
        H.pose_hold(pc, "R", shoulder=(R(64), 0, R(az)), elbow=(R(14), 0, 0), frame=f)
    c = cam_shot(n, (-13.6, -3.7, 1.6), (-5.5, 0.0, 1.55), (-12.9, -3.55, 1.6), (6.0, -1.0, 1.5), lens=28, ease=True)
    H.handheld(c, n, amp=0.008, rate=0.5, rot_amp=0.002)
    aimed_area((-8.0, -1.0, 4.0), (-10.2, -3.75, 1.3), 700.0, 2.0, (0.45, 0.55, 0.95), "pcrim")
    mark(pc_head=(-10.3, -3.75, 1.83), pc_feet=(-10.3, -3.75, 0.0), text=(0, 0, 1.75), second=(-6.3, 0, 2.0), far_lamp=(19, -0.9, 3.4),
         door=(3.7, 0, 1.2))
    L.bake_static()


# ============================================================================= S12 a different wall: the messages begin

def S12(L, n):
    M.night_sky(stars=0.3, hor=(0.02, 0.026, 0.05), zen=(0.003, 0.004, 0.011))
    brick = M.mat_sooty_brick("brick12", c1=(0.05, 0.036, 0.036), c2=(0.1, 0.064, 0.052), mortar=(0.085, 0.08, 0.075), soot=0.5)
    H.box_mesh("wall12", [(0.0, 0.2, 2.9, 6.5, 0.2, 2.9), (-2.75, -0.06, 2.9, 0.24, 0.06, 2.9), (3.05, -0.06, 2.9, 0.24, 0.06, 2.9)], brick)
    H.box_mesh("dado12", [(0.0, -0.006, 0.42, 6.5, 0.007, 0.42)], L.mat_noise_surface("tar", (0.008, 0.008, 0.009), (0.03, 0.03, 0.032), scale=6,
                                                                                bump=0.2, voronoi=False, rough=0.45))
    H.box_mesh("sill12", [(0.0, -0.03, 0.86, 6.5, 0.03, 0.03)], L.mat_principled("sill12_m", (0.05, 0.05, 0.048), rough=0.7))
    pipe = L.prim("cyl", loc=(2.25, -0.1, 2.9), vertices=10, radius=0.055, depth=5.8)
    L.assign(pipe, L.mat_principled("pipe12", (0.03, 0.034, 0.03), rough=0.5, metal=0.6))
    flag = L.mat_noise_surface("flags12", (0.02, 0.02, 0.022), (0.075, 0.075, 0.075), scale=5, bump=0.25, voronoi=True, rough=0.35)
    H.ground_box("pave12", -12, 12, -9, 0, z=0.0, mat=flag)
    lamp = M.hooded_lamp((-1.75, 0.0, 3.5), energy=850.0, name="lamp12")
    lamp_buzz(lamp, n, 850.0, dips=((52, 54, 0.5),))
    aimed_area((3.5, -5.0, 3.0), (0, 0, 1.6), 75.0, 4.0, (0.45, 0.55, 0.95), "coldfill12")
    W = M.chalk_text(["HAGLEY", "WOOD", ("BELLA", 1.28)], loc=(0.0, 0.0, 2.3), height=0.3, line_gap=0.33, width=0.014, seed=7, name="bella",
                     write=[(6, 34), (37, 56), (60, 92)])
    M.chalk_follow(W["sched"])
    M.chalk_dust(W["sched"], every=2)
    c = cam_shot(n, (0.25, -3.7, 1.2), (0.0, 0.0, 1.16), (0.1, -3.1, 1.28), (0.0, 0.0, 1.31), lens=35)
    H.handheld(c, n, amp=0.006, rate=0.6, rot_amp=0.002)
    M.fog((0, -3, 3), (26, 14, 7), density=0.025)
    b = W["bounds"]
    mark(text_top=(0, 0, 2.3 + b[3]), text_bot=(0, 0, 2.3 + b[2]), text_l=(b[0], 0, 1.7), text_r=(b[1], 0, 1.7), lamp=(-1.75, -0.9, 3.3))
    L.bake_static()


# ============================================================================= HAGLEY WOOD (S03, S04, S05, S07, S08)

def Hw(x, y):
    base = 0.55 * noise.noise(Vector((x * 0.03, y * 0.03, 0.7))) + 0.12 * noise.noise(Vector((x * 0.13, y * 0.13, 2.1)))
    b0 = 0.55 * noise.noise(Vector((0.0, 0.0, 0.7))) + 0.12 * noise.noise(Vector((0.0, 0.0, 2.1)))
    return (base - b0) * M.smoothstep(2.5, 10.0, math.hypot(x, y))


def _clear(x, y):
    return math.hypot(x, y) < 6.5 or (-44.0 < y < -4.0 and abs(x - 1.0) < 3.6)


def wood(L, fog=0.03, sun_e=1.2, sun_col=(0.75, 0.8, 1.0), sun_rot=(R(-76), 0, R(-30)), sky=None, sky_s=1.0, fill=500.0,
         fill_col=(0.5, 0.6, 0.9), green=0.1, leaves=False, scrub=True):
    sky = sky or dict(hor=(0.3, 0.33, 0.42), mid=(0.17, 0.21, 0.32), zen=(0.05, 0.075, 0.15))
    bg = M.dawn_sky(strength=sky_s, **sky)
    sun = L.sun(rot=sun_rot, energy=sun_e, color=sun_col, angle=3.0, name="lowsun")
    gm, gs = M.mat_season_ground("floor_m", green_amt=green)
    M.heightfield("floor", -95, 95, -95, 95, 96, 96, Hw, mat=gm)
    bark = L.mat_noise_surface("wbark", (0.03, 0.03, 0.03), (0.13, 0.125, 0.115), scale=6, bump=0.35, voronoi=False)
    H.bare_forest_z("near", [(-46, 46, -50, 42)], Hw, count=105, seed=11, height=(9.0, 17.0), mat=bark, depth=3, avoid=_clear)
    far = H.bare_forest_z("far", [(-115, 115, 42, 120), (-115, -46, -70, 42), (46, 115, -70, 42), (-115, 115, -115, -50)], Hw, count=230,
                          seed=5, height=(10.0, 20.0), mat=bark, depth=2)
    far.visible_shadow = False
    if scrub:
        sc = H.bare_forest_z("scrub", [(-32, 32, -42, 30)], Hw, count=80, seed=21, height=(1.2, 3.2), mat=bark, depth=2,
                             avoid=lambda x, y: math.hypot(x, y) < 4.2 or (-44.0 < y < -3.0 and abs(x - 1.0) < 2.6))
        sc.visible_shadow = False
    elm = M.wych_elm(loc=(0, 0, 0), height=2.7, radius=0.8, seed=8, leaves=leaves)
    if fill:
        aimed_area((-4.0, -11.0, 5.0), (0, 0, 1.6), fill, 6.0, fill_col, "woodfill")
    M.fog((0, 0, 3.0), (190, 190, 7.5), density=fog, color=(0.62, 0.68, 0.82))
    bpy.context.scene.eevee.volumetric_end = 120
    return {"elm": elm, "sun": sun, "bg": bg, "ground": gs, "bark": bark}


def boys(spots, heights=(1.42, 1.34, 1.48, 1.38)):
    """Four small faceless boys (1940s caps); never identified, always seen from behind."""
    out = []
    for i, (x, y, rz) in enumerate(spots):
        p = H.figure(f"boy{i}", height=heights[i % 4], cap=(i != 1), color=(0.014, 0.014, 0.018))
        p["root"].location = (x, y, Hw(x, y))
        p["root"].rotation_euler = (0, 0, rz)
        out.append(p)
    return out


def S03(L, n):
    # blue dusk: glide through the mist toward the squat old elm and its dark hollow
    W = wood(L, fog=0.017, sun_e=1.3, sky_s=0.9, fill=1500.0)
    c = cam_shot(n, (2.2, -24.0, 1.45), (0.0, 0.0, 1.5), (0.9, -10.6, 1.5), (0.0, 0.0, 1.75), lens=35)
    H.handheld(c, n, amp=0.01, rate=0.4, rot_amp=0.002)
    M.falling_leaves([(-2.2, -5.0, 4.2), (1.8, -3.5, 5.0), (3.0, -1.0, 4.5), (-1.0, -1.8, 5.5), (-3.2, -0.5, 3.8), (0.8, -6.0, 3.6)], 1, n,
                     fall=2.2, seed=3)
    mark(elm_base=(0, 0, 0), rim=(0, 0, 2.7), cleft=tuple(W["elm"]["cleft"]), shoots=(0, 0, 6.3))
    L.bake_static()


def S04(L, n):
    # under the map card, then: late afternoon, four boys walk into the wood toward the distant elm (seen from far behind)
    W = wood(L, fog=0.026, sun_e=2.2, sun_col=(1.0, 0.84, 0.62), sun_rot=(R(-74), 0, R(-34)),
             sky=dict(hor=(0.5, 0.46, 0.42), mid=(0.3, 0.33, 0.4), zen=(0.1, 0.14, 0.24)), sky_s=1.0, fill=0.0)
    B = boys([(-0.6, -23.0, 0.0), (0.2, -24.3, 0.0), (0.9, -22.6, 0.0), (1.6, -23.9, 0.0)])
    for i, p in enumerate(B):
        x, y = p["root"].location.x, p["root"].location.y
        dx = (-0.25, 0.1, -0.1, -0.3)[i]
        H.walk(p, 1, n, stride=0.36, rate=1.1 + 0.06 * i, travel=((x, y, Hw(x, y)), (x + dx, y + 4.6, Hw(x + dx, y + 4.6))))
    c = cam_shot(n, (3.9, -37.5, 1.7), (0.6, -21.0, -0.6), (3.6, -35.2, 1.7), (0.4, -18.5, -0.3), lens=50)
    H.handheld(c, n, amp=0.008, rate=0.4, rot_amp=0.0015)
    aimed_area((6.0, -40.0, 5.0), (0.5, -21.0, 1.0), 900.0, 6.0, (0.55, 0.62, 0.85), "boysfill")
    mark(boy_head=(0.2, -21.0, 1.4), boy_feet=(0.2, -21.0, 0.0), elm_base=(0, 0, 0), rim=(0, 0, 2.7), shoots=(0, 0, 6.3))
    L.bake_static()


CLIMB_A = R(-64)  # where the climber stands on the bole (angle in XY; the cleft faces -90 deg)


def S05(L, n):
    # one climbs the bole and looks down into the hollow; the other three watch from below. All from behind, far.
    W = wood(L, fog=0.015, sun_e=3.0, sun_col=(1.0, 0.8, 0.55), sun_rot=(R(-78), 0, R(-24)),
             sky=dict(hor=(0.6, 0.52, 0.44), mid=(0.34, 0.36, 0.42), zen=(0.11, 0.15, 0.25)), sky_s=1.0, fill=1300.0, fill_col=(0.6, 0.66, 0.85))
    elm = W["elm"]
    B = boys([(-1.15, -2.9, R(-14)), (0.15, -3.4, R(4)), (1.25, -2.7, R(22))])
    for i, p in enumerate(B):  # they look up at the climber
        p["neck"].rotation_euler = (R(22), 0, 0)
    B[2]["shoulderR"].rotation_euler = (R(20), 0, 0)
    B[2]["shoulderR"].keyframe_insert("rotation_euler", frame=28)
    B[2]["shoulderR"].rotation_euler = (R(118), 0, R(-10))
    B[2]["shoulderR"].keyframe_insert("rotation_euler", frame=44)
    B[2]["shoulderR"].keyframe_insert("rotation_euler", frame=n)
    # the climber, on a burr on the right shoulder of the bole
    rr = elm["rad"](CLIMB_A, 0.5) + 0.2
    cx, cy = rr * math.cos(CLIMB_A), rr * math.sin(CLIMB_A)
    k = H.figure("climber", height=1.4, cap=True, color=(0.014, 0.014, 0.018))
    heading = math.atan2(cx, -cy)  # face the centre of the trunk
    kr = k["root"]
    for f, z, lean in ((1, 0.9, 6), (30, 1.5, 10), (52, 1.58, 24), (n, 1.58, 27)):
        kr.location = (cx, cy, z)
        kr.rotation_euler = (R(-lean), 0, heading)
        kr.keyframe_insert("location", frame=f)
        kr.keyframe_insert("rotation_euler", frame=f)
    for f, sh, el in ((1, 150, 20), (30, 165, 25), (52, 120, 55), (n, 118, 58)):
        for tag, sg in (("L", -1), ("R", 1)):
            H.pose_hold(k, tag, shoulder=(R(sh), 0, R(8 * sg)), elbow=(R(el), 0, 0), frame=f)
    for f, hp in ((1, 55), (16, 10), (30, 40), (44, 5), (n, 5)):
        k["hipL"].rotation_euler = (R(hp), 0, 0)
        k["kneeL"].rotation_euler = (R(-hp * 1.2), 0, 0)
        k["hipL"].keyframe_insert("rotation_euler", frame=f)
        k["kneeL"].keyframe_insert("rotation_euler", frame=f)
    for f, nk in ((1, 10), (50, 5), (66, -38), (n, -40)):
        k["neck"].rotation_euler = (R(nk), 0, 0)
        k["neck"].keyframe_insert("rotation_euler", frame=f)
    burr = L.prim("ico", loc=(cx * 0.9, cy * 0.9, 1.35), subdivisions=2, radius=0.24)
    burr.scale = (1.0, 1.0, 0.7)
    L.assign(burr, elm["trunk"].data.materials[0])
    L.smooth(burr)
    c = cam_shot(n, (1.6, -13.2, 0.9), (0.0, 0.0, 1.0), (1.1, -9.6, 1.0), (0.0, 0.0, 1.25), lens=35)
    H.handheld(c, n, amp=0.008, rate=0.4, rot_amp=0.0015)
    M.falling_leaves([(-1.5, -4.0, 4.0), (2.0, -2.0, 4.8), (0.5, -5.5, 3.5)], 10, n, fall=2.0, seed=5)
    mark(elm_base=(0, 0, 0), rim=(0, 0, 2.7), cleft=tuple(elm["cleft"]), shoots=(0, 0, 6.3), climber_head=(cx * 0.4, cy * 0.4, 2.95), climber_feet=(cx, cy, 1.75),
         boy_head=(0.15, -3.4, 1.4), boy_feet=(0.15, -3.4, 0))
    L.bake_static()


def detective(name="detective", height=1.8):
    p = H.figure(name, height=height, coat=True, color=(0.016, 0.015, 0.016))
    hm = p["torso"].data.materials[0]
    brim = L.prim("cyl", loc=(0, 0, 0.2), vertices=18, radius=0.175, depth=0.02)
    crown = L.prim("cyl", loc=(0, 0, 0.265), vertices=18, radius=0.105, depth=0.13)
    for o in (brim, crown):
        L.assign(o, hm)
        o.parent = p["neck"]
    return p


def S07(L, n):
    # the search: constables with lanterns, a detective, a ladder on the bole, a canvas screen. Nothing from inside is shown.
    W = wood(L, fog=0.034, sun_e=0.45, sun_col=(0.6, 0.7, 1.0), sky=dict(hor=(0.3, 0.24, 0.24), mid=(0.12, 0.14, 0.24), zen=(0.03, 0.045, 0.1)),
             sky_s=0.75, fill=260.0)
    elm = W["elm"]
    M.wood_ladder((1.05, -1.6, Hw(1.05, -1.6)), (0.62, -0.74, 2.5))
    M.canvas_screen((-2.55, -1.5, Hw(-2.55, -1.5)), (-1.5, 0.75, Hw(-1.5, 0.75)), height=1.95)
    a = H.figure("pcA", height=1.82, color=(0.012, 0.013, 0.02))
    H.custodian_helmet(a)
    a["root"].location = (0.45, -2.0, Hw(0.45, -2.0))
    a["root"].rotation_euler = (0, 0, R(-8))
    a["neck"].rotation_euler = (R(20), 0, 0)
    H.pose_hold(a, "R", shoulder=(R(126), 0, R(-6)), elbow=(R(16), 0, 0))
    for f, yaw in ((1, -10), (int(n * 0.6), 12), (n, 6)):
        a["neck"].rotation_euler = (R(20), 0, R(yaw))
        a["neck"].keyframe_insert("rotation_euler", frame=f)
    bpy.context.view_layer.update()
    hand = a["elbowR"].matrix_world @ Vector((0, 0, -0.34 * 1.82 / 1.75))
    la, lpa = M.lantern((hand.x, hand.y, hand.z - 0.36), energy=420.0, name="lanA", flicker_n=n)
    b = H.figure("pcB", height=1.78, color=(0.012, 0.013, 0.02))
    H.custodian_helmet(b)
    p0, p1 = (3.7, -3.5), (2.1, -2.35)
    b["root"].rotation_euler = (0, 0, math.atan2(p0[0] - p1[0], p1[1] - p0[1]))
    H.walk(b, 1, n, stride=0.3, rate=0.8, travel=((p0[0], p0[1], Hw(*p0)), (p1[0], p1[1], Hw(*p1))), skip=("armR",))
    H.pose_hold(b, "R", shoulder=(R(28), 0, 0), elbow=(R(20), 0, 0))
    lb, lpb = M.lantern((0, 0, 0), energy=380.0, name="lanB", flicker_n=n)
    lb.parent = b["root"]
    lb.location = (0.3, 0.28, 0.5)
    d = detective()
    d["root"].location = (-1.35, -2.75, Hw(-1.35, -2.75))
    d["root"].rotation_euler = (0, 0, R(-16))
    d["neck"].rotation_euler = (R(14), 0, 0)
    for tag in ("L", "R"):
        H.pose_hold(d, tag, shoulder=(R(-14), 0, 0), elbow=(R(-25), 0, 0))
    # foreground trunks the camera slides behind
    for i, (x, r) in enumerate(((-1.9, 0.13), (0.0, 0.1), (2.6, 0.16))):
        t = L.prim("cyl", loc=(x, -11.5 + 0.4 * i, 7.0 + Hw(x, -11.5)), vertices=10, radius=r, depth=14.6)
        L.assign(t, W["bark"])
    c = cam_shot(n, (-3.4, -15.5, 1.5), (0.2, 0.0, 1.35), (0.8, -15.2, 1.55), (0.0, 0.0, 1.45), lens=50)
    H.handheld(c, n, amp=0.006, rate=0.4, rot_amp=0.0012)
    mark(elm_base=(0, 0, 0), rim=(0, 0, 2.7), cleft=tuple(elm["cleft"]), shoots=(0, 0, 6.3), pcA_head=(0.45, -2.0, 1.95), pcA_feet=(0.45, -2.0, 0),
         det_head=(-1.35, -2.75, 1.9), screen=(-2.0, -0.4, 1.0))
    L.bake_static()


def S08(L, n):
    # time-lapse on the elm: about eighteen months of days, nights and seasons; the bole stays still and dark
    W = wood(L, fog=0.022, sun_e=2.4, sun_col=(1.0, 0.86, 0.66), sky=dict(hor=(0.5, 0.5, 0.52), mid=(0.3, 0.35, 0.45), zen=(0.1, 0.16, 0.3)),
             sky_s=1.0, fill=420.0, leaves=True, scrub=False)
    elm, sun, bg, gs = W["elm"], W["sun"], W["bg"], W["ground"]
    # seasons from autumn 1941 to April 1943: (frame, snow, green)
    M.key_socket(gs["snow"], [(1, 0.0), (11, 0.0), (17, 0.9), (26, 0.85), (31, 0.0), (56, 0.0), (62, 0.95), (72, 0.9), (78, 0.0), (n, 0.0)])
    M.key_socket(gs["green"], [(1, 0.05), (28, 0.05), (36, 0.75), (46, 0.8), (53, 0.15), (76, 0.1), (n, 0.35)])
    lv = elm["leaves"]
    for f, s in ((1, 0.6), (32, 0.6), (39, 1.0), (49, 1.0), (54, 0.75), (n, 0.75)):
        lv.scale = (s, s, s)
        lv.keyframe_insert("scale", frame=f)
    for f, hid in ((1, True), (32, False), (54, True)):
        lv.hide_render = hid
        lv.keyframe_insert("hide_render", frame=f)
    cyc = 22.0
    for f in range(1, n + 1):
        u = ((f - 1) / cyc + 0.5) % 1.0          # 0 = midnight, 0.5 = noon (noon falls on frames 1, 23, 45, 67, 89)
        day = math.sin(math.pi * u) ** 1.4
        cold = 0.5 - 0.5 * math.cos(2 * math.pi * (f - 20) / 45.0)  # winters (f~20, f~65) colder light
        sun.data.energy = 2.6 * (0.05 + 0.95 * day)
        sun.data.color = (1.0, 0.82 + 0.1 * cold, 0.62 + 0.3 * cold)
        sun.rotation_euler = (R(-58 - 22 * abs(2 * u - 1)), 0, R(40 - 140 * u))
        sun.data.keyframe_insert("energy", frame=f)
        sun.data.keyframe_insert("color", frame=f)
        sun.keyframe_insert("rotation_euler", frame=f)
        bg.inputs[1].default_value = 0.12 + 0.95 * day
        bg.inputs[1].keyframe_insert("default_value", frame=f)
    snow = M.snowfall((0, -4, 4), (16, 14, 9), n, count=1400, radius=0.007, fall=3.0, wind=(1.0, 0.0, 0.0), seed=5, name="snowA",
                      cam=((0.6, -11.5, 1.45), (0.55, -10.9, 1.45)), clear=2.0)
    for f, v in ((1, True), (11, False), (27, True), (57, False), (73, True)):
        snow.hide_render = v
        snow.keyframe_insert("hide_render", frame=f)
    spots = [(-2.5 + 5.0 * random.Random(i).random(), -5.5 + 5.0 * random.Random(i + 40).random(), 3.2 + 2.6 * random.Random(i + 80).random())
             for i in range(12)]
    M.falling_leaves(spots, 1, 13, fall=3.0, seed=2, name="leafA")
    M.falling_leaves(spots, 46, 59, fall=3.0, seed=7, name="leafB")
    c = cam_shot(n, (0.6, -11.5, 1.45), (0.0, 0.0, 1.1), (0.55, -10.9, 1.45), (0.0, 0.0, 1.15), lens=50)
    mark(elm_base=(0, 0, 0), rim=(0, 0, 2.7), cleft=tuple(elm["cleft"]), shoots=(0, 0, 6.3))
    L.bake_static()


# ============================================================================= S06 looking up from inside the hollow

def S06(L, n):
    # POV from the dark inside the trunk, looking straight up: sky, rim, shoots; the boy leans in, then jerks back.
    # Nothing inside the trunk is shown - the camera only looks up.
    L.set_world((0.0, 0.0, 0.0), 0.0)
    Hh = M.hollow_interior(height=1.75, radius=0.66, seed=5)
    rz, ro = Hh["rim_z"], Hh["r_open"]
    m, nn, l = L._mat("sky_disc")
    for nd in list(nn):
        if nd.type == "BSDF_PRINCIPLED":
            nn.remove(nd)
    em = nn.new("ShaderNodeEmission")
    tc = nn.new("ShaderNodeTexCoord")
    gr = nn.new("ShaderNodeTexGradient")
    gr.gradient_type = "SPHERICAL"
    mp = nn.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.05, 0.05, 0.05)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])
    l.new(mp.outputs[0], gr.inputs["Vector"])
    rp = nn.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].position = 0.0
    rp.color_ramp.elements[0].color = (0.2, 0.26, 0.4, 1)
    rp.color_ramp.elements[1].position = 1.0
    rp.color_ramp.elements[1].color = (0.62, 0.64, 0.66, 1)
    l.new(gr.outputs["Fac"], rp.inputs["Fac"])
    l.new(rp.outputs["Color"], em.inputs[0])
    em.inputs[1].default_value = 1.6
    l.new(em.outputs[0], nn["Material Output"].inputs["Surface"])
    sky = L.prim("plane", loc=(0, 0, rz + 9.0), size=80)
    L.assign(sky, m)
    sky.visible_shadow = False
    # daylight falling into the hollow lights only the upper wall; it dies away to black toward the lens
    L.area((0, 0, rz + 0.25), (0, 0, 0), energy=7.0, size=0.8, color=(0.75, 0.82, 1.0), name="skylight")
    L.point((0, 0.0, rz - 0.55), energy=0.8, color=(0.7, 0.78, 1.0), radius=0.2, name="bounce")
    boy = H.figure("boy_top", height=1.4, cap=True, color=(0.01, 0.01, 0.012))
    br = boy["root"]
    by = ro + 0.42
    br.rotation_euler = (0, 0, math.pi)  # faces -Y, toward the opening
    lean_in, f_in, f_out = 82, 15, 27
    for f, y, z, lean, nk in ((1, by + 0.5, rz - 1.05, 18, 0), (f_in, by, rz - 0.78, lean_in, -30), (f_out - 1, by + 0.01, rz - 0.78, lean_in + 2, -34),
                              (f_out + 4, by + 0.55, rz - 0.9, 8, 10), (f_out + 8, by + 1.4, rz - 1.0, -10, 10), (n, by + 1.4, rz - 1.0, -10, 10)):
        br.location = (0.06, y, z)
        br.keyframe_insert("location", frame=f)
        boy["pelvis"].rotation_euler = (R(-lean), 0, 0)
        boy["pelvis"].keyframe_insert("rotation_euler", frame=f)
        boy["neck"].rotation_euler = (R(nk), 0, 0)
        boy["neck"].keyframe_insert("rotation_euler", frame=f)
        for tag, sg in (("L", -1), ("R", 1)):
            H.pose_hold(boy, tag, shoulder=(R(30), 0, R(18 * sg)), elbow=(R(30), 0, 0), frame=f)
    M.set_interp(br, "LINEAR")
    cz = rz - 1.3
    c = cam_shot(n, (0.0, 0.03, cz), (0.0, -0.3, rz), (0.0, 0.03, cz + 0.07), (0.0, -0.29, rz), lens=18)
    mt = L.mat_principled("dust6_m", (0.9, 0.9, 0.95), rough=1, emit=(0.8, 0.85, 1.0), emit_strength=0.5)
    L.particle_cloud((0, 0, rz - 0.3), (0.7, 0.7, 0.7), count=110, radius=0.0016, drift=(0.0, 0.0, -0.12), seed=6, nframes=n, name="dust6", mat=mt)
    M.falling_leaves([(0.12, -0.1, rz + 0.3)], f_out + 2, n + 20, fall=1.0, drift=(-0.1, 0.12), size=0.045, seed=4, name="leaf6",
                     color=(0.1, 0.07, 0.03))
    mark(open_c=(0, 0, rz), open_n=(0, ro, rz), open_s=(0, -ro, rz), open_e=(ro, 0, rz), boy_head=(0.06, 0.1, rz + 0.05))
    L.bake_static()


# ============================================================================= S09 height chart

FT = 0.3048


def S09(L, n):
    L.set_world((0.004, 0.005, 0.007), 1.0)
    wallm = L.mat_noise_surface("stwall", (0.085, 0.095, 0.09), (0.15, 0.16, 0.145), scale=3, bump=0.15, voronoi=False, rough=0.85)
    H.box_mesh("wall9", [(0, 0.1, 2.0, 5.0, 0.1, 2.0)], wallm)
    H.box_mesh("dado9", [(0, -0.006, 0.4, 5.0, 0.007, 0.4), (0, -0.02, 0.82, 5.0, 0.02, 0.025)],
               L.mat_noise_surface("stdado", (0.016, 0.034, 0.026), (0.035, 0.066, 0.05), scale=4, bump=0.1, voronoi=False, rough=0.5))
    H.ground_box("floor9", -5, 5, -8, 0, z=0.0, mat=M.mat_planks("floor9_m", c1=(0.03, 0.022, 0.015), c2=(0.085, 0.06, 0.04), width=0.14, axis="X"))
    H.box_mesh("panel9", [(0, -0.004, 1.5, 1.0, 0.004, 0.66)], L.mat_noise_surface("panel9_m", (0.035, 0.045, 0.045), (0.06, 0.075, 0.07), scale=6,
                                                                             bump=0.08, voronoi=False, rough=0.85))
    ink = L.mat_principled("chart_ink", (0.6, 0.58, 0.5), rough=0.8, emit=(0.6, 0.58, 0.5), emit_strength=0.25)
    lines = []
    k = 6
    while k * FT / 2 <= 2.1:
        z = k * FT / 2
        if z > 0.9:
            foot = (k % 2 == 0)
            lines.append((0.12 if foot else 0.3, -0.009, z, 0.84 if foot else 0.6, 0.002, 0.007 if foot else 0.004))
        k += 1
    H.box_mesh("chart_lines", lines, ink)
    for ft in (4, 5, 6):
        t = L.text3d(f"{ft} FT", loc=(-0.93, -0.011, ft * FT + 0.02), size=0.085, extrude=0.0, mat=ink, name=f"ft{ft}", align="LEFT")
        t.data.font = M._font(M.F_ANTON) or t.data.font
    fig = M.flat_figure(5 * FT, color=(0.34, 0.34, 0.36))
    fig.location = (2.1, -0.045, 0.0)
    fig.keyframe_insert("location", frame=1)
    fig.location = (0.14, -0.045, 0.0)
    fig.keyframe_insert("location", frame=22)
    red = L.mat_emission("red9", (0.9, 0.05, 0.03), 2.2)
    bar = H.box_mesh("mark5", [(0.12, -0.02, 5 * FT, 0.86, 0.003, 0.009), (-0.7, -0.02, 5 * FT, 0.05, 0.003, 0.03), (0.95, -0.02, 5 * FT, 0.05, 0.003, 0.03)], red)
    bar.visible_shadow = False
    M.hide_until(bar, 24)
    aimed_spot((0.7, -2.7, 3.3), (0.1, 0.0, 1.35), 520.0, 62, (0.85, 0.9, 1.0), "overhead", blend=0.7, radius=0.12)
    aimed_area((-2.5, -3.0, 1.6), (0, 0, 1.3), 40.0, 2.0, (0.5, 0.6, 0.9), "fill9")
    c = cam_shot(n, (0.25, -5.2, 1.25), (0.1, 0.0, 1.02), (0.2, -4.5, 1.28), (0.1, 0.0, 1.05), lens=50)
    mark(head=(0.14, 0, 5 * FT), feet=(0.14, 0, 0), six=(0.14, 0, 6 * FT), four=(0.14, 0, 4 * FT), panel_l=(-1.0, 0, 1.5), panel_r=(1.0, 0, 1.5))
    L.bake_static()


# ============================================================================= S10 evidence table (generic props)

def S10(L, n):
    L.set_world((0.002, 0.002, 0.003), 1.0)
    M.desk(size=(1.6, 1.3))
    blot = M.rounded_box((0.0, 0.0, 0.002), (0.37, 0.3, 0.004), (0.045, 0.06, 0.05), bevel=0.2, name="blotter")
    M.plain_shoe((-0.135, 0.045, 0.004), rot_z=R(8))
    pad = M.rounded_box((0.105, -0.06, 0.009), (0.085, 0.085, 0.012), (0.5, 0.48, 0.42), bevel=0.3, name="pad")
    M.gold_ring((0.105, -0.06, 0.0165))
    M.striped_scrap((-0.08, -0.07, 0.004), size=(0.125, 0.08), rot_z=R(-9))
    M.paper_tag((0.12, 0.105, 0.005), rot_z=R(-12), string_to=(0.07, 0.07, 0.03), name="tagA")
    M.paper_tag((0.125, -0.005, 0.005), rot_z=R(6), string_to=(0.108, -0.05, 0.018), name="tagB")
    M.paper_tag((-0.02, -0.118, 0.005), rot_z=R(-4), string_to=(-0.06, -0.085, 0.008), name="tagC")
    M.desk_lamp((0.42, 0.36, 0.0), (0.0, 0.0, 0.0), energy=42.0, rot_z=R(-45))
    no_shadow(L.area((-0.2, -0.1, 0.9), (0, 0, 0), energy=5.0, size=0.8, color=(0.55, 0.65, 0.95), name="cool10"))
    c = H.cam((0.0, -0.18, 0.92), (0.0, -0.18, 0.0), lens=50)
    for f, z, roll in ((1, 0.92, R(-3.0)), (n, 0.86, R(3.0))):
        c.location = (0.0, -0.18, z)
        c.rotation_euler = (0.0, 0.0, roll)
        c.keyframe_insert("location", frame=f)
        c.keyframe_insert("rotation_euler", frame=f)
    L.linear_fcurves(c)
    motes(n, (0.0, 0.0, 0.16), (0.5, 0.5, 0.26), count=110, radius=0.0011, drift=(0.004, 0.002, 0.004), emit=0.4, name="motes10")
    mark(shoe_heel=(-0.135, 0.045, 0.03), shoe_toe=(0.108, 0.079, 0.02), ring=(0.105, -0.06, 0.017), scrap=(-0.08, -0.07, 0.004),
         bottom_tag=(-0.02, -0.118, 0.005))
    L.bake_static()


# ============================================================================= S11 the record sheet: NAME stays blank

def S11(L, n):
    L.set_world((0.002, 0.002, 0.003), 1.0)
    M.desk(size=(1.6, 1.3))
    fd = M.case_folder((-0.03, 0.03, 0.0), rot_z=R(-3), size=(0.5, 0.36), label="")
    fd["cover"].rotation_euler = (0, R(-178), 0)
    sheet = M.empty("sheet", (0.0, 0.035, 0.046))
    sheet.rotation_euler = (0, 0, R(2))
    pg = L.prim("plane", loc=(0, 0, 0), size=1)
    pg.scale = (0.21, 0.297, 1)
    L.assign(pg, M.mat_paper("form_p", (0.74, 0.71, 0.6)))
    pg.parent = sheet
    ink = L.mat_principled("form_ink", (0.04, 0.035, 0.03), rough=0.8)
    grey = L.mat_principled("form_grey", (0.26, 0.24, 0.2), rough=0.9)
    bars, rules = [], []
    bars.append((0.0, 0.128, 0.0006, 0.07, 0.006, 0.0003))            # printed heading bar (no text)
    rules.append((0.02, 0.074, 0.0006, 0.065, 0.0007, 0.0003))        # the empty NAME rule
    y = 0.045
    rnd = random.Random(6)
    while y > -0.13:
        bars.append((-0.068, y, 0.0006, 0.018, 0.0028, 0.0003))
        bars.append((0.025 - 0.02 * rnd.random(), y, 0.0006, 0.045 + 0.018 * rnd.random(), 0.0028, 0.0003))
        rules.append((0.02, y - 0.006, 0.0006, 0.065, 0.0004, 0.0003))
        y -= 0.026
    H.box_mesh("form_bars", bars, grey, parent=sheet)
    H.box_mesh("form_rules", rules, ink, parent=sheet)
    t = L.text3d("NAME", loc=(-0.086, 0.076, 0.0008), rot=(0, 0, 0), size=0.013, extrude=0.0, mat=ink, name="name_lbl", align="LEFT")
    t.data.font = M._font(M.F_SERIF_B) or t.data.font
    t.parent = sheet
    tw = M.box_typewriter((0.02, 0.46, 0.0), rot_z=R(3))
    car = M.empty("carriage", (0.0, 0.0, 0.0), tw)
    H.box_mesh("car_bar", [(0, 0.15, 0.205, 0.27, 0.012, 0.012), (-0.26, 0.15, 0.225, 0.012, 0.02, 0.03), (0.26, 0.15, 0.225, 0.012, 0.02, 0.03)],
               L.mat_principled("car_m", (0.09, 0.095, 0.09), rough=0.3, metal=0.8), parent=car)
    stop = 20
    for f, x in ((1, -0.085), (6, -0.05), (7, -0.05), (12, -0.012), (13, -0.012), (stop - 1, 0.026), (stop, 0.03), (n, 0.03)):
        car.location = (x, 0, 0)
        car.keyframe_insert("location", frame=f)
    M.set_interp(car, "LINEAR")
    keys = [ch for ch in tw.children if ch.type == "MESH" and ch.location.y < 0.0 and 0.12 < ch.location.z < 0.19]
    rk = random.Random(3)
    f = 2
    while f < stop - 1 and keys:
        kk = rk.choice(keys)
        z0 = kk.location.z
        for ff, dz in ((f - 1, 0.0), (f, -0.008), (f + 2, 0.0)):
            kk.location.z = z0 + dz
            kk.keyframe_insert("location", index=2, frame=ff)
        kk.location.z = z0
        f += 3
    M.desk_lamp((0.4, 0.3, 0.0), (0.0, 0.1, 0.0), energy=9.0, rot_z=R(-60))
    no_shadow(L.area((-0.7, 0.2, 0.7), (0, R(-55), 0), energy=2.0, size=0.7, color=(0.5, 0.62, 0.95), name="window11"))
    c = cam_shot(n, (0.0, -0.5, 0.8), (0.0, 0.1, 0.0), (0.0, -0.45, 0.72), (0.0, 0.1, 0.0), lens=50)
    mark(name_line=(0.02, 0.11, 0.046), sheet_top=(0, 0.218, 0.046), sheet_bot=(0, -0.078, 0.046), keys=(0.02, 0.37, 0.15),
         carriage=(0.02, 0.6, 0.2))
    L.bake_static()


# ============================================================================= EVIDENCE BOARD (S14-S17)

CARD_A, CARD_B = (-0.75, 1.08), (0.55, 1.03)
CARD_SIZE = (1.1, 0.66)
NEWS_AT = (0.85, 1.66)
MARK_A = (CARD_A[0] + 0.2, -0.022, CARD_A[1] + 0.17)
MARK_B = (CARD_B[0] + 0.17, -0.022, CARD_B[1] - 0.2)
QMARKS = [(-1.27, 2.05), (-0.42, 2.14), (0.12, 1.9), (-1.3, 0.12), (-0.5, -0.02), (0.22, 0.14), (1.3, 0.22), (1.28, 2.25), (-0.9, -0.85),
          (0.5, -0.8)]


def board(L, n, stage):
    """stage 14: card A slams in at f8. 15: A is up. 16: A carries its DISMISSED mark; B slams in at f8, the newspaper is pinned
    at f34 and the string draws. 17: everything is up (B still unmarked)."""
    L.set_world((0.003, 0.003, 0.004), 1.0)
    B = M.evidence_board(w=3.2, h=5.0, lamp_energy=230)
    aimed_area((-2.5, -3.5, 1.0), (0, 0, 1.0), 22.0, 3.0, (0.5, 0.6, 0.85), "coldfill")
    M.qmark_cards(QMARKS, size=(0.38, 0.46))
    a = M.paper_card("WITCHCRAFT?", (CARD_A[0], -0.012, CARD_A[1]), size=CARD_SIZE, rot_y=-0.04, badge="THEORY", name="cardA", text_size=0.165)
    out = {"B": B, "a": a}
    if stage == 14:
        M.slam_in(a, 8, lead=6)
        M.hide_until(a, 2)
    if stage >= 16:
        out["markA"] = M.stamp_mark("DISMISSED", MARK_A, size=0.13, rot=-0.16, name="markA")
        b = M.paper_card("SPY RING?", (CARD_B[0], -0.012, CARD_B[1]), size=CARD_SIZE, rot_y=0.035, badge="THEORY", name="cardB", text_size=0.175)
        out["b"] = b
        nw = M.newspaper((NEWS_AT[0], -0.014, NEWS_AT[1]), size=(0.46, 0.32), name="clipping", masthead="")
        nw.rotation_euler = (R(90), R(-5), 0)
        nw.scale = (1.75, 1.75, 1.75)
        pin = L.prim("sphere", loc=(0, 0.14, 0.02), radius=0.012, segments=10, ring_count=6)
        L.assign(pin, L.mat_principled("pin_n", (0.6, 0.04, 0.03), rough=0.3))
        pin.parent = nw
        st = M.red_string([(CARD_B[0], -0.045, CARD_B[1] + 0.27), (NEWS_AT[0] + 0.02, -0.045, NEWS_AT[1] + 0.24)], name="string")
        out.update(news=nw, string=st)
        if stage == 16:
            M.slam_in(b, 8, lead=6)
            M.hide_until(b, 2)
            nw.scale = (0.02,) * 3
            nw.keyframe_insert("scale", frame=1)
            nw.keyframe_insert("scale", frame=33)
            nw.scale = (1.75 * 1.08,) * 3
            nw.keyframe_insert("scale", frame=37)
            nw.scale = (1.75,) * 3
            nw.keyframe_insert("scale", frame=40)
            M.hide_until(nw, 33)
            M.curve_draw(st, 38, 52)
            M.hide_until(st, 38)
    return out


def stamp_hit(n, target, f_hit, side=1, name="stamp", tilt=-0.16):
    """Rubber stamp comes in from the camera side, hits the card at f_hit (pad flat on the board, tilted like the mark it
    leaves) and lifts away."""
    st = SC.rubber_stamp((0, 0, 0), size=0.12, name=name)
    st.scale = (3.4, 3.4, 3.4)
    tx, tz = target
    keys = ((1, (tx + side * 0.9, -1.9, tz + 0.75), (R(70), tilt, R(side * 18))), (f_hit, (tx, -0.03, tz), (R(90), tilt, 0)),
            (f_hit + 3, (tx, -0.03, tz), (R(90), tilt, 0)), (f_hit + 12, (tx + side * 0.75, -1.5, tz + 0.95), (R(72), tilt, R(side * 14))),
            (f_hit + 20, (tx + side * 1.9, -2.6, tz + 1.9), (R(60), tilt, R(side * 25))), (n, (tx + side * 1.9, -2.6, tz + 1.9), (R(60), tilt, R(side * 25))))
    for f, loc, rot in keys:
        st.location = loc
        st.rotation_euler = rot
        st.keyframe_insert("location", frame=f)
        st.keyframe_insert("rotation_euler", frame=f)
    for fc in L._fcurves(st.animation_data.action):
        for kp in fc.keyframe_points:
            if kp.co[0] <= f_hit:
                kp.interpolation = "LINEAR"
    return st


def S14(L, n):
    # THEORY 1: the WITCHCRAFT? card slams onto the board among blank question cards
    board(L, n, 14)
    c = cam_shot(n, (CARD_A[0], -5.6, 0.75), (CARD_A[0], 0.0, 0.62), (CARD_A[0], -4.2, 0.55), (CARD_A[0], 0.0, 0.46), lens=50, ease=True)
    M.shake(c, [8], amp=0.014, decay=7)
    motes(n, (-0.5, -0.9, 1.0), (2.4, 0.9, 2.4), count=160, radius=0.002, drift=(0.008, 0, 0.008), emit=0.3, name="motes14")
    mark(cardA=(CARD_A[0], 0, CARD_A[1]), cardA_top=(CARD_A[0], 0, CARD_A[1] + 0.33), cardA_bot=(CARD_A[0], 0, CARD_A[1] - 0.33),
         cardA_l=(CARD_A[0] - 0.55, 0, CARD_A[1]), cardA_r=(CARD_A[0] + 0.55, 0, CARD_A[1]), lamp=(0, -0.9, 2.7))
    L.bake_static()


def S15(L, n):
    # macro: the red stamp comes down on the card: DISMISSED
    board(L, n, 15)
    hit = 7
    stamp_hit(n, (MARK_A[0], MARK_A[2]), hit, side=1)
    M.stamp_mark("DISMISSED", MARK_A, size=0.13, rot=-0.16, name="markA", frame=hit + 1)
    p0, t0 = (-2.35, -5.2, 0.55), (-0.72, 0.0, 0.965)
    p1 = tuple(p0[i] + (t0[i] - p0[i]) * 0.05 for i in range(3))
    c = cam_shot(n, p0, t0, p1, t0, lens=85)
    M.shake(c, [hit], amp=0.02, decay=8)
    mark(cardA=(CARD_A[0], 0, CARD_A[1]), cardA_top=(CARD_A[0], 0, CARD_A[1] + 0.33), cardA_bot=(CARD_A[0], 0, CARD_A[1] - 0.33),
         cardA_l=(CARD_A[0] - 0.55, 0, CARD_A[1]), cardA_r=(CARD_A[0] + 0.55, 0, CARD_A[1]))
    L.bake_static()


def S16(L, n):
    # THEORY 2: SPY RING? slams in beside the dismissed card; red string to a generic newspaper cutting (no masthead)
    board(L, n, 16)
    c = H.cam((0.12, -4.6, 0.6), (0.12, 0.0, 0.45), lens=50)
    H.cam_move(c, [(1, (0.12, -4.6, 0.6), (0.12, 0.0, 0.45)), (12, (0.14, -4.6, 0.6), (0.14, 0.0, 0.45)), (46, (0.55, -4.6, 0.6), (0.55, 0.0, 0.45)),
                   (n, (0.6, -4.3, 0.58), (0.6, 0.0, 0.47))], ease=True)
    M.shake(c, [8], amp=0.014, decay=7)
    mark(cardB=(CARD_B[0], 0, CARD_B[1]), cardB_top=(CARD_B[0], 0, CARD_B[1] + 0.33), cardB_bot=(CARD_B[0], 0, CARD_B[1] - 0.33),
         cardA=(CARD_A[0], 0, CARD_A[1]), news=(NEWS_AT[0], 0, NEWS_AT[1]), news_top=(NEWS_AT[0], 0, NEWS_AT[1] + 0.28),
         news_r=(NEWS_AT[0] + 0.4, 0, NEWS_AT[1]))
    L.bake_static()


def S17(L, n):
    # the stamp again: NEVER PROVEN; the lamp swings a little
    O = board(L, n, 17)
    hit = 6
    stamp_hit(n, (MARK_B[0], MARK_B[2]), hit, side=-1, tilt=0.14)
    M.stamp_mark("NEVER PROVEN", MARK_B, size=0.12, rot=0.14, name="markB", frame=hit + 1)
    lamp = O["B"]["lamp"]
    for f in range(1, n + 1, 2):
        a = 7.0 * math.exp(-max(0, f - hit) / 40.0) * math.sin((f - hit) * 0.42) if f >= hit else 0.0
        lamp.rotation_euler = (R(-28), R(a), 0)
        lamp.keyframe_insert("rotation_euler", frame=f)
    p0, t0 = (2.15, -5.2, 0.5), (0.53, 0.0, 0.915)
    p1 = tuple(p0[i] + (t0[i] - p0[i]) * 0.05 for i in range(3))
    c = cam_shot(n, p0, t0, p1, t0, lens=85)
    M.shake(c, [hit], amp=0.02, decay=8)
    mark(cardB=(CARD_B[0], 0, CARD_B[1]), cardB_top=(CARD_B[0], 0, CARD_B[1] + 0.33), cardB_bot=(CARD_B[0], 0, CARD_B[1] - 0.33),
         cardB_l=(CARD_B[0] - 0.55, 0, CARD_B[1]), cardB_r=(CARD_B[0] + 0.55, 0, CARD_B[1]))
    L.bake_static()


# ============================================================================= S18 archive: the gap on the shelf

def S18(L, n):
    L.set_world((0.003, 0.0035, 0.005), 1.0)
    A = M.archive_shelves(x0=-8.4, x1=8.4, y=0.0, levels=5, gap=(3, 8, 1), seed=7, name="rackA")
    Bk = M.archive_shelves(x0=-8.4, x1=8.4, y=0.0, levels=5, seed=12, name="rackB")
    Bk["obj"].rotation_euler = (0, 0, math.pi)
    Bk["obj"].location = (0, -2.5, 0)
    conc = L.mat_noise_surface("arch_floor", (0.03, 0.03, 0.032), (0.09, 0.09, 0.09), scale=5, bump=0.15, voronoi=False, rough=0.5)
    H.ground_box("floor18", -12, 12, -4, 1.5, z=0.0, mat=conc)
    H.box_mesh("walls18", [(0, 0.6, 1.6, 12, 0.05, 1.6), (0, -3.1, 1.6, 12, 0.05, 1.6), (0, -1.25, 3.05, 12, 2.0, 0.05), (10.5, -1.25, 1.6, 0.05, 2.0, 1.6)],
               L.mat_noise_surface("arch_wall", (0.03, 0.033, 0.035), (0.075, 0.08, 0.08), scale=3, bump=0.15, voronoi=False, rough=0.9))
    g = A["gap"]
    # strip lights along the aisle; the one over the gap flickers once
    tube_m = L.mat_emission("tube18", (0.75, 0.9, 1.0), 9.0)
    lights = []
    for i, x in enumerate((-5.6, -1.9, g.x + 0.4, 5.6)):
        tb = L.prim("cyl", loc=(x, -1.25, 2.93), vertices=8, radius=0.02, depth=1.1, rot=(0, R(90), 0))
        L.assign(tb, tube_m if i != 2 else L.mat_emission("tube18b", (0.75, 0.9, 1.0), 9.0))
        tb.visible_shadow = False
        la = L.area((x, -1.25, 2.86), (0, 0, 0), energy=150.0 if i == 2 else 60.0, size=0.5, color=(0.72, 0.86, 1.0), name=f"strip{i}")
        la.data.shape = "RECTANGLE"
        la.data.size = 1.0
        la.data.size_y = 0.12
        lights.append((la, tb))
    la, tb = lights[2]
    H.key_energy(la, [(1, 150), (21, 150), (22, 12), (24, 130), (25, 8), (27, 150), (n, 150)])
    H.key_emission(tb.active_material, [(1, 9), (21, 9), (22, 0.6), (24, 8), (25, 0.4), (27, 9), (n, 9)])
    void = H.box_mesh("gap_back", [(g.x, 0.44, g.z + 0.02, 0.2, 0.01, 0.22)], L.mat_principled("void18", (0.004, 0.004, 0.005), rough=1.0))
    tag = A["tag"]
    for f in range(1, n + 1, 3):
        tag.rotation_euler = (0, R(13.0 * math.exp(-f / 70.0) * math.sin(f * 0.33) + 6.0), 0)
        tag.keyframe_insert("rotation_euler", frame=f)
    c = H.cam((-3.4, -1.55, 1.5), (-0.8, 0.0, 1.45), lens=35)
    H.cam_move(c, [(1, (-3.4, -1.55, 1.5), (-0.8, 0.0, 1.45)), (36, (g.x - 0.75, -1.5, 1.55), (g.x - 0.02, 0.0, g.z - 0.2)),
                   (n, (g.x - 0.5, -1.3, 1.57), (g.x, 0.0, g.z - 0.18))], ease=True)
    motes(n, (g.x - 0.2, -0.45, 1.7), (1.6, 0.5, 1.2), count=140, radius=0.0014, drift=(0.006, 0.0, -0.01), color=(0.8, 0.9, 1.0), emit=0.4, name="motes18")
    mark(gap=tuple(g), gap_top=(g.x, 0, g.z + 0.2), gap_bot=(g.x, 0, g.z - 0.2), tag=(g.x - 0.05, 0, g.z + 0.15), top_shelf=(g.x, 0, A["top_z"]))
    L.bake_static()


# ============================================================================= S19 the obelisk and the painted question

def hill(x, y):
    r = math.hypot(x, y)
    return (-0.0017 * r * r + 0.5 * noise.noise(Vector((x * 0.03, y * 0.03, 3.3))) * M.smoothstep(6.0, 30.0, r)) * M.smoothstep(4.0, 14.0, r)


def S19(L, n):
    bg = M.dawn_sky(hor=(0.4, 0.3, 0.36), mid=(0.15, 0.2, 0.36), zen=(0.025, 0.045, 0.13), strength=1.0)
    L.sun(rot=(R(84), 0, R(-27)), energy=1.5, color=(1.0, 0.56, 0.26), angle=2.0, name="lastlight")
    grass = L.mat_noise_surface("hillgrass", (0.02, 0.03, 0.012), (0.075, 0.085, 0.035), scale=2.5, bump=0.3, voronoi=False, rough=1.0)
    M.heightfield("hill", -260, 260, -260, 260, 131, 131, hill, mat=grass)
    far = H.ground_box("valley", -3000, 3000, -3000, 3000, z=-95.0, mat=L.mat_principled("valley_m", (0.012, 0.018, 0.025), rough=1.0))
    O = M.obelisk(loc=(0, 0, -0.05), height=25.0, base=3.0, mat=L.mat_noise_surface("ob_stone", (0.07, 0.065, 0.055), (0.2, 0.185, 0.155), scale=1.6, bump=0.35, voronoi=True, rough=0.9))
    paint = M.mat_chalk("paint", color=(0.82, 0.82, 0.78), under=(0.3, 0.27, 0.22), skip=0.18, emit=0.06, scale=60.0)
    zt = O["ped_z1"] - 0.5
    P = M.chalk_text(["WHO PUT", "BELLA", "IN THE", "WITCH ELM"], loc=(0.0, O["ped_y"], zt), height=0.45, line_gap=0.36, width=0.03, seed=12,
                     jitter=0.8, mat=paint, name="painted", flat=0.12, slope=0.02)
    rnd = random.Random(8)
    spots = []
    for _ in range(1500):
        a, r = rnd.uniform(0, 6.283), rnd.uniform(75, 250)
        x, y = r * math.cos(a), r * math.sin(a)
        if y < -20 and abs(x) < 40:
            continue
        spots.append((x, y, hill(x, y) - 0.3, rnd.uniform(9, 17)))
    M.fast_conifers("woods", spots, mat=L.mat_principled("woods_m", (0.008, 0.012, 0.012), rough=1.0), seed=4)
    M.wind_grass("blades", -9, 9, -6.2, 3, zf=hill, count=6000, seed=4, h=(0.12, 0.3), wind=0.05, speed=0.3,
                 avoid=lambda x, y: abs(x) < 3.6 and abs(y) < 3.6, mat=L.mat_principled("blade_m", (0.09, 0.085, 0.035), rough=1.0))
    M.fog((0, 60, -32), (700, 700, 44), density=0.012, color=(0.5, 0.58, 0.8))
    bpy.context.scene.eevee.volumetric_end = 300
    aimed_area((-6.0, -12.0, 3.0), (0, O["ped_y"], 2.6), 250.0, 5.0, (0.55, 0.62, 0.9), "skyfill")
    b = P["bounds"]
    zc = zt + (b[2] + b[3]) / 2
    c = H.cam((0.8, -7.9, 1.0), (0.0, O["ped_y"], 1.4), lens=24)
    H.cam_move(c, [(1, (0.8, -7.9, 1.0), (0.0, O["ped_y"], 1.25)), (56, (0.65, -7.3, 1.25), (0.0, O["ped_y"], 1.45)),
                   (n, (1.5, -10.6, 3.1), (0.0, 0.0, 11.5))], ease=True)
    H.handheld(c, n, amp=0.006, rate=0.4, rot_amp=0.001)
    mark(text_top=(0, O["ped_y"], zt + b[3]), text_bot=(0, O["ped_y"], zt + b[2]), text_l=(b[0], O["ped_y"], zc), text_r=(b[1], O["ped_y"], zc),
         ped_top=(0, O["ped_y"], O["ped_z1"]), apex=(0, 0, 25.0), base=(0, -3.4, 0.0))
    L.bake_static()
