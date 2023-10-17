#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 


###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'
############################################################

>run_gather_all_poe.sh

modnam=sref
verify=$1
export vday=$VDATE


MODEL=`echo $modnam | tr '[a-z]' '[A-Z]'`


>run_gather_${verify}.sh

    echo  "export output_base=${WORK}/gather" >> run_gather_${verify}.sh 
    echo  "export verify=$verify" >> run_gather_${verify}.sh 

    echo  "export vbeg=03" >> run_gather_${verify}.sh
    echo  "export vend=21" >> run_gather_${verify}.sh
    echo  "export valid_increment=21600" >>  run_gather_${verify}.sh

    echo  "export model=$modnam" >> run_gather_${verify}.sh
    echo  "export MODEL=${MODEL}" >> run_gather_${verify}.sh
    echo  "export stat_file_dir=${COMOUTsmall}" >> run_gather_${verify}.sh
    #echo  "export stat_file_dir=${WORK}/${verify}/stat" >> run_gather_${verify}.sh
    echo  "export gather_output_dir=${WORK}/gather " >> run_gather_${verify}.sh

    if [ $verify = grid2obs ] ; then   
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/StatAnlysis_fcstSREF_obsPREPBUFR_GatherByDay.conf " >> run_gather_${verify}.sh
    elif [ $verify = precip ] ; then
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/StatAnlysis_fcstSREF_obsCCPA_GatherByDay.conf " >> run_gather_${verify}.sh
    fi

    if [ $SENDCOM = 'YES' ]; then
   echo "cp ${WORK}/gather/${vday}/${modnam}_${verify}_${vday}.stat  $COMOUTfinal/evs.stats.${model}.${verify}.v${vday}.stat">>run_gather_${verify}.sh
    fi
  chmod +x run_gather_${verify}.sh

  echo "${DATA}/run_gather_${verify}.sh" >> run_gather_all_poe.sh 




chmod +x run_gather_all_poe.sh

 ${DATA}/run_gather_all_poe.sh
