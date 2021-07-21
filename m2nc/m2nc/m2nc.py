"""
Script to convert m-maps to netCDF maps

Author: Vassilis Daioglou
Date: April 2021
    - July 2021: Added nc2m functionality
"""
import numpy as np
from functions import m2nc, nc2m, get_mmapping
from dirs import InputDir

# File identifying grid coordinates of m-map, needed to create m-2-grid mapping
grdfile  = np.loadtxt(InputDir.data_dir + 'mcoord.txt')
mapping = get_mmapping(grdfile)

print("\n***Runningm2nc***")
# List of maps to convert from m to nc
    # Create list of maps to be outputted with the following information:
    # 1. m-map file name, 2. Map Title, 3. Variable Name, 4. Unit, 5. Output Name, 6. Has time dimension (boolean)
m2nc_maps_list = [
            #['EFMapType2_t.out','Non-Woody Gradual Emission Factor','NWOOD_EF_Gradual','kgCO2/km^2','NWOOD_EF_Gradual_t',True],
            #['nw_EmisType1_pkm.out','Instantaneous Emission Factor','EF_Instant','kgCO2/km^2','EF_Instant',False],
            #['nw_EmisType2ST_pkm.out','Non-Woody Gradual Emission Factor','NWOOD_EF_Gradual','kgCO2/km^2','NWOOD_EF_Gradual',False],
            #['wd_EmisType2ST_pkm.out','Woody Gradual Emission Factor','WOODY_EF_Gradual','kgCO2/km^2','WOODY_EF_Gradual',False],
            #['sc_EmisType2ST_pkm.out','Sugarcane Gradual Emission Factor','SUGAR_EF_Gradual','kgCO2/km^2','SUGAR_EF_Gradual',False],
            #['mz_EmisType2ST_pkm.out','Maize Gradual Emission Factor','MAIZE_EF_Gradual','kgCO2/km^2','MAIZE_EF_Gradual',False],
            #['oc_EmisType2ST_pkm.out','Oilcrops Gradual Emission Factor','OILCR_EF_Gradual','kgCO2/km^2','OILCR_EF_Gradual',False],
            #['ImplementationMap.dat','Implementation Factor','Impl_fac','-','Impl_fac',True],
            #['BFCellFrac.dat','Fraction of Grid Cell Currently Used for Biofuels','BFCellFrac','-','BFCellFrac',True],
            ]
            
for outmap in m2nc_maps_list:
    print("Processing Map: ", outmap[1])
    write_m2nc = m2nc(outmap[0], outmap[1], outmap[2], outmap[3], outmap[4], outmap[5], mapping)
    write_m2nc.run_m2nc() 

print("\n***Runningnc2m***")
# List of maps to convert from nc to m
    # 1. nc-map file name, 2. Variable Name, 3. Output Name, 4. Has time dimension (boolean)
nc2m_maps_list = [
    ['consumption_waterstress_majorbasins.nc','waterstress','consumption_waterstress_majorbasins',True]
]

for outmap in nc2m_maps_list:
    print("Processing Map: ", outmap[1])
    write_nc2m = nc2m(outmap[0], outmap[1], outmap[2], outmap[3], mapping)
    write_nc2m.run_nc2m() 
