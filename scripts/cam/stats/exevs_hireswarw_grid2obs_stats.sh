#!/bin/sh
###############################################################################
# 
# Name:     exevs_hireswarw_grid2obs_stats.sh
# Abstract: Generate grid-to-observations verification statistics using METplus 
#           for the High-resolution Window Advanced Research WRF model
#
###############################################################################

set -x
echo

export USE_CASE_abbrev="g2os"

# Set run mode
if [ $RUN_ENVIR = nco]; then
    export evs_run_mode="production"
else
    export evs_run_mode=$evs_run_mode
fi
echo "RUN MODE:$evs_run_mode"

# Make use case directory
mkdir -p $USE_CASE
cd $USE_CASE

# Check user's config settings
python $USHevs/global_det/global_det_atmos_check_settings.py
stats=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran global_det_atmos_check_settings.py"
echo

# Link needed data files and set up model information
mkdir -p data
python $USHevs/global_det/global_det_atmos_get_data_files.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran global_det_get_data_files.py"
echo

# Create output directories
python $USHevs/global_det_global_det_atmos_create_output_dirs.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran global_det_atmos_create_output_dirs.py"
echo

# Create job scripts data
python $USHevs/global_det/global_det_atmos/create_stats_job_scripts.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran global_det_atmos_create_stats_jobs_scripts.py"

# Run job scripts for prep, make_met_data, and gather
for group in prep make_met_data gather; do
    chmod u+x metplus_job_scripts/$group/job*
    group_ncount_poe=$(ls -l metplus_job_scripts/$group/poe* |wc -l)
    group_ncount_job=$(ls -l metplus_job_scripts/$group/job* |wc -l)
    if [ $USER_CFP = YES ]; then
        nc=0
        while [ $nc -lt $group_ncount_poe ]; do
            nc=$((nc+1))
            poe_script=$DATA/$USE_CASE/metplus_job_scripts/$group/poe_jobs${nc}
            chmod 775 $poe_script
            export MP_PGMMODEL=mpmd
            export MP_CMDFILE=${poe_script}
            if [ $machine = WCOSS2 ]; then
                launcher="mpiexec -np $group_ncount_job --cpu-bind verbose,core cfp"
            elif [$machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET]; then
                launcher="srun --export=ALL --multi-prog"
            fi
            $launcher $MP_CMDFILE
        done
    else
        nc=0
        while [$nc -lt $group_ncount_job ]; do
            nc=$((nc+1))
            sh +x $DATA/$RUN/metplus_job_scripts/group_job${nc}
        done
    fi
done

# Copy stat files to desired location

# Send data to METviewer AWS server

# Clean up

