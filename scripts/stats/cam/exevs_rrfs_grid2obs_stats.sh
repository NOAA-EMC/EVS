#!/bin/bash -e

# =============================================================================
#
# NAME: exevs_rrfs_grid2obs_stats.sh
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Handle all components of an EVS RRFS Grid2Obs - Statistics 
#          job
# DEPENDENCIES: $HOMEevs/jobs/JEVS_CAM_STATS 
#
# =============================================================================

set -x

# Set Basic Environment Variables
export machine=${machine:-"WCOSS2"}
export PYTHONPATH=$USHevs/$COMPONENT:$PYTHONPATH
last_cyc="21"
NEST_LIST="conus ak spc_otlk firewx hi pr subreg"
VERIF_TYPES="raob metar"

# Reformat MET Data
export job_type="reformat"
export njob=1
export run_restart=true
for NEST in $NEST_LIST; do
    export NEST=$NEST
    for VERIF_TYPE in $VERIF_TYPES; do
        export VERIF_TYPE=$VERIF_TYPE
        source $config
        source $USHevs/cam/cam_stats_grid2obs_filter_valid_hours_list.sh

        # Check For Restart Files
        if [ "$run_restart" = true ]; then
            python ${USHevs}/cam/cam_production_restart.py
            export err=$?; err_chk
            export run_restart=false
        fi

        for VHOUR in $VHOUR_LIST; do
            export VHOUR=$VHOUR
            # Check User's Configuration Settings
            python $USHevs/cam/cam_check_settings.py
            export err=$?; err_chk
     
            # Check Availability of Input Data
            python $USHevs/cam/cam_check_input_data.py
            export err=$?; err_chk
     
            # Create Output Directories
            python $USHevs/cam/cam_create_output_dirs.py
            export err=$?; err_chk
    
            # Preprocess Prepbufr Data
            python $USHevs/cam/cam_stats_grid2obs_preprocess_prepbufr.py
            export err=$?; err_chk

            # Create Reformat Job Script 
            python $USHevs/cam/cam_stats_grid2obs_create_job_script.py
            export err=$?; err_chk
            export njob=$((njob+1))
        done
    done
done

# Submit All Mail Messages
if [ "$SENDMAIL" == "YES" ]; then
    if [ ! -z "${MAILTO}" ]; then
        $USHevs/cam/cam_submit_mail_messages.sh
        export err=$?; err_chk
    fi
fi

# Create Reformat POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/cam/cam_stats_grid2obs_create_poe_job_scripts.py
    export err=$?; err_chk
fi

# Create Reformat Working Directories
python $USHevs/cam/cam_create_child_workdirs.py
export err=$?; err_chk

