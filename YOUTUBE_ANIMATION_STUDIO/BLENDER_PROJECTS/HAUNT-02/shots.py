"""HAUNT-02 — The Real Room 217 (Stanley Hotel). One builder per shot: def Sxx(L, n)."""
import importlib, sys, os, math, random
_LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PIPELINE", "blender")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import lib_haunted as H
importlib.reload(H)
import bpy

CC = H.CORR_CAM
S01_N = 118
# S09 / S15 locked composition (orbit start)
BED_C = (-0.2, 0.3, 0.7)


def _orbit_pos(deg, r=2.5, h=1.75):
    a = math.radians(deg)
    return (BED_C[0] + r * math.cos(a), BED_C[1] + r * math.sin(a), h)


S09_P0 = _orbit_pos(-112)
S09_T = (BED_C[0] + 0.05, BED_C[1] + 0.2, 0.62)


def _night_world(L, c=(0.004, 0.005, 0.009)):
    H.eevee_quality()
    L.set_world(c, 1.0)


# --------------------------------------------------------------------------- S01 corridor cold open
def S01(L, n):
    _night_world(L)
    H.hotel_corridor(n, sconce_level=0.3, d217="ajar", spill=1.0)
    H.corridor_camera(n, "push", frac=1.0)
    L.bake_static()


# --------------------------------------------------------------------------- S02 hotel facade
def S02(L, n):
    H.eevee_quality()
    bpy.context.scene.eevee.volumetric_end = 140
    L.set_world((0.02, 0.03, 0.055), 1.0)
    H.hotel_facade(n)
    L.sun(rot=(1.0, 0.0, 2.8), energy=1.6, color=(0.6, 0.7, 1.0), angle=6)
    moon = L.prim("sphere", loc=(-40, 260, 120), segments=24, ring_count=12, radius=7)
    L.assign(moon, L.mat_emission("moonm", (0.8, 0.85, 1.0), 3))
    # layered fog cards in front of the mountains + volume around the hotel
    L.fog_volume(center=(0, -10, 10), size=(140, 110, 30), density=0.006, color=(0.7, 0.75, 0.85))
    H.snowfall((0, -25, 9), (40, 40, 22), n, count=1800, speed=1.2)
    p0, t0 = (0.0, -78.0, 24.0), (0.0, 0.0, 9.0)
    p1, t1 = (0.0, -50.0, 4.0), (0.0, 0.0, 10.5)
    c = H.cam(p0, t0, lens=35)
    H.cam_move(c, [(1, p0, t0), (n, p1, t1)])
    L.bake_static()


# --------------------------------------------------------------------------- S03 the dream: fire hose
def S03(L, n):
    _night_world(L, (0.003, 0.003, 0.004))
    s = H.hotel_corridor(n, mode="dream", sconce_level=0.55, d217="closed", spill=0.4, far_window=0.6, dust_count=300)
    for i, sc in enumerate(s["sconces"]):
        H.flicker_mat_with_light(sc["light"], sc["mat"], n, sc["light"].data.energy, 3.5 * 0.55, seed=i + 3, depth=0.9, rate=1.3,
                                 blackouts=((10, 13), (30, 33), (50, 52)))
    pts = []
    for k in range(40):
        y = 15.0 - k * (11.8 / 39)
        pts.append((0.45 * math.sin(y * 0.9) * (0.4 + 0.6 * (y - 3) / 12), y, 0.05))
    H.fire_hose(pts, n, start_frac=0.08, end_frame=n - 4)
    # small running shadow on the far wall (child figure never seen, only its shadow)
    ch = H.figure("runner", height=1.05)
    for o in [ch[k] for k in ch if hasattr(ch[k], "type") and ch[k].type == "MESH"]:
        o.visible_camera = False
    ch["root"].rotation_euler = (0, 0, -math.pi / 2)
    H.walk(ch, 1, n, stride=0.7, rate=2.2, travel=((-1.3, 22.0, 0), (1.3, 22.0, 0)))
    L.point((0.0, 19.5, 0.9), energy=250, color=(0.8, 0.88, 1.0), radius=0.02, name="shadowcaster")
    p0, t0 = (0.25, 1.4, 0.32), (0.0, 12.0, 0.7)
    c = H.cam(p0, t0, lens=20, roll=math.radians(12))
    H.cam_move(c, [(1, p0, t0, math.radians(12)), (n, (0.2, 1.75, 0.3), (0.05, 12.0, 0.65), math.radians(13))])
    H.handheld(c, n, amp=0.02, rate=0.9, rot_amp=0.01)
    L.cam_light(c, energy=8, color=(0.8, 0.85, 1.0))
    L.bake_static()


