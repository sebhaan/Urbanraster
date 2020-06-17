# Rasterisation Script
import os
import numpy as np
import subprocess
import geopandas as gpd
import pandas as pd

"""
Author: Sebastian Haan
Affiliation: Sydney Information Hub, The University of Sydney

Comments:
For computational speed most functions in this script make use of the gdal libraries using system commands.
There exist various python bindings for gdal (such as osgeo), but seem to be at the current state not as reliable or flexible enough.
"""

def poly2raster(infile, outpath, featurelist, polymask = None, pixsize = 100, nodataval = '-9999', interpol = 'average', crs = 'epsg:3577'):
	""" Generates rasterfiles in GeoTiff format from polygon shapefile for each feature in featurelist.  
	Rastergeneration is performed with gdal in two steps: 
	1) Upsampled raster generation at four times raster resolution
	2) Downsampling and interpolation to final raster

	INPUT
	:param infile: Path and filename of input polygon file (in .shp or .gpkg format); need to inlude default column with 'geometry'
	:param outpath: Path name to output directory
	:param featurelist: List of Features (columns) name of feature to rasterize, in string format ['feature1', 'feature2']
	:param polymask: Path+name of mask shapefile (.shp or .gpkg format) that is used to clip raster according to shapefile geometry
	:param pixsize: pixelsize in meters (same for x and y), default 100m x 100m
	:param nodataval: Value for No-data entries (Default: -9999)
	:param interpol: Raster Interpolation option ('average' (recommended), 'near', 'bilinear', 'cubic', cubicspline) 
	:param crs: Coordinate reference system (Default 'epsg:3577' - Australian Albers meters) 	
	"""

	### Check if output path exists, if not create path
	if not os.path.exists(outpath):
		os.makedirs(outpath)

	### Reproject input polygon file to meter system
	print("Reading in polygon file....")
	poly = gpd.read_file(infile)
	# Read coordinate reference system (crs) of source:
	crs_current = poly.crs
	crs_meter = {'init': crs}
	if crs_current != crs_meter:
		print('Converting input file to meters...')
		poly = poly.to_crs({'init': crs})
		poly = poly[featurelist + ['geometry']]
		fname_poly = outpath + 'poly_temp.shp'
		poly.to_file(fname_poly)
		# Flag to clean and renove this temporary polygon file later again:
		clean_polytemp = True
	else:
		fname_poly = infile
		clean_polytemp = False

	###Create raster image for each feature in featurelist
	xres = yres = str(int(pixsize))
	xres_up = yres_up = str(int(pixsize // 4))
	srcfile = fname_poly
	nfeature = len(featurelist)
	dstfile_temp = outpath + 'temp.tif'
	dstfile_temp2 = outpath + 'temp2.tif'

	for i, feature in enumerate(featurelist):
		tempfile = dstfile_temp
		print('Rasterizing feature ' + feature + ' ...')
		# Define raster output filename:
		dstfile = outpath + 'raster_' + str(int(pixsize)) + 'm_' + feature + '.tif'
		str_rasterize_options =  '-a ' + feature  + ' -a_nodata ' + nodataval + ' -tr ' + xres_up + ' ' + yres_up + ' -ot Float64 '
		# Create upsampled raster file
		cmd = subprocess.call('gdal_rasterize ' + str_rasterize_options + srcfile + ' ' + dstfile_temp, shell=True)
		if cmd == 0:
			if polymask is not None:
				# Crop raster to cutline and overwite temporary file with cropped file
				print("Cropping of raster with polygon mask ...")
				cmd_mask = subprocess.call('gdalwarp -srcnodata ' + nodataval + ' -dstnodata ' + nodataval + 
					' -crop_to_cutline -cutline ' + polymask + ' ' + dstfile_temp + ' ' + dstfile_temp2, shell=True)
				tempfile = dstfile_temp2
			# if upsample sucessfull start with interpolation to final downsampled raster
			str_warp_options = '-tr ' + xres + ' ' + yres + ' -srcnodata ' + nodataval + ' -dstnodata ' + nodataval + ' -r ' + interpol + ' '
			cmd2 = subprocess.call('gdalwarp ' + str_warp_options + tempfile + ' ' + dstfile, shell=True)
			if cmd2 == 0: 
				print('Rasterfile ' + str(i+1) + ' created out of ' + str(nfeature) + ' : ' + dstfile)
				# Clean up and remove temporary upsampled file 
				#print('Cleaning up...')
				os.remove(dstfile_temp)
			else:
				print('Failed to create downsampled rasterfile with gdalwarp.')
			if cmd_mask == 0:
					os.remove(dstfile_temp2)
		else:
			print('Failed to create rasterfile with gdal_rasterize.')
	if clean_polytemp:
		print("Cleaning up ...")
		os.remove(outpath + 'poly_temp.shp')
		os.remove(outpath + 'poly_temp.cpg')
		os.remove(outpath + 'poly_temp.dbf')
		os.remove(outpath + 'poly_temp.prj')
		os.remove(outpath + 'poly_temp.shx')
	#print('FINISHED')
	

def combine_geodata(fname_poly, fname_data, featurelist, polymask = None,  outfile = None, indexname = 'SA1_7DIG11'):
	"""Combines feature data with geopolygons

	INPUT
	:param fname_poly: Directory Path and filname for the regions polygons (format either .gpkg or .shp)
	:param fname_data: Data table with features (columns) for each of the region (rows). Format as .csv file
	:param featurelist: list of feature names as appear in header of fname_data, i string format e.g. ['feature1', 'feature2', ... ]
	:param polymask: Path+filename of mask shapefile (.shp or .gpkg format) that is used to clip regions of source file
	:param outfile:  Directory Path and filename for combined output file (optional) 
	:param indexname: String, name of index that is shared between polygons data and feature data
	Both files, polygon file and feature data, need to have same index in first column with leable in headre as indexname.
	Note that alogoritthm selects only regions which match index, others will be disregarded

	RETURN
	Geopandas dataframe
	Feature list
	"""
	poly = gpd.read_file(fname_poly)
	poly[indexname] = poly[indexname].astype(str)
	crs_current = poly.crs
	if polymask is not None:
		#Select only polygons that intersect with mask (hard-crop to cutline applied later in poly2raster):
		print("Clipping source file polygons that intersect with mask ... ")
		gpd_mask = gpd.read_file(polymask)
		if gpd_mask.crs != crs_current:
			# If crs of mask is different from source, convert mask's crs to source crs:
			gpd_mask = gpd_mask.to_crs(crs_current)
		join = gpd.sjoin(gpd_mask, poly, how = 'inner',op='intersects') # fastest method for intersection since using rtree internally
		poly = poly.loc[join.index_right]
		#poly = poly[poly.geometry.intersects(gpd_mask.geometry[0])] # alterbative to sjoin but very slow
	df = pd.read_csv(fname_data) 
	df[indexname] = df[indexname].astype(str)
	df = df[[indexname] + featurelist]
	# Merge the two files based on common index name:
	comb = poly.merge(df, how = 'left', on = indexname)
	# Check for non-valid data (e.g. if not all regions have data)
	null = len(comb[comb[featurelist[0]].isnull()]) 
	if null > 0:
		print('Warning: ' + str(int(null)) + ' regions with non-valid data for feature ' + featurelist[0])
	header = list(comb)
	if 'TOTAL' and 'AREASQKM' in header:
		# Calculate population density per 100m x 100m if available
		print('''Calculating Population Density per 100m x 100m and adding to featurelist as 'POPDENS_100m' ''')
		comb["POPDENS_100m"] = comb.TOTAL.values / (comb.AREASQKM.values * 100) 
		featurelist = featurelist + ['POPDENS_100m']
		featurelist.remove('TOTAL')
	print('Saving file to ' + outfile + ' ...')
	comb = comb[[indexname] + featurelist + ['geometry']]
	if outfile is not None:
		comb.to_file(outfile, driver = 'GPKG', index = False)
	return comb, featurelist


def rasterdiff(name_raster1, name_raster2, outfile, norm = False):
	""" Subtract raster2 from raster 1 and applies optional normalisation using another rastser
	:param raster1: path+fielname for input raster 1
	:param raster2: path+fielname for input raster 2, same shape as raster 1
	:param outfile: path+fielname for output raster
	:param norm: calculate relative chnage
	"""
	# example: gdal_calc.py -A input.tif -B input2.tif --NoDataValue=-9999 --outfile=result.tif --calc="(A+B)/2"
	dstfile = outfile
	if norm:
		str_operation = " --overwrite --quiet --NoDataValue=-9999 --calc='divide(A-B,B, out=zeros_like(A)-9999, where=(A>-9999) & (B>0))'" 
		cmd = subprocess.call("gdal_calc.py -A " + name_raster1 + " -B " + name_raster2 + " --outfile=" + dstfile + str_operation, shell=True)
	else:
		str_operation = " --overwrite --quiet --NoDataValue=-9999 --calc='(A-B) * (A>-9999) * (B>-9999)'"
		cmd = subprocess.call("gdal_calc.py -A " + name_raster1 + " -B " + name_raster2 + " --outfile=" + dstfile + str_operation, shell=True)
	if cmd != 0:
		print("rasterdiff failed!")


def rasterprod(name_raster1, name_raster2, outfile):
	""" Subtract raster2 from raster 1 and applies optional normalisation using another rastser
	:param raster1: path+fielname for input raster 1
	:param raster2: path+fielname for input raster 2, same shape as raster 1
	:param outfile: path+fielname for output raster
	"""
	# example: gdal_calc.py -A input.tif -B input2.tif --NoDataValue=-9999 --outfile=result.tif --calc="(A+B)/2"
	dstfile = outfile
	str_operation = " --overwrite --quiet --NoDataValue=-9999 --calc='(A* B)* (B>0) * (A>=0)'"
	cmd = subprocess.call("gdal_calc.py -A " + name_raster1 + " -B " + name_raster2 + " --outfile=" + dstfile + str_operation, shell=True)
	if cmd != 0:
		print("rasterdiff failed!")
