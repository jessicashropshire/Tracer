# An assembly modeling the PETAL dish, located at Sde Boker, Israel [1]
#
# References:
# [1] Biryukov, S. Determining the optical properties of PETAL, the 400 m(2)
#     parabolic dish at Sede Boqer, 2004, J. of Solar Energy Engineering.

from .. import optics_callables as opt
from ..assembly import Assembly
from ..object import AssembledObject
from ..surface import Surface
from ..paraboloid import OctagonalParabolicDishGM
import numpy as N
from .Two_N_parameters_cavity import TwoNparamcav
from tracer.models.Bladed_Receiver import test_receiver


class PETAL(TwoNparamcav):
    def __init__(self, diameter, focal_length,\
        receiver_pos, receiver_side, dish_opt_eff,\
        receiver_aspect=1.):
  # dish = PETAL(1., self.f, self.H, self.receiver_size, self.w, homog_opt_eff=0.9,dish_opt_eff=0.9, self.receiver_aspect=1)
        """
        Arguments:
        diameter - of the circle bounding the hexagonal aperture. 
        focal_length - of the parabolic dish
        dish_opt_eff - the optical efficiency of the dish
        receiver_pos - the distance along the optical axis from the dish to the
            receiver's end surface - the PV panel (should be about the focal 
            length)
        receiver_side - the receiver is square, with this side length.
        homogenizer_depth - the homogenizer has base dimensions to fit the PV
            square, and this height.
        homog_opt_eff - the optical efficiency of each mirror in the homogenizer
        receiver_aspect - allows creation of a non-square homogenizer. If this
            is set to a number not 1, then the x dimension will be changed, y
            remains == receiver_side
	need to loose the homogenizer 
	One snowman says to the other snowman:  You smell carrot?
        """
	#print(receiver_pos,'receiver_pos')
        dish_surf = Surface(OctagonalParabolicDishGM(diameter, focal_length), 
            opt.RealReflective(1 - dish_opt_eff,0.01))
        receiver_dims = (receiver_side, receiver_side*receiver_aspect)
	'''
	TwoNparamcav. __init__(self, apertureRadius=[0.22], frustaRadii=[0.75], frustaDepths=[0.2], coneDepth=1., eps_wall=0.04, absReceiver=0.9, emsReceiver=0.2, aperture_position=0.6, envelope_radius=0.23, envelope_depth = None, specular_receiver=False)
	'''
	#TwoNparamcav. __init__(self, apertureRadius=[0.22,0.23,0.24,0.25,0.26], frustaRadii=[0.75,0.76,0.77,0.78,0.79], frustaDepths=0.2, coneDepth=1., eps_wall=0.04, absReceiver=0.9, emsReceiver=0.2, 		#aperture_position=0.6, envelope_radius = [0.23,0.24,0.25,0.26,0.27], envelope_depth = None, specular_receiver=False)
	'''
	HomogenizedLocalReceiver.__init__(self, dish_surf, receiver_pos, \
            receiver_dims, homogenizer_depth, homog_opt_eff)
	
	f = diameter/4./(sqrt(2) - 1)
   	W = diameter/2. * sqrt(pi/concentration)
   	n = virt_sources + 1
   	H = n*W*f/(diameter - n*W)
   	return f, W, H  Need f, H
	'''
	self._mr=dish_surf
        # for later interrogation:
        self._ext_dims = (diameter, receiver_pos)
        # just assigning values here in this section
	#receiver=TwoNparamcav([0.22], [0.75], [0.2], 1., 0.04, 0.9, 0.2, 0.6, 0.23, None, False)
	
	#recv = AssembledObject(surfs=[receiver_surf])
	recv, a, b =test_receiver(receiver_side,receiver_side,0.9,0.1)
	#recv_surf=Surface(recv, opt.LambertianReceiver(0.9))
	refl_1 = AssembledObject(surfs=[dish_surf])
	refl = Assembly(objects=[refl_1])
	#self._assemblies=Assembly(objects=[dish], subassemblies=[recv])
	
	#self._assemblies=Assembly(objects=[recv], subassemblies=[refl])
	Assembly.__init__(self,objects=[recv],subassemblies=[refl])
	# def __init__(self, objects=None, subassemblies=None, location=None, rotation=None)

    def get_external_dimensions(self):
        """
        Returns the external dimensions (the ones you would put in an assembly
        drawing, the bounding cylinder dimensions) of the entire assembly.
        
        Returns:
        diameter - of the dish
        full_height - from the dish base to the receiver surface.
        """
        return self._ext_dims # no relating to the sub class here
    def get_main_reflector(self):
        return self._mr
def petal_dish(diameter, receiver_pos, receiver_side, dish_opt_eff,receiver_aspect=1.):
	f = diameter/4./(N.sqrt(2) - 1)
	H = receiver_pos-f
	PETAL_dish = PETAL(diameter, f, receiver_pos, receiver_side, dish_opt_eff,receiver_aspect)
	return PETAL_dish, f, H
