#  Main run script for running all data processing routines

"""
version: 1.0
Author: Sebastian Haan
Affiliation: Sydney Information Hub, The University of Sydney

This script runs the main data preprocessing, rasterisation, and visualisation processes

Please change settings in the file settings.yaml
or change function parameters in script below
"""

# Import standard libraries
import os
import glob
import numpy as np
import subprocess
import geopandas as gpd
import pandas as pd
import yaml

# import custom scripts
from lib.rasterize import *
from lib.visual import *

### Import setting parameters and names:
with open('settings.yaml') as f:
	cfg = yaml.safe_load(f)
for key in cfg:
	globals()[str(key)] = cfg[key]


###### Preprocessing Geo Boundaries (Optional)
if process_geodata:
	import preprocess_geodata

###### Preprocessing Income Input Data (Optional)
if process_income:
	import preprocess_income


###### Rasterization of Data to Geo-Tiff files
# See also rasterize.py
poly_syd06 = inpath_preprocessed + name_poly06
data_syd06 = inpath_preprocessed + name_data06
poly_syd11 = inpath_preprocessed + name_poly11
data_syd11 = inpath_preprocessed + name_data11
poly_syd16 = inpath_preprocessed + name_poly16
data_syd16 = inpath_preprocessed + name_data11
# For each year combine feature data with polygon shape and run rasterization
# 2006 
fname = inpath_preprocessed + 'SYD06mask_COMB.gpkg'
df06, features06 = combine_geodata(fname_poly = poly_syd06 , fname_data = data_syd06, 
	featurelist = features, polymask = mask, outfile = fname, indexname = indexname)
poly2raster(fname, outpath = outpath06, featurelist = features06, polymask = mask, pixsize = pixelsize)
# 2011
fname = inpath_preprocessed + 'SYD11mask_COMB.gpkg'
df11, features11 = combine_geodata(fname_poly = poly_syd11 , fname_data = data_syd11 , 
	featurelist = features, polymask = mask, outfile = fname, indexname = indexname)
poly2raster(fname, outpath = outpath11, featurelist = features11, polymask = mask, pixsize = pixelsize)
# 2016
fname = inpath_preprocessed + 'SYD16mask_COMB.gpkg'
df16, features16 = combine_geodata(fname_poly = poly_syd16 , fname_data = data_syd16 , 
	featurelist = features, polymask = mask, outfile = fname, indexname = indexname)
poly2raster(fname, outpath = outpath16, featurelist = features16, polymask = mask, pixsize = pixelsize)

# CONTINUE TESTING FROM HERE  

###### Calculate gain/loss for each feature over time
outpath_change = '../Results/Income_change/'
features.remove('TOTAL')

if calc_change | calc_change2:
	if not os.path.exists(outpath_change):
		os.makedirs(outpath_change)
	for i, feature in enumerate(features):
		## Calcuate income percentage changes for the three different time periods:
		if calc_change:
			print("Calculating Change rasters for " + feature + ' ...')
			in06 = outpath06 + 'raster_' + str(int(pixelsize)) + 'm_' + feature + '.tif'
			in11 = outpath11 + 'raster_' + str(int(pixelsize)) + 'm_' + feature + '.tif'
			in16 = outpath16 + 'raster_' + str(int(pixelsize)) + 'm_' + feature + '.tif'
			rasterdiff(in11, in06, outfile = outpath_change + 'rasterchange_2011-2006_'+ feature + '_' +str(int(pixelsize)) + 'm.tif')
			rasterdiff(in16, in11, outfile = outpath_change + 'rasterchange_2016-2011_'+ feature + '_'+ str(int(pixelsize)) + 'm.tif')
			rasterdiff(in16, in06, outfile = outpath_change + 'rasterchange_2016-2006_'+ feature + '_'+ str(int(pixelsize)) + 'm.tif')
		if calc_change2:
			## Calcuate income population changes for the three different time periods:
			# First calcuate population number in each income bin:
			fname_pop06 = outpath06 + 'raster_pop_' + str(int(pixelsize)) + 'm_' + feature + '.tif'
			fname_pop11 = outpath11 + 'raster_pop_' + str(int(pixelsize)) + 'm_' + feature + '.tif'
			fname_pop16 = outpath16 + 'raster_pop_' + str(int(pixelsize)) + 'm_' + feature + '.tif'
			norm06 = outpath06 + 'raster_' + str(int(pixelsize)) + 'm_' + 'POPDENS_100m.tif'
			norm11 = outpath11 + 'raster_' + str(int(pixelsize)) + 'm_' + 'POPDENS_100m.tif'
			norm16 = outpath16 + 'raster_' + str(int(pixelsize)) + 'm_' + 'POPDENS_100m.tif'
			rasterprod(in06, norm06, outfile = fname_pop06)
			rasterprod(in11, norm11, outfile = fname_pop11)
			rasterprod(in16, norm16, outfile = fname_pop16)
			# Now calcuate poplation change
			rasterdiff(fname_pop11, fname_pop06, outfile = outpath_change + 'rasterchange_pop_2011-2006_'+ feature + '_'+ str(int(pixelsize)) + 'm.tif', norm = True)
			rasterdiff(fname_pop16, fname_pop11, outfile = outpath_change + 'rasterchange_pop_2016-2011_'+ feature + '_'+ str(int(pixelsize)) + 'm.tif', norm = True)
			rasterdiff(fname_pop16, fname_pop06, outfile = outpath_change + 'rasterchange_pop_2016-2006_'+ feature + '_'+ str(int(pixelsize)) + 'm.tif', norm = True)



