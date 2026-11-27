"""MURDER-04 - The Zodiac "340" cipher (mailed Nov 1969, solved Dec 2020).
Shot builders: def SXX(L, n). Cipher grid / screens / CRT TV builders live in PIPELINE/blender/lib_murder.py.
Glyphs are illustrative STAND-INS (Latin/Greek letters, mirrored/rotated, simple shapes); never a reproduction of
the real sheet. Flat textures (screens, newspaper, TV pictures) come from make_textures.py (Pillow, run on demand).
Grid layout: 20 rows x 17 cols in the XZ plane facing -Y, centred at GRID_C, row 0 on top.
"""
import os, sys, math, random, importlib, subprocess
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_murder as M
import studio_lib as L
importlib.reload(M)
import bpy
from mathutils import Vector, noise

R = math.radians
TEX = os.path.join(_HERE, "tex")
GRID_C = (0.0, 0.0, 1.5)
CW, CH = 0.1, 0.12
RED = (1.0, 0.06, 0.03)
AMBER = (1.0, 0.55, 0.15)
PLAIN = "IHOPEYOUAREHAVINGLOTSOFUNINTRYINGTOCATCHME"


def tex(name):
    p = os.path.join(TEX, name)
    if not os.path.exists(p):
        subprocess.run(["python3", os.path.join(_HERE, "make_textures.py")], check=False)
    return p


def lin(o):
    M.set_interp(o, "LINEAR")


def const(o):
    M.set_interp(o, "CONSTANT")


# ============================================================================= cipher grid scene

def grid_scene(L, n, light=1.0, dust=True, cold=(0.85, 0.9, 1.0), paper=True):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0.0)
    G = M.cipher_grid(rows=20, cols=17, cw=CW, ch=CH, origin=GRID_C, paper=paper)
    tgt = M.empty("gl_tgt", GRID_C)
    sp = L.spot((0.3, -2.6, GRID_C[2] + 2.6), (0, 0, 0), energy=380 * light, size_deg=55, blend=0.8, color=cold, name="toplight",
                radius=0.4)
    M.aim(sp, tgt)
    L.area((0, -3, GRID_C[2]), (R(90), 0, 0), energy=10 * light, size=3, color=cold, name="fill")
    if dust:
        L.particle_cloud((0, -1.4, GRID_C[2] + 1.0), (3, 1.2, 1.2), count=90, radius=0.002, drift=(0.01, 0, -0.012), nframes=n,
                         name="dust", mat=L.mat_principled("dust_m", (0.5, 0.5, 0.48), emit=(1, 1, 0.95), emit_strength=0.08))
    return G, sp


def front_cam(L, loc, lens=50, name="cam"):
    cam, _ = L.camera(loc=loc, target=None, lens=lens, name=name)
    cam.rotation_euler = (R(90), 0, 0)  # looking +Y at the grid
    cam.data.clip_start = 0.01
    return cam


def grid_flicker(G, n, count=40, seed=5, color=RED, peak=2.0, f0=1):
    rnd = random.Random(seed)
    for k in range(count):
        r, c = rnd.randrange(G["rows"]), rnd.randrange(G["cols"])
        o = G["g"][r][c]
        f = rnd.randint(f0, n)
        M.set_glyph(o, 1, color, 0.0)
        M.set_glyph(o, f - 1, color, 0.0)
        M.set_glyph(o, f + 1, color, peak * rnd.uniform(0.5, 1.0))
        M.set_glyph(o, f + 6, color, 0.0)


def full_dist(lens):
    """Camera distance that fits the full grid width (plus margin) in a 9:16 frame."""
    half_w = 18 * 0.5625 / lens
    return 1.05 / half_w


# S01 frame-1 framing (macro row drift) - also the end frame of S24
S01_ROW = 4
S01_LOC0 = (-0.42, -0.8, GRID_C[2] + 1.2 - (S01_ROW + 0.5) * CH)
S01_LOC0b = (-0.30, -0.8, GRID_C[2] + 1.2 - (S01_ROW + 0.5) * CH)  # f8: still drifting along the row
FULL_LOC = (0.0, -full_dist(50) - 0.0, GRID_C[2] - 0.32)


def S01(L, n):
    G, sp = grid_scene(L, n)
    grid_flicker(G, n, count=55, seed=5)
    cam = front_cam(L, S01_LOC0, lens=85)
    keys = [(1, S01_LOC0, 85), (8, S01_LOC0b, 85), (36, (0.0, -full_dist(50) * 0.97, GRID_C[2] - 0.3), 50),
            (n, (0.0, -full_dist(50) * 0.93, GRID_C[2] - 0.3), 50)]
    for f, p, lens in keys:
        cam.location = p
        cam.keyframe_insert("location", frame=f)
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=f)
    lin(cam)
    # ease-out pull back between f8..f36
    for fc in M.L._fcurves(cam.animation_data.action):
        for kp in fc.keyframe_points:
            if int(kp.co[0]) == 8:
                kp.interpolation = "BEZIER"
                kp.easing = "EASE_OUT"
    L.handheld(cam, n, amp=0.004, rate=0.6, rot_amp=0.002)
    L.bake_static()


def S24(L, n):
    G, sp = grid_scene(L, n)
    grid_flicker(G, n, count=30, seed=24)
    cam = front_cam(L, S01_LOC0, lens=85)
    start = (S01_LOC0[0] - 0.15, -1.3, S01_LOC0[2] + 0.15)
    for f, p, lens in ((1, start, 60), (n, S01_LOC0, 85)):
        cam.location = p
        cam.keyframe_insert("location", frame=f)
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=f)
    # glyph at S01 f1 state flickering like S01's start
    L.bake_static()


def S02(L, n):
    G, sp = grid_scene(L, n, cold=(0.9, 0.95, 1.0))
    for r in range(20):
        f = 2 + int(r * (n - 8) / 20)
        for c in range(17):
            o = G["g"][r][c]
            M.set_glyph(o, 1, (1, 1, 1), 0.0)
            M.set_glyph(o, f - 1, (1, 1, 1), 0.0)
            M.set_glyph(o, f, (1, 1, 1), 0.9)
            M.set_glyph(o, f + 4, (1, 1, 1), 0.12)
    d = full_dist(35)
    cam = front_cam(L, (0, -d * 0.55, GRID_C[2] + 0.9), lens=35)
    cam.rotation_euler = (R(80), 0, 0)
    cam.keyframe_insert("rotation_euler", frame=1)
    cam.keyframe_insert("location", frame=1)
    cam.rotation_euler = (R(98), 0, 0)
    cam.location = (0, -d * 0.62, GRID_C[2] - 0.1)
    cam.keyframe_insert("rotation_euler", frame=n)
    cam.keyframe_insert("location", frame=n)
    L.bake_static()


