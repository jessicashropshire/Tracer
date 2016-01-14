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

import numpy as N
from tracer.sources_jess import solar_disk_bundle
#from tracer.models.tau_minidish import standard_minidish
from tracer.models.PETAL_dish_jess import PETAL
from tracer.models.PETAL_dish_jess import petal_dish
from tracer import spatial_geometry as G

class DishScene(TracerScene):
    """
    Extends TracerScene with the variables required for this example and adds
    handling of simulation-specific details, like colouring the dish elements
    and setting proper resolution.
    """
    refl = t_api.Float(1., label='Edge reflections')
    concent = t_api.Float(450, label='Concentration')
    disp_num_rays = t_api.Int(40)# why an integer
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
	
        #standard_minidish_measures(diameter, concentration, virt_sources): diameter is equal to 1
        # PPETAL_dish def __init__(self, diameter, focal_length,\
        #receiver_pos, receiver_side, homogenizer_depth, homog_opt_eff, dish_opt_eff,\
        #receiver_aspect=1.):
	#petal_dish(self, diameter, receiver_pos, receiver_side, dish_opt_eff,\
        #receiver_aspect=1.)
        # Add GUI annotations to the dish assembly:
        #for surf in dish.get_homogenizer().get_surfaces():
	for surf in dish.get_surfaces():
            surf.colour = (1., 0., 0.)
        dish.get_main_reflector().colour = (0., 0., 1.)
	print(self.receiver_pos)

        source = solar_disk_bundle(self.disp_num_rays,f, N.c_[[0., 0., f + H]], N.r_[0., 0., 1.], 0.5, 0.190)
#solar_disk_bundle(num_rays,  receiver_position(centre disk for the sun rays),  direction,  radius, ang_range, flux=None, radius_in=0., angular_span=[0.,2.*N.pi]) N.r_ must be a unit vector
	#source = solar_disk_bundle(self.disp_num_rays, N.c_[[0., 0., f + H + 0.5]], N.r_[0., 0., -1.], 0.5, 0.197)
	# what is this 0.5 here
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
scene.configure_traits()
v=mayavi.mayavi()
m=v.load_module(dish)
a=v.load_module(source)
v.render()
mlab.scalarbar()

