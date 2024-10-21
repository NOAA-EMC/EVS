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
mkdir -p ${VYYYYmm}_daily_stats
mkdir -p ${VYYYYmm}_station_info
mkdir -p jobs
mkdir -p job_work_dir

# Set jobs for temporal run
if [ $temporal = daily ]; then
    export group_list="reformat_data assemble_data generate_stats gather_stats"
elif [ $temporal = monthly ]; then
    export group_list="summarize_stats write_reports concatenate_reports"
fi

# Create and run job scripts
for group in $group_list; do
    export JOB_GROUP=$group
    mkdir -p jobs/${JOB_GROUP}
    echo "Creating and running jobs for WMO stats: ${JOB_GROUP}"
    python $USHevs/global_det/global_det_atmos_stats_wmo_create_${temporal}_job_scripts.py
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
    python $USHevs/global_det/global_det_atmos_copy_job_dir_output.py
    export err=$?; err_chk
done

# Send for missing files
if [ $SENDMAIL = YES ] ; then
    if ls $DATA/mail_* 1> /dev/null 2>&1; then
        for FILE in $DATA/mail_*; do
            $FILE
        done
    fi
fi

#########################################################################
# HOLD FOR DBN ALERTS FOR FILES TO DISSEMATE TO ECMWF
# ECMWF is currently the Lead Centre for Deterministic NWP Verification
#########################################################################
# DBN Alerts for monthly jobs
#if [ $temporal = monthly ]; then
#    if [ $SENDDBN = YES ]; then
#        $DBNROOT/bin/dbn_alert MODEL EVS_WMO $job $COMOUT/${MODELNAME}.${VDATE}/202408_kwbc_daily.rec2
#        $DBNROOT/bin/dbn_alert MODEL EVS_WMO $job $COMOUT/${MODELNAME}.${VDATE}/202408_kwbc_monthly.rec2
#        $DBNROOT/bin/dbn_alert MODEL EVS_WMO $job $COMOUT/${MODELNAME}.${VDATE}/202408_kwbc_dd10m.svs
#        $DBNROOT/bin/dbn_alert MODEL EVS_WMO $job $COMOUT/${MODELNAME}.${VDATE}/202408_kwbc_ff10m.svs
#        $DBNROOT/bin/dbn_alert MODEL EVS_WMO $job $COMOUT/${MODELNAME}.${VDATE}/202408_kwbc_rh2m.svs
#        $DBNROOT/bin/dbn_alert MODEL EVS_WMO $job $COMOUT/${MODELNAME}.${VDATE}/202408_kwbc_t2m.svs
#        $DBNROOT/bin/dbn_alert MODEL EVS_WMO $job $COMOUT/${MODELNAME}.${VDATE}/202408_kwbc_tcc.svs
#        $DBNROOT/bin/dbn_alert MODEL EVS_WMO $job $COMOUT/${MODELNAME}.${VDATE}/202408_kwbc_tp06.svs
#        $DBNROOT/bin/dbn_alert MODEL EVS_WMO $job $COMOUT/${MODELNAME}.${VDATE}/202408_kwbc_tp24.svs
#    fi
#fi
