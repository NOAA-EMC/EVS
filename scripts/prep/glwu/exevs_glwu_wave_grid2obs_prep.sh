#!/bin/bash
###############################################################################
<<<<<<< HEAD
# Name of Script: exevs_glwu_fcst_prep.sh
=======
# Name of Script: exevs_glwu_wave_grid2obs_prep.sh
>>>>>>> develop
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

<<<<<<< HEAD


# n024 is nowcast = f000 forecast
mkdir -p $COMOUTprep/glwu.$VDATE/$RUN
mkdir -p $DATA/glwu.$VDATE/$RUN

################################################################################
# Create today's GLWU individual fcst grib2 files and add them to the archive
################################################################################
mkdir -p ${DATA}/glwu_nc
mkdir -p ${DATA}/glwu_grib2

echo 'Copying GLWU wave grib2 and nc files'

HHs='00 06 12 18'
leads='000 024 048 072 096 120 144 168 192'

mtype='glwu glwu_lc grlc_2p5km grlc_2p5km_lc grlc_2p5km_lc_sr grlc_2p5km_sr grlr_500m grlr_500m_lc'


if [[ ${mtype} == "glwu" || ${mtype} == "glwu_lc" ]];then
  for HH in ${HHs} ; do
     for lead in ${leads} ; do
	filename="glwu.${mtype}.t${HH}z.nc"
	newname="glwu.${mtype}.${INITDATE}.t${HH}z.nc"
	if [ ! -s glwu.${INITDATE}/${filename} ]; then
	   export subject="F${lead} GLWU Forecast Data Missing for EVS ${COMPONENT}"
	   echo "Warning: No GLWU forecast was available for ${INITDATE}${HH}f${lead}" > mailmsg
	   echo "Missing file is glwu.${INITDATE}/${filename}" >> mailmsg
	   echo "Job ID: $jobid" >> mailmsg
	   cat mailmsg | mail -s "$subject" $MAILTO
        else
	   if [ ! -s ${ARCglwu}/${newname} ]; then
	      cp -v glwu.${INITDATE}/${filename} $DATA/glwu_nc/${newname}/
	      if [ $SENDCOM = YES ]; then
		 cp -v $DATA/glwu_nc/ ${ARCglwu}/glwu_nc/${newname}/
	      fi
	   fi
	fi
   done
  done
else
  for HH in ${HHs} ; do
     for lead in ${leads} ; do	   
	filename="glwu.${mtype}.t${HH}z.grib2"
	if [ ! -s glwu.${INITDATE}/${filename} ]; then
	    export subject="F${hr} GLWU Forecast Data Missing for EVS ${COMPONENT}"
	    echo "Warning: No GLWU forecast was available for ${INITDATE}${HH}f${lead}" > mailmsg
	    echo "Missing file is glwu.${INITDATE}/${filename}" >> mailmsg
	    echo "Job ID: $jobid" >> mailmsg
	    cat mailmsg | mail -s "$subject" $MAILTO
        else
	    if [ ! -s ${ARCglwu}/${newname} ]; then
	       cp -v glwu.${INITDATE}/${filename} $DATA/glwu_grib2/${newname}/
	       if [ $SENDCOM = YES ]; then
		  cp -v $DATA/glwu_grib2/ ${ARCglwu}/glwu_grib2/${newname}/
	       fi
	    fi
	fi
   done
  done
fi
=======
###############################################################################
# Create today's GLWU individual fcst grib2 files and add them to the archive
################################################################################

mkdir -p ${DATA}/nc
mkdir -p ${DATA}/gribs

echo 'Copying GLWU wave grib2 and nc files'

HHs='01 07 13 19'
fcsts="$(seq -s ' ' 0 144)"

for mtype in glwu glwu_lc grlc_2p5km grlc_2p5km_lc grlc_2p5km_lc_sr grlc_2p5km_sr grlr_500m grlr_500m_lc ; do
	export mtype=${mtype}
	if [ "${mtype}" == "grlc_2p5km" ] || [ "${mtype}" == "grlc_2p5km_lc" ]; then
		for HH in ${HHs} ; do
			filename="${MODELNAME}.${mtype}.t${HH}z.grib2"
			fullname="${COMINglwu}/${MODELNAME}.${INITDATE}/${filename}"
			DATAfilename="${DATA}/gribs/${MODELNAME}.${mtype}.${INITDATE}.t${HH}z.grib2"
			if [ ! -s ${fullname} ]; then
				echo "WARNING: No GLWU forecast was available for ${INITDATE}${HH}"
				if [ $SENDMAIL = YES ]; then
					export subject="GLWU Forecast Data Missing for EVS ${COMPONENT}"
					echo "WARNING: No GLWU forecast was available for ${INITDATE}${HH}" > mailmsg
					echo "Missing file is glwu.${INITDATE}/${filename}" >> mailmsg
					echo "Job ID: $jobid" >> mailmsg
					cat mailmsg | mail -s "$subject" $MAILTO
				fi
			else
				cp -v $fullname $DATAfilename
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
>>>>>>> develop

############################################################
# convert NDBC *.txt files into a netcdf file using ASCII2NC
############################################################

<<<<<<< HEAD
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


# Create the masks
$HOMEevs/scripts/$STEP/$COMPONENT/glwu_regions.sh

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
=======
mkdir -p ${DATA}/ndbc
mkdir -p ${DATA}/ncfiles
mkdir -p ${COMOUT}.${INITDATE}/ndbc/${VERIF_CASE}
export MET_NDBC_STATIONS=${FIXevs}/ndbc_stations/ndbc_stations.xml
ndbc_txt_ncount=$(ls -l $DCOMINndbc/$INITDATE/validation_data/marine/buoy/*.txt |wc -l)
if [ $ndbc_txt_ncount -gt 0 ]; then
	python $USHevs/${COMPONENT}/glwu_wave_prep_read_ndbc.py
	export err=$?; err_chk

	ndbc_gl_ncount=$(ls -l ${COMOUT}.${INITDATE}/ndbc/*.txt |wc -l)
	if [ $ndbc_gl_ncount -gt 0 ]; then
		run_metplus.py -c $PARMevs/metplus_config/machine.conf \
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
		echo "WARNING: No NDBC data at Great Lakes region was available for valid date ${INITDATE}."
	fi
else
	echo "WARNING: No NDBC data was available for valid date ${INITDATE}."
	if [ $SENDMAIL = YES ] ; then
 		export subject="NDBC Data Missing for EVS ${COMPONENT}"
		echo "WARNING: No NDBC data was available for valid date ${INITDATE}." > mailmsg
		echo "Missing files are located at $DCOMINndbc/${INITDATE}/validation_data/marine/buoy/." >> mailmsg
		echo "Job ID: $jobid" >> mailmsg
		cat mailmsg | mail -s "$subject" $MAILTO
	fi
fi

###################################################################################
>>>>>>> develop

echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs prep *** "

################################ END OF SCRIPT ###########
