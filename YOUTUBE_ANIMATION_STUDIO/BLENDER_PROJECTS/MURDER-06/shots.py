"""MURDER-06 - Mary Celeste (found 4 Dec 1872) and Conan Doyle's 1884 story.
Shot builders: def SXX(L, n). Reusable builders (brigantine, swell sea, barrels, sounding rod, deck pump, lifeboat,
deerstalker, legend_grade compositor) live in PIPELINE/blender/lib_murder.py.
Ship layout: bow +X, stern -X, waterline z=0, deck z=1.5, length 31 m, beam 7.5 m; foremast x=6, mainmast x=-3,
deckhouse x -12..-6, wheel x=-13.35, stern davits x~-16.5.
Grading rule: LEGEND scenes (S02, S03, S10, S13) = warm sepia + grain via the compositor (legend_grade) and carry
FOLKLORE; record scenes = cold grey-green daylight.
"""
import os, sys, math, random, importlib
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_murder as M
import studio_lib as L
importlib.reload(M)
import bpy
from mathutils import Vector

R = math.radians
DZ = M.DECK_Z
DAY = (0.75, 0.85, 0.8)


def lin(o):
    M.set_interp(o, "LINEAR")


def cam_path(n, c0, c1, t0, t1, lens=35, ease=True, parent=None):
    cam, ct = L.camera(loc=c0, target=t0, lens=lens)
    cam.data.clip_end = 2000
    if parent is not None:
        cam.parent = parent
        ct.parent = parent
    L.cam_keys(cam, [(1, c0), (n, c1)])
    ct.location = t0
    ct.keyframe_insert("location", frame=1)
    ct.location = t1
    ct.keyframe_insert("location", frame=n)
    if not ease:
        lin(cam)
        lin(ct)
    return cam, ct


def vol_end(d=250):
    e = bpy.context.scene.eevee
    if hasattr(e, "volumetric_end"):
        e.volumetric_end = d


def fog_keys(fog_obj, pairs):
    v = [nd for nd in fog_obj.data.materials[0].node_tree.nodes if nd.type == "PRINCIPLED_VOLUME"][0]
    for f, d in pairs:
        v.inputs["Density"].default_value = d
        v.inputs["Density"].keyframe_insert("default_value", frame=f)


def atlantic(n, fog_d=0.02, fog_center=(0, 0, 6), fog_size=(400, 400, 14), sun_e=0.6, wave=0.55, strength=1.0, dusk=False,
             wave_offset=0):
    if dusk:
        M.dawn_sky(hor=(0.2, 0.2, 0.22), mid=(0.12, 0.13, 0.15), zen=(0.05, 0.055, 0.07), strength=strength)
    else:
        M.dawn_sky(hor=(0.4, 0.44, 0.42), mid=(0.3, 0.34, 0.33), zen=(0.17, 0.2, 0.21), strength=strength)
    L.sun(rot=(R(45), 0, R(-30)), energy=sun_e, color=DAY, angle=R(35), name="overcast")
    sea = M.swell_sea(size=900, res=170, n=n, height=wave, color=(0.03, 0.045, 0.045))
    if wave_offset:
        sea.modifiers["swell"].time_offset = wave_offset
    fog = M.fog(fog_center, fog_size, density=fog_d, color=(0.62, 0.68, 0.66))
    vol_end(260)
    return sea, fog


def bob(root, n, base, rot_z=0.0, travel=None, t_off=0.0, amp=(0.22, 0.025, 0.03), per=(5.5, 7.0, 6.2)):
    b = Vector(base)
    for f in list(range(1, n + 1, 3)) + [n]:
        t = f / 24.0 + t_off
        k = (f - 1) / max(1, n - 1)
        p = b + (Vector(travel) * k if travel else Vector())
        p.z += amp[0] * math.sin(2 * math.pi * t / per[0] + 1)
        root.location = p
        root.rotation_euler = (amp[1] * math.sin(2 * math.pi * t / per[1] + 2), amp[2] * math.sin(2 * math.pi * t / per[2] + 3), rot_z)
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_euler", frame=f)


def wheel_drift(P, n, amp=R(14), per=4.0, t_off=0.0):
    w = P.get("wheel")
    if not w:
        return
    for f in list(range(1, n + 1, 3)) + [n]:
        t = f / 24.0 + t_off
        w.rotation_euler = (amp * math.sin(2 * math.pi * t / per) + 0.3 * amp * math.sin(2 * math.pi * t / (per * 2.3)), 0, 0)
        w.keyframe_insert("rotation_euler", frame=f)


def falls_swing(P, n, amp=0.18):
    for i, pv in enumerate(P["falls"]):
        for f in list(range(1, n + 1, 3)) + [n]:
            pv.rotation_euler = (amp * math.sin(f * 0.16 + i * 1.7), amp * 0.6 * math.sin(f * 0.11 + i), 0)
            pv.keyframe_insert("rotation_euler", frame=f)


# ============================================================================= S01 / S19 ship out of the fog

S01_SHIP0 = (-6.0, 0.0, 0.0)
S01_TRAVEL = (5.0, 0.6, 0.0)
S01_C0 = (52.0, -26.0, 2.2)
S01_C1 = (46.0, -22.5, 2.5)
S01_T = (0.0, 0.0, 9.5)


def ship_emerges(L, n, c0, c1, t0, t1, ship_base, travel, t_off=0.0, fog_pairs=None, wave_offset=0):
    sea, fog = atlantic(n, fog_d=0.02, fog_center=(20, -10, 7), fog_size=(160, 120, 16), wave_offset=wave_offset)
    if fog_pairs:
        fog_keys(fog, fog_pairs)
    P = M.brigantine("ship", sails="half")
    bob(P["root"], n, ship_base, rot_z=R(-16), travel=travel, t_off=t_off)
    wheel_drift(P, n, t_off=t_off)
    falls_swing(P, n)
    L.area((-40, 30, 30), (R(-60), 0, R(-130)), energy=6000, size=40, color=(0.75, 0.85, 0.82), name="rimsky")
    cam, ct = cam_path(n, c0, c1, t0, t1, lens=35, ease=False)
    L.handheld(cam, n, amp=0.02, rate=0.5, rot_amp=0.004)
    return P, cam


