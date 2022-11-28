#!/bin/bash -l

cd /lfs/h2/emc/vpppg/noscrub/binbin.zhou/EVS/ecf/mesoscale.dev/stats
rm evs*stats.o*

qsub jevs_sref_cnv_stats.ecf 
wait 1800

qsub jevs_sref_precip_stats.ecf
qsub jevs_sref_grid2obs_stats.ecf

