"""
This example shows, in 3D,  a dish with a homogenizer, defined by its geometric
concentration, and number of reflections in the homogenizer. You can play with
both values, and each change will cause the scene to redraw.
"""

import traits.api as t_api
import traitsui.api as tui
from tvtk.pyface.scene_editor import SceneEditor
from mayavi.core.ui.mayavi_scene import MayaviScene
from mayavi import mlab
from tracer.mayavi_ui.scene_view import TracerScene
from tracer.tracer_engine import TracerEngine
from tracer.CoIn_rendering.rendering import *
import numpy as N
from tracer.sources import solar_disk_bundle
#from tracer.models.tau_minidish import standard_minidish
from tracer.models.PETAL_dish_jess_2 import PETAL
from tracer.models.PETAL_dish_jess_2 import petal_dish
from tracer import spatial_geometry as G
from tracer.assembly import Assembly
from tracer.analysis import *



class DishScene(TracerScene):
    """
    Extends TracerScene with the variables required for this example and adds
    handling of simulation-specific details, like colouring the dish elements
    and setting proper resolution.
    """
    refl = t_api.Float(0.9, label='dish_opt_efficiency')
    concent = t_api.Float(2100, label='Concentration')
    disp_num_rays = t_api.Int(5000)# why an integer
    #receiver_pos = t_api.Float(4)# a single numer on the z axis
    receiver_side=5.# the dimension of the side of a square receiver
    
    def __init__(self):
        dish, source = self.create_dish_source()
        TracerScene.__init__(self, dish, source)
        self.set_background((0., 0.5, 1.)) # this one changes color
    
    def create_dish_source(self):
        """
        Creates the two basic elements of this simulation: the parabolic dish,
        and the pillbox-sunshape ray bundle. Uses the variables set by 
        TraitsUI.
        """
	diameter=26.3
	receiver_pos=15.8
        dish, f, H = petal_dish(diameter, receiver_pos, self.receiver_side, self.refl, 1.)
	print(f,'f')
	#receiver=TwoNparamcav([0.22], [0.75], [0.2], 1., 0.04, 0.9, 0.2, 0.6, 0.23, None, False)
	#receiver_surf=Surface(receiver, opt.LambertianReceiver(0.9))
	#recv = AssembledObject(surfs=[receiver_surf])
	#self._assemblies=Assembly(objects=[dish], subassemblies=[recv])
	#petal_dish(self, diameter, receiver_pos, receiver_side, dish_opt_eff,\
        #receiver_aspect=1.)
        #Add GUI annotations to the dish assembly:
        #for surf in dish.get_homogenizer().get_surfaces():

	for surf in dish.get_surfaces():
            surf.colour = (1., 0., 0.)
        dish.get_main_reflector().colour = (0., 0., 1.)
	theta=0.
    	alpha=0.04#print(self.receiver_pos)
	x=-N.cos(theta)*N.sin(alpha)
	y=-N.sin(theta)*N.sin(alpha)
	z=-N.cos(alpha)
	# the transformation matrix needs to be a 4*4 rotational matric
        source = solar_disk_bundle(self.disp_num_rays, N.c_[[0., 0., f + H ]], N.r_[x,y,z], diameter/2, 0.00467)
#solar_disk_bundle(num_rays,  center,  direction,  radius, ang_range, flux=None, radius_in=0., angular_span=[0.,2.*N.pi]):) N.r_ must be a unit vector
	#source = solar_disk_bundle(self.disp_num_rays, N.c_[[0., 0., f + H + 0.5]], N.r_[0., 0., -1.], 0.5, 0.197)
	# what is this 0.5 here
	#print(source,'source')
        source.set_energy(N.ones(self.disp_num_rays)*1000.*N.pi*diameter**2*0.25/float(self.disp_num_rays) )# gives intensity value which is the inverse of the number of solar arrays
        
        return dish, source

    @t_api.on_trait_change('refl, concent')
    def recreate_dish(self):
        """
        Makes sure that the scene is redrawn upon dish design changes.
        """
        dish, source = self.create_dish_source()
        self.set_assembly(dish)
        self.set_source(source)
    
    # Parameters of the form that is shown to the user:
    view = tui.View(
        tui.Item('_scene', editor=SceneEditor(scene_class=MayaviScene),
            height=500, width=500, show_label=True),
        tui.HGroup('-', 
            tui.Item('concent', editor=tui.TextEditor(evaluate=float, auto_set=True)), 
            tui.Item('refl', editor=tui.TextEditor(evaluate=float, auto_set=True))))

scene = DishScene()
engine=TracerEngine(scene._asm)

