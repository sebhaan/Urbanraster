# Utility functions
"""
Author: Sebastian Haan
Affiliation: Sydney Information Hub, The University of Sydney
"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d


def calc_weights(bins, ubins, perc, pop):
	"""
	Calculate the transformtaion matrix to convert income bins to customised bins 
	(see/change incsteps below)
	:param bins: lower boundary of bins
	:param ubins: upper boundary of bins
	:param perc: Cumulative percentage of income bin
	:param pop: Population in each income bin
	"""
	# calculate median:
	fit = interp1d(perc, ubins, kind = 'linear')
	med = fit(50).mean()
	# calcualte conversion matrix from income bin to new 5 bins relative to median:
	incsteps = np.asarray([0., 0.5, 0.8, 1.2, 2.,100]) * med
	# total population number:
	pop_total = np.sum(pop)
	# initialise weight matrix:
	weights = np.zeros((5, len(bins)))
	perc_pop = np.zeros(5)
	# calculating weight matrix:
	for i in range(len(incsteps)-1):
		for j in range(len(bins)):
			if (bins[j] > incsteps[i]) & (ubins[j] < incsteps[i+1]):
				weights[i, j] = 1.
			elif (bins[j] > incsteps[i]) & (bins[j] < incsteps[i+1]) & (ubins[j] > incsteps[i+1]):
				weights[i, j] = (incsteps[i+1] - bins[j]) / (ubins[j] - bins[j])
			elif (bins[j] < incsteps[i]) & (ubins[j] > incsteps[i]) & (ubins[j] < incsteps[i+1]):
				weights[i, j] = (ubins[j] - incsteps[i]) / (ubins[j] - bins[j])
			elif (bins[j] < incsteps[i]) & (ubins[j] > incsteps[i+1]):
				weights[i, j] = (incsteps[i+1] - incsteps[i]) / (ubins[j] - bins[j])
			else:
				weights[i, j] = 0.
		# calculate population percentage for the new customised bins:
		perc_pop[i] = np.dot(weights[i], pop)
	perc_pop = np.round((perc_pop / pop_total * 100.), 2)
	return weights, perc_pop, np.round(med, 1)

def lin_transform(df, Aw, newcol_names = None, decround=None):
	""" Generates dataframe with new income bins based on precaculated weights transformation and old bins
	NEWBINS = Aw * OLDBINS ... 
	With * the dot product (each new bin is sum of old bins multiplied with esepctive weight)
	Weight can be calculated first with function calc_weight()
	:input df: Pandas dataframe with original income bins (oldbins), first column should be anindex
	:param Aw: weight matrix with shape (newbins, oldbins)
	:param newcol_names: define new column names, e.g. ['bin1', 'bin2', 'bin3',...], same number as length of bins
	:param decround: number of decimals after comma to round final dataframe
	"""
	if newcol_names is None:
		newcol_names = []
		for i in range(Nbinsnew):
			newcol_names = np.append(newcol_names, 'Bin' + str(int(i)))
	newcol_names = np.asarray(newcol_names).astype(str)
	Nbinsnew, Nbinsold = Aw.shape[0], Aw.shape[1]
	data = df.iloc[:,1 : Nbinsold + 1].to_numpy()
	index = list(df)[0]
	newdf = df[[index]].copy()
	#newdf = df.copy()
	#newdata = np.zeros((len(data), Nbinsnew))
	#for i in range(len(data)):
	#	newdata[i] = np.dot(Aw, data[i])
	newdata = np.dot(Aw, data.T).T
	# include in dataframe
	total = np.nansum(newdata, axis = 1)
	#newdata = newdata / total.reshape(-1,1)
	newdata = np.divide(newdata, total.reshape(-1,1), out=np.zeros_like(newdata), where=total.reshape(-1,1)!=0)
	if decround is not None: 
		newdata = np.round(newdata, decround)
	for i in range(Nbinsnew):
			newdf[newcol_names[i]] = newdata[:,i]
	#newdf['TOTAL'] = total
	return newdf
