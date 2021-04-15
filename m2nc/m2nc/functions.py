"""
Functions required to convert m-maps to netCDF maps

All functions are inside the m2nc class. 

Each instance of this class converts an m-map to a netCDFmap 
"""
import netCDF4
import numpy as np
from pym import read_mym, load_mym
from dirs import InputDir
from outputs import WriteMaps

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
            self.mmap, self.time = read_mym(self.mmap_in, path= InputDir.in_dir)
        else:
            self.mmap = read_mym(self.mmap_in, path= InputDir.in_dir)

        # Create map linking m-maps to lat/lon matrix
        print("\tCreating gridded map")
        gridmap = self.get_gridmap(self.mmap, self.mapping, self.timexist)
        
        # *** WRITE OUTPUT ***
        print("\tWriting netCDF output")
        writemap = WriteMaps(gridmap, self.map_title, self.map_var, self.map_unit, self.map_outname)
        writemap.maptime2nc() if self.timexist else writemap.map2nc()
    

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