engine.ray_tracer(scene._source, 10, 1e-9, True )
#engine.ray_tracer(scene._source, 10, 1e-9, True )
source=engine.tree._bunds[0].get_energy()
reflect_1=engine.tree._bunds[1].get_energy()
receive_1=engine.tree._bunds[2].get_energy()
reflect_2=engine.tree._bunds[3].get_energy()
receive_2=engine.tree._bunds[4].get_energy()
reflect_3=engine.tree._bunds[5].get_energy()
receive_3=engine.tree._bunds[6].get_energy()

print(engine.tree._bunds[0].get_energy(),'tree',len(engine.tree._bunds[0].get_energy()))
print(engine.tree._bunds[1].get_energy(),'tree',len(engine.tree._bunds[1].get_energy()))
print(engine.tree._bunds[2].get_energy(),'tree',len(engine.tree._bunds[2].get_energy()))
print(engine.tree._bunds[3].get_energy(),'tree',len(engine.tree._bunds[3].get_energy()))
print(engine.tree._bunds[4].get_energy(),'tree',len(engine.tree._bunds[4].get_energy()))
print(engine.tree._bunds[5].get_energy(),'tree',len(engine.tree._bunds[5].get_energy()))
print(engine.tree._bunds[6].get_energy(),'tree',len(engine.tree._bunds[6].get_energy()))
print(N.sum(engine.tree._bunds[2].get_energy()),'first bounce')
print(N.sum(engine.tree._bunds[4].get_energy()),'second bounce')
print(N.sum(engine.tree._bunds[6].get_energy()),'third bounce')

eff=(N.sum(engine.tree._bunds[2].get_energy())+N.sum(engine.tree._bunds[4].get_energy())+N.sum(engine.tree._bunds[6].get_energy()))*9/sum(engine.tree._bunds[1].get_energy())
#eff=(N.sum(engine.tree._bunds[2].get_energy())+N.sum(engine.tree._bunds[4].get_energy())+N.sum(engine.tree._bunds[6].get_energy()))*9/(len(engine.tree._bunds[1].get_energy())*engine.tree._bunds[1].get_energy()[0])
block=reflect_1[reflect_1==0]/len(reflect_1)
spill=(reflect_1[reflect_1!=0]-len(receive_1))/reflect_1[reflect_1!=0]
print(block,'block',spill,'spill')
print(eff,'eff') #  the demoninator includes the sum rays on the back. i.e. the blocking is accounted for

engine.minener = 1e-20
recv=scene._asm.get_local_objects()[0] #here the scene._asm is an assembly and _object[1] returns an object Now it's really the receiver
print(scene._asm.get_local_objects(),'scene_recv')
count = 0
totalenergy = 0

for face in recv.get_surfaces(): # definitely has gone through only one iteration. check .surface for definitioin
	#energy, pts = face._optics.get_all_hits()
	#that's when everything gets doubled
	print(recv.get_surfaces())
	energy, pts =face.get_optics_manager().get_all_hits() # an instance of a reflective receiver
	print(energy,len(energy),'energy')
	subtotalenergy = energy.sum() # for each surface
	#print(subtotalenergy,'subtotalenergy')
	totalenergy += subtotalenergy
	x, y = face.global_to_local(pts)[:2]
	rngx = scene.receiver_side/2 #0.5
	rngy = scene.receiver_side/2 #0.5

	bins = 100 #50 100*100
	H, xbins, ybins = N.histogram2d(x,y,bins,range=([-rngx,rngx],[-rngy,rngy]), weights=energy)
	print(N.amax(H)/(scene.receiver_side/bins)**2,'intensity')
	#print(H, xbins, ybins) # H is the total energy for each grid
	#print(N.sum(H),'sum of H')
	extent = [ybins[0], ybins[-1], xbins[-1], xbins[0]]
        plt.imshow(H, extent=extent, interpolation='nearest')
        plt.colorbar()
	if count == 0:
		plt.title("Front")
		H_front=N.sum(H)
		print(H_front,'front')
	else:
		plt.title(str(count))
		H_back=N.sum(H)
		print(H_back,'back')
        plt.show()
	count += 1


#assume 218 heliostats
#eff = totalenergy/(218*hstat_rays)
#print("Blade apsorptivity = "+str(absorp))
#print("Effective absorptivity = "+str(eff))
#engine.ray_tracer(rays=10, iters=10, minE=1e-9, tree=True )
#scene.configure_traits()
view=Renderer(engine)
#view.show_geom()
view.show_rays()


'''
engine=TracerEngine(asm)
engine.minener = 1e-20
view=Renderer(engine)
view.show_geom() to show the geometry only

        view.show_rays() to show the rays and the geometry
'''


