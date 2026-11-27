def _cave(L, n):
    pts=[(0,0,0),(0,8,0.5),(2,16,-0.5),(1,24,0)]
    cave,samp=L.cave_tunnel(pts,radius=2.6,seed=4)
    L.stalactites(samp[10:60],count=20); L.boulders(samp[5:60],count=12)
    L.water_volume(center=(0,12,0),size=(30,40,20),color=(0.3,0.5,0.45),density=0.05)
    L.particle_cloud((0,8,0),(5,10,4),count=900,radius=0.008,nframes=n)
    return samp
def S01(L, n):
    _cave(L,n)
    d=L.char_diver(light_energy=1500); L.path_follow(d['root'],[(0,4,0),(0.3,7,0.2)],1,n); L.anim_swim(d,n)
    cam,_=L.camera(loc=(1.2,1.5,0.9),target=d['root'],lens=24)
    L.cam_keys(cam,[(1,(1.2,1.5,0.9)),(n,(0.8,4.0,0.7))]); L.handheld(cam,n)
def S02(L, n):
    _cave(L,n)
    d=L.char_diver(light_energy=1500); d['root'].location=(0,6,0); L.anim_swim(d,n)
    L.particle_cloud((0,6,-1),(3,3,2),count=3000,radius=0.012,nframes=n,name="siltout",drift=(0,0,0.15))
    cam,_=L.camera(loc=(0.5,3.5,0.4),target=d['root'],lens=30)
