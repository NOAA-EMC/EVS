#!/bin/ksh
#*************************************************************
# Purpose: Run aigefs_atmos_prep job
#          1. Build sub-task scripts 
#          2. Run the sub-task scripts
#
# Updated: 10/03/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#*************************************************************            
set -x 

#*****************************************************************
# Check if all prep sub-tasks are completed in the previous runs
if [ ! -s $COMOUTcompleted/prep_subtasks_completed ] ; then
mkdir -p $WORK/completed
#*****************************************************************

#*************************************************************
# Build 5 poe scripts to collect their sub-tasks, respectively
#*************************************************************
>run_get_all_gens_atmos_poe.sh
>run_get_all_gens_apcp24h_poe.sh

for model in gefs aigefs ; do 
  if [ $model = gefs ] ; then
    if [ $get_gefs = yes ] ; then	   
      for ihour in 00 06 12 18 ; do
       for fhr_range in range1 range2 range3 range4 range5 range6 range7 range8 range9 range10 range11 range12 range13 range14 range15 range16; do	     
	#*******************************************
	# Build sub-task scripts for GEFS atmosphere
	#*******************************************       
	>get_data_${model}_${ihour}_${fhr_range}.sh
	if [ $fhr_range = range1 ] ; then
	  fhr_beg=00
          fhr_end=24
        elif [ $fhr_range = range2 ] ; then
          fhr_beg=30
          fhr_end=48
        elif [ $fhr_range = range3 ] ; then
          fhr_beg=54
          fhr_end=72
	elif [ $fhr_range = range4 ] ; then
	  fhr_beg=78
	  fhr_end=96
	elif [ $fhr_range = range5 ] ; then
          fhr_beg=102
          fhr_end=120
        elif [ $fhr_range = range6 ] ; then
          fhr_beg=126
          fhr_end=144
        elif [ $fhr_range = range7 ] ; then
          fhr_beg=150
          fhr_end=168
        elif [ $fhr_range = range8 ] ; then
          fhr_beg=174
          fhr_end=192
        elif [ $fhr_range = range9 ] ; then
          fhr_beg=198
          fhr_end=216
        elif [ $fhr_range = range10 ] ; then
          fhr_beg=222
          fhr_end=240
        elif [ $fhr_range = range11 ] ; then
          fhr_beg=246
          fhr_end=264
        elif [ $fhr_range = range12 ] ; then
          fhr_beg=270
          fhr_end=288
        elif [ $fhr_range = range13 ] ; then
          fhr_beg=294
          fhr_end=312
        elif [ $fhr_range = range14 ] ; then
          fhr_beg=318
          fhr_end=336
        elif [ $fhr_range = range15 ] ; then
          fhr_beg=342
          fhr_end=360
        elif [ $fhr_range = range16 ] ; then
          fhr_beg=366
          fhr_end=384
        fi

	# Check for restart: if this task has been completed in the previous run, then skip it
	if [ ! -e $COMOUTcompleted/get_data_${model}_${ihour}_${fhr_range}.completed ] ; then
          echo "$USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh $model $ihour $fhr_beg $fhr_end" >> get_data_${model}_${ihour}_${fhr_range}.sh

          # Indicate this task is completed for restart
	  echo ">$WORK/completed/get_data_${model}_${ihour}_${fhr_range}.completed" >> get_data_${model}_${ihour}_${fhr_range}.sh 
	  echo "echo "get_data_${model}_${ihour}_${fhr_range} task is completed" >> $WORK/completed/get_data_${model}_${ihour}_${fhr_range}.completed" >> get_data_${model}_${ihour}_${fhr_range}.sh
	  echo "if [ $SENDCOM = YES ] ; then" >> get_data_${model}_${ihour}_${fhr_range}.sh
	  echo "  cp -f $WORK/completed/get_data_${model}_${ihour}_${fhr_range}.completed $COMOUTcompleted" >> get_data_${model}_${ihour}_${fhr_range}.sh
	  echo "fi" >> get_data_${model}_${ihour}_${fhr_range}.sh

          chmod +x get_data_${model}_${ihour}_${fhr_range}.sh
	  echo "${DATA}/get_data_${model}_${ihour}_${fhr_range}.sh" >> run_get_all_gens_atmos_poe.sh
	fi
       done
      done
    fi

    if [ $get_gefs_apcp24h = yes ] ; then
      for ihour in 00 12 ; do
	#*****************************************
        # Build sub-task scripts for GEFS 24h APCP
	#*****************************************
        >get_data_${model}_${ihour}_apcp24h.sh
        # Check for restart: if this task has been completed in the previous run, then skip it
	if [ ! -e $COMOUTcompleted/get_data_${model}_${ihour}_apcp24h.completed ] ; then
          echo "$USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh ${model}_apcp24h $ihour 0 384" >> get_data_${model}_${ihour}_apcp24h.sh

          # Indicate this task is completed for restart
	  echo ">$WORK/completed/get_data_${model}_${ihour}_apcp24h.completed" >> get_data_${model}_${ihour}_apcp24h.sh
	  echo "echo "get_data_${model}_${ihour}_apcp24h task is completed" >> $WORK/completed/get_data_${model}_${ihour}_apcp24h.completed" >> get_data_${model}_${ihour}_apcp24h.sh
	  echo "if [ $SENDCOM = YES ] ; then" >> get_data_${model}_${ihour}_apcp24h.sh
	  echo "  cp -f $WORK/completed/get_data_${model}_${ihour}_apcp24h.completed $COMOUTcompleted" >> get_data_${model}_${ihour}_apcp24h.sh
	  echo "fi" >> get_data_${model}_${ihour}_apcp24h.sh

	  chmod +x get_data_${model}_${ihour}_apcp24h.sh
	  echo "${DATA}/get_data_${model}_${ihour}_apcp24h.sh" >> run_get_all_gens_apcp24h_poe.sh
	fi
      done	
    fi			

  elif [ $model = aigefs ] ; then  
    if [ $get_aigefs = yes ] ; then 
      for ihour in 00 06 12 18 ; do
       for fhr_range in range1 range2 range3 range4 range5 range6 range7 range8 ; do
	#*******************************************
	# Build sub-task scripts for AIGEFS atmosphere
	#*******************************************
	>get_data_${model}_${ihour}_${fhr_range}.sh
	if [ $fhr_range = range1 ] ; then
          fhr_beg=00
	  fhr_end=48
        elif [ $fhr_range = range2 ] ; then
          fhr_beg=54
	  fhr_end=96
        elif [ $fhr_range = range3 ] ; then
          fhr_beg=102
          fhr_end=144
        elif [ $fhr_range = range4 ] ; then
          fhr_beg=150
          fhr_end=192
        elif [ $fhr_range = range5 ] ; then
          fhr_beg=198
          fhr_end=240
        elif [ $fhr_range = range6 ] ; then
          fhr_beg=246
          fhr_end=288
        elif [ $fhr_range = range7 ] ; then
          fhr_beg=294
          fhr_end=336
        elif [ $fhr_range = range8 ] ; then
          fhr_beg=342
          fhr_end=384
        fi

	# Check for restart: if this task has been completed in the previous run, then skip it
	if [ ! -e $COMOUTcompleted/get_data_${model}_${ihour}_${fhr_range}.completed ] ; then
          echo "$USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh $model $ihour $fhr_beg $fhr_end" >> get_data_${model}_${ihour}_${fhr_range}.sh

          # Indicate this task is completed for restart
	  echo ">$WORK/completed/get_data_${model}_${ihour}_${fhr_range}.completed" >> get_data_${model}_${ihour}_${fhr_range}.sh
	  echo "echo "get_data_${model}_${ihour}_${fhr_range} task is completed" >> $WORK/completed/get_data_${model}_${ihour}_${fhr_range}.completed" >> get_data_${model}_${ihour}_${fhr_range}.sh
	  echo "if [ $SENDCOM = YES ] ; then" >> get_data_${model}_${ihour}_${fhr_range}.sh
	  echo "  cp -f $WORK/completed/get_data_${model}_${ihour}_${fhr_range}.completed $COMOUTcompleted" >> get_data_${model}_${ihour}_${fhr_range}.sh
	  echo "fi" >> get_data_${model}_${ihour}_${fhr_range}.sh

	  chmod +x get_data_${model}_${ihour}_${fhr_range}.sh
	  echo "${DATA}/get_data_${model}_${ihour}_${fhr_range}.sh" >> run_get_all_gens_atmos_poe.sh
	fi
       done
      done
    fi 

    if [ $get_aigefs_apcp24h = yes ] ; then
      for ihour in 00 12 ; do
	#****************************************
	# Build sub-task scripts for CMCE 24h APCP
	#****************************************
	>get_data_${model}_${ihour}_apcp24h.sh
        # Check for restart: if this task has been completed in the previous run, then skip it
	if [ ! -e $COMOUTcompleted/get_data_${model}_${ihour}_apcp24h.completed ] ; then
	  echo "$USHevs/${COMPONENT}/evs_get_gens_${RUN}_data.sh ${model}_apcp24h $ihour 0 384" >> get_data_${model}_${ihour}_apcp24h.sh

          # Indicate this task is completed for restart
	  echo ">$WORK/completed/get_data_${model}_${ihour}_apcp24h.completed" >> get_data_${model}_${ihour}_apcp24h.sh
	  echo "echo "get_data_${model}_${ihour}_apcp24h task is completed" >> $WORK/completed/get_data_${model}_${ihour}_apcp24h.completed" >> get_data_${model}_${ihour}_apcp24h.sh
	  echo "if [ $SENDCOM = YES ] ; then" >> get_data_${model}_${ihour}_apcp24h.sh
	  echo "  cp -f $WORK/completed/get_data_${model}_${ihour}_apcp24h.completed $COMOUTcompleted" >> get_data_${model}_${ihour}_apcp24h.sh
	  echo "fi" >> get_data_${model}_${ihour}_apcp24h.sh

	  chmod +x get_data_${model}_${ihour}_apcp24h.sh
	  echo "${DATA}/get_data_${model}_${ihour}_apcp24h.sh" >> run_get_all_gens_apcp24h_poe.sh
	fi
      done
    fi

  else
    echo "WARNING: wrong model: $model"
  fi