# ============================================================================= S03 1969 newsroom

def S03(L, n):
    L.set_world(color=(0.02, 0.022, 0.03), strength=1.0)
    fl = L.prim("plane", loc=(0, 2, 0), size=1)
    fl.scale = (14, 14, 1)
    L.assign(fl, L.mat_noise_surface("floor", (0.04, 0.035, 0.03), (0.09, 0.08, 0.07), scale=4, bump=0.1, voronoi=False))
    bw = L.prim("plane", loc=(0, 6.5, 2), size=1, rot=(R(90), 0, 0))
    bw.scale = (14, 4, 1)
    L.assign(bw, L.mat_noise_surface("wall", (0.06, 0.06, 0.05), (0.12, 0.11, 0.09), scale=3, bump=0.1, voronoi=False))
    # venetian blind window with city glow
    win = M.image_plane(tex("city_glow.png"), (1.5, 6.45, 1.9), (3.2, 1.6), emit=2.0, name="city")
    sm = L.mat_principled("slat", (0.25, 0.24, 0.2), rough=0.6)
    for k in range(14):
        s = L.prim("cube", loc=(1.5, 6.38, 1.15 + k * 0.115))
        s.scale = (1.65, 0.01, 0.03)
        s.rotation_euler = (R(30), 0, 0)
        L.assign(s, sm)
    L.area((1.5, 6.0, 1.9), (R(-90), 0, 0), energy=60, size=3, color=(0.5, 0.6, 1.0), name="winspill")
    wood = M.mat_wood_dark("deskwood")
    for (x, y) in ((0, 0), (-1.6, 2.2), (1.4, 2.4), (-1.4, 4.4), (1.6, 4.6)):
        t = L.prim("cube", loc=(x, y, 0.74))
        t.scale = (0.75, 0.42, 0.025)
        L.assign(t, wood)
        for sx in (-0.7, 0.7):
            lg = L.prim("cube", loc=(x + sx, y, 0.37))
            lg.scale = (0.025, 0.38, 0.37)
            L.assign(lg, wood)
        if (x, y) != (0, 0):
            M.box_typewriter((x - 0.2, y - 0.05, 0.765), rot_z=random.Random(int(x * 10)).uniform(-0.2, 0.2), name=f"tw{x}{y}")
            M.hanging_lamp((x, y, 1.95), energy=140, name=f"hl{x}{y}")
    M.box_typewriter((0.42, 0.12, 0.765), rot_z=R(-12), name="tw0")
    M.hanging_lamp((0.0, 0.0, 1.85), energy=700, name="hl0")
    # clerk silhouette behind the desk, shirt + tie
    clerk = L.char_figure("clerk", color=(0.05, 0.05, 0.055), height=1.78)
    clerk["root"].location = (-0.05, 0.62, 0)
    clerk["root"].rotation_euler = (0, 0, R(180))
    shirt = L.mat_principled("shirt", (0.35, 0.35, 0.33), rough=0.8)
    L.assign(clerk["torso"], shirt)
    tie = L.prim("cube", loc=(0, 0.125, 0.32))
    tie.scale = (0.025, 0.01, 0.2)
    L.assign(tie, L.mat_principled("tie", (0.03, 0.03, 0.04), rough=0.6))
    tie.parent = clerk["pelvis"]
    clerk["pelvis"].rotation_euler = (0.25, 0, 0)
    for t, s in (("L", 1), ("R", -1)):
        sh = clerk["shoulder" + t]
        for f, v in ((1, (0.9, 0, s * 0.35)), (30, (1.0, 0, s * 0.3)), (46, (0.95, 0, s * 0.45)), (n, (0.6, 0, s * 0.2))):
            sh.rotation_euler = v
            sh.keyframe_insert("rotation_euler", frame=f)
        clerk["elbow" + t].rotation_euler = (0.9, 0, 0)
    # envelope in hands, then the folded sheet slides out onto the desk under the lamp
    env = L.prim("cube", loc=(-0.05, 0.25, 0.95), name="envelope")
    env.scale = (0.12, 0.004, 0.07)
    env.rotation_euler = (R(60), 0, 0)
    L.assign(env, M.mat_paper("envm", (0.72, 0.68, 0.58)))
    for f, p in ((1, (-0.05, 0.25, 0.95)), (40, (-0.05, 0.22, 0.97)), (n, (-0.4, 0.3, 0.9))):
        env.location = p
        env.keyframe_insert("location", frame=f)
    sheet = M.image_plane(tex("cipher_sheet.png"), (-0.05, 0.22, 0.95), (0.2, 0.26), rot=(R(60), 0, 0), name="sheet")
    for f, p, r in ((1, (-0.05, 0.24, 0.95), R(60)), (40, (-0.05, 0.24, 0.96), R(60)), (62, (0.0, 0.0, 0.8), R(5)),
                    (n, (0.0, -0.02, 0.768), 0.0)):
        sheet.location = p
        sheet.rotation_euler = (r, 0, R(8))
        sheet.keyframe_insert("location", frame=f)
        sheet.keyframe_insert("rotation_euler", frame=f)
    L.fog_volume(center=(0, 3, 1.5), size=(12, 10, 3), density=0.05, color=(0.85, 0.8, 0.7))
    L.particle_cloud((0, 0.3, 1.4), (2, 1.5, 1), count=250, radius=0.003, drift=(0.01, 0, 0.01), nframes=n, name="motes")
    cam, ct = L.camera(loc=(0.6, -2.2, 3.3), target=(0.0, 0.25, 0.8), lens=35)
    L.cam_keys(cam, [(1, (0.6, -2.2, 3.3)), (n, (0.15, -0.75, 2.0))])
    ct.keyframe_insert("location", frame=1)
    ct.location = (0.0, 0.05, 0.78)
    ct.keyframe_insert("location", frame=n)
    L.bake_static()


# ============================================================================= S04 dark fog plate (map)

