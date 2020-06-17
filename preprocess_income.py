# Income Data preprocesing and Plot Exploratory Data Characteristics
import numpy as np
import geopandas as gpd
import pandas as pd
from scipy.interpolate import interp1d
from lib.utils import *
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

"""
Author: Sebastian Haan
Affiliation: Sydney Information Hub, The University of Sydney

Comment: Highly customised to input data for processing raw input data;
File names for coriginal input data have to changed below in script (not in settings.yaml)
"""


########## Settings


with open('settings.yaml') as f:
	cfg = yaml.safe_load(f)
for key in cfg:
	globals()[str(key)] = cfg[key]

### set parameters below in settings.yaml:
# outpath_preproc_inc = '../Results/preprocessed/'
# plot_exp = False


### Explore Area sizes
infile = inpath + 'SA1_Data_2016/1270055001_sa1_2016_aust_shape/SA1_2016_AUST.shp'

d16 = gpd.read_file(infile)

syd16 = d16[d16.GCC_NAME16 == 'Greater Sydney'].copy()

selcols = ['SA1_7DIG16',
 'AREASQKM16',
 'geometry']

syd16 = syd16[selcols]
#syd16.to_file('SYD16.gpkg', driver = 'GPKG')

if plot_exp:
	# histogram on log scale. 
	# Use non-equal bin sizes, such that they look equal on log scale.
	logbins = np.logspace(np.log(syd16.AREASQKM16.min() * 1e6),np.log(syd16.AREASQKM16.max()* 1e6),100, base = np.exp(1))
	plt.hist(syd16.AREASQKM16 * 1e6, bins=logbins)
	#sns.distplot(syd16.AREASQKM16, bins=logbins)
	plt.xscale('log')
	plt.axvline(np.median(syd16.AREASQKM16)* 1e6, color='k')
	plt.xlabel('AREA SQM 2016')
	plt.savefig(outpath_preproc_inc  + 'Dist_area2016.png')
	#plt.show()

"""
infile2 = inpath + 'SYD06.gpkg'
d06 = gpd.read_file(infile2)

d06 = d06.to_crs({'init': 'epsg:3577'})

d06['AREA_SQM'] = d06.area

if plot_exp:
	logbins = np.logspace(np.log(d06.AREA_SQM.min()),np.log(d06.AREA_SQM.max()),100, base = np.exp(1))
	plt.hist(d06.AREA_SQM, bins=logbins)
	#sns.distplot(syd16.AREASQKM16, bins=logbins)
	plt.xscale('log')
	plt.axvline(np.median(d06.AREA_SQM), color='k')
	plt.xlabel('AREA SQM 2006')
	plt.savefig(outpath_preproc_inc  + 'Dist_area2006.png')
	#plt.show()
"""

#### Test in income bins:

# 2016
fname_inc16 = inpath + 'SA1_Data_2016/SA1_NSW_2016_Income_edited.csv'
fname_pop16 = inpath + 'SA1_Data_2016/SA1_NSW_2016_UR_edited.csv'

inc16 = pd.read_csv(fname_inc16)
tot16 = inc16[inc16.SA1_CODE7 == 'Total'].copy()
bins = list(tot16)
bins = bins[1:-1]
bins = np.asarray(bins).astype(int)
ubins = bins[1:]
ubins = np.append(ubins, 2*bins[-1] - bins[-2])
ubins = np.asarray(ubins).astype(int)

array = tot16.to_numpy()
array = array[0]
ntot = array[-1]
array = array[1:-1].astype(int)
perc16 = np.cumsum(array)/ntot * 100



res16 = pd.DataFrame(np.asarray([bins, ubins,np.round(perc16).astype(int)]).T, columns=['Weekly_Income_From', 'Weekly_Income_To', 'Percentile'])
print('Percentile 2016')
diff = np.zeros(len(bins))
for i, perc in enumerate(perc16):
	print(bins[i], '-', ubins[i], np.round(perc,1))
	if i < len(bins)-1:
		diff[i] = 0.5 * (bins[i] + bins[i+1])
	else:
		diff[i] = bins[i] + (bins[i] - bins[i-1])

