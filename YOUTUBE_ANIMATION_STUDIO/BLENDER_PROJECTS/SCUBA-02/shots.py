"""SCUBA-02 — The Dive Boat Left Without Them (Tom & Eileen Lonergan, St Crispin's Reef, 1998).
One builder per shot: def Sxx(L, n). Scuba builders live in PIPELINE/blender/lib_scuba.py.
Real people are faceless figures; no bodies, no sharks.
"""
import sys, os, math, random, importlib
import bpy
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_scuba as S
importlib.reload(S)

PI = math.pi
GOLD = dict(top=(0.05, 0.16, 0.45), horizon=(1.0, 0.55, 0.25), sun_col=(1.0, 0.68, 0.38))
S01_CAM_A = (0.15, -2.2, 1.0)
S01_CAM_B = (0.1, -1.6, 0.95)
S01_TGT = (0.0, 30.0, 0.9)
S01_BOB = 0.9  # phase


# ----------------------------------------------------------------------------- helpers

def _finish(L):
    """Area fills never scatter in volumes (they show as glowing rectangles), then bake static modifiers."""
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "AREA":
            o.data.volume_factor = 0.0
    L.bake_static()


def sun_vec(elev_deg, az_deg):
    e, a = math.radians(elev_deg), math.radians(az_deg)
    return Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))


def surface_env(L, n, elev=12, az=8, top=GOLD["top"], horizon=GOLD["horizon"], sun_col=GOLD["sun_col"], sun_energy=4.5,
                wave=1.0, chop=1.0, wind=11, deep=(0.0, 0.07, 0.11), shallow=(0.0, 0.25, 0.3), t0=1.0, sky_strength=1.0,
                ocean_size=120, res=9, sun_disc=12.0, far=True, rough=0.06):
    S.setup(vol_end=100)
    sv = sun_vec(elev, az)
    S.sky_gradient(top=top, horizon=horizon, strength=sky_strength, sun_dir=sv, sun_col=sun_col, sun_size=0.012,
                   sun_strength=sun_disc, below=tuple(c * 0.4 for c in deep))
    m = S.mat_ocean("sea", deep=deep, shallow=shallow, rough=rough)
    sea = S.ocean(size=ocean_size, nframes=n, wave_scale=wave, choppiness=chop, resolution=res, spatial=40, wind=wind,
                  mat=m, t0=t0, repeat=1)
    if far:
        fp = L.prim("plane", loc=(0, 0, -0.35), size=6000, name="farsea")
        L.assign(fp, m)
    s = L.sun(rot=(0, 0, 0), energy=sun_energy, color=sun_col, angle=0.8)
    s.rotation_euler = (-sv).to_track_quat("-Z", "Y").to_euler()
    return sea, s


def far_cam(cam):
    cam.data.clip_end = 6000
    cam.data.clip_start = 0.05
    return cam


def two_divers(L, n, a=(-0.55, 4.2), b=(0.6, 4.9), phase=0.0, end_match=None):
    """The Lonergans at the surface: two swimmers bobbing, backs to camera."""
    out = []
    for i, (p, bcd) in enumerate(((a, (0.05, 0.12, 0.32)), (b, (0.08, 0.3, 0.35)))):
        sw = S.swimmer(f"diver{i}", bcd=bcd, seed=i)
        r = sw["root"]
        r.location = (p[0], p[1], -0.02)
        r.rotation_euler = (0, 0, 0.15 * (1 - 2 * i))
        ph = phase + i * 1.7
        S.bob(r, n + 2, amp=0.1, rate=0.32, phase=ph, tilt=0.05)
        out.append(sw)
    return out


def boat_on_horizon(L, n, dist=240, x=-18, recede=30, name="boat"):
    b, _ = S.dive_boat(name)
    r = b
    r.rotation_euler = (0, 0, 0.15)
    L.cam_keys(r, [(1, (x, dist, -0.2)), (n, (x - 4, dist + recede, -0.3))], ease=False)
    w = S.wake(start=(0, -8.5, 0.05), length=dist * 0.85, width0=3, width1=16, angle=0.0, name=name + "_wake", strength=0.9)
    w.parent = r
    w.location = (0, 0, 0.25)
    return r


# ----------------------------------------------------------------------------- S01 / S18 the empty horizon

def _horizon_shot(L, n, cam_from, cam_to, t0=1.0, phase=S01_BOB, boat_from=(-18, 240), recede=40):
    surface_env(L, n, elev=11, az=6, t0=t0, wave=1.3, chop=1.1)
    two_divers(L, n, phase=phase)
    boat_on_horizon(L, n, dist=boat_from[1], x=boat_from[0], recede=recede)
    cam, tgt = L.camera(loc=cam_from, target=S01_TGT, lens=35)
    far_cam(cam)
    L.cam_keys(cam, [(1, cam_from), (n, cam_to)])
    # swell lifting the camera (deterministic, phase-matched for the loop)
    return cam


def S01(L, n):
    cam = _horizon_shot(L, n, S01_CAM_A, S01_CAM_B)
    _swell(cam, n, S01_CAM_A, S01_CAM_B, 0.0)
    _finish(L)


def _swell(cam, n, a, b, ph):
    for f in range(1, n + 1, 3):
        t = (f - 1) / max(1, n - 1)
        p = Vector(a).lerp(Vector(b), t * t * (3 - 2 * t))
        z = p.z + 0.12 * math.sin(2 * PI * 0.28 * (f / 24) + ph)
        cam.location = (p.x, p.y, z)
        cam.keyframe_insert("location", frame=f)