def S04(L, n):
    M.night_sky(stars=0.3, zen=(0.002, 0.003, 0.006), hor=(0.01, 0.014, 0.022))
    L.sun(rot=(R(70), 0, R(20)), energy=1.6, color=(0.55, 0.62, 0.8), name="moon")
    M.cloud_volume((0, 40, 0), (80, 50, 30), density=0.25, scale=0.6, drift=(1.2, 0, 0.2), n=n, color=(0.5, 0.55, 0.65), name="fog")
    M.bokeh_lights((0, 90, -8), (120, 20, 4), count=40, seed=6, strength=6,
                   colors=((1.0, 0.7, 0.4), (1.0, 0.85, 0.6)))
    cam, ct = L.camera(loc=(0, -10, 2), target=(0, 40, 0), lens=35)
    L.cam_keys(cam, [(1, (0, -10, 2)), (n, (0, -6, 1.8))])
    L.bake_static()


# ============================================================================= S05 kitchen table -> 340 grid whip

def S05(L, n):
    L.set_world(color=(0.004, 0.003, 0.002), strength=1.0)
    tb = L.prim("cube", loc=(0, 0, 0.74))
    tb.scale = (1.0, 0.7, 0.025)
    L.assign(tb, L.mat_noise_surface("tablem", (0.18, 0.1, 0.05), (0.32, 0.2, 0.1), scale=3, bump=0.1, voronoi=False, rough=0.5))
    M.coffee_cup((-0.35, 0.18, 0.765), name="cup1")
    M.coffee_cup((0.42, 0.25, 0.765), color=(0.55, 0.15, 0.1), name="cup2")
    small = M.image_plane(tex("cipher_sheet.png"), (0.12, 0.08, 0.767), (0.24, 0.31), rot=(0, 0, R(-12)), name="first_cipher")
    paper = M.image_plane(tex("newspaper.png"), (-0.05, -0.02, 0.772), (0.42, 0.56), rot=(0, 0, R(6)), name="newspaper")
    hit = 55
    for f, p, r in ((1, (-0.05, -0.02, 0.772), R(6)), (hit - 3, (-0.05, -0.02, 0.772), R(6)), (hit + 4, (-1.4, -0.4, 1.1), R(60))):
        paper.location = p
        paper.rotation_euler = (0, 0, r)
        paper.keyframe_insert("location", frame=f)
        paper.keyframe_insert("rotation_euler", frame=f)
    # pencil marks on the small sheet
    M.glow_poly([(0.02, 0.0, 0.769), (0.14, 0.05, 0.769), (0.2, 0.15, 0.769)], color=(0.3, 0.3, 0.3), strength=0.3, bevel=0.0015,
                name="pencil")
    lamp = L.spot((0.6, 0.6, 1.7), (0, 0, 0), energy=160, size_deg=75, blend=0.7, color=(1.0, 0.7, 0.4), name="lamp", radius=0.2)
    M.aim(lamp, M.empty("lt", (0, 0, 0.75)))
    L.point((0.5, 0.6, 1.5), energy=20, color=(1.0, 0.7, 0.4), radius=0.3, name="lampfill")
    # the 340 grid standing in the dark behind; camera whips up to it (defocused) on "This one didn't"
    G = M.cipher_grid(rows=20, cols=17, cw=CW, ch=CH, origin=(0.0, 4.0, 1.6), name="bg")
    for r in range(20):
        for c in range(17):
            if (r * 7 + c * 3) % 9 == 0:
                o = G["g"][r][c]
                M.set_glyph(o, 1, RED, 0.0)
                M.set_glyph(o, hit + 2, RED, 0.0)
                M.set_glyph(o, hit + 6, RED, 0.7)
    gl = L.spot((0, 1.5, 3.5), (0, 0, 0), energy=600, size_deg=50, blend=0.6, color=(0.85, 0.9, 1.0), name="gridlight")
    M.aim(gl, M.empty("gt", (0, 4.0, 1.6)))
    cam, ct = L.camera(loc=(0.0, -0.75, 1.55), target=(0.0, 0.05, 0.76), lens=40)
    L.cam_keys(cam, [(1, (0.0, -0.75, 1.55)), (hit - 2, (0.0, -0.66, 1.45)), (hit + 4, (0.0, -0.9, 1.5)), (n, (0.0, -0.8, 1.5))])
    for f, p in ((1, (0.0, 0.05, 0.76)), (hit - 2, (0.0, 0.05, 0.76)), (hit + 4, (0.0, 4.0, 1.45)), (n, (0.0, 4.0, 1.45))):
        ct.location = p
        ct.keyframe_insert("location", frame=f)
    L.dof(cam, distance=1.0, fstop=1.6)
    L.bake_static()


# ============================================================================= modern monitor rooms

def solver_room(L, n, loc=(0, 0, 0), screen_tex="letters_scroll.png", tint=(0.8, 1.0, 0.9), glow=(0.6, 0.85, 1.0), rot_z=0.0,
                name="room", seed=1, figure=True, lamp=None, strength=3.0, scroll=(0, 0.25), steps=None, scale=(1, 0.35)):
    root = M.empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    desk = L.prim("cube", loc=(0, 0, 0.73))
    desk.scale = (0.8, 0.4, 0.02)
    L.assign(desk, L.mat_principled(name + "_desk", (0.03, 0.03, 0.032), rough=0.25))
    desk.parent = root
    sm, em = M.mat_screen(name + "_scr", tex(screen_tex), strength=strength, scroll=scroll, n=n, scale=scale, tint=tint,
                          flicker=0.05, seed=seed, steps=steps)
    mon = M.monitor((0, 0.15, 0.75), screen_mat=sm, name=name + "_mon")
    mon["root"].parent = root
    gl = L.area((0, 0.1, 0.75 + mon["center_z"]), (R(90), 0, 0), energy=30, size=0.6, color=glow, name=name + "_glow")
    gl.rotation_euler = (R(-90), 0, 0)  # faces -Y (toward the solver)
    gl.parent = root
    fig = None
    if figure:
        fig = L.char_figure(name + "_solver", color=(0.02, 0.02, 0.024), height=1.78)
        M.seated_pose(fig, slump=0.0, lean=-0.15)
        fig["pelvis"].location.z = 0.5
        for t in ("L", "R"):
            fig["hip" + t].rotation_euler = (R(88), 0, 0)
            fig["knee" + t].rotation_euler = (R(-85), 0, 0)
            fig["shoulder" + t].rotation_euler = (0.9, 0, 0)
            fig["elbow" + t].rotation_euler = (0.8, 0, 0)
        fig["neck"].rotation_euler = (0.1, 0, 0)
        fig["root"].parent = root
        fig["root"].location = (0, -0.75, 0)
    if lamp:
        lp = L.point((-0.6, 0.0, 1.2), energy=lamp, color=(1.0, 0.65, 0.3), radius=0.15, name=name + "_lamp")
        lp.parent = root
    return root, mon, fig


# ----------------------------------------------------------------------------- S06 three panels

