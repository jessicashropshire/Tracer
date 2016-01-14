# Implements a circular paraboloid surface
#
# References:
# [1] http://www.siggraph.org/education/materials/HyperGraph/raytrace/rtinter4.htm
# [2] http://en.wikipedia.org/wiki/Parabola

import numpy as N
from quadric import QuadricGM

class Paraboloid(QuadricGM):
    """Implements the geometry of a circular paraboloid surface"""
    def __init__(self, a=1., b=None):
        """               
        Arguments: 
        a, b - describe the paraboloid as z = (x/a)**2 + (y/b)**2
            (sorry, legacy)
        
        Private attributes:                                                                  
        a, b - describe the paraboloid as z = a*x**2 + b*y**2
        """ 
        if b is None:
	        b = a

        QuadricGM.__init__(self)
        self.a = 1./(a**2)
        self.b = 1./(b**2)

    def _normals(self, hits, directs):
        """
        Finds the normal to the parabola in a bunch of intersection points, by
        taking the derivative and rotating it. Used internally by quadric.
        
        Arguments:
        hits - the coordinates of intersections, as an n by 3 array.
        directs - directions of the corresponding rays, n by 3 array.
        """
        hit = N.dot(N.linalg.inv(self._working_frame), N.vstack((hits.T, N.ones(hits.shape[0]))))
        dir_loc = N.dot(self._working_frame[:3,:3].T, directs.T)

        partial_x = 2*hit[0]*self.a
        partial_y = 2*hit[1]*self.b
        partial_z = -1*N.ones(N.shape(hits)[0])
        
        local_normal = N.vstack((partial_x, partial_y, partial_z))
        local_unit = local_normal/N.sqrt(N.sum(local_normal**2, axis=0))

        down = N.sum(dir_loc * local_unit, axis=0) > 0
        local_unit[:,down] *= -1

        normals = N.dot(self._working_frame[:3,:3], local_unit)
        
        return normals

    
    def get_ABC(self, ray_bundle):
        """
        Determines the variables forming the relevant quadric equation, [1]
        """
        # Transform the the direction and position of the rays temporarily into the
        # frame of the paraboloid for calculations
	#print(self._working_frame[:3,:3], 'working_frame',ray_bundle.get_directions(),'ray_bundle_get directions')
	dir(ray_bundle)
        d = N.dot(self._working_frame[:3,:3].T, ray_bundle.get_directions())
        v = N.dot(N.linalg.inv(self._working_frame), 
            N.vstack((ray_bundle.get_vertices(), N.ones(d.shape[1]))))[:3]
        
        A = self.a*d[0]**2 + self.b*d[1]**2
        B = 2*self.a*d[0]*v[0] + 2*self.b*d[1]*v[1] - d[2] 
        C = self.a*v[0]**2 + self.b*v[1]**2 - v[2]
        
        return A, B, C


class ParabolicDishGM(Paraboloid):
    """
    A paraboloid that marks rays outside its diameter as missing. The
    parameters for the paraboloid's equation are determined from the focal
    length.
    """
    def __init__(self, diameter, focal_length):
        """
        Arguments:
        diameter - of the circular aperture created by cutting the paraboloid
            with a plane parallel to the xy plane.
        focal_length - distance of the focal point from the origin.
        """
        par_param = 2.*N.sqrt(focal_length) # [2]
        Paraboloid.__init__(self, par_param, par_param)
        self._R = float(diameter/2.) # For the mesh
        self._h = float((diameter/2./par_param)**2)
    
    def _select_coords(self, coords, prm):
        """
        Choose between two intersection points on a quadric surface.
        This implementation extends QuadricGM's behaviour by not choosing
        intersections outside the circular aperture.
        
        Arguments:
        coords - a 2 by 3 by n array whose each column is the global coordinates
            of one intersection point of a ray with the sphere.
        prm - the corresponding parametric location on the ray where the
            intersection occurs.

        Returns:
        The index of the selected intersection, or None if neither will do.
        """
        select = N.empty(prm.shape[1])
        select.fill(N.nan)

        positive = prm > 1e-10
        
        coords = N.concatenate((coords, N.ones((2,1,coords.shape[2]))), axis=1)
        local_z = N.sum(N.linalg.inv(self._working_frame)[None,2,:,None]*coords, axis=1)
	#working frame, a 4*4 homogeneous transform array representing the surface frame in the global coordinates. 
        under_cut = (local_z <= self._h) & (local_z >= 0)
        hitting = under_cut & positive

        select[N.logical_and(*hitting)] = 1
        one_hitting = N.logical_xor(*hitting)
        select[one_hitting] = N.nonzero(hitting.T[one_hitting,:])[1]

        return select
    
    def mesh(self, resolution=None):
        """
        Represent the surface as a mesh in local coordinates. Uses polar
        bins, i.e. the points are equally distributed by angle and radius,
        not by x,y.
        
        Arguments:
        resolution - in points per unit length (so the number of points 
            returned is O(A*resolution**2) for area A)
        
        Returns:
        x, y, z - each a 2D array holding in its (i,j) cell the x, y, and z
            coordinate (respectively) of point (i,j) in the mesh.
        """
        if resolution is None:
            #resolution = 2*N.pi*self._R / 40
            resolution = 40.
        # Generate a circular-edge mesh using polar coordinates.
        r_end = self._R*(1.+1./resolution)
        rs = N.r_[0:r_end:self._R/resolution]
        # Make the circumferential points at the requested resolution.
        ang_end = 2*N.pi*(1.+1./(self._R*resolution))
        angs = N.r_[0:ang_end:2*N.pi/(self._R*resolution)]

        x = N.outer(rs, N.cos(angs))
        y = N.outer(rs, N.sin(angs))
        z = self.a*x**2 + self.b*y**2

        return x, y, z

