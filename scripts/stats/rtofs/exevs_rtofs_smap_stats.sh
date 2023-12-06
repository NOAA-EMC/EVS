#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_smap_stats.sh
# Purpose of Script: To create stat files for RTOFS SSS forecasts verified
#    with SMAP data using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

export VARS="sss"
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

# check if obs file exists; send alert email if not
export JDATE=$(date2jday.sh $VDATE)
min_size=2404
if [ -s $DCOMROOT/$VDATE/validation_data/marine/smap/SP_D${JDATE}_Map_SATSSS_data_1day.nc ]; then
	actual_size=$(wc -c <"$DCOMROOT/$VDATE/validation_data/marine/smap/SP_D${JDATE}_Map_SATSSS_data_1day.nc")
	if [ $actual_size -ge $min_size ]; then
   		if [ -s $COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc ] ; then
      			for fday in 0 1 2 3 4 5 6 7 8; do
        			fhr=$(($fday * 24))
        			fhr2=$(printf "%02d" "${fhr}")
        			export fhr3=$(printf "%03d" "${fhr}")
        			INITDATE=$($NDATE -${fhr} ${VDATE}${vhr} | cut -c 1-8)
        			if [ -s $COMIN/prep/$COMPONENT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f${fhr3}_prog.$RUN.nc ] ; then
          				for vari in ${VARS}; do
            					export VAR=$vari
            					export VARupper=$(echo $VAR | tr '[a-z]' '[A-Z]')
            					mkdir -p $STATSDIR/$RUN.$VDATE/$VAR
            					if [ -s $COMOUTsmall/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat ]; then
              						cpreq -v $COMOUTsmall/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat $STATSDIR/$RUN.$VDATE/$VAR/.
            					else
              						run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
              						-c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/GridStat_fcstRTOFS_obsSMAP_climoWOA23.conf
              						export err=$?; err_chk
              						if [ $SENDCOM = "YES" ]; then
                  						mkdir -p $COMOUTsmall/$VAR
                  						cpreq -v $STATSDIR/$RUN.$VDATE/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat $COMOUTsmall/$VAR/.
              						fi
            					fi
          				done
        			else
          				echo "WARNING: Missing RTOFS f${fhr3} prog file for $VDATE: $COMIN/prep/$COMPONENT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f${fhr3}_prog.$RUN.nc"
        			fi
      			done
   		else
     			echo "WARNING: Missing RTOFS f000 ice file for $VDATE: $COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc"
   		fi
	else
		echo "WARNING:  Missing SMAP data file for $VDATE: $DCOMROOT/$VDATE/validation_data/marine/smap/SP_D${JDATE}_Map_SATSSS_data_1day.nc"
		if [ $SENDMAIL = YES ] ; then
			export subject="SMAP Data Missing for EVS RTOFS"
			echo "Warning: No SMAP data was available for valid date $VDATE." > mailmsg
			echo "Missing file is $DCOMROOT/$VDATE/validation_data/marine/smap/SP_D${JDATE}_Map_SATSSS_data_1day.nc." >> mailmsg
			cat mailmsg | mail -s "$subject" $MAILTO
		fi

	fi
else
   echo "WARNING:  Missing SMAP data file for $VDATE: $DCOMROOT/$VDATE/validation_data/marine/smap/SP_D${JDATE}_Map_SATSSS_data_1day.nc"
   if [ $SENDMAIL = YES ] ; then
       export subject="SMAP Data Missing for EVS RTOFS"
       echo "Warning: No SMAP data was available for valid date $VDATE." > mailmsg
       echo "Missing file is $DCOMROOT/$VDATE/validation_data/marine/smap/SP_D${JDATE}_Map_SATSSS_data_1day.nc." >> mailmsg
       cat mailmsg | mail -s "$subject" $MAILTO
   fi
fi

# check if stat files exist


for vari in ${VARS}; do
  export VAR=$vari
  export VARupper=$(echo $VAR | tr '[a-z]' '[A-Z]')
  export STATSOUT=$STATSDIR/$RUN.$VDATE/$VAR
  mkdir -p $STATSOUT
  VAR_file_count=$(find $STATSOUT -type f -name "*.stat" |wc -l)
  if [[ $VAR_file_count -ne 0 ]]; then
    # sum small stat files into one big file using Stat_Analysis
    run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
    -c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/StatAnalysis_fcstRTOFS.conf
    export err=$?; err_chk
    if [ $SENDCOM = "YES" ]; then
      cpreq -v $STATSOUT/evs.stats.${COMPONENT}.${RUN}.${VERIF_CASE}_${VAR}.v${VDATE}.stat $COMOUTfinal/.
    fi
  else
     echo "WARNING: Missing RTOFS_${RUNupper}_$VARupper stat files for $VDATE in $STATSDIR/$RUN.$VDATE/$VAR/*.stat" 
  fi
done

# Cat the METplus log files
mkdir -p $DATA/logs
log_dir=$DATA/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
    for log_file in $log_dir/*; do
        echo "Start: $log_file"
        cat $log_file
        echo "End: $log_file"
    done
fi