def S06(L, n):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0)
    # three stacked panels (frame upper 2/3); each a solver room seen from behind-left
    W = 3.2
    pitch = 1.32
    zc = [2.0 + pitch, 2.0, 2.0 - pitch]
    looks = [("letters_scroll.png", (0.7, 1.0, 0.85), (0.5, 0.85, 1.0)), ("mosaic.png", (0.8, 0.95, 1.0), (0.55, 0.8, 1.0)),
             ("az_window.png", (0.9, 1.0, 0.9), (0.7, 1.0, 0.8))]
    sl = [-1, 1, -1]
    for k in range(3):
        base = (0, 0, zc[k] - 1.05)
        root, mon, fig = solver_room(L, n, loc=base, screen_tex=looks[k][0], tint=looks[k][1], glow=looks[k][2], rot_z=R(-35),
                                     name=f"p{k}", seed=k, scroll=(0, 0.25) if k == 0 else (0, 0), scale=(1, 0.35) if k == 0 else (1, 1))
        f0 = 1 + k * 5
        root.location = (sl[k] * 4.5, base[1], base[2])
        root.keyframe_insert("location", frame=f0)
        root.location = base
        root.keyframe_insert("location", frame=f0 + 9)
        root.location = (base[0] - sl[k] * 0.12, base[1], base[2])
        root.keyframe_insert("location", frame=n)
        bw = L.prim("plane", loc=(0, 1.6, zc[k]), size=1, rot=(R(90), 0, 0))
        bw.scale = (W, pitch, 1)
        L.assign(bw, L.mat_principled(f"bw{k}", (0.012, 0.012, 0.014), rough=0.9))
    # black mask with three windows (keeps each room inside its panel)
    import bmesh
    bm = bmesh.new()
    hw, hh = W / 2 - 0.04, pitch / 2 - 0.035
    xs = [-6, -hw, hw, 6]
    zs_edges = [-6]
    for k in (2, 1, 0):
        zs_edges += [zc[k] - hh, zc[k] + hh]
    zs_edges += [12]
    for i in range(3):
        for j in range(len(zs_edges) - 1):
            if i == 1 and j % 2 == 1:
                continue  # window
            x0, x1, z0, z1 = xs[i], xs[i + 1], zs_edges[j], zs_edges[j + 1]
            vs = [bm.verts.new((x0, -1.6, z0)), bm.verts.new((x1, -1.6, z0)), bm.verts.new((x1, -1.6, z1)), bm.verts.new((x0, -1.6, z1))]
            bm.faces.new(vs)
    mask = L.mesh_from_bm("mask", bm)
    L.assign(mask, L.mat_emission("maskm", (0.0, 0.0, 0.0), 0.0))
    for k in range(3):
        fr = M.glow_poly(M.rect_pts(0, zc[k], 2 * hw, 2 * hh, y=-1.62), color=(0.9, 0.12, 0.08), strength=2.5, bevel=0.006,
                         name=f"pframe{k}", closed=True)
    cam, _ = L.camera(loc=(0, -12, 1.85), target=None, lens=50)
    M.ortho(cam, 5.3)
    cam.rotation_euler = (R(90), 0, 0)
    cam.keyframe_insert("location", frame=1)
    cam.data.ortho_scale = 5.3
    cam.data.keyframe_insert("ortho_scale", frame=1)
    cam.data.ortho_scale = 5.1
    cam.data.keyframe_insert("ortho_scale", frame=n)
    L.bake_static()


def monitor_plate(L, n, screen_tex, tint, glow, lamp=None, rot=0.0, steps=None, scale=(1, 1), scroll=(0, 0), fstop=1.2):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0)
    root, mon, fig = solver_room(L, n, screen_tex=screen_tex, tint=tint, glow=glow, rot_z=rot, lamp=lamp, steps=steps, scale=scale,
                                 scroll=scroll)
    bw = L.prim("plane", loc=(0, 2.0, 1.5), size=1, rot=(R(90), 0, 0))
    bw.scale = (8, 4, 1)
    L.assign(bw, L.mat_principled("bw", (0.02, 0.02, 0.022), rough=0.9))
    return root, mon, fig


def S07(L, n):
    monitor_plate(L, n, "letters_scroll.png", (0.7, 1.0, 0.85), (0.5, 0.85, 1.0), scroll=(0, 0.25), scale=(1, 0.35))
    cam, ct = L.camera(loc=(0.9, -1.6, 1.4), target=(0, 0.0, 1.1), lens=50)
    L.cam_keys(cam, [(1, (0.9, -1.6, 1.4)), (n, (0.8, -1.4, 1.38))])
    L.dof(cam, distance=1.4, fstop=2.8)
    L.bake_static()


def S08(L, n):
    monitor_plate(L, n, "mosaic.png", (0.8, 0.95, 1.0), (0.55, 0.8, 1.0), steps=(6, [(0, 0), (0.5, 0), (0, 0.5), (0.5, 0.5)]),
                  scale=(0.5, 0.5))
    cam, ct = L.camera(loc=(-0.9, -1.5, 1.35), target=(0, 0.0, 1.1), lens=50)
    L.cam_keys(cam, [(1, (-0.9, -1.5, 1.35)), (n, (-0.8, -1.35, 1.33))])
    L.dof(cam, distance=1.4, fstop=2.8)
    L.bake_static()


def S09(L, n):
    monitor_plate(L, n, "az_window.png", (0.9, 1.0, 0.9), (0.7, 1.0, 0.8), lamp=25)
    cam, ct = L.camera(loc=(0.7, -1.7, 1.5), target=(0, 0.0, 1.1), lens=50)
    L.cam_keys(cam, [(1, (0.7, -1.7, 1.5)), (n, (0.6, -2.0, 1.55))])
    L.dof(cam, distance=1.4, fstop=2.8)
    L.bake_static()


# ============================================================================= S10 reading arrow shatters

