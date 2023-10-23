#!/bin/ksh

# Script: evs_global_ens_snow_ice.sh
# Purpose: run Global ensembles (GEFS, CMCE, EC and NAES)  snow and sea ice verification for upper fields 
#            end 24hr APCP by setting several METPlus environment variables and running METplus conf files 
# Input parameters:
#   (1) model_list: either gefs or cmce or ecme or naefs or all
#   (2) verify_list: either upper or precip or all
# Execution steps:
#   Both upper and precip have similar steps:
#   (1) Set/export environment parameters for METplus conf files and put them into  procedure files 
#   (2) Set running conf files and put them into  procedure files           
#   (3) Put all MPI procedure files into one MPI script file run_all_gens_sea_ice_poe.sh
#   (4) If $run_mpi is yes, run the MPI script  in paraalel
#        otherwise run the MPI script in sequence
# Note: total number of parallels = grid2grid (models x cycles) + precip (models)
#   The maximum (4 models) = 4 + 2 + 2 + 2 + 4 = 14,  in this case 14 nodes should be set in its ecf,   
#
# Author: Binbin Zhou, IMSG
# Update log: 2/4/2022, beginning version  
#

set -x 



###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'

############################################################

>run_all_gens_snow_ice_poe.sh

modnam=$1
verify=$2

$USHevs/global_ens/evs_gens_atmos_check_input_files.sh osi_saf
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh $modnam


tail='/atmos'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN


anl=osi_saf
export cyc='00'


if [ $verify = sea_ice ] ; then 

      MODL=`echo $modnam | tr '[a-z]' '[A-Z]'`

      if [ $modnam = gefs ] ; then
        mbrs=30
      elif [ $modnam = cmce ] ; then
        mbrs=20
      elif [ $modnam = ecme ] ; then
        mbrs=50
      else
        echo "wrong model: $modnam"
      fi 

    #for average in 24 168 ; do 
    for average in 24 ; do 

        past=`$NDATE -$average ${vday}01`
        export vday1=${past:0:8}
	export period=multi.${vday1}00to${vday}00_G004
        
        >run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh

	echo  "export average=$average" >>  run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
	echo  "export period=$period"  >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
        echo  "export output_base=${WORK}/${verify}/run_${modnam}_valid_at_t${cyc}z_${verify}_${average}" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh

        echo  "export modelpath=$COM_IN" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh

        echo  "export OBTYPE=OSI_SAF" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
        echo  "export maskpath=$maskpath" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh

        echo  "export obsvhead=$anl" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
        echo  "export obsvgrid=$period" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
        echo  "export obsvpath=$COM_IN" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
     
        echo  "export modelgrid=grid3.icec_${average}h.f" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
        echo  "export model=$modnam"  >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
        echo  "export MODEL=$MODL" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
        echo  "export modelhead=$modnam" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh

        echo  "export vbeg=$cyc" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
        echo  "export vend=$cyc" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
        echo  "export valid_increment=21600" >>  run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh


         if [ $average = 24 ] ; then
	  echo  "export lead='24, 48, 72, 96, 120, 144, 168, 192, 216,  240,  264,  288,  312,  336,  360,  384' "  >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
	  #echo  "export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384' "  >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
         elif  [ $average = 168 ] ; then
           echo  "export lead='168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384' "  >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
         fi

        echo  "export modeltail='.nc'" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh
        echo  "export members=$mbrs" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh


        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstGEFS_obsOSI_SAF.conf " >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh

	echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstGEFS_obsOSI_SAF.conf " >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstGEFS_obsOSI_SAF_mean.conf " >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh

        [[ $SENDCOM="YES" ]] && echo "cp \$output_base/stat/${modnam}/*.stat $COMOUTsmall" >> run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh

        chmod +x run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh

        echo "${DATA}/run_${modnam}_valid_at_t${cyc}z_${verify}_${average}.sh" >> run_all_gens_sea_ice_poe.sh

   done 

   chmod 775 run_all_gens_sea_ice_poe.sh

   
fi   




if [ -s run_all_gens_sea_ice_poe.sh ] ; then
    ${DATA}/run_all_gens_sea_ice_poe.sh	 
fi


if [ $gather = yes ] ; then

  $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME $verify 00 00 

fi
 
 
