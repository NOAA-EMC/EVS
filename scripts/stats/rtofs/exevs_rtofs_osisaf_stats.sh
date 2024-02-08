#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_osisaf_stats.sh
# Purpose of Script: To create stat files for RTOFS sea ice concentration
#    forecasts verified with OSI-SAF data using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

export VARS="sic"
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

for hem in nh sh; do
  if [ -s $COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/ice_conc_${hem}_polstere-100_multi_${VDATE}1200.nc ] ; then
      for fday in 0 1 2 3 4 5 6 7 8; do
        fhr=$(($fday * 24))
        fhr2=$(printf "%02d" "${fhr}")
        export fhr3=$(printf "%03d" "${fhr}")
        INITDATE=$($NDATE -${fhr} ${VDATE}${vhr} | cut -c 1-8)
        if [ -s $COMIN/prep/$COMPONENT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f${fhr3}_ice.$RUN.nc ] ; then
          for vari in ${VARS}; do
            export VAR=$vari
            export VARupper=$(echo $VAR | tr '[a-z]' '[A-Z]')
            mkdir -p $STATSDIR/$RUN.$VDATE/$VAR
            if [ -s $COMOUTsmall/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${hem}_${fhr2}0000L_${VDATE}_000000V.stat ]; then
              cp -v $COMOUTsmall/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${hem}_${fhr2}0000L_${VDATE}_000000V.stat $STATSDIR/$RUN.$VDATE/$VAR/.
            else
              run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
              -c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/GridStat_fcstRTOFS_obsOSISAF_${hem}.conf
              export err=$?; err_chk
              if [ $SENDCOM = "YES" ]; then
                  mkdir -p $COMOUTsmall/$VAR
		  if [ -s $STATSDIR/$RUN.$VDATE/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${hem}_${fhr2}0000L_${VDATE}_000000V.stat ] ; then
                  	cp -v $STATSDIR/$RUN.$VDATE/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${hem}_${fhr2}0000L_${VDATE}_000000V.stat $COMOUTsmall/$VAR/.
		  fi
              fi
            fi
          done
        else
          echo "WARNING: Missing RTOFS f${fhr3} ice file for $VDATE: $COMIN/prep/$COMPONENT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f${fhr3}_ice.$RUN.nc"
        fi
      done
  else
   echo "WARNING: Missing OSI-SAF ${hem} data file for $VDATE: $COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/ice_conc_${hem}_polstere-100_multi_${VDATE}1200.nc"
  fi
done

# check if stat files exist
for vari in ${VARS}; do
  export VAR=$vari
  export VARupper=$(echo $VAR | tr '[a-z]' '[A-Z]')
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
     echo "WARNING: Missing RTOFS_${RUNupper}_$VARupper stat files for $VDATE in $STATSDIR/$RUN.$VDATE/$VAR/*.stat" 
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
