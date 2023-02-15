#!/bin/bash

#------------------------------------------------
# Run the GEFS-Wave EVS prep, stats, plots and   
# transfer the plots to emcrzdm                  
#                                                
# Deanna Spindler                                
# 15 February 2023                               
#------------------------------------------------

srcDir='/path/to/cron/scripts'
EVShome='/path/to/EVS'
GEFSecf="${EVShome}/ecf/global_ens"

# remove the previous log files
rm -f /path/to/cron/logs/transfer_gefs_EVS.log

job1=$(qsub ${GEFSecf}/prep/jevs_global_ens_wave_grid2obs_prep.ecf)
job2=$(qsub -W depend=afterok:${job1} ${GEFSecf}/stats/jevs_global_ens_wave_grid2obs_stats.ecf)
job3=$(qsub -W depend=afterok:${job2} ${GEFSecf}/plots/jevs_global_ens_wave_grid2obs_plots.ecf)
qsub -W depend=afterok:${job3} ${srcDir}/transfer_gefs_evs.pbs

