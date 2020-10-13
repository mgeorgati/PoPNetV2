# Imports
import subprocess
import os
import gdal
import ogr
import osr
import psycopg2
import time
from import_to_postgres import import_to_postgres
from import_to_postgres import restructure_tables
from postgres_to_raster import psqltoshp
from postgres_to_raster import shptoraster

def process_data( pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path,temp_shp_path,temp_tif_path,
                  init_import_to_postgres,restructure_tables_sql,init_export_data,init_rasterize_data,engine):
    #Start total preparation time timer
    start_total_algorithm_timer = time.time()

    if not os.path.exists(temp_shp_path):
        os.makedirs(temp_shp_path)

    if not os.path.exists(temp_tif_path):
        os.makedirs(temp_tif_path)

    # Importing data to postgres--------------------------------------------------------------------------------------
    if init_import_to_postgres == "yes":
        print("------------------------------ IMPORTING DATA TO POSTGRES ------------------------------")
        import_to_postgres( pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path,engine)

    # Restructuring tables in postgres--------------------------------------------------------------------------------------
    if restructure_tables_sql == "yes":
        print("------------------------------ RESTRUCTURING TABLES IN POSTGRES ------------------------------")
        restructure_tables( pgpath, pghost, pgport, pguser, pgpassword, pgdatabase,ancillary_data_folder_path, engine)

     # Export layers from postgres to shp -------------------------------------------------------------------------------
    if init_export_data == "yes":
        print("------------------------------ EXPORTING DATA FROM POSTGRES ------------------------------")
        psqltoshp( pghost, pguser, pgpassword, pgdatabase, temp_shp_path, engine)

    # Rasterize layers from postgres -----------------------------------------------------------------------------------
    if init_rasterize_data == "yes":
        print("------------------------------------ RASTERIZING DATA ------------------------------------")
        shptoraster(pghost, pguser, pgpassword, pgdatabase, temp_shp_path,temp_tif_path)

    # Merge layers by subregion name and by year -----------------------------------------------------------------------------------
    if merge_data_subregion == "yes":
        print("------------------------------------ RASTERIZING DATA ------------------------------------")
        mergeRasters(pghost, pguser, pgpassword, pgdatabase, temp_shp_path,temp_tif_path)

    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))

