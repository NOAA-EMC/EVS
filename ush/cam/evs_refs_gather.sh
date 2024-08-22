#!/bin/ksh
#************************************************************
# Purpose: collet small stat files to form a big stat file
#   Input parameter: verify - verification case (VERIF_CASE)
# Last update: 05/30/2024, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************

set -x 
export regrid='NONE'

modnam=href
verify=$1

if [ $verify = precip ] ; then
 if [ "$verif_precip" = "no" ] ; then
  MODELS='REFS_SNOW'
 elif [ "$verif_snowfall" = "no" ] ; then
  MODELS='REFS REFS_MEAN REFS_PMMN REFS_LPMM REFS_AVRG  REFS_PROB REFS_EAS'
 else
  MODELS='REFS REFS_MEAN REFS_PMMN REFS_LPMM REFS_AVRG  REFS_PROB REFS_EAS REFS_SNOW'
 fi
 for MODL in $MODELS ; do
   if [ -s $COMOUTsmall/${MODL}/*.stat ] ; then
      get_gather=yes
   fi
 done
elif [ $verify = grid2obs ] ; then
 MODELS='REFS REFS_MEAN REFS_PROB'
 if [ -s $COMOUTsmall/*.stat ] ; then
    get_gather=yes
 fi
elif [ $verify = spcoutlook ] ; then
 MODELS='REFS_MEAN'
 if [ -s $COMOUTsmall/*.stat ] ; then
    get_gather=yes
 fi
fi 

if [ $get_gather = yes ] ; then

#****************************************
# Build a POE script to collect sub-jobs
#****************************************
>run_gather_all_poe.sh
for MODL in $MODELS ; do

    modl=`echo $MODL | tr '[A-Z]' '[a-z]'`

#************************************************
# Build sub-jobs
#***********************************************
>run_gather_${verify}_${MODL}.sh

    echo  "export output_base=${WORK}/gather" >> run_gather_${verify}_${MODL}.sh 
    echo  "export verify=$verify" >> run_gather_${verify}_${MODL}.sh 


    echo  "export vbeg=00" >> run_gather_${verify}_${MODL}.sh
    echo  "export vend=23" >> run_gather_${verify}_${MODL}.sh
    echo  "export valid_increment=3600" >>  run_gather_${verify}_${MODL}.sh
    echo  "export model=$modnam" >> run_gather_${verify}_${MODL}.sh
    echo  "export stat_file_dir=${COMOUTsmall}" >> run_gather_${verify}_${MODL}.sh
    echo  "export gather_output_dir=${WORK}/gather " >> run_gather_${verify}_${MODL}.sh
    echo  "export MODEL=${MODL}" >> run_gather_${verify}_${MODL}.sh
    echo  "export modl=$modl" >> run_gather_${verify}_${MODL}.sh

    if [ $verify = grid2obs ] || [ $verify = spcoutlook ] ; then 
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/StatAnlysis_fcstREFS_obsPREPBUFR_GatherByDay.conf " >> run_gather_${verify}_${MODL}.sh
    elif [ $verify = precip ] ; then
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/StatAnlysis_fcstREFS_obsAnalysis_GatherByDay.conf " >> run_gather_${verify}_${MODL}.sh
   fi

    echo "[[ $SENDCOM = YES  && -s ${WORK}/gather/${vday}/${MODL}_${verify}_${vday}.stat ]] && cp -v ${WORK}/gather/${vday}/${MODL}_${verify}_${vday}.stat  $COMOUTfinal/evs.stats.${modl}.${verify}.v${vday}.stat" >> run_gather_${verify}_${MODL}.sh

    chmod +x run_gather_${verify}_${MODL}.sh
 
    echo "${DATA}/run_gather_${verify}_${MODL}.sh" >> run_gather_all_poe.sh    
   
done

chmod 775 run_gather_all_poe.sh

#*****************************
#  Run the POE script
#*****************************
  if [ $run_mpi = yes ] ; then
    mpiexec -np 3 -ppn 3 --cpu-bind verbose,depth cfp ${DATA}/run_gather_all_poe.sh
    export err=$?; err_chk
  else
    ${DATA}/run_gather_all_poe.sh
    export err=$?; err_chk
  fi

else
  echo "NO stat files exsist in $COMOUTsmall directory"
fi 

