# ---------------------------------------------------------------------------
# index.py
# Created on: ti jan 06 2009 02:27:15 
# Usage: index <mappe> <shapefil.shp>
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcgisscripting

# Create the Geoprocessor object
gp = arcgisscripting.create()

# Script arguments...
Ind = sys.argv[1]
if Ind == '#':
 Ind = "C:\\temp\\x.shp" # provide a default value if unspecified


# Process: Add Spatial Index...
gp.AddSpatialIndex_management(Ind, "0", "0", "0")