done # end of model loop


#*************************************************
# Run 5 poe scripts in MPI parallel or in sequence
#*************************************************  
if [ $run_mpi = yes ] ; then

  if [ -s run_get_all_gens_atmos_poe.sh ] ; then
    chmod +x run_get_all_gens_atmos_poe.sh 
    mpiexec -n 96 -ppn 48 --cpu-bind verbose,core cfp ${DATA}/run_get_all_gens_atmos_poe.sh
    export err=$?; err_chk
  fi
 
  #*************************************************************************************
  # After the above poe scripts are finished, following non-mpi parallel jobs can be run
  #*************************************************************************************
  if [ -s run_get_all_gens_apcp24h_poe.sh ] ; then
    chmod +x run_get_all_gens_apcp24h_poe.sh
    ${DATA}/run_get_all_gens_apcp24h_poe.sh
    export err=$?; err_chk
  fi

else

  if [ -s run_get_all_gens_atmos_poe.sh ] ; then
    chmod +x run_get_all_gens_atmos_poe.sh 
    ${DATA}/run_get_all_gens_atmos_poe.sh
    export err=$?; err_chk
  fi

  if [ -s run_get_all_gens_apcp24h_poe.sh ] ; then
    chmod +x run_get_all_gens_apcp24h_poe.sh
    ${DATA}/run_get_all_gens_apcp24h_poe.sh
    export err=$?; err_chk
  fi

fi

# Indicate all sub-tasks are completed
>$WORK/completed/prep_subtasks_completed
echo "All prep sub-tasks are completed" >> $WORK/completed/prep_subtasks_completed

if [ $SENDCOM = YES ] ; then
  cp -f $WORK/completed/prep_subtasks_completed $COMOUTcompleted
fi
           
fi # end of check restart for all sub-tasks
