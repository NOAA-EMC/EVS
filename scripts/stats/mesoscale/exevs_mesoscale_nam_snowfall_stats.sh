#!/bin/sh
###############################################################################
# Name of Script: exevs_mesoscale_nam_snowfall_stats.sh 
# Purpose of Script: This script generates snowfall
#                    verification statistics using METplus for the
#                    atmospheric component of NAM models
# Log history:
###############################################################################

set -x
  export machine=${machine:-"WCOSS2"} 
  export VERIF_CASE_STEP_abbrev="snowfalls"
  export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH

# Set run mode
  export evs_run_mode=$evs_run_mode
  source $config

# Make directory
mkdir -p $DATA/logs
mkdir -p $DATA/confs
mkdir -p $DATA/data
mkdir -p $DATA/tmp
mkdir -p $DATA/jobs
mkdir -p $DATA/${MODELNAME}.${VDATE}
mkdir -p $DATA/${RUN}.${VDATE}/$MODELNAME/$VERIF_CASE

# Get NAM and NOHRSC
python $USHevs/mesoscale/mesoscale_snowfall_stats_get_data.py

    export err=$?; err_chk

# Send for missing files
if ls $DATA/mail_* 1> /dev/null 2>&1; then
    for FILE in $DATA/mail_*; do
        $FILE
    done
fi

# What jobs to run
if [ $vhr = 18 ]; then
    JOB_GROUP_list="assemble_data generate_stats gather_stats"
else
    JOB_GROUP_list="assemble_data generate_stats"
fi

# Create and run job scripts
for group in $JOB_GROUP_list; do
    export JOB_GROUP=$group
    mkdir -p $DATA/jobs/$JOB_GROUP
    echo "Creating and running jobs for snowfall stats: ${JOB_GROUP}"
    python $USHevs/mesoscale/mesoscale_snowfall_stats_create_job_scripts.py

    export err=$?; err_chk

    chmod u+x $DATA/jobs/$JOB_GROUP/*
    group_ncount_job=$(ls -l $DATA/jobs/$JOB_GROUP/job* |wc -l)
    nc=1
    if [ $USE_CFP = YES ]; then
        group_ncount_poe=$(ls -l $DATA/jobs/$JOB_GROUP/poe* |wc -l)
        while [ $nc -le $group_ncount_poe ]; do
            poe_script=$DATA/jobs/$JOB_GROUP/poe_jobs${nc}
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
            nc=$((nc+1))
        done
    else
        while [ $nc -le $group_ncount_job ]; do
            sh +x $DATA/jobs/$JOB_GROUP/job${nc}
            nc=$((nc+1))
        done
    fi
    if [ $JOB_GROUP = gather_stats ]; then
        # Copy output files into the correct EVS COMOUT directory
        if [ $SENDCOM = YES ]; then
           if [ -s $DATA/${MODELNAME}.${VDATE}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ]; then
              cp -v $DATA/${MODELNAME}.${VDATE}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat $COMOUTfinal/.
	   fi
        fi
    fi
done

echo "******************************"
echo "Begin to print METplus Log files "
  cat $DATA/logs/*
echo "End to print METplus Log files "

