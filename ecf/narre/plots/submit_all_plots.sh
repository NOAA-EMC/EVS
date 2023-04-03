#!/bin/bash 

cd /lfs/h2/emc/vpppg/noscrub/binbin.zhou/EVS/ecf/narre/plots

qsub jevs_narre_past31days_plots.ecf  
qsub jevs_narre_past90days_plots.ecf
