import subprocess
import os
import sys
path=r"C:\\FUME\\popnetv2\\data\\pop_tur"
python_scripts_folder_path = r'C:\Users\NM12LQ\Anaconda3\Scripts'
outfile2011 = path + "\\2011withExtra4.tif"
outfile2017 = path + "\\2017withExtra4.tif"
ancillary_data_path = "C:\\FUME\\popnetv2\\data\\AncillaryData\\CPH_data"

# Merging files for 2011
print("Merging files for 2011")
tur = "{}\\cph_2011_pop_origin_new_tur.tif".format(path)
CA = "{}\\totalPop_central_asia_2011.tif".format(path)
EA = "{}\\totalPop_eastern_asia_2011.tif".format(path)
EE = "{}\\totalPop_eastern_europe_2011.tif".format(path)
NAf = "{}\\totalPop_northern_africa_2011.tif".format(path)
NAm = "{}\\totalPop_northern_america_2011.tif".format(path)
NE = "{}\\totalPop_northern_europe_2011.tif".format(path)
SA = "{}\\totalPop_southern_asia_2011.tif".format(path)
SEA = "{}\\totalPop_southern_eastern_asia_2011.tif".format(path)
SE = "{}\\totalPop_southern_europe_2011.tif".format(path)
WA = "{}\\totalPop_western_asia_2011.tif".format(path)
WE = "{}\\totalPop_western_europe_2011.tif".format(path)
sogn = ancillary_data_path + "\\cph_sogn.tif"
forests = ancillary_data_path + "\\cph_forestsReProj.tif"
vand = ancillary_data_path +  "\\cph_vandReProj.tif"
cmd_tif_merge = "python {0}\gdal_merge.py -o {1} -separate {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15}" \
    .format(python_scripts_folder_path, outfile2011, tur,
    CA,EA,EE,NAf,NAm,NE,SA,SEA,SE,WA,WE, forests, vand)
print(cmd_tif_merge)
subprocess.call(cmd_tif_merge, shell=False)

# Merging files for 2011
print("Merging files for 2017")
tur = path + "\\cph_2017_pop_origin_new_tur.tif"
CA = path + "\\totalPop_central_asia_2017.tif"
EA = path + "\\totalPop_eastern_asia_2017.tif"
EE = path + "\\totalPop_eastern_europe_2017.tif"
NAf = path + "\\totalPop_northern_africa_2017.tif"
NAm = path + "\\totalPop_northern_america_2017.tif"
NE = path + "\\totalPop_northern_europe_2017.tif"
SA = path + "\\totalPop_southern_asia_2017.tif"
SEA = path +"\\totalPop_southern_eastern_asia_2017.tif"
SE = path + "\\totalPop_southern_europe_2017.tif"
WA = path + "\\totalPop_western_asia_2017.tif"
WE = path + "\\totalPop_western_europe_2017.tif"
sogn = ancillary_data_path + "\\cph_sogn.tif"
forests = ancillary_data_path + "\\cph_forestsReProj.tif"
vand = ancillary_data_path +  "\\cph_vandReProj.tif"
cmd_tif_merge = "python {0}\gdal_merge.py -o {1}  -separate {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15}" \
    .format(python_scripts_folder_path, outfile2017, tur,
    CA,EA,EE,NAf,NAm,NE,SA,SEA,SE,WA,WE, forests,vand)
print(cmd_tif_merge)
subprocess.call(cmd_tif_merge, shell=False)