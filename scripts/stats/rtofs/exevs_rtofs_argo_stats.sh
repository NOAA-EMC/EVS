#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_argo_stats.sh
# Purpose of Script: To create stat files for RTOFS ocean temperature and
#    salinity forecasts verified with Argo data using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

export VARS="temp psal"
export RUNupper=$(echo $RUN | tr '[a-z]' '[A-Z]')

export STATSDIR=$DATA/stats
mkdir -p $STATSDIR

# get the months for the climo files:
#     for day < 15, use the month before + valid month
#     for day >= 15, use valid month + the month after
MM=$(echo $VDATE |cut -c5-6)
DD=$(echo $VDATE |cut -c7-8)
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

  if [ -s $COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/argo.$VDATE.nc ] ; then
    if [ -s $COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc ] ; then
      for fday in 0 1 2 3 4 5 6 7 8; do
        fhr=$(($fday * 24))
        fhr2=$(printf "%02d" "${fhr}")
        export fhr3=$(printf "%03d" "${fhr}")
        INITDATE=$($NDATE -${fhr} ${VDATE}${vhr} | cut -c 1-8)
        if [ -s $COMIN/prep/$COMPONENT/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f${fhr3}_daily_3ztio.$RUN.nc ] ; then
          for vari in ${VARS}; do
            export VAR=$vari
            mkdir -p $STATSDIR/$RUN.$VDATE/$VAR
            if [ -s $COMOUTsmall/$VAR/point_stat_RTOFS_${RUNupper}_${VAR}_Z${levl}_${fhr2}0000L_${VDATE}_000000V.stat ]; then
              cp -v $COMOUTsmall/$VAR/point_stat_RTOFS_${RUNupper}_${VAR}_Z${levl}_${fhr2}0000L_${VDATE}_000000V.stat $STATSDIR/$RUN.$VDATE/$VAR/.
            else
              run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
              -c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/PointStat_fcstRTOFS_obs${RUNupper}_climoWOA23_$VAR.conf
              export err=$?; err_chk
              if [ $SENDCOM = "YES" ]; then
                  mkdir -p $COMOUTsmall/$VAR
		  if [ -s $STATSDIR/$RUN.$VDATE/$VAR/point_stat_RTOFS_${RUNupper}_${VAR}_Z${levl}_${fhr2}0000L_${VDATE}_000000V.stat ] ; then
                  	cp -v $STATSDIR/$RUN.$VDATE/$VAR/point_stat_RTOFS_${RUNupper}_${VAR}_Z${levl}_${fhr2}0000L_${VDATE}_000000V.stat $COMOUTsmall/$VAR/.
		  fi
              fi
            fi
          done
        else
          echo "WARNING: Missing RTOFS f${fhr3} 3dz file for $VDATE: $COMIN/prep/$COMPONENT/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f${fhr3}_daily_3ztio.$RUN.nc"
        fi
      done
    else
      echo "WARNING: Missing RTOFS f000 ice file for $VDATE: $COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc"
    fi
  else
    echo "WARNING: Missing ARGO data file for $VDATE: $COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/argo.$VDATE.nc"
  fi
done

export STATSOUT=$STATSDIR/$RUN.$VDATE/$VAR

# check if stat files exist
for vari in ${VARS}; do
  export VAR=$vari
  export STATSOUT=$STATSDIR/$RUN.$VDATE/$VAR
  VAR_file_count=$(ls -l $STATSDIR/$RUN.$VDATE/$VAR/*.stat |wc -l)
  if [[ $VAR_file_count -ne 0 ]]; then
    # sum small stat files into one big file using Stat_Analysis
    run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
    -c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/StatAnalysis_fcstRTOFS.conf
    export err=$?; err_chk
    if [ $SENDCOM = "YES" ]; then
      if [ -s $STATSOUT/evs.stats.${COMPONENT}.${RUN}.${VERIF_CASE}_${VAR}.v${VDATE}.stat ] ; then
	    cp -v $STATSOUT/evs.stats.${COMPONENT}.${RUN}.${VERIF_CASE}_${VAR}.v${VDATE}.stat $COMOUTfinal/.
      fi
    fi
  else
     echo "WARNING: Missing RTOFS_${RUNupper}_$VAR stat files for $VDATE in $STATSDIR/$RUN.$VDATE/$VAR/*.stat" 
  fi
done

# Cat the METplus log files
log_dir=$DATA/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
    for log_file in $log_dir/*; do
        echo "Start: $log_file"
        cat $log_file
        echo "End: $log_file"
    done
fi
