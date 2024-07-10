#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_wave_grid2obs_stats.sh
# Developers: Deanna Spindler / Deanna.Spindler@noaa.gov
#             Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det wave stats step
#                    for the grid-to-obs verification. It uses METplus to
#                    generate the statistics.
###############################################################################

set -x

#############################
## grid2obs wave model stats
#############################

cd $DATA
echo "in $0"
echo "Starting grid2obs_stats for ${MODELNAME} ${RUN}"
echo "Starting at : `date`"
echo ' '
echo " *** ${MODELNAME}-${RUN} grid2obs stats ***"
echo ' '

export MODNAM=`echo $MODELNAME | tr '[a-z]' '[A-Z]'`
mkdir -p ${DATA}/gribs
mkdir -p ${DATA}/ncfiles
mkdir -p ${DATA}/all_stats
mkdir -p ${DATA}/jobs
mkdir -p ${DATA}/logs
mkdir -p ${DATA}/confs
mkdir -p ${DATA}/tmp

valid_hours='0 6 12 18'

##########################
# get the model fcst files
##########################
if [ $MODELNAME == "gfs" ]; then
    init_hours='0 6 12 18'
    lead_hours='0 6 12 18 24 30 36 42 48 54 60 66 72 78
                84 90 96 102 108 114 120 126 132 138 144 150 156 162
                168 174 180 186 192 198 204 210 216 222 228 234 240 246
                252 258 264 270 276 282 288 294 300 306 312 318 324 330
                336 342 348 354 360 366 372 378 384'
else
    err_exit "${MODELNAME} NOT VALID"
fi

############################################
# Get prepped ASCII2NC NBDC file
############################################
echo 'Getting NDBC ascii2nc file'
input_ascii2nc_ndbc_file=$COMIN/prep/${COMPONENT}/wave.${VDATE}/ndbc/ndbc.${VDATE}.nc
tmp_ascii2nc_ndbc_file=${DATA}/ncfiles/ndbc.${VDATE}.nc
if [[ $input_ascii2nc_ndbc_file == *"/com/"* ]] || [[ $input_ascii2nc_ndbc_file == *"/dcom/"* ]]; then
    alert_word="WARNING"
else
    alert_word="NOTE"
fi
if [[ -s $input_ascii2nc_ndbc_file ]]; then
    echo "Copying $input_ascii2nc_ndbc_file to $tmp_ascii2nc_ndbc_file"
    cp -v $input_ascii2nc_ndbc_file $tmp_ascii2nc_ndbc_file
else
    echo "${alert_word}: ${input_ascii2nc_ndbc_file} does not exist"
    if [ $SENDMAIL = YES ]; then
        export subject="NDBC Data Missing for EVS ${COMPONENT}"
        echo "Warning: No NDBC data was available for valid date ${VDATE}" > mailmsg
        echo "Missing file is ${input_ascii2nc_ndbc_file}" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
    fi
fi

############################################
# Get prepped PB2NC GDAS files
############################################
echo ' '
echo 'Getting GDAS pb2nc files'
for valid_hour in ${valid_hours} ; do
    valid_hour2=$(printf "%02d" "${valid_hour}")
    input_pb2nc_gdas_file=$COMIN/prep/${COMPONENT}/wave.${VDATE}/prepbufr_gdas/gdas.SFCSHP.${VDATE}${valid_hour2}.nc
    tmp_pb2nc_gdas_file=${DATA}/ncfiles/gdas.SFCSHP.${VDATE}${valid_hour2}.nc
    if [[ -s $input_pb2nc_gdas_file ]]; then
        echo "Copying $input_pb2nc_gdas_file to $tmp_pb2nc_gdas_file"
        cp -v $input_pb2nc_gdas_file $tmp_pb2nc_gdas_file
        chmod 640 $tmp_pb2nc_gdas_file
        chgrp rstprod $tmp_pb2nc_gdas_file
    else
        if [[ $input_pb2nc_gdas_file == *"/com/"* ]] || [[ $input_pb2nc_gdas_file == *"/dcom/"* ]]; then
            alert_word="WARNING"
        else
            alert_word="NOTE"
        fi
        echo "${alert_word}: $input_pb2nc_gdas_file does not exist"
        if [ $SENDMAIL = YES ] ; then
            export subject="GDAS Prepbufr Data Missing for EVS ${COMPONENT}"
            echo "Warning: No GDAS Prepbufr was available for valid date ${VDATE}${valid_hour2}" > mailmsg
            echo "Missing file is $input_pb2nc_gdas_file" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
        fi
    fi