###### Visualisation (optional)
# See also visual.py
if make_plots2d:
	# Make 2D plots of all tif files in results folders: outpath_change, outpath06, outpath11
	list_all = glob.glob(outpath_change + '*.tif')
	list_all.extend(glob.glob(outpath06 + '*.tif'))
	list_all.extend(glob.glob(outpath11 + '*.tif'))
	list_all.extend(glob.glob(outpath16 + '*.tif'))
	# crs for unprojected coordinate system Lat/Lng
	outputEPSG = 'EPSG:4326'
	# Ceraet out files with projection  in meters
	list_all2 =  [x.replace('.tif', '_epsg4326.tif') for x in list_all]
	# Create corresponding output image names
	list_fname_out = [x.replace('.tif', '.png') for x in list_all]
	list_fname_out_zoom = [x.replace('.tif', '_zoom.png') for x in list_all]
	print("Creating 2D map and zoom maps ...")
	for i in range(len(list_all)):
		# Fisrt transform to unprojected coordinate system in Lat/Lng
		fname_raster = list_all[i]
		fname_raster2 = list_all2[i]
		fname_out = list_fname_out[i]
		fname_out_zoom = list_fname_out_zoom[i]
		print("Plotting 2D images for rasterfile " + fname_raster2 + " ...")
		transform_crs(fname_raster, fname_raster2, crs_out = outputEPSG)
		# Make image of entire region:
		simplemap2d(fname_raster2, fname_out, logscale = False, show = False)   
		# Make image of zoomed-in region (sepcified in zbox parameter):
		simplemap2d(fname_raster2, fname_out_zoom, zoombox = zbox, show = False)  

if make_webmap3d:
	### Create interactive 3D webmap
	# First, enable Mapbox for basemap layers
	try:
		# enable mapbox, read key form file:
		keyfile = open(fname_mbox,"r") 
		key_mbox = keyfile.read()
		keyfile.close()
	except:
		key_mbox = None
		print("WARNING: Failed to setup Mapbox from keyfile.") 
		print("Continuing without mapbox basemap layers or set before in terminal with 'export MAPBOX_API_KEY=<mapbox-key-here>.' ")
	# Run creation of 3D webmap
	webmap3d(infname_3D, outpath_3D, outname_3D, featurename = featurename_3D, zfilter = zfilter_3D, nodataval = -9999, cmap= 'viridis', mbkey = key_mbox)
	# infname_3D = '../Results/Income_change/rasterchange_2016-2006_VERY_LOW_100m.tif'  
	# outname_3D = 'demo_rasterchange_2016-2006_VERY_LOW_100m'  
	# featurename_3D  = 'Income_Change' 
	# zfilter_3D = None                                                                                                                           
	# webmap3d(infname_3D, outpath_3D, outname_3D, featurename = featurename_3D, zfilter = zfilter_3D, nodataval = -9999, cmap= 'viridis', mbkey = key_mbox)

print("FINISHED")

"""
add here other options and comments:

How to make gifs from images:
convert -delay 100 Popdens06.png Popdens11.png Popdens16.png Popdens.gif
"""