def S01(L, n):
    ship_emerges(L, n, S01_C0, S01_C1, S01_T, S01_T, S01_SHIP0, S01_TRAVEL, fog_pairs=[(1, 0.03), (n, 0.017)])
    L.bake_static()


def S19(L, n):
    # loop: ends exactly on S01 frame 1 (camera, ship position/phase, fog density)
    k = n / 88.0
    c0 = tuple(S01_C0[i] - (S01_C1[i] - S01_C0[i]) * k for i in range(3))
    base = tuple(S01_SHIP0[i] - S01_TRAVEL[i] * k for i in range(3))
    trav = tuple(S01_TRAVEL[i] * k for i in range(3))
    ship_emerges(L, n, c0, S01_C0, S01_T, S01_T, base, trav, t_off=-(n - 1) / 24.0, fog_pairs=[(1, 0.045), (n, 0.03)],
                 wave_offset=n - 1)
    L.bake_static()


# ============================================================================= legend cabin (S02, S03, S10, S13)

def legend_cabin(L, n, steam_until=None, props=True):
    L.set_world((0.01, 0.008, 0.006), 1.0)
    panel = M.mat_planks("panel", c1=(0.16, 0.09, 0.045), c2=(0.32, 0.19, 0.09), width=0.18, axis="X", rough=0.6)
    panel_y = M.mat_planks("panel_y", c1=(0.16, 0.09, 0.045), c2=(0.32, 0.19, 0.09), width=0.18, axis="Y", rough=0.6)
    floor = M.mat_planks("cfloor", c1=(0.1, 0.06, 0.03), c2=(0.22, 0.14, 0.07), width=0.15, axis="X")
    fl = L.prim("plane", loc=(0, 0, 0), size=1)
    fl.scale = (4.0, 3.0, 1)
    L.assign(fl, floor)
    back = L.prim("cube", loc=(0, 1.5, 1.1))
    back.scale = (2.0, 0.04, 1.1)
    L.assign(back, panel)
    for s in (-1, 1):
        sd = L.prim("cube", loc=(s * 2.0, 0, 1.1))
        sd.scale = (0.04, 1.5, 1.1)
        L.assign(sd, panel_y)
    ceil = L.prim("cube", loc=(0, 0, 2.2))
    ceil.scale = (2.0, 1.5, 0.04)
    L.assign(ceil, panel)
    for x in (-1.2, 0.0, 1.2):
        bm = L.prim("cube", loc=(x, 0, 2.12))
        bm.scale = (0.06, 1.5, 0.06)
        L.assign(bm, floor)
    # porthole with grey daylight
    ring = L.prim("torus", loc=(-1.1, 1.47, 1.45), major_radius=0.2, minor_radius=0.035, rot=(R(90), 0, 0))
    brass = L.mat_principled("brass", (0.55, 0.38, 0.15), rough=0.3, metal=0.9)
    L.assign(ring, brass)
    gl = L.prim("cyl", loc=(-1.1, 1.49, 1.45), vertices=24, radius=0.19, depth=0.01, rot=(R(90), 0, 0))
    L.assign(gl, L.mat_emission("port", (0.7, 0.75, 0.75), 2.0))
    # name board on the wall: MARIE CELESTE (the fictional name)
    nb = L.prim("cube", loc=(0.55, 1.45, 1.6))
    nb.scale = (0.55, 0.02, 0.1)
    L.assign(nb, L.mat_principled("nb", (0.08, 0.05, 0.03), rough=0.5))
    nbm = L.mat_principled("nbtext", (0.7, 0.5, 0.2), rough=0.3, metal=0.8, emit=(0.9, 0.65, 0.3), emit_strength=0.6)
    nt = L.text3d("MARIE CELESTE", loc=(0.55, 1.425, 1.6), size=0.11, extrude=0.004, mat=nbm, name="nameboard")
    nt.data.font = M._font(M.F_SERIF_B) or nt.data.font
    nt.data.align_y = "CENTER"
    # table + breakfast
    tb = L.prim("cube", loc=(0.2, 0.3, 0.74))
    tb.scale = (0.8, 0.5, 0.03)
    L.assign(tb, floor)
    for (x, y) in ((-0.5, -0.1), (0.9, -0.1), (-0.5, 0.7), (0.9, 0.7)):
        lg = L.prim("cube", loc=(x, y, 0.36))
        lg.scale = (0.04, 0.04, 0.36)
        L.assign(lg, floor)
    cloth = L.prim("plane", loc=(0.2, 0.3, 0.772), size=1)
    cloth.scale = (1.5, 0.95, 1)
    L.assign(cloth, L.mat_noise_surface("cloth", (0.6, 0.56, 0.48), (0.75, 0.72, 0.64), scale=30, bump=0.1, voronoi=False))
    china = L.mat_principled("china", (0.8, 0.78, 0.72), rough=0.25)
    items = []
    for i, (x, y) in enumerate(((-0.2, 0.05), (0.6, 0.05), (0.2, 0.6))):
        pl = L.prim("cyl", loc=(x, y, 0.785), vertices=24, radius=0.13, depth=0.015, name=f"plate{i}")
        L.assign(pl, china)
        egg = L.prim("sphere", loc=(x + 0.03, y, 0.81), radius=0.03, segments=10, ring_count=6, name=f"egg{i}")
        egg.scale = (1, 1, 1.3)
        L.assign(egg, L.mat_principled("egg", (0.8, 0.7, 0.5), rough=0.4))
        items += [pl, egg]
    cups = []
    for i, (x, y) in enumerate(((-0.02, 0.12), (0.42, 0.14))):
        cu = M.coffee_cup((x, y, 0.775), color=(0.8, 0.78, 0.72), name=f"cup{i}")
        cups.append((x, y))
        items.append(cu)
    pot = L.prim("sphere", loc=(0.25, 0.42, 0.88), radius=0.11, segments=16, ring_count=10, name="teapot")
    pot.scale = (1, 1, 0.85)
    L.assign(pot, china)
    sp = L.prim("cyl", loc=(0.38, 0.42, 0.9), vertices=8, radius=0.018, depth=0.16, rot=(0, R(55), 0), name="spout")
    L.assign(sp, china)
    lid = L.prim("sphere", loc=(0.25, 0.42, 0.97), radius=0.03, segments=8, ring_count=5, name="potlid")
    L.assign(lid, china)
    bread = M.rounded_box((-0.4, 0.45, 0.82), (0.24, 0.13, 0.09), (0.45, 0.28, 0.12), bevel=0.4, name="loaf")
    items += [pot, sp, lid, bread]
    # steam wisps (small volumes) from the cups and the spout
    steams = []
    for i, (x, y) in enumerate(cups + [(0.47, 0.42)]):
        z0 = 0.87 if i < 2 else 0.98
        st = M.cloud_volume((x, y, z0 + 0.22), (0.12, 0.12, 0.45), density=4.0, scale=6.0, contrast=(0.45, 0.75),
                            drift=(0.0, 0.0, 0.25), n=steam_until or n, color=(0.95, 0.92, 0.88), name=f"steam{i}")
        steams.append(st)
    # warm practical lamp (hanging) + porthole daylight
    lamp = M.hanging_lamp((0.2, 0.3, 1.75), energy=140, color=(1.0, 0.7, 0.4), name="cabinlamp", cord=0.4)
    pt = L.point((0.2, 0.0, 1.5), energy=40, color=(1.0, 0.72, 0.45), radius=0.3, name="warmfill")
    port = L.spot((-1.1, 1.8, 1.45), (R(100), 0, R(180)), energy=60, size_deg=50, blend=0.8, color=(0.8, 0.85, 0.85), name="portlight")
    return {"items": items, "steams": steams, "lamp": lamp, "warm": pt, "nameboard": nt, "nbm": nbm}


