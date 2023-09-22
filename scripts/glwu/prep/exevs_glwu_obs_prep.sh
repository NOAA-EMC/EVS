#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_obs_prep.sh
# Purpose of Script: To pre-process NDBC validation data.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

# convert NDBC *.txt files into a netcdf file using ASCII2NC
export RUN=ndbc
mkdir -p $COMOUTprep/glwu.$VDATE/$RUN

export MET_NDBC_STATIONS=${FIXevs}/ndbc_stations/ndbc_stations.xml
ndbc_txt_ncount=$(ls -l $COMINobs/$VDATE/validation_data/marine/buoy/*.txt |wc -l)
#if [ -s $COMINobs/$VDATE/validation_data/marine/buoy/activestations.xml ] ; then
if [ $ndbc_txt_ncount -gt 0 ]; then
  run_metplus.py -c $CONFIGevs/metplus_glwu.conf \
  -c $CONFIGevs/grid2obs/$STEP/ASCII2NC_obsNDBC.conf
else
  export subject="NDBC Data Missing for EVS glwu"
  echo "Warning: No NDBC data was available for valid date $VDATE." > mailmsg
  echo "Missing files are located at $COMINobs/$VDATE/validation_data/marine/buoy/." >> mailmsg
  cat mailmsg | mail -s "$subject" $maillist
fi


exit

################################ END OF SCRIPT ################################