res16.to_csv(outpath_preproc_inc  + 'Percentile_2016.csv')

array16 = array *1.
bins16 = bins *1.
ubins16 = ubins *1.
diff16 = diff *1
ntot16 = ntot * 1


# 2011
fname_inc11 = inpath + 'SA1_Data_2011/SA1_NSW_2011_Income_edited.csv'

inc11 = pd.read_csv(fname_inc11)
tot11 = inc11[inc11.SA1_CODE7 == 'Total'].copy()
bins = list(tot11)
bins = bins[1:-1]
bins = np.asarray(bins).astype(int)
ubins = bins[1:]
ubins = np.append(ubins, 2*bins[-1] - bins[-2])
ubins = np.asarray(ubins).astype(int)

array = tot11.to_numpy()
array = array[0]
ntot = array[-1]
array = array[1:-1].astype(int)
perc11 = np.cumsum(array)/ntot * 100



res11 = pd.DataFrame(np.asarray([bins,ubins, np.round(perc11).astype(int)]).T, columns=['Weekly_Income_From', 'Weekly_Income_To', 'Percentile'])
print('Percentile 2011')
diff = np.zeros(len(bins))
for i, perc in enumerate(perc11):
	print(bins[i], '-', ubins[i], np.round(perc,1))
	if i < len(bins)-1:
		diff[i] = 0.5 * (bins[i] + bins[i+1])
	else:
		diff[i] = bins[i] + (bins[i] - bins[i-1])

res11.to_csv(outpath_preproc_inc  + 'Percentile_2011.csv')

array11 = array *1.
bins11 = bins *1.
ubins11 = ubins *1.
diff11 = diff *1.
ntot11 = ntot * 1


#### Calculatiung new income bins
print('Computing conversion matrix from old to new income bins...')
# 2006
fname_inc06 = inpath + 'CCD_Data_2006/CCD_NSW_2006_Income_edited.csv'

inc06 = pd.read_csv(fname_inc06)
tot06 = inc06[inc06.ASGC_CODE7 == 'Total'].copy()
bins = list(tot06)
bins = bins[1:-1]
bins = np.asarray(bins).astype(int)
ubins = bins[1:]
ubins = np.append(ubins, 2*bins[-1] - bins[-2])
ubins = np.asarray(ubins).astype(int)

array = tot06.to_numpy()
array = array[0]
ntot = array[-1]
array = array[1:-1].astype(int)
perc06 = np.cumsum(array)/ntot * 100



res06 = pd.DataFrame(np.asarray([bins,ubins, np.round(perc06).astype(int)]).T, columns=['Weekly_Income_From', 'Weekly_Income_To','Percentile'])
print('Percentile 2006')
diff = np.zeros(len(bins))
for i, perc in enumerate(perc06):
	print(bins[i], '-', ubins[i], np.round(perc,1))
	if i < len(bins)-1:
		diff[i] = 0.5 * (bins[i] + bins[i+1])
	else:
		diff[i] = bins[i] + (bins[i] - bins[i-1])

res06.to_csv(outpath_preproc_inc  + 'Percentile_2006.csv')

array06 = array *1.
bins06 = bins *1.
ubins06 = ubins *1.
diff06 = diff *1.
ntot06 = ntot * 1

if plot_exp:
	plt.clf()
	sns.set_style("whitegrid")
	plt.plot(ubins16, perc16, color = 'darkblue', label = '2016')
	plt.plot(ubins11, perc11, color = 'blue', label = '2011')
	plt.plot(ubins06, perc06, color = 'lightblue', label = '2006')
	plt.axhline(50, color='k', ls='dotted')
	plt.legend(loc = 'upper left')
	plt.xlabel('Weekly Income')
	plt.ylabel('Percentile')
	plt.savefig(outpath_preproc_inc  + 'Perc_income.png')


