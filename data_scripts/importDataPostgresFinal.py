import os
import subprocess
import psycopg2

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

def extract_featuresGDB(pghost, pguser, pgpassword, pgdatabase, listFeatures, GDB_path):
    # Delete table if exists -----------------------------------------------------
    # connect to postgres
    connection = psycopg2.connect(database=pgdatabase, user=pguser, host=pghost, password=pgpassword)
    cursor = connection.cursor()
    # add postgis extension if not existing
    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    connection.commit()
    # closing connection
    cursor.close()
    connection.close()

    for feature in listFeatures:
        cmd_tif_merge = """ogr2ogr -overwrite -f 'PostgreSQL' PG:"host='{0}' user='{1}' dbname='{2}' password='{3}'" {4} {5}""".format(pghost, pguser, pgdatabase, pgpassword, GDB_path, feature)
        print(cmd_tif_merge)
        subprocess.call(cmd_tif_merge, shell=False)

def rename_Tablefeatures():
    #connect to postgres
    conn = psycopg2.connect(database="{}_data".format(city), user="postgres", host="localhost", password="postgres")
    cur = conn.cursor()
    #cur.execute("ALTER TABLE sø RENAME TO {0}_lakes;".format(city))
    #conn.commit()
    cur.execute("ALTER TABLE sø RENAME TO {0}_lakes;\
                ALTER TABLE {0}_lakes add column geom geometry(MultiPolygon,3035); \
                UPDATE {0}_lakes SET geom = ST_Transform({0}_lakes.shape, 3035);".format(city))
    conn.commit()

    cur.execute("ALTER TABLE skov RENAME TO {0}_forests;\
                ALTER TABLE {0}_forests add column geom geometry(MultiPolygon,3035); \
                UPDATE {0}_forests SET geom = ST_Transform({0}_forests.shape, 3035);".format(city))
    conn.commit()

