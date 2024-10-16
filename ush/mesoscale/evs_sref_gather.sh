#!/bin/ksh
set -x 

#************************************************************
# Purpose: collet small stat files to form a big stat file 
#   Input parameter: verify - verification case (VERIF_CASE)
# Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************

export regrid='NONE'

#*******************************************
# Build POE script to collect sub-jobs
# ******************************************
>run_gather_all_poe.sh

modnam=sref
verify=$1
export vday=$VDATE


MODEL=`echo $modnam | tr '[a-z]' '[A-Z]'`

#************************************************
# Build sub-jobs
# ***********************************************
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

   echo "[[ $SENDCOM = YES  &&  -s ${WORK}/gather/${vday}/${modnam}_${verify}_${vday}.stat ]] && cp -v ${WORK}/gather/${vday}/${modnam}_${verify}_${vday}.stat  $COMOUTfinal/evs.stats.${model}.${verify}.v${vday}.stat">>run_gather_${verify}.sh

  chmod +x run_gather_${verify}.sh

  echo "${DATA}/run_gather_${verify}.sh" >> run_gather_all_poe.sh 

chmod +x run_gather_all_poe.sh

#********************************************
#  Run the POE script
#*******************************************
${DATA}/run_gather_all_poe.sh
export err=$?; err_chk


