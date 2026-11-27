"""MURDER-02 - Somerton Man / Tamam Shud (1948 -> 2022).
Shot builders: def SXX(L, n). Reusable builders in PIPELINE/blender/lib_murder.py.
Desk scenes: desktop at z=0, lamp warm from camera-left/back. Beach: seawall along X at y=0, sand toward -Y,
sea beyond y<-26 (camera usually on the sand looking +Y at the wall = east, dawn glow behind the houses).
"""
import os, sys, math, importlib, random
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_murder as M
importlib.reload(M)
from mathutils import Vector

R = math.radians


def lin(o):
    M.set_interp(o, "LINEAR")


# ----------------------------------------------------------------------------- evidence desk

def desk_scene(L, n, lamp_energy=14, lamp_loc=(-0.35, 0.45, 0.0), lamp_target=(0, 0, 0), dust=True, cold_fill=0.5):
    L.set_world((0.004, 0.005, 0.007), 1.0)
    M.desk(size=(2.4, 1.6))
    # back wall far in the dark
    w = L.prim("plane", loc=(0, 0.9, 0.6), size=1, rot=(math.pi / 2, 0, 0))
    w.scale = (4, 2, 1)
    L.assign(w, L.mat_noise_surface("deskwall", (0.012, 0.012, 0.014), (0.03, 0.03, 0.034), scale=4, bump=0.1, voronoi=False))
    root, sp = M.desk_lamp(lamp_loc, lamp_target, energy=lamp_energy, rot_z=R(-35))
    # cold moonlight-ish fill from the right (desaturated murder palette)
    if cold_fill:
        L.area((0.8, -0.5, 0.7), (R(60), 0, R(55)), energy=cold_fill, size=1.0, color=(0.55, 0.65, 0.9), name="coldfill")
    if dust:
        L.particle_cloud((0, 0.05, 0.25), (0.8, 0.6, 0.5), count=350, radius=0.0012, drift=(0.008, 0, -0.006), nframes=n,
                         mat=L.mat_principled("dust", (0.9, 0.8, 0.6), emit=(1, 0.8, 0.5), emit_strength=0.5), name="dust")
    return sp


def sand_grains(center=(0, 0, 0), size=(0.16, 0.12), count=160):
    m = L.mat_principled("grain", (0.55, 0.45, 0.3), rough=0.8)
    return L.particle_cloud((center[0], center[1], 0.0007), (size[0], size[1], 0.0004), count=count, radius=0.0009, mat=m,
                            drift=(0, 0, 0), nframes=2, name="grains")


S01_C0 = (0.06, -0.33, 0.16)
S01_C1 = (0.04, -0.25, 0.12)
S01_T = (0.0, 0.0, 0.004)


def macro_scrap(L, n, c_from, c_to, unroll=None, tweezers_anim=False):
    desk_scene(L, n, lamp_energy=10, lamp_target=(0, 0, 0))
    root, paper, bd = M.rolled_scrap((0.0, -0.028, 0.0045), rot_z=R(-8))
    sand_grains()
    tw = None
    if tweezers_anim:
        tw = M.tweezers((0.035, 0.03, 0.18), rot=(R(-25), R(20), 0))
    cam, ct = L.camera(loc=c_from, target=S01_T, lens=85)
    L.cam_keys(cam, [(1, c_from), (n, c_to)])
    lin(cam)
    L.dof(cam, target=root, fstop=4.0)
    return root, paper, bd, tw, cam


def S01(L, n):
    root, paper, bd, tw, cam = macro_scrap(L, n, S01_C0, S01_C1, tweezers_anim=True)
    # tweezers come down, grip the free end, lift and the strip unrolls
    f_grip, f_end = int(n * 0.4), n
    tw.keyframe_insert("location", frame=1)
    tw.location = (0.004, 0.034, 0.012)
    tw.rotation_euler = (R(-10), R(8), 0)
    tw.keyframe_insert("location", frame=f_grip)
    tw.keyframe_insert("rotation_euler", frame=f_grip)
    tw.rotation_euler = (R(-25), R(20), 0)
    tw.keyframe_insert("rotation_euler", frame=1)
    tw.location = (0.004, 0.06, 0.03)
    tw.rotation_euler = (R(-10), R(8), 0)
    tw.keyframe_insert("location", frame=f_end)
    tw.keyframe_insert("rotation_euler", frame=f_end)
    bd.angle = 2 * math.pi * 2.1
    paper.keyframe_insert('modifiers["curl"].angle', frame=f_grip)
    bd.angle = R(40)
    paper.keyframe_insert('modifiers["curl"].angle', frame=f_end)
    L.bake_static()


def S22(L, n):
    back = tuple(S01_C0[i] + (S01_C0[i] - S01_C1[i]) * 0.8 for i in range(3))
    macro_scrap(L, n, back, S01_C0)
    L.bake_static()


def S02(L, n):
    # macro plate under the scrap overlay: unrolled strip, slow zoom, very shallow focus
    desk_scene(L, n, lamp_energy=9)
    root, paper, bd = M.rolled_scrap((0.0, -0.03, 0.0005), rot_z=R(-80))
    bd.angle = R(15)
    sand_grains()
    cam, ct = L.camera(loc=(0.0, -0.2, 0.22), target=(0, 0, 0), lens=85)
    L.cam_keys(cam, [(1, (0.0, -0.2, 0.22)), (n, (0.0, -0.16, 0.18))])
    lin(cam)
    L.dof(cam, distance=0.24, fstop=2.0)
    L.bake_static()


