import pandas as pd
import numpy as np
import geopandas as gpd
from numpy import copy
from shapely.geometry import Point

from osgeo import gdal
from osgeo.gdalconst import GDT_Float32

import sys
import numpy as np

# Read CSV of Raster Attribute Table, recoded with old and new values
df= pd.read_csv(r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\ecocomm_test\ecomm_rat.csv")\
.loc[:,["VALUE", "VALUE_NEW"]]

# Dictionary: old values ar ekeys, new values are values
dict= {k: list(v) for k, v in df.groupby('VALUE')['VALUE_NEW']}
dict

# Set filepath
# input file path (ESRI Grid file)
fp= r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\ecocomm\ecomm11_types\w001001.adf"
# output geotiff file
op= r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\Python Output\ecomm11_recode.tif"

# Open the file:
raster = gdal.Open(fp)

# Check type of the variable
type(raster)

# Read in information on the raster band
band = raster.GetRasterBand(1)
rows = raster.RasterYSize
cols = raster.RasterXSize
vals = band.ReadAsArray(0, 0, cols, rows)

# Copy data for recoding
data = np.array(vals)

newdata = copy(data)
newdata

# Use dictionary key, value pairs to recode
for k, v in dict.items(): newdata[data==k] = v

# create single-band float32 output raster
driver = gdal.GetDriverByName('GTiff')
out_data = driver.Create(op, cols, rows, 1, GDT_Float32)

# georeference the image and set the projection
out_data.SetGeoTransform(raster.GetGeoTransform())
out_data.SetProjection(raster.GetProjection())

# write the data to output file
out_data.GetRasterBand(1).WriteArray(newdata)
out_data.GetRasterBand(1).SetNoDataValue(-32768)

  # flush data to disk
out_data.FlushCache()
