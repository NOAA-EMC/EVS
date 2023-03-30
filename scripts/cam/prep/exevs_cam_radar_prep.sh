#!/bin/bash
###############################################################################
# Name of Script: exevs_cam_radar_prep.sh
# Contact(s):     Logan Dawson
# Purpose of Script: This script preprocesses MRMS radar observations for 
#                    CAM verification.
# History Log:
# 12/22/2022: Initial script assembled by Logan Dawson 
###############################################################################


set +x

echo 
echo " ENTERING SUB SCRIPT $0 "
echo

set -x




############################################################
# Copy and unzip MRMS product files
############################################################
mkdir -p $COMOUTmrms

python $USHevs/${COMPONENT}/prep_mrms_radar_files.py
export err=$?; err_chk


############################################################
# Set some other environment variables 
############################################################
export VERIF_GRID=G227
export VERIF_GRID_DX=5.079
export GAUSS_RAD=25.395
export MAX_REGRID_WIDTH=17



############################################################
# Check for MRMS files to process or exit gracefully
############################################################

RADAR_FIELDS="REFC RETOP"

#export DOMAIN="conus alaska"
export DOMAIN=conus

# Regrid each MRMS product
for RADAR_FIELD in ${RADAR_FIELDS}; do

   if [ $RADAR_FIELD = REFC ]; then
      MRMS_PRODUCT=MergedReflectivityQCComposite_00.50
   elif [ $RADAR_FIELD = REFD1 ]; then
      MRMS_PRODUCT=SeamlessHSR_00.00
   elif [ $RADAR_FIELD = RETOP ]; then
      MRMS_PRODUCT=EchoTop18_00.50
   fi

   if [ -e $DATA/MRMS_${DOMAIN}_tmp/${MRMS_PRODUCT}_${VDATE}-${cyc}0000.grib2 ]; then

      ${METPLUS_PATH}/ush/run_metplus.py -c $PARMevs/metplus_config/machine.conf $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/${STEP}/RegridDataPlane_obsMRMS_${RADAR_FIELD}.conf
      export err=$?; err_chk

   else

      export subject="${MRMS_PRODUCT} missing for ${VDATE}${cyc}"
      export maillist=${maillist:-'logan.dawson@noaa.gov'}
      echo "Warning: The ${MRMS_PRODUCT} observation file for ${VDATE}${cyc} is missing. METplus will not run.">>mailmsg
      cat mailmsg | mail -s "$subject" $maillist

   fi	

done


if [ $SENDCOM = YES ]; then
   mkdir -p $COMOUTmrms/${DOMAIN}
   for FILE in $DATA/MRMS_${DOMAIN}/*; do
      cp -v $FILE $COMOUTmrms/${DOMAIN}
   done
fi



############################################################
# Extra step used in dev testing 
############################################################

if [ $DOGRAPHX = YES ]; then
   export CARTOPY_PROD=/apps/ops/prod/data/cartopy
   python ${USHevs}/cam/mrms_plot.py ${VDATE}${cyc}
   export err=$?; err_chk
fi


exit