# ----------------------------------------------------------------------------- beach

def beach(L, n, dawn=0.0, figure=True, houses=True, lamps=True, mist=0.02):
    """dawn 0 = pre-dawn (pink-grey, cold), 1 = sunrise (warm low sun)."""
    sun_dir = (0.2, 1.0, 0.08)
    if dawn < 0.5:
        M.dawn_sky(hor=(0.5, 0.36, 0.38), mid=(0.17, 0.17, 0.25), zen=(0.03, 0.04, 0.085), strength=1.0, sun_dir=sun_dir)
        L.sun(rot=(R(84), 0, R(168)), energy=0.6, color=(0.75, 0.7, 0.85), angle=8)
    else:
        M.dawn_sky(hor=(1.0, 0.62, 0.38), mid=(0.45, 0.38, 0.42), zen=(0.1, 0.14, 0.25), strength=1.2, sun_dir=sun_dir)
        L.sun(rot=(R(82), 0, R(170)), energy=3.0, color=(1.0, 0.72, 0.45), angle=3)
    sand = L.mat_noise_surface("sand", (0.38, 0.34, 0.28), (0.6, 0.55, 0.45), scale=9, bump=0.15, voronoi=False, rough=0.95)
    g = M.heightfield("sand", -70, 70, -60, 4, 120, 64,
                      lambda x, y: 0.06 * y + 0.12 * M.noise.noise(Vector((x * 0.1, y * 0.15, 0))) - 0.2 + (0.0 if y > -20 else (y + 20) * 0.03),
                      mat=sand)
    wet = L.mat_principled("wetsand", (0.16, 0.15, 0.13), rough=0.25)
    ws = L.prim("plane", loc=(0, -26, -1.95), size=1)
    ws.scale = (140, 8, 1)
    L.assign(ws, wet)
    M.sea(size=(400, 200), loc=(0, -130, -2.0), n=n, color=(0.03, 0.045, 0.06) if dawn < 0.5 else (0.08, 0.08, 0.09))
    M.surf_line(y=-24.5, z=-1.93, n=n, amp=1.4, period=4.5)
    M.seawall(length=140, h=1.7, y=0.0, steps_at=(-14.0, 22.0))
    # promenade + houses behind the wall
    prom = L.prim("plane", loc=(0, 8, 1.75), size=1)
    prom.scale = (140, 14, 1)
    L.assign(prom, L.mat_noise_surface("prom", (0.08, 0.08, 0.08), (0.16, 0.16, 0.15), scale=3, bump=0.1, voronoi=False))
    rail_m = L.mat_principled("rail", (0.03, 0.03, 0.03), rough=0.5, metal=0.5)
    rail = L.prim("cube", loc=(0, 0.3, 2.65))
    rail.scale = (70, 0.02, 0.02)
    L.assign(rail, rail_m)
    x = -60
    while x < 60:
        p = L.prim("cube", loc=(x, 0.3, 2.2))
        p.scale = (0.02, 0.02, 0.45)
        L.assign(p, rail_m)
        x += 2.0
    if houses:
        rnd = random.Random(4)
        hm = L.mat_principled("house", (0.035, 0.035, 0.04), rough=0.9)
        win = L.mat_emission("win", (1.0, 0.62, 0.3), 4.0)
        x = -60
        while x < 60:
            w = rnd.uniform(7, 11)
            h = rnd.uniform(4, 7)
            b = L.prim("cube", loc=(x + w / 2, 20 + rnd.uniform(-2, 3), 1.7 + h / 2))
            b.scale = (w / 2 - 0.6, 3, h / 2)
            L.assign(b, hm)
            rf = L.prim("cone", loc=(x + w / 2, b.location.y, 1.7 + h + 1.2), vertices=4, radius1=w * 0.6, depth=2.4, rot=(0, 0, R(45)))
            rf.scale = (1, 0.55, 1)
            L.assign(rf, hm)
            if rnd.random() < 0.35:
                wd = L.prim("plane", loc=(x + w / 2 + rnd.uniform(-1.5, 1.5), b.location.y - 3.02, 1.7 + h * 0.4), size=1,
                            rot=(math.pi / 2, 0, 0))
                wd.scale = (0.8, 1.0, 1)
                L.assign(wd, win)
            x += w
        # Norfolk-pine-ish silhouettes
        spots = [(rnd.uniform(-60, 60), rnd.uniform(12, 30), 1.7, rnd.uniform(10, 16)) for _ in range(9)]
        M.conifer_forest("pines", spots, mat=L.mat_principled("pine", (0.02, 0.025, 0.02), rough=0.9), seed=4, bare_frac=0.0)
    if lamps:
        lm = L.mat_principled("lamppost", (0.02, 0.02, 0.02), rough=0.5)
        for i, lx in enumerate((-30, -10, 10, 30)):
            post = L.prim("cyl", loc=(lx, 1.2, 1.7 + 2.0), vertices=8, radius=0.06, depth=4)
            L.assign(post, lm)
            bulb = L.prim("sphere", loc=(lx, 1.2, 5.8), radius=0.18, segments=12, ring_count=8)
            L.assign(bulb, L.mat_emission(f"lampb{i}", (1.0, 0.7, 0.38), 25 if dawn < 0.5 else 4))
            bulb.visible_shadow = False
            if dawn < 0.5:
                L.point((lx, 0.6, 5.6), energy=300, color=(1.0, 0.68, 0.36), radius=0.2, name=f"lamp{i}")
    if mist:
        M.fog((0, -10, 1.5), (140, 70, 8), density=mist, color=(0.7, 0.68, 0.75))
    fig = None
    if figure:
        fig = M.hiker("man", color=(0.012, 0.012, 0.015), height=1.75)
        M.seated_pose(fig)
        fig["root"].location = (4.0, -0.55, -0.05)
        fig["root"].rotation_euler = (0, 0, math.pi)
    return fig


