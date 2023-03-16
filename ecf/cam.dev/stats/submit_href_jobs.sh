#!/bin/bash -l

cd /lfs/h2/emc/vpppg/noscrub/${USER}/EVS/ecf/cam.dev/stats

qsub jevs_href_grid2obs_stats.ecf  
qsub jevs_href_precip_stats.ecf
qsub jevs_href_spcoutlook_stats.ecf
