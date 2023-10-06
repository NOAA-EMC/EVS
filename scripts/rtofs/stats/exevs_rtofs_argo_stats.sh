#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_argo_stats.sh
# Purpose of Script: To create stat files for RTOFS ocean temperature and
#    salinity forecasts verified with Argo data using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# check if argo nc file exists; exit if not
if [ ! -s $COMINfcst/rtofs.$VDATE/$RUN/argo.$VDATE.nc ] ; then
   echo "Missing Argo data file for $VDATE"
   exit 0
fi

# check if fcst files exist; exit if not
#   f000 forecast for VDATE
if [ ! -s $COMINfcst/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc ] ; then
   echo "Missing RTOFS f000 ice file for $VDATE" 
   exit 0
fi

if [ ! -s $COMINfcst/rtofs.$VDATE/$RUN/rtofs_glo_3dz_f000_daily_3ztio.$RUN.nc ] ; then
   echo "Missing RTOFS f000 3dz file for $VDATE" 
   exit 0
fi

#   f024 forecast for VDATE was issued 1 day earlier
INITDATE=$(date --date="$VDATE -1 day" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f024_daily_3ztio.$RUN.nc ] ; then
   echo "Missing RTOFS f024 3dz file for $VDATE" 
   exit 0
fi

#   f048 forecast for VDATE was issued 2 days earlier
INITDATE=$(date --date="$VDATE -2 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f048_daily_3ztio.$RUN.nc ] ; then
   echo "Missing RTOFS f048 3dz file for $VDATE" 
   exit 0
fi

#   f072 forecast for VDATE was issued 3 days earlier
INITDATE=$(date --date="$VDATE -3 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f072_daily_3ztio.$RUN.nc ] ; then
   echo "Missing RTOFS f072 3dz file for $VDATE" 
   exit 0
fi

#   f096 forecast for VDATE was issued 4 days earlier
INITDATE=$(date --date="$VDATE -4 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f096_daily_3ztio.$RUN.nc ] ; then
   echo "Missing RTOFS f096 3dz file for $VDATE" 
   exit 0
fi

#   f120 forecast for VDATE was issued 5 days earlier
INITDATE=$(date --date="$VDATE -5 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f120_daily_3ztio.$RUN.nc ] ; then
   echo "Missing RTOFS f120 3dz file for $VDATE" 
   exit 0
fi

#   f144 forecast for VDATE was issued 6 days earlier
INITDATE=$(date --date="$VDATE -6 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f144_daily_3ztio.$RUN.nc ] ; then
   echo "Missing RTOFS f144 3dz file for $VDATE" 
   exit 0
fi

#   f168 forecast for VDATE was issued 7 days earlier
INITDATE=$(date --date="$VDATE -7 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f168_daily_3ztio.$RUN.nc ] ; then
   echo "Missing RTOFS f168 3dz file for $VDATE" 
   exit 0
fi

#   f192 forecast for VDATE was issued 8 days earlier
INITDATE=$(date --date="$VDATE -8 days" +%Y%m%d)
if [ ! -s $COMINfcst/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f192_daily_3ztio.$RUN.nc ] ; then
   echo "Missing RTOFS f192 3dz file for $VDATE" 
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

# run Point_Stat
for levl in 0 50 125 200 400 700 1000 1400; do
  export LVL=$levl

  if [ $levl -eq 0 ] ; then
    export ZRANGE=0-4
  fi

  if [ $levl -eq 50 ] ; then
    export ZRANGE=48-52
  fi

  if [ $levl -eq 125 ] ; then
    export ZRANGE=123-127
  fi

  if [ $levl -eq 200 ] ; then
    export ZRANGE=198-202
  fi

  if [ $levl -eq 400 ] ; then
    export ZRANGE=398-402
  fi

  if [ $levl -eq 700 ] ; then
    export ZRANGE=698-702
  fi

  if [ $levl -eq 1000 ] ; then
    export ZRANGE=997-1003
  fi

  if [ $levl -eq 1400 ] ; then
    export ZRANGE=1397-1403
  fi

  run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
  -c $CONFIGevs/${VERIF_CASE}/$STEP/PointStat_fcstRTOFS_obsARGO_climoWOA23_$VAR.conf
done

if [ $SENDCOM = "YES" ]; then
 cp $STATSDIR/$RUN.$VDATE/$VAR/*stat $COMOUTsmall
fi
export STATSOUT=$STATSDIR/$RUN.$VDATE/$VAR

# check if stat files exist; exit if not
if [ ! -s $COMOUTsmall/point_stat_RTOFS_ARGO_${VAR}_Z1400_1920000L_${VDATE}_000000V.stat ] ; then
   echo "Missing RTOFS_ARGO_$VAR stat files for $VDATE" 
   exit 0
fi

# sum small stat files into one big file using Stat_Analysis
mkdir -p $COMOUTfinal

run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
-c $CONFIGevs/${VERIF_CASE}/$STEP/StatAnalysis_fcstRTOFS.conf

if [ $SENDCOM = "YES" ]; then
 cp $STATSOUT/evs*stat $COMOUTfinal
fi

# archive final stat file
#rsync -av $COMOUTfinal $ARCHevs

exit

################################ END OF SCRIPT ################################
