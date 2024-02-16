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

mkdir -p $COMOUTprep/glwu.$VDATE/$RUN
mkdir -p $DATA/glwu.$VDATE/$RUN

################################################################################
# Create today's GLWU individual fcst grib2 files and add them to the archive
################################################################################
mkdir -p ${DATA}/nc
mkdir -p ${DATA}/grib2

echo 'Copying GLWU wave grib2 and nc files'

HHs='01 07 13 19'
leads='000 024 048 072 096 120 144'

mtypes='glwu glwu_lc grlc_2p5km grlc_2p5km_lc grlc_2p5km_lc_sr grlc_2p5km_sr grlr_500m grlr_500m_lc'

for mtype in $mtypes; do
	if [[ ${mtype} == "grlc_2p5km" || ${mtype} == "grlc_2p5km_lc" ]]; then
		for HH in ${HHs} ; do
			filename="glwu.${mtype}.t${HH}z.grib2"
			COMINfilename="${COMINglwu}/${MODELNAME}.${INITDATE}/${filename}"
			DATAfilename="${DATA}/grib2/${MODELNAME}.${INITDATE}.t${HH}z.grib2"
			if [ ! -s COMINfilename ]; then
				if [ SENDMAIL = YES ]; then
					export subject="F${lead} GLWU Forecast Data Missing for EVS ${COMPONENT}"
					echo "WARNING: No GLWU forecast was available for ${INITDATE}${HH}f${lead}" > mailmsg
					echo "Missing file is glwu.${INITDATE}/${filename}" >> mailmsg
					echo "Job ID: $jobid" >> mailmsg
					cat mailmsg | mail -s "$subject" $MAILTO
				fi
			else
				cp -v $COMINfilename $DATAfilename
			fi
			if [ -s $DATAfilename ]; then
				for lead in ${leads} ; do		
					if [ $lead = 0 ]; then
						grib2_match=":surface:anl:"
					else
						grib2_match=":${fcst} hour fcst:"
					fi
					DATAfilename_fcst="${DATA}/grib2/${MODELNAME}.${INITDATE}.t${HH}z.f${fcst}.grib2"
					ARCmodelfilename="${ARCmodel}/${MODELNAME}.${INITDATE}.t${HH}z.f${fcst}.grib2"
					wgrib2 $DATAfilename -match "$grib2_match" -grib $DATAfilename_fcst > /dev/null
					export err=$?; err_chk
					if [ $SENDCOM = YES ]; then
						cp -v $DATAfilename_fcst ${ARCmodelfilename}/.
					fi
				done
			fi
		done
	fi
done

############################################################
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
fi


############################################
# get the GDAS prepbufr files for yesterday 
############################################

echo 'Copying GDAS prepbufr files'

for HH in 00 06 12 18 ; do
	export inithour=t${HH}z
	if [ ! -s ${COMINobsproc}.${INITDATE}/${HH}/atmos/gdas.${inithour}.prepbufr ]; then
		export subject="GDAS Prepbufr Data Missing for EVS ${COMPONENT}"
		echo "WARNING: No GDAS Prepbufr was available for init date ${INITDATE}${HH}" > mailmsg
		echo "WARNING: Missing file is ${COMINobsproc}.${INITDATE}/${HH}/atmos/gdas.${inithour}.prepbufr" >> mailmsg
		echo "Job ID: $jobid" >> mailmsg
		cat mailmsg | mail -s "$subject" $MAILTO
	else
		cp -v ${COMINobsproc}.${INITDATE}/${HH}/atmos/gdas.${inithour}.prepbufr ${DATA}/gdas.${INITDATE}${HH}.prepbufr
	fi
done


############################################
# run PB2NC                                 
############################################

echo 'Run pb2nc'

for HH in 00 12; do
	export HH=$HH
	export inithour=t${HH}z
	if [ -s ${DATA}/gdas.${INITDATE}${HH}.prepbufr ]; then
		if [ ! -s ${COMOUT}.${INITDATE}/${MODELNAME}/${VERIF_CASE}/gdas.${INITDATE}${HH}.nc ]; then
			run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}/PB2NC_wave.conf
			export err=$?; err_chk
			if [ $SENDCOM = YES ]; then
				cp -v $DATA/ncfiles/gdas.${INITDATE}${HH}.nc ${COMOUT}.${INITDATE}/${MODELNAME}/${VERIF_CASE}/.
			fi
		fi
		chmod 640 $DATA/ncfiles/gdas.${INITDATE}${HH}.nc
		chgrp rstprod $DATA/ncfiles/gdas.${INITDATE}${HH}.nc	
	fi
done

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