done

####################
# quick error check
####################
nc=$(ls ${DATA}/ncfiles/gdas.SFCSHP.${VDATE}*.nc | wc -l | awk '{print $1}')
echo " Found ${DATA}/ncfiles/gdas.SFCSHP.${VDATE}*.nc for ${VDATE}"
if [ "${nc}" != '0' ]; then
    echo "Successfully found ${nc} GDAS pb2nc files for valid date ${VDATE}"
else
    echo "NOTE: No GDAS netcdf files for valid date ${VDATE} in ${DATA}/ncfiles"
fi
nc=$(ls ${DATA}/ncfiles/ndbc.${VDATE}*.nc | wc -l | awk '{print $1}')
echo " Found ${DATA}/ncfiles/ndbc.${VDATE}*.nc for ${VDATE}"
if [ "${nc}" != '0' ]; then
    echo "Successfully found ${nc} NDBC ascii2nc files for valid date ${VDATE}"
else
    echo "NOTE: No NDBC netcdf file for valid date ${VDATE} in ${DATA}/ncfiles"
fi

############################################
# create point_stat files
############################################
echo ' '
echo 'Creating point_stat files'
poe_script=${DATA}/jobs/run_all_PointStat_poe.sh
for valid_hour in ${valid_hours} ; do
    valid_hour2=$(printf "%02d" "${valid_hour}")
    if [ ${valid_hour2} = '00' ] ; then
        wind_level_str="'{ name=\"WIND\"; level=\"(0,*,*)\"; }'"
        htsgw_level_str="'{ name=\"HTSGW\"; level=\"(0,*,*)\"; }'"
        perpw_level_str="'{ name=\"PERPW\"; level=\"(0,*,*)\"; }'"
    elif [ ${valid_hour2} = '06' ] ; then
        wind_level_str="'{ name=\"WIND\"; level=\"(2,*,*)\"; }'"
        htsgw_level_str="'{ name=\"HTSGW\"; level=\"(2,*,*)\"; }'"
        perpw_level_str="'{ name=\"PERPW\"; level=\"(2,*,*)\"; }'"
    elif [ ${valid_hour2} = '12' ] ; then
        wind_level_str="'{ name=\"WIND\"; level=\"(4,*,*)\"; }'"
        htsgw_level_str="'{ name=\"HTSGW\"; level=\"(4,*,*)\"; }'"
        perpw_level_str="'{ name=\"PERPW\"; level=\"(4,*,*)\"; }'"
    elif [ ${valid_hour2} = '18' ] ; then
        wind_level_str="'{ name=\"WIND\"; level=\"(6,*,*)\"; }'"
        htsgw_level_str="'{ name=\"HTSGW\"; level=\"(6,*,*)\"; }'"
        perpw_level_str="'{ name=\"PERPW\"; level=\"(6,*,*)\"; }'"
    fi
    for fhr in ${lead_hours} ; do
        matchtime=$($NDATE -${fhr} ${VDATE}${valid_hour2})
        match_date=$(echo ${matchtime} | cut -c 1-8)
        match_hr=$(echo ${matchtime}  | cut -c 9-10)
        match_fhr=$(printf "%02d" "${match_hr}")
        flead=$(printf "%03d" "${fhr}")
        flead2=$(printf "%02d" "${fhr}")
        MODELNAME_upper=$(echo $MODELNAME | tr '[a-z]' '[A-Z]')
        if [ $MODELNAME == "gfs" ]; then
            input_model_file=$COMIN/prep/$COMPONENT/${RUN}.${match_date}/${MODELNAME}/${MODELNAME}${RUN}.${match_date}.t${match_fhr}z.global.0p25.f${flead}.grib2
        fi
        tmp_model_file=$DATA/gribs/${MODELNAME}${RUN}.${match_date}.t${match_fhr}z.global.0p25.f${flead}.grib2
        if [[ -s $input_model_file ]]; then
            if [[ ! -s $tmp_model_file ]]; then
                cp -v $input_model_file $tmp_model_file
            fi
        else
            if [[ $input_model_file == *"/com/"* ]] || [[ $input_model_file == *"/dcom/"* ]]; then
                alert_word="WARNING"
            else
                alert_word="NOTE"
            fi
            echo "${alert_word}: $input_model_file does not exist"
            if [ $SENDMAIL = YES ]; then
                export subject="F${flead} ${MODELNAME_upper} Forecast Data Missing for EVS ${COMPONENT}"
                echo "Warning: No ${MODELNAME_upper} forecast was available for ${matchtime}f${flead}" > mailmsg
                echo "Missing file is ${input_model_file}" >> mailmsg
                echo "Job ID: $jobid" >> mailmsg
                cat mailmsg | mail -s "$subject" $MAILTO
            fi
        fi
        if [[ -s $tmp_model_file ]]; then
            for OBSNAME in GDAS NDBC; do
                if [ $OBSNAME = GDAS ]; then
                    tmp_OBSNAME_file=${DATA}/ncfiles/gdas.SFCSHP.${VDATE}${valid_hour2}.nc
                elif [ $OBSNAME = NDBC ]; then
                    tmp_OBSNAME_file=${DATA}/ncfiles/ndbc.${VDATE}.nc
                fi
                tmp_stat_file=$DATA/all_stats/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${valid_hour2}0000V.stat
                output_stat_file=$COMOUTsmall/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${valid_hour2}0000V.stat
                if [[ -s $output_stat_file ]]; then
                    cp -v $output_stat_file $tmp_stat_file
                else
                    if [[ -s $tmp_OBSNAME_file ]]; then
                        echo "#!/bin/bash" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        echo "" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        echo "export valid_hour2=$valid_hour2" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        echo "export wind_level_str=${wind_level_str}" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        echo "export htsgw_level_str=${htsgw_level_str}" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        echo "export perpw_level_str=${perpw_level_str}" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        echo "export flead=${flead}" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        echo "export MODNAM=${MODNAM}" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        echo "run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}/PointStat_fcstGLOBAL_DET_obs${OBSNAME}_climoERA5_Wave_Multifield.conf" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        if [ $SENDCOM = YES ]; then
                            echo "if [ -f $tmp_stat_file ]; then cp -v $tmp_stat_file $output_stat_file; fi" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        fi
                        chmod +x ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
                        echo "${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh" >> $poe_script
                    fi
                fi
            done
        fi
    done
