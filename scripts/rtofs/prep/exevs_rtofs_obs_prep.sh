#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_obs_prep.sh
# Purpose of Script: To pre-process OSI-SAF, NDBC, and Argo validation data.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# convert OSI-SAF data into lat-lon grid
export RUN=osisaf
mkdir -p $COMOUTprep/rtofs.$VDATE/$RUN

for ftype in nh sh; do
cdo remapbil,$FIXevs/rtofs_$RUN.grid \
$COMINobs/$VDATE/seaice/osisaf/ice_conc_${ftype}_polstere-100_multi_${VDATE}1200.nc \
$COMOUTprep/rtofs.$VDATE/$RUN/ice_conc_${ftype}_polstere-100_multi_${VDATE}1200.nc
done

# convert NDBC *.txt files into a netcdf file using ASCII2NC
export RUN=ndbc
mkdir -p $COMOUTprep/rtofs.$VDATE/$RUN

run_metplus.py -c $CONFIGevs/metplus_rtofs.conf \
-c $CONFIGevs/grid2obs/$STEP/ASCII2NC_obsNDBC.conf

# convert Argo basin files into a netcdf file using python embedding
export RUN=argo
mkdir -p $COMOUTprep/rtofs.$VDATE/$RUN

run_metplus.py -c $CONFIGevs/metplus_rtofs.conf \
-c $CONFIGevs/grid2obs/$STEP/ASCII2NC_obsARGO.conf

exit

################################ END OF SCRIPT ################################