def S10(L, n):
    G, sp = grid_scene(L, n)
    hit = 24
    p0 = G["pos"](0, 0, y=-0.03)
    p1 = G["pos"](0, 8, y=-0.03)
    import bmesh
    from mathutils import Matrix
    bm = bmesh.new()
    for (x0, z0, x1, z1) in ((-0.25, -0.012, 0.0, 0.012),):
        vs = [bm.verts.new((x0, 0, z0)), bm.verts.new((x1, 0, z0)), bm.verts.new((x1, 0, z1)), bm.verts.new((x0, 0, z1))]
        bm.faces.new(vs)
    vs = [bm.verts.new((0.0, 0, -0.04)), bm.verts.new((0.07, 0, 0.0)), bm.verts.new((0.0, 0, 0.04))]
    bm.faces.new(vs)
    arrow = L.mesh_from_bm("arrow", bm)
    am = L.mat_emission("arrow_m", (1, 1, 1), 6.0)
    L.assign(arrow, am)
    em = [nd for nd in am.node_tree.nodes if nd.type == "EMISSION"][0]
    arrow.location = (p0.x - 0.1, p0.y - 0.02, p0.z)
    arrow.keyframe_insert("location", frame=1)
    arrow.location = (p1.x, p0.y - 0.02, p0.z)
    arrow.keyframe_insert("location", frame=hit - 4)
    arrow.keyframe_insert("location", frame=hit)
    for f, c, s in ((1, (1, 1, 1), 6), (hit - 3, (1, 1, 1), 6), (hit - 2, RED, 14), (hit, RED, 10)):
        em.inputs[0].default_value = (*c, 1)
        em.inputs[1].default_value = s
        em.inputs[0].keyframe_insert("default_value", frame=f)
        em.inputs[1].keyframe_insert("default_value", frame=f)
    M.hide_until(arrow, 1)
    arrow.hide_render = False
    arrow.keyframe_insert("hide_render", frame=hit)
    arrow.hide_render = True
    arrow.keyframe_insert("hide_render", frame=hit + 1)
    # shards
    rnd = random.Random(3)
    sm = L.mat_emission("shard_m", RED, 10)
    for i in range(36):
        s = L.prim("plane", loc=(0, 0, 0), size=1)
        s.scale = (rnd.uniform(0.008, 0.02), rnd.uniform(0.004, 0.012), 1)
        L.assign(s, sm)
        s.visible_shadow = False
        st = Vector((p1.x + rnd.uniform(-0.25, 0.05), p0.y - 0.03, p0.z + rnd.uniform(-0.01, 0.01)))
        v = Vector((rnd.uniform(-1, 1), rnd.uniform(-0.8, -0.1), rnd.uniform(-1, 1))) * rnd.uniform(0.4, 1.2)
        for f in (hit, n):
            t = (f - hit) / 24
            s.location = st + v * t + Vector((0, 0, -0.6 * t * t))
            s.rotation_euler = (rnd.uniform(0, 6) + 8 * t, rnd.uniform(0, 6) + 5 * t, rnd.uniform(0, 6))
            s.keyframe_insert("location", frame=f)
            s.keyframe_insert("rotation_euler", frame=f)
        lin(s)
        for f, sc_ in ((hit, 1.0), (n, 0.2)):
            s.scale = (s.scale.x * sc_ if f == n else s.scale.x, s.scale.y * sc_ if f == n else s.scale.y, 1)
            s.keyframe_insert("scale", frame=f)
        M.hide_until(s, hit)
    # first-row glyphs light white as the arrow passes, then red flash
    for c in range(9):
        o = G["g"][0][c]
        f = 1 + int((hit - 4) * c / 8)
        M.set_glyph(o, 1, (1, 1, 1), 0.0)
        M.set_glyph(o, f, (1, 1, 1), 0.5)
        M.set_glyph(o, hit - 1, (1, 1, 1), 0.3)
        M.set_glyph(o, hit + 1, RED, 0.9)
        M.set_glyph(o, hit + 10, RED, 0.0)
    flash = L.point((p1.x, -0.4, p1.z), energy=0, color=RED, radius=0.3, name="flash")
    for f, e in ((1, 0), (hit - 1, 0), (hit + 1, 30), (hit + 8, 0)):
        flash.data.energy = e
        flash.data.keyframe_insert("energy", frame=f)
    d = full_dist(50)
    cam = front_cam(L, (0, -d * 0.95, GRID_C[2] - 0.2), lens=50)
    cam.keyframe_insert("location", frame=1)
    cam.location = (-0.25, -d * 0.55, p0.z - 0.42)
    cam.keyframe_insert("location", frame=hit + 6)
    cam.location = (-0.22, -d * 0.52, p0.z - 0.42)
    cam.keyframe_insert("location", frame=n)
    M.shake(cam, [hit], amp=0.01, decay=6)
    L.bake_static()


# ============================================================================= S11 diagonal reading order

def S11(L, n):
    G, sp = grid_scene(L, n)
    # grid splits into three sections (rows 0-8, 9-17, 18-19)
    for r in range(20):
        dz = 0.0 if r < 9 else (0.07 if r < 18 else 0.14)
        for c in range(17):
            o = G["g"][r][c]
            o.keyframe_insert("location", frame=1)
            o.location.z -= dz
            o.keyframe_insert("location", frame=14)
    # dim the light to ~30 %
    for f, e in ((1, sp.data.energy), (20, sp.data.energy * 0.35)):
        sp.data.energy = e
        sp.data.keyframe_insert("energy", frame=f)
    path = M.hop_path(9, 17, start=(0, 0), dr=1, dc=2, count=24)
    pts = []
    f_hop = [7 + int(k * 1.9) for k in range(len(path))]
    strip_z = GRID_C[2] - 10 * CH - 0.3
    for k, (r, c) in enumerate(path):
        o = G["g"][r][c]
        f = f_hop[k]
        M.set_glyph(o, 1, RED, 0.0)
        M.set_glyph(o, f - 1, RED, 0.0)
        M.set_glyph(o, f, RED, 1.2)
        p = o.location.copy()
        pts.append((p.x, p.y - 0.01, p.z))
        # lift then slide into the re-ordered strip
        fl = 50 + k
        o.keyframe_insert("location", frame=fl - 6)
        o.location = (p.x, p.y - 0.18, p.z)
        o.keyframe_insert("location", frame=fl)
        o.location = (-0.8 * 1.7 / 2 * 1.0 + k * 0.07, p.y - 0.12, strip_z)
        o.keyframe_insert("location", frame=fl + 14)
    # one short glowing hop segment per step (no line across the sheet when the path wraps)
    tmat = L.mat_emission("trail_m", RED, 5.0)
    tm = [nd for nd in tmat.node_tree.nodes if nd.type == "EMISSION"][0].inputs[1]
    for k in range(len(path) - 1):
        if path[k + 1][1] < path[k][1]:
            continue
        seg = M.glow_poly([pts[k], pts[k + 1]], color=RED, strength=5, bevel=0.003, name=f"hop{k}")
        seg.data.materials[0] = tmat
        M.curve_draw(seg, f_hop[k], f_hop[k + 1])
    for f, s_ in ((1, 5), (52, 5), (70, 0.6)):
        tm.default_value = s_
        tm.keyframe_insert("default_value", frame=f)
    d = full_dist(35)
    cam = front_cam(L, (0, -d * 1.05, GRID_C[2] - 0.2), lens=35)
    cam.rotation_euler = (R(86), 0, 0)
    cam.keyframe_insert("location", frame=1)
    cam.keyframe_insert("rotation_euler", frame=1)
    cam.location = (0.1, -d * 0.98, GRID_C[2] - 0.4)
    cam.rotation_euler = (R(84), 0, R(-3))
    cam.keyframe_insert("location", frame=n)
    cam.keyframe_insert("rotation_euler", frame=n)
    L.bake_static()


