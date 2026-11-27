"""HAUNT-01 thumbnail hero stills (NOT part of the video; shots.py is the video source).
Purpose-built compositions for the custom Shorts thumbnail, rendered with a copy of render_shot.py pointed at this file.
THUMB_A: low, tight on the askew chair with the recorder's red REC lamp glowing behind it ("THE TAPES").
THUMB_B: the chair (with a jumper on its back) in the foreground and its person-like shadow on the wall, as in S09 ("2% FAKED?").
  The source of the shadow stays in frame on purpose: the image poses the question, it does not claim a figure."""
import importlib, sys, os, math
_LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "PIPELINE", "blender")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)
import lib_haunted as H
importlib.reload(H)


def _obj(name):
    import bpy
    return bpy.data.objects[name]


def THUMB_A(L, n):
    H.eevee_quality()
    L.set_world((0.004, 0.006, 0.012), 1.0)
    s = H.enfield_bedroom(n, chair="A", rec_on=True, dust_count=300, moon=0.9)
    # brighter REC lamp + red spill across the cabinet and chair back
    H.key_emission(s["rec"]["rec_mat"], [(1, 140.0)])
    s["rec"]["rec_light"].data.energy = 3.0
    rx, ry, rz = H.REC_POS[0]
    L.point((rx - 0.2, ry - 0.2, rz + 0.18), energy=2.0, color=(1.0, 0.06, 0.03), radius=0.03, name="recspill")
    # cold moon kick on the chair so its silhouette separates from the wall
    k = L.spot((-0.6, 0.2, 2.2), (0, 0, 0), energy=90, size_deg=35, blend=0.7, color=(0.6, 0.72, 1.0), name="chairkick", radius=0.05)
    H.aim(k, (-0.6, 0.2, 2.2), (-0.2, 1.15, 0.5))
    c = H.cam((0.32, -0.45, 0.92), (0.0, 1.4, 0.55), lens=30)
    L.dof(c, distance=1.75, fstop=5.0)
    L.cam_light(c, energy=14, color=(0.65, 0.75, 1.0), size_deg=80)
    L.bake_static()


def THUMB_B(L, n):
    H.eevee_quality()
    L.set_world((0.003, 0.004, 0.008), 1.0)
    s = H.enfield_bedroom(n, chair="A", rec_on=True, moon=0.4, jumper=True, dust_count=300)
    lp = H.bedside_lamp((-1.05, 1.35, 0.55), on=True, energy=0.0, name="lowlamp")
    lp["root"].rotation_euler = (0, math.radians(-70), 0.1)
    key = L.spot((-1.15, 1.12, 0.72), (0, 0, 0), energy=260, size_deg=56, blend=0.35, color=(1.0, 0.7, 0.4), name="lowkey", radius=0.012)
    H.aim(key, (-1.15, 1.12, 0.72), (1.65, 1.0, 0.9))
    c = H.cam((-1.2, -1.5, 1.05), (1.0, 1.65, 1.0), lens=24)
    L.cam_light(c, energy=8, color=(0.65, 0.75, 1.0), size_deg=80)
    L.bake_static()
