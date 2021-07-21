"""
Script to convert m-maps to netCDF maps

Author: Vassilis Daioglou
Date: April 2021
"""
import numpy as np
from functions import m2nc, get_mmapping
from dirs import InputDir

# Create list of maps to be outputted with the following information:
    # 1. m-map file name, 2. Map Title, 3. Variable Name, 4. Unit, 5. Output Name, 6. Has time dimension (boolean)
        
output_maps_list = [
            #['EFMapType2_t.out','Non-Woody Gradual Emission Factor','NWOOD_EF_Gradual','kgCO2/km^2','NWOOD_EF_Gradual_t',True],
            #['nw_EmisType1_pkm.out','Instantaneous Emission Factor','EF_Instant','kgCO2/km^2','EF_Instant',False],
            #['nw_EmisType2ST_pkm.out','Non-Woody Gradual Emission Factor','NWOOD_EF_Gradual','kgCO2/km^2','NWOOD_EF_Gradual',False],
            #['wd_EmisType2ST_pkm.out','Woody Gradual Emission Factor','WOODY_EF_Gradual','kgCO2/km^2','WOODY_EF_Gradual',False],
            #['sc_EmisType2ST_pkm.out','Sugarcane Gradual Emission Factor','SUGAR_EF_Gradual','kgCO2/km^2','SUGAR_EF_Gradual',False],
            #['mz_EmisType2ST_pkm.out','Maize Gradual Emission Factor','MAIZE_EF_Gradual','kgCO2/km^2','MAIZE_EF_Gradual',False],
            #['oc_EmisType2ST_pkm.out','Oilcrops Gradual Emission Factor','OILCR_EF_Gradual','kgCO2/km^2','OILCR_EF_Gradual',False],
            #['ImplementationMap.dat','Implementation Factor','Impl_fac','-','Impl_fac',True],
            ['BFCellFrac.dat','Fraction of Grid Cell Currently Used for Biofuels','BFCellFrac','-','BFCellFrac',True],
            ]
            
# File identifying grid coordinates of m-map, needed to create m-2-grid mapping
grdfile  = np.loadtxt(InputDir.data_dir + 'mcoord.txt')
mapping = get_mmapping(grdfile)

for outmap in output_maps_list:
    print("\nProcessing Map: ", outmap[1])
    write_output = m2nc(outmap[0], outmap[1], outmap[2], outmap[3], outmap[4], outmap[5], mapping)
    write_output.run_m2nc() 
