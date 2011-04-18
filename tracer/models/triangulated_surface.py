
import numpy as np
from ..object import AssembledObject
from ..surface import Surface
from ..triangular_face import TriangularFace

class TriangulatedSurface(AssembledObject):
    """
    Represent a set of triangular faces composing a surface.
    """
    
    def __init__(self, vertices, faces, optics, transform=None):
        """
        Create the triangular faces from a list of vertices and the topology
        information. Somewhat like VRML's IndexedFaceSet, only limited to
        triangular faces.
        
        Arguments:
        vertices - an (n,3) array of n 3D points in the object's frame.
        faces - an (n,3) integer array, each row is 3 indices into the
            vertices array, for the 3 vertices of one triangular face.
        optics - the optics manager to assign each surface.
        transform - a 4x4 array representing the homogenous transformation 
            matrix of this object relative to the coordinate system of its 
            container
        """
        pos = vertices[faces[:,0]]
        edges = vertices[faces[:,1:],:] - pos[:,None,:]
        edge_norms = np.sqrt(np.sum(edges**2, axis=2))
        
        xs = edges[:,0] / edge_norms[:,0,None]
        zs = np.cross(edges[:,0], edges[:,1]) / edge_norms[:,1,None]
        ys = np.cross(zs, xs)
        
        rots = np.concatenate((xs[...,None], ys[...,None], zs[...,None]), axis=2)
        edges_local = np.sum(rots.transpose(0,2,1)[:,None,...]*edges[:,:,None,:], axis=3)
        
        face_list = [Surface(TriangularFace(edges_local[face_ix].T), optics,
            location=pos[face_ix], rotation=rots[face_ix]) \
            for face_ix in xrange(faces.shape[0])]
        
        AssembledObject.__init__(self, face_list, None, transform)

