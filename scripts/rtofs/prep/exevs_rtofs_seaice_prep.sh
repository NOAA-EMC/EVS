#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_seaice_prep.sh
# Purpose of Script: To pre-process OSI-SAF validation data.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# convert OSI-SAF data into lat-lon grid
mkdir -p $COMOUT/rtofs.$VDATE/osisaf

for ftype in nh sh; do
cdo remapbil,$FIXevs/rtofs_osisaf.grid \
$COMINobs/$VDATE/seaice/osisaf/ice_conc_${ftype}_polstere-100_multi_${VDATE}1200.nc \
$COMOUT/rtofs.$VDATE/osisaf/ice_conc_${ftype}_polstere-100_multi_${VDATE}1200.nc
done

exit

################################ END OF SCRIPT ################################
