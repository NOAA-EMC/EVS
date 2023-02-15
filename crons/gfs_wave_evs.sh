#!/bin/bash

#------------------------------------------------
# Run the GFS-Wave EVS prep, stats, and plot     
# then transfer the plots to emcrzdm             
#                                                
# Deanna Spindler                                
# 15 February 2023                               
#------------------------------------------------

srcDir='/path/to/cron/scripts'
EVShome='/path/to/EVS'
GFSecf="${EVShome}/ecf/global_det"

# remove the previous log files
rm -f /path/to/cron/logs/transfer_gfs_EVS.log

job1=$(qsub ${GFSecf}/prep/jevs_global_det_wave_grid2obs_prep.ecf)
job2=$(qsub -W depend=afterok:${job1} ${GFSecf}/stats/jevs_global_det_wave_grid2obs_stats.ecf)
job3=$(qsub -W depend=afterok:${job2} ${GFSecf}/plots/jevs_global_det_wave_grid2obs_plots.ecf)
qsub -W depend=afterok:${job3} ${srcDir}/transfer_gfs_evs.pbs