class HexagonalParabolicDishGM(Paraboloid):
    """
    A paraboloid that marks rays outside a regular hexagon perimeter as
    missing. The parameters for the paraboloid's equation are determined
    from the focal length. The hexagon is oriented with two parallel to the
    Y axis.
    """    
    def __init__(self, diameter, focal_length):
        """
        Arguments:
        diameter - of the circle bounding the regular hexagonal aperture of the
            dish.
        focal_length - distance of the focal point from the origin.
        """
        par_param = 2*N.sqrt(focal_length) # [2]
        Paraboloid.__init__(self, par_param, par_param)
        self._R = diameter/2.
    
    def _select_coords(self, coords, prm):
        """
        Choose between two intersection points on a quadric surface.
        This implementation extends QuadricGM's behaviour by not choosing
        intersections outside the hexagon aperture.
        
        Arguments:
        coords - a 2 by 3 by n array whose each column is the global coordinates
            of one intersection point of a ray with the sphere. Why 2 by three here, doesn't concatenate with 
        prm - the corresponding parametric location on the ray where the
            intersection occurs.

        Returns:
        The index of the selected intersection, or None if neither will do.
        """
        select = QuadricGM._select_coords(self, coords, prm) # defaults

        coords = N.concatenate((coords, N.ones((2,1,coords.shape[2]))), axis=1) # n rays two clusters of row matrices with n elements of one concatenated horizontally 2*4*n ats.
        local = N.sum(N.linalg.inv(self._working_frame)[None,:2,:,None] * \
            coords[:,None,:,:], axis=2)
        #working frame, a 4*4 homogeneous transform array representing the surface frame in the global coordinates. This is an elementwise multiplication, interesting. 
	#2*4 and three extra layers. Imitation of a dot product. Now the coordinates transferred back to the local ones.
        abs_x = abs(local[:,0,:])
        abs_y = abs(local[:,1,:])
        outside = abs_x > N.sqrt(3)*self._R/2.
        outside |= abs_y > self._R - N.tan(N.pi/6.)*abs_x
        inside = (~outside) & (prm > 1e-9)
        
        select[~N.logical_or(*inside)] = N.nan
        one_hit = N.logical_xor(*inside)
        select[one_hit] = N.nonzero(inside.T[one_hit,:])[1]

        return select
    def mesh(self, resolution=None):
        """
        Represent the surface as a mesh in local coordinates. Uses polar
        bins, i.e. the points are equally distributed by angle and radius,
        not by x,y.
        
        Arguments:
        resolution - in points per unit length (so the number of points 
            returned is O(A*resolution**2) for area A)
        
        Returns:
        x, y, z - each a 2D array holding in its (i,j) cell the x, y, and z
            coordinate (respectively) of point (i,j) in the mesh.
        """
        if resolution is None:
            #resolution = 2*N.pi*self._R / 40
            resolution = 40.
        # Generate a circular-edge mesh using polar coordinates.
        r_end = self._R*(1.+1./resolution)
        rs = N.r_[0:r_end:self._R/resolution]
        # Make the circumferential points at the requested resolution.
        ang_end = 2*N.pi*(1.+1./(self._R*resolution))
        angs = N.r_[0:ang_end:2*N.pi/(self._R*resolution)]

        x = N.outer(rs, N.cos(angs))
        y = N.outer(rs, N.sin(angs))
        z = self.a*x**2 + self.b*y**2

        return x, y, z
