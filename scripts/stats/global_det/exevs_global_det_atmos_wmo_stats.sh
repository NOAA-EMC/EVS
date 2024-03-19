#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_atmos_wmo_stats.sh
# Developers: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det atmos WMO stats step.
#                    It does grid-to-grid and grid-to-observations following the
#                    WMO requirements.
###############################################################################

set -x

# Set month and year
export VYYYYmm=$(echo $VDATE | cut -c1-6)

# Make directories
mkdir -p ${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE} ${MODELNAME}.${VDATE}
mkdir -p gdas_cnvstat
chmod 750 gdas_cnvstat
chgrp rstprod gdas_cnvstat
mkdir -p ${VYYYYmm}_daily_stats
mkdir -p jobs logs confs tmp

# Create and run job scripts for reformat_data generate_stats, gather_stats, and summarize_stats
for group in reformat_data generate_stats gather_stats summarize_stats; do
    export JOB_GROUP=$group
    mkdir -p jobs/${JOB_GROUP}
    echo "Creating and running jobs for WMO stats: ${JOB_GROUP}"
    python $USHevs/global_det/global_det_atmos_stats_wmo_create_job_scripts.py
    export err=$?; err_chk
    chmod u+x jobs/$group/*
    nc=1
    if [ $USE_CFP = YES ]; then
        group_ncount_poe=$(ls -l  jobs/$group/poe* |wc -l)
        while [ $nc -le $group_ncount_poe ]; do
            poe_script=$DATA/jobs/$group/poe_jobs${nc}
            chmod 775 $poe_script
            export MP_PGMMODEL=mpmd
            export MP_CMDFILE=${poe_script}
            if [ $machine = WCOSS2 ]; then
                nselect=$(cat $PBS_NODEFILE | wc -l)
                nnp=$(($nselect * $nproc))
                launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,core cfp"
            elif [ $machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
                export SLURM_KILL_BAD_EXIT=0
                launcher="srun --export=ALL --multi-prog"
            fi
            $launcher $MP_CMDFILE
            export err=$?; err_chk
            nc=$((nc+1))
        done
    else
        group_ncount_job=$(ls -l  jobs/$group/job* |wc -l)
        while [ $nc -le $group_ncount_job ]; do
            $DATA/jobs/$group/job${nc}
            export err=$?; err_chk
            nc=$((nc+1))
        done
    fi
done

# Send for missing files
if [ $SENDMAIL = YES ] ; then
    if ls $DATA/mail_* 1> /dev/null 2>&1; then
        for FILE in $DATA/mail_*; do
            $FILE
        done
    fi
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

# Combine monthly summary files into 1
tmp_monthly_stats_file_wildcard=${DATA}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}/gfs.*.${VYYYYmm}_*Z.summary.stat
tmp_monthly_stat_file_count=$(ls $tmp_monthly_stats_file_wildcard 2> /dev/null | wc -l)
tmp_monthly_stat_file=${DATA}/${MODELNAME}.${VDATE}/${NET}.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VYYYYmm}.stat
output_monthly_stat_file=${COMOUT}/${MODELNAME}.${VDATE}/${NET}.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VYYYYmm}.stat
if [ ! -s ${output_monthly_stat_file} ]; then
    >${tmp_monthly_stat_file}
    if [ ${tmp_monthly_stat_file_count} != "0" ]; then
        for tmp_monthly_stats_file in $tmp_monthly_stats_file_wildcard; do
            cat $tmp_monthly_stats_file >> ${tmp_monthly_stat_file}
        done
        if [ $SENDCOM = YES ]; then
            if [ -f ${tmp_monthly_stat_file} ]; then cp -v ${tmp_monthly_stat_file} ${output_monthly_stat_file}; fi
        fi
    else
        echo "NOTE: No files matching ${tmp_monthly_stats_file_wildcard}"
    fi
else
    echo "Copying ${output_monthly_stat_file} to ${tmp_monthly_stat_file}"
    cp -v ${output_monthly_stat_file} ${tmp_monthly_stat_file}
fi

# Format daily & monthly stats for WMO rec2 - domain
for temporal in daily monthly; do
    tmp_temporal_wmo_rec2_file=${DATA}/${MODELNAME}.${VDATE}/${VYYYYmm}_kwbc_${temporal}.rec2
    output_temporal_wmo_rec2_file=${COMOUT}/${MODELNAME}.${VDATE}/${VYYYYmm}_kwbc_${temporal}.rec2
    if [ ! -s ${output_temporal_wmo_rec2_file} ]; then
        python $USHevs/global_det/global_det_atmos_stats_wmo_format_rec2_domain_${temporal}.py
        export err=$?; err_chk
        if [ $SENDCOM = YES ]; then
            if [ -f ${tmp_temporal_wmo_rec2_file} ]; then cp -v ${tmp_temporal_wmo_rec2_file} ${output_temporal_wmo_rec2_file}; fi
        fi
    else
        echo "Copying ${output_temporal_wmo_rec2_file} to ${tmp_temporal_wmo_rec2_file}"
        cp -v ${output_temporal_wmo_rec2_file} ${tmp_temporal_wmo_rec2_file}
    fi
done
