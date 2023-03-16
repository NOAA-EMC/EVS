#!/bin/bash -l
cd /lfs/h2/emc/vpppg/noscrub/binbin.zhou/EVS/ecf/cam.dev/plots

qsub jevs_href_grid2obs_ctc_past31days_plots.ecf   
#qsub jevs_href_grid2obs_mlcape_past31days_plots.ecf  
qsub jevs_href_profile_past31days_plots.ecf 
qsub jevs_href_grid2obs_ecnt_past31days_plots.ecf  
qsub jevs_href_precip_past31days_plots.ecf
qsub jevs_href_snowfall_past31days_plots.ecf

qsub jevs_href_grid2obs_ctc_past90days_plots.ecf
#qsub jevs_href_grid2obs_mlcape_past90days_plots.ecf
qsub jevs_href_profile_past90days_plots.ecf
qsub jevs_href_grid2obs_ecnt_past90days_plots.ecf
qsub jevs_href_precip_past90days_plots.ecf
qsub jevs_href_snowfall_past90days_plots.ecf

qsub jevs_href_precip_spatial_plots.ecf