def S18(L, n):
    # ends exactly where S01 begins (camera, ocean time, bob phase), then hard cut back to S01
    start = (0.2, -2.8, 1.05)
    t0 = 1.0 - (n - 1) / 24
    phase = S01_BOB - 2 * PI * 0.32 * (n - 1) / 24
    cam = _horizon_shot(L, n, start, S01_CAM_A, t0=t0, phase=phase, boat_from=(-18, 240), recede=0)
    # boat already gone in the loop-back: hide it (empty horizon)
    for o in bpy.data.objects:
        if o.name.startswith("boat"):
            o.hide_render = True
    ph = -2 * PI * 0.28 * (n - 1) / 24
    _swell(cam, n, start, S01_CAM_A, ph)
    _finish(L)


# ----------------------------------------------------------------------------- S02 / S10 map backgrounds

def _aerial_reef_bg(L, n, drift=(6, 4)):
    S.setup()
    S.sky_gradient(top=(0.3, 0.5, 0.8), horizon=(0.8, 0.85, 0.9))
    sb = L.prim("plane", loc=(0, 0, -4), size=200, name="reefbed")
    L.assign(sb, S.mat_caustic_ground("rb", c1=(0.1, 0.35, 0.35), c2=(0.6, 0.62, 0.45), strength=0.4, scale=0.15, nframes=n,
                                      base_scale=0.05))
    m = S.mat_water_surface("aerialw", color=(0.0, 0.25, 0.3), rough=0.05, alpha=0.55, ripple=0.3, nframes=n)
    w = L.prim("plane", loc=(0, 0, 0), size=200, name="aerialwater")
    L.assign(w, m)
    L.sun(rot=(0.5, 0.2, 0.4), energy=4, color=(1, 0.95, 0.85))
    cam, _ = L.camera(loc=(0, 0, 60), lens=35)
    cam.rotation_euler = (0, 0, 0.3)
    L.cam_keys(cam, [(1, (0, 0, 60)), (n, (drift[0], drift[1], 54))], ease=False)
    _finish(L)


def S02(L, n):
    _aerial_reef_bg(L, n)


def S10(L, n):
    _aerial_reef_bg(L, n, drift=(-5, 6))


# ----------------------------------------------------------------------------- S03 bright reef

def reef_env(L, n, vol=0.07, depth=8.0):
    S.setup(vol_end=60)
    L.set_world(color=(0.05, 0.35, 0.5), strength=1.0)
    S.world_volume(color=(0.1, 0.55, 0.7), density=vol, anisotropy=0.6, absorption=(0.6, 0.9, 0.95),
                   center=(0, 0, -depth / 2 - 1), size=(70, 70, depth + 1.9))
    sb = L.seabed(size=80, strength=0.6, mat=S.mat_caustic_ground("reefsand", c1=(0.16, 0.22, 0.2), c2=(0.34, 0.38, 0.32),
                                                                   nframes=n, strength=0.9, scale=0.5,
                                                                   caustic=(0.7, 1.0, 0.95)))
    sb.location.z = -depth
    corals = L.coral_field(area=8, count=70, seed=4, z=-depth + 0.1)
    surf = L.prim("plane", loc=(0, 0, 0), size=120, name="undersurface")
    L.assign(surf, S.mat_water_surface("usurf", color=(0.2, 0.5, 0.6), rough=0.1, alpha=1.0, under_color=(0.3, 0.75, 0.85),
                                       under_strength=1.0, ripple=0.4, nframes=n))
    surf.visible_shadow = False
    L.sun(rot=(0.25, 0.1, 0.3), energy=5, color=(0.85, 1.0, 1.0), angle=4)
    S.god_rays(center=(0, 3, -0.1), count=8, length=10, spread=7, tilt=(0.25, 0.1), color=(0.8, 1.0, 1.0), strength=1.0,
               alpha=0.22, nframes=n)
    return sb


def S03(L, n):
    reef_env(L, n)
    divers = []
    for i, (x, col) in enumerate(((-0.6, (0.9, 0.35, 0.05)), (0.7, (0.2, 0.6, 0.9)))):
        dv = L.char_diver(f"ld{i}", suit=(0.03, 0.03, 0.04), accent=col, tanks="single", light_on=False)
        L.path_follow(dv["root"], [(x, -4 + 0.4 * i, -4.6 - 0.3 * i), (x + 0.1, 2.5 + 0.4 * i, -4.4 - 0.3 * i)], 1, n, ease=False)
        L.anim_swim(dv, n, kick_rate=0.8 + 0.1 * i, amp=0.3, arm_sweep=False)
        car = bpy.data.objects.new(f"bc{i}", None)
        bpy.context.scene.collection.objects.link(car)
        L.path_follow(car, [(x, -3.5 + 0.4 * i, -4.2 - 0.3 * i), (x + 0.1, 3.0 + 0.4 * i, -4.0 - 0.3 * i)], 1, n, ease=False, look=False)
        for b in L.bubbles_stream((0, 0, 0), count=35, nframes=n, rise=2.5, spread=0.15, seed=10 + i, name=f"lb{i}", size=0.04):
            b.parent = car
        divers.append(dv)
    L.fish_school((2.5, 3, -5.5), count=60, radius=2.2, nframes=n, seed=3, color=(0.95, 0.8, 0.2), orbit_speed=0.35, size=0.1)
    L.fish_school((-3, 6, -6.5), count=40, radius=1.8, nframes=n, seed=6, color=(0.6, 0.75, 0.9), orbit_speed=-0.3, size=0.09)
    L.particle_cloud((0, 0, -4), (16, 16, 8), count=1200, radius=0.008, nframes=n, drift=(0.05, 0.02, 0.02), name="plankton")
    cam, tgt = L.camera(loc=(5.2, -3.5, -3.6), target=(0.0, -2.0, -4.8), lens=24)
    L.cam_keys(cam, [(1, (5.2, -4.2, -3.6)), (n, (5.2, 2.2, -3.4))], ease=False)
    L.cam_keys(tgt, [(1, (0.0, -2.6, -4.8)), (n, (0.0, 3.6, -4.7))], ease=False)
    L.handheld(cam, n, amp=0.03, rate=0.4)
    _finish(L)