# Run All RRFS grid2obs/stats Reformat Jobs
chmod u+x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/*
ncount_job=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job* |wc -l)
nc=1
if [ $USE_CFP = YES ]; then
    ncount_poe=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/poe* |wc -l)
    while [ $nc -le $ncount_poe ]; do
        poe_script=${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/poe_jobs${nc}
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        if [ $machine = WCOSS2 ]; then
            launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
        elif [$machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
            export SLURM_KILL_BAD_EXIT=0
            launcher="srun --export=ALL --multi-prog"
        else
            err_exit "Cannot submit jobs to scheduler on this machine.  Set USE_CFP=NO and retry."
        fi
        $launcher $MP_CMDFILE
        export err=$?; err_chk
        nc=$((nc+1))
    done
else
    set -x
    while [ $nc -le $ncount_job ]; do
        ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
        export err=$?; err_chk
        nc=$((nc+1))
    done
    set -x
fi

# Copy Reformat Output to Main Directory
for CHILD_DIR in ${DATA}/${VERIF_CASE}/METplus_output/workdirs/${job_type}/*; do
    cp -ruv $CHLD_DIR/* ${DATA}/${VERIF_CASE}/METplus_output/.
    export err=$?; err_chk
done

# Generate MET Data
export job_type="generate"
export njob=1
for NEST in $NEST_LIST; do
    export NEST=$NEST
    for VERIF_TYPE in $VERIF_TYPES; do
        export VERIF_TYPE=$VERIF_TYPE
        source $config
        source $USHevs/cam/cam_stats_grid2obs_filter_valid_hours_list.sh
        for VAR_NAME in $VAR_NAME_LIST; do
            export VAR_NAME=$VAR_NAME
            for VHOUR in $VHOUR_LIST; do
                export VHOUR=$VHOUR
                # Check User's Configuration Settings
                python $USHevs/cam/cam_check_settings.py
                export err=$?; err_chk
         
                # Create Output Directories
                python $USHevs/cam/cam_create_output_dirs.py
                export err=$?; err_chk
         
                # Create Generate Job Script 
                python $USHevs/cam/cam_stats_grid2obs_create_job_script.py
                export err=$?; err_chk
                export njob=$((njob+1))
            done
        done
    done 
done

# Create Generate POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/cam/cam_stats_grid2obs_create_poe_job_scripts.py
    export err=$?; err_chk
fi

# Create Generate Working Directories
python $USHevs/cam/cam_create_child_workdirs.py
export err=$?; err_chk

# Run All RRFS grid2obs/stats Generate Jobs
chmod u+x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/*
ncount_job=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job* |wc -l)
nc=1
if [ $USE_CFP = YES ]; then
    ncount_poe=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/poe* |wc -l)
    while [ $nc -le $ncount_poe ]; do
        poe_script=${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/poe_jobs${nc}
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        if [ $machine = WCOSS2 ]; then
            launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
        elif [$machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
            export SLURM_KILL_BAD_EXIT=0
            launcher="srun --export=ALL --multi-prog"
        else
            err_exit "Cannot submit jobs to scheduler on this machine.  Set USE_CFP=NO and retry."
        fi
        $launcher $MP_CMDFILE
        export err=$?; err_chk
        nc=$((nc+1))
    done
else
    set -x
    while [ $nc -le $ncount_job ]; do
        ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
        export err=$?; err_chk
        nc=$((nc+1))
    done
    set -x
fi

# Copy Generate Output to Main Directory
for CHILD_DIR in ${DATA}/${VERIF_CASE}/METplus_output/workdirs/${job_type}/*; do
    cp -ruv $CHLD_DIR/* ${DATA}/${VERIF_CASE}/METplus_output/.
    export err=$?; err_chk
done

export job_type="gather"
export njob=1
for VERIF_TYPE in $VERIF_TYPES; do
    export VERIF_TYPE=$VERIF_TYPE
    source $config
    source $USHevs/cam/cam_stats_grid2obs_filter_valid_hours_list.sh
    if [[ ! -z $VHOUR_LIST ]]; then
        # Create Output Directories
        python $USHevs/cam/cam_create_output_dirs.py
        export err=$?; err_chk
    
        # Create Gather Job Script
        python $USHevs/cam/cam_stats_grid2obs_create_job_script.py
        export err=$?; err_chk
        export njob=$((njob+1))
    fi
done


# Create Gather POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/cam/cam_stats_grid2obs_create_poe_job_scripts.py
    export err=$?; err_chk
fi

# Create Gather Working Directories
python $USHevs/cam/cam_create_child_workdirs.py
export err=$?; err_chk

# Run All RRFS grid2obs/stats Gather Jobs
chmod u+x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/*
ncount_job=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job* |wc -l)
nc=1
if [ $USE_CFP = YES ]; then
    ncount_poe=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/poe* |wc -l)
    while [ $nc -le $ncount_poe ]; do
        poe_script=${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/poe_jobs${nc}
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        if [ $machine = WCOSS2 ]; then
            launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
        elif [$machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
            export SLURM_KILL_BAD_EXIT=0
            launcher="srun --export=ALL --multi-prog"
        else
            err_exit "Cannot submit jobs to scheduler on this machine.  Set USE_CFP=NO and retry."
        fi
        $launcher $MP_CMDFILE
        export err=$?; err_chk
        nc=$((nc+1))
    done
else
    set -x
    while [ $nc -le $ncount_job ]; do
        ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
        export err=$?; err_chk
        nc=$((nc+1))
    done
    set -x
fi

# Copy Gather Output to Main Directory
for CHILD_DIR in ${DATA}/${VERIF_CASE}/METplus_output/workdirs/${job_type}/*; do
    cp -ruv $CHLD_DIR/* ${DATA}/${VERIF_CASE}/METplus_output/.
    export err=$?; err_chk
done

export job_type="gather2"
export njob=1
export VERIF_TYPE=$VERIF_TYPE
source $config
export VHOUR_LIST="00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23"
if [[ ! -z $VHOUR_LIST ]]; then
    # Create Output Directories
    python $USHevs/cam/cam_create_output_dirs.py
    export err=$?; err_chk

    # Create Gather 2 Job Script
    python $USHevs/cam/cam_stats_grid2obs_create_job_script.py
    export err=$?; err_chk
    export njob=$((njob+1))
fi


# Create Gather 2 POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/cam/cam_stats_grid2obs_create_poe_job_scripts.py
    export err=$?; err_chk
fi

# Create Gather 2 Working Directories
python $USHevs/cam/cam_create_child_workdirs.py
export err=$?; err_chk

# Run All RRFS grid2obs/stats Gather 2 Jobs
chmod u+x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/*
ncount_job=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job* |wc -l)
nc=1
if [ $USE_CFP = YES ]; then
    ncount_poe=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/poe* |wc -l)
    while [ $nc -le $ncount_poe ]; do
        poe_script=${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/poe_jobs${nc}
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        if [ $machine = WCOSS2 ]; then
            launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
        elif [$machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
            export SLURM_KILL_BAD_EXIT=0
            launcher="srun --export=ALL --multi-prog"
        else
            err_exit "Cannot submit jobs to scheduler on this machine.  Set USE_CFP=NO and retry."
        fi
        $launcher $MP_CMDFILE
        export err=$?; err_chk
        nc=$((nc+1))
    done
else
    set -x
    while [ $nc -le $ncount_job ]; do
        ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
        export err=$?; err_chk
        nc=$((nc+1))
    done
    set -x
fi

# Copy Gather 2 Output to Main Directory
for CHILD_DIR in ${DATA}/${VERIF_CASE}/METplus_output/workdirs/${job_type}/*; do
    cp -ruv $CHLD_DIR/* ${DATA}/${VERIF_CASE}/METplus_output/.
    export err=$?; err_chk
done

# Copy files to desired location
#all commands to copy output files into the correct EVS COMOUT directory
if [ $SENDCOM = YES ]; then
    for MODEL_DIR_PATH in $MET_PLUS_OUT/stat_analysis/$MODELNAME*; do
        for FILE in $MODEL_DIR_PATH/*; do
            if [ -s "$FILE" ]; then
                cp -v $FILE $COMOUTsmall/gather_small/.
            fi
        done
    done
fi

# Final Stats Job
if [ "$vhr" -ge "$last_cyc" ]; then
    if [ $SENDCOM = YES ]; then
        export job_type="gather3"
        export njob=1
        source $config
        source $USHevs/cam/cam_stats_grid2obs_filter_valid_hours_list.sh
        # Create Output Directories
        python $USHevs/cam/cam_create_output_dirs.py
        export err=$?; err_chk

        # Create Gather 3 Working Directories
        python $USHevs/cam/cam_create_child_workdirs.py
        export err=$?; err_chk

        # Create Gather 3 Job Script
        python $USHevs/cam/cam_stats_grid2obs_create_job_script.py
        export err=$?; err_chk
        export njob=$((njob+1))

        # Create Gather 3 POE Job Scripts
        if [ $USE_CFP = YES ]; then
            python $USHevs/cam/cam_stats_grid2obs_create_poe_job_scripts.py
            export err=$?; err_chk
        fi

        # Run All NAM Nest grid2obs/stats Gather 3 Jobs
        chmod u+x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/*
        ncount_job=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job* |wc -l)
        nc=1
        if [ $USE_CFP = YES ]; then
            ncount_poe=$(ls -l ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/poe* |wc -l)
            while [ $nc -le $ncount_poe ]; do
                poe_script=${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/poe_jobs${nc}
                chmod 775 $poe_script
                export MP_PGMMODEL=mpmd
                export MP_CMDFILE=${poe_script}
                if [ $machine = WCOSS2 ]; then
                    launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
                elif [ $machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
                    export SLURM_KILL_BAD_EXIT=0
                    launcher="srun --export=ALL --multi-prog"
                else
                    err_exit "Cannot submit jobs to scheduler on this machine.  Set USE_CFP=NO and retry."
                fi
                $launcher $MP_CMDFILE
                export err=$?; err_chk
                nc=$((nc+1))
            done
        else
            set -x
            while [ $nc -le $ncount_job ]; do
                ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
                export err=$?; err_chk
                nc=$((nc+1))
            done
            set -x
        fi

        # Copy Gather 3 Output to Main Directory
        for CHILD_DIR in ${DATA}/${VERIF_CASE}/METplus_output/workdirs/${job_type}/*; do
            cp -ruv $CHLD_DIR/* ${DATA}/${VERIF_CASE}/METplus_output/.
            export err=$?; err_chk
        done
    fi
fi