# --------------------------------------------------------------------------- S04 King at the window
def S04(L, n):
    _night_world(L)
    r = H.room217(n, lamp_on=True, lamp_energy=14, moon=1.0)
    w = H.figure("writer", height=1.8, coat=False)
    w["root"].location = (1.55, 0.6, 0)
    w["root"].rotation_euler = (0, 0, -math.pi / 2)
    H.pose_hold(w, "R", shoulder=(0.35, 0, 0.25), elbow=(2.0, 0, 0))
    em = L.mat_emission("ember", (1.0, 0.35, 0.08), 40)
    e = L.prim("sphere", loc=(0, 0, 0), segments=8, ring_count=6, radius=0.009)
    L.assign(e, em)
    e.parent = w["neck"]
    e.location = (0.16, 0.12, 0.06)
    el = L.point((0, 0, 0), energy=1.5, color=(1.0, 0.4, 0.1), radius=0.01, name="emberl")
    el.parent = w["neck"]
    el.location = (0.16, 0.16, 0.06)
    H.key_emission(em, [(f, 40 if (f // 18) % 2 == 0 else 70) for f in range(1, n + 1, 6)], interp="BEZIER")
    # smoke wisp
    sm = L.mat_principled("smoke", (0.7, 0.72, 0.78), rough=1, emit=(0.5, 0.55, 0.65), emit_strength=0.3, alpha=0.35)
    sm.surface_render_method = "BLENDED"
    base = (1.55 - 0.12 * 0 + 0.06, 0.6 + 0.16, 1.75)
    pts = [(base[0] + 0.03 * math.sin(k * 1.3), base[1] + 0.02 * math.cos(k), base[2] + 0.08 * k) for k in range(12)]
    wisp = L.guideline(pts, mat=sm, thickness=0.01, name="wisp")
    wisp.keyframe_insert("rotation_euler", frame=1)
    wisp.rotation_euler = (0.05, -0.08, 0.3)
    wisp.keyframe_insert("rotation_euler", frame=n)
    p0, t0 = (-1.25, 2.1, 1.7), (1.9, 0.35, 1.35)
    c = H.cam(p0, t0, lens=35)
    H.cam_move(c, [(1, p0, t0), (n, (-0.85, 1.85, 1.68), (1.9, 0.35, 1.38))])
    L.cam_light(c, energy=10, color=(0.6, 0.7, 1.0))
    L.bake_static()


# --------------------------------------------------------------------------- S05 corridor reverse angle
def S05(L, n):
    _night_world(L)
    H.hotel_corridor(n, sconce_level=0.12, d217="ajar", spill=1.6, far_window=0.35, fog=0.02, dust_count=300)
    p, t = (0.25, 22.6, 1.6), (0.5, 8.0, 1.15)
    c = H.cam(p, t, lens=28)
    c.data.keyframe_insert("lens", frame=1)
    c.data.lens = 28 * 1.03
    c.data.keyframe_insert("lens", frame=n)
    L.cam_light(c, energy=20, color=(0.6, 0.7, 1.0))
    L.bake_static()


# --------------------------------------------------------------------------- S06 1911: gas leak
def S06(L, n):
    H.eevee_quality()
    L.set_world((0.03, 0.022, 0.014), 1.0)
    r = H.room217(n, era="1911", gaslamp=True, dust_count=300)
    g = (-2.1 + 0.26, 0.9, 2.1)
    p0, p1 = (1.3, -1.7, 1.7), (0.3, -0.75, 1.85)
    p0, p1 = (1.6, -2.1, 1.65), (0.6, -1.0, 1.8)
    c = H.cam(p0, g, lens=30)
    H.cam_move(c, [(1, p0, g, None, 30), (n, p1, g, None, 50)])
    L.cam_light(c, energy=8, color=(1.0, 0.85, 0.6))
    L.bake_static()


# --------------------------------------------------------------------------- S07 1911: the chambermaid with a candle
def S07(L, n):
    H.eevee_quality()
    L.set_world((0.02, 0.015, 0.01), 1.0)
    r = H.room217(n, era="1911", gaslamp=True, dust_count=250)
    bpy.data.objects["daywin"].data.energy = 160
    bpy.data.objects["sepfill"].data.energy = 25
    d = r["door"]
    d.keyframe_insert("rotation_euler", frame=1)
    d.rotation_euler = (0, 0, math.radians(95))
    d.keyframe_insert("rotation_euler", frame=22)
    maid = H.figure("maid", height=1.62, dress=True, apron=True, color=(0.015, 0.013, 0.012))
    maid["root"].rotation_euler = (0, 0, math.radians(-10))
    H.walk(maid, 10, n - 10, stride=0.3, rate=0.8, travel=((-1.25, -3.1, 0), (-1.0, -1.0, 0)), skip=("armR",))
    maid["root"].location = (-1.25, -3.1, 0)
    maid["root"].keyframe_insert("location", frame=1)
    H.pose_hold(maid, "R", shoulder=(0.9, 0, 0.1), elbow=(0.6, 0, 0))
    cd = H.candle(parent=maid["elbowR"], loc=(0, 0, -0.32), energy=45)
    cd["root"].rotation_euler = (-1.5, 0, 0)
    H.flicker_mat_with_light(cd["light"], cd["flame"], n, 45, 25, seed=4, depth=0.25, rate=0.8)
    p, t = (1.75, 1.1, 1.6), (-1.1, -1.9, 1.05)
    c = H.cam(p, t, lens=35)
    H.cam_move(c, [(1, p, t), (n, (1.7, 1.0, 1.6), (-1.05, -1.75, 1.05))])
    L.cam_light(c, energy=6, color=(1.0, 0.85, 0.6))
    L.bake_static()


# --------------------------------------------------------------------------- S08 the blast (flash -> hole in the ceiling, from below)
def S08(L, n):
    H.eevee_quality()
    L.set_world((0.02, 0.018, 0.016), 1.0)
    W, D, Hh = 8.0, 8.0, 3.6
    wall = L.mat_principled("dinwall", (0.42, 0.36, 0.28), rough=0.8)
    fl = L.prim("plane", loc=(0, 0, 0), size=1)
    fl.scale = (W, D, 1)
    L.assign(fl, L.WOOD_OLD())
    ceil = H.box_mesh("dceil", [(0, 0, Hh + 0.15, W / 2, D / 2, 0.15)], L.mat_principled("dceilm", (0.5, 0.45, 0.36), rough=0.8))
    cut = L.prim("ico", loc=(0.0, 0.6, Hh + 0.15), subdivisions=3, radius=0.75)
    cut.scale = (1.3, 1.0, 0.6)
    L.add_displace(cut, strength=0.35, scale=0.25, name="holed")
    bo = ceil.modifiers.new("hole", "BOOLEAN")
    bo.object = cut
    bo.operation = "DIFFERENCE"
    cut.hide_render = True
    cut.hide_viewport = True
    H.box_mesh("dwalls", [(0, D / 2, Hh / 2, W / 2, 0.05, Hh / 2), (W / 2, 0, Hh / 2, 0.05, D / 2, Hh / 2), (-W / 2, 0, Hh / 2, 0.05, D / 2, Hh / 2),
                          (0, -D / 2, Hh / 2, W / 2, 0.05, Hh / 2)], wall)
    # room above (bright, smoky) seen through the hole
    H.box_mesh("above", [(0, 0.6, Hh + 2.2, 2.5, 2.5, 0.05)], L.mat_principled("abovem", (0.5, 0.45, 0.38)))
    sp = L.spot((0.0, 0.6, Hh + 2.0), (0, 0, 0), energy=1800, size_deg=60, blend=0.5, color=(1.0, 0.9, 0.75), name="holebeam", radius=0.3)
    H.room_fog((0, 0, Hh / 2 + 0.5), (W, D, Hh + 1), density=0.07, color=(0.8, 0.75, 0.68), name="dustfog")
    # dining tables + debris
    tm = L.mat_principled("tablecloth", (0.75, 0.72, 0.65), rough=0.9)
    for (x, y) in ((-2.0, 1.5), (2.2, 1.8), (-1.8, -1.6)):
        H.box_mesh(f"tab{x}", [(x, y, 0.75, 0.6, 0.6, 0.03), (x, y, 0.38, 0.05, 0.05, 0.37)], tm)
    rnd = random.Random(5)
    deb = [(rnd.uniform(-1.2, 1.2), 0.6 + rnd.uniform(-1, 1), 0.04, rnd.uniform(0.04, 0.15), rnd.uniform(0.03, 0.1), 0.03, rnd.uniform(0, 3)) for _ in range(30)]
    H.box_mesh("debris", deb, L.mat_principled("debm", (0.35, 0.3, 0.24), rough=0.9))
    dc = L.particle_cloud((0.0, 0.6, Hh + 1.5), (2.2, 2.2, 7.0), count=1800, radius=0.008,
                          mat=L.mat_principled("plaster_dust", (0.8, 0.76, 0.68), rough=1, emit=(0.6, 0.55, 0.45), emit_strength=0.15),
                          drift=(0.0, 0.0, -1.1), nframes=n, name="falling")
    # flash: white card in front of the lens, fading frames 1-7
    p, t = (2.2, -3.2, 0.7), (0.0, 0.5, Hh)
    c = H.cam(p, t, lens=24)
    fm = L.mat_emission("flash", (1.0, 0.97, 0.9), 60)
    fc = L.prim("plane", loc=(0, 0, -0.2), size=1)
    fc.parent = c
    L.assign(fc, fm)
    H.key_emission(fm, [(1, 60), (3, 40), (5, 12), (7, 2), (9, 0)], interp="LINEAR")
    H.key_vis(fc, [(1, True), (9, False)])
    fl_l = L.point((0, 0.6, Hh + 0.5), energy=0, color=(1, 0.95, 0.85), radius=0.5, name="flashl")
    H.key_energy(fl_l, [(1, 60000), (4, 20000), (8, 0)], interp="LINEAR")
    rnd = random.Random(2)
    for f in range(1, 16):
        k = (1 - f / 16) * 0.06
        c.location = (p[0] + rnd.uniform(-k, k), p[1] + rnd.uniform(-k, k), p[2] + rnd.uniform(-k, k))
        c.keyframe_insert("location", frame=f)
    c.location = p
    c.keyframe_insert("location", frame=16)
    L.cam_light(c, energy=8, color=(0.9, 0.85, 0.8))
    L.bake_static()


# --------------------------------------------------------------------------- S09 present day: suitcase closed, lamp flicks
def _room_present(L, n, case_state):
    _night_world(L)
    r = H.room217(n, case_state=case_state, lamp_on=True, lamp_energy=30, moon=0.8)
    return r


def S09(L, n):
    r = _room_present(L, n, "closed")
    dl = r["desklamp"]
    pairs = [(1, 24), (int(n * 0.24), 0), (int(n * 0.24) + 3, 24), (int(n * 0.42), 0), (int(n * 0.42) + 4, 24)]
    H.key_energy(dl["light"], pairs)
    H.key_emission(dl["shade_mat"], [(f, 1.6 if e else 0) for f, e in pairs])
    keys = [(1, S09_P0, S09_T), (n, _orbit_pos(-102), S09_T)]
    c = H.cam(S09_P0, S09_T, lens=28)
    H.cam_move(c, keys)
    L.cam_light(c, energy=12, color=(0.7, 0.75, 0.9))
    L.bake_static()


# --------------------------------------------------------------------------- S10 the faint chambermaid down the corridor
def S10(L, n):
    _night_world(L)
    s = H.hotel_corridor(n, sconce_level=0.0, d217="closed", spill=0.3, far_window=1.4, fog=0.035, dust_count=200)
    sc = H.sconce((-(H.CORR_W / 2 - 0.01), 18.25, 1.95), 1, level=0.6, name="onlysconce")
    maid = H.figure("ghostmaid", height=1.62, dress=True, apron=True, color=(0.08, 0.09, 0.11))
    for k, o in maid.items():
        if hasattr(o, "type") and o.type == "MESH":
            for m in o.data.materials:
                bs = m.node_tree.nodes["Principled BSDF"]
                bs.inputs["Alpha"].default_value = 0.32
                bs.inputs["Emission Color"].default_value = (0.4, 0.5, 0.7, 1)
                bs.inputs["Emission Strength"].default_value = 0.25
                m.surface_render_method = "BLENDED"
    maid["root"].location = (-0.45, 19.2, 0)
    maid["root"].rotation_euler = (0, 0, math.pi)
    H.linen_trolley((0.4, 19.5, 0), math.pi / 2)
    p, t = (0.1, -0.4, 1.55), (-0.1, 19.0, 1.05)
    c = H.cam(p, t, lens=85)
    H.cam_move(c, [(1, p, t), (n, (0.1, 0.0, 1.55), t)])
    L.bake_static()


# --------------------------------------------------------------------------- S11 / S13 evidence board
def _board(L, n, cards):
    H.eevee_quality()
    L.set_world((0.01, 0.01, 0.012), 1.0)
    H.box_mesh("bwall", [(0, 0.2, 0, 4, 0.05, 4)], L.mat_principled("bw", (0.05, 0.05, 0.055), rough=0.9))
    H.evidence_board("board", 2.4, 4.0)
    H.box_mesh("scraps", [(0.95, -0.006, 0.55, 0.2, 0.002, 0.26, 0.1), (-0.95, -0.006, -0.5, 0.22, 0.002, 0.16, -0.08),
                          (-0.85, -0.006, 1.0, 0.2, 0.002, 0.15, 0.05), (0.9, -0.006, -1.4, 0.25, 0.002, 0.2, -0.05)],
               H.mat_paper("scrap", (0.6, 0.57, 0.48)))
    k = L.spot((-2.2, -1.8, 3.2), (0, 0, 0), energy=1000, size_deg=50, blend=0.5, color=(1.0, 0.78, 0.5), name="desklamp", radius=0.1)
    H.aim(k, (-2.2, -1.8, 3.2), (0.1, 0, 0.3))
    L.area((0, -3, 0.5), (math.pi / 2, 0, 0), energy=8, size=3, color=(0.6, 0.7, 0.9), name="boardfill")
    return cards()


def _record_cards(n, animate=True):
    ink = L_.mat_principled("ink3", (0.04, 0.035, 0.03), rough=0.6)
    hdr = H.pinned_card("c_rec", (0.0, -0.012, 1.15), 1.5, 1.05, ["Survived the 1911 blast", "Two broken ankles", "Returned to work"],
                        header="WHAT THE RECORD SAYS", size=0.085, font_size_header=0.11, rot=math.radians(-1.2))
    # ankle + bandage icon
    icon = H.pinned_card("c_ankle", (-0.15, -0.012, 0.0), 0.95, 0.8, [], rot=math.radians(2.5), color=(0.84, 0.8, 0.7))
    H.box_mesh("leg", [(-0.05, -0.008, 0.08, 0.05, 0.002, 0.22), (0.07, -0.008, -0.14, 0.17, 0.002, 0.05)], ink, parent=icon)
    band = L_.mat_principled("bandage", (0.92, 0.9, 0.86), rough=0.9)
    H.box_mesh("band", [(-0.04, -0.012, z, 0.075, 0.002, 0.018, 0.0) for z in (-0.06, 0.0, 0.06)], band, parent=icon)
    H.box_mesh("bandr", [(-0.04, -0.013, z, 0.075, 0.001, 0.004) for z in (-0.03, 0.03)], L_.mat_principled("bandr", (0.6, 0.55, 0.5)), parent=icon)
    if animate:
        hdr.scale = (1.35, 1.35, 1.35)
        hdr.keyframe_insert("scale", frame=1)
        hdr.scale = (1, 1, 1)
        hdr.keyframe_insert("scale", frame=5)
        lines = [o for o in bpy.data.objects if o.name.startswith("c_rec_t")]
        for i, o in enumerate(sorted(lines, key=lambda o: o.name)):
            H.key_vis(o, [(1, False), (18 + 9 * i, True)])
    return hdr, icon


def S11(L, n):
    global L_
    L_ = L
    _board(L, n, lambda: _record_cards(n, True))
    c = H.cam((0.0, -4.4, 0.55), (0.0, 0, 0.45), lens=50)
    H.cam_move(c, [(1, (0.0, -4.4, 0.55), (0.0, 0, 0.45)), (n, (-0.03, -4.0, 0.55), (-0.03, 0, 0.47))], ease=False)
    L.bake_static()


def S13(L, n):
    global L_
    L_ = L

    def cards():
        _record_cards(n, False)
        fc = H.pinned_card("c_died", (0.1, -0.014, -1.0), 1.4, 0.8, ["DIED IN 217"], header="DIED HERE? NO.", size=0.13, font_size_header=0.14,
                           rot=math.radians(-1.5), color=(0.88, 0.85, 0.74))
        H.box_mesh("strike", [(0.0, -0.012, 0.05, 0.5, 0.002, 0.012)], L.mat_principled("strike", (0.75, 0.03, 0.02), rough=0.5), parent=fc)
        return fc
    _board(L, n, cards)
    c = H.cam((0.08, -4.0, -0.95), (0.1, 0, -1.35), lens=50)
    H.cam_move(c, [(1, (0.08, -4.0, -0.95), (0.1, 0, -1.35)), (n, (0.1, -3.6, -0.97), (0.1, 0, -1.37))])
    L.bake_static()


# --------------------------------------------------------------------------- S12 daylight: she goes back to work
def S12(L, n):
    H.eevee_quality()
    L.set_world((0.05, 0.04, 0.03), 1.0)
    H.hotel_corridor(n, mode="day", sconce_level=0.0, d217="closed", spill=0.0, fog=0.02, dust_count=400)
    L.area((0, 12, 2.9), (0, 0, 0), energy=600, size=6, color=(1.0, 0.9, 0.75), name="dayfill")
    maid = H.figure("daymaid", height=1.62, dress=True, apron=True, color=(0.03, 0.03, 0.035))
    H.walk(maid, 1, n, stride=0.32, rate=0.9, travel=((0.0, 3.2, 0), (0.05, 5.8, 0)), skip=("armL", "armR"))
    for side in ("L", "R"):
        H.pose_hold(maid, side, shoulder=(0.9, 0, 0), elbow=(0.9, 0, 0))
    lin = H.box_mesh("linen", [(0, 0, 0, 0.2, 0.15, 0.09)], L.mat_principled("linenm", (0.9, 0.88, 0.84), rough=0.9), bevel=0.02)
    lin.parent = maid["pelvis"]
    lin.location = (0, 0.32, 0.38)
    p0, t0 = (0.1, -0.6, 1.55), (0.0, 9.0, 1.0)
    c = H.cam(p0, t0, lens=35)
    H.cam_move(c, [(1, p0, t0), (n, (0.12, 1.5, 1.55), (0.05, 11.0, 1.0))], ease=False)
    L.bake_static()


# --------------------------------------------------------------------------- S14 the ghost tour
def S14(L, n):
    _night_world(L, (0.003, 0.004, 0.007))
    H.hotel_corridor(n, sconce_level=0.3, d217="closed", spill=0.6, far_window=1.0, dust_count=250)
    exit_f = n - 22
    group = []
    starts = [(0.45, 10.45), (0.7, 10.85), (0.35, 11.25), (0.65, 11.65), (0.4, 12.05)]
    travel = 3.75
    for i, (x, y) in enumerate(starts):
        f = H.figure(f"tour{i}", height=[1.8, 1.7, 1.62, 1.85, 1.68][i], coat=i > 0)
        f["root"].rotation_euler = (0, 0, math.pi)
        H.walk(f, 1, exit_f, stride=0.4, rate=1.25, travel=((x, y, 0), (x, y - travel, 0)), skip=(("armR",) if i == 0 else ()))
        group.append(f)
    g = group[0]
    H.pose_hold(g, "R", shoulder=(0.9, 0, 0.15), elbow=(0.0, 0, 0))
    lan = H.empty("lantern", parent=g["elbowR"])
    lan.location = (0, 0, -0.42)
    lan.rotation_euler = (-0.9, 0, 0)
    H.box_mesh("lanframe", [(sx * 0.07, sy * 0.07, 0, 0.008, 0.008, 0.1) for sx in (-1, 1) for sy in (-1, 1)] +
               [(0, 0, 0.1, 0.08, 0.08, 0.01), (0, 0, -0.1, 0.08, 0.08, 0.01)], L.mat_principled("lanf", (0.05, 0.04, 0.03), metal=0.6), parent=lan)
    lm = L.mat_emission("lanflame", (1.0, 0.7, 0.35), 12)
    gl = L.prim("sphere", loc=(0, 0, 0), segments=10, ring_count=6, radius=0.04)
    L.assign(gl, lm)
    gl.parent = lan
    ll = L.point((0, 0, 0), energy=160, color=(1.0, 0.68, 0.35), radius=0.05, name="lanl")
    ll.parent = lan
    H.flicker_mat_with_light(ll, lm, n, 160, 12, seed=7, depth=0.3, rate=0.7)
    H.key_vis([gl], [(1, True)])
    # after the group leaves, the lantern light must be gone too (it is parented, so it leaves with them)
    p, t = (-1.05, 9.5, 1.45), (1.2, 9.5, 1.3)
    c = H.cam(p, t, lens=24)
    L.cam_light(c, energy=25, color=(0.6, 0.7, 1.0))
    L.bake_static()


# --------------------------------------------------------------------------- S15 the reveal: suitcase unpacked
def S15(L, n):
    r = _room_present(L, n, "open")
    H.folded_clothes((-0.2, 0.9, 0.665), 0.0)
    H.shoes_pair((-0.85, 0.15, 0), 0.0)
    c = H.cam(S09_P0, S09_T, lens=28)
    c.data.keyframe_insert("lens", frame=1)
    c.data.lens = 28 * 1.03
    c.data.keyframe_insert("lens", frame=n)
    L.cam_light(c, energy=12, color=(0.7, 0.75, 0.9))
    L.bake_static()


# --------------------------------------------------------------------------- S16 loop: door closes its light, then S01 start
def S16(L, n):
    _night_world(L)
    s = H.hotel_corridor(n, sconce_level=0.3, d217="closed", spill=1.0)
    off_f, cut_f = 36, 52
    d = s["doors"][217]
    closed = d.rotation_euler.z
    d.keyframe_insert("rotation_euler", index=2, frame=1)
    d.rotation_euler.z = closed - 0.13
    d.keyframe_insert("rotation_euler", index=2, frame=cut_f)
    for fc in H.L._fcurves(d.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"
    H.key_energy(s["spill"], [(1, 120), (off_f, 0), (cut_f, 650)])
    H.key_emission(s["strip_mat"], [(1, 4.0), (off_f, 0.0), (cut_f, 0.0)])
    H.key_emission(s["slit_mat"], [(1, 0.0), (cut_f, 8.0)])
    H.key_emission(s["wedge_mat"], [(1, 0.0), (cut_f, 0.9)])
    cm = H.cam(CC["start"], CC["target"], lens=CC["lens"])
    e = tuple(CC["start"][i] + (CC["end"][i] - CC["start"][i]) * (n - cut_f) / S01_N for i in range(3))
    H.cam_move(cm, [(1, CC["start"], CC["target"]), (cut_f, CC["start"], CC["target"]), (n, e, CC["target"])], ease=False)
    L.cam_light(cm, energy=12, color=(0.9, 0.85, 0.8), size_deg=70)
    L.bake_static()
