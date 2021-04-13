"""
Functions required to convert m-maps to netCDF maps

All functions are inside the m2nc class. 

Each instance of this class converts an m-map to a netCDFmap 
"""
import netCDF4
import numpy as np
import numpy.ma as ma
from pym import read_mym, load_mym
from dirs import InputDir
from outputs import WriteMaps

class m2nc:
    """
    Class which converts m-maps to netCDF maps.

    This class reads in required details of an m-map. It then converts this
    map from a vector into a grid, and subsequently outputs it, including
    metadata into a netCDF map.
    """
    def __init__(self, mmap_in, map_title, map_var, map_unit, map_outname, timexist):
        self.mmap_in = mmap_in
        self.map_title = map_title
        self.map_var = map_var
        self.map_unit = map_unit
        self.map_outname = map_outname
        self.timexist = timexist

    def run_m2nc(self):
        """
        Function which starts procedure.
        Reads in ancilliary data needed to convert m-map to grids. 
            - text file linking m-map verctor to coordinates
            - Generic map used to apply masking of oceans etc.
        """
        # *** DATA NEEDED TO GET THE m-to-netCDF MAPPING ***
        self.grdfile  = np.loadtxt(InputDir.data_dir + 'mcoord.txt')
        
        # Get map for masking
        self.maskmap = netCDF4.Dataset(InputDir.data_dir + 'GNLCT_30MIN.nc')
        self.maskmap = self.maskmap.variables['GNLCT_30MIN'][:]

        # Produce NC maps
        self.make_nc_map()

    def make_nc_map(self):
        """
        Procedure which m-maps (vectors) to to grids and subsequently to netCDF maps

        First: Map m-map vector to grid using a file (grdfile) linking m-map cells to coordinates
        This produces a "mapping"

        Second: Using the "mapping", m-maps are converted to grid

        Third: Output this grid as a netCDF file  
        """
        if self.timexist:
            self.mmap, self.time = read_mym(self.mmap_in, path= InputDir.in_dir)
        else:
            self.mmap = read_mym(self.mmap_in, path= InputDir.in_dir)

        # Create map linking m-maps to lat/lon matrix
        mapping = self.get_mmapping()
        gridmap = self.get_gridmap(self.mmap, mapping, self.timexist)
        gridmap = np.ma.masked_where(self.maskmap[0] == self.maskmap.fill_value, gridmap) 
        gridmap = ma.masked_values(gridmap, self.maskmap.fill_value)

        # *** WRITE OUTPUT ***
        writemap = WriteMaps(gridmap, self.map_title, self.map_var, self.map_unit, self.map_outname)
        writemap.maptime2nc() if self.timexist else writemap.map2nc()
    
    def read_map(self, file_name, var_name, type='float32', maskvalue=-9999):
        """
        Return an array with the values of a variable in a netCDF map
        """
        nc_map = netCDF4.Dataset(InputDir.data_dir + file_name)
        var_array = self.extract_map(nc_map, var_name, type, maskvalue)
        return var_array

    def extract_map(self, file, variable, type='float32', maskvalue=-9999):
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

    def get_mmapping(self): 
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
        for i in range(len(self.grdfile)):   # per row
            loc_lon = np.where(lons == self.grdfile[i,0])
            loc_lat = np.where(lats == self.grdfile[i,1])
            mapping[loc_lat[0].astype(np.int32),loc_lon[0].astype(np.int32)] = i
        return mapping

    def get_gridmap(self, mmap, mapping, existtime):
        """
        For each row in m-map get the map's value 
        Put that value in relevant location of new lat/lon matrix
        using the mapping matrix
        """
        if existtime:
            gridmap = np.zeros((len(self.time), 360, 720))
            for t in range(len(self.time)):
                print("time-step: ",t)
                for i in range(len(mmap[0])):
                    map_loc = np.where(mapping == i) # Returns 2d array with lat & lon location for that m-map row
                    gridmap[t,map_loc[0], map_loc[1]] = mmap[t][i]
                
                # Using list comprehension (THIS IS SLOWER!!)
                #[gridmap[t, mmap[t][np.where(mapping == i)[0]].astype(np.int32), mmap[t][np.where(mapping == i)[1]].astype(np.int32)] for i in range(len(mmap[0]))]
                
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
