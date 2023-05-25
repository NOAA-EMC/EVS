#!/bin/sh
###############################################################################
# Name of Script: exevs_nam_grid2obs_stats.sh 
# CONTRIBUTOR(S): RS, roshan.shrestha@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# Purpose of Script: This script generates grid-to-observations
#                    verification statistics using METplus for the
#                    atmospheric component of NAM models
# Log history:
###############################################################################

set -x

  export VERIF_CASE_STEP_abbrev="g2os"
  
# Set run mode
  if [ $RUN_ENVIR = nco ]; then
      export evs_run_mode="production"
      source $config
  else
      export evs_run_mode=$evs_run_mode
  fi
  echo "RUN MODE:$evs_run_mode"
  
# Make directory
  mkdir -p ${VERIF_CASE}_${STEP}
  mkdir -p $DATA/logs
  mkdir -p $DATA/stat
 
# Set env  
  export OBSDIR=OBS
  export fcstmax=84
  
  export model1=`echo $MODELNAME | tr a-z A-Z`
  export model0=`echo $MODELNAME | tr A-Z a-z`
  echo $model1
  
  for WVAR in $VAR_NAME_LISTJ; do
	  if [ $WVAR = SBCAPE ] || [ $WVAR = MLCAPE ] || [ $WVAR = HPBL ] || \
	       [ $WVAR = TMP2m ] || [ $WVAR = DPT2m ] || [ $WVAR = RH2m ] || \
	       [ $WVAR = PRESsl ] || [ $WVAR = UGRD_VGRD10m ] || \
	       [ $WVAR = UGRD10m ] || [ $WVAR = VGRD10m ] || [ $WVAR = WIND ] || \
               [ $WVAR = GUST ] || [ $WVAR = VIS ] || [ $WVAR = CEIL ]  ; then
		  Testdev=yes
# SBCAPE MLCAPE HPBL TMP2m DPT2m RH2m PRESsl UGRD_VGRD10m UGRD10m VGRD10m WIND GUST VIS CEIL
	  else
		  Testdev=no
	  fi
	  if [ $Testdev = yes ]; then
		  # New dev works here
		  export VAR_NAME=${WVAR}
######################################################################################################
# Set Basic Environment Variables
NEST_LIST="conus ak spc_otlk subreg"
# NEST_LIST="conus ak spc_otlk"
VERIF_TYPES="raob metar"

