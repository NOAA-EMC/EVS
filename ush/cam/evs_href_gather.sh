#!/bin/ksh
#************************************************************
# Purpose: collet small stat files to form a big stat file
#   Input parameter: verify - verification case (VERIF_CASE)
# Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************

set -x 
export regrid='NONE'

modnam=href
verify=$1

get_gather=no

if [ $verify = precip ] ; then
 if [ "$verif_precip" = "no" ] ; then
  MODELS='HREF_SNOW'
 elif [ "$verif_snowfall" = "no" ] ; then
  MODELS='HREF HREF_MEAN HREF_PMMN HREF_LPMM HREF_AVRG  HREF_PROB HREF_EAS'
 else
  MODELS='HREF HREF_MEAN HREF_PMMN HREF_LPMM HREF_AVRG  HREF_PROB HREF_EAS HREF_SNOW'
 fi
  for MODL in $MODELS ; do
    if [ -s $COMOUTsmall/${MODL}/*.stat ] ; then
      get_gather=yes
    fi
  done
elif [ $verify = grid2obs ] ; then
 MODELS='HREF HREF_MEAN HREF_PROB'
 if [ -s $COMOUTsmall/*.stat ] ; then
    get_gather=yes
 fi
elif [ $verify = spcoutlook ] ; then
 MODELS='HREF_MEAN'
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
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/StatAnlysis_fcstHREF_obsPREPBUFR_GatherByDay.conf " >> run_gather_${verify}_${MODL}.sh
    elif [ $verify = precip ] ; then
      echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/StatAnlysis_fcstHREF_obsAnalysis_GatherByDay.conf " >> run_gather_${verify}_${MODL}.sh
   fi

    echo "[[ $SENDCOM = YES  && -s ${WORK}/gather/${vday}/${MODL}_${verify}_${vday}.stat ]] && cp -v ${WORK}/gather/${vday}/${MODL}_${verify}_${vday}.stat  $COMOUTfinal/evs.stats.${modl}.${verify}.v${vday}.stat" >> run_gather_${verify}_${MODL}.sh

    chmod +x run_gather_${verify}_${MODL}.sh
 
    echo "${DATA}/run_gather_${verify}_${MODL}.sh" >> run_gather_all_poe.sh    
   
done

chmod 775 run_gather_all_poe.sh

#*****************************
#  Run the POE script
#*****************************
${DATA}/run_gather_all_poe.sh
export err=$?; err_chk

else
  echo "NO stat files exsist in $COMOUTsmall directory" 
fi 

