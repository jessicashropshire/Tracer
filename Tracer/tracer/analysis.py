#Python Packages
import numpy as N
from numpy import r_
from scipy.constants import degree
import matplotlib.pyplot as plt
#Tracer Packages
from tracer.ray_bundle import RayBundle
from tracer.sources import pillbox_sunshape_directions
from tracer.assembly import Assembly
from tracer.spatial_geometry import roty, rotx, rotz, rotation_to_z
from tracer.tracer_engine import TracerEngine
from tracer.tracer_engine_mp import TracerEngineMP
from tracer.optics_callables import *
#Tracer Models
from tracer.models.heliostat_field import HeliostatField, radial_stagger, solar_vector
#Coin3D renderer
from tracer.CoIn_rendering.rendering import *

import copy

def hist_comb(recv, no_of_bins=100):
		"""Returns a combined histogram of all critical surfaces and relevant data"""
		# H is the histogram array
		# boundlist is a list of plate boundaries given in x coordinates
		# extent is a list of [xmin,xmax,ymin,ymax] values
		# binarea is the area of each bin. Used to estimate flux concentration

		# Define empty elements
		X_offset = 0	# Used to shift values to the right for each subsequent surface
		all_X = []	# List of all x-coordinates
		all_Y = []	# List of all y-coordinates
		all_E = []	# List of all energy values
		boundlist = [0]	# List of plate boundaries, starts with x=0

		#print("length here"+str(len((self.plant.get_local_objects()[0]).get_surfaces())))

		#for plate in self.crit_ls:	#For each surface within the list of critical surfs
		crit_length = 1
		count = 0
		for surface in recv.surfaces:
			# returns all coordinates where a hit occured and its energy absorbed
			energy, pts = surface.get_optics_manager().get_all_hits()
			corners = surface.mesh(1) #corners is an array of all corners of the plate
			# BLC is bottom left corner "origin" of the histogram plot
			# BRC is the bottom right corner "x-axis" used for vector u
			# TLC is the top right corner "y-axis" used for vector v
			BLC = N.array([corners[0][1][1],corners[1][1][1],corners[2][1][1]])
			BRC = N.array([corners[0][0][1],corners[1][0][1],corners[2][0][1]])
			TLC = N.array([corners[0][1][0],corners[1][1][0],corners[2][1][0]])
			# Get vectors u and v in array form of array([x,y,z])
			u = BRC - BLC
			v = TLC - BLC
			# Get width(magnitude of u) and height(magnitude of v) in float form
			w = (sum(u**2))**0.5
			h = (sum(v**2))**0.5
			# Get unit vectors of u and v in form of array([x,y,z])
			u_hat = u/w
			v_hat = v/h
			# Local x-position determined using dot product of each point with direction
			# Returns a list of local x and y coordinates
			origin = N.array([[BLC[0]],[BLC[1]],[BLC[2]]])
			local_X = list((N.array(N.matrix(u_hat)*N.matrix(pts-origin))+X_offset)[0])
			#local_Y = list((N.array(N.matrix(v_hat)*N.matrix(pts-origin)))[0])
			local_Y = list((((N.array(N.matrix(v_hat)*N.matrix(pts-origin)))[0])*-1)+h)
			# Adds to the lists
			all_X += local_X
			all_Y += local_Y
			all_E += list(energy)
			X_offset += w
			boundlist.append(X_offset)
			count += 1
		# Now time to build a histogram
		rngy = h
		rngx = X_offset
		bins = [no_of_bins,int(no_of_bins*X_offset)]
		H,ybins,xbins = N.histogram2d(all_Y,all_X,bins,range=([0,rngy],[0,rngx]), weights=all_E)
		extent = [xbins[0],xbins[-1],ybins[0],ybins[-1]]
		binarea = (float(h)/no_of_bins)*(float(X_offset)/int(no_of_bins*X_offset))

		#Edit this later
		img = plt.imshow(H,extent = extent,interpolation='nearest')
		plt.colorbar()

		# Display the vertical lines
		y = r_[0,h]
		n = 1
		for bound in boundlist:
			globals()['line%s' % n] = plt.plot(r_[bound,bound],y,color='k') #Shows plate boundaries
			n += 1
		#plt.xlim(0,boundlist[-1]) #bounds the graph
		plt.show()
		return H, boundlist, extent, binarea

def energies(recv):
		"""Returns the total number of hits on the heliostats, receiver and the total energy absorbed"""
		
		totalenergy = 0.0
		totalhits = 0
		#length = 0
		#for surface in self.plant.get_local_objects()[0].get_surfaces():
		for surface in recv.get_surfaces():
			energy, pts = surface.get_optics_manager().get_all_hits()
			absorp = surface._opt._opt._abs
			#length += len(energy)
			#plt.plot(range(0,len(energy)),energy,'ro')
			#plt.show()
			totalenergy += sum(energy)
			totalhits += sum(energy == absorp)
		#print("Length is"+str(length))
		return totalenergy, totalhits

