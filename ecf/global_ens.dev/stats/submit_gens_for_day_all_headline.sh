#!/bin/bash -l

export VDATE=20221110 
qsub jevs_gefs_headline_grid2grid_stats.ecf 
qsub jevs_naefs_headline_grid2grid_stats.ecf 
qsub jevs_gfs_headline_grid2grid_stats.ecf 

