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

modl=$1
verify=$2
beg=$3
end=$4

if [ $modl = all ] ; then
  models="gefs cmce ecme naefs"
else
  models=$modl
fi 

for modnam in $models ; do

   MODEL=`echo $modnam | tr '[a-z]' '[A-Z]'`
   output_base=${WORK}/gather

   >run_gather_${modnam}_${verify}.sh

    echo  "export output_base=$output_base" >> run_gather_${modnam}_${verify}.sh 
    echo  "export verify=$verify" >> run_gather_${modnam}_${verify}.sh 

    echo  "export vbeg=$beg" >> run_gather_${modnam}_${verify}.sh
    echo  "export vend=$end" >> run_gather_${modnam}_${verify}.sh
    echo  "export valid_increment=21600" >>  run_gather_${modnam}_${verify}.sh

    echo  "export model=$modnam" >> run_gather_${modnam}_${verify}.sh
    echo  "export MODEL=${MODEL}" >> run_gather_${modnam}_${verify}.sh
    echo  "export stat_file_dir=${COMOUTsmall}" >> run_gather_${modnam}_${verify}.sh

    echo  "export gather_output_dir=${WORK}/gather " >> run_gather_${modnam}_${verify}.sh

    if [ $verify = grid2obs ] ; then   
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/StatAnlysis_fcstGENS_obsPREPBUFR_GatherByDay.conf " >> run_gather_${modnam}_${verify}.sh
    elif [ $verify = grid2grid ] ; then
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/StatAnlysis_fcstGENS_obsAnalysis_GatherByDay.conf " >> run_gather_${modnam}_${verify}.sh
    elif [ $verify = precip ] ; then
     echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/StatAnlysis_fcstGENS_obsCCPA_GatherByDay.conf " >> run_gather_${modnam}_${verify}.sh
    elif [ $verify = snowfall ] ; then
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/StatAnlysis_fcstGENS_obsNOHRSC_GatherByDay.conf " >> run_gather_${modnam}_${verify}.sh
    elif [ $verify = sea_ice ] ; then
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/StatAnlysis_fcstGENS_obsOSI_SAF_GatherByDay.conf " >> run_gather_${modnam}_${verify}.sh
    elif [ $verify = sst24h ] ; then
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/StatAnlysis_fcstGENS_obsGHRSST_GatherByDay.conf " >> run_gather_${modnam}_${verify}.sh
    elif [ $verify = cnv ] ; then
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/StatAnlysis_fcstGENS_obsPREPBUFR_CNV_GatherByDay.conf " >> run_gather_${modnam}_${verify}.sh
    fi

    [[ $SENDCOM="YES" ]] && echo "cp $output_base/${vday}/${modnam}_${verify}_${vday}.stat $COMOUTfinal/evs.stats.${modnam}.${RUN}.${verify}.v${vday}.stat" >> run_gather_${modnam}_${verify}.sh
  chmod +x run_gather_${modnam}_${verify}.sh

  echo "${DATA}/run_gather_${modnam}_${verify}.sh" >> run_gather_all_poe.sh 

done

chmod 775 run_gather_all_poe.sh

 ${DATA}/run_gather_all_poe.sh
