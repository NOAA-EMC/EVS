#!/bin/sh
# Program Name: evs_seasonal_stats
# Author(s)/Contact(s): Shannon Shields
# Abstract: Run METplus for seasonal grid-to-grid and grid-to-obs verification to produce stats
# History Log:

set -x

if [ $VERIF_CASE = grid2grid ] ; then
    echo
    echo "===== RUNNING GRID-TO-GRID STATS VERIFICATION  ====="
    export STEP="stats"
    export VERIF_CASE_STEP="grid2grid_stats"
    export VERIF_CASE_STEP_abbrev="g2gstats"
fi

if [ $VERIF_CASE = grid2obs ] ; then
    echo
    echo "===== RUNNING GRID-TO-OBSERVATIONS STATS VERIFICATION  ====="
    export STEP="stats"
    export VERIF_CASE_STEP="grid2obs_stats"
    export VERIF_CASE_STEP_abbrev="g2ostats"
fi

# Set up directories
mkdir -p $VERIF_CASE_STEP
cd $VERIF_CASE_STEP

# Set up domains
if [ $domain = "GLOBAL" ]
then
	export grid=G003
	export poly=
fi

if [ $domain = "NH" ]
then
	export grid=G085
	export poly=
fi

if [ $domain = "SH" ]
then
	export grid=G086
	export poly=
fi

if [ $domain = "CONUS" ]
then
	export grid=G003
	export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Bukovsky_G003_CONUS.nc
fi

if [ $domain = "CCONUS" ]
then
	export grid=G003
	export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Bukovsky_G003_CONUS_Central.nc
fi

if [ $domain = "SCONUS" ]
then
	export grid=G003
	export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Bukovsky_G003_CONUS_South.nc
fi

if [ $domain = "ECONUS" ]
then
	export grid=G003
	export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Bukovsky_G003_CONUS_East.nc
fi

if [ $domain = "WCONUS" ]
then
	export grid=G003
	export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Bukovsky_G003_CONUS_West.nc
fi

if [ $domain = "AK" ]
then
	export grid=G003
	export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Alaska_G003.nc
fi

if [ $domain = "HWI" ]
then
	export grid=G003
	export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/Hawaii_G003.nc
fi

if [ $domain = "40S40N" ]
then
	export grid=G003
	export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_40S_40N.nc
fi

if [ $domain = "Nino" ]
then
	export grid=G003
	export poly=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_Nino1_2.nc, /lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_Nino3.nc, /lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_Nino3_4.nc, /lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks/G003_Nino4.nc

# Check user's configuration file
python $USHevs/seasonal/check_seasonal_config.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran check_seasonal_config.py"
echo

# Set up environment variables for initialization, valid, and forecast hours and source them
python $USHevs/seasonal/set_init_valid_fhr_seasonal_info.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran set_init_valid_fhr_info.py"
echo
. $DATA/$VERIF_CASE_STEP/python_gen_env_vars.sh
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully sourced python_gen_env_vars.sh"
echo

# Link needed data files and set up model information
#mkdir -p data
#python $USHevs/seasonal/get_seasonal_data_files.py
#status=$?
#[[ $status -ne 0 ]] && exit $status
#[[ $status -eq 0 ]] && echo "Successfully ran get_seasonal_data_files.py"
#echo

# Create output directories for METplus
python $USHevs/seasonal/create_METplus_seasonal_output_dirs.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran create_METplus_output_dirs.py"
echo

# Create job scripts to run METplus
python $USHevs/seasonal/create_METplus_seasonal_job_scripts.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran create_METplus_job_scripts.py"

# Run METplus job scripts
chmod u+x metplus_job_scripts/job*
if [ $USE_CFP = YES ]; then
    ncount=$(ls -l  metplus_job_scripts/poe* |wc -l)
    nc=0
    while [ $nc -lt $ncount ]; do
        nc=$((nc+1))
	poe_script=$DATA/$VERIF_CASE_STEP/metplus_job_scripts/poe_jobs${nc}
	chmod 775 $poe_script
	export MP_PGMMODEL=mpmd
	export MP_CMDFILE=${poe_script}
	if [ $machine = WCOSS2 ]; then
            export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
	    launcher="mpiexec -np 128 -ppn 128 --cpu-bind verbose,depth cfp"
	elif [ $machine = HERA -o $machine = ORION ]; then
	    launcher="srun --export=ALL --multi-prog"
	fi
	$launcher $MP_CMDFILE
    done
else
    ncount=$(ls -l  metplus_job_scripts/job* |wc -l)
    nc=0
    while [ $nc -lt $ncount ]; do
	nc=$((nc+1))
	sh +x $DATA/$VERIF_CASE_STEP/metplus_job_scripts/job${nc}
    done
fi

# Copy stat files to desired location
python $USHevs/seasonal/copy_seasonal_stat_files.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran copy_seasonal_stat_files.py"
echo

# Send data to METviewer AWS server and clean up
if [ $SENDMETVIEWER = YES ]; then
    python $USHevs/seasonal/load_to_METviewer_AWS.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran load_to_METviewer_AWS.py"
    echo
else
    if [ $KEEPDATA = NO ]; then
	cd ..
	rm -rf $RUN
    fi
fi
