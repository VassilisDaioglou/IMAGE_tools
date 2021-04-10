"""
Script to convert m-maps to netCDF maps

Author: Vassilis Daioglou
Date: April 2021
"""
import netCDF4
import numpy as np
import numpy.ma as ma
from pym import read_mym, load_mym
from dirs import InputDir
from functions import read_map, get_mmapping, get_gridmap
from outputs import WriteMaps

# *** DATA NEEDED TO GET THE m-to-netCDF MAPPING ***
regionmap = read_map(InputDir.data_dir + 'region27.nc', 'region27')       
grdfile  = np.loadtxt(InputDir.data_dir + 'mcoord.txt')

# Get map for masking
maskmap = netCDF4.Dataset(InputDir.data_dir + 'GNLCT_30MIN.nc')
maskmap = maskmap.variables['GNLCT_30MIN'][:]

# Get area map 
area = netCDF4.Dataset(InputDir.data_dir + 'garea.nc')
area = area.variables['garea'][:]


# *** START ROUTINE ***
mmap_in = 'BioEFLT_NWOOD.out'
map_title = 'Non-woody LT Emission Factor'
map_var = 'BioEFLT_NWOOD'
map_unit = 'kgCO2/GJ'
map_outname = 'BioEFLT_NWOOD'
timexist = False

if timexist:
    mmap,time = read_mym(mmap_in, path= InputDir.in_dir)
else:
    mmap = read_mym(mmap_in, path= InputDir.in_dir)

# Create map linking m-maps to lat/lon matrix
mapping = get_mmapping(grdfile)
gridmap = get_gridmap(mmap,mapping,timexist)
gridmap = np.ma.masked_where(maskmap[0] == maskmap.fill_value, gridmap) 
gridmap = ma.masked_values(gridmap, maskmap.fill_value)

# *** WRITE OUTPUT ***
writemap = WriteMaps(gridmap, map_title, map_var, map_unit, map_outname)
writemap.maptime2nc() if timexist else writemap.map2nc()