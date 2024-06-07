#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_grid2obs_stats.sh
# Purpose of Script: To create stat files for RTOFS ocean temperature and
#    salinity forecasts verified with Argo and NDBC data using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
# Modified for EVSv2:
# By: Samira Ardani (samira.ardani@noaa.gov)
# 05/2024: Combined the stats scripts into two scripts "grid2obs" and "grid2grid"
#          and modified the paths to small/large stats files
###############################################################################

set -x
export STATSDIR=$DATA/stats
mkdir -p $STATSDIR

########################################
# PointStat for Argo:
########################################

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

if [ $RUN = argo ]; then
	export VARS="temp psal"
	export RUNupper=$(echo $RUN | tr '[a-z]' '[A-Z]')
	EVSINfilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/argo.$VDATE.nc
	COMINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc
	
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
  
  		if [ -s $EVSINfilename ] ; then
    			if [ -s $COMINicefilename ] ; then
      				for fday in 0 1 2 3 4 5 6 7 8; do
        				fhr=$(($fday * 24))
        				fhr2=$(printf "%02d" "${fhr}")
        				export fhr3=$(printf "%03d" "${fhr}")
					match_date=$(date --date="${VDATE} ${fhr} hours ago" +"%Y%m%d")
					COMINrtofsfilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_3dz_f${fhr3}_daily_3ztio.$RUN.nc
					if [ -s $COMINrtofsfilename ] ; then
          					for vari in ${VARS}; do
            						export VAR=$vari
            						mkdir -p $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR
            						if [ -s $COMOUTsmall/$VAR/point_stat_RTOFS_${RUNupper}_${VAR}_Z${levl}_${fhr2}0000L_${VDATE}_000000V.stat ]; then
              							cp -v $COMOUTsmall/$VAR/point_stat_RTOFS_${RUNupper}_${VAR}_Z${levl}_${fhr2}0000L_${VDATE}_000000V.stat $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR/.
           						else
              							run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
              							-c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/PointStat_fcstRTOFS_obs${RUNupper}_climoWOA23_$VAR.conf
              							export err=$?; err_chk
              							if [ $SENDCOM = "YES" ]; then
                  							mkdir -p $COMOUTsmall/$VAR
		  							if [ -s $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR/point_stat_RTOFS_${RUNupper}_${VAR}_Z${levl}_${fhr2}0000L_${VDATE}_000000V.stat ] ; then
                  								cp -v $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR/point_stat_RTOFS_${RUNupper}_${VAR}_Z${levl}_${fhr2}0000L_${VDATE}_000000V.stat $COMOUTsmall/$VAR/.
									fi
								fi
							fi
						done
					else
						echo "WARNING: Missing RTOFS f${fhr3} 3dz file for $VDATE: ${COMINrtofsfilename}"
					fi
				done
			else
				echo "WARNING: Missing RTOFS f000 ice file for $VDATE: ${COMINicefilename}"
			fi
		else
			echo "WARNING: Missing ARGO data file for $VDATE: $EVSINfilename"
		fi
	done

elif [ $RUN = ndbc ]; then
	export VARS="sst"
	export RUNupper="NDBC_STANDARD"
	EVSINfilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/ndbc.${VDATE}.nc
	COMINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc
	if [ -s $EVSINfilename ] ; then
		if [ -s $COMINicefilename ] ; then
			for fday in 0 1 2 3 4 5 6 7 8; do
				fhr=$(($fday * 24))
				fhr2=$(printf "%02d" "${fhr}")
				export fhr3=$(printf "%03d" "${fhr}")
				match_date=$(date --date="${VDATE} ${fhr} hours ago" +"%Y%m%d")
				COMINrtofsfilename=$COMIN/prep/$COMPONENT/rtofs.${match_date}/$RUN/rtofs_glo_2ds_f${fhr3}_prog.$RUN.nc
				if [ -s $COMINrtofsfilename ] ; then
					for vari in ${VARS}; do
						export VAR=$vari
						export VARupper=$(echo $VAR | tr '[a-z]' '[A-Z]')
						mkdir -p $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR
						if [ -s $COMOUTsmall/$VAR/point_stat_RTOFS_NDBC_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat ]; then
							cp -v $COMOUTsmall/$VAR/point_stat_RTOFS_NDBC_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat $STATSDIR/${RUNmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR/.
						else
							run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
							-c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/PointStat_fcstRTOFS_obsNDBC_climoWOA23.conf
							export err=$?; err_chk
							if [ $SENDCOM = "YES" ]; then
								mkdir -p $COMOUTsmall/$VAR
								if [ -s $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR/point_stat_RTOFS_NDBC_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat ] ; then
									cp -v $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR/point_stat_RTOFS_NDBC_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat $COMOUTsmall/$VAR/.
								fi
							fi
						fi
					done
				else
					echo "WARNING: Missing RTOFS f${fhr3} prog file for $VDATE: $COMINrtofsfilename"
				fi
			done
		else
			echo "WARNING: Missing RTOFS f000 ice file for $VDATE: $COMINicefilename"
		fi
	else
		echo "WARNING: Missing NDBC data file for $VDATE: $EVSINfilename"
	fi
fi

######################################
# check if stat files exist
######################################
if [ $RUN = argo ]; then
	for vari in ${VARS}; do
  		export VAR=$vari
  		export STATSOUT=$STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR
  		VAR_file_count=$(ls -l $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR/*.stat |wc -l)
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
     			echo "WARNING: Missing RTOFS_${RUNupper}_$VAR stat files for $VDATE in $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR/*.stat" 
  		fi
	done
elif [ $RUN = ndbc ]; then
	
	for vari in ${VARS}; do
  		export VAR=$vari
  		export STATSOUT=$STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR
  		VAR_file_count=$(ls -l $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR/*.stat |wc -l)
  		if [[ $VAR_file_count -ne 0 ]]; then
    		# sum small stat files into one big file using Stat_Analysis
    			run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
    			-c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/StatAnalysis_fcstRTOFS_obsNDBC.conf
    			export err=$?; err_chk
    			if [ $SENDCOM = "YES" ]; then
      				if [ -s $STATSOUT/evs.stats.${COMPONENT}.ndbc_standard.${VERIF_CASE}_${VAR}.v${VDATE}.stat ] ; then
	    				cp -v $STATSOUT/evs.stats.${COMPONENT}.ndbc_standard.${VERIF_CASE}_${VAR}.v${VDATE}.stat $COMOUTfinal/.
      				fi
    			fi
  		else
     			echo "WARNING: Missing RTOFS_${RUNupper}_$VAR stat files for $VDATE in $STATSDIR/${RUNsmall}.$VDATE/$RUN/${VERIF_CASE}/$VAR/*.stat" 
  		fi
	done
fi

############################
