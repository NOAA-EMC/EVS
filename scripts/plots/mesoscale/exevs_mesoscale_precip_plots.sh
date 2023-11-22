#!/bin/bash -e

# =============================================================================
#
# NAME: exevs_mesoscale_precip_plots.sh
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
#                 Roshan Shrestha, roshan.shrestha@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Handle all components of an EVS Mesoscale Precipitation - Plots job
# DEPENDENCIES: $HOMEevs/jobs/mesoscale/plots/JEVS_MESOSCALE_PLOTS 
#
# =============================================================================

set -x

# Set Basic Environment Variables
export machine=${machine:-"WCOSS2"}
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH
export njob=1
export evs_run_mode=$evs_run_mode
source $config

# Check User's Configuration Settings
python $USHevs/mesoscale/mesoscale_check_settings.py
export err=$?; err_chk

# Create Output Directories
python $USHevs/mesoscale/mesoscale_create_output_dirs.py
export err=$?; err_chk

# Check For Restart Files
if [ $evs_run_mode = production ]; then
    python ${USHevs}/mesoscale/mesoscale_production_restart.py
    export err=$?; err_chk

fi

# Create Job Script 
python $USHevs/mesoscale/mesoscale_plots_precip_create_job_scripts.py
export err=$?; err_chk

export njob=$((njob+1))

# Create POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/mesoscale/mesoscale_plots_precip_create_poe_job_scripts.py
    export err=$?; err_chk

fi

# Run All Mesoscale precip/plots Jobs
chmod u+x ${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/*
ncount_job=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/job* |wc -l)
nc=1
if [ $USE_CFP = YES ]; then
    ncount_poe=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/poe* |wc -l)
    while [ $nc -le $ncount_poe ]; do
        poe_script=${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/poe_jobs${nc}
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        if [ $machine = WCOSS2 ]; then
	    nselect=$(cat $PBS_NODEFILE | wc -l)
    	    nnp=$(($nselect * $nproc))
       	    launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,depth cfp"
            # launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
	    # ---
        elif [$machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
            export SLURM_KILL_BAD_EXIT=0
            launcher="srun --export=ALL --multi-prog"
        else
            err_exit "Cannot submit jobs to scheduler on this machine.  Set USE_CFP=NO and retry."
        fi
        $launcher $MP_CMDFILE
        nc=$((nc+1))
    done
else
    while [ $nc -le $ncount_job ]; do
        ${DATA}/${VERIF_CASE}/${STEP}/plotting_job_scripts/job${nc}
        nc=$((nc+1))
    done
fi

# Tar and Copy output files to EVS COMOUT directory
  find ${DATA}/${VERIF_CASE}/* -type f \( -name "*.png" -o -name "*.gif" \) -print | tar -cvf ${DATA}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.v${VDATE}.tar --transform='s#.*/##' -T -

if [ $SENDCOM = YES ]; then
    cpreq -v ${DATA}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.v${VDATE}.tar ${COMOUTplots}/.
fi

if [ $SENDDBN = YES ]; then
        $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job ${COMOUTplots}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.v${VDATE}.tar
fi