done
ncount_job=$(ls -l ${DATA}/jobs/run_PointStat*.sh |wc -l)
if [[ $ncount_job -gt 0 ]]; then
    if [ $USE_CFP = YES ]; then
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        nselect=$(cat $PBS_NODEFILE | wc -l)
        nnp=$(($nselect * $nproc))
        launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,core cfp"
        $launcher $MP_CMDFILE
        export err=$?; err_chk
    else
        ${poe_script}
        export err=$?; err_chk
    fi
fi

####################
# gather all the files
####################
nc=$(ls ${DATA}/all_stats/*stat | wc -l | awk '{print $1}')
echo " Found ${nc} ${DATA}/all_stats/*stat files for valid date ${VDATE} "
if [ "${nc}" != '0' ]; then
    echo "Small stat files found for valid date ${VDATE}"
    # Use StatAnalysis to gather the small stat files into one file
    run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}/StatAnalysis_fcstGLOBAL_DET.conf
    export err=$?; err_chk
else
    echo "WARNING: No small stat files found in ${DATA}/all_stats/*stat"
fi
# check to see if the large stat file was made, copy it to $COMOUTfinal
nc=$(ls ${DATA}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat | wc -l | awk '{print $1}')
echo " Found ${nc} large stat file for valid date ${VDATE} "
if [ "${nc}" != '0' ]; then
    echo "Large stat file found for ${VDATE}"
    if [ $SENDCOM = YES ]; then
        if [ -f ${DATA}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ]; then
            cp -v ${DATA}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ${COMOUTfinal}/.
        fi
    fi
else
    echo "WARNING: No large stat file found at ${DATA}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat"
fi

msg="JOB $job HAS COMPLETED NORMALLY."

echo ' '
echo "Ending grid2obs_stats for ${MODELNAME} ${RUN}"
echo "Ending at : `date`"
echo ' '