# ----------------------------------------------------------------------------- dive-boat deck set (S04/S17)

def deck_set(L, n, morning=False):
    if morning:
        surface_env(L, n, elev=28, az=120, top=(0.35, 0.55, 0.85), horizon=(0.85, 0.88, 0.9), sun_col=(1.0, 0.95, 0.88),
                    sun_energy=5, wave=0.3, ocean_size=80, res=8, sun_disc=6)
    else:
        surface_env(L, n, elev=45, az=200, top=(0.2, 0.45, 0.85), horizon=(0.75, 0.82, 0.9), sun_col=(1.0, 0.95, 0.85),
                    sun_energy=6, wave=0.3, ocean_size=80, res=8, sun_disc=6)
    boat, _ = S.dive_boat("deckboat")
    # benches along the aft deck
    wood = L.mat_principled("bench", (0.75, 0.75, 0.72), rough=0.5)
    for sx in (-1, 1):
        b = L.prim("cube", loc=(sx * 1.9, -3.3, 1.55), name="bench")
        b.scale = (0.25, 2.6, 0.06)
        L.assign(b, wood)
    # passengers seated, faceless, wetsuits
    rnd = random.Random(5)
    for sx in (-1, 1):
        for k in range(5):
            if rnd.random() < 0.15:
                continue
            fg = L.char_figure(name=f"pax{sx}{k}", color=(0.02 + rnd.random() * 0.03, 0.02, 0.03 + rnd.random() * 0.05),
                               height=rnd.uniform(1.6, 1.85))
            r = fg["root"]
            r.location = (sx * 1.9, -5.4 + k * 1.0, 1.61 - 0.95 * 0.95 + 0.04)
            r.rotation_euler = (0, 0, -sx * PI / 2)
            for tag in ("L", "R"):
                fg[f"hip{tag}"].rotation_euler = (1.5, 0, 0)
                fg[f"knee{tag}"].rotation_euler = (-1.5, 0, 0)
                fg[f"shoulder{tag}"].rotation_euler = (0.4, 0, 0)
                fg[f"elbow{tag}"].rotation_euler = (0.9, 0, 0)
    return boat


