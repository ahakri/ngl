"""SCUBA-01 — He Survived 60 Hours Inside a Sunken Ship (Harrison Okene, tug Jascon-4, 2013).
One builder per shot: def Sxx(L, n). Scuba builders live in PIPELINE/blender/lib_scuba.py.
Okene is always a faceless dark silhouette; no bodies are ever shown.
"""
import sys, os, math, random, importlib
import bpy
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_HERE)), "PIPELINE", "blender"))
import lib_scuba as S
importlib.reload(S)

PI = math.pi
WATER = 1.2           # waterline inside the compartment (air pocket = 2.4 - 1.2 = 1.2 m ~ 4 ft)
ROOM = (2.4, 2.2, 2.4)
CAM01_A = (0.1, -2.75, 1.4)   # S01 start (S20 ends here for the loop)
CAM01_B = (0.08, -2.15, 1.36)
CAM01_T = (0.0, 0.4, 0.88)
WARM = (1.0, 0.78, 0.52)
TEAL = (0.35, 0.8, 0.8)


# ----------------------------------------------------------------------------- helpers

def _objs():
    return set(bpy.data.objects)


def _group(before, name, pivot=(0, 0, 0)):
    """Parent all new top-level objects to a pivot empty (so a whole set can roll/tilt)."""
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    pv = Vector(pivot)
    for o in set(bpy.data.objects) - before:
        if o is root or o.parent is not None:
            continue
        o.location = o.location - pv
        o.parent = root
    root.location = pv
    return root


def _pose(fig, f, **rots):
    for k, v in rots.items():
        fig[k].rotation_euler = v
        fig[k].keyframe_insert("rotation_euler", frame=f)


def _world(col=(0.004, 0.012, 0.014), strength=1.0):
    L.set_world(color=col, strength=strength) if False else None


def okene_figure(L, name="okene", loc=(0.35, 0.3, 0.0), rot_z=0.9, n=100, arm_up=True, bob=0.025, color=(0.05, 0.05, 0.055)):
    """Faceless silhouette treading water with head+shoulders above the waterline."""
    fig = L.char_figure(name=name, color=color, height=1.75)
    r = fig["root"]
    r.location = (loc[0], loc[1], WATER - 1.42 + loc[2])
    r.rotation_euler = (0.08, 0, rot_z)
    for tag, s in (("L", 1), ("R", -1)):
        fig[f"hip{tag}"].rotation_euler = (0.55 + 0.1 * s, 0, 0)
        fig[f"knee{tag}"].rotation_euler = (-1.1, 0, 0)
    fig["shoulderL"].rotation_euler = (0.5, 0, -0.5)
    fig["elbowL"].rotation_euler = (0.8, 0, 0)
    if arm_up:
        fig["shoulderR"].rotation_euler = (2.45, 0, 0.25)
        fig["elbowR"].rotation_euler = (0.35, 0, 0)
    else:
        fig["shoulderR"].rotation_euler = (0.5, 0, 0.5)
        fig["elbowR"].rotation_euler = (0.8, 0, 0)
    fig["neck"].rotation_euler = (-0.25, 0, 0)  # chin up toward the air
    # breathing / treading bob
    base = Vector(r.location)
    for f in range(1, n + 1, 3):
        t = f / 24
        r.location = (base.x, base.y, base.z + bob * math.sin(t * 2.2))
        r.keyframe_insert("location", frame=f)
        fig["shoulderL"].rotation_euler = (0.5 + 0.25 * math.sin(t * 2.2), 0, -0.5)
        fig["shoulderL"].keyframe_insert("rotation_euler", frame=f)
    return fig


def flashlight_prop(L, loc, aim, energy=120, n=100, bobamp=0.01, name="flash"):
    """Small handheld torch floating at the waterline: body, glowing lens, spot cone into the water."""
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    root.location = loc
    d = Vector(aim).normalized()
    root.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    body = L.prim("cyl", loc=(0, 0, 0.09), vertices=12, radius=0.03, depth=0.2, name=name + "_body")
    L.assign(body, L.mat_principled(name + "_bm", (0.6, 0.15, 0.05), rough=0.4))
    body.parent = root
    lens = L.prim("cyl", loc=(0, 0, -0.012), vertices=12, radius=0.034, depth=0.01, name=name + "_lens")
    L.assign(lens, L.mat_emission(name + "_lm", (1, 0.85, 0.6), 25))
    lens.parent = root
    sp = L.spot((0, 0, -0.03), (0, 0, 0), energy=energy, size_deg=30, blend=0.5, color=(1, 0.82, 0.6), name=name + "_spot")
    sp.parent = root
    base = Vector(loc)
    for f in range(1, n + 1, 4):
        root.location = (base.x, base.y, base.z + bobamp * math.sin(f * 0.21))
        root.keyframe_insert("location", frame=f)
    return root, sp


def okene_set(L, n, ripple=0.012, debris=500, fig=True, flashlight=True, water_density=0.35, arm_up=True,
              fig_loc=(0.05, 0.35, 0.0), fig_rot=0.75, pocket_light=30, drips=True):
    """The inverted compartment (S01/S07/S14/S19/S20): water to 1.2 m, air pocket above, Okene in the pocket."""
    S.setup()
    L.set_world(color=(0.003, 0.01, 0.012), strength=1.0)
    w, d, h = ROOM
    P = S.inverted_compartment(w=w, d=d, h=h, water=WATER, nframes=n, water_density=water_density,
                               water_col=(0.25, 0.62, 0.58), ripple_amp=ripple, rust=0.6)
    out = {"cmp": P}
    if fig:
        out["fig"] = okene_figure(L, n=n, arm_up=arm_up, loc=fig_loc, rot_z=fig_rot)
    if flashlight:
        out["flash"], out["flash_spot"] = flashlight_prop(L, (-0.55, -0.35, WATER + 0.01), (-0.25, 0.9, -0.6),
                                                          energy=220, n=n)
        S.beam_cone((0, 0, 0), (0, 0, -1), length=1.6, radius=0.45, color=(1, 0.85, 0.6), strength=1.2, alpha=0.18,
                    name="flashbeam", parent=out["flash_spot"])
    # air-pocket bounce: warm light reflected up off the water onto the overhead + walls
    out["bounce"] = L.area((0.0, 0.2, WATER + 0.06), (0, 0, 0), energy=pocket_light, size=1.6, color=WARM, name="bounce")
    out["bounce"].rotation_euler = (PI, 0, 0)  # emit upward
    out["underfill"] = L.point((0.4, -0.5, 0.45), energy=12, color=(0.3, 0.8, 0.75), radius=0.4, name="underfill")
    out["rim"] = L.point((-0.6, 0.85, h - 0.35), energy=8, color=WARM, radius=0.15, name="rim")
    if debris:
        L.particle_cloud((0, 0, WATER / 2), (w * 0.95, d * 0.95, WATER * 0.9), count=debris, radius=0.003, nframes=n,
                         drift=(0.01, 0.0, 0.015), name="debris",
                         mat=L.mat_principled("debris_m", (0.6, 0.6, 0.5), rough=1, emit=(0.4, 0.45, 0.35), emit_strength=0.15))
    if drips:
        S.drips([(-0.6, 0.2, h - 0.02), (0.75, -0.2, h - 0.02), (0.1, 0.7, h - 0.02)], n, fall=h - WATER, seed=3)
    return out


# ----------------------------------------------------------------------------- S01

def S01(L, n):
    o = okene_set(L, n)
    cam, _ = L.camera(loc=CAM01_A, target=CAM01_T, lens=24)
    L.cam_keys(cam, [(1, CAM01_A), (n, CAM01_B)], ease=False)
    L.handheld(cam, n, amp=0.012, rate=0.5)
    L.cam_light(cam, energy=18, color=(0.5, 0.85, 0.9), size_deg=80)
    L.bake_static()


# ----------------------------------------------------------------------------- S02 night capsize

