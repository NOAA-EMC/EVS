#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_smos_stats.sh
# Purpose of Script: To create stat files for RTOFS SSS forecasts verified
#    with SMOS data using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

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

export JDATE=$(date2jday.sh $VDATE)
min_size=2404

#####################################################
# GridStat for smos, smap, ghrsst and aviso
#####################################################

for Rcase in smos smap ghrsst aviso; do
	if [ $Rcase = smap ]; then
		DCOMINrtofsfilename=$DCOMROOT/$VDATE/validation_data/marine/smos/SM_D${JDATE}_Map_SATSSS_data_1day.nc
		COMINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc
		COMINrtofsfilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f${fhr3}_prog.$RUN.nc
		export VARS="sss"
		export RUNupper=$(echo $Rcase | tr '[a-z]' '[A-Z]')
		CLIMO=WOA23

	elif [ $Rcase = smos ]; then
		DCOMINrtofsfilename=$DCOMROOT/$VDATE/validation_data/marine/smap/SP_D${JDATE}_Map_SATSSS_data_1day.nc
		COMINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc
		COMINrtofsfilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f${fhr3}_prog.$RUN.nc
		export VARS="sss"
		export RUNupper=$(echo $Rcase | tr '[a-z]' '[A-Z]')
		CLIMO=WOA23

	elif [ $Rcase = ghrsst ]; then
		DCOMINrtofsfilename=$DCOMROOT/$VDATE/validation_data/marine/ghrsst/${VDATE}_OSPO_L4_GHRSST.nc
		COMINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc
		COMINrtofsfilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f${fhr3}_prog.$RUN.nc
		export VARS="sst"
		export RUNupper=$(echo $Rcase | tr '[a-z]' '[A-Z]')
		CLIMO=WOA23

	elif [ $Rcase = aviso ]; then
		DCOMINrtofsfilename=$DCOMROOT/$VDATE/validation_data/marine/aviso/nrt_global_allsat_phy_l4_${VDATE}_${VDATE}.nc
		COMINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc
		COMINrtofsfilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f${fhr3}_diag.$RUN.nc
		export VARS="ssh"
		export RUNupper=$(echo $Rcase | tr '[a-z]' '[A-Z]')
		CLIMO=HYCOM
	fi

	if [ -s $DCOMINrtofsfilename ] ; then
	actual_size=$(wc -c <"$DCOMINrtofsfilename")
		if [ $actual_size -ge $min_size ]; then
     			if [ -s $COMINicefilename ] ; then
      				for fday in 0 1 2 3 4 5 6 7 8; do
        				fhr=$(($fday * 24))
        				fhr2=$(printf "%02d" "${fhr}")
        				export fhr3=$(printf "%03d" "${fhr}")
					match_date=$(date --date="${VDATE} ${fhr} hours ago" +"%Y%m%d")
					if [ -s $COMINrtofsfilename ] ; then
          					for vari in ${VARS}; do
            						export VAR=$vari
            						export VARupper=$(echo $VAR | tr '[a-z]' '[A-Z]')
            						mkdir -p $STATSDIR/$RUN.$VDATE/$VAR
            						if [ -s $COMOUTsmall/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${fhr2}0000L_${match_date}_000000V.stat ]; then
              							cp -v $COMOUTsmall/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${fhr2}0000L_${match_date}_000000V.stat $STATSDIR/$RUN.$VDATE/$VAR/.
            						else
              							run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
              							-c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/GridStat_fcstRTOFS_obsSMOS_climo$CLIMO.conf
              							export err=$?; err_chk
              							if [ $SENDCOM = "YES" ]; then
                  							mkdir -p $COMOUTsmall/$VAR
									if [ -s $STATSDIR/$RUN.$VDATE/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat ] ; then
                  								cp -v $STATSDIR/$RUN.$VDATE/$VAR/grid_stat_RTOFS_${RUNupper}_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat $COMOUTsmall/$VAR/.
									fi
              							fi
            						fi
          					done
					else
          					echo "WARNING: Missing RTOFS f${fhr3} file for $VDATE: $COMINrtofsfilename"
        				fi
      				done
   			else
     				echo "WARNING: Missing RTOFS f000 ice file for $VDATE: $COMINicefilename"
   			fi
		else
   			echo "WARNING:  Missing SMOS data file for $VDATE: $DCOMINrtofsfilename"
   			if [ $SENDMAIL = YES ] ; then
       				export subject="${RUNupper} Data Missing for EVS RTOFS"
       				echo "Warning: No ${RUNupper} data was available for valid date $VDATE." > mailmsg
       				echo "Missing file is ${DCOMINrtofsfilename}." >> mailmsg
       				cat mailmsg | mail -s "$subject" $MAILTO
   			fi
		fi
	else
		echo "WARNING:  Missing ${RUNupper} data file for $VDATE: $DCOMINrtofsfilename"
		if [ $SENDMAIL = YES ] ; then
			export subject="${RUNupper} Data Missing for EVS RTOFS"
			echo "Warning: No ${RUNupper} data was available for valid date $VDATE." > mailmsg
			echo "Missing file is ${DCOMINrtofsfilename}." >> mailmsg
			cat mailmsg | mail -s "$subject" $MAILTO
		fi
	fi

done

################################
# GridStat for osisaf
################################

for Rcase in osisaf; do
	export VARS="sic"
	export RUNupper=$(echo $Rcase | tr '[a-z]' '[A-Z]')
	for hem in nh sh; do
		EVSINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/ice_conc_${hem}_polstere-100_multi_${VDATE}1200.nc
		if [ -s $EVSINicefilename ] ; then
			for fday in 0 1 2 3 4 5 6 7 8; do
				fhr=$(($fday * 24))
				fhr2=$(printf "%02d" "${fhr}")
			        export fhr3=$(printf "%03d" "${fhr}")
				match_date=$(date --date="${VDATE} ${fhr} hours ago" +"%Y%m%d")
				COMINrtofsfilename=$COMIN/prep/$COMPONENT/rtofs.${match_date}/$RUN/rtofs_glo_2ds_f${fhr3}_ice.$RUN.nc
			        if [ -s $COMINrtofsfilename ] ; then
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
					echo "WARNING: Missing RTOFS f${fhr3} ice file for $VDATE: ${COMINrtofsfilename}"
				fi
			done
		else
			echo "WARNING: Missing OSI-SAF ${hem} data file for $VDATE: $EVSINicefilename"
		fi
	done
done



#########################################################################
# check if stat files exist
#########################################################################
#
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
	    if [ -s $STATSOUT/evs.stats.${COMPONENT}.${RUN}.${VERIF_CASE}_${VAR}.v${VDATE}.stat ]; then
      		cp -v $STATSOUT/evs.stats.${COMPONENT}.${RUN}.${VERIF_CASE}_${VAR}.v${VDATE}.stat $COMOUTfinal/.
	    fi
    fi
  else
     echo "WARNING: Missing RTOFS_${RUNupper}_$VARupper stat files for $VDATE in $STATSDIR/$RUN.$VDATE/$VAR/*.stat" 
  fi
done

############################
# Cat the METplus log files
###########################

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
