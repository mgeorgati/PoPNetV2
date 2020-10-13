# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
from sqlalchemy import create_engine
from process import process_data

# ATTENSION ------------------------------------------------------------------------------------------------------------
# Before running this script, a database should be created in postgres and the database information entered below, if
# it's not the same. Furthermore, the Project_data folder, scound be placed in the same folder as the scripts
# (main, process, import_to_postgres, postgres_to_shp, postgres_queries and rast_to_vec_grid)
city ='cph'
# Folder strudture:
# scripts
# Project_data

# Specify country to extract data from ---------------------------------------------------------------------------------
#country = 'Monaco'

# choose processes to run ----------------------------------------------------------------------------------------------
# Initial preparation of Population data ("yes" / "no") csvTOdbTOshpTOtif
init_prep = "no"
#Import data to postgres? ("yes" / "no")
init_import_to_postgres = "no"
# Run postgres queries? ("yes" / "no")
restructure_tables_sql = "no"
# export data from postgres? ("yes" / "no")
init_export_data = "no"
# rasterize data from postgres? ("yes" / "no")
init_rasterize_data = "no"
# Merge data from postgres? ("yes" / "no")
#init_merge_data = "no"

# Merge data by sub_region_name and by year ("yes" / "no")
merge_data_subregion = "no"

# calculate multiple train buffers? (dict{'column_name':biffersize in meters} or one ("yes", buffersize in meters)?
#multiple_train = "yes"
#multiple_train_dict = {'station2':2000, 'station5':5000, 'station10':10000, 'station20':20000}
#one_train_buffer = "yes", 10000

# Specify database information -----------------------------------------------------------------------------------------
# path to postgresql bin folder
pgpath = r';C:\Program Files\PostgreSQL\12\bin'
pghost = 'localhost'
pgport = '5432'
pguser = 'postgres'
pgpassword = 'postgres'
pgdatabase = 'dst_data'
#connection
engine = create_engine('postgresql://postgres:postgres@localhost:5432/dst_data')

# DIFFERENT PATHS ------------------------------------------------------------------------------------------------------
# Get path to main script
python_script_dir = os.path.dirname(os.path.abspath(__file__))
print(python_script_dir)
# Paths for the data / folders in the Project_data folder --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path = python_script_dir + "\\Project_data\\dst_data".format(city) #"\Project_data\DST_raw_data"

#path to folder for intermediate shapefiles of all years and all origins
temp_shp_path = python_script_dir + "\\Project_data\\temp_shp".format(city)
print(temp_shp_path)
temp_tif_path = python_script_dir + "\\Project_data\\temp_tif".format(city)
#path to GADM folder
#gadm_folder_path = python_script_dir + "\Project_data\GADM"
#path to GHS folder
#ghs_folder_path = python_script_dir + "\Project_data\GHS"

# Paths to storage during the data preparation (AUTOMATICALLY CREATED) -------------------------------------------------
#path to temp folder - will contain temporary files
#temp_folder_path = python_script_dir + "\Temp"
#Files to be merged folder
#merge_folder_path = python_script_dir + "\Tif_to_merge"
#path to data folder to store the final tif files
#finished_data_path = python_script_dir + "\Finished_data"

# Other Paths to necessary python scripts and functions ----------------------------------------------------------------
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'C:\Users\NM12LQ\Anaconda3\Scripts'
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'C:\Users\NM12LQ\Anaconda3\Lib\site-packages\osgeo'


process_data( pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path,temp_shp_path,temp_tif_path,
                  init_import_to_postgres,restructure_tables_sql,init_export_data,init_rasterize_data,engine)