def S02(L, n):
    S.setup(vol_end=200)
    S.sky_gradient(top=(0.004, 0.008, 0.02), horizon=(0.09, 0.16, 0.3), strength=1.0, sun_dir=(0.0, 1.0, 0.05),
                   sun_col=(0.5, 0.7, 1.0), sun_size=0.05, sun_strength=1.5, below=(0.01, 0.02, 0.03))
    sea = S.ocean(size=220, nframes=n, wave_scale=1.6, choppiness=1.2, resolution=11, spatial=60, wind=22, speed=1.0,
                  mat=S.mat_ocean("sea_night", deep=(0.002, 0.008, 0.012), shallow=(0.03, 0.07, 0.1), rough=0.12,
                                  under=(0.02, 0.05, 0.06), under_strength=0.2))
    pivot = bpy.data.objects.new("roll", None)
    bpy.context.scene.collection.objects.link(pivot)
    tug, P = S.tug("jascon", lit_windows=True, rusted=0.0)
    tug.parent = pivot
    tug.location = (0, 0, -1.25)
    pivot.location = (0, 0, 0)
    # heavy rolling then over past 90 deg (the capsize reads around 2 s in, after the map)
    rk = [(1, 0.12), (14, -0.18), (28, 0.28), (40, 0.05), (52, 0.55), (66, 1.2), (80, 1.85), (n, 2.35)]
    for f, a in rk:
        pivot.rotation_euler = (0.02 * math.sin(f * 0.2), a, 0.0)
        pivot.keyframe_insert("rotation_euler", frame=f)
    for f, z in ((1, 0.0), (40, 0.1), (60, -0.3), (n, -1.4)):
        pivot.location = (0, 0, z)
        pivot.keyframe_insert("location", frame=f)
    # windows die as she goes over
    win = bpy.data.materials.get("jascon_win")
    if win:
        em = [nd for nd in win.node_tree.nodes if nd.type == "EMISSION"][0]
        for f, v in ((1, 6), (60, 6), (66, 0.6), (70, 4), (76, 0.0), (n, 0.0)):
            em.inputs[1].default_value = v
            em.inputs[1].keyframe_insert("default_value", frame=f)
    # moon/dawn rim from behind + cold fill
    L.sun(rot=(math.radians(84), 0, math.radians(180)), energy=1.2, color=(0.55, 0.7, 1.0), angle=3)
    L.area((-14, 18, 9), (0, 0, 0), energy=4000, size=10, color=(0.5, 0.65, 1.0), name="fill")
    bpy.data.objects["fill"].rotation_euler = (Vector((14, -18, -8)).to_track_quat("-Z", "Y").to_euler())
    L.point((0, 3.5, 6.5), energy=200, color=(1, 0.75, 0.45), radius=0.5, name="decklamp").parent = tug
    # spray + rain
    L.particle_cloud((0, 4, 1.0), (12, 16, 3), count=250, radius=0.025, nframes=n, drift=(0.6, -0.3, 0.5), name="spray",
                     mat=L.mat_principled("spray_m", (0.8, 0.9, 1.0), rough=0.3, emit=(0.4, 0.5, 0.6), emit_strength=0.5))
    rain = L.particle_cloud((0, 0, 0.6), (40, 40, 3.0), count=900, radius=0.012, nframes=n, drift=(0.3, 0, -3.0),
                            name="rain", mat=L.mat_principled("rain_m", (0.7, 0.8, 0.9), rough=0.3, emit=(0.4, 0.5, 0.6),
                                                              emit_strength=0.6))
    rain.scale = (1, 1, 6)
    cam, tgt = L.camera(loc=(-9.5, 24.0, 3.4), target=(0, 1.0, 2.0), lens=35)
    L.cam_keys(cam, [(1, (-9.5, 24.0, 3.4)), (n, (-8.6, 22.0, 3.1))])
    L.handheld(cam, n, amp=0.08, rate=0.5, rot_amp=0.01)
    L.bake_static()


# ----------------------------------------------------------------------------- S03 the room tips

def S03(L, n):
    S.setup()
    L.set_world(color=(0, 0, 0), strength=0)
    w, d, h = 1.6, 1.8, 2.2
    before = _objs()
    P = S.inverted_compartment(w=w, d=d, h=h, water=0.02, nframes=n, water_density=0.0, rust=0.15,
                               wall_col=(0.55, 0.6, 0.55), light_fitting=False, ripple_amp=0.0)
    for k in ("volume", "surface"):
        bpy.data.objects.remove(P[k], do_unlink=True)
    room = _group(before, "room", pivot=(0, 0, h / 2))
    room.rotation_euler = (0, PI, 0)  # flip upright: toilet now on the floor, door opening from the floor
    # (after the flip: floor at local z=+h/2 -> world bottom). Camera, figure, props all ride with the room.
    # ceiling bulb fixture (local -h/2 region == world top after flip)
    fix = L.prim("cube", loc=(0, 0, -h / 2 + 0.03), name="fixture")
    fix.scale = (0.08, 0.08, 0.03)
    L.assign(fix, L.mat_principled("fixm", (0.1, 0.1, 0.1)))
    fix.parent = room
    hang = bpy.data.objects.new("hang", None)
    bpy.context.scene.collection.objects.link(hang)
    hang.parent = room
    hang.location = (0, 0, -h / 2 + 0.05)
    cord = L.prim("cyl", loc=(0, 0, -0.2), vertices=6, radius=0.006, depth=0.4, name="cord")
    L.assign(cord, L.mat_principled("cordm", (0.02, 0.02, 0.02)))
    cord.parent = hang
    bulbm = L.mat_emission("bulbm", (1.0, 0.8, 0.5), 30)
    bulb = L.prim("sphere", loc=(0, 0, -0.45), segments=12, ring_count=8, radius=0.05, name="bulb")
    L.assign(bulb, bulbm)
    bulb.parent = hang
    lamp = L.point((0, 0, -0.5), energy=35, color=(1.0, 0.78, 0.5), radius=0.05, name="bulb_light")
    lamp.parent = hang
    # NOTE: hang's local frame is flipped by the room (pi about Y) -> local -Z is world +Z; so the cord hangs "up"
    # in local terms. Correct by giving hang a base rotation of pi about Y (cancels) and then counter-rolling.
    # roll: the ship heels over
    roll = [(1, 0.0), (10, 0.06), (18, -0.03), (30, 0.18), (42, 0.35), (54, 0.62), (n, 0.8)]
    for f, a in roll:
        room.rotation_euler = (0, PI + a, 0)
        room.keyframe_insert("rotation_euler", frame=f)
        lag = a * 0.75 + (0.08 * math.sin(f * 0.35) if f > 20 else 0)
        hang.rotation_euler = (0, PI - lag, 0)
        hang.keyframe_insert("rotation_euler", frame=f)
    # flicker then die
    L.flicker(lamp, n, base=35, seed=4, depth=0.25, rate=0.6, blackouts=((40, 41), (n - 7, n + 2)))
    em = [nd for nd in bulbm.node_tree.nodes if nd.type == "EMISSION"][0]
    for f, v in ((1, 30), (39, 30), (40, 0.5), (43, 0.5), (44, 30), (n - 8, 30), (n - 7, 0.2), (n, 0.2)):
        em.inputs[1].default_value = v
        em.inputs[1].keyframe_insert("default_value", frame=f)
    # figure braced against the side wall (room-local coords: z is flipped => build in world then parent w/o inverse)
    fig = L.char_figure(name="okene", color=(0.06, 0.06, 0.065), height=1.72)
    fr = fig["root"]
    fr.parent = room
    # room-local with pi flip: world (x,y,z) = (-lx, ly, -lz) + pivot
    fr.location = (0.25, 0.45, h / 2)
    fr.rotation_euler = (0, PI, PI + 0.5)
    _pose(fig, 1, shoulderL=(0.3, 0, -1.3), shoulderR=(0.3, 0, 1.3), elbowL=(0.6, 0, 0), elbowR=(0.6, 0, 0),
          hipL=(0.1, 0, -0.15), hipR=(-0.1, 0, 0.15))
    _pose(fig, n, shoulderL=(0.4, 0, -1.55), shoulderR=(0.1, 0, 1.6), elbowL=(0.3, 0, 0), elbowR=(0.2, 0, 0),
          hipL=(0.2, 0, -0.25), hipR=(-0.1, 0, 0.3))
    # door swings shut (door is on the room's -X wall in build coords => hinge empty)
    door = P.get("door")
    if door:
        hinge = bpy.data.objects.new("hinge", None)
        bpy.context.scene.collection.objects.link(hinge)
        hinge.parent = room
        hinge.location = (door.location.x, door.location.y - 0.42, door.location.z)
        door.parent = hinge
        door.location = (0, 0.42, 0)
        for f, a in ((1, -1.1), (16, -1.0), (30, -0.2), (34, 0.0), (n, 0.0)):
            hinge.rotation_euler = (0, 0, a)
            hinge.keyframe_insert("rotation_euler", frame=f)
    # rush of water under/through the door + sliding bucket
    wm = S.mat_water_surface("rush_m", color=(0.03, 0.12, 0.13), rough=0.05, alpha=0.8)
    sheet = L.prim("plane", loc=(-w / 2 + 0.3, 0, h / 2 - 0.03), size=1, name="rush")
    sheet.parent = room
    L.assign(sheet, wm)
    for f, sx, sy in ((1, 0.01, 0.01), (34, 0.05, 0.6), (48, 0.5, 1.4), (n, 1.3, 1.7)):
        sheet.scale = (sx, sy, 1)
        sheet.location = (-w / 2 + 0.05 + sx / 2, 0, h / 2 - 0.03)
        sheet.keyframe_insert("scale", frame=f)
        sheet.keyframe_insert("location", frame=f)
    L.particle_cloud((-w / 2 + 0.1, 0, h / 2 - 0.2), (0.1, 0.8, 0.3), count=200, radius=0.005, nframes=n,
                     drift=(0.8, 0, -0.3), name="rushspray",
                     mat=L.mat_principled("rsm", (0.7, 0.85, 0.9), rough=0.2, emit=(0.3, 0.45, 0.5), emit_strength=0.5)).parent = room
    bucket = L.prim("cyl", loc=(-0.45, -0.55, h / 2 - 0.14), vertices=14, radius=0.12, depth=0.26, name="bucket")
    L.assign(bucket, L.mat_principled("bucketm", (0.1, 0.25, 0.6), rough=0.5))
    bucket.parent = room
    for f, x in ((1, -0.45), (30, -0.4), (45, -0.1), (n, 0.5)):
        bucket.location = (x, -0.55, h / 2 - 0.14)
        bucket.keyframe_insert("location", frame=f)
    # camera locked to the room
    cam, _ = L.camera(loc=(0, -0.85, 0.0), lens=16)
    cam.parent = room
    cam.rotation_euler = (PI / 2 - 0.1, PI, 0)  # world: looking +Y, slightly down (inside the flipped parent)
    L.cam_keys(cam, [(1, (0, -0.88, 0.0)), (n, (0, -0.72, -0.05))])
    L.cam_light(cam, energy=6, color=(0.7, 0.8, 0.9))
    L.bake_static()