# ============================================================================= S12 / S13 / S14 screens

def S12(L, n):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0)
    root, mon, fig = solver_room(L, n, screen_tex="mosaic.png", tint=(0.8, 0.95, 1.0), glow=(0.55, 0.85, 1.0), rot_z=0.0,
                                 figure=True, steps=(4, [(0, 0), (0.5, 0), (0, 0.5), (0.5, 0.5), (0.25, 0.25)]), scale=(0.5, 0.5),
                                 strength=4.0)
    fig["root"].location = (0.42, -0.95, 0)
    sc = mon["screen"]
    c = Vector((0, 0.15 - 0.0195, 0.75 + mon["center_z"]))
    cam, ct = L.camera(loc=(c.x - 0.12, -1.25, c.z + 0.04), target=tuple(c), lens=50)
    L.cam_keys(cam, [(1, (c.x - 0.12, -1.25, c.z + 0.04)), (n, (c.x - 0.02, -0.45, c.z + 0.01))])
    L.dof(cam, target=M.empty("sf", tuple(c)), fstop=2.0)
    L.bake_static()


def S13(L, n):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0)
    root, mon, fig = solver_room(L, n, screen_tex="az_window.png", tint=(0.9, 1.0, 0.92), glow=(0.7, 1.0, 0.8), rot_z=0.0,
                                 figure=True, lamp=30, strength=3.0)
    sc = mon["screen"]
    W, Hh = 0.62, 0.36
    cz = 0.75 + mon["center_z"]
    sy = 0.15 - 0.021
    # scrolling candidate lines over the window's text panel
    gm, _ = M.mat_screen("gib", tex("gib_scroll.png"), strength=3.0, scroll=(0, 0.35), n=n, scale=(1, 0.25), tint=(0.9, 1.0, 0.9))
    gl = L.prim("plane", loc=(0, sy, cz - Hh * 0.1), size=1, rot=(R(90), 0, 0))
    gl.scale = (W * 0.94, Hh * 0.7, 1)
    L.assign(gl, gm)
    # score bar climbing
    bar = L.prim("plane", loc=(0, sy - 0.001, cz + Hh * 0.33), size=1, rot=(R(90), 0, 0), name="score")
    L.assign(bar, L.mat_emission("barm", (0.4, 1.0, 0.5), 4.0))
    x0, x1 = -W * 0.32, W * 0.45
    for f, fr in ((1, 0.05), (int(n * 0.4), 0.35), (int(n * 0.7), 0.5), (n, 0.72)):
        w = (x1 - x0) * fr
        bar.scale = (w, Hh * 0.07, 1)
        bar.location.x = x0 + w / 2
        bar.keyframe_insert("scale", frame=f)
        bar.keyframe_insert("location", frame=f)
    fig["root"].location = (-0.32, -0.8, 0)
    fig["root"].rotation_euler = (0, 0, R(-15))
    tgt = (0, sy, cz)
    r_ = 1.25
    cam, ct = L.camera(loc=(0, 0, 0), target=tgt, lens=35)
    for f, a in ((1, R(-32)), (n, R(-22))):
        cam.location = (r_ * math.sin(a), sy - r_ * math.cos(a), cz + 0.2)
        cam.keyframe_insert("location", frame=f)
    L.dof(cam, target=M.empty("sf", tgt), fstop=2.4)
    L.bake_static()


def S14(L, n):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0)
    # dim gibberish screen behind a split-flap decode line
    gm, _ = M.mat_screen("gib", tex("gib_scroll.png"), strength=0.5, scroll=(0, 0.0), n=n, scale=(1, 0.25), tint=(0.8, 1.0, 0.85))
    scr = L.prim("plane", loc=(0, 0.01, 0), size=1, rot=(R(90), 0, 0))
    scr.scale = (2.0, 3.2, 1)
    L.assign(scr, gm)
    rnd = random.Random(14)
    line = "QXZRTLOTSOFUNKWPVB"
    good = set(range(5, 13))  # "LOTSOFUN" -> spaced "LOTS OF FUN"
    disp = "QXZRT" + "LOTS OF FUN" + "KWPV"
    ink = M.mat_glyph("flap", ink=(0.1, 0.12, 0.11), glow=5.0)
    cellw = 0.085
    N = len(disp)
    cardm = L.mat_principled("cardm", (0.02, 0.025, 0.025), rough=0.4)
    for i, ch in enumerate(disp):
        x = -cellw * (N - 1) / 2 + i * cellw
        card = L.prim("plane", loc=(x, -0.002, 0.0), size=1, rot=(R(90), 0, 0))
        card.scale = (cellw * 0.9, 0.15, 1)
        L.assign(card, cardm)
        is_good = 5 <= i < 16 and ch != " "
        final = ch if ch != " " else None
        seq = [rnd.choice(M.CIPHER_LET) for _ in range(5)]
        f_end = 8 + (i - 5) * 2 if is_good else n + 10
        f = 1
        objs = []
        k = 0
        while f < min(f_end, n):
            o = M.letter_obj(seq[k % len(seq)], 0.12, ink, (x, -0.008, 0.0), name=f"fl{i}_{k}")
            M.set_glyph(o, 1, (0.6, 1.0, 0.7), 0.4)
            nf = f + rnd.randint(2, 4)
            for ff, hide in ((1, True), (max(1, f - 1), True), (f, False), (nf, True)):
                o.hide_render = hide
                o.keyframe_insert("hide_render", frame=max(1, ff))
            o.scale = (1, 0.2, 1)
            o.keyframe_insert("scale", frame=f)
            o.scale = (1, 1, 1)
            o.keyframe_insert("scale", frame=f + 1)
            f = nf
            k += 1
        if is_good and final:
            o = M.letter_obj(final, 0.12, ink, (x, -0.008, 0.0), name=f"good{i}")
            M.set_glyph(o, 1, RED, 0.0)
            M.set_glyph(o, f_end, RED, 1.4)
            M.hide_until(o, f_end)
            o.scale = (1, 0.2, 1)
            o.keyframe_insert("scale", frame=f_end)
            o.scale = (1.0, 1.0, 1.0)
            o.keyframe_insert("scale", frame=f_end + 2)
    L.point((0, -0.6, 0.05), energy=10, color=(1.0, 0.3, 0.2), radius=0.2, name="redglow")
    cam, _ = L.camera(loc=(0, -4.1, -0.55), target=None, lens=50)
    cam.rotation_euler = (R(90), 0, 0)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0, -3.8, -0.52)
    cam.keyframe_insert("location", frame=n)
    L.bake_static()