def crew_with_clipboard(L, n, loc, rot_z, name, hat=(0.9, 0.9, 0.88), ticks=6, tick_start=10, tick_every=8, check=None):
    fg = L.char_figure(name=name, color=(0.04, 0.05, 0.08), height=1.8)
    r = fg["root"]
    r.location = loc
    r.rotation_euler = (0, 0, rot_z)
    cap = L.prim("sphere", loc=(0, 0.02, 0.18), segments=14, ring_count=8, radius=0.115, name=name + "_cap")
    cap.scale = (1, 1.05, 0.55)
    L.assign(cap, L.mat_principled(name + "_capm", hat, rough=0.5))
    cap.parent = fg["neck"]
    # clipboard held in front of the chest
    fg["shoulderL"].rotation_euler = (0.9, 0, -0.2)
    fg["elbowL"].rotation_euler = (1.3, 0, 0)
    cb = bpy.data.objects.new(name + "_cbroot", None)
    bpy.context.scene.collection.objects.link(cb)
    cb.parent = r
    cb.location = (-0.05, 0.38, 1.25)
    cb.rotation_euler = (-0.9, 0, 0)
    brd = L.prim("cube", loc=(0, 0, 0), name=name + "_board")
    brd.scale = (0.12, 0.16, 0.008)
    L.assign(brd, L.mat_principled(name + "_brdm", (0.35, 0.22, 0.1), rough=0.6))
    brd.parent = cb
    paper = L.prim("cube", loc=(0, -0.01, 0.009), name=name + "_paper")
    paper.scale = (0.105, 0.135, 0.002)
    L.assign(paper, L.mat_principled(name + "_pap", (0.95, 0.95, 0.92), rough=0.8))
    paper.parent = cb
    ink = L.mat_principled(name + "_ink", (0.02, 0.02, 0.05), rough=0.6)
    # tally marks appear one by one (no names)
    for k in range(ticks):
        grp, j = divmod(k, 5)
        if j < 4:
            t = L.prim("cube", loc=(-0.07 + grp * 0.07 + j * 0.012, 0.06 - (grp // 2) * 0.05, 0.012), name=name + "_tick")
            t.scale = (0.002, 0.018, 0.001)
        else:
            t = L.prim("cube", loc=(-0.07 + grp * 0.07 + 0.018, 0.06 - (grp // 2) * 0.05, 0.013), name=name + "_tick")
            t.scale = (0.03, 0.002, 0.001)
            t.rotation_euler = (0, 0, 0.5)
        L.assign(t, ink)
        t.parent = cb
        f = tick_start + k * tick_every
        sc = t.scale.copy()
        t.scale = (0, 0, 0)
        t.keyframe_insert("scale", frame=max(1, f - 1))
        t.scale = sc
        t.keyframe_insert("scale", frame=f + 1)
    # pen hand ticking
    fg["shoulderR"].rotation_euler = (1.0, 0, 0.3)
    fg["elbowR"].rotation_euler = (1.2, 0, 0)
    for f in range(1, n + 1, 4):
        fg["elbowR"].rotation_euler = (1.2 + 0.12 * math.sin(f * 0.8), 0, 0)
        fg["elbowR"].keyframe_insert("rotation_euler", frame=f)
    if check:
        tick = check_mark(L, name + "_check", (0, 0.0, 0.25), size=0.16)
        tick.parent = cb
        tick.scale = (0, 0, 0)
        tick.keyframe_insert("scale", frame=check)
        tick.scale = (1.3, 1.3, 1.3)
        tick.keyframe_insert("scale", frame=check + 4)
        tick.scale = (1, 1, 1)
        tick.keyframe_insert("scale", frame=check + 7)
    return fg, cb


def check_mark(L, name, loc, size=0.2, color=(0.2, 1.0, 0.45)):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = size * 0.12
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(2)
    for i, (x, y) in enumerate(((-0.5, 0.0), (-0.15, -0.4), (0.55, 0.5))):
        sp.points[i].co = (x * size, y * size, 0, 1)
    o = L.link(bpy.data.objects.new(name, cu))
    o.location = loc
    o.data.materials.append(L.mat_emission(name + "_m", color, 6))
    return o


def S04(L, n):
    deck_set(L, n)
    fg, cb = crew_with_clipboard(L, n, (0.25, -3.0, 1.3), PI, "crew", ticks=9, tick_start=12, tick_every=8)
    cam, tgt = L.camera(loc=(2.6, -10.5, 9.5), target=(0.2, -3.6, 1.6), lens=28)
    L.cam_keys(cam, [(1, (2.6, -10.5, 9.5)), (n, (0.6, -4.6, 3.6))])
    L.cam_keys(tgt, [(1, (0.2, -3.4, 1.5)), (n, (0.15, -2.7, 2.35))])
    _finish(L)


def S17(L, n):
    deck_set(L, n, morning=True)
    crew_with_clipboard(L, n, (-0.45, -3.2, 1.3), PI - 0.35, "crewA", ticks=8, tick_start=8, tick_every=9, check=int(n * 0.55))
    crew_with_clipboard(L, n, (0.6, -2.6, 1.3), PI + 0.4, "crewB", hat=(0.1, 0.25, 0.6), ticks=8, tick_start=12,
                        tick_every=9, check=int(n * 0.62))
    cam, tgt = L.camera(loc=(-2.0, -7.4, 3.4), target=(0.05, -2.8, 2.2), lens=35)
    L.cam_keys(cam, [(1, (-2.0, -7.6, 3.4)), (n, (1.6, -7.8, 3.3))])
    L.handheld(cam, n, amp=0.01, rate=0.4)
    _finish(L)


# ----------------------------------------------------------------------------- S05 the double count

def S05(L, n):
    surface_env(L, n, elev=40, az=210, top=(0.2, 0.45, 0.85), horizon=(0.75, 0.82, 0.9), sun_col=(1, 0.95, 0.85),
                sun_energy=6, wave=0.3, ocean_size=80, res=8, sun_disc=6)
    boat, _ = S.dive_boat("b5")
    boat.rotation_euler = (0, 0, PI / 2)  # side-on: bow toward -X
    ghost = S.mat_beam("ghostm", (0.6, 0.95, 1.0), 2.0, alpha=0.9)
    jump = 30
    figs = []
    for i, (yy, dz) in enumerate(((-0.6, 0.0), (0.6, 0.15))):
        fg = L.char_figure(name=f"sw{i}", color=(0.03, 0.03, 0.04), height=1.75)
        r = fg["root"]
        r.rotation_euler = (0, 0, -PI / 2)
        x0 = -6.5 + i * 0.7
        keys = [(1, (x0, yy, 1.3)), (jump - 8 + i * 3, (x0, yy, 1.3)), (jump + i * 3, (x0 - 1.4, yy, 2.4)),
                (jump + 10 + i * 3, (x0 - 2.4, yy, -1.3)), (n, (x0 - 2.6, yy, -1.2))]
        L.cam_keys(r, keys)
        _pose(fg, 1, shoulderL=(0.2, 0, -0.2), shoulderR=(0.2, 0, 0.2))
        _pose(fg, jump + i * 3, shoulderL=(2.9, 0, -0.3), shoulderR=(2.9, 0, 0.3), hipL=(0.3, 0, 0), hipR=(0.3, 0, 0))
        figs.append(fg)
        # ghost duplicate standing back at the ladder/deck edge (counted again)
        gh = L.char_figure(name=f"ghost{i}", height=1.75)
        for o in bpy.data.objects:
            if o.name.startswith(f"ghost{i}") and o.type == "MESH":
                L.assign(o, ghost)
        gr = gh["root"]
        gr.location = (x0, yy, 1.3)
        gr.rotation_euler = (0, 0, -PI / 2 + 0.6)
        gr.scale = (0.001,) * 3
        gr.keyframe_insert("scale", frame=jump + 14 + i * 4)
        gr.scale = (1, 1, 1)
        gr.keyframe_insert("scale", frame=jump + 18 + i * 4)
    # splashes
    spl = L.mat_principled("splm", (0.9, 0.95, 1.0), rough=0.3, emit=(0.5, 0.6, 0.65), emit_strength=0.6)
    for i in range(2):
        pc = L.particle_cloud((-8.6 + i * 0.7, -0.6 + 1.2 * i, 0.4), (1.2, 1.2, 1.0), count=500, radius=0.03, nframes=n,
                              drift=(0, 0, 0.2), name=f"splash{i}", seed=80 + i, mat=spl)
        f0 = jump + 9 + i * 3
        pc.scale = (0.01,) * 3
        pc.keyframe_insert("scale", frame=f0)
        pc.scale = (1.0, 1.0, 1.6)
        pc.keyframe_insert("scale", frame=f0 + 5)
        pc.scale = (1.4, 1.4, 0.3)
        pc.keyframe_insert("scale", frame=f0 + 22)
        pc.scale = (0.01,) * 3
        pc.keyframe_insert("scale", frame=f0 + 30)
    cam, tgt = L.camera(loc=(-6.5, -13.0, 0.6), target=(-6.2, 0, 1.6), lens=35)
    far_cam(cam)
    L.cam_keys(tgt, [(1, (-6.0, 0, 1.7)), (jump + 10, (-7.6, 0, 1.0)), (n, (-7.0, 0, 1.2))])
    L.handheld(cam, n, amp=0.05, rate=0.5)
    _finish(L)


def _pose(fig, f, **rots):
    for k, v in rots.items():
        fig[k].rotation_euler = v
        fig[k].keyframe_insert("rotation_euler", frame=f)


# ----------------------------------------------------------------------------- S06 aerial: boat turns for home

def S06(L, n):
    surface_env(L, n, elev=22, az=250, wave=0.45, ocean_size=160, res=9, far=True, deep=(0.0, 0.1, 0.14), shallow=(0.0, 0.3, 0.34))
    boat, _ = S.dive_boat("homebound")
    pts = []
    for k in range(9):
        t = k / 8
        a = -0.2 + 1.0 * t
        pts.append((-14 + 30 * math.sin(a) * 0.6 + 4 * t, -18 + 34 * t, 0.0))
    L.path_follow(boat, pts, 1, n, ease=False)
    wk = S.wake(start=(0, -8.0, 0.0), length=70, width0=3, width1=18, angle=0.0, name="homewake", curve=-0.007,
                strength=1.0)
    wk.parent = boat
    wk.location = (0, 0, 0.35)
    cam, tgt = L.camera(loc=(-30, -42, 55), target=(-6, -2, 0), lens=35)
    far_cam(cam)
    L.cam_keys(cam, [(1, (-30, -42, 55)), (n, (-28, -38, 56))], ease=False)
    L.cam_keys(tgt, [(1, (-8, -10, 0)), (n, (-4, 2, 0))], ease=False)
    _finish(L)


# ----------------------------------------------------------------------------- S07 crane up from two heads

def S07(L, n):
    surface_env(L, n, elev=9, az=270, top=(0.06, 0.16, 0.42), horizon=(0.95, 0.55, 0.3), sun_col=(1.0, 0.62, 0.35),
                sun_energy=3.5, deep=(0.0, 0.04, 0.09), shallow=(0.0, 0.14, 0.22), wave=0.45, ocean_size=160, res=9)
    ds = two_divers(L, n, a=(-0.35, 0.0), b=(0.35, 0.25))
    for d in ds:
        ring = L.prim("torus", loc=d["root"].location, major_radius=0.45, minor_radius=0.04, name="foamring")
        L.assign(ring, L.mat_principled("foamm", (0.9, 0.95, 0.95), rough=0.6, emit=(0.4, 0.45, 0.45), emit_strength=0.4))
        ring.parent = d["root"]
        ring.location = (0, 0, 0.0)
    cam, _ = L.camera(loc=(0, 0, 4), lens=50)
    far_cam(cam)
    cam.rotation_euler = (0, 0, 0.4)
    keys = [(1, 4.0), (int(n * 0.35), 18), (n, 140)]
    for f, z in keys:
        cam.location = (0.05, 0.1, z)
        cam.keyframe_insert("location", frame=f)
    for f, ln in ((1, 50), (n, 28)):
        cam.data.lens = ln
        cam.data.keyframe_insert("lens", frame=f)
    for fc in L._fcurves(cam.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "SINE"
            kp.easing = "EASE_IN"
    _finish(L)


# ----------------------------------------------------------------------------- S08 the bag left aboard

def S08(L, n):
    S.setup(vol_end=20)
    L.set_world(color=(0.02, 0.03, 0.04), strength=1)
    S.world_volume(color=(1, 0.95, 0.85), density=0.06, anisotropy=0.6, center=(0, 0, 1.05), size=(3.3, 4.3, 2.2))
    w, d, h = 3.2, 4.2, 2.1
    wall = S.mat_paint("cabw", (0.82, 0.82, 0.78), rough=0.5, grime=0.2)
    floor = L.mat_noise_surface("cabf", (0.25, 0.27, 0.28), (0.4, 0.42, 0.43), scale=10, bump=0.2, voronoi=False)
    for loc, sc, m in (((0, 0, -0.03), (w / 2, d / 2, 0.03), floor), ((0, 0, h + 0.03), (w / 2, d / 2, 0.03), wall),
                       ((0, d / 2, h / 2), (w / 2, 0.04, h / 2), wall), ((-w / 2, 0, h / 2), (0.04, d / 2, h / 2), wall),
                       ((0, -d / 2 - 0.3, h / 2), (w / 2, 0.04, h / 2), wall)):
        o = L.prim("cube", loc=loc, name="cab")
        o.scale = sc
        L.assign(o, m)
    # starboard wall with porthole (boolean)
    sw = L.prim("cube", loc=(w / 2, 0, h / 2), name="cabE")
    sw.scale = (0.04, d / 2, h / 2)
    L.assign(sw, wall)
    cut = L.prim("cyl", loc=(w / 2, 0.3, 1.45), vertices=32, radius=0.24, depth=0.4, rot=(0, PI / 2, 0), name="portcut")
    bo = sw.modifiers.new("cut", "BOOLEAN")
    bo.object = cut
    bo.operation = "DIFFERENCE"
    cut.hide_render = True
    ring = L.prim("torus", loc=(w / 2 - 0.05, 0.3, 1.45), major_radius=0.26, minor_radius=0.04, rot=(0, PI / 2, 0), name="portring")
    L.assign(ring, L.mat_principled("brass", (0.7, 0.5, 0.2), rough=0.3, metal=1))
    # daylight slat through the porthole
    sp = L.spot((w / 2 + 1.5, 0.6, 2.4), (0, 0, 0), energy=9000, size_deg=12, blend=0.15, color=(1.0, 0.9, 0.72), name="daylight",
                radius=0.02)
    sp.rotation_euler = (Vector((-1.0, -0.2, 0.75)) - Vector((w / 2 + 1.5, 0.6, 2.4))).to_track_quat("-Z", "Y").to_euler()
    L.point((0, 0, 1.9), energy=40, color=(0.7, 0.8, 0.9), radius=0.5, name="cabfill")
    # bench and the lone bag
    bench = L.prim("cube", loc=(-1.0, 0.0, 0.42), name="cbench")
    bench.scale = (0.35, 1.6, 0.05)
    L.assign(bench, L.mat_principled("cbm", (0.4, 0.3, 0.2), rough=0.5))
    for yy in (-1.3, 1.3):
        lg = L.prim("cube", loc=(-1.0, yy, 0.2), name="cbleg")
        lg.scale = (0.3, 0.04, 0.2)
        L.assign(lg, L.mat_principled("cbm2", (0.3, 0.22, 0.15)))
    bag = L.prim("cube", loc=(-1.0, -0.45, 0.68), name="bag")
    bag.scale = (0.28, 0.5, 0.21)
    L.bevel(bag, 0.08, 3)
    L.add_displace(bag, strength=0.02, scale=0.1, name="bagd")
    L.assign(bag, L.mat_noise_surface("bagm", (0.02, 0.06, 0.16), (0.05, 0.12, 0.3), scale=40, bump=0.2, voronoi=False))
    for k in (-0.2, 0.2):
        st = L.prim("torus", loc=(-1.0, -0.45 + k, 0.92), major_radius=0.14, minor_radius=0.018, rot=(0, PI / 2, 0), name="handle")
        st.scale = (1, 1, 0.6)
        L.assign(st, L.mat_principled("strap", (0.02, 0.02, 0.02)))
    zp = L.prim("cube", loc=(-1.0 + 0.285, -0.45, 0.75), name="zip")
    zp.scale = (0.005, 0.45, 0.01)
    L.assign(zp, L.mat_principled("zipm", (0.7, 0.7, 0.7), metal=1, rough=0.3))
    L.particle_cloud((0, 0, 1.2), (2.8, 3.5, 1.8), count=900, radius=0.0015, nframes=n, drift=(0.02, 0.03, 0.01), name="dust",
                     mat=L.mat_principled("dustm", (1, 0.95, 0.85), rough=1, emit=(1, 0.9, 0.75), emit_strength=0.6))
    # crew silhouette stops and looks
    fg = L.char_figure(name="crewlook", color=(0.03, 0.035, 0.05), height=1.8)
    r = fg["root"]
    r.rotation_euler = (0, 0, PI / 2 + 0.6)
    L.anim_walk(fg, 1, 26, stride=0.4, travel=((1.0, 1.9, 0), (0.55, 0.85, 0)))
    for k in ("hipL", "hipR", "kneeL", "kneeR", "shoulderL", "shoulderR"):
        fg[k].rotation_euler = (0, 0, 0)
        fg[k].keyframe_insert("rotation_euler", frame=30)
    fg["neck"].rotation_euler = (0, 0, 0)
    fg["neck"].keyframe_insert("rotation_euler", frame=28)
    fg["neck"].rotation_euler = (0.35, 0, -0.1)
    fg["neck"].keyframe_insert("rotation_euler", frame=44)
    r.keyframe_insert("location", frame=n)
    cam, tgt = L.camera(loc=(0.9, -1.9, 1.35), target=(-0.95, -0.4, 0.7), lens=35)
    L.cam_keys(cam, [(1, (0.95, -1.95, 1.4)), (n, (0.35, -1.4, 1.2))])
    L.handheld(cam, n, amp=0.006, rate=0.4)
    _finish(L)


# ----------------------------------------------------------------------------- S09 / S16 document backgrounds

def _table_bg(L, n, items="passports"):
    L.set_world(color=(0.02, 0.02, 0.025), strength=1)
    tb = L.prim("plane", loc=(0, 0, 0), size=6, name="table")
    L.assign(tb, L.mat_noise_surface("tablem", (0.06, 0.035, 0.02), (0.18, 0.1, 0.05), scale=3, bump=0.2, voronoi=False))
    L.area((0.6, -0.4, 2.0), (0.3, 0.2, 0), energy=120, size=1.2, color=(1.0, 0.88, 0.7), name="desklamp")
    rnd = random.Random(2)
    objs = []
    if items == "passports":
        specs = [((-0.42, 0.75, 0.0), (0.22, 0.16, 0.012), (0.08, 0.1, 0.25), 0.3),
                 ((0.4, 0.8, 0.0), (0.22, 0.16, 0.012), (0.08, 0.1, 0.25), -0.25),
                 ((0.05, -0.85, 0.0), (0.24, 0.13, 0.025), (0.18, 0.09, 0.04), 0.1)]
    else:
        specs = [((-0.35, 0.8, 0.0), (0.3, 0.2, 0.005), (0.85, 0.82, 0.75), 0.15),
                 ((0.35, -0.8, 0.0), (0.3, 0.2, 0.005), (0.85, 0.82, 0.75), -0.12)]
    for i, (loc, sc, col, rz) in enumerate(specs):
        o = L.prim("cube", loc=loc, name=f"item{i}")
        o.scale = sc
        L.bevel(o, 0.01)
        L.assign(o, L.mat_principled(f"itemm{i}", col, rough=0.6))
        if items == "passports" and i < 2:
            em = L.prim("cyl", loc=(0, 0, 1.01), vertices=20, radius=0.4, depth=0.1, name=f"emb{i}")
            L.assign(em, L.mat_principled("gold", (0.8, 0.6, 0.2), metal=1, rough=0.3))
            em.parent = o
        start = (loc[0] * 3.5, loc[1] * 2.2, sc[2])
        L.cam_keys(o, [(1 + i * 5, start), (14 + i * 5, (loc[0], loc[1], sc[2]))])
        o.rotation_euler = (0, 0, rz)
        objs.append(o)
    cam, _ = L.camera(loc=(0, 0, 3.2), lens=35)
    cam.rotation_euler = (0, 0, 0)
    L.cam_keys(cam, [(1, (0, 0, 3.3)), (n, (0, 0, 3.0))])
    _finish(L)


def S09(L, n):
    _table_bg(L, n, "passports")


def S16(L, n):
    _table_bg(L, n, "cards")


# ----------------------------------------------------------------------------- S11 empty sea, aircraft shadow

def S11(L, n):
    surface_env(L, n, elev=55, az=30, top=(0.45, 0.5, 0.55), horizon=(0.62, 0.66, 0.68), sun_col=(0.85, 0.88, 0.9),
                sun_energy=2.0, deep=(0.02, 0.08, 0.1), shallow=(0.12, 0.22, 0.24), wave=0.6, ocean_size=160, res=9,
                sun_disc=0.5, rough=0.18)
    sh = bpy.data.objects.new("planeshadow", None)
    bpy.context.scene.collection.objects.link(sh)
    m = L.mat_principled("shadowm", (0, 0, 0), rough=1, alpha=0.55)
    m.surface_render_method = "BLENDED"
    for loc, sc in (((0, 0, 0), (1.0, 7.0, 0.01)), ((0, 1.0, 0), (9.0, 1.1, 0.01)), ((0, -5.8, 0), (3.2, 0.7, 0.01))):
        o = L.prim("cube", loc=loc, name="shadowpart")
        o.scale = sc
        L.bevel(o, 0.4)
        L.assign(o, m)
        o.parent = sh
    sh.rotation_euler = (0, 0, -0.5)
    L.cam_keys(sh, [(1, (-40, 10, 1.0)), (n, (30, 60, 1.0))], ease=False)
    cam, tgt = L.camera(loc=(0, -40, 26), target=(0, 20, 0), lens=24)
    far_cam(cam)
    L.cam_keys(cam, [(1, (0, -40, 26)), (n, (0, -25, 25))], ease=False)
    L.cam_keys(tgt, [(1, (0, 20, 0)), (n, (0, 35, 0))], ease=False)
    L.handheld(cam, n, amp=0.1, rate=0.3)
    _finish(L)


# ----------------------------------------------------------------------------- beach (S12/S13)

def beach_env(L, n, low_sun=False):
    S.setup()
    if low_sun:
        S.sky_gradient(top=(0.25, 0.35, 0.55), horizon=(1.0, 0.72, 0.45), sun_dir=sun_vec(6, 280), sun_col=(1, 0.7, 0.4),
                       sun_strength=8)
        s = L.sun(rot=(0, 0, 0), energy=4, color=(1.0, 0.72, 0.45), angle=1.0)
        s.rotation_euler = (-sun_vec(6, 280)).to_track_quat("-Z", "Y").to_euler()
    else:
        S.sky_gradient(top=(0.42, 0.47, 0.52), horizon=(0.7, 0.72, 0.72), strength=1.0)
        s = L.sun(rot=(0.7, 0.2, 2.2), energy=1.5, color=(0.85, 0.88, 0.9), angle=15)
    sand = L.prim("plane", loc=(0, 0, 0), size=80, name="sand")
    sub = sand.modifiers.new("sub", "SUBSURF")
    sub.subdivision_type = "SIMPLE"
    sub.levels = sub.render_levels = 5
    L.add_displace(sand, strength=0.08, scale=1.5, name="sandd")
    L.assign(sand, L.mat_noise_surface("sandm", (0.48, 0.42, 0.32), (0.72, 0.66, 0.52), scale=30, bump=0.3, voronoi=False))
    return s


def _wash(L, n, x0=1.2):
    """Shallow sea on the right with a foam edge sliding in and out over the sand (tilted slightly)."""
    wm = S.mat_water_surface("washm", color=(0.05, 0.18, 0.2), rough=0.05, alpha=0.8, ripple=0.2, nframes=n)
    sea = L.prim("plane", loc=(x0 + 20, 0, 0.02), size=1, name="shallows")
    sea.scale = (40, 80, 1)
    L.assign(sea, wm)
    foam = S.wake(start=(0, -40, 0), length=80, width0=1.2, width1=1.2, angle=PI, name="foamline", strength=1.0, segs=40)
    foam.location = (x0 + 0.3, 0, 0.035)
    foam.rotation_euler = (0, 0, 0)
    for o in (sea, foam):
        for f, dx in ((1, 0.0), (n * 0.4, -0.8), (n * 0.75, 0.2), (n, -0.5)):
            o.location.x = (x0 + 20 if o is sea else x0 + 0.3) + dx
            o.keyframe_insert("location", frame=int(f))
    return sea


def S12(L, n):
    beach_env(L, n)
    _wash(L, n, x0=1.0)
    S.bcd_vest(loc=(0.8, 1.5, 0.08), rot=(0.1, 0.05, 0.6))
    ws = S.wetsuit(loc=(0.4, 6.2, 0.03), rot=(0, 0, 2.4))
    S.seaweed_clump((0.4, 6.2, 0.0), count=16, seed=2)
    S.seaweed_clump((1.2, 3.5, 0.0), count=8, seed=5)
    cam, tgt = L.camera(loc=(-0.6, -0.6, 0.4), target=(0.7, 1.6, 0.1), lens=35)
    far_cam(cam)
    L.cam_keys(cam, [(1, (-0.6, -0.7, 0.4)), (n, (-0.5, 2.6, 0.38))], ease=False)
    L.cam_keys(tgt, [(1, (0.8, 1.5, 0.1)), (int(n * 0.45), (0.8, 2.6, 0.1)), (n, (0.4, 6.2, 0.05))])
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 1.6
    for f, dd in ((1, 2.6), (int(n * 0.45), 2.4), (int(n * 0.7), 3.9), (n, 3.7)):
        cam.data.dof.focus_distance = dd
        cam.data.dof.keyframe_insert("focus_distance", frame=f)
    L.handheld(cam, n, amp=0.01, rate=0.4)
    _finish(L)


def S13(L, n):
    beach_env(L, n, low_sun=True)
    sl = S.dive_slate(loc=(0, 0, 0.01), rot=(0.04, -0.03, 0.4))
    L.particle_cloud((0, 0, 0.05), (1.5, 1.5, 0.08), count=400, radius=0.0012, nframes=n, drift=(0.3, 0.05, 0.0), name="sandblow",
                     mat=L.mat_principled("sbm", (0.75, 0.65, 0.5), rough=1))
    cam, tgt = L.camera(loc=(0.05, -0.55, 0.32), target=(0.0, 0.0, 0.01), lens=50)
    L.cam_keys(cam, [(1, (0.05, -0.6, 0.34)), (n, (0.03, -0.45, 0.27))])
    L.dof(cam, target=sl, fstop=1.4)
    L.handheld(cam, n, amp=0.004, rate=0.4)
    _finish(L)


# ----------------------------------------------------------------------------- S14 empty sunset

def S14(L, n):
    surface_env(L, n, elev=4, az=14, top=(0.02, 0.06, 0.16), horizon=(0.75, 0.28, 0.08), sun_col=(1.0, 0.45, 0.15),
                sun_energy=3, deep=(0.0, 0.03, 0.06), shallow=(0.02, 0.08, 0.12), wave=0.6, ocean_size=160, res=9,
                sun_disc=5, sky_strength=0.55)
    cam, _ = L.camera(loc=(0, -3, 2.2), target=(0, 100, 2.2), lens=35)
    far_cam(cam)
    L.cam_keys(cam, [(1, (0, -3, 2.2)), (n, (0, -2.4, 2.2))], ease=False)
    _finish(L)


# ----------------------------------------------------------------------------- S15 looking up at the empty surface

def S15(L, n):
    S.setup(vol_end=60)
    L.set_world(color=(0.02, 0.12, 0.2), strength=0.6)
    vol = S.world_volume(color=(0.2, 0.55, 0.7), density=0.05, anisotropy=0.7, absorption=(0.05, 0.25, 0.4),
                         center=(0, 0, -15.1), size=(80, 80, 30))
    sea = S.ocean(size=120, nframes=n, wave_scale=0.6, resolution=8, spatial=40,
                  mat=S.mat_ocean("seau", under=(0.5, 0.85, 1.0), under_strength=2.5))
    sea.location.z = 0
    under = bpy.data.materials["seau"].node_tree.nodes
    em = [nd for nd in under if nd.type == "EMISSION"][0]
    for f, v in ((1, 2.5), (n, 0.6)):
        em.inputs[1].default_value = v
        em.inputs[1].keyframe_insert("default_value", frame=f)
    rays = S.god_rays(center=(0, 6, -0.2), count=9, length=16, spread=6, tilt=(0.15, 0.05), color=(0.8, 1.0, 1.0),
                      strength=1.2, alpha=0.3, nframes=n)
    for r in rays:
        m = r.data.materials[0]
        e = [nd for nd in m.node_tree.nodes if nd.type == "EMISSION"][0]
        for f, v in ((1, 1.2), (n, 0.15)):
            e.inputs[1].default_value = v
            e.inputs[1].keyframe_insert("default_value", frame=f)
    for f, v in ((1, 0.05), (n, 0.09)):
        vol.inputs["Density"].default_value = v
        vol.inputs["Density"].keyframe_insert("default_value", frame=f)
    L.sun(rot=(0.2, 0.1, 0.3), energy=3, color=(0.8, 1.0, 1.0), angle=4)
    L.particle_cloud((0, 4, -6), (14, 14, 10), count=1200, radius=0.01, nframes=n, drift=(0, 0, 0.05), name="plankton")
    cam, tgt = L.camera(loc=(0, -2, -9), target=(0, 6, -9), lens=20)
    L.cam_keys(tgt, [(1, (0, 8, -10.5)), (n, (0, 5.5, -1.0))])
    L.handheld(cam, n, amp=0.03, rate=0.3)
    _finish(L)
