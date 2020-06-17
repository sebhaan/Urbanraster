# Urbanraster: Rasterization for Spatial-Temporal Studies

This software transforms data with temporal inconsistent geographic boundary shapes into a consistent set of geo-referenced raster files. This solution allows to correct spatial-temporal inconsistencies as, e.g., found in public census data and provides a data framework to analysis and visualisation spatial-temporal pattern such as the change of income distributions.

Core features are

 - Fast rasterization of feature data with polygon boundaries to regular grids
 - shape boundary interpolation
 - masking of region of interest
 - Automatic calculation of temporal feature changes
 - Generation of Geo-Tiff files for each feature  (optional as csv point data, included in function webmap3D); can be post-processed or visualised in most GIS tools (e.g. QGIS)
 - Basic 2D visualisation of raster files
 - Generation of interactive 3D maps (based on deck.gl)

This software also includes multiple customised scripts for preprocessing:

 - Exploratory data analysis of area sizes and income bins based on ABS census data
 - Transformation of income bins to relative income levels, which allows to compare same income bins over time
 - Multiple preprocessing function for filtering and merging different input data sets


## INSTALLATION AND REQUIREMENTS

Requires Python 3 (tested with Python 3.7.3)

The following libraries have to be installed:

- GDAL 
- numpy
- matplotlib
- seaborn
- scipy
- rasterio
- pandas
- geopandas
- PyYAML

and for 3D visualisation:

- pydeck 

see for more details requirements.txt

Optional: 
The 3D visualisation uses Mapbox basemap layers. Register with Mapbox for your Mapbox access token:
https://account.mapbox.com/access-tokens/ 
(The service is free until a certain level of traffic is exceeded)
Then save your key in a private file, e.g. "mbox.txt" or, alternatively run in terminal  export MAPBOX_API_KEY=<mapbox-key-here> before running Python script



## GETTING STARTED 

1) change the main settings such as filenames and parameters in settings.yaml

2) run python mainscript.py (in ipython "run mainscript")

The rasterization requires at least two files: One tabular file in csv format with preprocessed feature data (one feature per column), and one shapefile (.shp or .gpkg) for the polygon boundaries. Both files need to have the same indexname for matching the corresponding regions. Optional include polyogn to mask region of interest. See settings.yaml.
Example files are include in the folder Data/Preprocessed

Recommended to customise mainscript.py, e.g. just run parts of the script (comment out irrelevant functions or change settings)

The main functions for rasterization can be found in lib/rasterize.py
Visualisation functions are defined in  lib/visual.py

For changing preprocessing scripts see:

 - see proprocess_income.py for exploring and transforming income ABS data
 - see proprocess_income.py for masking geo data and calculation of area sizes

Note that for running preprocessing scripts the filenames for the unprocessed input data has to set in the proprocess_income.py file.


## EXAMPLES


Problem
_______

Change of Statistical Area 1 (SA1) boundaries from one census year to the other:
![SA1 Boundary Change](/demo/boundary.gif)


Raster Result Examples
______________
Chnage of Low Income Population Percentage form 2006 to 206 in Greater Sydney
![Low Income Change Greater Sydney 206-2016](/demo/INC_VERYLOW.gif)
![Low Income Change Central Sydney 206-2016](/demo/INC_VERYLOW_zoom.gif)


Example Web 3D based on deck.gl
_______________________________

[![Population Density](/demo/demo_POPDENS_cover.png)](http://htmlpreview.github.com/?https://github.sydney.edu.au/sebhaan/Urbanraster/blob/urbanraster_v1/demo/demo_raster_100m_POPDENS_100m.html)


## Attribution and Acknowledgments

This software has been developed in collaboration with the University of Sydney.

If you make use of this code for your research project, please include the following acknowledgment:

“This research was supported by the Sydney Informatics Hub, a Core Research Facility of the University of Sydney.”


## Software Contributors


Sebastian Haan: Main contributor and software development of Urbanraster


## License

Copyright 2020 Sebastian Haan

This is a free software made available under the AGPL License. For details see the LICENSE file.
