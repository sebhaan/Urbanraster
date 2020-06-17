# Visualisation of raster data, eiter as 2D or interactive web 3D using pydeck 
# (python wrapper for deck.gl, see https://deckgl.readthedocs.io/en/latest/?)
# optional with Mapbox baselayers: run in terminal export MAPBOX_API_KEY=<mapbox-key-here>


"""
Author: Sebastian Haan
Affiliation: Sydney Information Hub, The University of Sydney

Comments:
- Setup mapbox key (run export MAPBOX_API_KEY=<mapbox-key-here>), or save in keyfile (see settings.yaml)
see also https://docs.mapbox.com/help/troubleshooting/how-to-use-mapbox-securely/
- 3D visualsiation requires pydeck; installation: pip install pydeck 
- make gif from multiple pictures, e.g.: convert -delay 100 Popdens06.png Popdens11.png Popdens16.png Popdens.gif
- other recommended tools for vsiualisation: QGIS (open-source), ArcGIS, folium (python open source)
"""

import os
import subprocess
import numpy as np
import pandas as pd
import pydeck as pdk
import rasterio
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors
from matplotlib.colors import LogNorm



# First transform image into Lat/Lng coorindate system
def transform_crs(fname_in, fname_out, crs_out = 'EPSG:4326'):
    """transforms raster coordinate system into new crs
    :param fname_in: input path and filename 
    :param fname_in: ouput path and filename
    :param crs_out: string of ccordinate reference system (crs) in EPSG fromat e.g. 'EPSG:4326'
    """
    str_op = "gdalwarp -overwrite -srcnodata '-9999' -dstnodata '-9999' -q -t_srs "
    cmd = subprocess.call(str_op + crs_out + ' ' + fname_in + ' ' + fname_out, shell=True)

def raster2csv(input_file, path_out, fname_out, nodataval = -9999, zfilter = None):
    """transforms raster coordinate system into new crs
    :param input_file: input path and filename of raster tif file ()
    :param path_out: path for output filen
    :param fname_out: output filename, should end with .csv
    :param nodataval: exclude valuse of nodata
    :param zfilter: values below treshold value are excluded

    saves csv file with header X,Y,Z
    """
    if not os.path.exists(path_out):
        os.makedirs(outpath)
    str_op = "gdal_translate -r average -a_nodata " + str(nodataval) + " -epo -unscale -q -of xyz -co ADD_HEADER_LINE=YES -co COLUMN_SEPARATOR=',' "
    if zfilter is None: 
        cmd = subprocess.call(str_op + input_file + ' ' + path_out + fname_out, shell=True)
    else:
        # Write temporary file first and then filter rows that are above treshold and are finite
        cmd = subprocess.call(str_op + input_file + ' ' + path_out + 'temp.csv', shell=True)
        if cmd == 0:
            temp = pd.read_csv(path_out + 'temp.csv')
            temp = temp[(temp.Z != nodataval) & (temp.Z > zfilter) & (~temp.Z.isnull()) & (~temp.X.isnull()) & (~temp.Y.isnull())]
            temp.to_csv(path_out + fname_out, index = False)
            # Clean up:
            os.remove(path_out + 'temp.csv')
    if cmd != 0:
        print('raster2csv failed!')

def simplemap2d(fname_in, fname_out, zoombox = None, logscale = False, nodataval = -9999, show = False, cmap= 'viridis', dpi = 300):
    """plot image in static 2D and save as png
    :param fname_in: input path and filename of raster tif file 
    :param fname_out: path and filenmae for output file (should end in .png)
    :param zoombox: [min_lng, max_lng, min_lat, max_lat]
    :param nodataval: exclude valuse of nodata
    :param show: if True plot in matplotlib window
    :param cmap: matplotlub color map to use, default 'viridis'
    :param dpi: resolution in dots per inch, default 300
    """
    # rasterio imshow version but can't handle nodata correction:
    #rasterio.plot.show(fname_in, cmap = cmap) #
    # Use instead matplotlib version
    raster = rasterio.open(fname_in)
    rasterdata = raster.read(1) 
    # remove nodata values and replcae wigth nan values (ignored by matplotlib)
    rasterdata[rasterdata == nodataval] = np.nan
    if logscale & (np.nanmin(rasterdata) <= 0):
        #logscale = False
        print('simplemap2d logscale WARNING: Data include values smaller than zero.')            
    # Set extent to bounding box coordinates:
    bb = raster.bounds
    ext=[bb[0],bb[2],bb[1],bb[3]]
    raster.close()
    plt.clf()
    if logscale:
        plt.imshow(rasterdata, cmap = cmap, extent = ext, aspect ='equal', norm=LogNorm())
    else: 
        plt.imshow(rasterdata, cmap = cmap, extent = ext, aspect ='equal')
    if zoombox is not None:
        zoombox = np.asarray(zoombox)
        plt.xlim(zoombox[0], zoombox[1])
        plt.ylim(zoombox[2], zoombox[3])
    #plt.axes().set_aspect('equal')
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(fname_out, dpi=dpi)
    if show: 
        plt.show()