def S03(L, n):
    beach(L, n, dawn=0.0, figure=False, mist=0.03)
    cam, ct = L.camera(loc=(-6, -40, 3.0), target=(0, 0, 3.0), lens=28)
    L.cam_keys(cam, [(1, (-6, -40, 3.0)), (n, (-2, -37, 3.0))])
    lin(cam)
    L.bake_static()


def S04(L, n):
    beach(L, n, dawn=0.0, figure=True, mist=0.025)
    cam, ct = L.camera(loc=(-3.0, -22.0, 1.4), target=(2.5, 0, 1.2), lens=35)
    L.cam_keys(cam, [(1, (-3.0, -22.0, 1.4)), (n, (0.5, -22.0, 1.4))])
    lin(cam)
    ct.keyframe_insert("location", frame=1)
    ct.location = (4.5, 0, 1.2)
    ct.keyframe_insert("location", frame=n)
    lin(ct)
    L.bake_static()


def S19(L, n):
    beach(L, n, dawn=1.0, figure=False, lamps=True, mist=0.02)
    cam, ct = L.camera(loc=(-8.0, -9.0, 1.2), target=(10, -1.5, 1.4), lens=28)
    L.cam_keys(cam, [(1, (-8.0, -9.0, 1.2)), (n, (-6.0, -8.0, 1.2))])
    lin(cam)
    L.bake_static()


# ----------------------------------------------------------------------------- S05 jacket, label cut out

def S05(L, n):
    desk_scene(L, n, lamp_energy=22, lamp_loc=(-0.55, 0.35, 0.0), lamp_target=(0, 0.1, 0))
    j = M.folded_jacket((0, 0, 0), rot_z=R(4))
    M.scissors((0.33, -0.12, 0), rot_z=R(-30))
    # a couple of loose cut threads near the label patch
    th = L.mat_principled("thread", (0.6, 0.55, 0.45), rough=0.8)
    for i in range(3):
        t = L.prim("cyl", loc=(0.03 * i - 0.02, 0.2 + 0.045 + 0.004 * i, 0.054), vertices=4, radius=0.0007, depth=0.015,
                   rot=(math.pi / 2, 0, 0.6 * i))
        L.assign(t, th)
    c0, c1 = (0.12, -0.12, 0.62), (0.01, 0.18, 0.42)
    cam, ct = L.camera(loc=c0, target=(0.06, -0.1, 0), lens=50)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    lin(cam)
    ct.keyframe_insert("location", frame=1)
    ct.location = (0.0, 0.2, 0.05)
    ct.keyframe_insert("location", frame=n)
    lin(ct)
    L.bake_static()


# ----------------------------------------------------------------------------- S06 / S07 cloakroom

def cloakroom(L, n, lamp_e=260):
    L.set_world((0.003, 0.003, 0.004), 1.0)
    fl = L.prim("plane", loc=(0, -2, 0), size=1)
    fl.scale = (12, 8, 1)
    L.assign(fl, L.mat_noise_surface("floor", (0.03, 0.025, 0.02), (0.08, 0.065, 0.05), scale=6, bump=0.2, voronoi=False))
    wall = L.prim("plane", loc=(0, 1.5, 2), size=1, rot=(math.pi / 2, 0, 0))
    wall.scale = (12, 4, 1)
    L.assign(wall, L.mat_noise_surface("cwall", (0.07, 0.07, 0.06), (0.15, 0.14, 0.12), scale=3, bump=0.25, voronoi=False))
    M.luggage_shelf(x_range=(-4, 4), y=1.0, levels=(0.0, 0.9, 1.8), skip_slot=(1, 0.3))
    case = M.suitcase((0.3, 1.0, 1.32), size=(0.66, 0.22, 0.42), color=(0.24, 0.12, 0.05), name="thecase", tag_string=True)
    shade = L.prim("cone", loc=(0.3, -0.2, 3.1), vertices=24, radius1=0.3, radius2=0.06, depth=0.25)
    L.assign(shade, L.mat_principled("shade", (0.05, 0.06, 0.05), rough=0.4, metal=0.7))
    cord = L.prim("cyl", loc=(0.3, -0.2, 3.8), vertices=6, radius=0.008, depth=1.2)
    L.assign(cord, L.mat_principled("cord", (0.02, 0.02, 0.02)))
    bulb = L.prim("sphere", loc=(0.3, -0.2, 2.98), radius=0.06, segments=12, ring_count=8)
    L.assign(bulb, L.mat_emission("bulb", (1.0, 0.75, 0.45), 30))
    bulb.visible_shadow = False
    lamp = L.spot((0.3, -0.2, 2.95), (R(18), 0, 0), energy=lamp_e * 3, size_deg=80, blend=0.7, color=(1.0, 0.72, 0.42), name="lamp", radius=0.08)
    L.flicker(lamp, n, depth=0.15, rate=0.5, seed=3)
    L.area((-3, -3, 2.5), (R(60), 0, R(-40)), energy=25, size=3, color=(0.5, 0.6, 0.85), name="coldfill")
    L.particle_cloud((0.3, 0.2, 1.6), (2.0, 1.5, 2.0), count=400, radius=0.003, drift=(0.02, 0, -0.01), nframes=n,
                     mat=L.mat_principled("dust", (0.9, 0.8, 0.6), emit=(1, 0.8, 0.5), emit_strength=0.4))
    return case, lamp


