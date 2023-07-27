#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_aviso_stats.sh
# Purpose of Script: To create stat files for RTOFS SSH forecasts verified
#    with AVISO data using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# check if obs file exists; exit if not
if [ ! -s $COMINobs/$VDATE/validation_data/marine/cmems/ssh/nrt_global_allsat_phy_l4_${VDATE}_${VDATE}.nc ] ; then
   export subject="AVISO Data Missing for EVS RTOFS"
   echo "Warning: No AVISO data was available for valid date $VDATE." > mailmsg
   echo "Missing file is $COMINobs/$VDATE/validation_data/marine/cmems/ssh/nrt_global_allsat_phy_l4_${VDATE}_${VDATE}.nc." >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist
   exit 0
fi

# check if fcst files exist; exit if not
#   f000 forecast for VDATE
if [ ! -s $COMINfcst/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc ] ; then
   echo "Missing RTOFS f000 ice file for $VDATE" 
   exit 0
fi

if [ ! -s $COMINfcst/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_diag.$RUN.nc ] ; then
   echo "Missing RTOFS f000 diag file for $VDATE" 
   exit 0
fi

#   f024 forecast for VDATE was issued 1 day earlier
INITDATE=$(date --date="$VDATE -1 day" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f024_diag.$RUN.nc ] ; then
   echo "Missing RTOFS f024 diag file for $VDATE" 
   exit 0
fi

#   f048 forecast for VDATE was issued 2 days earlier
INITDATE=$(date --date="$VDATE -2 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f048_diag.$RUN.nc ] ; then
   echo "Missing RTOFS f048 diag file for $VDATE" 
   exit 0
fi

#   f072 forecast for VDATE was issued 3 days earlier
INITDATE=$(date --date="$VDATE -3 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f072_diag.$RUN.nc ] ; then
   echo "Missing RTOFS f072 diag file for $VDATE" 
   exit 0
fi

#   f096 forecast for VDATE was issued 4 days earlier
INITDATE=$(date --date="$VDATE -4 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f096_diag.$RUN.nc ] ; then
   echo "Missing RTOFS f096 diag file for $VDATE" 
   exit 0
fi

#   f120 forecast for VDATE was issued 5 days earlier
INITDATE=$(date --date="$VDATE -5 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f120_diag.$RUN.nc ] ; then
   echo "Missing RTOFS f120 diag file for $VDATE" 
   exit 0
fi

#   f144 forecast for VDATE was issued 6 days earlier
INITDATE=$(date --date="$VDATE -6 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f144_diag.$RUN.nc ] ; then
   echo "Missing RTOFS f144 diag file for $VDATE" 
   exit 0
fi

#   f168 forecast for VDATE was issued 7 days earlier
INITDATE=$(date --date="$VDATE -7 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f168_diag.$RUN.nc ] ; then
   echo "Missing RTOFS f168 diag file for $VDATE" 
   exit 0
fi

#   f192 forecast for VDATE was issued 8 days earlier
INITDATE=$(date --date="$VDATE -8 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f192_diag.$RUN.nc ] ; then
   echo "Missing RTOFS f192 diag file for $VDATE" 
   exit 0
fi

# get the months for the climo files:
#     for day < 15, use the month before + valid month
#     for day >= 15, use valid month + the month after

export STATSDIR=$DATA/stats
mkdir -p $STATSDIR

MM=$(date --date=$VDATE +%m)
DD=$(date --date=$VDATE +%d)
if [ $DD -lt 15 ] ; then
   NM=`expr $MM - 1`
   if [ $NM -eq 0 ] ; then
      NM=12
   fi
   NM=$(printf "%02d" $NM)
   export SM=$NM
   export EM=$MM
else
   NM=`expr $MM + 1`
   if [ $NM -eq 13 ] ; then
      NM=01
   fi
   NM=$(printf "%02d" $NM)
   export SM=$MM
   export EM=$NM
fi

# run Grid_Stat
run_metplus.py -c $CONFIGevs/metplus_rtofs.conf \
-c $CONFIGevs/${VERIF_CASE}/$STEP/GridStat_fcstRTOFS_obsAVISO_climoHYCOM.conf

cp $STATSDIR/$RUN.$VDATE/*stat $COMOUTsmall
export STATSOUT=$STATSDIR/$RUN.$VDATE

# check if stat files exist; exit if not
if [ ! -s $COMOUTsmall/grid_stat_RTOFS_AVISO_SSH_1920000L_${VDATE}_000000V.stat ] ; then
   echo "Missing RTOFS_AVISO_SSH stat files for $VDATE" 
   exit 0
fi

# sum small stat files into one big file using Stat_Analysis

run_metplus.py -c $CONFIGevs/metplus_rtofs.conf \
-c $CONFIGevs/${VERIF_CASE}/$STEP/StatAnalysis_fcstRTOFS.conf

cp $STATSOUT/evs*stat $COMOUTfinal

exit

################################ END OF SCRIPT ################################
