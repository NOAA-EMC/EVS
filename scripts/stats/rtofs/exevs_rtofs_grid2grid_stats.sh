#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_grid2grid_stats.sh
# Purpose of Script: To create stat files for RTOFS, grid2grid verification cases.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
# Modified for EVSv2:
# By: Samira Ardani (samira.ardani@noaa.gov)
# 05/2024: Combined the stats scripts into two scripts "grid2obs" and "grid2grid"
# 	   and modified the paths to small/large stats files.
# 09/2024: Variable names changed:
# 1- $RUN=ocean for each step of EVSv2-RTOFS was defined to be consistent with other EVS components. 
# 2- $RUN was defined in all j-jobs. 
# 3- $RUNsmall was renamed to $RUN in stats j-job and all stats scripts; and 
# 4- For all observation types, variable $OBTYPE was used instead of $RUN throughout all scripts.

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

#########################################################################################
# GridStat
########################################################################################

if [ $OBTYPE = osisaf ]; then
	export VARS="sic"
	export OBTYPEupper=$(echo $OBTYPE | tr '[a-z]' '[A-Z]')
	for hem in nh sh; do
		EVSINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$OBTYPE/ice_conc_${hem}_polstere-100_multi_${VDATE}1200.nc
		if [ -s $EVSINicefilename ] ; then
			for fday in 0 1 2 3 4 5 6 7 8; do
				fhr=$(($fday * 24))
				fhr2=$(printf "%02d" "${fhr}")
			        export fhr3=$(printf "%03d" "${fhr}")
				match_date=$(date --date="${VDATE} ${fhr} hours ago" +"%Y%m%d")
				COMINrtofsfilename=$COMIN/prep/$COMPONENT/rtofs.${match_date}/$OBTYPE/rtofs_glo_2ds_f${fhr3}_ice.$OBTYPE.nc
			        if [ -s $COMINrtofsfilename ] ; then
					for vari in ${VARS}; do
						export VAR=$vari
						export VARupper=$(echo $VAR | tr '[a-z]' '[A-Z]')
						mkdir -p $STATSDIR/${RUN}.$VDATE/$OBTYPE/${VERIF_CASE}/$VAR
						if [ -s $COMOUTsmall/$VAR/grid_stat_RTOFS_${OBTYPEupper}_${VARupper}_${hem}_${fhr2}0000L_${VDATE}_000000V.stat ]; then
							cp -v $COMOUTsmall/$VAR/grid_stat_RTOFS_${OBTYPEupper}_${VARupper}_${hem}_${fhr2}0000L_${VDATE}_000000V.stat $STATSDIR/${RUN}.$VDATE/$OBTYPE/${VERIF_CASE}/$VAR/.
						else
							run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
						       -c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/GridStat_fcstRTOFS_obsOSISAF_${hem}.conf
							export err=$?; err_chk           
							if [ $SENDCOM = "YES" ]; then
								mkdir -p $COMOUTsmall/$VAR
								if [ -s $STATSDIR/${RUN}.$VDATE/$OBTYPE/${VERIF_CASE}/$VAR/grid_stat_RTOFS_${OBTYPEupper}_${VARupper}_${hem}_${fhr2}0000L_${VDATE}_000000V.stat ] ; then
						                	cp -v $STATSDIR/${RUN}.$VDATE/$OBTYPE/${VERIF_CASE}/$VAR/grid_stat_RTOFS_${OBTYPEupper}_${VARupper}_${hem}_${fhr2}0000L_${VDATE}_000000V.stat $COMOUTsmall/$VAR/.
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
else

	if [ $OBTYPE = smos ]; then
		DCOMINrtofsfilename=$DCOMROOT/$VDATE/validation_data/marine/smos/SM_D${JDATE}_Map_SATSSS_data_1day.nc
		COMINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$OBTYPE/rtofs_glo_2ds_f000_ice.$OBTYPE.nc
		export ftype="prog"
		export VARS="sss"
		export OBTYPEupper=$(echo $OBTYPE | tr '[a-z]' '[A-Z]')
		CLIMO=WOA23

	elif [ $OBTYPE = smap ]; then
		DCOMINrtofsfilename=$DCOMROOT/$VDATE/validation_data/marine/smap/SP_D${JDATE}_Map_SATSSS_data_1day.nc
		COMINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$OBTYPE/rtofs_glo_2ds_f000_ice.$OBTYPE.nc
		export ftype="prog"
		export VARS="sss"
		export OBTYPEupper=$(echo $OBTYPE | tr '[a-z]' '[A-Z]')
		CLIMO=WOA23

	elif [ $OBTYPE = ghrsst ]; then
		DCOMINrtofsfilename=$DCOMROOT/$VDATE/validation_data/marine/ghrsst/${VDATE}_OSPO_L4_GHRSST.nc
		COMINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$OBTYPE/rtofs_glo_2ds_f000_ice.$OBTYPE.nc
		export ftype="prog"
		export VARS="sst"
		export OBTYPEupper=$(echo $OBTYPE | tr '[a-z]' '[A-Z]')
		CLIMO=WOA23

	elif [ $OBTYPE = aviso ]; then
		DCOMINrtofsfilename=$DCOMROOT/$VDATE/validation_data/marine/cmems/ssh/nrt_global_allsat_phy_l4_${VDATE}_${VDATE}.nc
		COMINicefilename=$COMIN/prep/$COMPONENT/rtofs.$VDATE/$OBTYPE/rtofs_glo_2ds_f000_ice.$OBTYPE.nc
		export ftype="diag"
		export VARS="ssh"
		export OBTYPEupper=$(echo $OBTYPE | tr '[a-z]' '[A-Z]')
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
					COMINrtofsfilename=$COMIN/prep/$COMPONENT/rtofs.${match_date}/$OBTYPE/rtofs_glo_2ds_f${fhr3}_${ftype}.$OBTYPE.nc
					if [ -s $COMINrtofsfilename ] ; then
          					for vari in ${VARS}; do
            						export VAR=$vari
            						export VARupper=$(echo $VAR | tr '[a-z]' '[A-Z]')
            						mkdir -p $STATSDIR/${RUN}.$VDATE/$OBTYPE/${VERIF_CASE}/$VAR
            						if [ -s $COMOUTsmall/$VAR/grid_stat_RTOFS_${OBTYPEupper}_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat ]; then
              							cp -v $COMOUTsmall/$VAR/grid_stat_RTOFS_${OBTYPEupper}_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat $STATSDIR/${RUN}.$VDATE/$OBTYPE/${VERIF_CASE}/$VAR/.
            						else
              							run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
              							-c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/GridStat_fcstRTOFS_obs${OBTYPEupper}_climo$CLIMO.conf
              							export err=$?; err_chk
              							if [ $SENDCOM = "YES" ]; then
                  							mkdir -p $COMOUTsmall/$VAR
									if [ -s $STATSDIR/${RUN}.$VDATE/$OBTYPE/${VERIF_CASE}/$VAR/grid_stat_RTOFS_${OBTYPEupper}_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat ] ; then
                  								cp -v $STATSDIR/${RUN}.$VDATE/$OBTYPE/${VERIF_CASE}/$VAR/grid_stat_RTOFS_${OBTYPEupper}_${VARupper}_${fhr2}0000L_${VDATE}_000000V.stat $COMOUTsmall/$VAR/.
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
       				export subject="${OBTYPEupper} Data Missing for EVS RTOFS"
       				echo "Warning: No ${OBTYPEupper} data was available for valid date $VDATE." > mailmsg
       				echo "Missing file is ${DCOMINrtofsfilename}." >> mailmsg
       				cat mailmsg | mail -s "$subject" $MAILTO
   			fi
		fi
	else
		echo "WARNING:  Missing ${OBTYPEupper} data file for $VDATE: $DCOMINrtofsfilename"
		if [ $SENDMAIL = YES ] ; then
			export subject="${OBTYPEupper} Data Missing for EVS RTOFS"
			echo "Warning: No ${OBTYPEupper} data was available for valid date $VDATE." > mailmsg
			echo "Missing file is ${DCOMINrtofsfilename}." >> mailmsg
			cat mailmsg | mail -s "$subject" $MAILTO
		fi
	fi
