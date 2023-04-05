#!/bin/bash
#
#
yyyy=2023
mm=02
for dd in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28  ; do
 export VDATE=$yyyy$mm$dd
 /lfs/h2/emc/vpppg/noscrub/binbin.zhou/EVS/ecf/global_ens.dev/stats/jevs_gefs_headline_grid2grid_stats.ecf
 /lfs/h2/emc/vpppg/noscrub/binbin.zhou/EVS/ecf/global_ens.dev/stats/jevs_gfs_headline_grid2grid_stats.ecf
 /lfs/h2/emc/vpppg/noscrub/binbin.zhou/EVS/ecf/global_ens.dev/stats/jevs_naefs_headline_grid2grid_stats.ecf
done
#
