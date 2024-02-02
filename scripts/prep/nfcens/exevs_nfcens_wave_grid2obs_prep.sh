#!/bin/bash
###############################################################################
# Name of Script: exevs_nfcens_wave_grid2obs_prep.sh                           
# Deanna Spindler / Deanna.Spindler@noaa.gov                                   
# Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: Run the grid2obs data prep for any global wave model      
#                    (deterministic and ensemble: GEFS-Wave, GFS-Wave, NWPS)   
#                                                                              
# Usage:                                                                       
#  Parameters: None                                                            
#  Input files:                                                                
#     gdas.${inithour}.prepbufr                                                   
#  Output files:                                                               
#     gdas.${validdate}.nc                                                     
#     individual fcst grib2 files                                              
#  Condition codes:                                                            
#     99  - Missing input file                                                 
#  User controllable options: None                                             
###############################################################################

set -x 

##############################
## grid2obs NFCENS Model Prep 
##############################

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
# create today's NFCENS individual fcst grib2 files and add them to the archive
###############################################################################
HHs='00 12'

mkdir -p ${DATA}/gribs

for HH in ${HHs} ; do
    # copy the model grib2 files
    COMINfilename="${COMINnfcens}/${MODELNAME}.${INITDATE}/HTSGW_mean.t${HH}z.grib2"
    DATAfilename="${DATA}/gribs/HTSGW_mean.${INITDATE}.t${HH}z.grib2"
    if [ ! -s $COMINfilename ]; then
	    if [ $SENDMAIL = YES ]; then
		    export subject="NFCENS Forecast Data Missing for EVS ${COMPONENT}"
		    echo "WARNING: No NFCENS forecast was available for ${INITDATE}${HH}" > mailmsg
		    echo "WARNING: Missing file is $COMINfilename" >> mailmsg
		    echo "Job ID: $jobid" >> mailmsg
		    cat mailmsg | mail -s "$subject" $MAILTO
	    fi
    else
        cp -v $COMINfilename $DATAfilename
    fi
    if [ -s $DATAfilename ]; then
        fcst=0
        # create the individual fcst files for every 6hrs
        while (( $fcst <= 240 )); do
            FCST=$(printf "%03d" "$fcst")
            DATAfilename_fhr=${DATA}/gribs/HTSGW_mean.${INITDATE}.t${HH}z.f${FCST}.grib2
            ARCmodelfilename_fhr=${ARCmodel}/HTSGW_mean.${INITDATE}.t${HH}z.f${FCST}.grib2
            if [ ! -s $ARCmodelfilename_fhr ]; then
                if [ $fcst = 0 ]; then
                    grib2_match_fhr=":surface:anl:"
                else
                    grib2_match_fhr=":${fcst} hour fcst:"
                fi
                DATAfilename_fhr=${DATA}/gribs/HTSGW_mean.${INITDATE}.t${HH}z.f${FCST}.grib2
                wgrib2 $DATAfilename -match "$grib2_match_fhr" -grib $DATAfilename_fhr > /dev/null
                export err=$?; err_chk
		if [ $SENDCOM = YES ]; then
                    cp -v $DATAfilename_fhr ${ARCmodel}/.
                fi
            fi
            fcst=$(( $fcst+ 6 ))
        done
    fi
done

############################################
# get the GDAS prepbufr files for yesterday 
############################################
echo 'Copying GDAS prepbufr files'

for HH in 00 06 12 18 ; do

  export inithour=t${HH}z
  if [ ! -s ${COMINobsproc}.${INITDATE}/${HH}/atmos/gdas.${inithour}.prepbufr ]; then
	  if [ $SENDMAIL = YES ];then
		  export subject="GDAS Prepbufr Data Missing for EVS ${COMPONENT}"
		  echo "WARNING: No GDAS Prepbufr was available for init date ${INITDATE}${HH}" > mailmsg
		  echo "WARNING: Missing file is ${COMINobsproc}.${INITDATE}/${HH}/atmos/gdas.${inithour}.prepbufr" >> mailmsg
		  echo "Job ID: $jobid" >> mailmsg
		  cat mailmsg | mail -s "$subject" $MAILTO
	  fi
  else
      cp -v ${COMINobsproc}.${INITDATE}/${HH}/atmos/gdas.${inithour}.prepbufr ${DATA}/gdas.${INITDATE}${HH}.prepbufr
  fi

done

############################################
# run PB2NC                                 
############################################
echo 'Run pb2nc'

mkdir $DATA/ncfiles

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
# Cat the prep log files
##########################################
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
echo ' '

# End of NFCENS grid2obs prep script -------------------------------------- #
