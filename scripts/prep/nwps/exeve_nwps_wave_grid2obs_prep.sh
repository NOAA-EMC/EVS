#!/bin/bash
###############################################################################
# Name of Script: exevs_nwps_wave_grid2obs_prep.sh
# Purpose of Script: To pre-process nwps forecast data into the same spatial
#    and temporal scales as validation data.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

##############################
## grid2obs NWPS Model Prep 
###############################

cd $DATA
echo "Starting grid2obs_prep for ${MODELNAME}_${RUN}"

echo ' '
echo ' *************************************'
echo " *** ${MODELNAME}-${RUN} grid2obs prep ***"
echo ' *************************************'
echo ' '
echo "Starting at : `date`"
echo '-------------'
echo ' '


################################################################################
# Create today's NWPS individual fcst grib2 files and add them to the archive
################################################################################
mkdir -p ${DATA}/grib2

echo 'Copying NWPS wave grib2 files'

HHs='00 06 12 18'
leads='000 024 048 072 096 120 144 168 192'
regions='ar er pr sr wr'

for region in ${regions} ; do
	COMINregion="${COMINnwps}/${region}.${INITDATE}"
	if [ ! -s $COMINregion ]; then
		if [ $SENDMAIL = YES ]; then
			export subject="NWPS Forecast Data Missing for ${region} EVS ${COMPONENT}"
			echo "WARNING: No NWPS forecast was available for ${region}" > mailmsg
			echo "WARNING: Missing file is $COMINregion" >> mailmsg
			echo "Job ID: $jobid" >> mailmsg
			cat mailmsg | mail -s "$subject" $MAILTO
		fi
	else
	find ${COMINregion} -name \*.grib2 -exec cp {} ${DATA}/grib2 \;
	fi
done

wfos='aer afg ajk alu akq box car chs gys olm lwx mhx okx phi gum hfo bro crp hgx jax key lch lix mfi mlb mob sju tae tbw eka lox mfr mtr pqr sew sgx'
CGs='CG1 CG2 CG3 CG4 CG5 CG6'
for wfo in $wfos; do
	for CG in $CGs; do
		for HH in ${HHs}; do
			DATAfilename=${DATA}/gribs/${wfo}_nwps_${CG}_${INITHOUR}_${HH}00.grib2
			if [ ! -s DATAfilename ]; then
				echo "WARNING: NO NWPS forecast was available for valid date ${INITDATE}"
				if [ $SENDMAIL = YES ] ; then
					export subject="NWPS Forecast Data Missing for EVS ${COMPONENT}"
					echo "Warning: No RTOFS forecast was available for ${VDATE}${lead}" > mailmsg
					echo "Missing file is ${input_rtofs_file}" >> mailmsg
					echo "Job ID: $jobid" >> mailmsg
	    				cat mailmsg | mail -s "$subject" $MAILTO
				fi
			else
				while (( $fcst <= 144 )); do
					FCST=$(printf "%03d" "$fcst")
	    				DATAfilename_fhr=${DATA}/gribs/${wfo}_nwps_${CG}_${INITHOUR}_${HH}00_f${FCST}.grib2
					ARCmodelfilename_fhr=${ARCmodel}/${wfo}_nwps_${CG}_${INITHOUR}_${HH}00_f${FCST}.grib2
					if [ ! -s $ARCmodelfilename_fhr ]; then
						if [ $fcst = 0 ]; then
							grib2_match_fhr=":surface:anl:"
						else
	    						grib2_match_fhr=":${fcst} hour fcst:"
						fi
						DATAfilename_fhr=${DATA}/gribs/${wfo}_nwps_${CG}_${INITHOUR}_${HH}00_f${FCST}.grib2
						wgrib2 $DATAfilename -match "$grib2_match_fhr" -grib $DATAfilename_fhr > /dev/null
						export err=$?; err_chk
						if [ $SENDCOM = YES ]; then
							cp -v $DATAfilename_fhr ${ARCmodel}/.
						fi
					fi
					fcst=$(( $fcst+ 1 ))
				done
			fi
		done
	done
done
	
###########################################################
# convert NDBC *.txt files into a netcdf file using ASCII2NC
############################################################

export RUN=ndbc
mkdir -p $COMOUTprep/glwu.$VDATE/$RUN
mkdir -p ${DATA}/ncfiles
export MET_NDBC_STATIONS=${FIXevs}/ndbc_stations/ndbc_stations.xml
ndbc_txt_ncount=$(ls -l $DCOMINndbc/$VDATE/validation_data/marine/buoy/*.txt |wc -l)
if [ $ndbc_txt_ncount -gt 0 ]; then
   run_metplus.py -c $CONFIGevs/metplus_glwu.conf \
     -c $CONFIGevs/grid2obs/$STEP/ASCII2NC_obsNDBC.conf
   export err=$?; err_chk
   if [ $SENDCOM = YES ]; then
	   cp -v $DATA/ncfiles/ndbc.${INITDATE}.nc ${COMOUT}.${INITDATE}/${MODELNAME}/${VERIF_CASE}/.
   fi
else
	if [ $SENDMAIL = YES ] ; then
 	export subject="NDBC Data Missing for EVS ${COMPONENT}"
	echo "Warning: No NDBC data was available for valid date $VDATE." > mailmsg
	echo "Missing files are located at $COMINobs/$VDATE/validation_data/marine/buoy/." >> mailmsg
	echo "Job ID: $jobid" >> mailmsg
	cat mailmsg | mail -s "$subject" $MAILTO
fi


##########################################
## Cat the prep log files
###########################################
log_dir=$DATA/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
	for log_file in $log_dir/*; do
		echo "Start: $log_file"
		cat $log_file
		echo "End: $log_file"
	done
fi
########################################

echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs prep *** "

################################ END OF SCRIPT ###########
