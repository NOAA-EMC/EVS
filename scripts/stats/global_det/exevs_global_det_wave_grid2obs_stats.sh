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
# create ASCII2NC NBDC files and PB2NC GDAS files
############################################
poe_script=${DATA}/jobs/run_all_2NC_poe.sh
echo 'Creating NDBC ascii2nc files'
input_ascii2nc_ndbc_path=$COMIN/prep/${COMPONENT}/wave.${VDATE}/ndbc
tmp_ascii2nc_ndbc_file=${DATA}/ncfiles/ndbc.${VDATE}.nc
output_ascii2nc_ndbc_file=$COMOUTndbc/ndbc.${VDATE}.nc
if [[ -s $output_ascii2nc_ndbc_file ]]; then
    cpreq -v $output_ascii2nc_ndbc_file $tmp_ascii2nc_ndbc_file
else
    nbdc_txt_ncount=$(ls -l ${input_ascii2nc_ndbc_path}/*.txt |wc -l)
    if [[ $nbdc_txt_ncount -ne 0 ]]; then
        echo "#!/bin/bash" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "export MET_NDBC_STATIONS=${FIXevs}/ndbc_stations/ndbc_stations.xml" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}/ASCII2NC_obsNDBC.conf" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        if [ $SENDCOM = YES ]; then
            echo "cpreq -v $tmp_ascii2nc_ndbc_file $output_ascii2nc_ndbc_file" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        fi
        chmod +x ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh" >> $poe_script
    else
        if [[ $input_ascii2nc_ndbc_path == *"/com/"* ]] || [[ $input_ascii2nc_ndbc_path == *"/dcom/"* ]]; then
￼           alert_word="WARNING"
￼       else
￼           alert_word="NOTE"
￼       fi
￼       echo "${alert_word}: No files in $input_ascii2nc_ndbc_path"
    fi
fi
echo ' '
echo 'Creating GDAS pb2nc files'
for valid_hour in ${valid_hours} ; do
    valid_hour2=$(printf "%02d" "${valid_hour}")
    input_pb2nc_prepbufrgdas_file=$COMINobsproc/gdas.${VDATE}/${valid_hour2}/atmos/gdas.t${valid_hour2}z.prepbufr
    tmp_pb2nc_prepbufrgdas_file=${DATA}/ncfiles/gdas.${VDATE}${valid_hour2}.nc
    output_pb2nc_prepbufrgdas_file=$COMOUTprepbufr/gdas.${VDATE}${valid_hour2}.nc
    if [[ -s $output_pb2nc_prepbufrgdas_file ]]; then
        cpreq -v $output_pb2nc_prepbufrgdas_file $tmp_pb2nc_prepbufrgdas_file
        chmod 640 $tmp_pb2nc_prepbufrgdas_file
        chgrp rstprod $tmp_pb2nc_prepbufrgdas_file
    else
        if [ ! -s $input_pb2nc_prepbufrgdas_file ] ; then
            if [[ $input_pb2nc_prepbufrgdas_file == *"/com/"* ]] || [[ $input_pb2nc_prepbufrgdas_file == *"/dcom/"* ]]; then
                alert_word="WARNING"
            else
                alert_word="NOTE"
            fi
            echo "${alert_word}: $input_pb2nc_prepbufrgdas_file does not exist"
            if [ $SENDMAIL = YES ] ; then
                export subject="GDAS Prepbufr Data Missing for EVS ${COMPONENT}"
                echo "Warning: No GDAS Prepbufr was available for valid date ${VDATE}${valid_hour}" > mailmsg
                echo "Missing file is $input_pb2nc_prepbufrgdas_file" >> mailmsg
                echo "Job ID: $jobid" >> mailmsg
                cat mailmsg | mail -s "$subject" $MAILTO
            fi
        else
            echo "#!/bin/bash" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
            echo "" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
            echo "export valid_hour2=$valid_hour2" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
            echo "run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}/PB2NC_obsPrepbufrGDAS.conf" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
            echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
            echo "chmod 640 $tmp_pb2nc_prepbufrgdas_file" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
            echo "chgrp rstprod $tmp_pb2nc_prepbufrgdas_file" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
            if [ $SENDCOM = YES ]; then
                echo "cpreq -v $tmp_pb2nc_prepbufrgdas_file $output_pb2nc_prepbufrgdas_file" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
                echo "chmod 640 $output_pb2nc_prepbufrgdas_file" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
                echo "chgrp rstprod $output_pb2nc_prepbufrgdas_file" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
            fi
            chmod +x ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh
            echo "${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${valid_hour2}.sh" >> $poe_script
        fi
    fi
done
ncount_job=$(ls -l ${DATA}/jobs/run*2NC_*.sh |wc -l)
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
# quick error check
####################
nc=`ls ${DATA}/ncfiles/gdas.${VDATE}*.nc | wc -l | awk '{print $1}'`
echo " Found ${DATA}/ncfiles/gdas.${VDATE}*.nc for ${VDATE}"
if [ "${nc}" != '0' ]; then
    echo "Successfully found ${nc} GDAS pb2nc files for valid date ${VDATE}"
else
    echo "NOTE: No GDAS netcdf files for valid date ${VDATE} in ${DATA}/ncfiles"
fi
nc=`ls ${DATA}/ncfiles/ndbc.${VDATE}*.nc | wc -l | awk '{print $1}'`
echo " Found ${DATA}/ncfiles/ndbc.${VDATE}*.nc for ${VDATE}"
if [ "${nc}" != '0' ]; then
    echo "Successfully found ${nc} NDBC ascii2nc files for valid date ${VDATE}"
else
    echo "NOTE: No NDBC netcdf files for valid date ${VDATE} in ${DATA}/ncfiles"
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
        if [ $MODELNAME == "gfs" ]; then
            input_model_file=$COMIN/prep/$COMPONENT/${RUN}.${match_date}/${MODELNAME}/${MODELNAME}${RUN}.${match_date}.t${match_fhr}z.global.0p25.f${flead}.grib2
        fi
        tmp_model_file=$DATA/gribs/${MODELNAME}${RUN}.${match_date}.t${match_fhr}z.global.0p25.f${flead}.grib2
        if [[ -s $input_model_file ]]; then
            if [[ ! -s $tmp_model_file ]]; then
                cpreq -v $input_model_file $tmp_model_file
            fi
        else
            if [[ $input_model_file == *"/com/"* ]] || [[ $input_model_file == *"/dcom/"* ]]; then
                alert_word="WARNING"
            else
                alert_word="NOTE"
            fi
            echo "${alert_word}: $input_model_file does not exist"
        fi
        if [[ -s $tmp_model_file ]]; then
            for OBSNAME in GDAS NDBC; do
                if [ $OBSNAME = GDAS ]; then
                    tmp_OBSNAME_file=${DATA}/ncfiles/gdas.${VDATE}${valid_hour2}.nc
                elif [ $OBSNAME = NDBC ]; then
                    tmp_OBSNAME_file=${DATA}/ncfiles/ndbc.${VDATE}.nc
                fi
                tmp_stat_file=$DATA/all_stats/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${valid_hour2}0000V.stat
                output_stat_file=$COMOUTsmall/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${valid_hour2}0000V.stat
                if [[ -s $output_stat_file ]]; then
                    cpreq -v $output_stat_file $tmp_stat_file
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
                            echo "cpreq -v $tmp_stat_file $output_stat_file" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${valid_hour2}_f${flead}.sh
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
    echo "NOTE: No small stat files found in ${DATA}/all_stats/*stat"
fi
# check to see if the large stat file was made, copy it to $COMOUTfinal
nc=$(ls ${DATA}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat | wc -l | awk '{print $1}')
echo " Found ${nc} large stat file for valid date ${VDATE} "
if [ "${nc}" != '0' ]; then
    echo "Large stat file found for ${VDATE}"
    if [ $SENDCOM = YES ]; then
        cpreq -v ${DATA}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ${COMOUTfinal}/.
    fi
else
    echo "NOTE: No large stat file found at ${DATA}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat"
fi

# Cat the METplus log files
log_dir=$DATA/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
    for log_file in $log_dir/*; do
        echo "Start: $log_file"
        cat $log_file
        echo "End: $log_file"
    done
fi

msg="JOB $job HAS COMPLETED NORMALLY."

echo ' '
echo "Ending grid2obs_stats for ${MODELNAME} ${RUN}"
echo "Ending at : `date`"
echo ' '
