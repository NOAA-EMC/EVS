#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_wave_grid2obs_prep.sh
# Purpose of Script: To pre-process glwu forecast data into the same spatial
#    and temporal scales as validation data.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

##############################
## grid2obs GLWU Model Prep 
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

###############################################################################
# Create today's GLWU individual fcst grib2 files and add them to the archive
################################################################################

mkdir -p ${DATA}/nc
mkdir -p ${DATA}/gribs
#mkdir -p $COMOUTprep/glwu.${INITDATE}/$RUN

echo 'Copying GLWU wave grib2 and nc files'

HHs='01 07 13 19'
fcsts='0 24 48 72 96 120 144'

#mtypes='glwu glwu_lc grlc_2p5km grlc_2p5km_lc grlc_2p5km_lc_sr grlc_2p5km_sr grlr_500m grlr_500m_lc'

for mtype in glwu glwu_lc grlc_2p5km grlc_2p5km_lc grlc_2p5km_lc_sr grlc_2p5km_sr grlr_500m grlr_500m_lc ; do
	export mtype=${mtype}
	if [ "${mtype}" == "grlc_2p5km" ] || [ "${mtype}" == "grlc_2p5km_lc" ]; then
		for HH in ${HHs} ; do
			filename="${MODELNAME}.${mtype}.t${HH}z.grib2"
			COMINfilename="${COMINglwu}/${MODELNAME}.${INITDATE}/${filename}"
			DATAfilename="${DATA}/gribs/${MODELNAME}.${mtype}.${INITDATE}.t${HH}z.grib2"
			if [ ! -s ${COMINfilename} ]; then
				if [ SENDMAIL = YES ]; then
					export subject="GLWU Forecast Data Missing for EVS ${COMPONENT}"
					echo "WARNING: No GLWU forecast was available for ${INITDATE}${HH}" > mailmsg
					echo "Missing file is glwu.${INITDATE}/${filename}" >> mailmsg
					echo "Job ID: $jobid" >> mailmsg
					cat mailmsg | mail -s "$subject" $MAILTO
				fi
			else
				cp -v $COMINfilename $DATAfilename
			fi
			if [ -s $DATAfilename ]; then
				for fcst in ${fcsts} ; do
					FCST=$(printf "%03d" "$fcst")		
					if [ ${fcst} = 0 ]; then
						grib2_match=":surface:anl:"
					else
						grib2_match=":${fcst} hour fcst:"
					fi
					DATAfilename_fcst="${DATA}/gribs/${MODELNAME}.${mtype}.${INITDATE}.t${HH}z.f${FCST}.grib2"
					ARCmodelfilename="${ARCmodel}/${MODELNAME}.${mtype}.${INITDATE}.t${HH}z.f${FCST}.grib2"
					wgrib2 $DATAfilename -match "$grib2_match" -grib $DATAfilename_fcst > /dev/null
					export err=$?; err_chk
					if [ $SENDCOM = YES ]; then
						cp -v $DATAfilename_fcst ${ARCmodelfilename}
					fi
				done
			fi
		done
	fi
done

############################################################
# convert NDBC *.txt files into a netcdf file using ASCII2NC
############################################################

#mkdir -p $COMOUTprep/glwu.${INITDATE}/$RUN
mkdir -p ${DATA}/ndbc
mkdir -p ${DATA}/ncfiles
export MET_NDBC_STATIONS=${FIXevs}/ndbc_stations/ndbc_stations.xml
ndbc_txt_ncount=$(ls -l $DCOMINndbc/$INITDATE/validation_data/marine/buoy/*.txt |wc -l)
if [ $ndbc_txt_ncount -gt 0 ]; then
	python $USHevs/${COMPONENT}/glwu_wave_prep_read_ndbc.py
	export err=$?; err_chk

	run_metplus.py -c $PARMevs/metplus_config/machine.conf \
   	-c $CONFIGevs/$STEP/$COMPONENT/${RUN}_${VERIF_CASE}/ASCII2NC_obsNDBC.conf
   	export err=$?; err_chk

   	tmp_ndbc_file=$DATA/ncfiles/ndbc.${INITDATE}.nc
   	output_ndbc_file=${COMOUT}.${INITDATE}/${MODELNAME}/${VERIF_CASE}/ndbc.${INITDATE}.nc
   	if [ $SENDCOM = YES ]; then
		if [ -s $tmp_ndbc_file ]; then
	   		cp -v $tmp_ndbc_file $output_ndbc_file
	   	fi
   	fi
else
	if [ $SENDMAIL = YES ] ; then
 		export subject="NDBC Data Missing for EVS ${COMPONENT}"
		echo "Warning: No NDBC data was available for valid date ${INITDATE}." > mailmsg
		echo "Missing files are located at $DCOMINndbc/${INITDATE}/validation_data/marine/buoy/." >> mailmsg
		echo "Job ID: $jobid" >> mailmsg
		cat mailmsg | mail -s "$subject" $MAILTO
	fi
fi

###################################################################################
# Create masks for Great Lakes regions
# NOTE: script below is calling MET's gen_vx_mask directly instead of using METplus
# keeping it in a ush script; future use should use METplus to do this
###################################################################################

$USHevs/${COMPONENT}/${COMPONENT}_${STEP}_regions.sh

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
#######################################

echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs prep *** "

################################ END OF SCRIPT ###########