def S02(L, n):
    C = legend_cabin(L, n)
    M.legend_grade(sepia=1.0, grain=0.06)
    cam, ct = cam_path(n, (-1.2, -1.2, 1.3), (-0.2, -1.35, 1.25), (-0.2, 0.25, 0.85), (0.5, 0.25, 0.85), lens=50, ease=False)
    L.dof(cam, distance=1.6, fstop=2.8)
    L.bake_static()


def S03(L, n):
    fz = 10
    C = legend_cabin(L, n, steam_until=fz)
    G = M.legend_grade(sepia=1.0, grain=0.06)
    G["cold"].default_value = 0.0
    G["cold"].keyframe_insert("default_value", frame=fz)
    G["cold"].default_value = 1.0
    G["cold"].keyframe_insert("default_value", frame=fz + 18)
    # lamp flickers out to cold grey
    for lt in (C["lamp"], C["warm"]):
        e0 = lt.data.energy
        for f, k in ((1, 1.0), (fz, 1.0), (fz + 2, 0.3), (fz + 4, 0.9), (fz + 6, 0.15), (fz + 9, 0.6), (fz + 12, 0.05), (n, 0.05)):
            lt.data.energy = e0 * k
            lt.data.keyframe_insert("energy", frame=f)
    cold = L.area((0.2, -0.8, 2.1), (R(20), 0, 0), energy=0, size=2.5, color=(0.7, 0.78, 0.8), name="coldsky")
    for f, e in ((1, 0), (fz + 6, 0), (fz + 16, 60)):
        cold.data.energy = e
        cold.data.keyframe_insert("energy", frame=f)
    # name board flickers
    em = C["nbm"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for f in range(1, n + 1, 2):
        em.default_value = 0.6 * (0.2 if (f // 2) % 5 in (1, 3) and f > fz else 1.0)
        em.keyframe_insert("default_value", frame=f)
    cam, ct = L.camera(loc=(-0.1, -1.3, 1.25), target=(0.3, 0.6, 1.05), lens=40)
    cam.data.keyframe_insert("lens", frame=1)
    cam.data.lens = 41.2
    cam.data.keyframe_insert("lens", frame=n)
    L.bake_static()


def S10(L, n):
    C = legend_cabin(L, n)
    M.legend_grade(sepia=1.0, grain=0.07)
    cam, ct = cam_path(n, (-0.5, -1.4, 1.35), (-0.03, -0.18, 0.98), (-0.02, 0.12, 0.85), (-0.02, 0.12, 0.85), lens=35)
    cam.data.keyframe_insert("lens", frame=1)
    cam.data.lens = 85
    cam.data.keyframe_insert("lens", frame=n)
    for o in (cam, cam.data):
        for fc in L._fcurves(o.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "EXPO"
                kp.easing = "EASE_IN"
    L.bake_static()


def S13(L, n):
    C = legend_cabin(L, n)
    G = M.legend_grade(sepia=1.0, grain=0.06)
    rnd = random.Random(3)
    objs = C["items"] + C["steams"] + [bpy.data.objects[nm] for nm in ("cloth",) if nm in bpy.data.objects]
    for i, o in enumerate(C["items"] + C["steams"]):
        f = 14 + int(i * 40 / len(C["items"] + C["steams"])) + rnd.randint(0, 4)
        s0 = o.scale.copy()
        o.keyframe_insert("scale", frame=f)
        o.scale = (s0.x * 1.08, s0.y * 1.08, s0.z * 1.08)
        o.keyframe_insert("scale", frame=f + 3)
        o.scale = (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=f + 9)
    cl = bpy.data.objects.get("cloth")
    G["sepia"].keyframe_insert("default_value", frame=30)
    G["sepia"].default_value = 0.0
    G["sepia"].keyframe_insert("default_value", frame=75)
    G["cold"].default_value = 0.0
    G["cold"].keyframe_insert("default_value", frame=30)
    G["cold"].default_value = 0.75
    G["cold"].keyframe_insert("default_value", frame=75)
    G["grain"].keyframe_insert("default_value", frame=40)
    G["grain"].default_value = 0.02
    G["grain"].keyframe_insert("default_value", frame=75)
    for lt in (C["lamp"], C["warm"]):
        e0 = lt.data.energy
        lt.data.keyframe_insert("energy", frame=30)
        lt.data.energy = e0 * 0.08
        lt.data.keyframe_insert("energy", frame=75)
    sky = L.area((0.2, 0.3, 2.15), (0, 0, 0), energy=0, size=1.2, color=(0.72, 0.8, 0.82), name="skylight")
    sky.data.keyframe_insert("energy", frame=30)
    sky.data.energy = 90
    sky.data.keyframe_insert("energy", frame=75)
    cut = bpy.data.objects.get("Cube")
    # water drips from the deckhead
    dm = L.mat_principled("drip", (0.6, 0.65, 0.66), rough=0.05, emit=(0.5, 0.55, 0.56), emit_strength=0.4)
    for k in range(4):
        x, y = 0.6 - 0.35 * k, 0.1 + 0.15 * (k % 2)
        d = L.prim("sphere", loc=(x, y, 2.14), radius=0.012, segments=8, ring_count=5)
        d.scale = (1, 1, 1.6)
        L.assign(d, dm)
        for c in range(3):
            f0 = 50 + k * 13 + c * 22
            if f0 + 8 > n:
                break
            d.location = (x, y, 2.14)
            d.keyframe_insert("location", frame=f0)
            d.location = (x, y, 0.78)
            d.keyframe_insert("location", frame=f0 + 8)
            d.location = (x, y, 2.14)
            d.keyframe_insert("location", frame=f0 + 9)
        M.set_interp(d, "LINEAR")
    cam, ct = cam_path(n, (-0.3, -1.45, 1.35), (-0.2, -1.25, 1.32), (0.2, 0.5, 0.95), (0.2, 0.5, 0.95), lens=35)
    L.bake_static()


# ============================================================================= S04 map plate

def S04(L, n):
    sea, fog = atlantic(n, fog_d=0.015, sun_e=0.35, strength=0.6)
    cam, ct = cam_path(n, (0, -40, 7), (0, -40, 7), (0, 60, 2), (0, 60, 2), lens=35)
    cam.data.keyframe_insert("lens", frame=1)
    cam.data.lens = 37
    cam.data.keyframe_insert("lens", frame=n)
    P = M.brigantine("ship", sails="half", davit_falls=False, deck_props=False)
    bob(P["root"], n, (30, 140, 0), rot_z=R(70))
    L.bake_static()


# ============================================================================= S05 stern: name and empty davits

def S05(L, n):
    sea, fog = atlantic(n, fog_d=0.02, fog_center=(-20, 0, 7), fog_size=(120, 120, 16))
    P = M.brigantine("ship", sails="half")
    bob(P["root"], n, (0, 0, 0), rot_z=0.0, amp=(0.12, 0.012, 0.012))
    falls_swing(P, n, amp=0.25)
    L.area((-22, -8, 4), (R(70), 0, R(-70)), energy=900, size=6, color=DAY, name="sternfill")
    cam, ct = cam_path(n, (-25.5, -5.0, 1.5), (-23.0, -5.2, 6.2), (-15.6, 0.0, 1.5), (-16.4, 0.0, 4.0), lens=35)
    L.handheld(cam, n, amp=0.015, rate=0.5, rot_amp=0.003)
    L.bake_static()


# ============================================================================= S08 sounding rod on deck / S15 pump / S18 wheel

def deck_set(n, pump=True, fog_d=0.03):
    sea, fog = atlantic(n, fog_d=fog_d, fog_center=(0, 0, 7), fog_size=(140, 120, 16))
    P = M.brigantine("ship", sails="half", deck_props=pump)
    bob(P["root"], n, (0, 0, 0), amp=(0.12, 0.015, 0.012))
    return P, fog


def S08(L, n):
    P, fog = deck_set(n)
    r = P["root"]
    rod = M.sounding_rod((0.4, -1.6, DZ), rot_z=R(12))
    rod.parent = r
    # open pump-well cover beside it
    dark = L.mat_principled("well", (0.004, 0.004, 0.004), rough=1)
    hole = L.prim("plane", loc=(-0.6, -1.1, DZ + 0.003), size=1)
    hole.scale = (0.36, 0.36, 1)
    L.assign(hole, dark)
    hole.parent = r
    wm = L.mat_noise_surface("coverwood", (0.12, 0.09, 0.06), (0.26, 0.2, 0.14), scale=10, bump=0.2, voronoi=False)
    for (x, y, sx, sy) in ((-0.6, -0.9, 0.2, 0.025), (-0.6, -1.3, 0.2, 0.025), (-0.8, -1.1, 0.025, 0.2), (-0.4, -1.1, 0.025, 0.2)):
        b = L.prim("cube", loc=(x, y, DZ + 0.03))
        b.scale = (sx, sy, 0.03)
        L.assign(b, wm)
        b.parent = r
    cv = L.prim("cube", loc=(-1.2, -1.5, DZ + 0.02))
    cv.scale = (0.22, 0.22, 0.02)
    cv.rotation_euler = (0, 0, R(20))
    L.assign(cv, wm)
    cv.parent = r
    L.area((2.5, -4.5, DZ + 3.5), (R(55), 0, R(30)), energy=250, size=3, color=DAY, name="deckfill")
    cam, ct = cam_path(n, (2.4, -3.6, DZ + 2.6), (1.4, -2.9, DZ + 1.7), (0.6, -0.6, DZ + 1.2), (0.2, -1.45, DZ), lens=50,
                       parent=r)
    L.bake_static()


def S15(L, n):
    P, fog = deck_set(n, pump=False)
    r = P["root"]
    pm = M.deck_pump((-1.0, 1.2, DZ), dismantled=True, name="pump_d")
    pm.parent = r
    water = L.prim("cyl", loc=(-1.0, 1.75, DZ + 0.01), vertices=20, radius=0.2, depth=0.01)
    L.assign(water, L.mat_principled("wellwater", (0.02, 0.03, 0.03), rough=0.05))
    water.parent = r
    rim = L.prim("torus", loc=(-1.0, 1.75, DZ + 0.02), major_radius=0.22, minor_radius=0.03)
    L.assign(rim, L.mat_principled("wellrim", (0.1, 0.08, 0.06), rough=0.7))
    rim.parent = r
    for f in range(1, n + 1, 3):
        water.location.z = DZ - 0.02 + 0.015 * math.sin(f * 0.4)
        water.rotation_euler = (0.08 * math.sin(f * 0.3), 0.08 * math.cos(f * 0.35), 0)
        water.keyframe_insert("location", frame=f)
        water.keyframe_insert("rotation_euler", frame=f)
    L.area((0.8, -2.0, DZ + 3.0), (R(50), 0, R(30)), energy=250, size=3, color=DAY, name="deckfill")
    tgt = (-0.9, 1.25, DZ + 0.6)
    cam, ct = L.camera(loc=(0, 0, 0), target=tgt, lens=50)
    cam.parent = r
    ct.parent = r
    for f, a in ((1, R(-35)), (n, R(-15))):
        cam.location = (tgt[0] + 3.2 * math.sin(a), tgt[1] - 3.2 * math.cos(a), DZ + 1.9)
        cam.keyframe_insert("location", frame=f)
    L.bake_static()


def S18(L, n):
    P, fog = deck_set(n, fog_d=0.035)
    r = P["root"]
    wheel_drift(P, n, amp=R(10), per=3.0)
    M.cloud_volume((-14, 0, DZ + 2.5), (30, 20, 5), density=0.25, scale=0.9, drift=(0, 2.5, 0), n=n, color=(0.7, 0.75, 0.74),
                   name="fogroll")
    L.area((-10, 3, DZ + 4), (R(50), 0, R(150)), energy=400, size=4, color=DAY, name="wheelfill")
    cam, ct = cam_path(n, (-8.6, 0.6, DZ + 1.9), (-10.6, 0.3, DZ + 1.75), (-13.35, 0.0, DZ + 1.35), (-13.35, 0.0, DZ + 1.3), lens=35,
                       parent=r)
    L.bake_static()


# ============================================================================= below deck: S06 stores, S07 hold, S14 fumes

def hold_shell(length=16.0, half_w=3.2, h=2.6, hatch=(8.0, 1.0), name="hold"):
    planks = M.mat_planks(name + "_pl", c1=(0.05, 0.035, 0.022), c2=(0.13, 0.09, 0.055), width=0.2, axis="X")
    fl = L.prim("plane", loc=(length / 2 - 1, 0, 0), size=1)
    fl.scale = (length + 4, half_w * 2, 1)
    L.assign(fl, planks)
    for s in (-1, 1):
        w = L.prim("cube", loc=(length / 2 - 1, s * half_w, h / 2))
        w.scale = (length / 2 + 2, 0.05, h / 2)
        L.assign(w, planks)
    hx, hw = hatch
    for (x0, x1) in ((-3, hx - hw), (hx + hw, length + 2)):
        c = L.prim("cube", loc=((x0 + x1) / 2, 0, h))
        c.scale = ((x1 - x0) / 2, half_w, 0.06)
        L.assign(c, planks)
    for x in range(-2, int(length) + 2, 1):
        if abs(x - hx) < hw:
            continue
        bm = L.prim("cube", loc=(x, 0, h - 0.1))
        bm.scale = (0.07, half_w, 0.08)
        L.assign(bm, planks)
    end = L.prim("cube", loc=(length + 1, 0, h / 2))
    end.scale = (0.05, half_w, h / 2)
    L.assign(end, planks)
    return planks


def S06(L, n):
    L.set_world((0.004, 0.004, 0.005), 1.0)
    planks = M.mat_planks("st_pl", c1=(0.05, 0.035, 0.022), c2=(0.14, 0.095, 0.06), width=0.18, axis="X")
    fl = L.prim("plane", loc=(0, 0.5, 0), size=1)
    fl.scale = (5, 4, 1)
    L.assign(fl, planks)
    bw = L.prim("cube", loc=(0, 1.25, 1.2))
    bw.scale = (2.5, 0.04, 1.2)
    L.assign(bw, planks)
    sack = (0.42, 0.36, 0.26)
    rnd = random.Random(5)
    cask = M.barrel_mesh("cask", r=0.16, h=0.42, bulge=0.03)
    for lev, z in enumerate((0.55, 1.15, 1.75)):
        sh = L.prim("cube", loc=(0, 0.95, z - 0.03))
        sh.scale = (2.2, 0.3, 0.025)
        L.assign(sh, planks)
        x = -2.0
        while x < 2.0:
            if rnd.random() < 0.45:
                o = L.link(bpy.data.objects.new("cask", cask))
                o.location = (x + 0.18, 0.95, z)
                x += 0.4
            else:
                w = rnd.uniform(0.32, 0.45)
                M.rounded_box((x + w / 2, 0.95, z + 0.17), (w, 0.38, 0.34), sack, bevel=0.35, name="sack", rot=(0, 0, rnd.uniform(-0.1, 0.1)))
                x += w + 0.04
    for xx in (-2.1, 0, 2.1):
        up = L.prim("cube", loc=(xx, 0.95, 1.0))
        up.scale = (0.04, 0.3, 1.0)
        L.assign(up, planks)
    big = M.barrel_mesh("water_barrel", r=0.3, h=0.85)
    for x in (-1.6, -0.9, 1.1, 1.75):
        o = L.link(bpy.data.objects.new("wbarrel", big))
        o.location = (x, 0.35, 0)
    c0, c1 = (-0.3, -1.5, 1.45), (0.25, -1.45, 1.45)
    cam, ct = cam_path(n, c0, c1, (-1.6, 1.0, 1.0), (1.6, 1.0, 1.1), lens=28)
    L.handheld(cam, n, amp=0.02, rate=0.8, rot_amp=0.006)
    lan = L.spot((0.3, -1.3, 1.2), (0, 0, 0), energy=300, size_deg=60, blend=0.7, color=(1.0, 0.68, 0.38), name="lantern")
    M.aim(lan, ct)
    L.flicker(lan, n, depth=0.12, rate=0.5, seed=3)
    L.point((0.3, -1.2, 1.1), energy=8, color=(1.0, 0.65, 0.35), radius=0.1, name="langlow")
    L.particle_cloud((0, 0.3, 1.2), (3, 1.0, 1.5), count=300, radius=0.002, drift=(0.01, 0, 0.005), seed=4, nframes=n, name="dust")
    L.bake_static()


def hold_barrels():
    me = M.barrel_mesh("barrel", r=0.32, h=0.95)
    stencil = L.mat_principled("stencil", (0.75, 0.72, 0.62), rough=0.8)
    rows = [(-2.0, 15.0, 1.25, 3, True), (-2.0, 15.0, -1.25 - 0.0, 3, True), (-2.0, 15.0, 2.3, 3, True), (-2.0, 15.0, -2.3, 3, True)]
    objs = M.barrel_stacks(rows, me, stencil=(3, 6, 10, 14), stencil_mat=stencil)
    return objs


def S07(L, n):
    L.set_world((0.006, 0.007, 0.008), 1.0)
    hold_shell()
    hold_barrels()
    # a few standing barrels in the aisle, two of them open and empty
    me_open = M.barrel_mesh("barrel_open", r=0.32, h=0.95, open_top=True)
    me = bpy.data.meshes["barrel"]
    for (x, y, m_) in ((4.0, 0.3, me_open), (4.8, -0.25, me), (9.5, 0.2, me_open)):
        o = L.link(bpy.data.objects.new("standing", m_))
        o.location = (x, y, 0.0)
    tip = L.link(bpy.data.objects.new("tipped", me_open))
    tip.location = (7.0, -0.1, 0.33)
    tip.rotation_euler = (0, R(90), R(25))
    # water glinting on the floor
    wm, nn, l = L._mat("bilge")
    p = nn["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.01, 0.012, 0.012, 1)
    p.inputs["Roughness"].default_value = 0.05
    tc = nn.new("ShaderNodeTexCoord"); nz = nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3
    mp = nn.new("ShaderNodeMapping"); l.new(tc.outputs["Object"], mp.inputs["Vector"]); l.new(mp.outputs[0], nz.inputs["Vector"])
    bp = nn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15
    l.new(nz.outputs["Fac"], bp.inputs["Height"]); l.new(bp.outputs["Normal"], p.inputs["Normal"])
    mp.inputs["Location"].keyframe_insert("default_value", frame=1)
    mp.inputs["Location"].default_value = (0.5, 0.3, 0.4)
    mp.inputs["Location"].keyframe_insert("default_value", frame=n)
    w = L.prim("plane", loc=(6, 0, 0.015), size=1)
    w.scale = (18, 1.3, 1)
    L.assign(w, wm)
    # grey shaft through the open hatch + hanging lantern
    L.spot((8.0, 0.0, 5.0), (0, 0, 0), energy=4000, size_deg=30, blend=0.3, color=(0.75, 0.82, 0.85), name="hatchshaft")
    L.point((3.0, 0.0, 2.2), energy=60, color=(1.0, 0.65, 0.35), radius=0.1, name="lantern")
    M.lantern((3.0, 0.0, 2.0), energy=0.0, name="hlantern")
    L.water_volume(center=(6, 0, 1.3), size=(20, 6.4, 2.6), color=(0.8, 0.8, 0.78), density=0.05, anisotropy=0.6, name="holdair")
    L.particle_cloud((6, 0, 1.4), (12, 1.2, 2.0), count=600, radius=0.002, drift=(0.0, 0, 0.01), seed=4, nframes=n, name="dust")
    cam, ct = cam_path(n, (-1.2, 0.0, 1.25), (2.6, 0.0, 1.25), (8.0, 0.0, 1.1), (10.0, 0.0, 1.2), lens=24, ease=False)
    L.handheld(cam, n, amp=0.01, rate=0.5, rot_amp=0.003)
    L.cam_light(cam, energy=25, color=(0.7, 0.75, 0.8))
    L.bake_static()


def S14(L, n):
    L.set_world((0.004, 0.005, 0.006), 1.0)
    hold_shell(hatch=(5.0, 1.0))
    hold_barrels()
    planks = bpy.data.materials["hold_pl"]
    # hatch lid hinged on one edge, slams open at 2.9 s
    hp = M.empty("hatch_hinge", (4.0, -1.0, 2.66))
    lid = L.prim("cube", loc=(1.0, 1.0, 0.03))
    lid.scale = (1.0, 1.0, 0.04)
    L.assign(lid, planks)
    lid.parent = hp
    fo = int(2.9 * 24)
    hp.rotation_euler = (0, 0, 0)
    hp.keyframe_insert("rotation_euler", frame=fo - 3)
    hp.rotation_euler = (0, R(-115), 0)
    hp.keyframe_insert("rotation_euler", frame=fo + 2)
    hp.rotation_euler = (0, R(-100), 0)
    hp.keyframe_insert("rotation_euler", frame=fo + 5)
    shaft = L.spot((5.0, 0.0, 6.0), (0, 0, 0), energy=0, size_deg=35, blend=0.3, color=(0.8, 0.88, 0.92), name="burst")
    for f, e in ((1, 0), (fo - 1, 0), (fo + 1, 12000), (fo + 6, 6000), (n, 4500)):
        shaft.data.energy = e
        shaft.data.keyframe_insert("energy", frame=f)
    L.point((1.0, 0.0, 1.8), energy=40, color=(1.0, 0.65, 0.35), radius=0.1, name="lantern")
    M.cloud_volume((4.0, 0.0, 1.2), (12, 2.2, 2.4), density=0.5, scale=1.2, contrast=(0.4, 0.75), drift=(0.4, 0.1, 0.15), n=n,
                   color=(0.55, 0.75, 0.5), name="fumes", emit=(0.25, 0.4, 0.2), emit_strength=0.15)
    L.water_volume(center=(4, 0, 1.3), size=(16, 6.4, 2.6), color=(0.8, 0.82, 0.8), density=0.03, anisotropy=0.6, name="holdair")
    cam, ct = cam_path(n, (0.2, 0.25, 0.45), (0.8, 0.2, 0.5), (4.6, 0.0, 2.5), (4.8, 0.0, 2.7), lens=24)
    L.cam_light(cam, energy=20, color=(0.6, 0.75, 0.6))
    M.shake(bpy.context.scene.camera, [fo + 1], amp=0.03, decay=8)
    L.bake_static()


# ============================================================================= S09 cutaway diagram (hull cross-section)

def S09(L, n):
    L.set_world((0.0, 0.0, 0.0), 0.0)
    cyan = (0.2, 0.85, 1.0)
    hw = M.SHIP_B / 2
    top, keel = 2.15, -2.3
    sec = [(1.0, 1.0), (1.0, 0.55), (0.985, 0.0), (0.93, -0.35), (0.78, -0.65), (0.5, -0.88), (0.18, -1.0), (0.0, -1.0)]
    pts = [(fy * hw, (top * fz if fz > 0 else keel * -fz)) for fy, fz in sec]
    outline = [(y, 0.0, z) for (y, z) in pts] + [(-y, 0.0, z) for (y, z) in reversed(pts[:-1])]
    hull_c = M.glow_poly(outline, color=cyan, strength=4.0, bevel=0.035, name="hull_c")
    hull_g = M.glow_poly(outline, color=(0.25, 1.0, 0.35), strength=6.0, bevel=0.05, name="hull_g")
    M.hide_until(hull_g, 52)
    M.glow_poly([(-hw * 0.97, 0.0, DZ), (hw * 0.97, 0.0, DZ)], color=cyan, strength=2.5, bevel=0.02, name="deck_l")
    M.glow_poly([(-hw * 0.6, 0.0, -1.9), (hw * 0.6, 0.0, -1.9)], color=cyan, strength=1.5, bevel=0.015, name="floor_l")
    M.glow_poly([(0, 0.0, DZ), (0, 0.0, 7.5)], color=cyan, strength=2.0, bevel=0.03, name="mast_l")
    # outer sea level stays put
    M.glow_poly([(-9, 0.02, 0.0), (9, 0.02, 0.0)], color=(0.15, 0.4, 1.0), strength=3.0, bevel=0.025, name="sea_l")
    sea = L.prim("plane", loc=(0, 0.05, -4.5), size=1, rot=(R(90), 0, 0))
    sea.scale = (18, 9, 1)
    L.assign(sea, L.mat_emission("sea_fill", (0.02, 0.06, 0.16), 1.0))
    # inner water rising to 3.5 ft (1.07 m) above the hold floor (shape-key fill)
    lvl = -1.9 + 1.07
    inner = [(y * 0.92, z) for (y, z) in pts if z <= lvl]
    def wall_at(z):
        for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
            if min(z0, z1) <= z <= max(z0, z1):
                return (y0 + (y1 - y0) * (z - z0) / ((z1 - z0) or 1)) * 0.92
        return hw * 0.9
    wy = wall_at(lvl)
    poly = [(wy, lvl)] + inner + [(-y, z) for (y, z) in reversed(inner[:-1])] + [(-wy, lvl)]
    poly = [(y, max(z, -1.9)) for (y, z) in poly]
    vs = [(y, -0.03, z) for (y, z) in poly] + [(0, -0.03, -1.9)]
    c = len(poly)
    faces = [(c, i, (i + 1) % c) for i in range(c)]
    wat = M.mesh_obj("water_in", vs, faces, mat=L.mat_emission("water_m", (0.1, 0.45, 0.9), 2.0))
    wat.shape_key_add(name="Basis")
    sk = wat.shape_key_add(name="full")
    for i, v in enumerate(wat.data.shape_keys.key_blocks["Basis"].data):
        v.co = (v.co.x * 0.25, v.co.y, -1.9)
    sk.value = 0.0
    sk.keyframe_insert("value", frame=6)
    sk.value = 1.0
    sk.keyframe_insert("value", frame=46)
    mk = M.glow_poly([(-hw * 0.95, -0.05, lvl), (hw * 0.95, -0.05, lvl)], color=(1.0, 0.3, 0.2), strength=4.0, bevel=0.02, name="mark")
    M.hide_until(mk, 8)
    t = L.text3d("3.5 FT", loc=(-hw * 0.95 + 0.9, -0.06, lvl + 0.25), size=0.32, extrude=0, mat=L.mat_emission("mk_t", (1.0, 0.35, 0.25), 3.0),
                 name="mark_t")
    t.data.font = M._font(M.F_OSWALD) or t.data.font
    M.hide_until(t, 8)
    cam, ct = L.camera(loc=(0, -30, 1.5), target=None, lens=50)
    cam.rotation_euler = (R(90), 0, 0)
    M.ortho(cam, 22)
    cam.data.keyframe_insert("ortho_scale", frame=1)
    cam.data.ortho_scale = 19.5
    cam.data.keyframe_insert("ortho_scale", frame=n)
    cam.location = (0, -30, 3.4)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0, -30, 3.0)
    cam.keyframe_insert("location", frame=n)
    L.bake_static()


# ============================================================================= S11 magazine page / S12 Doyle's desk

def S11(L, n):
    L.set_world((0.002, 0.002, 0.003), 1.0)
    M.desk(size=(3.0, 2.2))
    pg = M.newspaper((0.0, 0.0, 0.0), rot_z=R(-6), size=(0.3, 0.42), name="mag", masthead="")
    pg.keyframe_insert("rotation_euler", frame=1)
    pg.rotation_euler = (0, 0, R(-2))
    pg.keyframe_insert("rotation_euler", frame=n)
    M.oil_lamp((0.4, 0.35, 0.0), energy=25, flicker_n=n)
    M.book((-0.38, 0.3, 0.0), rot_z=R(15), title=None, name="b1")
    cam, ct = L.camera(loc=(0.0, -0.02, 1.15), target=(0.0, 0.0, 0.0), lens=50)
    cam.constraints.clear()
    cam.rotation_euler = (0, 0, R(-2))
    cam.keyframe_insert("rotation_euler", frame=1)
    cam.rotation_euler = (0, 0, R(3))
    cam.keyframe_insert("rotation_euler", frame=n)
    L.bake_static()


def S12(L, n):
    L.set_world((0.004, 0.0035, 0.003), 1.0)
    wall = L.prim("plane", loc=(0, 2.0, 1.5), size=1, rot=(R(90), 0, 0))
    wall.scale = (8, 4, 1)
    L.assign(wall, L.mat_noise_surface("wallp", (0.08, 0.05, 0.03), (0.16, 0.1, 0.06), scale=4, bump=0.2, voronoi=False))
    floor = L.prim("plane", loc=(0, 0, 0), size=1)
    floor.scale = (8, 8, 1)
    L.assign(floor, M.mat_planks("floor", c1=(0.05, 0.03, 0.02), c2=(0.12, 0.07, 0.04), width=0.14, axis="X"))
    dk = M.mat_wood_dark("desk_m")
    top = L.prim("cube", loc=(0, 0.9, 0.76))
    top.scale = (0.75, 0.38, 0.025)
    L.assign(top, dk)
    for (x, y) in ((-0.68, 0.58), (0.68, 0.58), (-0.68, 1.22), (0.68, 1.22)):
        lg = L.prim("cube", loc=(x, y, 0.37))
        lg.scale = (0.03, 0.03, 0.37)
        L.assign(lg, dk)
    ms = L.prim("plane", loc=(-0.05, 0.85, 0.79), size=1, rot=(0, 0, R(8)))
    ms.scale = (0.22, 0.3, 1)
    L.assign(ms, M.mat_paper("ms", (0.7, 0.66, 0.55)))
    pen = L.prim("cyl", loc=(0.12, 0.8, 0.795), vertices=8, radius=0.004, depth=0.16, rot=(0, R(90), R(30)))
    L.assign(pen, L.mat_principled("pen", (0.02, 0.02, 0.02), rough=0.3))
    for i in range(3):
        M.book((0.55, 1.05 - i * 0.002, 0.785 + i * 0.025), size=(0.15, 0.22, 0.024), cover=(0.2, 0.05 + 0.03 * i, 0.03), rot_z=R(80 + i * 5),
               name=f"bk{i}")
    lr, lp = M.oil_lamp((-0.55, 1.05, 0.785), energy=45, flicker_n=n)
    L.chair((0, 0.25, 0), rot_z=0)
    fg = L.char_figure("writer", color=(0.02, 0.018, 0.018), coat=True)
    fg["root"].location = (0, 0.25, -0.42)
    for t, s in (("L", 1), ("R", -1)):
        fg["hip" + t].rotation_euler = (R(85), 0, 0)
        fg["knee" + t].rotation_euler = (R(-85), 0, 0)
        fg["shoulder" + t].rotation_euler = (R(55), 0, s * -0.15)
        fg["elbow" + t].rotation_euler = (R(45), 0, 0)
    fg["neck"].rotation_euler = (R(20), 0, 0)
    fg["pelvis"].rotation_euler = (R(8), 0, 0)
    for f in range(1, n + 1, 4):
        fg["elbowR"].rotation_euler = (R(45) + 0.06 * math.sin(f * 0.5), 0, 0.04 * math.sin(f * 0.7))
        fg["elbowR"].keyframe_insert("rotation_euler", frame=f)
    # side table with the deerstalker (a nod to the detective he would later create)
    st = L.prim("cyl", loc=(1.35, 0.55, 0.6), vertices=24, radius=0.28, depth=0.03)
    L.assign(st, dk)
    sl = L.prim("cyl", loc=(1.35, 0.55, 0.3), vertices=8, radius=0.03, depth=0.6)
    L.assign(sl, dk)
    M.deerstalker((1.35, 0.55, 0.62), rot_z=R(30))
    hatlight = L.spot((1.0, -0.3, 1.7), (0, 0, 0), energy=0, size_deg=25, blend=0.6, color=(1.0, 0.75, 0.45), name="hatlight")
    M.aim(hatlight, M.empty("hat_t", (1.35, 0.55, 0.65)))
    for f, e in ((1, 0), (int(n * 0.55), 0), (int(n * 0.85), 90), (n, 90)):
        hatlight.data.energy = e
        hatlight.data.keyframe_insert("energy", frame=f)
    L.point((-0.6, -0.8, 1.6), energy=12, color=(0.9, 0.7, 0.5), radius=0.5, name="roomfill")
    ctr = Vector((0.4, 0.7, 0.85))
    cam, ct = L.camera(loc=(0, 0, 0), target=None, lens=40)
    tg = M.empty("arc_t", (0.0, 0.85, 0.9))
    c = cam.constraints.new("TRACK_TO")
    c.target = tg
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    for f, a, r_, tp in ((1, R(-150), 2.4, (0.0, 0.85, 0.95)), (int(n * 0.5), R(-120), 2.3, (0.3, 0.75, 0.9)), (n, R(-95), 1.9, (1.25, 0.55, 0.66))):
        cam.location = (ctr.x + r_ * math.cos(a), ctr.y + r_ * math.sin(a), 1.45 - 0.15 * (f / n))
        cam.keyframe_insert("location", frame=f)
        tg.location = tp
        tg.keyframe_insert("location", frame=f)
    L.particle_cloud((0.2, 0.6, 1.2), (1.6, 1.2, 1.0), count=200, radius=0.0015, drift=(0.01, 0, 0.005), seed=4, nframes=n, name="motes")
    L.bake_static()


# ============================================================================= S16 lifeboat + ship pulling away (DRAMATISATION)

def S16(L, n):
    sea, fog = atlantic(n, fog_d=0.02, fog_center=(40, 0, 7), fog_size=(200, 120, 16), wave=0.4)
    fog_keys(fog, [(1, 0.018), (n, 0.04)])
    bt, figs = M.lifeboat((0, 0, 0.1), people=4)
    bob(bt, n, (0, 0, 0.1), rot_z=R(15), amp=(0.15, 0.05, 0.03), per=(4.5, 5.5, 5.0))
    P = M.brigantine("ship", sails="full", fill=0.8, davit_falls=False)
    bob(P["root"], n, (48, 14, 0), rot_z=R(8), travel=(30, 4, 0))
    L.area((-6, -6, 6), (R(55), 0, R(-45)), energy=300, size=6, color=DAY, name="boatfill")
    cam, ct = cam_path(n, (-7.5, -3.2, 2.1), (-7.4, -3.1, 2.1), (20.0, 5.0, 3.5), (24.0, 6.0, 3.5), lens=35)
    L.handheld(cam, n, amp=0.03, rate=0.4, rot_amp=0.006)
    L.bake_static()


# ============================================================================= S17 memorial: lantern on a plank at dusk

def S17(L, n):
    sea, fog = atlantic(n, fog_d=0.015, fog_center=(0, 30, 6), fog_size=(140, 100, 14), sun_e=0.15, wave=0.15, strength=0.7, dusk=True)
    root = M.empty("float", (0, 0, 0))
    pl = L.prim("cube", loc=(0, 0, 0.02))
    pl.scale = (0.7, 0.16, 0.04)
    L.assign(pl, L.mat_noise_surface("plank", (0.08, 0.06, 0.04), (0.18, 0.14, 0.1), scale=8, bump=0.2, voronoi=False))
    pl.parent = root
    lr, lp = M.lantern((0, 0, 0.06), energy=30, name="lantern", flicker_n=n)
    lr.parent = root
    lr.scale = (1.6, 1.6, 1.6)
    bob(root, n, (0, 0, 0.0), amp=(0.06, 0.06, 0.05), per=(3.5, 4.2, 3.9))
    L.area((2, 4, 2), (R(-60), 0, R(150)), energy=40, size=4, color=(0.55, 0.6, 0.7), name="rim")
    cam, ct = cam_path(n, (0.3, -4.2, 0.75), (0.2, -3.0, 0.6), (0.0, 0.0, -0.25), (0.0, 0.0, -0.2), lens=50)
    L.bake_static()