# Reformat MET Data
export job_type="reformat"
export njob=1
for NEST in $NEST_LIST; do
	export NEST=$NEST
	for VERIF_TYPE in $VERIF_TYPES; do
		export VERIF_TYPE=$VERIF_TYPE
		if [ $RUN_ENVIR = nco ]; then
			export evs_run_mode="production"
			source $config
			source $USHevs/mesoscale/mesoscale_stats_grid2obs_filter_valid_hours_list.sh
		else
			export evs_run_mode=$evs_run_mode
			source $config
			source $USHevs/mesoscale/mesoscale_stats_grid2obs_filter_valid_hours_list.sh
		fi
		echo "RUN MODE: $evs_run_mode"
		for VHOUR in $VHOUR_LIST; do
			export VHOUR=$VHOUR
            # Check User's Configuration Settings
            python $USHevs/mesoscale/mesoscale_check_settings.py
            status=$?
            [[ $status -ne 0 ]] && exit $status
            [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_check_settings.py ($job_type)"
            echo

            # Create Output Directories	    
            python $USHevs/mesoscale/mesoscale_create_output_dirs.py
	    status=$?
	    [[ $status -ne 0 ]] && exit $status
	    [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_create_output_dirs.py ($job_type)"

            # Create Reformat Job Script
            python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_job_script.py
            status=$?
            [[ $status -ne 0 ]] && exit $status
            [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_stats_grid2obs_create_job_script.py ($job_type)"
            export njob=$((njob+1))
        done
    done
done

# Create Reformat POE Job Scripts
if [ $USE_CFP = YES ]; then
	python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_poe_job_scripts.py
	status=$?
	[[ $status -ne 0 ]] && exit $status
	[[ $status -eq 0 ]] && echo "Successfully ran mesoscale_stats_grid2obs_create_poe_job_scripts.py ($job_type)"
fi


echo "*****************************
echo "Reformat jobs begin"
date
echo "*****************************



# Run All NAM grid2obs/stats Reformat Jobs
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
			export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
			launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
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
		sh +x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
		nc=$((nc+1))
	done
fi

echo "*****************************
echo "Reformat jobs done"
date
echo "*****************************


# Generate MET Data
export job_type="generate"
export njob=1
for NEST in $NEST_LIST; do
	export NEST=$NEST
	for VERIF_TYPE in $VERIF_TYPES; do
		export VERIF_TYPE=$VERIF_TYPE
		if [ $RUN_ENVIR = nco ]; then
			export evs_run_mode="production"
			source $config
		else
			export evs_run_mode=$evs_run_mode
			source $config
		fi
		for VAR_NAME in $VAR_NAME_LIST; do
			export VAR_NAME=$VAR_NAME
			for VHOUR in $VHOUR_LIST; do
				export VHOUR=$VHOUR
                # Check User's Configuration Settings
                python $USHevs/mesoscale/mesoscale_check_settings.py
                status=$?
                [[ $status -ne 0 ]] && exit $status
                [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_check_settings.py ($job_type)"
                echo

               # Create Output Directories
               python $USHevs/mesoscale/mesoscale_create_output_dirs.py
                status=$?
                 [[ $status -ne 0 ]] && exit $status
                 [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_create_output_dirs.py ($job_type)"

                # Create Generate Job Script
                python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_job_script.py
                status=$?
                [[ $status -ne 0 ]] && exit $status
                [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_stats_grid2obs_create_job_script.py ($job_type)"
                export njob=$((njob+1))
            done
        done
    done 
done

# Create Generate POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_poe_job_scripts.py
        status=$?
	    [[ $status -ne 0 ]] && exit $status
    	    [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_stats_grid2obs_create_poe_job_scripts.py ($job_type)"
fi


echo "*****************************
echo "Generate jobs begin"
date
echo "*****************************

# Run All NAM grid2obs/stats Generate Jobs
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
			export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
			launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
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
		sh +x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
		nc=$((nc+1))
	done
fi


echo "*****************************
echo "Generate jobs done"
date 
echo "*****************************

export job_type="gather"
export njob=1
for VERIF_TYPE in $VERIF_TYPES; do
	export VERIF_TYPE=$VERIF_TYPE
	if [ $RUN_ENVIR = nco ]; then
		export evs_run_mode="production"
		source $config
	else
		export evs_run_mode=$evs_run_mode
		source $config
	fi
    # Create Output Directories
    python $USHevs/mesoscale/mesoscale_create_output_dirs.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_create_output_dirs.py ($job_type)"
    
    # Create Gather Job Script
    python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_job_script.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_stats_grid2obs_create_job_script.py ($job_type)"
    export njob=$((njob+1))
done


# Create Gather POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_poe_job_scripts.py
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_stats_grid2obs_create_poe_job_scripts.py ($job_type)"
fi


echo "*****************************
echo "Gather jobs begin"
date 
echo "*****************************


# Run All NAM grid2obs/stats Gather Jobs
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
			export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
			launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
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
		sh +x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
		nc=$((nc+1))
	done
fi
 
echo "*****************************
echo "Gather jobs done"
date 
echo "*****************************

export job_type="gather2"
export njob=1
if [ $RUN_ENVIR = nco ]; then
	export evs_run_mode="production"
	source $config
else
	export evs_run_mode=$evs_run_mode
	source $config
fi

# Create Output Directories
python $USHevs/mesoscale/mesoscale_create_output_dirs.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran mesoscale_create_output_dirs.py ($job_type)"

# Create Gather 2 Job Script
python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_job_script.py
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran mesoscale_stats_grid2obs_create_job_script.py ($job_type)"
export njob=$((njob+1))

# Create Gather 2 POE Job Scripts
if [ $USE_CFP = YES ]; then
    python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_poe_job_scripts.py
        status=$?
	    [[ $status -ne 0 ]] && exit $status
	        [[ $status -eq 0 ]] && echo "Successfully ran mesoscale_stats_grid2obs_create_poe_job_scripts.py ($job_type)"
fi


echo "*****************************
echo "Gather2 jobs begin"
date 
echo "*****************************

# Run All NAM grid2obs/stats Gather 2 Jobs
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
			export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
			launcher="mpiexec -np $nproc -ppn $nproc --cpu-bind verbose,depth cfp"
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
		sh +x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
		nc=$((nc+1))
	done
fi

echo "*****************************
echo "Gather2 jobs done"
date 
echo "*****************************












######################################################################################################
	  else
### Already done VV
    source $config
    # select var to work on
    export VAR_NAME=${WVAR}
    # Verification Var
    source ${USHevs}/mesoscale/run_var_${model0}.sh
  
    for VHOUR in $VHOUR_LIST; do
      export VHOUR=$VHOUR
      cyc=$VHOUR
      
      if [ $cyc = 00 ] || [ $cyc = 06 ] || [ $cyc = 12 ] || [ $cyc = 18 ];  then
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PB2NC_obsRAOB.conf 
        # export err=$?; err_chk
  
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstMESOSCALE_obsRAOB.conf
        # export err=$?; err_chk
  
      fi
      
      if [ $cyc = 23 ];   then
        mkdir -p $COMOUTfinal
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstMESOSCALE_obsRAOB_GatherByDay.conf 
  
      fi
    done
### Already done ^^
	  fi
  done
  
  # Copy output files into the correct EVS COMOUT directory
    if [ $SENDCOM = YES ]; then
      for MODEL_DIR_PATH in $MET_PLUS_OUT/gather_small/stat_analysis/$MODELNAME*; do
        MODEL_DIR=$(echo ${MODEL_DIR_PATH##*/})
        mkdir -p $COMOUT/$MODEL_DIR
        for FILE in $MODEL_DIR_PATH/*; do
          cp -v $FILE $COMOUT/$MODEL_DIR/.
        done
      done
      for MODEL_DIR_PATH in $MET_PLUS_OUT/raob/point_stat/$MODELNAME*; do
        MODEL_DIR=$(echo ${MODEL_DIR_PATH##*/})
        mkdir -p $COMOUTsmall/$MODEL_DIR
        for FILE in $MODEL_DIR_PATH/*; do
          cp -v $FILE $COMOUTsmall/$MODEL_DIR/.
        done
      done
    fi
  
exit
