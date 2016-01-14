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
from tracer.models.PETAL_dish_jess import PETAL
from tracer.models.PETAL_dish_jess import petal_dish
from tracer import spatial_geometry as G
from tracer.assembly import Assembly
from tracer.analysis import *



class DishScene(TracerScene):
    """
    Extends TracerScene with the variables required for this example and adds
    handling of simulation-specific details, like colouring the dish elements
    and setting proper resolution.
    """
    refl = t_api.Float(1., label='Edge reflections')
    concent = t_api.Float(450, label='Concentration')
    disp_num_rays = t_api.Int(2000)# why an integer
    receiver_pos = t_api.Float(1)# a single numer on the z axis
    receiver_side=t_api.Float(1)# the dimension of the side of a square receiver
    
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
        dish, f, H = petal_dish(1., self.receiver_pos, self.receiver_side, self.refl, 1.)
	print(f,'f')
	#receiver=TwoNparamcav([0.22], [0.75], [0.2], 1., 0.04, 0.9, 0.2, 0.6, 0.23, None, False)
	#receiver_surf=Surface(receiver, opt.LambertianReceiver(0.9))
	#recv = AssembledObject(surfs=[receiver_surf])
	#self._assemblies=Assembly(objects=[dish], subassemblies=[recv])
        #standard_minidish_measures(diameter, concentration, virt_sources): diameter is equal to 1
        #PPETAL_dish def __init__(self, diameter, focal_length,\
        #receiver_pos, receiver_side, homogenizer_depth, homog_opt_eff, dish_opt_eff,\
        #receiver_aspect=1.):
	#petal_dish(self, diameter, receiver_pos, receiver_side, dish_opt_eff,\
        #receiver_aspect=1.)
        #Add GUI annotations to the dish assembly:
        #for surf in dish.get_homogenizer().get_surfaces():
	for surf in dish.get_surfaces():
            surf.colour = (1., 0., 0.)
        dish.get_main_reflector().colour = (0., 0., 1.)
	theta=0.1
    	alpha=0.1#print(self.receiver_pos)
	x=-N.cos(theta)*N.sin(alpha)
	y=-N.sin(theta)*N.sin(alpha)
	z=-N.cos(alpha)
	# the transformation matrix needs to be a 4*4 rotational matric
        source = solar_disk_bundle(self.disp_num_rays, N.c_[[0., 0., f + H ]], N.r_[x,y,z], 0.5, 0.00467)
#solar_disk_bundle(num_rays,  center,  direction,  radius, ang_range, flux=None, radius_in=0., angular_span=[0.,2.*N.pi]):) N.r_ must be a unit vector
	#source = solar_disk_bundle(self.disp_num_rays, N.c_[[0., 0., f + H + 0.5]], N.r_[0., 0., -1.], 0.5, 0.197)
	# what is this 0.5 here
	#print(source,'source')
        source.set_energy(N.ones(self.disp_num_rays)*1000./float(self.disp_num_rays) )# gives intensity value which is the inverse of the number of solar arrays
        
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
#print(engine.tree._bunds[0].get_energy(),'tree')
#print(engine.tree._bunds[1].get_energy(),'tree')
#print(engine.tree._bunds[2].get_energy(),'tree')
engine.minener = 1e-20

recv=scene._asm.get_local_objects()[0] #here the scene._asm is an assembly and _object[1] returns an object
count = 0
totalenergy = 0

for face in recv.surfaces: # definitely has gone through only one iteration. check .surface for definitioin
	#energy, pts = face._optics.get_all_hits()
	#that's when everything gets doubled
	
	energy, pts =face.get_optics_manager().get_all_hits() # an instance of a reflective receiver
	#print(energy.sum())
	subtotalenergy = energy.sum() # for each surface
	#print(subtotalenergy,'subtotalenergy')
	totalenergy += subtotalenergy
	x, y = face.global_to_local(pts)[:2]
	rngx = 0.2 #0.5
	rngy = 0.2 #0.5

	bins = 100 #50
	H, xbins, ybins = N.histogram2d(x,y,bins,range=([-rngx,rngx],[-rngy,rngy]), weights=energy)
	#print(H, xbins, ybins)
	print(N.sum(H),'sum of H')
	extent = [ybins[0], ybins[-1], xbins[-1], xbins[0]]
        plt.imshow(H, extent=extent, interpolation='nearest')
        plt.colorbar()
	if count == 0:
		plt.title("Front")
	else:
		plt.title(str(count))
        #plt.show()
	count += 1
print('total energy below')
print(totalenergy)
	#assume 218 heliostats
	#eff = totalenergy/(218*hstat_rays)
	#print("Blade apsorptivity = "+str(absorp))
	#print("Effective absorptivity = "+str(eff))
#engine.ray_tracer(rays=10, iters=10, minE=1e-9, tree=True )
#scene.configure_traits()
#view=Renderer(engine)
#view.show_geom()
#view.show_rays()


'''
engine=TracerEngine(asm)
engine.minener = 1e-20
view=Renderer(engine)
view.show_geom() to show the geometry only

        view.show_rays() to show the rays and the geometry
'''


