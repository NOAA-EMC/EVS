#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_smap_stats.sh
# Purpose of Script: To create stat files for RTOFS SSS forecasts verified
#    with SMAP data using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# check if obs file exists; exit if not
export JDATE=$(date --date="$VDATE" +%Y%j)

if [ ! -s $COMINobs/$VDATE/validation_data/marine/smap/SP_D${JDATE}_Map_SATSSS_data_1day.nc ] ; then
   if [ $SENDMAIL = YES ] ; then
       export subject="SMAP Data Missing for EVS RTOFS"
       echo "Warning: No SMAP data was available for valid date $VDATE." > mailmsg
       echo "Missing file is $COMINobs/$VDATE/validation_data/marine/smap/SP_D${JDATE}_Map_SATSSS_data_1day.nc." >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
   fi
fi

# check if fcst files exist; exit if not
#   f000 forecast for VDATE
if [ ! -s $COMINfcst/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc ] ; then
   echo "Missing RTOFS f000 ice file for $VDATE" 
   exit
fi

if [ ! -s $COMINfcst/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_prog.$RUN.nc ] ; then
   echo "Missing RTOFS f000 prog file for $VDATE" 
   exit
fi

#   f024 forecast for VDATE was issued 1 day earlier
INITDATE=$(date --date="$VDATE -1 day" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f024_prog.$RUN.nc ] ; then
   echo "Missing RTOFS f024 prog file for $VDATE" 
   exit
fi

#   f048 forecast for VDATE was issued 2 days earlier
INITDATE=$(date --date="$VDATE -2 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f048_prog.$RUN.nc ] ; then
   echo "Missing RTOFS f048 prog file for $VDATE" 
   exit
fi

#   f072 forecast for VDATE was issued 3 days earlier
INITDATE=$(date --date="$VDATE -3 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f072_prog.$RUN.nc ] ; then
   echo "Missing RTOFS f072 prog file for $VDATE" 
   exit
fi

#   f096 forecast for VDATE was issued 4 days earlier
INITDATE=$(date --date="$VDATE -4 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f096_prog.$RUN.nc ] ; then
   echo "Missing RTOFS f096 prog file for $VDATE" 
   exit
fi

#   f120 forecast for VDATE was issued 5 days earlier
INITDATE=$(date --date="$VDATE -5 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f120_prog.$RUN.nc ] ; then
   echo "Missing RTOFS f120 prog file for $VDATE" 
   exit
fi

#   f144 forecast for VDATE was issued 6 days earlier
INITDATE=$(date --date="$VDATE -6 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f144_prog.$RUN.nc ] ; then
   echo "Missing RTOFS f144 prog file for $VDATE" 
   exit
fi

#   f168 forecast for VDATE was issued 7 days earlier
INITDATE=$(date --date="$VDATE -7 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f168_prog.$RUN.nc ] ; then
   echo "Missing RTOFS f168 prog file for $VDATE" 
   exit
fi

#   f192 forecast for VDATE was issued 8 days earlier
INITDATE=$(date --date="$VDATE -8 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f192_prog.$RUN.nc ] ; then
   echo "Missing RTOFS f192 prog file for $VDATE" 
   exit
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
run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
-c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/GridStat_fcstRTOFS_obsSMAP_climoWOA23.conf

if [ $SENDCOM = "YES" ]; then
 cp $STATSDIR/$RUN.$VDATE/*stat $COMOUTsmall
fi
export STATSOUT=$STATSDIR/$RUN.$VDATE

# check if stat files exist; exit if not
if [ ! -s $COMOUTsmall/grid_stat_RTOFS_SMAP_SSS_1920000L_${VDATE}_000000V.stat ] ; then
   echo "Missing RTOFS_SMAP_SSS stat files for $VDATE" 
   exit
fi

# sum small stat files into one big file using Stat_Analysis

run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
-c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/StatAnalysis_fcstRTOFS.conf

if [ $SENDCOM = "YES" ]; then
 cp $STATSOUT/evs*stat $COMOUTfinal
fi

exit

################################ END OF SCRIPT ################################