def S06(L, n):
    case, lamp = cloakroom(L, n)
    case.location = (0.3, 1.0, 1.32)
    case.keyframe_insert("location", frame=1)
    case.keyframe_insert("location", frame=8)
    case.location = (0.3, 0.72, 1.32)
    case.keyframe_insert("location", frame=34)
    c0, c1 = (-1.4, -3.4, 1.7), (-0.6, -1.9, 1.55)
    cam, ct = L.camera(loc=c0, target=(0.3, 0.9, 1.45), lens=35)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    lin(cam)
    L.handheld(cam, n, amp=0.008)
    L.bake_static()


def S07(L, n):
    case, lamp = cloakroom(L, n)
    case.location = (0.3, 0.72, 1.32)
    c0, c1 = (0.62, 0.05, 1.86), (0.55, 0.16, 1.82)
    cam, ct = L.camera(loc=c0, target=(0.36, 0.68, 1.65), lens=50)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    lin(cam)
    L.dof(cam, distance=0.62, fstop=2.8)
    L.bake_static()


# ----------------------------------------------------------------------------- S08 - S10 the book

BOOK_TITLE = "THE\nRUBAIYAT\nOF\nOMAR KHAYYAM"


def S08(L, n):
    desk_scene(L, n, lamp_energy=16)
    bk = M.book((0.0, 0.03, 0.0), title=BOOK_TITLE, rot_z=R(-6))
    bk.location = (0.0, 0.03, 0.22)
    bk.rotation_euler = (R(-12), R(8), R(-20))
    bk.keyframe_insert("location", frame=1)
    bk.keyframe_insert("rotation_euler", frame=1)
    bk.location = (0.0, 0.03, 0.0)
    bk.rotation_euler = (0, 0, R(-6))
    bk.keyframe_insert("location", frame=6)
    bk.keyframe_insert("rotation_euler", frame=6)
    bk.location = (0.0, 0.03, 0.004)
    bk.keyframe_insert("location", frame=8)
    bk.location = (0.0, 0.03, 0.0)
    bk.keyframe_insert("location", frame=10)
    M.snow_burst((0.0, 0.03, 0.01), n, 6, count=250, radius=0.0012, spread=0.25, rise=0.05, seed=81, name="puff", emit=0.4)
    # the scrap slides in and aligns with the book's edge (the matched tear)
    root, paper, bd = M.rolled_scrap((0.25, -0.12, 0.0006), rot_z=R(-96))
    bd.angle = R(6)
    root.keyframe_insert("location", frame=1)
    root.keyframe_insert("location", frame=22)
    root.location = (0.095, -0.06, 0.0006)
    root.keyframe_insert("location", frame=46)
    root.rotation_euler = (0, 0, R(-96))
    root.keyframe_insert("rotation_euler", frame=22)
    root.rotation_euler = (0, 0, R(-96 + 0))
    root.keyframe_insert("rotation_euler", frame=46)
    # match-cut highlight: thin glowing line at the book's edge when the strip lands
    gl = L.prim("cube", loc=(0.067, 0.03 - 0.05, 0.004), name="matchline")
    gl.scale = (0.0012, 0.05, 0.0012)
    gl.rotation_euler = (0, 0, R(-6))
    L.assign(gl, L.mat_emission("matchline_m", (1.0, 0.85, 0.55), 8))
    M.hide_until(gl, 46)
    piv = M.empty("orbit", (0.03, 0.0, 0))
    cam, ct = L.camera(loc=(0.05, -0.42, 0.3), target=(0.04, 0.0, 0.01), lens=50)
    cam.parent = piv
    piv.rotation_euler = (0, 0, R(-6))
    piv.keyframe_insert("rotation_euler", frame=1)
    piv.rotation_euler = (0, 0, R(8))
    piv.keyframe_insert("rotation_euler", frame=n)
    lin(piv)
    L.bake_static()


def S09(L, n):
    desk_scene(L, n, lamp_energy=14)
    bk = M.book((0.0, 0.0, 0.0), title=BOOK_TITLE, rot_z=R(-4))
    c0, c1 = (0.03, -0.36, 0.22), (0.02, -0.29, 0.18)
    cam, ct = L.camera(loc=c0, target=(0.0, 0.01, 0.022), lens=85)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    lin(cam)
    L.dof(cam, target=bk, fstop=4.0)
    L.bake_static()


