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
mkdir -p ${DATA}/gribs

echo 'Copying NWPS wave grib2 files'

HHs='00 06 12 18'
fcsts='000 024 048 072 096 120 144'
regions='ar er pr sr wr'

for region in ${regions} ; do
	COMINregion="${COMINnwps}/${region}.${INITDATE}"
	if [ ! -s $COMINregion ]; then
		echo "WARNING: No NWPS forecast was available for ${region}"
		if [ $SENDMAIL = YES ]; then
			export subject="Forecast Data Missing for ${region} EVS ${COMPONENT}"
			echo "WARNING: No NWPS forecast was available for ${region}" > mailmsg
			echo "WARNING: Missing file is $COMINregion" >> mailmsg
			echo "Job ID: $jobid" >> mailmsg
			cat mailmsg | mail -s "$subject" $MAILTO
		fi
	else
		find ${COMINregion} -name \*.grib2 -exec cp {} ${DATA}/gribs \;
	fi
done

wfos='aer afg ajk alu akq box car chs gys olm lwx mhx okx phi gum hfo bro crp hgx jax key lch lix mfi mlb mob sju tae tbw eka lox mfr mtr pqr sew sgx'
#CG1 is the main domain. CG2-CG6 are the nested domains.
#CGs='CG1 CG2 CG3 CG4 CG5 CG6'
CGs='CG1'
for wfo in $wfos; do
	for CG in $CGs; do
		for HH in ${HHs}; do
			DATAfilename=${DATA}/gribs/${wfo}_nwps_${CG}_${INITDATE}_${HH}00.grib2
			if [ ! -s ${DATAfilename} ]; then
				echo "WARNING: NO NWPS forecast was available for valid date ${INITDATE}"
			else
				fcst=0
				while (( $fcst <= 144 )); do
					FCST=$(printf "%03d" "$fcst")
	    				DATAfilename_fhr=${DATA}/gribs/${wfo}_nwps_${CG}.${INITDATE}.t${HH}z.f${FCST}.grib2
					ARCmodelfilename_fhr=${ARCmodel}/${wfo}_nwps_${CG}.${INITDATE}.t${HH}z.f${FCST}.grib2
					if [ ! -s $ARCmodelfilename_fhr ]; then
						if [ $fcst = 0 ]; then
							grib2_match_fhr=":surface:anl:"
						else
	    						grib2_match_fhr=":${fcst} hour fcst:"
						fi
						DATAfilename_fhr=${DATA}/gribs/${wfo}_nwps_${CG}.${INITDATE}.t${HH}z.f${FCST}.grib2
						wgrib2 $DATAfilename -match "$grib2_match_fhr" -grib $DATAfilename_fhr > /dev/null
						export err=$?; err_chk
						
						if [ -s $DATAfilename_fhr ]; then
							if [ $SENDCOM = YES ]; then
								cp -v $DATAfilename_fhr ${ARCmodel}/.
							fi
						else
							echo "WARNING: No NWPS Forecast Data was available for ${INITDATE}${HH}"
						fi
					fi
					fcst=$(( $fcst+ 24 ))
				done
			fi
		done
	done
done
	
###########################################################
# convert NDBC *.txt files into a netcdf file using ASCII2NC
############################################################

mkdir -p ${DATA}/ndbc
mkdir -p ${DATA}/ncfiles
mkdir -p ${COMOUT}.${INITDATE}/ndbc/${VERIF_CASE}
export MET_NDBC_STATIONS=${FIXevs}/ndbc_stations/ndbc_stations.xml
ndbc_txt_ncount=$(ls -l $DCOMINndbc/$INITDATE/validation_data/marine/buoy/*.txt |wc -l)
if [ $ndbc_txt_ncount -gt 0 ]; then
	python $USHevs/${COMPONENT}/nwps_wave_prep_read_ndbc.py
	export err=$?; err_chk
   
	
	run_metplus.py -c $CONFIGevs/machine.conf \
     	-c $CONFIGevs/$STEP/$COMPONENT/${RUN}_${VERIF_CASE}/ASCII2NC_obsNDBC.conf
   	export err=$?; err_chk

	tmp_ndbc_file=$DATA/ncfiles/ndbc.${INITDATE}.nc
	output_ndbc_file=${COMOUT}.${INITDATE}/ndbc/${VERIF_CASE}/ndbc.${INITDATE}.nc
	if [ $SENDCOM = YES ]; then
		if [ -s $tmp_ndbc_file ]; then
			cp -v $tmp_ndbc_file $output_ndbc_file
		fi
	fi
else
	echo "WARNING: No NDBC data was available for valid date ${INITDATE}."
	if [ $SENDMAIL = YES ]; then
		export subject="NDBC Data Missing for EVS ${COMPONENT}"
		echo "WARNING: No NDBC data was available for valid date ${INITDATE}." > mailmsg
		echo "Missing files are located at $COMINobs/${INITDATE}/validation_data/marine/buoy/." >> mailmsg
		echo "Job ID: $jobid" >> mailmsg
		cat mailmsg | mail -s "$subject" $MAILTO
	fi
fi


########################################

echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs prep *** "

################################ END OF SCRIPT ###########
