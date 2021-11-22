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
from dirs import InputDir, OutputDir


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
            # 1. nc-map file name, 2. Variable Name, 3. Output Name, 4. Has time dimension (boolean), 5. Timestep, 6. 3rd Dimension index -in case of filtering (boolean), 7. M-file header comment, 8. Multiplier
        nc2m_maps_list = [
            ['GLANDCOVERDETAIL_30MIN_HE.nc','GLANDCOVERDETAIL_30MIN','Half_Earth_constraint',True, 2100, 5,'Half Earth Biodiversity Constraint',1],
            #['GLANDCOVERDETAIL_30MIN_double_AICHI.nc','GLANDCOVERDETAIL_30MIN','Double_AICHI_constraint',True, 27, 5,'Double-AICHI Biodiversity Constraint',1],
            #['socio-political_feasability_score.nc','socio-political_feasability_score','socio-political_feasability_score',False,'Socio-political feasability score from Roe et al (2021)',1]
            #['Species_loss_factors_total.nc','layer','Species_loss_factor',False,"Species loss factors (terrestrial vertebrates), 1e9 10log loss/Ha",1e9]
            #['consumption_waterstress_majorbasins.nc','waterstress','consumption_waterstress_majorbasins',True,1,"Consumption Waterstress Major Basins",1],
            #['consumption_waterstress_smallbasins.nc','waterstress','consumption_waterstress_smallbasins',True,1,"Consumption Waterstress Small Basins",1],
            #['withdrawals_waterstress_majorbasins.nc','waterstress','withdrawals_waterstress_majorbasins',True,1,"Withdrawals Waterstress Major Basins",1],
            #['withdrawals_waterstress_smallerbasins.nc','waterstress','withdrawals_waterstress_smallerbasins',True,1,"Withdrawals Waterstress Small Basins",1]
        ]

        for outmap in nc2m_maps_list:
            print("Processing Map: ", outmap[6])
            write_nc2m = nc2m(outmap[0], outmap[1], outmap[2], outmap[3], outmap[4], outmap[5], outmap[6], outmap[7], mapping)
            write_nc2m.run_nc2m() 
    
    if run.list2m or run.list2nc:
        print("\n***Start processing list data***")
        from outputs import WriteMaps
        import pandas as pd
        # First have to read in nc map with country IDs
        print("\tReading in nc country-map")
        cntry_map = nc2m.read_map('blank positional argument', InputDir.data_dir + 'countries_grid.nc', 'layer')
        
        # Second have to read in list data with appropriate format:
        print("\tReading in listed data")
        list_df = pd.read_excel(InputDir.list_in_dir + 'Mapping_countries_grid_feasibility.xlsx', sheet_name = 'Mapping', header = 1)

        # Identify column in list to be mapped (i.e. variable)
        map_var = 'spfs_cor'

        # For every country ID on cntry_map, find required value on list_df
        print("\tAssigning listed data to gridded map")
        gridmap = np.zeros((360, 720))
        
        cntry_map[cntry_map.mask] = cntry_map.fill_value    # have to make sure that the fill value is returned on masked cells
        for i in range(360):
            for j in range(720):
                print("Coordinates: ", i, ', ', j)
                gridmap[i,j] = list_df.loc[list_df['grdID'] == cntry_map[i,j], map_var].iloc[0]

        gridmap = np.ma.masked_where(gridmap == cntry_map.fill_value, gridmap)
        
        if run.list2nc:
             # 1. Map Tital, 2. Variable Name, 3. Unit, 4. Output Name, 5. Time exit (boolean)
            list2nc_maps_list = ['Socio-political feasability score',map_var,'-','socio-political_feasability_score',False]

            print("\tWriting netCDF output")
            writemap = WriteMaps(gridmap, list2nc_maps_list[0], list2nc_maps_list[1], list2nc_maps_list[2], list2nc_maps_list[3], list2nc_maps_list[4])
            writemap.maptime2nc()
        
        if run.list2m:
            from pym import write_mym
            vectormap = nc2m.get_vectormap('missing positional argument',gridmap, mapping, False)
            write_mym(data=vectormap, variable_name=map_var, filename='socio-political_feasability_score', path= OutputDir.m_out_dir, comment='Socio-political feasability score from Roe et al (2021)')
        
        print("done")

if __name__ == "__main__":
    run = RunFunction()

     # Run main emission-cost-supply tool
    main(run)