#_______________________First Files and Processes_________________________
# Import NutsFile, clip to Case Study extent
# Import Corine files, clip, use to create grid and iterate_grid 
# Import grids to DB and create BBox
def initialProcess(pgpath, pghost, pgport, pguser, pgpassword,pgdatabase):
    conn = psycopg2.connect(database="{}_data".format(city), user="postgres", host="localhost", password="postgres")
    cur = conn.cursor()
    # Setting environment for psql
    os.environ['PATH'] = pgpath
    os.environ['PGHOST'] = pghost
    os.environ['PGPORT'] = pgport
    os.environ['PGUSER'] = pguser
    os.environ['PGPASSWORD'] = pgpassword
    os.environ['PGDATABASE'] = pgdatabase

    # Loading shapefile into postgresql
    print("Importing 2021 Nuts3 to postgres")
    NutsPath = ancillary_data_folder_path + "/ref-nuts-2021-01m/NUTS_RG_01M_2021_3035_LEVL_3/NUTS_RG_01M_2021_3035_LEVL_3.shp"
    cmds = 'shp2pgsql -I -s 3035  {0} public.nuts | psql'.format(NutsPath)
    print(cmds)
    subprocess.call(cmds, shell=True)

    # Create Table for Country Case Study
    print("---------- Creating table for country, if it doesn't exist ----------")
    print("Checking {0} Case Study table".format(country))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_cs');".format(country))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} Case Study Area Nuts3 table already exists".format(country))

    else:
        print("Creating {0} Case Study Area Nuts3".format(city))
        cur.execute("create table {0}_cs as \
                        SELECT * from nuts WHERE cntr_code= '{1}' ;".format(country,country))
        conn.commit()

    # Create Table for City Case Study
    print("---------- Creating table for Case Study, if it doesn't exist ----------")
    print("Checking {0} Case Study table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_cs');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} Case Study Area Nuts3".format(city))
        # bbox from NUTS3 (+buffer = 100m):
        cur.execute("create table {0}_cs as \
                        SELECT * from nuts WHERE NUTS_ID='{1}' OR NUTS_ID='{2}' ;".format(city, cph_nuts3_cd1, cph_nuts3_cd2))
        conn.commit()
    else:
        print("{0} Case Study Area Nuts3 table already exists".format(city))

    # ----- Clipping corine to case study extent ------------------------
    corinePath = ancillary_data_folder_path + "/corine"
    for file in os.listdir(corinePath):
        if file.endswith('.tif'):
            filePath = corinePath + "/" + file

            print("------------------------------ Clipping Corine rasters by extent of case study area ------------------------------")
            csPath = temp_shp + "/{0}_cs.shp".format(city)
            cmds = 'gdalwarp -of GTiff -cutline {0}\
                 -crop_to_cutline -dstalpha "{2}/{5}" "{3}/{4}_{5}"'.format(csPath,filePath,corinePath, temp_tif,city, file)
            subprocess.call(cmds, shell=True)

    # ----- Creating Grid ------------------------
    print("------------------------------ Creating Grid ------------------------------")
    print("Extracting corine extent for {0}".format(city))
    # Getting extent of ghs pop raster
    data = gdal.Open(temp_tif + "\{0}_U2018_CLC2012_V2020_20u1.tif".format(city))
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None

    # Creating polygon grid that matches the population grid and the corine-----------------------------------------------------------
    print("------------------------------ Creating vector grid for {0} ------------------------------".format(city))
    outpath = temp_shp + "/{0}_grid.shp".format(city)
    rasttovecgrid(outpath, minx, maxx, miny, maxy, 100, 100)

    # Creating polygon grid with larger grid size, to split the smaller grid and iterate in postgis --------------------
    print("------------------------------ Creating larger iteration vector grid for {0} ------------------------------"
              .format(country))
    outpath = temp_shp + "/{0}_iteration_grid.shp".format(city)
    rasttovecgrid(outpath, minx, maxx, miny, maxy, 500, 500)

    # Loading shapefile into postgresql
    print("Importing Grid to postgres")
    gridPath = temp_shp + "/{0}_grid.shp".format(city)
    cmds = 'shp2pgsql -I -s 3035  {0} public.{1}_grid | psql'.format(gridPath, city)
    subprocess.call(cmds, shell=True)

    # Loading shapefile into postgresql
    print("Importing Iteration Grid to postgres")
    gridPath = temp_shp + "/{0}_iteration_grid.shp".format(city)
    cmds = 'shp2pgsql -I -s 3035 {0} public.{1}_iteration_grid | psql'.format(gridPath, city)
    subprocess.call(cmds, shell=True)

     # Create Table for bbox
    print("---------- Creating table for Bbox, if it doesn't exist ----------")
    print("Checking {0} bounding box table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_bbox');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} bounding box table from grid".format(city))
        # bbox from NUTS3 (+buffer = 100m):
        cur.execute("create table {0}_bbox as \
                    SELECT ST_Buffer(ST_SetSRID(ST_Extent(geom),3035) \
                    ,100,'endcap=square join=mitre') as geom FROM {0}_grid;".format(city))
        conn.commit()
    else:
        print("{0} bounding box table already exists".format(city))

    #_______________________Water Bodies (Sea, Lakes, Wetlands)_________________________
    # Reprojection, Clip to Extent, Union, Rasterize

    print("Checking {0} subdivided ocean table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_subdivided_ocean');".format(country))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} subdivided ocean table".format(country))
        # Ocean from administrative + bbox:
        cur.execute("create table {0}_subdivided_ocean as \
            Select ST_Subdivide(ST_Difference({0}_bbox.geom, (Select ST_UNION({1}_cs.geom) as union))) \
            as geom from {0}_bbox, {1}_cs group by {0}_bbox.geom;".format(city,country))
        conn.commit()
    else:
        print("{0} subdivided ocean table already exists".format(country))

    #-------------------------------------------------------------------------------------------------------------------
    print("Checking {0} subdivided waterbodies table".format(city))

    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_water');".format(
                country))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} subdivided waterbodies table".format(city))
            # Creating waterbodies layer
        cur.execute("create table {0}_water as \
                                with a as ( \
                                select {0}_lakes.objectid, ST_Intersection({0}_lakes.geom, {0}_cs.geom) as geom\
                                FROM {0}_lakes, cph_cs\
                                where ST_Intersects({0}_lakes.geom, {0}_cs.geom))\
                                select geom FROM {0}_subdivided_ocean\
                                UNION\
                                select ST_Subdivide(ST_Union(geom)) from a;".format(city))  # 3.32 min
        conn.commit()
    else:
        print("{0} subdivided waterbodies table already exists".format(country))
    
    #_______________________Train Stations_________________________
    
    # Loading shapefile into postgresql
    print("Importing Railways to postgres")
    railPath = ancillary_data_folder_path + "/railways/trainstations.shp"
    cmds = 'shp2pgsql -I -s 25832  {0} public.trainst | psql'.format(railPath)
    print(cmds)
    subprocess.call(cmds, shell=True)

# Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating necessary tables, if they don't exist ----------")
    print("Checking {0} train stations table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_trainst');".format(country))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} train stations table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_trainst as \
                    select trainst.gid, trainst.year, ST_Intersection(ST_Transform(trainst.geom, 3035), {0}_cs.geom) as geom\
                    FROM trainst, cph_cs\
                    where ST_Intersects(ST_Transform(trainst.geom, 3035), {0}_cs.geom);".format(city))
        conn.commit()
    else:
        print("{0} train stations table already exists".format(city))

    #_______________________Bus Stops_________________________
    # Loading shapefile into postgresql
    print("Importing Bus Stops to postgres")
    busstPath = ancillary_data_folder_path + "/buses/busst.shp"
    cmds = 'shp2pgsql -I -s 25832  {0} public.busst | psql'.format(busstPath)
    print(cmds)
    subprocess.call(cmds, shell=True)

#_______________________Natural Environment (Forest, )_________________________
# Reprojection, Clip to Extent, Union, Rasterize

#_______________________Restricted Areas (Natura2000, Cultural Heritage)_________________________

