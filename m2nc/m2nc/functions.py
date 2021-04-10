"""
Functions
"""
import netCDF4
import numpy as np
import numpy.ma as ma
from dirs import InputDir

def read_map(file_name, var_name, type='float32', maskvalue=-9999):
    """
    Return an array with the values of a variable in a netCDF map
    """
    nc_map = netCDF4.Dataset(InputDir.data_dir + file_name)
    var_array = extract_map(nc_map, var_name, type, maskvalue)
    return var_array

def extract_map(file, variable, type='float32', maskvalue=-9999):
    """
    Returns a numpy array of the variable in a netCDF file
    Inputs:
    1. netCDF File
    2. Variable name
    3. Data type of output. float64 by default
    4. Mask value: -9999 by default

    Output:
    Masked numpy array of correct dtype and mask fill_value

    Comment:
    Have to store a pre-corrected version of the map
    because the fill_value changes during operations.
    This is a numpy bug, see: https://github.com/numpy/numpy/issues/3762
    """
    varin = file.variables[variable][:]
    varout = np.array(varin, dtype=type)
    varout = np.ma.masked_where(varin == varin.fill_value, varout)
    varout = ma.masked_values(varout, maskvalue)
    return varout

def get_mmapping(grdfile): 
    """
    Returns a matrix which maps the rows of m-maps 
    on a grid of latitude/longitude
    """
    nlats = 360
    nlons = 720
    lats = np.zeros(nlats)
    lons = np.zeros(nlons)
    lats[:] = 90. - (180./nlats)*np.arange(nlats) # north pole to south pole
    lons[:] = -180. + (180./nlats)*np.arange(nlons) # 180degree longitude eastward

    mapping = np.zeros((360,720))
    for i in range(len(grdfile)):   # per row
        loc_lon = np.where(lons == grdfile[i,0])
        loc_lat = np.where(lats == grdfile[i,1])
        mapping[loc_lat[0].astype(np.int32),loc_lon[0].astype(np.int32)] = i
    return mapping

def get_gridmap(mmap,mapping, existtime):
    """
    For each row in m-map get the map's value 
    Put that value in relevant location of new lat/lon matrix
    using the mapping matrix
    """
    if existtime:
        gridmap = np.zeros((len(time), 360, 720))
        for t in range(len(time)):
            for i in range(len(mmap[0])):
                map_loc = np.where(mapping == i) # Returns 2d array with lat & lon location for that m-map row
                gridmap[t,map_loc[0].astype(np.int32),map_loc[1].astype(np.int32)] = mmap[t][i]
        
        # Incase timesteps are missing:
        if len(gridmap) < 27:
            newtsteps = 27 - len(gridmap)
            newtdata = np.zeros((newtsteps,360,720))
            newtdata[:,:,:] = gridmap[0,:,:]
            gridmap = np.insert(gridmap,0,newtdata,axis=0)
    else:
        gridmap = np.zeros((360,720))
        for i in range(len(mmap[0])):
            map_loc = np.where(mapping == i) # Returns 2d array with lat & lon location for that m-map row
            gridmap[map_loc[0].astype(np.int32),map_loc[1].astype(np.int32)] = mmap[0][i]

    return gridmap

def get_r2map(array, regionmap):
    """
    Convert array of some regional values factors into a map
    
    Input:
    (i) Array of values, shape: (TIMESTEP, [VALUES], REGION)
    (ii) Length of array of values
    (iii) Region Map array, shape: (NLATS, NLONS)

    Ouput:
    Map of array values, shape: (TIMESTEP, lats, lons, [VALUES])
    """
    q, r = regionmap.shape
    region27_long = regionmap.reshape(q*r)

    array_len = len(array[0])

    result_r = np.array([array[:,:,i-1] for i in region27_long.data])
    result = result_r.transpose(1,0,2).reshape(NTIMES,q,r,array_len)

    return result