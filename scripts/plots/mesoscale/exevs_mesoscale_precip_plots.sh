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

export njob=1
export evs_run_mode=$evs_run_mode
source $config

# Check User's Configuration Settings
python $USHevs/mesoscale/mesoscale_check_settings.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran mesoscale_check_settings.py"
echo

# Create Output Directories
python $USHevs/mesoscale/mesoscale_create_output_dirs.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran mesoscale_create_output_dirs.py"

# Check For Restart Files
if [ $evs_run_mode = production ]; then
    python ${USHevs}/mesoscale/mesoscale_production_restart.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran ${USHevs}/mesoscale/mesoscale_production_restart.py"
fi

# Create Job Script 
python $USHevs/mesoscale/mesoscale_plots_precip_create_job_scripts.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran mesoscale_plots_precip_create_job_scripts.py"
export njob=$((njob+1))

# Create POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/mesoscale/mesoscale_plots_precip_create_poe_job_scripts.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_plots_precip_create_poe_job_scripts.py"
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
            echo "Cannot submit jobs to scheduler on this machine.  Set USE_CFP=NO and retry."
            exit 1    
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

# Copy files to desired location
#all commands to copy output files into the correct EVS COMOUT directory
if [ $SENDCOM = YES ]; then
    find ${DATA}/${VERIF_CASE}/out/*/*/*.{png,gif} -type f -print | tar -cvf ${DATA}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.v${VDATE}.tar -T -
    cp ${DATA}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.v${VDATE}.tar ${COMOUTplots}/.
fi

if [ $SENDDBN = YES ]; then
        $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job ${COMOUTplots}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.v${VDATE}.tar
fi


