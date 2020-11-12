import os
import subprocess
import gdal
import psycopg2
import time
from sqlalchemy import create_engine
from rast_to_vec_grid import rasttovecgrid
from importDataPostgresFinal import extract_featuresGDB, initialProcess
from calc_Rails import  calculateRail,calculateRailBuffers
from calc_Water import  calculateWater
from calc_Buses import  all_aboutBuses,iterate_busAnalysis

city= 'cph'
country = "DK"
cph_nuts3_cd1= 'DK011'
cph_nuts3_cd2= 'DK012'
listo =["hav", "Jernbane", "Sø","Naturreservat", "Skov", "bebyggelses_område"]
path= "C:/FUME/popnetv2/data_scripts/ProjectData/AncillaryData/DK_data/d200_GDB_UTM32-EUREF89/D200_2015_UTM32_EUREF89.gdb"

pgpath = r';C:\Program Files\PostgreSQL\9.5\bin'
pghost = 'localhost'
pgport = '5432'
pguser = 'postgres'
pgpassword = 'postgres'
pgdatabase = '{}_data'.format(city)

conn = psycopg2.connect(database="{}_data".format(city), user="postgres", host="localhost", password="postgres",sslmode="disable")
cur = conn.cursor()


temp_tif = "C:/FUME/popnetv2/data_scripts/ProjectData/temp_tif"
temp_shp = "C:/FUME/popnetv2/data_scripts/ProjectData/temp_shp"
ancillary_data_folder_path = "C:/FUME/popnetv2/data_scripts/ProjectData/AncillaryData"
#Run following functions 
#extract_featuresGDB(pghost, pguser, pgpassword, pgdatabase, listo, path)
#rename_Tablefeatures()
#initialProcess()
#initCoverAnalysis()
#calculateWater()
#calculateRail(ancillary_data_folder_path, city,country,conn,cur)
calculateRailBuffers(city,conn,cur) ####
#all_aboutBuses(ancillary_data_folder_path,city,conn,cur)
iterate_busAnalysis(conn,cur,city)


#_______________________Cover Analysis_the beginning_________________________
def initCoverAnalysis():
    conn = psycopg2.connect(database="{}_data".format(city), user="postgres", host="localhost", password="postgres")
    cur = conn.cursor()

    print("Checking {0} cover analysis table".format(city))
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public'\
         AND tablename = '{0}_cover_analysis');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis table".format(city))
        # Watercover percentage:
        cur.execute("Create table {0}_cover_analysis as \
                            (SELECT * \
                            FROM {0}_grid);".format(city))  # 4.3 sec
        conn.commit()
    else:
        print("{0} cover analysis table already exists".format(city))
    #-------------------------------------------------------------------------------------------------------------------

#_______________________Roads_________________________
# Process shp adding field and defining the train stations (0),metro stations M1,2 (2000), metro stations M3,4 (2020)
# Import shp to postgres, clip to case study extent,

