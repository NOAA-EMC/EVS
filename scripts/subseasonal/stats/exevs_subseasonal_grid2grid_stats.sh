#!/bin/bash
# Program Name: exevs_subseasonal_grid2grid_stats.sh
# Author(s)/Contact(s): Shannon Shields
# Abstract: Run METplus for subseasonal grid-to-grid verification to produce 
#           stats
# History Log:

set -x

echo
echo "===== RUNNING GRID-TO-GRID STATS VERIFICATION  ====="
export STEP="stats"
export VERIF_CASE_STEP="grid2grid_stats"
export VERIF_CASE_STEP_abbrev="g2gstats"

# Set up directories
mkdir -p $VERIF_CASE_STEP
cd $VERIF_CASE_STEP

# Set up domains
#if [ $domain = "GLOBAL" ]
#then
	#export grid=G003
	#export poly=
#fi

#if [ $domain = "NH" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_NHEM.nc
#fi

#if [ $domain = "SH" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_SHEM.nc
#fi

#if [ $domain = "CONUS" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Bukovsky_G003_CONUS.nc
#fi

#if [ $domain = "CCONUS" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Bukovsky_G003_CONUS_Central.nc
#fi

#if [ $domain = "SCONUS" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Bukovsky_G003_CONUS_South.nc
#fi

#if [ $domain = "ECONUS" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Bukovsky_G003_CONUS_East.nc
#fi

#if [ $domain = "WCONUS" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Bukovsky_G003_CONUS_West.nc
#fi

#if [ $domain = "AK" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Alaska_G003.nc
#fi

#if [ $domain = "HWI" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Hawaii_G003.nc
#fi

#if [ $domain = "40S40N" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_40S_40N.nc
#fi

#if [ $domain = "Nino" ]
#then
	#export grid=G003
	#export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_Nino1_2.nc, /lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_Nino3.nc, /lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_Nino3_4.nc, /lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_Nino4.nc
#fi

# Check user's configuration file
python $USHevs/subseasonal/check_subseasonal_config_stats.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran check_subseasonal_config_stats.py"
echo

# Set up environment variables for initialization, valid, and forecast hours and source them
python $USHevs/subseasonal/set_init_valid_fhr_subseasonal_stats_info.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran set_init_valid_fhr_subseasonal_stats_info.py"
echo
. $DATA/$VERIF_CASE_STEP/python_gen_env_vars.sh
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully sourced python_gen_env_vars.sh"
echo

# Create output directories for METplus
python $USHevs/subseasonal/create_METplus_subseasonal_output_dirs.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran create_METplus_subseasonal_output_dirs.py"
echo

# Link needed data files and set up model information
python $USHevs/subseasonal/subseasonal_get_data_files.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran subseasonal_get_data_files.py"
echo

# Create job scripts to run METplus for reformat_data, assemble_data, generate_stats, and gather_stats
for group in reformat_data assemble_data generate_stats gather_stats; do
    export JOB_GROUP=$group
    echo "Creating and running jobs for grid-to-grid stats: ${JOB_GROUP}"
    python $USHevs/subseasonal/subseasonal_stats_grid2grid_create_job_scripts.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran subseasonal_stats_grid2grid_create_job_scripts.py"
    chmod u+x $DATA/$VERIF_CASE_STEP/METplus_job_scripts/$group/*
    group_ncount_job=$(ls -l  $DATA/$VERIF_CASE_STEP/METplus_job_scripts/$group/job* |wc -l)
    nc=1
    if [ $USE_CFP = YES ]; then
        group_ncount_poe=$(ls -l  $DATA/$VERIF_CASE_STEP/METplus_job_scripts/$group/poe* |wc -l)
        while [ $nc -le $group_ncount_poe ]; do
	    poe_script=$DATA/$VERIF_CASE_STEP/METplus_job_scripts/$group/poe_jobs${nc}
	    chmod 775 $poe_script
	    export MP_PGMMODEL=mpmd
	    export MP_CMDFILE=${poe_script}
	    if [ $machine = WCOSS2 ]; then
	        export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
	        launcher="mpiexec -np ${nproc} -ppn ${nproc} --cpu-bind verbose,depth cfp"
	    elif [ $machine = HERA -o $machine = ORION ]; then
		export SLURM_KILL_BAD_EXIT=0
	        launcher="srun --export=ALL --multi-prog"
	    fi
	    $launcher $MP_CMDFILE
	    nc=$((nc+1))
        done
    else
        while [ $nc -le $group_ncount_job ]; do
	    sh +x $DATA/$VERIF_CASE_STEP/METplus_job_scripts/$group/job${nc}
	    nc=$((nc+1))
        done
    fi
done

# Copy stat files to desired location
if [ $SENDCOM = YES ]; then
    for RUN_DATE_PATH in $DATA/$VERIF_CASE_STEP/METplus_output/$RUN.*; do
	RUN_DATE_DIR=$(echo ${RUN_DATE_PATH##*/})
	for RUN_DATE_SUBDIR_PATH in $DATA/$VERIF_CASE_STEP/METplus_output/$RUN_DATE_DIR/*; do
            RUN_DATE_SUBDIR=$(echo ${RUN_DATE_SUBDIR_PATH##*/})
	    for FILE in $RUN_DATE_SUBDIR_PATH/$VERIF_CASE/*; do
		cp -v $FILE $COMOUT/$RUN_DATE_DIR/$RUN_DATE_SUBDIR/$VERIF_CASE/.
	    done
        done
    done
    for MODEL in $model_list; do
	for MODEL_DATE_PATH in $DATA/$VERIF_CASE_STEP/METplus_output/$MODEL.*; do
	    MODEL_DATE_SUBDIR=$(echo ${MODEL_DATE_PATH##*/})
	    for FILE in $DATA/$VERIF_CASE_STEP/METplus_output/$MODEL_DATE_SUBDIR/*; do
		cp -v $FILE $COMOUT/$MODEL_DATE_SUBDIR/.
	    done
        done
    done
fi

# Send data to archive
if [ $SENDARCH = YES ]; then
    python $USHevs/subseasonal/copy_subseasonal_stat_files.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran copy_subseasonal_stat_files.py"
    echo
fi

# Send data to METviewer AWS server and clean up
if [ $SENDMETVIEWER = YES ]; then
    python $USHevs/subseasonal/subseasonal_load_to_METviewer_AWS.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran subseasonal_load_to_METviewer_AWS.py"
    echo
else
    if [ $KEEPDATA = NO ]; then
	cd $DATAROOTtmp
	rm -rf $DATA
    fi
fi