CODE = ["WRGOABABD", "MLIAOI", "WTBIMPANETP", "MLIABOAIAQC", "ITTMTSAMSTGAB"]


def back_cover(L, n, flip=True, uv=True):
    desk_scene(L, n, lamp_energy=10, cold_fill=0.3)
    bk = M.book((0.0, 0.0, 0.0), title=BOOK_TITLE, rot_z=0)
    pencil = L.mat_principled("pencil", (0.25, 0.25, 0.27), rough=0.5, emit=(0.75, 0.55, 1.0), emit_strength=0.0)
    holder = M.empty("codeholder", (0, 0, -0.0004))
    holder.parent = bk
    holder.rotation_euler = (0, math.pi, 0)
    for i, line in enumerate(CODE):
        t = L.text3d(line, loc=(0, 0.045 - i * 0.017, 0), rot=(0, 0, 0), size=0.011, extrude=0, mat=pencil, name=f"code{i}")
        t.data.font = M._font(M.F_SERIF)
        t.parent = holder
        if i == 1:
            st = L.prim("cube", loc=(0, 0.045 - i * 0.017 + 0.003, 0))
            st.scale = (0.03, 0.0005, 0.0002)
            L.assign(st, pencil)
            st.parent = holder
    # phone number: deliberately unreadable smudges (number is not shown)
    sm = L.mat_principled("smudge", (0.3, 0.3, 0.32), rough=0.6, emit=(0.7, 0.5, 1.0), emit_strength=0.0)
    for k in range(7):
        s = L.prim("plane", loc=(-0.035 + k * 0.009, -0.07, 0), size=1)
        s.scale = (0.006, 0.009, 1)
        L.assign(s, sm)
        s.parent = holder
    if flip:
        bk.location = (0.0, 0.0, 0.0)
        bk.rotation_euler = (0, 0, 0)
        bk.keyframe_insert("rotation_euler", frame=1)
        bk.keyframe_insert("location", frame=1)
        bk.location = (0.0, 0.0, 0.07)
        bk.rotation_euler = (0, math.pi / 2, 0)
        bk.keyframe_insert("location", frame=8)
        bk.keyframe_insert("rotation_euler", frame=8)
        bk.location = (0.0, 0.0, 0.022)
        bk.rotation_euler = (0, math.pi, 0)
        bk.keyframe_insert("location", frame=15)
        bk.keyframe_insert("rotation_euler", frame=15)
    else:
        bk.location = (0, 0, 0.022)
        bk.rotation_euler = (0, math.pi, 0)
    if uv:
        uvl = L.area((-0.3, 0, 0.25), (0, R(-40), 0), energy=8, size=0.15, color=(0.5, 0.2, 1.0), name="uv")
        uvl.keyframe_insert("location", frame=20)
        uvl.location = (0.3, 0, 0.25)
        uvl.rotation_euler = (0, R(40), 0)
        uvl.keyframe_insert("location", frame=n)
        for mm in (pencil, sm):
            p = mm.node_tree.nodes["Principled BSDF"]
            p.inputs["Emission Strength"].default_value = 0.0
            p.inputs["Emission Strength"].keyframe_insert("default_value", frame=20)
            p.inputs["Emission Strength"].default_value = 1.6
            p.inputs["Emission Strength"].keyframe_insert("default_value", frame=min(n, 50))
    return bk


def S10(L, n):
    back_cover(L, n, flip=True, uv=True)
    cam, ct = L.camera(loc=(0.0, -0.02, 0.5), target=(0, 0.0, 0), lens=50)
    L.cam_keys(cam, [(1, (0.0, -0.02, 0.5)), (n, (0.0, -0.015, 0.46))])
    lin(cam)
    L.bake_static()


def code_plate(L, n, z0, z1, blur=True):
    back_cover(L, n, flip=False, uv=False)
    cam, ct = L.camera(loc=(0.03, -0.12, z0), target=(0, 0.02, 0.02), lens=50)
    L.cam_keys(cam, [(1, (0.03, -0.12, z0)), (n, (0.02, -0.1, z1))])
    lin(cam)
    if blur:
        L.dof(cam, distance=0.08, fstop=1.4)
    L.bake_static()


def S11(L, n):
    code_plate(L, n, 0.42, 0.36)


def S20(L, n):
    code_plate(L, n, 0.38, 0.33)


def S21(L, n):
    code_plate(L, n, 0.33, 0.27)


def S12(L, n):
    # inquest beat: dim desk plate, the plaster bust silhouette far back in the dark, lamp low
    desk_scene(L, n, lamp_energy=8, lamp_target=(0.1, 0.25, 0.1), cold_fill=0.8)
    M.plaster_bust((0.12, 0.35, 0.0), scale=0.7)
    M.book((-0.12, -0.05, 0.0), title=BOOK_TITLE, rot_z=R(15))
    cam, ct = L.camera(loc=(-0.05, -0.75, 0.32), target=(0.05, 0.2, 0.12), lens=50)
    L.cam_keys(cam, [(1, (-0.05, -0.75, 0.32)), (n, (0.0, -0.62, 0.29))])
    lin(cam)
    L.dof(cam, distance=0.95, fstop=2.0)
    L.bake_static()


