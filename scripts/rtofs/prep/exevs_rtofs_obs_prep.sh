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
mkdir -p $DATA/rtofs.$VDATE/$RUN

if [ -s $COMINobs/$VDATE/seaice/osisaf/ice_conc_nh_polstere-100_multi_${VDATE}1200.nc ] ; then
  for ftype in nh sh; do
    cdo remapbil,$FIXevs/rtofs_$RUN.grid \
    $COMINobs/$VDATE/seaice/osisaf/ice_conc_${ftype}_polstere-100_multi_${VDATE}1200.nc \
    $DATA/rtofs.$VDATE/$RUN/ice_conc_${ftype}_polstere-100_multi_${VDATE}1200.nc
    cp $DATA/rtofs.$VDATE/$RUN/ice_conc_${ftype}_polstere-100_multi_${VDATE}1200.nc $COMOUTprep/rtofs.$VDATE/$RUN
  done
else
  export subject="OSI-SAF Data Missing for EVS RTOFS"
  echo "Warning: No OSI-SAF data was available for valid date $VDATE." > mailmsg
  echo "Missing file is $COMINobs/$VDATE/seaice/osisaf/ice_conc_nh_polstere-100_multi_${VDATE}1200.nc." >> mailmsg
  cat mailmsg | mail -s "$subject" $maillist
fi

# convert NDBC *.txt files into a netcdf file using ASCII2NC
export RUN=ndbc
mkdir -p $COMOUTprep/rtofs.$VDATE/$RUN

if [ -s $COMINobs/$VDATE/validation_data/marine/buoy/activestations.xml ] ; then
  run_metplus.py -c $CONFIGevs/metplus_rtofs.conf \
  -c $CONFIGevs/grid2obs/$STEP/ASCII2NC_obsNDBC.conf
else
  export subject="NDBC Data Missing for EVS RTOFS"
  echo "Warning: No NDBC data was available for valid date $VDATE." > mailmsg
  echo "Missing files are located at $COMINobs/$VDATE/validation_data/marine/buoy/." >> mailmsg
  cat mailmsg | mail -s "$subject" $maillist
fi

# convert Argo basin files into a netcdf file using python embedding
export RUN=argo
mkdir -p $COMOUTprep/rtofs.$VDATE/$RUN

if [ -s $COMINobs/$VDATE/validation_data/marine/argo/atlantic_ocean/${VDATE}_prof.nc ] ; then
  run_metplus.py -c $CONFIGevs/metplus_rtofs.conf \
  -c $CONFIGevs/grid2obs/$STEP/ASCII2NC_obsARGO.conf
else
  export subject="Argo Data Missing for EVS RTOFS"
  echo "Warning: No Argo data was available for valid date $VDATE." > mailmsg
  echo "Missing file is $COMINobs/$VDATE/validation_data/marine/argo/atlantic_ocean/${VDATE}_prof.nc." >> mailmsg
  cat mailmsg | mail -s "$subject" $maillist
fi

exit

################################ END OF SCRIPT ################################
