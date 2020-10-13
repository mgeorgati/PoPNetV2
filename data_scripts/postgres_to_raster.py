import os
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from osgeo import gdal, ogr,osr

def psqltoshp( pghost, pguser, pgpassword, pgdatabase, temp_shp_path, engine):

    sql="""SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='public' AND TABLE_CATALOG='dst_data'AND TABLE_TYPE = 'BASE TABLE' AND table_name!='spatial_ref_sys'"""

    df = pd.read_sql_query(sql, engine)

    tables = df['table_name'].to_list()

    for table in tables:
        if table.endswith("_new"):
            sql="""SELECT gridid,origin,pop,geom FROM {}""".format(table)
            # Store the data as a variable
            df = gpd.GeoDataFrame.from_postgis(sql, engine)
            origins=df.origin.unique()
            #print(origins)

            #create shapefile for each origin for each table
            for origin in origins:
                sql_selection="""SELECT gridid,origin,pop,geom FROM {} where origin='{}'""".format(table,origin)
                df_selection = gpd.GeoDataFrame.from_postgis(sql_selection, engine)
                df_selection.to_file(temp_shp_path + "/{}_{}.shp".format(table,origin),driver="ESRI Shapefile")

def shptoraster(pghost, pguser, pgpassword, pgdatabase, temp_shp_path,temp_tif_path):
    filenames=[]
    # Define pixel_size and NoData value of new raster

    for file in os.listdir(temp_shp_path):
        filename = os.fsdecode(file)
            #print(filename)
        if filename.endswith('.shp'): # whatever file types you're using...
            filenames.append(filename)

            pixel_size = 100
            NoData_value = 0

            for file in filenames:
                print(file)
            #filenames.append(filename)
                #subfolder = temp_shp_path.decode('utf-8')

                name=os.path.splitext(file)[0]
                daShapefile = "{}\\{}".format(temp_shp_path,file)
                #print(subfolder)
                driver = ogr.GetDriverByName('ESRI Shapefile')

                dataSource = driver.Open(daShapefile, 0) # 0 means read-only. 1 means writeable.

                # Check to see if shapefile is found.
                if dataSource is None:
                    print ('Could not open %s' % (daShapefile))
                else:
                    print ('Opened %s' % (daShapefile))
                    layer = dataSource.GetLayer()
                    featureCount = layer.GetFeatureCount()
                    print ("Number of features in %s: %d" % (os.path.basename(daShapefile),featureCount))

                    # Filename of the raster Tiff that will be created
                    raster_fn = "{}\\{}.tif".format(temp_tif_path,name)
                    #print(raster_fn)

                    #Open the data source and read in the extent
                    source_ds = ogr.Open(file)
                    #print(source_ds)

                    source_layer = dataSource.GetLayer()
                    srs= source_layer.GetSpatialRef()
                    #x_min= 4456367.0
                    #x_max= 4497109.0
                    #y_min= 3608529.0
                    #y_max= 3636789.0
                    x_min, x_max, y_min, y_max = source_layer.GetExtent()

                    #print(source_layer)
                    # Create the destination data source
                    x_res = int((x_max - x_min + pixel_size) / pixel_size)
                    y_res = int((y_max - y_min + pixel_size) / pixel_size)
                    target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float32)
                    x= x_min-(pixel_size/2)
                    y= y_max+(pixel_size/2)

                    target_ds.SetGeoTransform((x, pixel_size, 0, y, 0, -pixel_size))

                    target_wkt=srs.ExportToWkt()
                    target_ds.SetProjection(target_wkt)

                    band = target_ds.GetRasterBand(1)
                    band.SetNoDataValue(NoData_value)

                    # Rasterize
                    gdal.RasterizeLayer(target_ds, [1], source_layer, options=["ATTRIBUTE=POP", "ALL_TOUCHED=FALSE"], burn_values=[1])
                    target_ds = None

pgpath = r';C:\Program Files\PostgreSQL\12\bin'
pghost = 'localhost'
pgport = '5432'
pguser = 'postgres'
pgpassword = 'postgres'
pgdatabase = 'dst_data'
shp_path="C:\FUME\popnetv2\data\AncillaryData\CPH_data"
tif_path="C:\FUME\popnetv2\data\AncillaryData\CPH_data"
shptoraster(pghost, pguser, pgpassword, pgdatabase, shp_path,tif_path)