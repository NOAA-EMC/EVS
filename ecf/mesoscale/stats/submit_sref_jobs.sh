#!/bin/bash -l

cd /lfs/h2/emc/vpppg/noscrub/${USER}/EVS/ecf/mesoscale/stats
rm evs*stats.o*

qsub jevs_sref_cnv_stats.ecf 
sleep 1800
qsub jevs_sref_precip_stats.ecf
qsub jevs_sref_grid2obs_stats.ecf