def aboutBuses():
    # Loading shapefile into postgresql
    print("Importing Bus Stops to postgres")
    busstPath = ancillary_data_folder_path + "/buses/busst.shp"
    cmds = 'shp2pgsql -I -s 25832  {0} public.busst | psql'.format(busstPath)
    print(cmds)
    subprocess.call(cmds, shell=True)

    # Loading shapefile into postgresql
    print("Importing Bus Lines to postgres")
    buslnPath = ancillary_data_folder_path + "/buses/busln.shp"
    cmds = 'shp2pgsql -I -s 25832  {0} public.busln | psql'.format(buslnPath)
    print(cmds)
    subprocess.call(cmds, shell=True)

    # Creating table for Bus Stops ----------------------------------------------------------------------------------------
    print("---------- Creating necessary tables, if they don't exist ----------")
    print("Checking {0} bus stops table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_busst');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} train stations table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_busst as \
                    select busst.gid, ST_Intersection(ST_Transform(busst.geom, 3035), {0}_cs.geom) as geom\
                    FROM busst, {0}_cs\
                    where ST_Intersects(ST_Transform(busst.geom, 3035), {0}_cs.geom);".format(city))
        conn.commit()
    else:
        print("{0} bus stops table already exists".format(city))

    #-------------------------------------------------------------------------------------------------------------------

    # Creating table for Bus Lines ----------------------------------------------------------------------------------------
    print("---------- Creating necessary tables, if they don't exist ----------")
    print("Checking {0} bus lines table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_busln');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} train lines table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_busln as \
                    select busln.gid, ST_Intersection(ST_Transform(busln.geom, 3035), {0}_cs.geom) as geom\
                    FROM busln, {0}_cs\
                    where ST_Intersects(ST_Transform(busln.geom, 3035), {0}_cs.geom);".format(city))
        conn.commit()
    else:
        print("{0} bus lines table already exists".format(city))
    #-------------------------------------------------------------------------------------------------------------------

    print("Checking {0} cover analysis - bus stop distance column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                    FROM information_schema.columns \
                    WHERE table_schema='public' AND table_name='{0}_cover_analysis' AND column_name='busst_dist');".format(
        city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - bus stop distance column".format(city))
        # Adding road distance column to cover analysis table
        cur.execute(
            "Alter table {0}_cover_analysis ADD column busst_dist double precision default 0;".format(
                city))  # 14.8 sec
        conn.commit()
    else:
        print("{0} cover analysis - bus stop distance column already exists".format(city))

# Calculating train stations based on count ----------------------------------------------------------------------------------------
    print("---------- Calculating bus stops ----------")
    # start total query time timer
    start_query_time = time.time()
     # getting id number of chunks within the iteration grid covering the city ---------------------------------------
    ids = []
    cur.execute("SELECT gid FROM {0}_iteration_grid;".format(city))
    chunk_id = cur.fetchall()

    # saving ids to list
    for id in chunk_id:
        ids.append(id[0])

    # iterate through chunks
    for chunk in ids:
        # start single chunk query time timer
        t0 = time.time()

        # Create table containing centroids of the original small grid within the land cover of the country
        cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT id, ST_Centroid({0}_cover_analysis.geom) AS geom \
                            FROM {0}_cover_analysis, {0}_iteration_grid \
                            WHERE {0}_iteration_grid.gid = {1} \
                            AND ST_Intersects({0}_iteration_grid.geom, {0}_cover_analysis.geom) \
                            AND {0}_cover_analysis.water_cover < 99.999);".format(city, chunk))  # 1.7 sec
        # check if chunk query above returns values or is empty
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, moving to next chunk".format(chunk, len(ids)))
            conn.rollback()
        else:
            conn.commit()
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))

            # Index chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geom);".format(chunk))  # 175 ms
            conn.commit()

            # Counting number of train stations within x km distance
            cur.execute("with a as (select chunk_nr{1}.id, count(*) from {0}_busst, chunk_nr{1} \
            where st_dwithin(chunk_nr{1}.geom, {0}_busst.geom, 800) \
            group by chunk_nr{1}.id) \
            update {0}_cover_analysis set busst_dist = a.count from a where a.id = {0}_cover_analysis.id;".format(city, chunk))  # 4.1 sec
            conn.commit()

            # Drop chunk_nr table
            cur.execute("DROP TABLE chunk_nr{0};".format(chunk))  # 22 ms
            conn.commit()

            # stop single chunk query time timer
            t1 = time.time()

            # calculate single chunk query time in minutes
            total = (t1 - t0) / 60
            print("Chunk number: {0} took {1} minutes to process".format(chunk, total))
    # stop total query time timer
    stop_query_time = time.time()

    # calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total bus distance query time : {0} minutes".format(total_query_time)) #13min



 # Calculating road distance ----------------------------------------------------------------------------------------
    print("---------- Calculating bus distance ----------")
    # start total query time timer
    start_query_time = time.time()
    print("Creating table with roads within the country")
    #Creating table with roads within the country
    cur.execute("CREATE TABLE {0}_iterate_roads AS (SELECT {0}_groads.gid, ST_Transform(ST_SetSRID({0}_groads.geom, 4326), 54009) AS geom FROM {0}_groads, {0}_adm \
                WHERE ST_DWithin({0}_adm.geom, ST_Transform(ST_SetSRID({0}_groads.geom, 4326), 54009), 1));".format(country))  # 1.10 min

    # creating index on roads table
    cur.execute("CREATE INDEX {0}_iterate_roads_gix ON {0}_iterate_roads USING GIST (geom);".format(country))  # 21 ms
    conn.commit()


    # iterating through chunks
    for chunk in ids:
        # start single chunk query time timer
        t0 = time.time()

        # Create table containing centroids of the original small grid within the land cover of the country
        cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT id, ST_Centroid({0}_cover_analysis.geom) AS geom \
                    FROM {0}_cover_analysis, {0}_iteration_grid \
                    WHERE {0}_iteration_grid.gid = {1} \
                    AND ST_Intersects({0}_iteration_grid.geom, {0}_cover_analysis.geom) \
                    AND {0}_cover_analysis.water_cover < 99.999);".format(country, chunk))  # 1.7 sec
        # check if chunk query above returns values or is empty
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, moving to next chunk".format(chunk, len(ids)))
            conn.rollback()
        else:
            conn.commit()
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))

            # Index chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geom);".format(chunk))  # 175 ms
            conn.commit()

            # Create table containing water_cover cell id and distance ALL
            cur.execute("WITH a AS (SELECT Distinct ON (chunk_nr{1}.id) chunk_nr{1}.id as id, \
            ST_Distance(chunk_nr{1}.geom, {0}_iterate_roads.geom) AS r_dist from {0}_iterate_roads, chunk_nr{1}, {0}_adm \
            WHERE st_DWithin(chunk_nr{1}.geom, {0}_iterate_roads.geom, 30000) order by chunk_nr{1}.id, r_dist asc) \
            UPDATE {0}_cover_analysis SET rdist = r_dist from a WHERE a.id = {0}_cover_analysis.id;".format(country, chunk))  # 4.1 sec
            conn.commit()

            # Drop chunk_nr table
            cur.execute("DROP TABLE chunk_nr{0};".format(chunk))  # 22 ms
            conn.commit()

            # stop single chunk query time timer
            t1 = time.time()

            # calculate single chunk query time in minutes
            total = (t1 - t0) / 60
            print("Chunk number: {0} took {1} minutes to process".format(chunk, total))

    # stop total query time timer
    stop_query_time = time.time()

    #calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total road distance query time : {0} minutes".format(total_query_time))

    # Drop roads iteration table
    cur.execute("DROP TABLE {0}_iterate_roads;".format(country))
    conn.commit()