# ----------------------------------------------------------------------------- shared wreck scene

def _sea_floor(L, n, size=120, mat=None):
    sb = L.seabed(size=size, strength=0.5, mat=mat or L.mat_noise_surface("silt_s", (0.05, 0.06, 0.05), (0.14, 0.15, 0.12),
                                                                            scale=6, bump=0.15, voronoi=False))
    return sb


def wreck_scene(L, n, rest_z=5.65, vol_density=0.045, ambient=0.15):
    S.setup(vol_end=45, vol_tile="4", vol_samples=20)
    vol_density *= 0.45
    L.set_world(color=(0.01, 0.04, 0.05), strength=ambient)
    S.world_volume(color=(0.15, 0.45, 0.5), density=vol_density, anisotropy=0.5, absorption=(0.05, 0.25, 0.3))
    _sea_floor(L, n)
    tug, P = S.tug("wreck", rusted=0.7, house_col=(0.6, 0.62, 0.58),
                   hull_cols=[(-1, (0.24, 0.07, 0.04)), (1.2, (0.05, 0.05, 0.05)), (2.15, (0.5, 0.5, 0.48))])
    tug.rotation_euler = (0, PI, 0.35)
    tug.location = (0, 0, rest_z)
    # hide the mast (it would pierce the bed) — snapped off
    for nm in ("wreck_mast", "wreck_yard"):
        if nm in bpy.data.objects:
            bpy.data.objects[nm].hide_render = True
    return tug, P


def _hull_fill(L, k=1.0):
    """Cold soft key + rim so the hull reads in dark water (no fog-wall from a camera lamp)."""
    a = L.area((-9, -10, 12), (0, 0, 0), energy=2500 * k, size=8, color=(0.5, 0.8, 0.9), name="hullkey")
    a.rotation_euler = (Vector((0, 0, 3)) - Vector((-9, -10, 12))).to_track_quat("-Z", "Y").to_euler()
    b = L.area((8, 10, 9), (0, 0, 0), energy=1500 * k, size=6, color=(0.3, 0.6, 0.8), name="hullrim")
    b.rotation_euler = (Vector((0, 0, 3)) - Vector((8, 10, 9))).to_track_quat("-Z", "Y").to_euler()


# ----------------------------------------------------------------------------- S04 sinking and settling

def S04(L, n):
    tug, P = wreck_scene(L, n, vol_density=0.05)
    land = 58
    rest = 5.65
    for f, z, ry in ((1, 15.0, PI - 0.12), (20, 11.5, PI - 0.08), (40, 7.6, PI - 0.03), (land, rest, PI), (land + 4, rest - 0.08, PI + 0.01),
                     (n, rest, PI)):
        tug.location = (0, 0, z)
        tug.rotation_euler = (0.03, ry, 0.35)
        tug.keyframe_insert("location", frame=f)
        tug.keyframe_insert("rotation_euler", frame=f)
    # bubbles trailing from the hull (carrier follows the hull's position)
    car = bpy.data.objects.new("carrier", None)
    bpy.context.scene.collection.objects.link(car)
    for f, z in ((1, 15.0), (20, 11.5), (40, 7.6), (land, rest), (n, rest)):
        car.location = (0, 0, z)
        car.keyframe_insert("location", frame=f)
    for i, (x, y) in enumerate(((0.8, -3), (-0.6, 1.5), (0.2, 4.5))):
        bs = L.bubbles_stream((x, y, 0.4), count=40, nframes=n, rise=6.0, spread=0.35, seed=20 + i, name=f"hb{i}", size=0.07)
        for b in bs:
            b.parent = car
    # silt burst on impact
    for i, (sx, life) in enumerate(((1.0, 1.0), (1.6, 0.7))):
        pc = L.particle_cloud((0, 0, 0.6), (14, 16, 1.4), count=1200, radius=0.03, nframes=n, drift=(0, 0, 0.2),
                              name=f"silt{i}", seed=30 + i,
                              mat=L.mat_principled(f"siltm{i}", (0.35, 0.33, 0.25), rough=1, emit=(0.2, 0.22, 0.18), emit_strength=0.15))
        pc.scale = (0.01, 0.01, 0.01)
        pc.keyframe_insert("scale", frame=land - 1)
        pc.scale = (0.5 * sx, 0.5 * sx, 0.4)
        pc.keyframe_insert("scale", frame=land + 2)
        pc.scale = (1.1 * sx, 1.1 * sx, 1.3)
        pc.keyframe_insert("scale", frame=n)
    L.particle_cloud((0, 0, 8), (30, 30, 20), count=1200, radius=0.02, nframes=n, drift=(0, 0, -0.1), name="snow")
    L.sun(rot=(0.2, 0.1, 0.3), energy=1.2, color=(0.5, 0.8, 0.9), angle=10)
    tgt = bpy.data.objects.new("tgt", None)
    bpy.context.scene.collection.objects.link(tgt)
    for f, z in ((1, 13.5), (20, 10.5), (40, 7.0), (land, 4.2), (n, 3.9)):
        tgt.location = (0, 0, z)
        tgt.keyframe_insert("location", frame=f)
    cam, _ = L.camera(loc=(-13.0, -12.0, 6.5), target=tgt, lens=28)
    L.cam_keys(cam, [(1, (-13.0, -12.0, 8.0)), (land, (-12.0, -11.0, 5.2)), (n, (-11.7, -10.7, 5.0))])
    L.handheld(cam, n, amp=0.04, rate=0.4)
    L.cam_light(cam, energy=60, color=(0.55, 0.85, 0.95), size_deg=60)
    _hull_fill(L)
    # shake on impact
    for fc in L._fcurves(cam.animation_data.action):
        pass
    L.bake_static()


# ----------------------------------------------------------------------------- S05 inverted corridor

