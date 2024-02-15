#!/bin/ksh
#*************************************************************************************************
# Purpose:  Run NAEFS  prep job
#           1. Generate sub-tasks to run $USHevs/global_ens/evs_get_naefs_atmos_data.sh
#           2. Run the sub-tasks
#
# Last updated 11/15/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#************************************************************************************************

set -x 

#*************************************************
# Build a poe script to collect sub-tasks
# ************************************************
>run_get_all_naefs_atmos_poe.sh

if [ $get_model_bc = yes ] ; then
 for model in gefs_bc cmce_bc ; do 
      for ihour in 00 12 ; do
       for fhr_range in range1 range2 range3 range4 range5 range6 range7 range8 ; do
	#**********************************
	# Build sub-task scripts
	# ********************************
	>get_data_${model}_${ihour}_${fhr_range}.sh
	 if [ $fhr_range = range1 ] ; then
           fhr_beg=00
	   fhr_end=48
         elif [ $fhr_range = range2 ] ; then
	   fhr_beg=60
	   fhr_end=96
        elif [ $fhr_range = range3 ] ; then
          fhr_beg=108
          fhr_end=144
        elif [ $fhr_range = range4 ] ; then
          fhr_beg=156
          fhr_end=192
        elif [ $fhr_range = range5 ] ; then
          fhr_beg=204
          fhr_end=240
        elif [ $fhr_range = range6 ] ; then
          fhr_beg=252
          fhr_end=288
        elif [ $fhr_range = range7 ] ; then
          fhr_beg=300
          fhr_end=336
        elif [ $fhr_range = range8 ] ; then
          fhr_beg=348
          fhr_end=384
         fi
         echo "$USHevs/global_ens/evs_get_naefs_atmos_data.sh $model $ihour $fhr_beg $fhr_end" >> get_data_${model}_${ihour}_${fhr_range}.sh
         chmod +x get_data_${model}_${ihour}_${fhr_range}.sh
         echo "${DATA}/get_data_${model}_${ihour}_${fhr_range}.sh" >> run_get_all_naefs_atmos_poe.sh
       done
      done
 done #end of model
fi

if [ $get_gefs_bc_apcp24h = yes ] ; then
 for model in gefs_bc ; do
  for ihour in 00 12 ; do
    >get_data_${model}_${ihour}_apcp24h.sh
    echo "$USHevs/global_ens/evs_get_naefs_atmos_data.sh ${model}_apcp24h $ihour 0 384" >> get_data_${model}_${ihour}_apcp24h.sh
    chmod +x get_data_${model}_${ihour}_apcp24h.sh
    echo "${DATA}/get_data_${model}_${ihour}_apcp24h.sh" >> run_get_all_naefs_atmos_poe.sh
  done
 done
fi

#*****************************************
# Run poe script
# ***************************************
if [ $run_mpi = yes ] ; then
 if [ -s run_get_all_naefs_atmos_poe.sh ] ; then
   chmod +x run_get_all_naefs_atmos_poe.sh 
   mpiexec  -n 34 -ppn 34 --cpu-bind verbose,depth cfp  ${DATA}/run_get_all_naefs_atmos_poe.sh
   export err=$?; err_chk
 fi
else
 if [ -s run_get_all_naefs_atmos_poe.sh ] ; then
   chmod +x run_get_all_naefs_atmos_poe.sh 
   ${DATA}/run_get_all_naefs_atmos_poe.sh
   export err=$?; err_chk
 fi
fi 
