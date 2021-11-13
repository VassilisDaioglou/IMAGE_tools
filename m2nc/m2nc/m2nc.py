"""
Script to produce maps and convert between formats (m & netCDF)

Author: Vassilis Daioglou
Date:   April 2021: m2nc functionality
        July 2021: Added nc2m functionality
        November 2021: Added list2map (m&netCDF) functionality
"""
import numpy as np
from flags import RunFunction
from functions import m2nc, nc2m, get_mmapping
from dirs import InputDir


def main(run):
    # File identifying grid coordinates of m-map, needed to create m-2-grid mapping
    grdfile  = np.loadtxt(InputDir.data_dir + 'mcoord.txt')
    mapping = get_mmapping(grdfile)

    if run.m2nc:
        print("\n***Running m2nc***")
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

    if run.nc2m:
        print("\n***Running nc2m***")
        # List of maps to convert from nc to m
            # 1. nc-map file name, 2. Variable Name, 3. Output Name, 4. Has time dimension (boolean), M-file header comment,Multiplier
        nc2m_maps_list = [
            #['Species_loss_factors_total.nc','layer','Species_loss_factor',False,"Species loss factors (terrestrial vertebrates), 1e9 10log loss/Ha",1e9]
            #['consumption_waterstress_majorbasins.nc','waterstress','consumption_waterstress_majorbasins',True,"Consumption Waterstress Major Basins",1],
            #['consumption_waterstress_smallbasins.nc','waterstress','consumption_waterstress_smallbasins',True,"Consumption Waterstress Small Basins",1],
            #['withdrawals_waterstress_majorbasins.nc','waterstress','withdrawals_waterstress_majorbasins',True,"Withdrawals Waterstress Major Basins",1],
            #['withdrawals_waterstress_smallerbasins.nc','waterstress','withdrawals_waterstress_smallerbasins',True,"Withdrawals Waterstress Small Basins",1]
        ]

        for outmap in nc2m_maps_list:
            print("Processing Map: ", outmap[5])
            write_nc2m = nc2m(outmap[0], outmap[1], outmap[2], outmap[3], outmap[4], outmap[5], mapping)
            write_nc2m.run_nc2m() 
    
    if run.list2m or run.list2nc:
        print("\n***Start processing list data***")
        from outputs import WriteMaps
        import pandas as pd
        # First have to read in nc map with country IDs
        print("\tReading in nc country-map")
        cntry_map = nc2m.read_map('blank positional argument', InputDir.data_dir + 'countries_grid.nc', 'layer')
        print("\tReading in listed data")
        # Second have to read in list data with appropriate format:
        list_df = pd.read_excel(InputDir.list_in_dir + 'Mapping_countries_grid_feasibility.xlsx', sheet_name = 'Mapping', header = 1)

        # For every country ID on cntry_map, find required value on list_df
        #list_df.loc[list_df['grdID'] == 2, 'spfs_cor']
        print("\tAssigning listed data to gridded map")
        gridmap = np.zeros((360, 720))
        
        #cntry_map[cntry_map.mask] = cntry_map.fill_value    # have to make sure that the fill value is returned on masked cells
        #gridmap[:,:] = list_df.loc[list_df['grdID'] == cntry_map[:,:], 'spfs_cor'].iloc[0]
        
        for i in range(360):
            for j in range(720):
                print("Coordinates: ", i, ', ', j)
                cntry_map[cntry_map.mask] = cntry_map.fill_value    # have to make sure that the fill value is returned on masked cells
                gridmap[i,j] = list_df.loc[list_df['grdID'] == cntry_map[i,j], 'spfs_cor'].iloc[0]
        
        map_title = 'Socio-political feasability score'
        map_var = 'spfs'
        map_unit = '-'
        map_outname = 'socio-political_feasability_score'
        timexist = False

        print("\tWriting netCDF output")
        #writemap = WriteMaps(gridmap, self.map_title, self.map_var, self.map_unit, self.map_outname, self.timexist)
        writemap = WriteMaps(gridmap, map_title, map_var, map_unit, map_outname, timexist)
        writemap.maptime2nc()


        print("done")

if __name__ == "__main__":
    run = RunFunction()

     # Run main emission-cost-supply tool
    main(run)