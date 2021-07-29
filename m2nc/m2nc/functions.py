"""
Functions required to convert m-maps to netCDF maps

All functions are inside the m2nc class. 

Each instance of this class converts an m-map to a netCDFmap 
"""
import netCDF4
import numpy as np
import numpy.ma as ma
from pym import read_mym, load_mym, write_mym
from dirs import InputDir, OutputDir
from outputs import WriteMaps

# Constants
class Constants: 
    NC = 66663

def get_mmapping(grdfile): 
    """
    Returns a list which links the rows of m-maps 
    to an x,y coordinate based on the latutudes and longitudes in
    a defining grdfile
    """
    nlats = 360
    nlons = 720
    lats = np.zeros(nlats)
    lons = np.zeros(nlons)
    lats[:] = 90. - (180./nlats)*np.arange(nlats) # north pole to south pole
    lons[:] = -180. + (180./nlats)*np.arange(nlons) # 180degree longitude eastward

    mapping = []
    for i in range(len(grdfile)):   # per row
        loc_lon = np.where(lons == grdfile[i,0])
        loc_lat = np.where(lats == grdfile[i,1])
        mapping.append([loc_lat[0].astype(np.int32), loc_lon[0].astype(np.int32)])
    return mapping

class m2nc:
    """
    Class which converts m-maps to netCDF maps.

    This class reads in required details of an m-map.
    It also reads in a 'mapping' array which links each m-map row to a x,y coordinate
    
    Subsequently, this class converts the m-map from a vector into a grid. 
    
    Then it  outputs it as a netCDF map, including relevant metadata.
    """
    def __init__(self, mmap_in, map_title, map_var, map_unit, map_outname, timexist, mapping):
        self.mmap_in = mmap_in
        self.map_title = map_title
        self.map_var = map_var
        self.map_unit = map_unit
        self.map_outname = map_outname
        self.timexist = timexist
        self.mapping = mapping

    def run_m2nc(self):
        """
        First: Read in the m-map

        Second: Using the "mapping", m-maps are converted to grid

        Third: Output this grid as a netCDF file  
        """
        print("\tReading in m-map")
        if self.timexist:
            self.mmap, self.time = read_mym(self.mmap_in, path= InputDir.m_in_dir)
        else:
            self.mmap = read_mym(self.mmap_in, path= InputDir.m_in_dir)

        # Create map linking m-maps to lat/lon matrix
        print("\tCreating gridded map")
        gridmap = self.get_gridmap(self.mmap, self.mapping, self.timexist)
        
        # *** WRITE OUTPUT ***
        print("\tWriting netCDF output")
        writemap = WriteMaps(gridmap, self.map_title, self.map_var, self.map_unit, self.map_outname, self.timexist)
        writemap.maptime2nc()

    def get_gridmap(self, mmap, mapping, existtime):
        """
        For each row in m-map get the required coordinates on an x,y grid 
        
        The resultant gridmap is declared as an NaN grid, so that netCDF can automatically apply a mask.
        """
        if existtime:
            gridmap = np.zeros((len(self.time), 360, 720)) * np.nan
            for t in range(len(self.time)):
                for i in range(len(mmap[0])):
                    map_loc = mapping[i]
                    gridmap[t,map_loc[0], map_loc[1]] = mmap[t][i]
                
            # Incase timesteps are missing:
            if len(gridmap) < 27:
                newtsteps = 27 - len(gridmap)
                newtdata = np.zeros((newtsteps,360,720))
                newtdata[:,:,:] = gridmap[0,:,:]
                gridmap = np.insert(gridmap,0,newtdata,axis=0)
        else:
            gridmap = np.zeros((360,720)) * np.nan
            for i in range(len(mmap[0])):
                map_loc = mapping[i]
                gridmap[map_loc[0],map_loc[1]] = mmap[0][i]

        return gridmap

class nc2m:
    """
    Class which converts netCDF maps to m-maps.

    This class reads in required details of an ncetCDF.
    It also reads in a 'mapping' array which links each m-map row to a x,y coordinate
    
    Subsequently, this class converts the grid of a netCDF map to a vector. 
    
    Then it  outputs it as an m-map.
    """
    def __init__(self, ncmap_in, map_var, map_outname, timexist, mapping):
        self.ncmap_in = ncmap_in
        self.map_var = map_var
        self.map_outname = map_outname
        self.timexist = timexist
        self.mapping = mapping

    def run_nc2m(self):
        """
        First: Read in the nc-map

        Second: Using the "mapping", m-maps are converted to grid

        Third: Output this grid as a netCDF file  
        """
        print("\tReading in nc-map")
        self.ncmap = self.read_map(InputDir.nc_in_dir + self.ncmap_in, self.map_var)                      # km^2, [NLATS,NLONS], Area per grid cell

        # Create map linking m-maps to lat/lon matrix
        print("\tCreating vector map")
        vectormap = self.get_vectormap(self.ncmap, self.mapping, self.timexist)
        
        # *** WRITE OUTPUT ***
        print("\tWriting m output")
        if self.timexist:
            timesteps=range(len(self.ncmap))
            write_mym(vectormap, years=timesteps, variable_name="data", filename=self.map_outname, filepath= OutputDir.m_out_dir, comment="Empty!")
        else:
            write_mym(vectormap, variable_name="data", filename=self.map_outname, filepath= OutputDir.m_out_dir, comment="Empty!")

    def read_map(self, file_loc, var_name, type='float32', maskvalue=-9999):
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
        nc_map = netCDF4.Dataset(file_loc)
        var_in = nc_map.variables[var_name][:]
        var_array = np.array(var_in, dtype=type)
        var_array = np.ma.masked_where(var_in == var_in.fill_value, var_array)
        var_array = ma.masked_values(var_array, maskvalue)
        
        return var_array

    def get_vectormap(self, ncmap, mapping, existtime):
            """
            For each row in m-map get the required coordinates on an x,y grid 
            
            Lookup ncmap value at these coordinates, and assign to vectormap row
            
            The resultant gridmap is declared as an NaN grid, so that netCDF can automatically apply a mask.
            """
            if existtime:
                vectormap = np.zeros((len(self.ncmap), Constants.NC)) * np.nan
                for t in range(len(self.ncmap)):
                    print("timestep: ", t)
                    for i in range(Constants.NC):
                        map_loc = mapping[i]
                        vectormap[t,i] = ncmap[t,map_loc[0], map_loc[1]]
                    
            else:
                vectormap = np.zeros(Constants.NC) * np.nan
                for i in range(Constants.NC):
                    map_loc = mapping[i]
                    vectormap[i] = ncmap[map_loc[0], map_loc[1]]

            return vectormap
