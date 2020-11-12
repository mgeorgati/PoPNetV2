import os
import subprocess
import psycopg2
import time
city= 'cph'
pgpath = r';C:\Program Files\PostgreSQL\9.5\bin'
pghost = 'localhost'
pgport = '5432'
pguser = 'postgres'
pgpassword = 'postgres'
pgdatabase = '{}_data'.format(city)
ancillary_data_folder_path = "C:/FUME/popnetv2/data_scripts/ProjectData/AncillaryData"

#_______________________Roads_________________________
# Process shp adding field and defining the train stations (0),metro stations M1,2 (2000), metro stations M3,4 (2020)
# Import shp to postgres, clip to case study extent,

def all_aboutBuses(ancillary_data_folder_path,city,conn,cur):

    # Creating table for Bus Stops ----------------------------------------------------------------------------------------
    print("---------- Creating necessary tables, if they don't exist ----------")
    print("Checking {0} bus stops table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_busst');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} train stations table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_busst as \
                    select busst.gid,busst.existsfrom, ST_Intersection(ST_Transform(busst.geom, 3035), {0}_cs.geom) as geom\
                    FROM busst, {0}_cs\
                    where ST_Intersects(ST_Transform(busst.geom, 3035), {0}_cs.geom);".format(city))
        conn.commit()
    else:
        print("{0} bus stops table already exists".format(city))

    # Creating column Year for Bus Stops ----------------------------------------------------------------------------------------
    print("Checking {0} Bus Stops - year column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                    FROM information_schema.columns \
                    WHERE table_schema='public' AND table_name='{0}_busst' AND column_name='year');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} Bus Stops - year column".format(city))
        # Adding road distance column to cover analysis table
        cur.execute(
            "Alter table {0}_busst ADD column year varchar default 0;\
            UPDATE {0}_busst SET year = LEFT(CAST(existsfrom AS varchar),4)".format(city))  # 14.8 sec
        conn.commit()
    else:
        print("{0} Bus Stops - year column already exists".format(city))




def bus_analysis(conn,cur,city,startYear, endYear):

        print("Checking {0} bus analysis - distance column per year of analysis".format(city))
        cur.execute("SELECT EXISTS (SELECT 1 \
                        FROM information_schema.columns \
                        WHERE table_schema='public' AND table_name='{0}_cover_analysis' AND column_name='busst_{1}');".format(
            city,startYear))
        check = cur.fetchone()
        if check[0] == False:
            print("Creating {0} bus analysis - bus stop distance column".format(city))
            # Adding road distance column to cover analysis table
            cur.execute(
                "Alter table {0}_cover_analysis ADD column busst_{1} int default 0;".format(
                    city, startYear))  # 14.8 sec
            conn.commit()
        else:
            print("{0} cover analysis - bus stop busst_{1} column already exists".format(city,startYear))

        # Calculating bus stops based on count ----------------------------------------------------------------------------------------
        print("---------- Calculating bus stops for years: {0}, {1}----------".format(startYear, endYear))
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
                where {0}_busst.year = '{2}' AND {0}_busst.year = '{3}' AND st_dwithin(chunk_nr{1}.geom, {0}_busst.geom, 800) \
                group by chunk_nr{1}.id) \
                update {0}_cover_analysis set busst_{2} = a.count from a where a.id = {0}_cover_analysis.id;".format(city, chunk, startYear, endYear))  # 4.1 sec
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
        print("Total road distance query time : {0} minutes".format(total_query_time)) #13min

def iterate_busAnalysis(conn,cur,city):
    startYear = 2000
    
    while startYear < 2006:
        endYear = startYear+1
        bus_analysis(conn,cur,city,startYear, endYear)
        startYear += 2
        bus_analysis(conn,cur,city,startYear, endYear)