fit = interp1d(perc06, ubins06, kind = 'linear')
med06 = np.round(fit(50).mean(),1)
fit = interp1d(perc11, ubins11, kind = 'linear')
med11 = np.round(fit(50).mean(),1)
fit = interp1d(perc16, ubins16, kind = 'linear')
med16 = np.round(fit(50).mean(),1)

print("Median 2006:", med06)
print("Median 2011:", med11)
print("Median 2016:", med16)


# Calculate weight matrix and percent of population for each census year:		
weights06, percpop06, med06 = calc_weights(bins06, ubins06, perc06, array06)
weights11, percpop11, med11 = calc_weights(bins11, ubins11, perc11, array11)
weights16, percpop16, med16 = calc_weights(bins16, ubins16, perc16, array16)


def print_incbins(med):
	print("Very low income (<50% median inc): <", np.round(med/2.).astype(int))
	print("Low income (50% - 80% median inc):  ", np.round(0.5 * med).astype(int), ' to ', np.round(0.8 * med).astype(int))
	print("Moderate income (80 - 120% median inc):  ", np.round(0.8 * med).astype(int), ' to ',  np.round(1.2 * med).astype(int))
	print("High income (120% - 200% median inc):  ", np.round(1.2 * med).astype(int), ' to ',  np.round(2. * med).astype(int))
	print("Very high income (>200% median inc):  >", np.round(2. * med).astype(int))


if plot_exp:
	widths = 2. * (diff06-bins06) - 20
	plt.clf()
	fig, ax = plt.subplots()
	#sns.barplot(diff06.astype(int), y=array06/ntot06 * 100, facecolor='lightblue', ax = ax)
	plt.bar(x = bins06, height = array06/ntot06 * 100, width=widths, align = 'edge', color='lightblue', edgecolor = 'darkblue')
	#plt.axvline(med06, color = 'k')
	plt.axvline(med06, color='k', label='median', ls='dotted')
	plt.axvline(med06/2., color = 'r', ls = '--',label='0.5 median')
	plt.axvline(0.8* med06, color = 'b', ls = '--',label='0.8 median')
	plt.axvline(1.2* med06, color = 'b', ls = '--',label='1.2 median')
	plt.axvline(2.* med06, color = 'r', ls = '--',label='2 median')
	plt.xlim(0, bins06[-1] + 0.5 * widths[-1])
	hmax = np.max(array06/ntot06 * 100)
	xpos = 0.5 * np.asarray([0.5, (0.5 + 0.8), (0.8 + 1.2), (1.2 + 2.), (2 + 2.5)]) * med06
	for i, txt in enumerate(percpop06):
		plt.text(xpos[i],hmax, s= str(np.round(txt).astype(int)) + '%', horizontalalignment='center') 
	plt.legend()
	plt.xlabel('Weekly Income')
	plt.ylabel('Population [%]')
	plt.savefig(outpath_preproc_inc  + 'Income_2006.png')

	widths = 2. * (diff11-bins11) - 20
	plt.clf()
	fig, ax = plt.subplots()
	#sns.barplot(diff06.astype(int), y=array06/ntot06 * 100, facecolor='lightblue', ax = ax)
	plt.bar(x = bins11, height = array11/ntot11 * 100, width=widths, align = 'edge', color='lightblue', edgecolor = 'darkblue')
	#plt.axvline(med06, color = 'k')
	plt.axvline(med11, color='k', label='median', ls='dotted')
	plt.axvline(med11/2., color = 'r', ls = '--',label='0.5 median')
	plt.axvline(0.8* med11, color = 'b', ls = '--',label='0.8 median')
	plt.axvline(1.2* med11, color = 'b', ls = '--',label='1.2 median')
	plt.axvline(2.* med11, color = 'r', ls = '--',label='2 median')
	plt.xlim(0, bins11[-1] + 0.5 * widths[-1])
	hmax = np.max(array11/ntot11 * 100)
	xpos = 0.5 * np.asarray([0.5, (0.5 + 0.8), (0.8 + 1.2), (1.2 + 2.), (2 + 2.5)]) * med11
	for i, txt in enumerate(percpop11):
		plt.text(xpos[i],hmax, s= str(np.round(txt).astype(int)) + '%', horizontalalignment='center') 
	plt.legend()
	plt.xlabel('Weekly Income')
	plt.ylabel('Population [%]')
	plt.savefig(outpath_preproc_inc  + 'Income_2011.png')

	widths = 2. * (diff16-bins16) - 20
	plt.clf()
	fig, ax = plt.subplots()
	#sns.barplot(diff06.astype(int), y=array06/ntot06 * 100, facecolor='lightblue', ax = ax)
	plt.bar(x = bins16, height = array16/ntot16 * 100, width=widths, align = 'edge', color='lightblue', edgecolor = 'darkblue')
	#plt.axvline(med06, color = 'k')
	plt.axvline(med16, color='k', label='median', ls='dotted')
	plt.axvline(med16/2., color = 'r', ls = '--',label='0.5 median')
	plt.axvline(0.8* med16, color = 'b', ls = '--',label='0.8 median')
	plt.axvline(1.2* med16, color = 'b', ls = '--',label='1.2 median')
	plt.axvline(2.* med16, color = 'r', ls = '--',label='2 median')
	plt.xlim(0, bins16[-1] + 0.5 * widths[-1])
	hmax = np.max(array16/ntot16 * 100)
	xpos = 0.5 * np.asarray([0.5, (0.5 + 0.8), (0.8 + 1.2), (1.2 + 2.), (2 + 2.5)]) * med16
	for i, txt in enumerate(percpop16):
		plt.text(xpos[i],hmax, s= str(np.round(txt).astype(int)) + '%', horizontalalignment='center') 
	plt.legend()
	plt.xlabel('Weekly Income')
	plt.ylabel('Population [%]')
	plt.savefig(outpath_preproc_inc  + 'Income_2016.png')


