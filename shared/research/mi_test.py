import time, sys, mitsuba as mi
print(mi.variants())
var = sys.argv[1]
mi.set_variant(var)
t=time.time()
scene = mi.load_dict({
 'type':'scene','integrator':{'type':'path','max_depth':4},
 'sensor':{'type':'perspective','fov':40,'to_world':mi.ScalarTransform4f().look_at(origin=[0,1,4],target=[0,0.5,0],up=[0,1,0]),
   'film':{'type':'hdrfilm','width':int(sys.argv[2]),'height':int(sys.argv[3])},'sampler':{'type':'independent','sample_count':int(sys.argv[4])}},
 'emitter':{'type':'constant','radiance':{'type':'rgb','value':0.4}},
 'sun':{'type':'sphere','center':[-3,5,3],'radius':1.0,'emitter':{'type':'area','radiance':{'type':'rgb','value':[8,7,6]}}},
 'floor':{'type':'rectangle','to_world':mi.ScalarTransform4f().rotate([1,0,0],-90).scale(5),'bsdf':{'type':'diffuse','reflectance':{'type':'rgb','value':[0.7,0.5,0.35]}}},
 'head':{'type':'sphere','center':[0,0.6,0],'radius':0.6,'bsdf':{'type':'principled','base_color':{'type':'rgb','value':[0.65,0.4,0.25]},'roughness':0.6,'specular':0.3}},
})
print('load',round(time.time()-t,2))
t=time.time(); img = mi.render(scene); mi.util.write_bitmap(f'mi_{var}.png', img); print('render',var,sys.argv[2:],round(time.time()-t,2))
