    
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

k-means aperture optimization utilities.
see example1.py file for use cases.

'''

import numpy as np 
from scipy.signal import convolve2d
from scipy.optimize import fmin, minimize
from scipy.ndimage import shift 
from scipy.stats import trimboth
from sklearn.cluster import KMeans

__version__ = "0.4"

### ---------------------------------------------------------------------------
### ---------------------------------------------------------------------------

def cross_dilate(init_mask, N):
	final_mask = init_mask.copy()
	for i in range(0, N):
		final_mask = convolve2d(final_mask, 
			[[0, 1, 0], [1, 1, 1], [0, 1, 0]], mode='same')
	return final_mask > 0

### ---------------------------------------------------------------------------
### ---------------------------------------------------------------------------

def lfstdv(y_in, x_in=None):
	y = y_in.copy()
	if x_in != None:
		y = y[np.argsort(x_in)]
	delta = np.sort((y[1:-1]-y[2:])-0.5*(y[:-2]-y[2:]))

	###    scaled to match standard deviation of
	###    gaussian noise on constant signal 
	###    also, trim outliers.
	return 0.8166137*np.std( trimboth( delta, 0.05 ) )

### ---------------------------------------------------------------------------
### ---------------------------------------------------------------------------

def scatterscale(params, data, aperture_id, ret=False):
	Z = np.unique(aperture_id)
	s = []
	for z in Z:
		s.append(np.sum(aperture_id==z))
	id_leavout = Z[np.argmax(s)]

	scaled_data = np.zeros(data.shape)
	count = 0

	for z in Z:
		if z == id_leavout:
			scaled_data[aperture_id==z] = data[aperture_id==z]
			continue
		scaled_data[aperture_id==z] = data[aperture_id==z] * params[count]
		count += 1
	if ret:
		return scaled_data
	return lfstdv(scaled_data)

### ---------------------------------------------------------------------------
### ---------------------------------------------------------------------------

def scatternorm(data, aperture_id):
	param0 = np.ones(np.unique(aperture_id).size - 1)
	result = minimize(scatterscale, param0, args=(data, aperture_id), 
					method='powell', options={'disp':True})
	return scatterscale(result.x, data, aperture_id, ret=True)

### ---------------------------------------------------------------------------
### ---------------------------------------------------------------------------

def cluster(data, mask0, N=5):

	features = []
	for i in range(0, data.shape[0]):
		v  = data[i].copy()
		v /= np.nanmean(v[mask0])
		features.append(v[mask0].ravel())
	features = np.array(features)
	features[np.isnan(features)] = 0.0

	model = KMeans(init='k-means++', n_clusters=N, n_init=min(5*N, data.shape[0]), algorithm='full')
	model.fit(features)
	aperture_id = model.predict(features)
	for z in np.unique(aperture_id):
		print('Aperture %d -- %d images'%(z+1, np.sum(aperture_id==z)))
	return aperture_id

### ---------------------------------------------------------------------------
### ---------------------------------------------------------------------------

def reduce_apertures(data, mask0, aperture_id, correct=True, thresh=0.99, grow=1):

	time_series = np.zeros(aperture_id.shape) 

	for z in np.unique(aperture_id):
		inds = np.where(aperture_id==z)

		delta = data[inds].copy()
		delta_ratio = data[inds].copy() ### left redundant in case a sky ratio is needed
		max_delta = np.nanmean(delta, axis=0)
		max_delta_ratio = np.nanmean(delta_ratio, axis=0)
		max_delta[max_delta<=0] = 0
		max_delta[np.isnan(max_delta)] = 0
		temp_mask = mask0.copy()
		max_delta[~temp_mask] = 0
		max_delta_ratio[~temp_mask] = np.inf
		tot = np.nansum(max_delta[temp_mask])
		while np.nansum(max_delta[temp_mask]) / tot > thresh:
			ij = np.unravel_index(max_delta_ratio.argmin(), max_delta_ratio.shape)
			temp_mask[ij] = False
			max_delta_ratio[ij] = np.inf

		temp_mask = cross_dilate(temp_mask, grow)
		for i in inds[0]:
			time_series[i] = np.nansum(data[i][temp_mask])

	if correct:
		time_series = scatternorm(time_series, aperture_id)
	return time_series

### ---------------------------------------------------------------------------
### ---------------------------------------------------------------------------