### Write results of weights to file
np.savetxt(outpath_preproc_inc +'weights06.csv', weights06, delimiter = ',')
np.savetxt(outpath_preproc_inc +'weights11.csv', weights11, delimiter = ',')
np.savetxt(outpath_preproc_inc +'weights16.csv', weights16, delimiter = ',')
#for loading data use np.loadtxt('weights...csv')


###
# Apply weights to calculate new income bins
# Note that "TOTAL" in input income data is more than sum of individual income bins of the input data (TOTAL = Total population including non-income?)
# Thus, the new 5 income bins are therefore given in percentage (each bin divided by sum of income bins) rather than "TOTAL"
print('Calculating and saving new income bins...')
dfnew06 = lin_transform(inc06, weights06, newcol_names = ['VERY_LOW', 'LOW', 'MID', 'HIGH', 'VERY_HIGH'], decround =4) 
dfnew06['TOTAL'] = inc06['Total']
dfnew06.rename(columns={"ASGC_CODE7": "SA1_CODE7"}, inplace = True)
dfnew06.to_csv(outpath_preproc_inc  + 'NEWPERC_INC06.csv', index = False)  

dfnew11 = lin_transform(inc11, weights11, newcol_names = ['VERY_LOW', 'LOW', 'MID', 'HIGH', 'VERY_HIGH'], decround =4) 
dfnew11['TOTAL'] = inc11['Total']
dfnew11.to_csv(outpath_preproc_inc  + 'NEWPERC_INC11.csv', index = False)  

dfnew16 = lin_transform(inc16, weights16, newcol_names = ['VERY_LOW', 'LOW', 'MID', 'HIGH', 'VERY_HIGH'], decround =4) 
dfnew16['TOTAL'] = inc16['Total']
dfnew16.to_csv(outpath_preproc_inc  + 'NEWPERC_INC16.csv', index = False)  

print('Preprocessing Income data finished')