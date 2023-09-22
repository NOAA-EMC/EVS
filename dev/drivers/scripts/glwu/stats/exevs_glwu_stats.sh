#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_stats.sh
# Purpose of Script: To create stat files for GLWU forecasts verified with
#    NDBC buoy data using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# check if ndbc nc file exists; exit if not
if [ ! -s $COMINobs/glwu.$VDATE/$RUN/ndbc.${VDATE}.nc ] ; then
   export subject="NDBC Data Missing for EVS GLWU"
   export maillist=${maillist:-'geoffrey.manikin@noaa.gov,lichuan.chen@noaa.gov'}
   echo "Warning: No NDBC data was available for valid date $VDATE." > mailmsg
#   cat mailmsg | mail -s "$subject" $maillist
   exit 0
fi

# check if fcst files exist; exit if not
#   f000 forecast for VDATE
if [ ! -s $COMINfcst/glwu.$VDATE/glwu.grlc_2p5km.t01z.grib2 ] ; then
   echo "Missing GLWU fcst file for $VDATE" 
   exit
fi

#   f024 forecast for VDATE was issued 1 day earlier
INITDATE=$(date --date="$VDATE -1 day" +%Y%m%d)
if [ ! -s $COMINfcst/glwu.$INITDATE/glwu.grlc_2p5km.t01z.grib2 ] ; then
   echo "Missing GLWU fcst file for $INITDATE" 
   exit
fi

#   f048 forecast for VDATE was issued 2 days earlier
INITDATE=$(date --date="$VDATE -2 days" +%Y%m%d)
if [ ! -s $COMINfcst/glwu.$INITDATE/glwu.grlc_2p5km.t01z.grib2 ] ; then
   echo "Missing GLWU fcst file for $INITDATE" 
   exit 
fi

#   f072 forecast for VDATE was issued 3 days earlier
INITDATE=$(date --date="$VDATE -3 days" +%Y%m%d)
if [ ! -s $COMINfcst/glwu.$INITDATE/glwu.grlc_2p5km.t01z.grib2 ] ; then
   echo "Missing GLWU fcst file for INITDATE" 
   exit 
fi

#   f096 forecast for VDATE was issued 4 days earlier
INITDATE=$(date --date="$VDATE -4 days" +%Y%m%d)
if [ ! -s $COMINfcst/glwu.$INITDATE/glwu.grlc_2p5km.t01z.grib2 ] ; then
   echo "Missing GLWU fcst file for $INITDATE" 
   exit 
fi

#   f120 forecast for VDATE was issued 5 days earlier
INITDATE=$(date --date="$VDATE -5 days" +%Y%m%d)
if [ ! -s $COMINfcst/glwu.$INITDATE/glwu.grlc_2p5km.t01z.grib2 ] ; then
   echo "Missing GLWU fcst file for $INITDATE" 
   exit 
fi

#   f144 forecast for VDATE was issued 6 days earlier
INITDATE=$(date --date="$VDATE -6 days" +%Y%m%d)
if [ ! -s $COMINfcst/glwu.$INITDATE/glwu.grlc_2p5km.t01z.grib2 ] ; then
   echo "Missing GLWU fcst file for $INITDATE" 
   exit 
fi

# run Point_Stat
run_metplus.py -c $CONFIGevs/metplus_glwu.conf \
-c $CONFIGevs/${VERIF_CASE}/$STEP/PointStat_fcstGLWU_obsNDBC_htsgw.conf

# check if stat files exist; exit if not
if [ ! -s $COMOUTsmall/point_stat_GLWU_NDBC_HTSGW_1440000L_${VDATE}_000000V.stat ] ; then
   echo "Missing GLWU_NDBC_HTSGW stat files for $VDATE" 
   exit
fi

# sum small stat files into one big file using Stat_Analysis
mkdir -p $COMOUTfinal

run_metplus.py -c $CONFIGevs/metplus_glwu.conf \
-c $CONFIGevs/${VERIF_CASE}/$STEP/StatAnalysis_fcstGLWU_obsNDBC.conf

# archive final stat file
rsync -av $COMOUTfinal $ARCHevs

exit

################################ END OF SCRIPT ################################