def webmap3d(input_file, path_out, fname_out, featurename = 'Z', zfilter = None, nodataval = -9999, cmap= 'viridis', mbkey = None):
    """Creates interactive 3D Webmap using pydeck (wrapper for deck.gl), currently limited to positive values only
    Use carefully, still in testing
    Includes following main processing stesp:
    1) reprojection of cooridnate system to Lng and Lat and extration of grid cell positions in database
    2) Creating webmap with deck.gl
    :param input_file: input path and filename of raster tif file 
    :param path_out: output path, will be also used to save temporary files
    :param fname_out: filenmae for output file (ending.html fill be added automatically)
    :param featurename: Name of feature that is shwon as elevation so that properly labeld in plot, default 'Z' 
    :param zfilter: values below treshold value are excluded
    :param logscale:  
    :param nodataval: exclude valuse of nodata
    :param cmap: matplotlub color map to use, default 'viridis' (others e.g. 'Reds', 'Blues'..)
    :param mbkey: Mapbox key (string), defaults to None if not set
    """
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    # Open raster file
    raster = rasterio.open(input_file)
    # Check if rasterfile is not projected (not in meters buty in Lat Lng)
    if raster.crs.is_projected:
        # If projected, convert to non-projected system for Lat Lng values
        outputEPSG = 'EPSG:4326'
        print('Convert raster coordinate system to ' +  outputEPSG + ' ...')
        fname_raster2 = path_out + fname_out + 't_crsproj.tif'
        transform_crs(input_file, fname_raster2, crs_out = outputEPSG)
        raster = rasterio.open(fname_raster2)
    else:
        fname_raster2 = input_file
    # Read in raster coordinate info
    bbox = raster.bounds
    view_lon = 0.5* (bbox[2] + bbox[0])
    view_lat = bbox[1]
    print('Transform raster tif to csv file ...')
    fname_csv ='temp_rasterdata.csv'
    raster2csv(fname_raster2, path_out = path_out, fname_out = fname_csv, nodataval= nodataval, zfilter = zfilter)
    # Read in data in Pandas dataframe
    print('Processing Data ...')
    data = pd.read_csv(path_out +fname_csv)
    #offset = np.nanmin(data.Z.values)
    #if offset > 0.: offset =0
    el_scale = abs(1000/np.percentile(data.Z.values,  90))
    el_range = [np.nanmin(data.Z.values) * el_scale, np.nanmax(data.Z.values) * el_scale] 
    # Apply color map
    cmap = plt.get_cmap(cmap)
    # Clip and normalise colorscheme:  
    z99 = np.percentile(data.Z.values,99)
    colval = data.Z.values * 1.
    colval[colval > z99] = z99
    colval /= colval.max()
    colrgb = cmap(colval) * 255
    # Convert colors into RGBA values
    colrgb_str = [list(colx) for colx in colrgb] 
    data['color'] = colrgb_str
    #rename layers for better labeling:
    data.rename(columns={"X": "LNG", "Y": "LAT", "Z": featurename}, inplace = True) 
    print('Creating html page ...')
    # Deck Layer definition, using 'GridCellLayer'
    layer = pdk.Layer(
        'GridCellLayer',
        data,
        get_position='[LNG, LAT]',
        auto_highlight=True,
        pickable=True,
        cellsize=100,
        elevation_scale=el_scale,
        elevation_range=el_range,
        get_elevation= featurename,
        get_color='color',
        extruded=True,               
        coverage=1)
    # Set the viewport location
    view_state = pdk.ViewState(
        longitude=view_lon,
        latitude=view_lat,
        zoom=8,
        min_zoom=5,
        max_zoom=15,
        pitch=40.5,
        bearing=-27.36)
    # Render
    r = pdk.Deck(
        layers=[layer], 
        initial_view_state=view_state,
        mapbox_key = mbkey)
    r.to_html(path_out + fname_out + '.html', notebook_display=False)
    raster.close()
    # Cleaning up temporary files if required (comment out):
    #os.remove(fname_raster2)
    #os.remove(path_out +fname_csv)