fi

#########################################################################
# check if stat files exist
#########################################################################
#
for vari in ${VARS}; do
  export VAR=$vari
  export VARupper=$(echo $VAR | tr '[a-z]' '[A-Z]')
  export STATSOUT=$STATSDIR/${RUN}.$VDATE/$OBTYPE/${VERIF_CASE}/$VAR
  mkdir -p $STATSOUT
  VAR_file_count=$(find $STATSOUT -type f -name "*.stat" |wc -l)
  if [[ $VAR_file_count -ne 0 ]]; then
    # sum small stat files into one big file using Stat_Analysis
    run_metplus.py -c ${PARMevs}/metplus_config/machine.conf \
    -c $CONFIGevs/$STEP/$COMPONENT/${VERIF_CASE}/StatAnalysis_fcstRTOFS.conf
    export err=$?; err_chk
    if [ $SENDCOM = "YES" ]; then
	    if [ -s $STATSOUT/evs.stats.${COMPONENT}.${OBTYPE}.${VERIF_CASE}_${VAR}.v${VDATE}.stat ]; then
      		cp -v $STATSOUT/evs.stats.${COMPONENT}.${OBTYPE}.${VERIF_CASE}_${VAR}.v${VDATE}.stat $COMOUTfinal/.
	    fi
    fi
  else
     echo "WARNING: Missing RTOFS_${OBTYPEupper}_$VARupper stat files for $VDATE in $STATSDIR/${RUN}.$VDATE/$OBTYPE/${VERIF_CASE}/$VAR/*.stat" 
  fi
done

#######################################################################