# ----------------------------------------------------------------------------- S13 theory board

CARDS = [("SPY", (-0.6, -0.01, 1.05), R(-4)), ("LOST\nLOVE", (0.55, -0.01, 0.15), R(5)), ("SUICIDE", (-0.45, -0.01, -0.85), R(-3))]


def S13(L, n):
    L.set_world((0.002, 0.002, 0.003), 1.0)
    M.evidence_board(lamp_energy=200)
    L.particle_cloud((0, -1.2, 0.5), (3, 2, 4), count=500, radius=0.004, drift=(0.03, 0, -0.03), nframes=n,
                     mat=L.mat_principled("dust", (0.9, 0.8, 0.6), emit=(1, 0.8, 0.5), emit_strength=0.4))
    # blank silhouette card at the centre-right
    sil = M.paper_card(" ", (0.75, -0.01, 1.55), rot_y=R(3), badge=None, name="unknown", size=(0.6, 0.75))
    dark = L.mat_principled("sil", (0.02, 0.02, 0.022), rough=0.8)
    hd = L.prim("sphere", loc=(0, -0.008, 0.08), radius=1, segments=16, ring_count=8)
    hd.scale = (0.1, 0.002, 0.125)
    sh = L.prim("sphere", loc=(0, -0.008, -0.25), radius=1, segments=16, ring_count=8)
    sh.scale = (0.24, 0.002, 0.15)
    for o in (hd, sh):
        L.assign(o, dark)
        o.parent = sil
    qm = L.text3d("?", loc=(0, -0.012, 0.03), size=0.16, extrude=0, mat=L.mat_principled("qm", (0.6, 0.55, 0.45)), name="qm")
    qm.parent = sil
    hits = [5, 22, 41]
    roots = []
    for i, ((txt, loc, rot), f) in enumerate(zip(CARDS, hits)):
        r = M.paper_card(txt, loc, rot_y=rot, name=f"card{i}", text_size=0.22 if "\n" not in txt else 0.17)
        M.hide_until(r, f - 5)
        M.slam_in(r, f, lead=5)
        roots.append(r)
    # red string from each card pin to the silhouette card, appears with the card
    sm = L.mat_principled("string", (0.55, 0.02, 0.02), rough=0.6, emit=(0.4, 0.0, 0.0), emit_strength=0.3)
    tgt = Vector((0.75, -0.04, 1.55 + 0.375 - 0.06))
    for i, ((txt, loc, rot), f) in enumerate(zip(CARDS, hits)):
        a = Vector((loc[0], -0.04, loc[2] + 0.31 - 0.06))
        d = tgt - a
        st = L.prim("cyl", loc=(a + tgt) / 2, vertices=6, radius=0.006, depth=d.length)
        st.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        L.assign(st, sm)
        M.hide_until(st, f + 3)
    cam, ct = L.camera(loc=(0.05, -4.6, 0.25), target=(0.05, 0, 0.2), lens=35)
    keys = [(1, (0.05, -4.6, 0.25))]
    y = -4.6
    for f in hits:
        keys.append((f, (0.05, y, 0.25)))
        y += 0.17
        keys.append((f + 4, (0.05, y, 0.25)))
    keys.append((n, (0.05, y + 0.1, 0.25)))
    L.cam_keys(cam, keys)
    M.shake(cam, hits, amp=0.02, decay=6)
    L.bake_static()


# ----------------------------------------------------------------------------- S14 cemetery

def S14(L, n):
    M.night_sky(stars=0.5, hor=(0.02, 0.025, 0.04))
    M.moon(rot=(R(60), 0, R(-140)), energy=0.9, color=(0.55, 0.65, 1.0))
    grass = L.mat_noise_surface("cgrass", (0.015, 0.02, 0.012), (0.05, 0.055, 0.035), scale=10, bump=0.3, voronoi=False)
    M.heightfield("cground", -40, 40, -30, 60, 80, 90, lambda x, y: 0.15 * M.noise.noise(Vector((x * 0.1, y * 0.1, 0))), mat=grass)
    stone = L.mat_noise_surface("stone", (0.18, 0.18, 0.17), (0.38, 0.37, 0.35), scale=6, bump=0.4)
    rnd = random.Random(5)
    for row in range(9):
        for col in range(-7, 8):
            if rnd.random() < 0.12:
                continue
            x = col * 2.2 + rnd.uniform(-0.2, 0.2)
            y = row * 3.2 + rnd.uniform(-0.2, 0.2)
            if row == 1 and col == 0:
                continue
            M.headstone((x, y, 0), rot_z=rnd.uniform(-0.08, 0.08), w=rnd.uniform(0.5, 0.75), h=rnd.uniform(0.7, 1.1),
                        mat=stone, kind=rnd.choice((0, 0, 1, 2)), name=f"hs{row}_{col}")
    # the lit plot: plain headstone, low barrier tape posts, work light on tripod
    M.headstone((0, 3.2, 0), w=0.6, h=0.85, mat=stone, kind=1, name="plotstone")
    plot = L.prim("plane", loc=(0, 2.0, 0.03), size=1)
    plot.scale = (1.0, 2.0, 1)
    L.assign(plot, L.mat_noise_surface("tarp", (0.02, 0.05, 0.08), (0.04, 0.09, 0.14), scale=8, bump=0.2, voronoi=False, rough=0.4))
    tape = L.mat_principled("tape", (0.8, 0.6, 0.05), rough=0.5, emit=(0.6, 0.45, 0.02), emit_strength=0.2)
    for (x, y) in ((-1.3, 0.5), (1.3, 0.5), (1.3, 3.6), (-1.3, 3.6)):
        p = L.prim("cyl", loc=(x, y, 0.45), vertices=6, radius=0.02, depth=0.9)
        L.assign(p, tape)
    for (a, b) in (((-1.3, 0.5), (1.3, 0.5)), ((1.3, 0.5), (1.3, 3.6)), ((-1.3, 0.5), (-1.3, 3.6))):
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.82)
        t = L.prim("cube", loc=mid)
        t.scale = (max(0.005, abs(b[0] - a[0]) / 2), max(0.005, abs(b[1] - a[1]) / 2), 0.02)
        L.assign(t, tape)
    wl, sp = M.work_light((2.4, 0.2, 0), (0, 2.6, 0.2), energy=1800)
    L.flicker(sp, n, depth=0.12, rate=0.6, seed=7)
    M.fog((0, 15, 1.2), (80, 60, 3.5), density=0.06, color=(0.6, 0.65, 0.75))
    c0, c1 = (-2.8, -7.5, 6.0), (-2.2, -6.0, 1.9)
    cam, ct = L.camera(loc=c0, target=(0.2, 2.6, 0.4), lens=35)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    L.bake_static()


