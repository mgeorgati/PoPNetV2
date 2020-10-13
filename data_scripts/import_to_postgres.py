# This script imports data to postgres
import pandas as pd
import os
import psycopg2


def import_to_postgres(pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path, engine):
    # ----- Importing data to postgres ---------------------------------------------------------------------------------

    filesList=[]
    for subdirs, dirs, files in os.walk(ancillary_data_folder_path):
    #sorted_files = sorted(files)
        for file in files:
            print(file)
            if file.endswith(".xlsx"):
                fileName = file.split(".xlsx")[0]
                df = pd.read_excel(r'{0}/{1}'.format(ancillary_data_folder_path,file), index_col=0)

                # Delete table if exists -----------------------------------------------------
                # connect to postgres
                connection = psycopg2.connect(database=pgdatabase, user=pguser, host=pghost, password=pgpassword)
                cursor = connection.cursor()

                # add postgis extension if not existing
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

                # check for table and delete it if exists
                cursor.execute("DROP TABLE  IF EXISTS  {};".format(fileName))
                connection.commit()
                # closing connection
                cursor.close()
                connection.close()
                df.reset_index(level=0, inplace=True)
                df.columns = df.columns.str.replace(' ', '_')
                df.columns = [x.lower() for x in df.columns]
                print(df.columns)
                filesList.append(fileName)
                #what if table already exists
                df.to_sql('{}'.format(fileName), engine)


def restructure_tables(pgpath, pghost, pgport, pguser, pgpassword, pgdatabase,ancillary_data_folder_path,  engine):
    filesList=[]
    for subdirs, dirs, files in os.walk(ancillary_data_folder_path):
        for file in files:
            if file.endswith(".xlsx"):
                fileName = file.split(".xlsx")[0]
                filesList.append(fileName)

            for i in filesList:

                # connect to postgres -----------------------------------------------------
                connection = psycopg2.connect(database=pgdatabase, user=pguser, host=pghost, password=pgpassword)
                cursor = connection.cursor()

                # Drop table if exists
                cursor.execute("""DROP TABLE  IF EXISTS  {}_new;""".format(i))

                # Create new table
                sql = """CREATE TABLE {}_new (gridid varchar, year int, total_pop varchar, var_type varchar,  pop float, origin varchar);""".format(i)
                cursor.execute(sql)
                print(sql)
                myQuery = """SELECT * FROM {}""".format(i)
                df = pd.read_sql_query(myQuery, engine)

                cols = df.columns.tolist()
                #print(cols)
                for val in df.columns[5:]:
                    sql1="""INSERT INTO {0}_new (gridid, year, total_pop, var_type, pop )
                            SELECT {1}.gc100m,{2}.year,{3}.Total_population_in_cell, {4}.Variable_type,{5}.{6} FROM {7} WHERE "{8}"!=0;""".format(i,i,i,i,i,i,val,i,val) #{}

                    sql2=""" UPDATE {}_new SET origin='{}' where origin IS NULL;""".format(i,val) #{}

                    cursor.execute(sql1)
                    cursor.execute(sql2)

                    connection.commit()


                # Alter new table, add columns and populate them with lat,lon and geom
                sql3 = """ALTER TABLE {}_new ADD COLUMN x float,
                                            ADD COLUMN y float,
                                            ADD COLUMN geom geometry(Point, 3035);""".format(i)
                cursor.execute(sql3)

                sql4 = """UPDATE {}_new SET y=split_part(gridid, 'N', 1)::float;
                          UPDATE {}_new SET x=SUBSTRING(gridid, 9, 7)::float;
                          UPDATE {}_new SET geom = ST_SetSRID(ST_MakePoint(x, y), 3035);""".format(i,i,i)

                cursor.execute(sql4)
                connection.commit()

                cursor.close()
                connection.close()