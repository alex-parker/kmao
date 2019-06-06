    
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

Example application of kmao utilities on 
Kepler K2 eclipsing binary data.
Uses lightkurve for data fetching. 

'''


from kmao import *
import lightkurve as lk
import matplotlib.pyplot as plt 

if __name__ == "__main__":


	### fetch target pixel file for an eclipsing binary.
	targ_id = 'EPIC 202063160'
	pixels = lk.search_targetpixelfile(targ_id).download()

	flux = pixels.flux 
	times = pixels.time 

	### create a big initial aperture
	mask0 = cross_dilate( pixels.pipeline_mask, 5)

	### initial alignment of centroids
	CX, CY = pixels.estimate_centroids(aperture_mask=mask0)
	mCX, mCY = np.mean(CX), np.mean(CY)

	for i in range(flux.shape[0]):
		flux[i] = shift(flux[i], (mCY-CY[i], mCX-CX[i]), order=0)

	### cluster images into 30 groups
	aperture_id = cluster(flux, mask0, 30)

	### optimize apertures, determine aperture corrections, return kmao time series
	time_series_30 = reduce_apertures(flux, mask0, aperture_id, correct=True)

	### perform again, but only use a single aperture
	### No aperture corrections for this case.
	time_series_1 = reduce_apertures(flux, mask0, 0*aperture_id, correct=False)

	### normalize to median
	time_series_30 /= np.nanmedian(time_series_30)
	time_series_1 /= np.nanmedian(time_series_1)

	sig6_30 =  lfstdv(time_series_30)*1E6/np.sqrt(12)
	sig6_1  =  lfstdv(time_series_1)*1E6/np.sqrt(12)

	print('Approximate 6-hour scatter,  1 aperture:  %.1f ppm'%(sig6_1))
	print('Approximate 6-hour scatter, 30 apertures: %.1f ppm'%(sig6_30))

	plt.scatter(times, time_series_1, marker='.', color='r', s=3, alpha=0.5)
	plt.scatter(times, time_series_30, marker='.', color='k', s=1)
	plt.xlabel('Time (BJD-2454833)')
	plt.ylabel('Relative Flux')
	plt.title(targ_id)
	plt.show()