class OctagonalParabolicDishGM(Paraboloid):
    """
    A paraboloid that marks rays outside a regular hexagon perimeter as
    missing. The parameters for the paraboloid's equation are determined
    from the focal length. The hexagon is oriented with two parallel to the
    Y axis.
    """    
    def __init__(self, diameter, focal_length):
        """
        Arguments:
        diameter - of the circle bounding the regular hexagonal aperture of the
            dish.
        focal_length - distance of the focal point from the origin.
        """
        par_param = 2*N.sqrt(focal_length) # [2]
        Paraboloid.__init__(self, par_param, par_param)
        self._R = diameter/2.
    
    def _select_coords(self, coords, prm):
        """
        Choose between two intersection points on a quadric surface.
        This implementation extends QuadricGM's behaviour by not choosing
        intersections outside the hexagon aperture.
        
        Arguments:
        coords - a 2 by 3 by n array whose each column is the global coordinates
            of one intersection point of a ray with the sphere.
        prm - the corresponding parametric location on the ray where the
            intersection occurs.

        Returns:
        The index of the selected intersection, or None if neither will do.
        """
        select = QuadricGM._select_coords(self, coords, prm) # defaults

        coords = N.concatenate((coords, N.ones((2,1,coords.shape[2]))), axis=1)
        local = N.sum(N.linalg.inv(self._working_frame)[None,:2,:,None] * \
            coords[:,None,:,:], axis=2)
        
        abs_x = abs(local[:,0,:])
        abs_y = abs(local[:,1,:])
	a=abs_x > N.cos(N.pi/8.)*self._R
	b=abs_y > N.cos(N.pi/8.)*self._R
        outside = a | b
        outside |= abs_y > self._R*N.cos(N.pi/8.)- N.tan(N.pi/4.)*(abs_x-self._R*N.sin(N.pi/8.))
        inside = (~outside) & (prm > 1e-9)
        
        select[~N.logical_or(*inside)] = N.nan
        one_hit = N.logical_xor(*inside)
        select[one_hit] = N.nonzero(inside.T[one_hit,:])[1]

        return select
    def mesh(self, resolution=None):
        """
        Represent the surface as a mesh in local coordinates. Uses polar
        bins, i.e. the points are equally distributed by angle and radius,
        not by x,y.
        
        Arguments:
        resolution - in points per unit length (so the number of points 
            returned is O(A*resolution**2) for area A)
        
        Returns:
        x, y, z - each a 2D array holding in its (i,j) cell the x, y, and z
            coordinate (respectively) of point (i,j) in the mesh.
	the neshing gives a circular shape for the parabolic_dish
        """
        if resolution is None:
            #resolution = 2*N.pi*self._R / 40
            resolution = 40.
        # Generate a circular-edge mesh using polar coordinates.
        r_end = self._R*(1.+1./resolution)
        rs = N.r_[0:r_end:self._R/resolution]
        # Make the circumferential points at the requested resolution.
        ang_end = 2*N.pi*(1.+1./(self._R*resolution))
        angs = N.r_[0:ang_end:2*N.pi/(self._R*resolution)]

        x = N.outer(rs, N.cos(angs))
        y = N.outer(rs, N.sin(angs))
        z = self.a*x**2 + self.b*y**2

        return x, y, z

class RectangularParabolicDishGM(Paraboloid):
    """
    A paraboloid that marks rays outside a rectangle perimeter as missing i.e.
    the dish has a rectangular aperture. The parameters for the paraboloid's
    equations are determined from the focal length. The sides of the rectangle
    are oriented parallel to the X, Y axes.
    """
    def __init__(self, width, height, focal_length):
        par_param = 2*math.sqrt(focal_length)
        Paraboloid.__init__(self, par_param, par_param)
        self._half_dims = N.c_[[width, height]]/2
        #self._R = float(math.sqrt((width/2)**2 + (height/2)**2))
        self._w, self._h = width/2., height/2.


    def _select_coords(self, coords, prm):
        """
        Choose between two intersection points on a quadric surface.
        This implementation extends QuadricGM's behaviour by not choosing
        intersections outside the rectangular aperture.
        
        Arguments:
        coords - a 2 by 3 by n array whose each column is the global coordinates
            of one intersection point of a ray with the sphere.
        prm - the corresponding parametric location on the ray where the
            intersection occurs.

        Returns:
        The index of the selected intersection, or None if neither will do.
        """
        select = QuadricGM._select_coords(self, coords, prm)

        coords = N.concatenate((coords, N.ones((2,1,coords.shape[2]))), axis = 1)
        # assumed no additional parameters to coords, axis = 1
        #local = N.sum(N.linalg.inv(self._working_frame)[None,:2,:,None]*coords, axis=1)
        local = N.sum(N.linalg.inv(self._working_frame)[None,:2,:,None] * \
            coords[:,None,:,:], axis=2)

        abs_x = abs(local[:,0,:])
        abs_y = abs(local[:,1,:])
        outside = abs_x > self._w
        outside |= abs_y > self._h
        inside = (~outside) & (prm > 1e-9)

        select[~N.logical_or(*inside)] = N.nan
        one_hit = N.logical_xor(*inside)
        select[one_hit] = N.nonzero(inside.T[one_hit,:])[1]

        return select

    def mesh(self, resolution=None):
        """
        Represent the surface as a mesh in local coordinates.
        
        Arguments:
        resolution - in points per unit length (so the number of points 
            returned is O(A*resolution**2) for area A)
        
        Returns:
        x, y, z - each a 2D array holding in its (i,j) cell the x, y, and z
            coordinate (respectively) of point (i,j) in the mesh.
        """
        if resolution == None:
            resolution = 40
        points = N.ceil(resolution*self._half_dims.reshape(-1)*2)
        points[points < 2] = 2 # At least the edges of the range.
        xs = N.linspace(-self._half_dims[0,0], self._half_dims[0,0], points[0])
        ys = N.linspace(-self._half_dims[1,0], self._half_dims[1,0], points[1])
        
        x, y = N.broadcast_arrays(xs[:,None], ys)
        z = self.a*x**2 + self.b*y**2
        #print(">>> heliostat", x, y, z)
        return x, y, z
    

