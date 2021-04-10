"""
Script to convert m-maps to netCDF maps

Author: Vassilis Daioglou
Date: April 2021
"""
from functions import m2nc

# Create list of maps to be outputted with the following information:
    # 1. m-map file name, 2. Map Title, 3. Variable Name, 4. Unit, 5. Output Name, 6. Has time dimension (boolean)
        
output_maps_list = [
            ['nw_EmisType2ST_pkm.out','Woody Gradual Emission Factor','WOODY_EF_Gradual','kgCO2/km^2','WOODY_EF_Gradual',False]]
        
for outmap in output_maps_list:
    m2nc = m2nc(outmap[0], outmap[1], outmap[2], outmap[3], outmap[4], outmap[5])
    m2nc.run_m2nc() 
