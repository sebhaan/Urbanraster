# Preprocessing geodata and selecting regions
"""
Author: Sebastian Haan
Affiliation: Sydney Information Hub, The University of Sydney
"""

import os 
import numpy as np
import geopandas as gpd
import pandas as pd
import yaml


########## Settings


with open('settings.yaml') as f:
	cfg = yaml.safe_load(f)
for key in cfg:
	globals()[str(key)] = cfg[key]

# parameters below defined in settings.yaml
#outpath_preproc_geo = '../Data/Preprocessed/'
#preprocess_all = True # formating of entire NSW geo data


if not os.path.exists(outpath_preproc_geo):
	os.makedirs(outpath_preproc_geo)


if preprocess_syd:
	### Select Sydney metropolitan region  based on 2016 definition:
	reg_str = 'Greater Sydney'
	print("Filtering 2016 ...")
	infile = inpath + 'SA1_Data_2016/1270055001_sa1_2016_aust_shape/SA1_2016_AUST.shp'
	df = gpd.read_file(infile)
	syd16 = df[df.GCC_NAME16 == reg_str].copy()
	syd16 = syd16[['SA1_7DIG16', 'AREASQKM16', 'geometry']]
	syd16.rename(columns={"SA1_7DIG16": "SA1_CODE7", "AREASQKM16": "AREASQKM"}, inplace = True)

	# Get boundary shape of Sydney metropolitan
	temp = syd16[['geometry']].copy()
	temp['SYD'] = 1
	sydshape = temp.dissolve(by = 'SYD')
	sydshape = sydshape[['geometry']]
	sydshape.to_file(outpath_preproc_geo + 'SYD_SHAPE.gpkg', driver = 'GPKG')

	# Read in again to remove multi egomatry format
	sydshape = gpd.read_file(outpath_preproc_geo + 'SYD_SHAPE.gpkg')
	syd16 = syd16.to_crs({'init': 'epsg:3577'})
	syd16.to_file(outpath_preproc_geo + 'SYD16.gpkg', driver = 'GPKG', index = False)
	# Use this Sydney outer shape to crop and define other census:
	#sydshape2 = syd16[['geometry']].unary_union 



	infile = inpath + "/Preprocessed/SYD06_QGISclip.gpkg"
	df = gpd.read_file(infile)
	syd06 = df[['CD_CODE06', 'geometry']].copy()
	syd06 = syd06.to_crs({'init': 'epsg:3577'})
	syd06["AREASQKM"] = syd06.area * 1e-6
	syd06.rename(columns={"CD_CODE06": "SA1_CODE7"}, inplace = True)
	syd06.to_file(outpath_preproc_geo + 'SYD06.gpkg', driver = 'GPKG', index = False)	

	#2011
	print("Filtering 2011 ...")
	infile = inpath + "/Preprocessed/SYD11_QGISclip.gpkg"
	df = gpd.read_file(infile)
	syd11 = df[['SA1_7DIG11', 'geometry']].copy()
	syd11 = syd11.to_crs({'init': 'epsg:3577'})
	syd11["AREASQKM"] = syd11.area * 1e-6
	syd11.rename(columns={"SA1_7DIG11": "SA1_CODE7"}, inplace = True)
	syd11.to_file(outpath_preproc_geo + 'SYD11.gpkg', driver = 'GPKG', index = False)	


if preprocess_all:
	print("Processing 2016  ...")
	infile = inpath + 'SA1_Data_2016/1270055001_sa1_2016_aust_shape/SA1_2016_AUST.shp'
	df = gpd.read_file(infile)
	df = df[['SA1_7DIG16', 'AREASQKM16', 'geometry']]
	df.rename(columns={"SA1_7DIG16": "SA1_CODE7", "AREASQKM16": "AREASQKM"}, inplace = True)
	df = df[df.geometry.notnull()]
	df = df.to_crs({'init': 'epsg:3577'})
	df.to_file(outpath_preproc_geo + 'SA1_2016_AUST_meters.gpkg', driver = 'GPKG', index = False)

	#2011
	print("Processing 2011  ...")
	infile = inpath + "/SA1_Data_2011/1270055001_sa1_2011_aust_shape/SA1_2011_AUST.shp"
	df = gpd.read_file(infile)
	df = df[['SA1_7DIG11', 'geometry']].copy()
	df = df[df.geometry.notnull()]
	df = df.to_crs({'init': 'epsg:3577'})
	df["AREASQKM"] = df.area * 1e-6
	df.rename(columns={"SA1_7DIG11": "SA1_CODE7"}, inplace = True)
	df.to_file(outpath_preproc_geo + 'SA1_2011_AUST_meters.gpkg', driver = 'GPKG', index = False)	

	#2006
	print("Processing 2006  ...")
	infile = inpath + "/CCD_Data_2006/1259030002_cd06answ_shape/CD06aNSW.shp"
	df = gpd.read_file(infile)
	df = df[['CD_CODE06', 'geometry']].copy()
	df = df[df.geometry.notnull()]
	df = df.to_crs({'init': 'epsg:3577'})
	df["AREASQKM"] = df.area * 1e-6
	df.rename(columns={"CD_CODE06": "SA1_CODE7"}, inplace = True)
	df.to_file(outpath_preproc_geo + 'SA1_2006_NSW_meters.gpkg', driver = 'GPKG', index = False)	

print('Preprocessing Geodata finished')