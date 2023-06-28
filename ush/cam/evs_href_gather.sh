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

modnam=href
verify=$1

if [ $verify = precip ] ; then
 MODELS='HREF HREF_MEAN HREF_PMMN HREF_LPMM HREF_AVRG  HREF_PROB HREF_EAS HREF_SNOW'
elif [ $verify = grid2obs ] ; then
 MODELS='HREF HREF_MEAN HREF_PROB'
elif [ $verify = spcoutlook ] ; then
 MODELS='HREF_MEAN'
fi 

for MODL in $MODELS ; do

    modl=`echo $MODL | tr '[A-Z]' '[a-z]'`

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

    echo "cp ${WORK}/gather/${vday}/${MODL}_${verify}_${vday}.stat  $COMOUTfinal/evs.stats.${modl}.${verify}.v${vday}.stat" >> run_gather_${verify}_${MODL}.sh

    chmod +x run_gather_${verify}_${MODL}.sh
 
    echo "${DATA}/run_gather_${verify}_${MODL}.sh" >> run_gather_all_poe.sh    
   
done

chmod 775 run_gather_all_poe.sh

 ${DATA}/run_gather_all_poe.sh

exit

