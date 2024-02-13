#!/bin/ksh
set -x 
#**************************************************************************
#  Purpose: To combine narre's small stat files to a big stat file 
#  Last update: 10/27/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
#



export regrid='NONE'

>run_gather_all_poe.sh

modnam=$MODELNAME
verifys=$VERIF_CASE


for verify in $verifys   ; do 

    MODEL=`echo $modnam | tr '[a-z]' '[A-Z]'`

  >run_gather_${verify}.sh

    
    echo  "export output_base=${WORK}/gather" >> run_gather_${verify}.sh 
    echo  "export verify=$verify" >> run_gather_${verify}.sh 

    echo  "export vbeg=00" >> run_gather_${verify}.sh
    echo  "export vend=23" >> run_gather_${verify}.sh
    echo  "export valid_increment=3600" >>  run_gather_${verify}.sh

    echo  "export OBTYPE=PREPBUFR" >>  run_gather_${verify}.sh


    echo  "export model=$modnam" >> run_gather_${verify}.sh
    echo  "export MODEL=${MODEL}_MEAN" >> run_gather_${verify}.sh
    echo  "export stat_file_dir=${COMOUTsmall}" >> run_gather_${verify}.sh
    echo  "export gather_output_dir=${WORK}/gather " >> run_gather_${verify}.sh

    echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/StatAnlysis_fcstNARRE_obsPREPBUFR_GatherByDay.conf " >> run_gather_${verify}.sh

    echo "echo gather Metplus log file start:" >> run_gather_${verify}.sh
    echo "cat \$output_base/logs/*" >> run_gather_${verify}.sh
    echo "echo gather Metplus log file end:" >> run_gather_${verify}.sh 

    echo "[[ $SENDCOM = "YES" && -s ${WORK}/gather/${vday}/${MODEL}_MEAN_grid2obs_${vday}.stat ]] && cp -v ${WORK}/gather/${vday}/${MODEL}_MEAN_grid2obs_${vday}.stat  $COMOUTfinal/evs.stats.${model}.mean.grid2obs.v${vday}.stat">>run_gather_${verify}.sh

  chmod +x run_gather_${verify}.sh

  echo "${DATA}/run_gather_${verify}.sh" >> run_gather_all_poe.sh 


done 

chmod 775 run_gather_all_poe.sh

 ${DATA}/run_gather_all_poe.sh
 export err=$?; err_chk