# ----------------------------------------------------------------------------- S15 lab

def S15(L, n):
    L.set_world((0.01, 0.012, 0.015), 1.0)
    bench = L.prim("cube", loc=(0, 0, -0.02))
    bench.scale = (1.4, 0.6, 0.02)
    L.assign(bench, L.mat_principled("bench", (0.75, 0.77, 0.78), rough=0.35))
    tiles = L.mat_grid("tiles", color=(0.25, 0.27, 0.3), bg=(0.5, 0.53, 0.55), scale=7, width=0.05, strength=0.05)[0]
    wall = L.prim("plane", loc=(0, 0.6, 0.6), size=1, rot=(math.pi / 2, 0, 0))
    wall.scale = (3, 1.4, 1)
    wp = L.mat_noise_surface("labwall", (0.18, 0.2, 0.22), (0.3, 0.32, 0.34), scale=3, bump=0.05, voronoi=False)
    L.assign(wall, wp)
    M.plaster_bust((-0.18, 0.15, 0.0), scale=0.75)
    tube, liq = M.test_tube((0.16, -0.02, 0.0))
    rack = L.prim("cube", loc=(0.16, -0.02, 0.03))
    rack.scale = (0.05, 0.025, 0.03)
    L.assign(rack, L.mat_principled("rack", (0.85, 0.85, 0.85), rough=0.4))
    tw = M.tweezers((-0.05, -0.03, 0.2), rot=(0, R(30), 0))
    hair = L.prim("cyl", loc=(0, 0, -0.03), vertices=4, radius=0.0005, depth=0.05)
    L.assign(hair, L.mat_principled("hair", (0.05, 0.04, 0.03)))
    hair.parent = tw
    tw.keyframe_insert("location", frame=1)
    tw.keyframe_insert("rotation_euler", frame=1)
    tw.location = (0.16, -0.02, 0.24)
    tw.rotation_euler = (0, 0, 0)
    tw.keyframe_insert("location", frame=int(n * 0.6))
    tw.keyframe_insert("rotation_euler", frame=int(n * 0.6))
    tw.location = (0.16, -0.02, 0.17)
    tw.keyframe_insert("location", frame=n)
    lp = L.area((0, -0.2, 0.9), (R(12), 0, 0), energy=18, size=0.6, color=(0.85, 0.93, 1.0), name="lablight")
    L.point((0.16, -0.06, 0.08), energy=0.6, color=(0.3, 0.9, 1.0), radius=0.02, name="tubeglow")
    c0, c1 = (-0.1, -0.85, 0.32), (0.1, -0.45, 0.2)
    cam, ct = L.camera(loc=c0, target=(-0.02, 0.05, 0.15), lens=50)
    L.cam_keys(cam, [(1, c0), (n, c1)])
    ct.keyframe_insert("location", frame=1)
    ct.location = (0.14, 0.0, 0.1)
    ct.keyframe_insert("location", frame=n)
    L.dof(cam, target=tube, fstop=4.0)
    L.bake_static()


# ----------------------------------------------------------------------------- S16 - S18 DNA / family tree