def S05(L, n):
    S.setup()
    L.set_world(color=(0.002, 0.008, 0.01), strength=1)
    length, w, h = 8.0, 1.5, 2.3
    wl = h - 0.4  # water to near the (inverted) floor
    steel = S.mat_paint("cor_wall", (0.32, 0.36, 0.32), rough=0.55, grime=0.5, rust=0.6, scale=2.5)
    deckm = L.mat_noise_surface("cor_deck", (0.06, 0.06, 0.055), (0.2, 0.19, 0.17), scale=14, bump=0.5, metal=0.5)
    pipem = S.mat_paint("cor_pipe", (0.35, 0.25, 0.15), rough=0.4, metal=0.6, grime=0.3, rust=0.6)
    doorm = S.mat_paint("cor_door", (0.45, 0.45, 0.4), rough=0.5, grime=0.5, rust=0.5)
    for sx in (-1, 1):
        o = L.prim("cube", loc=(sx * (w / 2 + 0.04), length / 2, h / 2), name="cwall")
        o.scale = (0.04, length / 2 + 0.5, h / 2 + 0.05)
        L.assign(o, steel)
        for k, z in enumerate((h - 0.25, h - 0.4, 0.5)):
            p = L.prim("cyl", loc=(sx * (w / 2 - 0.06 - 0.03 * k), length / 2, z), vertices=10, radius=0.035, depth=length + 1,
                       rot=(PI / 2, 0, 0), name="cpipe")
            L.assign(p, pipem)
        # doors every 2 m, opening reaching up to the (inverted) floor
        for y in (1.5, 3.5, 5.5):
            fr = L.prim("cube", loc=(sx * (w / 2 - 0.01), y, h - 1.0), name="cdoor")
            fr.scale = (0.03, 0.42, 0.98)
            L.assign(fr, doorm)
            for dy in (-0.45, 0.45):
                jb = L.prim("cube", loc=(sx * (w / 2 - 0.03), y + dy, h - 1.0), name="cjamb")
                jb.scale = (0.04, 0.04, 1.0)
                L.assign(jb, steel)
    top = L.prim("cube", loc=(0, length / 2, h + 0.04), name="cdeck")
    top.scale = (w / 2 + 0.1, length / 2 + 0.5, 0.04)
    L.assign(top, deckm)
    bot = L.prim("cube", loc=(0, length / 2, -0.04), name="cceil")
    bot.scale = (w / 2 + 0.1, length / 2 + 0.5, 0.04)
    L.assign(bot, steel)
    for y in (1.0, 4.0, 7.0):  # dead lamps now on the bottom
        lp = L.prim("cube", loc=(0, y, 0.04), name="deadlamp")
        lp.scale = (0.25, 0.08, 0.03)
        L.assign(lp, L.mat_principled("dlm", (0.5, 0.55, 0.5), rough=0.2))
    # end wall with a doorway that glints: an air surface lit beyond
    for sx in (-1, 1):
        e = L.prim("cube", loc=(sx * (w / 2 - 0.2), length, h / 2), name="endwall")
        e.scale = (0.22, 0.05, h / 2)
        L.assign(e, steel)
    lint = L.prim("cube", loc=(0, length, 0.35), name="endsill")  # (inverted: sill near the old ceiling)
    lint.scale = (w / 2, 0.05, 0.35)
    L.assign(lint, steel)
    beyond = L.prim("cube", loc=(0, length + 1.5, h / 2), name="beyond")
    beyond.scale = (1.6, 0.05, h / 2 + 0.3)
    L.assign(beyond, steel)
    L.point((0, length + 0.9, wl + 0.25), energy=25, color=WARM, radius=0.3, name="pocketglow")
    L.area((0, length + 0.8, wl + 0.02), (PI, 0, 0), energy=20, size=1.2, color=WARM, name="pocketbounce")
    # water
    L.water_volume(center=(0, length / 2 + 1, wl / 2), size=(w + 0.4, length + 4, wl), color=(0.25, 0.6, 0.55), density=0.3,
                   anisotropy=0.6, absorption=(0.02, 0.12, 0.12), name="cwater")
    sm = S.mat_water_surface("csurf", color=(0.01, 0.04, 0.045), rough=0.02, alpha=0.9, under_color=(0.2, 0.45, 0.42),
                             under_strength=0.12, ripple=0.05, nframes=n)
    S.wavy_plane(size=(w + 0.2, length + 3.5), nframes=n, loc=(0, length / 2 + 1, wl), amp=0.01, mat=sm, name="csurface")
    L.particle_cloud((0, length / 2, wl / 2), (w, length, wl), count=900, radius=0.006, nframes=n, drift=(0, 0.05, 0.02),
                     name="cdebris", mat=L.mat_principled("cdm", (0.6, 0.6, 0.5), rough=1, emit=(0.4, 0.45, 0.35), emit_strength=0.15))
    # camera: head height just under the surface, slow dolly forward
    cam, tgt = L.camera(loc=(0.05, -0.6, wl - 0.25), target=(0.1, 7.5, wl - 0.15), lens=20)
    L.cam_keys(cam, [(1, (0.05, -0.6, wl - 0.25)), (n, (0.08, 1.4, wl - 0.22))], ease=False)
    L.handheld(cam, n, amp=0.02, rate=0.6)
    # the hand on the right wall pipe, intermittent torch in the other hand
    hd = S.hand("ohand", color=(0.07, 0.07, 0.075), scale=1.3)
    hr = hd["root"]
    hr.parent = cam
    hr.location = (0.17, -0.12, -0.32)
    hr.rotation_euler = (-1.35, 0.0, -0.25)
    S.curl(hd, 1, 0.5)
    for f in range(1, n + 1, 6):
        hr.location = (0.17 + 0.012 * math.sin(f * 0.3), -0.12, -0.32 + 0.02 * math.sin(f * 0.15))
        hr.keyframe_insert("location", frame=f)
    L.point((0.12, -0.05, -0.15), energy=2.5, color=(1, 0.85, 0.65), radius=0.05, name="handkey").parent = cam
    torch = L.spot((-0.15, -0.15, 0), (0.05, -0.05, 0), energy=260, size_deg=26, blend=0.5, color=(1, 0.85, 0.65), name="ctorch")
    torch.parent = cam
    L.flicker(torch, n, base=260, seed=8, depth=0.6, rate=0.5, blackouts=((14, 17), (33, 35)))
    L.cam_light(cam, energy=6, color=(0.5, 0.8, 0.85))
    L.bake_static()


# ----------------------------------------------------------------------------- S06 cutaway diagram

