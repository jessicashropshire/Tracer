"""
This module contains functions to create some frequently-used light sources.
Each function returns a RayBundle instance that represents the distribution of
rays expected from that source.

References:from 
.. [1] Monte Carlo Ray Tracing, Siggraph 2003 Course 44
"""

from numpy import random, linalg as LA
import numpy as N
from .ray_bundle import RayBundle
from .spatial_geometry import *




def solar_disk_bundle(num_rays, focal_length, center,  normal,  radius, ang_range, flux=None, radius_in=0., angular_span=[0.,2.*N.pi]):
    """
    Generates a ray bundle emanating from a disk, or more precisely the receiver position, with each surface element of 
    the disk having the same ray density. The rays all point at directions uniformly 
    distributed between a given angle range from a given direction.
    Setting of the bundle's energy is left to the caller.
    
    Arguments:
    num_rays - number of rays to generate.
    center - a column 3-array with the 3D coordinate of the disk's center
    direction - a 1D 3-array with the unit average direction vector for the
        bundle.
    radius - of the disk.
    ang_range - in radians, the maximum deviation from <direction>.Coz the numpy sin function deals with radians. 
    flux - if not None, the ray bundle's energy is set such that each ray has
        an equal amount of energy, and the total energy is flux*pi*radius**2
    
    Returns: 
    A RayBundle object with the above characteristics set.
    """

	# FIXME why should 'center' be a column vector... that's just annoying.

    radius = float(radius)
    radius_in = float(radius_in)
    # what is radius_in?
    perp_rot = rotation_to_z(normal)    
    xi1 = random.uniform(size=num_rays)# num_rays number of random number from 0 to 1
    thetas = random.uniform(low=angular_span[0], high=angular_span[1], size=num_rays) # the 
    rs = N.sqrt(radius_in**2.+xi1*(radius**2.-radius_in**2.))
    xs = rs * N.cos(thetas)
    ys = rs * N.sin(thetas)
    abs_x=abs(xs)
    abs_y=abs(ys) 
    a=abs_x > N.cos(N.pi/8.)*radius
    b=abs_y > N.cos(N.pi/8.)*radius
    outside = a | b
    outside |= abs_y > radius*N.cos(N.pi/8.)- N.tan(N.pi/4.)*(abs_x-radius*N.sin(N.pi/8.)) 
        
    
    focus=N.array([[0],[0],[focal_length]])
    #end=N.tile(focus,(1,num_rays))
    vertices_local = N.vstack((xs, ys, N.ones(num_rays)*2))
    vertices_local[:,outside] = N.nan
    vertices_global = N.dot(perp_rot, vertices_local)
    #a=vertices_local-end
    a= N.dot(perp_rot, N.c_[[0., 0., -1]])
    directions=N.tile(a,(1,num_rays))
    #directions = N.dot(perp_rot,a)
    # Rotate locations to the plane defined by <direction>:
    # this is creating a flat disk at the centre of the solar reflector
    rayb = RayBundle(vertices=vertices_global, directions=directions) 
    #rayb = RayBundle(vertices=vertices_global + center, directions=directions) 
    # random point on the dish, spill box defined directions
    if flux != None:
        rayb.set_energy(N.pi*(radius**2.-radius_in**2.)/num_rays*flux*N.ones(num_rays))
    return rayb
    # 



# vim: et:ts=4