def tree_graphic(L, n, slot_color=(0.3, 0.9, 1.0), slot_strength=3.0, draw=(10, 50)):
    L.set_world((0, 0, 0.002), 1.0)
    lm = L.mat_emission("treeline", (0.25, 0.8, 1.0), 3.0)
    rnd = random.Random(3)
    # three generations of nodes converging to one slot at the bottom
    gens = [[(-3.0 + 0.85 * i, 4.2) for i in range(8)], [(-2.55 + 1.7 * i, 2.6) for i in range(4)], [(-1.7, 1.0), (1.7, 1.0)]]
    end = (0.0, -0.6)
    curves = []
    nodes_m = L.mat_emission("node", (0.85, 0.95, 1.0), 4.0)
    for g, gen in enumerate(gens):
        nxt = gens[g + 1] if g + 1 < len(gens) else [end]
        for i, p in enumerate(gen):
            q = nxt[min(len(nxt) - 1, i * len(nxt) // len(gen))]
            c = M.tree_lines([p], q, lm, name=f"tl{g}_{i}")[0]
            M.curve_draw(c, draw[0] + g * (draw[1] - draw[0]) // 3, draw[0] + (g + 1) * (draw[1] - draw[0]) // 3)
            curves.append(c)
            nd = L.prim("cube", loc=(p[0], 0, p[1]))
            nd.scale = (0.18, 0.01, 0.1)
            L.assign(nd, nodes_m)
    # the empty name slot
    slot_m = L.mat_emission("slot", slot_color, slot_strength)
    for (x, z, sx, sz) in ((0, -0.6 + 0.0, 1.2, 0.02), (0, -1.3, 1.2, 0.02), (-1.2, -0.95, 0.02, 0.35), (1.2, -0.95, 0.02, 0.35)):
        b = L.prim("cube", loc=(x, 0, z))
        b.scale = (sx, 0.02, sz)
        L.assign(b, slot_m)
    return slot_m, curves


def S16(L, n):
    tree_graphic(L, n, draw=(int(n * 0.35), int(n * 0.85)))
    root, objs = M.dna_helix(n_pairs=22, radius=0.55, pitch=2.6, height=4.2)
    root.location = (0, 0, 1.8)
    root.rotation_euler = (0, R(90), 0)
    root.keyframe_insert("rotation_euler", frame=1)
    root.rotation_euler = (R(160), R(90), 0)
    root.keyframe_insert("rotation_euler", frame=n)
    lin(root)
    root.scale = (1, 1, 1)
    root.keyframe_insert("scale", frame=int(n * 0.3))
    root.scale = (0.45, 0.45, 0.45)
    root.location = (0, 0, 4.9)
    root.keyframe_insert("scale", frame=int(n * 0.7))
    root.keyframe_insert("location", frame=int(n * 0.7))
    root.location = (0, 0, 1.8)
    root.keyframe_insert("location", frame=int(n * 0.3))
    cam, ct = L.camera(loc=(0, -5.0, 1.9), target=(0, 0, 1.8), lens=35)
    L.cam_keys(cam, [(1, (0, -5.0, 1.9)), (int(n * 0.3), (0.3, -5.2, 1.9)), (n, (0, -12.5, 1.6))])
    ct.keyframe_insert("location", frame=1)
    ct.keyframe_insert("location", frame=int(n * 0.3))
    ct.location = (0, 0, 1.4)
    ct.keyframe_insert("location", frame=n)
    L.bake_static()


def S17(L, n):
    # colour flips cold -> warm as the slot fills with the proposed name
    slot_m, curves = tree_graphic(L, n, draw=(1, 2))
    em = [nd for nd in slot_m.node_tree.nodes if nd.type == "EMISSION"][0]
    em.inputs[0].default_value = (0.3, 0.9, 1.0, 1)
    em.inputs[0].keyframe_insert("default_value", frame=1)
    em.inputs[0].default_value = (1.0, 0.62, 0.2, 1)
    em.inputs[0].keyframe_insert("default_value", frame=10)
    em.inputs[1].default_value = 8.0
    em.inputs[1].keyframe_insert("default_value", frame=10)
    fill = L.prim("cube", loc=(0, 0.03, -0.95))
    fill.scale = (1.15, 0.01, 0.32)
    L.assign(fill, L.mat_emission("slotfill", (1.0, 0.55, 0.2), 1.2))
    M.hide_until(fill, 6)
    L.particle_cloud((0, -0.5, 0.5), (8, 2, 8), count=600, radius=0.012, drift=(0, 0, 0.05), nframes=n,
                     mat=L.mat_emission("embers", (1.0, 0.6, 0.25), 3.0))
    cam, ct = L.camera(loc=(0, -12.5, 1.6), target=(0, 0, 1.4), lens=35)
    L.cam_keys(cam, [(1, (0, -12.5, 1.6)), (n, (0, -7.0, 0.2))])
    ct.keyframe_insert("location", frame=1)
    ct.location = (0, 0, -0.3)
    ct.keyframe_insert("location", frame=n)
    L.bake_static()


def S18(L, n):
    slot_m, curves = tree_graphic(L, n, slot_color=(1.0, 0.6, 0.2), slot_strength=5, draw=(1, 2))
    fill = L.prim("cube", loc=(0, 0.03, -0.95))
    fill.scale = (1.15, 0.01, 0.32)
    L.assign(fill, L.mat_emission("slotfill", (0.6, 0.3, 0.12), 0.8))
    red = L.point((0, -2, -0.5), energy=0, color=(1.0, 0.1, 0.08), radius=0.5)
    cam, ct = L.camera(loc=(0, -7.0, 0.2), target=(0, 0, -0.3), lens=35)
    L.cam_keys(cam, [(1, (0, -7.0, 0.2)), (n, (0, -6.6, 0.15))])
    lin(cam)
    M.shake(cam, [10], amp=0.06, decay=8)
    L.bake_static()