def S06(L, n):
    L.set_world(color=(0, 0, 0), strength=0)
    def plane(name, x0, x1, z0, z1, y, col, s=1.0, alpha=None):
        o = L.prim("plane", loc=((x0 + x1) / 2, y, (z0 + z1) / 2), rot=(PI / 2, 0, 0), size=1, name=name)
        o.scale = (x1 - x0, z1 - z0, 1)
        if alpha is None:
            L.assign(o, S.flat_mat(name + "_m", col, s))
        else:
            m = S.mat_beam(name + "_m", col, s, alpha=alpha)
            L.assign(o, L.mat_emission(name + "_m", col, s))
        return o

    def line(name, pts, col=(0.75, 0.8, 0.8), wd=0.035, s=1.5, y=-0.3):
        cu = bpy.data.curves.new(name, "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = wd
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for i, (x, z) in enumerate(pts):
            sp.points[i].co = (x, y, z, 1)
        o = L.link(bpy.data.objects.new(name, cu))
        o.data.materials.append(L.mat_emission(name + "_m", col, s))
        return o

    w, h, wl = 2.4, 2.4, WATER
    plane("bg", -8, 8, -8, 8, 0.6, (0.004, 0.02, 0.03), 1)
    # grid lines (blueprint feel)
    for k in range(-8, 9):
        line(f"gx{k}", [(k * 0.6, -6), (k * 0.6, 6)], col=(0.05, 0.15, 0.18), wd=0.006, s=1, y=0.5)
        line(f"gz{k}", [(-6, k * 0.6), (6, k * 0.6)], col=(0.05, 0.15, 0.18), wd=0.006, s=1, y=0.5)
    # inverted hull section: keel at top, deck at bottom; flooded interior
    hb, kz, dz = 3.6, 3.7, -0.9
    sec = [(1.0, 1.0), (1.0, 0.72), (0.97, 0.45), (0.86, 0.22), (0.62, 0.07), (0.3, 0.01), (0.0, 0.0)]
    pts = [(xn * hb, kz - (kz - dz) * zn) for xn, zn in sec] + [(-xn * hb, kz - (kz - dz) * zn) for xn, zn in reversed(sec[:-1])]
    pts = pts + [pts[0]]
    line("hull", pts, col=(0.85, 0.9, 0.9), wd=0.05, s=2.0)
    bm_ = S.bmesh.new()
    vs = [bm_.verts.new((x, 0.3, z)) for x, z in pts[:-1]]
    bm_.faces.new(vs)
    hf = L.mesh_from_bm("hullfill", bm_)
    L.assign(hf, S.flat_mat("hullfill_m", (0.01, 0.09, 0.11), 1))
    # seabed + superstructure stub (crushed into silt)
    plane("seabed", -8, 8, -6, dz - 0.6, 0.2, (0.06, 0.045, 0.03), 1)
    line("bedline", [(-8, dz - 0.6), (8, dz - 0.6)], col=(0.4, 0.32, 0.2), wd=0.03)
    line("house", [(-1.4, dz), (-1.4, dz - 0.6), (1.4, dz - 0.6), (1.4, dz)], col=(0.6, 0.65, 0.65), wd=0.035)
    # compartment
    plane("water", -w / 2, w / 2, 0, wl, 0.1, (0.03, 0.3, 0.32), 1.2)
    plane("air", -w / 2, w / 2, wl, h, 0.1, (1.0, 0.78, 0.45), 1.3)
    line("room", [(-w / 2, 0), (-w / 2, h), (w / 2, h), (w / 2, 0), (-w / 2, 0)], col=(0.9, 0.95, 0.95), wd=0.045, s=2.5)
    wline = line("waterline", [(-w / 2, wl), (w / 2, wl)], col=(0.5, 1.0, 1.0), wd=0.025, s=4)
    # tiny figure (flat black silhouette) with head in the pocket
    fig = L.char_figure(name="dfig", color=(0.0, 0.0, 0.0), height=1.75)
    fig["root"].location = (-0.25, 0.0, wl - 1.52)
    fig["root"].rotation_euler = (0, 0, PI / 2)
    for tag in ("L", "R"):
        fig[f"hip{tag}"].rotation_euler = (0.5, 0, 0)
        fig[f"knee{tag}"].rotation_euler = (-1.0, 0, 0)
    fig["shoulderR"].rotation_euler = (2.5, 0, 0)
    for o in bpy.data.objects:
        if o.name.startswith("dfig") and o.type == "MESH":
            L.assign(o, S.flat_mat("figflat", (0.0, 0.0, 0.0), 0))
    # measurement bracket draws on (waterline -> overhead)
    bx = w / 2 + 0.35
    S.draw_on_curve([(bx - 0.18, -0.2, wl), (bx, -0.2, wl), (bx, -0.2, h), (bx - 0.18, -0.2, h)], 4, 22, color=(1.0, 0.85, 0.25),
                    width=0.04, strength=5, name="bracket")
    for f, s in ((1, 0.0), (6, 2.5), (16, 1.0)):
        wline.data.materials[0].node_tree.nodes["Emission"].inputs[1].default_value = s * 3
        wline.data.materials[0].node_tree.nodes["Emission"].inputs[1].keyframe_insert("default_value", frame=f)
    cam, _ = L.camera(loc=(0.4, -14, 0.25), target=(0.4, 0, 0.25), lens=50)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 8.2
    cam.data.keyframe_insert("ortho_scale", frame=1)
    cam.data.ortho_scale = 7.5
    cam.data.keyframe_insert("ortho_scale", frame=n)
    L.bake_static()


# ----------------------------------------------------------------------------- S07 waterline close-up

def S07(L, n):
    o = okene_set(L, n, ripple=0.006, debris=300, flashlight=True, arm_up=False, fig_loc=(0.1, 0.25, 0.0), fig_rot=1.45,
                  pocket_light=22)
    fig = o["fig"]
    head = fig["head"]
    # breath vapour: soft spheres puffing from the mouth side
    vm = L.mat_principled("vap", (0.8, 0.8, 0.78), rough=1.0, emit=(0.6, 0.55, 0.5), emit_strength=0.3, alpha=0.18)
    vm.surface_render_method = "BLENDED"
    hx = fig["root"].location
    mouth = Vector((hx.x - 0.12, hx.y + 0.02, WATER + 0.17))
    for k in range(5):
        p = L.prim("sphere", loc=mouth, segments=12, ring_count=8, radius=0.05, name=f"vap{k}")
        L.assign(p, vm)
        f0 = 4 + k * 11
        p.scale = (0.01,) * 3
        p.keyframe_insert("scale", frame=f0)
        p.keyframe_insert("location", frame=f0)
        p.scale = (1.6, 1.0, 1.0)
        p.location = mouth + Vector((-0.12, -0.05, 0.06))
        p.keyframe_insert("scale", frame=f0 + 14)
        p.keyframe_insert("location", frame=f0 + 14)
        p.scale = (0.01,) * 3
        p.keyframe_insert("scale", frame=f0 + 22)
    S.ripple_rings((hx.x, hx.y, WATER + 0.004), n, count=3, every=14, max_r=0.55, name="neckring")
    # sickly shift of the pocket light as CO2 rises
    b = o["bounce"].data
    for f, c in ((1, WARM), (n, (0.95, 0.6, 0.45))):
        b.color = c
        b.keyframe_insert("color", frame=f)
    tgt = (hx.x - 0.05, hx.y, WATER - 0.06)
    cam, _ = L.camera(loc=(hx.x - 0.35, hx.y - 1.25, WATER + 0.02), target=tgt, lens=50)
    L.cam_keys(cam, [(1, (hx.x - 0.45, hx.y - 1.3, WATER + 0.03)), (n, (hx.x - 0.25, hx.y - 1.15, WATER + 0.01))])
    L.handheld(cam, n, amp=0.006, rate=0.5)
    L.dof(cam, distance=1.25, fstop=2.0)
    L.cam_light(cam, energy=5, color=(0.5, 0.85, 0.9), size_deg=60)
    L.bake_static()


# ----------------------------------------------------------------------------- S08 the dark wreck

def S08(L, n):
    tug, P = wreck_scene(L, n, vol_density=0.06, ambient=0.08)
    L.particle_cloud((0, 0, 7), (34, 34, 16), count=1800, radius=0.02, nframes=n, drift=(0.05, 0, -0.12), name="snow",
                     mat=L.mat_principled("snowm", (0.8, 0.85, 0.8), rough=1, emit=(0.4, 0.5, 0.5), emit_strength=0.3))
    L.fish_school((-2, -4, 9), count=35, radius=3.0, nframes=n, seed=5, color=(0.4, 0.5, 0.55), orbit_speed=0.25, size=0.15)
    L.sun(rot=(0.15, 0.05, 0.3), energy=0.5, color=(0.4, 0.7, 0.85), angle=10)
    cam, _ = L.camera(loc=(-11, -14, 7.5), target=(0, 0, 6.0), lens=24)
    L.cam_keys(cam, [(1, (-10.0, -12.8, 6.8)), (n, (-11.4, -14.6, 7.4))], ease=False)
    L.handheld(cam, n, amp=0.03, rate=0.3)
    L.cam_light(cam, energy=40, color=(0.45, 0.7, 0.9), size_deg=70)
    _hull_fill(L, 0.6)
    L.bake_static()


# ----------------------------------------------------------------------------- S09 divers descend

def S09(L, n):
    tug, P = wreck_scene(L, n, vol_density=0.05, ambient=0.1)
    tug.location = (0, 0, 5.65)
    # down-line from the surface to the hull
    S_line = L.guideline([(1.2, -1.0, 40), (1.0, -0.6, 9.0)], thickness=0.015, name="downline")
    divers = []
    for i, (col, off, z0) in enumerate((((0.95, 0.75, 0.05), (0.55, -0.9), 18.0), ((0.92, 0.92, 0.9), (1.6, -0.2), 19.6))):
        dv = S.rescue_diver(f"rd{i}", helmet=col, light_energy=1800)
        r = dv["root"]
        r.rotation_euler = (PI / 2 - 0.5, 0.1 * (1 - 2 * i), 0.4 * i)
        dv["torch"].rotation_euler = (-PI / 2 + 0.25, 0, 0)
        dv["torch"].location = (0.15, 0.62, 0.2)
        L.cam_keys(r, [(1, (off[0], off[1], z0)), (n, (off[0], off[1], z0 - 1.6))], ease=False)
        L.anim_swim(dv, n, kick_rate=0.6, amp=0.2)
        bs = L.bubbles_stream((off[0], off[1], z0 + 0.5), count=25, nframes=n, rise=3.0, spread=0.15, seed=40 + i,
                              name=f"rdb{i}", size=0.04)
        S.beam_cone((0, 0, 0), (0, 0, 1), length=9, radius=1.6, color=(0.8, 0.92, 1.0), strength=1.4, alpha=0.18,
                    name=f"rdbeam{i}", parent=dv["torch"]).rotation_euler = (PI, 0, 0)
        divers.append(dv)
    L.particle_cloud((1, -0.5, 14), (10, 10, 12), count=1200, radius=0.015, nframes=n, drift=(0, 0, 0.05), name="plank")
    L.sun(rot=(0.1, 0.05, 0.3), energy=0.8, color=(0.4, 0.7, 0.85), angle=10)
    cam, _ = L.camera(loc=(4.0, -5.5, 22.5), target=(0.9, -0.3, 12.5), lens=28)
    L.cam_keys(cam, [(1, (4.0, -5.5, 22.5)), (n, (3.9, -5.3, 21.2))], ease=False)
    L.handheld(cam, n, amp=0.03, rate=0.4)
    L.cam_light(cam, energy=40, color=(0.5, 0.8, 0.9))
    _hull_fill(L, 0.5)
    L.bake_static()


# ----------------------------------------------------------------------------- S10 along the hull

def S10(L, n):
    tug, P = wreck_scene(L, n, vol_density=0.055, ambient=0.08)
    tug.rotation_euler = (0, PI, 0.0)
    dv = S.rescue_diver("rdA", helmet=(0.95, 0.75, 0.05), light_energy=2500)
    r = dv["root"]
    y0, y1 = -5.5, 1.0
    z = 2.3
    L.path_follow(r, [(4.1, y0, z), (4.0, (y0 + y1) / 2, z + 0.1), (4.1, y1, z)], 1, n, ease=False)
    L.anim_swim(dv, n, kick_rate=0.9, amp=0.3)
    # torch sweeps toward the hull side / portholes
    t = dv["torch"]
    for f, rz, rx in ((1, 0.9, PI / 2 - 0.1), (n * 0.45, 0.4, PI / 2 + 0.15), (n, 1.1, PI / 2 - 0.05)):
        t.rotation_euler = (rx, 0, rz)
        t.keyframe_insert("rotation_euler", frame=int(f))
    beam = S.beam_cone((0, 0, 0), (0, 0, 1), length=6, radius=1.2, color=(0.85, 0.93, 1.0), strength=1.3, alpha=0.2,
                       name="rdAbeam", parent=t)
    beam.rotation_euler = (PI, 0, 0)
    bs = L.bubbles_stream((0, 0, 0), count=30, nframes=n, rise=2.5, spread=0.15, seed=51, name="rdAb", size=0.04)
    car = bpy.data.objects.new("bcar", None)
    bpy.context.scene.collection.objects.link(car)
    L.path_follow(car, [(4.1, y0 + 0.4, z + 0.3), (4.1, y1 + 0.4, z + 0.4)], 1, n, ease=False, look=False)
    for b in bs:
        b.parent = car
    kick = L.particle_cloud((4.3, (y0 + y1) / 2 - 1.5, 0.5), (2.5, 7, 1.0), count=900, radius=0.025, nframes=n,
                            drift=(0, 0.2, 0.25), name="kicksilt",
                            mat=L.mat_principled("ksm", (0.35, 0.33, 0.25), rough=1, emit=(0.2, 0.2, 0.15), emit_strength=0.15))
    cam, _ = L.camera(loc=(8.8, y0 - 0.5, 2.6), target=r, lens=24)
    L.cam_keys(cam, [(1, (8.8, y0 - 1.2, 2.8)), (n, (8.8, y1 - 1.0, 2.7))], ease=False)
    L.handheld(cam, n, amp=0.03, rate=0.4)
    L.cam_light(cam, energy=30, color=(0.5, 0.8, 0.9))
    _hull_fill(L, 0.5)
    L.bake_static()


# ----------------------------------------------------------------------------- helmet cam set (S11/S12)

def helmetcam_set(L, n):
    S.setup()
    L.set_world(color=(0.003, 0.008, 0.008), strength=1)
    w, d, h = ROOM
    wl = 1.75  # camera is in the flooded part; the air pocket is above, out of frame top
    P = S.inverted_compartment(w=w + 0.6, d=d + 0.6, h=h, water=wl, nframes=n, water_density=0.5,
                               water_col=(0.3, 0.38, 0.32), ripple_amp=0.008, rust=0.8, wall_col=(0.4, 0.42, 0.38),
                               open_front=False)
    L.particle_cloud((0, -0.2, wl / 2), (w, d, wl), count=1500, radius=0.006, nframes=n, drift=(0.02, 0.02, 0.01),
                     name="backscatter", mat=L.mat_principled("bsm", (0.8, 0.8, 0.75), rough=1, emit=(0.6, 0.6, 0.55), emit_strength=0.5))
    return P, wl


def _helmet_cam(L, n, loc0, loc1, tgt, lens=18):
    cam, _ = L.camera(loc=loc0, target=tgt, lens=lens)
    L.cam_keys(cam, [(1, loc0), (n, loc1)])
    L.handheld(cam, n, amp=0.03, rate=0.9, rot_amp=0.02)
    torch = L.spot((0.12, 0.1, 0), (0, 0, 0), energy=400, size_deg=34, blend=0.35, color=(0.85, 0.95, 0.9), name="htorch")
    torch.parent = cam
    S.scanlines(cam, lens=lens, strength=0.35)
    tc = L.text3d("REC  00:47:12", loc=(-0.032, 0.058, -0.12), rot=(0, 0, 0), size=0.0055, mat=L.mat_emission("tcm", (0.9, 0.95, 0.9), 2),
                  align="LEFT", name="timecode")
    tc.parent = cam
    dot = L.prim("sphere", loc=(-0.036, 0.0605, -0.12), segments=8, ring_count=6, radius=0.0018, name="recdot")
    L.assign(dot, L.mat_emission("recm", (1, 0.1, 0.05), 6))
    dot.parent = cam
    return cam, torch


def S11(L, n):
    P, wl = helmetcam_set(L, n)
    cam, torch = _helmet_cam(L, n, (0.6, -1.0, 0.9), (0.55, -0.85, 0.95), tgt=(0.0, 0.5, 1.2))
    # torch sweeps by panning the target
    tgt = cam.constraints[0].target
    for f, p in ((1, (0.9, 0.9, 0.7)), (n * 0.55, (-0.1, 0.6, 1.25)), (n, (-0.25, 0.55, 1.35))):
        tgt.location = p
        tgt.keyframe_insert("location", frame=int(f))
    hd = S.hand("okhand", color=(0.07, 0.065, 0.06), scale=1.6)
    r = hd["root"]
    r.rotation_euler = (-(PI / 2 + 0.3), 0, 0.2)  # fingers pointing down from the air pocket
    for f, p in ((1, (-0.55, 0.65, 1.95)), (n * 0.5, (-0.4, 0.62, 1.62)), (n, (-0.32, 0.6, 1.5))):
        r.location = p
        r.keyframe_insert("location", frame=int(f))
    S.curl(hd, 1, 0.25)
    S.curl(hd, n, 0.15)
    L.bake_static()


def S12(L, n):
    P, wl = helmetcam_set(L, n)
    cam, torch = _helmet_cam(L, n, (0.4, -0.9, 1.05), (0.12, -0.2, 1.28), tgt=(-0.3, 0.6, 1.45), lens=18)
    hd = S.hand("okhand", color=(0.07, 0.065, 0.06), scale=1.6)
    r = hd["root"]
    r.rotation_euler = (-(PI / 2 + 0.3), 0, 0.2)
    r.location = (-0.32, 0.6, 1.5)
    S.curl(hd, 1, 0.15)
    S.curl(hd, n, 0.15)
    # diver's glove enters from lower right of frame (parented to cam), reaching toward the still hand
    gl = S.hand("glove", color=(0.02, 0.02, 0.025), scale=1.9, glove=True)
    g = gl["root"]
    g.parent = cam
    for f, p in ((1, (0.22, -0.22, -0.35)), (n * 0.8, (0.06, -0.06, -0.42)), (n, (0.05, -0.05, -0.43))):
        g.location = p
        g.keyframe_insert("location", frame=int(f))
    g.rotation_euler = (-1.25, 0, 0.5)
    S.curl(gl, 1, 0.2)
    cuff = L.prim("cyl", loc=(0, -0.22, 0), vertices=12, radius=0.06, depth=0.08, rot=(PI / 2, 0, 0), name="cuff")
    L.assign(cuff, L.mat_principled("cuffm", (0.9, 0.55, 0.05), rough=0.5))
    cuff.parent = g
    L.bake_static()


# ----------------------------------------------------------------------------- S13 the grip

def S13(L, n):
    S.setup()
    L.set_world(color=(0.003, 0.012, 0.014), strength=1)
    L.water_volume(center=(0, 0, 0), size=(6, 6, 4), color=(0.06, 0.32, 0.3), density=0.25, anisotropy=0.6,
                   absorption=(0.02, 0.12, 0.12), name="gwater")
    grab = 22
    hd = S.hand("okhand", color=(0.08, 0.07, 0.065), scale=2.2)
    r = hd["root"]
    r.rotation_euler = (-(PI / 2 + 0.25), 0, 0.0)
    L.cam_keys(r, [(1, (0.02, 0.05, 0.42)), (grab, (0.0, 0.02, 0.2)), (n, (0.0, 0.03, 0.24))])
    gl = S.hand("glove", color=(0.02, 0.02, 0.025), scale=2.4, glove=True)
    g = gl["root"]
    g.rotation_euler = (PI / 2 - 0.25, 0, 0.3)
    L.cam_keys(g, [(1, (0.06, 0.0, -0.3)), (grab, (0.03, 0.0, -0.06)), (n, (0.03, 0.01, -0.03))])
    cuff = L.prim("cyl", loc=(0, -0.22, 0), vertices=12, radius=0.06, depth=0.08, rot=(PI / 2, 0, 0), name="cuff")
    L.assign(cuff, L.mat_principled("cuffm", (0.9, 0.55, 0.05), rough=0.5))
    cuff.parent = g
    S.curl(hd, 1, 0.2)
    S.curl(hd, grab - 2, 0.25)
    S.curl(hd, grab + 4, 1.15)
    S.curl(hd, n, 1.2)
    S.curl(gl, 1, 0.2)
    S.curl(gl, grab, 0.3)
    S.curl(gl, grab + 5, 1.1)
    bs = L.bubbles_stream((0.03, 0.0, 0.05), count=40, nframes=n, rise=1.5, spread=0.25, seed=61, name="gripb", size=0.025)
    # torch flare sweeping across behind the hands
    tor = L.point((0.6, 0.6, 0.0), energy=60, color=(1.0, 0.9, 0.75), radius=0.05, name="flare")
    L.cam_keys(tor, [(1, (0.8, 0.8, -0.2)), (grab, (0.15, 0.5, 0.0)), (n, (-0.6, 0.7, 0.1))])
    tor.data.energy = 30
    tor.data.keyframe_insert("energy", frame=1)
    tor.data.energy = 260
    tor.data.keyframe_insert("energy", frame=grab + 1)
    tor.data.energy = 80
    tor.data.keyframe_insert("energy", frame=n)
    disc = L.prim("sphere", loc=(0, 0, 0), segments=12, ring_count=8, radius=0.03, name="flaredisc")
    L.assign(disc, L.mat_emission("fdm", (1, 0.95, 0.85), 40))
    disc.parent = tor
    L.area((0, -0.6, 0.8), (0.9, 0, 0), energy=8, size=0.6, color=WARM, name="warmkey")
    cam, _ = L.camera(loc=(0.0, -1.1, 0.12), target=(0.02, 0.0, 0.08), lens=40)
    cam.data.lens = 40
    cam.data.keyframe_insert("lens", frame=grab - 1)
    cam.data.lens = 62
    cam.data.keyframe_insert("lens", frame=grab + 3)
    cam.data.lens = 66
    cam.data.keyframe_insert("lens", frame=n)
    cam.data.lens = 40
    L.handheld(cam, n, amp=0.01, rate=0.8)
    L.dof(cam, distance=1.1, fstop=2.8)
    L.cam_light(cam, energy=6, color=(0.5, 0.85, 0.9))
    L.bake_static()


# ----------------------------------------------------------------------------- S14 alive

def _diver_in_pocket(L, n, loc, aim, energy=700, surfacing=None):
    """Rescue diver's helmet + shoulders breaking the surface; torch lights the pocket."""
    dv = S.rescue_diver("rescuer", helmet=(0.95, 0.75, 0.05), light_energy=energy, umbilical=False)
    r = dv["root"]
    r.rotation_euler = (PI / 2 - 0.2, 0, 0)
    r.rotation_euler.z = math.atan2(-(aim[0] - loc[0]), aim[1] - loc[1])
    dv["torch"].rotation_euler = (0.25, 0, 0)  # belly-forward, slightly up
    if surfacing:
        L.cam_keys(r, [(f, p) for f, p in surfacing])
    else:
        r.location = loc
    return dv


def S14(L, n):
    o = okene_set(L, n, pocket_light=12, arm_up=False, fig_loc=(-0.25, 0.35, 0.0), fig_rot=-0.9)
    o["flash_spot"].data.energy = 40
    dv = _diver_in_pocket(L, n, (0.45, 0.1, WATER - 0.62), (-0.25, 0.35), energy=600,
                          surfacing=[(1, (0.5, 0.05, WATER - 1.0)), (int(n * 0.55), (0.48, 0.08, WATER - 0.62)),
                                     (n, (0.48, 0.08, WATER - 0.6))])
    dv["torch"].data.color = (1.0, 0.92, 0.8)
    S.ripple_rings((0.48, 0.1, WATER + 0.004), n, count=3, every=12, max_r=0.6, name="diverring", start=int(n * 0.35))
    L.point((0.3, 0.4, WATER + 0.5), energy=25, color=WARM, radius=0.2, name="torchbounce")
    tgt = (0.1, 0.25, WATER + 0.15)
    cam, _ = L.camera(loc=(-0.6, -1.9, WATER + 0.35), target=tgt, lens=24)
    L.cam_keys(cam, [(1, (-0.75, -1.85, WATER + 0.35)), (n, (0.25, -1.95, WATER + 0.3))])
    L.handheld(cam, n, amp=0.01, rate=0.5)
    L.cam_light(cam, energy=10, color=(0.5, 0.85, 0.9))
    L.bake_static()


# ----------------------------------------------------------------------------- S15/S16 physiology diagram

def _xray(L, n, swell_at=None, arrow=False):
    L.set_world(color=(0, 0, 0), strength=0)
    bg = L.prim("plane", loc=(0, 0.8, 1.0), rot=(PI / 2, 0, 0), size=1, name="bg")
    bg.scale = (14, 14, 1)
    L.assign(bg, S.flat_mat("bgm", (0.005, 0.02, 0.035), 1))
    for k in range(-10, 11):
        for horiz in (0, 1):
            cu = bpy.data.curves.new("g", "CURVE")
            cu.dimensions = "3D"
            cu.bevel_depth = 0.004
            sp = cu.splines.new("POLY")
            sp.points.add(1)
            if horiz:
                sp.points[0].co, sp.points[1].co = (-5, 0.7, 1 + k * 0.3, 1), (5, 0.7, 1 + k * 0.3, 1)
            else:
                sp.points[0].co, sp.points[1].co = (k * 0.3, 0.7, -3, 1), (k * 0.3, 0.7, 5, 1)
            o = L.link(bpy.data.objects.new("grid", cu))
            o.data.materials.append(S.flat_mat("gridm", (0.03, 0.12, 0.15), 1))
    fig = L.char_figure(name="xfig", height=1.75)
    xm = S.mat_beam("xraym", (0.35, 0.85, 1.0), 1.2, alpha=0.9)
    for o in bpy.data.objects:
        if o.name.startswith("xfig") and o.type == "MESH":
            L.assign(o, xm)
    fig["root"].rotation_euler = (0, 0, PI)
    fig["root"].location = (-0.25, 0, 0)
    for tag, s in (("L", 1), ("R", -1)):
        fig[f"shoulder{tag}"].rotation_euler = (0, 0, s * -0.18)
        fig[f"hip{tag}"].rotation_euler = (0, 0, s * -0.05)
    # gas dots sampled inside the body
    rnd = random.Random(7)
    capsules = [((-0.25, 0, 1.27), (0.15, 0.08, 0.28), 60), ((-0.25, 0, 1.73), (0.07, 0.07, 0.08), 8),
                ((-0.35, 0, 0.55), (0.05, 0.05, 0.4), 16), ((-0.15, 0, 0.55), (0.05, 0.05, 0.4), 16),
                ((-0.5, 0, 1.2), (0.03, 0.03, 0.3), 10), ((0.0, 0, 1.2), (0.03, 0.03, 0.3), 10)]
    dm = L.mat_emission("dotm", (1.0, 0.85, 0.3), 6)
    dots = []
    for c, r, cnt in capsules:
        for i in range(cnt):
            while True:
                v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
                if v.length <= 1:
                    break
            p = Vector(c) + Vector((v.x * r[0], v.y * r[1] - 0.15, v.z * r[2]))
            d = L.prim("ico", loc=p, subdivisions=1, radius=0.018, name="dot")
            L.assign(d, dm)
            dots.append(d)
    return fig, dots


def S15(L, n):
    fig, dots = _xray(L, n)
    rnd = random.Random(3)
    for d in dots:
        f0 = rnd.randint(2, int(n * 0.85))
        d.scale = (0.01,) * 3
        d.keyframe_insert("scale", frame=f0)
        d.scale = (1.3,) * 3
        d.keyframe_insert("scale", frame=f0 + 3)
        d.scale = (1,) * 3
        d.keyframe_insert("scale", frame=f0 + 6)
    cam, _ = L.camera(loc=(-0.05, -9, 1.05), target=(-0.05, 0, 1.05), lens=50)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 3.6
    cam.data.keyframe_insert("ortho_scale", frame=1)
    cam.data.ortho_scale = 3.3
    cam.data.keyframe_insert("ortho_scale", frame=n)
    L.bake_static()


def S16(L, n):
    fig, dots = _xray(L, n)
    rnd = random.Random(3)
    swell = int(n * 0.3)
    for d in dots:
        d.scale = (1,) * 3
        d.keyframe_insert("scale", frame=1)
        d.keyframe_insert("scale", frame=swell)
        s = rnd.uniform(1.8, 3.0)
        d.scale = (s,) * 3
        d.keyframe_insert("scale", frame=swell + 12)
    rm = L.mat_emission("redm", (1.0, 0.15, 0.1), 6)
    # arrow shoots up from the chest
    S.draw_on_curve([(0.55, -0.3, 0.3), (0.55, -0.3, 2.0)], 2, 14, color=(1.0, 0.85, 0.3), width=0.05, strength=6, name="arrow")
    head = L.prim("cone", loc=(0.55, -0.3, 2.08), vertices=12, radius1=0.14, radius2=0.0, depth=0.24, name="arrowhead")
    L.assign(head, L.mat_emission("ahm", (1.0, 0.85, 0.3), 6))
    head.scale = (0.01,) * 3
    head.keyframe_insert("scale", frame=13)
    head.scale = (1,) * 3
    head.keyframe_insert("scale", frame=15)
    xs = int(n * 0.55)
    for a in (0.75, -0.75):
        bar = L.prim("cube", loc=(0.55, -0.4, 1.2), name="xbar")
        bar.scale = (0.06, 0.02, 0.6)
        bar.rotation_euler = (0, a, 0)
        L.assign(bar, rm)
        sc = bar.scale.copy()
        bar.scale = (0.01, 0.01, 0.01)
        bar.keyframe_insert("scale", frame=xs - 1)
        bar.scale = (sc.x * 1.6, sc.y, sc.z * 1.6)
        bar.keyframe_insert("scale", frame=xs + 2)
        bar.scale = sc
        bar.keyframe_insert("scale", frame=xs + 5)
    cam, _ = L.camera(loc=(0.05, -9, 1.15), target=(0.05, 0, 1.15), lens=50)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 3.5
    # quick shake on the X
    for f in range(1, n + 1):
        k = max(0.0, 1 - abs(f - xs - 2) / 6) if f >= xs else 0
        cam.location = (0.05 + 0.03 * k * math.sin(f * 3.1), -9, 1.15 + 0.03 * k * math.cos(f * 2.3))
        cam.keyframe_insert("location", frame=f)
    L.bake_static()


# ----------------------------------------------------------------------------- S17 chamber on deck

def S17(L, n):
    S.setup(vol_end=60)
    L.set_world(color=(0.005, 0.008, 0.015), strength=1)
    S.world_volume(color=(0.6, 0.6, 0.65), density=0.012, anisotropy=0.4)
    deck = L.prim("plane", loc=(0, 0, 0), size=40, name="deck")
    L.assign(deck, S.mat_paint("deckm", (0.12, 0.14, 0.12), rough=0.35, grime=0.5, rust=0.3, scale=1.2))
    ch = S.decompression_chamber(loc=(0, 1.2, 0), length=3.4, radius=0.85)
    # railing + bulkhead behind
    bh = L.prim("cube", loc=(0, 4.0, 2.0), name="bulkhead")
    bh.scale = (8, 0.1, 2.0)
    L.assign(bh, S.mat_paint("bhm", (0.55, 0.57, 0.55), rough=0.5, grime=0.5, rust=0.3))
    for x in range(-6, 7, 2):
        p = L.prim("cyl", loc=(x, -3.5, 0.55), vertices=8, radius=0.03, depth=1.1, name="rail")
        L.assign(p, L.mat_principled("railm", (0.8, 0.75, 0.2), rough=0.4))
    rl = L.prim("cyl", loc=(0, -3.5, 1.1), vertices=8, radius=0.035, depth=14, rot=(0, PI / 2, 0), name="railtop")
    L.assign(rl, L.mat_principled("railm2", (0.8, 0.75, 0.2), rough=0.4))
    # hatch on the +X end swings shut (find hatch + wheel + spokes and hinge them)
    hx = 3.4 / 2 + 0.85 * 0.45
    hinge = bpy.data.objects.new("hhinge", None)
    bpy.context.scene.collection.objects.link(hinge)
    hinge.parent = ch
    hinge.location = (hx, -0.5, 0.85 + 0.35)
    for o in list(ch.children):
        if any(k in o.name for k in ("hatch", "wheel", "spoke")):
            o.parent = hinge
            o.location = (o.location.x - hx, o.location.y + 0.5, o.location.z - 1.2)
    for f, a in ((1, -1.4), (int(n * 0.25), -1.3), (int(n * 0.65), -0.05), (n, 0.0)):
        hinge.rotation_euler = (0, 0, a)
        hinge.keyframe_insert("rotation_euler", frame=f)
    # two helmeted crew silhouettes at the hatch
    for i, (x, y, rz) in enumerate(((hx + 0.9, -0.9, 2.2), (hx + 0.45, 0.6, 2.9))):
        fg = L.char_figure(name=f"crew{i}", color=(0.03, 0.03, 0.035), height=1.8)
        fg["root"].location = (x, y, 0)
        fg["root"].rotation_euler = (0, 0, rz)
        hat = L.prim("sphere", loc=(0, 0, 0.17), segments=16, ring_count=8, radius=0.13, name=f"hat{i}")
        hat.scale = (1, 1.1, 0.7)
        L.assign(hat, L.mat_principled(f"hatm{i}", (0.95, 0.95, 0.92) if i else (0.95, 0.6, 0.05), rough=0.35))
        hat.parent = fg["neck"]
        _pose(fg, 1, shoulderR=(1.4, 0, 0), elbowR=(0.3, 0, 0))
        _pose(fg, int(n * 0.65), shoulderR=(1.2, 0, 0), elbowR=(0.6, 0, 0))
        _pose(fg, n, shoulderR=(1.25, 0, 0), elbowR=(0.5, 0, 0))
    # sodium floodlights
    for x, z in ((-4, 5.0), (5, 5.5)):
        fl = L.spot((x, -1.5, z), (0, 0, 0), energy=1800, size_deg=70, blend=0.6, color=(1.0, 0.55, 0.2), name="flood")
        fl.rotation_euler = (Vector((0.5, 1.2, 0.5)) - Vector((x, -1.5, z))).to_track_quat("-Z", "Y").to_euler()
        lamp = L.prim("cube", loc=(x, -1.5, z), name="floodlamp")
        lamp.scale = (0.25, 0.1, 0.15)
        L.assign(lamp, L.mat_emission("floodm", (1.0, 0.6, 0.25), 20))
    # steam from a vent + light rain
    L.particle_cloud((-1.9, 1.2, 2.2), (0.4, 0.4, 1.6), count=500, radius=0.04, nframes=n, drift=(0.1, 0, 0.6), name="steam",
                     mat=L.mat_principled("stm", (0.8, 0.8, 0.8), rough=1, emit=(0.5, 0.45, 0.4), emit_strength=0.3))
    vent = L.prim("cyl", loc=(-1.9, 1.2, 1.9), vertices=10, radius=0.06, depth=0.3, name="vent")
    L.assign(vent, L.mat_principled("ventm", (0.3, 0.3, 0.3), metal=1, rough=0.3))
    rain = L.particle_cloud((0, 0, 2.5), (14, 14, 1.0), count=1000, radius=0.008, nframes=n, drift=(0.2, 0, -2.0), name="rain",
                            mat=L.mat_principled("rainm", (0.8, 0.8, 0.9), rough=0.3, emit=(0.6, 0.5, 0.4), emit_strength=0.5))
    rain.scale = (1, 1, 5)
    cam, tg = L.camera(loc=(4.6, -3.8, 0.6), target=(1.7, 0.5, 1.3), lens=28)
    L.cam_keys(cam, [(1, (4.6, -3.8, 0.6)), (n, (2.6, -2.5, 1.0))])
    L.cam_keys(tg, [(1, (1.7, 0.5, 1.3)), (n, (0.5, 0.4, 1.4))])
    L.handheld(cam, n, amp=0.015, rate=0.5)
    L.cam_light(cam, energy=40, color=(0.6, 0.7, 0.9))
    L.bake_static()


# ----------------------------------------------------------------------------- S18 timeline background

def S18(L, n):
    o = okene_set(L, n, debris=400, pocket_light=18, drips=False)
    cam, _ = L.camera(loc=(-0.6, -1.9, 1.5), target=(0.2, 0.4, 1.4), lens=30)
    L.cam_keys(cam, [(1, (-0.7, -1.9, 1.5)), (n, (0.5, -1.9, 1.45))], ease=False)
    L.dof(cam, distance=0.6, fstop=0.8)
    L.cam_light(cam, energy=10, color=(0.5, 0.85, 0.9))
    L.bake_static()


# ----------------------------------------------------------------------------- S19 found

def S19(L, n):
    o = okene_set(L, n, pocket_light=14, arm_up=False, fig_loc=(-0.1, 0.4, 0.0), fig_rot=0.2)
    o["flash_spot"].data.energy = 40
    dv = _diver_in_pocket(L, n, (0.65, -0.3, WATER - 0.62), (-0.1, 0.4), energy=500)
    # torch beam settles onto the figure
    t = dv["torch"]
    for f, rx, ry in ((1, 0.6, 0.45), (int(n * 0.5), 0.3, 0.05), (n, 0.25, 0.0)):
        t.rotation_euler = (rx, ry, 0)
        t.keyframe_insert("rotation_euler", frame=f)
    L.point((0.0, 0.3, WATER + 0.55), energy=18, color=WARM, radius=0.2, name="torchbounce")
    cam, _ = L.camera(loc=(-0.2, -1.6, WATER + 0.45), target=(-0.05, 0.35, WATER + 0.2), lens=35)
    L.cam_keys(cam, [(1, (-0.2, -1.6, WATER + 0.45)), (n, (-0.18, -1.5, WATER + 0.44))])
    L.handheld(cam, n, amp=0.006, rate=0.5)
    L.cam_light(cam, energy=8, color=(0.5, 0.85, 0.9))
    L.bake_static()


# ----------------------------------------------------------------------------- S20 loop back to S01

def S20(L, n):
    o = okene_set(L, n)
    # rescue diver's torch pushing in from below the waterline (front-left, deep)
    dv = S.rescue_diver("rescuer", helmet=(0.95, 0.75, 0.05), light_energy=500, umbilical=False)
    r = dv["root"]
    r.rotation_euler = (0.55, 0, -0.35)
    L.cam_keys(r, [(1, (-0.9, -1.6, 0.15)), (n, (-0.55, -0.95, 0.35))])
    L.anim_swim(dv, n, kick_rate=0.7, amp=0.25)
    dv["torch"].rotation_euler = (PI / 2 + 0.35, 0, 0)
    S.beam_cone((0, 0, 0), (0, 0, 1), length=2.5, radius=0.6, color=(0.85, 0.95, 1.0), strength=1.4, alpha=0.25,
                name="s20beam", parent=dv["torch"]).rotation_euler = (PI, 0, 0)
    L.bubbles_stream((-0.7, -1.2, 0.5), count=30, nframes=n, rise=0.8, spread=0.1, seed=71, name="s20b", size=0.025)
    pre = (CAM01_A[0] + 0.03, CAM01_A[1] - 0.55, CAM01_A[2] + 0.05)
    cam, _ = L.camera(loc=pre, target=CAM01_T, lens=24)
    L.cam_keys(cam, [(1, pre), (n, CAM01_A)], ease=False)
    L.cam_light(cam, energy=18, color=(0.5, 0.85, 0.9), size_deg=80)
    L.bake_static()
