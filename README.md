# `kmao`
## *k*-Means Aperture Optimization for Kepler K2 data
---

k-Means Aperture Optization (`kmao`) is a technique for correcting aperture photometry in the presence of target motion and saturation. 

`kmao` optimizes a small *set* of apertures. These apertures each apply to a unique sub-set of the target images that have similar properties. The assigment of images to these sets is done via *k*-means clustering on the target pixel files.

The advantage of this approach is that it requires no external information to correct photometry of a source. As such, the photometry of a uniquely moving, saturated source can be corrected using `kmao` as easily as a stationary, un-saturated source.

This repository currently contains preliminary scripts demonstrating this technique in support of Parker et al. (submitted, PASP).

## Requirements
To run the example scripts:

numpy
scipy
astropy
lightkurve
matplotlib
sklearn

## Running the example scripts

## References

Parker, A. Hörst, S., Ryan, E., & Howett, C. (PASP, submitted). "k-Means Aperture Optimization Applied to Kepler K2 Time Series Photometry of Titan."




