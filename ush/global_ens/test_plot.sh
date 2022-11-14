#!/bin/ksh

set -x 

YYYY=2022

last=Oct

sed -e "s!YYYY!${yyyy}!g" -e "s!December!$last!g"  /lfs/h2/emc/vpppg/noscrub/binbin.zhou/EVS/ush/global_ens/evs_global_ens_headline_plot.py  >  evs_global_ens_headline_plot.py 


python evs_global_ens_headline_plot.py