# ============================================================================= S15 / S17 blurred grid plates

def S15(L, n):
    G, sp = grid_scene(L, n)
    grid_flicker(G, n, count=30, seed=15)
    d = full_dist(50)
    cam = front_cam(L, (0, -d * 0.8, GRID_C[2] - 0.3), lens=50)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0.1, -d * 0.75, GRID_C[2] - 0.3)
    cam.keyframe_insert("location", frame=n)
    L.dof(cam, distance=d * 0.35, fstop=1.4)
    L.bake_static()


def flip_grid(L, n, G, f_col, letter_glow=0.35):
    """Flip glyphs into plaintext-style letters column by column (f_col[c] = frame column c starts flipping; None = never)."""
    lm = M.mat_glyph("letters", ink=(0.03, 0.025, 0.035))
    rnd = random.Random(2)
    letters = []
    for r in range(G["rows"]):
        for c in range(G["cols"]):
            idx = r * G["cols"] + c
            ch = PLAIN[idx] if idx < len(PLAIN) else rnd.choice("ETAOINSHRDLUCMFYWGPB")
            o = G["g"][r][c]
            p = o.location.copy()
            lo = M.letter_obj(ch, CH * 0.72, lm, p, name=f"let_{r}_{c}")
            amt = 0.9 if idx < len(PLAIN) else letter_glow
            lo.color = (*AMBER, amt)
            f0 = f_col[c]
            if f0 is None:
                lo.hide_render = True
                lo.scale = (1, 1, 1)
                letters.append(lo)
                continue
            # symbol turns edge-on, letter turns in
            o.rotation_euler = (R(90), 0, 0)
            o.keyframe_insert("rotation_euler", frame=max(1, f0))
            o.rotation_euler = (R(90), 0, R(90))
            o.keyframe_insert("rotation_euler", frame=f0 + 3)
            lo.rotation_euler = (R(90), 0, R(-90))
            lo.keyframe_insert("rotation_euler", frame=max(1, f0 + 3))
            lo.rotation_euler = (R(90), 0, 0)
            lo.keyframe_insert("rotation_euler", frame=f0 + 6)
            M.hide_until(lo, f0 + 3)
            letters.append(lo)
    return letters


def S16(L, n):
    G, sp = grid_scene(L, n, cold=(0.75, 0.85, 1.0))
    f_col = [None] * 17
    for c in range(8, 17):
        f_col[c] = 2 + (16 - c) * 3
    flip_grid(L, n, G, f_col)
    warm = L.spot((1.8, -2.2, GRID_C[2] + 1.5), (0, 0, 0), energy=0, size_deg=40, blend=0.8, color=(1.0, 0.6, 0.25), name="warm")
    M.aim(warm, M.empty("wt", (0.5, 0, GRID_C[2])))
    for f, e in ((1, 0), (n, 350)):
        warm.data.energy = e
        warm.data.keyframe_insert("energy", frame=f)
    d = full_dist(50)
    cam = front_cam(L, (0, -d * 1.0, GRID_C[2] - 0.3), lens=50)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0, -d * 0.9, GRID_C[2] - 0.28)
    cam.keyframe_insert("location", frame=n)
    L.bake_static()


def S17(L, n):
    G, sp = grid_scene(L, n, light=0.6, cold=(0.75, 0.85, 1.0))
    f_col = [None] * 8 + [1] * 9
    flip_grid(L, n, G, f_col)
    warm = L.spot((1.8, -2.2, GRID_C[2] + 1.5), (0, 0, 0), energy=300, size_deg=40, blend=0.8, color=(1.0, 0.6, 0.25), name="warm")
    M.aim(warm, M.empty("wt", (0.5, 0, GRID_C[2])))
    d = full_dist(50)
    cam = front_cam(L, (0, -d * 0.85, GRID_C[2] - 0.3), lens=50)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0, -d * 0.8, GRID_C[2] - 0.3)
    cam.keyframe_insert("location", frame=n)
    L.dof(cam, distance=d * 0.3, fstop=1.4)
    L.bake_static()


def S20(L, n):
    G, sp = grid_scene(L, n, light=0.6, cold=(1.0, 0.85, 0.65), paper=True)
    letters = flip_grid(L, n, G, [1] * 17, letter_glow=0.5)
    rnd = random.Random(20)
    for lo in letters:
        a0 = lo.color[3]
        f = rnd.randint(4, n - 4)
        lo.color = (*AMBER, a0)
        lo.keyframe_insert("color", frame=1)
        lo.keyframe_insert("color", frame=f)
        lo.color = (0.4, 0.4, 0.45, 0.0)
        lo.keyframe_insert("color", frame=f + 3)
    sp.data.keyframe_insert("color", frame=1)
    sp.data.color = (0.7, 0.8, 1.0)
    sp.data.keyframe_insert("color", frame=n)
    d = full_dist(50)
    cam = front_cam(L, (0, -d * 0.75, GRID_C[2] - 0.3), lens=50)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0, -d * 0.9, GRID_C[2] - 0.32)
    cam.keyframe_insert("location", frame=n)
    L.bake_static()


# ============================================================================= S18 / S19 1969 TV

def tv_room(L, n, img):
    L.set_world(color=(0.0, 0.0, 0.0), strength=0)
    fl = L.prim("plane", loc=(0, 0, 0), size=1)
    fl.scale = (8, 8, 1)
    L.assign(fl, L.mat_noise_surface("rug", (0.04, 0.03, 0.025), (0.09, 0.06, 0.04), scale=20, bump=0.2, voronoi=False))
    bw = L.prim("plane", loc=(0, 0.6, 1.5), size=1, rot=(R(90), 0, 0))
    bw.scale = (8, 3, 1)
    L.assign(bw, L.mat_noise_surface("wallp", (0.05, 0.045, 0.035), (0.1, 0.09, 0.07), scale=8, bump=0.1, voronoi=False))
    sm, em = M.mat_tv_screen("tvscr", tex(img), n, strength=2.4, static=0.3)
    tv = M.crt_tv((0, 0, 0), screen_mat=sm)
    sc = tv["screen_center"]
    gl = L.area((sc[0], sc[1] - 0.05, sc[2]), (R(90), 0, 0), energy=40, size=0.5, color=(0.75, 0.85, 1.0), name="tvglow")
    gl.rotation_euler = (R(-90), 0, 0)
    L.flicker(gl, n, depth=0.25, rate=0.6, seed=4)
    L.point((sc[0], sc[1] - 1.0, sc[2]), energy=6, color=(0.75, 0.85, 1.0), radius=0.5, name="tvspill")
    return tv, sc


