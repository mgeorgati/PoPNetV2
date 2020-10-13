import os
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from osgeo import gdal, ogr,osr
import fnmatch
import rasterio

# find files in directory. based on yours, but modified to return a list.
def find_dir(path, name_filter):
    result = []
    for root, dirs, files in os.walk(path):
        for filename in fnmatch.filter(files, name_filter):
            result.append(os.path.join(root, filename))
    #print(result)
    return result

#filesA = find_dir(tif_pathA, "*.tif")
#filesB = find_dir(tif_pathB, "*.tif")

#___________________________
print("Check if the files between the years and create empty rasters for mismatches of countries")
def createEmptyTif(tif_pathA,tif_pathB,yearA,yearB):
    for filenameA in os.listdir(tif_pathA):

        abbrA = filenameA.split("_",-1)[-1]
        abbr = filenameA.split("_",0)[0]

        fileB = Path("{0}\\cph_{1}_pop_origin_new_{2}".format(tif_pathB,yearB,abbrA))
        if fileB.exists():
            print(fileB, ': exists,Check Next')

        else:
            print(fileB , "doesn't exist, Creating raster")
            with rasterio.open('{0}/cph_{1}_pop_origin_new_dnk.tif'.format(tif_pathA,yearA)) as dd:
                new_dataset = rasterio.open(
                    "{0}/cph_{1}_pop_origin_new_{2}".format(tif_pathB,yearB,abbrA),
                    'w',
                    driver='GTiff',
                    height=dd.shape[0],
                    width=dd.shape[1],
                    count=1,
                    dtype=rasterio.float64,
                    crs=dd.crs,
                    transform= dd.transform
                 )

            new_dataset.close()

yearC="2017"
yearD= "2011"

pathA ="C:\FUME\DST_Data\Project_data\\temp_tif\{}".format(yearC)
pathB ="C:\FUME\DST_Data\Project_data\\temp_tif\{}".format(yearD)
createEmptyTif(pathA,pathB,yearC,yearD)