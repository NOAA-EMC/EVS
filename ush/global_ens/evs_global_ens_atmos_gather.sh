#!/bin/ksh
#************************************************************
# Purpose: collet small stat files to form a big stat file
#          by using MET StatAnlysis tool
#   Input parameter:
#     modl   - model name 
#     verify - verification case (VERIF_CASE)
#     beg    - validation begin time
#     end    - validation end time
#
# Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************
set -x 


###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'


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
   #***************************************
   # Build sub-task scripts
   #**************************************
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
    nsmall_stat_files=$(find ${COMOUTsmall} -type f 2>/dev/null | wc -l)
    if [ $nsmall_stat_files -eq 0 ]; then
      err_exit "No small stats files in ${COMOUTsmall}"
    fi
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
    echo "export err=\$?; err_chk" >> run_gather_${modnam}_${verify}.sh
    if [ $SENDCOM="YES" ] ; then
        echo "if [ -s  \$output_base/${vday}/${modnam}_${verify}_${vday}.stat ]; then" >> run_gather_${modnam}_${verify}.sh
        echo "    cp -v \$output_base/${vday}/${modnam}_${verify}_${vday}.stat $COMOUTfinal/evs.stats.${modnam}.${RUN}.${verify}.v${vday}.stat" >> run_gather_${modnam}_${verify}.sh
        echo "fi" >> run_gather_${modnam}_${verify}.sh
    fi
  chmod +x run_gather_${modnam}_${verify}.sh
  echo "${DATA}/run_gather_${modnam}_${verify}.sh" >> run_gather_all_poe.sh 
done

#*******************************
# Run su-tasks
#******************************
chmod 775 run_gather_all_poe.sh
${DATA}/run_gather_all_poe.sh