def S18(L, n):
    tv, sc = tv_room(L, n, "tv_talkshow.png")
    cam, ct = L.camera(loc=(0.25, -2.4, 0.95), target=(sc[0], sc[1], sc[2] - 0.05), lens=35)
    L.cam_keys(cam, [(1, (0.25, -2.4, 0.95)), (n, (0.15, -1.9, 0.9))])
    L.bake_static()


def S19(L, n):
    tv, sc = tv_room(L, n, "tv_phone.png")
    cam, ct = L.camera(loc=(0.05, -1.5, sc[2] + 0.02), target=(sc[0], sc[1], sc[2] - 0.02), lens=50)
    L.cam_keys(cam, [(1, (0.05, -1.5, sc[2] + 0.02)), (n, (0.02, -1.25, sc[2] + 0.0))])
    L.bake_static()


# ============================================================================= S21 / S23 desk plates

def desk_plate(L, n, label="ZODIAC", typewriter=False):
    L.set_world(color=(0.003, 0.003, 0.004), strength=1.0)
    M.desk(size=(3, 2))
    fold = L.prim("cube", loc=(0.05, 0.1, 0.01), name="folder")
    fold.scale = (0.24, 0.31, 0.008)
    fold.rotation_euler = (0, 0, R(-5))
    L.assign(fold, M.mat_paper("manila", (0.55, 0.42, 0.22)))
    lbl = L.text3d(label, loc=(0.05, 0.2, 0.02), rot=(0, 0, R(-5)), size=0.05, extrude=0,
                   mat=L.mat_principled("lblink", (0.05, 0.04, 0.03)), name="lbl")
    lbl.data.font = M._font(M.F_MONO) or lbl.data.font
    if typewriter:
        M.box_typewriter((-0.45, 0.35, 0), rot_z=R(15), name="tw")
    M.desk_lamp((0.55, 0.6, 0), (0.05, 0.1, 0), energy=45, rot_z=R(150))


def S21(L, n):
    desk_plate(L, n, "ZODIAC", typewriter=True)
    cam, ct = L.camera(loc=(0.0, -0.55, 0.85), target=(0.05, 0.12, 0), lens=35)
    L.cam_keys(cam, [(1, (0.0, -0.55, 0.85)), (n, (0.02, -0.42, 0.75))])
    L.bake_static()


def S23(L, n):
    L.set_world(color=(0.003, 0.003, 0.004), strength=1.0)
    M.desk(size=(3, 2))
    M.box_typewriter((0.0, 0.1, 0), rot_z=0.0, name="tw")
    M.desk_lamp((0.5, 0.45, 0), (0.0, 0.15, 0.2), energy=55, rot_z=R(150))
    # a small strip of 13 stand-in glyphs on a paper scrap beside the machine (lit red, typed one by one)
    G = M.cipher_grid(rows=1, cols=13, cw=0.03, ch=0.036, origin=(-0.05, -0.25, 0.004), seed=13, name="z13",
                      margin=(0.03, 0.03))
    for c in range(13):
        o = G["g"][0][c]
        M.hide_until(o, 20 + c * 6)
    # lay flat on the desk
    for c in range(13):
        o = G["g"][0][c]
        z = o.location.z
        o.location = (o.location.x, -0.25 - 0.0, 0.0045)
        o.rotation_euler = (0, 0, 0)
    G["paper"].location = (-0.05, -0.25, 0.003)
    G["paper"].rotation_euler = (0, 0, 0)
    cam, ct = L.camera(loc=(0.05, -0.9, 0.7), target=(0.0, 0.0, 0.1), lens=35)
    L.cam_keys(cam, [(1, (0.05, -0.9, 0.7)), (n, (0.0, -0.6, 0.45))])
    ct.keyframe_insert("location", frame=1)
    ct.location = (-0.05, -0.15, 0.05)
    ct.keyframe_insert("location", frame=n)
    L.bake_static()


# ============================================================================= S22 Z13 / Z32 rise below the grid

def S22(L, n):
    G, sp = grid_scene(L, n)
    gm = G["mat"]
    strips = []
    z13 = M.cipher_grid(rows=1, cols=13, cw=CW, ch=CH, origin=(0, 0, GRID_C[2] - 1.9), seed=13, name="z13", mat=gm)
    z32 = M.cipher_grid(rows=4, cols=8, cw=CW, ch=CH, origin=(0, 0, GRID_C[2] - 2.75), seed=32, name="z32", mat=gm)
    for S, f0, zc in ((z13, 6, GRID_C[2] - 1.9), (z32, 14, GRID_C[2] - 2.75)):
        objs = [o for row in S["g"] for o in row] + [S["paper"]]
        W = S["cols"] * CW + 0.24
        Hh = S["rows"] * CH + 0.32
        fr = M.glow_poly(M.rect_pts(0, zc, W, Hh, y=-0.01), color=RED, strength=6, bevel=0.006, name="out", closed=True)
        objs.append(fr)
        M.curve_draw(fr, f0 + 14, f0 + 30)
        for o in objs:
            o.keyframe_insert("location", frame=f0 + 16)
            o.location.z -= 0.6
            o.keyframe_insert("location", frame=f0)
        lt = L.spot((0, -1.6, zc + 1.0), (0, 0, 0), energy=250, size_deg=45, blend=0.8, color=(0.9, 0.9, 1.0), name=f"sl{f0}")
        M.aim(lt, M.empty(f"st{f0}", (0, 0, zc)))
    d = full_dist(35)
    cam = front_cam(L, (0, -d * 0.85, GRID_C[2] - 0.2), lens=35)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0, -d * 0.85, GRID_C[2] - 1.85)
    cam.keyframe_insert("location", frame=int(n * 0.6))
    cam.location = (0, -d * 0.82, GRID_C[2] - 1.9)
    cam.keyframe_insert("location", frame=n)
    L.bake_static()
