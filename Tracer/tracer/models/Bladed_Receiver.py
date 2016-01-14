#Assembly stage of multiple faces

from tracer.object import AssembledObject
from tracer.surface import Surface
from tracer.flat_surface import RectPlateGM
from tracer.paraboloid import ParabolicDishGM, RectangularParabolicDishGM
from tracer import optics_callables as opt
from tracer.spatial_geometry import general_axis_rotation
from tracer.surface import Surface

from numpy import r_
import numpy as N
import types
import math 

def z_rot(x_ang,y_ang,z_ang):
    """
    Returns the rotation matrix of a rotation about each coordinate axes done one after another. Input in Radians.
    """
    #remove my
    mx = N.matrix(general_axis_rotation(r_[1,0,0],x_ang))
    my = N.matrix(general_axis_rotation(r_[0,1,0],y_ang))
    mz = N.matrix(general_axis_rotation(r_[0,0,1],z_ang))
    M1 = my*mx
    M2 = mz*M1
    return M2
 
def surfaces_for_next_iteration(self, rays, surface_id):
    """
    Informs the ray tracer that some of the surfaces can be skipped in the
    next ireration for some of the rays.
    This implementation marks all surfaces as irrelevant to all rays.
    
    Arguments:
    rays - the RayBundle to check. 
    surface_id - the index of the surface which generated this bundle.
    
    Returns:
    an array of size s by r for s surfaces in this object and r rays,
        stating whether ray i=1..r should be intersected with surface j=1..s
        in the next iteration.
    """
    return N.zeros((len(self.surfaces), rays.get_num_rays()), dtype=N.bool)

def cavity_receiver(width, height, absorptivity=1.):
    """
    Constructs a lambertian receiver consisting of three faces. Returns a list of receiving faces, the assembled object
    """
    front = Surface(RectPlateGM(width, height),opt.LambertianReceiver(absorptivity),location=r_[0.,0.,0.],rotation=general_axis_rotation(r_[1,0,0],N.pi/2))
    left = Surface(RectPlateGM(width, height),opt.LambertianReceiver(absorptivity),location=r_[width/2,width/2,0.],rotation=general_axis_rotation(r_[0,1,0],N.pi/-2))
    left.width = width
    left.height = height/2.
    right = Surface(RectPlateGM(width, height),opt.LambertianReceiver(absorptivity),location=r_[width/-2,width/2,0.],rotation=general_axis_rotation(r_[0,1,0],N.pi/2))
    right.width = width
    right.height = height/2.
    rec_obj = AssembledObject(surfs=[left, front, right])
    #obj.surfaces_for_next_iteration = types.MethodType(surfaces_for_next_iteration, obj, obj.__class__)
    return rec_obj,[left, front, right], [left, front, right]

def thin_bladed_receiver(width, height, absorptivity, blades):
    """
    Constructs lambertian receiver consisting of thin blades.
    """
    front = Surface(RectPlateGM(width, height),opt.LambertianReceiver(absorptivity),location=r_[0.,width/-2.,0.],rotation=general_axis_rotation(r_[1,0,0],N.pi/2))
    n = 0
    front.axis = [1,0,0]
    front.tilt = N.pi/2
    crit_ls = []
    crit_ls.append(front)
    while n < blades:
	blade = Surface(RectPlateGM(width, height),opt.LambertianReceiver(absorptivity),location=r_[width/2-(n*width/(blades-1)),0.,0.],rotation=general_axis_rotation(r_[0,1,0],N.pi/-2))
	blade.number = n+1
	blade.axis = [0,1,0]
	blade.tilt = N.pi/2
	crit_ls.append(blade)
	n += 1
    rec_obj = AssembledObject(surfs=crit_ls)
    #obj.surfaces_for_next_iteration = types.MethodType(surfaces_for_next_iteration, obj, obj.__class__)
    return rec_obj, obj_ls, crit_ls

def Lamby(a,x,y,z,rx,ry,rz,w,h,sigma_xy):
	"""
	Simplified Lambertian plate generator
	"""
	#rv=opt.ReflectiveReceiver(a)
	#surface = Surface(RectPlateGM(w,h),opt.LambertianReceiver(a),location=r_[x,y,z],rotation=z_rot(rx,ry,rz))
	surface = Surface(RectPlateGM(w,h),opt.RealReflectiveReceiver(a,sigma_xy),location=r_[x,y,z],rotation=z_rot(rx,ry,rz))
	return surface

def test_receiver(width, height, receiver_pos, absorptivity,sigma_xy):
    """
    Constructs a test receiver
    """
    front = Lamby(absorptivity,0.,0.,receiver_pos,0.,0.,0.,width,height,sigma_xy)
    #front = Surface(RectPlateGM(width,height),opt.LambertianReceiver(absorptivity),location=r_[0.,1,0.],rotation=z_rot(N.pi/2,N.pi/2,N.pi/2))
    back = Lamby(1.0,0.,0.,receiver_pos+0.001,0.,0.,0.,width,height,sigma_xy)
    obj = AssembledObject(surfs=[front,back])
    return obj, [front], [front]

def cavity_aligned(width,height,absorptivity):
	"""Constructs a lambertian cavity receiver with aligned surfaces"""
	a = absorptivity
	left = Lamby(a,width/2.,0,0,N.pi/-2.,0,N.pi/2.,width,height)
	centre = Lamby(a,0,width/-2.,0,N.pi/-2,0,0,width,height)
	right = Lamby(a,width/-2.,0,0,N.pi/-2.,0,N.pi/-2.,width,height)
	rec_obj = AssembledObject(surfs=[left,centre,right])
	surf_ls = [left,centre,right]
	crit_ls = [left,centre,right]
	return rec_obj, surf_ls, crit_ls
