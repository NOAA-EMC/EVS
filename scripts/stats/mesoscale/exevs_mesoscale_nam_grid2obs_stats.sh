#!/bin/sh
###############################################################################
# Name of Script: exevs_mesoscale_nam_grid2obs_stats.sh 
# CONTRIBUTOR(S): RS, roshan.shrestha@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# Purpose of Script: This script generates grid-to-observations
#                    verification statistics using METplus for the
#                    atmospheric component of NAM models
# Log history:
###############################################################################

set -x
  export machine=${machine:-"WCOSS2"}
  export VERIF_CASE_STEP_abbrev="g2os"
  export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH


# Set run mode
  export evs_run_mode=$evs_run_mode

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
  
# Set Basic Environment Variables
  last_vhr=21
  NEST_LIST="namer conus ak spc_otlk subreg conusp"
  VERIF_TYPES="raob metar"

echo "*****************************"
echo "Reformat setup begin"
echo "*****************************"

# Reformat MET Data
  export job_type="reformat"
  export njob=1
  for NEST in $NEST_LIST; do
     export NEST=$NEST
     for VERIF_TYPE in $VERIF_TYPES; do
        export VERIF_TYPE=$VERIF_TYPE
        export evs_run_mode=$evs_run_mode
        source $config
        
        if [ ${#VAR_NAME_LIST} -lt 1 ]; then
           continue
        fi
      # Check for restart files reformat
        echo " Check for restart files reformat begin"
        if [ $evs_run_mode = production ]; then
           ${USHevs}/mesoscale/mesoscale_stats_g2o_production_restart.sh
	   export err=$?; err_chk
        fi
        echo " Check for restart files reformat done"
        
        for VHOUR in $VHOUR_LIST; do
           export VHOUR=$VHOUR
         # Check User's Configuration Settings
           python $USHevs/mesoscale/mesoscale_check_settings.py
           export err=$?; err_chk
           
         # Check for data files
           python $USHevs/mesoscale/mesoscale_check_input_data.py
           export err=$?; err_chk
           
         # Create Output Directories	    
           python $USHevs/mesoscale/mesoscale_create_output_dirs.py
           export err=$?; err_chk
           
         # Create Reformat Job Script
           python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_job_script.py
           export err=$?; err_chk
           
           export njob=$((njob+1))
           echo "Done $VHOUR"
        done
        echo "Done $VERIF_TYPE"
     done
     echo "Done $NEST"
  done

# Create Reformat POE Job Scripts
  if [ $USE_CFP = YES ]; then
     python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_poe_job_scripts.py
     export err=$?; err_chk
  fi

echo "*****************************"
echo "Reformat jobs begin"
echo "*****************************"

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
           nselect=$(cat $PBS_NODEFILE | wc -l)
           nnp=$(($nselect * $nproc))
           launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,core cfp"
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
        sh +x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
        nc=$((nc+1))
     done
  fi

echo "*****************************"
echo "Reformat jobs done"
echo "*****************************"

# Generate MET Data
  export job_type="generate"
  export njob=1
  for NEST in $NEST_LIST; do
     export NEST=$NEST
     for VERIF_TYPE in $VERIF_TYPES; do
        export VERIF_TYPE=$VERIF_TYPE
        export evs_run_mode=$evs_run_mode
        source $config
        
        if [ ${#VAR_NAME_LIST} -lt 1 ]; then
           continue
        fi
          
        for VAR_NAME in $VAR_NAME_LIST; do
           export VAR_NAME=$VAR_NAME
	   for VHOUR in $VHOUR_LIST; do
              export VHOUR=$VHOUR
              
	    # Check User's Configuration Settings
              python $USHevs/mesoscale/mesoscale_check_settings.py
              export err=$?; err_chk
              
            # Create Output Directories
              python $USHevs/mesoscale/mesoscale_create_output_dirs.py
              export err=$?; err_chk
              
            # Create Generate Job Script
              python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_job_script.py
              export err=$?; err_chk
              
              export njob=$((njob+1))
           done
        done
     done 
  done

# Create Generate POE Job Scripts
  if [ $USE_CFP = YES ]; then
     python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_poe_job_scripts.py
     export err=$?; err_chk
  fi

echo "*****************************"
echo "Generate jobs begin"
echo "*****************************"

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
           nselect=$(cat $PBS_NODEFILE | wc -l)
           nnp=$(($nselect * $nproc))
           launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,core cfp"
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
        sh +x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
        nc=$((nc+1))
     done
  fi

echo "*****************************"
echo "Generate jobs done"
echo "*****************************"

  export job_type="gather"
  export njob=1
  for VERIF_TYPE in $VERIF_TYPES; do
     export VERIF_TYPE=$VERIF_TYPE
     export evs_run_mode=$evs_run_mode
     source $config
     
     if [ ${#VAR_NAME_LIST} -lt 1 ]; then
        continue
     fi
     
   # Create Output Directories
     python $USHevs/mesoscale/mesoscale_create_output_dirs.py
     export err=$?; err_chk
     
   # Create Gather Job Script
     python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_job_script.py
     export err=$?; err_chk
     
     export njob=$((njob+1))
  done

# Create Gather POE Job Scripts
  if [ $USE_CFP = YES ]; then
     python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_poe_job_scripts.py
     export err=$?; err_chk
  fi

echo "*****************************"
echo "Gather jobs begin"
echo "*****************************"

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
           nselect=$(cat $PBS_NODEFILE | wc -l)
           nnp=$(($nselect * $nproc))
           launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,core cfp"
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
        sh +x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
	nc=$((nc+1))
     done
  fi

echo "*****************************"
echo "Gather jobs done"
echo "*****************************"

# Copy stat output files to EVS COMOUTsmall directory
  if [ $SENDCOM = YES ]; then
     for VERIF_TYPE in $VERIF_TYPES;do
        for MODEL_DIR_PATH in $MET_PLUS_OUT/$VERIF_TYPE/point_stat/$MODELNAME*; do
           if [ -d $MODEL_DIR_PATH ]; then
              MODEL_DIR=$(echo ${MODEL_DIR_PATH##*/})
              mkdir -p $COMOUTsmall
              for FILE in $MODEL_DIR_PATH/*; do
                 cp -v $FILE $COMOUTsmall/.
              done
           fi
        done
    done
  fi

echo "*****************************"
echo "Gather3 jobs begin"
echo "*****************************"

# Final Stats Job
  export job_type="gather3"
  export njob=1
  export evs_run_mode=$evs_run_mode
  source $config
  
# Create Output Directories
  python $USHevs/mesoscale/mesoscale_create_output_dirs.py
  export err=$?; err_chk
  
# Create Gather 3 Job Script
  python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_job_script.py
  export err=$?; err_chk
  
  export njob=$((njob+1))
  
# Create Gather 3 POE Job Scripts
  if [ $USE_CFP = YES ]; then
     python $USHevs/mesoscale/mesoscale_stats_grid2obs_create_poe_job_scripts.py
     export err=$?; err_chk
  fi
  
# Run All NAM grid2obs/stats Gather 3 Jobs
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
           nselect=$(cat $PBS_NODEFILE | wc -l)
           nnp=$(($nselect * $nproc))
           launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,core cfp"
        elif [ $machine = HERA -o $machine = ORION -o $machine = S4 -o $machine = JET ]; then
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
        sh +x ${DATA}/${VERIF_CASE}/${STEP}/METplus_job_scripts/${job_type}/job${nc}
        nc=$((nc+1))
     done
  fi

echo "*****************************"
echo "Gather3 jobs done"
echo "*****************************"

# Copy output files into the correct EVS COMOUT directory
  if [ $SENDCOM = YES ]; then
     for MODEL_DIR_PATH in $MET_PLUS_OUT/gather_small/stat_analysis/$MODELNAME*; do
        MODEL_DIR=$(echo ${MODEL_DIR_PATH##*/})
        mkdir -p $COMOUT/$MODEL_DIR
        for FILE in $MODEL_DIR_PATH/*; do
           if [ -s $FILE ]; then
              cp -v $FILE $COMOUT/$MODEL_DIR/.
	   fi
        done
     done
   fi

echo "******************************"
echo "Begin to print METplus Log files "
  cat $DATA/grid2obs/METplus_output/*/*/pb2nc/logs/*
echo "End to print METplus Log files "

