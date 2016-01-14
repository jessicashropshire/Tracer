# Various routines for vector geometry, rotations, etc.
# References:
# [1] John J. Craig, Introduction to Robotics, 3rd ed., 2005. 

from math import sin,  cos
import numpy as N

def general_axis_rotation(axis,  ang):
    """Generates a rotation matrix around <axis> by <angle>, using the right-hand
    rule.
    Arguments: 
        axis - a 3-component 1D array representing a unit vector
        angle - rotation counterclockwise in radians around the axis when the axis 
            points to the viewer.
    Returns: A 3x3 array representing the matrix of rotation.
    Reference: [1] p.47
    """
    s = N.round_(sin(ang), decimals=14); c = N.round_(cos(ang), decimals=14); v = 1 - c
    add = N.array([[0,          -axis[2], axis[1]],  
                            [axis[2],  0,          -axis[0]], 
                            [-axis[1], axis[0],  0        ] ])
    return N.multiply.outer(axis,  axis)*v + N.eye(3)*c + add*s

def rotation_to_z(vecs):
    """
    Generate a rotation into a frame whose Z zxis points along the direction
    indicated by ``vecs``. The rest of the directions are determined by
    requiring the new X to lie on the XY plane of the original frame, and by
    the right-hand rule.
    
    In the singular case that the required direction is the Z axis, the
    original frame is retained.
    
    Arguments:
    vec - a 3-component 1D array representing a unit direction in 3D space.
    
    Returns:
    A 3x3 array representing the global-to-local rotation to get the desired
        frame.
    """
	# the [:,None] seems to be just adding another set of bracket to the array
    vecs = N.atleast_2d(vecs)
    perp = N.hstack((vecs[:,1][:,None],  -vecs[:,0][:,None],
        N.zeros((vecs.shape[0], 1)) )) # extracting the number opf rows in the direction array
	# the perp array reverse the fist and second column of dirction and append zero to it. The normal vector in the x-y plane
    perp[N.all(perp == 0., axis=1)] = N.r_[1.,  0.,  0.]
	#N.all returns booleans. if all components in any rows are zero, t.he row is replaced by a unit vector 1,0,0 
	# axis=0, the evaluation is column wise, axis is 1 the evaluation is performed rowwise. 
	# this is between the first and second row. This is to avoid the 0 element in division
    perp /= N.sqrt(N.sum(perp**2., axis=1))[:,None] # elementwise operation, replaced by the magnitude of the direction vector. Now it's only unit vector
    perp_rot = N.concatenate((perp[...,None], N.cross(vecs, perp)[...,None],
        vecs[...,None]), axis=0)# axis equal to 2? It is a columnwise concatenation. The vecs be a unit vector? Oh yes. Need the inverse to complete the rotation int he right direction
    #print('the rotational matrix',perp_rot)
    # perp_rot_inv=N.linalg.inv(perp_rot)

    return N.squeeze(perp_rot)

def generate_transform(axis, angle, translation):
    """Generates a transformation matrix                                                      
    Arguments: axis - a 3-component 1D array giving the unit vector to rotate about          qhelp()
    angle - angle of rotation counter clockwise in radians about the given axis in the 
    parent frame                         
    translation - a 3-component column vector giving the translation along the coordinates
    of the parent object/assembly
    """  
    rot = general_axis_rotation(axis, angle) # here gives a 3 by 3 matrix
    return N.vstack((N.hstack((rot, translation)), N.r_[[0,0,0,1.]]))
    # now we have a 4*4 transformation matrix. The original coordinate of the point need to be added by 1 at the end.

def rotx(ang):
    """Generate a homogenous trransform for ang radians around the x axis"""
    # Rotation matrix in the y-z plane
    s = N.sin(ang); c = N.cos(ang)
    return N.array([
        [1., 0, 0, 0],
        [0, c,-s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1.]
    ])

def roty(ang):
    """Generate a homogenous trransform for ang radians around the y axis"""
    # Rotation matrix in the x-z plane
    s = N.sin(ang); c = N.cos(ang)
    return N.array([
        [c, 0, s, 0],
        [0, 1., 0, 0],
        [-s,0, c, 0],
        [0, 0, 0, 1.]
    ])

def rotz(ang):
    """Generate a homogenous trransform for ang radians around the z axis"""
    # Rotation matrix in the x-y plane
    s = N.sin(ang); c = N.cos(ang)
    return N.array([
        [c,-s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1., 0],
        [0, 0, 0, 1.]
    ])

def translate(x=0, y=0, z=0):
    """Generate a homogenous transform for translation by x, y, z"""
    return N.array([
        [1., 0, 0, x],
        [0, 1., 0, y],
        [0 ,0, 1., z],
        [0, 0, 0, 1.]
    ])
    # Only taking care of the translate part. Notice again the original coordination shoudl be augmented by 1 int he fourth dimension. 
