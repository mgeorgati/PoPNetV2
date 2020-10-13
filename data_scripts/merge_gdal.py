import os
import subprocess
import fnmatch


path11 = "C:\\FUME\\popnetv2\\data\\2011"
path17 = "C:\\FUME\\popnetv2\\data\\2017"

with open("{}\\file11.txt".format(path11),"w+") as text_file:
    for filename in os.listdir(path11):

        text_file.writelines("{}\\".format(path11) + filename + "\n")
        text_file.close
with open("{}\\file17.txt".format(path17),"w+") as text_file:
    for filename in os.listdir(path17):

        text_file.writelines("{}\\".format(path17) + filename + "\n")
        text_file.close

cmd_tif_merge = "gdalbuildvrt -separate -input_file_list {}\\file11.txt {}\\vrt2011.vrt".format(path11,path11)
print(cmd_tif_merge)
subprocess.call(cmd_tif_merge, shell=False)
cmd_tif_translate = "gdal_translate {}\\vrt2011.vrt {}\\2011.tif ".format(path11,path11)
print(cmd_tif_translate)
subprocess.call(cmd_tif_translate, shell=False)

cmd_tif_merge = "gdalbuildvrt -separate -input_file_list {}\\file17.txt {}\\vrt2017.vrt".format(path17,path17)
print(cmd_tif_merge)
subprocess.call(cmd_tif_merge, shell=False)
cmd_tif_translate = "gdal_translate {}\\vrt2017.vrt {}\\2017.tif ".format(path17,path17)
print(cmd_tif_translate)
subprocess.call(cmd_tif_translate, shell=False)